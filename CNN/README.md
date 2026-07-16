# KI‑Meilenstein 3: Das Convolutional Neural Network (CNN)

> **🎯 Warum ist das cool?**
> Mit nur **4 kleinen Filtern (je 3×3)** lernt das Netz, handgeschriebene Ziffern zu erkennen — dieselbe Technik, mit der die US-Post seit den 90er-Jahren Postleitzahlen liest und mit der dein Smartphone Gesichter findet. Und das Beste: Die gelernten Filter sehen am Ende aus wie **Kantendetektoren**, die man später auch im visuellen Cortex des Gehirns fand — das CNN entdeckt sie **von selbst**.

## 📖 Einleitung

Im vorherigen Meilenstein haben wir gesehen, dass ein **Multi‑Layer‑Perzeptron (MLP)** einfache Bilder klassifizieren kann — solange sie exakt an derselben Stelle stehen wie im Training. Verschiebt man das Bild um ein paar Pixel, bricht die Erkennung zusammen.

Der Grund: Ein MLP behandelt jedes Pixel als **eigenständiges Merkmal**. Es hat kein Konzept von **Nachbarschaft** oder **Lokalität** — für das MLP sind Pixel (3,4) und Pixel (3,5) genauso unabhängig voneinander wie Pixel (0,0) und Pixel (13,13).

Genau dieses Problem löst das **Convolutional Neural Network (CNN)**. Es wurde 1998 von **Yann LeCun** und Kollegen in der Arbeit *„Gradient‑Based Learning Applied to Document Recognition“* (Proceedings of the IEEE, 86(11), 2278–2324) beschrieben — die Geburtsstunde des Netzes **LeNet‑5**, mit dem in den USA über Jahre hinweg handgeschriebene Postleitzahlen automatisch gelesen wurden.

Die Kernidee ist so einfach wie genial:

> Statt jedes Pixel einzeln mit einem eigenen Gewicht zu betrachten, lernt das Netz **kleine Filter** (typisch 3×3 oder 5×5), die über das gesamte Bild **gleitend** angewendet werden.

Damit lernt das CNN nicht mehr „an Position (3,4) sollte ein Pixel leuchten“, sondern **„irgendwo im Bild gibt es eine schräge Kante nach rechts oben“**. Diese Fähigkeit heißt **Translations­invarianz** — und sie ist der Grund, warum CNNs bis heute das Rückgrat der Bildverarbeitung sind.

In diesem Meilenstein bauen wir ein **CNN von Grund auf** — die Faltung, das Pooling und das Backprop schreiben wir selbst, nur die Vektor-Rechnung überlassen wir NumPy. Wir trainieren es auf **MNIST‑Lite** (14×14‑Ausschnitten des klassischen MNIST‑Datensatzes von LeCun 1998) und vergleichen es direkt mit einem MLP.

---

## 🎯 Lernziele

- Verstehen, was eine **Faltung (Convolution)** anschaulich bedeutet.
- Die Rolle von **Filtern**, **Aktivierung (ReLU)** und **Pooling** erkennen.
- Begreifen, warum **geteilte Gewichte** (weight sharing) so mächtig sind.
- Den Begriff **Translations­invarianz** an einem konkreten Beispiel erleben.
- Ein CNN im Vergleich zum MLP messen — bei **gleicher Anzahl Parameter** und auf **verschobenen** Bildern.
- Die historische Bedeutung von LeNet‑5 (LeCun 1998) einordnen.

---

## 🕰️ Historischer Kontext: Von LeNet zur Bildrevolution

Bereits in den 1980er Jahren experimentierten Forscher mit dem Gedanken, biologisch inspirierte Filter in neuronale Netze einzubauen. Kunihiko Fukushima entwickelte 1980 das **Neocognitron** — die konzeptionelle Vorstufe der CNNs. Aber erst LeCun kombinierte diese Idee mit **Backpropagation** aus dem MLP‑Kapitel und schuf damit ein trainierbares, praktikables Modell.

Meilensteine der CNN‑Geschichte:

| Jahr | Ereignis | Bedeutung |
|------|----------|-----------|
| 1980 | Fukushima: Neocognitron | Idee der lokalen Filter |
| 1989 / 1998 | LeCun: **LeNet‑5** | Erstes trainierbares CNN, US‑Post nutzt es |
| 2012 | **AlexNet** (Krizhevsky, Sutskever, Hinton) | Gewinnt ImageNet, entfacht Deep‑Learning‑Boom |
| 2015 | **ResNet** (He et al.) | Ermöglicht sehr tiefe Netze (>100 Schichten) |

