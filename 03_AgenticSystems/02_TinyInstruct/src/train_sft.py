"""
train_sft.py - Instruction-Tuning per maskiertem Loss (SFT)

Was hier passiert (in einem Satz):
    * dieselbe GPTMini-Architektur wie in Kapitel 3.1 (TinyGPT)
    * dieselbe Optimizer-/Scaler-/Autocast-Infrastruktur wie in Kap. 3.1
    * ABER: die Labels kommen aus dem `InstructionDataset` bereits mit
      IGNORE_INDEX (-100) fuer alle Prompt-Positionen -> der Cross-Entropy-
      Loss gibt fuer diese Positionen automatisch 0 Gradient aus.

Das Ergebnis: das Modell lernt ausschliesslich, die Response zu erzeugen,
gegeben den (nicht mit-gelernten) Prompt-Kontext. Genau der Sprung, um den
es in diesem Kapitel geht.

Hinweis zum Loss-Shift: In TinyGPT (Kap. 3.1) wird der Nachwortprognose-
Shift IM Trainings-Loop erzeugt:

    labels[:, :-1] = input_ids[:, 1:]
    labels[:, -1]  = -100

Hier machen wir es exakt gleich - nur dass unsere `labels` aus dem Dataset
schon "die richtigen Zieltokens an derselben Position wie in input_ids"
enthalten, mit IGNORE_INDEX an den Prompt-Positionen. Wir muessen also nur
noch den Shift anwenden, die IGNORE_INDEX-Maske wandert dabei einfach
implizit mit. Das ist bewusst so gewaehlt, damit der Vergleich mit TinyGPT
Zeile fuer Zeile nachvollziehbar bleibt.
"""

from __future__ import annotations

import argparse
import json
import os
from multiprocessing import freeze_support

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.cuda.amp import autocast, GradScaler
from tqdm import tqdm
from transformers import LlamaTokenizerFast

from data import (
    IGNORE_INDEX,
    InstructionDataset,
    debug_show_masking,
    format_prompt,
    load_instruction_samples,
)
from model import build_model


DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# Wir verwenden bewusst denselben Tokenizer wie Kapitel 3.1, damit ein
# TinyGPT-Checkpoint eingespielt werden kann, ohne dass sich Vokabular oder
# Embeddings verschieben.
TOKENIZER_NAME = "hf-internal-testing/llama-tokenizer"


# -------------------------------------------------------------------------
# Config
# -------------------------------------------------------------------------

def load_config(profile: str, config_path: str) -> dict:
    with open(config_path, "r") as f:
        cfg = json.load(f)
    if profile not in cfg:
        raise KeyError(
            f"Profil '{profile}' nicht in {config_path}. "
            f"Verfuegbar: {list(cfg.keys())}"
        )
    return cfg[profile]


# -------------------------------------------------------------------------
# Trainings-Loop (Kern)
# -------------------------------------------------------------------------

def compute_sft_loss(
    model, input_ids, attention_mask, labels, vocab_size,
):
    """
    Berechnet den SFT-Loss. Vergleiche mit TinyGPT (train_gpt_mini.py):

        labels[:, :-1] = input_ids[:, 1:]  # Nachwort-Vorhersage
        labels[:, -1]  = -100

    In TinyInstruct kommen `labels` aus dem Dataset schon vor-maskiert
    (IGNORE_INDEX auf Prompt-Positionen). Wir muessen also NUR noch den
    Shift der Nachwortprognose durchfuehren - und die Maske wandert
    dabei implizit mit.
    """
    # Nachwortprognose-Shift wie in Kap. 3.1 (nur eben mit unseren
    # bereits maskierten labels).
    shifted_labels = labels.clone()
    shifted_labels[:, :-1] = labels[:, 1:]
    shifted_labels[:, -1] = IGNORE_INDEX

    logits = model(input_ids, attention_mask=attention_mask)  # (B, T, V)
    loss = F.cross_entropy(
        logits.view(-1, vocab_size),
        shifted_labels.view(-1),
        ignore_index=IGNORE_INDEX,
    )
    return loss


