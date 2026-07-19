# 🗺️ Roadmap: Milestones in Computing

Ein Lehrpfad in **fünf Meilensteinen**, der vom kleinsten selbst simulierten Prozessor über das erste Perceptron bis zu einem eigenen kleinen Netzwerkstack führt.

Zielgruppe: **Abiturienten und Studienanfänger**, die Python grundlegend beherrschen und Interesse haben, unter die Motorhaube ihres Computers zu schauen.

---

## 🧭 Der rote Faden

Jedes Kapitel beantwortet eine konkrete Frage und öffnet damit die nächste:

| Nr. | Meilenstein | Neu | Grenze — motiviert nächsten Schritt |
|-----|-------------|-----|--------------------------------------|
| **1** | **CPU** (Von Neumann 1945 → 6502 / 8080 → Intel 8086) | Bus, Register, ALU, Mikrocode, Assembler | Nur *ein* Programm läuft gleichzeitig |
| **2** | **Betriebssystem** (GM-NAA I/O 1955 → Atlas 1961 → Unix 1969) | Prozess, Segment, Context-Switch, HLT-Trap | Programme muss man in Assembler schreiben — schmerzhaft |
| **3** | **Compiler** (FORTRAN 1957 → LISP 1958 → C 1972) | Lexer, Parser, AST, Codegenerator | Ein Rechner ist eine Insel |
| **4** | **Perceptron auf der CPU** (Rosenblatt 1958 → Minsky/Papert 1969) | MUL/JN-Opcode, 4-Bit-2K, Schwellwert-Neuron | XOR nicht lösbar → *Machine Intelligence, Kap. 2: MLP* |
| **5** | **Netzwerk** (ARPANET 1969 → TCP/IP 1974) | Frame, Header, Checksum, Retransmission | *(zeigt: LLM-API ist HTTP über TCP über IP über Ethernet)* |

---

## 📚 Aktueller Stand

- [x] **Meilenstein 1**: 4-Bit-CPU-Simulator mit Bus, ALU, RAM, Mikrocode-ROM, drei CPU-Konfigurationen (minimal, akku-basiert, zwei-Register)
- [x] **Meilenstein 2**: Mini-OS in zwei Ausbaustufen:
  - **Weg 1**: kooperatives Multitasking (Python-orchestriert, YIELD-Opcode, Segment-Register)
  - **Weg 2**: Batch-OS als *echtes* Assembler-Programm (10 Instruktionen, BP-Register, HLT-Trap)
- [x] **Meilenstein 3**: Multi-Sprach-Compiler (COBOL, FORTRAN, C, LISP) → gemeinsamer AST → derselbe Assembler
- [x] **Meilenstein 4**: Perceptron auf der 4-Bit-CPU — MUL/JN-Erweiterung, 16-Instruktions-Programm klassifiziert AND/OR/NAND, XOR bleibt unlösbar
- [ ] **Meilenstein 5**: Netzwerkstack (HTTP-GET zum LLM-Service) — *in Planung*

---

## 🎬 Übergreifende narrative Klammer

Alle vier Meilensteine bauen auf **derselben 4-Bit-CPU** auf. Der OS-Kernel läuft auf ihr, der Compiler generiert Code für sie, das Netzwerk-Kapitel wird zwei Instanzen davon miteinander kommunizieren lassen.

Damit ist die didaktische Erzählung durchgängig: *ein Prozessor, viele Anwendungen.*

Nach diesem Teil hat man das komplette **Fundament der Informatik** einmal selbst gebaut und kann in *Machine Intelligence* mit einem festen Verständnis dessen weitermachen, worauf die neuronalen Netze eigentlich laufen.

---

## 🛠️ Technisches Vorgehen

| Bereich | Meilenstein 1–4 |
|---------|-----------------|
| Sprache | Deutsch |
| Numerik | Reines Python (keine externen Abhängigkeiten) |
| Frameworks | keine |
| UI | Terminal (ANSI-Farben, Cursor-Positionierung) |
| Zielarchitektur | Selbst simulierte 4-Bit-CPU mit 16 Opcodes |

Wir bauen **alles selbst**: den CPU-Kern, den Assembler-Parser, das OS-Programm, die Compiler-Frontends, die Testinfrastruktur. Kein PyTorch, kein TCP-Stack aus der Standardbibliothek, keine Docker-Container.

---

## 🧭 Was lebt heute noch von diesen Ideen?

| Meilenstein | Status heute | Warum es hier drin ist |
|-------------|--------------|-----------------------|
| **1. CPU** | Ideen fast unverändert. Moderne CPUs sind massiv skalierte Von-Neumann-Maschinen (Pipelining, Cache, Multicore, Vector), aber im Kern immer noch: Register laden → Rechnen → Speichern. | Weil jede weitere Schicht auf CPU-Semantik aufbaut. |
| **2. OS** | Batch weitgehend historisch, kooperatives Multitasking abgelöst durch preemptives. Aber der **Context-Switch** ist konzeptionell identisch. Segment-Register lebt im x86-Real-Mode weiter, x86-64 nutzt Paging. | Zeigt, wo *Kernel/User-Trennung* herkommt. |
| **3. Compiler** | Alle vier Ausgangssprachen leben. Die *Architektur* (Frontend → AST → Codegen) ist bei GCC/LLVM identisch, nur eine Größenordnung ausgereifter. | Der Ansatz „Sprache ist reine Ergonomie" ist heute wichtiger denn je (siehe: Rust, Go, Swift, Kotlin — vier neue Sprachen in einem Jahrzehnt). |
| **4. Netzwerk** | TCP/IP ist unverändert seit 1983 der Standard. HTTP/QUIC sind nur weitere Schichten darauf. | Zeigt: die *einfachen* Ideen (Frame, Ack, Retransmit) tragen ein weltweites Netz. |

**Eine Beobachtung**: Alle vier Bausteine wurden zwischen 1945 und 1974 erfunden — in weniger als 30 Jahren. Die folgenden 50 Jahre waren Ausbau und Skalierung, keine Neuerfindung.

---

## 🔭 Wie geht es weiter?

Nach diesen vier Meilensteinen ist die klassische *„wie funktioniert ein Computer"*-Frage beantwortet. Der Weg von hier ist:

- **[`02_MachineIntelligence/`](../02_MachineIntelligence/)** — Die 60 Jahre KI-Forschung von 1958 bis 2018 — vom Perceptron bis zum ersten GPT. Die neuronalen Netze, die wir dort bauen, laufen konzeptionell auf denselben Grundprinzipien: sie werden vom Compiler in Instruktionen übersetzt, laufen auf CPUs (bzw. deren skalierter Verwandtschaft, den GPUs), werden vom OS orchestriert und kommunizieren über Netzwerke.

- **[`03_AgenticSystems/`](../03_AgenticSystems/)** — Anwendungen und Skalierung: wie aus Mini-GPT die heutigen LLMs, Agenten und Domänen-Modelle wurden.

Wer alle drei Teile durchgearbeitet hat, versteht: **die letzten 80 Jahre Informatik sind eine einzige zusammenhängende Erzählung.** Nichts ist Magie, alles ist gebaut.
