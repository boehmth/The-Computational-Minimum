# KI-Meilenstein 1: Das Perceptron

> **🎯 Warum ist das cool?**
> Ein neuronales Netz mit **einem einzigen Neuron** lernt selbstständig, kleinere von größeren Zahlen zu unterscheiden — nur aus Beispielen, ohne dass ihm jemand die Regel „x₁ < x₂" erklärt hat. Das ist das kleinstmögliche funktionierende „lernende System" — und der Grundbaustein für alles, was danach kommt (auch für ChatGPT).

## 🌉 Der Anfang: Ein einzelnes Neuron lernt

1958 stellte der Psychologe **Frank Rosenblatt** am Cornell Aeronautical Laboratory in Buffalo eine Idee vor, die die Informatik verändern sollte: das **Perceptron**. Sein Aufsatz *„The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain"* (Psychological Review, 1958) war das **erste algorithmisch beschriebene neuronale Netz** und schlug eine Brücke zwischen Psychologie, Neurowissenschaft und Informatik.

Der zentrale Gedanke war radikal: Statt einer Maschine explizit Regeln zu programmieren, sollte sie **aus Beispielen lernen** — indem sie ihre Gewichte anhand ihrer Fehler nach und nach anpasst. Rosenblatt baute sogar eine Hardware-Umsetzung, den **Mark I Perceptron**, der einfache visuelle Muster erkennen konnte.

In diesem Meilenstein programmieren wir genau dieses Modell und lassen es die Regel lernen:

> **Ist die erste Zahl kleiner als die zweite?**

So schlicht das Perceptron auch ist — es enthält bereits den Kern dessen, was maschinelles Lernen so kraftvoll macht: die Fähigkeit, Struktur in Daten durch wiederholtes Sehen und kleine Anpassungen zu entdecken.

---

## 🕰️ Historischer Kontext

| Jahr | Ereignis | Bedeutung |
|------|----------|-----------|
| **1943** | McCulloch & Pitts: künstliches Neuron | Erstes mathematisches Modell eines Neurons — aber ohne Lernen |
| **1949** | Hebb: *„Zellen, die zusammen feuern, verbinden sich"* | Neurobiologische Grundlage für Lernregeln |
| **1958** | **Rosenblatt: Perceptron** | Erstes lernendes neuronales Netz; Cornell baut den *Mark I Perceptron* |
| **1969** | Minsky & Papert: *Perceptrons* | Beweis der Grenzen (XOR nicht lernbar) → löst den ersten *KI-Winter* aus |
| **1986** | Rumelhart, Hinton & Williams: Backpropagation | Ermöglicht mehrschichtige Netze — Comeback der neuronalen Netze |
| **heute** | Milliarden von Perceptron-artigen Neuronen | In jedem Transformer, jedem GPT, jedem Bildmodell |

Das Perceptron ist damit **kein historisches Kuriosum**, sondern der elementare Baustein, aus dem alle modernen KI-Modelle aufgebaut sind.

---

## 🧠 Die Aufgabe: „ist x₁ < x₂?"

Wir geben dem Perceptron Paare $(x_1, x_2)$ und wollen, dass es lernt:

$$
y = \begin{cases} 1 & \text{wenn } x_1 < x_2 \\ 0 & \text{sonst} \end{cases}
$$

Das ist ein **linear trennbares Problem**: Die Entscheidungsgrenze ist die Gerade $x_1 = x_2$ im zweidimensionalen Eingaberaum. Alle Punkte darüber gehören zur Klasse `1`, alle darunter oder darauf zur Klasse `0`.

Um die Aufgabe geometrisch zu sehen, hilft eine **Label-Matrix** für den Bereich 3–9:

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

Alle `1`en liegen **oberhalb** der Diagonalen, alle `0`en **auf oder unterhalb**. Die Entscheidungsgrenze ist eine Gerade durch diese Matrix — genau die Art von Problem, die ein Perceptron lernen kann.

**Warum diese Aufgabe?** Sie ist minimal, aber vollständig:

1. **Linear trennbar** — perfekt zum Perceptron passend.
2. **Zwei Dimensionen** — die gelernte Entscheidungsgrenze lässt sich in der Ebene veranschaulichen.
3. **Generalisierbar prüfbar** — wir trainieren auf 3–9 und testen auf 10–12: hat das Modell die *Regel* gelernt oder nur die Beispiele auswendig?

