# Die Von-Neumann-Architektur — Programm und Daten im selben Speicher

*Deep Dive für Kapitel [`01_CPU`](../01_CPU/README.md). Ergänzt den README-
Abschnitt „Wie kommt aus einem Kabelbaum eine Rechenmaschine?" um die
formale Grundlage: was genau ist ein Computer, wie führt er eine
Instruktion aus, und was steckt hinter dem Mikrocode-Zyklus.*

Die meisten gängigen Digitalrechner entsprechen der **Von-Neumann-
Architektur**, die Mitte der 1940er Jahre von John von Neumann in
seinem *„First Draft of a Report on the EDVAC"* (1945) formuliert
wurde. Die Idee ist heute so selbstverständlich, dass ihre eigentliche
Radikalität leicht übersehen wird: **Programm und Daten liegen im
selben Speicher, in gleicher Binärkodierung**. Was Instruktion und was
Datum ist, entscheidet allein der Kontext, in dem der Prozessor die
betreffende Speicherzelle liest.

Bevor wir die Architektur genauer betrachten, lohnt ein Blick auf zwei
Vorstufen: den Automatenbegriff und das EVA-Prinzip.

──────────◆──────────◆──────────◆──────────◆──────────

## Automaten, Computer, Programme

### Der Automatenbegriff

Ein **Automat** ist im allgemeinsten Sinne ein technisches Gerät —
mechanisch, elektrisch, elektronisch — das eine Eingabe entgegennimmt
und in Abhängigkeit von dieser Eingabe *und* dem inneren Zustand des
Geräts eine Ausgabe produziert.

Ein **endlicher Automat** besitzt nur endlich viele Eingaben und
endlich viele innere Zustände. In der Praxis synonym mit „Automat":
Getränkeautomat, Fahrkartenautomat, Waschmaschinen-Steuerung. Diese
Geräte akzeptieren eine Eingabe (Geld, Produktwahl, Programmwahl),
haben Zustände (Produkt vorrätig / nicht, Waschgang läuft / Endphase),
und produzieren Ausgaben (Ware, Wechselgeld, Endsignal).

### Was einen Computer daraus macht

Ein **Computer** ist ein spezieller Automat mit einer entscheidenden
Zusatz-Eigenschaft:

> Ein Computer ist ein Automat, dessen Verhalten durch ein
> **austauschbares Programm** gesteuert wird.

Genau die *freie Programmierbarkeit* ist das Unterscheidungsmerkmal.
Ein Getränkeautomat ist nicht programmierbar — sein Verhalten liegt in
der Verkabelung fest. Ein Computer dagegen führt für unterschiedliche
Programme unterschiedliche Berechnungen durch, ohne dass an der
Hardware etwas geändert werden muss. Dieselbe Maschine kann Zahlen
sortieren, Bilder rendern oder ein neuronales Netz trainieren — es
kommt allein darauf an, welches Programm gerade im Speicher steht.

Ein **Programm** ist dabei eine Folge von Anweisungen, die den
Regeln einer bestimmten Programmiersprache gehorchen. Diese
Anweisungen werden in der Regel sequenziell abgearbeitet, mit
Wiederholungen (Schleifen), Verzweigungen (Sprünge) und optional
parallelen Abschnitten.

### Hardware vs. Software

Die **Hardware** eines Computersystems umfasst alle Bauelemente: den
Prozessor (der Programme ausführt), den Speicher (der Programme und
Daten aufnimmt), Peripheriegeräte (zur Ein- und Ausgabe) und Vernetzungs-
komponenten.

Die **Software** ist die Gesamtheit aller Programme, die auf dieser
Hardware laufen können. Der Trick der Von-Neumann-Architektur ist, dass
sie den Grenzbereich zwischen beidem gestaltet: das Programm ist eine
*Datenstruktur* im selben Speicher, der auch die eigentlichen
Rechendaten hält. Das ist keine Selbstverständlichkeit — historisch
gab es Konkurrenzarchitekturen (die *Harvard-Architektur* mit
getrennten Speichern für Instruktion und Daten, wie sie bis heute in
einigen Mikrocontrollern verwendet wird), aber Von Neumanns Idee hat
sich durchgesetzt, weil sie zwei sehr wichtige Fähigkeiten erlaubt:
**selbstmodifizierende Programme** und **Programme, die Programme
laden** (Compiler, Betriebssysteme, Interpreter).

