"""
test_reward.py - Standalone-Beweis der Reasoning-Belohnung (kein PyTorch)

Was dieses Skript zeigt:

Eine einfache regelbasierte Bewertung reicht aus, um zwischen 'gutes
Reasoning' und 'schlechtes Reasoning' zu unterscheiden - kein
Reward-Modell, kein Mensch, keine Semantik-Analyse noetig.

Wir generieren eine Aufgabe (aus data.py) und lassen den Reward auf
sechs typische Modell-Ausgaben laufen:

    (1) Perfekt: Denkspur + korrekte Antwort im \\boxed{...}
    (2) Perfektes Format, aber falsche Antwort
    (3) Korrekte Antwort, aber ohne Denkspur (nur \\boxed{})
    (4) Denkspur, aber keine \\boxed{}-Antwort
    (5) Nur eine nackte Zahl, kein Format
    (6) Sinnfreier Text

Erwartetes Ergebnis:
    (1) -> 1.0    (voller Erfolg)
    (2) -> 0.1    (Trostpreis fuer korrektes Format)
    (3) -> 0.0    (nicht mal probiert zu denken)
    (4) -> 0.0    (kein pruefbares Endergebnis)
    (5) -> 0.0
    (6) -> 0.0

Genau nach dieser Abstufung lernt das Modell im RL-Training:
- (1) wird mit Faktor 1.0 verstaerkt, kommt haeufig vor beim Nachtrainieren
- (2) mit Faktor 0.1 - kleiner Impuls, damit das FORMAT zumindest bleibt
- (3)-(6) tragen praktisch nichts bei

Kein PyTorch, kein Netz - laeuft mit reinem Python + re.
"""

from __future__ import annotations

from data import generate_dataset
from reward import compute_reward


def _fake_answer_correct_with_think(example) -> str:
    """(1) Perfekt: Denkspur und richtige Antwort."""
    return (
        "<think>\n"
        "Schritt fuer Schritt gerechnet, komme ich auf das Ergebnis unten.\n"
        "</think>\n"
        f"\\boxed{{{example.expected_answer}}}"
    )


def _fake_answer_wrong_with_think(example) -> str:
    """(2) Perfektes Format, aber falsche Antwort."""
    wrong = str(int(example.expected_answer) + 1)
    return (
        "<think>\n"
        "Ich habe hier vermutlich einen Fehler gemacht.\n"
        "</think>\n"
        f"\\boxed{{{wrong}}}"
    )


def _fake_answer_correct_no_think(example) -> str:
    """(3) Richtige Antwort, aber ohne Denkspur."""
    return f"\\boxed{{{example.expected_answer}}}"


def _fake_answer_think_no_boxed(example) -> str:
    """(4) Denkspur, aber keine \\boxed{}-Antwort."""
    return (
        "<think>\n"
        "Meiner Rechnung nach ist das Ergebnis ungefaehr {expected}.\n"
        "</think>\n"
        f"Die Antwort ist {example.expected_answer}."
    )


def _fake_answer_naked(example) -> str:
    """(5) Nur eine nackte Zahl."""
    return example.expected_answer


def _fake_answer_gibberish(example) -> str:
    """(6) Sinnfreier Text."""
    return "Ich weiss es nicht, aber der Himmel ist blau."


def main():
    dataset = generate_dataset(1, seed=7)
    ex = dataset[0]

    print("=" * 72)
    print("Prompt (Ausschnitt):")
    print(ex.prompt.strip())
    print(f"\nErwartete Antwort: {ex.expected_answer!r}")
    print("=" * 72)

    scenarios = [
        ("(1) perfekt: think + korrekt",             _fake_answer_correct_with_think),
        ("(2) format ok, falsch",                    _fake_answer_wrong_with_think),
        ("(3) korrekt, aber ohne <think>",           _fake_answer_correct_no_think),
        ("(4) think, aber keine boxed-Antwort",      _fake_answer_think_no_boxed),
        ("(5) nur nackte Zahl",                      _fake_answer_naked),
        ("(6) sinnfreier Text",                      _fake_answer_gibberish),
    ]

    for label, fake in scenarios:
        output = fake(ex)
        r = compute_reward(output, ex.expected_answer)
        print(f"\n--- {label} ---")
        print(f"Modell-Ausgabe:")
        for line in output.splitlines():
            print(f"    {line}")
        print(f"Reward: {r.total:+.2f}   [{r.why()}]")

    print("\n" + "=" * 72)
    print("BEOBACHTUNG:")
    print("  Nur (1) bekommt volle Belohnung (1.0). (2) bekommt einen kleinen")
    print("  Trostpreis (0.1), weil das FORMAT stimmt - das Modell wird also")
    print("  motiviert, das Denkformat beizubehalten, auch wenn es die Antwort")
    print("  falsch hat. (3)-(6) tragen nichts bei.")
    print()
    print("Kern-Kapitel-Aussage: Kein Reward-Modell, keine menschlichen Labels,")
    print("keine Bewertung der Denkspur selbst - trotzdem eine ausreichend")
    print("scharfe Belohnungsstruktur, damit RL Reasoning lernt.")


if __name__ == "__main__":
    main()