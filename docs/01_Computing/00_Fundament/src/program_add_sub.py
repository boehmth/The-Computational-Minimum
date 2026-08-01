r"""
program_add_sub.py - Turing-Maschine, die (3 + 4) - 1 = 6 rechnet

Dieses Programm ist die didaktische Bruecke zum Kapitel 01 (4-Bit-CPU):
DIESELBE Aufgabe, die dort in wenigen Assembler-Instruktionen erledigt
wird, laeuft hier als Turing-Maschine mit rund 30 Schritten und einer
kleinen Zustandstabelle. Man sieht damit auf einen Blick, warum die
Turing-Maschine ein herrliches Beweiswerkzeug, aber ein absurder Bauplan
fuer einen Rechner ist.

UNAeRE KODIERUNG
================

Zahlen werden nicht binaer, sondern durch Anzahl der Striche dargestellt:

    3  -->  '|||'
    4  -->  '||||'
    1  -->  '|'

Rechenoperationen sind Markierungen im Band:

    +  =  Addition (zwei Strich-Bloecke zusammenschieben)
    -  =  Subtraktion (rechten Block vom linken Block abziehen)
    _  =  leere Zelle (bei uns 'Blank')

DAS BAND (16 Zellen)
====================

Position:   0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
Initial:    |  |  |  +  |  |  |  |  -  |  _  _  _  _  _  _
                        \___3___/   \___4___/   \_1_/
                         (das ist gerade 8 Striche + '+' + '-')

Erwartetes Endergebnis (nach dem Halt):

Position:   0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
End:        |  |  |  _  |  |  |  _  _  _  _  _  _  _  _  _
                        (6 Striche insgesamt = 6)

Die 6 Striche liegen bewusst NICHT direkt nebeneinander. Um sie fuer
menschliche Augen "sauber" nach links zu schieben, braeuchte es weitere
15-20 Schritte reinen Bandtransport. Wir verzichten darauf: das
"Zaehle die Striche" ist inhaltlich vollstaendig, und der Kontrast zur
CPU (dort ist das Ergebnis einfach in einem Register) wird umso
deutlicher.

DIE ZUSTANDSTABELLE
===================

     Zustand         gelesen  ->  geschrieben  Bewegung  neuer Zustand
     ---------------------------------------------------------------
     ADD_PLUS         |            |             R         ADD_PLUS
     ADD_PLUS         +            _             R         SUB_MINUS

     SUB_MINUS        |            |             R         SUB_MINUS
     SUB_MINUS        _            _             R         SUB_MINUS
     SUB_MINUS        -            -             L         SUB_DEL_LEFT

     SUB_DEL_LEFT     |            _             R         SUB_ERASE_MINUS

     SUB_ERASE_MINUS  -            _             R         SUB_DEL_RIGHT

     SUB_DEL_RIGHT    |            _             L         SHIFT_HOME
     SUB_DEL_RIGHT    _            _             L         SUB_DEL_RIGHT

     SHIFT_HOME       |            |             L         SHIFT_HOME
     SHIFT_HOME       _            _             L         SHIFT_HOME
     ; Sonderfall: bei Position 0 fangen L-Bewegungen nicht mehr
     ; (siehe TuringMachine.step). Wir loesen ab wenn Kopf==0 UND wir
     ; auf einem Strich sind (oder auch nicht, egal) -> HALT.

Wir realisieren HALT in SHIFT_HOME dadurch, dass wir einen kuenstlichen
Zaehler nutzen: wenn wir 10-mal 'L' probieren und uns nicht mehr
bewegen, dann sind wir am Bandrand. Simpler ist aber: wir zaehlen die
Regel-Anwendungen in SHIFT_HOME nach, und der Runner setzt HALT, sobald
Kopf bei 0 UND Zustand SHIFT_HOME.
"""

from __future__ import annotations

import argparse
import sys

# Der Kern-Simulator liegt neben dieser Datei; Import per relativem Pfad.
from turing_machine import TuringMachine, run


# -------------------------------------------------------------------------
# Die Zustandstabelle
# -------------------------------------------------------------------------

