"""
02 · model_plans  —  Kapitel 2, Miniatur 2

Slide-Anker :  P2 — same tools, three prompts, three different plans
Laufzeit    :  ~10 Sekunden
Kosten      :  ~800-1500 Tokens

Zwei Werkzeuge, drei natürlichsprachliche Aufgaben.  Das Modell
produziert für jede Aufgabe einen unterschiedlichen Plan.  Kein
if/elif in unserem Code.

Das ist Prinzip 2 in Aktion.

Ausführen:
    python "Agentic Systems/02_ToolsAndPlanning/src/02_model_plans.py"
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS   = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat, extract_json
from common.ui  import soft_frame, phase_break, wrap


SYSTEM = """Du bist ein Einkaufsassistent. Du hast zwei Werkzeuge:

  calculator(operation, a, b)
       operation ∈ {multiply, add, subtract, divide}

  currency_converter(amount, source, target)
       source, target ∈ {EUR, USD}

Antworte AUSSCHLIESSLICH mit strikt gültigem JSON in diesem Schema:

  {
    "intent": "<ein Satz>",
    "plan": [
      {"tool": "calculator",         "operation": "...", "a": ..., "b": ...},
      {"tool": "currency_converter", "amount": ..., "source": "...", "target": "..."}
    ]
  }

Führe NICHTS aus.  Gib nur den Plan zurück."""


# Zahlen ohne Tausender-Trennzeichen, um den deutschen/englischen
# Dezimal-Konflikt zu vermeiden.
AUFGABEN = [
    "Was ist der Gesamtpreis für 43177 Einheiten zu je 14694 EUR?",
    "Ich habe ein Budget von 132877 USD — wie viele Einheiten kann ich zu je 5.30 EUR pro Stück kaufen?",
    "Was ist der Gesamtpreis in EUR für 43177 Einheiten zu je 14694 USD?",
]


def render_plan(plan_obj: dict) -> list[str]:
    """Verwandle die JSON-Antwort in menschenlesbare Zeilen für ein soft_frame."""
    lines = [f"intent : {plan_obj.get('intent', '(kein intent angegeben)')}"]
    steps = plan_obj.get("plan") or []
    if not steps:
        lines.append("(kein Plan im Response — Modell hat vermutlich prosaisch geantwortet)")
        return lines
    for i, step in enumerate(steps, start=1):
        tool = step.get("tool")
        details = {k: v for k, v in step.items() if k != "tool"}
        lines.append(f"step {i}: {tool}({details})")
    return lines


def main():
    for i, aufgabe in enumerate(AUFGABEN, start=1):
        phase_break(f"AUFGABE {i}")
        soft_frame("Aufgabe (natürliche Sprache)", wrap(aufgabe))

        r = chat(system=SYSTEM, user=aufgabe, want_json=True)

        try:
            plan_obj = extract_json(r.text)
        except Exception as e:
            soft_frame(
                "Parse-Fehler",
                [f"{e}", "", "Roh-Output:", *wrap(r.text)],
            )
            continue

        soft_frame(
            f"Plan des Modells   ({r.tokens_out} Tokens ausgehend)",
            render_plan(plan_obj),
        )

    print()
    print("→ Dasselbe Werkzeug-Set, drei Aufgaben, drei verschiedene Pläne.")
    print("→ Kein Ingenieur hat 'wenn USD im Text, dann konvertiere' geschrieben.")
    print("→ Das Modell entscheidet den Ablauf zur Laufzeit — Prinzip 2.")


if __name__ == "__main__":
    main()