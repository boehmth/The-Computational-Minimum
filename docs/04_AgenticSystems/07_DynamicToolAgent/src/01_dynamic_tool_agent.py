"""
01 · dynamic_tool_agent  —  Kapitel 7, Miniatur 1

Slide-Anker :  P3 in seiner härtesten Form — der Agent schreibt sich Werkzeuge selbst
Laufzeit    :  10–60 Sekunden (mehrere LLM-Aufrufe pro Aufgabe)
Kosten      :  einige tausend Tokens (Agent-Turn + Tool-Generierung)

Drei mögliche Aktionen pro Turn, jede als JSON:
    generate_tool  -> Runner ruft zweites LLM für Code-Generierung auf,
                      validiert per AST-Whitelist, registriert die Funktion.
    call_tool      -> Runner ruft eine registrierte Funktion mit Argumenten auf.
    final_answer   -> Loop-Ende.

WICHTIG (nur zu Lehrzwecken):
Die AST-Whitelist + eingeschränkte Builtins sind eine didaktische Annäherung,
KEIN Ersatz für echtes Sandboxing (Subprozess + Ressourcenlimits, WASM-Sandbox,
RestrictedPython). Nicht produktiv mit nicht-vertrauenswürdigem Input nutzen.

Ausführen:
    python "07_DynamicToolAgent/src/01_dynamic_tool_agent.py"
"""
from __future__ import annotations

import ast
import datetime
import math
import re
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

_HERE = Path(__file__).resolve()
_AS = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat, extract_json  # noqa: E402


AGENT_SYSTEM_PROMPT = """\
Du bist ein Agent, der Aufgaben löst, indem du bei Bedarf Werkzeuge (Tools) benutzt. Du selbst kannst NICHT zuverlässig rechnen oder exakte Datenverarbeitung durchführen – dafür brauchst du Tools.

Du bekommst in jeder Nachricht entweder die Original-Aufgabe oder das Ergebnis einer vorherigen Aktion. Du antwortest IMMER ausschließlich mit einem einzigen JSON-Objekt (kein Fließtext davor oder danach, keine Markdown-Codeblöcke), mit genau einem der folgenden drei Formate:

1) Ein neues Tool wird benötigt:
{"thought": "...", "action": "generate_tool", "tool_name": "snake_case_name", "tool_description": "präzise Beschreibung inkl. Parameter mit Typen und Rückgabewert"}

2) Ein bereits existierendes Tool aufrufen:
{"thought": "...", "action": "call_tool", "tool_name": "name", "tool_args": {"param1": "wert1"}}

3) Aufgabe abschließend beantworten:
{"thought": "...", "action": "final_answer", "answer": "die Antwort für den Nutzer"}

Regeln:
- Prüfe zuerst, ob ein passendes Tool in "Verfügbare Tools" existiert.
- Erzeuge Tools allgemein/wiederverwendbar (z. B. "fakultaet_berechnen" statt "fakultaet_von_12").
- Tools sind reine, zustandslose Funktionen ohne Seiteneffekte.
- Bei Fehler: Tool neu generieren oder mit anderen Args erneut aufrufen.
- Antworte NUR mit dem JSON-Objekt.
"""

TOOL_GENERATOR_SYSTEM_PROMPT = """\
Du generierst Python-Code für genau EINE Funktion, die als Tool läuft. Vorgaben:

- NUR Python-Code, keine Erklärungen, keine Markdown-Codeblöcke, kein Text davor/danach.
- Genau eine Top-Level-Funktion mit exakt dem geforderten Namen.
- Ausschließlich benannte Parameter (keine *args/**kwargs) mit Typ-Annotationen.
- Rückgabewert JSON-serialisierbar (str, int, float, bool, list, dict).
- Erlaubte Module (bereits importiert, voll qualifiziert verwenden): math, re, statistics, datetime.
- KEINE eigenen imports, kein open(), eval(), exec(), __import__, keine Dunder-Namen, keine Netzwerk-/Dateizugriffe, kein global/nonlocal.
- Robuste Eingabeprüfung, ValueError bei ungültigen Eingaben.

Erzeuge jetzt den Code für:
Name: {tool_name}
Beschreibung: {tool_description}
"""


