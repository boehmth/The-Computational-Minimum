# 📖 3.1 LLM-Grundlagen — GPT-1.5

## 🎯 Das Problem des Vorgängers

Kapitel `07_Transformer` (Teil 2) hat gezeigt, wie Self-Attention parallele
Sequenzverarbeitung ermöglicht — aber das dort gebaute Modell löst eine eng
umrissene Aufgabe. Es fehlt noch ein Modell, das Sprache generativ vorhersagt
und dieses gelernte Sprachverständnis flexibel auf beliebige nachgelagerte
Aufgaben überträgt, statt für jede Aufgabe von vorn zu lernen.

## 📜 Historischer Kontext: Generative Pre-Training (2018)

Im Juni 2018 veröffentlichten Alec Radford und Kollegen bei OpenAI das Paper
*"Improving Language Understanding by Generative Pre-Training"* — später als
GPT-1 bekannt. Die Kernidee war methodisch einfach, aber folgenreich: Statt
für jede NLP-Aufgabe (Klassifikation, Textähnlichkeit, Frage-Antwort,
Textual Entailment) ein eigenes, von Grund auf trainiertes Modell zu bauen,
trainiert man zunächst ein einzelnes generatives Sprachmodell unüberwacht auf
großen Textmengen (BooksCorpus) — reine Nächstes-Wort-Vorhersage. Dieses
vortrainierte Modell wird anschließend für jede Zielaufgabe separat
feinjustiert, meist mit nur minimalen architektonischen Anpassungen
(task-spezifische Input-Transformationen).

Wichtig für die Einordnung: Ein *"chat-fähiges"* Sprachmodell im heutigen Sinn
existierte zu diesem Zeitpunkt konzeptionell noch gar nicht. GPT-1 wurde nicht
gebaut, um Dialoge zu führen oder Instruktionen zu befolgen, sondern um zu
zeigen, dass sich aus reinem, unüberwachtem Sprachverständnis übertragbare
Repräsentationen für klassische NLP-Aufgaben gewinnen lassen. Das ist ein
Gedanke, der der Information-Retrieval-Tradition — der Suche nach
übertragbaren, aufgabenunabhängigen Repräsentationen von Text — näher steht,
als es die heutige, oft mit ChatGPT gleichgesetzte Wahrnehmung von "GPT"
vermuten lässt.

Der Berührungspunkt zu meiner eigenen Dissertation (2016, probabilistisches
Modell für Collaborative Information Retrieval) ist kein direkter —
Sprachmodelle im heutigen Sinn spielten dort keine Rolle. Aber
Textklassifikation, das Lernen von Modellparametern aus
natürlichsprachlichen Daten und die Suche nach relevanten
Repräsentationen sind seit jeher Kernthemen des Information Retrieval —
eine Linie, die sich bis in heutige RAG-Systeme fortsetzt, wo IR als
Retrieval-Komponente wörtlich wieder auftaucht.

Erst der nächste Meilenstein (3.2, TinyInstruct — Instruktions-
Feinjustierung durch maskierten Loss) verwandelt dieses Prinzip in einen
Instruction-Follower; die dann in 3.3 (TinyChat) folgende Präferenz-
Ausrichtung ist die zweite Schicht, die aus einem Instruction-Follower
einen konsistenten Assistenten macht.

## 😮 Der Wow-Effekt: Was ein reines Sprachmodell kann — und was nicht

*[Platzhalter — Beispiel-Textfortsetzungen des lokal trainierten Modells
einfügen]*

```
Prompt:       "and so she went on"
Fortsetzung:  [Platzhalter]

Prompt:       "Was ist die Hauptstadt von Frankreich?"
Fortsetzung:  [Platzhalter — zeigt vermutlich, dass das Modell die Frage
               NICHT beantwortet, sondern nur plausibel fortsetzt]
```

Genau dieser Kontrast — flüssige, plausible Fortsetzungen, aber keine
Fähigkeit, eine Frage als Frage zu erkennen und gezielt zu beantworten — ist
die Brücke zum nächsten Unterkapitel.

## 🧠 Was du baust

- Ein Decoder-only Transformer (Post-LN, GPT-1-Architektur) — dieselbe
  Grundarchitektur wie in `07_Transformer`, jetzt aber trainiert auf echten
  Webtext-Daten (FineWeb-Edu) statt auf Spielzeugbeispielen
- Ein vollständiges Trainings-Setup: Tokenisierung, Padding-Maskierung
  (Attention *und* Loss), Mixed-Precision-Training
- Reine Nächstes-Token-Generierung per Top-k-Sampling — ganz ohne
  Instruktionsfähigkeit

> ⚠️ **Bewusster Bruch mit dem "ohne Frameworks"-Prinzip der Teile 1 und 2.**
> Ab hier verlassen wir bewusst die reine Von-Grund-auf-Philosophie: Bei
> Modellen dieser Größenordnung ist das Nachbauen der Low-Level-Mechanik
> (CUDA-Kernel, verteiltes Training, Tokenizer) nicht mehr lehrreich, sondern
> nur noch Infrastrukturarbeit. Was bleibt, ist das Verständnis der
> Architektur- und Trainings-Entscheidungen — nicht mehr jede Zeile
> Low-Level-Code. Details dazu im Kopf von `train_gpt_mini.py`.

## 🚀 Schnelleinstieg

```bash
python 03_AgenticSystems/01_LLMGrundlagen/src/train_gpt_mini.py --profile laptop
```

Voraussetzungen: `torch`, `transformers`, `datasets`, `tqdm`
(`pip install torch transformers datasets tqdm`)

## 📚 Quellen

- Radford, A., Narasimhan, K., Salimans, T., Sutskever, I. (2018).
  *Improving Language Understanding by Generative Pre-Training.* OpenAI.

## ✏️ Übungen

*[Platzhalter]*

## ➡️ Grenzen dieses Meilensteins

GPT-1.5 vervollständigt Text plausibel, folgt aber keiner Instruktion und
führt keinen Dialog. Kapitel 3.2 zeigt, wie ein zusätzlicher Trainingsschritt
(Masking-basierte Feinjustierung) genau diese Lücke schließt.