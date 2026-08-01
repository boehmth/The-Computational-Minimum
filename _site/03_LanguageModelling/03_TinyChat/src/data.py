"""
data.py - Praeferenzdatensatz fuer DPO (Kap. 3.3, TinyChat)

Kern-Idee dieses Kapitels: statt einem Beispiel (Instruction, Response)
haben wir jetzt ein *Tripel*

    (prompt, chosen, rejected)

- `prompt`   = die Instruktion (identisches Format wie in Kap. 3.2!)
- `chosen`   = die bevorzugte Antwort
- `rejected` = die abgelehnte Antwort

Der DPO-Loss (siehe `train_dpo.py`) wird gleichzeitig auf `chosen` und
`rejected` ausgewertet und "schiebt" die Modell-Wahrscheinlichkeiten so,
dass die bevorzugte Antwort haeufiger wird und die abgelehnte seltener -
alles relativ zu einem eingefrorenen Referenzmodell (dem SFT-Modell aus
Kap. 3.2).

Das Format der einzelnen Antworten bleibt identisch zu 3.2: derselbe
`### Instruction: ... ### Response: ...`-Rahmen, dieselbe maskierte
Loss-Logik. Der Unterschied sitzt in `train_dpo.py`, nicht hier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import torch
from torch.utils.data import Dataset

# Wir nutzen bewusst *dieselben* Format- und Maskierungs-Funktionen wie in
# Kap. 3.2. Wenn du das Instruction-Format aenderst, muessen 3.2 und 3.3
# gemeinsam angepasst werden - sonst passt der DPO-Anker (SFT-Modell) nicht
# mehr zur DPO-Eingabe.
import os
import sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_TINYINSTRUCT_SRC = os.path.normpath(os.path.join(_HERE, "..", "..", "02_TinyInstruct", "src"))
if _TINYINSTRUCT_SRC not in sys.path:
    sys.path.insert(0, _TINYINSTRUCT_SRC)

from data import (  # noqa: E402  (Import nach sys.path-Aenderung)
    IGNORE_INDEX,
    format_prompt,
    format_full,
    mask_prompt_labels,
)


# -------------------------------------------------------------------------
# 1. Praeferenzdatensatz laden
# -------------------------------------------------------------------------

def load_preference_samples(n_samples: int) -> List[Dict[str, str]]:
    """
    Laedt Praeferenz-Tripel im Format {prompt, chosen, rejected}.

    Bevorzugt `Anthropic/hh-rlhf` (menschliche Praeferenzen).
    Fallback: eingebauter Mini-Datensatz.
    """
    try:
        from datasets import load_dataset

        # hh-rlhf hat das Format {'chosen': "...", 'rejected': "..."} mit
        # bereits eingebettetem Prompt. Wir muessen den Prompt aus dem
        # gemeinsamen Praefix extrahieren und in unser Instruct-Format
        # bringen.
        ds = load_dataset("Anthropic/hh-rlhf", split="train")
        samples: List[Dict[str, str]] = []
        for row in ds:
            chosen_text = row["chosen"]
            rejected_text = row["rejected"]

            prompt, chosen, rejected = _split_hh_rlhf_row(chosen_text, rejected_text)
            if prompt is None:
                continue  # ungeeignetes Beispiel (Multi-Turn etc.) - ueberspringen
            samples.append({
                "prompt":   prompt,
                "chosen":   chosen,
                "rejected": rejected,
            })
            if len(samples) >= n_samples:
                break

        if len(samples) < n_samples:
            print(f"[data] Warnung: nur {len(samples)} verwertbare HH-RLHF-"
                  f"Beispiele gefunden (angefordert: {n_samples}).")
        return samples

    except Exception as err:
        print(f"[data] Konnte HH-RLHF nicht laden ({err}); "
              f"nutze eingebauten Mini-Datensatz.")
        return _fallback_samples()[:n_samples]


def _split_hh_rlhf_row(chosen_text: str, rejected_text: str):
    """
    HH-RLHF-Rows sehen so aus:

        "\n\nHuman: <prompt>\n\nAssistant: <antwort>"

    Fuer die didaktische Klarheit halten wir uns auf Single-Turn-Beispiele
    (genau ein "Human:" und ein "Assistant:") und lassen den Rest weg.
    """
    def _parse_single_turn(text: str):
        # Erwartetes Muster: irgendwas + "Human: X" + "Assistant: Y".
        marker_h = "Human:"
        marker_a = "Assistant:"
        if marker_h not in text or marker_a not in text:
            return None, None
        if text.count(marker_h) != 1 or text.count(marker_a) != 1:
            return None, None
        prompt = text.split(marker_h, 1)[1].split(marker_a, 1)[0].strip()
        response = text.split(marker_a, 1)[1].strip()
        if not prompt or not response:
            return None, None
        return prompt, response

    p_c, r_c = _parse_single_turn(chosen_text)
    p_r, r_r = _parse_single_turn(rejected_text)
    if p_c is None or p_r is None:
        return None, None, None
    # HH-RLHF: der Prompt ist in chosen und rejected identisch (per Design)
    if p_c != p_r:
        return None, None, None
    return p_c, r_c, r_r


def _fallback_samples() -> List[Dict[str, str]]:
    """
    Winziger, didaktisch konstruierter Datensatz. Jede "chosen"-Antwort
    ist offensichtlich besser als die "rejected"-Antwort in einer klar
    benennbaren Dimension (Vollstaendigkeit, Struktur, Hoeflichkeit).
    """
    return [
        {
            "prompt":   "Erklaere in ein bis zwei Saetzen, wie eine CPU funktioniert.",
            "chosen":   "Eine CPU liest Instruktionen aus dem Speicher, dekodiert sie "
                        "und fuehrt sie mit Hilfe ihrer arithmetisch-logischen Einheit aus.",
            "rejected": "Sie rechnet halt.",
        },
        {
            "prompt":   "Uebersetze 'Guten Morgen' ins Englische.",
            "chosen":   "Good morning.",
            "rejected": "Vermutlich 'good morning', aber ich bin mir nicht sicher.",
        },
        {
            "prompt":   "Nenne zwei Vorteile erneuerbarer Energien.",
            "chosen":   "1) Sie verursachen kaum CO2-Emissionen im Betrieb. "
                        "2) Ihre Brennstoffe (Wind, Sonne) sind kostenlos verfuegbar.",
            "rejected": "Sie sind gut fuer die Umwelt, so ungefaehr.",
        },
        {
            "prompt":   "Was ist die Hauptstadt von Frankreich?",
            "chosen":   "Die Hauptstadt von Frankreich ist Paris.",
            "rejected": "Frankreich hat auf jeden Fall eine Hauptstadt.",
        },
        {
            "prompt":   "Nenne drei Primzahlen.",
            "chosen":   "Drei Primzahlen sind 2, 3 und 5.",
            "rejected": "Zum Beispiel 4, 6 und 8.",
        },
    ] * 40


# -------------------------------------------------------------------------
# 2. Tokenisierung eines Praeferenz-Tripels
# -------------------------------------------------------------------------

@dataclass
class PreferenceExample:
    """Ein tokenisiertes Praeferenz-Tripel fuer DPO.

    Attribute:
        chosen_ids, chosen_labels, chosen_mask      -- Tokens der chosen-Antwort
        rejected_ids, rejected_labels, rejected_mask -- Tokens der rejected-Antwort

    Die Labels haben IGNORE_INDEX im Prompt-Teil (wie in 3.2). Die
    DPO-Log-Wahrscheinlichkeit wird spaeter nur ueber die
    Nicht-IGNORE-Positionen aggregiert -> vergleichbare Werte fuer
    chosen und rejected.
    """
    chosen_ids: torch.Tensor
    chosen_labels: torch.Tensor
    chosen_mask: torch.Tensor
    rejected_ids: torch.Tensor
    rejected_labels: torch.Tensor
    rejected_mask: torch.Tensor


class PreferenceDataset(Dataset):
    """
    Baut aus (prompt, chosen, rejected)-Tripeln Trainings-Tripel mit
    maskierten Labels. Padded auf feste Laenge (`block_size`).
    """

    def __init__(
        self,
        samples: List[Dict[str, str]],
        tokenize_fn: Callable[[str], List[int]],
        pad_token_id: int,
        block_size: int,
        eos_token_id: Optional[int] = None,
    ):
        self.pad_token_id = pad_token_id
        self.block_size = block_size

        self.examples: List[PreferenceExample] = []
        for s in samples:
            ex = self._build_example(
                prompt=s["prompt"],
                chosen=s["chosen"],
                rejected=s["rejected"],
                tokenize_fn=tokenize_fn,
                eos_token_id=eos_token_id,
            )
            if ex is not None:
                self.examples.append(ex)

        print(f"[data] {len(self.examples)} Praeferenz-Tripel geladen "
              f"(block_size={block_size}).")

    def _pack_one_side(
        self,
        prompt: str,
        response: str,
        tokenize_fn: Callable[[str], List[int]],
        eos_token_id: Optional[int],
    ):
        """
        Tokenisiert (prompt, response), setzt Labels mit IGNORE_INDEX im
        Prompt-Teil und paddet auf block_size. Gibt (input_ids, labels,
        attention_mask) als drei Long-Tensoren zurueck, oder None wenn
        das Beispiel nicht passt (z. B. zu lang oder Praefix-Mismatch).
        """
        prompt_text = format_prompt(prompt)
        full_text = format_full(prompt, response)

        prompt_ids = tokenize_fn(prompt_text)
        full_ids = tokenize_fn(full_text)

        if full_ids[: len(prompt_ids)] != prompt_ids:
            return None
        if len(full_ids) > self.block_size:
            return None

        labels = mask_prompt_labels(prompt_ids, full_ids, eos_token_id)

        pad_len = self.block_size - len(full_ids)
        input_ids = full_ids + [self.pad_token_id] * pad_len
        attention_mask = [1] * len(full_ids) + [0] * pad_len
        labels = labels + [IGNORE_INDEX] * pad_len

        return (
            torch.tensor(input_ids, dtype=torch.long),
            torch.tensor(labels, dtype=torch.long),
            torch.tensor(attention_mask, dtype=torch.long),
        )

    def _build_example(
        self,
        prompt: str,
        chosen: str,
        rejected: str,
        tokenize_fn: Callable[[str], List[int]],
        eos_token_id: Optional[int],
    ) -> Optional[PreferenceExample]:
        c = self._pack_one_side(prompt, chosen, tokenize_fn, eos_token_id)
        r = self._pack_one_side(prompt, rejected, tokenize_fn, eos_token_id)
        if c is None or r is None:
            return None
        c_ids, c_labels, c_mask = c
        r_ids, r_labels, r_mask = r
        return PreferenceExample(
            chosen_ids=c_ids,
            chosen_labels=c_labels,
            chosen_mask=c_mask,
            rejected_ids=r_ids,
            rejected_labels=r_labels,
            rejected_mask=r_mask,
        )

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        e = self.examples[idx]
        return {
            "chosen_ids":      e.chosen_ids,
            "chosen_labels":   e.chosen_labels,
            "chosen_mask":     e.chosen_mask,
            "rejected_ids":    e.rejected_ids,
            "rejected_labels": e.rejected_labels,
            "rejected_mask":   e.rejected_mask,
        }
