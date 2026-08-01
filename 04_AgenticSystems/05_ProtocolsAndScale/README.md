# Kapitel 5 · Protokolle und Skalierung

**Wie fremde Werkzeuge und fremde Agenten mit deinem Loop reden — ohne dass du für jedes einen eigenen Wrapper schreibst.**

Zwei Miniaturen. Die erste zeigt einen minimalen **MCP-Server** und den zugehörigen **Client**: JSON-RPC 2.0 über stdio, Werkzeug-Entdeckung, Werkzeug-Aufruf. Die zweite zeigt einen **A2A-Client**, der einen Agent-Endpunkt anspricht — dasselbe Wire-Format wie MCP, aber der Callable ist ein Modell, kein Werkzeug.

Beides in ~100-150 Zeilen Python, ohne Framework.

---

## 📜 Historischer Kontext

Vor November 2024 sah die Werkzeug-Landschaft so aus:

- Anthropic Claude hatte seine eigenen `<tool_use>`-Tags im Text.
- OpenAI hatte `function_calling` mit einem eigenen JSON-Schema.
- Google Gemini hatte `function_declarations` — verwandt, aber nicht kompatibel.
- Jedes Unternehmen hatte seine eigenen internen Werkzeug-Registries mit ihren eigenen Schemas.

Das Ergebnis: **N × M bespoke Integrationen**. 10 Modelle × 20 Werkzeuge = 200 handgeschriebene Adapter. Jede neue Kombination ein neues Adapter-Projekt. Jede Werkzeug-API-Änderung ein Refactor über 10 Modelle hinweg.

**November 2024 · Anthropic veröffentlicht das Model Context Protocol (MCP)**. Ein einfacher Vorschlag: standardisiere das *Werkzeug-Schema* — nicht das Modell, nicht den Client, sondern das *dazwischen*. Ein MCP-Server bietet Werkzeuge über eine JSON-RPC-2.0-Schnittstelle an. Jeder Client, der MCP spricht, kann jeden Server ansprechen. Aus *N × M* wird *N + M*.

Der Trick: **MCP ist absichtlich fast leer**. Es definiert nur die *Rahmung*:

- `initialize` — Handshake, Version, Capabilities
- `tools/list` — welche Werkzeuge bietest du an? (Namen + Beschreibungen + JSON-Schemas)
- `tools/call` — führe Werkzeug X mit Argumenten Y aus
- `prompts/list`, `resources/list` — optionale Erweiterungen

Kein Framework. Kein magischer Runtime. Nur ein bewährtes RPC-Format (JSON-RPC 2.0, aus dem Jahr 2005) und eine kleine Menge standardisierter Methoden.

**Anfang 2025 · Google formuliert A2A (Agent-to-Agent)**. Dieselbe Beobachtung, eine Ebene höher: wenn Werkzeuge standardisiert erreichbar sein können, warum nicht auch *Agenten*? Ein A2A-Endpunkt akzeptiert eine natürlichsprachliche Anfrage und liefert eine natürlichsprachliche Antwort — mit Zwischen-Updates zum Fortschritt. Aus Client-Sicht ist ein A2A-Server nicht unterscheidbar von einem MCP-Server mit einem einzigen sehr allgemeinen "Werkzeug" namens "frag mich was".

Zusammen ergibt sich eine Architektur, die vor MCP nicht möglich war:

> Dein Agent-Loop kann fremde Werkzeuge (über MCP) und fremde Agenten (über A2A) nutzen, ohne dass du für sie irgendeinen bespoke Code schreibst. Der Loop-Runner braucht nur *einen* MCP/A2A-Client — und die Werkzeug-Landschaft wächst, ohne dass dein Loop-Code sich ändert.

---

## 🔬 Die zwei Miniaturen

### `src/01_mcp_client.py` (+ `src/mcp_server.py`) — Server und Client sprechen JSON-RPC

Zwei Dateien. Die erste (`mcp_server.py`) ist eine minimale MCP-Server-Implementierung — sie registriert **zwei Werkzeuge**:

