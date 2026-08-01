"""
data.py - Instruktions-Datensatz mit maskiertem SFT-Loss

DIDAKTISCHE POINTE DIESES KAPITELS
==================================

Der gesamte Unterschied zwischen einem "Text-Vervollstaendiger" (TinyGPT
aus 3.1) und einem "Instruction-Follower" (TinyInstruct, dieses Kapitel)
sitzt in EINER Idee, die weiter unten in `mask_prompt_labels()` in einer
einzigen Zeile umgesetzt wird:

    labels[:len(prompt_ids)] = IGNORE_INDEX  # -100

Das heisst: der Cross-Entropy-Loss ignoriert alle Tokens, die zum
Prompt/Instruction-Teil gehoeren. Er berechnet Gradienten nur fuer den
Response-Teil. Aus der Perspektive des Modells wird der Prompt dadurch
zu einem reinen Kontext, den es LESEN aber nicht VERVOLLSTAENDIGEN muss.
Was es zu vervollstaendigen lernt, ist ausschliesslich die Antwort.

Alles andere in dieser Datei (Datensatz-Laden, Format-Assemblierung,
Tokenisierung, Padding) ist Infrastruktur. Die didaktische Pointe steckt
in genau der Zeile oben.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import torch
from torch.utils.data import Dataset


IGNORE_INDEX = -100  # PyTorch-Konvention: Positionen mit diesem Label
                    # werden von F.cross_entropy(...) im Loss uebergangen.

PROMPT_TEMPLATE = (
    "### Instruction:\n"
    "{instruction}\n\n"
    "### Response:\n"
)
RESPONSE_SUFFIX = "\n"  # trennt Response vom (eventuell folgenden) EOS/Padding


# -------------------------------------------------------------------------
# 1. Datensatz laden
# -------------------------------------------------------------------------

def load_instruction_samples(n_samples: int) -> List[Dict[str, str]]:
    """
    Laedt eine kleine Menge Instruction/Response-Paare.

    Bevorzugt wird `tatsu-lab/alpaca` (52k Beispiele, per GPT-3.5 generiert),
    weil er ohne Login zugreifbar ist und ein sauberes Format hat.

    Fallback: ein winziger, eingebauter Beispiel-Datensatz, damit das
    Skript auch offline lauffaehig bleibt (nuetzlich fuer den Rauchtest
    und den Ehrgeiz "laeuft ohne Netzverbindung").
    """
    try:
        from datasets import load_dataset

        ds = load_dataset("tatsu-lab/alpaca", split="train")
        # Wir filtern das Feld `input` raus, das bei Alpaca oft mit einem
        # zusaetzlichen Kontext gefuellt ist, aber fuer die didaktische
        # Klarheit dieses Kapitels stoerend waere. Wir wollen reines
        # Instruction -> Response.
        samples: List[Dict[str, str]] = []
        for row in ds:
            if row.get("input"):
                continue  # ueberspringen, wir wollen nur Instr./Resp.-Paare
            samples.append({
                "instruction": row["instruction"].strip(),
                "response":    row["output"].strip(),
            })
            if len(samples) >= n_samples:
                break
        if len(samples) < n_samples:
            print(
                f"[data] Warnung: nur {len(samples)} passende Alpaca-Beispiele "
                f"gefunden (angefordert: {n_samples}). Trainiere mit weniger."
            )
        return samples

    except Exception as err:
        print(f"[data] Konnte Alpaca nicht laden ({err}); nutze eingebauten Mini-Datensatz.")
        return _fallback_samples()[:n_samples]


def _fallback_samples() -> List[Dict[str, str]]:
    """
    Eingebauter, sehr kleiner Instruction-Datensatz - reicht fuer einen
    Rauchtest, dass der Trainings-Loop laeuft. Dass er inhaltlich zu
    duenn ist, um wirklich Instruction-Following zu induzieren, ist
    Absicht (und Teil von Uebung 1 im README).
    """
    return [
        {"instruction": "Was ist die Hauptstadt von Frankreich?",
         "response":    "Die Hauptstadt von Frankreich ist Paris."},
        {"instruction": "Nenne drei Primzahlen.",
         "response":    "Drei Primzahlen sind 2, 3 und 5."},
        {"instruction": "Uebersetze 'Guten Morgen' ins Englische.",
         "response":    "Good morning."},
        {"instruction": "Erklaere in einem Satz, was ein Transistor ist.",
         "response":    "Ein Transistor ist ein Halbleiterbauelement, "
                        "das elektrische Signale verstaerken oder schalten kann."},
        {"instruction": "Nenne zwei Planeten unseres Sonnensystems.",
         "response":    "Zwei Planeten sind Erde und Mars."},
    ] * 40  # x 40, damit ein Trainings-Loop nicht mit N=5 sofort endet


# -------------------------------------------------------------------------
# 2. Format-Assemblierung und Tokenisierung
# -------------------------------------------------------------------------

def format_prompt(instruction: str) -> str:
    """Baut den Prompt-Teil (alles bis einschliesslich '### Response:\n')."""
    return PROMPT_TEMPLATE.format(instruction=instruction.strip())


def format_full(instruction: str, response: str) -> str:
    """Baut den vollstaendigen Trainingstext: Prompt + Response + Suffix."""
    return format_prompt(instruction) + response.strip() + RESPONSE_SUFFIX


def mask_prompt_labels(
    prompt_ids: List[int],
    full_ids: List[int],
    eos_token_id: Optional[int],
) -> List[int]:
    """
    *** DIE ZENTRALE FUNKTION DIESES KAPITELS ***

    Erstellt die Label-Sequenz fuer den SFT-Loss:
      - Positionen im Prompt-Teil -> IGNORE_INDEX (kein Lernsignal)
      - Positionen im Response-Teil -> die tatsaechliche Token-ID (Lernsignal)
      - optional: EOS am Ende als zusaetzliches Response-Token

    Das ist die eine Idee, die den Sprung "Sprachmodell -> Instruction-
    Follower" ausmacht. Im Vergleich zur reinen Nachwortprognose in TinyGPT
    (labels = input_ids, shift +1) haben wir hier eine zusaetzliche Maskierung:
    nur der Response-Bereich zaehlt.
    """
    labels = list(full_ids)                     # zunaechst 1:1 die Eingabe
    labels[: len(prompt_ids)] = [IGNORE_INDEX] * len(prompt_ids)  # <<< die eine Zeile
    if eos_token_id is not None and full_ids and full_ids[-1] != eos_token_id:
        # Optional: haenge EOS ans Label an, damit das Modell lernt, die
        # Antwort auch aktiv zu BEENDEN, nicht nur zu generieren.
        pass  # bewusst weggelassen, damit die "eine Zeile" die eine Zeile bleibt.
    return labels


# -------------------------------------------------------------------------
# 3. Dataset-Klasse fuer den Trainings-Loop
# -------------------------------------------------------------------------

@dataclass
class InstructionExample:
    input_ids: torch.Tensor       # (T,) LongTensor
    attention_mask: torch.Tensor  # (T,) LongTensor {0,1}
    labels: torch.Tensor          # (T,) LongTensor mit IGNORE_INDEX im Prompt-Teil


class InstructionDataset(Dataset):
    """
    Baut aus (instruction, response)-Paaren Trainingsbeispiele mit
    maskierten Labels. Padded auf feste Laenge (`block_size`), damit ein
    naiver DataLoader ohne Custom-Collator funktioniert.
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

        self.examples: List[InstructionExample] = []
        for s in samples:
            example = self._build_example(
                instruction=s["instruction"],
                response=s["response"],
                tokenize_fn=tokenize_fn,
                eos_token_id=eos_token_id,
            )
            if example is not None:
                self.examples.append(example)

        print(f"[data] {len(self.examples)} Trainingsbeispiele "
              f"(block_size={block_size}, verwendet: {len(samples)} Rohbeispiele).")

    def _build_example(
        self,
        instruction: str,
        response: str,
        tokenize_fn: Callable[[str], List[int]],
        eos_token_id: Optional[int],
    ) -> Optional[InstructionExample]:
        prompt_text = format_prompt(instruction)
        full_text = format_full(instruction, response)

        prompt_ids = tokenize_fn(prompt_text)
        full_ids   = tokenize_fn(full_text)

        # Sanity: der Prompt muss ein Praefix des vollen Texts sein.
        # Sollte der Tokenizer BOS o.ae. anders behandeln, fallen wir
        # sanft zurueck (verwerfen dieses Beispiel), statt falsch zu labeln.
        if full_ids[: len(prompt_ids)] != prompt_ids:
            return None

        if len(full_ids) > self.block_size:
            return None  # zu lang - weglassen, statt die Response abzuschneiden

        labels = mask_prompt_labels(prompt_ids, full_ids, eos_token_id)

        # Auf block_size padden
        pad_len = self.block_size - len(full_ids)
        input_ids = full_ids + [self.pad_token_id] * pad_len
        attention_mask = [1] * len(full_ids) + [0] * pad_len
        labels = labels + [IGNORE_INDEX] * pad_len  # Padding zaehlt auch nicht

        return InstructionExample(
            input_ids=torch.tensor(input_ids, dtype=torch.long),
            attention_mask=torch.tensor(attention_mask, dtype=torch.long),
            labels=torch.tensor(labels, dtype=torch.long),
        )

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        e = self.examples[idx]
        return {
            "input_ids":      e.input_ids,
            "attention_mask": e.attention_mask,
            "labels":         e.labels,
        }


