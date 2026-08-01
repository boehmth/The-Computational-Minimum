# Kapitel 7 · Der Agent, der seine eigenen Werkzeuge schreibt

**Wenn das Modell nicht nur entscheidet, *welches* Werkzeug es benutzt, sondern das Werkzeug bei Bedarf *neu erschafft* — was ändert sich dann am Prinzip 3?**

Drei Miniaturen, jede eine Ausbaustufe der gleichen Idee. Der Agent hat **keine fest verdrahteten Werkzeuge** mehr. Wenn er für eine Aufgabe ein Werkzeug braucht, das er noch nicht kennt, lässt er sich den Python-Code dafür von einem zweiten LLM-Aufruf generieren, validiert ihn (AST-Whitelist + eingeschränkte Builtins), führt ihn aus und legt ihn in einer Registry ab — für spätere Aufgaben. Die zweite Ausbaustufe persistiert die generierten Tools auf Platte, sodass sie über Programm-Läufe hinweg erhalten bleiben. Die dritte Ausbaustufe repariert den generierten Code selbst, wenn er kaputt ist — mit einem spezialisierten Repair-LLM-Aufruf.

Am Ende hat dein Agent nach 4 Fragen 4 neu geschriebene Werkzeuge in seiner Registry, die er beim nächsten Mal *nicht mehr neu generieren muss*. Und eine dritte Miniatur zeigt: **wenn der generierte Code kaputt ist, lässt der Agent ihn von einem weiteren LLM-Aufruf reparieren** — dieselbe LLM-guided-Recovery-Idee aus Kap. 3, nur eine Ebene tiefer.

> **Slide-Anker im Foliensatz:** Slides **45** (*"Where agents are heading — from tool users to tool makers: Fixed tools → Generated tools → Self-extending capability"*) und **46** (*"How this deck was made"* — der Foliensatz selbst wurde von Cline gebaut, dem Agenten, der zur Laufzeit Werkzeuge generiert). Kapitel 7 ist die kleinstmögliche ehrliche Miniatur der mittleren Stufe: ein Agent, der zwischen "Fixed tools" (Kap. 1–6) und "Self-extending" (Devin, SWE-agent) sitzt.

---

## 📏 Skalierung als roter Faden

Bevor die Miniaturen im Detail beschrieben werden, lohnt es sich, kurz *einen einzigen Punkt* aus dem Repo herauszuziehen: **jede Erweiterung bisher war eine Skalierung derselben Grundidee.**

| Kapitel | Werkzeug-Palette | Wer definiert die Werkzeuge? | Was skaliert? |
|---|---|---|---|
| **1** | keine | — | (nur LLM, kein Werkzeug) |
| **2** | 1 Werkzeug (`calculator`) | Entwickler, zur Design-Zeit | Prinzip: *Trennung Modell/Werkzeug* |
| **2** (Miniatur 2) | 2 Werkzeuge (`calculator` + `currency_converter`) | Entwickler, zur Design-Zeit | *Modell wählt aus Menge* |
| **3** | 2 Werkzeuge, im Loop | Entwickler, zur Design-Zeit | *Werkzeug-Aufrufe verketten* |
| **5** | beliebig viele, über MCP | Fremde Teams, zur Design-Zeit | *Werkzeug-Katalog wächst extern* |
| **7 · M1/M2** | beliebig viele, **runtime-generiert** | Das Modell, zur Laufzeit | *Katalog wächst intern beim Benutzen* |
| **7 · M3** | dito, **plus Selbstheilung** | Das Modell + ein Repair-LLM | *Katalog wird auch repariert, wenn er kaputt ist* |

Der Bogen lautet: *Wenn der Calculator ein Werkzeug sein kann, dann kann alles ein Werkzeug sein.* Und *wenn eine feste Menge von Werkzeugen funktioniert, kann eine dynamische Menge funktionieren.* Und *wenn ein Runtime-generiertes Werkzeug kaputt sein kann, dann muss die Reparatur auch Runtime sein — mit demselben LLM-Muster wie in Kap. 3.*

