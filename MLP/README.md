# KI‑Meilenstein 2: Das Multi‑Layer‑Perzeptron (MLP)

> **🎯 Warum ist das cool?**
> Wir stapeln nur eine **zweite Schicht Neuronen** auf das Perceptron drauf — und plötzlich kann das Netz nicht nur Geraden ziehen, sondern **beliebig geschwungene Formen** erkennen: Kreise, Buchstaben, komplizierte Muster. Dieser eine Baustein — mit dem Trainings­algorithmus **Backpropagation** — ist der Grund­stein von *Deep Learning* und läuft heute in jeder KI, von der Handschrift­erkennung deiner Bank bis zu ChatGPT.

## 📖 Einleitung

Das Perceptron aus dem vorherigen Meilenstein zeigt bereits die Grundidee des maschinellen Lernens: **Lernen aus Daten**. Aber es hat eine harte Grenze — es kann nur Muster erkennen, die sich durch eine **Gerade** trennen lassen. Bei der Kreis-Aufgabe scheitert es zwangsläufig, weil kein einzelnes Neuron eine gebogene Grenze zeichnen kann.

Damit ein Netz komplexere Muster erkennen kann, braucht es zwei Zutaten:

1. **Mehrere Schichten** von Neuronen (statt nur einer),
2. eine **nicht-lineare Aktivierungsfunktion** dazwischen.

Genau das leistet das **Multi‑Layer‑Perzeptron (MLP)** — der erste Schritt in Richtung dessen, was wir heute *Deep Learning* nennen.

In diesem Meilenstein werden wir:

- ein MLP **von Grund auf** in reinem Python bauen,
- **Vorwärts­berechnung**, **Backpropagation** und **Gradienten­abstieg** selbst umsetzen,
- es auf einfachen **9×9-Bitmap-Buchstaben** (A, L, R) trainieren,
- die Robustheit anhand von **Rauschen** und **Verschiebungen** testen,
- verstehen, **warum MLPs funktionieren — und wo sie an Grenzen stoßen**.

---

## 🕰️ Historischer Kontext: Der Backpropagation‑Durchbruch (1986)

Die Idee mehrschichtiger neuronaler Netze existierte bereits in den 1960er-Jahren. Doch jahrzehntelang blieben sie praktisch unbrauchbar. Der Grund war einfach:

> Niemand wusste, wie man die **verborgenen Schichten** trainieren sollte.

Das änderte sich 1986, als **David E. Rumelhart**, **Geoffrey E. Hinton** und **Ronald J. Williams** ihren wegweisenden Artikel veröffentlichten:

**„Learning representations by back‑propagating errors" (Nature, 1986)**

Diese Arbeit führte **Backpropagation** ein — den Algorithmus, der Deep Learning erst ermöglichte.

Backpropagation erlaubt:

- Training von Netzen mit **mehreren Schichten**,
- Lernen **interner Repräsentationen**,
- Lösen **nicht-linearer** Klassifikations­probleme,
- die Geburt der modernen neuronalen Netze.

Ohne Übertreibung: **Backpropagation ist das Fundament der gesamten modernen KI — CNNs, RNNs, Transformer und LLMs beruhen alle darauf.**

---

## 🧠 Was das MLP gegenüber dem Perceptron neu einführt

Ein MLP erweitert das Perceptron um zwei entscheidende Konzepte:

- **Verborgene Schichten (Hidden Layers)**: eine oder mehrere Zwischen­schichten zwischen Eingabe und Ausgabe. Sie lernen, aus den Rohdaten sinnvolle **Zwischen­merkmale** zu extrahieren.
- **Nicht-lineare Aktivierungen** (bei uns: Sigmoid). Ohne sie wäre ein Netz mit vielen Schichten immer noch nur ein linearer Klassifikator — die Nicht-Linearität macht das Netz **ausdrucksstärker**.

Damit kann das MLP:

- **gebogene Entscheidungs­grenzen** ziehen,
- **hierarchische Merkmale** aufbauen (kleine Bausteine → größere Muster),
- **komplexe Zusammenhänge** in den Daten erfassen.

In unserem konkreten Fall: Das MLP kann die Buchstaben **A**, **L** und **R** aus 9×9-Pixel-Rastern erkennen — was ein einlagiges Perceptron nicht schaffen würde.

---

## 🖼️ Datensatz: 9×9‑Bitmap‑Buchstaben

Wir stellen jeden Buchstaben als 9×9-Raster aus 0/1-Werten dar:

- 81 Eingabe­merkmale (ein Pixel = ein Neuron in der Eingabe­schicht),
- einfach genug zum Nachvollziehen,
- komplex genug, um nicht-lineares Lernen zu erfordern.

Beispiel (Buchstabe A):

```
.........
...###...
..#####..
.##...##.
.##...##.
.#######.
.#######.
.##...##.
.........
```

---

## 🧩 Modellarchitektur

Unser MLP besteht aus drei Schichten:

- **Eingabe­schicht:** 81 Neuronen (ein Neuron pro Pixel)
- **Verborgene Schicht:** z. B. 20 Neuronen
- **Ausgabe­schicht:** 3 Neuronen (A, L, R)

Aktivierungs­funktionen:

- **Verborgene Schicht:** Sigmoid
- **Ausgabe­schicht:** Sigmoid (als Vertrauens­werte pro Klasse)

Diagramm:

```
81 Pixel  ->  [ Dense: 81 -> 20, Sigmoid ]  ->  [ Dense: 20 -> 3, Sigmoid ]  ->  A / L / R
```

