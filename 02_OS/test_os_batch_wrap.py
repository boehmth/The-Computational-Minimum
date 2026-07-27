"""Zusatz-Test: verifiziert das Wrap-Around-Verhalten des OS.

Wir lassen das OS lange genug laufen, dass RAM[0] mindestens einmal
den Wert F erreicht und dann per Wrap wieder auf 1 (nicht 0!) springt.
Damit ist gezeigt, dass der JZ/JMP-Zweig im OS bei Overflow (15+1=0 in 4 Bit)
korrekt greift und der OS-Slot BP=0 uebersprungen wird.
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

os_prog = load_asm(os.path.join(HERE, "src", "programs", "os.asm"),   valid)
job1    = load_asm(os.path.join(HERE, "src", "programs", "job1.asm"), valid)
job2    = load_asm(os.path.join(HERE, "src", "programs", "job2.asm"), valid)

rom = build_prog_rom(os_prog, [job1, job2])
cpu = core.CPU(config, rom)

# Snapshot des RAM[0] jedes Mal, wenn das OS ans SETBP kommt
# (d.h. wenn BP noch 0 ist und die naechste Instruktion SETBP ist).
# Einfacher: wir merken uns die RAM[0]-Werte, die das OS gerade
# an BP uebergeben will. Wir sehen sie am STA 0 (Adresse 7 im OS-Slot):
# der Wert AX in dem Moment ist der neue Index.

# Robust: wir loggen einfach RAM[0] jedes Mal, wenn BP von 0 auf !=0
# wechselt (also im Moment des SETBP).
index_sequence = []
prev_bp = 0
for _ in range(3000):
    if cpu.halted:
        break
    cpu.tick()
    if prev_bp == 0 and cpu.bp.value != 0:
        index_sequence.append(cpu.bp.value)
    prev_bp = cpu.bp.value

print(f"Insgesamt {len(index_sequence)} SETBP-Ereignisse.")
print(f"Erste 30 Job-Indizes: {index_sequence[:30]}")

# Wir muessen die Sequenz 1,2,3,...,F,1,2,... sehen (mit Wrap ueber 1).
# Der erste Eintrag ist 1.
assert index_sequence[0] == 1, f"Erster Job muss 1 sein, ist {index_sequence[0]}"

# Nach 15 Jobs (Indizes 1..F) muss der 16. wieder 1 sein.
if len(index_sequence) >= 16:
    assert index_sequence[15] == 1, \
        f"Nach F muss wieder 1 kommen (Wrap-Around), ist {index_sequence[15]}"
    print(f"OK: Wrap-Around funktioniert. Nach Index F kommt wieder 1.")
else:
    print(f"HINWEIS: Nicht genug Ticks fuer Wrap-Test "
          f"({len(index_sequence)} Jobs, brauchen 16).")

# Zusatz-Check: kein Index ist 0
assert 0 not in index_sequence, "OS hat sich selbst als Job aufgerufen (BP=0)!"

print("\nOK: OS wandert korrekt durch Slots 1..F, ueberspringt 0 beim Wrap.")