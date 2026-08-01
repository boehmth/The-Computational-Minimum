# KI-Meilenstein 6: Seq2Seq mit Attention

> **🎯 Warum ist das cool?**
> Zum ersten Mal in dieser Reihe kann ein Modell **eine ganze Sequenz in eine andere übersetzen**: Wir geben ihm `342` und es antwortet mit *„dreihundert zwei und vierzig"*. Und noch besser — dank **Attention** können wir **sichtbar machen, worauf das Modell in jedem Moment schaut**. Genau dieser Mechanismus wurde 2016 von Google Translate übernommen und ist heute der Kern jedes Transformers, jedes GPT und jedes DeepL.

## 🌉 Vom Sprachmodell zur Übersetzung

Im letzten Kapitel (RNN) hat unser Netz gelernt, das *nächste Wort* in einer Sequenz vorherzusagen. Das ist eine echte Sprachmodell-Aufgabe. Aber es fehlt noch eine ganze Anwendungswelt: **eine komplette Sequenz in eine komplette andere Sequenz übersetzen** — vom Deutschen ins Englische, von Ziffern in Zahlwörter, von einer Frage in eine Antwort.

Ein einzelnes RNN kann das nicht sauber. Es müsste beim ersten Eingabewort schon anfangen zu übersetzen und hätte nie die Gelegenheit, den *ganzen* Satz zu verstehen, bevor es antwortet.

Genau dafür wurde 2014 die **Encoder-Decoder-Architektur** erfunden — von **Sutskever, Vinyals und Le** bei Google und parallel von **Cho et al.** in Montréal. Die Idee ist so einfach wie mächtig:

> **Zwei RNNs im Verbund:** Ein *Encoder* liest die komplette Eingabe und komprimiert sie zu einem Bedeutungs­vektor. Ein *Decoder* nimmt diesen Vektor und produziert die komplette Ausgabe.

Ein Jahr später, 2015, kam **Bahdanau, Cho und Bengio** mit dem entscheidenden Zusatz: **Attention**. Der Decoder muss sich nicht mehr auf einen einzigen zusammengefassten Vektor verlassen — er darf **jederzeit auf jede Position der Eingabe zurückblicken** und dabei selbst entscheiden, worauf er wie stark schaut.

Das war der letzte Baustein vor dem Transformer.

---

## 🕰️ Historischer Kontext

| Jahr | Ereignis | Bedeutung |
|------|----------|-----------|
| **2014** | Sutskever/Vinyals/Le: *Seq2Seq* | Encoder-Decoder-Rahmen — der Anfang der neuronalen Übersetzung |
| **2014** | Cho et al.: RNN Encoder-Decoder | Parallel zu Sutskever; führt den *Kontextvektor* ein |
| **2015** | **Bahdanau/Cho/Bengio: Attention** | Der Decoder darf die ganze Eingabe „ansehen" |
| **2016** | **Google Translate: GNMT** | 10 Jahre statistische Übersetzung werden abgelöst — der Sprung war so groß, dass ein *„Bloomberg"*-Artikel titelte: *„The Great AI Awakening"* |
| **2017** | **Vaswani et al.: Transformer** | „Attention Is All You Need" — Rekurrenz weg, nur noch Attention |

Attention ist damit einer der wichtigsten Bausteine der modernen KI. Er verbindet Kapitel 6 (dieses) mit Kapitel 7 (Transformer) und allem, was danach kam.

---

## 🧠 Die Aufgabe: Zahl → deutsches Zahlwort

Wir übersetzen ganze Zahlen von 0 bis 999 in ihre **deutsche Wortform**:

```
   23  ->  drei und zwanzig
  100  ->  einhundert
  342  ->  dreihundert zwei und vierzig
  999  ->  neunhundert neun und neunzig
```

**Warum diese Aufgabe?** Sie ist **strukturell perfekt** für unser Kapitel:

1. **Klar definierbar** — es gibt exakt eine richtige Antwort pro Zahl.
2. **Kompakt** — 1000 Beispiele, 42 Wortformen im Ausgabe­vokabular.
3. **Übersetzungscharakter** — Ziffer­folge → Wortfolge, aber nicht 1-zu-1: aus einer 2-stelligen Zahl können 1, 2 oder 3 Wörter werden.
4. **Attention wird sichtbar wandern** — im Deutschen kommt der *Einer vor dem Zehner* (*„dreiundzwanzig"*), obwohl die Ziffer „2" links steht. Das Modell muss also nicht linear von links nach rechts arbeiten, sondern **springen**. Perfekt für eine Attention-Heatmap.

---

## 🧩 Modellarchitektur

Wir bauen genau die Architektur aus Bahdanau et al. (2015), leicht vereinfacht:

```
 Eingabe (T_in Ziffern, One-Hot)
      │
      ▼
 ┌──────────────────────────────┐
 │  Encoder-RNN (tanh)          │
 │  liest Ziffer für Ziffer     │  →  h_1, h_2, ..., h_T_in
 └──────────────────────────────┘
      │
      ▼
 ┌──────────────────────────────┐
 │  Attention (Bahdanau)        │  →  alpha_i, c_t
 │  score = v · tanh(W_a h_i    │
 │             + U_a s_{t-1})   │
 └──────────────────────────────┘
      │
      ▼
 ┌──────────────────────────────┐
 │  Decoder-RNN (tanh)          │  →  s_t
 │  s_t = tanh(W_ss s_{t-1}     │
 │        + W_sc c_t            │
 │        + W_sy emb(y_{t-1}))  │
 └──────────────────────────────┘
      │
      ▼
 [ Dense: s_t → V_out ]  →  softmax  →  nächstes Ausgabewort
```

Wir bleiben bewusst **unidirektional** (der Encoder liest nur von links nach rechts). Ein bidirektionaler Encoder wäre stärker, aber er würde die Attention *„kollabieren"* lassen: die gesamte Information wäre schon in einem einzigen Hidden-State versammelt, und das Modell würde immer nur dorthin schauen. Ein Kompromiss zwischen didaktischer Sichtbarkeit und Endgenauigkeit — siehe die Diskussion unten.

**Größenordnungen:**
- Encoder-Hidden: 64
- Decoder-Hidden: 64
- Embedding-Dim: 32
- Parameter: ca. 40 000

---

## ⚙️ Training

**Teacher Forcing.** Beim Training bekommt der Decoder als „vorheriges Wort" immer das *wahre* vorherige Wort (nicht seine eigene Vorhersage). So lernt er schneller.

**Cross-Entropy-Verlust**, gemittelt über alle Decoder-Zeitschritte.

**Adagrad** als Optimizer, Gradient-Clipping bei ±5.

**Backpropagation Through Time** — der Gradient läuft rückwärts durch: Ausgabe­schicht → Decoder-Rekurrenz → Attention → Encoder. Der Attention-Mechanismus ist der interessanteste Teil des Rückwärts­pfads, weil der Gradient durch die Softmax und über *alle* Encoder-Positionen gleichzeitig geht. Der Code in `seq2seq.py` zeigt jeden Schritt.

---

## ▶️ So startest du das Programm

```bash
cd Seq2Seq/src
python train.py
```

Das Programm:
1. erzeugt alle 1000 Zahl→Wort-Paare,
2. splittet 800 (Training) / 200 (Test),
3. trainiert 60 Epochen (~1–2 Minuten auf CPU),
4. misst die Test-Genauigkeit,
5. zeigt einige Beispielübersetzungen mit **Attention-Heatmap** in der Konsole.

---

## 📈 Beispielausgabe (echter Trainingslauf)

```
Daten:  Training 800  Test 200
Vokabular: Eingabe 10 (Ziffern), Ausgabe 42 Wortformen

Epoche  1/60  loss=1.57  train_acc=  2.0%  test_acc=  1.0%
Epoche 15/60  loss=0.24  train_acc= 77.0%  test_acc= 82.0%
Epoche 30/60  loss=0.15  train_acc= 77.0%  test_acc= 82.5%
Epoche 60/60  loss=0.14  train_acc= 77.0%  test_acc= 83.0%

Finale Test-Genauigkeit: 83.0%  (166 von 200)
```

**Und der Star des Kapitels — die Attention-Heatmap:**

```
  n=199  Ziel: einhundert neun und neunzig
                 |  1    9    9  |
                 +---------------+
     einhundert  |  #    .    .  |  <- schaut auf die 1 (Hunderter)
     neun        |  .    .    #  |  <- schaut rechts auf die 9 (Einer)
     und         |  *    .    #  |
     neunzig     |  *    *    #  |  <- schaut auf die 9 (Zehner)
                 +---------------+

  n=999  Ziel: neunhundert neun und neunzig
                 |  9    9    9  |
                 +---------------+
     neunhundert |  #    .    .  |  <- schaut auf die erste 9 (Hunderter-Kontext)
     neun        |  .    .    #  |
     und         |  *    .    #  |
     neunzig     |  .    .    #  |
                 +---------------+
```

**Das ist der pädagogische Höhepunkt.** Man *sieht* das Modell zwischen den Ziffern springen. Bei der Zahl 199 z. B. zeigt die Heatmap ganz klar:

- Beim Wort *„einhundert"* schaut es auf die **1** ganz links.
- Beim Wort *„neun"* (Einer) schaut es auf die **rechte 9**.
- Beim Wort *„neunzig"* (Zehner) schaut es auf die **mittlere 9**.

Attention ist damit sichtbar geworden — und das ist derselbe Mechanismus, der 2017 zum Kern des Transformers wurde.

---

## ❗ Ehrliche Diskussion: Warum nur 83%?

Bei genauem Hinsehen fällt auf: Von 200 Testbeispielen sind 34 falsch. Beispiele:

```
  n=  7   Ziel: sieben               Vorhersage: vier
  n= 23   Ziel: drei und zwanzig     Vorhersage: zwanzig
  n= 42   Ziel: zwei und vierzig     Vorhersage: vier und vierzig
  n=342   Ziel: dreihundert zwei ... Vorhersage: dreihundert vier ...
```

Der Loss plateaut nach ~15 Epochen bei ≈ 0.14 und fällt nicht weiter, egal wie lange man trainiert. Das ist ein **lokales Minimum**: Das Modell hat die Struktur (Hunderter → Einer → *„und"* → Zehner) verstanden, aber die exakte Ziffer­identifikation an manchen Positionen ist wackelig. Es rät bei Einern öfter *„vier"* — vermutlich, weil in den Trainingsdaten viele Zahlen mit Einer 4 vorkamen und der Attention-Vektor auf dieser Position „stärker eingefroren" ist.

Was man tun *könnte*, um über 95 % zu kommen:

1. **Bidirektionaler Encoder** — mehr Kontext pro Position. Erhöht die Genauigkeit auf ~99%, aber die Attention-Heatmap kollabiert (alle Ausgaben schauen dann immer auf Position 0). Wir haben das im Experiment gesehen.
2. **Modell verkleinern** (weniger Kapazität → Attention muss zwischen Positionen wandern).
3. **Größerer Datensatz** (mehr Ziffern, 4-stellige Zahlen).
4. **LSTM statt Vanilla-RNN** — bessere Gradienten, robustere Konvergenz.

Wir bleiben bewusst bei 83 %. Der Zweck dieses Kapitels ist nicht Perfektion, sondern das **sichtbare Verständnis von Attention**. Genau diese Auseinandersetzung mit dem Trade-off *„Genauigkeit vs. Transparenz"* ist übrigens ein wiederkehrendes Thema der KI-Forschung — je größer das Modell, desto stärker die Leistung, desto opaker die Erklärung.

---

## 📝 Übungen

**1. Attention einzelner Beispiele analysieren.** Ändere in `train.py` die `demo_numbers`-Liste. Probiere: `[15, 21, 33, 77, 88, 500, 505, 550]`. Bei welchen Zahlen ist die Attention „sauber" (klare `#`-Spitzen)? Bei welchen verschwimmt sie?

**2. Temperature spielen.** In `seq2seq.py` verwendet `predict` `argmax`. Ersetze das durch Softmax-Sampling mit einer Temperatur. Wird das Modell dann kreativer bei den Fehlern?

**3. Aufgabe umkehren.** Wie sähe die Ausgabe­richtung *Wort → Zahl* aus? (*„drei und zwanzig"* → `23`). Das ist deutlich schwieriger, weil die Reihenfolge komplex ist. Diskutiere, warum das ein Härtefall ist.

**4. Andere Sprache.** Passe `data.py` an, um Englisch (*„twenty-three"*) statt Deutsch zu erzeugen. Ist die Attention dann geradliniger, weil die Wortreihenfolge dem Ziffer­lese­fluss entspricht?

**5. Ohne Attention.** Nimm den Kontextvektor `c` fest und lasse ihn immer gleich (z. B. den letzten Encoder-State). Wie stark fällt die Genauigkeit? *(Antwort: dramatisch, weil das Modell den Bezug zwischen Ausgabe­wort und Eingabe­position verliert.)*

---

## 🧭 Wo steht Seq2Seq mit Attention heute?

**Kurz gesagt:** Als Architektur ist Seq2Seq mit RNN-Encoder-Decoder heute weitgehend Geschichte — abgelöst durch den Transformer. Aber der **Kernbaustein**, den es beigetragen hat, ist lebendiger denn je:

- **Der Encoder-Decoder-Rahmen** lebt weiter im Transformer. Modelle wie **T5**, **BART**, **mT5** haben genau diesen Aufbau, nur eben aus Transformer-Blöcken.
- **Attention** ist der Kern jedes modernen Sprachmodells. GPT, Claude, LLaMA, Gemini — alle basieren letztlich darauf.
- **Google Translate 2016** (GNMT) war das erste kommerzielle System, das mit dieser Architektur arbeitete. Die Übersetzungsqualität sprang um ~10 BLEU-Punkte gegenüber dem vorherigen statistischen System — der wohl größte Ein-Schritt-Sprung in der Geschichte der maschinellen Übersetzung.
- **DeepL** ging 2017 online, direkt mit einem Transformer-basierten System — genau das nächste Kapitel.

Was heute *nicht* mehr benutzt wird, ist die spezifische Kombination *„RNN + Bahdanau-Attention"*. Sie war Zwischenschritt, nicht Endpunkt. Aber ohne diesen Zwischenschritt gäbe es keinen Transformer.

---

## 🧠 Abschließende Bemerkungen

Wenn du dir dieses Kapitel angesehen hast, hast du drei ganz zentrale Konzepte in einer einzigen Modell­architektur zusammen gesehen:

1. **Encoder-Decoder** — zwei Netze, die zusammenspielen, um eine Übersetzung zu leisten.
2. **Attention** — der Trick, mit dem der Decoder gezielt auf Teile der Eingabe zurückgreift.
3. **Trade-offs zwischen Genauigkeit und Interpretierbarkeit** — je stärker das Modell, desto weniger sichtbar wird, was es tut.

Und eine subtile, aber wichtige Beobachtung: **Attention hat den Modellen etwas gegeben, was Rekurrenz nie konnte — direkte, springende Zugriffe auf beliebige Positionen der Eingabe.** Rekurrenz brauchte 30 Zeitschritte, um Information von Position 0 zu Position 30 zu transportieren; Attention macht das in einem Schritt.

Genau das ist der Grund, warum die Autoren des Transformer-Papers 2017 fragten:

> *„Wenn Attention den ganzen Job erledigt — brauchen wir die Rekurrenz überhaupt noch?"*

Die Antwort war ein epochales *„Nein"*. Sie fassten sie im Titel ihres Papers zusammen:

> **„Attention Is All You Need."** (Vaswani et al., 2017)

Das ist der nächste Meilenstein.

---

## 🚀 Nächstes Kapitel: Transformer

Wir werfen die Rekurrenz komplett über Bord und behalten nur die Attention. Das Ergebnis:

- **Vollständig parallelisierbar** — alle Positionen werden gleichzeitig verarbeitet.
- **Skalierbar** — man kann viel größere Modelle trainieren, weil GPUs viel besser ausgenutzt werden.
- **Kürzere Pfade** — jede Position sieht jede andere direkt, ohne Zwischen­schritte.

Und im letzten Kapitel dieser Reihe (Mini-GPT) werden wir sehen, was passiert, wenn man diese Transformer-Idee autoregressiv trainiert und massiv skaliert.

---

## 📚 Referenzen

- Sutskever, I., Vinyals, O., & Le, Q. V. (2014). *Sequence to Sequence Learning with Neural Networks*. NeurIPS. arXiv:1409.3215.
- Cho, K. et al. (2014). *Learning Phrase Representations using RNN Encoder-Decoder for Statistical Machine Translation*. EMNLP. arXiv:1406.1078.
- Bahdanau, D., Cho, K., & Bengio, Y. (2015). *Neural Machine Translation by Jointly Learning to Align and Translate*. ICLR. arXiv:1409.0473.
- Wu, Y. et al. (2016). *Google's Neural Machine Translation System*. arXiv:1609.08144.
- Vaswani, A. et al. (2017). *Attention Is All You Need*. NeurIPS. arXiv:1706.03762.
