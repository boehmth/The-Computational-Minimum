"""Zwei-Register-CPU (AX + BX).

Anders als bei der Akku-CPU (`config_acc.py`) rechnet die ALU hier
mit ZWEI Registern gegeneinander:

  * **AX** — Akkumulator (Zielregister, Farbe magenta)
  * **BX** — zweites Register (Farbe gelb)
  * ALU rechnet immer AX (op) BX. Der Operand fuer ADD/SUB kommt
    NICHT aus dem IR, sondern aus BX. Das ist die klassische
    Register-Register-Architektur (Intel 8080 → 8086, AX/BX).

Damit ist der Sprachumfang echt reicher als bei der Akku-Variante:
Ausdruecke wie `a + b`, wo beide Operanden Variablen sind, brauchen
kein RAM-Zwischenspiel. Man macht einfach:

    LDA  a     ; AX ← RAM[a]
    LDBM b     ; BX ← RAM[b]
    ADD        ; AX ← AX + BX
    STA  c     ; RAM[c] ← AX

Fuer einen (spaeteren) Compiler ist das die deutlich angenehmere
Zielsprache.
"""
from . import core
from .core import (ProgramCounter, Register, InstructionRegister, RAM,
                   ALU, ALUOp)


DEFAULT_PROGRAM = """; Zwei-Register-CPU: (3 + 4) − 1 = 6 mit AX + BX.
LDI  3       ; AX ← 3
LDB  4       ; BX ← 4        (Immediate in BX)
ADD          ; AX ← AX + BX  = 7  (Register-Register!)
LDB  1       ; BX ← 1
SUB          ; AX ← AX − BX  = 6
STA  5       ; RAM[5] ← AX
LDI  0       ; AX ← 0
LDA  5       ; AX ← RAM[5]   (Reload)
OUT          ; OUT ← AX
HLT
"""


def _build_alu(ax, bx, x=0, y=0):
    """ALU: rechnet AX (op) BX."""
    ops = [
        ALUOp("ADD",
              fn=lambda a, b: (a + b) & 0xF,
              carry=lambda a, b: (a + b) > 0xF,
              description="AX + BX"),
        ALUOp("SUB",
              fn=lambda a, b: (a - b) & 0xF,
              carry=lambda a, b: (a - b) < 0,
              description="AX - BX"),
    ]
    return ALU(x, y, ax, b_source=bx, operations=ops, default_op="ADD")


def build_cpu_config():
    bus_y = 8

    # 6 Bus-Elemente oberhalb des Bus (AX + BX + PC + IR + ALU + OUT)
    step_x = 20
    pc  = ProgramCounter(1 + 0*step_x, 2)
    ax  = Register(     1 + 1*step_x, 2, "AX")
    bx  = Register(     1 + 2*step_x, 2, "BX")
    alu = _build_alu(ax, bx, x=1 + 3*step_x, y=2)
    ir  = InstructionRegister(1 + 4*step_x, 2)
    out_reg = Register( 1 + 5*step_x, 2, "OUT")

    ram = RAM(1, bus_y + 2)

    # 6 Boxen à 20 = 121, aber die Bus-Zeile wird von der
    # Decoder-View unten diktiert (90 + 2 + 28 = 120). Wir nehmen 122.
    layout_width = 122

    # Alle Bus-Elemente
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
        # AX <- imm  (kommt aus IR)
        "LDI":  [{"IR_OUT", "AX_IN", "END"}],

        # BX <- imm
        "LDB":  [{"IR_OUT", "BX_IN", "END"}],

        # AX <- RAM[a]
        "LDA":  [{"RAM_OUT", "AX_IN", "END"}],

        # BX <- RAM[a]
        "LDBM": [{"RAM_OUT", "BX_IN", "END"}],

        # RAM[a] <- AX
        "STA":  [{"AX_OUT", "RAM_IN", "END"}],

        # AX <- AX + BX  (echte Register-Register-Op)
        "ADD":  [{"ALU_OUT", "AX_IN", "ALU_ADD", "END"}],

        # AX <- AX - BX
        "SUB":  [{"ALU_OUT", "AX_IN", "ALU_SUB", "END"}],

        # AX <-> BX?  Nur AX -> BX ist nuetzlich: MOV BX, AX
        "MOV":  [{"AX_OUT", "BX_IN", "END"}],

        # OUT <- AX
        "OUT":  [{"AX_OUT", "OUT_IN", "END"}],

        # PC <- imm
        "JMP":  [{"IR_OUT", "PC_IN", "END"}],

        # PC <- imm wenn Carry
        "JC":   [lambda cpu: ({"IR_OUT", "PC_IN", "END"}
                              if cpu.carry else {"END"})],

        # PC <- imm wenn AX == 0
        "JZ":   [lambda cpu: ({"IR_OUT", "PC_IN", "END"}
                              if cpu.acc.value == 0 else {"END"})],

        "HLT":  [{"HLT", "END"}],
        "NOP":  [{"END"}],
    }

    OPCODE_INFO = {
        "LDI":  "AX ← imm",
        "LDB":  "BX ← imm",
        "LDA":  "AX ← RAM[a]",
        "LDBM": "BX ← RAM[a]",
        "STA":  "RAM[a] ← AX",
        "ADD":  "AX ← AX + BX",
        "SUB":  "AX ← AX − BX",
        "MOV":  "BX ← AX",
        "OUT":  "OUT ← AX",
        "JMP":  "PC  ← imm",
        "JC":   "PC  ← imm if C=1",
        "JZ":   "PC  ← imm if AX==0",
        "HLT":  "halt",
        "NOP":  "no-op",
    }

    all_signals = [
        "CE",
        "PC_IN",
        "AX_IN", "AX_OUT",
        "BX_IN", "BX_OUT",
        "ALU_OUT", "ALU_ADD", "ALU_SUB",
        "IR_OUT",
        "RAM_IN", "RAM_OUT",
        "OUT_IN",
        "HLT", "END",
    ]

    return {
        "name":          "two-reg (AX + BX, register-register)",
        "elements":      elements,
        "microcode":     MICROCODE,
        "opcode_info":   OPCODE_INFO,
        "all_signal_names": all_signals,
        "pc":  pc,  "ir":  ir,  "ram": ram, "alu": alu,
        # Wir nutzen die core-Semantik: 'acc' ist immer das
        # Zielregister der ALU. Bei two_reg ist das AX.
        "acc": ax, "tmp": bx, "out_reg": out_reg,
        "bus_y": bus_y,
        "layout_width": layout_width,
        "default_program": DEFAULT_PROGRAM,
    }
