# KI-Meilenstein 7: Der Transformer

> **🎯 Warum ist das cool?**
> Wir werfen die Rekurrenz komplett über Bord und behalten nur die **Attention**. Das Ergebnis ist die Architektur, auf der heute *alles* aufbaut — ChatGPT, Claude, Gemini, DeepL, BERT, Stable Diffusion. Und wir sehen, was der zentrale Gedanke von 2017 wirklich war: **„Attention Is All You Need."** Jede Position schaut auf jede andere Position — parallel, ohne Zeitschleife.

> ⚠️ **Hinweis: Dieses Kapitel ist in zwei Phasen aufgeteilt.**
> **Phase 1 (jetzt):** komplette Forward-Architektur mit sichtbarer Multi-Head-Attention — aber **ohne Training**. Das Modell zeigt, wie der Datenfluss aussieht, wie Encoder und Decoder zusammenspielen und wie mehrere Köpfe parallel „schauen". Die Vorhersagen sind zufällig, weil die Gewichte noch nicht angelernt sind — die *Struktur* aber ist vollständig.
> **Phase 2 (Ausblick):** Backward-Pass und Training-Loop. Das ist der aufwendigste Teil (~400 zusätzliche Zeilen inkl. Debugging). Er folgt in einem eigenen Update dieses Kapitels.

## 🌉 Vom Seq2Seq zum reinen Attention-Modell

Im letzten Meilenstein (Seq2Seq mit Attention) hatten wir zwei RNNs, die per Attention miteinander verbunden waren. Attention war ein **Zusatz** neben der Rekurrenz. Sie half dem Decoder, an jede Stelle der Eingabe zurückzuschauen — aber die Wörter wurden immer noch **Schritt für Schritt** durch die RNNs geschickt.

Das war der Flaschenhals. Rekurrenz erzwingt Sequenz: erst Wort 1, dann Wort 2, dann Wort 3. Auf einer modernen GPU mit tausenden Kernen ist das eine massive Verschwendung — der ganze Chip wartet auf einen einzigen Hidden-State.

2017 stellten **Vaswani, Shazeer, Parmar et al.** eine radikale Frage:

> *„Wenn Attention den ganzen Job erledigt — brauchen wir die Rekurrenz überhaupt noch?"*

Die Antwort war ein epochales *„Nein"*. Sie fassten sie im Titel ihres Papers zusammen:

> **„Attention Is All You Need."** (Vaswani et al., 2017)

Der Transformer war geboren. Er wirft die Rekurrenz komplett weg und behält *nur* Attention — jetzt sogar in einer noch mächtigeren Form: **Self-Attention** (jede Position schaut auf *alle* Positionen der eigenen Sequenz) und **Multi-Head-Attention** (mehrere Köpfe schauen parallel unter verschiedenen Blickwinkeln). Und weil kein RNN mehr da ist, kann die gesamte Sequenz **parallel** verarbeitet werden.

---

## 🕰️ Historischer Kontext

| Jahr | Ereignis | Bedeutung |
|------|----------|-----------|
| **2015** | Bahdanau et al.: Attention | Zusatz zum RNN-Seq2Seq — Decoder darf auf Eingabe zurückschauen |
| **2017** | **Vaswani et al.: *„Attention Is All You Need"*** | Der Transformer. Rekurrenz weg, nur Attention |
| **2018** | **BERT** (Devlin et al.) | Erster Encoder-only-Transformer für Textverständnis — SOTA in fast jedem NLP-Benchmark |
| **2018** | **GPT-1** (Radford et al.) | Erster Decoder-only-Transformer als autoregressives Sprachmodell |
| **2019** | GPT-2 (Radford et al.) | 1.5 Mrd. Parameter — erstmals *öffentlich* beeindruckende Textgenerierung |
| **2020** | GPT-3 (Brown et al.) | 175 Mrd. Parameter — Few-Shot-Lernen wird sichtbar |
| **2020** | Vision Transformer (Dosovitskiy et al.) | Transformer schafft es in die Bildverarbeitung |
| **2022** | ChatGPT (OpenAI) | Erste massentaugliche KI-Anwendung — 100 Mio. Nutzer in 2 Monaten |
| **heute** | Claude, Gemini, LLaMA, Mistral, DeepSeek, ... | Alle sind Transformer-Varianten. Die Architektur ist der Konsens. |

