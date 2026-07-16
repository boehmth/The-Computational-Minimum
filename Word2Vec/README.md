# KI-Meilenstein 4: Word Embeddings (Word2Vec)

> **🎯 Warum ist das cool?**
> Nach dem Training kann man mit Wörtern **rechnen wie mit Vektoren**: `König − Mann + Frau ≈ Königin`. Niemand hat dem Modell die Bedeutung der Wörter erklärt — es hat sie allein aus den Kontexten in den Grimmschen Märchen abgelesen. Und genau dieses Prinzip — **Bedeutung aus Kontext** — ist die Grundlage aller heutigen großen Sprachmodelle wie GPT und Claude.

## 🌉 Auf einmal geht es ums Verstehen

Mit diesem Kapitel beginnt **Phase B** der Reihe. Bis hierher konnten wir Zeichen und Wörter *lesen* — als Bytes, als Pixel, als klassifizierbare Muster. Ab jetzt geht es um etwas Neues:

> **Was bedeuten diese Zeichen eigentlich?**

Ein Computer, der ein Handschrift-Foto in die Buchstabenfolge `KOENIG` überführt, weiß immer noch nichts über *Könige*. Für ihn ist das nur eine Kette von sechs Zeichen. Er hat keine Ahnung, dass ein König etwas mit einer Königin zu tun hat, oder dass Könige in einem Schloss wohnen und nicht in einer Zahnbürste.

Das zu ändern ist der Kern dieses und der nächsten Kapitel. Wir beginnen ganz vorne — bei der Repräsentation *einzelner Wörter*.

---

## 📖 Einleitung

Bis jetzt haben wir mit **Bildern** und **Zahlen** gearbeitet — Dinge, die man leicht in einen Vektor stecken kann. Ein Pixel ist eine Zahl, 81 Pixel sind 81 Zahlen. So einfach.

Jetzt kommt Sprache. Und Sprache besteht aus **Wörtern** — und Wörter sind keine Zahlen. Sie sind Symbole. Wie füttert man einem neuronalen Netz das Wort *Königin*? Man kann es ja nicht einfach in eine Matrix stecken.

Der erste Versuch: **One-Hot-Kodierung.**
- Man nummeriert alle Wörter des Vokabulars (z. B. 1636 Wörter).
- Jedes Wort wird ein 1636-Vektor mit einer einzigen `1` an seiner Position und lauter `0` sonst.

Damit kann ein Netz *rechnen* — aber es weiß nichts. Denn:

> One-Hot-Vektoren enthalten **keinerlei Information über Bedeutung**. Der Vektor für *König* steht senkrecht auf dem Vektor für *Königin* — genauso wie er senkrecht auf *Zahnbürste* steht. Aus Sicht des Netzes sind alle Wörter gleich weit voneinander entfernt.

Das ist ein enormes Problem. Und die Lösung ist eine der schönsten Ideen der modernen KI:

> **Wir lernen für jedes Wort einen kleinen Vektor (z. B. 64 Zahlen), der seine Bedeutung repräsentiert — indirekt, aus dem Kontext, in dem das Wort im Text auftaucht.**

Wörter, die in ähnlichem Kontext vorkommen — *König* und *Königin*, *Wald* und *Baum*, *Vater* und *Mutter* — bekommen ähnliche Vektoren. Und dann kann man am Ende sogar **mit Bedeutungen rechnen**:

    König − Mann + Frau ≈ Königin

Diese Idee ist so radikal wie schön: **Bedeutung als Position im Vektorraum.** Sie stammt in ihrer heute gebräuchlichen Form von **Tomáš Mikolov** und Kollegen (Google, 2013) und heißt **Word2Vec**.

---

## 🕰️ Historischer Kontext

Wörter als Vektoren zu repräsentieren ist älter als 2013 — die Idee reicht bis in die 1980er zurück (Hinton u. a., *Distributed Representations*) und findet 2003 einen ersten prominenten neuronalen Ausdruck. Word2Vec ist **nicht** der Erfinder dieser Idee, sondern ihr **radikaler Simplifizierer**.

