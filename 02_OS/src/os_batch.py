"""os_batch -- Runner fuer das *echte* OS-Programm (Weg 2).

Waehrend `os_sim.py` das MiniOS in Python realisiert (kooperatives
Multitasking, Segment-Register), zeigt dieser Runner die
konsequente Alternative: das OS ist selbst ein Assembler-Programm,
das im Programmspeicher bei BP=0 liegt und aus den 16 Opcodes der
CPU besteht.

Konzept:
  * PROG-ROM hat 256 Zellen (16 Slots à 16 Instruktionen).
  * Slot BP=0 haelt das OS-Programm (`programs/os.asm`).
  * Slots BP=1..F halten die Jobs, die auf der Kommandozeile
    uebergeben werden (oder Default: job1 + job2).
  * Uninitialisierte Zellen enthalten (HLT, 0) — dadurch kehrt ein
    "leerer" Slot sofort ins OS zurueck.
  * Der Runner tickt einfach die CPU. Alle Umschaltungen zwischen
    OS und User macht die CPU-Hardware (BP + HLT-Trap + SETBP).

Aufruf:
    python os_batch.py                     # Default: job1 + job2
    python os_batch.py j1.asm j2.asm ...   # eigene Jobs (bis zu 15)
"""
import os
import sys
import time

# UTF-8 fuer Box-Zeichen unter Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from cpu_sim import core, asm, config_batch_os
from cpu_sim.core import (goto, clear_screen, c, vpad, Panel,
                          DecoderView, Element)


# ============================================================
# Programmspeicher-Layout (256 Zellen, 16 Slots à 16 Instruktionen)
# ============================================================

SLOT_SIZE = 16
NUM_SLOTS = 16
PROG_SIZE = SLOT_SIZE * NUM_SLOTS   # 256

# Fuer "leere" Zellen: HLT mit Operand 0. Kommt vor allem dort vor,
# wo kein Job geladen ist -- die CPU trifft dann sofort HLT und
# kehrt ins OS zurueck.
EMPTY_CELL = ("HLT", 0)


def load_asm(path, valid_opcodes):
    with open(path, "r", encoding="utf-8") as f:
        return asm.parse_asm(f.read(), valid_opcodes)


def build_prog_rom(os_prog, jobs):
    """256-Zellen-ROM aus OS + Jobs zusammensetzen.

    os_prog: Liste (opcode, operand) fuer BP=0. Muss <= 16 sein.
    jobs:    Liste von Listen (opcode, operand). Erster Job -> BP=1, usw.
             Max. 15 Jobs.
    """
    if len(os_prog) > SLOT_SIZE:
        raise ValueError(f"OS ist {len(os_prog)} Instruktionen lang, "
                         f"maximal {SLOT_SIZE} erlaubt.")
    if len(jobs) > NUM_SLOTS - 1:
        raise ValueError(f"Zu viele Jobs: {len(jobs)}, max {NUM_SLOTS-1}.")

    rom = [EMPTY_CELL] * PROG_SIZE

    # OS bei Offset 0
    for i, instr in enumerate(os_prog):
        rom[i] = instr

    # Jobs bei Offset 16*bp fuer bp=1..
    for bp_idx, job in enumerate(jobs, start=1):
        if len(job) > SLOT_SIZE:
            raise ValueError(f"Job #{bp_idx} ist {len(job)} Instruktionen "
                             f"lang, maximal {SLOT_SIZE} erlaubt.")
        base = bp_idx * SLOT_SIZE
        for i, instr in enumerate(job):
            rom[base + i] = instr

    return rom


# ============================================================
# Anzeigen: Slot-Table (welcher Slot hat welchen Job?)
# ============================================================