# -------------------------------------------------------------------------
# 4. Debugging-Hilfe (menschlich lesbar zeigen, was maskiert wird)
# -------------------------------------------------------------------------

def debug_show_masking(
    example: Dict[str, torch.Tensor],
    tokenizer,
    max_tokens: int = 60,
) -> str:
    """
    Nuetzlich fuer die 'Was passiert wenn die Maskierung fehlt?'-Uebung
    aus dem README. Rendert Tokens nebeneinander mit Markierung, welche
    Positionen im Loss gelernt werden und welche nicht.

    Beispielausgabe (gekuerzt):

        Token          | Label
        ---------------+----------
        '### '         | IGNORE
        'Instruction'  | IGNORE
        ':'            | IGNORE
        ...
        'Response'     | IGNORE
        ':'            | IGNORE
        'Die'          | 'Die'    <-- ab hier zaehlt der Loss
        ' Hauptstadt'  | ' Hauptstadt'
        ...
    """
    input_ids = example["input_ids"].tolist()
    labels    = example["labels"].tolist()

    lines = ["Token          | Label", "---------------+----------"]
    shown = 0
    for tok_id, lab in zip(input_ids, labels):
        if shown >= max_tokens:
            lines.append("...            | ...")
            break
        tok_str = tokenizer.decode([tok_id])
        if lab == IGNORE_INDEX:
            lab_str = "IGNORE"
        else:
            lab_str = repr(tokenizer.decode([lab]))
        lines.append(f"{repr(tok_str):<15}| {lab_str}")
        shown += 1
    return "\n".join(lines)
