"""cpu_sim.core -- Framework fuer die 4-Bit-CPU-Simulation.

Enthaelt alle wiederverwendbaren Bausteine:

  * Terminal-Utilities (goto, clear_screen, Farben, ANSI-safe Padding)
  * Element (Basisklasse aller Bus-faehigen und Anzeige-Elemente)
  * Bus-Elemente: ProgramCounter, Register, ALU, RAM, InstructionRegister
  * ControlUnit: iteriert ueber Mikrobefehle des aktuellen Opcodes
  * Anzeige-Views: ProgramMemoryView, MicrocodeROMView, OpcodeHelpView
  * CPU: haelt Elemente + ControlUnit + macht die 3 Bus-Schleifen
  * Panel: sammelt Elemente zum Zeichnen

Die eigentliche Konfiguration (welche Elemente, welcher Mikrocode,
welche ALU-Operationen) kommt aus einer separaten Config-Datei -
siehe config_minimal.py und config_acc.py.
"""
import os
import re
import sys
from abc import ABC, abstractmethod


# ============================================================
# Terminal-Utilities
# ============================================================

def goto(x, y):
    print(f"\033[{y};{x}H", end="")

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

RESET = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"
INV   = "\033[7m"

FG = {
    "gray":    "\033[90m",
    "red":     "\033[31m",
    "green":   "\033[32m",
    "yellow":  "\033[33m",
    "blue":    "\033[34m",
    "magenta": "\033[35m",
    "cyan":    "\033[36m",
    "white":   "\033[97m",
    "bgreen":  "\033[92m",
    "bcyan":   "\033[96m",
    "byellow": "\033[93m",
    "bmagenta":"\033[95m",
}

def c(text, color):
    return f"{FG[color]}{text}{RESET}"

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")

def strip_ansi(s):
    return _ANSI_RE.sub("", s)

def vlen(s):
    """Sichtbare Laenge (ANSI-Escape-Sequenzen ignoriert)."""
    return len(strip_ansi(s))

def vpad(s, width, align="left"):
    """Auf sichtbare Breite paddieren (ANSI-safe)."""
    n = vlen(s)
    if n >= width:
        return s
    pad = " " * (width - n)
    if align == "right":
        return pad + s
    if align == "center":
        left = (width - n) // 2
        return " " * left + s + " " * (width - n - left)
    return s + pad

def fmt_value(v, color="white", bits=4):
    return c(f"{v:X}", color) + c(f"  0b{v:0{bits}b}", "gray")


# ============================================================
# Bus-Basisklasse
# ============================================================

class Gate:
    NONE = 0
    IN = 1
    OUT = 2


