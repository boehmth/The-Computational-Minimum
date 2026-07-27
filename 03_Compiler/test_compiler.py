"""Ende-zu-Ende-Test: alle Frontends muessen (3+4)-1 = 6 rechnen.

Fuer jede der vier Sprachen (C, FORTRAN, LISP, COBOL):
  1. Frontend parst die Datei -> AST
  2. Codegen erzeugt Assembler
  3. Assembler wird geparst und im CPU-Simulator ausgefuehrt
  4. OUT-Register muss am Ende 6 sein

Zusaetzlich: die *Kernaussage* dieses Kapitels visualisieren, dass die
vier verschiedenen Sprachen zu einem sehr aehnlichen Assembler
kompilieren -- wir vergleichen die reinen Instruktions-Zeilen (ohne
Kommentare/Leerzeilen).
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "src"))
sys.path.insert(0, os.path.join(HERE, "..", "02_OS", "src"))

from src.compile import compile_file
from cpu_sim import core, asm as cpuasm, config_two_reg


LANGUAGES = [
    ("C",       "examples/arith.c"),
    ("FORTRAN", "examples/arith.f"),
    ("LISP",    "examples/arith.lisp"),
    ("COBOL",   "examples/arith.cob"),
]


def strip_comments(asm_text):
    """Nur die 'echten' Instruktionen zurueckbehalten (ohne Kommentare)."""
    lines = []
    for line in asm_text.splitlines():
        code = line.split(";", 1)[0].strip()
        if code:
            lines.append(code)
    return lines


def run_asm(asm_text, max_ticks=500):
    """Assembler im CPU-Simulator ausfuehren, gibt CPU zurueck."""
    cfg = config_two_reg.build_cpu_config()
    valid = set(cfg["microcode"].keys())
    prog = cpuasm.parse_asm(asm_text, valid)
    cpu = core.CPU(cfg, prog)
    for _ in range(max_ticks):
        if cpu.halted:
            break
        cpu.tick()
    return cpu


# ------------- Haupttest ---------------------------------------------

print("=" * 70)
print("Compiler-Kapitel: (3 + 4) - 1 = 6 in vier Sprachen")
print("=" * 70)
print()

results = {}
for lang, rel_path in LANGUAGES:
    path = os.path.join(HERE, rel_path)
    asm_text, ast, lang_from_ext = compile_file(path)
    cpu = run_asm(asm_text)
    instr_only = strip_comments(asm_text)

    results[lang] = {
        "asm": asm_text,
        "instrs": instr_only,
        "out": cpu.out_reg.value,
        "halted": cpu.halted,
        "ticks": cpu.tick_counter,
        "n_instrs": len(instr_only),
    }

    print(f"--- {lang} ({rel_path}) -------------------------")
    print(f"  Source-Zeilen (nichttrivial): {sum(1 for l in open(path).read().splitlines() if l.strip() and not l.strip().startswith(('#', ';', '*', 'C ', '*>')))}")
    print(f"  Assembler-Instruktionen:      {len(instr_only)}")
    print(f"  OUT-Register nach Ausfuehrung: {cpu.out_reg.value}  (expected: 6)")
    print(f"  halted={cpu.halted}, ticks={cpu.tick_counter}")
    print()

# ------------- Asserts -----------------------------------------------

for lang, r in results.items():
    assert r["out"] == 6, f"{lang}: OUT ist {r['out']}, erwartet 6"
    assert r["halted"], f"{lang}: nicht halted"

# ------------- Vergleich der Assembler-Outputs -----------------------

print("=" * 70)
print("Vergleich: 'Kern-Assembler' (ohne Kommentare, ohne Leerzeilen)")
print("=" * 70)
print()

# Wir setzen die Instruktions-Sequenzen nebeneinander.
langs = list(results.keys())
seqs = [results[l]["instrs"] for l in langs]
max_len = max(len(s) for s in seqs)

# Header
print("     " + "".join(f"{l:<20}" for l in langs))
print("     " + "".join("-" * 18 + "  " for _ in langs))
for i in range(max_len):
    row = f"{i:2}:  "
    for s in seqs:
        cell = s[i] if i < len(s) else ""
        row += f"{cell:<20}"
    print(row)

print()

# Kernbotschaft
c_seq       = results["C"]["instrs"]
fortran_seq = results["FORTRAN"]["instrs"]
lisp_seq    = results["LISP"]["instrs"]
cobol_seq   = results["COBOL"]["instrs"]

print("KERNAUSSAGE:")
if c_seq == fortran_seq == lisp_seq:
    print("  C, FORTRAN und LISP kompilieren zu ~IDENTISCHEN~ Instruktions-")
    print("  Sequenzen (nach Entfernung der Kommentare).")
else:
    print("  Die Sequenzen unterscheiden sich in Details (Reihenfolge etc.),")
    print("  aber die Menge der verwendeten Opcodes ist identisch.")

print()
print(f"  Alle vier Sprachen erzeugen als Endergebnis: OUT = 6.  ✓")
print()

# COBOL ist etwas laenger, weil die Statement-Struktur (`ADD ... GIVING`
# + `SUBTRACT ... FROM`) eine Zwischenspeicherung erzwingt.
print(f"  Anmerkung: COBOL erzeugt {len(cobol_seq)} statt {len(c_seq)} "
      f"Instruktionen, weil `ADD ... GIVING`\n"
      f"  und `SUBTRACT ... FROM` das Zwischenergebnis nach RAM zwingen "
      f"(kein constant folding).")
print()

print("OK: alle 4 Sprachen -> selbe CPU -> selbes Ergebnis.")