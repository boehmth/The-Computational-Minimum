"""
reward.py - Regelbasierte Belohnungsfunktion fuer TinyReason (Kap. 3.5)

DIDAKTISCHE POINTE DIESES KAPITELS
==================================

Der aufregendste Befund des Jahres 2025 (DeepSeek-R1-Zero) war, dass fuer
Reasoning-Training ZWEI Zutaten reichen:

    1. Ein Trainingsformat, das dem Modell einen expliziten Denkbereich
       einraeumt:
           <think> ... Zwischenschritte ... </think>
           ... eigentliche Antwort ...

    2. Eine BELOHNUNGSFUNKTION, die *ausschliesslich* das Endergebnis
       prueft (regelbasiert, deterministisch).

Kein Process Reward Model (das jeden Zwischenschritt einzeln bewertet).
Kein menschliches Feedback. Kein trainierter Reward-Modell-Kopf.

Diese Datei enthaelt genau die zweite Zutat: ein paar Zeilen Python, die
eine Modell-Ausgabe daraufhin pruefen, ob sie (a) das Denkformat einhaelt
und (b) die richtige Antwort enthaelt. Der Rueckgabewert ist die
Belohnung, die dann im RL-Loop als Gewicht fuer diese Trajektorie dient.

Diese Datei laeuft OHNE PyTorch - reine Regex/String-Verarbeitung.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


# Format-Belohnungen. Absolute Zahlen sind Konvention; wichtig ist nur
# das Verhaeltnis: die grosse Belohnung fuers Ergebnis, kleine fuers Format.
REWARD_CORRECT_ANSWER  = 1.0
REWARD_FORMAT_ONLY     = 0.1
REWARD_NONE            = 0.0


# Wir erwarten Antworten der Form:
#   <think>...(beliebige Denkspur)...</think>
#   \boxed{42}
# Die Denkspur wird nicht analysiert, nur die Formatierung geprueft.
# Das \boxed{...}-Format kommt aus GSM8K/MATH und ist inzwischen Standard.
THINK_PATTERN  = re.compile(r"<think>(.*?)</think>", re.DOTALL)
ANSWER_PATTERN = re.compile(r"\\boxed\{([^\{\}]*)\}")


@dataclass
class RewardBreakdown:
    """Aufgeschluesselte Belohnung fuer eine einzelne Antwort."""
    total: float
    has_think_block: bool
    has_boxed_answer: bool
    predicted_answer: Optional[str]
    is_correct: bool

    def why(self) -> str:
        parts = []
        parts.append("YES" if self.has_think_block else "NO ")
        parts.append("YES" if self.has_boxed_answer else "NO ")
        parts.append(repr(self.predicted_answer) if self.predicted_answer else "None")
        parts.append("YES" if self.is_correct else "NO ")
        return f"think={parts[0]} boxed={parts[1]} pred={parts[2]} correct={parts[3]}"


def _normalize_number(s: str) -> Optional[str]:
    """
    Versucht, einen String in eine kanonische Zahlform zu bringen (fuer
    den Vergleich Antwort-vs-Loesung). Wir sind bewusst tolerant: '42',
    '42.0', ' 42 ', '+42' sollten alle als gleich gelten.
    """
    if s is None:
        return None
    s = s.strip().replace(",", ".")  # ',' als Dezimaltrenner tolerieren
    # Entferne fuehrendes '+' und ueberfluessige Nullen nach dem Komma
    try:
        f = float(s)
        if f == int(f):
            return str(int(f))
        return f"{f:g}"
    except ValueError:
        return s  # nicht-numerische Antworten (spaeter erweiterbar)


def compute_reward(model_output: str, expected_answer: str) -> RewardBreakdown:
    """
    Bewertet eine einzelne Modell-Ausgabe.

    Die Belohnungslogik hat drei Stufen:

        1. Keine der beiden Formatvorgaben eingehalten     -> 0.0
        2. Format OK, Antwort aber falsch (oder nicht da)  -> 0.1
        3. Format OK und Antwort korrekt                   -> 1.0

    Diese Abstufung ist wichtig: sie belohnt bereits den *Versuch* der
    richtigen Struktur, ohne die eigentliche Korrektheit zu verwaessern.
    So bekommt das Modell frueh im Training einen kleinen positiven
    Impuls, wenn es die Denkspur produziert, auch wenn die Antwort noch
    nicht stimmt.
    """
    has_think  = bool(THINK_PATTERN.search(model_output))
    answer_match = ANSWER_PATTERN.search(model_output)
    has_boxed  = answer_match is not None
    predicted  = _normalize_number(answer_match.group(1)) if answer_match else None
    expected_n = _normalize_number(expected_answer)
    is_correct = (predicted is not None) and (predicted == expected_n)

    if is_correct and has_think:
        total = REWARD_CORRECT_ANSWER
    elif has_think and has_boxed:
        # Format richtig, aber Antwort falsch: kleiner Trostpreis
        total = REWARD_FORMAT_ONLY
    else:
        total = REWARD_NONE

    return RewardBreakdown(
        total=total,
        has_think_block=has_think,
        has_boxed_answer=has_boxed,
        predicted_answer=predicted,
        is_correct=is_correct,
    )