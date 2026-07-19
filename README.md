# The Computational Minimum

**Milestones in Computing, Machine Intelligence, and Agentic Systems.**

Ein Lehrpfad in drei Teilen, der vom kleinsten selbst gebauten Prozessor bis zu autonomen KI-Systemen führt. Alles selbst programmiert, ohne Frameworks. Jede Multiplikation, jedes Bit, jede Instruktion ist im Code sichtbar.

---

## 📜 Der Bogen der Reihe

Zwischen dem ersten mechanischen Rechenwerk und einem modernen agentischen KI-System liegen zwei parallele Erzählstränge:

1. **Wie funktioniert ein Computer überhaupt?** — Hardware, Software, Betriebssystem, Compiler, Netzwerk. Das *zeitlose* Fundament der Informatik.
2. **Wie kommt aus dem Computer eine lernende — und heute handelnde — Maschine?** — 60 Jahre neuronale Netze vom Perceptron (1958) über den Transformer (2017) bis zu GPT und darüber hinaus.

Dieses Repository erzählt beide Geschichten und ihre Fortsetzung in drei aufeinander aufbauenden Teilen:

| Teil | Zeitraum | Titel | Fokus |
|------|----------|-------|-------|
| **[01_Computing](01_Computing/)** | *zeitlos* | **Milestones in Computing** | 4-Bit-CPU, Betriebssystem, Compiler, Netzwerk |
| **[02_MachineIntelligence](02_MachineIntelligence/)** | **1958 → 2018** *(60 Jahre)* | **Milestones in Machine Intelligence** | Perceptron → Transformer → Mini-GPT |
| **[03_AgenticSystems](03_AgenticSystems/)** | **2018 → heute** *(10 Jahre)* | **Milestones in Agentic Systems** | LLMs, Reasoning, Werkzeug-Nutzung, autonome Agenten *(in Vorbereitung)* |

Der rote Faden durch alle drei Teile: **kleinstes selbst gebautes Modell zeigt das Prinzip, historische Erzählung erklärt, warum es so aussieht, und der Ausblick zeigt, wohin es führt.**

---

## 🧭 Übersicht

### 🔧 [01_Computing](01_Computing/) — Milestones in Computing

Die vier klassischen Grundlagenthemen der Informatik, jeweils als selbst gebautes Miniaturmodell:

| Nr. | Kapitel | Kern |
|-----|---------|------|
| **1** | [`01_CPU/`](01_Computing/01_CPU/) | 4-Bit-CPU mit Bus, ALU, Mikrocode-ROM, Kontroll­einheit |
| **2** | [`02_OS/`](01_Computing/02_OS/) | Zwei OS-Modelle: kooperatives Multitasking (Python) + Batch-OS (in Assembler geschrieben) |
| **3** | [`03_Compiler/`](01_Computing/03_Compiler/) | Vier Frontends (COBOL, FORTRAN, C, LISP) → gemeinsamer AST → derselbe Assembler |
| **4** | [`04_PerceptronOnCPU/`](01_Computing/04_PerceptronOnCPU/) | Rosenblatt-Perceptron als 16-Instruktions-Assembler — klassifiziert AND/OR/NAND, scheitert an XOR *(Brücke zu Teil 2)* |
| **5** | `05_Network/` | *(geplant)* Zwei simulierte CPUs, HTTP-GET zum LLM-Service |

Was dieser Teil klärt: *„Wie kommt aus Transistoren eine Maschine, die Programme ausführt?"*

### 🧠 [02_MachineIntelligence](02_MachineIntelligence/) — Milestones in Machine Intelligence

Von einem einzelnen Neuron (1958) bis zum eigenen GPT-artigen Modell — acht Meilensteine, die den Weg der KI-Forschung nachzeichnen:

| Nr. | Kapitel | Kern |
|-----|---------|------|
| **1** | [`01_Perceptron/`](02_MachineIntelligence/01_Perceptron/) | Rosenblatt 1958 — Ein Neuron lernt eine Gerade |
| **2** | [`02_MLP/`](02_MachineIntelligence/02_MLP/) | Rumelhart 1986 — Backprop und nicht-lineare Grenzen |
| **3** | [`03_CNN/`](02_MachineIntelligence/03_CNN/) | LeCun 1998 — Faltung, Pooling, MNIST-Zeichen |
| **4** | [`04_Word2Vec/`](02_MachineIntelligence/04_Word2Vec/) | Mikolov 2013 — Wörter als Vektoren |
| **5** | [`05_RNN/`](02_MachineIntelligence/05_RNN/) | Elman 1990 / LSTM 1997 — Sequenzen und Gedächtnis |
| **6** | [`06_Seq2Seq/`](02_MachineIntelligence/06_Seq2Seq/) | Bahdanau 2015 — Attention |
| **7** | [`07_Transformer/`](02_MachineIntelligence/07_Transformer/) | Vaswani 2017 — Self-Attention, parallel |
| **8** | *(geplant)* `08_MiniGPT/` | Radford 2018 — Autoregressives Sprachmodell |

