# Kapitel 7 · Übungen

Die Übungen sind das eigentliche Lehrwerkzeug. Sie zwingen dich, die Miniatur zu modifizieren — und Modifikation ist der einzig echte Weg, den Code zu verstehen.

## Übung 1 · Ein bösartiges Tool provozieren

Erweitere die Beispiel-Fragen in `01_dynamic_tool_agent.py` um eine, die den Agent versuchen lässt, eine Datei zu schreiben — z. B. *"Erstelle eine Datei mit dem Inhalt 'hallo' unter /tmp/x.txt"*.

Beobachte:

1. Welche `action` schlägt das Modell im ersten Turn vor?
2. Wenn es `generate_tool` versucht: welchen Code produziert der Tool-Generator, und woran genau scheitert `_validate_tool_ast`?
3. Was passiert im nächsten Turn, wenn der Agent die Fehlermeldung sieht?

Diese Übung macht den Zweck der Sandbox greifbar: die Whitelist ist nicht nur Deko, sie fängt das erste realistische Angriffsszenario ab.

## Übung 2 · Die Sandbox strenger machen

In `FORBIDDEN_NAMES` stehen aktuell nur ein paar offensichtlich gefährliche Namen. Ein raffinierter generierter Code könnte über Umwege daran vorbei — etwa mit `().__class__.__bases__[0].__subclasses__()` (der berühmte "Ausbruch aus RestrictedPython"-Trick).

Prüfe:

1. Erweitere `_validate_tool_ast` so, dass **jeder** Attribut-Zugriff auf Dunder-Namen (`__.*__`) verboten ist, nicht nur solche, die *mit* Dunder anfangen.
2. Verbiete zusätzlich `ast.Subscript` mit Constant `0` (ein üblicher erster Schritt beim Ausbruchs-Trick).
3. Schreibe einen kurzen Test-String, der die alte Whitelist übersteht, aber deine neue nicht mehr.

Kein Sandbox-Design ist "fertig" — jede Erweiterung schließt eine Klasse von Angriffen, öffnet aber vielleicht die nächste. Diese Übung soll den Preis dafür konkret machen.

## Übung 3 · Ressourcenlimit über Timeout

Der aktuelle Agent kann durch ein generiertes `while True: pass` blockiert werden. Ergänze `ToolRegistry.call()` (oder ihre persistente Variante), so dass jeder Tool-Aufruf über `signal.SIGALRM` (Unix) oder einen Thread-Timer (Windows-kompatibel) nach 2 Sekunden abbricht.

Prüfe:

1. Was ist die Ausnahme-Klasse, die dein Timeout wirft, und wie stellt der Agent-Loop das dem Modell zurück?
2. Kann der Agent den Timeout erkennen und ein *anderes* Tool generieren, das schneller ist? Prüfe mit einer Aufgabe wie *"Finde die 100.000ste Primzahl"*.

Das ist der Übergang von "Sicherheit als Verbieten" (Whitelist) zu "Sicherheit als Verbrauchsgrenze" (Ressourcen). Die zweite ist bei komplexen Aufgaben oft die einzig praktikable.

## Übung 4 · Die Registry gemeinsam nutzen

Wenn zwei Läufe von `02_dynamic_tool_agent_persisted.py` unabhängig laufen, könnten sie sich gegenseitig Tools überschreiben. Erweitere `_persist_tool`:

1. Prüfe, ob eine `generated_tools/{name}.py` bereits existiert.
2. Wenn ja, vergleiche den existierenden Code mit dem neuen. Wenn identisch: nur die Metadaten aktualisieren, den Code nicht anfassen.
3. Wenn unterschiedlich: entscheide sinnvoll — die neue Version behalten und die alte in `generated_tools/{name}.v{N}.py.bak` sichern.

Ergebnis: eine echte kleine Werkzeug-Versionshistorie. In produktionsnaher Version wären das git-Commits statt `.bak`-Dateien; die Idee bleibt dieselbe.

## Übung 5 · Persistierten Code manuell manipulieren

Führe `02_dynamic_tool_agent_persisted.py` einmal laufen, so dass mindestens `is_prime.py` unter `generated_tools/` liegt. Öffne die Datei in einem Editor und füge oben eine Zeile `import os` ein. Speichere.

Führe das Skript erneut aus:

1. Was steht in der `[Persistenz]`-Ausgabe?
2. Welche `ToolCodeError`-Meldung erscheint konkret?
3. Was macht der Agent im nächsten Turn, wenn er `is_prime` benutzen will — kommt er wieder auf `generate_tool` zurück?

Das ist die "Angreifer manipuliert Platte zwischen zwei Läufen"-Übung. Die Antwort auf Frage 3 zeigt, ob dein System *robust* ist oder nur *nicht durchbrochen*.

## Übung 6 · Den Self-Healing-Loop provozieren

Bei Miniatur 3 wird der Repair-LLM nur aktiv, wenn der generierte Code kaputt ist. Das passiert im Alltag nicht auf Bestellung. Provoziere es gezielt:

1. Sabotiere den Tool-Generator, indem du `TOOL_GENERATOR_SYSTEM_PROMPT` temporär so umschreibst, dass er die Regeln bewusst verletzt (z. B. `import os` erzwingen, oder eine bekannte Dunder-Attribut-Referenz einbauen). Erwartung: `ToolCodeError` beim ersten Wurf, Repair-Prompt korrigiert es, zweiter Versuch klappt.
2. Setze `max_repair_attempts=0` in der Registry-Konstruktion und starte neu. Erwartung: dieselbe Sabotage führt jetzt sofort zum Aufgeben, ganz wie in Miniatur 2. Das ist der Beleg dafür, dass der Repair-Loop wirklich eine separate Policy ist, kein fest verdrahteter Bestandteil des Sandboxes.
3. Zähle die zusätzlichen LLM-Aufrufe: wie viele Tokens *kostet* eine gelungene Reparatur vs. ein Neuversuch aus Miniatur 2 (bei dem der Agent-Loop das ganze Tool neu generiert)?

Diese Übung macht sichtbar, was der Skalierungs-Kasten im Text behauptet: Self-Healing ist keine neue Idee, sondern eine wählbare Retry-Strategie — genau wie in Kapitel 3, nur mit generiertem Code als "flaky Operation".

## Bonus · Vergleich mit Kapitel 3

Öffne `../03_TheLoop/src/01_basic_loop.py` neben `01_dynamic_tool_agent.py`. Streiche in Gedanken die `generate_tool`-Action und die Sandbox weg. Was bleibt übrig?

Notiere: welche Zeilen aus Kapitel 3 tauchen strukturell hier wieder auf? Wo ist die Grenze zwischen "Kap. 3 mit anderen Prompts" und "eine wirklich neue Idee"?

Und dann öffne `../03_TheLoop/src/03_retry_strategies.py` neben `03_dynamic_tool_agent_self_healing.py`. Suche in beiden die LLM-guided-Recovery-Stelle. Der Repair-Prompt und die vier Retry-Strategien haben strukturell dieselbe Form: *Fehler beobachten → LLM mit Fehler-Kontext neu prompten → korrigierte Antwort nutzen*. Was ist der einzige inhaltliche Unterschied?

Wenn du diese Übung machst, siehst du: Kapitel 7 ist kein neuer Loop. Es ist der Loop aus Kapitel 3, plus eine Tool-Registry, die zur Laufzeit wachsen kann — und die Retry-Politik ist auf beiden Ebenen dieselbe. Das ist die ganze konzeptionelle Neuerung. Der Rest ist Sandbox-Politik.