| Jahr | Ereignis | Was daran neu ist |
|------|----------|-------------------|
| 2003 | **Bengio et al.: Feedforward Neural Language Model (NNLM)** | Ein NN, das das nächste Wort in einem festen Fenster vorhersagt. **Embeddings entstehen als Nebenprodukt** dieser Sprachmodell-Aufgabe. |
| 2010 | **Mikolov et al.: RNN-based Language Model** | Erstes *rekurrentes* Sprachmodell — verarbeitet Wörter *in Reihenfolge*, mit Gedächtnis. (Kommt in Meilenstein 5!) |
| 2013 | **Mikolov et al.: Word2Vec** (Skip-Gram, CBOW) | **Bewusste Vereinfachung**: Kein Sprachmodell mehr, nur noch Embeddings. Kein Hidden Layer, keine volle Softmax — dadurch 1000× schneller als 2003. |
| 2014 | Pennington: GloVe | Alternative Methode über Kookkurrenz-Statistiken |
| 2018+ | ELMo, BERT, GPT | Kontextabhängige Embeddings (jedes Wort bekommt je nach Satz einen anderen Vektor) |

**Kurz gesagt:** Bengio 2003 zeigte, dass ein NN Sprache modellieren *kann*. Mikolov 2010 zeigte, dass RNNs es *besser* können. Und Mikolov 2013 (Word2Vec) sagte: *"Wenn wir nur die Embeddings brauchen — dann sparen wir uns den ganzen Rest."* Das machte Wort-Embeddings zum ersten Mal für jeden zugänglich.

---

## 🧠 Was Word2Vec neu einführt

### 1. Vokabular
Wir zerlegen den Text in **Wörter (Tokens)** und geben jedem einen festen Index 0..V−1. Bei uns: V = 1636.

### 2. Embedding-Matrizen
Zwei Matrizen der Größe V × D (bei uns D = 64):
- `W_in`  — ein Vektor pro Wort als **Zentrumswort**.
- `W_out` — ein Vektor pro Wort als **Kontext-/Negativwort**.

Nach dem Training verwenden wir **`W_in` als Wort-Embedding**.

### 3. Selbstüberwachtes Lernen
Wir müssen **keine Labels von Hand vergeben** — der Text selbst liefert das Trainingssignal:

> Für jedes Wort im Text schauen wir, welche Wörter *in seiner Nähe* stehen. Diese Nachbarschaft ist das Zielsignal.

Diese Idee — **self-supervised learning** — ist die Grundlage aller heutigen großen Sprachmodelle (GPT, BERT, LLaMA).

### 4. Was Word2Vec bewusst *weglässt*

Bengios NNLM (2003) war ein volles **Sprachmodell**: Es sollte die *Wahrscheinlichkeit des nächsten Wortes* über das gesamte Vokabular vorhersagen. Dafür brauchte es:

- einen **Hidden Layer** mit hunderten Neuronen,
- eine **Softmax über V Ausgänge** in jedem Trainingsschritt (bei V = 20 000 pro Schritt teuer),
- eine sorgfältig konstruierte Verlustfunktion.

Word2Vec verzichtet auf all das — bewusst:

| Aspekt | Bengio 2003 (NNLM) | Word2Vec 2013 |
|--------|--------------------|---------------|
| Aufgabe | Nächstes Wort vorhersagen | Nur: „gehören zwei Wörter zusammen?" |
| Architektur | Embedding + Hidden + Softmax | Nur zwei Embedding-Matrizen |
| Ausgabe­schicht | Softmax über V | Sigmoid pro Wortpaar |
| Was ist das Ziel? | Sprachmodell (Wortfolgen) | Reine Wort-Embeddings |
| Trainings­aufwand | Stunden bis Tage auf einer CPU | Minuten |