class SlotTableView(Element):
    """Zeigt die 16 PROG-Slots + welcher gerade aktiv ist (via BP)."""
    def __init__(self, x, y, cpu, slot_names):
        self.cpu = cpu
        self.slot_names = slot_names   # dict {bp_index: name}
        super().__init__(x, y, width=44, height=NUM_SLOTS + 3,
                         name="PROG-ROM Slots")

    def render(self):
        cur_bp = self.cpu.bp.value if self.cpu.bp else 0
        lines = [c(" BP  Slot-Inhalt                       ", "white")]
        for bp in range(NUM_SLOTS):
            # Zaehle nicht-leere Zellen in diesem Slot
            base = bp * SLOT_SIZE
            used = sum(1 for i in range(SLOT_SIZE)
                       if self.cpu.program[base + i] != EMPTY_CELL)
            name = self.slot_names.get(bp, "")
            if not name and used == 0:
                name = "(leer)"
            elif not name:
                name = "(unbekannt)"
            marker = c("►", "byellow") if bp == cur_bp else " "
            row_color = "byellow" if bp == cur_bp else \
                        ("gray" if used == 0 else "white")
            lines.append(c(
                f" {marker} {bp:X}  {name:<24}  {used:2d}/16 Instr",
                row_color))
        return self.framed(lines, frame_color="white")


# ============================================================
# Main
# ============================================================

def main(argv):
    args = argv[1:]

    config = config_batch_os.build_cpu_config()
    valid  = set(config["microcode"].keys())

    # OS immer aus programs/os.asm
    os_path = os.path.join(HERE, "programs", "os.asm")
    os_prog = load_asm(os_path, valid)

    # Jobs: entweder von Kommandozeile oder Default
    if args:
        job_paths = args
    else:
        job_paths = [
            os.path.join(HERE, "programs", "job1.asm"),
            os.path.join(HERE, "programs", "job2.asm"),
        ]

    jobs = [load_asm(p, valid) for p in job_paths]
    slot_names = {0: "os (kernel)"}
    for i, p in enumerate(job_paths, start=1):
        slot_names[i] = os.path.basename(p).replace(".asm", "")

    # ROM zusammensetzen
    rom = build_prog_rom(os_prog, jobs)

    # CPU mit ROM
    cpu = core.CPU(config, rom)

    # Panel + Views
    panel = Panel()
    for e in cpu.elements.values():
        panel.add(e)
    panel.add(cpu.bp)      # BP separat, weil nicht im elements-Dict
    panel.add(cpu.cu)

    DEC_Y = max(cpu.cu.y + cpu.cu.height,
                (cpu.ram.y + cpu.ram.height) if cpu.ram else 0) + 1
    decoder = DecoderView(1, DEC_Y, cpu)
    panel.add(decoder)

    slot_view = SlotTableView(decoder.x + decoder.width + 2, DEC_Y,
                              cpu, slot_names)
    panel.add(slot_view)

    clear_screen()
    title = f"══ Batch-OS  [{config.get('name', '?')}] "
    goto(1, 1)
    print(c(title + "═" * max(0, cpu.layout_width - len(title)), "white"))

    STATUS_Y = DEC_Y + max(decoder.height, slot_view.height) + 1

    tick_delay = 0.15
    MAX_TICKS = 2000

    while not cpu.halted and cpu.tick_counter < MAX_TICKS:
        cpu.tick()
        panel.update()
        cpu.draw_bus()

        # Statuszeile
        goto(1, STATUS_Y)
        print(c("─" * cpu.layout_width, "gray"))
        goto(1, STATUS_Y + 1)
        bp_v = cpu.bp.value
        cur_name = slot_names.get(bp_v, "?")
        mode = c("KERNEL", "bmagenta") if bp_v == 0 else c("USER", "bgreen")
        pc_str = c(f"{cpu.pc.value:X}", "byellow")
        bp_str = c(f"{bp_v:X}", "bmagenta")
        ax_str = c(f"{cpu.acc.value:X}", "bmagenta")
        bx_str = c(f"{cpu.tmp.value:X}", "byellow")
        out_str = c(f"{cpu.out_reg.value:X}", "bcyan")
        print(f"  mode={mode}  BP={bp_str}  PC={pc_str}  "
              f"AX={ax_str} BX={bx_str} OUT={out_str}  "
              f"slot='{cur_name}'  tick={cpu.tick_counter:<4}      ")

        sys.stdout.flush()
        time.sleep(tick_delay)

    goto(1, STATUS_Y + 3)
    if cpu.halted:
        print(c(" ► OS hat selbst HLT ausgefuehrt -- System heruntergefahren.",
                "red"))
    else:
        print(c(f" ► MAX_TICKS ({MAX_TICKS}) erreicht -- Abbruch.",
                "byellow"))
    goto(1, STATUS_Y + 5)


if __name__ == "__main__":
    main(sys.argv)