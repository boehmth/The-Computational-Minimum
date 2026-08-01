# The Computational Minimum

**Ein dreiteiliges Buch, das aus dem Nichts erklärt, wie moderne KI wirklich funktioniert — vom Transistor bis zum agentischen Sprachmodell, alles selbst gebaut, ohne Framework-Magie.**

---

## 📜 Worum es geht

Vor jedem Sprachmodell, das heute in den Nachrichten auftaucht, liegen 80
Jahre Informatik: eine 4-Bit-CPU, ein Batch-OS, ein Compiler, ein einzelnes
Neuron, eine Grafikkarte, die eigentlich für Videospiele gebaut wurde, und
ein Netzwerk, das dafür sorgt, dass 10 000 dieser Karten miteinander reden
können. Dieses Buch geht diese 80 Jahre in drei Teilen von Anfang bis Ende
durch — mit einem einzigen Anspruch:

> **Nichts ist Magie. Alles ist gebaut. Und man kann jeden Baustein selbst
> nachbauen, klein genug, um ihn auf einem Laptop laufen zu lassen.**

Für **Abiturienten, Studienanfänger, Lehrkräfte** und alle, die verstehen
wollen, was hinter ChatGPT, DeepSeek und Co. wirklich passiert — nicht auf
der Buzzword-Ebene, sondern auf der Ebene, auf der man selbst programmieren
kann.

---

## 🎯 Die These: Skalierung, gefunden durch Experiment

Dem Buch liegt eine These zugrunde, die sich durch alle drei Teile zieht:

> **Skalierung ist die durchgehende Herausforderung der Informatik.
> Experiment — nicht Theorie — ist die Methode, mit der jede ihrer Grenzen
> überwunden wurde.**

- Eine 4-Bit-CPU ist bereits Turing-vollständig. Jede größere CPU danach ist
  *Skalierung* derselben Idee.
- Ein einzelnes Neuron zeigt das Lernprinzip vollständig. Jede tiefere
  Architektur bis zum Transformer ist im Kern *Skalierung* dieser einen
  Idee — mit neuen Strukturen genau *dort*, wo die vorherige Skalierung an
  eine Wand lief.
- Ein LLM lernt "denken" nicht, weil jemand die Theorie dazu geschrieben
  hätte, sondern weil DeepSeek 2025 empirisch beobachtete, dass ein
  bestimmter Trainings­anreiz dieses Verhalten hervorbringt.

Jede dieser Skalierungsgrenzen wurde nicht am Reißbrett bewiesen, sondern
durch Ausprobieren gefunden. Kapitel `01_Computing/00_Fundament` benennt
dieses Prinzip zu Beginn ausdrücklich, indem es die *ingenieur­getriebene*
Tradition (Zuse, Z3 1941) und die *theoretisch-mathematische* Tradition
(Turing, Church 1936) nebeneinanderstellt — und offenlegt, dass dieses
Buch bewusst der ersten folgt.

---

## 📚 Die drei Teile

### [`01_Computing/`](01_Computing/) — Wie ein Computer wirklich funktioniert

Sechs Meilensteine, die klassische *„Was steckt drin?"*-Frage, alle in
reinem Python selbst gebaut:

| Nr. | Kapitel | Was gebaut wird |
|-----|---------|-----------------|
| 0 | `00_Fundament` | Standortbestimmung: Turing vs. Zuse, warum dieses Buch dem Zuse-Weg folgt — mit einem winzigen Turing-Maschinen-Simulator |
| 1 | `01_CPU` | Eine simulierte 4-Bit-CPU mit Bus, ALU, Mikrocode-ROM — Live-Ansicht im Terminal |
| 2 | `02_OS` | Zwei Mini-Betriebssysteme: kooperatives Multitasking (YIELD) und ein Batch-OS, das selbst nur 10 Assembler-Instruktionen ist |
| 3 | `03_Compiler` | Vier Sprachen (COBOL, FORTRAN, C, LISP) → *ein* AST → *ein* Assembler → derselbe 4-Bit-CPU-Code |
| 4 | `04_PerceptronOnCPU` | Rosenblatts Perceptron als 16-Instruktionen-Programm auf der 4-Bit-CPU — löst AND/OR/NAND, scheitert an XOR (KI-Winter live) |
| 5 | `05_GPU` | Vom Grafikbeschleuniger zum KI-Rechenwerk: Shader → BrookGPU → CUDA → AlexNet, mit einem SIMT-Simulator in Python |
| 6 | `06_Network` *(geplant)* | Zwei Rechner reden miteinander: Frames, Header, Checksum, Retransmission — „ein API-Call an ChatGPT ist 1970er-Technik" |

