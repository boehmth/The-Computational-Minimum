# Schaltnetze und Schaltwerke — die Bausteine unter der CPU

*Deep Dive für Kapitel [`01_CPU`](../01_CPU/). Wer den Wow-Moment der
Simulation sehen will, bleibt beim README; wer verstehen will, warum
ein einzelner Bus-Draht nicht in Rauch aufgeht, ist hier richtig.*

Auf Hardware-Ebene wird die verarbeitete Information als Bitfolge —
also als Folge von Nullen und Einsen — dargestellt. Das gesamte
Verhalten eines Computers lässt sich mit zwei Bausteinklassen
vollständig beschreiben:

- **Schaltnetzen** (kombinatorischen Gattern ohne Zustand) und
- **Schaltwerken** (getakteten Schaltnetzen *mit* Zustand).

Dieser Abschnitt gibt einen geordneten Überblick über die Bausteine,
mit denen ein Digitalrechner nach Von-Neumann-Architektur aufgebaut
wird. Wir beginnen bei den drei booleschen Grundoperationen und arbeiten
uns bis zum Bus-Konzept vor — genau das Bus-Konzept, das in der
Simulation der 4-Bit-CPU (Kapitel 01) sichtbar wird.

──────────◆──────────◆──────────◆──────────◆──────────

## Boolesche Grundoperationen

Verknüpfungen von Bits werden mit Hilfe **logischer Operationen**
realisiert. Aus einer Kombination der drei Grundoperationen UND, ODER
und NICHT lassen sich alle notwendigen arithmetischen und logischen
Funktionen konstruieren — eine Beobachtung, die auf George Boole (1854)
zurückgeht und die Grundlage der gesamten Digitallogik ist.

### Definition: die drei Grundoperationen

**Negation (NICHT, $\neg$)** ist unär und berechnet das Komplement:

| $a$ | $\neg a$ |
|:-:|:-:|
| 0 | 1 |
| 1 | 0 |

**Konjunktion (UND, $\wedge$)** ist binär und ergibt genau dann `1`,
wenn *beide* Eingaben `1` sind:

| $a$ | $b$ | $a \wedge b$ |
|:-:|:-:|:-:|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

**Disjunktion (ODER, $\vee$)** ist binär und ergibt genau dann `0`,
wenn *beide* Eingaben `0` sind:

| $a$ | $b$ | $a \vee b$ |
|:-:|:-:|:-:|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 1 |

Elektronische Bauteile, die solche Verknüpfungen implementieren, heißen
**Gatter**. Zusammengeschaltete Gatter bilden ein **Schaltnetz**. Der
Übergang ist fließend: „Gatter" bezieht sich meist auf einzelne, wenige
Transistoren umfassende Bauteile, „Schaltnetz" auf ihre Komposition.

### Warum genau UND, ODER, NICHT?

Diese drei Operationen bilden eine *funktional vollständige* Basis: jede
boolesche Funktion $f: \{0,1\}^n \to \{0,1\}$ lässt sich aus ihnen
zusammensetzen. Beweis-Skizze: jede Wahrheitstabelle lässt sich in
**disjunktiver Normalform** darstellen — als ODER über alle
Konjunktionen (mit ggf. negierten Eingängen) der Zeilen, in denen die
Funktion `1` liefert. In Hardware kommt man tatsächlich mit *einer*
einzigen Operation aus (NAND oder NOR), aber die drei klassischen sind
lesbarer.

──────────◆──────────◆──────────◆──────────◆──────────

## Arithmetische Operationen: vom Bit zur Zahl

### Binär-Addition per Hand

Zwei mehrstellige Binärzahlen werden stellenweise addiert, mit einem
Übertrag zur nächsthöheren Stelle. Beispiel: $2 + 3 = 5$ in drei
Stellen:

```
    010
  + 011
  -----
  ü  1        (Übertrag von Stelle 0 nach Stelle 1)
  s 101       (Summe: binär 5)
```

Das Muster ist mechanisch, wiederholt sich Stelle für Stelle und lässt
sich damit direkt in Hardware gießen.

### Halbaddierer (HADD)

Ein **Halbaddierer** liefert für zwei Eingangs-Bits $a, b$ eine
zweistellige Ausgabe: die Summe $s$ und den Übertrag $\ddot{u}$.

| $a$ | $b$ | $s$ | $\ddot{u}$ |
|:-:|:-:|:-:|:-:|
| 0 | 0 | 0 | 0 |
| 1 | 0 | 1 | 0 |
| 0 | 1 | 1 | 0 |
| 1 | 1 | 0 | 1 |

Aus der Tabelle liest man ab:

$$
s = a \oplus b, \qquad \ddot{u} = a \wedge b
$$

