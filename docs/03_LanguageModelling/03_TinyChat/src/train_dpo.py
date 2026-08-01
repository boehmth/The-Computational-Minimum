"""
train_dpo.py - Direct Preference Optimization (Kap. 3.3, TinyChat)

DIDAKTISCHE POINTE DIESES KAPITELS
==================================

Der DPO-Loss (Rafailov et al., 2023) sieht kompliziert aus, ist aber
letztlich ein einfacher Klassifikations-Loss auf Paaren von Antworten:

    loss = -log_sigmoid( beta * (
        (logp_pi(chosen)   - logp_ref(chosen)  )     # wie viel STAERKER die
      - (logp_pi(rejected) - logp_ref(rejected))     # neue Policy die
    ))                                               # chosen-Antwort bevorzugt,
                                                     # relativ zum Anker

Was passiert intuitiv:
- Die Politur-Policy (pi) darf sich von der Referenz (ref, dem SFT-Modell
  aus Kap. 3.2) entfernen - aber NUR so, dass sie chosen-Antworten
  bevorzugt und rejected-Antworten unterdrueckt.
- Das Vorzeichen von "wie viel wahrscheinlicher unter pi als unter ref"
  entscheidet, ob dieses Paar den Loss senkt oder nicht.
- `beta` ist der einzige echte Hyperparameter: klein = zaghafte Anpassung
  nahe am SFT-Anker; gross = aggressive Anpassung, riskiert Overfitting
  und Mode-Collapse.

Der ganze Rest dieser Datei ist Buchhaltung:
  * Tokenisieren (in `data.py`)
  * Log-Wahrscheinlichkeiten der Response-Tokens einsammeln
  * Mit dem Referenzmodell dasselbe unter torch.no_grad() ausrechnen
  * Beide Differenzen bilden, sigmoid, log, negativ - fertig.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
from multiprocessing import freeze_support

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.cuda.amp import autocast, GradScaler
from tqdm import tqdm
from transformers import LlamaTokenizerFast

from data import IGNORE_INDEX, PreferenceDataset, load_preference_samples

# Wir muessen `build_model` aus Kap. 3.2 wiederverwenden, damit die
# Modell-Architektur exakt identisch bleibt (das ist Voraussetzung dafuer,
# dass wir den SFT-Checkpoint einfach als Startpunkt laden koennen).
import sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_TINYINSTRUCT_SRC = os.path.normpath(os.path.join(_HERE, "..", "..", "02_TinyInstruct", "src"))
if _TINYINSTRUCT_SRC not in sys.path:
    sys.path.insert(0, _TINYINSTRUCT_SRC)
from model import build_model  # noqa: E402


DEFAULT_CONFIG_PATH = os.path.join(_HERE, "config.json")
TOKENIZER_NAME = "hf-internal-testing/llama-tokenizer"


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
# Kern: Log-Wahrscheinlichkeit einer Antwort (nur ueber Response-Tokens)
# -------------------------------------------------------------------------

def response_logprob(logits: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
    """
    Summiert die Log-Wahrscheinlichkeiten des Modells fuer die Response-
    Tokens (Positionen, an denen labels != IGNORE_INDEX ist).

    Vorgehen (dieselbe Shift-Logik wie in Kap. 3.1 und 3.2):
      1. Nachwortprognose-Shift: shifted_labels[i] = labels[i+1]
      2. Positionen mit shifted_labels == IGNORE_INDEX ausblenden
      3. Ueber die verbleibenden Positionen die Log-Prob des Zieltokens
         aufsummieren -> ein Wert pro Beispiel im Batch.

    Rueckgabe: Tensor der Form (B,) - eine Log-Wahrscheinlichkeit pro
    Batch-Element.
    """
    # 1) Shift wie in Kap. 3.1/3.2
    shifted_labels = labels.clone()
    shifted_labels[:, :-1] = labels[:, 1:]
    shifted_labels[:, -1] = IGNORE_INDEX

    # 2) Log-Softmax ueber das Vokabular
    log_probs = F.log_softmax(logits, dim=-1)  # (B, T, V)

    # 3) Log-Prob des jeweiligen Ziel-Tokens einsammeln
    #    Wir ersetzen IGNORE_INDEX temporaer durch 0, damit `gather`
    #    nicht crashed, und multiplizieren nachher mit der Maske.
    valid_mask = (shifted_labels != IGNORE_INDEX)                         # (B, T)
    labels_for_gather = shifted_labels.clone()
    labels_for_gather[~valid_mask] = 0
    per_tok_logp = log_probs.gather(-1, labels_for_gather.unsqueeze(-1)).squeeze(-1)  # (B, T)

    # 4) Nur ueber die Response-Positionen summieren
    per_tok_logp = per_tok_logp * valid_mask.float()
    return per_tok_logp.sum(dim=-1)  # (B,)


# -------------------------------------------------------------------------
# Kern: DPO-Loss
# -------------------------------------------------------------------------

def dpo_loss(
    policy_chosen_logp: torch.Tensor,
    policy_rejected_logp: torch.Tensor,
    ref_chosen_logp: torch.Tensor,
    ref_rejected_logp: torch.Tensor,
    beta: float,
):
    """
    Berechnet den DPO-Loss und ein paar Diagnose-Groessen.

    Die zentrale Formel (Rafailov et al. 2023, Gl. 7):

        L_DPO = -E[ log sigmoid( beta * (
                    (logp_pi(chosen)   - logp_ref(chosen)  )
                  - (logp_pi(rejected) - logp_ref(rejected))
                ) ) ]

    Rueckgabe:
        loss:            skalarer Loss (Mittelwert ueber den Batch)
        chosen_reward:   beta * (logp_pi(chosen)   - logp_ref(chosen))   pro Beispiel
        rejected_reward: beta * (logp_pi(rejected) - logp_ref(rejected)) pro Beispiel
        pref_acc:        Anteil der Beispiele, bei denen chosen > rejected
    """
    chosen_reward   = beta * (policy_chosen_logp   - ref_chosen_logp)
    rejected_reward = beta * (policy_rejected_logp - ref_rejected_logp)

    # sigmoid((chosen_reward - rejected_reward)/beta * beta) = sigmoid(diff)
    # aber wir folgen direkt der Definition oben.
    logits = chosen_reward - rejected_reward
    loss = -F.logsigmoid(logits).mean()

    pref_acc = (logits > 0).float().mean()  # wie oft trifft die Policy die Praeferenz richtig?
    return loss, chosen_reward, rejected_reward, pref_acc


# -------------------------------------------------------------------------
# Trainings-Loop
# -------------------------------------------------------------------------

def train(cfg, tokenizer, device, output_dir):
    # ---- Daten -----------------------------------------------------------
    raw_samples = load_preference_samples(cfg["N_PREFERENCE_SAMPLES"])

    def tokenize_fn(text: str):
        return tokenizer.encode(text, add_special_tokens=False)

    dataset = PreferenceDataset(
        samples=raw_samples,
        tokenize_fn=tokenize_fn,
        pad_token_id=tokenizer.pad_token_id,
        block_size=cfg["BLOCK_SIZE"],
        eos_token_id=tokenizer.eos_token_id,
    )
    if len(dataset) == 0:
        raise RuntimeError(
            "Nach der Filterung sind keine Trainingsbeispiele uebrig. "
            "Vermutlich sind chosen/rejected laenger als BLOCK_SIZE."
        )

    loader = DataLoader(dataset, batch_size=cfg["BATCH_SIZE"], shuffle=True)

    # ---- Modell: Policy + Referenz --------------------------------------
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

    # Die Referenz ist eine EINGEFRORENE Kopie desselben SFT-Modells.
    # Ohne diesen Anker kann DPO das Modell unlimitiert 'verbiegen', was
    # zu Mode-Collapse und stumpfen Antworten fuehrt (der Grund fuer den
    # KL-Term in der urspruenglichen RLHF-Formulierung).
    print("[train] Baue Referenz-Modell (eingefrorene Kopie der Policy)...")
    reference = copy.deepcopy(policy)
    for p in reference.parameters():
        p.requires_grad_(False)
    reference.eval()

    optimizer = torch.optim.AdamW(policy.parameters(), lr=cfg["LEARNING_RATE"])
    use_amp = device.type == "cuda"
    scaler = GradScaler(enabled=use_amp)
    beta = cfg["DPO_BETA"]

    print(f"[train] Starte DPO-Training auf {device} "
          f"({cfg['EPOCHS']} Epochen, {len(dataset)} Praeferenz-Tripel, "
          f"batch={cfg['BATCH_SIZE']}, beta={beta}).")

    for epoch in range(cfg["EPOCHS"]):
        policy.train()
        loop = tqdm(loader, desc=f"Epoch {epoch+1}/{cfg['EPOCHS']}")

        for batch in loop:
            c_ids    = batch["chosen_ids"].to(device)
            c_labels = batch["chosen_labels"].to(device)
            c_mask   = batch["chosen_mask"].to(device)
            r_ids    = batch["rejected_ids"].to(device)
            r_labels = batch["rejected_labels"].to(device)
            r_mask   = batch["rejected_mask"].to(device)

            optimizer.zero_grad()
            with autocast(enabled=use_amp):
                # --- Policy: Log-Wahrscheinlichkeiten fuer beide Seiten
                policy_chosen_logits   = policy(c_ids, attention_mask=c_mask)
                policy_rejected_logits = policy(r_ids, attention_mask=r_mask)
                policy_chosen_logp   = response_logprob(policy_chosen_logits,   c_labels)
                policy_rejected_logp = response_logprob(policy_rejected_logits, r_labels)

                # --- Referenz: dasselbe, aber ohne Gradienten
                with torch.no_grad():
                    ref_chosen_logits   = reference(c_ids, attention_mask=c_mask)
                    ref_rejected_logits = reference(r_ids, attention_mask=r_mask)
                    ref_chosen_logp   = response_logprob(ref_chosen_logits,   c_labels)
                    ref_rejected_logp = response_logprob(ref_rejected_logits, r_labels)

                # --- Der DPO-Loss (die "eine Zeile" dieses Kapitels)
                loss, chosen_reward, rejected_reward, pref_acc = dpo_loss(
                    policy_chosen_logp,
                    policy_rejected_logp,
                    ref_chosen_logp,
                    ref_rejected_logp,
                    beta=beta,
                )

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            loop.set_postfix(
                loss=float(loss.detach().cpu()),
                pref_acc=float(pref_acc.detach().cpu()),
                r_chosen=float(chosen_reward.mean().detach().cpu()),
                r_rejected=float(rejected_reward.mean().detach().cpu()),
            )

    # ---- Checkpoint -----------------------------------------------------
    os.makedirs(output_dir, exist_ok=True)
    ckpt_path = os.path.join(output_dir, "tinychat_dpo.pt")
    torch.save({
        "model_state_dict": policy.state_dict(),
        "config": cfg,
    }, ckpt_path)
    print(f"[train] Modell gespeichert unter {ckpt_path}")
    return policy, ckpt_path


# -------------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------------

def main():
    freeze_support()

    parser = argparse.ArgumentParser(
        description="TinyChat: DPO-Feinjustierung auf einem SFT-getunten "
                    "GPTMini (aus Kap. 3.2) mit Praeferenz-Tripeln."
    )
    parser.add_argument("--profile", default="laptop",
                        help="Config-Profil (test | laptop).")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH,
                        help="Pfad zur config.json.")
    parser.add_argument("--output-dir",
                        default=os.path.join(_HERE, "..", "checkpoints"),
                        help="Zielordner fuer den DPO-Checkpoint.")
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
        print("[main] WARNUNG: SFT_MODEL_CKPT ist null. Ohne SFT-Anker macht "
              "DPO didaktisch keinen Sinn - fuer einen Rauchtest OK, aber "
              "die trainierten Rewards werden nahe 0 bleiben, weil Policy "
              "und Referenz beim Start identisch (zufaellig) sind.")

    train(cfg, tokenizer, device, args.output_dir)


if __name__ == "__main__":
    main()