def train(cfg, tokenizer, device, output_dir):
    # ---- Daten -----------------------------------------------------------
    raw_samples = load_instruction_samples(cfg["N_INSTRUCTION_SAMPLES"])

    def tokenize_fn(text: str) -> list:
        # `add_special_tokens=False`, weil BOS/EOS im Instruct-Format nicht
        # gewuenscht sind (wir wollen exakte Praefix-Uebereinstimmung
        # zwischen prompt_ids und full_ids in data.py).
        return tokenizer.encode(text, add_special_tokens=False)

    dataset = InstructionDataset(
        samples=raw_samples,
        tokenize_fn=tokenize_fn,
        pad_token_id=tokenizer.pad_token_id,
        block_size=cfg["BLOCK_SIZE"],
        eos_token_id=tokenizer.eos_token_id,
    )

    if len(dataset) == 0:
        raise RuntimeError(
            "Nach der Filterung sind keine Trainingsbeispiele uebrig. "
            "Vermutlich sind alle Beispiele laenger als BLOCK_SIZE oder "
            "der Praefix-Sanity-Check schlaegt fehl. Setze BLOCK_SIZE hoch."
        )

    # Zeige zur Kontrolle EIN Beispiel mit Maskierung, damit man sehen
    # kann, dass die didaktische Pointe tatsaechlich zutrifft:
    print("\n--- Kontrolle: so sieht ein maskiertes Trainingsbeispiel aus ---")
    print(debug_show_masking(dataset[0], tokenizer, max_tokens=40))
    print("---------------------------------------------------------------\n")

    loader = DataLoader(dataset, batch_size=cfg["BATCH_SIZE"], shuffle=True)

    # ---- Modell ---------------------------------------------------------
    model = build_model(
        vocab_size=tokenizer.vocab_size,
        context_length=cfg["BLOCK_SIZE"],
        embed_dim=cfg["EMBED_DIM"],
        n_heads=cfg["HEADS"],
        n_layers=cfg["LAYERS"],
        checkpoint_path=cfg.get("BASE_MODEL_CKPT"),
        device=device,
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg["LEARNING_RATE"])
    use_amp = device.type == "cuda"
    scaler = GradScaler(enabled=use_amp)

    # ---- Trainings-Loop -------------------------------------------------
    print(f"[train] Starte SFT-Training auf {device} "
          f"({cfg['EPOCHS']} Epochen, {len(dataset)} Beispiele, "
          f"Batch={cfg['BATCH_SIZE']}, LR={cfg['LEARNING_RATE']}).")

    model.train()
    for epoch in range(cfg["EPOCHS"]):
        loop = tqdm(loader, desc=f"Epoch {epoch+1}/{cfg['EPOCHS']}")
        for batch in loop:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)

            optimizer.zero_grad()
            with autocast(enabled=use_amp):
                loss = compute_sft_loss(
                    model, input_ids, attention_mask, labels,
                    vocab_size=tokenizer.vocab_size,
                )

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            loop.set_postfix(loss=float(loss.detach().cpu()))

    # ---- Checkpoint -----------------------------------------------------
    os.makedirs(output_dir, exist_ok=True)
    ckpt_path = os.path.join(output_dir, "tinyinstruct_sft.pt")
    torch.save({
        "model_state_dict": model.state_dict(),
        "config": cfg,
    }, ckpt_path)
    print(f"[train] Modell gespeichert unter {ckpt_path}")

    return model, ckpt_path


# -------------------------------------------------------------------------
# Kurze End-of-Training-Demo
# -------------------------------------------------------------------------

def demo_generate(model, tokenizer, device, prompts, max_new_tokens=60, top_k=40):
    """Kurze Sanity-Demo: fuer ein paar Instruktionen eine Antwort erzeugen."""
    model.eval()
    for instruction in prompts:
        prompt_text = format_prompt(instruction)
        input_ids = tokenizer.encode(
            prompt_text, return_tensors="pt", add_special_tokens=False
        ).to(device)
        generated = input_ids
        with torch.no_grad():
            for _ in range(max_new_tokens):
                logits = model(generated)
                next_logits = logits[:, -1, :]
                probs = torch.softmax(next_logits, dim=-1)
                top_probs, top_idx = torch.topk(probs, top_k)
                next_token = top_idx[0, torch.multinomial(top_probs[0], 1)]
                generated = torch.cat((generated, next_token.unsqueeze(0)), dim=1)
        text = tokenizer.decode(generated[0], skip_special_tokens=True)
        # Nur den Response-Anteil zeigen (alles nach "### Response:"):
        marker = "### Response:"
        if marker in text:
            response = text.split(marker, 1)[1].strip()
        else:
            response = text
        print(f"\n[DEMO] Instruction: {instruction}")
        print(f"[DEMO] Response:    {response}")


# -------------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------------

def main():
    freeze_support()

    parser = argparse.ArgumentParser(
        description="TinyInstruct: SFT auf einem GPTMini-Base-Modell "
                    "durch maskierten Loss (nur Response zaehlt)."
    )
    parser.add_argument("--profile", default="laptop",
                        help="Config-Profil (test | laptop | lima).")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH,
                        help="Pfad zur config.json.")
    parser.add_argument("--output-dir",
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "checkpoints"),
                        help="Zielordner fuer den SFT-Checkpoint.")
    parser.add_argument("--no-demo", action="store_true",
                        help="Nach dem Training keine Beispielgenerierung ausfuehren.")
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

    model, ckpt_path = train(cfg, tokenizer, device, args.output_dir)

    if not args.no_demo:
        demo_prompts = [
            "Was ist die Hauptstadt von Frankreich?",
            "Nenne drei Primzahlen.",
            "Erklaere in einem Satz, was ein Transistor ist.",
        ]
        print("\n" + "=" * 70)
        print("Beispielgenerierung mit dem SFT-Modell")
        print("(Achtung: bei einem Rauchtest-Profil und ohne echten TinyGPT-")
        print("Checkpoint sind die Antworten haeufig Unsinn - das ist normal.)")
        print("=" * 70)
        demo_generate(model, tokenizer, device, demo_prompts)


if __name__ == "__main__":
    main()