wobei $\oplus$ das exklusive ODER (XOR) bezeichnet. XOR wiederum lässt
sich aus UND/ODER/NICHT zusammensetzen: $a \oplus b = (a \wedge \neg b)
\vee (\neg a \wedge b)$.

### Volladdierer (VADD)

Der Halbaddierer reicht nur für die niedrigste Stelle. Ab der zweiten
Stelle muss der Übertrag der Vorstelle mit einfließen. Ein
**Volladdierer** hat deshalb *drei* Eingänge — $a, b, c_{\text{in}}$ —
und liefert Summe $s$ und Übertrag $c_{\text{out}}$. Er lässt sich aus
zwei Halbaddierern und einem ODER zusammenbauen:

```
      a ──┐
          ├─ HADD ─┬─── s1 ──┐
      b ──┘        │         ├─ HADD ─── s
                   └── ü1    │
                             └─ c_in
      ü_out = ü1  ∨  ü2
```

### Vom Volladdierer zum Rechenwerk

Ein **Rechenwerk** (die *Arithmetisch-Logische Einheit*, ALU) für
$n$-stellige Binärzahlen entsteht durch Kaskadierung: der Übertrag jedes
Volladdierers wird zum Übertrags-Eingang des nächsten. Dieser Aufbau
heißt **Ripple-Carry-Addierer** — einfach, aber langsam, weil der
Übertrag nacheinander durch alle Stellen "rieselt". Moderne CPUs
verwenden **Carry-Lookahead**-Varianten, die den Übertrag über
Präfix-Berechnung parallelisieren; im Kern basiert das aber immer noch
auf denselben UND/ODER-Operationen.

Da sich **alle vier Grundrechenarten** auf die Addition zurückführen
lassen (Subtraktion via Zweierkomplement, Multiplikation via wiederholte
Addition, Division via wiederholte Subtraktion), ist das Addierwerk das
Herzstück jeder ALU. Auch Vergleichsoperationen laufen darauf:
$a = b \iff a - b = 0$, also ein Blick auf die ALU-Ausgabe genügt. Der
`JZ`-Opcode in unserer 4-Bit-CPU (`Jump if Zero`) macht genau das.

──────────◆──────────◆──────────◆──────────◆──────────

## Bistabile Kippstufen: das erste Bit Gedächtnis

Reine Schaltnetze haben keinen Zustand — die Ausgabe hängt nur von der
aktuellen Eingabe ab. Für Register, Zähler und Speicher brauchen wir
Bauteile, die *ein Bit speichern* können, also einen früheren Zustand
über die Zeit erhalten. Solche Schaltungen heißen **Flip-Flops** oder
**bistabile Kippstufen**: sie haben genau zwei stabile Zustände (0 und 1)
und speichern denjenigen, in den sie zuletzt gesetzt wurden.

### RS-Flip-Flop (die Urform)

Das einfachste Flip-Flop hat zwei Eingänge — **R** (Reset) und **S**
(Set) — und zwei Ausgänge — **Q** und $\overline{Q}$, die immer
entgegengesetzt sind. Es wird aus zwei rückgekoppelten Gattern gebaut,
typischerweise zwei NANDs:

```
    S ──┤NAND├─── Q
         │        │
         └────────┼──┐
                  │  │
    R ──┤NAND├────┘  │
         │           │
         └───────────┘  → ¬Q
```

Verhalten:

- $S = 1, R = 0$: Ausgang $Q$ wird auf 1 *gesetzt*.
- $S = 0, R = 1$: Ausgang $Q$ wird auf 0 *zurückgesetzt*.
- $S = 0, R = 0$: Ausgang bleibt in seinem letzten Zustand — **das ist
  die Speicher-Eigenschaft**.
- $S = 1, R = 1$: **verboten** (widersprüchlich, kann zu instabilem
  Verhalten führen).

### JK-Flip-Flop (die praktische Variante)

Ein JK-Flip-Flop ist eine Erweiterung des RS-Flip-Flops mit einem
zusätzlichen **Takt-Eingang** $C$ (engl. *clock*) und ohne verbotenen
Zustand. Es akzeptiert seine Eingaben nur bei einer Taktflanke, was den
Betrieb *synchron* macht: alle Zustandswechsel im ganzen Prozessor
passieren gleichzeitig, gesteuert durch das Taktsignal.

Historische Randbemerkung: die Buchstaben *J* und *K* wurden vom
Erfinder Jack Kilby (späterer Nobelpreisträger für die Erfindung des
integrierten Schaltkreises) einfach als beliebige Bezeichner gewählt,
um das Flip-Flop von anderen Varianten zu unterscheiden.