**Roter Faden:** Jedes Kapitel behebt eine Grenze des vorherigen —
Assembler ist schmerzhaft → Compiler; ein Rechner ist eine Insel →
Netzwerk; ein Perceptron auf CPU skaliert nicht auf ein MLP → GPU; eine
GPU reicht nicht für GPT-3 → Netzwerk. Fünf der sechs Bausteine wurden
zwischen 1945 und 1974 erfunden — der einzige *wirklich* neue in 80 Jahren
ist die GPU als KI-Hardware, und selbst sie ist im Kern kein Bruch mit
Von Neumann, sondern eine besondere Skalierungsrichtung.

### [`02_MachineIntelligence/`](02_MachineIntelligence/) — 60 Jahre neuronale Netze

Acht Meilensteine vom ersten Neuron zum eigenen kleinen GPT — jeder in
reinem NumPy (oder Python), jeder als Antwort auf ein konkretes Scheitern
des Vorgängers:

| Nr. | Kapitel | Was gebaut wird |
|-----|---------|-----------------|
| 1 | `01_Perceptron` | Rosenblatt 1958 — ein Neuron lernt eine Gerade |
| 2 | `02_MLP` | Rumelhart 1986 — Hidden Layer, Backpropagation von Hand |
| 3 | `03_CNN` | LeCun 1998 — Faltung, Weight Sharing, MNIST lesen |
| 4 | `04_Word2Vec` | Mikolov 2013 — `könig − mann + frau ≈ königin` |
| 5 | `05_RNN` | Elman 1990 / Mikolov 2010 — Sequenzen und Gedächtnis |
| 6 | `06_Seq2Seq` | Bahdanau 2015 — Encoder/Decoder mit Attention |
| 7 | `07_Transformer` | Vaswani 2017 — Self-Attention, parallel |
| 8 | `08_MiniGPT` | Radford 2018 — ein autoregressives Sprachmodell, das ein eigenes kleines Grimm-Märchen schreibt |

**Ab Meilenstein 4** begleiten uns die **Grimmschen Märchen** als roter
Faden — Wow-Moment bei Word2Vec, dann Textgenerierung bei RNN und GPT.

**Bemerkenswerte Symmetrie:** Vom Perceptron (1958) bis zu GPT-1 (2018)
liegen genau 60 Jahre — dieselbe Zeitspanne wie vom Elektron (1897) zum
Transistor (1947). In beiden Fällen folgte auf die lange Grundlagenphase
eine kurze, explosive Anwendungsphase. Diese ist Gegenstand von Teil 3.

### [`03_AgenticSystems/`](03_AgenticSystems/) — Anwenden und Skalieren

Der zehn-Jahres-Sprint 2018 → heute. Hier folgen die Kapitel nicht mehr
einer Chronologie einzelner Modell-Erfindungen, sondern einer *Kette
neuer Skalierungsachsen und Trainings-Sprünge*, die in den 2020er Jahren
entdeckt wurden:

| Nr. | Kapitel | Kernidee |
|-----|---------|----------|
| 1 | `01_TinyGPT` | Reines Sprachmodell (GPT-1/GPT-3-Linie) — Scaling Laws (Kaplan 2020, Chinchilla 2022): mehr Parameter, mehr Daten, mehr Compute |
| 2 | `02_TinyInstruct` | Instruktions-Feinjustierung durch maskierten Loss (FLAN, T0, Alpaca, LIMA) — der Moment, in dem aus dem Text-Vervollständiger ein Instruction-Follower wird |
| 3 | `03_TinyChat` | Präferenz-Ausrichtung (RLHF → DPO) — aus dem Instruction-Follower wird ein konsistenter Chat-Assistent |
| 4 | `04_TinyMoE` | Mixture of Experts — zweite Skalierungsachse: Kapazität wächst, Kosten pro Token bleiben |
| 5 | `05_TinyReason` | Trainiertes Reasoning à la DeepSeek-R1 — dritte Achse: mehr Compute *zur Antwortzeit* statt beim Training |

**Vorwort und Klammer:** `03_AgenticSystems/PREFACE.md` zeichnet nach, wie
sich Skalierung in diesem Teil von einem Merkmal einzelner Kapitel zur
*Betriebsweise des gesamten Feldes* wandelt — mit DeepSeek-R1-Zero als
radikalstem Beleg dafür, dass sogar Reasoning experimentell *entdeckt*,
nicht theoretisch *konstruiert* wurde.

### [`04_AgenticSystemsEvo/`](04_AgenticSystemsEvo/) — Agentische Systeme als Laufzeit-Systeme