CNNs waren die **erste KI‑Technologie, die produktiv und in großem Maßstab funktioniert hat**. Sie sind der Grund, warum es heute Gesichtserkennung, autonomes Fahren und medizinische Bildanalyse gibt.

---

## 🧠 Was das CNN gegenüber dem MLP neu einführt

Ein CNN besteht aus vier neuen Bausteinen:

### 1. Convolution (Faltung)
Ein kleiner Filter (z. B. 3×3) gleitet über das Eingabebild und berechnet an jeder Position eine gewichtete Summe der überdeckten Pixel. Das Ergebnis ist eine **Feature Map** — eine Karte, in der Stellen aufleuchten, an denen der Filter „sein Muster gefunden“ hat.

### 2. Weight Sharing (geteilte Gewichte)
Der **gleiche** Filter wird an **jeder** Position des Bildes verwendet. Ein Filter, der eine horizontale Kante erkennt, tut das an jeder Bildstelle gleich gut. Das ist der Kern der Translations­invarianz — und der Grund, warum CNNs deutlich weniger Parameter brauchen als MLPs.

### 3. ReLU‑Aktivierung
Statt Sigmoid verwenden CNNs meist die **Rectified Linear Unit**: `ReLU(x) = max(0, x)`. Sie ist einfacher, schneller und vermeidet das Problem verschwindender Gradienten in tiefen Netzen.

### 4. Max‑Pooling
Nach der Faltung wird das Bild verkleinert, indem in jedem kleinen Bereich (z. B. 2×2) nur der stärkste Wert übernommen wird. Das macht das Netz **robuster gegen kleine Verschiebungen** und reduziert die Datenmenge.

---

## 📊 Anschauliche Darstellung: Wie eine Faltung funktioniert

Ein 3×3‑Filter, der eine **vertikale Kante** erkennt, könnte so aussehen:

```
Filter:            Eingabe (Ausschnitt):
[ -1  0  +1 ]      [  0   1   1 ]
[ -1  0  +1 ]  *   [  0   1   1 ]   -> Summe = +6  (starke vertikale Kante!)
[ -1  0  +1 ]      [  0   1   1 ]
```

Bei einem gleichmäßigen Bereich (alle Pixel gleich) wäre die Summe 0 — der Filter „reagiert“ nur auf das Muster, für das er gebaut wurde.

Beim Training lernt das CNN diese Filter **selbst** — niemand gibt ihm vor, wonach er suchen soll. Es entdeckt die nützlichen Muster (Kanten, Ecken, Rundungen …) durch Backpropagation, genau wie das MLP seine Gewichte gelernt hat. Am Ende dieses Kapitels wirst du die gelernten Filter in der Konsole sehen und Kantendetektoren wiedererkennen.

---

## 🧩 Modellarchitektur

Unser Mini‑CNN sieht so aus:

```
Eingabe (14 x 14 Bild)
      |
      v
[ Conv-Schicht: 8 Filter, 3x3, stride 1 ]  ->  8 Feature Maps a 12x12
      |
      v
[ ReLU-Aktivierung ]
      |
      v
[ Max-Pooling 2x2, stride 2 ]              ->  8 Feature Maps a 6x6
      |
      v
[ Flatten ]                                ->  8 * 6 * 6 = 288 Werte
      |
      v
[ Dense: 288 -> 10 Ausgangs-Neuronen ]
      |
      v
[ Softmax ]                                ->  Wahrscheinlichkeit fuer 0-9
```

**Zum Vergleich das MLP:**

```
Eingabe (14*14 = 196 Werte, flach)
      |
      v
[ Dense: 196 -> 32 (ReLU) ]
      |
      v
[ Dense: 32 -> 10 (Softmax) ]
```

Konkrete Zahlen:

|                        | MLP                   | CNN                          |
|------------------------|-----------------------|------------------------------|
| Eingang                | 196 Pixel (flach)     | 14×14 Bild (mit Struktur)    |
| Parameter              | **6 634**             | **2 970**                    |
| Weight Sharing         | nein                  | ja                           |
| Translations­invariant | nein                  | teilweise (durch Pooling)    |

**Das CNN hat weniger als die Hälfte der Parameter — und ist trotzdem stärker.** Das ist ein Musterbeispiel für „gute“ Inductive Biases: eine Architektur, die zur Struktur der Daten passt (Bilder haben Nachbarschaft, wiederkehrende lokale Muster), ist einem generischen Modell überlegen.

---

## ⚙️ Mathematische Formulierung

Die Faltung an Position $(i, j)$ mit einem 3×3‑Filter $K$ auf Eingabe $X$:

$$
Y_{i,j} = \sum_{a=0}^{2} \sum_{b=0}^{2} K_{a,b} \cdot X_{i+a,\, j+b} + b_K
$$

Danach ReLU:

$$
Z_{i,j} = \max(0,\, Y_{i,j})
$$

Max‑Pooling (2×2, Schrittweite 2):

$$
P_{i,j} = \max\big(Z_{2i,\,2j},\; Z_{2i,\,2j+1},\; Z_{2i+1,\,2j},\; Z_{2i+1,\,2j+1}\big)
$$

Die anschließende Dense‑Schicht funktioniert wie im MLP.

Das Training erfolgt wieder mit **Backpropagation** und **Gradient Descent** — dieselben Prinzipien wie im MLP‑Kapitel, nur auf die neuen Schichten übertragen.

---

## 🧮 Warum ab jetzt NumPy?

Im Perceptron‑ und im MLP‑Kapitel haben wir mit **reinen Python-Listen** gearbeitet. Das war didaktisch super — man konnte jede einzelne Multiplikation als `for`‑Schleife sehen. Bei einem MLP mit 3 Beispielen und 20 Neuronen ist das kein Problem.

Ab jetzt geht das nicht mehr. Ein CNN muss auf jedem Bild an jeder Position eine 3×3‑Faltung berechnen — das sind pro Bild fast 1000 Multiplikationen, mal 5000 Bilder pro Epoche, mal 8 Epochen. In reinem Python dauert das Stunden. Mit **NumPy** (Vektor‑ und Matrix­rechnung in C‑Geschwindigkeit) laufen dieselben Rechnungen in Sekunden.

**Was ändert sich?**

- Bilder sind jetzt `numpy.ndarray` statt Listen.
- Statt `for`‑Schleifen schreiben wir `A @ B` (Matrixmultiplikation) oder `x.max(axis=…)`.
- Die **Logik** bleibt genau dieselbe: Faltung ist Faltung, ReLU ist ReLU, Backprop ist Backprop. Wir benutzen keine Bibliothek wie PyTorch oder Keras — wir schreiben `forward` und `backward` immer noch selbst.

**Was ändert sich nicht?**

- Wir nutzen weiterhin **kein** Framework mit vorgefertigten Schichten (`torch.nn.Conv2d` o. ä.).
- Jede Zeile im Code ist nachvollziehbar; NumPy ist nur der schnelle Rechner darunter.

Das ist ein bewusster, wichtiger Zwischen­schritt: Vom Verstehen jeder einzelnen Operation → hin zu einer Denkweise in Vektoren und Matrizen, die spätestens beim Transformer unverzichtbar wird.

---

## 🖼️ Der Datensatz: MNIST‑Lite (14×14)

Wir verwenden **MNIST** — den historischen Datensatz, den Yann LeCun selbst zusammengestellt hat und auf dem LeNet‑5 1998 trainiert wurde. MNIST enthält 70 000 handgeschriebene Ziffern (0–9), original in 28×28 Pixeln.

Für unseren kleinen Meilenstein tun wir zwei Dinge:

1. **Verkleinerung auf 14×14** durch 2×2‑Blockmittelung. Damit reduziert sich der Rechenaufwand um den Faktor 4, und die Ziffern bleiben gut erkennbar.
2. **Kleines Subset**: 5000 Bilder zum Training, 1000 zum Testen. Das genügt, damit CNN und MLP klar unterschiedliche Ergebnisse zeigen, und das Training läuft in wenigen Sekunden.

MNIST wird beim ersten Ausführen automatisch über `sklearn.datasets.fetch_openml` heruntergeladen und lokal zwischen­gespeichert.

**Beispielbild** (Label = 6):

```
         -*%-
        *@+.
      :@%:
     +@%.
   .#@*
   %%: .--
  =@: #@#%%.
  .@@#%-.=@-
   .*@@@@+-
```

---

## ▶️ So startest du das Programm

```bash
cd CNN/src
pip install numpy scikit-learn      # nur beim ersten Mal
python main.py
```

Das Programm:

1. lädt MNIST‑Lite (beim ersten Aufruf ~10–30 Sekunden Download, danach gecacht),
2. trainiert das MLP (~1 Sekunde) und das CNN (~2 Sekunden),
3. testet beide Modelle auf Original‑, verschobenen und verrauschten Bildern,
4. zeigt einige Beispielvorhersagen und die gelernten CNN‑Filter.

---

## 📈 Beispielausgabe