Der Transformer ist damit **kein Zwischenschritt** wie RNN oder Seq2Seq — er ist der **aktuelle Standard**. Alle großen Sprachmodelle heute sind Varianten davon. Wenn du diese Architektur verstehst, verstehst du den Kern von ChatGPT.

---

## 🧠 Die Aufgabe: Zahl → deutsches Zahlwort (wie in Meilenstein 6)

Wir übersetzen ganze Zahlen von 0 bis 999 in ihre **deutsche Wortform** — **exakt dieselbe Aufgabe** wie im Seq2Seq-Kapitel:

```
   23  ->  drei und zwanzig
  100  ->  einhundert
  342  ->  dreihundert zwei und vierzig
  999  ->  neunhundert neun und neunzig
```

**Warum wieder diese Aufgabe?** Weil wir jetzt einen **direkten Vergleich** zwischen Seq2Seq und Transformer machen können:

1. **Gleiche Daten** — 1 000 Beispiele, 800/200 Train/Test-Split, identischer `data.py` wie in Meilenstein 6.
2. **Gleiche Metrik** — exakter Match auf Testset.
3. **Verschiedene Architekturen** — RNN-Encoder-Decoder mit Attention vs. reiner Attention-Encoder-Decoder.
4. **Attention wird sichtbar wandern** — im Deutschen kommt der *Einer vor dem Zehner* (*„dreiundzwanzig"*). Das Modell muss also nicht linear von links nach rechts arbeiten, sondern **springen**. Perfekt für Multi-Head-Heatmaps.

Der ganze Sinn dieses Kapitels ist die *Architektur*, nicht die Genauigkeit. Deswegen bleibt die Aufgabe klein und die Attention klar sichtbar.

---

## 🧩 Modellarchitektur

Der Transformer besteht aus **vier neuen Bausteinen** gegenüber dem Seq2Seq:

### 1. Scaled Dot-Product Attention

Das Herzstück. Für Query $Q$, Key $K$, Value $V$:

$$
\text{Attn}(Q, K, V) = \text{softmax}\!\left(\frac{Q K^T}{\sqrt{d_k}}\right) V
$$

Für jede Query-Position wird die Ähnlichkeit zu jeder Key-Position berechnet (Dot-Product), daraus über Softmax eine Verteilung gebildet, und die Values werden entsprechend gemischt. Die Skalierung mit $1/\sqrt{d_k}$ verhindert, dass die Dot-Products bei großer Dimension zu extremen Werten explodieren.

### 2. Multi-Head Attention

Statt *einer* großen Attention machen wir **h Attention-Köpfe parallel**. Jeder Kopf projiziert $Q$, $K$, $V$ in einen kleineren Unterraum $d_k = d_{\text{model}}/h$ und macht dort seine eigene Scaled-Dot-Product-Attention. Am Ende werden alle Köpfe konkateniert und linear projiziert.

Warum? Jeder Kopf kann einen **anderen Blickwinkel** lernen — einer schaut auf Positionen, einer auf Wortarten, einer auf lange Distanzen. Wir werden das in den Heatmaps sehen.

### 3. Positional Encoding

Ein Transformer hat keinen Begriff von *Reihenfolge* — er sieht alle Positionen gleichzeitig. Deshalb müssen wir die Position **explizit** in den Vektor hineincodieren. Vaswani et al. nutzen dazu eine schöne Konstruktion aus Sinus und Kosinus in verschiedenen Frequenzen:

$$
\text{PE}(pos, 2i) = \sin\!\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right) \qquad
\text{PE}(pos, 2i+1) = \cos\!\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)
$$

