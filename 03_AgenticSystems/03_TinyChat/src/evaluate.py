"""
evaluate.py - Vorher/Nachher-Vergleich SFT-Modell (Kap. 3.2) vs. DPO-Modell (Kap. 3.3)

Der Vergleich hier hat einen anderen Charakter als in 3.2:

    In 3.2 ging es um FAEHIGKEIT: "beantwortet das Modell die Frage
    ueberhaupt?" - der SFT-Sprung ist meist offensichtlich.

    In 3.3 geht es um QUALITAET: beide Modelle antworten schon zielgerichtet.
    Der Unterschied ist subtiler - die DPO-Antwort ist typischerweise
    strukturierter, hoeflicher, vollstaendiger oder vorsichtiger.

Deshalb sind die Prompts hier bewusst so gewaehlt, dass es MEHRERE plausible
Antworten gibt und die "gute" davon eine erkennbare Qualitaetsdimension hat.

Aufruf:

    python evaluate.py \
        --sft-ckpt ../../02_TinyInstruct/checkpoints/tinyinstruct_sft.pt \
        --dpo-ckpt ../checkpoints/tinychat_dpo.pt \
        --profile  laptop
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Optional

import torch
from transformers import LlamaTokenizerFast

# Aus Kap. 3.2 die format_prompt- und build_model-Funktionen wiederverwenden
_HERE = os.path.dirname(os.path.abspath(__file__))
_TINYINSTRUCT_SRC = os.path.normpath(os.path.join(_HERE, "..", "..", "02_TinyInstruct", "src"))
if _TINYINSTRUCT_SRC not in sys.path:
    sys.path.insert(0, _TINYINSTRUCT_SRC)
from data import format_prompt  # noqa: E402
from model import build_model  # noqa: E402


DEFAULT_CONFIG_PATH = os.path.join(_HERE, "config.json")
TOKENIZER_NAME = "hf-internal-testing/llama-tokenizer"


# Prompts, bei denen die DPO-Politur idealerweise sichtbar wird:
# es gibt mehrere plausible Antworten, und die "bessere" ist strukturierter
# oder vorsichtiger.
DEFAULT_PROMPTS = [
    "Erklaere mir kurz, wie eine CPU funktioniert.",
    "Nenne zwei Vorteile erneuerbarer Energien.",
    "Uebersetze 'Guten Morgen' ins Englische.",
    "Was ist die Hauptstadt von Frankreich?",
    "Wie berechne ich den Flaecheninhalt eines Rechtecks?",
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
) -> str:
    model.eval()
    prompt_text = format_prompt(instruction)
    input_ids = tokenizer.encode(
        prompt_text, return_tensors="pt", add_special_tokens=False
    ).to(device)

    generated = input_ids
    context_length = model.position_embedding.num_embeddings
    for _ in range(max_new_tokens):
        if generated.size(1) >= context_length:
            break
        logits = model(generated)
        next_logits = logits[:, -1, :]
        probs = torch.softmax(next_logits, dim=-1)
        top_probs, top_idx = torch.topk(probs, top_k)
        next_token = top_idx[0, torch.multinomial(top_probs[0], 1)]
        generated = torch.cat((generated, next_token.unsqueeze(0)), dim=1)
        if next_token.item() == tokenizer.eos_token_id:
            break

    text = tokenizer.decode(generated[0], skip_special_tokens=True)
    marker = "### Response:"
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text.strip()


def load_model_from_checkpoint(ckpt_path, cfg, tokenizer, device):
    return build_model(
        vocab_size=tokenizer.vocab_size,
        context_length=cfg["BLOCK_SIZE"],
        embed_dim=cfg["EMBED_DIM"],
        n_heads=cfg["HEADS"],
        n_layers=cfg["LAYERS"],
        checkpoint_path=ckpt_path,
        device=device,
    )


def print_side_by_side(prompts, sft_responses, dpo_responses):
    print("\n" + "=" * 78)
    print("VORHER/NACHHER-VERGLEICH: SFT-Modell (3.2) vs. DPO-Modell (3.3)")
    print("=" * 78)
    for i, instruction in enumerate(prompts):
        print(f"\n[Prompt #{i+1}]  {instruction}")
        print("-" * 78)
        if sft_responses is not None:
            print("SFT (TinyInstruct, 3.2):")
            print(f"    {sft_responses[i]}")
        if dpo_responses is not None:
            print("DPO (TinyChat,     3.3):")
            print(f"    {dpo_responses[i]}")
    print("\n" + "=" * 78)


def main():
    parser = argparse.ArgumentParser(
        description="Vergleicht SFT-Modell und DPO-Modell auf denselben Prompts.")
    parser.add_argument("--profile", default="laptop")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--sft-ckpt", default=None,
                        help="Pfad zum SFT-Modell aus Kap. 3.2.")
    parser.add_argument("--dpo-ckpt", default=None,
                        help="Pfad zum DPO-Modell aus diesem Kapitel.")
    parser.add_argument("--prompts", nargs="*", default=None)
    parser.add_argument("--max-new-tokens", type=int, default=80)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    if args.sft_ckpt is None and args.dpo_ckpt is None:
        parser.error("Mindestens einer von --sft-ckpt oder --dpo-ckpt muss angegeben sein.")

    cfg = load_config(args.profile, args.config)
    prompts = args.prompts if args.prompts else DEFAULT_PROMPTS

    if args.seed is not None:
        torch.manual_seed(args.seed)

    tokenizer = LlamaTokenizerFast.from_pretrained(TOKENIZER_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    sft_responses = None
    if args.sft_ckpt is not None:
        print(f"[eval] Lade SFT-Modell aus {args.sft_ckpt}")
        m = load_model_from_checkpoint(args.sft_ckpt, cfg, tokenizer, device)
        sft_responses = [
            generate_response(m, tokenizer, p, device, args.max_new_tokens)
            for p in prompts
        ]
        del m
        if device.type == "cuda":
            torch.cuda.empty_cache()

    dpo_responses = None
    if args.dpo_ckpt is not None:
        print(f"[eval] Lade DPO-Modell aus {args.dpo_ckpt}")
        m = load_model_from_checkpoint(args.dpo_ckpt, cfg, tokenizer, device)
        dpo_responses = [
            generate_response(m, tokenizer, p, device, args.max_new_tokens)
            for p in prompts
        ]

    print_side_by_side(prompts, sft_responses, dpo_responses)


if __name__ == "__main__":
    main()