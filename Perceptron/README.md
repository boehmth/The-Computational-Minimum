# KI‑Meilenstein 1: Das Perceptron

> **🎯 Warum ist das cool?**
> Ein neuronales Netz mit **einem einzigen Neuron** lernt selbstständig, kleinere von größeren Zahlen zu unterscheiden — nur aus Beispielen, ohne dass ihm jemand die Regel „x₁ < x₂" erklärt hat. Das ist das kleinstmögliche funktionierende „lernende System" — und der Grund­baustein für alles, was danach kommt (auch für ChatGPT).

## 📖 Einleitung
1958 stellte der Psychologe **Frank Rosenblatt** in seiner wegweisenden Arbeit *„The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain"* (Psychological Review, Bd. 65, Nr. 6, S. 386–408) das **Perceptron** vor. Diese Arbeit gilt weithin als **das erste algorithmisch beschriebene neuronale Netz** und schlägt eine Brücke zwischen Psychologie, Neurowissenschaft und Informatik.

Rosenblatt, damals am **Cornell Aeronautical Laboratory** in Buffalo (New York) tätig, verband Erkenntnisse aus Psychologie, Neurowissenschaft und Informatik. Sein interdisziplinärer Hintergrund erlaubte ihm, das Perceptron nicht nur als mathematisches Modell zu formulieren, sondern es zugleich als einen ersten Schritt zum Verständnis der Informations­verarbeitung im Gehirn zu begreifen.

Das Perceptron zeigte, dass Maschinen **Muster klassifizieren lernen** können, indem sie ihre Gewichte anhand von Fehlern anpassen — ein Vorgriff auf das moderne maschinelle Lernen. Rosenblatt baute sogar eine Hardware‑Umsetzung, den **Mark I Perceptron**, der einfache visuelle Muster erkennen konnte. Auch wenn das Modell auf linear trennbare Probleme beschränkt war (das XOR-Problem konnte es nicht lösen), war seine Veröffentlichung ein **Meilenstein der KI‑Forschung** und entfachte jahrzehntelange Erkundungen zu neuronalen Netzen.

In diesem Meilenstein programmieren wir ein einfaches **Perceptron**, das die Regel lernen soll:

> **Ist die erste Zahl kleiner als die zweite?**

Das ist ein linear trennbares Problem: Die Entscheidungsgrenze ist die Gerade

$x_1 = x_2$

im zweidimensionalen Eingaberaum. Alle Punkte unterhalb dieser Geraden (bei denen $x_1 < x_2$) gehören zur Klasse `1`, alle Punkte auf oder oberhalb gehören zur Klasse `0`. Wir werden sehen, dass diese scheinbar einfache Regel bereits die grundlegenden Prinzipien modernen maschinellen Lernens erlebbar macht:

- **Lernen aus Daten statt aus expliziten Regeln**,
- **Anpassung der Parameter (Gewichte und Bias) auf Grundlage von Fehlern**,
- **iterative Verbesserung über mehrere Trainings­durchläufe (Epochen) hinweg**, und
- **Generalisierung über die im Training gesehenen Beispiele hinaus**.

So schlicht das Perceptron auch ist — es enthält bereits den Kern dessen, was maschinelles Lernen so kraftvoll macht: die Fähigkeit, Struktur in Daten durch wiederholtes Sehen und kleine Anpassungen zu entdecken. In diesem Meilenstein bauen und erkunden wir diesen Mechanismus in seiner reinsten Form — mit einem minimalen Datensatz und einer transparenten Lernregel, die zeigt, wie eine Maschine eine Entscheidungsgrenze von Grund auf lernt.

---

## 🎯 Lernziele
- Verstehen, wie ein Perceptron zwei Klassen mit einer Geraden trennt.
- Beobachten, wie sich Gewichte und Bias während des Trainings anpassen.
- Die gelernten Parameter deuten: Ein Gewicht wird negativ (für die erste Zahl), das andere positiv (für die zweite Zahl).
- Die **Grenzen des Perceptrons** erkennen: Es funktioniert nur bei linear trennbaren Problemen.
- Sehen, wie **Menge und Vielfalt der Trainingsdaten** die Generalisierungs­fähigkeit beeinflussen.

## 📊 Konzeptuelles Diagramm