# ---------------------------------------------------------------------------
# Sandbox
# ---------------------------------------------------------------------------

_ALLOWED_BUILTIN_NAMES = (
    "len", "range", "abs", "min", "max", "sum", "round", "sorted",
    "str", "int", "float", "list", "dict", "tuple", "set", "bool",
    "enumerate", "zip", "map", "filter", "isinstance", "all", "any",
    "Exception", "ValueError", "TypeError", "ZeroDivisionError",
    "IndexError", "KeyError", "StopIteration",
)
_bns = __builtins__ if isinstance(__builtins__, dict) else vars(__builtins__)
ALLOWED_BUILTINS = {n: _bns[n] for n in _ALLOWED_BUILTIN_NAMES if n in _bns}

FORBIDDEN_NAMES = {
    "eval", "exec", "compile", "open", "__import__", "input", "globals",
    "locals", "vars", "getattr", "setattr", "delattr", "breakpoint",
    "os", "sys", "subprocess", "socket", "shutil", "pathlib",
}


class ToolCodeError(Exception):
    """Generierter Tool-Code besteht die Validierung nicht."""


def _validate_tool_ast(code: str, tool_name: str) -> ast.FunctionDef:
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as e:
        raise ToolCodeError(f"Kein gültiges Python: {e}")

    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    if len(funcs) != 1:
        raise ToolCodeError(f"Erwartet 1 Top-Level-Funktion, gefunden: {len(funcs)}")
    func = funcs[0]
    if func.name != tool_name:
        raise ToolCodeError(f"Funktionsname '{func.name}' != erwartet '{tool_name}'")
    if func.args.vararg or func.args.kwarg:
        raise ToolCodeError("*args/**kwargs sind nicht erlaubt")

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise ToolCodeError("Eigene imports nicht erlaubt")
        if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            raise ToolCodeError(f"Verbotener Name: {node.id}")
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise ToolCodeError(f"Dunder-Attribut verboten: {node.attr}")
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            raise ToolCodeError("global/nonlocal nicht erlaubt")
    return func


def compile_tool(code: str, tool_name: str) -> Callable[..., Any]:
    _validate_tool_ast(code, tool_name)
    sandbox: dict[str, Any] = {
        "__builtins__": ALLOWED_BUILTINS,
        "math": math, "re": re, "statistics": statistics, "datetime": datetime,
    }
    try:
        exec(compile(code, filename=f"<tool:{tool_name}>", mode="exec"), sandbox)
    except Exception as e:
        raise ToolCodeError(f"Fehler beim Kompilieren: {e}")
    func = sandbox.get(tool_name)
    if not callable(func):
        raise ToolCodeError(f"Keine Funktion '{tool_name}' nach exec()")
    return func


# ---------------------------------------------------------------------------
# Tool-Registry
# ---------------------------------------------------------------------------

@dataclass
class Tool:
    name: str
    description: str
    code: str
    func: Callable[..., Any]


@dataclass
class ToolRegistry:
    tools: dict[str, Tool] = field(default_factory=dict)

    def has(self, name: str) -> bool:
        return name in self.tools

    def register(self, name: str, description: str, code: str) -> Tool:
        func = compile_tool(code, name)
        tool = Tool(name=name, description=description, code=code, func=func)
        self.tools[name] = tool
        return tool

    def call(self, name: str, args: dict[str, Any]) -> Any:
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' existiert nicht")
        return self.tools[name].func(**args)

    def overview(self) -> str:
        if not self.tools:
            return "(noch keine Tools erzeugt)"
        return "\n".join(f"- {t.name}: {t.description}" for t in self.tools.values())


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

def _strip_code_fences(code: str) -> str:
    code = code.strip()
    code = re.sub(r"^```(python)?", "", code).rstrip("`").strip()
    return code


