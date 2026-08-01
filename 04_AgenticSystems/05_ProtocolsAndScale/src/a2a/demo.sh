#!/usr/bin/env bash
# demo.sh — one-shot A2A demo.
#
# Starts step_g_agent_server.py in the background, waits for it,
# fetches /.well-known/agent-card.json, runs step_h_agent_client.py,
# then shuts the server down.
#
# Usage:
#   ./demo.sh
#   ./demo.sh "What is 43177 times 14694?"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER="$SCRIPT_DIR/step_g_agent_server.py"
CLIENT="$SCRIPT_DIR/step_h_agent_client.py"
SERVER_URL="http://localhost:8000"
CARD_URL="$SERVER_URL/.well-known/agent-card.json"

USER_PROMPT="${1:-How many kilometres are 3 miles?}"

section() {
    echo
    printf '%s\n' "══════════════════════════════════════════════════════════════════════"
    printf '  %s\n' "$1"
    printf '%s\n' "══════════════════════════════════════════════════════════════════════"
}

# ── 1. launch server ─────────────────────────────────────────────────
section "1/4  starting A2A server (background)"
echo "→ python $SERVER"

LOGFILE="$(mktemp -t a2a_server.XXXXXX.log)"
python "$SERVER" >"$LOGFILE" 2>&1 &
SERVER_PID=$!

cleanup() {
    if kill -0 "$SERVER_PID" 2>/dev/null; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

# ── 2. wait for card endpoint ────────────────────────────────────────
section "2/4  waiting for server to accept requests"

READY=0
for _ in $(seq 1 40); do   # 40 * 0.4s = 16s max
    if curl -sSf --max-time 2 "$CARD_URL" >/dev/null 2>&1; then
        READY=1
        break
    fi
    sleep 0.4
done

if [[ "$READY" -ne 1 ]]; then
    echo "[error] server did not respond within 16 s" >&2
    echo "── server log ──" >&2
    cat "$LOGFILE" >&2 || true
    exit 1
fi
echo "→ server up at $SERVER_URL"

# ── 3. fetch agent card ──────────────────────────────────────────────
section "3/4  GET  $CARD_URL"

if command -v jq >/dev/null 2>&1; then
    curl -sS "$CARD_URL" | jq .
else
    curl -sS "$CARD_URL" | python -m json.tool
fi

# ── 4. run the client ────────────────────────────────────────────────
section "4/4  python step_h_agent_client.py \"$USER_PROMPT\""

set +e
python "$CLIENT" "$USER_PROMPT"
CLIENT_EXIT=$?
set -e

# ── 5. shutdown & summary ────────────────────────────────────────────
section "shutdown"

cleanup
trap - EXIT

if [[ -s "$LOGFILE" ]]; then
    echo "── server log ─────────────────────────────"
    cat "$LOGFILE"
fi
rm -f "$LOGFILE"

echo
if [[ "$CLIENT_EXIT" -eq 0 ]]; then
    echo "✓ demo complete"
else
    echo "✗ demo finished with errors (exit $CLIENT_EXIT)"
fi
exit "$CLIENT_EXIT"