Das ist der eigentliche Wert von Kap. 7: nicht die Neuheit der Werkzeug-Generierung, sondern das Wiedererkennen. **Kap. 7 ist Kap. 3 mit Werkzeugen auf beiden Ebenen** — beim Aufrufen *und* beim Erzeugen.

---

## 📜 Historischer Kontext

Die sechs vorigen Kapitel folgten einem klaren Bogen: das Modell nutzt Werkzeuge, die *du* geschrieben hast. Kapitel 2 (`calculator`, `currency_converter`). Kapitel 3 (Loop, der die vorhandenen Werkzeuge orchestriert). Kapitel 5 (fremde Werkzeuge über MCP). Immer: **Werkzeuge sind statisch, der Loop ist dynamisch.**

Ab 2024 begann eine kleine, aber folgenreiche Verschiebung. In der Reihenfolge:

- **März 2023** · Cai, Chen et al. — *"Large Language Models as Tool Makers"* (LATM, arXiv:2305.17126). Ein "Tool-Maker"-Modell schreibt wiederverwendbare Python-Funktionen für einen "Tool-User"-Agenten. Erstmals wird die Werkzeug-Bibliothek zur Laufzeit gebaut, nicht vorab.
- **Ende 2023** · Voyager (Wang et al., NVIDIA/Caltech) demonstriert dasselbe Prinzip in Minecraft: ein LLM-Agent, der sich sein Skill-Repertoire beim Spielen selbst schreibt — und dessen Skill-Bibliothek nach 200 Stunden Spielzeit mehr Fähigkeiten enthält als der Basis-Agent je hatte.
- **2024** · Code-Interpreter-artige Systeme werden Mainstream (OpenAI Advanced Data Analysis, Claude Code, Cursor-Agenten). Alle teilen dieselbe Struktur: das Modell schreibt Code, der Runner führt ihn aus, das Ergebnis fließt zurück ins nächste Modell-Turn.
- **2025** · State-of-the-Art-Agenten (Devin, SWE-agent, Claude Code) generieren zur Laufzeit ganze Sub-Programme, nicht mehr nur einzelne Tool-Calls. Der Unterschied zwischen *"das Modell benutzt Werkzeuge"* und *"das Modell schreibt Software"* verschwimmt.

Dieses Kapitel zeigt die kleinste ehrliche Version davon: **ein Agent, dessen Werkzeuge Runtime-generierter Python-Code sind**. Kein Framework. ~450 Zeilen inklusive Sandbox und Persistenz.

---

## 🔬 Die drei Miniaturen

### `src/01_dynamic_tool_agent.py` — der Agent generiert seine Werkzeuge zur Laufzeit

Der Kern-Loop hat drei mögliche Aktionen pro Turn, jede als JSON:

```json
{"action": "generate_tool", "tool_name": "...",  "tool_description": "..."}
{"action": "call_tool",     "tool_name": "...",  "tool_args": {...}}
{"action": "final_answer",  "answer": "..."}
```

Der Ablauf für eine typische Aufgabe (*"Ist 97 eine Primzahl?"*):

1. **Turn 1** — Der Agent sieht: Registry ist leer, es gibt kein `is_prime`. Er antwortet mit `generate_tool` und liefert Name (`is_prime`) und eine präzise Beschreibung.
2. **Zwischenschritt** — Der Runner schickt Name + Beschreibung an einen *zweiten* LLM-Aufruf (mit einem ganz eigenen System-Prompt für Code-Generierung), bekommt Python-Code zurück, prüft ihn via AST-Whitelist, kompiliert ihn im Sandbox-Namespace und legt die Funktion in der Registry ab.
3. **Turn 2** — Der Agent sieht jetzt: `is_prime` ist verfügbar. Er antwortet mit `call_tool`, `tool_args={"n": 97}`.
4. **Zwischenschritt** — Der Runner ruft die frisch registrierte Funktion auf, bekommt `True` zurück, hängt das Ergebnis an die Historie.
5. **Turn 3** — Der Agent antwortet mit `final_answer`: *"Ja, 97 ist eine Primzahl."*

