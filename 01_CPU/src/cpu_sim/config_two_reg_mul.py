"""Zwei-Register-CPU mit MUL und JN (erweiterte Variante).

Basiert auf `config_two_reg.py`, erweitert um zwei Opcodes, die
fuer arithmetische Anwendungen jenseits einfacher Additionen
noetig werden:

  * **MUL** — `AX := (AX * BX) mod 16`, Carry-Bit setzt, wenn das
    Produkt den 4-Bit-Bereich uebersteigt. Konsistent mit ADD/SUB,
    die auch modulo 16 rechnen und Carry setzen. Auf realer Hardware
    waere das ein Barrel-Multiplier -- teuer in Silizium, aber ein
    einzelner Takt. Bei uns kombinatorisch, wie ADD.

  * **JN** — Jump if Negative. Springt, wenn das oberste Bit von AX
    (Bit 3) gesetzt ist. In 4-Bit-Zweierkomplement bedeutet das:
    AX ∈ {8..F} entspricht AX ∈ {-8..-1}. Damit koennen wir echte
    Vorzeichen-Vergleiche machen: nach `AX := a - b` sagt JN uns
    `a < b`.

Warum die zwei Opcodes zusammen?

Sie sind das Minimum, um ein Perceptron (2 Eingaenge, 2 Gewichte,
Bias, Schwellwert-Aktivierung) sinnvoll in Assembler zu bauen:

    y = 1 if (w1*x1 + w2*x2 + b > 0) else 0

- MUL fuer die Gewichtungen `w*x`
- JN fuer den Schwellwert-Vergleich mit 0

Beides braucht man auch fuer jeden Compiler, der arithmetische
Ausdruecke mit `*` und Vergleichen `<`, `>` uebersetzen soll --
insofern ist diese Config auch die richtige Grundlage fuer einen
verbesserten Compiler-Backend.

Was ist mit NOP?

Wir opfern NOP, um im 16-Opcode-Rahmen zu bleiben. Der war ohnehin
nur eine Placeholder-Instruktion (`END` allein). Wer eine wirklich
leere Operation braucht, kann `JMP <naechste_addr>` schreiben.
"""
from . import core
from .core import (ProgramCounter, Register, InstructionRegister, RAM,
                   ALU, ALUOp)


DEFAULT_PROGRAM = """; Zwei-Register+MUL-CPU: (3 * 4) - 2 = 10.
LDI  3       ; AX := 3
LDB  4       ; BX := 4
MUL          ; AX := AX * BX = 12
LDB  2       ; BX := 2
SUB          ; AX := AX - BX = 10
OUT          ; OUT := 10
HLT
"""


def _build_alu(ax, bx, x=0, y=0):
    """ALU mit ADD, SUB, MUL. Alle rechnen AX (op) BX, mod 16."""
    ops = [
        ALUOp("ADD",
              fn=lambda a, b: (a + b) & 0xF,
              carry=lambda a, b: (a + b) > 0xF,
              description="AX + BX"),
        ALUOp("SUB",
              fn=lambda a, b: (a - b) & 0xF,
              carry=lambda a, b: (a - b) < 0,
              description="AX - BX"),
        ALUOp("MUL",
              fn=lambda a, b: (a * b) & 0xF,
              carry=lambda a, b: (a * b) > 0xF,
              description="AX * BX"),
    ]
    return ALU(x, y, ax, b_source=bx, operations=ops, default_op="ADD")


