# mini_agent · einen Agent Schritt für Schritt zusammenbauen

**Sechs Skripte, jedes fügt genau eine Fähigkeit hinzu. Nach 200 Zeilen deines eigenen Codes hast du einen echten kleinen Agenten — ohne Framework, ohne Magie.**

Diese Bonus-Serie ergänzt die zwei Haupt-Miniaturen des Kapitels (`../01_give_it_a_tool.py`, `../02_model_plans.py`). Die Haupt-Miniaturen zeigen den **Wow-Moment** — dasselbe Werkzeug, drei verschiedene Pläne. Die mini_agent-Serie hier zeigt das **Baugerüst darunter**: wie du von *"das Modell antwortet auf einen Prompt"* zu *"das Modell wählt aus mehreren Werkzeugen, das JSON wird geparst, Fehler werden abgefangen"* kommst.

Die Skripte *loopen* absichtlich nicht. Ein Aufruf, eine Entscheidung, eine Werkzeug-Ausführung. Das hält jedes Skript kurz genug, um es im Kopf zu behalten. Der Sprung zu `../../../03_TheLoop/src/01_basic_loop.py` wird dadurch sichtbar: *das einzige, was am Ende von Step F fehlt, ist das `while`-Schlüsselwort.*

## Der Pfad

| Step | Datei | Was ist neu |
|------|-------|-------------|
| A | `step_a_single_call.py` | System + User → LLM → drucken. Nichts anderes. |
| B | `step_b_structured_output.py` | Bitte um JSON mit `intent`-Feld. Parsen. Unbekannte Intents ablehnen. |
| C | `step_c_one_tool.py` | Intent `calculate` → Calculator ausführen. Sonst freundlich ablehnen. **Der Kern-Task aus der Kapitel-Aufgabe.** |
| D | `step_d_two_tools.py` | Zweites Werkzeug: `unit_convert`. Hart-kodierter Router (`if/elif`). |
| E | `step_e_tool_registry.py` | Werkzeuge werden zur Registry. Der System-Prompt wird *daraus generiert*. |
| F | `step_f_fallback_and_errors.py` | Kaputtes JSON, unbekanntes Tool, Tool-Exception — ein Retry, dann höflich ablehnen. |

Nach Step F: öffne `../../../03_TheLoop/src/01_basic_loop.py`. Der Diff ist ein `while` und eine History-Liste — das ist die ganze Strecke vom "Single-Shot-Dispatcher" zum "Agent-Loop".

## Ausführen

```powershell
cd "C:\Users\D041506\Source\Agentic Systems"

python "02_ToolsAndPlanning/src/mini_agent/step_a_single_call.py"
python "02_ToolsAndPlanning/src/mini_agent/step_c_one_tool.py" "What is 43177 times 14694?"
python "02_ToolsAndPlanning/src/mini_agent/step_e_tool_registry.py" "How many kilometres are 3 miles?"
```

Jedes Skript akzeptiert einen optionalen User-Prompt als `argv[1]`. Ohne Argument nutzt jedes seinen eigenen Demo-Prompt, sodass du sie einfach nur starten kannst.

## Was jeder Schritt wiederverwendet

Alle sechs Steps importieren `chat` und `extract_json` aus `common/llm.py`. Sonst wird nichts geteilt — keine Basis-Klasse, kein Framework. Wenn du Step A neben Step F legst und Zeile für Zeile vergleichst, siehst du genau, *welche Stücke eines Agenten deine sind* (Prinzip 3).

## Die zwei Werkzeuge

- **`calculator(operation, a, b)`** — dieselbe Form wie in `../01_give_it_a_tool.py`. Multiply/add/subtract/divide.
- **`unit_convert(value, source, target)`** — Längeneinheiten: Meilen, km, m, Fuß, Zoll, cm. Deterministische Tabelle, kein API.

Zwei Werkzeuge sind das Minimum, ab dem *"das Modell muss wählen"* real wird. Mit einem Werkzeug hat das Modell keine Entscheidung; mit zwei entscheidet allein die natürliche Sprache, welches läuft.

## Was diese Serie *nicht* ist

- **Kein Loop.** Jedes Skript ruft das LLM genau einmal, dispatched einmal, beendet sich. Der Loop ist in Kapitel 3.
- **Nicht produktionsreif.** Kein Rate-Limiting, keine Observability, kein Kosten-Cap, kein Tracing. Für das volle P3-Checkliste siehe die späteren Kapitel.
- **Kein Framework.** Falls du dasselbe in LangChain sehen willst: eine 10-Zeilen-Übersetzung ist in Kapitel 6 dokumentiert.

Der Zweck dieser Serie ist es, die *Form* eines Agenten in ~200 Zeilen deines eigenen Codes offensichtlich zu machen. Danach kannst du jedes Framework-basierte Agent-System öffnen und sagen: *"Ah, das da drin ist Step E. Und da hinten ist Step F. Und der Loop, den sie verbergen, ist das `while` aus Kapitel 3."*