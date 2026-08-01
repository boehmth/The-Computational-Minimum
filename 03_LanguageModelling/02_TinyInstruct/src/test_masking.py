"""
test_masking.py - Standalone-Testskript fuer die didaktische Kern-Logik

Dieses Skript beweist die zentrale Aussage des Kapitels ohne PyTorch:

    Der Prompt-Teil bekommt IGNORE_INDEX (-100), der Response-Teil bleibt
    als echte Token-IDs stehen. Der Loss lernt damit ausschliesslich die
    Antwort.

Ausfuehrung (kein PyTorch, keine Netzverbindung noetig):

    python test_masking.py
"""

from __future__ import annotations

from typing import List


IGNORE_INDEX = -100


# Wir duplizieren die Kern-Funktionen aus data.py hier bewusst, damit
# dieses Skript OHNE torch-Import lauffaehig ist. Wenn du die Datei in
# data.py aenderst, aktualisiere hier mit.

PROMPT_TEMPLATE = (
    "### Instruction:\n"
    "{instruction}\n\n"
    "### Response:\n"
)
RESPONSE_SUFFIX = "\n"


def format_prompt(instruction: str) -> str:
    return PROMPT_TEMPLATE.format(instruction=instruction.strip())


def format_full(instruction: str, response: str) -> str:
    return format_prompt(instruction) + response.strip() + RESPONSE_SUFFIX


def mask_prompt_labels(
    prompt_ids: List[int],
    full_ids: List[int],
) -> List[int]:
    """
    DIE zentrale Zeile dieses Kapitels: der Prompt-Teil wird auf
    IGNORE_INDEX gesetzt, alles danach bleibt als echte Ziel-ID.
    """
    labels = list(full_ids)
    labels[: len(prompt_ids)] = [IGNORE_INDEX] * len(prompt_ids)
    return labels


def fake_tokenizer(text: str) -> List[int]:
    """
    Winziger Fake-Tokenizer: 1 Zeichen = 1 Token. Reicht, um das PRINZIP
    zu zeigen, ohne HF-Modelle zu laden.
    """
    return [ord(c) for c in text]


def render_visualization(instruction: str, response: str) -> str:
    prompt_text = format_prompt(instruction)
    full_text = format_full(instruction, response)

    prompt_ids = fake_tokenizer(prompt_text)
    full_ids = fake_tokenizer(full_text)
    labels = mask_prompt_labels(prompt_ids, full_ids)

    lines = [
        f"Instruction: {instruction!r}",
        f"Response:    {response!r}",
        "",
        f"prompt_text ({len(prompt_ids)} Zeichen):",
        f"  {prompt_text!r}",
        "",
        f"full_text ({len(full_ids)} Zeichen):",
        f"  {full_text!r}",
        "",
        "Token-fuer-Token-Sicht (nur die ersten und die letzten Positionen):",
        "  Pos | Zeichen  | Label",
        "  ----+----------+-------------",
    ]

    def render_line(pos: int) -> str:
        ch = chr(full_ids[pos])
        lab = labels[pos]
        lab_str = "IGNORE" if lab == IGNORE_INDEX else f"chr({lab}) = {chr(lab)!r}"
        return f"  {pos:3d} | {ch!r:8s} | {lab_str}"

    # Erste 5, dann die Trenn-Positionen um den Response-Anfang, dann letzte 5
    boundary = len(prompt_ids)
    idxs = list(range(min(5, len(full_ids))))
    idxs += list(range(max(boundary - 2, 5), min(boundary + 4, len(full_ids))))
    idxs += list(range(max(len(full_ids) - 5, boundary + 4), len(full_ids)))
    # Duplikate entfernen und sortieren
    idxs = sorted(set(idxs))
    prev = -2
    for pos in idxs:
        if pos - prev > 1:
            lines.append("  ... |    ...   |    ...")
        lines.append(render_line(pos))
        prev = pos

    # Kern-Assertions
    n_ignored = sum(1 for l in labels if l == IGNORE_INDEX)
    n_kept = sum(1 for l in labels if l != IGNORE_INDEX)
    lines.append("")
    lines.append(f"  -> {n_ignored} Positionen mit IGNORE_INDEX (der Prompt-Teil)")
    lines.append(f"  -> {n_kept} Positionen mit echter Ziel-ID (der Response-Teil)")

    # Sanity: prompt ist Praefix
    assert full_ids[: len(prompt_ids)] == prompt_ids, \
        "Prompt ist kein Praefix des vollen Textes!"
    assert n_ignored == len(prompt_ids), \
        "Falsche Anzahl IGNORE_INDEX-Positionen!"
    assert n_kept + n_ignored == len(labels), \
        "Labels haben falsche Gesamtgroesse!"

    return "\n".join(lines)


def main():
    beispiele = [
        ("Was ist die Hauptstadt von Frankreich?",
         "Die Hauptstadt von Frankreich ist Paris."),
        ("Nenne drei Primzahlen.",
         "2, 3 und 5."),
    ]

    for i, (instruction, response) in enumerate(beispiele):
        print("=" * 72)
        print(f"Beispiel {i+1}")
        print("=" * 72)
        print(render_visualization(instruction, response))
        print()

    print("ALLE TESTS BESTANDEN.")
    print("Die 'eine Zeile', die den Kapitel-Sprung macht:")
    print("    labels[: len(prompt_ids)] = [IGNORE_INDEX] * len(prompt_ids)")


if __name__ == "__main__":
    main()