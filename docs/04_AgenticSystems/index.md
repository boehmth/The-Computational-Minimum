---
hide:
  - navigation
  - toc
---

# Milestones in Agentic Systems

**Sieben Meilensteine, die zeigen, wie aus einem Sprachmodell ein autonom handelndes System wird — vom "Hello, LLM"-Sechs-Zeiler bis zum Agent, der sich seine Werkzeuge selbst schreibt. Alles selbst programmiert, ohne Frameworks.**

──────────◆──────────◆──────────◆──────────◆──────────

## Willkommen

Dieses Repo ist der praktische Zwilling zum Foliensatz *"Why Agents, and Why Now"*. Der Foliensatz erzählt die Geschichte in Bildern; hier läuft dieselbe Geschichte als Code. In sieben Kapiteln von "das Modell antwortet auf einen Prompt" bis "das Modell schreibt seine eigenen Werkzeuge und speichert sie auf Platte".

Der rote Faden ist die These, dass zwischen GPT-1 (2018) und den State-of-the-Art-Code-Agenten (2025/2026) eine kontinuierliche **Antwortkette** liegt — jedes Kapitel beantwortet die Frage, die das vorherige aufwirft, mit einer neuen Fähigkeit, aber auch mit einem neuen Preis.

## Die drei Prinzipien

Alle sieben Kapitel sind Auswirkungen von genau drei Sätzen:

> **P1 · Was ein LLM ist** — Es konsumiert Text und produziert Text. Nichts anderes.  
> **P2 · Was ein Agent ist** — Das Modell entscheidet die Schritte zur Laufzeit. Nicht der Entwickler, nicht im Voraus.  
> **P3 · Was der Entwickler schuldet** — Alles rund um das Modell ist dein Code.

Wenn du diese drei Sätze in Fleisch und Blut hast, hast du auch den Kern jedes modernen Agent-Systems verstanden — inklusive der Frameworks, die du wahrscheinlich später benutzen wirst.

## Aufbau

Das Repo besteht aus sieben Kapiteln, jedes mit einer eigenen README, einer `src/`-Ordner mit lauffähigen Miniaturen und einer `EXERCISES.md` mit Übungen zur Vertiefung.

- **[Kapitel 1 · Text-in / Text-out](01_TextInTextOut/README.md)** — Was ein LLM aus API-Sicht wirklich ist.
- **[Kapitel 2 · Tools & Planning](02_ToolsAndPlanning/README.md)** — Werkzeuge und der erste Plan. *(Plus die Bonus-Serie `mini_agent/`: einen Agent in 6 Schritten selbst bauen.)*
- **[Kapitel 3 · Der Loop](03_TheLoop/README.md)** — Der externe Loop und was er kostet.
- **[Kapitel 4 · Reasoning innen drin](04_ReasoningInside/README.md)** — Der zweite Loop, unsichtbar.
- **[Kapitel 5 · Protokolle & Skalierung](05_ProtocolsAndScale/README.md)** — MCP und A2A. *(Plus die Bonus-Sektion `a2a/`: live-Server mit Inspector.)*
- **[Kapitel 6 · Wann NICHT bauen](06_WhenNotToBuild/README.md)** — Das Urteil.
- **[Kapitel 7 · Dynamic Tool Agent](07_DynamicToolAgent/README.md)** — Der Agent, der seine eigenen Werkzeuge schreibt.

## Wie du dieses Buch lesen kannst

Zwei Ebenen, je nach Zweck:

- **Die Kapitel-READMEs** liefern *Historischer Kontext, Wow-Moment und den roten Faden*. Wer nur einen Überblick will, bleibt hier und liest die Kapitel wie Zeitungsartikel.
- **Die Skripte in `src/`** liefern *ausführbaren Code*. Wer selbst experimentieren oder prüfen will, startet sie und liest die Ausgabe Zeile für Zeile.

Jedes Kapitel hat außerdem **Übungen** in `EXERCISES.md` — sie zwingen dich, die Miniatur zu modifizieren, und Modifikation ist der einzig echte Weg, den Code zu verstehen.

## Voraussetzungen

- **Python 3.10+**
- Zugang zu **SAP GenAI Hub** (Service-Key als `.env`) oder **Google Gemini** (API-Key als `GOOGLE_API_KEY`).
- `pip install -r requirements.txt`

Für die Bonus-Sektion in Kap. 5 (A2A-Server): zusätzlich `pip install fastapi uvicorn`.

## Woher es kommt

Dieses Repo hat einen Zwilling: den Foliensatz *"Why Agents, and Why Now"* (54 Slides, sechs Kapitel-Divider), der dieselbe Geschichte für ein weniger technisches Publikum erzählt. Wenn du den Foliensatz kennst — die Kapitel-Reihenfolge hier folgt genau seinem Bogen. Wenn du ihn nicht kennst, brauchst du ihn nicht: der Code steht für sich.

──────────◆──────────◆──────────◆──────────◆──────────

*Los geht's im [Vorwort](PREFACE.md) oder direkt in [Kapitel 1](01_TextInTextOut/README.md).*