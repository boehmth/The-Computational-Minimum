"""
01 · basic_loop  —  Kapitel 3, Miniatur 1

Slide-Anker :  P3 · The loop is yours to write
Laufzeit    :  ~20-40 Sekunden
Kosten      :  ~1500-4000 Tokens

Der eigentliche Agent — nackt.  ~60 Zeilen Python.  Keine Bibliothek.

Der Loop:
    while not done:
        model = call LLM with the whole history
        parse the JSON
        if it's {"final": ...}    ->  stop
        if it's {"tool": ...}     ->  run the tool, feed result back
        also: turn > MAX_TURNS    ->  break (safety net)
        also: same call repeats   ->  break (loop guard)

Alle drei Stop-Bedingungen sind explizit im Code.  Genau das ist
Prinzip 3 in Aktion.

Ausführen:
    python "Agentic Systems/03_TheLoop/src/01_basic_loop.py"
"""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS   = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat, extract_json
from common.ui  import hard_card, soft_frame, phase_break, wrap


SYSTEM = """Du bist ein Einkaufsassistent. Du hast zwei Werkzeuge:

  calculator(operation, a, b)              # multiply|add|subtract|divide
  currency_converter(amount, source, target)   # source, target ∈ {EUR, USD}

Bei jedem Turn: gib GENAU EIN JSON-Objekt aus, sonst nichts:

  {"tool": "<name>", "args": { ... }}    # Werkzeug rufen
    oder
  {"final": "<Antwort an den User>"}     # fertig

Du siehst das Werkzeug-Ergebnis in der nächsten User-Nachricht und
entscheidest dann den nächsten Schritt.  Mache weiter bis du
{"final": ...} ausgibst."""


TASK = ("Ich habe ein Budget von 132877 US-Dollar für Gadgets, die "
        "je 5.30 EUR kosten. Wie viele kann ich davon kaufen?")

MAX_TURNS = 6


# ------------------ Werkzeuge (deterministisches Python) ------------------

FX = {("USD", "EUR"): 0.92, ("EUR", "USD"): 1 / 0.92}


def calculator(operation, a, b):
    return {"multiply": a * b, "add": a + b,
            "subtract": a - b, "divide": a / b}[operation]


def currency_converter(amount, source, target):
    if source == target:
        return amount
    return round(amount * FX[(source, target)], 2)


TOOLS = {"calculator": calculator,
         "currency_converter": currency_converter}


# ------------------ Der Loop (P3: von dir geschrieben) ------------------

def run_agent(task: str):
    history = [
        {"role": "system", "content": SYSTEM},
        {"role": "user",   "content": task},
    ]
    total_in = total_out = 0
    last_call = None
    same_call_count = 0

    for turn in range(1, MAX_TURNS + 1):
        prompt = "\n\n".join(f"{m['role'].upper()}: {m['content']}"
                             for m in history)
        r = chat(system=SYSTEM, user=prompt, want_json=True, max_tokens=1024)
        total_in  += r.tokens_in
        total_out += r.tokens_out

        try:
            msg = extract_json(r.text)
        except Exception as e:
            hard_card(f"▸  TURN {turn}  ·  MODELL-Output (nicht parsbar)",
                      f"{r.tokens_out} Tokens · parse-Fehler",
                      r.text)
            print(f"[abort] parse fehlgeschlagen: {e}")
            return None

        # STOP A: finale Antwort
        if "final" in msg:
            hard_card(
                title    = f"▸  TURN {turn}  ·  MODELL SAGT FERTIG",
                subtitle = f"{r.tokens_out} Tokens · Stop = final-Marker",
                body     = json.dumps(msg, indent=2, ensure_ascii=False),
            )
            return {"final": msg["final"], "turns": turn,
                    "tokens_in": total_in, "tokens_out": total_out}

        # sonst: Werkzeug-Aufruf
        tool_name = msg.get("tool")
        args      = msg.get("args", {})
        call_sig  = (tool_name, json.dumps(args, sort_keys=True))

        # STOP B: derselbe Call 3× in Folge -> Loop-Guard
        if call_sig == last_call:
            same_call_count += 1
            if same_call_count >= 3:
                print("[abort] derselbe Werkzeug-Aufruf 3× in Folge — "
                      "Loop-Guard hat zugeschlagen")
                return None
        else:
            same_call_count = 0
        last_call = call_sig

        hard_card(
            title    = f"▸  TURN {turn}  ·  MODELL WILL EIN WERKZEUG",
            subtitle = f"{r.tokens_out} Tokens · Runner wird das jetzt ausführen",
            body     = json.dumps(msg, indent=2, ensure_ascii=False),
        )

        try:
            result = TOOLS[tool_name](**args)
        except Exception as e:
            result = {"error": str(e)}
        print(f"    → ausgeführt:  {tool_name}({args})  =  {result}")

        history.append({"role": "assistant", "content": r.text})
        history.append({"role": "user",
                        "content": f"[observation] {tool_name} lieferte {result}"})

    # STOP C: Turn-Limit
    print(f"[abort] MAX_TURNS ({MAX_TURNS}) erreicht ohne finale Antwort")
    return None


def main():
    phase_break("basic_loop.py  ·  der von dir gebaute Loop")

    soft_frame("DIE AUFGABE", wrap(TASK))

    soft_frame(
        "DREI STOP-BEDINGUNGEN  (alle in diesem File — genau das ist P3)",
        [
            "A.  Modell schickt {\"final\": ...}      ← Erfolgspfad",
            "B.  Derselbe Werkzeug-Aufruf 3× wiederholt  ← Loop-Guard",
            "C.  Turn-Zähler erreicht MAX_TURNS=6    ← Sicherheitsnetz",
        ],
    )

    result = run_agent(TASK)

    if result:
        soft_frame(
            "ZUSAMMENFASSUNG",
            [
                f"finale Antwort  →  {result['final']}",
                f"Turns benutzt   →  {result['turns']}  "
                f"(je ein HTTP-Aufruf ans Modell)",
                f"Tokens gesamt   →  "
                f"{result['tokens_in'] + result['tokens_out']}  "
                f"({result['tokens_in']} in + {result['tokens_out']} out)",
            ],
        )
    else:
        soft_frame("ZUSAMMENFASSUNG",
                   ["Keine finale Antwort. Siehe [abort]-Zeile oben."])

    print()
    print("→ Jeder Turn ist ein HTTP-Aufruf ans LLM.")
    print("→ Parsen, Dispatch, Loop-Kontrolle: alles in DIESEM File.")
    print("→ Keine Bibliothek hat das geschrieben.  Du hast es geschrieben.")
    print("→ Das ist Prinzip 3.")


if __name__ == "__main__":
    main()