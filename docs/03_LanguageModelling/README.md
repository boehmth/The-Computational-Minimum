# Teil 3: Die Entwicklung der Sprachmodelle *(in Vorbereitung)*

**Was in den letzten zehn Jahren aus den Grundlagen von Teil 2 gebaut wurde — und wie aus einem Text-Vervollständiger ein reasoning-fähiges Modell wurde.**

---

## 📜 Der Bogen

Am Ende von Teil 2 dieser Reihe hast du ein winziges GPT-artiges Modell selbst gebaut. Damit hast du **das Fundament** verstanden, auf dem alle heutigen Sprachmodelle stehen. Die spannende Frage lautet jetzt: **Was hat man daraus gemacht?**

Zwischen 2018 (GPT-1) und heute liegen weniger als zehn Jahre — aber in diesem Jahrzehnt hat sich mehr getan als in den 60 Jahren davor. Nicht durch neue Grundideen, sondern durch **massive Skalierung** und *neue Kombinationen* der vorhandenen Bausteine. Die Grundstruktur (Transformer, autoregressive Sprachmodellierung) blieb erstaunlich stabil — was sich änderte, waren die *Trainingsverfahren*, die aus einem Text-Vervollständiger einen hilfsbereiten Assistenten und schließlich ein reasoning-fähiges Modell machten.

Teil 3 zeichnet diesen Weg in fünf klar abgegrenzten Meilensteinen nach — jeder als Antwort auf ein konkretes Scheitern des Vorgängers, ganz im Sinne des roten Fadens, der sich durch die ganze Reihe zieht. Das Vorwort ([`PREFACE.md`](PREFACE.md)) ordnet diese fünf Kapitel in eine übergeordnete These ein: Sie sind zusammen die **Betriebsweise eines ganzen Feldes**, das seine Fortschritte durch Experiment und Ausprobieren findet, nicht durch Theorie am Reißbrett.

> **Wichtig zur Einordnung:** Teil 3 beschreibt die **Innenseite des Modells** — wie moderne LLMs trainiert, ausgerichtet und skaliert wurden. Was man *mit* diesen Modellen zur Laufzeit baut — Werkzeuge, Loops, Protokolle, Agenten — ist Gegenstand von **[Teil 4 · Agentic Systems](../04_AgenticSystems/README.md)**. Teil 3 endet dort, wo das Modell reasoning-fähig ist; Teil 4 beginnt dort, wo dieses Modell handelt.

---

## 🗺️ Die fünf Meilensteine

| Nr. | Ordner | Kernidee | Was neu ist |
|-----|--------|----------|-------------|
| **3.1** | [`01_TinyGPT/`](01_TinyGPT/README.md) | **Ein reines Sprachmodell** (GPT-1-artig) auf echten Webtext-Daten. | Autoregressive Nächstes-Token-Vorhersage. Vervollständigt Text plausibel — folgt aber keiner Instruktion. |
| **3.2** | [`02_TinyInstruct/`](02_TinyInstruct/README.md) | **Instruktions-Feinjustierung durch maskierten Loss** (FLAN, T0, Alpaca, LIMA). | *Nur die Antwort lernen, nicht die Frage.* Aus einem Text-Vervollständiger wird ein Instruction-Follower. |
| **3.3** | [`03_TinyChat/`](03_TinyChat/README.md) | **Präferenz-Ausrichtung** (RLHF, dann DPO). | Aus mehreren plausiblen Antworten die *bessere* wählen — nach menschlichem Maßstab. Aus dem Instruction-Follower wird ein konsistenter Chat-Assistent. |
| **3.4** | [`04_TinyMoE/`](04_TinyMoE/README.md) | **Mixture of Experts** (Shazeer, Switch, Mixtral, DeepSeek-MoE). | Kapazität wächst, ohne dass die Kosten pro Token proportional mitwachsen. Zweite Skalierungsachse. |
| **3.5** | [`05_TinyReason/`](05_TinyReason/README.md) | **Trainiertes Reasoning** (CoT → STaR → PRM → o1 → DeepSeek-R1). | Das Modell lernt, *vor* der Antwort zu denken. Dritte Skalierungsachse (Test-Time Scaling). |

**Damit ist Teil 3 inhaltlich abgeschlossen.** Die Themen, die ursprünglich als weitere Kapitel dieses Teils geplant waren (Werkzeug-Nutzung, Agenten, RAG, Multimodalität, Alignment), sind inzwischen in **[Teil 4 · Agentic Systems](../04_AgenticSystems/README.md)** aufgegangen — dort werden sie als Laufzeit-Systeme behandelt, nicht als Modell-Eigenschaften:

| Vorgesehen (früher Teil 3) | Jetzt behandelt in |
|----------------------------|--------------------|
| **Werkzeug-Nutzung** (Function-Calling, Code-Execution) | Teil 4 · Kapitel 2 (Tools & Planning) und Kapitel 7 (Dynamic Tool Agent) |
| **Agenten** (LLM plant, orchestriert Werkzeuge, bedient den Browser) | Teil 4 · Kapitel 3 (Der Loop) und Kapitel 7 (Dynamic Tool Agent) |
| **Retrieval-augmented Generation (RAG)** | Teil 4 · bewusst *kein* eigenes Kapitel (siehe [`04_AgenticSystems/ROADMAP.md`](../04_AgenticSystems/ROADMAP.md)) |
| **Multimodalität** | *(offen — nicht Teil der aktuellen Agentic-Systems-Erzählung)* |
| **Alignment und Sicherheit** | Teil 3 · Kapitel 3.3 (Präferenz-Ausrichtung) als Modell-Ebene; die Laufzeit-Verantwortung bleibt in Teil 4 |

---

## 🧭 Der rote Faden dieses Teils

Jedes Kapitel behebt eine Grenze des vorherigen — dieselbe Grammatik wie in den Teilen 1 und 2:

> **3.1** vervollständigt Text, folgt aber keiner Anweisung → **3.2** lernt Anweisungen zu folgen, aber wählt zwischen plausiblen Antworten nur zufällig → **3.3** wählt nach menschlicher Präferenz, ist aber ein dichtes Modell mit teurer Skalierung → **3.4** skaliert effizient über Experten, denkt aber weiterhin direkt → **3.5** lernt Zwischenschritte und wird reasoning-fähig.

Zusammen ist das die Geschichte, wie aus einem *Language Model* (2018) ein *Chat-Assistent* (2022), ein *effizientes MoE-Modell* (2024) und schließlich ein *reasoning-fähiges Modell* (2025) wurde — mit vier klar identifizierbaren, aufeinander aufbauenden Trainings-Sprüngen und *ohne* eine grundsätzliche Änderung der zugrundeliegenden Transformer-Architektur.

**Der Übergang zu Teil 4:** Am Ende von 3.5 steht ein Modell, das in Schritten denkt — aber es bleibt rein textuell. Es kann nicht auf die Welt zugreifen, keine Werkzeuge nutzen, keine Datei lesen. Genau hier setzt **[Teil 4](../04_AgenticSystems/README.md)** an: Er zeigt, wie aus einem reasoning-fähigen Modell ein handelnder Agent wird — durch Orchestrierung, Werkzeuge, Loops und Protokolle, die *außerhalb* des Modells liegen.

---

## 🛠️ Ein Unterschied zu Teil 1 und 2

In Teil 1 und Teil 2 haben wir **alles selbst gebaut**, ohne Frameworks. Für Teil 3 ist das anders: Ein modernes LLM lässt sich nicht mehr sinnvoll from-scratch bauen — die Trainingskosten liegen bei Millionen Euro, die Modelle bei hunderten Milliarden Parametern.

Wir werden deshalb in Teil 3 **kleine Open-Source-Modelle nutzen** (z. B. Llama, Mistral, Phi) und mit ihnen die *Ideen* der modernen KI-Landschaft zeigen. Die Modelle bleiben klein genug, dass man sie auf einem Laptop laufen lassen kann.

Die Botschaft bleibt: **verstehen, was drin steckt, statt Framework-Zauber zu bewundern.** Nur der Fokus verschiebt sich von *„baue es selbst"* zu *„verstehe, wie es kombiniert wird".* An genau der Stelle, an der eine Komponente zu klein für ein Framework ist (z. B. die *eine Zeile Loss-Maskierung* in 3.2 oder der *DPO-Loss* in 3.3), wird die entscheidende Änderung von Hand geschrieben.

---

## 🚧 Status

- ✅ **PREFACE + fünf Kapitel-READMEs** stehen mit vollständigem historischen Kontext, Kern-Idee, Wow-Moment-Skizze und Übungs-Skeleton.
- 🚧 **Code-Implementierungen** sind vorbereitet, aber noch nicht umgesetzt. Sie folgen in dieser Reihenfolge: TinyGPT (3.1), dann TinyInstruct (3.2, kleinster technischer Sprung), dann TinyChat (3.3, DPO), TinyMoE (3.4), TinyReason (3.5).
- ✅ **Inhaltlich abgeschlossen** — die ursprünglich geplanten Folge-Kapitel (Werkzeug-Nutzung, Agenten, RAG, Multimodalität, Alignment) sind in **[Teil 4 · Agentic Systems](../04_AgenticSystems/README.md)** aufgegangen.

Wer Teil 2 durchgearbeitet hat, hat das Vokabular und die Intuition, um jetzt schon Fachartikel zu LLMs und Reasoning-Modellen zu lesen — und um in Teil 4 zu verstehen, wie diese Modelle als Agenten eingesetzt werden.