──────────◆──────────◆──────────◆──────────◆──────────

## Das EVA-Prinzip

Die Umwandlung der Eingabedaten in Ausgabedaten durch die Verarbeitung
eines Computers wird schematisch durch das **EVA-Prinzip** beschrieben:

```
   ┌──────────┐      ┌─────────────┐      ┌──────────┐
   │ Eingabe  │ ───► │Verarbeitung│ ───► │ Ausgabe  │
   │(Tastatur │      │  (CPU +    │      │(Monitor, │
   │ Maus …)  │      │   RAM)     │      │ Drucker) │
   └──────────┘      └──────┬──────┘      └──────────┘
                            │
                     ┌──────▼──────┐
                     │ Speicher    │
                     │(SSD, HDD…)  │
                     └─────────────┘
```

- **E**ingabe: Rohdaten von Peripheriegeräten oder aus Dateien
- **V**erarbeitung: Ausführung von Instruktionen in CPU/RAM
- **A**usgabe: Ergebnisse an Peripheriegeräte oder in Dateien
- **Speicher** (die eigentlich unbenannte vierte Ebene): persistente
  Ablage von Daten *und* Programmen zwischen Läufen.

Das EVA-Prinzip ist stark vereinfacht — es sagt nichts über *wie* die
Verarbeitung intern abläuft. Genau das klärt die Von-Neumann-Architektur.

──────────◆──────────◆──────────◆──────────◆──────────

## Die Von-Neumann-Architektur im Detail

Ein Computer nach Von-Neumann-Architektur besteht aus fünf
Grundkomponenten:

```
   ┌──────────────────────────────────────────────────┐
   │                                                  │
   │   ┌────┐   ┌────────┐   ┌────────┐               │
   │   │ PC │   │  IR    │   │  ALU   │               │
   │   └─┬──┘   └───┬────┘   └───┬────┘               │
   │     │          │            │                    │
   │  ═══╧══════════╧════════════╧══════════ Bus      │
   │     │          │            │                    │
   │   ┌─┴──────┐   │       ┌────┴────┐               │
   │   │ RAM    │   │       │ Register│               │
   │   │ (Prog+ │   │       │ (ACC, …)│               │
   │   │  Daten)│   │       └─────────┘               │
   │   └────────┘   │                                 │
   │                │                                 │
   │           ┌────▼────────┐                        │
   │           │ Control Unit│  ← Mikrocode-ROM       │
   │           └─────────────┘                        │
   └──────────────────────────────────────────────────┘
```

Fünf Bausteine, ein gemeinsamer Bus. Die einzelnen Komponenten sind:

- **RAM** (Random Access Memory): der Hauptspeicher. Enthält *Programm
  und Daten* — dieselbe Bit-Sequenz, unterschiedliche Interpretation.
- **PC** (Program Counter): ein Register, das die Adresse der nächsten
  auszuführenden Instruktion enthält.
- **IR** (Instruction Register): das Register, in das die *gerade zu
  interpretierende* Instruktion geladen wird.
- **ALU** (Arithmetisch-Logische Einheit): führt Rechenoperationen und
  logische Verknüpfungen aus. Physikalisch das Addierwerk plus einige
  Logikgatter (siehe [`schaltnetze.md`](schaltnetze.md)).
- **Register**: kleine, schnelle Zwischenspeicher für Zwischenergebnisse
  (in unserer Simulation: `ACC`, `TMP`, `BX`, …). Deutlich schneller
  als RAM, dafür sehr wenige und sehr kleine.
- **Control Unit**: das *Steuerwerk*. Sie liest die aktuelle Instruktion
  aus dem IR, dekodiert sie mit Hilfe des Mikrocode-ROMs und erzeugt
  daraus die einzelnen Steuersignale, die die anderen Bausteine
  koordinieren.

Alle Bausteine sind an einen gemeinsamen **Bus** angeschlossen — die
Sammelleitung, die alle Datentransporte trägt. Auf realer Hardware sind
das Daten-, Adress- und Steuerbus getrennt; in unserer 4-Bit-Simulation
sind sie zu einem einzigen logischen Bus zusammengefasst.

──────────◆──────────◆──────────◆──────────◆──────────