```
[MNIST] Training:  (5000, 14, 14)  Labels: (5000,)
[MNIST] Test:      (1000, 14, 14)  Labels: (1000,)

--- Training MLP (6634 Parameter) ---
[MLP] Epoch 1/8 lr=0.100  train_acc=67.80%  val_acc=67.50%
[MLP] Epoch 4/8 lr=0.100  train_acc=88.50%  val_acc=86.40%
[MLP] Epoch 8/8 lr=0.050  train_acc=87.60%  val_acc=86.90%

--- Training CNN (2970 Parameter) ---
[CNN] Epoch 1/8 lr=0.100  train_acc=38.90%  val_acc=38.40%
[CNN] Epoch 4/8 lr=0.100  train_acc=92.90%  val_acc=90.50%
[CNN] Epoch 8/8 lr=0.050  train_acc=94.10%  val_acc=92.50%

Parameterzahl:  MLP = 6634   CNN = 2970

==== Robustheitsvergleich (Testdaten, 1000 Bilder) ====
  Original:                MLP 86.90%   CNN 92.50%
  Verschoben (+-2 Pixel):  MLP 26.20%   CNN 35.50%
  Verschoben + Rauschen:   MLP 23.00%   CNN 26.10%

==== Gelernte CNN-Filter (3x3) ====
  Filter 0:
     ++ --  +
     ++ -- --
      +  -  -              <- vertikale Kante (links hell, rechts dunkel)
  Filter 5:
     ++ ++ ++
     ++ ++  .
     ++ -- --              <- horizontale Kante (oben hell, unten dunkel)
```

Drei Dinge fallen sofort auf:

1. **Original**: Das CNN erreicht **92,5 %** gegenüber **86,9 %** beim MLP — bei **weniger als der Hälfte der Parameter**.
2. **Verschoben**: Das MLP bricht auf **26 %** ein — das CNN hält immerhin **36 %**. Beide sind weit weg von perfekt, weil sie ohne Data Augmentation nur eine feste Position gesehen haben.
3. **Filter sind Kantendetektoren**: Filter 0 ist eine klassische vertikale Kante, Filter 5 eine horizontale — und das ohne dass jemand dem Netz gesagt hätte, dass es nach Kanten suchen soll. Es hat sie **von selbst entdeckt**.

Genau diese Filter fand später auch die Neurowissenschaft im visuellen Cortex des Gehirns (Hubel & Wiesel, 1959) — CNNs sind, ohne dass wir es geplant hätten, biologisch plausibel.

---

## 📝 Übungen

### 1. Anzahl der Filter variieren
Ändere `num_filters=8` in `main.py` (z. B. auf 2, 4, 16) und beobachte:
- Wie ändert sich die Genauigkeit?
- Wie stark steigt die Trainingszeit?
- Ab wann bringen mehr Filter nichts mehr?

**Lernziel:** Modellkapazität ist ein Kompromiss — mehr ist nicht immer besser.

### 2. Pooling entfernen
Kommentiere den Pooling‑Schritt in `cnn.py` aus (setze `pool_h = conv_h`, `pool_w = conv_w` und lasse `pooled = conv_relu`). Was passiert bei verschobenen Bildern?

**Lernziel:** Pooling ist einer der Hauptgründe für Translations­invarianz.

### 3. Data Augmentation
Füge in `main.py` beim Training zufällige Verschiebungen (`shift_batch`) hinzu, sodass das CNN in jeder Epoche leicht verschobene Bilder sieht. Wie stark verbessert sich die Genauigkeit auf verschobenen Testbildern?

**Lernziel:** Selbst ein CNN wird durch Augmentation dramatisch robuster — Architektur und Trainings­daten arbeiten zusammen.

### 4. MLP größer machen
Erhöhe `hidden_size=32` im MLP auf 128. Nun hat das MLP viel mehr Parameter als das CNN. Wird es besser als das CNN? (Antwort: kaum — es lernt vor allem das Training auswendig, generalisiert aber nicht besser.)

**Lernziel:** Mehr Parameter helfen nur, wenn die Architektur zur Aufgabe passt.

---

## 🧪 Zentrale Beobachtungen

- **Auf Originalbildern gewinnt das CNN mit halb so vielen Parametern** — der eigentliche Kern der Botschaft.
- **Auf verschobenen Bildern brechen beide ein**, aber das CNN ist deutlich robuster. Für volle Translations­invarianz braucht es zusätzlich Data Augmentation oder Global Pooling — Themen, die in modernen Netzen (ResNet, ViT) weitergedacht wurden.
- **Gelernte Filter ähneln Kantendetektoren** — ähnliche Muster fand man im visuellen Cortex des Gehirns (Hubel & Wiesel 1959). Das CNN entdeckt sie eigenständig.
- **NumPy statt reinem Python** hat das Training von Minuten auf Sekunden verkürzt, ohne den didaktischen Charakter zu verlieren — jeder Schritt (Faltung, Pooling, ReLU, Backprop) ist von Hand geschrieben.

