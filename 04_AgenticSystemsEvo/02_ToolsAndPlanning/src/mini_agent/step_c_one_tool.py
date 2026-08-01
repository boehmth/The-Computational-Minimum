"""
Step C · one_tool  —  first real tool call
==========================================

Chapter: 2 · mini_agent (3/6)
Runtime: < 10 seconds

This is the step described in the task brief:

  1. take the user prompt, combine with the system prompt, send to LLM
  2. parse the JSON reply, and depending on intent either
       - execute a tool (calculator), or
       - print "sorry, cannot help".

No loop. One LLM call, one decision, one tool execution, exit.  A
one-shot dispatcher — but the model *chooses* what to do.  That is
Principle 2 in the smallest honest form.

Compare with `../01_give_it_a_tool.py` in this same chapter: same idea,
different framing. That file leads with the wow-moment (mental math
vs. tool). This file leads with the mechanics (dispatcher pattern).

Run:
    python "02_ToolsAndPlanning/src/mini_agent/step_c_one_tool.py"
    python "02_ToolsAndPlanning/src/mini_agent/step_c_one_tool.py" "What is 43177 times 14694?"
    python "02_ToolsAndPlanning/src/mini_agent/step_c_one_tool.py" "Hi there"
    python "02_ToolsAndPlanning/src/mini_agent/step_c_one_tool.py" "Write me a haiku about databases"
"""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS = _HERE.parent.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat, extract_json  # noqa: E402


SYSTEM = """You are a helpful assistant with ONE tool available:

  calculator(operation, a, b)
      operation ∈ { "multiply", "add", "subtract", "divide" }
      a, b are numbers

Reply with ONE JSON object, and nothing else, matching one of these:

  { "intent": "calculate",
    "tool":   "calculator",
    "args":   { "operation": "multiply", "a": 12, "b": 7 } }

  { "intent": "chitchat",
    "reply":  "<a short friendly answer>" }

  { "intent": "unknown",
    "reason": "<one short sentence>" }

Rules:
- Use "calculate" ONLY when the user asks for arithmetic that the
  calculator can perform.
- Use "chitchat" for greetings, small talk, or general knowledge
  questions you can answer directly.
- Use "unknown" for anything else.

Output the JSON only. No prose."""

DEFAULT_USER = "What is 43,177 times 14,694?"


# ------------------ the tool (deterministic Python) ------------------

def calculator(operation: str, a: float, b: float) -> float:
    ops = {
        "multiply": lambda x, y: x * y,
        "add":      lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "divide":   lambda x, y: x / y,
    }
    if operation not in ops:
        raise ValueError(f"unknown operation: {operation!r}")
    return ops[operation](a, b)


# ------------------ the one-shot dispatcher (P3, no loop yet) --------

def run_once(user: str) -> None:
    print(f"USER  →  {user}")
    print()

    r = chat(system=SYSTEM, user=user, want_json=True)

    print("┌── MODEL OUTPUT (raw) ───────────────────────")
    print(r.text.strip())
    print("└─────────────────────────────────────────────")

    try:
        msg = extract_json(r.text)
    except Exception as e:
        print()
        print(f"[error] could not parse JSON: {e}")
        print("ASSISTANT  →  Sorry, I can't help with that.")
        return

    print()
    print("┌── PARSED ───────────────────────────────────")
    print(json.dumps(msg, indent=2, ensure_ascii=False))
    print("└─────────────────────────────────────────────")
    print()

    intent = msg.get("intent")

    if intent == "calculate" and msg.get("tool") == "calculator":
        args = msg.get("args", {})
        try:
            result = calculator(**args)
        except Exception as e:
            print(f"[tool error] {e}")
            print("ASSISTANT  →  Sorry, I couldn't run the calculation.")
            return
        print(f"TOOL RUN   →  calculator({args})  =  {result}")
        print(f"ASSISTANT  →  The result is {result}.")

    elif intent == "chitchat":
        reply = msg.get("reply", "").strip()
        print(f"ASSISTANT  →  {reply or '(empty reply)'}")

    else:
        reason = msg.get("reason") or "no supported tool for this request"
        print(f"ASSISTANT  →  Sorry, I can't help with that. ({reason})")

    print()
    print(f"tokens: in={r.tokens_in}  out={r.tokens_out}")


def main() -> None:
    user = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USER
    run_once(user)
    print()
    print("→ Model decided. Python executed. One call, one dispatch, done.")
    print("→ Step D: add a second tool so the model must actually *choose*.")


if __name__ == "__main__":
    main()