"""
Step A · single_call  —  the smallest possible "agent"
======================================================

Chapter: 2 · Werkzeuge und der erste Plan · Bonus-Serie mini_agent (1/6)
Runtime: < 5 seconds
Cost   : a few hundred tokens

Before we talk about tools, JSON, or dispatch, let's be honest about
what a language-model call actually is:

    system_prompt + user_prompt  →  LLM  →  text

That is Principle 1 (text in, text out) in six lines.  Nothing on this
page is an "agent" yet — but every agent starts here.  The five
following steps will slowly turn this into one, without ever hiding
what happens on this page.

What to notice
--------------
- The system prompt gives the model a *role* and nothing else.
- We do not ask for JSON, we do not parse anything, we just print.
- The script exits after one HTTP round trip.

Run:
    python "02_ToolsAndPlanning/src/mini_agent/step_a_single_call.py"
    python "02_ToolsAndPlanning/src/mini_agent/step_a_single_call.py" "What is the capital of Portugal?"
"""

import sys
from pathlib import Path

# Repo-Root in sys.path, damit `common.llm` gefunden wird.
_HERE = Path(__file__).resolve()
_AS = _HERE.parent.parent.parent.parent  # mini_agent/ → src/ → 02_Tools…/ → Agentic Systems/
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat  # noqa: E402


SYSTEM = (
    "You are a concise, helpful assistant. "
    "Answer in one or two short sentences."
)

DEFAULT_USER = "In one sentence: what is an AI agent?"


def main() -> None:
    user = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USER

    print("┌── SYSTEM PROMPT ────────────────────────────")
    print(f"│  {SYSTEM}")
    print("└─────────────────────────────────────────────")
    print("┌── USER PROMPT ──────────────────────────────")
    print(f"│  {user}")
    print("└─────────────────────────────────────────────")

    r = chat(system=SYSTEM, user=user)

    print()
    print("┌── MODEL ANSWER ─────────────────────────────")
    for line in r.text.strip().splitlines() or [""]:
        print(f"│  {line}")
    print("└─────────────────────────────────────────────")
    print()
    print(f"tokens: in={r.tokens_in}  out={r.tokens_out}  "
          f"backend={r.backend}  model={r.model}")
    print()
    print("→ One call. One string back. No agency yet.")
    print("→ Step B: ask the model to answer in a structured way, so")
    print("  our code can react to it.")


if __name__ == "__main__":
    main()