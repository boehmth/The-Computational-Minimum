# Cover-Prompts für Teil 1 („Computing")

Diese Datei sammelt die Bild-Prompts, mit denen die Kapitel-Cover von Teil
1 erzeugt werden können. Zielästhetik: **1980er europäische
Elektronik-Album-Cover-Ikonografie** — flach, geometrisch, keine
Gesichter, keine Gradienten, keine Fototextur. Wiederkehrende visuelle
Sprache über alle sechs Kapitel.

**Empfohlener Bild-Generator:** Copilot Designer (copilot.microsoft.com,
DALL·E 3). Alternativ: Ideogram, Recraft, Adobe Firefly.

**Wichtig zum Urheberrecht:** Kein Bild und kein Prompt darf einen
konkreten Album- oder Bandnamen enthalten. Wir beziehen uns
ausschliesslich auf *strukturelle* Merkmale (Reduktion, geometrische
Silhouetten, ...). Bereits im Prompt selbst wird das Wort "Kraftwerk"
ebenfalls nicht verwendet.

---

## 🎨 Serie-Signatur: die gemeinsame Farbfamilie

Um die sechs Cover als *Serie* erkennbar zu machen, benutzen wir bei
jedem Bild dieselbe Grundpalette von **vier Farben**, jeweils in
wechselnder Rolle:

| Rolle | Farbe (Hex) | Verwendung |
|---|---|---|
| Papier / Hintergrund | `#f2ede4` (cream, warm off-white) | immer der Hintergrund |
| Struktur / Hauptlinie | `#1a2a5c` (deep navy blue) | immer die tragende Linie |
| Signal / Akzent | `#f2c94c` (signal yellow) | Highlights, Wege, Marker |
| Alarm / Kontrast | `#d64545` (warning red-orange) | seltene, aber deutliche Kollisions- / Grenzwerte |

Jedes Cover benutzt genau diese vier Farben. Kein Farbgradient. Kein
Farbtemperatur-Effekt. Reine Flächen, klare Kanten. Damit sind die sechs
Cover *unverkennbar eine Serie*, auch wenn die Motive selbst
unterschiedlich sind.

---

## 📖 Kapitel 00 — Fundament (Turing vs. Zuse)

**Thematischer Kern:** Zwei parallele Traditionen — die mathematische
(Turing-Maschine) und die ingenieurhafte (Zuse Z3). Das Buch bekennt
sich zum zweiten Weg.

**Metapher fürs Cover:** Zwei geometrische Strukturen nebeneinander im
selben Bild — links ein *stilisiertes Papierband mit Symbolen* (Turing-
Maschine), rechts eine *stilisierte Relais-Schaltmatrix aus Rechtecken*
(Zuse Z3). Beide gleich groß, aber die rechte ist etwas heller
akzentuiert — das Buch folgt ihr.

**Prompt:**

```
A minimalist, geometric poster illustration for a chapter titled
"Foundation: Two Answers to a Crisis". Two symbolic diagrams sit
side-by-side on a warm cream background.

Left half: a long horizontal paper tape drawn as a thin rectangle with
small equally-spaced squares along its length — some squares contain
simple geometric symbols (a dot, a small cross, a bar), others are
empty. The tape is oriented horizontally, drawn as a schematic
representation of a Turing machine. Above and below the tape, tiny
schematic marks suggest a read/write head.

Right half: a grid of small identical rectangles arranged in a
rectangular matrix (roughly 6 rows x 4 columns), each rectangle
representing an electromechanical relay. Some relays are filled in
signal yellow, others are left as outlines. A few thin lines connect
the relays to suggest wiring. The right diagram feels denser and
slightly warmer than the left.

Style: 1980s European electronic-music album cover aesthetic. Extreme
reduction. Flat color fills, no gradients, no shading, no textures.
Palette: cream / warm off-white paper background (#f2ede4), deep navy
blue (#1a2a5c) for the tape and relay outlines, signal yellow
(#f2c94c) for the filled relays and tape symbol highlights, single
warning red-orange (#d64545) used sparingly on one or two accent
elements. Uniform thin line weight throughout.

Absolutely no text or logos anywhere in the image.

Format: 16:9 landscape. High contrast. Suitable as a chapter opener
for a computer science textbook.
```