class Element(ABC):
    """Basisklasse aller Elemente (Bus-Teilnehmer oder Anzeige)."""

    def __init__(self, x, y, width, height, name=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.value = 0
        self.gate = Gate.NONE

    def read_from_bus(self, bus_value):
        if self.gate == Gate.IN:
            self.value = bus_value & 0b1111

    def write_to_bus(self):
        if self.gate == Gate.OUT:
            return self.value & 0b1111
        return None

    def gate_color(self):
        if self.gate == Gate.OUT:
            return "bgreen"
        if self.gate == Gate.IN:
            return "bcyan"
        return "gray"

    def framed(self, inner_lines, title=None, frame_color=None):
        """Unicode-Box um die Inhaltszeilen. ANSI-safe padding."""
        col = frame_color if frame_color else self.gate_color()
        w = self.width
        name = title if title is not None else self.name
        title_str = f" {name} "
        fill = "═" * max(0, (w - 2) - len(title_str))
        top    = "╔" + title_str + fill + "╗"
        bottom = "╚" + "═" * (w - 2) + "╝"
        lines = [c(top, col)]
        for line in inner_lines:
            padded = vpad(line, w - 2, align="left")
            lines.append(c("║", col) + padded + c("║", col))
        lines.append(c(bottom, col))
        return "\n".join(lines)

    def clear(self):
        for i in range(self.height):
            goto(self.x, self.y + i)
            print(" " * self.width)

    @abstractmethod
    def render(self):
        pass

    def draw(self):
        self.clear()
        for i, line in enumerate(self.render().split("\n")):
            goto(self.x, self.y + i)
            print(line, end="")


# ============================================================
# Konkrete Bus-Elemente
# ============================================================

# Einheitliche Breite fuer alle einfachen Register-artigen Boxen.
BOX_W = 18


def _reg_content(value_line, hint):
    """Zwei Inhaltszeilen fuer einen Register-Kasten:
       Zeile 1: Wert (hex + binaer)
       Zeile 2: kurzer Hinweistext (grau)
    Beide werden auf die volle Innenbreite gepadded."""
    inner = BOX_W - 2                     # 16 sichtbare Zeichen
    return [
        vpad(f" {value_line}", inner),
        vpad(c(f" {hint}", "gray"), inner),
    ]


class ProgramCounter(Element):
    def __init__(self, x, y):
        super().__init__(x, y, width=BOX_W, height=4, name="PC")

    def tick(self):
        self.value = (self.value + 1) & 0b1111

    def render(self):
        return self.framed(_reg_content(
            fmt_value(self.value, "byellow"),
            "program counter"))


class Register(Element):
    COLOR_MAP = {
        "ACC": "bmagenta", "TMP": "byellow",
        "A":   "bmagenta", "B":   "byellow",
        "OUT": "bcyan",
    }

    def __init__(self, x, y, name):
        super().__init__(x, y, width=BOX_W, height=4, name=name)

    def render(self):
        col = self.COLOR_MAP.get(self.name, "white")
        return self.framed(_reg_content(
            fmt_value(self.value, col),
            "4-bit register"))


class InstructionRegister(Element):
    def __init__(self, x, y):
        super().__init__(x, y, width=BOX_W, height=4, name="IR")

    def render(self):
        return self.framed(_reg_content(
            fmt_value(self.value, "byellow"),
            "operand field"))


class RAM(Element):
    def __init__(self, x, y, size=16):
        super().__init__(x, y, width=42, height=7, name="RAM 16x4")
        self.cells = [0] * size
        self.address = 0

    def read_from_bus(self, bus_value):
        if self.gate == Gate.IN:
            self.cells[self.address & 0xF] = bus_value & 0b1111

    def write_to_bus(self):
        if self.gate == Gate.OUT:
            return self.cells[self.address & 0xF] & 0b1111
        return None

    def render(self):
        addr = self.address & 0xF
        header = "    " + " ".join(c(f" {i:X} ", "gray") for i in range(4))
        rows = [header]
        for row in range(4):
            cells = []
            for col in range(4):
                i = row * 4 + col
                v = self.cells[i]
                if i == addr and self.gate != Gate.NONE:
                    col_name = "bgreen" if self.gate == Gate.OUT else "bcyan"
                    cells.append(c(f"[{v:X}]", col_name))
                elif i == addr:
                    cells.append(c(f"[{v:X}]", "byellow"))
                elif v != 0:
                    cells.append(c(f" {v:X} ", "white"))
                else:
                    cells.append(c(f" {v:X} ", "gray"))
            rows.append(c(f" {row:X}: ", "gray") + " ".join(cells))
        rows.append(c(f"  addr = {addr:X}   value = {self.cells[addr]:X}",
                      "gray"))
        return self.framed(rows)


# ============================================================
# ALU (konfigurierbar)
# ============================================================

class ALUOp:
    """Eine ALU-Operation.
      name:   String, z.B. "INC" -> Signal "ALU_INC"
      fn:     (acc, tmp) -> int (4-bit)
      carry:  optional (acc, tmp) -> bool
      unary:  True fuer Ops, die nur ACC brauchen (INC, NOT, ...)
    """
    def __init__(self, name, fn, carry=None, unary=False, description=""):
        self.name = name
        self.fn = fn
        self.carry_fn = carry
        self.unary = unary
        self.description = description


class ALU(Element):
    """Konfigurierbare ALU: haelt eine Menge erlaubter Ops.

    Der erste Operand ist immer der Akkumulator (acc).
    Der zweite Operand kommt aus 'b_source' — das kann sein:
      * None                       -> unaere Ops (INC, NOT, ...)
      * ein Register (z.B. TMP)    -> Register-Register-Ops
      * das IR                     -> "Immediate-Ops" a la ACC + imm
                                      (weil im IR nach dem Fetch der
                                      Operand der Instruktion steht)

    Das aktive Steuersignal (ALU_<OPNAME>) waehlt die Op aus.
    Wenn keins gesetzt ist, wird default_op ausgefuehrt.
    """

    def __init__(self, x, y, acc, b_source, operations, default_op):
        super().__init__(x, y, width=18, height=4, name="ALU")
        self.acc = acc
        self.b_source = b_source   # None / Register / IR
        self.operations = {op.name: op for op in operations}
        self.default_op_name = default_op
        self.current_op_name = default_op
        self.carry = False

    def signal_for(self, op_name):
        return f"ALU_{op_name}"

    def all_signals(self):
        return [self.signal_for(n) for n in self.operations]

    def apply_signals(self, signals):
        chosen = None
        for op_name in self.operations:
            if self.signal_for(op_name) in signals:
                chosen = op_name
                break
        self.current_op_name = chosen if chosen else self.default_op_name

    def compute(self):
        op = self.operations[self.current_op_name]
        a = self.acc.value
        b = self.b_source.value if self.b_source is not None else 0
        self.value = op.fn(a, b) & 0b1111
        self.carry = bool(op.carry_fn(a, b)) if op.carry_fn else False

    def render(self):
        op_col = "bgreen" if self.current_op_name in ("ADD", "INC") else \
                 "red"    if self.current_op_name in ("SUB", "NOT") else \
                 "byellow"
        op_text = c(self.current_op_name, op_col)
        cflag = c(f"C={int(self.carry)}",
                  "byellow" if self.carry else "gray")
        inner = BOX_W - 2
        return self.framed([
            vpad(f" {fmt_value(self.value, 'bgreen')}", inner),
            vpad(f" {op_text}  {cflag}", inner),
        ])


# ============================================================
# ControlUnit
# ============================================================

class ControlUnit(Element):
    MAX_STEPS = 4

    # Anzeige-Layout: wie viele Signale pro Zeile, wie breit pro Zelle
    SIG_COLS = 4
    SIG_CELL = 12   # sichtbare Zeichen pro Zelle (inkl. Trenn-Space)

    def __init__(self, x, y, cpu):
        super().__init__(x, y, width=self._compute_width(), height=8, name="CU")
        self.cpu = cpu
        self.step = 0
        self.active_signals = set()
        self.current_opcode = "NOP"
        self.current_operand = 0

    @classmethod
    def _compute_width(cls):
        # 2 (Rahmen) + 1 (linker Rand) + SIG_COLS * SIG_CELL + 1 (rechter Rand)
        return 2 + 1 + cls.SIG_COLS * cls.SIG_CELL + 1

    def next_control_word(self):
        if self.step == 0:
            # FETCH (hardwired, nicht im Mikrocode)
            addr = self.cpu.pc.value
            opcode, operand = self.cpu.program[addr % len(self.cpu.program)]
            self.current_opcode = opcode
            self.current_operand = operand
            if self.cpu.ir is not None:
                self.cpu.ir.value = operand & 0xF
            if self.cpu.ram is not None:
                self.cpu.ram.address = operand & 0xF
            self.cpu.current_instr_address = addr
            return {"CE"}

        steps = self.cpu.microcode.get(self.current_opcode, [{"END"}])
        idx = self.step - 1
        if idx >= len(steps):
            return {"END"}
        step = steps[idx]
        return step(self.cpu) if callable(step) else set(step)

    def advance(self, signals):
        if "END" in signals:
            self.step = 0
        else:
            self.step = (self.step + 1) % self.MAX_STEPS

    def render(self):
        def sig_cell(s):
            """Ein Signal als linksbuendige Zelle fester Breite."""
            if s in self.active_signals:
                if s.endswith("_OUT"):
                    colored = c(s, "bgreen")
                elif s.endswith("_IN"):
                    colored = c(s, "bcyan")
                else:
                    colored = c(s, "byellow")
            else:
                colored = c(s, "gray")
            # Feste Zellenbreite -> Signale sind spaltenweise aligned
            return vpad(colored, self.SIG_CELL, align="left")

        # Signale in ein festes Grid mit SIG_COLS Spalten packen
        sig_lines = []
        row = ""
        for i, s in enumerate(self.cpu.all_signal_names):
            row += sig_cell(s)
            if (i + 1) % self.SIG_COLS == 0:
                sig_lines.append(row)
                row = ""
        if row:
            sig_lines.append(row)

        if self.step == 0:
            phase = c("FETCH", "byellow")
        elif "HLT" in self.active_signals:
            phase = c("HALT", "red")
        else:
            phase = c(f"EXEC {self.step}", "bmagenta")

        boxes = "".join(
            c("[*]", "bmagenta") if i == self.step else c("[ ]", "gray")
            for i in range(self.MAX_STEPS)
        )

        header = [
            f" phase={phase}   step={boxes}",
            f" opcode={c(self.current_opcode, 'byellow')}"
            f"   operand={c(f'{self.current_operand:X}', 'byellow')}"
            f"   carry={c(str(int(self.cpu.carry)), 'byellow')}",
        ]
        # Hoehe dynamisch: 2 (Rahmen) + Header + Signalzeilen
        self.height = 2 + len(header) + len(sig_lines)
        content = [f" {ln}" for ln in header + sig_lines]
        return self.framed(content, title="ControlUnit", frame_color="white")


# ============================================================
# Anzeige-Views (kein Bus-Anschluss)
# ============================================================

class ProgramMemoryView(Element):
    def __init__(self, x, y, cpu):
        self.cpu = cpu
        super().__init__(x, y, width=28, height=len(cpu.program) + 2,
                         name="Programmspeicher")

    def render(self):
        lines = []
        for addr, (op, arg) in enumerate(self.cpu.program):
            active = (addr == self.cpu.current_instr_address)
            marker = c("►", "byellow") if active else " "
            row = f" {marker} {addr:X}: {op:<4} {arg:X}"
            row = c(row, "byellow") if active else c(row, "gray")
            lines.append(row)
        return self.framed(lines, frame_color="white")


class DecoderView(Element):
    """Kombinierte Mikrocode-ROM + Opcode-Tabelle.

    Zeigt alle Opcodes der CPU als Tabelle mit ihren Mikroschritten.
    Die Zeile des aktuellen Opcodes ist gelb hervorgehoben, das
    gerade abgearbeitete Mikroschritt-Set zusaetzlich invertiert.

    Fetch wird ganz oben in einer eigenen Zeile gezeigt - er ist
    hardwired und kein Bestandteil des ROM.
    """
    def __init__(self, x, y, cpu):
        self.cpu = cpu
        super().__init__(x, y, width=90, height=len(cpu.opcode_info) + 4,
                         name="Decoder / Mikrocode-ROM")

    def _step_text(self, step):
        if callable(step):
            return "λ(cpu) → conditional"
        if not step:
            return "{ }"
        return "{ " + ", ".join(sorted(step)) + " }"

    def render(self):
        cur_op   = self.cpu.cu.current_opcode
        cur_step = self.cpu.cu.step
        lines = []

        # ---- Fetch-Zeile (hardwired) ------------------------
        fetch_active = (cur_step == 0)
        marker = c("►", "byellow") if fetch_active else " "
        fetch_line = f" {marker} FETCH  (PROG → IR, set RAM.addr, CE)   [hardwired, alle Opcodes]"
        lines.append(c(fetch_line,
                       "byellow" if fetch_active else "gray"))
        lines.append(c(" " + "─" * (self.width - 4), "gray"))

        # ---- Opcode-Tabelle ---------------------------------
        lines.append(c(" op    Semantik              Mikroschritt(e)",
                       "white"))

        for op, desc in self.cpu.opcode_info.items():
            steps = self.cpu.microcode.get(op, [])
            is_current = (op == cur_op)
            base_color = "byellow" if is_current else "gray"

            if not steps:
                lines.append(c(
                    f" {op:<5} {desc:<20} (kein ROM-Eintrag)", "red"))
                continue

            # Erster Mikroschritt in derselben Zeile wie Opcode
            first_active = is_current and cur_step == 1
            first_txt = self._step_text(steps[0])
            first_col = "bmagenta" if first_active else base_color
            marker    = c("►", "byellow") if first_active else " "
            lines.append(c(
                f" {marker}{op:<5} {desc:<20} 1: {first_txt}", first_col))

            # Weitere Mikroschritte eingerueckt
            for i, step in enumerate(steps[1:], start=2):
                active = is_current and cur_step == i
                col = "bmagenta" if active else base_color
                marker = c("►", "byellow") if active else " "
                rest = self._step_text(step)
                lines.append(c(
                    f" {marker}     {'':<20} {i}: {rest}", col))

        # Hoehe dynamisch
        self.height = len(lines) + 2
        return self.framed(lines, frame_color="white")


# Alias fuer Rueckwaertskompatibilitaet mit runner.py
MicrocodeROMView = DecoderView
OpcodeHelpView   = DecoderView


# ============================================================
# Panel + CPU
# ============================================================

class Panel:
    def __init__(self):
        self.elements = []

    def add(self, element):
        self.elements.append(element)

    def update(self):
        for e in self.elements:
            e.draw()
        sys.stdout.flush()


BUS_SUFFIXES = ("_IN", "_OUT")


class CPU:
    """Generische CPU. Wird von einer Config zusammengesetzt.

    Erwartet in config:
      elements          : dict {PREFIX: Element} - Bus-Teilnehmer
      microcode         : dict {opcode: [step, ...]}
      opcode_info       : dict {opcode: 'kurzbeschreibung'}
      all_signal_names  : Liste aller Signale (fuer CU-Rendering)
      pc, ir, ram, alu, acc, tmp : direkte Referenzen (koennen None sein)
      bus_y             : y-Position der Bus-Linie
      layout_width      : Bildschirmbreite
    """

    def __init__(self, config, program):
        self.config = config
        self.program = program

        self.elements    = config["elements"]
        self.microcode   = config["microcode"]
        self.opcode_info = config.get("opcode_info", {})
        self.all_signal_names = config["all_signal_names"]

        self.pc  = config.get("pc")
        self.ir  = config.get("ir")
        self.ram = config.get("ram")
        self.alu = config.get("alu")
        self.acc = config.get("acc")
        self.tmp = config.get("tmp")
        self.out_reg = config.get("out_reg")

        self.bus_y = config.get("bus_y", 8)
        self.layout_width = config.get("layout_width", 140)

        self.bus = 0
        self.carry = False
        self.halted = False
        self.current_instr_address = 0
        self.tick_counter = 0

        # ControlUnit unter dem Bus
        self.cu = ControlUnit(1, self.bus_y + 2, self)

    # ---- die 3 Bus-Schleifen -------------------------------
    def set_gates(self, signals):
        for elem in self.elements.values():
            elem.gate = Gate.NONE
        for sig in signals:
            for suffix in BUS_SUFFIXES:
                if sig.endswith(suffix):
                    name = sig[:-len(suffix)]
                    if name in self.elements:
                        self.elements[name].gate = (
                            Gate.OUT if suffix == "_OUT" else Gate.IN
                        )

    def write_bus(self):
        writers = [e for e in self.elements.values() if e.gate == Gate.OUT]
        if len(writers) > 1:
            names = ", ".join(e.name for e in writers)
            raise RuntimeError(f"Bus-Konflikt: mehrere Treiber ({names})!")
        if writers:
            self.bus = writers[0].write_to_bus()

    def read_bus(self):
        for e in self.elements.values():
            if e.gate == Gate.IN:
                e.read_from_bus(self.bus)

    # ---- innere Aktionen (nach den Bus-Schleifen) ----------
    def apply_actions(self, signals):
        # ALU wurde bereits VOR write_bus konfiguriert und gerechnet
        # (in tick()). Hier nur die "Post-Bus"-Effekte: PC++ und HLT.
        if "CE" in signals and self.pc is not None:
            self.pc.tick()
        if "HLT" in signals:
            self.halted = True

    # ---- Bus zeichnen --------------------------------------
    def draw_bus(self):
        width = self.layout_width
        goto(1, self.bus_y)
        print(c("═" * width, "white"))
        if any(e.gate == Gate.OUT for e in self.elements.values()):
            bus_col = "bgreen"
        else:
            bus_col = "gray"
        label = f" BUS = {self.bus:X}  0b{self.bus:04b} "
        goto(max(1, (width - len(label)) // 2), self.bus_y)
        print(c(label, bus_col))

        for elem in self.elements.values():
            # Nur Elemente OBERHALB des Bus bekommen Stichleitungen
            if elem.y >= self.bus_y:
                continue
            cx = elem.x + elem.width // 2
            bottom = elem.y + elem.height
            if elem.gate == Gate.OUT:
                stem, arrow, col = "│", "▼", "bgreen"
            elif elem.gate == Gate.IN:
                stem, arrow, col = "│", "▲", "bcyan"
            else:
                stem, arrow, col = "┊", "┊", "gray"
            for row in range(bottom, self.bus_y):
                goto(cx, row)
                print(c(arrow if row == self.bus_y - 1 else stem, col))

    # ---- ein Takt ------------------------------------------
    def tick(self):
        """Ein Takt = eine der drei Bus-Schleifen plus innere Aktionen.

        Reihenfolge:
          1) Steuerwort holen (CU)
          2) Gates setzen
          3) ALU konfigurieren + kombinatorisch rechnen
             (WICHTIG: vor write_bus, damit ALU_OUT den frisch
             berechneten Wert auf den Bus legt und nicht ein
             Zwischenergebnis).
          4) write_bus
          5) read_bus (Empfaenger uebernehmen)
          6) Post-Bus-Aktionen: PC++, HLT
          7) Step-Counter weiter
        """
        if self.halted:
            return
        signals = self.cu.next_control_word()
        self.cu.active_signals = signals
        self.set_gates(signals)
        # ALU vor dem Bus rechnen (mit den *alten* ACC/TMP-Werten)
        if self.alu is not None:
            self.alu.apply_signals(signals)
            self.alu.compute()
            self.carry = self.alu.carry
        self.write_bus()
        self.read_bus()
        self.apply_actions(signals)
        self.cu.advance(signals)
        self.tick_counter += 1
