"""
train_moe.py - Sprachmodell-Training mit MoE (Kap. 3.4)

Der Trainings-Loop ist bewusst FAST identisch zu TinyGPT (Kap. 3.1).
Unterschied:

    * das Modell ist `GPTMiniMoE` statt `GPTMini`
    * der Loss ist:
          total_loss = language_loss + LOAD_BALANCE_WEIGHT * aux_loss
      wobei `aux_loss` = Mittelwert der pro-Layer-Load-Balancing-Losses.

Die beiden Loss-Anteile werden nebeneinander geloggt, damit man sieht,
wie sie sich waehrend des Trainings entwickeln:

  - language_loss faellt ueblicherweise stetig
  - aux_loss faellt vom Anfangswert (nahe N/K bei ganz-zufaelligem
    Gating) in Richtung 1.0, weil der Gradient das Gating auf
    Gleichverteilung schiebt.
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
from datasets import load_dataset, load_from_disk, Dataset

from model import GPTMiniMoE


DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
DATASET_NAME = "HuggingFaceFW/fineweb-edu"
TOKENIZER_NAME = "hf-internal-testing/llama-tokenizer"


def load_config(profile: str, config_path: str) -> dict:
    with open(config_path, "r") as f:
        cfg = json.load(f)
    return cfg[profile]


def main():
    freeze_support()

    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="laptop")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--output-dir",
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "checkpoints"))
    args = parser.parse_args()

    cfg = load_config(args.profile, args.config)

    TOKEN_BUDGET   = cfg["TOKEN_BUDGET"]
    BLOCK_SIZE     = cfg["BLOCK_SIZE"]
    BATCH_SIZE     = cfg["BATCH_SIZE"]
    EPOCHS         = cfg["EPOCHS"]
    EMBED_DIM      = cfg["EMBED_DIM"]
    HEADS          = cfg["HEADS"]
    LAYERS         = cfg["LAYERS"]
    LEARNING_RATE  = cfg["LEARNING_RATE"]
    NUM_EXPERTS    = cfg["NUM_EXPERTS"]
    TOP_K          = cfg["TOP_K"]
    LB_WEIGHT      = cfg["LOAD_BALANCE_WEIGHT"]

    TOKENIZED_PATH = f"tokenized_moe_{args.profile}"

    tokenizer = LlamaTokenizerFast.from_pretrained(TOKENIZER_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    # ---- Daten (analog zu TinyGPT) --------------------------------------
    def tokenize(example):
        return tokenizer(
            example["text"],
            truncation=True,
            padding="max_length",
            max_length=BLOCK_SIZE,
        )

    print(f"[data] Loading FineWeb-Edu (profile={args.profile}, token budget={TOKEN_BUDGET:,})...")

    if os.path.exists(TOKENIZED_PATH):
        print(f"[data] Found tokenized dataset - loading from disk ({TOKENIZED_PATH}).")
        tokenized = load_from_disk(TOKENIZED_PATH)
    else:
        streamed_ds = load_dataset(DATASET_NAME, split="train", streaming=True)
        texts, token_sum = [], 0
        for row in streamed_ds:
            texts.append(row["text"])
            token_sum += row.get("token_count", len(row["text"].split()))
            if token_sum >= TOKEN_BUDGET:
                break
        raw_dataset = Dataset.from_dict({"text": texts})
        print("[data] Tokenizing dataset...")
        tokenized = raw_dataset.map(tokenize, batched=True, remove_columns=["text"])
        tokenized.set_format(type="torch", columns=["input_ids", "attention_mask"])
        tokenized.save_to_disk(TOKENIZED_PATH)

    loader = DataLoader(tokenized, batch_size=BATCH_SIZE, shuffle=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_amp = device.type == "cuda"

    # ---- Modell ---------------------------------------------------------
    model = GPTMiniMoE(
        vocab_size=tokenizer.vocab_size,
        context_length=BLOCK_SIZE,
        embed_dim=EMBED_DIM,
        n_heads=HEADS,
        n_layers=LAYERS,
        num_experts=NUM_EXPERTS,
        top_k=TOP_K,
    ).to(device)

    n_params = sum(p.numel() for p in model.parameters())
    print(f"[model] GPTMiniMoE: N={NUM_EXPERTS} Experten, top-{TOP_K}, "
          f"~{n_params/1e6:.2f}M Gesamt-Parameter.")
    # Grob: jeder Token nutzt TOP_K/NUM_EXPERTS der Experten-Parameter
    # zuzueglich der Nicht-Expert-Anteile (Attention, Embeddings, Gate).
    print(f"[model] Aktive Experten-Fraktion pro Token: {TOP_K}/{NUM_EXPERTS} = "
          f"{100 * TOP_K / NUM_EXPERTS:.0f}%")

    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    scaler = GradScaler(enabled=use_amp)

    # ---- Trainings-Loop -------------------------------------------------
    print(f"[train] Starte MoE-Training auf {device} "
          f"(load_balance_weight={LB_WEIGHT})...")
    model.train()

    for epoch in range(EPOCHS):
        loop = tqdm(loader, desc=f"Epoch {epoch+1}/{EPOCHS}")
        for batch in loop:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            # Nachwortprognose-Shift wie in TinyGPT
            labels = input_ids.clone()
            labels[:, :-1] = input_ids[:, 1:]
            labels[:, -1]  = -100
            labels[attention_mask == 0] = -100

            optimizer.zero_grad()
            with autocast(enabled=use_amp):
                logits = model(input_ids, attention_mask=attention_mask)
                lm_loss = F.cross_entropy(
                    logits.view(-1, tokenizer.vocab_size),
                    labels.view(-1),
                    ignore_index=-100,
                )
                aux_loss = model.last_aux_loss
                total_loss = lm_loss + LB_WEIGHT * aux_loss

            scaler.scale(total_loss).backward()
            scaler.step(optimizer)
            scaler.update()

            loop.set_postfix(
                lm=float(lm_loss.detach().cpu()),
                aux=float(aux_loss.detach().cpu()),
                total=float(total_loss.detach().cpu()),
            )

    # ---- Checkpoint -----------------------------------------------------
    os.makedirs(args.output_dir, exist_ok=True)
    ckpt_path = os.path.join(args.output_dir, "tinymoe.pt")
    torch.save({"model_state_dict": model.state_dict(), "config": cfg}, ckpt_path)
    print(f"[train] Modell gespeichert unter {ckpt_path}")


if __name__ == "__main__":
    main()