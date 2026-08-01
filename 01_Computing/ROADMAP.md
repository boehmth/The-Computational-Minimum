# 🗺️ Roadmap: Milestones in Computing

Ein Lehrpfad in **sechs Meilensteinen**, der vom kleinsten selbst simulierten Prozessor über das erste Perceptron und die GPU als KI-Rechenwerk bis zu einem eigenen kleinen Netzwerkstack führt.

Zielgruppe: **Abiturienten und Studienanfänger**, die Python grundlegend beherrschen und Interesse haben, unter die Motorhaube ihres Computers zu schauen.

---

## 🧭 Der rote Faden

Jedes Kapitel beantwortet eine konkrete Frage und öffnet damit die nächste:

| Nr. | Meilenstein | Neu | Grenze — motiviert nächsten Schritt |
|-----|-------------|-----|--------------------------------------|
| **1** | **CPU** (Von Neumann 1945 → 6502 / 8080 → Intel 8086) | Bus, Register, ALU, Mikrocode, Assembler | Nur *ein* Programm läuft gleichzeitig |
| **2** | **Betriebssystem** (GM-NAA I/O 1955 → Atlas 1961 → Unix 1969) | Prozess, Segment, Context-Switch, HLT-Trap | Programme muss man in Assembler schreiben — schmerzhaft |
| **3** | **Compiler** (FORTRAN 1957 → LISP 1958 → C 1972) | Lexer, Parser, AST, Codegenerator | Sprache ist bequem — aber die Maschine bleibt seriell |
| **4** | **Perceptron auf der CPU** (Rosenblatt 1958 → Minsky/Papert 1969) | MUL/JN-Opcode, 4-Bit-2K, Schwellwert-Neuron | XOR nicht lösbar (→ *Machine Intelligence, Kap. 2: MLP*), und schon ein MLP wäre auf dieser CPU viel zu langsam |
| **5** | **GPU** (Fixed-Function 1996 → Shader 2001 → BrookGPU 2004 → CUDA 2006 → AlexNet 2012) | SIMT, Kernel, Warp, Parallel-Reduktion | Eine Maschine reicht nicht für GPT-3 → 10 000 GPUs müssen kommunizieren |
| **6** | **Netzwerk** (ALOHAnet 1970 → Ethernet 1976 → TCP/IP 1974/1983) | Probabilistischer Kanalzugriff, Kollisionsverhalten, S = G·exp(−G)-Kurve | *(schliesst Teil 1 ab: aus reiner Bit-Uebertragung wird noch keine Bedeutung — deshalb Teil 2)* |

---

## 📚 Aktueller Stand

- [x] **Meilenstein 1**: 4-Bit-CPU-Simulator mit Bus, ALU, RAM, Mikrocode-ROM, drei CPU-Konfigurationen (minimal, akku-basiert, zwei-Register)
- [x] **Meilenstein 2**: Mini-OS in zwei Ausbaustufen:
  - **Weg 1**: kooperatives Multitasking (Python-orchestriert, YIELD-Opcode, Segment-Register)
  - **Weg 2**: Batch-OS als *echtes* Assembler-Programm (10 Instruktionen, BP-Register, HLT-Trap)
- [x] **Meilenstein 3**: Multi-Sprach-Compiler (COBOL, FORTRAN, C, LISP) → gemeinsamer AST → derselbe Assembler
- [x] **Meilenstein 4**: Perceptron auf der 4-Bit-CPU — MUL/JN-Erweiterung, 16-Instruktions-Programm klassifiziert AND/OR/NAND, XOR bleibt unlösbar
- [x] **Meilenstein 5**: GPU-Kapitel — SIMT-Simulator (`gpu_sim.py`), Vektor-Add-/ReLU-/Dot-Kernels mit verifizierten Ergebnissen (~8× Speedup, log₂(n)-Reduktion), Matrix-Multiplikations-Vergleich (~102× Speedup) und CUDA-C-Anhang zum Lesen.
- [x] **Meilenstein 6**: ALOHA-Netzwerk-Simulator (`aloha.py`) — Pure + Slotted ALOHA, verifizierte Theoriekurven ($S_{\max}$ = 18,4 % / 36,8 %), ASCII-Zeitachse mit sichtbaren Kollisionen, historischer Ausblick auf CSMA/CD/Ethernet in `notes/ethernet.md`.


## 🎬 Übergreifende narrative Klammer

Die Meilensteine 1–4 und 6 bauen auf **derselben 4-Bit-CPU** auf. Der OS-Kernel läuft auf ihr, der Compiler generiert Code für sie, das Netzwerk-Kapitel wird zwei Instanzen davon miteinander kommunizieren lassen. Meilenstein 5 (GPU) bricht diese Klammer bewusst — er zeigt, dass eine *andere* Hardware-Architektur (viele einfache Kerne statt weniger komplexer) für einen bestimmten Aufgabentyp (Matrix-Multiplikation im neuronalen Netz) fundamental besser ist. Genau das ist der Grund, warum es zwischen CPU-Perceptron (Kap. 4) und AlexNet 2012 die eigentliche Deep-Learning-Welle brauchte.

