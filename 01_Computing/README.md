# Milestones in Computing

**Vom Transistor zum Programm — vier Meilensteine, die zeigen, wie ein Computer wirklich funktioniert.**

Alles selbst programmiert, ohne Frameworks. Jede Instruktion, jedes Bit, jedes Bus-Signal ist im Code sichtbar.

---

## 📜 Warum dieser Teil?

Das mag zunächst erstaunen: In einer Reihe über KI und Sprachmodelle mit *Rechnerarchitektur* beginnen? Aber es ist kein Umweg. Es ist die Grundlage.

Jedes neuronale Netz läuft auf einem Prozessor. Jeder Prozessor läuft in einem Betriebssystem. Jedes Programm ist durch einen Compiler übersetzt worden. Und wenn Modelle über Netzwerke kommunizieren — beim Training auf tausenden GPUs, beim Ausrollen als Cloud-Dienst — ist auch das ein Grundlagen­thema.

Wer nicht versteht, wie diese vier Schichten (CPU, OS, Compiler, Netzwerk) funktionieren, wird bei Fragen wie *„Warum ist mein Training so langsam?"* oder *„Warum verhält sich mein Modell auf einer anderen Maschine anders?"* im Dunkeln tappen. Wer sie versteht, hat die Werkzeuge, um solche Fragen zu beantworten.

Und noch wichtiger: dieser erste Teil gehört, anders als die Kapitel in *Machine Intelligence*, zu den **zeitlos gültigen** Grundlagen der Informatik. Die Ideen, die Turing, von Neumann, Backus, Ritchie und Kahn/Cerf hatten, funktionieren heute noch genau wie damals.

---

## 🕰️ Historischer Bogen

| Jahr | Ereignis | Kapitel |
|------|----------|---------|
| **1945** | Von Neumann — Architektur mit Speicher, ALU, Kontrolleinheit | **1. CPU** |
| **1947** | Erste Transistoren bei Bell Labs (Bardeen, Brattain, Shockley) | |
| **1948** | Kilburn / Manchester — erstes speicherprogrammiertes System | |
| **1955** | GM-NAA I/O — erstes echtes Batch-Betriebssystem | **2. OS** |
| **1957** | Backus (IBM) — FORTRAN, erster erfolgreicher Compiler | **3. Compiler** |
| **1958** | McCarthy (MIT) — LISP | |
| **1959** | Hopper et al. — COBOL, natürlichsprachliche Programmierung | |
| **1961** | Atlas Supervisor — erstes OS mit virtuellem Speicher | |
| **1969** | Ritchie & Thompson — Unix | |
| **1969** | ARPANET | **4. Network** |
| **1972** | Ritchie — C, „portables Assembler" | |
| **1974** | Kahn & Cerf — TCP/IP | |
| **1983** | ARPANET wird zum Internet | |

Zwei Jahrzehnte reichten aus, um die vier zeitlosen Bausteine der Informatik zu erfinden. Die 60 Jahre danach waren *Skalierung* dieser Ideen — nicht ihre Ablösung.

---

## 🧭 Die vier Meilensteine

### [`01_CPU/`](01_CPU/) — Eine 4-Bit-CPU von Hand

**Kern:** Ein simulierter Prozessor mit den fünf Bausteinen jeder Von-Neumann-Maschine — **Programmzähler**, **Register**, **ALU**, **Bus**, **Kontrolleinheit mit Mikrocode-ROM**. Programme sind in einer eigenen Assembler-Sprache mit 16 Opcodes geschrieben. Die Simulation läuft in einem Terminal-UI: man kann live zusehen, wie ein Programm Instruktion für Instruktion ausgeführt wird — welche Bus-Signale gerade aktiv sind, welche Werte in den Registern stehen, welcher Mikrocode-Eintrag gerade den Bus ansteuert.

**Wow-Moment:** Man sieht, wie aus einer einzigen Instruktion `ADD` in Wirklichkeit *drei* parallele Bus-Aktivitäten werden (`ALU_OUT`, `AX_IN`, `ALU_ADD`). Der Trick heißt Mikrocode, und er ist bis heute die Grundlage jeder CPU-Firmware.

### [`02_OS/`](02_OS/) — Ein Mini-Betriebssystem

**Kern:** Zwei verschiedene OS-Modelle auf derselben CPU-Basis:

- **Weg 1** — ein *kooperatives Multitasking-OS* mit **Segment-Register** und **YIELD**-Opcode. Zwei Prozesse laufen quasi-gleichzeitig, jeder in seinem eigenen RAM-Segment, das OS macht Context-Switches bei jedem YIELD. Nachbau von Mac OS Classic / Windows 3.x.

- **Weg 2** — ein *Batch-OS, das selbst ein Assembler-Programm ist* (im 4-Bit-Instruktionssatz der CPU). Es liegt bei `BP=0` im Programmspeicher, wird beim Boot ausgeführt, ruft User-Jobs nacheinander auf und bekommt via `HLT`-Trap die Kontrolle zurück. **10 Instruktionen** OS-Code, mehr braucht es nicht. Nachbau von GM-NAA I/O (1955).

**Wow-Moment:** Bei Weg 2 sieht man, wie ein „böser" User-Job durch einfaches Überschreiben einer RAM-Zelle den Scheduler manipulieren kann — genau die Unsicherheit, die zur Erfindung von MMUs und Speicherschutz führte.

### [`03_Compiler/`](03_Compiler/) — Vier Sprachen, ein Assembler

**Kern:** Vier Frontends (COBOL, FORTRAN, C, LISP), jedes mit eigener Grammatik und Boilerplate — von 5 Zeilen LISP bis 18 Zeilen COBOL. Alle produzieren denselben internen **AST** (Abstract Syntax Tree), aus dem ein gemeinsamer Codegenerator identischen Assembler-Code für die CPU aus Kapitel 1 erzeugt. Der Assembler läuft dann auf dem Simulator, und das Ergebnis-Register OUT enthält am Ende die berechnete Zahl.

**Wow-Moment:** Die Rechnung `(3 + 4) - 1 = 6` — in vier Sprachen geschrieben, kompiliert zu bit-identischen 13 Assembler-Instruktionen (nur COBOL braucht 2 mehr, weil `ADD ... GIVING` das Zwischenergebnis nach RAM zwingt). Die Botschaft: **Sprache ist reine Ergonomie. Die Maschine sieht immer nur die 16 Opcodes.**

### [`04_PerceptronOnCPU/`](04_PerceptronOnCPU/) — Das erste Perceptron als Assembler-Programm

