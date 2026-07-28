"""
turing_machine.py - Ein *endlicher* Turing-Maschinen-Simulator

Klassisch hat eine Turing-Maschine ein UNENDLICHES Band. Das ist im Beweis
schoen, im Bau absurd. Unsere Simulation nimmt bewusst ein ENDLICHES Band
mit fester Groesse (Default 16 Zellen) - damit man sieht, warum der Weg
von hier zur echten CPU (Kapitel 01) fast selbstverstaendlich ist:

    * Ein realer Rechner hat immer endlichen Speicher.
    * Die Turing-Maschine ist als Beweiswerkzeug gedacht, nicht als Bauplan.
    * Fuer eine 4-Bit-Zahl braucht sie in unaerer Kodierung bis zu 15 Zellen.
      Fuer eine 32-Bit-Zahl waeren es 4 Milliarden. Skalierungs-Absurditaet.

Das Modell selbst ist minimal:

    * Ein Band aus `n` Zellen mit Symbolen aus einem endlichen Alphabet.
    * Ein Kopf, der auf einer Zelle steht.
    * Ein Zustand aus einer endlichen Zustandsmenge.
    * Eine Uebergangstabelle: (Zustand, gelesenes Symbol) -> (neues Symbol,
      Kopfbewegung ('L','R','S'), Folgezustand).
    * Ein oder mehrere Endzustaende.

Das Rendering ist ein einfaches ANSI-Farb-Panel im Terminal.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

# -------------------------------------------------------------------------
# ANSI-Helfer (aehnlich Stil zu den CPU-Simulationen in 01_CPU)
# -------------------------------------------------------------------------

RESET = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"

BG_HEAD  = "\033[48;5;208m"   # orange Hintergrund unter dem Kopf
FG_HEAD  = "\033[38;5;16m"    # schwarze Schrift auf orange

FG_STATE = "\033[38;5;33m"    # blau
FG_RULE  = "\033[38;5;160m"   # rot
FG_STEP  = "\033[38;5;240m"   # dunkelgrau

BLANK_CHAR = "_"              # Symbol fuer leere Zelle


# -------------------------------------------------------------------------
# Datenstrukturen
# -------------------------------------------------------------------------

TransitionKey    = Tuple[str, str]                        # (state, read_symbol)
TransitionValue  = Tuple[str, str, str]                    # (write_symbol, move, next_state)
TransitionTable  = Dict[TransitionKey, TransitionValue]


@dataclass
class TuringMachine:
    """
    Ein einfaches, endliches Turing-Maschinen-Modell.

    Attribute:
        tape         : Liste der Bandzellen (str-Symbole der Laenge 1).
        head         : Position des Kopfs auf dem Band (0-basierter Index).
        state        : Aktueller Zustand.
        halt_states  : Menge der Endzustaende ({"HALT"} etc.).
        table        : Uebergangstabelle.
        step_count   : Anzahl bisher ausgefuehrter Schritte.
        history      : Fuer die Anzeige der zuletzt angewendeten Regel.
    """
    tape: List[str]
    state: str
    halt_states: List[str]
    table: TransitionTable
    head: int = 0
    step_count: int = 0
    last_rule: Optional[Tuple[TransitionKey, TransitionValue]] = None

    # ---------------------------------------------------------------------
    # Kern-Schritt
    # ---------------------------------------------------------------------

    def is_halted(self) -> bool:
        return self.state in self.halt_states

    def step(self) -> bool:
        """
        Fuehrt einen Schritt aus. Gibt True zurueck, wenn ein Schritt gemacht
        wurde, False wenn die Maschine bereits gehalten hat oder keine Regel
        greift (dann wird die Maschine zwangs-gehalten mit Zustand HALT_ERR).
        """
        if self.is_halted():
            return False

        read = self.tape[self.head]
        key = (self.state, read)
        if key not in self.table:
            # Keine passende Regel -> Sonder-Halt
            self.state = "HALT_ERR"
            self.last_rule = (key, ("?", "S", "HALT_ERR"))
            return False

        write, move, next_state = self.table[key]
        self.tape[self.head] = write
        if move == "L":
            self.head = max(0, self.head - 1)
        elif move == "R":
            self.head = min(len(self.tape) - 1, self.head + 1)
        # move == "S" -> stehenbleiben

        self.state = next_state
        self.step_count += 1
        self.last_rule = (key, (write, move, next_state))
        return True

    # ---------------------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------------------

    def render(self) -> str:
        """Rendert den aktuellen Maschinenzustand als mehrzeiligen String."""
        n = len(self.tape)

        # Zeile 1: obere Kante
        top = "┌" + "┬".join(["───"] * n) + "┐"
        # Zeile 2: die Zellen selbst; die Kopfposition wird hervorgehoben
        cells = []
        for i, sym in enumerate(self.tape):
            content = f" {sym} "
            if i == self.head:
                content = f"{BG_HEAD}{FG_HEAD}{BOLD} {sym} {RESET}"
            cells.append(content)
        mid = "│" + "│".join(cells) + "│"
        # Zeile 3: untere Kante
        bot = "└" + "┴".join(["───"] * n) + "┘"
        # Zeile 4: Positionsmarkierung (Zahl unter der aktuellen Zelle)
        pos = "  " + "  ".join(
            [f"{BOLD}{i:2d}{RESET}" if i == self.head else f"{DIM}{i:2d}{RESET}"
             for i in range(n)]
        )

        rule_str = ""
        if self.last_rule is not None:
            (s_from, r_from), (w, m, s_to) = self.last_rule
            arrow = {"L": "←", "R": "→", "S": "•"}.get(m, "?")
            rule_str = (
                f"{FG_RULE}Regel:{RESET}  "
                f"({s_from}, '{r_from}')  →  "
                f"schreibe '{w}',  Kopf {arrow},  Zustand {s_to}"
            )

        state_color = FG_STATE if not self.is_halted() else FG_RULE
        header = (
            f"{state_color}{BOLD}Zustand: {self.state}{RESET}"
            f"     {FG_STEP}Schritt {self.step_count}{RESET}"
        )

        return "\n".join([header, "", top, mid, bot, pos, "", rule_str])


# -------------------------------------------------------------------------
# Kleine CLI-Helfer
# -------------------------------------------------------------------------

def _clear_screen() -> None:
    """Loescht den Terminalbildschirm. Portabel: Windows und Unix."""
    os.system("cls" if os.name == "nt" else "clear")


def run(machine: TuringMachine,
        mode: str = "auto",
        delay: float = 0.35,
        max_steps: int = 500) -> None:
    """
    Fuehrt die Maschine bis zum Halt aus. Rendert nach jedem Schritt.

    Parameters
    ----------
    mode : "auto" | "step"
        "auto"  -> automatisch mit time.sleep(delay) Pause.
        "step"  -> nach jedem Schritt Enter druecken.
    delay : Pause in Sekunden zwischen den Schritten im Auto-Modus.
    max_steps : Sicherheitsobergrenze, damit die Simulation bei
                fehlerhaften Zustandstabellen nicht endlos laeuft.
    """
    # Anfangszustand rendern
    _clear_screen()
    print(machine.render())
    if mode == "step":
        try:
            input(f"\n{DIM}[Enter fuer naechsten Schritt]{RESET}")
        except (EOFError, KeyboardInterrupt):
            return

    while not machine.is_halted() and machine.step_count < max_steps:
        ok = machine.step()
        _clear_screen()
        print(machine.render())
        if not ok:
            break
        if machine.is_halted():
            break
        if mode == "step":
            try:
                input(f"\n{DIM}[Enter fuer naechsten Schritt]{RESET}")
            except (EOFError, KeyboardInterrupt):
                return
        else:
            time.sleep(delay)

    # Endzustand
    print()
    if machine.state == "HALT_ERR":
        print(f"{FG_RULE}⚠  Maschine ist ohne passende Regel gehalten.{RESET}")
    elif machine.step_count >= max_steps:
        print(f"{FG_RULE}⚠  Maximale Schrittzahl {max_steps} erreicht.{RESET}")
    else:
        print(f"{FG_STATE}{BOLD}✓ Maschine hat regulaer gehalten.{RESET}")
    print(f"  Bandinhalt : [{''.join(machine.tape)}]")
    print(f"  Schritte   : {machine.step_count}")


# -------------------------------------------------------------------------
# Selbsttest
# -------------------------------------------------------------------------

if __name__ == "__main__":
    # Minimales Beispiel: eine Maschine, die einfach nach rechts wandert
    # bis sie ein '_' findet und dann stoppt.
    tm = TuringMachine(
        tape=list("|||||___________"),
        state="RIGHT",
        halt_states=["HALT"],
        table={
            ("RIGHT", "|"): ("|", "R", "RIGHT"),
            ("RIGHT", "_"): ("_", "S", "HALT"),
        },
    )
    print("Turing-Maschine (Selbsttest, laeuft nach rechts bis '_'):")
    print()
    run(tm, mode="auto", delay=0.15)
