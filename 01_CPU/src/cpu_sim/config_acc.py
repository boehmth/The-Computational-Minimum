"""Akkumulator-CPU (ACC + IR).

Klassische SAP-1-artige Architektur:

  * ein einziges Datenregister: **ACC** (Akkumulator)
  * die ALU rechnet ACC (op) IR — der zweite Operand ist immer
    der Operand des aktuellen Befehls, wie er nach dem Fetch im
    IR steht. Es gibt bewusst **kein TMP-Register** — es waere
    redundant, weil das IR den Operanden ohnehin haelt.

Das macht die Befehle spuerbar kompakter als eine 2-Register-
Variante: statt `LDT n; ADD` genuegt jetzt `ADD n`.

Fuer Ausdruecke wie "a - b", wo beide Operanden Variablen sind,
muss man Zwischenergebnisse ueber den RAM leiten - das ist eine
gute didaktische Uebung: der RAM ist die "Erweiterungsflaeche"
der Register.
"""
from . import core
from .core import (ProgramCounter, Register, InstructionRegister, RAM,
                   ALU, ALUOp)


DEFAULT_PROGRAM = """; Akku-CPU: (3 + 4) - 1 = 6, ohne TMP.
LDI 3        ; ACC ← 3
ADD 4        ; ACC ← ACC + 4          (Operand kommt direkt aus IR)
SUB 1        ; ACC ← ACC - 1
STA 5        ; RAM[5] ← ACC (= 6)
LDI 0        ; ACC ← 0
LDA 5        ; ACC ← RAM[5]
OUT          ; OUT-Register ← ACC
HLT
"""


def _build_alu(acc, ir, x=0, y=0):
    """ALU mit zwei Ops (ADD, SUB), zweiter Operand ist immer IR."""
    ops = [
        ALUOp("ADD",
              fn=lambda a, b: (a + b) & 0xF,
              carry=lambda a, b: (a + b) > 0xF,
              description="ACC + IR"),
        ALUOp("SUB",
              fn=lambda a, b: (a - b) & 0xF,
              carry=lambda a, b: (a - b) < 0,
              description="ACC - IR"),
    ]
    return ALU(x, y, acc, b_source=ir, operations=ops, default_op="ADD")


def build_cpu_config():
    bus_y = 8

    # 5 Bus-Elemente oberhalb des Bus (kein TMP), jede Box 18 breit
    step_x = 20  # 18 Boxbreite + 2 Abstand
    pc  = ProgramCounter(1 + 0*step_x, 2)
    acc = Register(     1 + 1*step_x, 2, "ACC")
    ir  = InstructionRegister(1 + 2*step_x, 2)
    alu = _build_alu(acc, ir, x=1 + 3*step_x, y=2)
    out_reg = Register( 1 + 4*step_x, 2, "OUT")

    ram = RAM(1, bus_y + 2)

    # Layout-Breite: unter dem Bus liegen RAM (42) + CU (54, kommt von core)
    # + Decoder darunter (90) und rechts daneben PROG (28) = 120 min.
    layout_width = 120

    elements = {
        "PC":  pc,
        "ACC": acc,
        "IR":  ir,
        "ALU": alu,
        "RAM": ram,
        "OUT": out_reg,
    }

    MICROCODE = {
        # ACC <- imm    (imm steht im IR, also einfach IR->Bus->ACC)
        "LDI":  [{"IR_OUT", "ACC_IN", "END"}],

        # ACC <- RAM[a] (RAM.address ist beim Fetch mit dem Operanden
        # gesetzt worden; RAM legt seinen Wert auf den Bus, ACC liest)
        "LDA":  [{"RAM_OUT", "ACC_IN", "END"}],

        # RAM[a] <- ACC
        "STA":  [{"ACC_OUT", "RAM_IN", "END"}],

        # ACC <- ACC + imm   (imm im IR, ALU rechnet ACC+IR direkt)
        "ADD":  [{"ALU_OUT", "ACC_IN", "ALU_ADD", "END"}],

        # ACC <- ACC - imm
        "SUB":  [{"ALU_OUT", "ACC_IN", "ALU_SUB", "END"}],

        # OUT <- ACC
        "OUT":  [{"ACC_OUT", "OUT_IN", "END"}],

        # PC <- imm  (unbedingter Sprung)
        "JMP":  [{"IR_OUT", "PC_IN", "END"}],

        # PC <- imm  wenn Carry
        "JC":   [lambda cpu: ({"IR_OUT", "PC_IN", "END"}
                              if cpu.carry else {"END"})],

        # PC <- imm  wenn ACC == 0
        "JZ":   [lambda cpu: ({"IR_OUT", "PC_IN", "END"}
                              if cpu.acc.value == 0 else {"END"})],

        "HLT":  [{"HLT", "END"}],
        "NOP":  [{"END"}],
    }

    OPCODE_INFO = {
        "LDI": "ACC ← imm",
        "LDA": "ACC ← RAM[a]",
        "STA": "RAM[a] ← ACC",
        "ADD": "ACC ← ACC + imm",
        "SUB": "ACC ← ACC − imm",
        "OUT": "OUT ← ACC",
        "JMP": "PC  ← imm",
        "JC":  "PC  ← imm if C=1",
        "JZ":  "PC  ← imm if ACC==0",
        "HLT": "halt",
        "NOP": "no-op",
    }

    all_signals = [
        "CE",
        "PC_IN",
        "ACC_IN", "ACC_OUT",
        "ALU_OUT", "ALU_ADD", "ALU_SUB",
        "IR_OUT",
        "RAM_IN", "RAM_OUT",
        "OUT_IN",
        "HLT", "END",
    ]

    return {
        "name":          "acc (single register + IR immediate)",
        "elements":      elements,
        "microcode":     MICROCODE,
        "opcode_info":   OPCODE_INFO,
        "all_signal_names": all_signals,
        "pc":  pc,  "ir":  ir,  "ram": ram, "alu": alu,
        "acc": acc, "tmp": None, "out_reg": out_reg,
        "bus_y": bus_y,
        "layout_width": layout_width,
        "default_program": DEFAULT_PROGRAM,
    }