**Kern:** Rosenblatts Perceptron (1958) — ein einzelnes künstliches Neuron mit zwei Eingängen — in **16 Instruktionen** auf unserer 4-Bit-CPU. Wir erweitern die CPU um zwei neue Opcodes (`MUL` für die Gewichtungen, `JN` für „Jump if Negative" beim Schwellwert-Vergleich). Das Programm klassifiziert AND, OR, NAND perfekt. Beim vierten Test — XOR — findet auch eine erschöpfende Brute-Force-Suche über 512 Gewichts-Kombinationen keinen Satz, der alle 4 Fälle richtig klassifiziert.

**Wow-Moment:** Der Vergleich der drei Tabellen (AND/OR/NAND jeweils 4/4, XOR maximal 3/4) — und damit das empirische Wiedersehen von Minsky/Papert 1969. Der erste KI-Winter beginnt genau hier, an dieser einen 16-Instruktions-Grenze.

Dieses Kapitel ist die **Brücke zu Teil 2**: es zeigt, dass ein neuronales Netz aus Sicht der CPU nur ein sehr kurzes Programm ist. GPT ist Milliarden mal komplexer, aber die Grundoperation `w·x + b` läuft genau so.

### `05_Network/` — Zwei Rechner sprechen miteinander *(geplant)*

**Kern:** Zwei simulierte CPUs, die über einen einfachen Kommunikations­kanal (Byte-Stream) Nachrichten austauschen. Wir bauen einen minimalen „Protokollstack": Frames mit Header und Checksumme, ein Zustandsautomat für Verbindungsaufbau und -abbau, Retransmission bei Paketverlust. Kein IP, kein TCP im Detail — aber die *Ideen* dieser Schichten. Als kanonische Demo: ein handgeschriebener HTTP-GET-Request an einen imaginären LLM-Service — Byte für Byte sichtbar.

**Wow-Moment:** *(kommt noch)* — vermutlich der Moment, wo die simulierte Netzwerk-Botschaft `POST /v1/chat/completions` durch alle Schichten hindurch als eine Kette von Frames wiederauftaucht, und man sieht, dass ein API-Call an ChatGPT nichts anderes ist als 1970er-Technologie mit sehr viel mehr Bandbreite.

---

## 🧭 Der rote Faden

Jedes Kapitel behebt eine Grenze des vorherigen:

> **CPU allein**: Ein Programm läuft, aber wie kommen mehrere Programme auf denselben Rechner? → **OS**  
> **OS + CPU**: Programme laufen, aber wie schreibt man sie in einer Sprache, die einen Menschen nicht verrückt macht? → **Compiler**  
> **Compiler + OS + CPU**: Programme werden geschrieben und laufen, aber ein Rechner ist eine Insel — wie kommunizieren wir mit anderen? → **Netzwerk**

Am Ende dieses Teils hast du **alle vier klassischen Grundlagen der Informatik** einmal selbst gebaut. Damit kannst du dann fundiert nach `02_MachineIntelligence/` wechseln, in dem wir aus diesem Fundament heraus lernende Maschinen bauen.

---

## 🚀 Schnelleinstieg

```bash
cd 01_Computing

# Kapitel 1: CPU-Simulator (Live-UI)
python 01_CPU/src/main.py

# Kapitel 2, Weg 1: Kooperatives Multitasking mit YIELD
python 02_OS/src/os_sim.py

# Kapitel 2, Weg 2: Batch-OS, das selbst ein Assembler-Programm ist
python 02_OS/src/os_batch.py

# Kapitel 3: Compiler-Test — vier Sprachen, ein Assembler
python 03_Compiler/test_compiler.py

# Einzelnes Beispiel kompilieren:
cd 03_Compiler
python -m src.compile examples/arith.c --run
```

Alle Programme laufen mit **Python 3.7+** ohne externe Abhängigkeiten. Für die Terminal-UI benötigt man ein ANSI-fähiges Terminal (Windows Terminal, iTerm, Linux-Konsole).

---

## 🧠 Was dieser Teil bewusst nicht zeigt

- **Digitale Logik unterhalb der CPU** — wir setzen bei der Ebene „Bus, Register, ALU" ein, nicht bei Transistoren, Gattern, Flipflops. Das wäre ein eigener Meilenstein wert (z.B. ein NAND-Gate-Simulator, aus dem sich alles andere aufbauen lässt), aber er würde den Rahmen sprengen.
- **Moderne CPU-Techniken** — Pipelining, Out-of-Order-Execution, Cache-Hierarchien, Branch Prediction, Vector-Instruktionen, Multicore. Alles wichtig, alles gehört auf eine reale CPU, aber didaktisch würde es die Ideen unter Details begraben.
- **Vollständige Sprachen** — der Compiler in Kapitel 3 unterstützt nur einen winzigen Ausschnitt jeder Sprache. Er zeigt das *Prinzip*, nicht die Realität eines GCC oder LLVM.
- **Echte Netzwerkprotokolle** — Kapitel 4 wird TCP nicht komplett nachbauen. Es zeigt die *Ideen* (Frame, Header, Checksum, Retransmission), nicht den Standard.

Wenn du diese Beschränkungen für zu eng hältst, ist das genau der Punkt, an dem du bereit bist, dich mit den originalen Standards zu befassen — was dann viel einfacher fällt, wenn die Grundstruktur schon steht.

---

## 📚 Referenzen

- Petzold, C. (2000). *Code: The Hidden Language of Computer Hardware and Software*. Microsoft Press. Der Klassiker: vom Morsezeichen zum Computer, ganz ohne Vorwissen.
- Nisan, S., & Schocken, S. (2008). *The Elements of Computing Systems* — auch bekannt als „nand2tetris". Vom NAND-Gatter über CPU und Compiler bis zum Betriebssystem, alles selbst gebaut. Direkte Inspiration für diesen Teil.
- Patterson, D., & Hennessy, J. (2020). *Computer Organization and Design* (6th ed.). Der Standard-Lehrtext zur Rechnerarchitektur.
- Silberschatz, A., Galvin, P., & Gagne, G. (2018). *Operating System Concepts* (10th ed.). Standard-Referenz für OS.
- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2007). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Der „Dragon Book".
- Kurose, J., & Ross, K. (2020). *Computer Networking: A Top-Down Approach* (8th ed.). Standard-Text für Netzwerke.
- Tanenbaum, A. S. (2015). *Modern Operating Systems* (4th ed.). Pearson.