---

## 🧩 Modellarchitektur

Das Perceptron nimmt **zwei Eingaben**, multipliziert jede mit einem **Gewicht**, addiert einen **Bias**, und gibt das Ergebnis durch eine **Sprungfunktion**:

```

   x1 (erste Zahl)  -----> (w1) ---\
                                    +--> [ SUMME + BIAS ] --> [ SPRUNGFUNKTION ] --> AUSGABE (0/1)
   x2 (zweite Zahl) -----> (w2) ---/

```

Mathematisch:

$$
y = f\Big(\sum_{i=1}^{n} w_i \cdot x_i + b\Big)
$$

- $x_i$: Eingaben (Merkmale)
- $w_i$: Gewichte
- $b$: Bias (verschiebt die Entscheidungsgrenze)
- $f(\cdot)$: Aktivierungsfunktion — hier die Sprungfunktion: `1`, wenn Eingabe ≥ 0, sonst `0`

**Größenordnungen:**
- Eingaben: 2
- Gewichte: 2
- Bias: 1
- Parameter: **3**

Im allgemeinen Fall kann ein Perceptron beliebig viele Eingaben $x_1, \dots, x_n$ mit zugehörigen Gewichten haben. Wir beschränken uns bewusst auf zwei, damit die gelernte Entscheidungsgrenze in der Ebene sichtbar bleibt.

---

## ⚙️ Training

**Perceptron-Lernregel** (Rosenblatt, 1958). Für jedes Trainingsbeispiel wird die Vorhersage berechnet, der Fehler ($t - y$) gemessen und die Parameter angepasst:

$$
w_i \leftarrow w_i + \eta \cdot (t - y) \cdot x_i
$$

$$
b \leftarrow b + \eta \cdot (t - y)
$$

- $\eta$: Lernrate (hier 0.01)
- $t$: Ziel (0 oder 1)
- $y$: aktuelle Vorhersage

**Kein Gradientenabstieg, keine Backpropagation** — dafür ist der Sprung-Aktivierung nicht differenzierbar. Stattdessen: pragmatische Fehlerkorrektur. Bei richtiger Vorhersage passiert nichts, bei falscher Vorhersage werden die Gewichte in Richtung des korrekten Ergebnisses geschoben.

**Konvergenz-Garantie:** Rosenblatt konnte beweisen, dass diese Regel **immer konvergiert**, sofern das Problem linear trennbar ist. Bei nicht linear trennbaren Problemen (wie XOR oder einem Kreis) läuft sie ewig ins Leere.

---

## ▶️ So startest du das Programm

```bash
cd Perceptron/src
python perceptron.py
```

Das Programm:
1. lädt einen der drei Datensätze (`small`, `large`, `circle` — einstellbar über `DATASET_MODE`),
2. trainiert das Perceptron 5 Epochen lang,
3. gibt nach jeder Epoche Fehlerzahl, Genauigkeit, Gewichte und Bias aus,
4. evaluiert das Modell auf einem separaten Testdatensatz.

---

## 📈 Beispielausgabe (echter Trainingslauf, Lernrate = 0.01)

Das folgende Beispiel verwendet den **großen Trainingsdatensatz (3–9)**. Weil dieser den relevanten Eingaberaum gut abdeckt, konvergiert das Perceptron sehr schnell und generalisiert perfekt auf den Testbereich (10–12).

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

**Und der Star des Kapitels — die gelernten Gewichte:**

- $w_1 \approx -0.07$ (**negativ**, für die erste Zahl)
- $w_2 \approx +0.07$ (**positiv**, für die zweite Zahl)
- $b \approx -0.01$ (fast null)

Genau das braucht die Regel „$x_1 < x_2$": Je größer $x_2$ und je kleiner $x_1$, desto stärker wird die gewichtete Summe positiv — und desto sicherer sagt das Perceptron „1". Die Trennlinie geht praktisch durch den Ursprung, wie es sein muss für die Gerade $x_1 = x_2$.

**Das ist der pädagogische Höhepunkt:** Wir sehen dem Modell an den Gewichten an, *dass* es die Regel verstanden hat — nicht nur, dass es die Trainingsbeispiele auswendig kann. Auf ungesehenen Werten (10–12) erreicht es **100 %**, obwohl es diese Zahlen im Training nie gesehen hat.

