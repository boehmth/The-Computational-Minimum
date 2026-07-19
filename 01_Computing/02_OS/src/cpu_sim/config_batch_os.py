"""Batch-OS-CPU: Zwei-Register-CPU mit Base-Pointer fuer den Programmspeicher.

Kernidee (Weg 2 des OS-Kapitels): das OS ist *selbst* ein Programm, das
aus den 16 Opcodes der CPU besteht. Damit brauchen wir einen Mechanismus,
mit dem die CPU zwischen OS-Code und User-Code umschalten kann, ohne
dass es einen "Ring 0 in Python" gibt.

Der Mechanismus ist ein **Base-Pointer (BP, 4 Bit)** fuer den
Programmspeicher — analog zum SEG-Register fuer den Datenspeicher,
aber auf der Code-Seite. Er ist die Verallgemeinerung von
Batch-Rechnern der 1950er (IBM 704/7090, GM-NAA I/O): das OS ist ein
Programm, das nacheinander mehrere User-Jobs "auflegt" und wartet, bis
jeder mit HLT zurueckkehrt.

Layout des Programmspeichers (16 Slots à 16 Instruktionen = 256 Zellen):

    BP=0 : OS-Code
    BP=1 : User-Programm 1
    BP=2 : User-Programm 2
    ...
    BP=F : User-Programm 15

Physische Instruktionsadresse:  addr = (BP << 4) | PC.
Uninitialisierte Speicherzellen enthalten 0 → das entspricht per
Konvention dem Opcode HLT (Opcode 0). Das heisst: "leere Slots"
kehren automatisch ins OS zurueck.

Zwei neue Semantiken gegenueber der klassischen two-reg-CPU:

  * **HLT** setzt zusaetzlich BP:=0 und PC:=0. Damit uebernimmt das
    OS die Kontrolle zurueck. HLT ist also kein "Rechner stoppt", sondern
    ein "Yield-and-return-to-OS". Ein echtes Beenden gibt es nur, wenn
    das OS selbst HLT ausfuehrt (dann sind BP und PC danach zwar wieder 0,
    aber das OS hat ja gerade selbst HLT gemacht — die CPU-Schleife
    erkennt das und stoppt tatsaechlich).

  * **SETBP** ist der einzige neue Opcode. Semantik:
        BP := BX
        PC := 0
    Damit verlaesst das OS sich selbst und startet ein User-Programm.
    Der Wert kommt aus BX (nicht AX), damit AX frei bleibt fuer
    Register-Initialisierung des User-Programms.

Kein SEG-Register, kein YIELD. Der RAM ist wie in der klassischen
CPU nur 16 Zellen gross und wird von OS UND User geteilt — d.h.
ein User-Programm, das RAM[0] beschreibt, ueberschreibt den State
des OS. Das ist bewusst so und der zentrale didaktische Punkt:
frueher, ungeschuetzt, wie DOS < 5.0 oder CP/M.
"""
from . import core
from .core import (ProgramCounter, Register, InstructionRegister, RAM,
                   BasePointer, ALU, ALUOp)


DEFAULT_PROGRAM = """; Default (leer). Wird vom Batch-Runner ueberschrieben.
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

    # 7 Bus-Elemente oberhalb des Bus: PC, AX, BX, ALU, IR, BP, OUT
    step_x = 20
    pc  = ProgramCounter(1 + 0*step_x, 2)
    ax  = Register(     1 + 1*step_x, 2, "AX")
    bx  = Register(     1 + 2*step_x, 2, "BX")
    alu = _build_alu(ax, bx, x=1 + 3*step_x, y=2)
    ir  = InstructionRegister(1 + 4*step_x, 2)
    bp  = BasePointer(1 + 5*step_x, 2)
    out_reg = Register(1 + 6*step_x, 2, "OUT")

    ram = RAM(1, bus_y + 2, size=16)     # ungeschuetzte 16 Zellen fuer alle

    layout_width = 142

    # Bus-Teilnehmer. BP ist NICHT dabei — der einzige Weg, BP zu setzen,
    # ist der SETBP-Opcode (mikrocode-hardwired). Damit gibt es kein
    # BP_IN/BP_OUT-Signal, das ein User-Programm missbrauchen koennte.
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
        # BP <- BX; PC <- 0 (verlaesst OS, startet User-Prog).
        # Formal Ring-0-privilegiert (nur wenn BP=0 gueltig), aber
        # nicht enforced -- didaktischer Punkt: User koennte das auch,
        # es gibt keinen Schutz.
        "SETBP": [{"SETBP", "END"}],
        # HLT: BP <- 0; PC <- 0 (Kontrolle zurueck ans OS).
        # Wenn das OS selbst HLT macht, stoppt die Simulation wirklich.
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
        "SETBP": "BP←BX, PC←0",
        "HLT":   "BP←0, PC←0",
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
        "HLT", "SETBP", "END",
    ]

    return {
        "name":          "batch-OS CPU (AX+BX+BP, HLT=trap)",
        "elements":      elements,
        "microcode":     MICROCODE,
        "opcode_info":   OPCODE_INFO,
        "all_signal_names": all_signals,
        "pc":  pc,  "ir":  ir,  "ram": ram, "alu": alu,
        "acc": ax, "tmp": bx, "out_reg": out_reg,
        "bp":  bp,          # NEU: Base-Pointer fuer PROG-Speicher
        "bus_y": bus_y,
        "layout_width": layout_width,
        "default_program": DEFAULT_PROGRAM,
    }