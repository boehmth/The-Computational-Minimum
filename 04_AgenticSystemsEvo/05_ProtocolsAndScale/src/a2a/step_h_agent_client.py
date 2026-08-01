"""
Step H · agent_client  —  talk to the A2A server, byte by byte
==============================================================

Chapter: 5 · Protokolle und Skalierung · a2a live-server (2/2)

A hand-written client for the server from step G.  No SDK.  Every
request and response is printed so you can see the wire.

What it does
------------
1. GET  /.well-known/agent-card.json      → discover the agent
2. POST /  with a JSON-RPC message/send   → run one task
3. POST /  with a JSON-RPC tasks/get      → verify the same task
   can be re-fetched by id
4. Print the assistant's answer.

Same information the A2A Inspector shows in its browser UI — but here
we spell it out in ~60 lines so you can point at every field.

Prerequisites:
    pip install requests
    # and the server must already be running:
    python "05_ProtocolsAndScale/src/a2a/step_g_agent_server.py"  &

Run:
    python "05_ProtocolsAndScale/src/a2a/step_h_agent_client.py"
    python "05_ProtocolsAndScale/src/a2a/step_h_agent_client.py" "What is 43177 times 14694?"
"""
from __future__ import annotations

import json
import sys
import uuid
from typing import Any

try:
    import requests
except ImportError:
    raise SystemExit("Install with: pip install requests")


SERVER = "http://localhost:8000"


def dump(label: str, obj: Any) -> None:
    print(f"── {label} " + "─" * (60 - len(label)))
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def fetch_card() -> dict[str, Any]:
    print(f"\nGET  {SERVER}/.well-known/agent-card.json")
    r = requests.get(f"{SERVER}/.well-known/agent-card.json", timeout=10)
    r.raise_for_status()
    card = r.json()
    dump("AGENT CARD", card)
    return card


def send_message(text: str) -> dict[str, Any]:
    """Send a user message via JSON-RPC message/send. Returns the Task."""
    req = {
        "jsonrpc": "2.0",
        "id": uuid.uuid4().hex[:8],
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
            }
        },
    }
    print(f"\nPOST {SERVER}/    (message/send)")
    dump("REQUEST", req)
    r = requests.post(SERVER + "/", json=req, timeout=120)
    r.raise_for_status()
    resp = r.json()
    dump("RESPONSE", resp)
    if "error" in resp:
        raise RuntimeError(f"server error: {resp['error']}")
    return resp["result"]


def get_task(task_id: str) -> dict[str, Any]:
    """Re-fetch a task by id via JSON-RPC tasks/get."""
    req = {
        "jsonrpc": "2.0",
        "id": uuid.uuid4().hex[:8],
        "method": "tasks/get",
        "params": {"id": task_id},
    }
    print(f"\nPOST {SERVER}/    (tasks/get)")
    dump("REQUEST", req)
    r = requests.post(SERVER + "/", json=req, timeout=30)
    r.raise_for_status()
    resp = r.json()
    dump("RESPONSE", resp)
    return resp["result"]


def extract_agent_text(task: dict[str, Any]) -> str:
    """Pull the last agent-authored text part out of a task's history."""
    for msg in reversed(task.get("history") or []):
        if msg.get("role") == "agent":
            for p in msg.get("parts", []):
                if "text" in p:
                    return p["text"]
    return "(no agent reply found)"


def main() -> None:
    user_text = (sys.argv[1] if len(sys.argv) > 1
                 else "How many kilometres are 3 miles?")

    print("═" * 66)
    print(f"USER  →  {user_text}")
    print("═" * 66)

    card = fetch_card()
    print(f"\n(agent name: {card.get('name')!r},  "
          f"skills: {[s['id'] for s in card.get('skills', [])]})")

    task = send_message(user_text)
    task_id = task["id"]
    print(f"\n(server assigned task id: {task_id})")

    # Prove tasks/get works — same task, retrieved by id afterwards.
    task_again = get_task(task_id)
    if task_again["id"] != task_id:
        print("[warn] tasks/get returned a different task id!")

    answer = extract_agent_text(task_again)
    print()
    print("═" * 66)
    print(f"ASSISTANT  →  {answer}")
    print("═" * 66)
    print()
    print("→ Card discovered, message sent, task completed, task re-fetched.")
    print("→ Everything above went through plain JSON on one HTTP port.")
    print("→ That is A2A.  The A2A Inspector shows the same JSON in a browser.")


if __name__ == "__main__":
    main()