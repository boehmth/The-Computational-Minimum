# a2a · den mini-agent aus Kap. 2 live über A2A ansprechen

**Der Agent aus `../../../02_ToolsAndPlanning/src/mini_agent/step_f_fallback_and_errors.py` bekommt eine Netzwerk-Adresse. Kein neues Agent-Hirn — nur Transport.**

Die zwei Miniaturen im Kapitel oben (`../01_mcp_client.py`, `../02_a2a_client.py`) zeigen die **Nachrichten-Form** von MCP und A2A. Sie sprechen mit In-Prozess-Servern zu didaktischen Zwecken. Diese Bonus-Sektion hier zeigt das **echte Wire-Setup**: ein separater FastAPI-Server-Prozess, ein separater Client-Prozess, alles über HTTP + JSON-RPC.

Sinn: du siehst nicht nur die Nachrichten, du siehst *den ganzen Umweg über den Netzwerkstack*.

## Was du hier findest

| Datei | Was es tut |
|-------|------------|
| `step_g_agent_server.py` | FastAPI-Server: Agent-Card + JSON-RPC `message/send` + `tasks/get`. Wrappt `run_once()` aus Kap. 2 · step_f. |
| `step_h_agent_client.py` | 60-Zeilen-Client: Card holen, Nachricht schicken, Task pollen, Antwort drucken. |
| `demo.ps1` / `demo.sh` | Einzeilen-Demo: startet Server, wartet, feuert Client, druckt Log, beendet Server. |
| — (interaktiv) | Der [A2A Inspector](https://github.com/google-a2a/a2a-inspector) im Browser gegen `http://localhost:8000`. |

Vergleiche `step_g` mit `../../../02_ToolsAndPlanning/src/mini_agent/step_f_fallback_and_errors.py`: das Agent-Hirn ist unverändert. Aller neue Code ist Transport. Diese Unterscheidung ist der ganze Punkt der Sektion.

## Voraussetzungen

```bash
pip install fastapi uvicorn requests
```

Server benutzt dieselbe `common/llm.py`-Konfiguration wie der Rest des Repos (SAP GenAI Hub oder Gemini via `.env`).

## Ein-Kommando-Demo (empfohlen für Live-Vorführung)

```powershell
# Windows / PowerShell
.\demo.ps1
.\demo.ps1 "What is 43177 times 14694?"
```

```bash
# macOS / Linux / WSL
chmod +x demo.sh        # nur beim ersten Mal
./demo.sh
./demo.sh "What is 43177 times 14694?"
```

Beide Skripte:

1. starten `step_g_agent_server.py` im Hintergrund,
2. warten bis zu ~16 s, bis `/.well-known/agent-card.json` antwortet,
3. holen und pretty-printen die Agent-Card,
4. rufen `step_h_agent_client.py` mit deinem Prompt (Default: *"How many kilometres are 3 miles?"*) auf,
5. dumpen das Server-Log und beenden den Server.

Ergebnis: die ganze A2A-Story — Discovery, Invocation, Task-Retrieval, Teardown — in einem scrollbaren Transkript.

## Einzeln laufen lassen

```bash
# Terminal 1
python "05_ProtocolsAndScale/src/a2a/step_g_agent_server.py"
# → lauscht auf http://localhost:8000

# Terminal 2
python "05_ProtocolsAndScale/src/a2a/step_h_agent_client.py"
python "05_ProtocolsAndScale/src/a2a/step_h_agent_client.py" "What is 43177 times 14694?"

# oder direkt mit curl:
curl http://localhost:8000/.well-known/agent-card.json | python -m json.tool

curl -sS -X POST http://localhost:8000/ \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"message/send",
          "params":{"message":{"role":"user",
          "parts":[{"kind":"text","text":"How many km are 3 miles?"}]}}}'
```

## A2A Inspector (interaktiv)

Der **A2A Inspector** ist eine kleine Web-UI, die Google publiziert, um beliebige A2A-Agenten zu testen. Sie lädt die Agent-Card, rendert sie, gibt dir ein Chat-Fenster und zeigt jede JSON-RPC-Nachricht daneben — Postman-artig.

Da das Inspector-Projekt separat lebt und sich die Bootstrap-Anweisungen ändern, immer **das aktuelle README auf `google-a2a/a2a-inspector` konsultieren**. Das Muster bleibt stabil:

```bash
# Option A – Docker (einfachste für Live-Vorführung)
git clone https://github.com/google-a2a/a2a-inspector.git
cd a2a-inspector
docker compose up
# → dann http://localhost:<inspector-port> aufmachen (steht im Inspector-README)

# Option B – uv / npm dev mode
uv sync                    # oder: npm install
uv run inspector           # oder: npm run dev
```

Wenn der Inspector läuft:

1. Starte den mini-agent-Server: `python step_g_agent_server.py`.
2. Öffne den Inspector im Browser.
3. In das Feld "Agent URL" trage `http://localhost:8000` ein. Der Inspector holt `/.well-known/agent-card.json`, rendert Name/Skills/Capabilities und schaltet den Chat-Panel frei.
4. Ins Chat schreiben. Auf jeden "Send" bekommst du zwei Sachen gleichzeitig:
   - eine **Chat-Bubble** mit der Antwort des Agenten,
   - den **rohen JSON-RPC-Request und -Response** in einem Nebenpanel.

Das ist der Demo-Money-Shot. Nichts an deinem Server ist Magie; der Inspector beweist es, indem er die plain HTTP-Calls zeigt, die den Chat produziert haben.

**Screencast-Tipp**: da sowohl Inspector als auch dein Agent auf `localhost` laufen, funktioniert alles offline. Du kannst das im Flugzeug demonstrieren.

## Was A2A *nicht* löst

- **Agent-Qualität.** Ein langsamer oder falscher Agent bleibt langsam/falsch, wenn du ihn in A2A einwickelst. Das Protokoll ist orthogonal zum Reasoning innen.
- **Vertrauen.** Nur weil du einen Agenten *aufrufen kannst*, heißt das nicht, dass du es *solltest*. Auth (mTLS, OAuth, signierte Cards) ist eine separate Schicht.
- **State über Aufrufe hinweg.** Unser Server behandelt jeden Request als frischen Task und vergisst ihn danach. Echte Multi-Turn-Konversationen brauchen einen Task-Store — für die Praxis wäre das ein Redis oder Postgres. Kein Bestandteil dieser Miniatur.

## Wo diese Sektion im Bogen steht

- Kapitel 5, Miniatur 1 (`../01_mcp_client.py`) · **Werkzeuge in-process, MCP-Wire-Format.**
- Kapitel 5, Miniatur 2 (`../02_a2a_client.py`) · **Agent in-process, A2A-Wire-Format.**
- Kapitel 5, `a2a/` (**diese Sektion**) · **Agent als separater Prozess über HTTP.**
- Kapitel 7 (`../../../07_DynamicToolAgent/`) · **Werkzeug-Generierung zur Laufzeit** — kein direktes A2A-Thema, aber logisch die nächste Frage: was, wenn nicht mal die Werkzeuge menschgeschrieben sind?