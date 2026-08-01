"""
Step G · agent_server  —  put the mini agent behind an A2A endpoint
===================================================================

Chapter: 5 · Protokolle und Skalierung · a2a live-server (1/2)

We take the mini agent from Kapitel 2 (`02_ToolsAndPlanning/src/mini_agent/
step_f_fallback_and_errors.py`) and expose it over HTTP using the A2A
(Agent2Agent) protocol.

What A2A minimally is
---------------------
1. A static **agent card** served from `/.well-known/agent-card.json`.
   Any client can fetch this to discover what the agent does.
2. A **JSON-RPC 2.0** endpoint (we mount it at `/`) with two methods
   implemented here:
       message/send    — send a user message, get a task back
       tasks/get       — poll a task's status/result

Streaming (`message/stream`, SSE) and task cancellation are part of
the spec but not needed for this one-shot agent — we mark them as
`false` in the card and return a proper JSON-RPC error if called.

What is NEW compared to the mini_agent step F
---------------------------------------------
- FastAPI wiring.  About 40 lines.
- The agent brain itself is UNCHANGED: we import the same functions
  from step_f_fallback_and_errors.  All new code is transport, not
  intelligence.  That distinction is the whole point of this section.

Prerequisites:
    pip install fastapi uvicorn

Run:
    python "05_ProtocolsAndScale/src/a2a/step_g_agent_server.py"
    # → http://localhost:8000
    # → open http://localhost:8000/.well-known/agent-card.json in a browser
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Any

# Repo-Root und der mini_agent-Ordner müssen im sys.path stehen, damit
# wir das Agent-Brain aus Kap. 2 wiederverwenden können.
_HERE = Path(__file__).resolve()
_AS = _HERE.parent.parent.parent.parent  # a2a/ → src/ → 05_…/ → Agentic Systems/
_MINI = _AS / "02_ToolsAndPlanning" / "src" / "mini_agent"
for p in (_AS, _MINI):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from step_f_fallback_and_errors import (  # noqa: E402
    TOOLS,
    build_system_prompt,
    dispatch,
    parse_or_retry,
)

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError as e:
    raise SystemExit(
        "Missing dependency. Install with:  pip install fastapi uvicorn\n"
        f"(underlying error: {e})"
    )


# ---------------- the agent brain, wrapped as a function ------------
# Same logic as step F's run_once, but returns text instead of printing.

def run_agent(user_text: str) -> str:
    system = build_system_prompt(TOOLS)
    msg, _, _ = parse_or_retry(system, user_text)
    if msg is None:
        return "Sorry, I could not produce a valid response."

    intent = msg.get("intent")
    if intent == "use_tool":
        tool_name = msg.get("tool", "")
        args = msg.get("args", {})
        try:
            result = dispatch(tool_name, args, TOOLS)
        except Exception as e:
            return f"Sorry, I couldn't run that tool. ({type(e).__name__}: {e})"
        return f"The result of {tool_name}({args}) is {result}."
    if intent == "chitchat":
        return msg.get("reply", "").strip() or "(empty reply)"
    return f"Sorry, I can't help with that. ({msg.get('reason', 'no matching tool')})"


# ---------------- the A2A agent card --------------------------------

HOST = "localhost"
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}"

AGENT_CARD: dict[str, Any] = {
    "name": "mini-agent",
    "description": (
        "A minimal calculator + unit-conversion agent from Kap. 2's "
        "mini_agent step F, exposed via A2A for Kap. 5 to demonstrate "
        "the wire protocol."
    ),
    "url": BASE_URL,
    "version": "0.1.0",
    "protocolVersion": "0.2",
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": False,
    },
    "skills": [
        {
            "id": "calculate",
            "name": "arithmetic",
            "description": "Multiply, add, subtract, divide two numbers.",
            "tags": ["math", "calculator"],
            "examples": [
                "What is 43177 times 14694?",
                "Divide 100 by 7.",
            ],
        },
        {
            "id": "convert",
            "name": "length unit conversion",
            "description": "Convert a length between mile, km, m, ft, in, cm.",
            "tags": ["units", "conversion"],
            "examples": [
                "How many kilometres are 3 miles?",
                "Convert 180 cm to inches.",
            ],
        },
    ],
}


# ---------------- in-memory task store ------------------------------
#
# A2A models every interaction as a Task.  Even though our agent is
# synchronous, we still store the task so `tasks/get` works — that
# lets clients (and the Inspector) verify the status transitions.

TASKS: dict[str, dict[str, Any]] = {}


def _extract_user_text(message: dict[str, Any]) -> str:
    """Pull the first text part out of an A2A message object."""
    parts = message.get("parts") or []
    for p in parts:
        if p.get("kind") == "text" or "text" in p:
            return p.get("text", "")
    return ""


def _make_task(user_text: str, agent_text: str) -> dict[str, Any]:
    task_id = uuid.uuid4().hex
    return {
        "id": task_id,
        "kind": "task",
        "status": {"state": "completed"},
        "history": [
            {"role": "user",  "parts": [{"kind": "text", "text": user_text}]},
            {"role": "agent", "parts": [{"kind": "text", "text": agent_text}]},
        ],
    }


# ---------------- JSON-RPC helpers ----------------------------------

def _rpc_result(req_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _rpc_error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


# ---------------- FastAPI app ---------------------------------------

app = FastAPI(title="mini-agent A2A server")


@app.get("/.well-known/agent-card.json")
def agent_card() -> dict[str, Any]:
    return AGENT_CARD


@app.post("/")
async def jsonrpc(request: Request) -> JSONResponse:
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(_rpc_error(None, -32700, "Parse error"), status_code=400)

    req_id = body.get("id")
    method = body.get("method")
    params = body.get("params") or {}

    print(f"[rpc] ← {method}  id={req_id}")

    if method == "message/send":
        message = params.get("message") or {}
        user_text = _extract_user_text(message)
        if not user_text:
            return JSONResponse(_rpc_error(req_id, -32602, "empty message"))
        try:
            agent_text = run_agent(user_text)
        except Exception as e:
            agent_text = f"Sorry — internal error: {type(e).__name__}: {e}"
        task = _make_task(user_text, agent_text)
        TASKS[task["id"]] = task
        print(f"[rpc] → completed task {task['id'][:8]}…  ({agent_text[:60]!r})")
        return JSONResponse(_rpc_result(req_id, task))

    if method == "tasks/get":
        task_id = params.get("id") or params.get("taskId")
        task = TASKS.get(task_id)
        if not task:
            return JSONResponse(_rpc_error(req_id, -32001, f"unknown task: {task_id}"))
        return JSONResponse(_rpc_result(req_id, task))

    if method in ("message/stream", "tasks/cancel", "tasks/pushNotificationConfig/set"):
        return JSONResponse(_rpc_error(req_id, -32601, f"method not implemented: {method}"))

    return JSONResponse(_rpc_error(req_id, -32601, f"unknown method: {method}"))


# ---------------- entry point ---------------------------------------

def main() -> None:
    print("┌── mini-agent A2A server ─────────────────────")
    print(f"│  agent card : {BASE_URL}/.well-known/agent-card.json")
    print(f"│  JSON-RPC   : POST {BASE_URL}/")
    print("│  methods    : message/send, tasks/get")
    print("│  brain      : 02_ToolsAndPlanning/src/mini_agent/step_f  (unchanged)")
    print("└──────────────────────────────────────────────")
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()