Das folgende Diagramm zeigt das Perceptron in seiner einfachsten Form für diesen Meilenstein: Es nimmt **zwei Eingaben** (die beiden zu vergleichenden Zahlen), multipliziert jede mit einem **Gewicht** (W1, W2), addiert einen **Bias** und gibt das Ergebnis durch eine **Sprungfunktion**, um eine binäre Ausgabe (0 oder 1) zu erzeugen.

```

   x1 (erste Zahl)  -----> (W1) ---\
                                    +--> [ SUMME + BIAS ] --> [ SPRUNGFUNKTION ] --> AUSGABE (0/1)
   x2 (zweite Zahl) -----> (W2) ---/

```

Im allgemeinen Fall kann ein Perceptron beliebig viele Eingaben $x_1, x_2, \dots, x_n$ mit zugehörigen Gewichten $w_1, w_2, \dots, w_n$ verarbeiten. Die Struktur der Rechnung bleibt gleich — nur die Anzahl der Eingaben und Gewichte wächst. In diesem Meilenstein beschränken wir uns bewusst auf zwei Eingaben, damit die Geometrie und die gelernte Entscheidungsgrenze in der 2D-Ebene leicht zu veranschaulichen sind.

## ⚙️ Mathematische Formulierung

Das Perceptron berechnet seine Ausgabe als:

$$
y = f\Big(\sum_{i=1}^{n} w_i \cdot x_i + b\Big)
$$

- $x_i$: Eingaben (Merkmale)
- $w_i$: Gewichte (Wichtigkeit jeder Eingabe)
- $b$: Bias (verschiebt die Entscheidungsgrenze)
- $f(\cdot)$: Aktivierungsfunktion (hier: Sprungfunktion → gibt `1` aus, wenn Eingabe ≥ 0, sonst `0`)

Update-Regel:

$$
w_i \leftarrow w_i + \eta \cdot (t - y) \cdot x_i
$$

$$
b \leftarrow b + \eta \cdot (t - y)
$$

## ▶️ So startest du das Programm
Der Python-Code liegt in `Perceptron/src/perceptron.py`.

### Schritte
1. Öffne ein Terminal und wechsele in das Projekt­verzeichnis.
2. Starte das Programm mit:

    ```bash
    python src/perceptron.py
    ```

Beobachte die Ausgabe:

Das Programm gibt die gelernten Gewichte und den Bias nach dem Training aus.

Du siehst, wie das Perceptron seine Gewichte anpasst, um die Fälle korrekt zu trennen.

## 🧩 Beispielaufgabe

Um die Aufgabe geometrisch zu verstehen, hilft es, die Zielwerte (Labels) als **Matrix** zu betrachten. Jede Zeile entspricht einem festen Wert von **x₁**, jede Spalte einem festen Wert von **x₂**. Der Wert ist `1`, wenn $x_1 < x_2$, und sonst `0`.

Unten sehen wir die Label-Matrix für den Bereich **3–9**:

```
       x2 →    3  4  5  6  7  8  9
x1 ↓
3           [ 0  1  1  1  1  1  1 ]
4           [ 0  0  1  1  1  1  1 ]
5           [ 0  0  0  1  1  1  1 ]
6           [ 0  0  0  0  1  1  1 ]
7           [ 0  0  0  0  0  1  1 ]
8           [ 0  0  0  0  0  0  1 ]
9           [ 0  0  0  0  0  0  0 ]
```

Diese Matrix macht die Struktur der Aufgabe sichtbar:

- Alle `1`en liegen **oberhalb** der Diagonalen $x_1 = x_2$.
- Alle `0`en liegen **auf oder unterhalb** dieser Diagonalen.
- Die Entscheidungsgrenze ist also eine **Gerade** durch die Matrix.

Diese Darstellung zeigt: Die Regel $x_1 < x_2$ ist im Kern ein **geometrisches Trennproblem** — und genau so etwas lernt das Perceptron.


## 📈 Beispielausgabe (Lernrate = 0.01)

Das folgende Beispiel verwendet den **grossen Trainingsdatensatz (3–9)**. Weil dieser den relevanten Eingaberaum gut abdeckt, konvergiert das Perceptron sehr schnell und generalisiert perfekt auf den Testbereich (10–12).