Diese Position-Vektoren werden auf die Token-Embeddings **aufaddiert** — sie sind nicht trainierbar, sondern deterministisch berechnet.

### 4. Layer Normalization + Residual Connections

Jeder Sublayer wird eingerahmt von:
- **Residual Connection** (`x + Sublayer(x)`) — der Gradient kann direkt zurückfließen.
- **Layer Norm** — normiert jeden Token-Vektor auf Mittelwert 0 und Standardabweichung 1.

Ohne diese beiden Tricks lassen sich tiefe Transformer nicht sinnvoll trainieren.

### Gesamt-Architektur (Encoder-Decoder wie in Vaswani 2017)

```
Src-IDs (3 Ziffern)                       Tgt-IDs (Wörter + <sos>)
     │                                             │
     ▼                                             ▼
[ Embedding + Positional Encoding ]      [ Embedding + Positional Encoding ]
     │                                             │
     ▼                                             ▼
 ┌───────────────────────────┐            ┌────────────────────────────┐
 │ Encoder-Block × N          │            │ Decoder-Block × N          │
 │   • Multi-Head Self-Attn   │            │   • Masked Self-Attn       │
 │   • Feed-Forward MLP       │            │   • Cross-Attn (schaut     │
 │   • Layer Norm + Residual  │◀───────────│      auf Encoder)          │
 │                            │            │   • Feed-Forward MLP       │
 └───────────────────────────┘            │   • Layer Norm + Residual  │
                                           └────────────────────────────┘
                                                    │
                                                    ▼
                                       [ Dense: d_model → V_out → Softmax ]
                                                    │
                                                    ▼
                                              nächstes Wort
```

**Größenordnungen (unser konkretes Modell):**
- `d_model = 64` (Vaswani-Original: 512)
- `n_heads = 4` (Vaswani-Original: 8)
- `d_ff = 128` (Vaswani-Original: 2048)
- `N = 2` (Encoder- und Decoder-Blöcke; Vaswani-Original: 6)
- Parameter: **~172 000** (vs. ~40 000 beim Seq2Seq)
- GPT-4 (zum Vergleich): ~1.7 Billionen Parameter, also **10⁷-mal so groß**

Wir sind bewusst deutlich unter dem Original-Paper, weil bei dieser Aufgabe (10 Ziffern → 42 Wörter) alles darüber Overkill wäre.

---

## ⚙️ Training

**Kurz gesagt:** Beim Training minimieren wir den **Cross-Entropy-Verlust** über alle Ziel-Positionen — dieselbe Idee wie beim Seq2Seq, nur ohne Zeitschleife. Weil der Decoder eine **Causal Mask** hat, kann er beim Training alle Positionen *gleichzeitig* verarbeiten, ohne dabei „in die Zukunft zu schauen".

**Teacher Forcing** funktioniert wie beim Seq2Seq: Beim Training bekommt der Decoder als „vorheriges Wort" immer das *wahre* vorherige Wort, nicht seine eigene Vorhersage.

**Optimierer:** Adagrad mit Gradient-Clipping bei ±5, wie in den vorherigen Kapiteln.

> ⚠️ **Phase 1: Training noch nicht implementiert.**
> Der Backward-Pass durch Multi-Head-Attention, Layer Norm und die Encoder-Decoder-Blöcke ist der komplexeste Teil des ganzen Kapitels. Er kommt in Phase 2.
>
> In Phase 1 initialisieren wir das Modell nur mit **zufälligen Gewichten** und zeigen den Forward-Pass. Das genügt, um die *Architektur* sichtbar zu machen.

**Hyperparameter (geplant für Phase 2):**
- Epochen: 60 (wie Seq2Seq)
- Lernrate: 0.1
- Gradient Clipping: ±5

---

## ▶️ So startest du das Programm

```bash
cd Transformer/src
python main.py
```

