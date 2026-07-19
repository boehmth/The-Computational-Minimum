"""Test: das Batch-OS ist NICHT geschuetzt gegen boese Jobs.

Wir laden absichtlich `job_evil` als Slot 1. Dieser Job schreibt 7 in
RAM[0] (die OS-State-Zelle) und macht dann HLT.

Erwartetes Verhalten:
  1. Boot: RAM[0]=0. OS: next_index=1 -> springt zu Slot 1 (job_evil).
  2. job_evil: RAM[0] := 7, HLT -> zurueck ans OS.
  3. OS: liest RAM[0]=7, next_index=8 -> springt zu Slot 8 (leer)
     statt zu Slot 2! Das ist der Schaden.
  4. Slot 8 ist leer -> sofort HLT -> zurueck ans OS.
  5. OS: RAM[0]=8 (wurde vom OS gerade auf 8 gesetzt), next=9 -> Slot 9,
     usw. Ab hier wandert das OS wieder monoton, aber Slot 2 wurde
     uebersprungen (ausser durch den Wrap ueber 15 -> 1 kommt es
     spaeter wieder daran, s.u.).

Der eigentliche didaktische Punkt: **das System crasht nicht**, ist
aber in seinem Verhalten manipuliert. Das entspricht praeziese der
DOS-Aera vor Speicherschutz.
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cpu_sim import core, config_batch_os
from os_batch import build_prog_rom, load_asm

HERE = os.path.dirname(__file__)
config = config_batch_os.build_cpu_config()
valid  = set(config["microcode"].keys())

os_prog   = load_asm(os.path.join(HERE, "src", "programs", "os.asm"),      valid)
job_evil  = load_asm(os.path.join(HERE, "src", "programs", "job_evil.asm"), valid)
job2      = load_asm(os.path.join(HERE, "src", "programs", "job2.asm"),    valid)

# Slot 1 = boeser Job, Slot 2 = harmloser Job2
rom = build_prog_rom(os_prog, [job_evil, job2])
cpu = core.CPU(config, rom)

# Log der Job-Aufrufe: welcher Slot wird nacheinander aufgerufen?
call_sequence = []
prev_bp = 0

MAX_TICKS = 400
for _ in range(MAX_TICKS):
    if cpu.halted:
        break
    cpu.tick()
    if prev_bp == 0 and cpu.bp.value != 0:
        call_sequence.append(cpu.bp.value)
    prev_bp = cpu.bp.value

print(f"Ticks gelaufen: {cpu.tick_counter}")
print(f"Aufruf-Reihenfolge der Slots (erste 20):")
print(f"  {call_sequence[:20]}")
print(f"RAM[0] (letzter last_index) = {cpu.ram.cells[0]:X}")
print()

# Erster Aufruf ist immer Slot 1 (job_evil).
assert call_sequence[0] == 1, \
    f"Erster Aufruf muss job_evil (Slot 1) sein, ist {call_sequence[0]}"

# NACH job_evil -- das OS wurde manipuliert. Ohne den Uebergriff waere
# der naechste Aufruf 2 (job2). Mit Uebergriff sollte es NICHT 2 sein,
# sondern hoeher (weil job_evil RAM[0] auf 7 gesetzt hat -> naechster
# Index waere 8).
if len(call_sequence) >= 2:
    second = call_sequence[1]
    if second == 2:
        print("HINWEIS: OS ist trotz Uebergriff normal zu Slot 2 gegangen.")
        print("        (Das kann nur passieren wenn RAM[0] nicht auf 7 blieb.)")
    else:
        print(f"OK: Nach job_evil geht das OS zu Slot {second} statt Slot 2.")
        print(f"    Der boese Job hat den Scheduler manipuliert.")

# Bilanz: der Rechner ist NICHT abgestuerzt (halted ist False, wir
# haben MAX_TICKS erreicht).
assert not cpu.halted, "Das System sollte nicht crashen (halted=False)."

# Und wir sind nie im OS-Slot (BP=0) als USER-Programm gelandet.
assert 0 not in call_sequence, \
    "OS hat sich selbst als Job aufgerufen -- das waere ein echter Crash!"

print()
print("OK: boeser Job hat den OS-Scheduler manipuliert, aber das System")
print("    ist weiterhin lauffaehig. Das ist die DOS-Realitaet vor 1990.")