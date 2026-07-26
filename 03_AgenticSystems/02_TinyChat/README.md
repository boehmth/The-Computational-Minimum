# 📖 3.2 Instruktions- und Dialogfähigkeit — von GPT-3 zu InstructGPT

## 🎯 Das Problem des Vorgängers

Kapitel 3.1 hat gezeigt, wie ein reines Sprachmodell (GPT-1.5) Text plausibel
fortsetzt — aber eine Frage nicht als Frage erkennt und keiner Instruktion
folgt. Es fehlt der Schritt vom "Text-Vervollständiger" zum "Assistenten",
der Anweisungen versteht und gezielt darauf antwortet.

Dieser Schritt geschah historisch nicht auf einmal, sondern in vier klar
identifizierbaren Stufen zwischen 2020 und 2022. Jede Stufe löst ein
konkretes Problem der vorherigen — dasselbe Muster, das sich durch die ganze
Reihe zieht.

## 📜 Historischer Kontext: Vier Stufen zum Chat-Assistenten

### 1. GPT-3 (2020) — große Modelle, aber noch kein Chat

Brown et al. (2020), *"Language Models are Few-Shot Learners"*, zeigen: Ein
ausreichend großes, rein generativ vortrainiertes Sprachmodell kann Aufgaben
lösen, wenn man ihm die Aufgabe als Text vormacht (Few-Shot-Prompting).

Was GPT-3 **nicht** hat:

- keine Maskierung von Trainingsdaten
- keine Rollenstruktur (kein "User" / "Assistant")
- keine Instruktionsfähigkeit im eigentlichen Sinn
- keine Chat-Struktur

GPT-3 beweist nur: Skalierung allein bringt beeindruckende Fähigkeiten
hervor — löst aber nicht das Grundproblem aus 3.1.

### 2. FLAN / T0 (2021) — die ersten echten Instruction-Tuning-Ansätze

Hier beginnt die eigentliche Wende:

- **FLAN** (Wei et al., 2021, Google), *"Finetuned Language Models Are
  Zero-Shot Learners"* — erstes systematisches Instruction-Finetuning; zum
  ersten Mal wird der User-Teil eines Beispiels maskiert und nur die Antwort
  gelernt.
- **T0** (Sanh et al., 2021, BigScience), *"Multitask Prompted Training
  Enables Zero-Shot Task Generalization"* — Training auf prompt-formulierten
  Aufgaben über viele Task-Familien hinweg; Modelle lernen *Aufgaben*, nicht
  nur Sprache.

Was noch fehlt: eine systematische Optimierung nach *menschlichem
Qualitätsempfinden* statt nach reinem Trainingsverlust — und noch keine
konsistente Dialog-/Rollenstruktur.

### 3. Die RLHF-Linie (2017–2020) — Modelle nach menschlichen Präferenzen trainieren

Parallel zu FLAN/T0 entwickelt sich eine zweite, unabhängige Idee, die
InstructGPT später mit dem Instruction-Tuning zusammenführt:

- **Christiano et al. (2017)**, *"Deep Reinforcement Learning from Human
  Preferences"* — führt RLHF als Methode überhaupt ein, ursprünglich für
  Kontroll-/Spielaufgaben (Atari, Robotik), nicht für Sprache.
- **Ziegler et al. (2019)**, *"Fine-Tuning Language Models from Human
  Preferences"* — überträgt RLHF erstmals auf Sprachmodelle.
- **Stiennon et al. (2020)**, *"Learning to Summarize from Human Feedback"*
  — wendet RLHF konkret auf eine Sprachaufgabe (Zusammenfassung) an und wird
  zum direkten methodischen Vorläufer von InstructGPT.

Diese Linie löst ein anderes Problem als FLAN/T0: nicht *welche* Aufgaben ein
Modell lernt, sondern *wonach* es optimiert wird, wenn es mehrere plausible
Antworten geben könnte.

### 4. InstructGPT (2022) — die Zusammenführung

Ouyang et al. (2022), *"Training Language Models to Follow Instructions with
Human Feedback"*, verbinden beide Linien:

- Maskierung des User-Teils (aus FLAN/T0)
- Rollenstruktur (Instruction → Response)
- Supervised Fine-Tuning auf menschlich verfassten Beispielen
- Reinforcement Learning from Human Feedback (aus der Christiano/Ziegler/
  Stiennon-Linie)