Ein neuer, praxisnäherer Anschluss an Teil 3: nicht mehr primär die Frage,
wie LLMs **trainiert und skaliert** werden, sondern wie sie **zur Laufzeit**
mit Tools, Loops, Protokollen und dynamisch erzeugtem Code zu handlungsfähigen
Systemen werden.

| Fokus | Beispiele |
|------|-----------|
| Vom Prompt zur Aktion | Text-in/Text-out, Tool-Calling, Planning |
| Vom Einzelaufruf zum Agenten | externer Loop, Retry-Strategien, Reasoning-Modelle |
| Vom Einzelsystem zum Ökosystem | MCP, A2A, Dynamic Tool Agent |

**Einordnung:** `03_AgenticSystems/` erklärt den aktuellen LLM-Sprung eher aus
der Perspektive von **Training, Alignment und Skalierungsachsen**.
`04_AgenticSystemsEvo/` verschiebt den Blick auf die **Systemebene**:
Was muss außerhalb des Modells gebaut werden, damit aus einem LLM ein Agent
oder ein agentisches Softwaresystem wird?

Beide Teile sind daher keine Duplikate, sondern zwei komplementäre Blicke auf
dieselbe Gegenwart: **Teil 3 = das Modell selbst. Teil 4 = das System um das
Modell herum.**

---

## 🕰️ Der historische Bogen in einer Zeile

```
1936 ─── 1945 ─── 1958 ─── 1971 ─── 1986 ─── 2001 ─── 2012 ─── 2017 ─── 2020 ─── 2025
Turing   EDVAC    Perc.    4004     Backpr.  Shader   AlexNet  Transf.  GPT-3    R1
 └─────────────── Teil 1 ─────────────────┘ └────── Teil 2 ──────┘ └── Teil 3 ──┘
```

Fast alle in Teil 1 gezeigten Bausteine (CPU, OS, Compiler, Netzwerk)
entstanden in den drei Jahrzehnten von 1945 bis 1974. Die einzige *neue*
Rechen-Klasse in den 80 Jahren danach ist die GPU als KI-Hardware. Und
selbst diese Ausnahme bestätigt die These: sie war nicht *für* KI gebaut,
sondern wurde von der KI *gefunden*.

---

## 🚀 Schnelleinstieg

```bash
git clone <dieses-Repo>
cd The-Computational-Minimum

# Teil 1: 4-Bit-CPU-Simulator (Live-UI im Terminal)
python 01_Computing/01_CPU/src/main.py

# Teil 2: Ein Neuron lernt aus 2D-Punkten
cd 02_MachineIntelligence/01_Perceptron/src
python perceptron.py

# Teil 2: Der Höhepunkt — ein Mini-GPT schreibt sein eigenes Grimm-Märchen
cd ../../08_MiniGPT/src
python train.py  # (sobald Kap. 8 fertig ist)
```

Alle Programme laufen mit **Python 3.7+**. Ab Teil 2, Meilenstein 3 wird
**NumPy** gebraucht (plus `scikit-learn` für den MNIST-Loader). Für Teil 3
werden kleine Open-Source-Modelle wie Llama, Mistral oder Phi lokal
geladen — was nötig ist, wird im jeweiligen Kapitel dokumentiert.

---

## 📖 Das Buch als Online-Fassung

Alle Kapitel-READMEs und Deep Dives sind zusätzlich als **navigierbare
Website** verfügbar, gebaut mit **MkDocs Material**. Die Site wird bei
jedem Push auf `main` automatisch über GitHub Actions gebaut und auf
GitHub Pages deployt (siehe [`.github/workflows/deploy-docs.yml`](.github/workflows/deploy-docs.yml)).

**Aktuelle URL:** *sobald der erste Deploy durchgelaufen ist, unter
`https://<GitHub-User>.github.io/The-Computational-Minimum/`.*

### Lokal ansehen und weiterentwickeln

```bash
pip install -r requirements-docs.txt
python tools/sync_docs.py          # spiegelt READMEs -> docs/
python -m mkdocs serve             # http://127.0.0.1:8000
```

Der Sync-Schritt erzeugt einen `docs/`-Ordner mit einer Kopie aller
Buch-Dateien (die Original-Dateien in `01_Computing/` etc. bleiben
unangetastet). Danach kann MkDocs die Site live rendern und
aktualisieren, während du editierst.

`docs/` und `_site/` sind Build-Artefakte und in `.gitignore`
ausgeschlossen — du committest weiter die *Original*-Markdown-Dateien
im Repo.

