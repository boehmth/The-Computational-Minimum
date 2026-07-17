# KI-Meilenstein 3: Das Convolutional Neural Network (CNN)

> **🎯 Warum ist das cool?**
> Mit nur **8 kleinen Filtern (je 3×3)** lernt das Netz, handgeschriebene Ziffern zu erkennen — dieselbe Technik, mit der die US-Post seit den 90er-Jahren Postleitzahlen liest und mit der dein Smartphone Gesichter findet. Und das Beste: Die gelernten Filter sehen am Ende aus wie **Kantendetektoren**, die man später auch im visuellen Cortex des Gehirns fand — das CNN entdeckt sie **von selbst**.

## 🌉 Vom MLP zum bildbewussten Netz

Im vorherigen Meilenstein hat unser MLP kleine 9×9-Buchstaben klassifiziert — aber sobald wir das Bild um einen Pixel verschoben haben, brach die Erkennung zusammen. Der Grund: **Ein MLP behandelt jedes Pixel als eigenständiges Merkmal.** Für das MLP sind Pixel (3, 4) und Pixel (3, 5) so unabhängig voneinander wie Pixel (0, 0) und Pixel (13, 13). Es hat kein Konzept von **Nachbarschaft** oder **Lokalität**.

Genau dieses Problem löst das **Convolutional Neural Network (CNN)**. Die Idee, 1998 von **Yann LeCun** in *„Gradient-Based Learning Applied to Document Recognition"* (Proceedings of the IEEE, 86(11)) veröffentlicht, ist so einfach wie genial:

> Statt jedes Pixel einzeln mit einem eigenen Gewicht zu betrachten, lernt das Netz **kleine Filter** (typisch 3×3), die über das gesamte Bild **gleitend** angewendet werden.

Damit lernt das CNN nicht mehr „an Position (3, 4) sollte ein Pixel leuchten", sondern **„irgendwo im Bild gibt es eine schräge Kante nach rechts oben"**. Diese Fähigkeit heißt **Translations­invarianz** — und sie ist der Grund, warum CNNs bis heute das Rückgrat der Bildverarbeitung sind.

In diesem Meilenstein bauen wir ein **CNN von Grund auf** — die Faltung, das Pooling und das Backprop schreiben wir selbst, nur die Vektor-Rechnung überlassen wir NumPy. Wir trainieren es auf **MNIST-Lite** und vergleichen es direkt mit einem MLP.

---

## 🕰️ Historischer Kontext

| Jahr | Ereignis | Bedeutung |
|------|----------|-----------|
| **1959** | Hubel & Wiesel: Katzen-Sehrinde | Erste Entdeckung von *Kantendetektoren* im visuellen Cortex |
| **1980** | Fukushima: **Neocognitron** | Konzeptionelle Vorstufe der CNNs — Idee der lokalen Filter |
| **1989** | LeCun: erstes trainierbares CNN | Backpropagation + Faltung — funktioniert auf Postleitzahlen |
| **1998** | **LeCun: LeNet-5** | Wird von der US-Post in großem Maßstab eingesetzt |
| **2012** | **AlexNet** (Krizhevsky, Sutskever, Hinton) | Gewinnt ImageNet — entfacht den Deep-Learning-Boom |
| **2015** | **ResNet** (He et al.) | Ermöglicht sehr tiefe Netze (>100 Schichten) |
| **2020** | **Vision Transformer** (Dosovitskiy et al.) | Erste ernsthafte Konkurrenz durch Transformer-Architekturen |
| **heute** | Kameras, Autonomes Fahren, medizinische Bildgebung | CNNs sind eine der wenigen KI-Techniken, die massenhaft in Produktion sind |

CNNs waren die **erste KI-Technologie, die produktiv und in großem Maßstab funktioniert hat**. Sie sind der Grund, warum es heute Gesichtserkennung, autonomes Fahren und medizinische Bildanalyse gibt.

---

## 🧠 Die Aufgabe: Handgeschriebene Ziffern erkennen

Wir verwenden **MNIST** — den historischen Datensatz, den Yann LeCun selbst zusammengestellt hat und auf dem LeNet-5 1998 trainiert wurde. MNIST enthält 70 000 handgeschriebene Ziffern (0–9), original in 28×28 Pixeln.

Für unseren kleinen Meilenstein tun wir zwei Dinge:

1. **Verkleinerung auf 14×14** durch 2×2-Blockmittelung. Damit reduziert sich der Rechenaufwand um den Faktor 4, und die Ziffern bleiben gut erkennbar.
2. **Kleines Subset**: 5 000 Bilder zum Training, 1 000 zum Testen. Das genügt, damit CNN und MLP klar unterschiedliche Ergebnisse zeigen, und das Training läuft in wenigen Sekunden.

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

**Warum diese Aufgabe?** Sie ist strukturell perfekt für dieses Kapitel:

1. **Echte Bilddaten** — kein Spielzeug-Datensatz, sondern die klassische Handschrift-Erkennungs-Benchmark.
2. **Direkter Vergleich MLP vs. CNN** — wir trainieren *beide* Modelle auf denselben Daten und sehen den Unterschied schwarz auf weiß.
3. **Robustheits-Tests möglich** — durch Verschieben und Rauschen kann man Translations­invarianz messbar machen.
4. **Historische Kontinuität** — genau diese Aufgabe hat LeCun 1998 gelöst.

---

## 🧩 Modellarchitektur

Ein CNN besteht aus vier neuen Bausteinen gegenüber dem MLP:

- **Convolution (Faltung)** — ein kleiner Filter (3×3) gleitet über das Eingabebild und berechnet an jeder Position eine gewichtete Summe. Das Ergebnis ist eine **Feature Map**.
- **Weight Sharing** — der *gleiche* Filter wird an *jeder* Position verwendet. Ein Filter, der eine horizontale Kante erkennt, tut das an jeder Bildstelle gleich gut.
- **ReLU-Aktivierung** — `ReLU(x) = max(0, x)`. Einfacher, schneller und vermeidet das Problem verschwindender Gradienten in tiefen Netzen.
- **Max-Pooling** — reduziert die Bildgröße, indem in jedem 2×2-Bereich nur der stärkste Wert übernommen wird. Macht das Netz robuster gegen kleine Verschiebungen.

Unser Mini-CNN sieht so aus:

```
Eingabe (14 x 14 Bild)
      │
      ▼
[ Conv-Schicht: 8 Filter, 3x3, stride 1 ]  ->  8 Feature Maps a 12x12
      │
      ▼
[ ReLU-Aktivierung ]
      │
      ▼
[ Max-Pooling 2x2, stride 2 ]              ->  8 Feature Maps a 6x6
      │
      ▼
[ Flatten ]                                ->  8 * 6 * 6 = 288 Werte
      │
      ▼
[ Dense: 288 -> 10 Ausgangs-Neuronen ]
      │
      ▼
[ Softmax ]                                ->  Wahrscheinlichkeit fuer 0-9
```

**Zum Vergleich das MLP:**

```
Eingabe (14*14 = 196 Werte, flach)
      │
      ▼
[ Dense: 196 -> 32 (ReLU) ]
      │
      ▼
[ Dense: 32 -> 10 (Softmax) ]
```

**Größenordnungen:**

|                        | MLP                   | CNN                          |
|------------------------|-----------------------|------------------------------|
| Eingang                | 196 Pixel (flach)     | 14×14 Bild (mit Struktur)    |
| Parameter              | **6 634**             | **2 970**                    |
| Weight Sharing         | nein                  | ja                           |
| Translations­invariant | nein                  | teilweise (durch Pooling)    |

**Das CNN hat weniger als die Hälfte der Parameter — und ist trotzdem stärker.** Das ist ein Musterbeispiel für „gute" Inductive Biases: eine Architektur, die zur Struktur der Daten passt (Bilder haben Nachbarschaft, wiederkehrende lokale Muster), ist einem generischen Modell überlegen.

### Wie eine Faltung anschaulich funktioniert

Ein 3×3-Filter, der eine **vertikale Kante** erkennt, könnte so aussehen:

```
Filter:            Eingabe (Ausschnitt):
[ -1  0  +1 ]      [  0   1   1 ]
[ -1  0  +1 ]  *   [  0   1   1 ]   -> Summe = +6  (starke vertikale Kante!)
[ -1  0  +1 ]      [  0   1   1 ]
```

Bei einem gleichmäßigen Bereich (alle Pixel gleich) wäre die Summe 0 — der Filter „reagiert" nur auf das Muster, für das er gebaut wurde. Beim Training lernt das CNN diese Filter **selbst** — niemand gibt ihm vor, wonach er suchen soll.