---

## 📖 Kapitel 01 — CPU (die 4-Bit-CPU)

**Thematischer Kern:** Register laden, Bus, ALU, Mikrocode — der lineare
Fluss eines Programms durch eine Maschine.

**Metapher fürs Cover:** Ein *stilisierter Prozessor als Autobahn* —
Bus als eine breite gerade Straße, Register/ALU/PC als geometrische
Blöcke daran angeschlossen, Instruktionen als kleine Fahrzeuge, die
in einer Kolonne den Bus entlang wandern. Klare Kompositions-Achse
horizontal.

**Prompt:**

```
A minimalist, geometric poster illustration for a chapter titled
"CPU: A 4-Bit Von-Neumann Machine".

Composition: a single wide horizontal band across the middle of the
image represents a computer bus, drawn as a broad straight strip
(like a stylized highway or single-lane road) running left to right.

Attached to the top edge of the bus: four small identical rectangular
blocks labeled by simple geometric icons (a circle, a square, a
triangle, a horizontal bar) — these represent the registers, ALU,
program counter, and instruction register. Each block is connected to
the bus by a short straight vertical line.

On the bus itself: five identical small chevron arrows moving from
left to right, evenly spaced, all pointing forward — representing
instructions flowing through the CPU. All chevrons in the same signal
yellow color.

Below the bus, a thin baseline runs in parallel, suggesting the
control-signal line beneath the data path. It contains four small
notches marking clock ticks.

Style: 1980s European electronic-music album cover aesthetic. Flat
color, no gradients, no photorealism, no shading. Extremely reduced,
almost like a technical diagram or a printed circuit-board schematic.

Palette: cream / warm off-white paper background (#f2ede4), deep navy
blue (#1a2a5c) for the bus, blocks and lines, signal yellow (#f2c94c)
for the chevron instructions, single warning red-orange (#d64545) on
one small element (a status LED near the leftmost block).

Uniform thin line weight throughout. No text or logos anywhere.
Format: 16:9 landscape.
```

---

## 📖 Kapitel 02 — OS (das Mini-Betriebssystem)

**Thematischer Kern:** Zwei Prozesse teilen sich eine CPU, das OS
schaltet zwischen ihnen um. Context-Switch, YIELD, Segment.

**Metapher fürs Cover:** *Zwei separate, farblich unterschiedene
Programm-Zonen* (zwei verschiedene "Radiosender"), verbunden über
einen zentralen Umschalter. Beide Zonen im selben Bild, klar getrennt,
aber synchronisiert. Idee: Der OS ist der *Dirigent*, der zwischen
den beiden Signalen umschaltet.

**Prompt:**

```
A minimalist, geometric poster illustration for a chapter titled
"Operating System: Two Programs, One CPU".

Composition: the image is divided vertically into two halves by a
central pillar. The left half contains a stylized "program A": three
small rectangles stacked vertically with connecting lines, drawn in
signal yellow (#f2c94c). The right half contains a stylized "program
B": three small rectangles in a slightly different arrangement,
drawn in navy blue (#1a2a5c).

In the exact center, a small square symbol — the *scheduler* — sits
on the central pillar. From it, two thin arrows point outward:
one toward program A, one toward program B. Only one arrow is fully
solid; the other is dashed — representing "currently active vs.
paused".

Below the central symbol, a horizontal "clock ribbon" runs across the
full width: a thin line with regularly spaced tick marks, and above
each tick a tiny alternating marker A / B showing which program was
scheduled at that clock tick.

Style: 1980s European electronic-music album cover aesthetic. Flat
color, no gradients, no photorealism. Extreme reduction, technical-
diagram look.

Palette: cream / warm off-white paper background (#f2ede4), navy blue
(#1a2a5c) for structure and program B, signal yellow (#f2c94c) for
program A, warning red-orange (#d64545) sparingly on the scheduler
symbol.

Uniform thin line weight. No text or logos anywhere. Format: 16:9
landscape.
```

