"""
02 · a2a_client  —  Kapitel 5, Miniatur 2

Slide-Anker :  A2A · derselbe Wire-Format wie MCP, aber der Callable
              ist ein Agent, kein Werkzeug.
Laufzeit    :  15-30 Sekunden
Kosten      :  ~1500-3000 Tokens (der A2A-Server macht intern einen
              kleinen Agent-Loop mit dem LLM)

Wir simulieren einen A2A-Server, der einen "Einkaufs-Analyst-Agent"
hostet.  Der Client schickt eine natürlichsprachliche Anfrage; der
Server antwortet mit einer natürlichsprachlichen Analyse — nachdem
er intern seinen eigenen Loop (mit MCP-Werkzeugen aus Miniatur 1)
durchlaufen ist.

Aus Sicht des Clients:  DU SIEHST NUR ANFRAGE UND ANTWORT.
Der ganze Loop im Server ist unsichtbar.

Ausführen:
    python "Agentic Systems/05_ProtocolsAndScale/src/02_a2a_client.py"
"""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS   = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

sys.path.insert(0, str(_HERE.parent))
import mcp_server as MCP   # unsere MCP-Werkzeuge aus Miniatur 1  # noqa: E402

from common.llm import chat, extract_json                          # noqa: E402
from common.ui  import hard_card, soft_frame, phase_break, wrap    # noqa: E402


# ===========================================================================
#  Der simulierte A2A-Server (was in Produktion auf einem anderen Rechner läuft)
# ===========================================================================

AGENT_CARD = {
    "name":        "Einkaufs-Analyst-Agent",
    "description": "Analysiert die Situation eines Lieferanten anhand von "
                   "Stammdaten und offenen Bestellungen, und gibt eine "
                   "Empfehlung ab (Freigeben / Prüfen / Blockieren).",
    "url":         "https://example.com/agents/procurement-analyst",
    "version":     "0.1.0",
    "capabilities": {
        "streaming":     False,
        "pushNotifications": False,
    },
    "skills": [
        {
            "id":   "supplier-risk-check",
            "name": "Supplier Risk Check",
            "description": "Prüfe einen Lieferanten und gib eine Empfehlung",
            "inputModes":  ["text"],
            "outputModes": ["text"],
        },
    ],
}


AGENT_SYSTEM = """Du bist der Einkaufs-Analyst.  Du hast Zugriff auf ZWEI
MCP-Werkzeuge über einen JSON-RPC-Server:

  getSupplierMasterData(supplier_id)   → Stammdaten
  getOpenPurchaseOrders(supplier_id)   → offene Bestellungen

Bei jedem Turn: gib GENAU EIN JSON-Objekt aus, nichts anderes:

  {"tool": "<name>", "args": { ... }}
    oder
  {"final": "<eine strukturierte Empfehlung in prägnantem Deutsch>"}

Beispiel finale Antwort:
  {"final": "Empfehlung: FREIGEBEN.  Grund: ..."}

Nutze BEIDE Werkzeuge bevor du eine Empfehlung abgibst."""


def _rpc_to_mcp(method: str, params: dict | None = None) -> dict:
    """Kleiner Wrapper — der Agent nutzt intern denselben MCP-Server wie
    Miniatur 1 (Werkzeuge über JSON-RPC)."""
    req = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        req["params"] = params
    resp = MCP.dispatch(req)
    if "error" in resp:
        raise RuntimeError(f"MCP-Fehler: {resp['error']}")
    return resp["result"]


