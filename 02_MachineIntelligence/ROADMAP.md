# 🗺️ Roadmap: Das Computational Minimum — Teil 2

Ein Lehrpfad in **acht Meilensteinen**, der zeigt, wie moderne KI wirklich funktioniert — vom einfachsten neuronalen Netz (Perceptron, 1958) bis zu einem eigenen kleinen GPT-artigen Sprachmodell.

Zielgruppe: **Abiturienten und Studienanfänger**, die Mathematik auf Oberstufen­niveau beherrschen und Python grundlegend können. Jeder Meilenstein baut auf dem vorherigen auf und **behebt eine konkrete Schwäche des Vorgängers**.

---

## 🎬 Die große Erzählung: Vom Darstellen über das Erkennen zum Verstehen — und dann zu den Anwendungen

Diese Reihe ist Teil eines dreiteiligen Projekts, das den Bogen von den zeitlosen Grundlagen der Informatik bis zur KI der Gegenwart schlägt:

> **Teil 1** (separate Reihe): **Darstellen** — wie Zeichen, Texte und Zahlen in einem Computer gespeichert, übertragen und verarbeitet werden. Information, Kodierung, Algorithmen, Berechenbarkeit, Rechnerarchitektur, Compiler, Netzwerke.
>
> **Teil 2** (diese Reihe): **Erkennen** *(Meilenstein 1–3)* und **Verstehen** *(Meilenstein 4–8)* — 60 Jahre neuronale Netze in acht Meilensteinen.
>
> **Teil 3** (in Vorbereitung): **Anwenden und Skalieren** — was in den letzten 10 Jahren aus diesen Grundlagen gebaut wurde: LLMs im Detail, Domänen-Transformer (Zeitreihen, tabellarische Daten), Reasoning-Modelle wie DeepSeek-R1, Agenten mit LLMs als Gehirn.

Am Ende von Teil 1 kann der Computer Text **einlesen und übertragen**. In den Meilensteinen 1–3 dieser Reihe lernt er, Text zu **erkennen** (z. B. handgeschriebene Ziffern). Ab Meilenstein 4 geht es darum, Text auch zu **verstehen** — Bedeutung erfassen, Sätze bilden, eigene Texte erzeugen. Teil 3 dann fragt: *Was hat man daraus gebaut?*

### 📐 Die schöne Zeitsymmetrie

```
1958 ................................. 2018 ..........  heute
  |                                      |               |
  Perceptron                             GPT-1          GPT-4, DeepSeek,
  (Rosenblatt)                        (Radford)         Agenten, ...
  |                                      |               |
  |          Teil 2: 60 Jahre            |   Teil 3:    |
  |     Grundlagenforschung              |   10 Jahre    |
  |     (dieses Repository)              |  Anwendung    |
```

**60 Jahre vs. 10 Jahre.** Vom Perceptron bis zum ersten GPT dauerte es sechs Jahrzehnte. Von GPT-1 bis GPT-4 waren es fünf Jahre. Diese ungleiche Verteilung — lange Grundlagenphase, dann explosive Anwendungsphase — ist ein wiederkehrendes Muster: es gilt genauso für die 60 Jahre vom Elektron (1897) zum Transistor (1947) und die folgenden 50 Jahre der Halbleiter­revolution.

---

## 🧭 Der rote Faden innerhalb von Teil 2

Jedes Modell wird eingeführt, weil das vorherige an einer klar benennbaren Stelle scheitert:

> **Was das Modell noch nicht kann → das ist genau das Thema des nächsten Meilensteins.**

### Phase A — Erkennen (Kapitel 1–3)

| Nr. | Meilenstein | Neu | Grenze — motiviert nächsten Schritt |
|-----|-------------|-----|--------------------------------------|
| **1** | **Perceptron** (Rosenblatt 1958) | Lernen aus Daten, gewichtete Summe | nur linear trennbare Probleme |
| **2** | **MLP + Backprop** (Rumelhart et al. 1986) | Hidden Layer, nicht-lineare Grenzen | keine Lokalität, keine Translations­invarianz |
| **3** | **CNN** (LeCun 1998) | Faltung, Weight Sharing, Pooling — **Bilder + handgeschriebene Zeichen erkennen** | Wir können Zeichen **lesen** — aber nicht **verstehen** |

### Phase B — Verstehen (Kapitel 4–8)