```
Training mit Datensatzmodus: large
Epoche  1: Fehler=9, Genauigkeit=0.82, Gewichte=['-0.07', '0.07'], Bias=-0.01
Epoche  2: Fehler=0, Genauigkeit=1.00, Gewichte=['-0.07', '0.07'], Bias=-0.01
Epoche  3: Fehler=0, Genauigkeit=1.00, Gewichte=['-0.07', '0.07'], Bias=-0.01
Epoche  4: Fehler=0, Genauigkeit=1.00, Gewichte=['-0.07', '0.07'], Bias=-0.01
Epoche  5: Fehler=0, Genauigkeit=1.00, Gewichte=['-0.07', '0.07'], Bias=-0.01

Gelernte Parameter:
Gewichte=['-0.07', '0.07'], Bias=-0.01

Ergebnisse (Test):
x1 | x2 | Ziel | Vorhersage | korrekt?
-------------------------------------
10 | 10 |  0   |     0      |  ok
10 | 11 |  1   |     1      |  ok
10 | 12 |  1   |     1      |  ok
11 | 10 |  0   |     0      |  ok
11 | 11 |  0   |     0      |  ok
11 | 12 |  1   |     1      |  ok
12 | 10 |  0   |     0      |  ok
12 | 11 |  0   |     0      |  ok
12 | 12 |  0   |     0      |  ok

Test-Genauigkeit: 100.0%
```

**Was du hier siehst:**

- **Gewichte** haben nach dem Training ein klares Vorzeichen: $w_1 \approx -0.07$ (negativ, für die erste Zahl) und $w_2 \approx +0.07$ (positiv, für die zweite Zahl). Genau das braucht die Regel „$x_1 < x_2$": Je größer $x_2$ und je kleiner $x_1$, desto stärker ist die Ausgabe positiv.
- **Der Bias** bleibt fast null — die Trennlinie geht durch den Ursprung.
- **Nach nur einer Epoche** ist die Trainings­genauigkeit bereits sehr hoch, ab Epoche 2 keine Fehler mehr.
- **Auf ungesehenen Werten (10–12) erreicht das Modell 100 %** — es hat die Regel wirklich verstanden, nicht nur die Trainingsdaten auswendig gelernt.

Setze `DATASET_MODE = "small"` am Anfang von `perceptron.py`, um zu sehen, wie zu wenig Trainings­vielfalt die Generalisierung verschlechtert.

## 📝 Übungen

### **1. Den erweiterten linearen Datensatz nutzen (alle Paare aus 3–9)**

Setze in `perceptron.py`: `DATASET_MODE = "large"`.
Dieser Datensatz enthält alle Paare ($x_1$, $x_2$) für Zahlen 3–9 und bietet dem Perceptron eine breite und vielfältige Sammlung von Beispielen für die lineare Regel $x_1 < x_2$.

**Was du beobachten sollst:**
- schnelle und stabile Konvergenz
- sinnvolle Gewichte
- gute Generalisierung auf nicht gesehene Werte (z. B. 10–12)

**Lernziel:**
Ein Perceptron funktioniert gut, wenn das Problem linear trennbar ist **und** die Trainings­daten den relevanten Eingaberaum abdecken.

### **2. Den Kreis-Datensatz nutzen (widersprüchliches / nicht-lineares Beispiel)**

Setze in `perceptron.py`: `DATASET_MODE = "circle"`.
Dieser Datensatz kennzeichnet Punkte innerhalb eines Kreises mit `1` und Punkte außerhalb mit `0`. Keine Gerade kann diese beiden Regionen trennen.

**Was du beobachten sollst:**
- Das Perceptron konvergiert nicht.
- Die Genauigkeit bleibt niedrig oder schwankt.
- Die gelernten Gewichte ergeben keine sinnvolle Entscheidungsgrenze.

Hinweis: Für den Kreis-Datensatz brauchst du keinen separaten Testdatensatz. Das Perceptron scheitert schon bei den Trainingsdaten selbst, sodass ein zusätzlicher Test keinen weiteren Erkenntnisgewinn bringt. Wenn du dennoch einen Testdatensatz verwendest, muss er ebenfalls aus Kreisdaten bestehen.

**Lernziel:**
Diese Übung demonstriert die grundlegende Beschränkung des Perceptrons: Es kann keine nichtlinearen Entscheidungsgrenzen lernen, ganz gleich, wie lange man trainiert.

## 🧪 Zentrale Beobachtungen