---

## ⚙️ Training

Die Faltung an Position $(i, j)$ mit einem 3×3-Filter $K$ auf Eingabe $X$:

$$
Y_{i,j} = \sum_{a=0}^{2} \sum_{b=0}^{2} K_{a,b} \cdot X_{i+a,\, j+b} + b_K
$$

Danach ReLU: $Z_{i,j} = \max(0, Y_{i,j})$.

Max-Pooling (2×2, Schrittweite 2): $P_{i,j} = \max\big(Z_{2i,\,2j},\; Z_{2i,\,2j+1},\; Z_{2i+1,\,2j},\; Z_{2i+1,\,2j+1}\big)$.

Die anschließende Dense-Schicht funktioniert wie im MLP-Kapitel. Das Training erfolgt wieder mit **Backpropagation** und **Gradient Descent** — dieselben Prinzipien wie im MLP-Kapitel, nur auf die neuen Schichten übertragen. Wir schreiben `forward` und `backward` weiterhin selbst.

**Hyperparameter:**
- Lernrate: 0.1 (fällt in der Halbzeit auf 0.05 ab)
- Epochen: 8
- Filter-Anzahl: 8 (3×3)
- Batch-Größe: 32

### Warum ab jetzt NumPy?

Im Perceptron- und im MLP-Kapitel haben wir mit **reinen Python-Listen** gearbeitet. Bei einem MLP mit 3 Beispielen und 20 Neuronen ist das kein Problem. Ab jetzt geht das nicht mehr: Ein CNN muss auf jedem Bild an jeder Position eine 3×3-Faltung berechnen — pro Bild fast 1000 Multiplikationen, mal 5000 Bilder, mal 8 Epochen. In reinem Python dauert das Stunden. Mit **NumPy** (Vektor- und Matrix­rechnung in C-Geschwindigkeit) laufen dieselben Rechnungen in Sekunden.

Was ändert sich: Bilder sind jetzt `numpy.ndarray` statt Listen; statt `for`-Schleifen schreiben wir `A @ B` oder `x.max(axis=…)`. Was **nicht** ändert sich: Wir nutzen weiterhin *kein* Framework mit vorgefertigten Schichten (`torch.nn.Conv2d` o. ä.). Jede Zeile im Code ist nachvollziehbar; NumPy ist nur der schnelle Rechner darunter.

---

## ▶️ So startest du das Programm

```bash
cd CNN/src
pip install numpy scikit-learn      # nur beim ersten Mal
python main.py
```

Das Programm:

1. lädt MNIST-Lite (beim ersten Aufruf ~10–30 Sekunden Download, danach gecacht),
2. trainiert das MLP (~1 Sekunde) und das CNN (~10 Sekunden),
3. testet beide Modelle auf Original-, verschobenen und verrauschten Bildern,
4. zeigt einige Beispielvorhersagen und die gelernten CNN-Filter.

---

## 📈 Beispielausgabe (echter Trainingslauf)

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

**Und der Star des Kapitels — die gelernten Filter:**

Filter 0 ist eine klassische **vertikale Kante**, Filter 5 eine **horizontale Kante** — und das *ohne dass jemand dem Netz gesagt hätte*, dass es nach Kanten suchen soll. Es hat sie **von selbst entdeckt**, allein aus dem Ziel, Ziffern zu klassifizieren.

Genau diese Filter fand später auch die Neurowissenschaft im visuellen Cortex des Gehirns (**Hubel & Wiesel, 1959**) — CNNs sind, ohne dass wir es geplant hätten, biologisch plausibel geworden.

Drei Dinge fallen bei den Zahlen sofort auf:

1. **Original**: Das CNN erreicht **92.5 %** gegenüber **86.9 %** beim MLP — bei **weniger als der Hälfte der Parameter**.
2. **Verschoben**: Das MLP bricht auf **26 %** ein — das CNN hält immerhin **36 %**. Der Vorteil ist real, aber begrenzt.
3. **Selbstorganisation**: Die Filter sind Kantendetektoren geworden. Das war nicht programmiert, sondern *emergent*.

---

## ❗ Ehrliche Diskussion: Grenzen und Trade-offs

Auf verschobenen Bildern brechen **beide** Modelle stark ein. Warum? Weil sie im Training nur **eine feste Position** gesehen haben. Die Translations­invarianz des CNN durch Pooling reicht nur für **kleine** Verschiebungen (1–2 Pixel Wackeln); bei ±2 Pixel systematischer Verschiebung ist der Bildinhalt schon weitgehend an anderer Stelle.

