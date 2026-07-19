# Teil 3: Anwendungen und Skalierung *(in Vorbereitung)*

**Was in den letzten zehn Jahren aus den Grundlagen von Teil 2 gebaut wurde.**

---

## 📜 Der Bogen

Am Ende von Teil 2 dieser Reihe hast du ein winziges GPT-artiges Modell selbst gebaut. Damit hast du **das Fundament** verstanden, auf dem alle heutigen Sprachmodelle stehen. Die spannende Frage lautet jetzt: **Was hat man daraus gemacht?**

Zwischen 2018 (GPT-1) und heute liegen weniger als zehn Jahre — aber in diesem Jahrzehnt hat sich mehr getan als in den 60 Jahren davor. Nicht durch neue Grundideen, sondern durch **massive Skalierung** und *neue Kombinationen* der vorhandenen Bausteine.

Teil 3 wird diese Anwendungswelle konkret machen: mit kleinen, aber echten Miniaturbeispielen, die die *Ideen* der modernen KI-Landschaft nachvollziehbar machen — auch wenn wir die 100-Milliarden-Parameter-Modelle nicht mehr selbst trainieren können.

---

## 🗺️ Geplante Meilensteine

| Nr. | Thema | Kernidee |
|-----|-------|----------|
| **T3-1** | **LLMs im Detail** | Skalierungsgesetze (Chinchilla), Instruction Tuning, RLHF, DPO. Wie wird aus Mini-GPT → ChatGPT? |
| **T3-2** | **Domänen-Transformer** | Dieselbe Architektur, andere Daten: TimeGPT/Chronos (Zeitreihen), TabPFN (Tabellen), AlphaFold-Nachfolger (Proteine). |
| **T3-3** | **Reasoning-Modelle** | DeepSeek-R1, OpenAI o1: Chain-of-Thought, verzögertes Antworten, RL auf Reasoning. |
| **T3-4** | **Multimodalität** | Vision-Language-Models (CLIP, LLaVA, GPT-4V) — Bilder und Text im selben Vektorraum. |
| **T3-5** | **Mixture of Experts** | Wie DeepSeek/Mistral riesige Modelle bauen, die pro Anfrage nur einen Bruchteil ihrer Gewichte aktivieren. |
| **T3-6** | **Retrieval-augmented Generation (RAG)** | LLMs mit externem Wissen: Vektor-Datenbanken, semantische Suche. |
| **T3-7** | **Werkzeug-Nutzung** | Function-Calling, Code-Execution — vom Text-Generator zum Aufgabenlöser. |
| **T3-8** | **Agenten** | LLMs als Gehirn, das mehrere Schritte plant, Werkzeuge orchestriert, den Browser bedient. |
| **T3-9** | **Alignment und Sicherheit** | Wie hält man ein System bei der Wahrheit? Constitutional AI, Red-Teaming, Interpretierbarkeit. |

*(Die Reihenfolge und Auswahl ist noch nicht festgelegt — Teil 3 entsteht in einem eigenen Prozess.)*

---

## 🛠️ Ein Unterschied zu Teil 1 und 2

In Teil 1 und Teil 2 haben wir **alles selbst gebaut**, ohne Frameworks. Für Teil 3 ist das anders: Ein modernes LLM lässt sich nicht mehr sinnvoll from-scratch bauen — die Trainingskosten liegen bei Millionen Euro, die Modelle bei hunderten Milliarden Parametern.

Wir werden deshalb in Teil 3 **kleine Open-Source-Modelle nutzen** (z.B. Llama, Mistral, Phi) und mit ihnen die *Ideen* der modernen KI-Landschaft zeigen. Die Modelle bleiben klein genug, dass man sie auf einem Laptop laufen lassen kann.

Die Botschaft bleibt: **verstehen, was drin steckt, statt Framework-Zauber zu bewundern.** Nur der Fokus verschiebt sich von *„baue es selbst"* zu *„verstehe, wie es kombiniert wird".*

---

## 🚧 Status

Teil 3 ist noch nicht implementiert. Nachdem Teil 1 (Grundlagen: CPU, OS, Compiler, Netzwerk) und Teil 2 (KI: Perceptron → Mini-GPT) fertig sind, geht es hier weiter.

Wer Teil 2 durchgearbeitet hat, hat das Vokabular und die Intuition, um jetzt schon Fachartikel zu LLMs, Reasoning-Modellen und Agenten zu lesen — auch ohne diesen Teil.