def a2a_server_process_task(user_message: str, verbose: bool = True) -> dict:
    """Der Innere Loop des A2A-Servers.  Aus Sicht eines A2A-Clients ist
    das eine einzige RPC — er sieht nur Input und Output.  Wir drucken
    hier trotzdem alles, damit die Miniatur pädagogisch aufgeht.

    Returned dict im A2A-Task-Style:
        {"id": ..., "status": "completed",
         "history": [ ... ],
         "artifacts": [{"parts": [{"type": "text", "text": "..."}]}]}
    """

    # -------- Werkzeuge-Discovery via MCP --------
    tools_listing = _rpc_to_mcp("tools/list")
    tool_desc = "\n".join(
        f"  {t['name']}(supplier_id)   → {t['description']}"
        for t in tools_listing["tools"]
    )
    system = AGENT_SYSTEM + "\n\nVerfügbare Werkzeuge (aus MCP):\n" + tool_desc

    history = [
        {"role": "system", "content": system},
        {"role": "user",   "content": user_message},
    ]

    turns_taken = []
    total_tokens = 0
    MAX_TURNS = 5

    for turn in range(1, MAX_TURNS + 1):
        prompt = "\n\n".join(f"{m['role'].upper()}: {m['content']}"
                             for m in history)
        r = chat(system=system, user=prompt, want_json=True, max_tokens=1024)
        total_tokens += r.tokens
        msg = extract_json(r.text)

        if verbose:
            hard_card(
                title    = f"[A2A-Server intern]  Turn {turn}  ·  Modell-Output",
                subtitle = f"{r.tokens_out} out-Tokens · "
                           + ("final ✓" if "final" in msg
                              else f"tool: {msg.get('tool')}"),
                body     = json.dumps(msg, indent=2, ensure_ascii=False),
            )

        if "final" in msg:
            turns_taken.append(("final", msg["final"]))
            return {
                "id":     "task-001",
                "status": "completed",
                "history": [
                    {"role": "user",  "parts": [{"type": "text",
                                                 "text": user_message}]},
                    {"role": "agent", "parts": [{"type": "text",
                                                 "text": msg["final"]}]},
                ],
                "artifacts": [
                    {"parts": [{"type": "text", "text": msg["final"]}]},
                ],
                "_internal": {
                    "turns":  turn,
                    "tokens": total_tokens,
                    "trace":  turns_taken,
                },
            }

        # Werkzeug aufrufen (via MCP)
        tool_name = msg["tool"]
        args      = msg.get("args", {})
        try:
            mcp_result = _rpc_to_mcp("tools/call", {
                "name": tool_name, "arguments": args,
            })
            observation = mcp_result["content"][0]["text"]
        except Exception as e:
            observation = f"error: {e}"

        turns_taken.append((tool_name, args))

        if verbose:
            print(f"    → MCP-tools/call {tool_name}({args})  =  "
                  f"{observation[:100].strip()}...")

        history.append({"role": "assistant", "content": r.text})
        history.append({"role": "user",
                        "content": f"[observation] {tool_name} lieferte:\n"
                                   f"{observation}"})

    return {
        "id":     "task-001",
        "status": "failed",
        "error":  f"max turns ({MAX_TURNS}) exceeded",
        "_internal": {"turns": MAX_TURNS, "tokens": total_tokens},
    }


# ===========================================================================
#  Der A2A-Client (das, was ein anderer Agent oder Programm bei uns aufruft)
# ===========================================================================

def a2a_get_agent_card() -> dict:
    """A2A-Konvention: der Server publiziert eine Agent-Card unter
    /.well-known/agent.json.  Wir liefern sie hier direkt."""
    return AGENT_CARD


def a2a_send_task(user_message: str) -> dict:
    """A2A-Methode: tasks/send.  Client schickt eine Text-Nachricht,
    Server macht seinen Loop und antwortet mit einer strukturierten Task."""
    request = {
        "jsonrpc": "2.0",
        "id":      101,
        "method":  "tasks/send",
        "params": {
            "id":      "task-001",
            "message": {
                "role":  "user",
                "parts": [{"type": "text", "text": user_message}],
            },
        },
    }

    hard_card(
        title    = "▸  A2A-REQUEST  (Client → Agent)",
        subtitle = "JSON-RPC 2.0 · method='tasks/send'",
        body     = json.dumps(request, indent=2, ensure_ascii=False),
    )

    phase_break("intern  ·  der A2A-Server läuft jetzt seinen eigenen Loop")

    result = a2a_server_process_task(user_message, verbose=True)

    phase_break("intern  ·  A2A-Server fertig — sendet Response")

    hard_card(
        title    = "▸  A2A-RESPONSE  (Agent → Client)",
        subtitle = f"status={result.get('status')} · task-id={result.get('id')}",
        body     = json.dumps({k: v for k, v in result.items()
                               if not k.startswith("_")},
                              indent=2, ensure_ascii=False),
    )
    return result


