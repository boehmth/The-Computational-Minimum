# Kapitel 2 · Werkzeuge und der erste Plan

**Wie die Kontrolle über den Ablauf zur Laufzeit vom Entwickler ans Modell wandert.**

Zwei Miniaturen. Die erste zeigt einen einzelnen Werkzeug-Aufruf. Die zweite zeigt drei Aufgaben und drei unterschiedliche Aufruf-Reihenfolgen — keine davon in Python geschrieben.

---

## 📜 Historischer Kontext

Im Oktober 2022 veröffentlichten Yao et al. das Paper *"ReAct: Synergizing Reasoning and Acting in Language Models"* (arXiv:2210.03629). Der Titel klingt heute nach etwas Selbstverständlichem — der Inhalt war seinerzeit provokant:

Das damalige Standard-Modell war *"prompt in, answer out"*. Man gab dem Modell ein Chain-of-Thought-Beispiel und bekam am Ende eine Antwort. Das Modell entschied nichts. Es rechnete oder tat so, als würde es rechnen.

ReAct schlug vor: **das Modell soll zwischen Gedanken und Aktionen unterscheiden.** Ein Aktion-Token bedeutet einen Werkzeug-Aufruf. Das Modell produziert Gedanken (`Thought:`), dann eine Aktion (`Action: search[Milch]`), dann liest der Runner die Observation zurück (`Observation: 3,20 EUR`), dann kommen mehr Gedanken. Der Loop entsteht.

Fünf Monate später (März 2023) veröffentlichte Meta das *Toolformer*-Paper (arXiv:2302.04761): Modelle können lernen, *selbst zu entscheiden, wann* sie ein Werkzeug rufen. Und wieder drei Monate später (Juni 2023) veröffentlichte OpenAI *function calling* — die erste kommerzielle API, die eine JSON-Schema-basierte Werkzeug-Schnittstelle einbaute.

Zwei zusammenhängende Beobachtungen aus dieser Zeit:

1. **Werkzeug-Nutzung braucht keine spezielle Modell-Architektur.** Jedes fähige Sprachmodell kann Werkzeuge nutzen, wenn man ihm im System-Prompt erklärt, wie das Werkzeug heißt und wie der Aufruf aussieht. Function calling ist bequemer, aber nicht notwendig.
2. **Die Kontrolle über den Ablauf wandert.** In der Prä-ReAct-Ära entschied der Entwickler jede Verzweigung, jede Schleife. Nach ReAct entscheidet das Modell zur Laufzeit — welches Werkzeug, mit welchen Argumenten, in welcher Reihenfolge. Das ist der eigentliche Umbruch, der uns hierher gebracht hat.

Diese beiden Beobachtungen liegen den beiden Miniaturen zugrunde.

---

## 🔬 Die zwei Miniaturen

### `src/01_give_it_a_tool.py` — der erste Werkzeug-Aufruf

Wir nehmen dieselbe Multiplikation wie im vorigen Kapitel (`43,177 × 14,694`). Diesmal steht im System-Prompt: *"Du hast ein Werkzeug namens `calculator`. Um es zu benutzen, antworte ausschließlich mit einem JSON-Objekt."*

Das Modell antwortet nicht mit einer Zahl. Es antwortet mit:

```json
{"tool": "calculator", "operation": "multiply", "a": 43177, "b": 14694}
```

Ein tinyer Orchestrator (10 Zeilen Python im selben Skript) parst das JSON, ruft die Python-Funktion `calculator(...)` auf, und die Antwort stimmt.

**Was passiert hier eigentlich?** Zwei getrennte Verantwortungen:

- **Das Modell** identifiziert die Absicht (*hier muss multipliziert werden*) und produziert die strukturierte Repräsentation (*JSON mit den richtigen Argumenten*). Das ist Sprach-Arbeit.
- **Der Code** parst die Struktur und führt die Deterministik aus. Das ist Rechen-Arbeit.

Das ist die Trennlinie, die alles Weitere trägt. Der Fehler aus Kapitel 1 ist verschwunden. Nicht weil das Modell besser rechnet — sondern weil das Modell nicht mehr rechnet.

### `src/02_model_plans.py` — drei Aufgaben, drei Pläne

Wir erweitern das Werkzeug-Set um ein zweites: `currency_converter(betrag, quelle, ziel)`. Beide Werkzeuge sind im System-Prompt beschrieben. Dann stellen wir dem Modell drei natürlichsprachliche Aufgaben:

- *"Was ist der Gesamtpreis für 43,177 Einheiten zu je 14,694 EUR?"*
- *"Ich habe 132,877 USD Budget, wie viele Einheiten kann ich zu 5.3 EUR pro Stück kaufen?"*
- *"Was ist der Gesamtpreis in EUR für 43,177 Einheiten zu je 14,694 USD?"*

Das Modell produziert für jede Aufgabe einen *Plan* — eine geordnete Liste von Werkzeug-Aufrufen:

- Aufgabe 1 → `[calculator(multiply, 43177, 14694)]`
- Aufgabe 2 → `[currency_converter(132877, USD, EUR), calculator(divide, ..., 5.3)]`
- Aufgabe 3 → `[calculator(multiply, 43177, 14694), currency_converter(..., USD, EUR)]`