Für die *nächste* Frage, wenn sie wieder ein `is_prime`-artiges Werkzeug braucht, überspringt der Agent Schritt 1-2 und geht direkt zu `call_tool` — das Werkzeug ist ja schon da.

### `src/02_dynamic_tool_agent_persisted.py` — die Werkzeuge überleben den Prozess

Dieselbe Logik, plus eine Registry, die jedes registrierte Tool zusätzlich als `.py`-Datei unter `src/generated_tools/` schreibt, mit einer `index.json` als Metadaten. Beim nächsten Programm-Start lädt die Registry alle vorhandenen Tools von Platte — und validiert sie **erneut** über dieselbe AST-Whitelist. Das ist bewusst wichtig: wenn jemand die Dateien zwischen zwei Läufen manuell verändert hat, greift die Sicherheitsprüfung trotzdem.

Das Ergebnis: nach ein paar Läufen hat dein Agent eine kleine, wachsende Bibliothek an Werkzeugen, die er sich selbst geschrieben hat. Du kannst sie im Ordner `generated_tools/` anschauen und feststellen: das ist gewöhnlicher Python-Code. Zum Beispiel `is_prime.py`:

```python
def is_prime(n: int) -> bool:
    if not isinstance(n, int):
        raise ValueError("n must be an int")
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True
```

Kein magischer Wrapper. Kein Framework-Objekt. Nur eine Funktion, die das Modell geschrieben hat und die der Runner beim nächsten Start wieder einliest.

### `src/03_dynamic_tool_agent_self_healing.py` — der Agent repariert den kaputten Code

In Miniatur 1 und 2 gibt der Agent auf, wenn der generierte Code die AST-Validierung nicht besteht oder zur Laufzeit eine Exception wirft. Das ist die pädagogisch ehrlichste Version — es macht sichtbar, dass Fehler passieren. Aber es ist nicht das, was moderne Code-Agenten wie Cline oder Claude Code tun. Die machen etwas Konkreteres: sie **rufen ein weiteres LLM** mit einem Repair-Prompt auf, der den fehlerhaften Code plus die Fehlermeldung sieht, und lassen sich eine korrigierte Version geben.

Genau das steckt in `SelfHealingToolRegistry`. Ein Beispiel aus einem Lauf mit `temperature=0.2`:

```
[Schritt 1] 'Ich brauche ein Werkzeug für Median.' -> action=generate_tool
    -> generiere Tool-Code für 'median_of_list' ...
    -> Tool 'median_of_list' registriert (auf Anhieb korrekt).
[Schritt 2] -> action=call_tool
    -> Ergebnis von 'median_of_list({'values': [3, 1, 4, ...]})': 4.0

[Schritt 3] 'Ich brauche ein Mittelwert-Werkzeug für die zweite Liste.'
             -> action=generate_tool
    -> generiere Tool-Code für 'arithmetic_mean' ...
    -> Tool 'arithmetic_mean' registriert.
[Schritt 4] -> action=call_tool  (mit leerer Liste!)
    [repair] Runtime-Fehler in 'arithmetic_mean': ZeroDivisionError: division by zero
    [repair] Versuch 1/2 -- rufe Repair-LLM...
    -> Neuer Code registriert (jetzt mit if not values: raise ValueError...)
    -> Ergebnis: ValueError: 'arithmetic_mean' benötigt eine nicht-leere Liste
```

Zwei Punkte zum Anschauen:

1. **Die Retry-Politik lebt in der Registry, nicht im Agent-Loop.** Der Agent-Code aus Miniatur 1 wird unverändert wiederverwendet. Genau wie in Kap. 3, wo `03_retry_strategies.py` zeigt, dass eine Retry-Strategie ein austauschbares Modul ist — nicht ein fest verdrahtetes `try/except` mitten im Loop. Prinzip 3 in sauberer Form.
2. **Der Repair-Prompt ist ein *separater* System-Prompt.** Nicht dasselbe LLM mit derselben Rolle wie beim ersten Wurf, sondern ein spezialisierter Debugger-Prompt, der Name, Beschreibung, Code und Fehlermeldung bekommt. Das ist genau die "LLM-guided Recovery"-Strategie aus Kap. 3, hier auf den Sonderfall "kaputter generierter Code" spezialisiert.

Nach dem Repair-Loop gibt es dann drei mögliche Endzustände:

- **Erfolg** — der reparierte Code besteht die Validierung, läuft, gibt einen sinnvollen Wert zurück. Der neue Code ersetzt die alte Version in der Registry und wird auf Platte persistiert.
- **Aufgabe** — nach `max_repair_attempts` (Default 2) reißt der Repair-Loop ab und wirft die letzte Exception nach oben durch. Der Agent-Loop sieht dann eine normale `ToolCodeError`-/Runtime-Fehler-Meldung und muss selbst entscheiden, was er tut (meist: `final_answer` mit "leider ging das nicht").
- **`ValueError` durchgelassen** — wenn das Tool bewusst per `raise ValueError` seine Eingabe zurückweist (das gehört zum Contract, siehe `TOOL_GENERATOR_SYSTEM_PROMPT`), gilt das nicht als Bug. Die Registry lässt den Wurf durch und der Agent sieht ihn als normale Fehler-Observation — genau wie in Kap. 3 den Fehler eines statischen Tools.

Die Zeile, die die Rekursion greifbar macht, steht im Docstring des Skripts:

> *In Kap. 3 haben wir vier Retry-Strategien verglichen: naive, exponential backoff, circuit breaker, LLM-guided recovery. Genau die letzte Strategie wiederholt sich hier eine Ebene tiefer: das LLM debuggt seinen eigenen generierten Code. Das ist keine neue Idee — es ist die Rekursion von Kap. 3 auf Kap. 7.*

---

## 💡 Wow-Moment

Der wichtigste Moment ist nicht die Code-Generierung selbst — das ist inzwischen Standard-Repertoire jedes fähigen Modells. Der wichtige Moment ist die **Rekursion des Prinzips 3**.

> Prinzip 3 sagt: *alles rund um das Modell ist dein Code.*

In Kapitel 2 hieß das: der Parser ist dein Code, der Dispatcher ist dein Code, die Werkzeug-Implementierung ist dein Code.

In Kapitel 3 hieß das: der Loop ist dein Code, die Retry-Policy ist dein Code, die Stop-Bedingung ist dein Code.

In diesem Kapitel wird ein Stück *"dein Code"* zur Laufzeit vom Modell selbst geschrieben. **Aber die Verantwortung wandert nicht mit.** Was du weiterhin schreiben musst:

- Die **Sandbox** (`_validate_tool_ast`) — welche Sprach-Konstrukte sind erlaubt, welche verboten?
- Die **Namespace-Definition** (`ALLOWED_BUILTINS`, `ALLOWED_MODULES`) — was darf der generierte Code sehen?
- Die **Persistenz-Politik** — was wird auf Platte geschrieben, was gelöscht, was beim Start neu validiert?
- Das **Fehlerprotokoll** — was passiert, wenn der generierte Code die Validierung nicht besteht, eine Exception wirft, oder Unsinn zurückgibt?

Genau diese vier Verantwortungen sind der Grund, warum wir mit einer *engen* Sandbox anfangen (nur `math`, `re`, `statistics`, `datetime`; keine imports, kein `open`, kein `eval`). Sie sind nicht schön, aber sie sind der Preis dafür, dass man dem generierten Code trauen kann, während er im selben Python-Prozess wie der Agent läuft.

