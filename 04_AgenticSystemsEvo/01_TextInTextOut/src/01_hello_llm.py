"""
01 · hello_llm  —  Kapitel 1, Miniatur 1

Slide-Anker :  P1 · Text-in / Text-out
Laufzeit    :  < 3 Sekunden
Kosten      :  < 100 Tokens

Das kleinste Programm des ganzen Repos.  Ein einziger Aufruf.
Eine einzige Antwort.  Ein Beweis, dass ein LLM aus API-Sicht genau
eine Operation kennt: Text konsumieren, Text produzieren.

Ausführen:
    python "Agentic Systems/01_TextInTextOut/src/01_hello_llm.py"
"""

import sys
from pathlib import Path

# Erlaube "from common.llm import chat" durch import-path-manipulation.
# Wir sind hier in .../Agentic Systems/01_TextInTextOut/src/01_hello_llm.py
# und wollen .../Agentic Systems/ in den sys.path.
_HERE = Path(__file__).resolve()
_AS   = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat


def main():
    r = chat(
        system="Antworte in einem einzigen kurzen Satz.",
        user="Was ist die Hauptstadt von Frankreich?",
    )

    print("┌─────────────────────────────────────────────")
    print(f"│  backend  = {r.backend}")
    print(f"│  model    = {r.model}")
    print(f"│  tokens   = in:{r.tokens_in}  out:{r.tokens_out}")
    print("├──── Antwort des Modells ────────────────────")
    print(r.text.strip())
    print("└─────────────────────────────────────────────")
    print()
    print("→ Text hinein.  Text heraus.  Nichts anderes.")
    print("→ Alles was folgt, ist Code, der genau diese eine")
    print("  Operation geschickt orchestriert.")


if __name__ == "__main__":
    main()