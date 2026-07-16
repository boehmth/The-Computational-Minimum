# 🗺️ Roadmap: Das Computational Minimum — Teil 2

Ein Lehrpfad in **acht Meilensteinen**, der zeigt, wie moderne KI wirklich funktioniert — vom einfachsten neuronalen Netz (Perceptron, 1958) bis zu einem eigenen kleinen GPT-artigen Sprachmodell.

Zielgruppe: **Abiturienten und Studienanfänger**, die Mathematik auf Oberstufen­niveau beherrschen und Python grundlegend können. Jeder Meilenstein baut auf dem vorherigen auf und **behebt eine konkrete Schwäche des Vorgängers**.

---

## 🎬 Die große Erzählung: Vom Darstellen über das Erkennen zum Verstehen

Diese Reihe ist Teil einer größeren Erzählung. Sie folgt einem klaren Dreischritt:

> **Teil 1** (separate Reihe): **Darstellen** — wie Zeichen, Texte und Zahlen in einem Computer gespeichert, übertragen und verarbeitet werden. Information, Kodierung, Algorithmen, Berechenbarkeit, Rechnerarchitektur, Compiler, Netzwerke.
>
> **Teil 2** (diese Reihe): **Erkennen** *(Meilenstein 1–3)* und **Verstehen** *(Meilenstein 4–8)*.

Am Ende von Teil 1 kann der Computer Text **einlesen und übertragen**. In den Meilensteinen 1–3 dieser Reihe lernt er, Text zu **erkennen** (z. B. handgeschriebene Ziffern). Ab Meilenstein 4 geht es darum, Text auch zu **verstehen** — Bedeutung erfassen, Sätze bilden, eigene Texte erzeugen.

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

## 📚 Aktueller Stand

- [x] **Meilenstein 1**: Perceptron
- [x] **Meilenstein 2**: Multi-Layer Perceptron (MLP)
- [x] **Meilenstein 3**: Convolutional Neural Network (CNN)
- [x] **Meilenstein 4**: Word Embeddings (Word2Vec)
- [ ] Meilenstein 5: Recurrent Neural Network (RNN)
- [ ] Meilenstein 6: Seq2Seq mit Attention
- [ ] Meilenstein 7: Transformer
- [ ] Meilenstein 8: Mini-GPT

Optionaler Bonus-Meilenstein 9: **„Vom Basismodell zum Chatbot"** (Instruction Tuning, RLHF) — konzeptionell, ohne eigenen Code.

---

## 📖 Wie du dieses Repository durcharbeitest

1. Lies die README des jeweiligen Ordners von oben nach unten.
2. Führe das Programm aus (`python main.py` bzw. das dort angegebene Skript).
3. Beobachte die Ausgabe und vergleiche sie mit den Erwartungen im Text.
4. Arbeite die **Übungen am Ende des Kapitels** durch — sie sind der wichtigste Lernteil.
5. Geh erst dann zum nächsten Meilenstein weiter.

Viel Spaß beim Durcharbeiten!