## Fetch und Execute: der Zwei-Phasen-Zyklus

Jede Instruktion wird in zwei Phasen abgearbeitet:

1. **Fetch-Phase**: die Adresse aus dem `PC` wird auf den Bus gelegt,
   der Speicher liest das dortige Wort und legt es auf den Bus, das
   `IR` liest es. Ergebnis: die Instruktion steht im `IR`, und die
   Control Unit weiß, welcher Opcode auszuführen ist. Danach wird der
   `PC` inkrementiert (bei Sprüngen später überschrieben).
2. **Execute-Phase**: je nach Opcode werden ein oder mehrere zusätzliche
   Speicherzugriffe (Operanden holen), ALU-Operationen und Register-
   Transfers ausgeführt. Am Ende dieser Phase ist die Instruktion
   vollständig abgearbeitet.

Dieser Zyklus wiederholt sich, solange die CPU läuft. Das ist der
gesamte Kern des Computerbetriebs — alles andere ist Ausschmückung.

## Mikrocode: eine Instruktion, viele Schritte

Was auf Programm-Ebene wie eine einzelne Instruktion aussieht (z. B.
`ADD 5`), zerfällt intern in mehrere kleinere Schritte, die alle über
den Bus koordiniert werden müssen. Diese Schritte heißen **Mikroschritte**,
und die Folge der Steuerwörter, die eine Instruktion realisieren, heißt
**Mikrocode**.

**Definition.** Ein *Steuerwort* ist eine Menge von Steuersignalen, die
gleichzeitig aktiv sind. Steuersignale sind typischerweise Signale der
Form `<Element>_OUT` (aktiviere Ausgang) oder `<Element>_IN` (aktiviere
Eingang), plus einige globale Aktionen (`ALU_ADD`, `CE` für „inkrementiere
den PC", `HLT` für „halt"). Ein Mikrocode-Eintrag für einen Opcode ist
eine geordnete Liste solcher Steuerwörter.

