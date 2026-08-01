 # Milestones in Agentic Systems

**Sieben Meilensteine, die zeigen, wie aus einem Sprachmodell ein autonom handelndes System wird — bis hin zum Agent, der sich seine Werkzeuge selbst schreibt.**

Alles selbst programmiert, ohne Agent-Frameworks. Jeder Prompt, jeder Tool-Call, jede Retry-Entscheidung ist im Code sichtbar. Wenn du Backend-Zugriff auf SAP GenAI Hub hast, laufen alle Beispiele direkt gegen echte Modelle (`gpt-4o`, `anthropic--claude-4.5-sonnet`, o-Serie).

> **🇬🇧 English version:** [`README.en.md`](README.en.md). Every chapter has a parallel `README.en.md` and `EXERCISES.en.md`.

---

## 📜 Warum dieser Teil?

Am Ende von *Milestones in Machine Intelligence* hast du ein winziges GPT-artiges Modell selbst gebaut. Damit hast du **das Fundament** verstanden. Die spannende Frage lautet jetzt: **Was baut man darauf zur Laufzeit?**

Zwischen 2018 (GPT-1) und heute liegen weniger als zehn Jahre — aber der Schritt von *"Modell antwortet auf einen Prompt"* zu *"Modell plant, benutzt Werkzeuge, iteriert, korrigiert sich selbst"* ist qualitativ so groß wie der Schritt vom Perceptron zum Transformer.

Dieser Teil folgt genau dieser Bewegung. In sieben Kapiteln.

Er ist bewusst **kein Ersatz** für [`../03_LanguageModelling/README.md`](../03_LanguageModelling/README.md), sondern dessen systemische Fortsetzung:

- [`03_LanguageModelling/`](../03_LanguageModelling/README.md) fragt: **Wie wurden moderne LLMs trainiert, ausgerichtet und skaliert?**
- [`04_AgenticSystems/`](./README.md) fragt: **Wie werden diese Modelle als Agenten, Tool-Nutzer und Laufzeit-Systeme eingesetzt?**

Wenn Teil 3 die **Innenseite des Modells** beschreibt, beschreibt Teil 4 die **Außenseite des Modells**: Orchestrierung, Werkzeuge, Protokolle, Schleifen, Grenzen.

---

## 🕰️ Historischer Bogen

| Jahr | Ereignis | Kapitel |
|------|----------|---------|
| **1950** | Turing — *Computing Machinery and Intelligence* | **1. Text-in / Text-out** |
| **2018** | Radford (OpenAI) — GPT-1, autoregressives Sprachmodell | |
| **2022 Nov** | ChatGPT — die eine-Prompt-Ära beginnt | |
| **2022 Okt** | Yao et al. — **ReAct**, "reasoning + acting" | **2. Tools & Planning** |
| **2023 Mär** | Schick et al. — **Toolformer**, Modell lernt Tools zu rufen | |
| **2023 Mär** | Auto-GPT, BabyAGI — Loops im öffentlichen Bewusstsein | **3. Der Loop** |
| **2023 Jun** | OpenAI — function calling | |
| **2024 Sep** | OpenAI — **o1**, reasoning-Modelle | **4. Reasoning innen drin** |
| **2025 Feb** | Anthropic — Claude 3.7 extended-thinking | |
| **2025** | DeepSeek-R1 open-weight, RLVR-trainiert | |
| **2024 Nov** | Anthropic — **MCP**, Model Context Protocol | **5. Protokolle & Skalierung** |
| **2025** | Google — **A2A**, Agent-to-Agent Protokoll | |
| — | ...und die praktische Frage: *wann lohnt sich der ganze Aufwand?* | **6. Wann NICHT bauen** |
| **2023 Mai** | Cai et al. — *LLMs as Tool Makers* (LATM) | **7. Dynamic Tool Agent** |
| **2023 Okt** | NVIDIA — **Voyager**, wachsende Skill-Bibliothek in Minecraft | |
| **2025** | Devin · SWE-agent · Claude Code — Runtime-Code-Generierung wird Standard | |

Zehn Jahre — sieben Kapitel — je eine kleine, lauffähige Miniatur.

---

