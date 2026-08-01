# KI-Meilenstein 2: Das Multi-Layer-Perzeptron (MLP)

> **🎯 Warum ist das cool?**
> Wir stapeln nur eine **zweite Schicht Neuronen** auf das Perceptron drauf — und plötzlich kann das Netz nicht nur Geraden ziehen, sondern **beliebig geschwungene Formen** erkennen: Kreise, Buchstaben, komplizierte Muster. Dieser eine Baustein — zusammen mit dem Trainingsalgorithmus **Backpropagation** — ist der Grundstein von *Deep Learning* und läuft heute in jeder KI, von der Handschrift­erkennung deiner Bank bis zu ChatGPT.

## 🌉 Vom Perceptron zum tieferen Netz

Im letzten Kapitel hat unser Perceptron eine Regel gelernt, die sich durch eine **Gerade** ausdrücken lässt: „$x_1 < x_2$". Beim Kreis-Datensatz aber ist es kläglich gescheitert — 54 % Genauigkeit, kaum besser als Zufall. Der Grund: **ein einzelnes Neuron kann prinzipiell keine gebogene Grenze zeichnen.**

Damit ein Netz komplexere Muster erkennen kann, braucht es zwei Zutaten:

1. **Mehrere Schichten** von Neuronen (statt nur einer),
2. eine **nicht-lineare Aktivierungsfunktion** dazwischen.

Genau das leistet das **Multi-Layer-Perzeptron (MLP)** — der erste Schritt in Richtung dessen, was wir heute *Deep Learning* nennen. Und mit ihm kommt der Algorithmus, der die gesamte moderne KI überhaupt erst möglich gemacht hat: **Backpropagation**.

---

## 🕰️ Historischer Kontext

| Jahr | Ereignis | Bedeutung |
|------|----------|-----------|
| **1969** | Minsky & Papert: *Perceptrons* | Beweis, dass einlagige Perceptrons XOR nicht lösen können → erster KI-Winter |
| **1974** | Werbos: erste Backprop-Formulierung (Dissertation) | Idee ist da, wird aber weitgehend übersehen |
| **1986** | **Rumelhart, Hinton & Williams: *„Learning representations by back-propagating errors"*** | *Nature*-Publikation macht Backprop populär → Ende des ersten KI-Winters |
| **1989** | LeCun: erste erfolgreiche Anwendung auf Handschrifterkennung | Erste kommerzielle Anwendung neuronaler Netze (Postleitzahlen) |
| **2006** | Hinton et al.: Deep Belief Networks | Beginn des *Deep-Learning-Booms* |
| **heute** | Feed-Forward-Blöcke in jedem Transformer | GPT-4 enthält 96 MLP-Blöcke übereinander |

Backpropagation ist damit **das absolute Fundament** aller modernen neuronalen Netze — CNNs, RNNs, Transformer und LLMs beruhen alle darauf.

---

## 🧠 Die Aufgabe: Buchstaben aus 9×9-Pixeln erkennen

Wir stellen jeden Buchstaben als **9×9-Bitmap** aus 0/1-Werten dar. Das MLP soll lernen, die drei Buchstaben **A, L, R** zu unterscheiden:

```
Buchstabe A:              Buchstabe L:              Buchstabe R:
.........                 .........                 .........
...###...                 .##......                 .######..
..#####..                 .##......                 .##...##.
.##...##.                 .##......                 .##...##.
.##...##.                 .##......                 .######..
.#######.                 .##......                 .##..##..
.#######.                 .##......                 .##...##.
.##...##.                 .########                 .##...##.
.........                 .........                 .........
```

**Warum diese Aufgabe?** Sie hat für unseren didaktischen Zweck genau die richtige Größe:

1. **Nicht linear trennbar** — kein Perceptron dieser Welt könnte diese Muster mit einer einzigen Geraden auseinanderhalten.
2. **Klein genug** für reines Python — jeder Rechenschritt bleibt lesbar (keine Bibliotheken).
3. **Robustheits-Tests möglich** — wir können Rauschen hinzufügen und Bilder verschieben, um die Grenzen des Modells zu erkunden.
4. **Reale Anwendung als Vorbild** — genau so hat 1989 LeCun Postleitzahlen erkannt, nur mit größerem Datensatz.

---

## 🧩 Modellarchitektur

Ein MLP erweitert das Perceptron um zwei entscheidende Konzepte:

- **Verborgene Schichten (Hidden Layers)** — eine Zwischenschicht zwischen Eingabe und Ausgabe. Sie lernen, aus den Rohdaten sinnvolle **Zwischenmerkmale** zu extrahieren.
- **Nicht-lineare Aktivierung** (bei uns: Sigmoid). Ohne sie wäre ein Netz mit vielen Schichten immer noch nur ein linearer Klassifikator — die Nicht-Linearität macht das Netz **ausdrucksstärker**.

Unser Modell besteht aus drei Schichten:

```
 81 Pixel (Eingabe)
       │
       ▼
 ┌─────────────────────────────────────┐
 │  Dense: 81 → 20  (Sigmoid)          │  ← "verborgene Schicht"
 │  lernt Zwischen-Merkmale            │
 └─────────────────────────────────────┘
       │
       ▼
 ┌─────────────────────────────────────┐
 │  Dense: 20 → 3   (Sigmoid)          │  ← Ausgabe: Vertrauen pro Klasse
 └─────────────────────────────────────┘
       │
       ▼
   [A / L / R]  →  argmax  →  Vorhersage
```

**Größenordnungen:**
- Eingaben: 81 (9×9 Pixel)
- Verborgene Neuronen: 20
- Ausgabe: 3 (A, L, R)
- Parameter: 81·20 + 20 + 20·3 + 3 ≈ **1 700**

Damit ist das MLP **500× größer als das Perceptron** — aber immer noch winzig verglichen mit modernen Netzen (GPT-4: ~1.7 Billionen Parameter, also **10⁹-mal so groß**).

---

## ⚙️ Training: Backpropagation + Gradientenabstieg

Das Training verwendet drei Zutaten:

- **Mittlerer quadratischer Fehler (MSE)** als Verlustfunktion,
- **Gradientenabstieg** als Optimierer,
- **Backpropagation**, um die Gradienten Schicht für Schicht rückwärts zu bestimmen.

Der Kerntrick: Wir berechnen zuerst den Fehler an der Ausgabeschicht und propagieren ihn dann *rückwärts* durch das Netz. Für jede Verbindung berechnen wir, wie sehr sie zum Gesamtfehler beiträgt — und passen genau diese Gewichte an. Das ist im Wesentlichen die **Kettenregel der Differentialrechnung**, angewandt Schicht für Schicht.

Alles wird **händisch** implementiert — kein Framework, keine `torch.nn`-Bausteine. Jede einzelne Multiplikation ist im Code sichtbar. Das ist der ganze Punkt dieses Kapitels: Man sieht Backpropagation zum ersten Mal *funktionieren*.

**Hyperparameter:**
- Lernrate: 0.01
- Epochen: 5 000 (jede Epoche = alle drei Beispiele einmal durch das Netz)

---

## ▶️ So startest du das Programm

```bash
cd MLP/src
python mlp.py
```

Das Programm:
1. lädt die 9×9-Bitmaps für A, L, R,
2. trainiert das MLP über 5 000 Epochen (~10 Sekunden auf CPU),
3. wendet **leichtes Rauschen** auf die Bilder an und lässt das Netz die verrauschten Versionen klassifizieren.

---

## 📈 Beispielausgabe (echter Trainingslauf)

```
Epoche 0:    Gesamtfehler=2.2783
Epoche 500:  Gesamtfehler=1.1290
Epoche 1000: Gesamtfehler=0.5388
Epoche 1500: Gesamtfehler=0.2746
Epoche 2000: Gesamtfehler=0.1657
Epoche 2500: Gesamtfehler=0.1137
Epoche 3000: Gesamtfehler=0.0847
Epoche 3500: Gesamtfehler=0.0667
Epoche 4000: Gesamtfehler=0.0546
Epoche 4500: Gesamtfehler=0.0460

--- Vorhersagen bei leichtem Rauschen ---
A -> vorhergesagt: A (Vertrauen=0.42)
L -> vorhergesagt: L (Vertrauen=0.60)
R -> vorhergesagt: R (Vertrauen=0.61)
```

**Das ist der pädagogische Höhepunkt:** Der Gesamtfehler fällt **kontinuierlich und monoton** — genau das, was Backpropagation leisten soll. Das Netz lernt aus seinen Fehlern, Schritt für Schritt, ohne dass wir ihm die Regel „das ist ein A" jemals explizit gesagt hätten.