Das Programm:
1. lädt alle 1 000 Zahl→Wort-Paare,
2. initialisiert einen Encoder-Decoder-Transformer mit **zufälligen Gewichten**,
3. macht einen Forward-Pass durch das Modell und sammelt die Cross-Attention-Gewichte des letzten Decoder-Blocks,
4. rendert für einige Beispiele die **Multi-Head-Attention-Heatmaps** (alle 4 Köpfe parallel).

---

## 📈 Beispielausgabe (echter Forward-Pass, untrainiert)

```
Datensatz: 1000 Paare  |  Eingabe-Vokabular 10  |  Ausgabe-Vokabular 42
Modell:   d_model=64, n_heads=4, n_layers=2, d_ff=128
Parameter: 172,074

PHASE 1: Forward-Only Demo (Modell ist NICHT trainiert)

  n=199  Ziel: einhundert neun und neunzig               Vorhersage (untrainiert): achthundert achthundert achthundert achthundert ...
```

**Und der Star des Kapitels — die Multi-Head-Heatmap:**

Für die Zahl `199` produziert der Decoder in seinem letzten Cross-Attention-Layer für jede Ausgabe-Position **vier verschiedene Attention-Vektoren** (einen pro Kopf), die parallel gerendert werden:

```
              Kopf 0                           Kopf 1                           Kopf 2                           Kopf 3
               |  1    9    9  |                |  1    9    9  |                |  1    9    9  |                |  1    9    9  |
               +---------------+                +---------------+                +---------------+                +---------------+
  achthundert |  O    O    o  |    achthundert |  O    o    o  |    achthundert |  #    o    o  |    achthundert |  o    o    O  |
  achthundert |  o    O    o  |    achthundert |  O    o    o  |    achthundert |  O    o    o  |    achthundert |  o    o    O  |
  achthundert |  o    O    o  |    achthundert |  O    o    o  |    achthundert |  O    o    o  |    achthundert |  o    o    O  |
  achthundert |  o    O    o  |    achthundert |  O    o    o  |    achthundert |  O    o    o  |    achthundert |  o    o    O  |
               +---------------+                +---------------+                +---------------+                +---------------+
  Legende:  .  =  0.00..0.05   *  =  ..0.15   o  =  ..0.35   O  =  ..0.60   #  =  ..1.00
```

**Was hier sichtbar wird — obwohl das Modell untrainiert ist:**

1. **Vier Köpfe schauen alle auf verschiedene Stellen.** Kopf 0 schaut leicht auf die mittlere `9`, Kopf 2 stark auf die erste `1`, Kopf 3 auf die letzte `9`. Jeder Kopf hat einen eigenen zufälligen Blickwinkel. **Nach dem Training** wird dieser Blickwinkel *strukturiert* — z. B. „Kopf 0 = Hunderter-Position, Kopf 3 = Einer-Position".
2. **Die Vorhersagen sind Wortmüll** (*achthundert* für 199). Das ist erwartet — das Modell ist untrainiert.
3. **Aber die Architektur läuft.** Alle Shapes stimmen. Der Encoder-Decoder-Datenfluss ist vollständig. Wenn wir jetzt in Phase 2 den Backward-Pass ergänzen und trainieren, wird sich in genau diesen Heatmaps Struktur zeigen.

**Das ist der pädagogische Höhepunkt von Phase 1:** Wir sehen, wie **Multi-Head-Attention parallel operiert** — und wir sehen, dass alle Ausgabe-Positionen (nicht nur eine nach der anderen wie beim RNN) *gleichzeitig* berechnet werden. Kein Zeitschleifen-Code mehr, nur Matrizen.

---

## ❗ Ehrliche Diskussion: Was Phase 1 zeigt und was nicht

**Was Phase 1 zeigt:**
- Die komplette **Architektur** — Encoder, Decoder, alle Blöcke.
- **Multi-Head-Attention** parallel gerendert.
- **Positional Encoding** in Aktion (sonst würde der Transformer die Reihenfolge nicht kennen).
- **Layer Norm + Residual Connections** — die Stabilisierungs-Tricks.
- **Parallele Verarbeitung** — alle Positionen in einem Rutsch, nicht sequenziell.