### Vom Flip-Flop zum Register

Ein **Register** speichert nicht ein einzelnes Bit, sondern ein ganzes
Wort — bei uns 4 Bit, bei einem modernen x86-64-Kern 64 Bit. Man baut es
schlicht aus $n$ parallel geschalteten Flip-Flops, die alle denselben
Takt bekommen. In der Simulation der 4-Bit-CPU (`01_CPU/src/cpu_sim.py`)
sind das die Objekte `ACC`, `TMP`, `PC`, `IR` und so weiter: jedes von
ihnen ist konzeptionell ein Bündel aus vier getakteten Flip-Flops.

### Zähler als synchrone Schaltwerke

Kaskadiert man mehrere JK-Flip-Flops und verschaltet ihre Ausgänge
geeignet auf die Eingänge des jeweils folgenden Flip-Flops, erhält man
einen **Zähler**. Ein synchroner 2-Bit-Zähler zum Beispiel durchläuft
mit jedem Takt die Folge $00 \to 01 \to 10 \to 11 \to 00 \to \dots$ Der
**Programmzähler** (`PC`) einer CPU ist die skalierte Version davon: ein
Register, das bei jedem Takt seinen Wert entweder um eins erhöht (nach
einer normalen Instruktion) oder auf eine neue Adresse springt (nach
einem `JMP` oder `JZ`).

Flip-Flops und Zähler zusammen sind alles, was man braucht, um eine
Folge von Operationen durch ein Schaltwerk *steuern* zu lassen — genau
das, was in der Control Unit einer CPU passiert.

──────────◆──────────◆──────────◆──────────◆──────────

## Tri-State-Gatter und Bus-Konstruktion

Auch wenn alle notwendigen Schaltungen mit UND/ODER/NICHT
konstruierbar sind, fehlt uns für einen echten Rechner noch ein
Baustein: ein Weg, **mehrere Ausgänge parallel auf einer gemeinsamen
Leitung zu verschalten**, ohne Kurzschluss.

Genau das leisten **Tri-State-Gatter**. Sie haben nicht zwei, sondern
drei Zustände: logisch `0`, logisch `1`, und *hochohmig* $Z$. Der
dritte Zustand bedeutet, dass der Ausgang effektiv von der Leitung
*abgekoppelt* ist — er beeinflusst andere daran hängende Ausgänge nicht.

Ein Tri-State-Gatter hat zwei Eingänge — einen Daten-Eingang $a$ und
einen Aktivierungs-Eingang $\text{select}$ — und einen Ausgang $c$:

| $a$ | $\text{select}$ | $c$ |
|:-:|:-:|:-:|
| 0 | 0 | 0 |
| 1 | 0 | 1 |
| 0 | 1 | $Z$ |
| 1 | 1 | $Z$ |

*(Konvention: hier ist $\text{select}=0$ „durchlassen", $\text{select}=1$
„sperren". Andere Bücher wählen die Polarität umgekehrt — das ist reine
Konvention.)*

### Warum das den Bus möglich macht

Ein **Bus** ist eine gemeinsame Sammelleitung, die viele Bausteine
verbindet: Register, ALU, Speicher, I/O-Port. Ohne Tri-State-Gatter
würde jeder daran angeschlossene Ausgang permanent seinen Wert auf die
Leitung drücken; sobald zwei Ausgänge unterschiedliche Werte hätten,
gäbe es einen elektrischen Konflikt — bei realen Chips einen Kurzschluss,
in unserer Simulation einen `RuntimeError: Bus-Konflikt`.