Was man tun *könnte*, um das zu verbessern:

1. **Data Augmentation** — im Training zufällig verschobene, rotierte und leicht verrauschte Bilder zeigen. In der Praxis der wichtigste Hebel: allein Augmentation kann die Genauigkeit auf verschobenen Testbildern von 35 % auf > 90 % heben.
2. **Global Pooling** — statt Flatten am Ende ein Global-Average-Pooling verwenden. Das macht das Modell vollständig translations­invariant, verliert aber Positionsinformation.
3. **Größerer Trainingsdatensatz** — ganz MNIST (60 000 Bilder statt 5 000) und die vollen 28×28 Pixel.
4. **Mehr Schichten** — tiefe CNNs (LeNet-5 hatte schon zwei Conv-Blöcke; ResNet hat >100 Schichten).

Wir bleiben bewusst bei diesem minimalen CNN. Der Zweck ist nicht State-of-the-Art, sondern **den Vergleich zum MLP messbar zu machen** und die *Kernidee* — Faltung und Weight Sharing — sichtbar in Code und Ergebnissen zu zeigen.

---

## 📝 Übungen

**1. Anzahl der Filter variieren.** Ändere `num_filters=8` in `main.py` (z. B. auf 2, 4, 16). Wie ändert sich die Genauigkeit? Wie stark steigt die Trainingszeit? Ab wann bringen mehr Filter nichts mehr? *(Lernziel: Modellkapazität ist ein Kompromiss — mehr ist nicht immer besser.)*

**2. Pooling entfernen.** Kommentiere den Pooling-Schritt in `cnn.py` aus (setze `pool_h = conv_h`, `pool_w = conv_w` und lasse `pooled = conv_relu`). Was passiert bei verschobenen Bildern? *(Lernziel: Pooling ist einer der Hauptgründe für Translations­invarianz.)*

**3. Data Augmentation.** Füge in `main.py` beim Training zufällige Verschiebungen (`shift_batch`) hinzu. Wie stark verbessert sich die Genauigkeit auf verschobenen Testbildern? *(Lernziel: Architektur und Trainings­daten arbeiten zusammen.)*

**4. MLP größer machen.** Erhöhe `hidden_size=32` im MLP auf 128. Nun hat das MLP viel mehr Parameter als das CNN. Wird es besser als das CNN? *(Antwort: kaum — es lernt vor allem das Training auswendig. Lernziel: Mehr Parameter helfen nur, wenn die Architektur zur Aufgabe passt.)*

**5. Andere Filtergröße.** Ändere den Filter von 3×3 auf 5×5. Was passiert mit der Parameterzahl? Mit der Genauigkeit? Welchen Bereich des Bildes „sieht" der Filter jetzt auf einmal?

---

## 🧭 Wo steht das CNN heute?

CNNs sind, anders als Word2Vec oder RNNs, **auch heute noch führende Modelle** in vielen Anwendungen:

- **Bildverarbeitung im Alltag**: Kamera-Apps, Handy-Foto-Modi (Nachtmodus, Portrait, HDR), Gesichtserkennung, Kfz-Kennzeichen — all das läuft mit CNN-Varianten.
- **Medizinische Bildanalyse**: Tumor-Erkennung in Röntgen- und MRT-Bildern, Diabetes-Retinopathie-Screening. Hier sind CNNs oft besser als menschliche Radiologen.
- **Autonomes Fahren**: Alle Wahrnehmungs­systeme (Kamerabilder → Objekte, Fahrspuren, Fußgänger) sind CNN-basiert.
- **Embedded / On-Device**: Weil CNNs weniger Speicher und Rechenleistung brauchen als Transformer, laufen sie in Kameras, Drohnen, IoT-Geräten.

**Aber sie bekommen Konkurrenz.** Der **Vision Transformer (ViT, Dosovitskiy et al. 2020)** wendet die Transformer-Architektur auf Bilder an und übertrifft CNNs auf sehr großen Datensätzen (ImageNet-21k, JFT-300M). Bei kleinen bis mittleren Datensätzen (bis ~1 Mio. Bilder) sind CNNs aber weiterhin oft im Vorteil, weil ihre eingebaute Bildstruktur-Annahme (Lokalität, Translations­invarianz) das Lernen erleichtert.

