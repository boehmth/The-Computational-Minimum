"""cpu_sim.compiler.codegen -- AST -> Assembler fuer die 2-Register-CPU.

Ziel-CPU: `OS/src/cpu_sim/config_two_reg.py` (AX + BX, ADD/SUB, LDI, LDB,
LDA, LDBM, STA, MOV, OUT, JMP, JC, JZ, HLT, NOP). Also die "klassische"
Zwei-Register-CPU aus dem CPU-Kapitel.

Codegen-Strategie
-----------------
Wir folgen dem klassischen Rekursions-Muster fuer arithmetische
Ausdruecke: **das Ergebnis eines Ausdrucks liegt am Ende in AX**.

  * `Num(n)`  ->  LDI n
  * `Var(x)`  ->  LDA <addr(x)>
  * `BinOp(op, l, r)`:
        <l compilieren>       ; AX := eval(l)
        <r nach BX bringen>   ; via LDB (Immediate), LDBM (Variable),
                              ; oder Temp-Zelle (bei komplexen r)
        ADD / SUB             ; AX := AX (op) BX
  * `Assign(x, e)`:
        <e compilieren>       ; AX := eval(e)
        STA <addr(x)>
  * `Output(e)`:
        <e compilieren>
        OUT
  * `Program`: alle Statements der Reihe nach, dann HLT.

Symboltabelle
-------------
Wir verwalten `{name: ram_addr}`. Neue Variablen kriegen die naechste
freie RAM-Adresse. RAM hat 16 Zellen -- reicht fuer unsere Aufgabe.
"""
from . import astnodes as A


class CodeGenError(Exception):
    pass


class CodeGen:
    """AST -> Liste von Assembler-Zeilen (mit Kommentaren)."""

    RAM_SIZE = 16

    def __init__(self):
        self.symtab = {}
        self.next_addr = 0
        self.lines = []
        self._next_temp_id = 0

    # ---------- Symboltabelle -------------------------------
    def _alloc(self, name):
        if name in self.symtab:
            return self.symtab[name]
        if self.next_addr >= self.RAM_SIZE:
            raise CodeGenError(
                f"Kein RAM-Platz mehr fuer '{name}' "
                f"(nur {self.RAM_SIZE} Zellen)")
        addr = self.next_addr
        self.symtab[name] = addr
        self.next_addr += 1
        return addr

    def _addr_of(self, name):
        if name not in self.symtab:
            raise CodeGenError(f"Unbekannte Variable: {name!r}")
        return self.symtab[name]

    def _alloc_temp(self):
        name = f"$t{self._next_temp_id}"
        self._next_temp_id += 1
        return self._alloc(name)

    # ---------- Emit-Helfer ---------------------------------
    def _emit(self, instr, comment=""):
        if comment:
            self.lines.append(f"{instr:<12}  ; {comment}")
        else:
            self.lines.append(instr)

    def _emit_comment(self, text):
        self.lines.append(f"; {text}")

    # ---------- Ausdruecke ----------------------------------
    def gen_expr(self, node):
        if isinstance(node, A.Num):
            if not 0 <= node.value <= 15:
                raise CodeGenError(
                    f"Zahl {node.value} passt nicht in 4 Bit (0..15).")
            self._emit(f"LDI {node.value:X}", f"AX := {node.value}")
            return

        if isinstance(node, A.Var):
            addr = self._addr_of(node.name)
            self._emit(f"LDA {addr:X}",
                       f"AX := {node.name} (RAM[{addr:X}])")
            return

        if isinstance(node, A.BinOp):
            # Fall 1: rechte Seite ist Zahl -> Immediate in BX
            if isinstance(node.right, A.Num):
                self.gen_expr(node.left)
                self._emit(f"LDB {node.right.value:X}",
                           f"BX := {node.right.value}")
                self._emit_op(node.op)
                return

            # Fall 2: rechte Seite ist Variable -> LDBM direkt aus RAM
            if isinstance(node.right, A.Var):
                addr = self._addr_of(node.right.name)
                self.gen_expr(node.left)
                self._emit(f"LDBM {addr:X}",
                           f"BX := {node.right.name} (RAM[{addr:X}])")
                self._emit_op(node.op)
                return

            # Fall 3: rechts ist komplex -> Temp-Speicher
            temp = self._alloc_temp()
            self.gen_expr(node.right)
            self._emit(f"STA {temp:X}",
                       f"RAM[{temp:X}] := eval(right)  (temp)")
            self.gen_expr(node.left)
            self._emit(f"LDBM {temp:X}",
                       f"BX := temp")
            self._emit_op(node.op)
            return

        raise CodeGenError(f"Unbekannter Ausdruck: {node!r}")

    def _emit_op(self, op):
        if op == "+":
            self._emit("ADD", "AX := AX + BX")
        elif op == "-":
            self._emit("SUB", "AX := AX - BX")
        else:
            raise CodeGenError(f"Unbekannter Operator: {op!r}")

    # ---------- Statements ---------------------------------
    def gen_stmt(self, node):
        if isinstance(node, A.Assign):
            self._emit_comment(f"{node.name} = ...")
            self.gen_expr(node.expr)
            addr = self._alloc(node.name)
            self._emit(f"STA {addr:X}",
                       f"{node.name} (RAM[{addr:X}]) := AX")
            return

        if isinstance(node, A.Output):
            self._emit_comment("output ...")
            self.gen_expr(node.expr)
            self._emit("OUT", "OUT := AX (sichtbar am OUT-Register)")
            return

        raise CodeGenError(f"Unbekanntes Statement: {node!r}")

    # ---------- Programm -----------------------------------
    def gen_program(self, prog):
        if prog.source_language:
            self._emit_comment(f"Kompiliert aus {prog.source_language}")
        if prog.program_name:
            self._emit_comment(f"Programm: {prog.program_name}")
        if prog.author:
            self._emit_comment(f"Autor:    {prog.author}")
        if any([prog.source_language, prog.program_name, prog.author]):
            self._emit_comment("")

        for stmt in prog.statements:
            self.gen_stmt(stmt)

        self._emit_comment("")
        self._emit("HLT", "Programmende")
        return "\n".join(self.lines) + "\n"


def compile_ast(prog):
    """Convenience: nimm einen Program-AST, gib Assembler-String zurueck."""
    return CodeGen().gen_program(prog)