---

## ❗ Ehrliche Diskussion: Wann scheitert das Perceptron?

Das Perceptron ist **kein Universalwerkzeug**. Es hat eine harte Grenze: Es kann **nur linear trennbare Probleme** lösen. Das sieht man dramatisch am **Kreis-Datensatz** (setze `DATASET_MODE = "circle"` in `perceptron.py`):

```
Training mit Datensatzmodus: circle
Epoche  1: Fehler=24, Genauigkeit=0.70, Gewichte=['0.00', '-0.12'], Bias=0.00
Epoche  2: Fehler=27, Genauigkeit=0.67, Gewichte=['-0.05', '-0.14'], Bias=0.01
Epoche  3: Fehler=29, Genauigkeit=0.64, Gewichte=['-0.02', '-0.16'], Bias=0.04
Epoche  4: Fehler=30, Genauigkeit=0.63, Gewichte=['-0.03', '-0.18'], Bias=0.06
Epoche  5: Fehler=28, Genauigkeit=0.65, Gewichte=['-0.07', '-0.13'], Bias=0.08

Test-Genauigkeit: 54.3%
```

Die Genauigkeit **stabilisiert sich nicht** und liegt am Ende bei rund 54 % — kaum besser als Zufall. Die Fehleranzahl steigt sogar über die Epochen. Warum? Die tatsächliche Entscheidungsgrenze ist ein *Kreis*, aber das Perceptron kann nur eine Gerade lernen. Jede Gerade zerlegt den Kreis in zwei ungefähr gleich große Hälften, sodass zwangsläufig etwa die Hälfte der Punkte falsch klassifiziert wird. Es ist **nicht** ein Trainings- oder Datenproblem — es ist eine **grundsätzliche Darstellungs­beschränkung**.

**Auch beim kleinen Datensatz** (`DATASET_MODE = "small"`, nur Paare aus 4–7) sieht man ein zweites Problem: zu wenig Vielfalt in den Trainingsdaten führt zu wackeligen Gewichten und schlechterer Generalisierung. Das Problem ist zwar linear trennbar, aber das Modell hat einfach nicht genug Beispiele gesehen, um die *ganze* Regel zu extrahieren.

Diese beiden Fälle zeigen die zwei klassischen Fehlerquellen im maschinellen Lernen:

1. **Falsches Modell für das Problem** (Kreis-Datensatz) → egal wie viele Daten, es geht nicht.
2. **Zu wenige/schlecht verteilte Daten** (kleiner Datensatz) → Modell würde funktionieren, aber sieht die Regel nicht.

Genau diese Grenzen motivieren das nächste Kapitel: **Mehrschichtige Netze**, die auch nichtlineare Muster lernen können.

---

## 📝 Übungen

**1. Den erweiterten linearen Datensatz nutzen (alle Paare aus 3–9).** Setze in `perceptron.py`: `DATASET_MODE = "large"`. Dieser Datensatz enthält alle Paare $(x_1, x_2)$ für Zahlen 3–9 und bietet dem Perceptron eine breite, vielfältige Sammlung von Beispielen. **Was du beobachten sollst:** schnelle und stabile Konvergenz, sinnvolle Gewichte, gute Generalisierung auf nicht gesehene Werte (z. B. 10–12).

**2. Den Kreis-Datensatz nutzen.** Setze `DATASET_MODE = "circle"`. Punkte innerhalb eines Kreises bekommen Label `1`, außerhalb `0`. **Was du beobachten sollst:** Das Perceptron konvergiert *nicht*, die Genauigkeit bleibt bei ~50 %, die Gewichte stabilisieren sich nicht.

**3. Lernrate variieren.** Setze `LERNRATE = 0.001` und `LERNRATE = 0.5`. Wie ändert sich die Konvergenz? Bei sehr großer Lernrate „springen" die Gewichte, bei sehr kleiner Lernrate braucht das Modell mehr Epochen.

**4. Andere lineare Regel.** Ändere `datasets.py`, sodass die Label-Funktion nicht mehr „$x_1 < x_2$" ist, sondern z. B. „$x_1 + x_2 > 10$". Bleibt das linear trennbar? (Antwort: ja — es ist immer noch eine Gerade.) Was wären die erwarteten Vorzeichen der Gewichte?

