"""
test_dpo_loss.py - Standalone-Beweis fuer den DPO-Loss

Dieses Skript zeigt in einer 60-Zeilen-Rechnung ohne PyTorch, dass der
DPO-Loss genau das tut, was er verspricht:

    "Verschiebe die Modell-Wahrscheinlichkeiten so, dass chosen
     wahrscheinlicher wird als rejected - aber nicht zu weit weg von
     der Referenz."

Wir bauen synthetische Log-Wahrscheinlichkeiten fuer drei Szenarien und
zeigen den Loss-Wert und den 'preference accuracy' - genau so, wie die
Tqdm-Postfix-Zeilen es im echten Training tun.

Ausfuehrung (kein PyTorch, kein Netz):

    python test_dpo_loss.py
"""

from __future__ import annotations

import math


def log_sigmoid(x: float) -> float:
    """Numerisch stabile log-sigmoid Implementation."""
    # log(sigmoid(x)) = -softplus(-x) = -log(1 + exp(-x))
    # Fuer x >> 0 waechst exp(-x) gegen 0 -> log(1+0) = 0.
    # Fuer x << 0 approximieren wir direkt log(sigmoid(x)) ~ x.
    if x > 0:
        return -math.log1p(math.exp(-x))
    else:
        return x - math.log1p(math.exp(x))


def dpo_loss(
    policy_chosen_logp: float,
    policy_rejected_logp: float,
    ref_chosen_logp: float,
    ref_rejected_logp: float,
    beta: float,
):
    """
    Skalare Version des DPO-Loss. Rueckgabe:
        (loss, chosen_reward, rejected_reward, correctly_ordered)
    """
    chosen_reward   = beta * (policy_chosen_logp   - ref_chosen_logp)
    rejected_reward = beta * (policy_rejected_logp - ref_rejected_logp)
    logits = chosen_reward - rejected_reward
    loss = -log_sigmoid(logits)
    return loss, chosen_reward, rejected_reward, (logits > 0)


def print_scenario(name: str, **kwargs):
    print(f"\n--- {name} ---")
    for k, v in kwargs.items():
        print(f"  {k:25s} = {v:+.4f}")
    loss, cr, rr, ok = dpo_loss(**kwargs)
    print(f"  chosen_reward           = {cr:+.4f}   (=beta * (pi(c) - ref(c)))")
    print(f"  rejected_reward         = {rr:+.4f}   (=beta * (pi(r) - ref(r)))")
    print(f"  preferred order?        = {'YES  (chosen > rejected)' if ok else 'NO   (chosen < rejected)'}")
    print(f"  loss                    = {loss:+.4f}")


def main():
    print("=" * 72)
    print("DPO-Loss - drei Szenarien mit denselben Referenz-Werten")
    print("=" * 72)

    # Basis-Setup: die Referenz gibt beiden Antworten dieselbe
    # log-Wahrscheinlichkeit (-3.0). Das ist der Zustand direkt nach
    # dem SFT-Training, bevor DPO ueberhaupt einen Schritt gemacht hat.
    beta = 0.1
    ref_chosen_logp   = -3.0
    ref_rejected_logp = -3.0

    # ----- Szenario 1: Policy hat sich schon "richtig" bewegt -----
    #   pi(chosen)   ist wahrscheinlicher als ref  (Policy hat sie gehoben)
    #   pi(rejected) ist unwahrscheinlicher als ref (Policy hat sie gesenkt)
    print_scenario(
        "Szenario 1: Policy bevorzugt chosen bereits (idealer Fall)",
        policy_chosen_logp=-2.0,   # +1.0 gegenueber ref
        policy_rejected_logp=-4.0, # -1.0 gegenueber ref
        ref_chosen_logp=ref_chosen_logp,
        ref_rejected_logp=ref_rejected_logp,
        beta=beta,
    )

    # ----- Szenario 2: Policy neutral, unveraendert gegenueber Referenz -----
    #   Erwartung: loss ~ log(2) ~ 0.693, da chosen_reward == rejected_reward
    print_scenario(
        "Szenario 2: Policy unveraendert (Startzustand, loss ~ ln 2)",
        policy_chosen_logp=-3.0,
        policy_rejected_logp=-3.0,
        ref_chosen_logp=ref_chosen_logp,
        ref_rejected_logp=ref_rejected_logp,
        beta=beta,
    )

    # ----- Szenario 3: Policy hat die Praeferenz UMGEDREHT -----
    #   Sie bevorzugt rejected und unterdrueckt chosen. Erwartung: HOHER loss.
    print_scenario(
        "Szenario 3: Policy bevorzugt rejected (Alarm, loss sollte hoch sein)",
        policy_chosen_logp=-4.0,   # -1.0 gegenueber ref
        policy_rejected_logp=-2.0, # +1.0 gegenueber ref
        ref_chosen_logp=ref_chosen_logp,
        ref_rejected_logp=ref_rejected_logp,
        beta=beta,
    )

    print("\n" + "=" * 72)
    print("Beobachtungen (die sollten in den Zahlen oben sichtbar sein):")
    print("  1. Loss ist AM KLEINSTEN, wenn die Policy die Praeferenz bereits")
    print("     hat (Szenario 1). Der Gradient will dorthin.")
    print("  2. Loss ist ~ ln(2) ~ 0.693 wenn die Policy neutral ist")
    print("     (Szenario 2) - der Startzustand direkt nach dem SFT.")
    print("  3. Loss ist AM GROESSTEN, wenn die Policy die Praeferenz")
    print("     verletzt (Szenario 3).")
    print()
    print("Der Gradient dieses Loss ist der ganze Trainings-Mechanismus von")
    print("DPO. Kein Reward-Modell, kein PPO, keine KL-Extras - nur diese")
    print("eine Rechnung, wiederholt auf tausenden Praeferenz-Paaren.")


if __name__ == "__main__":
    main()