Das Kapitel-Skript sagt es im Docstring selbst deutlich:

> *Dynamisch generierten Code auszuführen ist grundsätzlich riskant. Die Validierung hier (AST-Whitelist + eingeschränkte Builtins) ist eine didaktische Annäherung, KEIN Ersatz für ein echtes Sandboxing (z. B. Subprozess mit Ressourcenlimits, WASM-Sandbox, RestrictedPython o. Ä.).*

Das ist Prinzip 3 in seiner härtesten Form. Das Framework, das dir das abnimmt, gibt es nicht — beziehungsweise: die Frameworks, die es *versuchen* (LangChain-`PythonREPLTool`, `LlamaIndex`-CodeInterpreter, Anthropics `computer_use`), verstecken die Politik nur, sie machen sie nicht sicher.

---

## ⚠️ Sicherheit — was diese Miniatur bewusst *nicht* tut

Zur Erinnerung, kurz und ehrlich:

- **Kein Prozess-Isolation.** Der generierte Code läuft im selben Python-Interpreter wie der Runner. Ein Ausbruch aus der AST-Whitelist würde reichen, um den Agent-Prozess zu übernehmen.
- **Keine Ressourcen-Limits.** Ein generiertes `while True: pass` wird den Agenten aufhängen. Kein Timeout, keine CPU-Grenze.
- **Kein Netzwerk-Schutz** außerhalb der Whitelist. Wir verlassen uns darauf, dass `socket`, `urllib`, `requests` in `FORBIDDEN_NAMES` stehen — das ist Verbieten-per-Namen, nicht Verbieten-per-Fähigkeit. Ein raffinierter generierter Code könnte über Umwege daran vorbei.
- **Keine formale Verifikation.** Wir prüfen die *Form* des Codes (AST), nicht seine *Semantik*. Ein syntaktisch harmloses `for i in range(10**12)` erfüllt die Whitelist und legt trotzdem den Prozess lahm.

Wenn du das Muster produktiv nutzen willst, ersetze `compile_tool()` durch einen echten Isolations-Mechanismus:

- **Subprozess** mit `resource.setrlimit` (CPU-Zeit, Speicher, Datei-Deskriptoren) und Kommunikation über JSON auf stdin/stdout — die einfachste ehrliche Antwort.
- **`RestrictedPython`** (Zope-Ökosystem) mit denselben Modul-Whitelists — mehr Bibliothek, weniger eigener Code.
- **WASM-Sandbox** (Wasmer, Wasmtime) mit einem Python-nach-WASM-Compiler wie Pyodide — echtes Prozess-Isolat mit Speicher-Grenze.
- **Container pro Aufruf** (Firecracker, gVisor) — die Enterprise-Antwort, mit Millisekunden-Kaltstart.

Die didaktische Version hier existiert, damit du siehst, *welche* Fragen ein Sandbox-Design überhaupt beantworten muss. Sobald du das siehst, wird die Wahl zwischen den vier Optionen oben zu einer nüchternen Kosten-/Sicherheits-Rechnung — statt zu einem "das kann doch nicht so schwer sein"-Bauchgefühl.

---

## 🚀 Ausführen

Voraussetzung: `.env` konfiguriert (siehe `../README.md`) und die Standard-Abhängigkeiten aus `../requirements.txt` installiert.

```powershell
cd "C:\Users\D041506\Source\Agentic Systems"

# Miniatur 1 — In-Memory-Registry, jedes Mal frisch
python "07_DynamicToolAgent/src/01_dynamic_tool_agent.py"

# Miniatur 2 — Persistente Registry, Tools überleben den Prozess
python "07_DynamicToolAgent/src/02_dynamic_tool_agent_persisted.py"
# Beim zweiten Aufruf siehst du: "[Persistenz] Geladen: 'is_prime'"
# und der Agent überspringt die Code-Generierung.

# Miniatur 3 — Selbstheilend: Repair-LLM bei kaputtem generierten Code
python "07_DynamicToolAgent/src/03_dynamic_tool_agent_self_healing.py"
# Die dritte Beispiel-Aufgabe (Mittelwert einer leeren Liste) triggert
# üblicherweise den Repair-Loop — du siehst "[repair]"-Zeilen mit dem
# Fehler-Typ und dem korrigierten Code.
```