## 🧭 Die sieben Meilensteine

### [`01_TextInTextOut/`](01_TextInTextOut/README.md) — Was ein LLM aus API-Sicht wirklich ist

**Kern:** Die kleinstmöglichen Programme. Ein Sechs-Zeiler `01_hello_llm.py` beweist das erste Prinzip: *ein LLM konsumiert Text und produziert Text — nichts anderes*. Ein zweites Skript `02_math_breaks.py` fragt das Modell nach dem Produkt zweier fünfstelliger Zahlen; das Ergebnis ist plausibel, aber falsch. Python rechnet daneben die Wahrheit.

**Wow-Moment:** Das Modell rät `6,343,522,638` — Python rechnet `634,442,838` — die Differenz ist ~6 Milliarden. Nicht weil das Modell "dumm" ist, sondern weil es Text vorhersagt, nicht rechnet. Diese Erkenntnis motiviert das gesamte restliche Kapitel-Repertoire.

**Brücke:** Wenn Modelle nicht rechnen, aber die Frage rechnen verlangt — wer rechnet dann? → Kapitel 2.

### [`02_ToolsAndPlanning/`](02_ToolsAndPlanning/README.md) — Werkzeuge und der erste Plan

**Kern:** Der Systemprompt beschreibt EIN Werkzeug (Taschenrechner). Das Modell erhält dieselbe Multiplikation wie im Kapitel 1 — und dieses Mal antwortet es nicht mit einer Zahl, sondern mit einem JSON-Objekt, das den Werkzeug-Aufruf beschreibt. Ein tinyer Orchestrator parst das JSON, führt die Deterministik in Python aus, und die Antwort stimmt. Ein zweites Skript zeigt: dasselbe Werkzeugpaar, drei natürlichsprachliche Aufgaben, drei verschiedene Aufrufreihenfolgen — keine davon in Python geschrieben.

**Wow-Moment:** *Same tools, three prompts, three different plans.* Kein Ingenieur hat die Reihenfolge festgelegt. Das ist der Moment, in dem die Kontrolle über den Ablauf vom Entwickler zum Modell wandert.

**Brücke:** Ein Werkzeug-Aufruf ist noch kein Loop. Was passiert, wenn die Aufgabe *mehrere* Werkzeug-Aufrufe braucht? → Kapitel 3.

### [`03_TheLoop/`](03_TheLoop/README.md) — Der externe Loop und was er kostet

**Kern:** Der eigentliche Agent. `while not done: LLM → parse → tool → observe`. In etwa 50 Zeilen Python. Ein zweites Skript instrumentiert den Loop und druckt Turn für Turn die kumulative Token-Zahl — man sieht das Token-Wachstum von 400 auf ~5000 in fünf Turns. Ein drittes Skript vergleicht **vier Retry-Strategien** nebeneinander: naive, exponential backoff, circuit breaker und LLM-guided recovery (das Modell selbst analysiert den Fehler und schlägt die nächste Strategie vor).

**Wow-Moment:** Bei Strategie D wird die Retry-Entscheidung *selbst* zu einem Modell-Aufruf. Der Loop enthält jetzt eine zweite, semantische Rekursions-Ebene: das Modell hilft dem Entwickler dabei, das Modell zu debuggen.

**Brücke:** Der Loop läuft auf einem *nicht-reasoning* Modell (`gpt-4o`). Was ändert sich, wenn das Modell selbst schon einen Loop drin hat? → Kapitel 4.

### [`04_ReasoningInside/`](04_ReasoningInside/README.md) — Der zweite Loop, unsichtbar

**Kern:** Derselbe Prompt, einmal an `gpt-4o` (Baseline, keine Reasoning-Tokens), einmal an `anthropic--claude-4.5-sonnet` mit `thinking={"type":"enabled"}` — beides *ein* HTTP-Aufruf, aber Claude liefert zwei Textströme zurück: einen privaten Thinking-Stream und die finale Antwort. Ein Provider-Matrix-Kasten zeigt, welche Anbieter die Thinking-Tokens im Response überhaupt sichtbar machen (Claude/DeepSeek: ja; OpenAI/Gemini: nur den Zähler in `usage`).

