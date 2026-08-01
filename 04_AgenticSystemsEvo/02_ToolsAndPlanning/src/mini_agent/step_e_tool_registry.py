"""
Step E · tool_registry  —  data, not code
=========================================

Chapter: 2 · mini_agent (5/6)
Runtime: < 10 seconds

Step D worked, but two things nag:

  1. The tool descriptions live in the system prompt as prose.
  2. The dispatcher is if/elif — adding a third tool would touch three
     places (function definition, prompt, dispatch).

We fix both by making tools *data*.  Each tool is a dictionary:

    { "name": "calculator",
      "description": "Pure arithmetic on two numbers.",
      "parameters": { ... JSON-schema-ish ... },
      "fn":          <the Python callable> }

The system prompt is *generated* from this list.  Dispatch is one
lookup.  Adding a tool means appending one entry — no other file
touched.  This is the same shape OpenAI's function-calling API and
MCP use, only written by hand so nothing is hidden.

Run:
    python "02_ToolsAndPlanning/src/mini_agent/step_e_tool_registry.py"
    python "02_ToolsAndPlanning/src/mini_agent/step_e_tool_registry.py" "What is 43177 times 14694?"
    python "02_ToolsAndPlanning/src/mini_agent/step_e_tool_registry.py" "How many kilometres are 3 miles?"
"""

import json
import sys
from pathlib import Path
from typing import Any, Callable

_HERE = Path(__file__).resolve()
_AS = _HERE.parent.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat, extract_json  # noqa: E402


# ---------------- the tools themselves ------------------------------

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


# ---------------- the registry --------------------------------------
#
# Each entry is pure data plus one callable.  To add a tool, append
# one dict.  Nothing else in this file needs to change.

TOOLS: list[dict[str, Any]] = [
    {
        "name": "calculator",
        "description": "Perform basic arithmetic on two numbers.",
        "parameters": {
            "operation": 'one of "multiply", "add", "subtract", "divide"',
            "a": "number",
            "b": "number",
        },
        "example_args": {"operation": "multiply", "a": 12, "b": 7},
        "fn": calculator,
    },
    {
        "name": "unit_convert",
        "description": "Convert a length value between two units.",
        "parameters": {
            "value": "number",
            "source": 'unit: one of "mile", "km", "m", "ft", "in", "cm"',
            "target": 'unit: one of "mile", "km", "m", "ft", "in", "cm"',
        },
        "example_args": {"value": 3, "source": "mile", "target": "km"},
        "fn": unit_convert,
    },
]


# ---------------- prompt is generated from the registry -------------

def build_system_prompt(tools: list[dict[str, Any]]) -> str:
    tool_blocks = []
    for t in tools:
        params = "\n      ".join(f"{k}: {v}" for k, v in t["parameters"].items())
        example = json.dumps(
            {"intent": "use_tool", "tool": t["name"], "args": t["example_args"]},
            ensure_ascii=False,
        )
        tool_blocks.append(
            f'- {t["name"]}\n'
            f'    description: {t["description"]}\n'
            f'    parameters:\n      {params}\n'
            f'    example: {example}'
        )
    tools_text = "\n\n".join(tool_blocks)

    return (
        "You are a helpful assistant with the following tools:\n\n"
        f"{tools_text}\n\n"
        "Reply with ONE JSON object, and nothing else, matching one of:\n\n"
        '  { "intent": "use_tool", "tool": "<name>", "args": { ... } }\n'
        '  { "intent": "chitchat", "reply":  "<short answer>" }\n'
        '  { "intent": "unknown",  "reason": "<one sentence>" }\n\n'
        "Pick the tool that best fits the user's request. If no tool "
        "fits and no small-talk reply is appropriate, use \"unknown\". "
        "Output the JSON only."
    )


# ---------------- dispatch: one lookup, no if/elif ------------------

def dispatch(name: str, args: dict, tools: list[dict[str, Any]]) -> Any:
    for t in tools:
        if t["name"] == name:
            fn: Callable = t["fn"]
            return fn(**args)
    raise ValueError(f"no such tool: {name!r}")


# ---------------- one-shot execution --------------------------------

DEFAULT_USER = "How many kilometres are 3 miles?"


def run_once(user: str) -> None:
    system = build_system_prompt(TOOLS)

    print(f"USER  →  {user}")
    print()
    print("┌── GENERATED SYSTEM PROMPT ─────────────────")
    for line in system.splitlines():
        print(f"│  {line}")
    print("└─────────────────────────────────────────────")
    print()

    r = chat(system=system, user=user, want_json=True)

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
        tool_name = msg.get("tool", "")
        args = msg.get("args", {})
        try:
            result = dispatch(tool_name, args, TOOLS)
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
    print(f"→ Registered tools: {[t['name'] for t in TOOLS]}")
    print("→ Add a new tool  =  append one dict.  No prompt edits.")
    print("→ Step F: what if the JSON is broken, or the tool crashes?")


if __name__ == "__main__":
    main()