Mit Tri-State-Gattern hingegen kann die Control Unit **genau einen
Sender** aktivieren (dessen $\text{select}$ auf „durchlassen" schalten)
und alle anderen sperren. Das Signal des Senders liegt sauber auf dem
Bus, alle Empfänger, deren `_IN`-Signal die Control Unit gerade setzt,
lesen ihn. Genau dieses Muster — *ein Sender, viele Empfänger, ein
Steuerwort pro Takt* — ist das, was man in der Simulation live sieht:

```
Steuerwort: {ACC_OUT, ALU_ADD, IR_IN}
              ↑ genau ein OUT-Signal
              ↑ das ALU_ADD ist eine "Aktion", nicht IN/OUT
              ↑ das IR_IN sagt "IR liest den Bus"
```

Auf realer Hardware sind Tri-State-Gatter meist als Puffer in die
Register selbst integriert (bei modernen CPUs sogar als Teil der
Register-File-Ausleseeinheit); in der Simulation sind sie als
`set_gates(...)`-Aufrufe explizit sichtbar.

──────────◆──────────◆──────────◆──────────◆──────────

## Der Bogen zurück — was man in der Simulation davon sieht

Alles bisher Beschriebene ist in der 4-Bit-CPU-Simulation aus Kapitel 01
*direkt beobachtbar*, nur eine Abstraktionsebene höher: statt Gattern
sehen wir Register, statt Volladdierer-Kaskaden eine `ALU`-Klasse, statt
elektrischer Tri-State-Puffer die drei-schleifige Bus-Logik
(`set_gates → write_bus → read_bus`). Die Übersetzung ist:

| Kapitel 01 (Simulation) | Hardware (dieser Deep Dive) |
|---|---|
| `class Register` | ~$n$ Flip-Flops im Gleichtakt |
| `class ALU` mit `add()` | Kaskadierter Volladdierer + Steuerlogik |
| `class ProgramCounter` mit `inc()` | Synchroner Zähler aus $\log_2(\text{RAM-Größe})$ Flip-Flops |
| `bus.set_gates({...})` | Aktivierungssignale an den Tri-State-Puffern aller Register |
| `RuntimeError: Bus-Konflikt` | Elektrischer Kurzschluss auf der realen Leitung |
| Mikrocode-ROM in der `ControlUnit` | Ein echtes ROM auf dem Chip mit vor-verdrahteten Steuerwörtern |

Wenn man das einmal gesehen hat, verlieren zwei Aussagen des Buchs
ihre Undurchsichtigkeit:

1. **„Alles in einer CPU lässt sich auf UND/ODER/NICHT zurückführen."**
   Ja — buchstäblich, über die Kaskade Halbaddierer → Volladdierer →
   ALU → Mikrocode-ROM → Kontroll-Zustandsautomat.
2. **„Der Von-Neumann-Flaschenhals liegt am Bus."**
   Ja — weil der Bus per Konstruktion nur einen Sender pro Takt zulässt,
   und alle Daten zwischen Registern und Speicher da hindurch müssen.
   Alles was moderne CPUs an Cache-Hierarchie und mehreren Bussen tun,
   ist letztlich ein Weg, den Flaschenhals zu erweitern.

Der Bogen zu den weiteren Kapiteln wird damit sehr direkt: das GPU-
Kapitel (05) diskutiert, was passiert, wenn man **viele parallele
Rechenwerke** an einen gemeinsamen (aber sehr breiten) Speicher hängt.
Das Perceptron-Kapitel (04) zeigt, dass ein einfaches Neuron —
`w·x + b` — auf dieser Hardware in genau 16 Instruktionen läuft. Der
Compiler (03) übersetzt Hochsprachen in dieselben ALU-Operationen. Und
das Mini-OS (02) baut auf denselben Registern das Konzept eines
Prozesses. Alles skaliert am Ende dieselbe Hardware-Grundstruktur.

──────────◆──────────◆──────────◆──────────◆──────────

## Weiterführende Lektüre

- **Schiffmann, W., & Schmitz, R. (2003).** *Technische Informatik 1 —
  Grundlagen der digitalen Elektronik* (5. Aufl.). Springer.
  [DOI: 10.1007/978-3-642-97369-7](https://link.springer.com/book/10.1007/978-3-642-97369-7)
  Das deutschsprachige Standardwerk zur Digitallogik: Gatter,
  Halb-/Volladdierer, Flip-Flop-Varianten, synchrone Schaltwerke,
  Tri-State und Bus-Konstruktion sind darin viel ausführlicher
  hergeleitet, als es dieser Deep Dive zulassen kann. *Persönliche
  Anmerkung des Autors: Prof. Schiffmann war einer meiner beiden Prüfer
  für den Master-Abschluss — insofern ist das hier nicht nur eine
  Literaturangabe, sondern auch eine kleine Verneigung.*
- Patterson, D., & Hennessy, J. (2020). *Computer Organization and
  Design* (6th ed.). Morgan Kaufmann. Kap. 3 (Arithmetik) und Kap. 4
  (Datapath) enthalten die kanonische Darstellung mit CarryLookahead-
  Addierern und Pipeline-Details.
- Nisan, S., & Schocken, S. (2008). *The Elements of Computing
  Systems*. MIT Press. Kap. 1–3: baut alles auf NAND-Gattern auf und
  entwickelt daraus eine komplette CPU. Genau die Umkehr-Perspektive
  dieses Deep Dive.
- Mano, M. M., & Ciletti, M. (2018). *Digital Design* (6th ed.).
  Pearson. Der Standard-Lehrtext zur Digitallogik (englischsprachig)
  mit einer detaillierten Behandlung von Flip-Flop-Varianten und
  synchronen Schaltwerken.

*→ zurück zum Kapitel-README: [`01_CPU/README.md`](../01_CPU/README.md)*