**Was Phase 1 nicht zeigt:**
- **Konvergenz**. Wir haben keinen Trainings-Loop.
- **Strukturierte Attention-Muster**. Weil die Gewichte zufällig sind, sind die Heatmaps auch zufällig verteilt.
- **Genauigkeit**. Die Vorhersagen sind Wortmüll.

**Was Phase 2 ergänzen wird:**
- Backward-Pass durch alle Bausteine (Softmax, Multi-Head-Attention, Layer Norm, FFN, Encoder/Decoder-Blöcke).
- Trainings-Loop mit Adagrad und Teacher Forcing.
- Auswertung: Testgenauigkeit vs. Seq2Seq, echte Attention-Heatmaps mit strukturierten Mustern.

**Warum diese Aufteilung?** Ein vollständiger Encoder-Decoder-Transformer inklusive korrekt implementiertem Backward-Pass ist mit ~700 Zeilen NumPy-Code das komplexeste Modell dieser Reihe. Debugging ohne PyTorch-Autograd ist mühsam — deshalb bauen wir zuerst die **Struktur** und zeigen, dass sie stimmt (Shape-Check, Attention-Rendering). Der Trainings-Teil folgt danach, wenn die Basis solide ist.

---

## 📝 Übungen

**1. Ändere die Anzahl der Köpfe.** Setze in `main.py` den `N_HEADS = 2` oder `N_HEADS = 8`. Wie ändert sich die Multi-Head-Heatmap? Wichtig: `d_model` muss durch `n_heads` teilbar sein.

**2. Vergleiche mit einem Seq2Seq-Beispiel.** Führe das Seq2Seq-Programm aus Meilenstein 6 und dann diesen Transformer aus. Vergleiche die Attention-Heatmaps: eine einzelne (Seq2Seq) vs. mehrere parallele Köpfe (Transformer).

**3. Positional Encoding visualisieren.** Rufe `positional_encoding(seq_len=16, d_model=64)` auf und drucke die Matrix aus. Welche Zeile bekommt welche Position? Warum sehen die Dimensionen unterschiedlich aus?

**4. Causal Mask prüfen.** Rufe `make_causal_mask(5)` auf. Warum wird gerade die *obere* Dreiecksmatrix maskiert und nicht die untere?

**5. Andere Layer-Anzahl.** Erhöhe `N_LAYERS = 4`. Wie ändert sich die Parameterzahl? Läuft das Modell noch in einer akzeptablen Zeit?

---

## 🧭 Wo steht der Transformer heute?

**Kurz gesagt:** Der Transformer ist die **dominante Architektur** der modernen KI. Anders als alle vorherigen Kapitel dieser Reihe ist er *kein* Zwischenschritt — sondern der aktuelle Stand.

- **Sprachmodelle**: GPT (1–4), Claude, Gemini, LLaMA, Mistral, DeepSeek, Qwen — alle sind Transformer. Sie unterscheiden sich in Größe, Trainingsdaten und feinen Design-Entscheidungen, aber die Grundarchitektur ist die aus Vaswani 2017.
- **Textverständnis (Encoder-only)**: BERT, RoBERTa, DeBERTa. Werden in fast jeder NLP-Pipeline eingesetzt: Suche, Klassifikation, Named-Entity-Erkennung.
- **Textgenerierung (Decoder-only)**: GPT-Familie und alle modernen LLMs. Hier gehen wir in Meilenstein 8 (Mini-GPT) weiter.
- **Übersetzung (Encoder-Decoder wie hier)**: DeepL, Google Translate seit 2018, T5, mT5, BART.
- **Bildverarbeitung**: Vision Transformer (ViT), Swin Transformer. Konkurrieren zunehmend mit CNNs bei großen Datensätzen.
- **Multimodalität**: CLIP, GPT-4V, LLaVA. Bild und Text im selben Transformer-Framework.

