"""
train_gpt_mini.py — Kapitel 3.1 "LLM-Grundlagen" (03_AgenticSystems)

Bewusster Philosophie-Bruch gegenueber Teil 1 und Teil 2:
Die Reihe verzichtet dort konsequent auf Frameworks, um jede Multiplikation
und jedes Bit sichtbar zu machen. Ab Teil 3 verlassen wir diese Von-Grund-auf-
Philosophie bewusst: Attention-Kernel, Mixed-Precision-Training und
Tokenizer/Datenpipelines auf Web-Scale-Daten von Hand nachzubauen waere an
diesem Punkt keine Lehrsubstanz mehr, sondern nur noch Infrastrukturarbeit.
Was zaehlt, ist ab hier das Verstehen der Architektur- und Trainings-
Entscheidungen — nicht mehr jede Zeile Low-Level-Code. Dieser Hinweis gehoert
so (oder aehnlich) an den Anfang des Kapitel-READMEs.

Aenderungen gegenueber der ersten Fassung:
  1. Tote Code-Stelle entfernt: `labels` wurden in tokenize() UND im Trainings-
     Loop gesetzt, der Wert aus tokenize() wurde nie benutzt.
  2. Padding wird jetzt tatsaechlich maskiert: sowohl in der Attention
     (key_padding_mask) als auch im Loss (Label auf -100 an Pad-Positionen).
     Vorher hat das Modell auf Pad-Tokens "vollwertig" trainiert.
  3. Config-Pfad ist relativ zum Skript und per --config ueberschreibbar,
     statt hart auf einen einzelnen Windows-Pfad zu zeigen.
"""

import os
import json
import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.cuda.amp import autocast, GradScaler
from transformers import LlamaTokenizerFast
from datasets import load_dataset, load_from_disk, Dataset
from tqdm import tqdm
from multiprocessing import freeze_support

# -----------------------------
# Config Loader
# -----------------------------

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config(profile, config_path):
    with open(config_path, "r") as f:
        cfg = json.load(f)
    return cfg[profile]


# -----------------------------
# Model Definition
# -----------------------------

class DecoderBlock(nn.Module):
    def __init__(self, embed_dim, n_heads):
        super().__init__()
        self.attn = nn.MultiheadAttention(embed_dim, n_heads, batch_first=True)
        self.ln1 = nn.LayerNorm(embed_dim)
        self.ff = nn.Sequential(
            nn.Linear(embed_dim, 4 * embed_dim),
            nn.ReLU(),
            nn.Linear(4 * embed_dim, embed_dim)
        )
        self.ln2 = nn.LayerNorm(embed_dim)

    def forward(self, x, key_padding_mask=None):
        T = x.size(1)
        causal_mask = torch.triu(torch.ones(T, T, device=x.device) * float('-inf'), 1)
        # key_padding_mask: True = Position ist Padding und wird von der
        # Attention komplett ignoriert (weder als Query- noch als Key-Ziel
        # relevant fuer echte Tokens).
        attn_out, _ = self.attn(
            x, x, x,
            attn_mask=causal_mask,
            key_padding_mask=key_padding_mask
        )
        x = self.ln1(x + attn_out)
        x = self.ln2(x + self.ff(x))
        return x


class GPTMini(nn.Module):
    def __init__(self, vocab_size, context_length, embed_dim, n_heads, n_layers):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        self.position_embedding = nn.Embedding(context_length, embed_dim)
        self.blocks = nn.ModuleList([DecoderBlock(embed_dim, n_heads) for _ in range(n_layers)])
        self.ln_final = nn.LayerNorm(embed_dim)
        self.output_head = nn.Linear(embed_dim, vocab_size)

    def forward(self, x, attention_mask=None):
        B, T = x.size()
        tok = self.token_embedding(x)
        pos = self.position_embedding(torch.arange(T, device=x.device).unsqueeze(0))
        x = tok + pos

        key_padding_mask = None
        if attention_mask is not None:
            # HF-Konvention: 1 = echtes Token, 0 = Padding.
            # PyTorchs MultiheadAttention erwartet das Gegenteil: True = ignorieren.
            key_padding_mask = attention_mask == 0

        for block in self.blocks:
            x = block(x, key_padding_mask=key_padding_mask)
        x = self.ln_final(x)
        return self.output_head(x)


# -----------------------------
# Text Generation
# -----------------------------

def generate_text(model, tokenizer, prompt, device, max_new_tokens=50, top_k=50):
    model.eval()
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    generated = input_ids

    for _ in range(max_new_tokens):
        with torch.no_grad():
            # Bei der Generierung gibt es kein Padding -> attention_mask=None ist korrekt.
            logits = model(generated)
            next_token_logits = logits[:, -1, :]
            probs = torch.softmax(next_token_logits, dim=-1)
            top_k_probs, top_k_indices = torch.topk(probs, top_k)
            next_token = top_k_indices[0, torch.multinomial(top_k_probs[0], 1)]
            generated = torch.cat((generated, next_token.unsqueeze(0)), dim=1)

    return tokenizer.decode(generated[0], skip_special_tokens=True)


