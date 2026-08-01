"""cpu_sim.compiler.ast -- gemeinsamer AST fuer alle Frontends.

Idee: jedes Sprach-Frontend parst seinen eigenen Text und produziert
denselben AST. Der Codegenerator (codegen.py) kennt nur den AST, nicht
die Quellsprache. Damit ist der Compiler *modular*: neue Sprachen
kosten nur ein Frontend.

Der AST ist bewusst minimalistisch, weil unsere Ziel-Aufgabe minimal
ist:

    (3 + 4) - 1

Wir brauchen:
  * Zahl-Literale        (Num)
  * Variablen-Referenzen (Var)
  * binaere Operationen  (BinOp: +, -)
  * Zuweisungen          (Assign)
  * Ausgabe              (Output)
  * eine Sequenz         (Program: Liste von Statements)

Fuer spaetere Ausbaustufen (Schleifen, if) waeren zusaetzliche
Node-Typen noetig -- die Struktur bleibt aber dieselbe.
"""
from dataclasses import dataclass, field
from typing import List, Optional


# ============================================================
# AST-Knoten
# ============================================================

@dataclass
class Num:
    """Zahl-Literal, 4-Bit-Wert (0..15)."""
    value: int


@dataclass
class Var:
    """Variablen-Referenz."""
    name: str


@dataclass
class BinOp:
    """Binaere Operation: op in {'+', '-'}."""
    op: str
    left: object     # AST-Knoten
    right: object    # AST-Knoten


@dataclass
class Assign:
    """Zuweisung: name = expr."""
    name: str
    expr: object     # AST-Knoten


@dataclass
class Output:
    """Ausgabe eines Ausdrucks (OUT-Register)."""
    expr: object


@dataclass
class Program:
    """Wurzelknoten: Liste von Statements + optionale Metadaten."""
    statements: List[object] = field(default_factory=list)
    # Metadaten aus dem Boilerplate (fuer die Compiler-Meldung)
    program_name: Optional[str] = None
    author: Optional[str] = None
    source_language: Optional[str] = None


# ============================================================
# Pretty-Print (fuer Debugging und Doku)
# ============================================================

def pp(node, indent=0) -> str:
    """AST als lesbare Baumstruktur ausgeben."""
    prefix = "  " * indent
    if isinstance(node, Program):
        lines = [f"{prefix}Program(name={node.program_name!r}, "
                 f"author={node.author!r}, lang={node.source_language!r})"]
        for stmt in node.statements:
            lines.append(pp(stmt, indent + 1))
        return "\n".join(lines)
    if isinstance(node, Num):
        return f"{prefix}Num({node.value})"
    if isinstance(node, Var):
        return f"{prefix}Var({node.name!r})"
    if isinstance(node, BinOp):
        return (f"{prefix}BinOp({node.op!r})\n"
                f"{pp(node.left,  indent+1)}\n"
                f"{pp(node.right, indent+1)}")
    if isinstance(node, Assign):
        return (f"{prefix}Assign({node.name!r})\n"
                f"{pp(node.expr, indent+1)}")
    if isinstance(node, Output):
        return (f"{prefix}Output\n"
                f"{pp(node.expr, indent+1)}")
    return f"{prefix}<?{node!r}?>"