Word2Vec ist also **nicht** nur eine schnellere Bengio-Variante — es ist ein anderes Ziel, das nebenbei extrem schnell erreichbar ist. Deshalb sagt es *kein nächstes Wort* vorher; es weiß nur, welche Wörter „zusammengehören". Für ein vollwertiges Sprachmodell brauchen wir wieder mehr — dazu kommen wir in Meilenstein 5 (RNN) und Meilenstein 8 (Mini-GPT).

---

## 🧩 Modellidee: Skip-Gram mit Negative Sampling

Zwei Word2Vec-Varianten:
- **CBOW:** Aus dem Kontext das mittlere Wort vorhersagen. Schneller, gut bei viel Daten.
- **Skip-Gram:** Aus dem mittleren Wort die Kontextwörter vorhersagen. Robuster bei kleineren Datenmengen.

Wir wählen **Skip-Gram**, weil unser Grimm-Korpus mit ~100 000 Wörtern klein ist.

### Das Skip-Gram-Prinzip in einem Bild

Fenster über den Text schieben. Mittleres Wort = **Zentrum** `c`, umliegende Wörter = **Kontext** `o`:

    ...  the  golden  |  BIRD  |  sang  a  song  ...
                         (c)      (o)  (o) (o)

Für jedes Paar `(c, o)` soll das Modell lernen: *„Diese beiden Wörter stehen zusammen."*

### Negative Sampling: der Trick

Eine echte Softmax über alle V Wörter wäre teuer. Der Trick von Mikolov: statt aller V Alternativen ziehen wir **wenige zufällige „Negativ-Wörter"** (typisch 5–15) und lernen:

- Das echte Paar `(c, o)` → Sigmoid soll gegen **1** gehen.
- Jedes Zufallspaar `(c, n_j)` → Sigmoid soll gegen **0** gehen.

Verlust für ein einzelnes Trainingspaar:

    L = -log σ(v_c · u_o)  -  Σ_j log σ(-v_c · u_nj)

wobei `σ` das Sigmoid ist und `v_c, u_o, u_nj` die entsprechenden Zeilen aus `W_in` bzw. `W_out`.

Wenn wir σ+ = σ(v_c · u_o) und σ-_j = σ(v_c · u_nj) abkürzen, sind die Gradienten schön einfach:

    dL / d(v_c · u_o)   =  σ+ − 1
    dL / d(v_c · u_nj)  =  σ-_j

Das heißt: Wir schieben das echte Kontextwort **näher** an das Zentrumswort, die Zufallswörter **weg** — mit einer Stärke, die davon abhängt, wie falsch das Modell gerade liegt. Die vollständige Herleitung steht als Kommentar im NumPy-Code in `word2vec.py`.

---

## 🖼️ Datensatz: Grimms Märchen (englisch)