# -----------------------------
# Main
# -----------------------------

def main():
    freeze_support()

    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="laptop")
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="Pfad zur config.json (Default: config.json neben diesem Skript)"
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "checkpoints"),
        help="Zielordner fuer den Base-Modell-Checkpoint. Kapitel 3.2 (TinyInstruct) "
             "und 3.3 (TinyChat) erwarten den dortigen State-Dict als BASE_MODEL_CKPT."
    )
    args = parser.parse_args()

    cfg = load_config(args.profile, args.config)

    TOKEN_BUDGET = cfg["TOKEN_BUDGET"]
    BLOCK_SIZE   = cfg["BLOCK_SIZE"]
    BATCH_SIZE   = cfg["BATCH_SIZE"]
    EPOCHS       = cfg["EPOCHS"]
    EMBED_DIM    = cfg["EMBED_DIM"]
    HEADS        = cfg["HEADS"]
    LAYERS       = cfg["LAYERS"]
    LEARNING_RATE = cfg["LEARNING_RATE"]

    DATASET_NAME = "HuggingFaceFW/fineweb-edu"
    TOKENIZED_PATH = f"tokenized_{args.profile}"

    tokenizer = LlamaTokenizerFast.from_pretrained("hf-internal-testing/llama-tokenizer")
    tokenizer.pad_token = tokenizer.eos_token

    def tokenize(example):
        # Hinweis: labels werden bewusst NICHT hier gesetzt, sondern erst im
        # Trainings-Loop, wo sie zusammen mit der Padding-Maske korrekt
        # geshiftet und maskiert werden koennen (siehe unten).
        return tokenizer(
            example["text"],
            truncation=True,
            padding="max_length",
            max_length=BLOCK_SIZE
        )

    print(f"Loading FineWeb-Edu (profile={args.profile}, token budget={TOKEN_BUDGET:,})...")
    streamed_ds = load_dataset(DATASET_NAME, split="train", streaming=True)

    texts, token_sum = [], 0
    for row in streamed_ds:
        texts.append(row["text"])
        token_sum += row["token_count"]
        if token_sum >= TOKEN_BUDGET:
            break

    if os.path.exists(TOKENIZED_PATH):
        print("Found tokenized dataset - loading from disk.")
        tokenized = load_from_disk(TOKENIZED_PATH)
    else:
        raw_dataset = Dataset.from_dict({"text": texts})
        print("Tokenizing dataset...")
        tokenized = raw_dataset.map(tokenize, batched=True, remove_columns=["text"])
        tokenized.set_format(type="torch", columns=["input_ids", "attention_mask"])
        tokenized.save_to_disk(TOKENIZED_PATH)

    loader = DataLoader(tokenized, batch_size=BATCH_SIZE, shuffle=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_amp = device.type == "cuda"

    model = GPTMini(
        vocab_size=tokenizer.vocab_size,
        context_length=BLOCK_SIZE,
        embed_dim=EMBED_DIM,
        n_heads=HEADS,
        n_layers=LAYERS
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    scaler = GradScaler(enabled=use_amp)

    print("Starting training...")
    model.train()

    for epoch in range(EPOCHS):
        loop = tqdm(loader, desc=f"Epoch {epoch+1}")

        for batch in loop:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            # Naechstes-Token-Vorhersage: labels sind input_ids um 1 verschoben.
            labels = input_ids.clone()
            labels[:, :-1] = input_ids[:, 1:]
            labels[:, -1] = -100

            # Positionen, die von Anfang an Padding waren, tragen keine
            # Lernsignal-Information -> aus dem Loss ausschliessen.
            labels[attention_mask == 0] = -100

            optimizer.zero_grad()

            with autocast(enabled=use_amp):
                logits = model(input_ids, attention_mask=attention_mask).view(-1, tokenizer.vocab_size)
                targets = labels.view(-1)
                loss = F.cross_entropy(logits, targets, ignore_index=-100)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            loop.set_postfix(loss=loss.item())

    # ---- Checkpoint speichern ------------------------------------------
    # Wir speichern den State-Dict in einem Format, das Kapitel 3.2
    # (`02_TinyInstruct/src/model.py`, Funktion `build_model`) direkt laden
    # kann: entweder als reines state_dict oder mit dem Schluessel
    # "model_state_dict" - beides wird akzeptiert. Wir waehlen die dict-
    # Variante, damit spaeter auch Trainings-Metadaten mit hinein passen.
    os.makedirs(args.output_dir, exist_ok=True)
    ckpt_path = os.path.join(args.output_dir, "tinygpt_base.pt")
    torch.save({
        "model_state_dict": model.state_dict(),
        "config": cfg,
    }, ckpt_path)
    print(f"\nBase-Modell gespeichert unter {ckpt_path}")
    print("  -> In Kapitel 3.2 (TinyInstruct) und 3.5 (TinyReason) diesen "
          "Pfad als BASE_MODEL_CKPT bzw. SFT_MODEL_CKPT in der config.json "
          "eintragen.")

    print("\nSample generation:")
    print(generate_text(model, tokenizer, "and so she went on", device))


if __name__ == "__main__":
    main()