# Vorwort · Warum Miniaturen?

Warum sieben Miniaturen und nicht ein "richtiges" Agenten-Framework?

Weil ein Framework die Antwort verkauft, bevor die Frage klar ist.

## Die Frage, die dieser Teil beantworten will

Wenn dir jemand sagt "wir bauen einen Agenten", ist das ein leerer Satz — bis du beantwortet hast:

- **Was macht das Modell selbst, und was macht der Code drum herum?**
- **Wo endet die Sprache-in-Sprache-aus-Illusion, und wo fängt Verantwortung an?**
- **Welche Fehlerklassen musst du in Kauf nehmen, welche musst du ausschließen?**
- **Und woran erkennst du, dass ein Agent überhaupt das richtige Werkzeug ist?**

Alle vier Fragen sind engineering-Fragen, keine LLM-Fragen. Sie kann dir Anthropic nicht beantworten und OpenAI nicht — sie müssen von dir und deinem Team beantwortet werden, in deinem konkreten Kontext.

Ein Framework nimmt dir *das Beantworten* ab. Es liefert Defaults für Retry-Strategien, für Stop-Bedingungen, für Kontext-Verwaltung, für Tool-Registrierung. Diese Defaults sind fast immer vernünftig — aber du wirst sie erst dann verstehen, wenn du selbst *einmal einen Agenten ohne sie* gebaut hast. Genau das ist der Zweck dieser Miniaturen.

## Was eine Miniatur ist

Eine Miniatur in diesem Sinn ist ein **einzelnes, in sich geschlossenes Python-Skript unter 200 Zeilen**, das genau *eine* Idee demonstriert. Es hat keine Abhängigkeiten außer dem geteilten `common/llm.py` (der HTTP-Client zu SAP GenAI Hub) und der Standardbibliothek. Es lässt sich in einem Terminal starten, produziert lesbaren Output, und der Output beweist einen Punkt.

Wenn du eine Miniatur *ausgeführt* und *verstanden* hast, hast du das Recht erworben, sie zu erweitern — oder durch ein Framework zu ersetzen. Vorher nicht.

## Warum das gerade jetzt wichtig ist

2025 ist die Zeit, in der jeder Frontend-Entwickler dir sagt "ich habe da eben einen Agenten mit LangChain gebaut". Was der Satz meist verschweigt: die Retry-Policy ist der LangChain-Default, die Stop-Bedingung ist der LangChain-Default, das Prompt-Template ist von einem Blog-Post kopiert, und wenn ein Tool 500 zurückgibt, wird der Agent bis zum Ende der Iterationsgrenze weiter Fehler produzieren.

Das ist nicht die Schuld von LangChain. Das ist die Konsequenz davon, die Werkzeuge zu benutzen, bevor man die Verantwortungen verstanden hat.

## Der Zwilling zu diesem Repo

Es gibt einen Foliensatz *"Why Agents, and Why Now"*, der dieselbe Geschichte für ein weniger technisches Publikum erzählt. Die Folien führen die drei Prinzipien ein:

> **P1** — Ein LLM konsumiert Text und produziert Text. Nichts anderes.  
> **P2** — Das Modell entscheidet die Schritte zur Laufzeit.  
> **P3** — Alles rund um das Modell ist dein Code.

Dieser Code-Teil ist die operative Seite dieser drei Sätze. Kein einziges Kapitel führt eine neue Idee ein — jedes Kapitel *demonstriert* eine der drei Prinzipien in Code, den du selbst laufen lassen kannst.

Innerhalb von *The Computational Minimum* ist dieser Teil außerdem die **System-Fortsetzung** zu [`../03_LanguageModelling/README.md`](../03_LanguageModelling/README.md): Dort geht es stärker um die Frage, wie moderne LLMs durch Training, Alignment und Skalierung entstanden sind; hier geht es um die Frage, was Entwickler dann **mit ihnen bauen**.

Wenn du den Foliensatz kennst: die Kapitel-Reihenfolge folgt genau dem Bogen des Talks. Kapitel 1 ist Folie 4-7 (P1 in Aktion). Kapitel 2 ist Folie 8-10 (das erste JSON, der erste Plan). Kapitel 3 ist Folie 21 (der Loop). Kapitel 4 ist Folie 22 (Reasoning innen drin). Kapitel 5 ist Folie 33 (MCP/A2A). Kapitel 6 ist Folie 37 (das Urteil). Kapitel 7 ist die zugespitzte 2026-Fortsetzung: Tool-Making und Runtime-Code-Generierung.

Wenn du den Foliensatz nicht kennst: du brauchst ihn nicht. Der Code steht für sich.

## Voraussetzungen

- **Python 3.10+** (typing-Features)
- Ein Zugang zu **SAP GenAI Hub** (Service Key JSON, gesetzt in `.env`)
- Optional: **Google Gemini** als Fallback-Backend
- Keine weiteren Abhängigkeiten außer `requests`, `python-dotenv` (siehe `../requirements.txt`)

Wenn du keinen GenAI-Hub-Zugang hast, lass die Beispiele mit `LLM_BACKEND=gemini` laufen — sie funktionieren mit Gemini flash-latest bei allen Kapiteln, mit leicht anderen Reasoning-Details in Kapitel 4.

## Wie man sich durcharbeitet

Ich empfehle: **eine Miniatur pro Kaffee**. Das heißt: lies die kurze Kapitel-README, führe die Skripte in `src/` aus, sieh dir *jede Zeile des Outputs* an und frage dich: *"Warum ist das so?"*. Wenn du eine Zeile nicht erklären kannst, lies die entsprechende Zeile im Skript. Wenn das Skript sie erklärt: gut. Wenn nicht: das ist ein Bug in der Erklärung, und ich freue mich über den Hinweis.

Am Ende jedes Kapitels stehen 2-3 Übungen in `EXERCISES.md`. Sie sind das eigentliche Lehrwerkzeug. Sie zwingen dich, die Miniatur zu modifizieren, und Modifikation ist der einzig echte Weg, Code zu verstehen.