"""
Step F · fallback_and_errors  —  the honest version
====================================================

Chapter: 2 · mini_agent (6/6)
Runtime: < 15 seconds

Steps A–E assumed the model behaves and the tools don't crash.  Neither
assumption holds in reality:

  - the model may emit malformed JSON, or valid JSON with wrong fields
  - the model may reference a tool that isn't in our registry
  - the tool call itself may raise (bad arg, divide by zero, ...)

This step adds a *minimum* amount of defensive code — one retry with a
corrective prompt for parse failures, and a clean refusal for everything
else.  Deliberately much smaller than `../../../03_TheLoop/src/03_retry_strategies.py`,
which covers a richer retry policy.  The point here is: even a single
retry closes the majority of the "why doesn't it work" gap.

After step F, compare with `../../../03_TheLoop/src/01_basic_loop.py`.
The diff is one `while` and a history list — that is the whole distance
from "single-shot dispatcher" to "agent loop".

Run:
    python "02_ToolsAndPlanning/src/mini_agent/step_f_fallback_and_errors.py"
    python "02_ToolsAndPlanning/src/mini_agent/step_f_fallback_and_errors.py" "What is 10 divided by 0?"
    python "02_ToolsAndPlanning/src/mini_agent/step_f_fallback_and_errors.py" "Tell me a joke"
    python "02_ToolsAndPlanning/src/mini_agent/step_f_fallback_and_errors.py" "Fetch the SAP homepage"
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


# ---------------- tools (same as step E) ----------------------------

def calculator(operation: str, a: float, b: float) -> float:
    ops = {
        "multiply": lambda x, y: x * y,
        "add":      lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "divide":   lambda x, y: x / y,
    }
    if operation not in ops:
        raise ValueError(f"unknown operation: {operation!r}")
    if operation == "divide" and b == 0:
        raise ZeroDivisionError("cannot divide by zero")
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


TOOLS: list[dict[str, Any]] = [
    {
        "name": "calculator",
        "description": "Perform basic arithmetic on two numbers.",
        "parameters": {
            "operation": 'one of "multiply", "add", "subtract", "divide"',
            "a": "number", "b": "number",
        },
        "example_args": {"operation": "multiply", "a": 12, "b": 7},
        "fn": calculator,
    },
    {
        "name": "unit_convert",
        "description": "Convert a length value between two units.",
        "parameters": {
            "value": "number",
            "source": 'one of "mile", "km", "m", "ft", "in", "cm"',
            "target": 'one of "mile", "km", "m", "ft", "in", "cm"',
        },
        "example_args": {"value": 3, "source": "mile", "target": "km"},
        "fn": unit_convert,
    },
]


def build_system_prompt(tools: list[dict[str, Any]]) -> str:
    blocks = []
    for t in tools:
        params = "\n      ".join(f"{k}: {v}" for k, v in t["parameters"].items())
        example = json.dumps(
            {"intent": "use_tool", "tool": t["name"], "args": t["example_args"]},
            ensure_ascii=False,
        )
        blocks.append(
            f'- {t["name"]}\n'
            f'    description: {t["description"]}\n'
            f'    parameters:\n      {params}\n'
            f'    example: {example}'
        )
    return (
        "You are a helpful assistant with the following tools:\n\n"
        + "\n\n".join(blocks)
        + "\n\nReply with ONE JSON object, and nothing else, matching one of:\n\n"
          '  { "intent": "use_tool", "tool": "<name>", "args": { ... } }\n'
          '  { "intent": "chitchat", "reply":  "<short answer>" }\n'
          '  { "intent": "unknown",  "reason": "<one sentence>" }\n\n'
        "Pick the tool that best fits the request. If no tool fits and no "
        "small-talk reply is appropriate, use \"unknown\". Output JSON only."
    )


def dispatch(name: str, args: dict, tools: list[dict[str, Any]]) -> Any:
    for t in tools:
        if t["name"] == name:
            fn: Callable = t["fn"]
            return fn(**args)
    raise LookupError(f"no such tool: {name!r}")


# ---------------- the defensive bits --------------------------------

def parse_or_retry(system: str, user: str) -> tuple[dict[str, Any] | None,
                                                    int, int]:
    """Try to obtain a valid JSON object from the model.
    Give it ONE second chance if the first response is unparseable.
    Return (parsed, tokens_in, tokens_out). `parsed` is None on give-up.
    """
    r1 = chat(system=system, user=user, want_json=True)
    tokens_in, tokens_out = r1.tokens_in, r1.tokens_out
    print("┌── ATTEMPT 1  (raw) ─────────────────────────")
    print(r1.text.strip())
    print("└─────────────────────────────────────────────")

    try:
        return extract_json(r1.text), tokens_in, tokens_out
    except Exception as e1:
        print(f"[warn] first attempt unparseable: {e1}")

    nudge = (
        f"{user}\n\n"
        "(SYSTEM NOTE: your previous reply was not valid JSON. "
        "Reply with a single JSON object matching the schema above, "
        "and nothing else.)"
    )
    r2 = chat(system=system, user=nudge, want_json=True)
    tokens_in += r2.tokens_in
    tokens_out += r2.tokens_out
    print()
    print("┌── ATTEMPT 2  (raw, after nudge) ────────────")
    print(r2.text.strip())
    print("└─────────────────────────────────────────────")

    try:
        return extract_json(r2.text), tokens_in, tokens_out
    except Exception as e2:
        print(f"[warn] second attempt also unparseable: {e2}")
        return None, tokens_in, tokens_out


def refuse(reason: str) -> None:
    print(f"ASSISTANT  →  Sorry, I can't help with that. ({reason})")


# ---------------- one-shot execution --------------------------------

DEFAULT_USER = "How many kilometres are 3 miles?"


def run_once(user: str) -> None:
    system = build_system_prompt(TOOLS)
    print(f"USER  →  {user}")
    print()

    msg, tokens_in, tokens_out = parse_or_retry(system, user)
    if msg is None:
        refuse("I could not produce a valid response after one retry.")
        print(f"\ntokens: in={tokens_in}  out={tokens_out}")
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
        except LookupError as e:
            refuse(f"unknown tool: {e}")
            print(f"\ntokens: in={tokens_in}  out={tokens_out}")
            return
        except TypeError as e:
            refuse(f"tool arguments did not fit: {e}")
            print(f"\ntokens: in={tokens_in}  out={tokens_out}")
            return
        except Exception as e:
            refuse(f"{type(e).__name__}: {e}")
            print(f"\ntokens: in={tokens_in}  out={tokens_out}")
            return
        print(f"TOOL RUN   →  {tool_name}({args})  =  {result}")
        print(f"ASSISTANT  →  The result is {result}.")

    elif intent == "chitchat":
        print(f"ASSISTANT  →  {msg.get('reply', '(empty)')}")

    else:
        refuse(msg.get("reason") or "no matching tool")

    print()
    print(f"tokens: in={tokens_in}  out={tokens_out}")


def main() -> None:
    user = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USER
    run_once(user)
    print()
    print("→ Malformed JSON     ⇒  one nudge, then refuse.")
    print("→ Unknown tool       ⇒  refuse.")
    print("→ Tool raised        ⇒  refuse with reason.")
    print()
    print("Compare this file with ../../../03_TheLoop/src/01_basic_loop.py — the")
    print("missing piece is *keeping the conversation going* after a tool result.")
    print("That one `while` is the whole distance to a real agent loop.")


if __name__ == "__main__":
    main()