Die folgenden Beobachtungen fassen zusammen, was du beim Ausführen der beiden Übungen sehen solltest:

- Mit dem **erweiterten linearen Datensatz (alle Paare 3–9)** konvergiert das Perceptron schnell, lernt stabile Gewichte und generalisiert gut auf nicht gesehene Werte. Dies zeigt: Ein linear trennbares Problem wird zuverlässig gelöst, wenn die Trainings­daten den relevanten Eingaberaum abdecken.

- Mit dem **Kreis-Datensatz** konvergiert das Perceptron nicht, weil das Muster nicht linear trennbar ist. Die Genauigkeit schwankt, die Gewichte stabilisieren sich nicht, und die gelernte Entscheidungsgrenze bleibt bedeutungslos. In der Praxis erreicht das Perceptron etwa 50 % Genauigkeit. Der Grund: Die tatsächliche Entscheidungsgrenze ist ein Kreis, während ein Perceptron nur eine Gerade lernen kann. Jede Gerade zerlegt den Kreis in zwei etwa gleich große Regionen, sodass das Modell zwangs­läufig rund die Hälfte der Punkte falsch klassifiziert. Anders gesagt: Die beste lineare Trennlinie ist hier nicht besser als zufälliges Raten.

- Selbst bei linearen Problemen kann **unzureichende oder schlecht verteilte Trainings­daten** die Genauigkeit senken — wie in der Beispielausgabe mit dem kleinen Datensatz gezeigt.

- In realen Anwendungen erreicht kein Modell zuverlässig 100 % Genauigkeit; das Perceptron bildet keine Ausnahme, besonders wenn die Daten begrenzt oder widersprüchlich sind.


## 🧠 Abschließende Bemerkungen

Das in diesem Meilenstein umgesetzte Perceptron veranschaulicht eine fundamentale geometrische Tatsache: Ein einlagiges Perceptron ist immer ein **linearer Klassifikator**. Es berechnet eine gewichtete Summe

$$
w_1 x_1 + w_2 x_2 + \dots + w_n x_n + b
$$

und wendet eine Sprungfunktion an, um zwischen zwei Klassen zu entscheiden. Die Gleichung

$$
w_1 x_1 + w_2 x_2 + \dots + w_n x_n + b = 0
$$

definiert eine **Hyperebene** in einem $n$-dimensionalen Raum — eine Gerade in 2D, eine Ebene in 3D und eine linear trennende Fläche in beliebigen Dimensionen. Als Folge kann ein Perceptron nur **linear trennbare** Muster lernen.

Das erklärt, warum das Modell die Regel $x_1 < x_2$ mühelos lernt: Die Entscheidungsgrenze ist eine Gerade. Es erklärt aber auch, warum das Perceptron beim Kreis-Datensatz scheitert: Keine einzelne Gerade (oder Ebene, oder Hyperebene) kann das Innere eines Kreises (oder einer Kugel) vom Äußeren trennen. Diese Grenze ist kein Implementierungs­detail, sondern eine grundsätzliche Darstellungs­beschränkung.

Diese Einsicht wurde von **Minsky & Papert (1969)** in ihrem einflussreichen Buch *Perceptrons* formalisiert. Sie bewiesen, dass einlagige Perceptrons keine nichtlinearen Funktionen wie Parität, Symmetrie oder einfache geometrische Formen darstellen können. Diese Analyse markierte einen Wendepunkt in der Geschichte der neuronalen Netze und motivierte die Entwicklung **mehrschichtiger Architekturen**, die nichtlineare Entscheidungsgrenzen lernen können.

Im nächsten Meilenstein erweitern wir das Perceptron zu einem **Multi-Layer-Perceptron (MLP)** und führen den **Backpropagation-Algorithmus** ein, mit dem das Netz komplexe, nichtlineare Muster wie Kreise, Buchstaben oder beliebige Formen lernen kann.


## 📚 Referenzen

Hodgkin, A. L., & Huxley, A. F. (1952). *A quantitative description of membrane current and its application to conduction and excitation in nerve*. Journal of Physiology, 117(4), 500–544.

Minsky, M., & Papert, S. (1969). *Perceptrons: An Introduction to Computational Geometry*. MIT Press.

Rosenblatt, F. (1958). *The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain*. Psychological Review, 65(6), 386–408.
