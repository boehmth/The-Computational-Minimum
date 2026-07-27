"""Headless-Test: MiniOS wechselt zwischen count_up und count_down."""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cpu_sim import core, asm, config_two_reg_seg
from cpu_sim.mini_os import MiniOS


def load(path, valid):
    with open(path, "r", encoding="utf-8") as f:
        return asm.parse_asm(f.read(), valid)


HERE = os.path.dirname(__file__)
config = config_two_reg_seg.build_cpu_config()
valid  = set(config["microcode"].keys())

prog_up   = load(os.path.join(HERE, "src", "programs", "count_up.asm"),   valid)
prog_down = load(os.path.join(HERE, "src", "programs", "count_down.asm"), valid)

cpu = core.CPU(config, prog_up)   # CPU-Init: program wird spaeter vom OS gesetzt
os_ = MiniOS(cpu, [("up", prog_up), ("down", prog_down)])

# 4 Runden lang laufen lassen (jede Runde = 1 kompletter Loop-Body eines Prozesses)
# Ein Loop-Body ist ~ 20-25 Takte (jede Instruktion = 2 Takte Fetch+Execute)
MAX_TICKS = 200
for _ in range(MAX_TICKS):
    if os_.all_halted():
        break
    os_.tick()

# Ergebnisse aus den Prozess-Segmenten auslesen
seg1_val = cpu.ram.cells[1 * 16 + 0]   # count_up: RAM[0] im Segment 1
seg2_val = cpu.ram.cells[2 * 16 + 0]   # count_down: RAM[0] im Segment 2

# OS-Segment: Kontexte + aktueller Prozess
os_seg = cpu.ram.cells[0:16]

print(f"After {cpu.tick_counter} ticks:")
print(f"  Prozess 'up'   (SEG=1) -> RAM[0]={seg1_val:X}  yields={os_.processes[0].yields}")
print(f"  Prozess 'down' (SEG=2) -> RAM[0]={seg2_val:X}  yields={os_.processes[1].yields}")
print(f"  OS-Segment (SEG=0)     -> {[f'{v:X}' for v in os_seg]}")
print(f"  Current pid            -> {cpu.ram.cells[0xF]}")

# Die beiden Prozesse sollen mindestens je 2-mal geyielded haben,
# und ihre Zaehler sollen sinnvolle Werte haben (Up > 0, Down < F).
assert os_.processes[0].yields >= 2, "up hat nicht genuegend geyielded"
assert os_.processes[1].yields >= 2, "down hat nicht genuegend geyielded"
assert seg1_val > 0,  "count_up hat nicht hochgezaehlt"
assert seg2_val < 0xF, "count_down hat nicht runtergezaehlt"

# Segmente sind unabhaengig — up sieht down's Werte nicht und umgekehrt
print("\nOK: 2 Prozesse laufen alternierend, jeder in seinem eigenen Segment.")