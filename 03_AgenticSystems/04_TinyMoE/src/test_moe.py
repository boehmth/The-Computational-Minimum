"""
test_moe.py - Standalone-Beweis: Load-Balancing verhindert Gating-Kollaps

Was dieses Skript zeigt (ohne PyTorch, ohne Gradienten, ohne echte Sprache):

Wir simulieren nur den Feedback-Loop, der in einem echten MoE-Gating
entsteht - reduziert auf seine Essenz:

    1. Fuer jedes Token entscheidet sich das Gating fuer den Experten mit
       dem hoechsten Score.
    2. Wenn ein Experte gewaehlt wird, wird sein Score ein bisschen
       erhoeht (das simuliert den positiven Backprop-Effekt: der aktive
       Experte wird besser, deshalb waehlt das Gating ihn beim naechsten
       Mal noch lieber).
    3. Ohne Gegensteuern kollabiert das auf "ein Experte bekommt alle
       Tokens". Das ist der Rich-get-Richer-Effekt.

    4. MIT Load-Balancing gibt es einen zweiten Schritt: haeufig
       gewaehlte Experten bekommen einen SCORE-ABZUG, seltene einen
       SCORE-BONUS. Das balanciert das System.

Kein PyTorch, kein Netz - reines Python.
"""

from __future__ import annotations

import random
from typing import List


NUM_EXPERTS = 4
STEPS = 2000
POSITIVE_FEEDBACK = 0.02   # so viel Score-Vorsprung baut ein Experte pro Wahl auf
BALANCING_STRENGTH = 0.2   # so stark drueckt der Load-Balancer den dominanten runter


def run(with_balancing: bool, seed: int = 42):
    """
    Simuliert STEPS Tokens. Jeder Token wird an den Experten mit dem
    hoechsten Score geroutet. Der gewaehlte Experte bekommt einen
    Score-Bonus (positive Rueckkopplung).
    Wenn `with_balancing` aktiv ist, wird zusaetzlich jeder Experte
    proportional zu seiner Ueberauslastung im "gleitenden Mittel"
    hinuntergedrueckt.
    """
    random.seed(seed)
    scores = [random.uniform(0, 0.01) for _ in range(NUM_EXPERTS)]
    # Kleiner initialer Vorsprung fuer Experte 0
    scores[0] += 0.05

    usage_count = [0] * NUM_EXPERTS
    for step in range(STEPS):
        chosen = max(range(NUM_EXPERTS), key=lambda i: scores[i])
        usage_count[chosen] += 1

        # Positive Rueckkopplung: der gewaehlte Experte wird "besser"
        scores[chosen] += POSITIVE_FEEDBACK

        if with_balancing:
            # Load-Balancing: bestrafe Experten proportional zu ihrem
            # Anteil an den bisherigen Wahlen (Overshoot ueber 1/N).
            total = sum(usage_count) or 1
            for i in range(NUM_EXPERTS):
                target = total / NUM_EXPERTS
                overshoot = usage_count[i] - target
                if overshoot > 0:
                    scores[i] -= BALANCING_STRENGTH * (overshoot / total)

    total = sum(usage_count)
    return [c / total for c in usage_count]


def bar(frac: float, width: int = 30) -> str:
    return "*" * int(round(frac * width))


def main():
    print("=" * 72)
    print("MoE Gating-Kollaps: mit und ohne Load-Balancing")
    print("=" * 72)
    print(f"({NUM_EXPERTS} Experten, {STEPS} Tokens, "
          f"positive_feedback={POSITIVE_FEEDBACK}, "
          f"balancing_strength={BALANCING_STRENGTH})")

    print("\nOHNE Load-Balancing:")
    fracs_no = run(with_balancing=False)
    for i, f in enumerate(fracs_no):
        print(f"  Experte {i}: {bar(f):<32s} ({100 * f:.1f} %)")

    print("\nMIT Load-Balancing:")
    fracs_yes = run(with_balancing=True)
    for i, f in enumerate(fracs_yes):
        print(f"  Experte {i}: {bar(f):<32s} ({100 * f:.1f} %)")

    print("\n" + "=" * 72)
    max_no  = max(fracs_no)
    max_yes = max(fracs_yes)
    print(f"Konzentration (Anteil des am meisten gewaehlten Experten):")
    print(f"    ohne Balancing: {100 * max_no:.1f} %  "
          f"(Gleichverteilung waere {100 / NUM_EXPERTS:.1f} %)")
    print(f"    mit Balancing:  {100 * max_yes:.1f} %")
    print()
    if max_no > 0.5 and max_yes < max_no - 0.15:
        print("BEOBACHTUNG (wie erwartet):")
        print("  Ohne Load-Balancing verstaerkt der Feedback-Loop den kleinsten")
        print("  Anfangsvorsprung von Experte 0 zu einem massiven Kollaps.")
        print("  MIT Load-Balancing wird jeder Experte, der ueberdurchschnittlich")
        print("  oft gewaehlt wird, aktiv gebremst. Das haelt die Verteilung breit.")
        print()
        print("Der Kernmechanismus in einer Zeile:")
        print("    aux_loss = num_experts * sum(fraction_i * routing_prob_i)")
        print("  -> hohe fraction * hohe prob => hoher Loss => Gradient druckt runter.")
    else:
        print("HINWEIS: Effekt schwach ausgepraegt - Parameter feinjustieren?")


if __name__ == "__main__":
    main()