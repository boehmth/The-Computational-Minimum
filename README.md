# The Computational Minimum — Teil 2

**Von der einfachen Neuron-Formel bis zum eigenen GPT-artigen Sprachmodell — in acht nachvollziehbaren Meilensteinen.**

Dieses Projekt ist der **zweite Teil** einer zweiteiligen Reihe, die zeigt, wie moderne KI wirklich funktioniert.

- **Teil 1** (separates Repository): **Darstellen** — wie ein Computer Zeichen, Zahlen und Texte speichert, überträgt und verarbeitet: Informations­theorie, Kodierung, Algorithmen, Berechenbarkeit, Rechnerarchitektur, Compiler, Netzwerke.
- **Teil 2** (dieses Repository): **Erkennen und Verstehen** — wie neuronale Netze aus Rohdaten lernen, was drinsteckt.

Zusammen ergibt das den Bogen: *„Zeichen darstellen (Teil 1) → Zeichen erkennen (Kap. 1–3) → Zeichen verstehen (Kap. 4–8)"*.

Jeder Meilenstein baut auf dem vorherigen auf und behebt eine konkrete Schwäche des Vorgängers. Es werden **keine fertigen Deep-Learning-Frameworks** verwendet — alle Modelle sind von Hand geschrieben, jede Multiplikation ist im Code sichtbar.

---

## 🚀 Schnelleinstieg

```bash
git clone <dieses-Repo>
cd The-Computational-Minimum

# Meilenstein 1 – Perceptron (reines Python)
cd Perceptron/src
python perceptron.py

# Meilenstein 2 – MLP (reines Python)
cd ../../MLP/src
python mlp.py

# Meilenstein 3 – CNN (NumPy, MNIST)
cd ../../CNN/src
pip install numpy scikit-learn
python main.py

# Meilenstein 4 – Word2Vec (Grimm-Märchen)
cd ../../Word2Vec/src
python main.py
```

Die einzige Abhängigkeit ab Meilenstein 3 ist **NumPy** (plus `scikit-learn` für den MNIST-Loader). Kein PyTorch, kein TensorFlow, keine vorgefertigten Schichten.

---

## 🗺️ Übersicht der Meilensteine

### Phase A — Zeichen **erkennen**

| Nr. | Ordner | Thema | Datensatz | Status |
|-----|--------|-------|-----------|--------|
| 1 | `Perceptron/` | Rosenblatt 1958 — Ein Neuron lernt eine Gerade | 2D-Zahlenpaare (`x1 < x2`) | ✅ |
| 2 | `MLP/` | Rumelhart et al. 1986 — Backprop und nicht-lineare Grenzen | 9×9-Bitmaps (A, L, R) | ✅ |
| 3 | `CNN/` | LeCun 1998 — Faltung, Pooling, Zeichenerkennung | MNIST 14×14 | ✅ |

### Phase B — Zeichen **verstehen**

| Nr. | Ordner | Thema | Datensatz | Status |
|-----|--------|-------|-----------|--------|
| 4 | `Word2Vec/` | Mikolov 2013 — Wörter als Vektoren, Semantik | Grimm-Märchen | ✅ |
| 5 | `RNN/` | Elman 1990 / LSTM 1997 / Mikolov 2010 — Sequenzen und Gedächtnis | Grimm-Märchen | ⏳ |
| 6 | `Seq2Seq/` | Bahdanau 2015 — Encoder/Decoder + Attention | Zahlenwörter | ⏳ |
| 7 | `Transformer/` | Vaswani 2017 — Self-Attention, parallel | Zahlenwörter | ⏳ |
| 8 | `MiniGPT/` | Radford 2018 — Autoregressives Sprachmodell | Grimm-Märchen | ⏳ |

Ausführlicher Überblick in [`ROADMAP.md`](ROADMAP.md).

---

## 🎯 Für wen ist das gedacht?

- **Schüler der Oberstufe** mit Interesse an KI, die verstehen wollen, wie ein Sprachmodell wirklich tickt.
- **Lehrkräfte**, die einen roten Faden für einen Wahlpflichtkurs oder eine AG suchen.
- **Alle Neugierigen**, die von Neuronen bis zu Transformer-Attention einen begreiflichen Aufbau wollen — ohne dass Frameworks das Wichtige verstecken.

---

## 🧭 Der rote Faden

Statt zusammen­hanglos Modelle vorzustellen, wird jeder Meilenstein als **Antwort auf ein konkretes Problem** eingeführt:

**Phase A — Erkennen:**
> Perceptron kann nur Geraden ziehen → **MLP löst nicht-lineare Probleme**.  
> MLP kennt keine Nachbarschaft → **CNN nutzt Bildstruktur und erkennt handgeschriebene Zeichen**.  
> Wir können jetzt Zeichen **lesen** — aber wir **verstehen** noch nichts. Zeit, das zu ändern.

**Phase B — Verstehen:**
> Ein Wort für sich hat keine Bedeutung → **Word2Vec repräsentiert Wörter als Vektoren**.  
> Wörter isoliert reichen nicht → **RNN modelliert Reihenfolgen**.  
> RNNs sind seriell und vergessen → **Seq2Seq + Attention verbessern beides**.  
> Rekurrenz ist langsam → **Transformer macht Attention parallel**.  
> Aus Transformer wird → **Mini-GPT: das eigene kleine Sprachmodell**.

So entsteht am Ende nicht nur ein Modell, sondern ein **Verständnis** dafür, warum die KI heute so aussieht, wie sie aussieht.

---

## 📜 Lizenz und Nutzung

Frei für den Bildungs­gebrauch. Beiträge, Übersetzungen und Ergänzungen sind willkommen.