def build_transition_table():
    """
    Baut das Regelwerk fuer '(3 + 4) - 1 = 6' auf 16 Bandzellen.

    Wir benutzen einen extra Zustand HALT (Endzustand), und einen
    Zustand HOME_DONE fuer 'Kopf bei 0 angekommen'.
    """
    T = {}

    # -------- Phase A: Addition ('+' loeschen) --------
    T[("ADD_PLUS", "|")] = ("|", "R", "ADD_PLUS")   # ueber '|' laufen
    T[("ADD_PLUS", "+")] = ("_", "R", "SUB_MINUS")  # '+' verschwindet

    # -------- Phase B: '-' finden --------
    T[("SUB_MINUS", "|")] = ("|", "R", "SUB_MINUS")
    T[("SUB_MINUS", "_")] = ("_", "R", "SUB_MINUS")
    T[("SUB_MINUS", "-")] = ("-", "L", "SUB_DEL_LEFT")

    # -------- Phase C: einen '|' links vom '-' loeschen --------
    # Damit realisieren wir "eine Einheit weniger im linken Block".
    T[("SUB_DEL_LEFT", "|")] = ("_", "R", "SUB_ERASE_MINUS")
    # (Wenn dort kein '|' waere, waere unsere Kodierung inkonsistent.)

    # -------- Phase D: '-' selbst loeschen --------
    T[("SUB_ERASE_MINUS", "-")] = ("_", "R", "SUB_DEL_RIGHT")

    # -------- Phase E: alle '|' rechts vom (ehemaligen) '-' loeschen --------
    # (Bei uns nur einer, aber allgemein gehalten.)
    T[("SUB_DEL_RIGHT", "|")] = ("_", "R", "SUB_DEL_RIGHT")
    T[("SUB_DEL_RIGHT", "_")] = ("_", "L", "SHIFT_HOME")

    # -------- Phase F: zurueck zur Startposition --------
    # Der Kopf wandert nach links; bei Position 0 wird L zu 'stehenbleiben'
    # (siehe TuringMachine.step), aber der Zustand aendert sich weiter.
    # Wir brauchen einen expliziten Halte-Trigger: erkenne 'Anfang' als
    # 'stehe auf | mit Zustand SHIFT_HOME'.
    T[("SHIFT_HOME", "|")] = ("|", "L", "SHIFT_HOME_MAYBE")
    T[("SHIFT_HOME", "_")] = ("_", "L", "SHIFT_HOME")

    # -------- Phase G: Halt-Check --------
    # SHIFT_HOME_MAYBE stellt fest, ob wir gerade EINEN Schritt weiter
    # links moeglich waren. Wenn wir wieder auf '|' stehen, sind wir
    # noch nicht ganz links (es gibt weitere Striche links von uns).
    # Wenn wir auf '_' stehen, waere das seltsam (Loch mitten in der
    # Zahl); in unserer Kodierung passiert das nicht direkt. Wir
    # unterscheiden einfach: bleibe im Shift-Loop bis wir mehrere
    # aufeinanderfolgende Schritte gleiches Ergebnis sehen -> HALT.
    #
    # Vereinfachung: nach einem einzelnen "L" pruefen wir einfach die
    # Kopfposition. Das machen wir im Wrapper unten, siehe run_with_halt.

    T[("SHIFT_HOME_MAYBE", "|")] = ("|", "L", "SHIFT_HOME_MAYBE")
    T[("SHIFT_HOME_MAYBE", "_")] = ("_", "L", "SHIFT_HOME_MAYBE")

    return T


# -------------------------------------------------------------------------
# Wrapper fuer den Halt-Check
# -------------------------------------------------------------------------

