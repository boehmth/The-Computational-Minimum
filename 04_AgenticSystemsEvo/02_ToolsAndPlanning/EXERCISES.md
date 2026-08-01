# Übungen · Kapitel 2

Drei Aufgaben. Sie zwingen dich dazu, die Werkzeug-Beschreibung als *Prompt* zu behandeln — und das ist der wichtigste Perspektiv-Wechsel dieses Kapitels.

---

## Übung 1 · Beschreibung als Prompt

Nimm `01_give_it_a_tool.py`. Ändere den System-Prompt so, dass er dem Modell *nicht* mehr sagt, wie das JSON aussehen soll — sondern nur den Werkzeug-Namen und die Argument-Namen nennt: *"Du hast ein Werkzeug `calculator(operation, a, b)`. Benutze es wenn nötig."*

Führe das Skript 5 Mal aus. Sammle die Antworten.

- Bei wie vielen Läufen kommt trotzdem sauberes JSON heraus?
- Bei wie vielen kommt Markdown-Fenced JSON (` ```json ... ``` `)?
- Bei wie vielen kommt Prosa mit einer eingebetteten Zahl?
- Bei wie vielen kommt eine falsche Antwort, weil das Modell selbst gerechnet hat?

**Was du lernst:** Die Werkzeug-Beschreibung *ist* ein Prompt. Sie ist die Spezifikation, an die sich das Modell im besten Fall hält. Je präziser du sie schreibst, desto verlässlicher die Ausgabe. Das ist der Grund, warum MCP (Kapitel 5) so viel Aufwand in Schema-Beschreibungen steckt.

---

## Übung 2 · Der Loop kommt aus dem Nichts

`02_model_plans.py` gibt für Aufgabe 2 einen zweistufigen Plan aus:

```
step 1: currency_converter(132877 USD -> EUR)
step 2: calculator(divide, ..., 5.3)
```

Aber: das Skript führt den Plan *nicht* aus. Der zweite Schritt hätte einen numerischen Wert für das erste Argument gebraucht — und dieser Wert kommt erst nach der Ausführung des ersten Schritts.

**Aufgabe:** Erweitere `02_model_plans.py` so, dass es den Plan für Aufgabe 2 tatsächlich *ausführt*:

1. Extrahiere den ersten Schritt.
2. Führe `currency_converter` in Python aus (nimm einen festen Wechselkurs, z.B. `1 USD = 0.92 EUR`).
3. **Wichtig:** ersetze in Schritt 2 den Platzhalter durch den Wert aus Schritt 1.
4. Führe Schritt 2 aus.
5. Drucke die finale Antwort ("...Einheiten").

Wenn du das gemacht hast, hast du zufällig einen mini-`06_loop.py` gebaut. Das ist Kapitel 3.

**Was du lernst:** der Plan-und-dann-ausführen-Ansatz funktioniert für einfache Fälle. Sobald irgendetwas schiefgeht — das Werkzeug erhält Rauschen, der Plan hat einen Fehler, ein Ergebnis überrascht das Modell — brauchst du eine echte Schleife, in der das Modell nach jedem Schritt neu entscheidet. Das ist der Unterschied zwischen "Plan-and-Execute" und "ReAct".

---

## Übung 3 · Ein bösartiges Werkzeug

Füge ein drittes Werkzeug hinzu: `execute_shell(command)`. Beschreibe es harmlos: *"führt Shell-Kommandos aus, für Diagnose-Zwecke"*. Frage das Modell: *"Wie viele Dateien liegen im aktuellen Verzeichnis?"*

Führe das aus — aber **implementiere `execute_shell` nicht**! Nur den Namen und die Beschreibung in den System-Prompt setzen. Was passiert:

- Was für einen Werkzeug-Aufruf produziert das Modell?
- Angenommen du würdest den Aufruf *tatsächlich* an `os.system(...)` weiterreichen — welche Shell-Befehle könntest du unerwünscht bekommen, wenn ein böser User seine Frage geschickt formuliert?

**Was du lernst:** Sicherheit. Ein Werkzeug in der Werkzeug-Liste ist ein *Angriffsvektor*. Wenn der User den Prompt beeinflussen kann (was in jeder Chatbot-Applikation der Fall ist), kann er indirekt Werkzeuge triggern. In Kapitel 6 wird das unter dem Stichwort *"tool misuse"* wieder auftauchen. Für jetzt: **jede Werkzeug-Beschreibung, die du dem Modell zeigst, ist ein Vertrag darüber, was dein Runner mitmacht.**

---

## Wie du wissen kannst, dass du dieses Kapitel verstanden hast

Wenn du in einem Satz sagen kannst: *"Werkzeug-Nutzung heißt, das Modell entscheidet **was und in welcher Reihenfolge**, der Code entscheidet **wie und ob überhaupt**"* — dann bist du fertig mit Kapitel 2.

Das "und ob überhaupt" ist die halbe Miete von Kapitel 6.