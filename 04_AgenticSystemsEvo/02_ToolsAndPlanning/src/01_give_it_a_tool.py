"""
01 · give_it_a_tool  —  Kapitel 2, Miniatur 1

Slide-Anker :  P2 in Miniatur — das Modell emittiert JSON, wir führen aus
Laufzeit    :  < 5 Sekunden
Kosten      :  ~120 Tokens

Dieselbe Multiplikation wie in Kapitel 1 — aber diesmal antwortet das
Modell nicht mit einer Zahl, sondern mit einem Werkzeug-Aufruf.

Zwei Verantwortungen, sichtbar getrennt:

    Das Modell     ->  identifiziert die Absicht, produziert das JSON
    Der Orchestrator ->  parst das JSON, führt Python aus

Der Fehler aus Kapitel 1 ist verschwunden — nicht weil das Modell
besser rechnet, sondern weil es nicht mehr rechnet.

Ausführen:
    python "Agentic Systems/02_ToolsAndPlanning/src/01_give_it_a_tool.py"
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS   = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat, extract_json
from common.ui  import hard_card, soft_frame, wrap


# ---------------------------------------------------------------------------
# Das Werkzeug (deterministisches Python, keine Magie)
# ---------------------------------------------------------------------------

def calculator(operation: str, a: float, b: float) -> float:
    ops = {"multiply": lambda x, y: x * y,
           "add":      lambda x, y: x + y,
           "subtract": lambda x, y: x - y,
           "divide":   lambda x, y: x / y}
    return ops[operation](a, b)


# ---------------------------------------------------------------------------
# Der System-Prompt, der das Werkzeug beschreibt
# ---------------------------------------------------------------------------

SYSTEM = """Du bist ein Einkaufsassistent. Du hast EIN Werkzeug:

  calculator(operation, a, b)

Um es zu benutzen, antworte AUSSCHLIESSLICH mit diesem JSON-Objekt und
nichts anderem:

  {"tool": "calculator", "operation": "multiply|add|subtract|divide",
   "a": <Zahl>, "b": <Zahl>}

Wenn keine Rechnung nötig ist, antworte im Klartext."""


def main():
    # Wir benutzen absichtlich Zahlen ohne Tausender-Trennzeichen und ohne
    # Komma, um den deutschen/englischen Dezimal-Konflikt zu vermeiden.
    # (Was passiert wenn man ihn nicht vermeidet, ist Übung 3 in Kapitel 6.)
    aufgabe = "Was ist der Gesamtpreis für 43177 Einheiten zu je 14694 EUR?"
    soft_frame("DIE AUFGABE", wrap(aufgabe))

    # 1) Modell erzeugt den Werkzeug-Aufruf als Text.
    r = chat(system=SYSTEM, user=aufgabe, want_json=True)
    hard_card(
        title    = "▸  MODELL-Output  (reiner Text)",
        subtitle = f"{r.tokens_out} Tokens · {r.model}",
        body     = r.text,
    )

    # 2) Orchestrator parst das JSON.
    try:
        call = extract_json(r.text)
    except Exception as e:
        soft_frame(
            "PARSE-FEHLER",
            [f"Das Modell hat kein sauberes JSON geliefert: {e}",
             "In Kapitel 3 sehen wir, was man dann tut (Retry-Policy)."],
        )
        return

    soft_frame(
        "ORCHESTRATOR hat geparst",
        [
            f"tool       : {call.get('tool')}",
            f"operation  : {call.get('operation')}",
            f"a          : {call.get('a'):,}",
            f"b          : {call.get('b'):,}",
        ],
    )

    # 3) Orchestrator führt das Werkzeug aus (deterministisch).
    result = calculator(call["operation"], call["a"], call["b"])
    soft_frame(
        "ORCHESTRATOR hat das Werkzeug ausgeführt",
        [
            f"{int(call['a']):,} × {int(call['b']):,}  =  {int(result):,} EUR",
            "",
            "Vergleich zu Kapitel 1: da rechnete das Modell selbst,",
            "                       Fehler war ~145,000.",
            "Hier rechnet Python.  Fehler ist 0.",
        ],
    )

    print()
    print("→ Modell identifiziert die Notwendigkeit.  Python führt aus.")
    print("→ Diese Trennung ist die Vertrauensgrenze jedes Agenten.")


if __name__ == "__main__":
    main()