Bei leichtem Rauschen (30 zufällig umgekippte Pixel) bleiben alle drei Vorhersagen **korrekt** — das MLP hat also nicht nur die Bilder auswendig gelernt, sondern eine echte Robustheit gegenüber kleinen Bildstörungen entwickelt.

---

## ❗ Ehrliche Diskussion: Zwei Schwächen werden sichtbar

### Schwäche 1: Rauschen ist gefährlich

Wir kippen zufällig einige Pixel im Eingabebild um:

- **kleines Rauschen** → das Modell bleibt richtig (siehe oben),
- **mittleres Rauschen** → das Vertrauen sinkt deutlich,
- **starkes Rauschen** → das Modell irrt sich.

Was das offenbart:

- Manche Pixel sind **sehr wichtig** (hohe Gewichte im Netz),
- andere sind fast **egal** (Gewichte nahe null),
- Rauschen schiebt die Eingabe **über die gelernte Entscheidungsgrenze**.

Das ist qualitativ nicht anders als beim Perceptron — nur die Grenze ist jetzt nicht mehr eine Gerade, sondern eine gebogene Hyperfläche im 81-dimensionalen Raum.

### Schwäche 2: Verschiebung um einen Pixel zerstört alles

Wenn wir dasselbe Buchstaben-Bitmap um **einen einzigen Pixel** nach rechts verschieben:

- versagt das MLP fast vollständig,
- viele verschobene Bilder werden gleich klassifiziert (meist als „A"),
- das Vertrauen wird niedrig und schwankt.

Das offenbart eine **grundlegende** Schwäche:

> **MLPs verstehen keine räumliche Struktur.**
> Für sie ist ein Bild einfach ein flacher Vektor aus 81 Zahlen. Es gibt keinen Begriff von „das Pixel daneben" oder „dieselbe Form, nur woanders".

Genau das motiviert das nächste Kapitel: **das Convolutional Neural Network (CNN)**, das Bildstruktur explizit ausnutzt.

---

## 📝 Übungen

**1. Hidden-Size variieren.** Ändere in `mlp.py` den Parameter `hidden_size` von 20 auf 5 und dann auf 100. Was passiert mit dem Trainingsfehler? Bei welcher Größe wird die Konvergenz merklich langsamer bzw. schneller? Bei welcher Größe könnte Overfitting einsetzen (Netz merkt sich die drei Bilder statt zu generalisieren)?

**2. Weitere Buchstaben hinzufügen.** Erweitere `datasets.py` um einen vierten Buchstaben (z. B. `B` oder `C`). Musst du dann `output_size` anpassen? Bleibt der Fehler weiterhin monoton fallend?

**3. Rauschen intensiv testen.** In `mlp.py` ruft `main()` `add_noise(vektor, flips=30)` auf. Erhöhe `flips` schrittweise auf 40, 50, 60 — ab welchem Rauschpegel bricht die Vorhersage zusammen? Kommt der Bruch abrupt oder graduell?

**4. Bild verschieben.** Schreibe eine kleine Funktion `shift_bitmap(bitmap, dx, dy)`, die eine 9×9-Matrix zyklisch verschiebt, und teste die Vorhersage-Genauigkeit für `dx=1, dy=0`. Wie viele der drei Buchstaben werden noch korrekt erkannt?

**5. Aktivierungs­funktion ersetzen.** Ersetze die Sigmoid-Aktivierung durch **ReLU** (`max(0, x)`). Trainingsfehler? Konvergenz? *Achtung*: Die Ableitung ist einfacher, aber die Ausgabeschicht sollte weiterhin Sigmoid bleiben, damit die Werte im Intervall [0, 1] als Vertrauens­wert interpretierbar bleiben.

---

## 🧭 Wo steht das MLP heute?

**Kurz gesagt:** Als eigenständige Architektur wird das MLP für ernsthafte Aufgaben kaum noch verwendet — Bilder gehen zu CNNs, Sprache zu Transformern. Aber:

- **Backpropagation ist das absolute Rückgrat** aller modernen neuronalen Netze. GPT-4, Stable Diffusion, AlphaFold, autonome Fahrzeuge — alle werden mit exakt demselben Algorithmus trainiert, den du hier gerade selbst geschrieben hast. Nur läuft er dort auf GPU-Clustern mit Billionen von Operationen pro Sekunde, statt in reinem Python mit for-Schleifen.
- **MLP-Schichten sind überall.** In einem Transformer heißen sie *„Feed-Forward-Blöcke"* — jeder Transformer-Block enthält ein 2-lagiges MLP. GPT-4 hat davon **96 Stück** übereinander. Anders gesagt: **Etwa die Hälfte der Rechenleistung** eines Transformers geht in genau die Art von Rechnung, die du hier selbst implementiert hast.
- **Rumelhart, Hinton, Williams (1986)** haben mit ihrer *Nature*-Publikation das Ende des ersten KI-Winters eingeleitet. Ohne diese Arbeit gäbe es keinen zweiten AI-Boom, und ohne den zweiten Boom keine heutige generative KI.

Kurz: Das MLP als „ganzes Modell" ist Geschichte. Der Trainingsalgorithmus und der Baustein „Feed-Forward-Schicht" sind so aktuell wie 1986 — nur eben milliardenfach vergrößert.

---

## 🧠 Abschließende Bemerkungen

Wenn du dir dieses Kapitel angesehen hast, hast du drei zentrale Ideen des maschinellen Lernens in Aktion gesehen:

1. **Nicht-Linearität durch Aktivierungsfunktionen.** Ohne Sigmoid (oder ReLU, tanh, …) wären beliebig viele Schichten immer noch nur ein linearer Klassifikator. Der Trick ist das *„krumm-Machen"* der Ausgabe.
2. **Backpropagation als Kettenregel-Trick.** Der Gradient läuft rückwärts durch das Netz und wird an jeder Verbindung mit der lokalen Ableitung multipliziert. Das ist mathematisch überraschend einfach, aber algorithmisch war es 1986 eine Sensation.
3. **Verteilte Repräsentationen.** Wissen wird nicht in einzelnen Neuronen gespeichert, sondern *über viele Gewichte verteilt*. Das macht das Netz robust — kein einzelner Ausfall zerstört sein Wissen.

Und eine subtile, aber wichtige Beobachtung: **Das MLP hat keinen Begriff von räumlicher Struktur.** Für uns ist ein „A" ein „A", egal ob es einen Pixel nach links oder rechts steht. Für das MLP sind das zwei komplett verschiedene Eingaben. Genau diese Blindheit gegenüber Verschiebungen wird das nächste Kapitel lösen.

---

## 🚀 Nächstes Kapitel: Convolutional Neural Networks (CNNs)

Im nächsten Meilenstein lösen wir genau die zwei Schwächen, die wir hier gefunden haben:

- **Lokalität:** CNNs betrachten das Bild in **kleinen lokalen Fenstern** (z. B. 3×3-Filtern) statt als flachen Vektor.
- **Translations­invarianz:** Der **gleiche Filter** wird an **jeder Position** des Bildes angewendet — dadurch findet das CNN Muster unabhängig davon, wo im Bild sie stehen.

Diese Idee stammt von **Yann LeCun (1998)**, der damit das berühmte **LeNet-5** baute und über Jahre hinweg handgeschriebene US-Postleitzahlen automatisch auslas.

Wir wechseln im CNN-Kapitel auch den **Datensatz**: Statt drei handgezeichneter 9×9-Bitmaps trainieren wir auf **MNIST** — dem historischen Datensatz mit 70 000 handgeschriebenen Ziffern, den LeCun selbst zusammengestellt hat. Dadurch wird der Vorteil des CNN gegenüber dem MLP direkt messbar sichtbar.

Außerdem führen wir dort **NumPy** ein, weil reines Python bei tausenden Bildern und Faltungen zu langsam würde — die Logik bleibt aber weiterhin von Hand geschrieben.

---

## 📚 Referenzen

- Werbos, P. J. (1974). *Beyond Regression: New Tools for Prediction and Analysis in the Behavioral Sciences*. PhD Thesis, Harvard University.
- Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). *Learning representations by back-propagating errors*. Nature, 323(6088), 533–536.
- McClelland, J. L., & Rumelhart, D. E. (1986). *Parallel Distributed Processing*. MIT Press.
- LeCun, Y., Boser, B., et al. (1989). *Backpropagation applied to handwritten zip code recognition*. Neural Computation, 1(4), 541–551.
- Bishop, C. M. (1995). *Neural Networks for Pattern Recognition*. Oxford University Press.
- Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning* (Kapitel 6). MIT Press.
