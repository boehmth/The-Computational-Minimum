"""
test_aloha.py - Standalone-Beweis: die klassischen ALOHA-Durchsatzkurven

Was dieses Skript zeigt (ohne Frameworks, ohne Netz):

1. Wir simulieren fuer eine Reihe von Angeboten G verschiedene
   ALOHA-Kanalauslastungen.
2. Wir vergleichen den *simulierten* Durchsatz mit der geschlossenen
   theoretischen Kurve (Abramson 1970, Roberts 1972):

     Pure ALOHA:      S = G * exp(-2G),  Maximum: S = 1/(2e) ~ 0.184
     Slotted ALOHA:   S = G * exp(-G),   Maximum: S = 1/e     ~ 0.368

3. Der zweite Kernpunkt: bei zu HOHER Last SINKT der Durchsatz sogar
   wieder - der Kanal kollabiert unter zu vielen Kollisionen.

4. Zum Abschluss ein kleines ASCII-Bild eines Pure-ALOHA-Laufs, damit
   man Kollisionen "live" sehen kann.

Kein Netz, kein PyTorch, reines Python.
"""

from __future__ import annotations

import math

from aloha import (
    demo_transmissions,
    render_timeline,
    simulate_pure_aloha,
    simulate_slotted_aloha,
    theory_pure_aloha,
    theory_slotted_aloha,
)


def hr():
    print("-" * 72)


def _bar(value: float, max_width: int = 30, max_value: float = 0.4) -> str:
    n = int(round(value / max_value * max_width))
    return "#" * max(0, min(n, max_width))


def scan_curves():
    """
    Erzeugt eine Tabelle 'angebotene Last G  ->  Durchsatz S'  fuer
    beide ALOHA-Varianten und vergleicht Simulation mit Theorie.
    """
    # Wir waehlen G-Werte, die den interessanten Bereich abdecken (das
    # Maximum plus die Ueberlast-Zone auf der rechten Seite).
    load_points = [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]

    print("\n" + "=" * 72)
    print("Durchsatz-Kurve  (angebotene Last G -> erfolgreicher Durchsatz S)")
    print("=" * 72)
    print("Format:  G   |  Pure ALOHA (sim  vs  theorie)  |  "
          "Slotted ALOHA (sim  vs  theorie)")
    hr()

    # Feste Aufgabengrosse - wir waehlen so, dass 'n_slots' fuer Slotted
    # gross genug ist, damit die Statistik stabil ist.
    n_slots = 2000

    for G in load_points:
        # Gesamt-Sendungsversuche = G * n_slots, verteilt auf ~50 Sender.
        n_senders = 50
        total_attempts = int(round(G * n_slots))
        per_sender = max(1, total_attempts // n_senders)
        # Anpassen, damit total_attempts wirklich ~ G * n_slots ist
        total_actual = n_senders * per_sender
        G_actual = total_actual / n_slots

        # Pure ALOHA
        r_pure = simulate_pure_aloha(
            n_senders=n_senders,
            packets_per_sender=per_sender,
            duration=float(n_slots),   # Dauer in "packet-length"-Einheiten
            packet_length=1.0,
            seed=42,
        )
        # Slotted ALOHA
        r_slot = simulate_slotted_aloha(
            n_senders=n_senders,
            packets_per_sender=per_sender,
            n_slots=n_slots,
            seed=42,
        )

        S_pure_theo = theory_pure_aloha(G_actual)
        S_slot_theo = theory_slotted_aloha(G_actual)

        print(f"G={G_actual:4.2f}  |  "
              f"Pure sim={r_pure.throughput:.3f}  th={S_pure_theo:.3f}  |  "
              f"Slotted sim={r_slot.throughput:.3f}  th={S_slot_theo:.3f}")

    hr()
    print(f"Theoretische Maxima:")
    print(f"  Pure ALOHA:    S_max = 1/(2e) = {1/(2*math.e):.3f}  (bei G=0.5)")
    print(f"  Slotted ALOHA: S_max = 1/e    = {1/math.e:.3f}  (bei G=1.0)")


def show_ascii_timeline():
    """Kleine ASCII-Visualisierung, um Kollisionen 'live' zu sehen."""
    print("\n" + "=" * 72)
    print("ASCII-Zeitachse eines Pure-ALOHA-Miniatur-Laufs")
    print("=" * 72)
    ts = demo_transmissions(seed=7)
    print(render_timeline(ts, duration=10.0, packet_length=1.0, width=60))
    n_ok = sum(1 for t in ts if t.succeeded)
    print(f"\n{n_ok}/{len(ts)} Sendungen erfolgreich.")


def show_throughput_bar_chart():
    """
    Klarer ASCII-Chart der Slotted-ALOHA-Theoriekurve, damit man das
    Maximum bei G=1 optisch sofort sieht.
    """
    print("\n" + "=" * 72)
    print("Slotted ALOHA - Theoriekurve als ASCII-Chart")
    print("=" * 72)
    print("G      S = G*exp(-G)")
    hr()
    for i in range(1, 41):
        G = i * 0.1
        S = theory_slotted_aloha(G)
        marker = "  <-- Maximum" if abs(G - 1.0) < 1e-6 else ""
        print(f"{G:4.1f}   {_bar(S)}  {S:.3f}{marker}")


def main():
    print("=" * 72)
    print("ALOHA-Protokoll: probabilistischer Zugriff auf einen geteilten Kanal")
    print("=" * 72)
    print("Kernfrage: bei welcher Last G kollabiert der Kanal?")

    scan_curves()
    show_ascii_timeline()
    show_throughput_bar_chart()

    print("\n" + "=" * 72)
    print("KERN-BEOBACHTUNG:")
    print("  - Pure ALOHA: max. 18.4 % Kanalauslastung bei G = 0.5.")
    print("  - Slotted ALOHA verdoppelt das auf 36.8 % - allein durch die")
    print("    Regel 'Sender darf nur zu Slot-Anfangszeiten senden'.")
    print("  - Bei G > 1 (Slotted) bzw. G > 0.5 (Pure) SINKT der Durchsatz")
    print("    wieder: mehr Sendeversuche -> mehr Kollisionen -> weniger")
    print("    erfolgreiche Pakete. Ein Kanal, der ueberlaeuft, ist schlechter")
    print("    als einer, der nur zur Haelfte genutzt wird.")
    print()
    print("Diese eine Formel - S = G * exp(-G) - trug den Kern-Insight, aus")
    print("dem Metcalfe 1973 bei Xerox PARC das CSMA/CD von Ethernet ableitete:")
    print("wenn man BEVOR dem Senden hoert, ob der Kanal frei ist, kann man")
    print("die 37 % nochmal deutlich uebertreffen. Siehe notes/ethernet.md.")


if __name__ == "__main__":
    main()