"""
Step B · structured_output  —  ask for JSON, react to it
========================================================

Chapter: 2 · mini_agent (2/6)
Runtime: < 5 seconds

Step A printed whatever the model said.  We cannot build on that:
"whatever the model said" is not something a program can branch on.

So we make one small change: the system prompt now *requires* a JSON
object with an `intent` field.  Our code parses it and reacts:

  - intent == "chitchat"  →  print the model's reply text
  - intent == "calculate" →  we don't handle it yet — polite refusal
  - anything else         →  polite refusal

No tools are called on this page.  We are only teaching ourselves the
handshake: *the model produces structured output, our code decides
what to do with it.*

Run:
    python "02_ToolsAndPlanning/src/mini_agent/step_b_structured_output.py"
    python "02_ToolsAndPlanning/src/mini_agent/step_b_structured_output.py" "Hi, how are you?"
    python "02_ToolsAndPlanning/src/mini_agent/step_b_structured_output.py" "What is 12 times 7?"
"""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS = _HERE.parent.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat, extract_json  # noqa: E402


SYSTEM = """You are a routing assistant. Read the user's message and
respond with ONE JSON object, and nothing else, in this exact shape:

  { "intent": "chitchat",  "reply":  "<a short friendly answer>" }
  { "intent": "calculate", "reason": "<one short sentence>" }
  { "intent": "unknown",   "reason": "<one short sentence>" }

Rules:
- "chitchat"   → greetings, small talk, general questions you can
                  answer from your own knowledge.
- "calculate"  → the user is asking for an arithmetic computation
                  (multiply, add, subtract, divide).
- "unknown"    → anything else.

Output the JSON only. No prose before or after."""

DEFAULT_USER = "Hi there — what can you do?"


def main() -> None:
    user = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USER

    print(f"USER  →  {user}")
    print()

    r = chat(system=SYSTEM, user=user, want_json=True)

    print("┌── RAW MODEL OUTPUT ─────────────────────────")
    print(r.text.strip())
    print("└─────────────────────────────────────────────")

    try:
        msg = extract_json(r.text)
    except Exception as e:
        print()
        print(f"[error] could not parse JSON: {e}")
        print("Sorry, I could not understand the model's response.")
        return

    print()
    print("┌── PARSED ───────────────────────────────────")
    print(json.dumps(msg, indent=2, ensure_ascii=False))
    print("└─────────────────────────────────────────────")
    print()

    intent = msg.get("intent")

    if intent == "chitchat":
        reply = msg.get("reply", "").strip()
        print(f"ASSISTANT  →  {reply or '(empty reply)'}")

    elif intent == "calculate":
        print("ASSISTANT  →  I recognised a calculation, but I don't "
              "have a calculator wired up yet.")
        print(f"              (model's reason: {msg.get('reason', '?')})")
        print("              Sorry, cannot help — see step C.")

    else:
        print("ASSISTANT  →  Sorry, I can't help with that request.")
        print(f"              (reason: {msg.get('reason', '?')})")

    print()
    print(f"tokens: in={r.tokens_in}  out={r.tokens_out}")
    print()
    print("→ The model made a decision. Our code read it and branched.")
    print("→ Step C: replace the 'sorry' branch with a real tool call.")


if __name__ == "__main__":
    main()