---

## 📖 Kapitel 03 — Compiler (vier Sprachen, ein Assembler)

**Thematischer Kern:** Verschiedene Sprachen führen zu derselben
Maschine — Sprache ist reine Ergonomie.

**Metapher fürs Cover:** *Trans-Europa-Express-Metapher*: vier
Bahnlinien aus vier Städten (COBOL, FORTRAN, C, LISP) laufen im
Zentrum zu einem einzigen Hauptbahnhof zusammen. Der Bahnhof ist die
CPU. Vier verschiedene Zug-Silhouetten mit unterschiedlichen "Farb-
Bändern" bringen ihre Passagiere alle zum selben Ziel.

**Prompt:**

```
A minimalist, geometric poster illustration for a chapter titled
"Compiler: Four Languages, One Assembler".

Composition: four thin straight lines (railway tracks) enter the
image from the four cardinal directions (top, right, bottom, left)
and converge in the exact center of the image at a single circular
node — the "central station" representing the CPU / assembler.

On each of the four tracks, a small geometric train silhouette moves
toward the center. Each train is a simple horizontal rectangle with
a distinctive small "flag" or "stripe" pattern on its side, indicating
its origin — for example: top train has a striped pattern, right train
has a checkered pattern, bottom train has a dotted pattern, left train
has a solid single-color body. Different patterns, same destination.

At the center node, small chevron marks indicate that everything
converges to a single stream of instructions leaving the station
downward.

Style: 1980s European electronic-music album cover aesthetic. Flat
color, no gradients, no photorealism. Technical, schematic, reduced.

Palette: cream / warm off-white paper background (#f2ede4), deep navy
blue (#1a2a5c) for the tracks, station and train outlines, signal
yellow (#f2c94c) for pattern accents on the trains, warning red-orange
(#d64545) sparingly on one train's flag and on the outgoing arrow
from the central station.

Uniform thin line weight. No text or logos anywhere. Format: 16:9
landscape.
```

---

## 📖 Kapitel 04 — PerceptronOnCPU (das erste Perceptron als 16-Instruktions-Programm)

**Thematischer Kern:** Ein einzelnes künstliches Neuron als
Assembler-Programm auf der 4-Bit-CPU. Es kann AND / OR / NAND lernen,
aber XOR nicht — das ist der KI-Winter live. Die zentrale Idee ist
*Mensch-Maschine* im wörtlichen Sinn: eine mathematische Idee wird zu
einer maschinellen Berechnung.

**Metapher fürs Cover:** Ein *stilisiertes Neuron* — ein zentraler
Kreis mit zwei Eingangs-Kanten (`x1`, `x2`), gewichtet, und einem
Schwellwert-Vergleich. Und darüber (oder darunter) eine *2×2-Wahrheits-
tabelle als Vier-Punkte-Diagramm*: drei davon können durch eine
Gerade getrennt werden (AND/OR/NAND), einer nicht (XOR — dargestellt
als kleines rotes Warnzeichen).

**Prompt:**

```
A minimalist, geometric poster illustration for a chapter titled
"Perceptron on a 4-Bit CPU: The First Neural Network".

Left half of the composition: a stylized artificial neuron drawn as
a single medium-sized circle. Two thin lines enter it from the left
(inputs x1 and x2), each labeled by a tiny geometric symbol (a small
square for x1, a small triangle for x2). The circle contains a
simple horizontal line with a small threshold marker — the activation.
One thin line exits the circle to the right (the output).

Right half: a 2x2 grid of four small dots representing the four
possible input combinations of a binary classification problem
(the corners of the XOR truth table). Three of the dots (top-left,
top-right, bottom-left) are drawn in signal yellow (#f2c94c). The
fourth dot (bottom-right) is drawn in warning red-orange (#d64545).
A single thin straight line attempts to separate the yellow dots from
the red one — but the line clearly fails: it cannot separate them
correctly. A small "X" or forbidden-symbol next to the red dot marks
the failure.

Style: 1980s European electronic-music album cover aesthetic. Flat
color, no gradients, no photorealism. Extremely reduced, schematic.

Palette: cream / warm off-white paper background (#f2ede4), navy blue
(#1a2a5c) for the neuron, the connecting lines, and the separation
attempt, signal yellow (#f2c94c) for the successful classifications,
warning red-orange (#d64545) for the impossible XOR case.

Uniform thin line weight. No text or logos anywhere. Format: 16:9
landscape.
```

