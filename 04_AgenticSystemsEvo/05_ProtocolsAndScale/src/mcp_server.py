"""
mcp_server.py — ein minimaler MCP-Server (Model Context Protocol).

Der ECHTE Standard läuft über stdio- oder HTTP+SSE-Kommunikation.
Für die Miniatur reicht ein in-Process Dispatcher: der Client
formuliert JSON-RPC-Nachrichten und ruft `dispatch(request)` auf.

Das lässt uns sehen, wie die *Nachrichten* aussehen und wie die
*Werkzeug-Registry* funktioniert — ohne mit subprocess / pipes / SSE
zu ringen.

Referenzen:
  - JSON-RPC 2.0 spec: https://www.jsonrpc.org/specification
  - MCP spec (Nov 2024, Anthropic): https://modelcontextprotocol.io
"""

from __future__ import annotations
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Werkzeug-Registry
# ---------------------------------------------------------------------------
# Jedes Werkzeug ist ein Eintrag:
#     name        — wie es der Client aufruft
#     description — natürlichsprachliche Beschreibung
#     input_schema — JSON-Schema für die Argumente
#     handler     — Python-Funktion, die den Aufruf macht
# ---------------------------------------------------------------------------

TOOLS: dict[str, dict[str, Any]] = {}


def register_tool(*, name: str, description: str,
                  input_schema: dict, handler: Callable):
    TOOLS[name] = {
        "name": name,
        "description": description,
        "inputSchema": input_schema,
        "_handler": handler,
    }


# ---------------------------------------------------------------------------
# Zwei Beispiel-Werkzeuge (SAP-artige Mock-Daten)
# ---------------------------------------------------------------------------

_SUPPLIERS = {
    "ACME-42": {"name": "ACME GmbH", "country": "DE",
                "payment_terms": "30 Tage netto", "credit_limit_eur": 250000},
    "GLOBEX-7": {"name": "Globex Corp", "country": "US",
                 "payment_terms": "45 Tage netto", "credit_limit_eur": 500000},
}

_OPEN_POS = {
    "ACME-42": [
        {"po": "4500123", "amount_eur":  12480, "status": "shipped"},
        {"po": "4500145", "amount_eur":   3220, "status": "pending"},
    ],
    "GLOBEX-7": [
        {"po": "4500098", "amount_eur":  87000, "status": "pending"},
    ],
}


def _get_supplier_master_data(supplier_id: str) -> dict:
    if supplier_id not in _SUPPLIERS:
        return {"error": "unknown supplier", "supplier_id": supplier_id}
    return {"supplier_id": supplier_id, **_SUPPLIERS[supplier_id]}


def _get_open_purchase_orders(supplier_id: str) -> dict:
    orders = _OPEN_POS.get(supplier_id, [])
    return {"supplier_id": supplier_id, "count": len(orders),
            "orders": orders}


register_tool(
    name="getSupplierMasterData",
    description="Liefert Stammdaten (Name, Land, Zahlungsziele, Kreditlimit) "
                "für einen Lieferanten anhand seiner ID.",
    input_schema={
        "type": "object",
        "properties": {
            "supplier_id": {
                "type": "string",
                "description": "eindeutige Lieferanten-ID, z.B. ACME-42",
            },
        },
        "required": ["supplier_id"],
    },
    handler=_get_supplier_master_data,
)

register_tool(
    name="getOpenPurchaseOrders",
    description="Liefert die offenen Bestellungen (mit Status und Betrag) "
                "für einen Lieferanten.",
    input_schema={
        "type": "object",
        "properties": {
            "supplier_id": {
                "type": "string",
                "description": "Lieferanten-ID",
            },
        },
        "required": ["supplier_id"],
    },
    handler=_get_open_purchase_orders,
)


# ---------------------------------------------------------------------------
# JSON-RPC-Dispatch
# ---------------------------------------------------------------------------
# Wir unterstützen die MCP-Kern-Methoden:
#   initialize   — Handshake, gibt server info + capabilities zurück
#   tools/list   — Liste aller registrierten Werkzeuge
#   tools/call   — führe ein Werkzeug aus
# ---------------------------------------------------------------------------

SERVER_INFO = {
    "name":    "agentic-systems-demo-server",
    "version": "0.1.0",
    "protocolVersion": "2024-11-05",
    "capabilities": {"tools": {"listChanged": False}},
}


def _tool_summary(tool: dict) -> dict:
    """Werkzeug für tools/list — ohne den Python-Handler."""
    return {
        "name":        tool["name"],
        "description": tool["description"],
        "inputSchema": tool["inputSchema"],
    }


def _make_error(id_: Any, code: int, message: str, data: Any = None) -> dict:
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": id_, "error": err}


def _make_result(id_: Any, result: Any) -> dict:
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def dispatch(request: dict) -> dict:
    """Nimmt einen JSON-RPC-2.0-Request-dict entgegen, gibt Response-dict zurück.

    Das ist die eine Funktion, die ein echter stdio-Server um eine
    `while True: line = sys.stdin.readline(); ...`-Schleife herum hätte.
    """
    id_    = request.get("id")
    method = request.get("method")

    if method == "initialize":
        # Der Client schickt uns seine Client-Info; wir bestätigen mit
        # unserer Server-Info und den Capabilities.
        return _make_result(id_, {"serverInfo": SERVER_INFO,
                                  "capabilities": SERVER_INFO["capabilities"]})

    if method == "tools/list":
        return _make_result(id_, {
            "tools": [_tool_summary(t) for t in TOOLS.values()],
        })

    if method == "tools/call":
        params = request.get("params") or {}
        name   = params.get("name")
        args   = params.get("arguments") or {}
        tool   = TOOLS.get(name)
        if tool is None:
            return _make_error(id_, -32601, f"unknown tool: {name!r}")
        try:
            result = tool["_handler"](**args)
        except TypeError as e:
            return _make_error(id_, -32602, f"invalid arguments: {e}")
        except Exception as e:
            return _make_error(id_, -32000, f"tool error: {e}")
        # MCP wickelt das Ergebnis in `content`-Blöcke.
        return _make_result(id_, {
            "content": [
                {"type": "text",
                 "text": _json_pretty(result)}
            ],
            "isError": False,
        })

    return _make_error(id_, -32601, f"unknown method: {method!r}")


# ---------------------------------------------------------------------------
# Kleine Hilfsfunktion
# ---------------------------------------------------------------------------

import json


def _json_pretty(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)