---

## 🧠 Abschließende Bemerkungen

Das CNN führt einen neuen Gedanken in die KI ein: **Architektur ist Wissen**. Wir haben dem Netz nichts über Bilder „erzählt“ — aber die Wahl, kleine Filter über das Bild gleiten zu lassen, ist selbst schon eine starke Annahme über die Welt: dass Bilder aus wiederkehrenden lokalen Mustern bestehen, die überall vorkommen können.

Diese Idee — **das Modell so bauen, dass es zur Struktur der Daten passt** — zieht sich durch das gesamte moderne Deep Learning:

- CNNs nutzen die Lokalität von Bildern.
- RNNs (später) nutzen die Reihenfolge in Sequenzen.
- Transformers nutzen, dass in Sprache jedes Wort mit jedem anderen zusammenhängen kann.

Bis jetzt haben wir uns nur mit **festen Eingabegrößen** beschäftigt — 2 Zahlen (Perceptron), 81 Pixel (MLP), 14×14 Pixel (CNN). Aber Sprache ist eine **Sequenz variabler Länge**: Sätze können 3 Wörter oder 30 Wörter haben. Weder Perceptron noch MLP noch CNN können damit natürlich umgehen.

### 🌉 Vom *Erkennen* zum *Verstehen*

Mit diesem Meilenstein endet die Phase **A** der Reihe. Wir können jetzt:

- (aus Teil 1) einen Text im Computer **darstellen** — als Zeichen, als Bytes, als Datei,
- (aus Perceptron/MLP) einfache Muster **klassifizieren**,
- (aus CNN + MNIST) sogar **handgeschriebenen Text erkennen** — das ist genau die Aufgabe, mit der LeCun 1998 die Postleitzahlen der US-Post automatisch las.

Das ist ein Etappenziel: Ein Computer kann jetzt Text **lesen**. Aber er **versteht** immer noch nichts. Für ihn ist ein Text nur eine Folge von Pixel-Formen, die er als Buchstaben klassifiziert. Was diese Buchstaben *bedeuten* — dass „König" mit „Königin" verwandt ist, dass „Wolf frisst Schaf" nicht dasselbe ist wie „Schaf frisst Wolf" — davon hat er keine Ahnung.

Ab dem nächsten Meilenstein beginnt deshalb Phase **B**: **Verstehen**. Und der erste Baustein dafür ist die Frage, wie man Wörter überhaupt sinnvoll in einem neuronalen Netz repräsentiert. Denn Wörter sind keine Zahlen — sie sind Symbole. Wie machen wir sie „mathematisch fassbar"?

Genau das ist das Thema des nächsten Meilensteins: **Word2Vec** — die Idee, Wörter als Vektoren in einem Bedeutungsraum darzustellen.

---

## 🚀 Nächstes Kapitel: Word Embeddings (Word2Vec)

Wir verlassen die Welt der Bilder und wenden uns Sprache zu. Der erste Schritt: Wie stellt man Wörter für ein neuronales Netz dar?

- **One‑Hot** funktioniert, verliert aber jede Bedeutung.
- **Word2Vec** (Mikolov, 2013) lernt Wortvektoren, in denen ähnliche Wörter im Vektorraum nahe beieinander liegen.
- Erstes „Wow“: `könig − mann + frau ≈ königin`.

Als Trainingsmaterial verwenden wir dann die **Grimm‑Märchen** — sie werden uns bis zum letzten Meilenstein begleiten.

---

## 📚 Referenzen

- LeCun, Y., Bottou, L., Bengio, Y., & Haffner, P. (1998). *Gradient‑Based Learning Applied to Document Recognition.* Proceedings of the IEEE, 86(11), 2278–2324.
- Fukushima, K. (1980). *Neocognitron: A Self‑Organizing Neural Network Model for a Mechanism of Pattern Recognition Unaffected by Shift in Position.* Biological Cybernetics, 36(4), 193–202.
- Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012). *ImageNet Classification with Deep Convolutional Neural Networks.* NeurIPS.
- He, K., Zhang, X., Ren, S., & Sun, J. (2015). *Deep Residual Learning for Image Recognition.* arXiv:1512.03385.
- Hubel, D. H., & Wiesel, T. N. (1959). *Receptive Fields of Single Neurones in the Cat's Striate Cortex.* Journal of Physiology.