Damit ist die didaktische Erzählung durchgängig: *ein Prozessor, viele Anwendungen — bis eine Anwendung so hungrig wird, dass sie sich einen neuen Prozessor sucht.*

Nach diesem Teil hat man das komplette **Fundament der Informatik plus des KI-Rechenwerks GPU** einmal selbst gebaut und kann in *Machine Intelligence* mit einem festen Verständnis dessen weitermachen, worauf die neuronalen Netze eigentlich laufen.

---

## 🛠️ Technisches Vorgehen

| Bereich | Meilenstein 1–6 |
|---------|-----------------|
| Sprache | Deutsch |
| Numerik | Reines Python (keine externen Abhängigkeiten) |
| Frameworks | keine — auch die GPU-Simulation ist reines Python |
| UI | Terminal (ANSI-Farben, Cursor-Positionierung) |
| Zielarchitektur | Selbst simulierte 4-Bit-CPU mit 16 Opcodes (Kap. 1–4, 6); eigenes SIMT-Simulationsmodell (Kap. 5) |

Wir bauen **alles selbst**: den CPU-Kern, den Assembler-Parser, das OS-Programm, die Compiler-Frontends, die Testinfrastruktur. Kein PyTorch, kein TCP-Stack aus der Standardbibliothek, keine Docker-Container.

---

## 🧭 Was lebt heute noch von diesen Ideen?

| Meilenstein | Status heute | Warum es hier drin ist |
|-------------|--------------|-----------------------|
| **1. CPU** | Ideen fast unverändert. Moderne CPUs sind massiv skalierte Von-Neumann-Maschinen (Pipelining, Cache, Multicore, Vector), aber im Kern immer noch: Register laden → Rechnen → Speichern. | Weil jede weitere Schicht auf CPU-Semantik aufbaut. |
| **2. OS** | Batch weitgehend historisch, kooperatives Multitasking abgelöst durch preemptives. Aber der **Context-Switch** ist konzeptionell identisch. Segment-Register lebt im x86-Real-Mode weiter, x86-64 nutzt Paging. | Zeigt, wo *Kernel/User-Trennung* herkommt. |
| **3. Compiler** | Alle vier Ausgangssprachen leben. Die *Architektur* (Frontend → AST → Codegen) ist bei GCC/LLVM identisch, nur eine Größenordnung ausgereifter. | Der Ansatz „Sprache ist reine Ergonomie" ist heute wichtiger denn je (siehe: Rust, Go, Swift, Kotlin — vier neue Sprachen in einem Jahrzehnt). |
| **4. Perceptron auf CPU** | Als eigenständige Anwendung obsolet, aber `w·x + b` ist der Kern *jedes* Neurons in *jedem* modernen Netz. | Zeigt, dass ein neuronales Netz aus Sicht der Maschine nur ein sehr kurzes Programm ist. |
| **5. GPU** | **Der aktuelle Standard** für alles KI-Training. NVIDIA H100/B200, Google TPUs, AMD MI300 sind alle SIMT-Beschleuniger — genau das Modell, das dieses Kapitel simuliert. Tensor Cores fügen darauf noch Matrix-Multiplikations-Spezialhardware hinzu. | Ohne GPU keine moderne KI. Punkt. |
| **6. Netzwerk** | TCP/IP ist unverändert seit 1983 der Standard. HTTP/QUIC sind nur weitere Schichten darauf. | Zeigt: die *einfachen* Ideen (Frame, Ack, Retransmit) tragen ein weltweites Netz — und ein weltweites GPU-Training. |

**Eine Beobachtung**: Fünf der sechs Bausteine (CPU, OS, Compiler, Perceptron, Netzwerk) wurden zwischen 1945 und 1974 erfunden — in weniger als 30 Jahren. Der sechste (GPU als KI-Hardware) ist etwa 25 Jahre später dazugekommen und ist damit **die einzige wirklich neue Klasse von Rechen­technik, die dieses Buch behandelt**. Alles andere ist Skalierung.

---

## 🔭 Wie geht es weiter?

Nach diesen sechs Meilensteinen ist die klassische *„wie funktioniert ein Computer"*-Frage vollständig beantwortet — inklusive der Antwort auf die Nachfolgefrage *„wie skaliert man ihn für KI?"*. Der Weg von hier ist:

- **[`02_MachineIntelligence/`](../02_MachineIntelligence/)** — Die 60 Jahre KI-Forschung von 1958 bis 2018 — vom Perceptron bis zum ersten GPT. Die neuronalen Netze, die wir dort bauen, laufen konzeptionell auf denselben Grundprinzipien: sie werden vom Compiler in Instruktionen übersetzt, laufen auf CPUs (bzw. deren skalierter Verwandtschaft, den GPUs), werden vom OS orchestriert und kommunizieren über Netzwerke.

- **[`03_LanguageModelling/`](../03_LanguageModelling/)** — Anwendungen und Skalierung: wie aus einem Mini-GPT die heutigen LLMs, Agenten und Domänen-Modelle wurden.

Wer alle drei Teile durchgearbeitet hat, versteht: **die letzten 80 Jahre Informatik sind eine einzige zusammenhängende Erzählung.** Nichts ist Magie, alles ist gebaut.


