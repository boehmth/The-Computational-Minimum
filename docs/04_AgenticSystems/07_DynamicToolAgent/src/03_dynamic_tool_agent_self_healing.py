"""
03 · dynamic_tool_agent_self_healing  —  Kapitel 7, Miniatur 3

Wie Miniatur 2, plus: wenn der generierte Code die Validierung nicht besteht
ODER beim Aufruf eine Exception wirft, geht der Agent NICHT sofort auf, sondern
lässt ein drittes LLM den Fehler analysieren und den Code reparieren.

Der Reparatur-Loop:
    1. Tool wird generiert   -> ToolCodeError (z. B. Syntax, verbotener Name)
                             ODER
                             -> Tool läuft, wirft aber Exception zur Laufzeit
    2. Runner ruft LLM mit REPAIR_SYSTEM_PROMPT auf. Kontext:
       - Tool-Name + Beschreibung
       - der fehlerhafte Code
       - die konkrete Fehlermeldung (ToolCodeError-Text oder traceback)
    3. LLM liefert reparierten Code zurück.
    4. Neuer Validierungs-Versuch. Bei Erfolg: Registry updaten und weiter.
       Bei erneutem Fehler: max. N-1 weitere Versuche, dann aufgeben.

Warum das interessant ist:
    In Kap. 3 (03_retry_strategies) haben wir vier Retry-Strategien vergleichen:
    naive, exponential backoff, circuit breaker, LLM-guided recovery. Genau die
    letzte Strategie wiederholt sich hier eine Ebene tiefer: das LLM debuggt
    seinen eigenen generierten Code. Das ist keine neue Idee -- es ist die
    Rekursion von Kap. 3 auf Kap. 7.

Wie in den anderen Miniaturen:
    Sandbox, Prompts, Agent-Loop kommen unverändert aus Miniatur 1.
    Persistenz-Schicht kommt unverändert aus Miniatur 2.
    Nur die Registry wird durch eine `SelfHealingToolRegistry` ersetzt.

Ausführen:
    python "07_DynamicToolAgent/src/03_dynamic_tool_agent_self_healing.py"
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys
import traceback
from dataclasses import dataclass
from typing import Any

_HERE = pathlib.Path(__file__).resolve()
_SRC = _HERE.parent
_AS = _SRC.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

# Miniatur 1 (Basis) + Miniatur 2 (Persistenz) laden -- wieder ohne Import-Magie.
# Die Zahlen-Präfixe im Dateinamen machen einen normalen `import` unmöglich.
def _load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_base = _load_module("_dta_base", _SRC / "01_dynamic_tool_agent.py")
_persisted = _load_module("_dta_persisted", _SRC / "02_dynamic_tool_agent_persisted.py")

Tool = _base.Tool
ToolCodeError = _base.ToolCodeError
compile_tool = _base.compile_tool
DynamicToolAgent = _base.DynamicToolAgent
_strip_code_fences = _base._strip_code_fences

PersistentToolRegistry = _persisted.PersistentToolRegistry

from common.llm import chat  # noqa: E402


# ---------------------------------------------------------------------------
# Repair-Prompt: ein spezialisierter System-Prompt nur fürs Debuggen
# ---------------------------------------------------------------------------

REPAIR_SYSTEM_PROMPT = """\
Du bist ein Python-Debugger. Du bekommst:
1. Den Namen und die Beschreibung eines Tools, das gebraucht wird.
2. Einen Python-Code-Versuch, der die Validierung nicht bestanden hat ODER \
zur Laufzeit einen Fehler geworfen hat.
3. Die konkrete Fehlermeldung.

Deine Aufgabe: den Code so umschreiben, dass er FUNKTIONIERT und die \
gleichen Regeln einhält wie beim ursprünglichen Generator:

- Genau eine Top-Level-Funktion mit exakt dem geforderten Namen.
- Nur benannte Parameter mit Typ-Annotationen.
- JSON-serialisierbarer Rückgabewert.
- Erlaubte Module (vollqualifiziert, ohne eigene imports): math, re, statistics, datetime.
- KEIN eval, exec, __import__, open, Dunder-Attribute, kein global/nonlocal.
- Robuste Eingabeprüfung, ValueError bei ungültigen Eingaben.

Gib AUSSCHLIESSLICH den reparierten Python-Code zurück -- keine Erklärung, \
kein Fließtext, keine Markdown-Codeblöcke. Konzentriere dich auf den \
konkreten Fehler und behebe ihn minimal-invasiv; behalte die ursprüngliche \
Intention der Funktion so weit wie möglich.

Tool-Name: {tool_name}
Tool-Beschreibung: {tool_description}

Fehlerhafter Code:
---
{broken_code}
---