**Drei Aufgaben, dasselbe Werkzeug-Set, drei völlig unterschiedliche Aufruf-Reihenfolgen.** Kein `if/elif` in unserem Code. Der Entwickler hat *nicht* geschrieben "wenn USD in der Frage vorkommt, dann konvertiere". Das Modell hat sich das selbst ausgedacht — für jede Aufgabe neu.

---

## 💡 Wow-Moment

Genau das ist Prinzip 2 in Aktion:

> **Das Modell entscheidet die Schritte zur Laufzeit. Nicht der Entwickler, nicht im Voraus.**

Vor 2023 hättest du für Aufgabe 2 vs. Aufgabe 3 zwei verschiedene Handler geschrieben (oder einen mit einem Verzweigungsbaum). Nach ReAct schreibst du eine Werkzeug-Beschreibung — und dieselbe Beschreibung, unverändert, deckt beide Aufgaben ab. Das Modell figuriert die Reihenfolge selbst aus.

Was du dabei verlierst: **Vorhersagbarkeit**. Beim nächsten Lauf könnte das Modell für Aufgabe 3 einen anderen Plan wählen — zum Beispiel zuerst den Einzelpreis in EUR umrechnen und dann multiplizieren. Beide Pläne sind mathematisch korrekt, aber sie sind nicht *derselbe* Plan. Das ist der Kompromiss, den man mit P2 einkauft, und der wird in Kapitel 6 zur Sprache kommen (Determinismus, Replay, Audit).

Was du gewinnst: **Anpassungsfähigkeit an neue Aufgaben, ohne Code-Änderung**. Wenn morgen jemand kommt und fragt *"Was ist der Gesamtpreis in USD für 43,177 Einheiten zu je 5.3 EUR?"* — das ist eine vierte Aufgabe, und dein Code funktioniert dafür schon. Ohne dass irgendjemand `if usd_target:` schreibt.

---

## 🚀 Ausführen

```powershell
cd "C:\Users\D041506\Source\RPT Agent"

python "Agentic Systems/02_ToolsAndPlanning/src/01_give_it_a_tool.py"
python "Agentic Systems/02_ToolsAndPlanning/src/02_model_plans.py"
```

Erwartete Ausgabe von `02_model_plans.py` (dein Modell wird leicht andere Formulierungen wählen, aber die *Struktur* wird passen):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    AUFGABE 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌── Aufgabe ─────────────────────────────────────────────────────────
│  Was ist der Gesamtpreis für 43,177 Einheiten zu je 14,694 EUR?
└─────────────────────────────────────────────────────────────────────

┌── Plan des Modells ────────────────────────────────────────────────
│  intent: Gesamtpreis berechnen
│  step 1: calculator({'operation': 'multiply', 'a': 43177, 'b': 14694})
└─────────────────────────────────────────────────────────────────────
```

...und so für alle drei Aufgaben, jede mit einem anderen Plan.

---

## 🎁 Bonus-Serie · `src/mini_agent/` — den Agent Schritt für Schritt bauen

Die zwei Miniaturen oben zeigen den **Wow-Moment**. Wer die Mechanik dahinter ganz sehen will — wie man von *"das Modell antwortet"* über *"strukturiertes JSON"* zu *"Tool-Registry mit Fehlerbehandlung"* kommt — findet unter [`src/mini_agent/`](src/mini_agent/) eine Sechs-Schritt-Serie:

| Step | Was ist neu |
|------|-------------|
| A | Das kleinstmögliche "Agent"-Skript: System + User → LLM → Text |
| B | JSON-Ausgabe mit `intent`-Feld, das der Code parst und danach verzweigt |
| C | Erste echte Werkzeug-Ausführung (Calculator) — der Kern-Task |
| D | Zweites Werkzeug (unit_convert), Modell muss zwischen beiden wählen |
| E | Tool-Registry als Daten; der System-Prompt wird daraus generiert |
| F | Ein Retry für kaputtes JSON, saubere Ablehnung bei anderen Fehlern |

Sechs Skripte, jedes eigenständig lauffähig, kein Framework. Details siehe [`src/mini_agent/README.md`](src/mini_agent/README.md).

Nach Step F: der einzige Unterschied zum echten Agent-Loop aus Kapitel 3 ist ein `while` und eine History-Liste. Wer die Serie durchgearbeitet hat, versteht den Loop-Schritt im nächsten Kapitel als *eine* neue Zeile — nicht als neuen Bauplan.

---

## 🧭 Brücke zum nächsten Kapitel

Bis hier war es *ein* Werkzeug-Aufruf pro Aufgabe (Miniatur 1) oder *ein Plan* pro Aufgabe, den wir aber nur *auslesen* und nicht ausführen (Miniatur 2). Die Aufgabe 2 der zweiten Miniatur zeigt schon: der Plan hat *zwei* Schritte. Der zweite Schritt hängt vom Ergebnis des ersten ab (man muss erst wissen, wie viele EUR die 132,877 USD sind, bevor man dividieren kann).

Das heißt: der Orchestrator muss den ersten Schritt ausführen, das Ergebnis dem Modell zurückgeben, das Modell muss den nächsten Schritt entscheiden. Das ist ein **Loop**, keine gerade Ausführung.

Und genau dieser Loop — was er kostet, was er falsch machen kann, und wer welche Verantwortung darin trägt — ist Kapitel 3.