**5. Extrapolation testen.** Trainiere auf 3–9 und teste auf $x_1, x_2 \in \{100, 101, 102\}$. Funktioniert es immer noch? Warum? *(Antwort: ja, weil die Regel skalenunabhängig ist — das Perceptron hat *keine* Zahlen auswendig gelernt, sondern eine geometrische Beziehung.)*

---

## 🧭 Wo steht das Perceptron heute?

**Kurz gesagt:** Als eigenständiges Modell ist das Perceptron praktisch nie mehr im Einsatz — es ist schlicht zu schwach. Aber der **konzeptionelle Kern** ist in **jedem** modernen neuronalen Netz enthalten:

- Ein einzelnes Neuron in einer Dense-Schicht eines Transformers rechnet **exakt dasselbe** wie hier: gewichtete Summe plus Bias, dann Aktivierung. Nur die Aktivierungsfunktion ist heute differenzierbar (ReLU, GELU) statt eine harte Sprungfunktion.
- Ein Modell wie GPT-4 besteht aus **Hunderten Milliarden** solcher Perceptron-artigen Bausteine, in vielen Schichten gestapelt und parallel geschaltet.
- **Die Lernregel** (Fehler messen, Gewichte anpassen) hat sich verfeinert (Backpropagation im nächsten Kapitel), aber das Grundprinzip *„lerne aus deinen Fehlern"* ist geblieben.

Die Grenze, die wir hier gefunden haben — nur lineare Trennung — hat 1969 Minsky & Papert dazu veranlasst, das Perceptron scharf zu kritisieren; das löste den ersten **KI-Winter** aus. Erst mit Backpropagation (1986) und mehrschichtigen Netzen wurde diese Grenze überwunden.

---

## 🧠 Abschließende Bemerkungen

Wenn du dir dieses Kapitel angesehen hast, hast du die grundlegendste Idee des maschinellen Lernens in ihrer reinsten Form gesehen:

1. **Ein Modell mit wenigen Parametern**, dessen Ausgabe eine einfache Funktion der Eingaben ist.
2. **Eine Lernregel**, die die Parameter anhand der Fehler schrittweise anpasst.
3. **Generalisierung**: das Modell lernt eine Regel, nicht die Daten.

Und eine subtile, aber wichtige Einsicht: **Das einlagige Perceptron ist immer ein linearer Klassifikator.** Die Gleichung $w_1 x_1 + w_2 x_2 + \dots + w_n x_n + b = 0$ definiert eine Hyperebene — eine Gerade in 2D, eine Ebene in 3D. Kein Perceptron dieser Welt kann ohne Trick eine gekrümmte Grenze lernen. Diese Grenze ist kein Implementierungsdetail, sondern eine **grundsätzliche Darstellungsbeschränkung**.

Genau diese Einsicht war 1969 der Grund, warum viele die neuronalen Netze für tot erklärten. Der Weg heraus war nicht, das Perceptron zu verbessern, sondern **viele Perceptrons zu stapeln** — und dafür einen neuen Lernalgorithmus zu erfinden.

---

## 🚀 Nächstes Kapitel: Multi-Layer Perceptron (MLP)

Wir stapeln mehrere Perceptron-Schichten übereinander und ersetzen die Sprungfunktion durch differenzierbare Aktivierungen. Das Ergebnis:

- **Nichtlineare Entscheidungsgrenzen** — Kreise, Kurven, beliebige Formen.
- **Backpropagation** — der Algorithmus, der es erlaubt, Fehler durch die Schichten „zurückzupropagieren".
- **Universelle Approximation** — mit genügend Neuronen kann ein MLP *jede* stetige Funktion beliebig genau annähern.

Der KI-Winter endet dort.

---

## 📚 Referenzen

- McCulloch, W. S., & Pitts, W. (1943). *A Logical Calculus of the Ideas Immanent in Nervous Activity*. Bulletin of Mathematical Biophysics, 5, 115–133.
- Hebb, D. O. (1949). *The Organization of Behavior*. Wiley.
- Rosenblatt, F. (1958). *The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain*. Psychological Review, 65(6), 386–408.
- Minsky, M., & Papert, S. (1969). *Perceptrons: An Introduction to Computational Geometry*. MIT Press.
- Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). *Learning Representations by Back-Propagating Errors*. Nature, 323(6088), 533–536.