**Wow-Moment:** Aus Sicht des Entwicklers ist es *ein* Aufruf — ein `chat()`, eine `Response`. Aus Sicht des Modells sind es Hunderte autoregressiver Forward-Passes, in denen das Modell seine eigenen frisch generierten Tokens liest. Der Loop hat sich vom Python-Code in die Modell-Architektur zurückgezogen — und dann, in einem dritten Fall, in den Provider-Server (Best-of-N, "reasoning: high").

**Brücke:** Ein Agent allein ist ein Werkzeug. Was, wenn viele Agenten miteinander sprechen sollen — oder wenn deine Werkzeuge zu vielen fremden Modellen offen sein sollen? → Kapitel 5.

### [`05_ProtocolsAndScale/`](05_ProtocolsAndScale/README.md) — MCP und A2A als lauffähige Miniaturen

**Kern:** Zwei kleine ausführbare Beispiele im ~50-Zeilen-Format:

- **Ein minimaler MCP-Server** (Anthropic Model Context Protocol, Nov 2024). Bietet ein Werkzeug `getSupplierMasterData(supplier_id)` per JSON-RPC über stdio an. Ein zweites Skript ist der zugehörige *Client*, der via `tools/list` das Werkzeug entdeckt und via `tools/call` ausführt. Kein Framework, nur `requests` und `json`.
- **Ein A2A-Client** (Google Agent-to-Agent, 2025). Zeigt: derselbe Wire-Format wie MCP, aber der aufgerufene Endpunkt ist selbst ein Agent, kein Werkzeug. Der "Rückrufer" ist eine Konversation, kein einzelner Funktionsaufruf.

**Wow-Moment:** Ein JSON-RPC-Aufruf, drei Zeilen Code, und die Werkzeuge deiner Kollegen (oder eines fremden Anbieters) sind live. Die *N×M*-Integrationskosten der Prä-MCP-Ära (jeder Client × jedes Werkzeug = eine bespoke API) kollabieren zu *N+M*.

**Brücke:** Jetzt können Agenten alles. Also — bauen wir für alles einen Agenten? Nein. → Kapitel 6.

### [`06_WhenNotToBuild/`](06_WhenNotToBuild/README.md) — Das Urteil

**Kern:** Zwei ausführbare Skripte demonstrieren die Anti-Muster:

- `01_agent_vs_sum.py` — baut absichtlich einen Agent für `sum([1,2,3,4,5])`. Vergleicht Latenz, Tokens und Kosten mit der Python-Ein-Zeile. Der Agent ist ~200× langsamer und kostet einige Cent für eine Operation, die 5 Zeichen Code kostet.
- `02_determinism_check.py` — schickt denselben Prompt fünfmal mit `temperature=0` an dasselbe Modell und zeigt, dass die Plan-Sequenz sich zwischen den Läufen unterscheiden kann. Für regulierte Prozesse ist das ein Defekt, kein Feature.

**Wow-Moment:** Der Zwei-Fragen-Test — *"Brauchst du Urteilsvermögen zur Laufzeit? Kannst du eine falsche Antwort in zwanzig tolerieren?"* — als praktisches Entscheidungswerkzeug. Nur wenn beide mit *ja* beantwortet werden, lohnt sich der Aufwand aus Kapitel 3.

**Brücke:** Kapitel 1–6 zeigen die Grundform. Kapitel 7 zeigt den State-of-the-Art im Sommer 2026 — was passiert, wenn nicht mal die Werkzeuge mehr von Menschen kommen?

### [`07_DynamicToolAgent/`](07_DynamicToolAgent/README.md) — Der Agent, der seine eigenen Werkzeuge schreibt

**Kern:** Der Agent hat *keine* fest verdrahteten Werkzeuge mehr. Wenn er für eine Aufgabe ein Werkzeug braucht, das er noch nicht kennt, wählt er per JSON die Aktion `generate_tool` — der Runner ruft daraufhin ein zweites LLM auf, das den Python-Code liefert. Eine AST-Whitelist prüft den Code (keine imports, kein `open`, keine Dunder-Attribute), kompiliert ihn im Sandbox-Namespace und legt ihn in einer Registry ab. Zwei Miniaturen: eine In-Memory-Registry, eine mit Platte-Persistenz.

