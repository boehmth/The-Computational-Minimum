"""
02 · math_breaks  —  Kapitel 1, Miniatur 2

Slide-Anker :  P1 · Text-in / Text-out — und warum das nicht reicht
Laufzeit    :  < 5 Sekunden
Kosten      :  ~50 Tokens

Fragt das Modell nach einer Multiplikation, die es zuverlässig nicht
im Kopf ausrechnen kann.  Zeigt beide Antworten (Modell vs. Python)
und macht die Differenz zur Motivation von Kapitel 2 sichtbar.

Ausführen:
    python "Agentic Systems/01_TextInTextOut/src/02_math_breaks.py"
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS   = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat
from common.ui  import hard_card, soft_frame, wrap


A = 43_177
B = 14_694


def _extract_number(text: str) -> int | None:
    """Erste zusammenhängende Ziffernfolge aus dem Modell-Output — mit
    Ignorieren von Kommas, Punkten (als Tausendertrennzeichen), €-Zeichen.
    Wenn das Modell prosaisch antwortet ('Das Ergebnis ist ...'), nehmen
    wir die längste gefundene Ziffernfolge."""
    if not text:
        return None
    cleaned = text.replace(",", "").replace(".", "").replace("_", "")
    numbers = []
    current = []
    for ch in cleaned:
        if ch.isdigit():
            current.append(ch)
        elif current:
            numbers.append("".join(current))
            current = []
    if current:
        numbers.append("".join(current))
    if not numbers:
        return None
    # nimm die längste gefundene Ziffernfolge — die trifft das Ergebnis
    # in > 95% der Fälle, unabhängig vom Antwort-Stil
    return int(max(numbers, key=len))


def main():
    aufgabe = f"Was ist {A:,} × {B:,}?  Antworte NUR mit der Zahl."
    soft_frame("DIE AUFGABE", wrap(aufgabe))

    # ---- Das Modell versucht es ----
    r = chat(
        system="Du bist ein Kopfrechner. Antworte nur mit einer Zahl.",
        user=aufgabe,
        max_tokens=64,
    )
    guess_str = r.text.strip()
    guess = _extract_number(guess_str)

    hard_card(
        title    = "▸  Das MODELL rät  (predict-next-token)",
        subtitle = f"{r.tokens_out} Tokens · {r.model}",
        body     = guess_str,
    )

    # ---- Python rechnet ----
    truth = A * B
    hard_card(
        title    = "▸  PYTHON rechnet  (deterministisch)",
        subtitle = "0 Tokens · Python-Multiplikation",
        body     = f"{truth:,}",
    )

    # ---- Differenz ----
    if guess is None:
        soft_frame(
            "DIFFERENZ",
            [
                "Konnte keine Zahl aus dem Modell-Output extrahieren.",
                f"Roh-Output: {guess_str!r}",
                "",
                "Das ist selbst schon ein Punkt: das Modell hält sich",
                "manchmal nicht an 'Antworte nur mit einer Zahl'.",
                "Parsen ist Aufgabe des Entwicklers — siehe Kapitel 3.",
            ],
        )
    else:
        delta = guess - truth
        percent = 100.0 * delta / truth if truth else float("nan")
        soft_frame(
            "DIFFERENZ",
            [
                f"Modell    →  {guess:>15,}",
                f"Python    →  {truth:>15,}",
                f"Delta     →  {delta:>+15,}",
                f"Fehler    →  {percent:>+14.4f} %",
                "",
                "Interpretation:",
                (
                    "  Größenordnung stimmt, mittlere Ziffern falsch."
                    if abs(percent) < 5
                    else "  Sogar die Größenordnung ist daneben."
                ),
                "  Das Modell hat die Aufgabe verstanden — nicht ausgeführt.",
            ],
        )

    print()
    print("→ 'Fast richtig' ist im Geschäft ein Defekt.")
    print("→ Kapitel 2: dem Modell ein Werkzeug geben statt es rechnen")
    print("  zu lassen — und die Kontrolle wechselt vom Modell an den Code.")


if __name__ == "__main__":
    main()