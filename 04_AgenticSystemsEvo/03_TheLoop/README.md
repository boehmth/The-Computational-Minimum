# Kapitel 3 · Der Loop

**Der eigentliche Agent — und was er kostet.**

Drei Miniaturen. Die erste baut den Loop in ~60 Zeilen Python. Die zweite instrumentiert ihn und zeigt, warum ein 3-Turn-Loop nicht ~3× die Kosten hat, sondern eher ~10×. Die dritte vergleicht vier verschiedene Retry-Strategien und zeigt, wo das Modell selbst zum Fehler-Analysten wird.

---

## 📜 Historischer Kontext

Am Ende von Kapitel 2 stand ein Plan mit einem Platzhalter:

```
step 1: currency_converter(132877 USD -> EUR)
step 2: calculator(divide, <result_from_step_1>, 5.3)
```

Das Modell hatte den Plan verstanden — aber es hatte noch nicht den Wert für den zweiten Schritt. Der Wert entsteht erst, wenn Schritt 1 ausgeführt ist. Das heißt: der Runner muss Schritt 1 ausführen, das Ergebnis dem Modell zurückgeben, und das Modell muss Schritt 2 neu formulieren (mit der jetzt bekannten Zahl statt dem Platzhalter). Das ist ein *Loop*.

**Oktober 2022** — Yao et al. mit dem *ReAct*-Paper (aus Kapitel 2) hatten diesen Loop schon formuliert: `Thought → Action → Observation → Thought → ...`. Der Loop endet, wenn das Modell eine finale Antwort produziert statt einer weiteren Aktion.

**März 2023** — *Auto-GPT* und *BabyAGI* landen als Viral-Repos auf GitHub. Zum ersten Mal sieht die Öffentlichkeit einen Agent, der *mehrere Turns* lang autonom weiterläuft — und dabei manchmal in Endlosschleifen gerät. Beide Repos waren technisch nicht bahnbrechend, aber sie machten dem Publikum klar: **der Loop ist die eigentliche Erfindung**, nicht das Modell. Das Modell ist der Motor. Der Loop ist das Auto.

**Juni 2023** — OpenAI führt *function calling* ein. Wenn du bis dahin einen Agent gebaut hattest, hattest du deinen eigenen JSON-Parser geschrieben. Function calling machte das leichter, aber es machte den *Loop* nicht überflüssig — er wurde nur an einer Stelle einfacher.

Seither ist der Loop in jeder Agent-Bibliothek zu finden: LangChain's `AgentExecutor`, Semantic Kernel's `Planner`, AutoGen's `initiate_chat`, OpenAI's Assistants API. Jede dieser Bibliotheken versteckt genau denselben Loop hinter einer schöneren Schnittstelle. Das erste Skript dieses Kapitels zeigt den Loop nackt — ohne Bibliothek. So verstehst du, was die Bibliotheken für dich tun (und was nicht).

---

## 🔬 Die drei Miniaturen

### `src/01_basic_loop.py` — der Loop in Rohform

Dieselbe Aufgabe wie Kapitel 2 Aufgabe 2: *"Ich habe 132877 USD, wie viele Einheiten zu 5.30 EUR pro Stück kann ich kaufen?"*. Diesmal aber:

- der System-Prompt erwartet **pro Turn ein einziges JSON-Objekt**: entweder ein Werkzeug-Aufruf oder `{"final": "..."}` als Abschluss;
- der Runner (die 60 Zeilen Python) fährt in einer `while`-Schleife, führt jeden Werkzeug-Aufruf aus, hängt das Ergebnis als "observation" an die Konversation und ruft das Modell erneut;
- **drei Stop-Bedingungen sind explizit im Code**: `{"final": ...}` (Erfolg), Turn-Limit (Sicherheitsnetz), same-tool-3-times-in-a-row (Loop-Guard).

Nach 2 oder 3 Turns kommt `{"final": "Du kannst ungefähr 23,073 Einheiten kaufen."}` heraus.

**Was du hier siehst:** einen Agent, der *nichts vom Modell versteckt*. Jede LLM-Antwort wird gedruckt. Jede Parse-Entscheidung ist im Code sichtbar. Jede Stop-Bedingung steht als `if` im Klartext da.

### `src/02_token_growth.py` — was der Loop wirklich kostet

Derselbe Loop, aber mit einer instrumentierten Aufgabe, die 3-4 Werkzeug-Aufrufe braucht. Nach jedem Turn druckt der Runner eine Zeile:

```
Turn 1:   in= 187   out= 34   cumulative= 221 tokens
Turn 2:   in= 265   out= 41   cumulative= 527 tokens
Turn 3:   in= 342   out= 39   cumulative= 908 tokens
Turn 4:   in= 421   out= 62   cumulative=1391 tokens
```

