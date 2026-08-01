"""
01 · mcp_client  —  Kapitel 5, Miniatur 1

Slide-Anker :  MCP · von N×M zu N+M
Laufzeit    :  < 3 Sekunden
Kosten      :  0 Tokens (kein LLM in dieser Miniatur — nur JSON-RPC)

Ein MCP-Client der:
  1. `initialize` sendet und die Server-Info zeigt
  2. `tools/list` fragt und die verfügbaren Werkzeuge druckt
  3. `tools/call` für getSupplierMasterData ausführt
  4. `tools/call` für getOpenPurchaseOrders ausführt

Der Server läuft in-process (siehe mcp_server.py) — für die Miniatur
reicht das, um die JSON-RPC-Nachrichten sichtbar zu machen.

In der Produktion würde der Server als eigener Prozess laufen
(stdio- oder HTTP+SSE-Kommunikation).

Ausführen:
    python "Agentic Systems/05_ProtocolsAndScale/src/01_mcp_client.py"
"""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS   = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

# Server-Modul aus DEMSELBEN Verzeichnis wie das Skript.  In der Produktion
# würde der Server als eigener Prozess laufen und wir würden ihm über
# stdio- oder HTTP+SSE Nachrichten schicken.
sys.path.insert(0, str(_HERE.parent))
import mcp_server as SERVER   # noqa: E402

from common.ui import hard_card, soft_frame, phase_break, wrap   # noqa: E402


# ---- kleiner Helper: Request bauen, dispatchen, beides drucken ----

_next_id = 0
def _next_request_id() -> int:
    global _next_id
    _next_id += 1
    return _next_id


def rpc(method: str, params: dict | None = None) -> dict:
    """Baut einen JSON-RPC-2.0-Request, ruft den Server-Dispatcher,
    druckt beide Nachrichten und gibt das Result-Feld der Response zurück."""
    request = {
        "jsonrpc": "2.0",
        "id":      _next_request_id(),
        "method":  method,
    }
    if params is not None:
        request["params"] = params

    hard_card(
        title    = "▸  REQUEST  (Client → Server)",
        subtitle = f"JSON-RPC 2.0 · method={method!r}",
        body     = json.dumps(request, indent=2, ensure_ascii=False),
    )

    response = SERVER.dispatch(request)

    hard_card(
        title    = "▸  RESPONSE  (Server → Client)",
        subtitle = ("Fehler: siehe error-Feld"
                    if "error" in response else "OK"),
        body     = json.dumps(response, indent=2, ensure_ascii=False),
    )

    if "error" in response:
        raise RuntimeError(f"RPC-Fehler: {response['error']}")
    return response["result"]


# ---- die vier Schritte ----

def main():
    phase_break("MCP-Miniatur · Handshake → List → Call")

    # -------- 1. initialize -----------------------------------------
    phase_break("1) initialize   —   'Hallo Server, welche Version sprichst du?'")
    server_info = rpc("initialize", {
        "protocolVersion": "2024-11-05",
        "clientInfo": {"name": "agentic-systems-demo-client",
                       "version": "0.1.0"},
        "capabilities": {},
    })
    soft_frame(
        "Server hat sich vorgestellt",
        [
            f"Name           : {server_info['serverInfo']['name']}",
            f"Version        : {server_info['serverInfo']['version']}",
            f"MCP-Protokoll  : {server_info['serverInfo']['protocolVersion']}",
            f"Capabilities   : {server_info['capabilities']}",
        ],
    )

    # -------- 2. tools/list -----------------------------------------
    phase_break("2) tools/list   —   'Welche Werkzeuge bietest du an?'")
    listing = rpc("tools/list")
    tool_lines = []
    for t in listing["tools"]:
        tool_lines.append(f"▸ {t['name']}")
        tool_lines.append(f"    {t['description']}")
        required = t['inputSchema'].get('required', [])
        for arg in required:
            arg_type = t['inputSchema']['properties'][arg].get('type', '?')
            tool_lines.append(f"    Argument (required): {arg}: {arg_type}")
        tool_lines.append("")
    soft_frame(f"Server bietet {len(listing['tools'])} Werkzeuge an",
               tool_lines)

    # -------- 3. tools/call — Werkzeug 1 ---------------------------
    phase_break("3) tools/call   —   getSupplierMasterData(ACME-42)")
    result1 = rpc("tools/call", {
        "name": "getSupplierMasterData",
        "arguments": {"supplier_id": "ACME-42"},
    })
    soft_frame(
        "Rohes Werkzeug-Ergebnis (aus content[type=text])",
        wrap(result1["content"][0]["text"]),
    )

    # -------- 4. tools/call — Werkzeug 2 ---------------------------
    phase_break("4) tools/call   —   getOpenPurchaseOrders(ACME-42)")
    result2 = rpc("tools/call", {
        "name": "getOpenPurchaseOrders",
        "arguments": {"supplier_id": "ACME-42"},
    })
    soft_frame(
        "Rohes Werkzeug-Ergebnis",
        wrap(result2["content"][0]["text"]),
    )

    # -------- der Punkt --------------------------------------------
    soft_frame(
        "WAS DU GERADE GESEHEN HAST",
        [
            "Vier Nachrichten.  Alle vier sind JSON-RPC 2.0.  Alle vier",
            "sind pures Text.  Kein Framework, keine Bibliothek.",
            "",
            "Ein anderer Client — von einer anderen Person, in einer anderen",
            "Sprache, für ein anderes Modell — würde EXAKT dieselben",
            "Nachrichten schicken und dieselben Antworten bekommen.",
            "",
            "Das ist der ganze Punkt von MCP: das *dazwischen* ist",
            "standardisiert.  Was rechts (Server) und links (Client) davon",
            "läuft, kann sich unabhängig entwickeln.",
        ],
    )

    print()
    print("→ Zwei Werkzeuge heute.  Zwanzig morgen.  Kein Refactor.")
    print("→ Der Loop-Runner (Kapitel 3) braucht nur EINEN MCP-Client,")
    print("  egal wie viele Server im Netzwerk hängen.")


if __name__ == "__main__":
    main()