| Nr. | Meilenstein | Neu | Grenze — motiviert nächsten Schritt |
|-----|-------------|-----|--------------------------------------|
| **4** | **Word Embeddings** (Mikolov 2013) | Wörter als Vektoren, Semantik | ein Wort für sich hat keinen Kontext |
| **5** | **RNN** (Elman 1990; RNN-LM: Mikolov 2010; LSTM: Hochreiter & Schmidhuber 1997) | Sequenzen, Gedächtnis | Info-Bottleneck bei langen Sequenzen |
| **6** | **Seq2Seq + Attention** (Bahdanau 2015) | Encoder/Decoder, Attention | rekurrent = seriell und langsam |
| **7** | **Transformer** (Vaswani 2017) | Self-Attention, parallel trainierbar | rein architektonisch — nun: skalieren! |
| **8** | **Mini-GPT** (Radford 2018) | Autoregressives Sprachmodell | Skalierung, Alignment (Ausblick) |

---

## 🎬 Übergreifende narrative Klammer

Ab **Meilenstein 4** begleiten uns die **Grimmschen Märchen** als roter Faden:

- **Word2Vec** wird darauf trainiert — Wow-Moment: `könig − mann + frau ≈ königin`
- **RNN** generiert grimm-artige Wörter und Satz­anfänge
- **Mini-GPT** schreibt am Ende **sein eigenes kleines Märchen**

Für die Meilensteine **6 (Seq2Seq)** und **7 (Transformer)** verwenden wir stattdessen **Zahlenwörter** (`23 → dreiundzwanzig`) — hier ist die Attention-Visualisierung auf einer klar strukturierten Aufgabe besonders lehrreich.

---

## 🛠️ Technisches Vorgehen

| Bereich | Meilenstein 1–2 | Meilenstein 3–8 |
|---------|-----------------|-----------------|
| Sprache | Deutsch | Deutsch |
| Numerik | Reines Python (Listen) | NumPy |
| Frameworks | keine | keine (kein PyTorch/Keras) |
| Aufbau | `forward` + `backward` selbst geschrieben | `forward` + `backward` selbst geschrieben |
| Datensatz | 2D-Punkte / 9×9-Bitmaps | MNIST 14×14, Grimm-Text, Zahlenwörter |

Wir bauen **nichts** mit vorgefertigten Schichten wie `torch.nn.Conv2d`. Jede Multiplikation ist im Code sichtbar. NumPy wird ab Meilenstein 3 zugelassen, weil reines Python bei größeren Datensätzen zu langsam wird — die Logik bleibt jedoch von Hand geschrieben.

---

## 🧭 Was lebt heute noch — und was nicht mehr?

Ein ehrlicher Blick auf die acht Meilensteine aus der Perspektive **2024/2025**:

| Meilenstein | Status heute | Warum es trotzdem hier drin ist |
|-------------|--------------|--------------------------------|
| **1. Perceptron** | Als eigenständiges Modell obsolet. | Der Kern jedes Neurons in jedem NN — von GPT bis Stable Diffusion. |
| **2. MLP / Backprop** | Ganze Modelle: obsolet. **Backprop: universell.** MLP-Blöcke stecken im Transformer (Feed-Forward). | Backpropagation ist **das** Fundament. Kein modernes NN funktioniert ohne. |
| **3. CNN** | **Weiterhin State-of-the-Art** in Bildverarbeitung, medizinischer Bildanalyse, autonomem Fahren, Embedded. Vision Transformer (ViT) drängen, ersetzen aber nicht überall. | Ewig relevant für alles Visuelle. |
| **4. Word2Vec** | Als Trainings-Methode weitgehend obsolet — abgelöst durch kontextabhängige Embeddings (BERT, GPT). | **Die Idee** „Bedeutung als Position im Vektorraum" ist in allen heutigen Sprachmodellen. Auch **self-supervised learning** wurde durch Word2Vec populär. |
| **5. RNN / LSTM** | Aus der Sprachverarbeitung **weitgehend verschwunden**. Noch in Nischen: Zeitreihen, Signal­verarbeitung, On-Device (Wake-Word). | Die Aufgabe *„nächstes Wort vorhersagen"* ist wortgleich die von GPT. Die Architektur wurde ersetzt, das Ziel nicht. |
| **6. Seq2Seq + Attention** | Der Encoder-Decoder-Rahmen lebt weiter (Transformer-Modelle). RNN-basiertes Seq2Seq: obsolet. | **Attention** wurde der Kern aller modernen Modelle. Google Translate 2016 war der erste große NMT-Erfolg. |
| **7. Transformer** | **Der aktuelle Standard.** ChatGPT, Claude, Gemini, DeepL, BERT, Stable Diffusion — alles Transformer-Varianten. | Wir sind angekommen. |
| **8. Mini-GPT** | Autoregressive Sprachmodelle sind heute die dominante Form („LLMs"). GPT-4, Claude, LLaMA. | Der Höhepunkt dieser Reihe. |

**Ein paar Beobachtungen:**

- Nur **Backprop, CNN und Transformer** sind heute noch direkt produktiv im Einsatz.
- **Word2Vec, RNN, Seq2Seq** sind *„Spuren auf dem Pfad zum Transformer"* — technisch überholt, aber didaktisch unverzichtbar, weil sie die *Ideen* enthalten, die im Transformer zusammenkommen: Embeddings, Kontext, Attention, autoregressive Generierung.
- **Die eigentliche Revolution** war nicht ein einzelnes Modell, sondern die Kombination: Transformer + massive Skalierung + self-supervised Training auf riesigen Textkorpora. Das ist der Weg von GPT-1 (2018) zu GPT-4 (2023).

Genau *deshalb* macht diese Reihe Sinn: um zu verstehen, warum GPT aussieht wie es aussieht, muss man den Weg dorthin kennen.

---

## 📚 Aktueller Stand

- [x] **Meilenstein 1**: Perceptron
- [x] **Meilenstein 2**: Multi-Layer Perceptron (MLP)
- [x] **Meilenstein 3**: Convolutional Neural Network (CNN)
- [x] **Meilenstein 4**: Word Embeddings (Word2Vec)
- [x] **Meilenstein 5**: Recurrent Neural Network (RNN)
- [x] **Meilenstein 6**: Seq2Seq mit Attention
- [~] **Meilenstein 7**: Transformer *(Phase 1 fertig: Forward + Multi-Head-Heatmaps. Phase 2 in Arbeit: Backward + Training)*
- [ ] Meilenstein 8: Mini-GPT

Optionaler Bonus-Meilenstein 9: **„Vom Basismodell zum Chatbot"** (Instruction Tuning, RLHF) — konzeptionell, ohne eigenen Code.

---

## 📖 Wie du dieses Repository durcharbeitest

1. Lies die README des jeweiligen Ordners von oben nach unten.
2. Führe das Programm aus (`python main.py` bzw. das dort angegebene Skript).
3. Beobachte die Ausgabe und vergleiche sie mit den Erwartungen im Text.
4. Arbeite die **Übungen am Ende des Kapitels** durch — sie sind der wichtigste Lernteil.
5. Geh erst dann zum nächsten Meilenstein weiter.

---

## 🔭 Ausblick auf Teil 3

Wer alle acht Meilensteine dieser Reihe durchgearbeitet hat, versteht die **Bausteine** aller heutigen Sprachmodelle. **Teil 3** beschäftigt sich dann mit der Frage, was in den letzten zehn Jahren aus diesen Bausteinen konkret gebaut wurde. Geplante Themen:

| Meilenstein | Thema | Kernidee |
|-------------|-------|----------|
| **T3-1** | **LLMs im Detail** | Skalierungs­gesetze (Chinchilla), Instruction Tuning, RLHF, DPO. Wie wird aus Mini-GPT → ChatGPT? |
| **T3-2** | **Domänen-Transformer** | Dieselbe Architektur, andere Daten: TimeGPT/Chronos (Zeitreihen), TabPFN (Tabellen), AlphaFold-Nachfolger (Proteine). |
| **T3-3** | **Reasoning-Modelle** | DeepSeek-R1, OpenAI o1: Chain-of-Thought, verzögertes Antworten, RL auf Reasoning. |
| **T3-4** | **Multimodalität** | Vision-Language-Models (CLIP, LLaVA, GPT-4V) — Bilder und Text im selben Vektorraum. |
| **T3-5** | **Retrieval-augmented Generation (RAG)** | LLMs mit externem Wissen: Vektor-Datenbanken, semantische Suche. |
| **T3-6** | **Werkzeug-Nutzung** | Function-Calling, Code-Execution — vom Text-Generator zum Aufgabenlöser. |
| **T3-7** | **Agenten** | LLMs als Gehirn, das mehrere Schritte plant, Werkzeuge orchestriert, den Browser bedient. |
| **T3-8** | **Alignment und Sicherheit** | Wie hält man ein System bei der Wahrheit? Constitutional AI, Red-Teaming, Interpretierbarkeit. |

Teil 3 wird stärker als Teil 2 auf **Frameworks** setzen (weil man ein modernes LLM nicht mehr sinnvoll from-scratch bauen kann), aber die Modelle bleiben **klein und interaktiv**, damit man tatsächlich mit ihnen experimentieren kann. Ohne das Verständnis aus Teil 2 wären viele der Ideen in Teil 3 nur Beschwörungs­formeln — mit ihm werden sie transparent.

Viel Spaß beim Durcharbeiten!
