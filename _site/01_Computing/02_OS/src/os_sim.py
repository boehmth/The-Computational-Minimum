"""os_sim -- Runner fuer das Mini-OS-Kapitel.

Startet zwei Prozesse (Default: count_up + count_down) auf einer
Two-Register-CPU mit SEG-Register und laesst das Mini-OS
zwischen ihnen wechseln.

Aufruf:
    python os_sim.py                       # Default: count_up + count_down
    python os_sim.py prog_a.asm prog_b.asm # eigene .asm-Files
"""
import os
import sys
import time

# Fuer die Box-Zeichen unter Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from cpu_sim import core, asm, config_two_reg_seg
from cpu_sim.core import (goto, clear_screen, c, vpad, vlen, Panel,
                          DecoderView, ProgramMemoryView, Element)
from cpu_sim.mini_os import MiniOS


# ============================================================
# Zusaetzliche Anzeige: Prozess-Tabelle
# ============================================================

class ProcessTableView(Element):
    """Zeigt die Prozess-Tabelle aus dem OS-Segment (SEG=0)."""
    def __init__(self, x, y, os_):
        self.os_ = os_
        # 1 Kopf + n Prozesse + 1 Zeile Statistik = n+2, plus Rahmen
        super().__init__(x, y, width=52,
                         height=len(os_.processes) + 4,
                         name="Prozess-Tabelle")

    def render(self):
        lines = [c(" pid  name         SEG   PC   AX   BX   status", "white")]
        for p in self.os_.processes:
            active = (p.pid == self.os_.current)
            status = c("HLT", "red") if p.halted else \
                     (c("RUN", "bgreen") if active else c("...", "gray"))
            base = p.pid * self.os_.SLOT_SIZE
            # Angezeigte Werte kommen aus dem OS-Segment (falls Prozess
            # NICHT gerade laeuft) oder direkt aus den CPU-Registern.
            if active:
                pc, ax, bx, seg = (self.os_.cpu.pc.value,
                                   self.os_.cpu.acc.value,
                                   self.os_.cpu.tmp.value,
                                   self.os_.cpu.seg.value)
            else:
                cells = self.os_.cpu.ram.cells
                pc  = cells[base + self.os_.OFFSET_PC]
                ax  = cells[base + self.os_.OFFSET_AX]
                bx  = cells[base + self.os_.OFFSET_BX]
                seg = cells[base + self.os_.OFFSET_SEG]
            marker = c("►", "byellow") if active else " "
            row_color = "byellow" if active else "gray"
            lines.append(c(
                f" {marker} {p.pid}   {p.name:<10}  {seg:X}    "
                f"{pc:X}    {ax:X}    {bx:X}   ", row_color) + status)
        # Statistik
        lines.append("")
        stats = "  ".join(
            f"{p.name}: {p.yields} yields, {p.ticks_used} ticks"
            for p in self.os_.processes)
        lines.append(c(" " + stats, "gray"))
        self.height = len(lines) + 2
        return self.framed(lines, frame_color="white")


# ============================================================
# Runner-Loop
# ============================================================

def load_program(path, valid_opcodes):
    with open(path, "r", encoding="utf-8") as f:
        return asm.parse_asm(f.read(), valid_opcodes)


def main(argv):
    args = argv[1:]

    # Config bauen
    config = config_two_reg_seg.build_cpu_config()
    valid  = set(config["microcode"].keys())

    # Zwei Programme laden
    if len(args) >= 2:
        prog_a_path, prog_b_path = args[0], args[1]
    else:
        prog_a_path = os.path.join(HERE, "programs", "count_up.asm")
        prog_b_path = os.path.join(HERE, "programs", "count_down.asm")

    prog_a = load_program(prog_a_path, valid)
    prog_b = load_program(prog_b_path, valid)

    # CPU + OS
    cpu = core.CPU(config, prog_a)      # Program-Ptr wird vom OS gesetzt
    os_ = MiniOS(cpu, [
        (os.path.basename(prog_a_path).replace(".asm", ""), prog_a),
        (os.path.basename(prog_b_path).replace(".asm", ""), prog_b),
    ])

    # Panel + Views
    panel = Panel()
    for e in cpu.elements.values():
        panel.add(e)
    panel.add(cpu.seg)     # SEG separat, weil nicht im elements-Dict
    panel.add(cpu.cu)

    # Decoder unter CU/RAM
    DEC_Y = max(cpu.cu.y + cpu.cu.height,
                (cpu.ram.y + cpu.ram.height) if cpu.ram else 0) + 1
    decoder = DecoderView(1, DEC_Y, cpu)
    panel.add(decoder)

    # Prozess-Tabelle rechts neben dem Decoder
    proc_table = ProcessTableView(decoder.x + decoder.width + 2, DEC_Y, os_)
    panel.add(proc_table)

    # Programmspeicher wird bei Kontext-Switch dynamisch neu erzeugt
    # (weil sich cpu.program aendert und der PROG-View seine Groesse
    # aus len(cpu.program) berechnet). Wir zeichnen ihn manuell in
    # der Loop, statt ihn ins Panel zu stecken.
    prog_view_x = proc_table.x
    prog_view_y = proc_table.y + proc_table.height + 1

    clear_screen()
    # Kopfzeile
    title = f"══ Mini-OS  [{config.get('name', '?')}] "
    goto(1, 1)
    print(c(title + "═" * max(0, cpu.layout_width - len(title)), "white"))

    STATUS_Y = max(DEC_Y + decoder.height,
                   prog_view_y + 10) + 1

    tick_delay = 0.4
    MAX_TICKS = 500

    while not os_.all_halted() and cpu.tick_counter < MAX_TICKS:
        os_.tick()
        panel.update()
        cpu.draw_bus()

        # Programmspeicher-View des aktuellen Prozesses zeichnen
        # (in einer eigenen y-Position, damit sich die Zeilenzahl
        # nicht mit dem Rest ueberlappt)
        pv = ProgramMemoryView(prog_view_x, prog_view_y, cpu)
        pv.draw()

        # Statuszeile
        goto(1, STATUS_Y)
        print(c("─" * cpu.layout_width, "gray"))
        goto(1, STATUS_Y + 1)
        proc = os_.processes[os_.current]
        pid_str = c(f"{os_.current} ({proc.name})", "byellow")
        seg_str = c(f"{cpu.seg.value:X}", "bmagenta")
        pc_str  = c(f"{cpu.pc.value:X}", "byellow")
        yielded = c("YIELD", "bmagenta") if cpu.yielded else "     "
        print(f"  active pid={pid_str}   SEG={seg_str}   PC={pc_str}   "
              f"tick={cpu.tick_counter:<3}  {yielded}      ")

        sys.stdout.flush()
        time.sleep(tick_delay)

    goto(1, STATUS_Y + 3)
    print(c(" ► Alle Prozesse angehalten. ", "red"))
    goto(1, STATUS_Y + 5)


if __name__ == "__main__":
    main(sys.argv)