Fehlermeldung:
{error_message}
"""


# ---------------------------------------------------------------------------
# SelfHealingToolRegistry
# ---------------------------------------------------------------------------

@dataclass
class SelfHealingToolRegistry(PersistentToolRegistry):
    """Persistente Registry, die bei ToolCodeError oder Runtime-Exception
    einen Repair-LLM-Aufruf startet und den Code erneut validiert.

    max_repair_attempts: wie viele zusätzliche LLM-Aufrufe pro Tool erlaubt
    sind. 0 = kein Self-Healing (dann wie Miniatur 2).
    """
    max_repair_attempts: int = 2
    verbose: bool = True

    # -- Register mit Self-Healing -------------------------------------

    def register(self, name: str, description: str, code: str) -> Tool:
        """Wie in Miniatur 2, aber bei ToolCodeError wird repariert."""
        attempt = 0
        current_code = code
        while True:
            try:
                # compile_tool validiert per AST + führt exec() aus.
                func = compile_tool(current_code, name)
                tool = Tool(name=name, description=description,
                            code=current_code, func=func)
                self.tools[name] = tool
                self._persist_tool(tool)
                if attempt > 0:
                    self._log(f"    [repair] Erfolgreich nach {attempt} Reparatur(en).")
                return tool
            except ToolCodeError as e:
                attempt += 1
                if attempt > self.max_repair_attempts:
                    self._log(f"    [repair] Aufgegeben nach {attempt-1} "
                              f"Reparatur-Versuchen: {e}")
                    raise
                self._log(f"    [repair] Versuch {attempt}/{self.max_repair_attempts}: "
                          f"'{e}' -- rufe Repair-LLM...")
                current_code = self._repair_code(name, description,
                                                 current_code, str(e))

    # -- Call mit Self-Healing -----------------------------------------

    def call(self, name: str, args: dict[str, Any]) -> Any:
        """Wie in Miniatur 2, aber Runtime-Exceptions triggern eine
        Reparatur des Tool-Codes. Falls die Reparatur erfolgreich ist,
        wird das Tool sofort mit den ursprünglichen Argumenten erneut
        aufgerufen."""
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' existiert nicht")

        attempt = 0
        while True:
            tool = self.tools[name]
            try:
                return tool.func(**args)
            except Exception as e:
                # ValueError-Wurf durch Input-Validation ist gewollt und
                # wird nicht als Bug behandelt -- der Agent soll die
                # Fehlermeldung sehen und mit anderen Args erneut rufen.
                if isinstance(e, ValueError):
                    raise
                attempt += 1
                if attempt > self.max_repair_attempts:
                    self._log(f"    [repair] Runtime-Fehler in '{name}' nach "
                              f"{attempt-1} Reparatur-Versuchen aufgegeben: {e}")
                    raise
                tb = traceback.format_exc(limit=3)
                self._log(f"    [repair] Runtime-Fehler in '{name}': {type(e).__name__}: {e}")
                self._log(f"    [repair] Versuch {attempt}/{self.max_repair_attempts} "
                          f"-- rufe Repair-LLM...")
                new_code = self._repair_code(name, tool.description, tool.code, tb)
                try:
                    new_func = compile_tool(new_code, name)
                except ToolCodeError as e2:
                    self._log(f"    [repair] Repair-Code war selbst ungültig: {e2}")
                    continue
                # Registry updaten, dann Loop wiederholen.
                repaired = Tool(name=name, description=tool.description,
                                code=new_code, func=new_func)
                self.tools[name] = repaired
                self._persist_tool(repaired)

    # -- Repair-LLM-Aufruf ---------------------------------------------

    def _repair_code(self, name: str, description: str,
                     broken_code: str, error_message: str) -> str:
        system = REPAIR_SYSTEM_PROMPT.format(
            tool_name=name,
            tool_description=description,
            broken_code=broken_code,
            error_message=error_message,
        )
        r = chat(system=system, user="Erzeuge den reparierten Code jetzt.")
        return _strip_code_fences(r.text)

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)


# ---------------------------------------------------------------------------
# Beispiel-Aufrufe
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = DynamicToolAgent(max_steps=8, verbose=True)
    # Wir tauschen die Registry gegen die selbst-heilende Variante.
    # Der Agent-Loop weiß davon nichts -- die Retry-Politik lebt in der
    # Registry, so wie in Kap. 3 die Retry-Politik in einer separaten Klasse
    # lebt statt im Loop-Rumpf. Prinzip 3 in seiner sauberen Form.
    agent.registry = SelfHealingToolRegistry(max_repair_attempts=2, verbose=True)
    agent.registry.load_from_disk()

    # Zwei Klassen von Aufgaben, um beide Repair-Pfade sichtbar zu machen:
    #
    #  (a) Aufgaben, bei denen der Generator meist auf Anhieb korrektem Code
    #      liefert -- Self-Healing bleibt still. Das ist der Normalfall.
    #  (b) Eine Aufgabe, die einen Runtime-Edge-Case triggert (Division durch
    #      Null oder ähnlich). Hier wird der Repair-Loop aktiv, weil das Tool
    #      im ersten Wurf oft nicht sauber genug validiert.
    beispiele = [
        "Was ist 12345 * 6789?",
        "Berechne den Median der Liste [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5].",
        # Diese Aufgabe zwingt das Modell, ein Tool zu bauen, das intern
        # dividieren muss -- ein häufiges Loch bei generiertem Code ist,
        # den Nulldivisions-Fall zu übersehen.
        "Was ist das arithmetische Mittel der Liste [10, 20, 30] "
        "geteilt durch das Mittel der Liste [] (leere Liste)?",
    ]

    for frage in beispiele:
        print("=" * 70)
        print(f"FRAGE: {frage}")
        antwort = agent.run(frage)
        print(f"ANTWORT: {antwort}")

    print("=" * 70)
    print("Am Ende registrierte Tools (persistiert unter generated_tools/):")
    print(agent.registry.overview())
    print()
    print("Vergleich zu Miniatur 2:")
    print("  Bei jedem [repair]-Log oben hätte Miniatur 2 die Aufgabe aufgegeben.")
    print("  Hier hat das Modell den generierten Code selbst korrigiert und der")
    print("  Loop lief weiter -- eine LLM-guided-Recovery-Strategie wie in Kap. 3,")
    print("  aber angewandt auf den vom Modell selbst geschriebenen Code.")