def build_cpu_config():
    bus_y = 8

    # Gleiche Bus-Layout wie config_two_reg: 6 Elemente oberhalb, RAM unten
    step_x = 20
    pc  = ProgramCounter(1 + 0*step_x, 2)
    ax  = Register(     1 + 1*step_x, 2, "AX")
    bx  = Register(     1 + 2*step_x, 2, "BX")
    alu = _build_alu(ax, bx, x=1 + 3*step_x, y=2)
    ir  = InstructionRegister(1 + 4*step_x, 2)
    out_reg = Register( 1 + 5*step_x, 2, "OUT")

    ram = RAM(1, bus_y + 2)

    layout_width = 122

    elements = {
        "PC":  pc,
        "AX":  ax,
        "BX":  bx,
        "ALU": alu,
        "IR":  ir,
        "RAM": ram,
        "OUT": out_reg,
    }

    MICROCODE = {
        # AX <- imm
        "LDI":  [{"IR_OUT", "AX_IN", "END"}],
        # BX <- imm
        "LDB":  [{"IR_OUT", "BX_IN", "END"}],
        # AX <- RAM[a]
        "LDA":  [{"RAM_OUT", "AX_IN", "END"}],
        # BX <- RAM[a]
        "LDBM": [{"RAM_OUT", "BX_IN", "END"}],
        # RAM[a] <- AX
        "STA":  [{"AX_OUT", "RAM_IN", "END"}],
        # AX <- AX + BX
        "ADD":  [{"ALU_OUT", "AX_IN", "ALU_ADD", "END"}],
        # AX <- AX - BX
        "SUB":  [{"ALU_OUT", "AX_IN", "ALU_SUB", "END"}],
        # AX <- AX * BX  (NEU)
        "MUL":  [{"ALU_OUT", "AX_IN", "ALU_MUL", "END"}],
        # BX <- AX
        "MOV":  [{"AX_OUT", "BX_IN", "END"}],
        # OUT <- AX
        "OUT":  [{"AX_OUT", "OUT_IN", "END"}],
        # PC <- imm
        "JMP":  [{"IR_OUT", "PC_IN", "END"}],
        # PC <- imm if C=1
        "JC":   [lambda cpu: ({"IR_OUT", "PC_IN", "END"}
                              if cpu.carry else {"END"})],
        # PC <- imm if AX==0
        "JZ":   [lambda cpu: ({"IR_OUT", "PC_IN", "END"}
                              if cpu.acc.value == 0 else {"END"})],
        # PC <- imm if AX < 0 (in Zweierkomplement: Bit 3 gesetzt)  (NEU)
        "JN":   [lambda cpu: ({"IR_OUT", "PC_IN", "END"}
                              if (cpu.acc.value & 0x8) else {"END"})],
        "HLT":  [{"HLT", "END"}],
    }

    OPCODE_INFO = {
        "LDI":  "AX ← imm",
        "LDB":  "BX ← imm",
        "LDA":  "AX ← RAM[a]",
        "LDBM": "BX ← RAM[a]",
        "STA":  "RAM[a] ← AX",
        "ADD":  "AX ← AX + BX",
        "SUB":  "AX ← AX − BX",
        "MUL":  "AX ← AX · BX",
        "MOV":  "BX ← AX",
        "OUT":  "OUT ← AX",
        "JMP":  "PC  ← imm",
        "JC":   "PC  ← imm if C=1",
        "JZ":   "PC  ← imm if AX==0",
        "JN":   "PC  ← imm if AX<0",
        "HLT":  "halt",
    }

    all_signals = [
        "CE",
        "PC_IN",
        "AX_IN", "AX_OUT",
        "BX_IN", "BX_OUT",
        "ALU_OUT", "ALU_ADD", "ALU_SUB", "ALU_MUL",
        "IR_OUT",
        "RAM_IN", "RAM_OUT",
        "OUT_IN",
        "HLT", "END",
    ]

    return {
        "name":          "two-reg + MUL/JN (erweitert)",
        "elements":      elements,
        "microcode":     MICROCODE,
        "opcode_info":   OPCODE_INFO,
        "all_signal_names": all_signals,
        "pc":  pc,  "ir":  ir,  "ram": ram, "alu": alu,
        "acc": ax, "tmp": bx, "out_reg": out_reg,
        "bus_y": bus_y,
        "layout_width": layout_width,
        "default_program": DEFAULT_PROGRAM,
    }