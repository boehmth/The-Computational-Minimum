# The Computational Minimum — Teil 2

**Von der einfachen Neuron-Formel bis zum eigenen GPT-artigen Sprachmodell — in acht nachvollziehbaren Meilensteinen.**

---

## 📜 Die Geschichte in einem Absatz

Zwischen 1958 und heute liegt eine der spektakulärsten Erfolgs­geschichten der Informatik. Sie beginnt mit **Frank Rosenblatts Perceptron** — einem einzelnen künstlichen Neuron, das aus Beispielen eine einfache Regel lernen kann — und endet bei **GPT-4** — einem Modell mit **hunderten Milliarden solcher Neuronen**, das Sprache beherrscht, programmiert, argumentiert und Bilder erzeugt. Dazwischen liegen sechs Jahrzehnte Forschung, ein *KI-Winter*, ein *Backpropagation-Durchbruch*, die *ImageNet-Revolution* und schließlich der *Transformer*. Diese Reihe zeichnet diesen Weg **in acht kleinen, selbst programmierten Modellen** nach. Jeder Meilenstein beantwortet eine konkrete Frage — und jede Antwort öffnet die nächste Frage.

> **Ein bemerkenswerter Zufall:** Vom Perceptron (1958) bis zu GPT-1 (2018) sind es genau **60 Jahre Grundlagenforschung** — genauso lang wie von der Entdeckung des Elektrons (1897) bis zum ersten Transistor (1947). Alles, was danach kam — GPT-2, GPT-3, ChatGPT, Claude, LLaMA, DeepSeek, autonome Agenten — sind **Anwendungen und Skalierungen** genau der Ideen, die in dieser Reihe stecken.

---

## 🎬 Die Dreiteilung der ganzen Reihe

Diese Reihe ist Teil eines größeren Projekts in drei Teilen. Zusammen bilden sie einen Bogen von den zeitlosen Grundlagen der Informatik bis zur KI der Gegenwart:

| Teil | Zeitraum | Thema | Fokus |
|------|----------|-------|-------|
| **1** | *ewig gültig* | **Darstellen** | Informations­theorie, Kodierung, Algorithmen, Berechenbarkeit, Rechnerarchitektur, Compiler, Netzwerke |
| **2** *(hier)* | **1958 → 2018** *(60 Jahre neuronale Netze)* | **Erkennen + Verstehen** | Perceptron → Transformer → Mini-GPT |
| **3** | **2018 → heute** *(das letzte Jahrzehnt der Anwendungs­welle)* | **Anwenden + Skalieren** | LLMs im Detail, Domänen-Transformer für Zeitreihen und tabellarische Daten, Reasoning-Modelle (DeepSeek-R1), Agenten mit LLM als Gehirn |

Anders gesagt:
- **Teil 1** klärt: *„Wie funktioniert ein Computer überhaupt?"* (zeitlos)
- **Teil 2** klärt: *„Wie kommt aus dem Computer eine lernende Maschine?"* (60 Jahre — endet mit dem Grundprinzip von GPT)
- **Teil 3** klärt: *„Was hat man daraus gebaut, und was kommt als Nächstes?"* (10 Jahre — endet in der Gegenwart)

---

## 🧭 Die acht Fragen, die zu GPT führen

Man kann die Reihe als eine Kette von acht Fragen lesen. Jede Frage wird durch das nächste Modell beantwortet, und jede Antwort führt zur nächsten Frage.

1. **Was heißt „lernen" für eine Maschine überhaupt?** → *Perceptron (1958):* Ein einzelnes Neuron passt Gewichte anhand von Fehlern an. Das kleinstmögliche lernende System.
2. **Wie geht das für Aufgaben, die keine Gerade lösen kann?** → *MLP + Backpropagation (1986):* Mehrere Schichten, nicht-lineare Aktivierungen — und der Algorithmus, mit dem bis heute jedes tiefe Netz trainiert wird.
3. **Wie kann ein Computer geschriebenen Text lesen — als Pixel auf Papier?** → *CNN (1998):* Faltung, Weight Sharing, Pooling. LeCuns LeNet las in den USA Postleitzahlen; wir lesen MNIST-Ziffern.
4. **Der Computer kann jetzt Buchstaben erkennen — aber was **bedeutet** ein Wort?** → *Word2Vec (2013):* Wörter werden Punkte in einem Bedeutungs­raum. Mit ihnen kann man **rechnen**: `König − Mann + Frau ≈ Königin`.
5. **Bedeutung ist gut — aber Sprache ist eine Reihenfolge. Wie fasst man das?** → *RNN (Elman 1990, Mikolov 2010):* Ein Netz mit Gedächtnis, das Wort für Wort liest und selbst welche erzeugt.
6. **Wie übersetzt man ganze Sätze, nicht nur einzelne Wörter?** → *Seq2Seq + Attention (Sutskever 2014, Bahdanau 2015):* Encoder-Decoder-Struktur, „schau nochmal auf jedes Eingabewort". Der Kern der modernen Übersetzung (Google Translate 2016).
7. **Rekurrenz ist langsam. Geht das auch parallel?** → *Transformer (Vaswani 2017):* „Attention Is All You Need". Rekurrenz weg, ganze Sequenzen auf einmal — die GPU wird endlich richtig ausgenutzt.
8. **Was passiert, wenn man das riesig skaliert?** → *Mini-GPT (Radford 2018):* Ein Transformer sagt das nächste Wort vorher, milliardenfach. Aus dem 8. Meilenstein wird — mit genug Daten und Rechnern — ChatGPT.