Kurz: **CNNs sind eine der wenigen Techniken dieser Reihe, die im Kern unverändert und massenhaft in Produktion sind.**

---

## 🧠 Abschließende Bemerkungen

Wenn du dir dieses Kapitel angesehen hast, hast du einen zentralen Gedanken der modernen KI in Aktion gesehen: **Architektur ist Wissen**. Wir haben dem Netz nichts über Bilder „erzählt" — aber die Wahl, kleine Filter über das Bild gleiten zu lassen, ist selbst schon eine starke Annahme über die Welt: dass Bilder aus wiederkehrenden lokalen Mustern bestehen, die überall vorkommen können.

Diese Idee — **das Modell so bauen, dass es zur Struktur der Daten passt** — zieht sich durch das gesamte moderne Deep Learning:

- **CNNs** nutzen die Lokalität von Bildern.
- **RNNs** (später) nutzen die Reihenfolge in Sequenzen.
- **Transformers** nutzen, dass in Sprache jedes Wort mit jedem anderen zusammenhängen kann.

Bis jetzt haben wir uns nur mit **festen Eingabegrößen** beschäftigt — 2 Zahlen (Perceptron), 81 Pixel (MLP), 14×14 Pixel (CNN). Aber Sprache ist eine **Sequenz variabler Länge**: Sätze können 3 Wörter oder 30 Wörter haben. Weder Perceptron noch MLP noch CNN können damit natürlich umgehen.

### 🌉 Vom *Erkennen* zum *Verstehen*

Mit diesem Meilenstein endet die Phase **A** der Reihe. Wir können jetzt:

- (aus Perceptron/MLP) einfache Muster **klassifizieren**,
- (aus CNN + MNIST) sogar **handgeschriebenen Text erkennen** — das ist genau die Aufgabe, mit der LeCun 1998 die Postleitzahlen der US-Post automatisch las.

Das ist ein Etappenziel: Ein Computer kann jetzt Text **lesen**. Aber er **versteht** immer noch nichts. Für ihn ist ein Text nur eine Folge von Pixel-Formen, die er als Buchstaben klassifiziert. Was diese Buchstaben *bedeuten* — dass „König" mit „Königin" verwandt ist, dass „Wolf frisst Schaf" nicht dasselbe ist wie „Schaf frisst Wolf" — davon hat er keine Ahnung.

Ab dem nächsten Meilenstein beginnt deshalb Phase **B**: **Verstehen**. Und der erste Baustein dafür ist die Frage, wie man Wörter überhaupt sinnvoll in einem neuronalen Netz repräsentiert.

---

## 🚀 Nächstes Kapitel: Word Embeddings (Word2Vec)

Wir verlassen die Welt der Bilder und wenden uns Sprache zu. Der erste Schritt: Wie stellt man Wörter für ein neuronales Netz dar?

- **One-Hot** funktioniert, verliert aber jede Bedeutung.
- **Word2Vec** (Mikolov, 2013) lernt Wortvektoren, in denen ähnliche Wörter im Vektorraum nahe beieinander liegen.
- Erstes „Wow": `könig − mann + frau ≈ königin`.

Als Trainingsmaterial verwenden wir dann die **Grimm-Märchen** — sie werden uns bis zum letzten Meilenstein begleiten.

---

## 📚 Referenzen

- Hubel, D. H., & Wiesel, T. N. (1959). *Receptive Fields of Single Neurones in the Cat's Striate Cortex*. Journal of Physiology, 148(3), 574–591.
- Fukushima, K. (1980). *Neocognitron: A Self-Organizing Neural Network Model for a Mechanism of Pattern Recognition Unaffected by Shift in Position*. Biological Cybernetics, 36(4), 193–202.
- LeCun, Y., Bottou, L., Bengio, Y., & Haffner, P. (1998). *Gradient-Based Learning Applied to Document Recognition*. Proceedings of the IEEE, 86(11), 2278–2324.
- Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012). *ImageNet Classification with Deep Convolutional Neural Networks*. NeurIPS.
- He, K., Zhang, X., Ren, S., & Sun, J. (2015). *Deep Residual Learning for Image Recognition*. arXiv:1512.03385.
- Dosovitskiy, A., et al. (2020). *An Image is Worth 16×16 Words: Transformers for Image Recognition at Scale*. arXiv:2010.11929.