Man sieht sofort: `tokens_in` **wächst mit jedem Turn**, weil die ganze bisherige Konversation (System-Prompt + alle vorherigen Model-Antworten + alle Observations) bei jedem Turn *neu* mitgeschickt werden muss. Der Loop hat kein Gedächtnis auf Modell-Seite — das *Gedächtnis ist der Prompt*.

**Was du hier siehst:** warum LLM-basierte Agenten so viel teurer sind als sie auf den ersten Blick aussehen. Wer 4 Turns rechnet, zahlt nicht das Vierfache eines einzelnen Aufrufs — er zahlt eher das Zehnfache, weil jeder späte Turn eine sehr lange Prompt-Historie tragen muss.

### `src/03_retry_strategies.py` — vier Strategien im direkten Vergleich

Ein simuliertes Werkzeug `flaky_price_lookup(sku)`, das die ersten drei Aufrufe mit HTTP 503 fehlschlägt und beim vierten das richtige Ergebnis liefert. Wir vergleichen vier Retry-Strategien:

- **A · naive** — `sleep(0.5), retry`, fest, ohne Nachdenken
- **B · exponential backoff** — `sleep(0.5, 1, 2, 4)`, klassisch
- **C · circuit breaker** — nach drei Fehlern für eine Cooldown-Periode aussteigen
- **D · LLM-guided recovery** — dem Modell den Fehlertext schicken und fragen *"was jetzt?"*

Jede Strategie wird gegen dieselbe Fehler-Sequenz gefahren. Am Ende druckt das Skript eine Vergleichs-Tabelle:

```
                   Versuche   Latenz     Tokens   Ergebnis
A · naive               4     2.0 s        0      OK
B · exp. backoff        4     7.5 s        0      OK
C · circuit breaker     3     3.5 s        0      Abbruch (ok für "fail fast")
D · LLM-guided          2     4.2 s      340      OK, mit begründetem Wechsel
```

**Was Strategie D besonders macht:** sie ist die einzige, die *versteht*, warum der Fehler passiert. Statt blind zu warten, wird der Fehlertext ans Modell geschickt: *"Die Preis-Suche liefert 503. Was jetzt?"* — und das Modell antwortet mit einer strukturierten Empfehlung: *"Nutze die gecachte Version, oder wechsle auf `fallback_price_lookup(sku)`."* Der Loop hat jetzt eine zweite Rekursions-Ebene: das Modell wird selbst zum Fehler-Diagnostiker.

Preis dafür: ein zusätzlicher LLM-Call pro Fehler. Für seltene, semantisch komplexe Fehler ist das billig. Für Massen-Timeouts wäre es ruinös.

---

## 💡 Wow-Moment

Der wichtigste Moment liegt in Miniatur 3, Strategie D.

Bis zu diesem Punkt in unserer Reihe hat das Modell nur *Aufgaben* gelöst — Multiplikationen, Werkzeug-Auswahl, Plan-Erstellung. In Strategie D löst das Modell zum ersten Mal ein *Problem des Programms selbst*: es analysiert eine Fehlermeldung und empfiehlt eine andere Programm-Aktion.

Das ist qualitativ neu. In Kapitel 4 werden wir sehen, dass moderne Reasoning-Modelle diese Fähigkeit *innerhalb eines einzigen Aufrufs* haben — das Modell "denkt" über seine eigene Antwort nach, bevor es sie ausliefert. Aber die Grundidee ist dieselbe: **das Modell wird zum Meta-Reasoner über seinen eigenen Kontext**. Strategie D ist die einfachste Version davon, die man von Hand bauen kann.

---

## 🚀 Ausführen

```powershell
cd "C:\Users\D041506\Source\RPT Agent"

python "Agentic Systems/03_TheLoop/src/01_basic_loop.py"
python "Agentic Systems/03_TheLoop/src/02_token_growth.py"
python "Agentic Systems/03_TheLoop/src/03_retry_strategies.py"
```

Erwartete Laufzeit: ~30-60 Sekunden pro Skript. Kosten: ~2000-6000 Tokens für Miniatur 1 und 2, ~500 Tokens für Miniatur 3 (weil dort viel simuliert wird).

---

## 🧭 Brücke zum nächsten Kapitel

Was wir in Kapitel 3 gebaut haben, ist ein **externer Loop** — der Loop lebt in unserem Python-Code, jeder Turn ist ein separater HTTP-Aufruf, jede Entscheidung "weiter oder fertig?" trifft *unser* Code.

Ende 2024 kam eine zweite Loop-Sorte in die Welt: der **innere Loop** — der Loop lebt *innerhalb eines einzigen HTTP-Aufrufs*, im Reasoning-Modell selbst. Wir schicken einen Prompt, das Modell "denkt" (produziert einen internen Chain-of-Thought), und wir bekommen zwei Ströme zurück: das Denken und die Antwort.