**Wow-Moment:** Nach 4 Fragen hat der Agent 4 Werkzeuge, die *er selbst geschrieben hat* — als gewöhnliche `.py`-Dateien unter `generated_tools/`. Aber: die Verantwortung wandert nicht mit. Die Sandbox, die Namespace-Definition, die Persistenz-Politik und das Fehlerprotokoll bleiben *dein* Code. Prinzip 3 in seiner härtesten Form.

**Bogen-Ende:** Systeme wie Devin, SWE-agent und Claude Code sind Ausbaustufen genau dieses Musters — mit besseren Sandboxes und echterem Tooling. Wer den Loop dieses Kapitels verstanden hat, kann jedes moderne Code-Agent-System analysieren.

---

## 🧭 Der rote Faden

Jedes Kapitel beantwortet die Frage, die das vorherige aufwirft:

> **Kapitel 1**: Ein LLM konsumiert und produziert Text. → Aber die Antwort ist manchmal falsch.  
> **Kapitel 2**: Gib ihm ein Werkzeug, dann rechnet es Python. → Aber viele Aufgaben brauchen mehrere Werkzeuge.  
> **Kapitel 3**: Bau einen Loop drumherum. → Aber du zahlst mit Tokens und Latenz.  
> **Kapitel 4**: Manche Modelle iterieren intern. → Aber sie ersetzen deinen Loop nicht.  
> **Kapitel 5**: Standardisiere die Werkzeugschnittstelle. → Aber jetzt kannst du "zu viel" bauen.  
> **Kapitel 6**: Weniger ist mehr. Bau nur, wenn P2+P3 sich lohnen.  
> **Kapitel 7**: Lass den Agent seine Werkzeuge selbst schreiben. → Aber Sandbox + Sicherheit wandern *nicht* mit an das Modell.

Am Ende hast du **alle sieben Miniaturen einmal selbst laufen lassen** und kannst dann fundiert entscheiden, wo ein Agent das richtige Werkzeug ist — und wo eine simple Python-Funktion es besser tut.

---

## 📏 Skalierung als der eigentliche Faden

Was der rote Faden oben *inhaltlich* aussagt, lässt sich in einem Wort zusammenfassen: **Skalierung**. Jedes Kapitel skaliert dieselbe Grundidee auf eine neue Ebene, ohne die vorige zu verwerfen.

| Kapitel | Werkzeug-Palette | Wer definiert die Werkzeuge? | Was skaliert? |
|---|---|---|---|
| **1** | keine | — | (nur LLM, kein Werkzeug) |
| **2** | 1 Werkzeug (`calculator`) | Entwickler, zur Design-Zeit | Prinzip: *Trennung Modell / Werkzeug* |
| **2** (Miniatur 2) | 2 Werkzeuge | Entwickler, zur Design-Zeit | *Modell wählt aus einer Menge* |
| **3** | 2 Werkzeuge, im Loop | Entwickler, zur Design-Zeit | *Werkzeug-Aufrufe verketten + Retries* |
| **5** | beliebig viele, über MCP | Fremde Teams, zur Design-Zeit | *Werkzeug-Katalog wächst extern* |
| **7 · M1/M2** | beliebig viele, **runtime-generiert** | Das Modell, zur Laufzeit | *Katalog wächst intern beim Benutzen* |
| **7 · M3** | dito, **plus Selbstheilung** | Modell + Repair-LLM | *Katalog wird auch repariert, wenn er kaputt ist* |

Der Bogen dahinter: *wenn der Calculator ein Werkzeug sein kann, kann alles ein Werkzeug sein. Wenn eine feste Menge funktioniert, kann eine dynamische Menge funktionieren. Wenn Runtime-generierter Code kaputt sein kann, muss auch die Reparatur Runtime sein — mit demselben LLM-Muster.* Kapitel 7 · Miniatur 3 ist daher kein neuer Bauplan, sondern die letzte Rekursion: der Retry aus Kapitel 3, angewandt auf den vom Modell selbst geschriebenen Code.

---

## 🚀 Schnelleinstieg