- `getSupplierMasterData(supplier_id)` — liefert (Mock-)Stammdaten für einen Lieferanten
- `getOpenPurchaseOrders(supplier_id)` — liefert (Mock-)offene Bestellungen

Beide sind bewusst SAP-artig gewählt: das sind genau die Werkzeuge, die ein Einkaufs-Agent in einem ERP-Kontext bräuchte.

Die zweite (`01_mcp_client.py`) ist der Client. Er:

1. Führt den Handshake (`initialize` senden, Response prüfen).
2. Fragt die Werkzeug-Liste ab (`tools/list`) — und druckt sie.
3. Führt einen Werkzeug-Aufruf aus (`tools/call getSupplierMasterData supplier_id=ACME-42`).
4. Zeigt die Antwort.

Der Server läuft in *derselben* Python-Runtime wie der Client — nicht als subprocess. Das ist eine bewusste Vereinfachung: in der realen Welt würde der Server als eigener Prozess laufen, über stdio- oder HTTP+SSE-Kommunikation. Für die Miniatur reicht es, wenn wir sehen, wie die **Nachrichten aussehen** und die **Registry funktioniert**. Der echte Wire-Format-Punkt bleibt: alles ist JSON-RPC 2.0, alles ist Text, alles ist standardisiert.

### `src/02_a2a_client.py` — der Callable ist ein Agent, kein Werkzeug

A2A ist im Wire-Format praktisch identisch mit MCP — nur dass die Methode `tasks/send` heißt statt `tools/call`, und der Server hat keine explizite Tools-Liste, sondern eine Agent-Beschreibung mit Fähigkeiten.

Die Miniatur simuliert einen A2A-Server, der einen kleinen "Preis-Recherche-Agent" hostet: er nimmt eine natürlichsprachliche Anfrage (*"Was kostet Produkt X in Region Y?"*), macht intern *seinen eigenen* LLM-Loop mit MCP-Werkzeugen, und liefert eine strukturierte Antwort zurück.

Aus Sicht des Clients: **du siehst nur die Anfrage und die Antwort**. Der ganze Loop im Inneren des Agents ist unsichtbar — genauso wie in Kapitel 4 der Thinking-Loop innerhalb eines reasoning-Modells unsichtbar war.

---

## 💡 Wow-Moment

Der wichtigste Moment ist in der ersten Miniatur, bei `tools/list`.

Der Client fragt: *"welche Werkzeuge hast du?"* — und der Server antwortet mit einer JSON-Liste, in der jedes Werkzeug einen Namen, eine Beschreibung und ein JSON-Schema für seine Argumente hat. Genau **dieses JSON-Schema** ist das, was du in Kapitel 2 händisch in den System-Prompt geschrieben hast — nur dass es jetzt vom Server *automatisch* kommt.

Das heißt: **wenn deinem Agent morgen ein neues Werkzeug zur Verfügung stehen soll, änderst du keine Zeile in deinem Loop.** Der Server-Betreiber (das kann eine andere Abteilung, ein externer Anbieter oder ein anderer Agent sein) registriert das Werkzeug in *seinem* Server. Beim nächsten `tools/list`-Aufruf sieht dein Client es. Fertig.

Für einen SAP-Kontext ist das strukturell wichtig: dein Genehmigungs-Agent braucht Zugriff auf Werkzeuge aus MM, FI, SD, HR — jedes davon von einer anderen Fachabteilung gebaut. Ohne MCP: 4 verschiedene Integration-Projekte, 4 verschiedene Adapter, 4 verschiedene Update-Zyklen. Mit MCP: 4 MCP-Server, ein Client, ein `tools/list`-Aufruf.

Und in der A2A-Miniatur siehst du: **wenn der andere Endpunkt nicht ein Werkzeug ist, sondern selbst ein Agent, ändert sich am Protokoll fast nichts**. Der Aufruf sieht identisch aus. Nur was drin passiert, ist völlig anders — ein ganzer Agent-Loop. Aus Sicht deines Codes: derselbe JSON-RPC-Aufruf.

