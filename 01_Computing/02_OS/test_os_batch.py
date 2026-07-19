"""Headless-Test fuer os_batch: das OS ist selbst ein Assembler-Programm.

Erwartetes Verhalten:
  * OS bei BP=0 startet, inkrementiert RAM[0] von 0 auf 1, springt via
    SETBP nach BP=1 (Job 1).
  * Job 1 rechnet 3+4=7, schreibt in RAM[1], macht HLT -> zurueck ans OS.
  * OS macht RAM[0] von 1 auf 2, springt nach BP=2 (Job 2).
  * Job 2 zaehlt bis 4, schreibt in RAM[2], macht HLT -> zurueck ans OS.
  * OS macht RAM[0] auf 3, springt nach BP=3 -- der Slot ist leer,
    trifft sofort HLT -> zurueck ans OS -> weiter durch alle leeren
    Slots bis zum Wrap.
  * Wir laufen fuer eine begrenzte Zahl an Ticks; die essentiellen
    Effekte muessen frueh sichtbar sein.
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cpu_sim import core, asm, config_batch_os
from os_batch import build_prog_rom, load_asm, SLOT_SIZE, EMPTY_CELL


HERE = os.path.dirname(__file__)
config = config_batch_os.build_cpu_config()
valid  = set(config["microcode"].keys())

os_prog = load_asm(os.path.join(HERE, "src", "programs", "os.asm"),   valid)
job1    = load_asm(os.path.join(HERE, "src", "programs", "job1.asm"), valid)
job2    = load_asm(os.path.join(HERE, "src", "programs", "job2.asm"), valid)

rom = build_prog_rom(os_prog, [job1, job2])
cpu = core.CPU(config, rom)

# Zaehle, wie oft welcher BP-Slot besucht wurde (fuer Diagnose)
bp_visits = {i: 0 for i in range(16)}
prev_bp = -1
os_completions = 0     # wie oft ist das OS neu gestartet (BP=0, PC=0)?

MAX_TICKS = 500
for _ in range(MAX_TICKS):
    if cpu.halted:
        break
    # OS-Startpunkt erkennen: FETCH-Phase bei BP=0, PC=0
    if cpu.cu.step == 0 and cpu.bp.value == 0 and cpu.pc.value == 0 \
            and prev_bp != 0:
        os_completions += 1
    bp_visits[cpu.bp.value] += 1
    prev_bp = cpu.bp.value
    cpu.tick()

# ------------------- Ergebnisse ------------------------------
print(f"Batch-OS lief {cpu.tick_counter} Ticks. halted={cpu.halted}.\n")
print(f"RAM[0] (last_index)  = {cpu.ram.cells[0]:X}")
print(f"RAM[1] (job1 output) = {cpu.ram.cells[1]:X}")
print(f"RAM[2] (job2 output) = {cpu.ram.cells[2]:X}")
print(f"OS-Runs (BP=0-Besuche) = {os_completions}")
print(f"BP-Visits: " + "  ".join(
    f"{k:X}:{v}" for k, v in bp_visits.items() if v > 0))
print(f"letzter OUT-Wert     = {cpu.out_reg.value:X}\n")

# ------------------- Asserts ---------------------------------
# job1 muss RAM[1] auf 7 gesetzt haben (3+4)
assert cpu.ram.cells[1] == 7, \
    f"job1 hat RAM[1] nicht auf 7 gesetzt (ist: {cpu.ram.cells[1]})"

# job2 muss RAM[2] auf 4 gesetzt haben (Schleife 0..4)
assert cpu.ram.cells[2] == 4, \
    f"job2 hat RAM[2] nicht auf 4 gesetzt (ist: {cpu.ram.cells[2]})"

# Das OS muss mindestens 2x gestartet sein (fuer job1 und job2),
# realistisch sogar deutlich oefter, weil es durch leere Slots wandert.
assert os_completions >= 2, \
    f"OS ist nur {os_completions}x gestartet (erwartet: >= 2)"

# BP=1 und BP=2 muessen besucht worden sein
assert bp_visits[1] > 0, "BP=1 (job1) wurde nie besucht"
assert bp_visits[2] > 0, "BP=2 (job2) wurde nie besucht"

# BP=3..F sind leer -> muessen ebenfalls besucht worden sein
# (das OS marschiert monoton durch alle Slots durch)
assert any(bp_visits[i] > 0 for i in range(3, 16)), \
    "Kein leerer Slot wurde besucht (OS scheint nicht weiterzumachen)"

print("OK: OS-Programm hat Job1 (3+4=7) und Job2 (Schleife bis 4) "
      "erfolgreich ausgefuehrt, danach durch leere Slots gewandert.")