Das folgende Beispiel — direkt aus dem Kap1-Ursprungstext — zeigt, wie
eine `LDI`-Instruktion (*load immediate*, „lade den Datenteil der
Instruktion direkt in das Register `ACC`") in Mikroschritte zerfällt.
Ausgangspunkt ist ein kleines dreizeiliges Maschinenprogramm im Speicher:

```asm
0x00:  LDI 15        ; ACC := 15
0x01:  SUB 5         ; ACC := ACC - 5
0x02:  JNZ 0x01      ; springe zurueck zu 0x01 wenn ACC != 0
```

Für unsere 4-Bit-Beispiel-CPU ist eine Instruktion 8 Bit breit: 4 Bit
Opcode + 4 Bit Operand. Wir haben also Platz für maximal 16 verschiedene
Instruktionen. Auswahl aus der Opcode-Tabelle:

| Befehl | OP-Code (4 Bit) | Bedeutung |
|---|---|---|
| `NOP` | `0000` | keine Operation |
| `LDI` | `0001` | lade Datenteil in Register `ACC` |
| `SUB` | `0011` | subtrahiere Datenteil vom Register `ACC` |
| `JNZ` | `0111` | springe zur Adresse, wenn `ACC != 0` |

### Der Fetch-Zyklus, mikroskopisch

Nehmen wir an, der `PC` steht auf `0x00` und die erste Instruktion soll
geholt werden. In drei Mikroschritten passiert dann Folgendes (die
Nummern in Klammern beziehen sich auf die Bus-Verschaltungen):

**Mikroschritt 1** — Adresse auf den Bus:

```
Steuerwort: { PC_OUT, MAR_IN }
   ▶ PC schreibt seinen Wert (0x00) auf den Bus.
   ▶ Das Speicheradressregister (MAR) liest ihn.
```

**Mikroschritt 2** — RAM-Zelle in das Instruktionsregister:

```
Steuerwort: { MAR_OUT, RAM_READ, IR_IN }
   ▶ MAR treibt seine Adresse auf den Adressbus.
   ▶ Der Speicher legt die Zelle 0x00 (Wert: LDI 15 = 0x1F) auf den Datenbus.
   ▶ Das Instruktionsregister (IR) liest den Datenbus.
```

Am Ende dieses Mikroschritts steht die vollständige Instruktion im
`IR`. Die Control Unit dekodiert den Opcode (`LDI` = `0001`) und weiß
jetzt, welche Mikroschritte in der Execute-Phase folgen müssen.

### Der Execute-Zyklus, mikroskopisch

Für `LDI 15` besteht die Execute-Phase aus genau einem Mikroschritt:

**Mikroschritt 3** — Operand aus dem IR in den ACC:

```
Steuerwort: { IR_OUT_OPERAND, ACC_IN, CE, END }
   ▶ IR treibt den Operanden-Teil (0xF = 15) auf den Bus.
   ▶ ACC liest den Bus.
   ▶ CE inkrementiert den PC auf 0x01 (naechste Instruktion).
   ▶ END signalisiert der Control Unit: naechste Fetch-Phase.
```

Damit ist die `LDI`-Instruktion vollständig abgearbeitet in **drei
Mikroschritten** (2 für Fetch, 1 für Execute), definiert durch ihre
Folge von Steuerwörtern:

$$
\mathtt{LDI} = \bigl[\, \{\mathtt{PC\_OUT}, \mathtt{MAR\_IN}\},\; \{\mathtt{MAR\_OUT}, \mathtt{RAM\_READ}, \mathtt{IR\_IN}\},\; \{\mathtt{IR\_OUT\_OP}, \mathtt{ACC\_IN}, \mathtt{CE}, \mathtt{END}\} \,\bigr]
$$

Für andere Opcodes sehen die Mikrocode-Folgen anders aus — `ADD` z. B.
braucht zusätzlich einen Schritt, der die ALU auf `ADD` schaltet und
das Ergebnis vom ALU-Ausgang zurück ins `ACC` bringt. Aber das Muster
ist immer dasselbe: **eine Instruktion = eine kurze Folge von
Bus-Verschaltungen**.

### Mikrocode als flexibler Vertrag

Weil die Mikroschritt-Folgen in einem *ROM* der Control Unit abgelegt
werden, lässt sich der Befehlssatz einer CPU relativ flexibel gestalten:
- Beim CPU-Entwurf werden die Mikrocode-Folgen einmal festgelegt.
- Durch andere Mikrocode-Tabellen kann man dasselbe Hardware-Layout auf
  einen anderen Befehlssatz umkonfigurieren.
- Einige CPUs (Intel, AMD) erlauben *Mikrocode-Updates* im Feld: der
  Hersteller kann Fehler in der Instruktionslogik nach der Auslieferung
  korrigieren, ohne den Chip zu tauschen.

In der Simulation der 4-Bit-CPU ist das Mikrocode-ROM als Python-Dict
sichtbar (z. B. in `01_CPU/src/cpu_sim/config_acc.py`) — man kann es
lesen und ändern, ohne den Rest der CPU-Logik zu berühren.

──────────◆──────────◆──────────◆──────────◆──────────

## Der Von-Neumann-Flaschenhals

Alle Datentransporte zwischen Speicher und CPU-Registern gehen durch
denselben Bus. Bei jedem Fetch-Zyklus muss die CPU also einen Bus-
Vorgang aufwenden, nur um die *nächste Instruktion* zu holen — bevor
sie überhaupt Rechendaten lesen kann. Dieser Umstand ist als
**Von-Neumann-Flaschenhals** bekannt (nach Backus 1978, der den Begriff
prägte).

Zwei Konsequenzen ziehen sich durch die gesamte Rechnerarchitektur
seit den 1960er Jahren:

1. **Register statt Speicher.** Jede CPU hat eine kleine Zahl sehr
   schneller Register, die Zwischenwerte ohne Bus-Zugriff halten. In
   unserer Simulation sind das `ACC`, `TMP`, `BX`; in einer x86-64-CPU
   sind es 16 Allzweckregister plus 32 SIMD-Register plus etliche
   Sonderregister.
2. **Cache-Hierarchien.** Zwischen CPU und RAM sitzt eine mehrstufige
   Hierarchie kleinerer, schnellerer Speicher (L1/L2/L3-Cache). Ein
   heutiger Cache-Hit auf L1 ist etwa 100× schneller als ein RAM-Zugriff.
   Der Cache ist konzeptionell immer noch RAM — er hängt am selben
   Adressraum — aber physisch näher an den Rechenwerken.

Auf unserer 4-Bit-Simulation gibt es keinen Cache; wir sehen den
Flaschenhals in Reinform: pro Instruktion sind mehrere Bus-Zugriffe
nötig, jeder davon ein sequenzieller Takt.

──────────◆──────────◆──────────◆──────────◆──────────

## Der Bogen zurück — was man in der Simulation davon sieht

Fast alles, was dieser Deep Dive beschreibt, ist in
`01_CPU/src/cpu_sim.py` direkt erkennbar. Die Übersetzung:

| Kapitel 01 (Simulation) | Von-Neumann-Konzept |
|---|---|
| `class CPU` | die gesamte Architektur (fünf Bausteine + Bus) |
| `class RAM` | der gemeinsame Speicher für Programm und Daten |
| `class ProgramCounter` | der `PC` (Adresse der nächsten Instruktion) |
| `class InstructionRegister` | das `IR` |
| `class ALU` | die arithmetisch-logische Einheit |
| `MICROCODE = { … }` in der Config | der Mikrocode-ROM |
| Der Live-Log „Schritt X: aktive Signale = {…}" | das aktuelle Steuerwort |
| Instruktions-Tabelle im UI | die aktuell dekodierte Instruktion |

Wer der Simulation zusieht, wie sie durch die `LDI 3; ADD 4; STA 5; …`-
Sequenz läuft, sieht *genau* die drei bis fünf Mikroschritte pro
Instruktion, die dieser Deep Dive beschreibt: Fetch (2 Schritte),
Operanden-Ladung (falls nötig), ALU-Operation (falls nötig), Ergebnis-
Schreiben. Das Modell ist bewusst ohne Cache und ohne Pipeline, damit
der Zwei-Phasen-Zyklus in seiner reinen Form zu erkennen ist.

Und der letzte Bogen: **Von-Neumann skaliert.** Ein moderner CPU-Kern
ist von aussen betrachtet immer noch eine Von-Neumann-Maschine: sie
liest Instruktionen aus dem Speicher, sie hat Register, sie hat eine
ALU. Was hinzugekommen ist — Pipelining, Out-of-Order-Execution,
Cache-Hierarchien, spekulative Ausführung, Multicore — sind alles
*Optimierungen* der gleichen Grundstruktur, keine Ablösungen. Der
nächste Deep Dive [`moderne_prozessoren.md`](moderne_prozessoren.md)
geht diesen Skalierungspfad Schritt für Schritt durch.

──────────◆──────────◆──────────◆──────────◆──────────

## Weiterführende Lektüre

- **von Neumann, J. (1945).** *First Draft of a Report on the EDVAC.*
  Moore School of Electrical Engineering, University of Pennsylvania.
  Das ursprüngliche Manifest der Architektur. Trotz seiner 80 Jahre
  überraschend gut lesbar; das Konzept „Programm und Daten im selben
  Speicher" wird in Abschnitt 4 geradezu beiläufig eingeführt.
- **Backus, J. (1978).** *Can Programming Be Liberated from the von
  Neumann Style? A Functional Style and Its Algebra of Programs.*
  Communications of the ACM, 21(8), 613–641. Der Turing-Award-Vortrag,
  in dem der Begriff „Von-Neumann-Flaschenhals" geprägt wurde.
- **Schiffmann, W., & Schmitz, R. (2002).** *Technische Informatik 2 —
  Grundlagen der Computertechnik* (5. Aufl.). Springer.
  Fortsetzung des in [`schaltnetze.md`](schaltnetze.md) genannten
  Buchs; behandelt Steuerwerk, Mikroprogrammierung und Instruktions-
  Sätze im Detail.
- **Patterson, D., & Hennessy, J. (2020).** *Computer Organization and
  Design* (6th ed.). Morgan Kaufmann. Kap. 4 („The Processor") ist eine
  ausführliche Beschreibung des Fetch/Decode/Execute-Zyklus mit
  MIPS-Beispielen.
- **Malvino, A. P., & Brown, J. A. (1993).** *Digital Computer
  Electronics* (3rd ed.). McGraw-Hill. Enthält das *SAP-1* (Simple As
  Possible), das direkte Vorbild für die 4-Bit-CPU-Simulation dieses
  Buchs.

*→ zurück zum Kapitel-README: [`01_CPU/README.md`](../01_CPU/README.md)*