Voraussetzung: du bist im Root von `The-Computational-Minimum`, hast die `.env` ausgefüllt und den passenden Service-Key bzw. API-Zugang konfiguriert. Die projektweiten Hinweise stehen im Haupt-Repo; teil-spezifische Abhängigkeiten liegen in [`requirements.txt`](requirements.txt).

```powershell
cd "C:\Users\thilo\Source\repos\The-Computational-Minimum\04_AgenticSystems"

# Kapitel 1
python "01_TextInTextOut/src/01_hello_llm.py"
python "01_TextInTextOut/src/02_math_breaks.py"

# Kapitel 2
python "02_ToolsAndPlanning/src/01_give_it_a_tool.py"
python "02_ToolsAndPlanning/src/02_model_plans.py"

# Kapitel 3
python "03_TheLoop/src/01_basic_loop.py"
python "03_TheLoop/src/02_token_growth.py"
python "03_TheLoop/src/03_retry_strategies.py"

# Kapitel 4
python "04_ReasoningInside/src/01_thinking_visible.py"

# Kapitel 5
python "05_ProtocolsAndScale/src/01_mcp_client.py"
python "05_ProtocolsAndScale/src/02_a2a_client.py"

# Kapitel 6
python "06_WhenNotToBuild/src/01_agent_vs_sum.py"
python "06_WhenNotToBuild/src/02_determinism_check.py"

# Kapitel 7
python "07_DynamicToolAgent/src/01_dynamic_tool_agent.py"
python "07_DynamicToolAgent/src/02_dynamic_tool_agent_persisted.py"
```

---

## 📖 Wie du diesen Teil durcharbeitest

1. Lies das Vorwort ([`PREFACE.md`](PREFACE.md)) — es ordnet die sieben Meilensteine ein.
2. Beginne mit Kapitel 1. Die README dort erklärt den historischen Kontext, dann führe die Skripte in `src/` aus.
3. Am Ende jedes Kapitels stehen **Übungen** in `EXERCISES.md` — sie sind das eigentliche Lehr-Werkzeug, weil sie zwingen, das Beispiel *zu variieren*.
4. Kapitel 5 (MCP + A2A) ist der einzige Punkt, an dem du zusätzliche Prozesse startest. Die anderen Kapitel sind reine Ein-Skript-Miniaturen.

---

## 🧠 Was dieser Teil bewusst nicht zeigt

- **Kein Framework**. Kein LangChain, kein Semantic Kernel, kein AutoGen, kein LlamaIndex. Alle Loops, alle Parser, alle Retry-Policies stehen im Klartext im Skript. Das ist unbequem — genau deshalb machen wir es. Ein Framework verbirgt genau die Verantwortungen, die dieser Teil sichtbar machen will (siehe Principle 3 unten).
- **Kein UI**. Alles läuft im Terminal. Wenn du das Ergebnis "hübsch" willst, ist das ein hervorragendes Übungsprojekt für Kapitel 5.
- **Keine Persistenz**. Kein RAG, kein Vector-Store, keine Chat-Historie über mehrere Sessions. Das sind sinnvolle nächste Schritte, aber nicht Meilensteine — sie sind Anwendungen der Meilensteine.

---

## 🧭 Die drei Prinzipien, die alle Kapitel tragen

Dieses Repo hat einen Zwilling: ein Foliensatz mit dem Titel *"Why Agents, and Why Now"*, der dieselbe Geschichte für ein weniger technisches Publikum erzählt. Aus ihm stammen die drei Prinzipien, die durch alle Kapitel laufen:

> **P1 · Was ein LLM ist** — Es konsumiert Text und produziert Text. Nichts anderes.  
> **P2 · Was ein Agent ist** — Das Modell entscheidet die Schritte zur Laufzeit. Nicht der Entwickler, nicht im Voraus.  
> **P3 · Was der Entwickler schuldet** — Alles rund um das Modell ist dein Code.

Jedes Kapitel ist eine Auswirkung eines dieser drei Prinzipien.

---

## 📜 Lizenz und Nutzung

Frei für den Bildungsgebrauch. Beiträge, Übersetzungen und Ergänzungen sind willkommen.