Der Bogen ist damit klar: **Lernen (1) → Nicht-Linearität (2) → Bilder & Schrift (3) → Bedeutung (4) → Reihenfolge (5) → Übersetzung (6) → Parallelität (7) → Skalierung (8).**

---

## 🎯 Was du am Ende können und verstehen wirst

Du wirst nicht nur wissen, *wie* GPT funktioniert — du wirst jeden Baustein davon **selbst programmiert** haben:

- Neuronen und Gewichts­updates aus dem Nichts,
- Backpropagation von Hand hergeleitet,
- Faltungs­filter, die sich zu Kantendetektoren entwickeln,
- Wortvektoren, die semantische Analogien lösen,
- ein RNN, das dir Grimm-artige Sätze schreibt,
- Attention-Heatmaps, die zeigen, worauf das Modell gerade *schaut*,
- ein Transformer, der die letzten drei Kapitel in einem einzigen Sprung zusammenfasst,
- ein winziges GPT, das aus deiner eigenen Textdatei Fortsetzungen erfindet.

Und vor allem: du wirst wissen, **warum** jeder dieser Bausteine erfunden wurde, welche Grenze er überwindet, und **was von ihm heute noch übrig ist** (bei manchen: alles, bei anderen: nur die Idee).

---

## 📍 Wo in der Reihe ist das hier?

Dieses Projekt ist **Teil 2 von drei**. Der aktuelle Bogen dieser Reihe:

*„Zeichen darstellen (Teil 1) → Zeichen erkennen (Kap. 1–3) → Zeichen verstehen (Kap. 4–8) → in Anwendungen skalieren (Teil 3)"*.

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

# Meilenstein 5 – Char-RNN (Grimm-Märchen, erzeugt eigenen Text)
cd ../../RNN/src
python main.py

# Meilenstein 6 – Seq2Seq + Attention (Zahl → deutsches Zahlwort)
cd ../../Seq2Seq/src
python train.py
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
| 5 | `RNN/` | Elman 1990 / LSTM 1997 / Mikolov 2010 — Sequenzen und Gedächtnis | Grimm-Märchen | ✅ |
| 6 | `Seq2Seq/` | Bahdanau 2015 — Encoder/Decoder + Attention | Zahlenwörter | ✅ |
| 7 | `Transformer/` | Vaswani 2017 — Self-Attention, parallel | Zahlenwörter | ⏳ |
| 8 | `MiniGPT/` | Radford 2018 — Autoregressives Sprachmodell | Grimm-Märchen | ⏳ |

Ausführlicher Überblick in [`ROADMAP.md`](ROADMAP.md). Die Positionierung und Motivation der ganzen Reihe steht im [Vorwort (PREFACE.md)](PREFACE.md).

---

## 🔭 Ausblick auf Teil 3 (in Vorbereitung)

Wenn du am Ende dieser Reihe angekommen bist, hast du **das Fundament**, auf dem alle heutigen Sprachmodelle stehen. Aber die spannende Frage ist: **Was hat man daraus gebaut?** Genau darum geht es in Teil 3:

- **LLMs im Detail** — Skalierungs­gesetze, Datenmengen, Instruction Tuning, RLHF/DPO. Wie wird aus einem Mini-GPT ein ChatGPT?
- **Domänen-Transformer** — dieselbe Architektur, andere Daten: **Zeitreihen** (TimeGPT, Chronos), **tabellarische Daten** (TabPFN), **Proteine** (AlphaFold-Nachfolger).
- **Reasoning-Modelle** — DeepSeek-R1, OpenAI o1: LLMs, die **erst nachdenken**, bevor sie antworten.
- **Agenten** — LLMs als Gehirn, das Werkzeuge benutzt: Suche, Code, APIs, den Browser. Der Übergang von *Text produzieren* zu *Aufgaben erledigen*.

Teil 3 setzt Teil 2 voraus. Wer die Meilensteine 1–8 durchgearbeitet hat, hat das Vokabular und die Intuition, um diesen zeitgenössischen Fragen zu folgen.

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