"""
data.py - Mehrstufige Rechenaufgaben fuer Reasoning-Training (Kap. 3.5)

Wir generieren Aufgaben, bei denen ein "direktes Raten" scheitert, aber
eine korrekte Schritt-fuer-Schritt-Rechnung zuverlaessig funktioniert.

Beispiel:
    Prompt:
        "Ein Bauer hat 17 Aepfel. Er verkauft 3 und pflueckt danach
         2 neue dazu. Wie viele Aepfel hat er jetzt? Denke Schritt fuer
         Schritt und schreibe die finale Antwort in \\boxed{...}."
    Erwartete Antwort:
        "16"

Solche Aufgaben sind Prompt-technisch klein (fitten in kleine Modelle),
haben aber einen klaren, deterministisch pruefbaren Endwert - genau die
Grundlage fuer regelbasiertes RL-Reasoning-Training (siehe reward.py).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional


PROMPT_TEMPLATE = (
    "Loese die folgende Aufgabe. Denke zuerst Schritt fuer Schritt zwischen "
    "<think> und </think>. Schreibe die finale Antwort danach in \\boxed{{...}}.\n\n"
    "Aufgabe: {task}\n"
)


@dataclass
class ReasoningExample:
    prompt: str
    expected_answer: str  # als String, damit reward.py normalisieren kann
    solution: str          # eine musterhafte Loesung mit Denkspur (nur als Referenz)


# -------------------------------------------------------------------------
# Aufgabengeneratoren
# -------------------------------------------------------------------------

def _sample_add_sub(rng: random.Random) -> ReasoningExample:
    """Aepfel-Aufgabe: Start + Zufuhren - Abgaenge."""
    start = rng.randint(10, 40)
    take  = rng.randint(1, 9)
    add   = rng.randint(1, 9)
    result = start - take + add

    task = (f"Ein Bauer hat {start} Aepfel. Er verkauft {take} und pflueckt "
            f"danach {add} neue dazu. Wie viele Aepfel hat er jetzt?")
    prompt = PROMPT_TEMPLATE.format(task=task)
    solution = (
        f"<think>\n"
        f"Start: {start}. Nach Verkauf: {start} - {take} = {start-take}. "
        f"Nach Pfluecken: {start-take} + {add} = {result}.\n"
        f"</think>\n"
        f"\\boxed{{{result}}}"
    )
    return ReasoningExample(prompt=prompt, expected_answer=str(result), solution=solution)


def _sample_multi_step(rng: random.Random) -> ReasoningExample:
    """3-Schritt-Aufgabe mit Multiplikation."""
    per_box = rng.randint(3, 8)
    n_boxes = rng.randint(2, 6)
    used    = rng.randint(1, 4)
    result  = per_box * n_boxes - used

    task = (f"In jeder Kiste sind {per_box} Buecher. Es gibt {n_boxes} Kisten. "
            f"Wenn wir {used} Buecher entnehmen, wie viele bleiben uebrig?")
    prompt = PROMPT_TEMPLATE.format(task=task)
    solution = (
        f"<think>\n"
        f"Gesamtzahl: {per_box} * {n_boxes} = {per_box*n_boxes}. "
        f"Nach Entnahme: {per_box*n_boxes} - {used} = {result}.\n"
        f"</think>\n"
        f"\\boxed{{{result}}}"
    )
    return ReasoningExample(prompt=prompt, expected_answer=str(result), solution=solution)


def _sample_trick(rng: random.Random) -> ReasoningExample:
    """
    Die klassische 'alle bis auf N' Fangfrage - genau der Aufgabentyp, den
    Chain-of-Thought-Prompting laut Wei et al. 2022 dramatisch verbessert.
    """
    total = rng.randint(10, 30)
    survive = rng.randint(3, total - 1)
    task = (f"Ein Bauer hat {total} Schafe. Alle bis auf {survive} sterben. "
            f"Wie viele Schafe bleiben uebrig?")
    prompt = PROMPT_TEMPLATE.format(task=task)
    solution = (
        f"<think>\n"
        f"'Alle bis auf {survive}' bedeutet: es bleiben genau {survive} uebrig, "
        f"nicht {total - survive}. Die anderen sind gestorben, aber die Frage "
        f"war 'wie viele bleiben uebrig'.\n"
        f"</think>\n"
        f"\\boxed{{{survive}}}"
    )
    return ReasoningExample(prompt=prompt, expected_answer=str(survive), solution=solution)


_GENERATORS = [_sample_add_sub, _sample_multi_step, _sample_trick]


def generate_dataset(n_samples: int, seed: int = 42) -> List[ReasoningExample]:
    """Erzeugt einen synthetischen Trainingsdatensatz."""
    rng = random.Random(seed)
    dataset: List[ReasoningExample] = []
    for _ in range(n_samples):
        gen = rng.choice(_GENERATORS)
        dataset.append(gen(rng))
    return dataset


def format_prompt(instruction_or_prompt: str) -> str:
    """Kompatibilitaets-Wrapper, falls Skripte den Namen aus 3.2/3.3 erwarten."""
    return instruction_or_prompt