Das ist die Skalierungs-Vermutung, die dem Protokoll zugrunde liegt: **wenn wir alles auf JSON-RPC standardisieren, spielt es keine Rolle mehr, was auf der anderen Seite läuft**. Ein statischer Werkzeug-Server, ein Runtime-generiertes SQL, ein Agent mit reasoning=high, oder eine Kette aus fünf spezialisierten Agents — alles sieht für deinen Client gleich aus.

---

## 🚀 Ausführen

```powershell
cd "C:\Users\<USERNAME>\Source\RPT Agent"

python "Agentic Systems/05_ProtocolsAndScale/src/01_mcp_client.py"
python "Agentic Systems/05_ProtocolsAndScale/src/02_a2a_client.py"
```

Die erste Miniatur ist rein deterministisch (kein LLM) — sie zeigt nur die JSON-RPC-Nachrichten. Die zweite ruft für den simulierten A2A-Agent das LLM auf und braucht deine `.env`-Konfiguration.

---

## 🎁 Bonus-Sektion · `src/a2a/` — der Live-Server mit dem A2A Inspector

Die beiden Miniaturen oben zeigen die **Nachrichten-Form** von MCP und A2A — beide In-Prozess, damit die Struktur der Aufrufe im Vordergrund steht. Wer die Sache *wirklich* über das Netz laufen lassen will, findet unter [`src/a2a/`](src/a2a/) einen eigenständig lauffähigen A2A-Server:

- **`step_g_agent_server.py`** · FastAPI-Server, der den mini-agent aus Kap. 2 (`../02_ToolsAndPlanning/src/mini_agent/step_f_fallback_and_errors.py`) über HTTP + JSON-RPC verfügbar macht. Agent-Card unter `/.well-known/agent-card.json`, `message/send` und `tasks/get` als JSON-RPC-Methoden.
- **`step_h_agent_client.py`** · 60-Zeilen-Client, der ohne SDK die Card holt, eine Nachricht schickt, den Task per ID wieder holt und die Antwort druckt. Jede Request und Response wird gedumpt, damit du das Wire-Format sehen kannst.
- **`demo.ps1` / `demo.sh`** · Ein-Kommando-Demo: startet Server, wartet, feuert Client, druckt Server-Log, beendet sauber. Ideal für Live-Vorträge.
- **A2A Inspector** · Googles Web-UI zum interaktiven Testen. Läuft auf `localhost`, zeigt Chat + rohes JSON-RPC parallel. Details siehe [`src/a2a/README.md`](src/a2a/README.md).

Der springende Punkt: das Agent-Hirn ist unverändert. Alles Neue in `step_g` ist Transport-Code. Wer das ganze Setup Zeile für Zeile lesen will, sieht in ~200 Python-Zeilen alles, was das A2A-Protokoll minimal ausmacht.

---

## 🧭 Brücke zum nächsten Kapitel

Am Ende von Kapitel 5 hast du gesehen: **du kannst fast alles bauen.** Werkzeuge einbinden ist trivial. Agenten aufrufen ist trivial. Der Loop skaliert.

Das führt zu einer neuen Gefahr: **du baust es, obwohl du es nicht solltest.**

Kapitel 6 ist das Urteil. Zwei Miniaturen zeigen, wo Agenten *nicht* das richtige Werkzeug sind — deterministische Aufgaben und Non-Determinismus-Probleme. Kein Framework, keine schöne Bibliothek kann diese Fragen für dich beantworten. Der Zwei-Fragen-Test aus dem Foliensatz wird zur Referenz: **brauchst du Urteilsvermögen zur Laufzeit? Kannst du eine falsche Antwort in zwanzig tolerieren?**

Wenn beide mit Ja beantwortet werden, war der Aufwand aus Kapitel 1-5 gerechtfertigt. Wenn nicht: schreib eine Python-Funktion.
