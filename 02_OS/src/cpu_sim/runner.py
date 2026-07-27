"""cpu_sim.runner -- Layout + Main-Loop fuer die Simulation.

Kapselt alles, was mit Bildschirm-Layout und Interaktion zu tun hat.
Bekommt eine fertige CPU (aus einer Config) und ein Programm."""
import sys
import time

from . import core
from .core import (goto, clear_screen, c, Panel, ProgramMemoryView,
                   DecoderView)


def run(cpu, source="(unknown)", tick_delay=0.6, max_ticks=500):
    """Fuehrt die CPU mit Live-Anzeige aus, bis HLT.

    Layout:
      Zeile 1:  Titel
      Zeilen 2..bus_y-1:  Bus-Elemente in einer Reihe
      Zeile bus_y:  Bus
      unter Bus:  RAM (links) + CU (rechts daneben)
      darunter:   Decoder-View (Fetch + Opcode-Tabelle)
      rechts vom Decoder auf dessen Hoehe:  Programmspeicher
      ganz unten: Statuszeile
    """
    clear_screen()

    panel = Panel()
    for e in cpu.elements.values():
        panel.add(e)
    panel.add(cpu.cu)

    # Decoder unter RAM/CU
    DEC_Y = max(cpu.cu.y + cpu.cu.height,
                (cpu.ram.y + cpu.ram.height) if cpu.ram else cpu.cu.y) + 1
    decoder = DecoderView(1, DEC_Y, cpu)
    panel.add(decoder)

    # Programmspeicher rechts NEBEN dem Decoder (nicht mehr oben rechts,
    # weil er dort mit anderen Boxen kollidieren kann)
    prog_view = ProgramMemoryView(decoder.x + decoder.width + 2, DEC_Y, cpu)
    panel.add(prog_view)

    # Kopfzeile: genau auf die Layout-Breite auffuellen
    title = f"══ 4-Bit CPU Simulator  [{cpu.config.get('name', '?')}] "
    padding = max(0, cpu.layout_width - len(title))
    goto(1, 1)
    print(c(title + "═" * padding, "white"))

    STATUS_Y = max(DEC_Y + decoder.height,
                   prog_view.y + prog_view.height) + 1

    while not cpu.halted and cpu.tick_counter < max_ticks:
        cpu.tick()
        panel.update()
        cpu.draw_bus()

        # Statuszeile ganz unten
        goto(1, STATUS_Y)
        print(c("─" * cpu.layout_width, "gray"))
        goto(1, STATUS_Y + 1)
        opc = c(cpu.cu.current_opcode, "byellow")
        opr = c(f"{cpu.cu.current_operand:X}", "byellow")
        stp = c(str(cpu.cu.step), "bmagenta")
        tck = c(str(cpu.tick_counter), "gray")
        pc  = c(f"{cpu.pc.value:X}", "byellow") if cpu.pc else "-"
        print(f"  tick={tck}   opcode={opc}   operand={opr}   "
              f"step={stp}   PC={pc}   src={c(source, 'gray')}      ")

        sys.stdout.flush()
        time.sleep(tick_delay)

    goto(1, STATUS_Y + 3)
    print(c(" ► CPU angehalten. ", "red") +
          c(_result_summary(cpu), "byellow"))
    goto(1, STATUS_Y + 5)


def _result_summary(cpu):
    parts = []
    if cpu.acc is not None:
        parts.append(f"ACC={cpu.acc.value:X}")
    if cpu.tmp is not None:
        parts.append(f"TMP={cpu.tmp.value:X}")
    if cpu.out_reg is not None:
        parts.append(f"OUT={cpu.out_reg.value:X}")
    if cpu.ram is not None:
        # zeige nicht-0 RAM-Zellen
        used = [(i, v) for i, v in enumerate(cpu.ram.cells) if v != 0]
        if used:
            parts.append("RAM=[" +
                         ", ".join(f"{i:X}:{v:X}" for i, v in used) + "]")
    return "Ergebnis: " + "  ".join(parts)


# ------------------------------------------------------------
# Headless-Variante (ohne Anzeige, fuer Tests)
# ------------------------------------------------------------
def run_headless(cpu, max_ticks=500):
    while not cpu.halted and cpu.tick_counter < max_ticks:
        cpu.tick()
    return cpu