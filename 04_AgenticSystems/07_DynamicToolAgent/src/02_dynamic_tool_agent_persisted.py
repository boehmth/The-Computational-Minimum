"""
02 · dynamic_tool_agent_persisted  —  Kapitel 7, Miniatur 2

Wie Miniatur 1, plus: einmal registrierte Tools werden zusätzlich unter
./generated_tools/ persistiert (eine .py-Datei pro Tool + eine index.json
mit Metadaten). Beim nächsten Programmstart werden sie automatisch
wieder geladen und ERNEUT validiert (die Sicherheitsprüfung greift
also auch für Code, der schon mal erfolgreich generiert wurde — falls
jemand die Dateien manuell verändert hat).

Der Effekt: nach ein paar Läufen hat dein Agent eine kleine, wachsende
Bibliothek an selbst geschriebenen Werkzeugen.

Ausführen:
    python "07_DynamicToolAgent/src/02_dynamic_tool_agent_persisted.py"
    # zweiter Aufruf: "[Persistenz] Geladen: 'is_prime'" -> Skip der Generierung
"""
from __future__ import annotations

import datetime
import importlib.util
import json
import pathlib
import sys
from dataclasses import dataclass, field
from typing import Any, Callable

_HERE = pathlib.Path(__file__).resolve()
_SRC = _HERE.parent
_AS = _SRC.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# 100 % Wiederverwendung: Miniatur 1 liefert Sandbox, Prompts und Agent-Loop.
# Wir überschreiben nur die Registry und den __main__-Block.
_mod_name = "_dynamic_tool_agent_base"
_spec = importlib.util.spec_from_file_location(_mod_name, _SRC / "01_dynamic_tool_agent.py")
assert _spec and _spec.loader
_base = importlib.util.module_from_spec(_spec)
sys.modules[_mod_name] = _base
_spec.loader.exec_module(_base)

Tool = _base.Tool
compile_tool = _base.compile_tool
ToolCodeError = _base.ToolCodeError
DynamicToolAgent = _base.DynamicToolAgent


# ---------------------------------------------------------------------------
# Persistente Registry
# ---------------------------------------------------------------------------

TOOLS_DIR = _SRC / "generated_tools"
TOOLS_INDEX_FILE = TOOLS_DIR / "index.json"


@dataclass
class PersistentToolRegistry:
    """Wie ToolRegistry (Miniatur 1), aber mit Platte-Persistenz.

    - register() schreibt Code + Metadaten in generated_tools/.
    - load_from_disk() liest sie beim Start wieder ein und validiert erneut.
    """
    tools: dict[str, Tool] = field(default_factory=dict)
    persist_dir: pathlib.Path = TOOLS_DIR

    # -- gleiche Schnittstelle wie in Miniatur 1 -----------------------

    def has(self, name: str) -> bool:
        return name in self.tools

    def register(self, name: str, description: str, code: str) -> Tool:
        func = compile_tool(code, name)
        tool = Tool(name=name, description=description, code=code, func=func)
        self.tools[name] = tool
        self._persist_tool(tool)
        return tool

    def call(self, name: str, args: dict[str, Any]) -> Any:
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' existiert nicht")
        return self.tools[name].func(**args)

    def overview(self) -> str:
        if not self.tools:
            return "(noch keine Tools erzeugt)"
        return "\n".join(f"- {t.name}: {t.description}" for t in self.tools.values())

    # -- Persistenz ----------------------------------------------------

    def _tool_file(self, name: str) -> pathlib.Path:
        return self.persist_dir / f"{name}.py"

    def _read_index(self) -> dict[str, dict[str, str]]:
        if not TOOLS_INDEX_FILE.exists():
            return {}
        try:
            return json.loads(TOOLS_INDEX_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_index(self, index: dict[str, dict[str, str]]) -> None:
        TOOLS_INDEX_FILE.write_text(
            json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _persist_tool(self, tool: Tool) -> None:
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._tool_file(tool.name).write_text(tool.code, encoding="utf-8")
        index = self._read_index()
        index[tool.name] = {
            "description": tool.description,
            "file": f"{tool.name}.py",
            "created": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        self._write_index(index)

    def load_from_disk(self, verbose: bool = True) -> None:
        """Lädt zuvor persistierte Tools und validiert sie erneut über
        compile_tool() — die AST-Whitelist gilt also auch für Code, der
        schon mal erfolgreich generiert wurde."""
        index = self._read_index()
        for name, meta in index.items():
            tool_file = self.persist_dir / meta.get("file", f"{name}.py")
            if not tool_file.exists():
                if verbose:
                    print(f"[Persistenz] Übersprungen: '{name}' – Datei fehlt")
                continue
            code = tool_file.read_text(encoding="utf-8")
            try:
                func = compile_tool(code, name)
            except ToolCodeError as e:
                if verbose:
                    print(f"[Persistenz] Übersprungen: '{name}' – ungültig ({e})")
                continue
            self.tools[name] = Tool(
                name=name, description=meta.get("description", ""),
                code=code, func=func,
            )
            if verbose:
                print(f"[Persistenz] Geladen: '{name}'")


# ---------------------------------------------------------------------------
# Beispiel-Aufrufe
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = DynamicToolAgent(max_steps=8, verbose=True)
    # Registry gegen die persistente Variante austauschen — der Agent-Loop
    # selbst weiß nichts von der Persistenz, siehe Kap. 3: der Loop ist
    # dein Code, alle Verantwortlichkeiten sind explizit trennbar.
    agent.registry = PersistentToolRegistry()
    agent.registry.load_from_disk()

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
    print("Am Ende registrierte Tools (persistiert unter generated_tools/):")
    print(agent.registry.overview())