# ===========================================================================
#  Main
# ===========================================================================

def main():
    phase_break("A2A-Miniatur · agent-card holen, task schicken, antwort empfangen")

    # -------- 1) Agent-Card lesen (der Client entdeckt den Agent) --------
    phase_break("1) Agent-Card  ·  wer ist der Agent, was kann er?")
    card = a2a_get_agent_card()
    soft_frame(
        "Agent-Card (typischerweise unter /.well-known/agent.json)",
        [
            f"Name         : {card['name']}",
            f"Beschreibung : {card['description']}",
            f"Version      : {card['version']}",
            "Skills:",
        ] + [f"  ▸ {s['name']} — {s['description']}" for s in card['skills']],
    )

    # -------- 2) Task schicken --------
    phase_break("2) tasks/send  ·  natürlichsprachliche Anfrage schicken")
    user_message = (
        "Ich muss entscheiden ob wir noch mehr bei ACME-42 bestellen können. "
        "Was ist die Empfehlung?"
    )
    hard_card(
        title    = "USER FRAGE (natürliche Sprache — kein JSON-Schema nötig)",
        subtitle = "der Client weiß NICHT welche Werkzeuge im Server stecken",
        body     = user_message,
    )

    result = a2a_send_task(user_message)

    # -------- 3) Antwort auspacken --------
    if result.get("status") == "completed":
        final_text = result["artifacts"][0]["parts"][0]["text"]
        internal = result.get("_internal", {})
        soft_frame(
            "WAS DER CLIENT SIEHT  (unabhängig davon was im Server war)",
            [
                "FINALE ANTWORT DES AGENTS:",
                *wrap(final_text),
                "",
                f"Turns im Server:   {internal.get('turns', '?')}",
                f"Tokens im Server:  {internal.get('tokens', '?')}",
                "",
                "Wichtig:  in Produktion wäre der Turn-Zähler und die",
                "Token-Zahl NICHT im Response.  Der Client sieht nur",
                "die finale Antwort.  Wir haben sie hier für die",
                "Pädagogik ergänzt.",
            ],
        )
    else:
        soft_frame(
            "TASK FEHLGESCHLAGEN",
            [f"Fehler: {result.get('error', 'unbekannt')}"],
        )

    # -------- der Punkt --------
    soft_frame(
        "WAS DU GERADE GESEHEN HAST",
        [
            "Ein A2A-Aufruf sieht aus wie ein MCP-Aufruf.  Beide sind",
            "JSON-RPC 2.0 über Text.  Der einzige Unterschied ist:",
            "",
            "  MCP:  method='tools/call'  →  Ziel ist ein Werkzeug",
            "  A2A:  method='tasks/send'  →  Ziel ist ein Agent",
            "",
            "Das Werkzeug antwortet mit Daten.  Der Agent antwortet mit",
            "Text — nach seinem eigenen internen Loop.",
            "",
            "Aus Sicht des Clients: derselbe wire format.  Die Komplexität",
            "hinter der Antwort ist unsichtbar.  Genau wie beim reasoning-",
            "Modell in Kapitel 4 — nur eine Ebene höher.",
        ],
    )

    print()
    print("→ Werkzeuge (MCP) und Agenten (A2A) sind aus Client-Sicht dasselbe:")
    print("  ein JSON-RPC-Aufruf, ein JSON-RPC-Response, Text hin und Text her.")
    print("→ Das ist der Punkt, an dem 'Agentic Systems' erst wirklich skalieren.")


if __name__ == "__main__":
    main()