---

## 🔧 Training: Backpropagation + Gradienten­abstieg

Das Training verwendet drei bekannte Zutaten:

- **Mittlerer quadratischer Fehler (MSE)** als Verlust­funktion,
- **Gradienten­abstieg** als Optimierer,
- **Backpropagation**, um die Gradienten Schicht für Schicht rückwärts zu bestimmen.

Alles wird **händisch** implementiert — kein Framework, keine `torch.nn`-Bausteine. Jede einzelne Multiplikation ist im Code sichtbar.

---

## ▶️ So startest du das Programm

Der Python-Code liegt in `MLP/src/`.

```bash
cd MLP/src
python mlp.py
```

Das Programm:
1. lädt die 9×9-Bitmaps für A, L, R,
2. trainiert das MLP über mehrere tausend Epochen,
3. testet es mit **verrauschten** Bildern und gibt die Vorhersagen aus.

---

## 🧪 Robustheits­test 1: Rauschen

Wir kippen zufällig einige Pixel im Eingabebild um:

- kleines Rauschen → das Modell bleibt richtig,
- mittleres Rauschen → das Vertrauen sinkt,
- starkes Rauschen → das Modell kann sich irren.

Was das offenbart:

- Manche Pixel sind **sehr wichtig** (hohe Gewichte),
- andere sind fast **egal** (Gewichte nahe null),
- Rauschen schiebt die Eingabe **über die Entscheidungsgrenze**.

---

## 🧪 Robustheits­test 2: Verschiebung

Wenn wir das Bitmap-Bild um **einen einzigen Pixel** verschieben:

- versagt das MLP fast vollständig,
- viele Bilder werden gleich klassifiziert (meist als „A"),
- das Vertrauen wird niedrig und schwankt.

Das offenbart eine grundlegende Schwäche:

> **MLPs verstehen keine räumliche Struktur.**
> Für sie ist ein Bild einfach ein flacher Vektor aus 81 Zahlen. Es gibt keinen Begriff von „das Pixel daneben" oder „dieselbe Form, nur woanders".

Genau das motiviert das nächste Kapitel: **das Convolutional Neural Network (CNN)**, das Bildstruktur explizit ausnutzt — und dabei einen deutlich größeren Datensatz (MNIST) verwendet.

---

## 🧠 Zentrale Erkenntnisse (Merksätze)

### **1. Nicht‑Linearität**
Verborgene Schichten erlauben dem MLP, gebogene und komplexe Entscheidungs­grenzen zu lernen.

### **2. Verteilte Repräsentationen**
Wissen wird über viele Gewichte verteilt gespeichert — nicht in einzelnen Neuronen.

### **3. Bedeutung der Merkmale**
Manche Eingaben sind viel wichtiger als andere; Rauschen macht diese Unterschiede sichtbar.

### **4. Begrenzte Robustheit**
MLPs verkraften kleines Rauschen, scheitern aber an strukturellen Änderungen.

### **5. Globale Verarbeitung**
Das MLP betrachtet das gesamte Bild auf einmal — es hat keinen Begriff von Lokalität.

### **6. Keine Translations­invarianz**
Eine Verschiebung um nur einen Pixel zerstört das gelernte Muster — eine gravierende Schwäche.

---

## 📦 Dateien in diesem Kapitel

- `mlp.py` — Implementierung des MLP,
- `datasets.py` — 9×9-Bitmaps der Buchstaben,
- `utils.py` — Rauschen, Aktivierungen, Hilfsfunktionen.

---

## 🚀 Nächstes Kapitel: Convolutional Neural Networks (CNNs)

Im nächsten Meilenstein lösen wir genau die zwei Schwächen, die wir hier gefunden haben:

- **Lokalität:** CNNs betrachten das Bild in **kleinen lokalen Fenstern** (z. B. 3×3-Filtern) statt als flachen Vektor.
- **Translations­invarianz:** Der **gleiche Filter** wird an **jeder Position** des Bildes angewendet — dadurch findet das CNN Muster unabhängig davon, wo im Bild sie stehen.

Diese Idee stammt von **Yann LeCun (1998)**, der damit das berühmte **LeNet‑5** baute und über Jahre hinweg handgeschriebene US-Postleitzahlen automatisch auslas.

Wir wechseln im CNN-Kapitel auch den **Datensatz**: Statt drei handgezeichneter 9×9-Bitmaps trainieren wir auf **MNIST** — dem historischen Datensatz mit 70 000 handgeschriebenen Ziffern, den LeCun selbst zusammengestellt hat. Dadurch wird der Vorteil des CNN gegenüber dem MLP direkt messbar sichtbar.

Außerdem führen wir dort **NumPy** ein, weil reines Python bei tausenden Bildern und Faltungen zu langsam würde — die Logik bleibt aber weiterhin von Hand geschrieben.

---

## 📚 Wichtige Referenzen

**Primärquelle**
- Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). *Learning representations by back‑propagating errors*. Nature, 323(6088), 533–536.

**Weitere Grundlagenliteratur**
- Werbos, P. J. (1974). Frühe Formulierung der Backpropagation-Idee (Dissertation).
- McClelland, J. L., & Rumelhart, D. E. (1986). *Parallel Distributed Processing*. MIT Press.
- Bishop, C. M. (1995). *Neural Networks for Pattern Recognition*. Oxford University Press.
- Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning* (Kapitel 6). MIT Press.