### Nur Teil 1 zunächst online

Um den Prototypen sauber zu halten, sind zunächst nur Teil 1 (Computing)
und die Grundlagen-Deep-Dives in der Online-Fassung enthalten. Teile 2
und 3 sind im Repo weiterhin lesbar (GitHub-Ordner-View), werden aber
erst in die Site aufgenommen, wenn ihre narrative Fassung reif ist.
Die Aktivierung erfolgt später schlicht durch Kommentaren in
`tools/sync_docs.py` und Nachziehen der Navigation in `mkdocs.yml`.

---

## 🛠️ Grundregeln der Reihe

Diese drei Regeln gelten für Teil 1 und 2 strikt, für Teil 3 mit einer
klaren Ausnahme:

1. **Alles selbst gebaut.** Kein PyTorch, kein TensorFlow, keine
   fertigen Layer. Jede Multiplikation, jeder Bus-Zyklus, jeder Gradient
   ist im Code sichtbar. Ab Meilenstein 3 in Teil 2 ist **NumPy** erlaubt,
   weil reines Python bei größeren Datensätzen zu langsam wird — die
   Logik bleibt trotzdem von Hand geschrieben.
2. **Klein genug für einen Laptop.** Keine Cloud-GPU nötig. Wo das nicht
   mehr geht (Teil 3), machen wir die Ideen an *kleinen* Open-Source-
   Modellen sichtbar, statt eigene Millionen-Euro-Trainings zu simulieren.
3. **Jeder Schritt hat eine ehrliche Grenze.** Am Ende jedes Kapitels
   steht, was das gebaute Modell *nicht* kann — und genau das ist die
   Motivation für das nächste Kapitel.

---

## 🎯 Zielgruppe

- **Schüler der Oberstufe** mit Mathematik auf Oberstufen­niveau und
  grundlegenden Python-Kenntnissen.
- **Studienanfänger** in Informatik, Elektrotechnik, Data Science.
- **Lehrkräfte**, die einen roten Faden für einen Wahlpflichtkurs, eine
  AG oder ein Seminar suchen.
- **Alle Neugierigen**, die verstehen möchten, wie ein Sprachmodell
  wirklich tickt — statt sich mit Buzzwords zufrieden zu geben.

Vorwissen, das *nicht* nötig ist: fortgeschrittene Mathematik,
Elektrotechnik, Frameworks, Cloud-Konten. Alles Wichtige wird an dem
Punkt erklärt, an dem es das erste Mal auftaucht.

---

## 🧭 Wie man das Buch liest

Zwei sinnvolle Wege:

**Weg A — von vorne nach hinten.** Der volle Bogen: erst verstehen, wie
ein Computer funktioniert, dann wie neuronale Netze funktionieren, dann
wie moderne KI-Systeme gebaut werden. Am belastbarsten, wenn man das
Fundament wirklich verinnerlichen will.

**Weg B — vom Interesse her.** Wer schon programmieren kann und in erster
Linie KI verstehen will, kann direkt mit Teil 2 anfangen und Teil 1 als
Nachschlagewerk verwenden. Der `00_Fundament`-Text und die Perceptron-auf-
CPU-Passage (Kap. 4 in Teil 1) lohnen sich aber auch dann — sie erklären,
*warum* die Reihe aussieht, wie sie aussieht.

Innerhalb jedes Teils sollte man streng der Reihenfolge folgen: jedes
Kapitel setzt das vorherige voraus, und die Übungen am Kapitelende sind
der wichtigste Lernteil.

---

## 📚 Status

- ✅ **Teil 1**: Kapitel 0–4 fertig; Kap. 5 (GPU) mit README fertig, Code
  in Arbeit; Kap. 6 (Netzwerk) geplant.
- ✅ **Teil 2**: Kapitel 1–6 fertig; Kap. 7 (Transformer) Phase 1 fertig
  (Forward + Multi-Head-Heatmaps), Phase 2 (Backward + Training) in
  Arbeit; Kap. 8 (Mini-GPT) geplant.
- 🚧 **Teil 3**: Vorwort und Kapitelgrundstruktur stehen; Implementierung
  in Vorbereitung.

Die jeweiligen `ROADMAP.md`-Dateien in den drei Teilen halten den
detaillierten Stand fest.

---

## 📜 Lizenz und Beiträge

Frei für den Bildungs­gebrauch. Beiträge, Übersetzungen und Ergänzungen
sind willkommen — bitte den Stil und die Grundregeln der Reihe
beibehalten (kein Framework-Zauber, jede Komponente selbst nachbaubar,
ehrliche Grenzen).