Erwartete Ausgabe für Miniatur 1 (erste der vier Beispiel-Fragen):

```
FRAGE: Was ist 12345 * 6789?
[Schritt 1] 'Ich brauche ein Multiplikationswerkzeug' -> action=generate_tool
    -> generiere Tool-Code für 'multiply_integers' ...
    -> Tool 'multiply_integers' registriert:
def multiply_integers(a: int, b: int) -> int:
    if not isinstance(a, int) or not isinstance(b, int):
        raise ValueError("a und b müssen ganze Zahlen sein")
    return a * b

[Schritt 2] 'Tool ist da, jetzt aufrufen' -> action=call_tool
    -> Ergebnis von 'multiply_integers({'a': 12345, 'b': 6789})': 83810205
[Schritt 3] 'Ergebnis vorhanden, antworten' -> action=final_answer
ANTWORT: 12345 * 6789 ergibt 83.810.205.
```

Nach allen vier Beispielen listet der Runner die Registry:

```
Am Ende registrierte Tools:
- multiply_integers: multipliziert zwei ganze Zahlen
- miles_to_meters:   konvertiert Meilen in Meter
- is_prime:          prüft, ob eine ganze Zahl >= 2 eine Primzahl ist
- factorial:         berechnet die Fakultät einer nichtnegativen ganzen Zahl
```

Vier Aufgaben → vier selbst geschriebene Werkzeuge, alle zur Wiederverwendung bereit.

---

## 🧭 Wo dieses Kapitel im Bogen steht

Der historische Bogen der ersten sechs Kapitel war:

> Kapitel 1: das Modell antwortet. → Aber die Antwort ist falsch.
> Kapitel 2: gib ihm ein Werkzeug. → Aber die Werkzeuge sind statisch.
> Kapitel 3: bau einen Loop. → Aber der Loop kostet Tokens.
> Kapitel 4: manche Modelle iterieren intern. → Aber sie ersetzen den Loop nicht.
> Kapitel 5: standardisiere die Werkzeug-Schnittstelle. → Aber die Werkzeuge kommen weiter von Menschen.
> Kapitel 6: das Urteil — nicht alles ist ein Agent.

**Kapitel 7 fragt: was, wenn nicht mal mehr die Werkzeuge von Menschen kommen müssen?**

Die Antwort dieses Kapitels ist zweigeteilt:

1. **Ja, das geht** — das Modell kann sich seine Werkzeuge selbst schreiben, und die Registry wächst mit jeder Aufgabe.
2. **Aber der Preis wandert nach unten** — jede Zeile, die früher ein Menschen-geschriebenes Werkzeug validiert hätte (Code-Review, Tests, Type-Checker), musst du jetzt durch Sandbox-Politik ersetzen. Und die Sandbox ist strenger als jeder Code-Review es je sein könnte, weil sie über beliebigen unbekannten Code entscheiden muss.

Das ist der State-of-the-Art im Sommer 2026. Systeme wie Devin, SWE-agent, Claude Code sind Ausbaustufen genau dieses Musters — mit besseren Sandboxes, mit echtem Tooling (git, filesystem, browser), mit mehreren zusammenwirkenden Agent-Rollen. Aber der Kern-Loop ist dieser hier.

Wenn du diesen Loop verstanden hast — die drei Aktionen, die Registry, die Sandbox — hast du das begriffliche Werkzeug in der Hand, um jedes moderne Code-Agent-System zu analysieren. Der Rest ist Engineering.