def run_with_halt(machine: TuringMachine, mode: str, delay: float) -> None:
    """
    Wrapper um `run`, der zusaetzlich anhaelt, sobald der Kopf auf
    Position 0 steht und der Zustand SHIFT_HOME oder SHIFT_HOME_MAYBE ist.

    Grund: unsere Zustandstabelle 'weiss' nicht, wo der Bandanfang ist.
    Der Kopf kann bei L-Bewegungen an Position 0 haengenbleiben (siehe
    TuringMachine.step); wir erkennen diesen Zustand extern.
    """
    from turing_machine import _clear_screen, RESET, FG_STATE, FG_RULE, BOLD, DIM
    import time as _time

    def is_effectively_halted(m):
        return (m.head == 0
                and m.state in ("SHIFT_HOME", "SHIFT_HOME_MAYBE"))

    _clear_screen()
    print(machine.render())
    if mode == "step":
        try:
            input(f"\n{DIM}[Enter fuer naechsten Schritt]{RESET}")
        except (EOFError, KeyboardInterrupt):
            return

    while not machine.is_halted() and machine.step_count < 500:
        machine.step()
        # Halt-Erkennung
        if is_effectively_halted(machine):
            machine.state = "HALT"
            machine.halt_states.append("HALT")
        _clear_screen()
        print(machine.render())
        if machine.is_halted():
            break
        if mode == "step":
            try:
                input(f"\n{DIM}[Enter fuer naechsten Schritt]{RESET}")
            except (EOFError, KeyboardInterrupt):
                return
        else:
            _time.sleep(delay)

    # Auswertung
    print()
    tape_str = "".join(machine.tape)
    n_strokes = tape_str.count("|")
    print(f"{FG_STATE}{BOLD}✓ Rechnung abgeschlossen.{RESET}")
    print(f"  Bandinhalt : [{tape_str}]")
    print(f"  Anzahl '|' : {n_strokes}   (erwartet: 6)")
    print(f"  Schritte   : {machine.step_count}")
    if n_strokes == 6:
        print(f"  {FG_STATE}(3 + 4) - 1 = 6  ✓{RESET}")
    else:
        print(f"  {FG_RULE}(3 + 4) - 1 = ?  Fehler!{RESET}")


# -------------------------------------------------------------------------
# Initial-Band bauen und Maschine starten
# -------------------------------------------------------------------------

def build_initial_tape(n_cells: int = 16):
    """
    Baut das Anfangsband fuer (3 + 4) - 1.

    Position:   0  1  2  3  4  5  6  7  8  9  10 ...
    Inhalt:     |  |  |  +  |  |  |  |  -  |  _  ...
    """
    tape = ["_"] * n_cells
    tape[0] = "|"
    tape[1] = "|"
    tape[2] = "|"
    tape[3] = "+"
    tape[4] = "|"
    tape[5] = "|"
    tape[6] = "|"
    tape[7] = "|"
    tape[8] = "-"
    tape[9] = "|"
    return tape


def main():
    # Windows-Konsole auf UTF-8 umstellen, damit Box-Zeichen (┌┬┐│└┴┘)
    # und Pfeile (←→•) korrekt gerendert werden.
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass  # aeltere Python-Version oder anderer Stream-Typ

    parser = argparse.ArgumentParser(
        description="Turing-Maschine, die (3 + 4) - 1 = 6 rechnet."
    )
    parser.add_argument(
        "--step", action="store_true",
        help="Nach jedem Schritt Enter druecken (didaktischer Modus).")
    parser.add_argument(
        "--delay", type=float, default=0.35,
        help="Pause in Sekunden zwischen den Schritten (nur im Auto-Modus).")
    parser.add_argument(
        "--fast", action="store_true",
        help="Kurzform fuer --delay=0.05.")
    args = parser.parse_args()

    mode = "step" if args.step else "auto"
    delay = 0.05 if args.fast else args.delay

    tape = build_initial_tape(n_cells=16)
    machine = TuringMachine(
        tape=tape,
        state="ADD_PLUS",
        halt_states=[],   # wird vom Wrapper dynamisch gesetzt
        table=build_transition_table(),
        head=0,
    )

    print()
    print("=" * 72)
    print("Turing-Maschine  ·  Aufgabe: (3 + 4) - 1 = 6  (unaere Kodierung)")
    print("=" * 72)
    print("Band initial:")
    print("  Positionen 0..2 : 3 Striche         (die Zahl 3)")
    print("  Position   3    : '+'               (Additionszeichen)")
    print("  Positionen 4..7 : 4 Striche         (die Zahl 4)")
    print("  Position   8    : '-'               (Subtraktionszeichen)")
    print("  Position   9    : 1 Strich          (die Zahl 1)")
    print("  Positionen 10.. : leer              ('_' = Blank)")
    print()
    print("Erwartetes Endergebnis: 6 Striche irgendwo auf dem Band.")
    print("=" * 72)
    print()

    run_with_halt(machine, mode=mode, delay=delay)


if __name__ == "__main__":
    main()
