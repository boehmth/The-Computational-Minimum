"""Perceptron auf der 4-Bit-CPU: AND, OR, NAND -- und XOR als Gegenbeispiel.

Das Programm in `src/programs/perceptron.asm` berechnet die klassische
Schwellwert-Formel eines einzelnen Neurons:

    y = 1  if  (w1*x1 + w2*x2 + b) > 0  else  0

Wir laden das Programm auf die erweiterte 2-Reg-CPU mit MUL/JN,
setzen (x1, x2, w1, w2, b) vor dem Start ins RAM, lassen laufen,
und lesen y aus OUT.

Damit klassifizieren wir alle 4 Kombinationen aus {0,1}^2 fuer
verschiedene Perceptron-Konfigurationen:

  * **AND**  (w1=1, w2=1, b=-1)   -> feuert nur bei (1,1)
  * **OR**   (w1=1, w2=1, b=0)    -> feuert bei allen ausser (0,0)
  * **NAND** (w1=-1, w2=-1, b=1)  -> feuert bei allen ausser (1,1)
  * **XOR**  -- **kein Gewichtssatz existiert**. Das ist Minskys
    beruehmtes 1969-Argument, das den ersten KI-Winter ausloeste.
    Wir demonstrieren das empirisch, indem wir zeigen: jeder
    Versuch, XOR mit einem einzelnen Perceptron zu loesen, muss
    an mindestens einer der 4 Eingabekombinationen scheitern.

RAM-Werte sind 4-Bit-Zweierkomplement: -1 ist 0xF (=1111 binaer),
weil 0xF + 1 = 0 modulo 16.
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(__file__)
# CPU-Simulator liegt in Kapitel 01_CPU (die MUL/JN-Erweiterung ist dort)
sys.path.insert(0, os.path.abspath(os.path.join(
    HERE, "..", "01_CPU", "src")))

from cpu_sim import core, asm, config_two_reg_mul


# ------------------------------------------------------------
# 4-Bit-Zweierkomplement-Helper
# ------------------------------------------------------------

def to_2k(v):
    """int (-8..7) -> 4-Bit-Zweierkomplement (0..15)."""
    if not -8 <= v <= 7:
        raise ValueError(f"{v} passt nicht in 4-Bit-Zweierkomplement")
    return v & 0xF


# ------------------------------------------------------------
# Programm einmal parsen
# ------------------------------------------------------------

CFG   = config_two_reg_mul.build_cpu_config()
VALID = set(CFG["microcode"].keys())

with open(os.path.join(HERE, "src", "programs", "perceptron.asm"),
          "r", encoding="utf-8") as f:
    PROG = asm.parse_asm(f.read(), VALID)

assert len(PROG) == 16, \
    f"Programm muss genau 16 Instruktionen haben, hat {len(PROG)}"


def run_perceptron(x1, x2, w1, w2, b, max_ticks=200):
    """Perceptron einmal ausfuehren, gibt (y, cpu) zurueck."""
    cpu = core.CPU(CFG, PROG)

    # RAM-Layout: 0=x1, 1=x2, 2=w1, 3=w2, 4=b, 5=partial
    cpu.ram.cells[0] = to_2k(x1)
    cpu.ram.cells[1] = to_2k(x2)
    cpu.ram.cells[2] = to_2k(w1)
    cpu.ram.cells[3] = to_2k(w2)
    cpu.ram.cells[4] = to_2k(b)

    for _ in range(max_ticks):
        if cpu.halted:
            break
        # Bei der reinen CPU wraps PC nach Adresse F auf 0.
        # Wir brechen sofort ab, wenn PC nach Ausfuehrung der letzten
        # Instruktion (OUT bei F=15) auf 0 wrapt -- das ist unser
        # "implizites HLT".
        cpu.tick()
        if cpu.pc.value == 0 and cpu.cu.step == 0 and cpu.tick_counter > 2:
            # Wir haben Adresse F ausgefuehrt und sind zurueck bei 0
            break

    return cpu.out_reg.value, cpu


# ------------------------------------------------------------
# Perceptron-Konfigurationen
# ------------------------------------------------------------

# Unsere Aktivierungsregel ist:  y = 1  if  sum >= 0  else  0
# (weil `JN` nur bei streng negativer Summe zum 0-Zweig springt).
# Der Bias muss deshalb so gewaehlt sein, dass "nicht-feuern"
# eine ECHT negative Summe erzeugt.

CONFIGS = [
    # (name, w1, w2, b,    expected_truth_table)
    ("AND",  1,  1, -2,   {(0,0): 0, (0,1): 0, (1,0): 0, (1,1): 1}),
    ("OR",   1,  1, -1,   {(0,0): 0, (0,1): 1, (1,0): 1, (1,1): 1}),
    ("NAND", -1, -1, 1,   {(0,0): 1, (0,1): 1, (1,0): 1, (1,1): 0}),
    # XOR-Wahrheitstabelle -- kein linear trennbarer Klassifikator
    ("XOR",  None, None, None,
                          {(0,0): 0, (0,1): 1, (1,0): 1, (1,1): 0}),
]


def eval_config(name, w1, w2, b, truth):
    """Perceptron mit (w1,w2,b) auf alle 4 Eingaben anwenden,
    vergleiche mit Wahrheitstabelle. Gibt (list_of_results, ok_count)."""
    results = []
    ok = 0
    for x1, x2 in [(0,0),(0,1),(1,0),(1,1)]:
        y, _ = run_perceptron(x1, x2, w1, w2, b)
        expected = truth[(x1,x2)]
        good = (y == expected)
        if good:
            ok += 1
        results.append((x1, x2, y, expected, good))
    return results, ok


# ------------------------------------------------------------
# Hauptteil
# ------------------------------------------------------------

print("=" * 66)
print("Perceptron auf 4-Bit-CPU  --  Boolesche Funktionen als Klassifikator")
print("=" * 66)
print()

# Fuer AND, OR, NAND: einmal durchrechnen mit den vorgegebenen Gewichten
for name, w1, w2, b, truth in CONFIGS:
    if name == "XOR":
        continue
    print(f"--- {name}  (w1={w1}, w2={w2}, b={b}) ---")
    results, ok = eval_config(name, w1, w2, b, truth)
    print(f"    x1 x2 |  y  (expected)  status")
    print(f"    ---------------------------------")
    for x1, x2, y, expected, good in results:
        mark = "✓" if good else "✗"
        print(f"     {x1}  {x2} |  {y}      ({expected})       {mark}")
    print(f"    -> {ok}/4 korrekt")
    print()
    assert ok == 4, f"{name}: nur {ok}/4 korrekt"


# ------------------------------------------------------------
# XOR: das beruehmte Minsky-Papert-Gegenbeispiel
# ------------------------------------------------------------

print("=" * 66)
print("XOR  --  das beruehmte Gegenbeispiel (Minsky & Papert 1969)")
print("=" * 66)
print()
print("Wir versuchen ALLE (w1, w2, b) im 2K-4-Bit-Bereich {-4..+3} durch.")
print("Fuer jeden Versuch zaehlen wir, wie viele der 4 Eingaben stimmen.")
print()

_, _, _, _, xor_truth = CONFIGS[3]
best_score = 0
best_cfg = None

# Wir suchen im Bereich -4..+3, das reicht didaktisch und haelt
# die MUL-Produkte im 4-Bit-Bereich (max |x*w| = 1*3 = 3).
for w1 in range(-4, 4):
    for w2 in range(-4, 4):
        for b in range(-4, 4):
            _, ok = eval_config("XOR", w1, w2, b, xor_truth)
            if ok > best_score:
                best_score = ok
                best_cfg = (w1, w2, b)

print(f"Beste gefundene Konfiguration: w1={best_cfg[0]}, w2={best_cfg[1]}, "
      f"b={best_cfg[2]}")
print(f"    ergibt {best_score}/4 richtige Antworten -- **niemals 4/4**.")
print()
print("Das ist mathematisch beweisbar (Perzeptron kann nur linear trennen).")
print("Fuer XOR braucht man mehrere Neuronen (=> MLP, Kapitel 02_MLP).")
print()

assert best_score < 4, f"XOR sollte NICHT loesbar sein, gefunden: {best_score}/4"

print("=" * 66)
print("OK: AND/OR/NAND perfekt geloest, XOR nicht loesbar mit einem Neuron.")
print("    Das ist genau die Situation, die 1969 den KI-Winter ausloeste --")
print("    und die 1986 durch Backprop und MLP ueberwunden wurde.")
print("=" * 66)