Wir laden die **englische Grimm-Ausgabe** von *Project Gutenberg* (eBook #2591) — sie enthält Übersetzungen der berühmten *Kinder- und Hausmärchen*. Auf Deutsch gibt es leider keine gut zugängliche Volltextausgabe im Netz, deshalb arbeiten wir mit der englischen Fassung. Die Grimm-Story bleibt dieselbe — nur die Wortoberfläche wechselt.

**Umfang:** ca. 530 kB Text, ca. 100 000 Wörter, Vokabular ca. 1 600 Wörter (min. 5 Vorkommen). Beim ersten Aufruf wird der Text automatisch heruntergeladen und lokal in `grimm_en.txt` zwischen­gespeichert.

---

## ▶️ So startest du das Programm

    cd Word2Vec/src
    pip install numpy scikit-learn
    python main.py

Das Programm:
1. lädt den Grimm-Text (~10 Sekunden Download beim ersten Aufruf, danach gecacht),
2. baut Vokabular und Trainings-Token,
3. trainiert Skip-Gram + Negative Sampling (~2 Minuten auf CPU),
4. gibt **Nachbarwörter**, **Analogien** und einen **2D-PCA-Plot** in der Konsole aus.

---

## 📈 Beispielausgabe

    Tokens gesamt: 101,632   Vokabular: 1,636   Trainings-IDs: 95,942
    [W2V] Epoche 1/4  Loss=2.80  Zeit=21s
    [W2V] Epoche 2/4  Loss=2.55  Zeit=29s
    [W2V] Epoche 3/4  Loss=2.51  Zeit=30s
    [W2V] Epoche 4/4  Loss=2.49  Zeit=24s

    Nachbarwoerter (Kosinusaehnlichkeit):
      king    -> ['bride', 'cook', 'merchant', 'boy', 'queen', 'woman', 'fox', ...]
      queen   -> ['princess', 'bride', 'frog', 'fisherman', 'merchant', 'miller', ...]
      forest  -> ['kitchen', 'wood', 'town', 'close', 'cellar', 'spot', 'room', ...]
      castle  -> ['courtyard', 'country', 'village', 'cottage', 'palace', 'mill', ...]
      gold    -> ['wine', 'pair', 'fur', 'kinds', 'flowers', 'stones', 'silver', ...]
      night   -> ['same', "o'clock", 'knocked', 'morning', 'arrived', 'noon', ...]

    Analogien:
      man : king    :: woman  : ?  ->  ['queen', 'next', 'princess', 'fox', 'cook']
      father : son  :: mother : ?  ->  ['daughter', 'hans', 'woman', 'gretel', ...]

Zwei Beobachtungen:

1. **Die Analogie `king − man + woman = queen` funktioniert.** Das Modell hat *niemand* beigebracht, dass Frauen und Männer im Gegensatz stehen — es hat diese Struktur allein aus dem Grimm-Text abgeleitet.
2. **Die Nachbarwörter bilden thematische Gruppen.** `castle` neben *courtyard, palace, cottage, mill*; `night` neben *morning, noon, o'clock*; `gold` neben *silver, stones, flowers*.

Der PCA-Plot zeigt Cluster in 2D:
- **oben**: Zeit-Wörter (*night, morning, day*)
- **rechts**: königliche Familie (*king, queen, princess, prince, daughter, son*)
- **links**: Räume und Natur (*forest, wood, tree, castle, house, sea*)
- **unten**: Eltern-Wörter und Metalle (*mother, father, gold, silver*)

Nicht jede Analogie klappt bei 100 000 Wörtern — `boy : prince :: girl : ?` liefert Unsinn. Bei Millionen-Wort-Korpora werden Analogien zuverlässiger.

---

## 📝 Übungen

### 1. Andere Nachbarwörter erkunden
Ergänze in `main.py` weitere Wörter (`bread`, `mountain`, `witch`, `dragon` ...). Welche Nachbarn ergeben Sinn, welche überraschen dich?

### 2. Analogien selbst finden
Probiere eigene Analogien: `queen : king :: princess : ?`, `wolf : forest :: fish : ?`. Bei welchen funktioniert es, bei welchen nicht — und warum?

### 3. Embedding-Dimension variieren
Setze `EMBED_DIM = 16` oder `EMBED_DIM = 128`. Was ändert sich an der Qualität der Nachbarwörter und an der Trainings­zeit?

**Lernziel:** Mehr Dimensionen erlauben feinere Unterscheidungen, kosten aber Rechenzeit und brauchen mehr Daten.

### 4. Fenstergröße variieren
Setze `WINDOW = 2` (nur direkte Nachbarn) oder `WINDOW = 10` (breiter Kontext). Beobachtung: kleines Fenster → *syntaktische* Ähnlichkeit (Verben mit Verben); großes Fenster → *thematische* Ähnlichkeit.

### 5. Vektor-Kombinationen
Berechne den Nachbarn zu einem selbst gewählten Vektor, z. B. `0.5 * (v[wolf] + v[fox])`. Welche Wörter erscheinen?

---

## 🧪 Zentrale Beobachtungen

- **Bedeutung ist Position.** Semantisch verwandte Wörter liegen nah beieinander.
- **Der Kontext ist der Lehrer.** Niemand hat dem Modell gesagt, dass `king` und `queen` verwandt sind — es hat aus den Kontexten in Grimms Märchen darauf geschlossen. Das ist **self-supervised learning** in seiner reinsten Form.
- **Analogien sind Vektor-Arithmetik.** Die Beziehung „männlich → weiblich" ist im Vektorraum eine ungefähr konstante Richtung.
- **Kleine Korpora, wackelige Analogien.** Mit 100 000 Wörtern sind viele Analogien noch instabil. Word2Vec entfaltet seine Stärke erst auf hundertfach größeren Texten; moderne Modelle wie GPT nutzen Milliarden.

---

## 🧠 Abschließende Bemerkungen

Word2Vec markiert einen Bruch: Zum ersten Mal in dieser Reihe haben wir ein Modell, das **niemand explizit gelabelt hat**. Der Text selbst war Lehrer.

Diese Idee — **die Struktur der Daten als Trainingssignal zu benutzen** — ist der Kern aller heutigen großen Sprachmodelle. GPT lernt „das nächste Wort vorherzusagen"; BERT lernt „das maskierte Wort zu ergänzen". Beides sind direkte Verwandte des Skip-Gram-Ziels.

Doch Word2Vec hat auch eine klare Grenze:

> **Ein Wort bekommt hier immer genau einen Vektor — egal in welchem Satz es steht.**

Das Wort *bank* hat für Word2Vec dieselbe Bedeutung, ob wir *"ich sitze auf einer Bank"* oder *"die Bank ist geschlossen"* sagen. Das reicht offensichtlich nicht, um Sprache wirklich zu verstehen.

Um Kontext wirklich zu erfassen, brauchen wir Modelle, die die **Reihenfolge und Umgebung** eines Wortes einbeziehen — **Sequenzmodelle**.

---

## 🚀 Nächstes Kapitel: Recurrent Neural Networks (RNNs)

Wir haben jetzt Wortvektoren mit Bedeutung. Aber Sprache ist mehr als ein Beutel von Wörtern — sie ist eine **Reihenfolge**:

> *„Der Wolf frisst das Schaf"* ≠ *„Das Schaf frisst den Wolf"*

Ein RNN (Recurrent Neural Network) verarbeitet Wörter **eines nach dem anderen** und trägt dabei einen inneren **Gedächtnis­zustand** mit. Damit kann es Reihenfolgen erfassen und sogar neue Sätze **generieren**.

Historisch geht der Ansatz auf **Elman (1990)** zurück; das erste *Sprachmodell* auf RNN-Basis stammt von **Mikolov (2010)** — also drei Jahre *vor* Word2Vec. LSTMs (**Hochreiter & Schmidhuber, 1997**) haben RNNs später deutlich lernfähiger gemacht.

Als Testaufgabe werden wir das RNN im nächsten Kapitel dazu bringen, **grimm-ähnliche Sätze zu erzeugen**: Zeichen für Zeichen, mit dem Charme alter Märchen. Es war einmal…

---

## 📚 Referenzen

- Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013). *Efficient Estimation of Word Representations in Vector Space*. arXiv:1301.3781.
- Mikolov, T., Sutskever, I., Chen, K., Corrado, G., & Dean, J. (2013). *Distributed Representations of Words and Phrases and their Compositionality*. NeurIPS.
- Pennington, J., Socher, R., & Manning, C. D. (2014). *GloVe: Global Vectors for Word Representation*. EMNLP.
- Bengio, Y., Ducharme, R., Vincent, P., & Jauvin, C. (2003). *A Neural Probabilistic Language Model*. JMLR.
- Mikolov, T., Karafiát, M., Burget, L., Černocký, J., & Khudanpur, S. (2010). *Recurrent Neural Network Based Language Model*. Interspeech.