class DynamicToolAgent:
    def __init__(self, max_steps: int = 8, verbose: bool = True):
        self.registry = ToolRegistry()
        self.max_steps = max_steps
        self.verbose = verbose

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    def run(self, task: str) -> str:
        # Wir bauen die "Konversationshistorie" als Text auf, den wir bei
        # jedem Turn als User-Nachricht mitschicken. Das ist bewusst simpel
        # — common/llm.chat() ist single-turn, also serialisieren wir hier
        # die Historie selbst (siehe Kap. 3: der Loop ist dein Code).
        history: list[str] = [f"Aufgabe: {task}"]

        for step in range(1, self.max_steps + 1):
            system = AGENT_SYSTEM_PROMPT + "\n\nVerfügbare Tools:\n" + self.registry.overview()
            user = "\n\n".join(history)

            r = chat(system=system, user=user, want_json=True)
            history.append(f"[Assistant] {r.text}")

            try:
                data = extract_json(r.text)
            except ValueError as e:
                self._log(f"[Schritt {step}] Antwort nicht als JSON parsebar: {e}")
                history.append(
                    "[System] Deine letzte Antwort war kein gültiges JSON im "
                    "geforderten Format. Bitte nur mit einem JSON-Objekt antworten."
                )
                continue

            action = data.get("action")
            self._log(f"[Schritt {step}] {data.get('thought', '')!r} -> action={action}")

            if action == "final_answer":
                return data.get("answer", "(keine Antwort geliefert)")

            elif action == "generate_tool":
                name = data["tool_name"]
                description = data["tool_description"]
                if self.registry.has(name):
                    result = f"Tool '{name}' existiert bereits, du kannst es direkt aufrufen."
                else:
                    result = self._generate_and_register(name, description)
                history.append(f"[System] {result}")

            elif action == "call_tool":
                name = data["tool_name"]
                args = data.get("tool_args", {}) or {}
                if not self.registry.has(name):
                    result = f"Fehler: Tool '{name}' existiert nicht. Erst generieren."
                else:
                    try:
                        value = self.registry.call(name, args)
                        result = f"Ergebnis von '{name}({args})': {value!r}"
                        self._log(f"    -> {result}")
                    except Exception as e:
                        result = f"Fehler beim Ausführen von '{name}({args})': {e}"
                        self._log(f"    -> {result}")
                history.append(f"[System] {result}")

            else:
                history.append(
                    f"[System] Unbekannte action '{action}'. Erlaubt: "
                    "generate_tool, call_tool, final_answer."
                )

        return "(Maximale Anzahl Schritte erreicht, ohne finale Antwort.)"

    def _generate_and_register(self, name: str, description: str) -> str:
        self._log(f"    -> generiere Tool-Code für '{name}' ...")
        prompt = TOOL_GENERATOR_SYSTEM_PROMPT.format(
            tool_name=name, tool_description=description
        )
        r = chat(system=prompt, user="Erzeuge den Code jetzt.")
        code = _strip_code_fences(r.text)

        try:
            tool = self.registry.register(name, description, code)
            self._log(f"    -> Tool '{name}' registriert:\n{tool.code}\n")
            return f"Tool '{name}' wurde erfolgreich erstellt und ist jetzt verfügbar."
        except ToolCodeError as e:
            self._log(f"    -> Validierung fehlgeschlagen: {e}\n{code}\n")
            return f"Fehler: generierter Code für '{name}' war ungültig: {e}"


# ---------------------------------------------------------------------------
# Beispiel-Aufrufe
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = DynamicToolAgent(max_steps=8, verbose=True)

    beispiele = [
        "Was ist 12345 * 6789?",
        "Wie viele Meter sind 3.5 Meilen?",
        "Ist 97 eine Primzahl?",
        "Berechne die Fakultät von 12.",
    ]

    for frage in beispiele:
        print("=" * 70)
        print(f"FRAGE: {frage}")
        antwort = agent.run(frage)
        print(f"ANTWORT: {antwort}")

    print("=" * 70)
    print("Am Ende registrierte Tools:")
    print(agent.registry.overview())
