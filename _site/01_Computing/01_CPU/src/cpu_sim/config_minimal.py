"""Minimal-CPU: nur ein Register (ACC) und eine ALU, die INC + NOT kann.

Zeigt didaktisch: mit INC und NOT alleine kann man alles rechnen.
  * Addition: INC in Schleife (n mal)
  * Subtraktion: 2er-Komplement:  b - a = INC(NOT(a)) + b  (Trick:
    weil hier kein ADD vorhanden ist, brauchen wir Schleifen fuer '+',
    aber NOT + INC macht Negation in 2 Takten anschaulich.)
  * Multiplikation, Division: verschachtelte Schleifen

Register:
  - ACC   (nur eins!)

Kein TMP, kein B. Die ALU rechnet nur mit ACC:
  INC:  ACC + 1
  NOT:  bitweises Invertieren

Befehle:
  LDI n     ACC <- n
  LDA a     ACC <- RAM[a]
  STA a     RAM[a] <- ACC
  INC       ACC <- ACC + 1
  NOT       ACC <- ~ACC (4-bit)
  OUT       OUT <- ACC
  JMP a     PC  <- a
  JZ  a     PC  <- a  wenn ACC == 0
  HLT
  NOP
"""
from . import core
from .core import (ProgramCounter, Register, InstructionRegister, RAM,
                   ALU, ALUOp)


DEFAULT_PROGRAM = """; Minimal-CPU: zaehlt ACC von 0 auf 5, dann HLT.
; Zeigt: mit INC + NOT + JZ + JMP alleine kann man eine
; Schleife (und damit Turing-vollstaendig) bauen.
;
; Idee: RAM[1] ist der Loop-Counter. Wir starten ihn bei -5
; (2er-Komplement in 4-bit: NOT(5)+1 = 0xA+1 = 0xB) und lassen
; ihn per INC in Richtung 0 laufen. Bei 0 -> Ende.
;
; RAM[0] ist unser Ergebnis-Zaehler. Der wird pro Durchgang
; um 1 erhoeht und in OUT gespiegelt.

LDI 0        ; 0:  ACC = 0
STA 0        ; 1:  RAM[0] = 0
LDI 5        ; 2:  ACC = 5
NOT          ; 3:  ACC = ~5 = 0xA
INC          ; 4:  ACC = 0xB = -5
STA 1        ; 5:  RAM[1] = -5 (Loop-Counter)

LDA 0        ; 6:  Schleifenkopf: ACC = RAM[0]
INC          ; 7:  ACC += 1
STA 0        ; 8:  RAM[0] = ACC
OUT          ; 9:  OUT   = ACC

LDA 1        ; A:  Counter laden
INC          ; B:  += 1 (Richtung 0)
STA 1        ; C:  Counter speichern
JZ  $F       ; D:  wenn ACC==0 -> Ende bei Adresse F
JMP 6        ; E:  sonst zurueck zum Schleifenkopf
HLT          ; F:  Ende
"""


def _build_alu(acc, x=0, y=0):
    ops = [
        ALUOp("INC",
              fn=lambda a, b: (a + 1) & 0xF,
              carry=lambda a, b: (a + 1) > 0xF,
              unary=True,
              description="ACC + 1"),
        ALUOp("NOT",
              fn=lambda a, b: (~a) & 0xF,
              unary=True,
              description="~ACC (4-bit)"),
    ]
    # b_source=None -> unaere Ops (INC/NOT arbeiten nur auf ACC)
    return ALU(x, y, acc, b_source=None, operations=ops, default_op="INC")


def build_cpu_config():
    bus_y = 8

    # 5 Bus-Elemente oberhalb des Bus (kein TMP), Boxbreite 18
    step_x = 20  # 18 + 2 Abstand
    pc  = ProgramCounter(1 + 0*step_x, 2)
    acc = Register(     1 + 1*step_x, 2, "ACC")
    alu = _build_alu(acc, x=1 + 2*step_x, y=2)
    ir  = InstructionRegister(1 + 3*step_x, 2)
    out_reg = Register(1 + 4*step_x, 2, "OUT")

    ram = RAM(1, bus_y + 2)

    # Layout-Breite: entspricht Akku-CPU (siehe config_acc.py)
    layout_width = 120

    elements = {
        "PC":  pc,
        "ACC": acc,
        "ALU": alu,
        "IR":  ir,
        "RAM": ram,
        "OUT": out_reg,
    }

    # --- JZ: bedingter Sprung, wenn ACC == 0 -------------------
    def jz_step(cpu):
        # Wenn ACC 0 ist, PC <- IR (Zieladresse), sonst NOP
        return ({"IR_OUT", "PC_IN", "END"}
                if cpu.acc.value == 0 else {"END"})

    MICROCODE = {
        "LDI":  [{"IR_OUT", "ACC_IN", "END"}],
        "LDA":  [{"RAM_OUT", "ACC_IN", "END"}],
        "STA":  [{"ACC_OUT", "RAM_IN", "END"}],

        # ALU nutzen: Signal fuer die Op + ALU_OUT + ACC_IN
        "INC":  [{"ALU_INC", "ALU_OUT", "ACC_IN", "END"}],
        "NOT":  [{"ALU_NOT", "ALU_OUT", "ACC_IN", "END"}],

        "OUT":  [{"ACC_OUT", "OUT_IN", "END"}],
        "JMP":  [{"IR_OUT", "PC_IN", "END"}],
        "JZ":   [jz_step],
        "HLT":  [{"HLT", "END"}],
        "NOP":  [{"END"}],
    }

    OPCODE_INFO = {
        "LDI": "ACC ← imm",
        "LDA": "ACC ← RAM[a]",
        "STA": "RAM[a] ← ACC",
        "INC": "ACC ← ACC + 1",
        "NOT": "ACC ← ~ACC",
        "OUT": "OUT ← ACC",
        "JMP": "PC  ← imm",
        "JZ":  "PC  ← imm if ACC==0",
        "HLT": "halt",
        "NOP": "no-op",
    }

    all_signals = [
        "CE",
        "PC_IN",
        "ACC_IN", "ACC_OUT",
        "ALU_OUT", "ALU_INC", "ALU_NOT",
        "IR_OUT",
        "RAM_IN", "RAM_OUT",
        "OUT_IN",
        "HLT", "END",
    ]

    return {
        "name":          "minimal (ACC only, ALU: INC + NOT)",
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