Das Ergebnis: Aus einem reinen Next-Token-Predictor wird ein Modell, das
gehorsam, hilfreich, dialogfähig und konsistent auf Instruktionen reagiert —
"wie ein Assistant".

> **ChatGPT (2022) hat kein eigenes Paper.** Es ist im Kern eine
> Produktversion aus GPT-3.5 + InstructGPT-Finetuning + Chat-Format +
> Multi-Turn-Dialogdaten — keine neue wissenschaftliche Methode, sondern die
> Zusammenführung der vier oben beschriebenen Bausteine zu einem Produkt.

*[Platzhalter — persönlicher Bezug: Berührungspunkt zur eigenen Dissertation
(2016, probabilistisches Modell für Collaborative Information Retrieval) —
kein direkter Einfluss auf Sprachmodelle, aber Textklassifikation und das
Lernen von Modellparametern aus natürlichsprachlichen Daten sind seit jeher
IR-Kernthemen, eine Linie, die sich bis in heutige RAG-Systeme fortsetzt]*

## 😮 Der Wow-Effekt: Vorher/Nachher im Vergleich

*[Platzhalter — Beispielausgaben: dasselbe Prompt einmal mit dem
GPT-1.5-Modell aus 3.1 (reine Fortsetzung) und einmal mit dem in diesem
Kapitel maskiert/instruktionsgetunten Modell (zielgerichtete Antwort)
gegenüberstellen]*

```
Prompt:              "Was ist die Hauptstadt von Frankreich?"

3.1 (GPT-1.5):        [Platzhalter — plausible, aber themenfremde Fortsetzung]
3.2 (instruktionsgetunt): [Platzhalter — direkte, zielgerichtete Antwort]
```

## 🧠 Was du baust

- Eine Trainingspipeline mit maskiertem Loss: nur der "Response"-Teil eines
  Instruction/Response-Paares fließt in den Loss ein (analog zu FLAN)
- Eine einfache Rollenstruktur (User/Assistant) im Eingabeformat
- *(optional, je nach Umfang)* eine vereinfachte Präferenz-Optimierung als
  didaktische Annäherung an RLHF — kein vollständiges PPO-Setup, sondern ein
  Miniaturbeispiel, das das Prinzip zeigt

> ⚠️ Wie in 3.1 gilt: Wir bauen hier bewusst nicht die komplette
> RLHF-Infrastruktur von Grund auf nach (Reward-Modell-Training + PPO wären
> für ein Lehrbeispiel dieser Größenordnung nicht mehr sinnvoll vermittelbar)
> — der Fokus liegt auf dem *Prinzip*, nicht der produktionsreifen
> Implementierung.

## 🚀 Schnelleinstieg

```bash
python 03_AgenticSystems/02_InstruktionUndDialog/src/train_instruct.py --profile laptop
```

## 📚 Quellen

- Brown, T. et al. (2020). *Language Models are Few-Shot Learners.*
- Wei, J. et al. (2021). *Finetuned Language Models Are Zero-Shot Learners.* (FLAN)
- Sanh, V. et al. (2021). *Multitask Prompted Training Enables Zero-Shot Task Generalization.* (T0)
- Christiano, P. et al. (2017). *Deep Reinforcement Learning from Human Preferences.*
- Ziegler, D. et al. (2019). *Fine-Tuning Language Models from Human Preferences.*
- Stiennon, N. et al. (2020). *Learning to Summarize from Human Feedback.*
- Ouyang, L. et al. (2022). *Training Language Models to Follow Instructions with Human Feedback.* (InstructGPT)

## ✏️ Übungen

*[Platzhalter]*

## ➡️ Grenzen dieses Meilensteins

InstructGPT-artige Modelle folgen Instruktionen und antworten dialogfähig —
aber sie beantworten auch mehrstufige, komplexe Probleme direkt und ohne
Zwischenschritte, was bei anspruchsvollen Aufgaben zu Fehlern führt. Kapitel
3.3 (Mixture of Experts) und 3.4 (Reasoning) zeigen, wie Modelle sowohl
effizienter skalieren als auch lernen, vor der Antwort zu "denken".