Was dieser Teil klärt: *„Wie kommt aus dem Computer eine lernende Maschine?"*

Der Begriff **„Machine Intelligence"** stammt von Alan Turing (1950, *„Computing Machinery and Intelligence"*) und ist über die Jahrzehnte immer wieder verwendet worden, wenn man den Marketing-Ton von „AI" vermeiden wollte. Für uns passt er, weil dieser Teil genau das behandelt: die *Maschinen*, die intelligentes Verhalten zeigen — nicht Marketing, nicht Ideologie, sondern das technische Fundament.

### 🤖 [03_AgenticSystems](03_AgenticSystems/) — Milestones in Agentic Systems *(in Vorbereitung)*

Was in den letzten zehn Jahren aus den Grundlagen von *Machine Intelligence* gebaut wurde: LLMs im Detail, Mixture-of-Experts, Reasoning-Modelle (DeepSeek-R1, o1), Retrieval-augmented Generation, Werkzeug-Nutzung, multimodale Systeme, autonome Agenten. Setzt *Machine Intelligence* voraus.

Der Titel **„Agentic Systems"** — statt „Agenten" oder „Anwendungen" — ist bewusst breiter gewählt: er umfasst alle Systeme, in denen ein Modell nicht nur eine Antwort produziert, sondern **plant, Werkzeuge benutzt, iteriert, und die Welt verändert**. Vom Function-Calling im LLM bis zum autonomen Multi-Agent-System.

---

## 🚀 Schnelleinstieg

```bash
git clone <dieses-Repo>
cd The-Computational-Minimum-main

# --- 01_Computing ---
# CPU-Simulator (Live-Terminal-UI):
python 01_Computing/01_CPU/src/main.py

# Batch-OS mit Assembler-Kernel:
python 01_Computing/02_OS/src/os_batch.py

# Compiler (vier Sprachen, dasselbe Ergebnis):
python 01_Computing/03_Compiler/test_compiler.py

# --- 02_MachineIntelligence ---
# Meilenstein 1: Perceptron (reines Python)
python 02_MachineIntelligence/01_Perceptron/src/perceptron.py

# Meilenstein 3: CNN auf MNIST (NumPy + scikit-learn)
python 02_MachineIntelligence/03_CNN/src/main.py

# Meilenstein 5: Char-RNN auf Grimm-Märchen
python 02_MachineIntelligence/05_RNN/src/main.py
```

Voraussetzungen:
- **Python 3.7+**
- Für **01_Computing** und die ersten beiden Kapitel von *Machine Intelligence*: **keine externen Abhängigkeiten**
- Ab **02_MachineIntelligence, Kapitel 3**: `numpy`, `scikit-learn` (`pip install numpy scikit-learn`)
- Kein PyTorch, kein TensorFlow, keine vorgefertigten Modell-Schichten

---

## 🎯 Für wen ist das gedacht?

- **Schüler der Oberstufe** und **Studienanfänger**, die verstehen wollen, wie Computer und KI wirklich funktionieren
- **Lehrkräfte**, die einen roten Faden für einen Kurs oder eine AG suchen
- **Ingenieurinnen und Entwickler**, die die Grundlagen ihres Feldes einmal *from scratch* durchdenken wollen
- **Alle Neugierigen**, die bei GPT nicht „irgendein Deep-Learning-Kram" hören wollen, sondern die Bausteine sehen

---

## 📖 Wie du dieses Repository durcharbeitest

1. Lies das Vorwort ([`PREFACE.md`](PREFACE.md)) — es ordnet die drei Teile ein.
2. Wähle einen Teil aus. Die Empfehlung ist: **01_Computing zuerst**, dann 02_MachineIntelligence, dann 03_AgenticSystems.
3. Innerhalb eines Teils: die Kapitel sind nummeriert, in dieser Reihenfolge durcharbeiten.
4. Für jedes Kapitel: die README lesen, das Programm ausführen, die Übungen am Ende bearbeiten.

Jedes Kapitel ist so aufgebaut, dass es **an einem Nachmittag verstehbar** ist — auch wenn man einige Nachmittage brauchen wird, um alle Details zu durchdringen.

---

## 📜 Lizenz und Nutzung

Frei für den Bildungsgebrauch. Beiträge, Übersetzungen und Ergänzungen sind willkommen.