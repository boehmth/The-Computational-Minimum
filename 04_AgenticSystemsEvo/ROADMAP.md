# Roadmap · Milestones in Agentic Systems

Wo dieses Repo herkommt, wo es steht, und wo es hin will.

## Der Ausgangspunkt

Ein Foliensatz — *"Why Agents, and Why Now"* — der die Geschichte in 54 Slides für ein Publikum ohne tiefen Python-Hintergrund erzählt. Der Foliensatz ist die Basis, dieses Repo ist der praktische Zwilling: dieselbe Geschichte, dieselben Meilensteine, aber diesmal als lauffähiger Code.

Der ursprüngliche Plan hatte **sechs Kapitel**, gespiegelt an den sechs Kapitel-Dividern des Foliensatzes. Die aktuelle Version hat sieben — Kapitel 7 (Dynamic Tool Agent) ist nachträglich hinzugekommen, weil dieselbe Struktur — Agent, der etwas zur Laufzeit lernt — im Sommer 2026 zum State-of-the-Art gehört und ohne sie die Erzählung heute unvollständig wirken würde.

## Aktueller Stand

- ✅ Alle sieben Kapitel haben README, `src/` mit lauffähigen Miniaturen und `EXERCISES.md`
- ✅ Deutsche und englische Fassungen für Kapitel 1–6 (`README.md` + `README.en.md`)
- ✅ Kapitel 2 ergänzt um die Bonus-Serie `mini_agent/` (6 Steps: Single-Call → Fallback)
- ✅ Kapitel 5 ergänzt um Bonus-Sektion `a2a/` (Live-Server + Client + Demo-Skripte)
- ✅ Kapitel 7 (**neu**) über Runtime-Werkzeug-Generierung mit AST-Sandbox
- ✅ mkdocs-Basis-Setup (index.md, sync_docs.py, mkdocs.yml, stylesheets)
- 🚧 Kapitel 7 · `README.en.md` und `EXERCISES.en.md` (englische Übersetzung noch offen)
- ✅ Manuelles Site-Deployment über `tools/deploy_site.py` (nutzt `mkdocs gh-deploy`, kein GitHub-Actions-Workflow nötig)

## Der rote Faden

Sieben Kapitel, sieben Fragen, sieben Antworten — jede Antwort löst ein Problem und wirft ein neues auf:

1. **Text-in / Text-out** — Ein LLM antwortet in Text. → *Aber die Antwort ist falsch, wenn rechnen nötig ist.*
2. **Tools & Planning** — Gib ihm ein Werkzeug. → *Aber der Plan hat mehrere Schritte.*
3. **Der Loop** — Bau einen Loop. → *Aber der Loop kostet Tokens.*
4. **Reasoning innen drin** — Das Modell iteriert intern. → *Aber der äußere Loop bleibt trotzdem dein Code.*
5. **Protokolle & Skalierung** — Standardisiere Werkzeug + Agent-Schnittstellen. → *Aber jetzt kannst du zu viel bauen.*
6. **Wann NICHT bauen** — Nicht alles ist ein Agent. → *Was ist der neue Stand, wenn Agenten Werkzeuge selbst schreiben können?*
7. **Dynamic Tool Agent** — Der Agent schreibt seine Werkzeuge selbst. → *Aber Sandbox + Sicherheit bleiben dein Code.*

Das ist das Buch. Wer diese sieben Antworten hat, hat auch die Landkarte, um jedes Agent-Framework der Welt zu lesen.

## Wohin es geht

Nachträgliche Erweiterungen, in Reihenfolge der Wahrscheinlichkeit:

- **Kap. 7 · Englische Übersetzung.** Das Kapitel ist bisher nur auf Deutsch verfasst. Parallel zu den bestehenden `.en.md`-Fassungen der anderen Kapitel.
- **CI-basiertes Site-Deployment (optional).** Aktuell wird die Site manuell via `python tools/deploy_site.py` deployt (nutzt `mkdocs gh-deploy`, pusht auf einen `gh-pages`-Branch). Wer möchte, kann daraus einen GitHub-Actions-Workflow machen, der auf jedem Push auf `main` automatisch deployt — dann fällt der manuelle Aufruf weg. Solange das Ziel-Repo keine Actions unterstützt (oder man sie bewusst nicht will), reicht das lokale Skript.
- **Bilder aus dem Foliensatz.** Der pptx-Foliensatz enthält Schlüssel-Grafiken (das "Anatomie eines Agenten"-Diagramm, die MCP/A2A-Wire-Format-Skizze, die drei Prinzipien als Hero-Slides). Diese als PNG extrahieren und in die Kapitel-READMEs einbetten, damit die Site nicht nur Text ist.
- **Kap. 8 (offen)?** Wenn Multi-Agent-Systeme (mehrere Agents, die miteinander sprechen, jeder mit seiner Aufgabe) sich als eigenständiger Meilenstein herausstellen — z. B. AutoGen, CrewAI, LangGraph — wäre das die nächste natürliche Erweiterung. Für den Sommer 2026 ist es noch nicht so klar, ob "Multi-Agent" wirklich eine neue Idee ist oder nur "Agenten, die A2A benutzen".

## Was bewusst nicht geplant ist

- **Kein Framework-Kapitel.** Es wird bewusst kein "Kapitel 8: LangChain / Semantic Kernel / AutoGen" geben. Frameworks sind Anwendungsschicht, nicht Meilenstein. Wer die sieben Meilensteine hat, versteht die Frameworks — nicht umgekehrt.
- **Kein RAG-Kapitel.** Retrieval Augmented Generation ist eine hervorragende Anwendung der Meilensteine, aber sie ist ein *Werkzeug* (siehe Kap. 2), keine eigene Idee. Ein Blog-Post oder Übungs-Bonus, kein Kapitel.
- **Kein Fine-Tuning-Kapitel.** Fine-Tuning gehört ins Nachbarrepo *Milestones in Machine Intelligence*, nicht hierher. Dieser Teil beginnt bei einem *fertigen* Modell und fragt nur, was man außenherum baut.