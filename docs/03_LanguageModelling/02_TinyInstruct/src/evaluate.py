"""
evaluate.py - Vorher/Nachher-Vergleich: Base-Modell vs. SFT-Modell

Der zentrale Vergleich dieses Kapitels: derselbe Prompt wird durch dasselbe
Modell geschickt, einmal vor und einmal nach dem SFT-Training. Der
Unterschied ist der ganze Kapitel-Inhalt in einer einzigen Ausgabe.

Aufruf:

    python evaluate.py \
        --base-ckpt   ../checkpoints/tinygpt_base.pt \
        --sft-ckpt    ../checkpoints/tinyinstruct_sft.pt \
        --profile     laptop

Wenn kein Base-Checkpoint angegeben ist, wird nur das SFT-Modell gezeigt
(nuetzlich fuer den Rauchtest). Wenn kein SFT-Checkpoint angegeben ist,
wird nur das Base-Modell gezeigt (der 'reine Vervollstaendiger').
"""

from __future__ import annotations

import argparse
import json
import os
from typing import List, Optional

import torch
from transformers import LlamaTokenizerFast

from data import format_prompt
from model import build_model


DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
TOKENIZER_NAME = "hf-internal-testing/llama-tokenizer"


DEFAULT_PROMPTS = [
    "Was ist die Hauptstadt von Frankreich?",
    "Nenne drei Primzahlen.",
    "Uebersetze 'Guten Morgen' ins Englische.",
    "Erklaere in einem Satz, was ein Transistor ist.",
    "Nenne zwei Planeten unseres Sonnensystems.",
]


def load_config(profile: str, config_path: str) -> dict:
    with open(config_path, "r") as f:
        cfg = json.load(f)
    return cfg[profile]


@torch.no_grad()
def generate_response(
    model,
    tokenizer,
    instruction: str,
    device: torch.device,
    max_new_tokens: int = 80,
    top_k: int = 40,
    temperature: float = 1.0,
) -> str:
    """Erzeugt eine Antwort auf eine Instruktion und gibt nur den
    Response-Anteil zurueck (alles nach '### Response:')."""
    model.eval()
    prompt_text = format_prompt(instruction)
    input_ids = tokenizer.encode(
        prompt_text, return_tensors="pt", add_special_tokens=False
    ).to(device)

    generated = input_ids
    context_length = model.position_embedding.num_embeddings
    for _ in range(max_new_tokens):
        # Kontext-Fenster nicht ueberschreiten
        if generated.size(1) >= context_length:
            break
        logits = model(generated)
        next_logits = logits[:, -1, :] / max(temperature, 1e-8)
        probs = torch.softmax(next_logits, dim=-1)
        top_probs, top_idx = torch.topk(probs, top_k)
        next_token = top_idx[0, torch.multinomial(top_probs[0], 1)]
        generated = torch.cat((generated, next_token.unsqueeze(0)), dim=1)

        # Optional: bei EOS abbrechen
        if next_token.item() == tokenizer.eos_token_id:
            break

    text = tokenizer.decode(generated[0], skip_special_tokens=True)
    marker = "### Response:"
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text.strip()


def load_model_from_checkpoint(
    ckpt_path: Optional[str],
    cfg: dict,
    tokenizer,
    device: torch.device,
):
    """
    Laedt ein GPTMini-Modell aus einem Checkpoint. Falls kein Pfad
    uebergeben ist, wird ein zufaellig initialisiertes Modell
    zurueckgegeben - nur nuetzlich als Kontrast, um zu zeigen, was
    'gar nicht trainiert' aussieht.
    """
    model = build_model(
        vocab_size=tokenizer.vocab_size,
        context_length=cfg["BLOCK_SIZE"],
        embed_dim=cfg["EMBED_DIM"],
        n_heads=cfg["HEADS"],
        n_layers=cfg["LAYERS"],
        checkpoint_path=ckpt_path,
        device=device,
    )
    return model


def print_side_by_side(
    prompts: List[str],
    base_responses: Optional[List[str]],
    sft_responses: Optional[List[str]],
):
    """Rendert eine kompakte Vorher/Nachher-Tabelle in Textform."""
    print("\n" + "=" * 78)
    print("VORHER/NACHHER-VERGLEICH: Base-Modell vs. SFT-Modell")
    print("=" * 78)
    for i, instruction in enumerate(prompts):
        print(f"\n[Prompt #{i+1}]  {instruction}")
        print("-" * 78)
        if base_responses is not None:
            print("Base (TinyGPT):")
            print(f"    {base_responses[i]}")
        if sft_responses is not None:
            print("SFT  (TinyInstruct):")
            print(f"    {sft_responses[i]}")
    print("\n" + "=" * 78)


def main():
    parser = argparse.ArgumentParser(
        description="Vergleicht die Antworten eines Base- und eines "
                    "SFT-Modells auf dieselben Instruktionen.")
    parser.add_argument("--profile", default="laptop",
                        help="Config-Profil (test | laptop | lima).")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--base-ckpt", default=None,
                        help="Pfad zum TinyGPT-Base-Modell (Kap. 3.1). "
                             "Wenn nicht angegeben, wird das Base-Modell "
                             "nur mit zufaelligen Gewichten geladen.")
    parser.add_argument("--sft-ckpt", default=None,
                        help="Pfad zum TinyInstruct-SFT-Modell "
                             "(Ausgabe von train_sft.py).")
    parser.add_argument("--prompts", nargs="*", default=None,
                        help="Eigene Prompts (sonst DEFAULT_PROMPTS).")
    parser.add_argument("--max-new-tokens", type=int, default=80)
    parser.add_argument("--seed", type=int, default=None,
                        help="Seed fuer reproduzierbare Generierung "
                             "(bei Top-k-Sampling nicht vollstaendig "
                             "deterministisch, aber ausreichend fuer "
                             "einen fairen Vorher/Nachher-Vergleich).")
    args = parser.parse_args()

    if args.base_ckpt is None and args.sft_ckpt is None:
        parser.error(
            "Mindestens einer von --base-ckpt oder --sft-ckpt muss "
            "angegeben sein - sonst gibt es nichts zu vergleichen.")

    cfg = load_config(args.profile, args.config)
    prompts = args.prompts if args.prompts else DEFAULT_PROMPTS

    if args.seed is not None:
        torch.manual_seed(args.seed)

    tokenizer = LlamaTokenizerFast.from_pretrained(TOKENIZER_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    base_responses = None
    if args.base_ckpt is not None:
        print(f"[eval] Lade Base-Modell aus {args.base_ckpt}")
        base_model = load_model_from_checkpoint(args.base_ckpt, cfg, tokenizer, device)
        base_responses = [
            generate_response(base_model, tokenizer, p, device, args.max_new_tokens)
            for p in prompts
        ]
        del base_model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    sft_responses = None
    if args.sft_ckpt is not None:
        print(f"[eval] Lade SFT-Modell aus {args.sft_ckpt}")
        sft_model = load_model_from_checkpoint(args.sft_ckpt, cfg, tokenizer, device)
        sft_responses = [
            generate_response(sft_model, tokenizer, p, device, args.max_new_tokens)
            for p in prompts
        ]

    print_side_by_side(prompts, base_responses, sft_responses)


if __name__ == "__main__":
    main()