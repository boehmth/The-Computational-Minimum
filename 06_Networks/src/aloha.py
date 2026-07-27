"""
aloha.py - Das ALOHA-Protokoll (Abramson 1970-71)

DIDAKTISCHE POINTE DIESES KAPITELS
==================================

Das ALOHA-Protokoll ist zu Netzwerken das, was die 4-Bit-CPU zu Prozessoren
ist: der minimale Prototyp, aus dem alles Weitere durch Skalierung und
Verfeinerung entstanden ist.

Die Idee, 1970-71 von Norman Abramson auf Hawaii gebaut, um Rechner auf
verschiedenen Inseln per Funk zu verbinden, ist radikal einfach:

    "Wenn du etwas zu senden hast, sende es. Wenn dein Paket kollidiert,
     warte eine zufaellige Zeit und versuche es nochmal."

Kein Handshake. Kein Master. Kein Scheduler. Nur: probabilistischer
Zugriff auf ein gemeinsames Medium.

Diese Datei simuliert zwei Varianten:

    1. Pure ALOHA (Abramson 1970): Sender darf jederzeit senden.
       Theoretischer Maximaldurchsatz: S = G * exp(-2G), Maximum bei G=0.5
       -> S_max = 1/(2e) ~ 18.4%.

    2. Slotted ALOHA (Roberts 1972): Sender darf nur zu Beginn eines
       festen Zeitslots senden.
       Theoretischer Maximaldurchsatz: S = G * exp(-G), Maximum bei G=1.0
       -> S_max = 1/e ~ 36.8%.

Die Verdoppelung von 18% auf 37% durch eine einzige Regel-Aenderung
(Slotting) war eines der ersten "kleinen Ideen, grosse Wirkung"-Ergebnisse
der Netzwerkforschung. Sie zeigt, warum ALOHA nicht nur historisch, sondern
konzeptionell so wichtig ist.

Metcalfe hat ALOHAs Analyse Anfang der 1970er gelesen und daraus
CSMA/CD -> Ethernet entwickelt (siehe notes/ethernet.md).

Kein Netz, keine externen Abhaengigkeiten - reines Python.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Tuple


# -------------------------------------------------------------------------
# Datenstrukturen
# -------------------------------------------------------------------------

@dataclass
class Transmission:
    """Ein Sendevorgang auf dem gemeinsamen Kanal."""
    sender_id: int
    start_time: float
    end_time: float
    succeeded: bool = False   # wird spaeter gesetzt


@dataclass
class SimResult:
    """Ergebnis einer Simulation."""
    total_attempts: int
    successful: int
    collisions: int
    duration: float
    offered_load: float       # G = versuchte Sendungen pro Slot-Zeit
    throughput: float         # S = erfolgreiche Sendungen pro Slot-Zeit

    def summary(self) -> str:
        return (f"G = {self.offered_load:.3f}   S = {self.throughput:.3f}   "
                f"(erfolgreich: {self.successful}/{self.total_attempts}, "
                f"Kollisionen: {self.collisions})")


# -------------------------------------------------------------------------
# Pure ALOHA
# -------------------------------------------------------------------------
# Kanal-Modell: alle Sender teilen sich EINEN Kanal. Wenn zwei oder mehr
# Sendungen sich zeitlich ueberlappen, kollidieren sie und beide (alle)
# gehen verloren.

def simulate_pure_aloha(
    n_senders: int,
    packets_per_sender: int,
    duration: float,
    packet_length: float = 1.0,
    seed: int = 42,
) -> SimResult:
    """
    Pure ALOHA: Jeder Sender darf zu jedem Zeitpunkt senden. Die
    Sendezeitpunkte sind gleichverteilt auf [0, duration).

    Ergebnis: Fuer jede Sendung schauen wir, ob im Intervall
        [start - packet_length,  start + packet_length]
    eine andere Sendung existiert (denn nur dann kann sie *ueberlappen*).
    """
    rng = random.Random(seed)
    transmissions: List[Transmission] = []
    for sender in range(n_senders):
        for _ in range(packets_per_sender):
            start = rng.uniform(0.0, duration)
            transmissions.append(Transmission(
                sender_id=sender,
                start_time=start,
                end_time=start + packet_length,
            ))

    # Nach Startzeit sortieren, um Nachbar-Ueberlappungen effizient
    # zu erkennen.
    transmissions.sort(key=lambda t: t.start_time)

    # Naive Kollisionserkennung: fuer jede Sendung pruefen wir, ob eine
    # andere sich zeitlich mit ihr ueberlappt.
    for i, t in enumerate(transmissions):
        collided = False
        # Rueckwaerts pruefen
        for j in range(i - 1, -1, -1):
            other = transmissions[j]
            if other.end_time <= t.start_time:
                break  # weiter zurueck kann nichts mehr ueberlappen
            if other.sender_id != t.sender_id:
                collided = True
                other.succeeded = False
        # Vorwaerts pruefen
        for j in range(i + 1, len(transmissions)):
            other = transmissions[j]
            if other.start_time >= t.end_time:
                break
            if other.sender_id != t.sender_id:
                collided = True
                other.succeeded = False
        t.succeeded = not collided

    successful = sum(1 for t in transmissions if t.succeeded)
    total = len(transmissions)
    collisions = total - successful

    # G und S in Einheiten von packet_length (Roberts-Konvention)
    slots = duration / packet_length
    offered_load = total / slots
    throughput = successful / slots

    return SimResult(
        total_attempts=total,
        successful=successful,
        collisions=collisions,
        duration=duration,
        offered_load=offered_load,
        throughput=throughput,
    )


# -------------------------------------------------------------------------
# Slotted ALOHA
# -------------------------------------------------------------------------
# Zusaetzliche Regel: Sender duerfen nur zu Beginn eines Zeitslots senden.
# Dadurch koennen nur Sendungen im *exakt gleichen* Slot kollidieren -
# das halbiert den "Gefahrenzeitraum" verglichen mit Pure ALOHA.

def simulate_slotted_aloha(
    n_senders: int,
    packets_per_sender: int,
    n_slots: int,
    seed: int = 42,
) -> SimResult:
    """
    Slotted ALOHA: jede Sendung startet zum Beginn eines der n_slots
    diskreten Zeitslots. Kollision <=> mehrere Sender waehlen denselben Slot.
    """
    rng = random.Random(seed)

    # Zaehle pro Slot, wie viele Sender ihn gewaehlt haben.
    slot_users: List[List[int]] = [[] for _ in range(n_slots)]
    total = 0
    for sender in range(n_senders):
        for _ in range(packets_per_sender):
            slot = rng.randrange(n_slots)
            slot_users[slot].append(sender)
            total += 1

    successful = sum(1 for users in slot_users if len(users) == 1)
    collisions = total - successful

    offered_load = total / n_slots
    throughput = successful / n_slots

    return SimResult(
        total_attempts=total,
        successful=successful,
        collisions=collisions,
        duration=float(n_slots),
        offered_load=offered_load,
        throughput=throughput,
    )


# -------------------------------------------------------------------------
# Theoretische Kurven (Roberts 1972)
# -------------------------------------------------------------------------

def theory_pure_aloha(G: float) -> float:
    """S = G * exp(-2G).  Maximum: S = 1/(2e) ~ 0.184 bei G = 0.5."""
    return G * math.exp(-2 * G)


def theory_slotted_aloha(G: float) -> float:
    """S = G * exp(-G).   Maximum: S = 1/e   ~ 0.368 bei G = 1.0."""
    return G * math.exp(-G)


# -------------------------------------------------------------------------
# Kurze ASCII-Visualisierung der Zeitachse
# -------------------------------------------------------------------------

def render_timeline(
    transmissions: List[Transmission],
    duration: float,
    packet_length: float = 1.0,
    width: int = 60,
) -> str:
    """
    Rendert die Sendungen als ASCII-Zeitachse. Jeder Sender bekommt eine
    eigene Zeile, aktive Sendezeiten werden als Balken angezeigt. Am Ende
    zeigt eine Statuszeile Kollisionen.
    """
    if not transmissions:
        return "(keine Sendungen)"

    sender_ids = sorted({t.sender_id for t in transmissions})
    lines = {sid: [" "] * width for sid in sender_ids}
    kollision_marker = [" "] * width

    def _slot(t: float) -> int:
        return max(0, min(width - 1, int(t / duration * width)))

    for t in transmissions:
        s = _slot(t.start_time)
        e = _slot(t.end_time)
        marker = "X" if not t.succeeded else "="
        for k in range(s, min(e + 1, width)):
            # Bei doppeltem Zugriff im selben Char: Kollision anzeigen
            if lines[t.sender_id][k] != " ":
                lines[t.sender_id][k] = "*"
            else:
                lines[t.sender_id][k] = marker
            if not t.succeeded:
                kollision_marker[k] = "!"

    out = []
    for sid in sender_ids:
        out.append(f"Sender {sid}: |{''.join(lines[sid])}|")
    out.append(f"Kollision: |{''.join(kollision_marker)}|")
    out.append("Legende:   '=' erfolgreich, 'X' kollidiert, "
               "'*' selber-Kanal-Ueberlappung, '!' Kollisions-Zeitpunkt")
    return "\n".join(out)


# -------------------------------------------------------------------------
# Nuetzliches: Zeitachsen-Beispiel fuer ein kurzes Demo-Setup
# -------------------------------------------------------------------------

def demo_transmissions(seed: int = 7) -> List[Transmission]:
    """
    Erzeugt ein winziges Beispiel: 3 Sender, je 2 Pakete, Dauer 10 -
    ideal zum Rendern mit `render_timeline`.
    """
    result = simulate_pure_aloha(
        n_senders=3,
        packets_per_sender=2,
        duration=10.0,
        packet_length=1.0,
        seed=seed,
    )
    # Wir muessten die Transmissions eigentlich zurueckliefern, aber
    # `simulate_pure_aloha` gibt nur den zusammengefassten Simult zurueck.
    # Fuer eine Demo-Variante bauen wir sie explizit nochmal:
    rng = random.Random(seed)
    ts: List[Transmission] = []
    for s in range(3):
        for _ in range(2):
            start = rng.uniform(0.0, 10.0)
            ts.append(Transmission(sender_id=s, start_time=start, end_time=start + 1.0))
    # Kollisionen bestimmen (Zeitueberlappung != selber Sender)
    ts.sort(key=lambda t: t.start_time)
    for i, t in enumerate(ts):
        col = False
        for other in ts:
            if other is t or other.sender_id == t.sender_id:
                continue
            if not (other.end_time <= t.start_time or other.start_time >= t.end_time):
                col = True
                break
        t.succeeded = not col
    return ts
