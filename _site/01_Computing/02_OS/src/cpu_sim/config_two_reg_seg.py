"""Zwei-Register-CPU mit Segment-Register und YIELD-Befehl.

Basiert auf der `config_two_reg` der CPU-Reihe, erweitert um zwei
neue Bausteine, die fuer ein Mini-OS mit kooperativem Multitasking
noetig sind:

  * **SEG** (4-Bit): Segment-Register. Legt fest, in welchem der
    16 RAM-Segmente die logischen Adressen des laufenden Prozesses
    landen. Der Nutzer-Code sieht weiterhin nur 16 Zellen (Adressen
    0..F); die CPU rechnet intern die physische Adresse aus:

        physical_addr = (SEG << 4) | logical_addr

    Damit haben wir bei sonst gleichem Programm 256 RAM-Zellen zur
    Verfuegung, aufgeteilt in 16 Kachel-Segmente à 16 Zellen. Das
    OS-Segment ist per Konvention SEG=0; SEG=1..F sind fuer bis zu
    15 Prozesse.

  * **YIELD** (Opcode): Signal fuer kooperatives Multitasking.
    Ein Prozess sagt damit "ich bin fertig fuer diese Runde, das
    OS darf einen anderen Prozess dranlassen". In der Simulation
    setzt YIELD nur ein Flag (cpu.yielded=True) — das eigentliche
    Umschalten macht der OS-Runner ausserhalb der CPU.

Der Rest ist identisch mit der klassischen two-reg-CPU:
  * AX + BX als Register
  * ALU rechnet AX (op) BX (ADD, SUB)
"""
from . import core
from .core import (ProgramCounter, Register, InstructionRegister, RAM,
                   SegmentRegister, ALU, ALUOp)


DEFAULT_PROGRAM = """; Default: zaehlt AX bei jedem YIELD um 1 hoch.
LDI 0
STA 0        ; RAM[0] = 0  (aktueller Zaehler)
LDA 0
LDB 1
ADD          ; AX = AX + 1
STA 0
OUT
YIELD        ; gib Kontrolle ans OS ab
JMP 2        ; zurueck zur Schleifenmitte
HLT
"""


def _build_alu(ax, bx, x=0, y=0):
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

    # 7 Bus-Elemente oberhalb des Bus:
    # PC, AX, BX, ALU, IR, SEG, OUT
    step_x = 20
    pc  = ProgramCounter(1 + 0*step_x, 2)
    ax  = Register(     1 + 1*step_x, 2, "AX")
    bx  = Register(     1 + 2*step_x, 2, "BX")
    alu = _build_alu(ax, bx, x=1 + 3*step_x, y=2)
    ir  = InstructionRegister(1 + 4*step_x, 2)
    seg = SegmentRegister(1 + 5*step_x, 2)
    out_reg = Register(1 + 6*step_x, 2, "OUT")

    # RAM mit 256 Zellen (16 Segmente à 16 Zellen)
    ram = RAM(1, bus_y + 2, size=256)

    layout_width = 142

    # Alle Bus-Elemente. SEG ist NICHT dabei — es ist bewusst kein
    # normaler Bus-Teilnehmer (nur das OS setzt SEG von außen).
    elements = {
        "PC":  pc,
        "AX":  ax,
        "BX":  bx,
        "ALU": alu,
        "IR":  ir,
        "RAM": ram,
        "OUT": out_reg,
        # SEG-Element wird nicht ins elements-Dict aufgenommen, damit
        # kein Signal SEG_IN/SEG_OUT existiert, was ein Programm
        # missbrauchen koennte.
    }

    MICROCODE = {
        # AX <- imm
        "LDI":  [{"IR_OUT", "AX_IN", "END"}],

        # BX <- imm
        "LDB":  [{"IR_OUT", "BX_IN", "END"}],

        # AX <- RAM[a]  (physisch: SEG*16 + a)
        "LDA":  [{"RAM_OUT", "AX_IN", "END"}],

        # BX <- RAM[a]
        "LDBM": [{"RAM_OUT", "BX_IN", "END"}],

        # RAM[a] <- AX
        "STA":  [{"AX_OUT", "RAM_IN", "END"}],

        # AX <- AX + BX
        "ADD":  [{"ALU_OUT", "AX_IN", "ALU_ADD", "END"}],

        # AX <- AX - BX
        "SUB":  [{"ALU_OUT", "AX_IN", "ALU_SUB", "END"}],

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

        # Kooperatives Multitasking: das Programm gibt ab
        "YIELD": [{"YIELD", "END"}],

        "HLT":  [{"HLT", "END"}],
        "NOP":  [{"END"}],
    }

    OPCODE_INFO = {
        "LDI":   "AX ← imm",
        "LDB":   "BX ← imm",
        "LDA":   "AX ← RAM[a]",
        "LDBM":  "BX ← RAM[a]",
        "STA":   "RAM[a] ← AX",
        "ADD":   "AX ← AX + BX",
        "SUB":   "AX ← AX − BX",
        "MOV":   "BX ← AX",
        "OUT":   "OUT ← AX",
        "JMP":   "PC  ← imm",
        "JC":    "PC  ← imm if C=1",
        "JZ":    "PC  ← imm if AX==0",
        "YIELD": "gib Kontrolle ans OS",
        "HLT":   "halt",
        "NOP":   "no-op",
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
        "HLT", "YIELD", "END",
    ]

    return {
        "name":          "two-reg + SEG (mit YIELD)",
        "elements":      elements,
        "microcode":     MICROCODE,
        "opcode_info":   OPCODE_INFO,
        "all_signal_names": all_signals,
        "pc":  pc,  "ir":  ir,  "ram": ram, "alu": alu,
        "acc": ax, "tmp": bx, "out_reg": out_reg,
        "seg": seg,     # NEU
        "bus_y": bus_y,
        "layout_width": layout_width,
        "default_program": DEFAULT_PROGRAM,
    }