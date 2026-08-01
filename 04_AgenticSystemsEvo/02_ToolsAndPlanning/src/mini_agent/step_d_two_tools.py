"""
Step D · two_tools  —  the model must choose
============================================

Chapter: 2 · mini_agent (4/6)
Runtime: < 10 seconds

Step C had one tool.  With one tool, the model doesn't really "choose"
anything — it either uses the tool or it doesn't.  Two tools is the
smallest interesting case: the model must decide, in natural language,
which of them fits the request.

New tool: `unit_convert(value, source, target)` for length units
(miles, km, metres, feet, inches, cm).  Deterministic, no API.

The dispatcher is still hard-coded (`if tool == "calculator": ...
elif tool == "unit_convert": ...`).  That is fine at two tools; it
starts to hurt at five.  Step E replaces the if/elif with a registry.

What to notice
--------------
- The two prompts "12 times 7" and "3 miles in km" look similar to a
  keyword matcher but route to different tools.  The choice is made by
  the model from meaning, not by us from surface strings.
- Nothing else changes: still one LLM call, still one dispatch, still
  no loop.

Run:
    python "02_ToolsAndPlanning/src/mini_agent/step_d_two_tools.py"
    python "02_ToolsAndPlanning/src/mini_agent/step_d_two_tools.py" "What is 43177 times 14694?"
    python "02_ToolsAndPlanning/src/mini_agent/step_d_two_tools.py" "How many kilometres are 3 miles?"
    python "02_ToolsAndPlanning/src/mini_agent/step_d_two_tools.py" "Convert 180 cm to inches"
"""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS = _HERE.parent.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat, extract_json  # noqa: E402


SYSTEM = """You are a helpful assistant with TWO tools available:

  calculator(operation, a, b)
      operation ∈ { "multiply", "add", "subtract", "divide" }
      a, b are numbers.
      Use for pure arithmetic.

  unit_convert(value, source, target)
      value is a number.
      source, target ∈ { "mile", "km", "m", "ft", "in", "cm" }
      Use for converting a length between two units.

Reply with ONE JSON object, and nothing else, matching one of:

  { "intent": "use_tool",
    "tool":   "calculator",
    "args":   { "operation": "multiply", "a": 12, "b": 7 } }

  { "intent": "use_tool",
    "tool":   "unit_convert",
    "args":   { "value": 3, "source": "mile", "target": "km" } }

  { "intent": "chitchat",
    "reply":  "<a short friendly answer>" }

  { "intent": "unknown",
    "reason": "<one short sentence>" }

Choose the tool that best fits the user's request. If neither tool
fits and no small-talk reply is appropriate, use "unknown".
Output the JSON only."""

DEFAULT_USER = "How many kilometres are 3 miles?"


# ------------------ the two tools ------------------------------------

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


_METRE_FACTOR = {
    "m": 1.0, "km": 1000.0, "cm": 0.01,
    "mile": 1609.344, "ft": 0.3048, "in": 0.0254,
}


def unit_convert(value: float, source: str, target: str) -> float:
    if source not in _METRE_FACTOR:
        raise ValueError(f"unknown source unit: {source!r}")
    if target not in _METRE_FACTOR:
        raise ValueError(f"unknown target unit: {target!r}")
    return round(float(value) * _METRE_FACTOR[source] / _METRE_FACTOR[target], 6)


# ------------------ hard-coded router (step E will improve this) -----

def dispatch(tool_name: str, args: dict):
    if tool_name == "calculator":
        return calculator(**args)
    if tool_name == "unit_convert":
        return unit_convert(**args)
    raise ValueError(f"no such tool: {tool_name!r}")


# ------------------ one-shot execution -------------------------------

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

    if intent == "use_tool":
        tool_name = msg.get("tool")
        args = msg.get("args", {})
        try:
            result = dispatch(tool_name, args)
        except Exception as e:
            print(f"[tool error] {e}")
            print("ASSISTANT  →  Sorry, I couldn't run that.")
            return
        print(f"TOOL RUN   →  {tool_name}({args})  =  {result}")
        print(f"ASSISTANT  →  The result is {result}.")

    elif intent == "chitchat":
        print(f"ASSISTANT  →  {msg.get('reply', '(empty)')}")

    else:
        reason = msg.get("reason") or "no matching tool"
        print(f"ASSISTANT  →  Sorry, I can't help with that. ({reason})")

    print()
    print(f"tokens: in={r.tokens_in}  out={r.tokens_out}")


def main() -> None:
    user = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USER
    run_once(user)
    print()
    print("→ Two tools, one dispatcher, no loop. The model chose.")
    print("→ Step E: make the tool list a registry, generate the prompt.")


if __name__ == "__main__":
    main()