**Was hat sich seit 2017 geändert?** Vor allem drei Dinge, die man aus dem Original-Paper nicht ablesen kann:

1. **Skalierung.** Vaswani hatte ~65 Mio. Parameter. GPT-4 hat ~1.7 Bio. Das ist ein Faktor 25 000. Die Grundarchitektur ist erstaunlich unverändert.
2. **Nur-Decoder statt Encoder-Decoder.** Für Sprachgenerierung ist der Encoder oft überflüssig — man macht alles im Decoder als autoregressives Modell. Das ist der Übergang zu Meilenstein 8 (Mini-GPT).
3. **Effizienz-Verbesserungen.** Flash Attention, Rotary Position Embeddings, Group-Query Attention, Sparse Attention. Alles Optimierungen, um dieselbe Grundidee größer und schneller zu machen.

Wenn du diesen Meilenstein durcharbeitest, hast du **den Kern moderner KI** verstanden. Alles Weitere ist Skalierung und Feinschliff.

---

## 🧠 Abschließende Bemerkungen

Wenn du dir dieses Kapitel angesehen hast — auch in seiner Phase-1-Form —, hast du drei zentrale Ideen der modernen KI in Aktion gesehen:

1. **Attention statt Rekurrenz.** Für Sequenzverarbeitung braucht man kein RNN. Es reicht, alle Positionen gegenseitig aufeinander schauen zu lassen. Das ist der Kern.
2. **Multi-Head als Parallelisierung des Blickwinkels.** Ein einzelner Attention-Kopf ist eine Perspektive. h Köpfe sind h Perspektiven parallel. Genau das macht den Transformer so ausdrucksstark.
3. **Positional Encoding als expliziter Reihenfolge-Hinweis.** Wenn wir die Zeitschleife weglassen, geht die Reihenfolge verloren — es sei denn, wir stecken sie *explizit* in die Vektoren hinein. Sinus/Kosinus ist eine schöne, deterministische Lösung.

Und eine subtile, aber wichtige Einsicht: **Attention ist eine Wichtungs-Operation, kein Speicher.** Anders als beim RNN gibt es keinen versteckten Zustand, der Information über die Zeit trägt. Stattdessen entscheidet jede Query in jedem Moment neu, wo sie hinschauen möchte. Das macht Attention *stateless* — und genau deshalb parallelisierbar.

---

## 🚀 Nächstes Kapitel: Mini-GPT

Der Transformer, den wir hier gebaut haben, ist ein **Encoder-Decoder** — er ist gebaut für Übersetzung. In Meilenstein 8 werfen wir sogar den Encoder weg und behalten nur den **Decoder**. Warum?

Weil für Sprachgenerierung (also *„das nächste Wort vorhersagen"*, wie schon beim RNN) ein Encoder überflüssig ist. Der Decoder allein — mit Self-Attention und Causal Mask — reicht aus. Das ist die Architektur von **GPT** (Radford et al. 2018) und aller nachfolgenden LLMs.

Wir werden ein **Mini-GPT** auf den Grimm-Märchen (Meilenstein 4/5) trainieren und ihm eigene kleine Märchen erzeugen lassen. Der Höhepunkt der Reihe.

---

## 📚 Referenzen

- Bahdanau, D., Cho, K., & Bengio, Y. (2015). *Neural Machine Translation by Jointly Learning to Align and Translate*. ICLR. arXiv:1409.0473.
- **Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). *Attention Is All You Need*. NeurIPS. arXiv:1706.03762.**
- Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2018). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. arXiv:1810.04805.
- Radford, A., Narasimhan, K., Salimans, T., & Sutskever, I. (2018). *Improving Language Understanding by Generative Pre-Training*. OpenAI Technical Report (GPT-1).
- Brown, T. B. et al. (2020). *Language Models are Few-Shot Learners*. NeurIPS (GPT-3). arXiv:2005.14165.
- Dosovitskiy, A. et al. (2020). *An Image is Worth 16×16 Words: Transformers for Image Recognition at Scale*. arXiv:2010.11929.
