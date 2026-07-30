"""
train_rl.py - Ergebnisbasiertes RL-Reasoning-Training (STaR / R1-Zero-Prinzip)

Der Trainings-Loop macht in jeder Iteration DREI Dinge:

    1. ROLLOUT:  Fuer jede Aufgabe erzeugt das Modell N verschiedene
                 Antworten (mit Temperatur-Sampling, damit die Antworten
                 diverser werden).
    2. REWARD:   Fuer jede Antwort berechnet compute_reward()
                 (aus reward.py) einen Wert 0.0 / 0.1 / 1.0.
    3. FILTER + SFT: Alle Antworten mit reward >= MIN_REWARD_TO_KEEP
                 werden als "gute Trajektorien" behalten. Auf diesen
                 macht das Modell einen normalen SFT-Schritt (maskierter
                 Loss - wie in Kap. 3.2, wo nur die Response zaehlt).

Das ist der STaR-Grundgedanke (Zelikman 2022): das Modell trainiert sich
selbst nach, indem es aus seinen eigenen erfolgreichen Antworten lernt.
Kein separates Reward-Modell, kein PPO, keine menschlichen Labels - nur
diese eine ergebnisbasierte Filterung.

Der Unterschied zu einem "richtigen" RL-Algorithmus wie GRPO/PPO ist,
dass wir hier keinen Advantage-Baseline oder KL-Constraint einbauen. Das
ist bewusst - das echte DeepSeek-R1-Zero-Rezept hat mehr Feintuning, aber
die Kern-Idee (regelbasierte Belohnung -> Selbsttraining aus erfolgreichen
Rollouts) ist bereits mit diesem einfacheren Aufbau sichtbar.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from multiprocessing import freeze_support

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torch.cuda.amp import autocast, GradScaler
from tqdm import tqdm
from transformers import LlamaTokenizerFast

from data import generate_dataset
from reward import compute_reward, REWARD_CORRECT_ANSWER


# Fuer build_model + IGNORE_INDEX + Dataset-Utility greifen wir auf 3.2 zurueck.
_HERE = os.path.dirname(os.path.abspath(__file__))
_TINYINSTRUCT_SRC = os.path.normpath(os.path.join(_HERE, "..", "..", "02_TinyInstruct", "src"))
if _TINYINSTRUCT_SRC not in sys.path:
    sys.path.insert(0, _TINYINSTRUCT_SRC)

# Wichtig: `data` als Modul aus 02_TinyInstruct heisst identisch zum lokalen
# data.py in 05_TinyReason. Wir importieren die noetigen Bausteine explizit
# mit alternativen Namen, um Konflikte zu vermeiden.
import importlib.util as _iu
_spec = _iu.spec_from_file_location("_tinyinstruct_data", os.path.join(_TINYINSTRUCT_SRC, "data.py"))
_tinstruct_data = _iu.module_from_spec(_spec)
_spec.loader.exec_module(_tinstruct_data)
IGNORE_INDEX = _tinstruct_data.IGNORE_INDEX
mask_prompt_labels = _tinstruct_data.mask_prompt_labels

from model import build_model  # aus 02_TinyInstruct/src/model.py


DEFAULT_CONFIG_PATH = os.path.join(_HERE, "config.json")
TOKENIZER_NAME = "hf-internal-testing/llama-tokenizer"


def load_config(profile: str, config_path: str) -> dict:
    with open(config_path, "r") as f:
        cfg = json.load(f)
    return cfg[profile]


# -------------------------------------------------------------------------
# Rollout: Modell erzeugt Antworten mit Temperatur-Sampling
# -------------------------------------------------------------------------

@torch.no_grad()
def rollout(model, tokenizer, prompt_ids, device, cfg):
    model.eval()
    generated = prompt_ids.clone().to(device)
    ctx_len = model.position_embedding.num_embeddings
    for _ in range(cfg["MAX_NEW_TOKENS"]):
        if generated.size(1) >= ctx_len:
            break
        logits = model(generated)
        next_logits = logits[:, -1, :] / max(cfg["TEMPERATURE"], 1e-8)
        probs = torch.softmax(next_logits, dim=-1)
        top_probs, top_idx = torch.topk(probs, cfg["TOP_K"])
        next_token = top_idx[0, torch.multinomial(top_probs[0], 1)]
        generated = torch.cat((generated, next_token.unsqueeze(0)), dim=1)
        if next_token.item() == tokenizer.eos_token_id:
            break
    return generated


# -------------------------------------------------------------------------
# Aufbau eines SFT-Beispiels aus einer erfolgreichen Rollout-Trajektorie
# -------------------------------------------------------------------------

class TrajectoryDataset(Dataset):
    """
    Erwartet Dictionaries {"input_ids", "attention_mask", "labels"} - wie
    in Kap. 3.2 - und liefert sie unveraendert an einen DataLoader.
    """
    def __init__(self, examples):
        self.examples = examples
    def __len__(self):
        return len(self.examples)
    def __getitem__(self, idx):
        return self.examples[idx]


def build_sft_example(prompt_ids, full_ids, block_size, pad_token_id):
    """
    Baut ein Batch-Element wie in 3.2:
      - labels haben IGNORE_INDEX im Prompt-Bereich, echte IDs im Response
      - alles gepadded auf block_size.
    """
    prompt_list = prompt_ids.tolist()
    full_list = full_ids.tolist()

    if full_list[: len(prompt_list)] != prompt_list:
        return None
    if len(full_list) > block_size:
        return None

    labels = mask_prompt_labels(prompt_list, full_list, None)
    pad_len = block_size - len(full_list)
    input_ids = full_list + [pad_token_id] * pad_len
    attention_mask = [1] * len(full_list) + [0] * pad_len
    labels = labels + [IGNORE_INDEX] * pad_len

    return {
        "input_ids":      torch.tensor(input_ids, dtype=torch.long),
        "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
        "labels":         torch.tensor(labels, dtype=torch.long),
    }


# -------------------------------------------------------------------------
# Trainings-Loop
# -------------------------------------------------------------------------

def train(cfg, tokenizer, device, output_dir):
    # ---- Modell ---------------------------------------------------------
    print("[train] Baue Policy-Modell...")
    policy = build_model(
        vocab_size=tokenizer.vocab_size,
        context_length=cfg["BLOCK_SIZE"],
        embed_dim=cfg["EMBED_DIM"],
        n_heads=cfg["HEADS"],
        n_layers=cfg["LAYERS"],
        checkpoint_path=cfg.get("SFT_MODEL_CKPT"),
        device=device,
    )

    optimizer = torch.optim.AdamW(policy.parameters(), lr=cfg["LEARNING_RATE"])
    use_amp = device.type == "cuda"
    scaler = GradScaler(enabled=use_amp)

    for epoch in range(cfg["EPOCHS"]):
        print(f"\n[epoch {epoch+1}/{cfg['EPOCHS']}] Erzeuge Trainingsaufgaben...")
        tasks = generate_dataset(cfg["N_TRAIN_TASKS"], seed=42 + epoch)

        # ---- Phase 1: Rollout + Reward ----------------------------------
        good_trajectories = []
        stats = {"total": 0, "correct": 0, "format_only": 0}

        loop = tqdm(tasks, desc="Rollout")
        for task in loop:
            prompt_ids = tokenizer.encode(
                task.prompt, return_tensors="pt", add_special_tokens=False,
            ).to(device)

            for _ in range(cfg["N_ROLLOUTS_PER_TASK"]):
                out_ids = rollout(policy, tokenizer, prompt_ids, device, cfg)
                out_text = tokenizer.decode(out_ids[0], skip_special_tokens=True)
                # Nur den Response-Teil hinter dem Prompt bewerten
                response_start = out_text.find(task.prompt)
                response_text = out_text[response_start + len(task.prompt):] if response_start >= 0 else out_text
                r = compute_reward(response_text, task.expected_answer)

                stats["total"] += 1
                if r.is_correct:
                    stats["correct"] += 1
                elif r.total > 0:
                    stats["format_only"] += 1

                if r.total >= cfg["MIN_REWARD_TO_KEEP"]:
                    example = build_sft_example(
                        prompt_ids.squeeze(0).cpu(),
                        out_ids.squeeze(0).cpu(),
                        cfg["BLOCK_SIZE"],
                        tokenizer.pad_token_id,
                    )
                    if example is not None:
                        good_trajectories.append(example)

            loop.set_postfix(
                good=len(good_trajectories),
                correct=stats["correct"],
                total=stats["total"],
            )

        print(f"[epoch {epoch+1}] Rollout-Statistik: "
              f"{stats['correct']}/{stats['total']} korrekt, "
              f"{stats['format_only']}/{stats['total']} nur Format, "
              f"{len(good_trajectories)} Trajektorien fuers Nachtrainieren.")

        if len(good_trajectories) == 0:
            print("[epoch] WARNUNG: keine erfolgreichen Trajektorien - der "
                  "Policy fehlt anscheinend Grundfaehigkeit. Starte 3.2 (SFT) "
                  "und trage den Checkpoint in config.json ein.")
            continue

        # ---- Phase 2: SFT auf den erfolgreichen Trajektorien -----------
        ds = TrajectoryDataset(good_trajectories)
        loader = DataLoader(ds, batch_size=cfg["BATCH_SIZE"], shuffle=True)

        policy.train()
        train_loop = tqdm(loader, desc="SFT")
        for batch in train_loop:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)

            # SFT-Shift wie in Kap. 3.2:
            shifted = labels.clone()
            shifted[:, :-1] = labels[:, 1:]
            shifted[:, -1] = IGNORE_INDEX

            optimizer.zero_grad()
            with autocast(enabled=use_amp):
                logits = policy(input_ids, attention_mask=attention_mask)
                loss = F.cross_entropy(
                    logits.view(-1, tokenizer.vocab_size),
                    shifted.view(-1),
                    ignore_index=IGNORE_INDEX,
                )
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            train_loop.set_postfix(loss=float(loss.detach().cpu()))

    # ---- Checkpoint -----------------------------------------------------
    os.makedirs(output_dir, exist_ok=True)
    ckpt_path = os.path.join(output_dir, "tinyreason.pt")
    torch.save({"model_state_dict": policy.state_dict(), "config": cfg}, ckpt_path)
    print(f"\n[train] Modell gespeichert unter {ckpt_path}")


def main():
    freeze_support()
    parser = argparse.ArgumentParser(
        description="TinyReason: ergebnisbasiertes RL-Reasoning-Training."
    )
    parser.add_argument("--profile", default="laptop",
                        help="Config-Profil (test | laptop).")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--output-dir",
                        default=os.path.join(_HERE, "..", "checkpoints"))
    args = parser.parse_args()

    cfg = load_config(args.profile, args.config)
    print("[main] Konfiguration:")
    for k, v in cfg.items():
        print(f"    {k} = {v}")

    tokenizer = LlamaTokenizerFast.from_pretrained(TOKENIZER_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[main] Device: {device}")

    if cfg.get("SFT_MODEL_CKPT") is None:
        print("[main] HINWEIS: SFT_MODEL_CKPT ist null. TinyReason funktioniert")
        print("       am besten, wenn das Startmodell aus Kap. 3.2 stammt und")
        print("       bereits Instruktionen befolgen kann. Ohne diesen Grund-")
        print("       zustand ist die Trefferquote im ersten Rollout praktisch 0.")

    train(cfg, tokenizer, device, args.output_dir)


if __name__ == "__main__":
    main()
