"""
01 · agent_vs_sum  —  Kapitel 6, Miniatur 1

Slide-Anker :  P3 Kehrseite · nicht jedes Werkzeug ist ein Nagel
Laufzeit    :  ~5 Sekunden
Kosten      :  ~150 Tokens (nur der Agent — sum() ist gratis)

Wir bauen ABSICHTLICH einen Agenten für eine Aufgabe, die niemand
mit einem Agenten lösen sollte:  sum([1,2,3,4,5]).

Vergleich:
  A · Python-Einzeiler        1 Mikrosekunde, 0 Tokens
  B · LLM-Agent               ~2 Sekunden,   ~80 Tokens

Ausführen:
    python "Agentic Systems/06_WhenNotToBuild/src/01_agent_vs_sum.py"
"""

import json
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS   = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat, extract_json
from common.ui  import hard_card, soft_frame, phase_break, wrap


NUMBERS = [1, 2, 3, 4, 5]


# ===========================================================================
#  Weg A · Python-Einzeiler
# ===========================================================================

def way_a_python():
    t0 = time.perf_counter_ns()
    result = sum(NUMBERS)
    latency_ns = time.perf_counter_ns() - t0
    return {"result": result, "latency_ns": latency_ns, "tokens": 0}


# ===========================================================================
#  Weg B · Agent mit calculator-Tool
# ===========================================================================

SYSTEM = """Du bist ein Rechenassistent.  Du hast EIN Werkzeug:

  calculator(operation, a, b)      # operation ∈ {add, subtract, multiply, divide}

Antworte AUSSCHLIESSLICH mit einem JSON-Objekt:
  {"tool": "calculator", "operation": "add", "a": <Zahl>, "b": <Zahl>}
    oder
  {"final": <Ergebnis als Zahl>}"""


def calculator(operation, a, b):
    return {"add": a + b, "subtract": a - b,
            "multiply": a * b, "divide": a / b}[operation]


def way_b_agent():
    """Ein winziger Loop.  Modell addiert Paar für Paar bis {"final": ...}."""
    t0 = time.perf_counter()
    task = (f"Was ist die Summe von {NUMBERS}?  "
            f"Nutze das calculator-Werkzeug Schritt für Schritt.")
    history = [{"role": "user", "content": task}]
    total_tokens = 0

    for turn in range(1, 15):
        prompt = "\n\n".join(f"{m['role'].upper()}: {m['content']}"
                             for m in history)
        r = chat(system=SYSTEM, user=prompt, want_json=True, max_tokens=256)
        total_tokens += r.tokens
        msg = extract_json(r.text)

        if "final" in msg:
            latency = time.perf_counter() - t0
            return {
                "result": msg["final"],
                "latency_s": latency,
                "tokens": total_tokens,
                "turns": turn,
            }

        name = msg["tool"]
        args = {k: v for k, v in msg.items() if k != "tool"}
        try:
            obs = calculator(**{k: args[k] for k in ("operation", "a", "b")})
        except Exception as e:
            obs = f"error: {e}"

        history.append({"role": "assistant", "content": r.text})
        history.append({"role": "user",
                        "content": f"[observation] calculator({args}) = {obs}"})

    return {"result": None, "latency_s": time.perf_counter() - t0,
            "tokens": total_tokens, "turns": -1,
            "note": "max turns exceeded"}


# ===========================================================================
#  Main
# ===========================================================================

def main():
    phase_break("agent_vs_sum.py  ·  absurder Vergleich, echter Punkt")

    soft_frame(
        "DIE AUFGABE (dieselbe für beide Wege)",
        [
            f"Summe von {NUMBERS} berechnen.",
            "Erwartete Antwort:  15",
            "Kein Zweifel.  Keine Interpretation.  Kein Urteilsvermögen nötig.",
        ],
    )

    # ---- Weg A ----
    phase_break("WEG A · sum() aus der Standardbibliothek")
    a = way_a_python()
    soft_frame(
        "Ergebnis",
        [
            f"result   : {a['result']}",
            f"latency  : {a['latency_ns']:>10} ns  "
            f"({a['latency_ns'] / 1000:.2f} µs)",
            f"tokens   : {a['tokens']}",
            "",
            "Code:  sum([1, 2, 3, 4, 5])",
        ],
    )

    # ---- Weg B ----
    phase_break("WEG B · LLM-Agent mit calculator-Werkzeug")
    print("  Der Agent läuft jetzt (kann 2-10 Sekunden dauern)...")
    print()
    b = way_b_agent()
    soft_frame(
        "Ergebnis",
        [
            f"result   : {b['result']}",
            f"latency  : {b['latency_s']:>10.3f} s  "
            f"({b['latency_s'] * 1_000_000_000:.0f} ns)",
            f"tokens   : {b['tokens']}",
            f"turns    : {b.get('turns', '?')}  "
            f"(HTTP-Aufrufe an das Modell)",
        ],
    )

    # ---- Vergleich ----
    if a["result"] == b["result"]:
        correctness = "✓ beide gleich"
    else:
        correctness = "✗ verschieden — Weg B hat sich verrechnet"

    ratio_latency = (b["latency_s"] * 1e9) / max(a["latency_ns"], 1)

    soft_frame(
        "VERGLEICH",
        [
            f"{'':<12}  {'Weg A · Python':<20}  {'Weg B · Agent':<20}",
            f"{'-'*76}",
            f"{'Ergebnis':<12}  {str(a['result']):<20}  {str(b['result']):<20}",
            f"{'Latenz':<12}  "
            f"{f'{a['latency_ns'] / 1000:.2f} µs':<20}  "
            f"{f'{b['latency_s']:.2f} s':<20}",
            f"{'Tokens':<12}  {str(a['tokens']):<20}  "
            f"{str(b['tokens']):<20}",
            f"{'Determin.':<12}  "
            f"{'✓ garantiert':<20}  "
            f"{'✗ nur wahrscheinlich':<20}",
            f"{'Auditbar':<12}  "
            f"{'✓ 12 Zeichen Code':<20}  "
            f"{'teilweise (log/trace)':<20}",
            "",
            f"Weg B ist ~{ratio_latency:>10,.0f}× langsamer als Weg A.",
            f"Korrektheit:  {correctness}",
        ],
    )

    # ---- der Punkt ----
    soft_frame(
        "DER ZWEI-FRAGEN-TEST",
        [
            "Vor jedem Agent-Projekt, ehrlich prüfen:",
            "",
            "  1. Braucht diese Aufgabe URTEILSVERMÖGEN zur Laufzeit?",
            "     — Für sum(): nein.",
            "     — Für 'welche Rechnung ist verdächtig?': ja.",
            "",
            "  2. Kannst du eine falsche Antwort in 20 tolerieren?",
            "     — Für sum(): nein (arithmetischer Fehler ist ein Defekt).",
            "     — Für 'Vorschlag für die nächste Woche': ja.",
            "",
            "Beide Fragen mit JA?  Agent ist ein Kandidat.",
            "Auch nur eine mit NEIN?  Schreib eine Funktion.",
        ],
    )

    print()
    print("→ Der Agent hat funktioniert.  Und war rund eine Million Mal")
    print("  langsamer.  Und hat Geld gekostet.  Und hätte falsch sein können.")
    print("→ 'Agent' ist ein Werkzeug — kein Standard-Layer.")


if __name__ == "__main__":
    main()