---

## 📖 Kapitel 05 — GPU (Von Grafikbeschleuniger zum KI-Rechenwerk)

**Thematischer Kern:** SIMT — viele Threads, ein Programm, verschiedene
Daten. Die Grafikkarte, die für Videospiele gebaut wurde und
zufällig zum KI-Rechenwerk wurde.

**Metapher fürs Cover:** *Ein Grid identischer geometrischer Einheiten
(die "Threads")*, die alle in dieselbe Richtung "denken" (dasselbe
Symbol im Inneren), aber verschiedene Daten (jeder Zelle ihr eigener
kleiner Farbwert). Am Rand des Grids: eine einzelne, viel dickere
Instruktion (die "Warp-Instruktion"), die alle Zellen gleichzeitig
auslöst — ein grosser Pfeil, der ins Grid weist.

**Prompt:**

```
A minimalist, geometric poster illustration for a chapter titled
"GPU: From Graphics to AI".

Composition: a large rectangular grid (8 columns x 4 rows = 32 cells)
fills the central two-thirds of the image. Each cell contains a
tiny identical arrow icon pointing upward — all 32 arrows are visually
identical, indicating that every "thread" executes the same
instruction. The cells differ only in their *background fill*: each
cell has a slightly different intensity of signal yellow (from
almost-cream to full yellow), representing that each thread works on
a different data value.

To the left of the grid, outside its border: a single much larger
thick arrow, pointing right (into the grid), drawn in navy blue
(#1a2a5c). This represents the *one warp-wide instruction* that
drives all 32 threads at once.

Above the grid, a thin horizontal band with 8 tick marks corresponds
to the columns, suggesting time or clock ticks.

Style: 1980s European electronic-music album cover aesthetic. Flat
color, no gradients (except stepped fills within each cell), no
photorealism. Geometric, technical, reduced.

Palette: cream / warm off-white paper background (#f2ede4), navy blue
(#1a2a5c) for the grid outline, arrows inside cells, and the large
warp instruction arrow, signal yellow (#f2c94c) as the varied fill
for the data cells, warning red-orange (#d64545) on one single cell
somewhere in the grid — representing a "divergent thread" that took
a different branch.

Uniform thin line weight for structure. No text or logos anywhere.
Format: 16:9 landscape.
```

---

## 📎 Praktische Hinweise für die Bild-Erzeugung

1. **Copilot Designer liefert typischerweise 4 Varianten pro Prompt.**
   Wähle diejenige, die am klarsten die Kern-Metapher trifft, nicht
   die "schönste". Ein leicht ungelenkes Cover, das das ALOHA-Prinzip
   auf einen Blick zeigt, ist besser als ein perfektes, bei dem die
   Kollisionsstelle unklar ist.

2. **Konsistenz-Check vor Speichern:** Vergleiche das neue Cover mit
   den bereits gespeicherten. Sind die vier Grundfarben ähnlich?
   Ist die Linienstärke vergleichbar? Ist der Weissraum ähnlich
   dominant? Falls stark abweichend: neue Runde generieren, oder die
   Farbcodes im Prompt schärfer betonen.

3. **Format:** 16:9 landscape ist der Standard, weil das im README
   als Header-Bild an Bildschirmen wie Print gut wirkt. Falls du für
   den späteren Buchdruck Portrait-Format brauchst, sag im Prompt
   einfach "portrait 3:4" — die Metaphern lassen sich alle vertikal
   spiegeln.

4. **Namenskonvention beim Speichern:** Konsistent zu Kap. 06 →
   `01_Computing/0X_Kapitelname/assets/cover.png`. Beim README-Einbau
   folge dem Muster aus 06_Networks (Bild direkt unter dem Titel,
   ein-Satz-Untertitel mit der Metaphern-Auflösung).
