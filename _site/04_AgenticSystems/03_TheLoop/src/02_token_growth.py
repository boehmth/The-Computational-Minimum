"""
02 · token_growth  —  Kapitel 3, Miniatur 2

Slide-Anker :  P3 · Der Loop kostet mehr als er auf den ersten Blick tut
Laufzeit    :  ~30-60 Sekunden
Kosten      :  ~3000-8000 Tokens

Derselbe Loop wie 01_basic_loop.py — aber:
  - eine Aufgabe, die 3-4 Werkzeug-Aufrufe braucht,
  - nach jedem Turn eine Zeile mit den Turn-Kosten,
  - am Ende ein Vergleich "kumulativ vs. ein hypothetischer einzelner Call".

Der Punkt: `tokens_in` wächst mit jedem Turn, weil die ganze bisherige
Konversation neu mitgeschickt wird.  Das Gedächtnis des Modells ist
der Prompt — und der wird länger.

Ausführen:
    python "Agentic Systems/03_TheLoop/src/02_token_growth.py"
"""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS   = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat, extract_json
from common.ui  import soft_frame, phase_break, wrap


SYSTEM = """Du bist ein Recherche-Assistent. Du hast drei Werkzeuge:

  fetch_stock(ticker)      # Preis und 30-Tage-Trend
  fetch_news(topic)        # Schlagzeilen der letzten 7 Tage
  summarise(texts)         # verdichtet auf einen Absatz

Bei jedem Turn: gib GENAU EIN JSON-Objekt aus:

  {"tool": "<name>", "args": { ... }}
    oder
  {"final": "<Antwort>"}

Nutze mindestens ZWEI Werkzeuge, bevor du {"final": ...} sagst."""


TASK = ("Gib mir ein einabsatziges Investment-Briefing zu SAP SE (Ticker SAP), "
        "das den aktuellen Preis/Trend und die Schlagzeilen der letzten Woche "
        "kombiniert.")

MAX_TURNS = 6


# ---- Werkzeuge (fest verdrahtete Antworten, um Kosten kalkulierbar zu halten) ----

def fake_tool(name, args):
    if name == "fetch_stock":
        return {"ticker": args.get("ticker", "SAP"),
                "price": 189.42, "trend_30d_pct": 3.7}
    if name == "fetch_news":
        topic = args.get("topic", "SAP SE")
        return {"headlines": [
            f"Analysten bullisch auf {topic}",
            f"Regulator eröffnet Prüfung zu {topic}",
            f"{topic} kündigt neue Produktlinie an",
        ]}
    if name == "summarise":
        return {"summary": ("Positiver Kurzfrist-Ausblick, geschmälert durch "
                            "regulatorischen Gegenwind; 30-Tage-Sicht neutral.")}
    return {"error": f"unknown tool {name}"}


def main():
    phase_break("token_growth.py  ·  was der Loop wirklich kostet")

    soft_frame("DIE AUFGABE", wrap(TASK))

    history = [
        {"role": "system", "content": SYSTEM},
        {"role": "user",   "content": TASK},
    ]
    stats = []
    cumulative = 0

    for turn in range(1, MAX_TURNS + 1):
        prompt = "\n\n".join(f"{m['role'].upper()}: {m['content']}"
                             for m in history)
        r = chat(system=SYSTEM, user=prompt, want_json=True, max_tokens=1024)
        cumulative += r.tokens
        stats.append((turn, r.tokens_in, r.tokens_out, cumulative))

        try:
            msg = extract_json(r.text)
        except Exception:
            print(f"[abort] Turn {turn} nicht parsbar; roh: {r.text[:200]}")
            return

        # Live-Zeile pro Turn
        print(f"  Turn {turn}:  in={r.tokens_in:>4}   out={r.tokens_out:>3}"
              f"   cumulative={cumulative:>5}   "
              f"({'final ✓' if 'final' in msg else 'tool: ' + str(msg.get('tool'))})")

        if "final" in msg:
            history.append({"role": "assistant", "content": r.text})
            break

        name = msg["tool"]
        args = msg.get("args", {})
        obs  = fake_tool(name, args)
        history.append({"role": "assistant", "content": r.text})
        history.append({"role": "user",
                        "content": f"[observation] {name}({args}) = {obs}"})

    # ------------- Wachstumstabelle -------------
    lines = [
        f"{'Turn':>4}  {'tokens_in':>10}  {'tokens_out':>10}"
        f"  {'cumulative':>10}",
        f"{'-'*4:>4}  {'-'*10:>10}  {'-'*10:>10}  {'-'*10:>10}",
    ]
    for t, ti, to, cum in stats:
        lines.append(f"{t:>4}  {ti:>10}  {to:>10}  {cum:>10}")
    soft_frame("TURN-BY-TURN TOKEN GROWTH", lines)

    if stats:
        first = stats[0][1] + stats[0][2]
        total = stats[-1][3]
        ratio = total / first if first else 0.0
        soft_frame(
            "WAS DAS BEDEUTET",
            [
                f"Turn 1 hat {first} Tokens gekostet (~1 hypothetischer",
                f"einzelner Call).",
                f"Der ganze Loop hat {total} Tokens gekostet.",
                f"Das ist das {ratio:.1f}-fache — für {len(stats)} Turns.",
                "",
                "Grund: bei Turn N wird die *gesamte* bisherige Konversation",
                "neu mitgeschickt.  Der Prompt wächst mit jedem Turn.",
                "Das Modell hat kein Gedächtnis — der Prompt IST das Gedächtnis.",
            ],
        )

    print()
    print("→ 10 Nutzer × 100 Tasks/Tag × N Turns = die Rechnung.")
    print("→ Deshalb: Turns cappen, Ergebnisse zwischen Turns zusammenfassen,")
    print("  billige Modelle für Routine, teure nur wenn nötig.")


if __name__ == "__main__":
    main()