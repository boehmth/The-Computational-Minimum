# Moderne Prozessoren — vom SAP-1 zum GPU-Cluster

*Deep Dive für Kapitel [`01_CPU`](../01_CPU/README.md) und [`05_GPU`](../05_GPU/README.md).
Nachdem die vorigen Deep Dives die Grundzüge der Von-Neumann-Maschine
etabliert haben, geht dieser Text den Skalierungspfad ab: welche
Optimierungen wurden in den letzten 60 Jahren auf die Grundstruktur
aufgesetzt, und warum kann man mit fast derselben Basis am Ende trotzdem
GPT-3 auf 10 000 GPUs trainieren?*

Die Wortbreite der 4-Bit-CPU aus Kapitel 01 entspricht dem historischen
Startpunkt der Mikroprozessor-Ära: dem **Intel 4004** von 1971. Zwei
Jahrzehnte später waren 32 Bit Standard, seit den 2000er Jahren dominieren
64-Bit-Systeme. Aber Wortbreite ist nur einer von mehreren Skalierungs-
Hebeln. Dieser Deep Dive nimmt die drei wichtigsten unter die Lupe:
**Pipelining**, **parallele Instruktionsströme** (Flynn-Klassifikation),
und die **exponentielle Zunahme der Transistorzahl** (Mooresches Gesetz).

──────────◆──────────◆──────────◆──────────◆──────────

## Wortbreite und Adressraum

Die **Wortbreite** einer CPU gibt an, wie viele Bit sie in einer einzigen
ALU-Operation oder einem einzigen Speichertransport verarbeiten kann.
Verdoppelt man sie, verdoppelt sich (bei entsprechender Software) die
verarbeitete Datenmenge pro Zyklus.

Zwei praktische Konsequenzen:

- **Direkte Verarbeitung großer Zahlen.** Für 64-Bit-Werte auf einer
  32-Bit-CPU braucht man zwei ALU-Operationen und Übertrags-Bookkeeping;
  auf einer 64-Bit-CPU eine. Bei Fließkomma-Multiplikationen — der Kern
  jedes neuronalen Netzes — macht das einen Faktor 2 aus.
- **Adressraum.** Ein 32-Bit-Adressbus kann höchstens $2^{32} = 4$ GByte
  RAM ansprechen. Ab 4 GByte hat man ein Problem — genau der Grund,
  warum ab ca. 2005 der Wechsel zu 64-Bit-Systemen einsetzte
  (Server zuerst, Consumer-PCs bis ca. 2010). Ein 64-Bit-Adressbus
  könnte theoretisch $2^{64} = 16$ Exabyte adressieren, mehr als jede
  praktische Maschine je hat.

Für unsere 4-Bit-CPU ist der Adressraum $2^4 = 16$ Zellen. Das ist der
Grund, warum das Perceptron in Kap. 04 in *genau* 16 Instruktionen
passen muss — größer geht nicht.

──────────◆──────────◆──────────◆──────────◆──────────

## Pipelining — mehrere Instruktionen gleichzeitig

Die klassische Zwei-Phasen-Ausführung (Fetch → Execute, siehe
[`von_neumann.md`](von_neumann.md)) ist konzeptionell klar, aber
verschwenderisch: während die Execute-Einheit arbeitet, liegt die
Fetch-Einheit still — und umgekehrt.

Die Idee des **Pipelinings** ist, die Instruktionsverarbeitung in
mehrere unabhängige *Stufen* zu zerlegen und dann jede Stufe mit einer
*anderen* Instruktion zu füttern, wie an einem Fließband:

```
Takt:          1     2     3     4     5     6
Stufe 1 (Fetch): I1   I2   I3   I4   I5   I6
Stufe 2 (Decode):     I1   I2   I3   I4   I5
Stufe 3 (Execute):         I1   I2   I3   I4
Stufe 4 (Write-Back):           I1   I2   I3
```

Am Anfang muss die Pipeline erst „gefüllt" werden (in obigem Beispiel
$k = 4$ Takte lang), aber danach wird pro Takt **eine** komplette
Instruktion fertig — statt einer alle $k$ Takte.

### Speed-up mathematisch

Für eine Pipeline mit $k$ Stufen und $n$ Instruktionen ergibt sich die
Ausführungszeit zu $k + (n-1)$ Takten (statt $n \cdot k$ ohne
Pipelining). Der **Speed-up** ist

$$
S = \frac{n \cdot k}{k + (n-1)}
$$

Für lange Instruktionsfolgen ($n \gg k$) nähert sich $S$ dem Wert $k$:
eine Pipeline mit $k$ Stufen ist im Idealfall $k$-mal so schnell.

Moderne CPUs haben 14 bis 20 Pipeline-Stufen (Intel Core i7: 14,
AMD Zen 3: ca. 19). Der praktische Speed-up liegt allerdings deutlich
unter $k$, weil Verzweigungen (`JMP`, `JZ`, …) die Pipeline **leeren**:
sobald die CPU nicht sicher weiß, welche Instruktion nach einem Sprung
folgt, muss sie warten oder spekulieren. Die **Sprungvorhersage**
(*branch prediction*) ist ein ganzer Forschungszweig für sich.

### Warum unsere Simulation kein Pipelining hat

Die 4-Bit-CPU aus Kap. 01 arbeitet bewusst *nicht* mit Pipelining — sie
zeigt den Zwei-Phasen-Zyklus in seiner reinen Form. Für die didaktische
Klarheit ist das ein bewusster Verzicht: sobald Pipelining ins Spiel
kommt, überschneiden sich die Mikroschritte mehrerer Instruktionen, und
der Zusammenhang „ein Steuerwort pro Takt" ist nicht mehr direkt zu
beobachten.

──────────◆──────────◆──────────◆──────────◆──────────

## Flynn-Klassifikation: eine Instruktion, viele Daten

Michael Flynn (1966) hat Rechnerarchitekturen nach der Anzahl der
gleichzeitigen **Instruktionsströme** und **Datenströme** klassifiziert.
Vier Klassen ergeben sich:

| Klasse | Bedeutung | Beispiel |
|---|---|---|
| **SISD** | Single Instruction, Single Data | Klassische Einkern-CPU (Intel 4004, unser 4-Bit-Simulator) |
| **SIMD** | Single Instruction, Multiple Data | Vektor-Prozessoren, SIMD-Erweiterungen in modernen CPUs (SSE, AVX), *GPU-Kerne* |
| **MISD** | Multiple Instruction, Single Data | Selten in reiner Form; einige spezielle Fehlertoleranz-Architekturen |
| **MIMD** | Multiple Instruction, Multiple Data | Multicore-CPUs, verteilte Cluster |

Für unser Buch sind vor allem SISD und SIMD wichtig. Die Grundidee:

- **SISD:** eine CPU führt Instruktionen nacheinander aus, auf einem
  Datenstrom. Das ist der einfache, klare Fall.
- **SIMD:** eine CPU führt *eine* Instruktion aus, aber sie wirkt
  gleichzeitig auf *viele* parallele Datenelemente. Wenn man z. B. zwei
  Vektoren mit 32 Elementen addieren möchte, braucht eine SISD-CPU 32
  aufeinanderfolgende ADD-Instruktionen, eine SIMD-CPU eine einzige.

Historisch begann SIMD in den 1970ern mit Vektor-Supercomputern (Cray-1,
1976). Heute steckt SIMD *in jedem* modernen Prozessor: Intels
**MMX**-Erweiterung (1996) führte 64-Bit-SIMD-Register ein, SSE (1999)
und AVX (2008/2011) erweiterten das auf 128 bzw. 256 Bit, AVX-512
(2016) auf 512 Bit — genug für 16 gleichzeitige 32-Bit-Fließkomma-
Multiplikationen.

### SIMD und GPUs

Der eigentliche SIMD-Champion ist aber nicht die CPU, sondern die
**GPU**. NVIDIAs CUDA-Modell heißt intern *Single Instruction, Multiple
Threads* (SIMT) — 32 Threads (ein *Warp*) führen gemeinsam dieselbe
Instruktion aus, jeder auf seinem eigenen Datenpunkt. Wenn 10 000
solcher Threads gleichzeitig laufen, hat man effektiv eine
10 000-fache SIMD-Maschine.

Genau das ist der Grund, warum GPUs für Deep Learning geradezu wie
gemacht sind: die Grundoperation eines neuronalen Netzes,
$y_j = \sigma\left(\sum_i w_{ji} x_i + b_j\right)$, ist für jedes $j$
unabhängig — dieselbe Instruktion, unterschiedliche Daten. SIMD-Ausführung
skaliert hier praktisch linear.

──────────◆──────────◆──────────◆──────────◆──────────

## Beispiel: SIMD als PMADDWD-Instruktion

Ein konkretes Beispiel aus Intels MMX-Befehlssatz: die Instruktion
`PMADDWD` (*Packed Multiply and Add Words to Doublewords*). Sie multipliziert
paarweise vier 16-Bit-Werte aus zwei Registern und addiert je zwei der
Ergebnisse:

```
Register A:  [a1 | a2 | a3 | a4]   (vier 16-Bit-Werte)
Register B:  [b1 | b2 | b3 | b4]

PMADDWD:
   c1 = a1*b1 + a2*b2
   c2 = a3*b3 + a4*b4

Register C:  [c1 | c2]              (zwei 32-Bit-Werte)
```

**Eine einzige Instruktion**, aber vier Multiplikationen und zwei
Additionen. Ein solcher Befehl ist besonders wertvoll für
Skalarprodukte — genau die Operation, die im Kern jeder
Matrix-Multiplikation und damit jedes MLP-Forward-Passes steht. Aus
CPU-Sicht ist das die Vorstufe zu dem, was eine GPU im Massenformat tut:
statt 4 paralleler MUL-Operationen macht ein GPU-Warp 32, und aus 32
Warps pro Streaming Multiprocessor werden auf einer H100 dann Tausende
gleichzeitiger Operationen.

──────────◆──────────◆──────────◆──────────◆──────────

## Cache-Hierarchien — den Flaschenhals umgehen

Der [`von_neumann.md`](von_neumann.md)-Deep Dive hat bereits den
**Von-Neumann-Flaschenhals** eingeführt: jeder Speicherzugriff braucht
Bus-Bandbreite. Auf realer Hardware wurde dieser Engpass ab den 1960er
Jahren durch **mehrstufige Cache-Hierarchien** entschärft. Die Idee:

- Register (im Kern der CPU): Zugriff in <1 Takt, aber winzig
- L1-Cache: 4–8 Takte, 32–64 KB, direkt am Kern
- L2-Cache: 12–20 Takte, 256 KB – 1 MB, pro Kern oder Kern-Cluster
- L3-Cache: 30–60 Takte, 8–64 MB, geteilt zwischen allen Kernen
- Hauptspeicher (RAM): 200–400 Takte, 8 GB und mehr, alle Kerne teilen sich

Das Prinzip ist einfach: jede Ebene ist etwa 10-mal größer, aber auch
etwa 10-mal langsamer als die vorherige. Wenn die CPU eine Speicherzelle
liest, wird sie automatisch in die schnelleren Ebenen kopiert; beim
nächsten Zugriff (falls in derselben Nachbarschaft) kommt sie aus dem
Cache.

Die Effektivität hängt daran, dass Programme meist **Lokalität** haben —
sie greifen auf benachbarte Adressen zu (räumliche Lokalität) oder
dieselben Adressen mehrfach (zeitliche Lokalität). Bei neuronalen Netzen
ist das der Grund, warum die Reihenfolge der Matrix-Multiplikation eine
Rolle spielt: cache-freundliche Blockung („tiling") kann einen Faktor 10
im Durchsatz ausmachen. Genau das behandelt Kapitel 05 mit der
gekachelten GPU-MatMul.

Auf unserer 4-Bit-Simulation gibt es keinen Cache; der RAM ist der
einzige Speicher jenseits der Register. Das ist historisch akkurat:
der Intel 4004 hatte auch keinen Cache. Caches als Standardausstattung
kamen erst mit dem Motorola 68020 (1984) und Intel 80386 (1985).

──────────◆──────────◆──────────◆──────────◆──────────

## Mooresches Gesetz — 60 Jahre Verdopplung

**Gordon Moore** (Mitgründer von Intel) beobachtete 1965, dass sich die
Anzahl der Transistoren auf einem Chip alle ein bis zwei Jahre
verdoppelte. Diese Faustregel — bekannt als *Mooresches Gesetz* — hat
sich als bemerkenswert stabil erwiesen. Ein paar Zahlen zur Orientierung:

| Jahr | Prozessor | Transistoren |
|---|---|---|
| 1971 | Intel 4004 | 2 300 |
| 1978 | Intel 8086 | 29 000 |
| 1985 | Intel 386 | 275 000 |
| 1993 | Intel Pentium | 3,1 Mio. |
| 2000 | Intel Pentium 4 | 42 Mio. |
| 2011 | Intel Core i7 (Sandy Bridge) | 1,16 Mrd. |
| 2020 | Apple M1 | 16 Mrd. |
| 2024 | NVIDIA H100 | 80 Mrd. |

In Kombination mit Frequenzsteigerungen und Verbesserungen der
Mikroarchitektur führte das zu einer massiven Steigerung der
**Rechenleistung** (gemessen in FLOPS — *Floating Point Operations
Per Second*):

- **Konrad Zuse Z3** (1941): 2 FLOPS
- **Cray-1** (1976): 500 MFLOPS
- **Heute ein Consumer-PC**: 30–100 GFLOPS
- **NVIDIA H100 (Deep Learning)**: 1 000 TFLOPS = 1 PFLOPS (mit
  spezialisierten Tensor-Cores)

Das ist ein Sprung um mehr als 14 Größenordnungen in etwa 80 Jahren —
und die Kurve ist noch nicht flach.

### Was der Trend heute macht

Reine **Frequenzsteigerungen** kamen um 2005 zum Erliegen (das
sogenannte *„Power Wall"*: mehr Frequenz bedeutet quadratisch mehr
Stromverbrauch und Wärme). Die Antwort war der Sprung zu **Multicore**-
Architekturen: statt eines schnelleren Kerns baute man mehrere Kerne
gleicher Frequenz. Aktuelle Consumer-CPUs haben 8–24 Kerne, Server-CPUs
64 und mehr.

Parallel dazu haben sich **spezialisierte Beschleuniger** entwickelt —
GPUs, TPUs (Google), Trainium (AWS), MI300 (AMD). Sie folgen alle dem
SIMD-Prinzip in extremer Form: sehr viele einfache Rechenwerke, sehr
breite Speicheranbindung, minimale Kontrolllogik. Kapitel 05
`05_GPU/` behandelt diese Architekturklasse ausführlich.

──────────◆──────────◆──────────◆──────────◆──────────

## Der Bogen zurück — vom SAP-1 zur Trainings-Farm

Alles bisher Beschriebene ist auf denselben fünf Bausteinen aufgebaut,
die Kapitel 01 zeigt: Programm-Zähler, Register, ALU, Bus, Control Unit.
Die Optimierungen der letzten 60 Jahre lassen sich in einer knappen
Tabelle zusammenfassen:

| Wovon fügt man mehr hinzu | Wie es heißt |
|---|---|
| Mehr Bits pro Wort | 4 → 8 → 16 → 32 → 64 Bit |
| Mehr Instruktionen gleichzeitig | Pipelining (14+ Stufen) |
| Mehr Daten pro Instruktion | SIMD, MMX/SSE/AVX/AVX-512 |
| Mehr Kerne | Multicore, 2 → 8 → 64 → tausend (GPU) |
| Mehr Speicher-Ebenen | L1/L2/L3-Cache, HBM, NVMe |
| Mehr Rechner | Cluster, Cloud, Compute-Farmen |

Alle diese Skalierungshebel sind additiv, keine ersetzt die anderen.
Und in jeder Ebene bleibt das Kernprinzip erhalten: Register laden,
Rechnen, Ergebnis speichern.

Das ist die eigentliche Botschaft dieses Deep Dives: **die Grundstruktur
von 1945 hält bis heute**. Was sich verändert hat, ist nur die Zahl der
gleichzeitigen Instanzen. Ein GPU-Cluster mit 10 000 Karten und
Millionen paralleler Rechenwerke ist immer noch eine Ansammlung von
Von-Neumann-Maschinen, nur eben *sehr viele davon, sehr parallel, sehr
schnell*. Der Bogen von der 4-Bit-CPU aus Kapitel 01 zu den
GPT-Trainingsfarmen der Gegenwart ist eine 60-Jahre-Skalierungs-
Geschichte auf demselben mathematischen Fundament.

──────────◆──────────◆──────────◆──────────◆──────────

## Weiterführende Lektüre

- **Moore, G. E. (1965).** *Cramming more components onto integrated
  circuits.* Electronics, 38(8). Der originale Artikel, aus dem später
  „Mooresches Gesetz" wurde. Nur wenige Seiten lang, historisch
  faszinierend.
- **Flynn, M. J. (1966).** *Very high-speed computing systems.*
  Proceedings of the IEEE, 54(12), 1901–1909. Die ursprüngliche
  Klassifikation SISD/SIMD/MISD/MIMD.
- **Patterson, D., & Hennessy, J. (2019).** *Computer Architecture: A
  Quantitative Approach* (6th ed.). Morgan Kaufmann. Der ausführliche
  Bruder von *Computer Organization and Design*, mit detaillierten
  Kapiteln zu Pipelining, Cache-Hierarchien und SIMD/Vektor-
  Erweiterungen.
- **Hennessy, J., & Patterson, D. (2019).** *A New Golden Age for
  Computer Architecture.* Communications of the ACM, 62(2), 48–60.
  Der Turing-Award-Vortrag zur Ära domänen­spezifischer Beschleuniger —
  eine der besten kompakten Erklärungen, warum GPUs, TPUs und ähnliche
  Chips gerade die interessantesten Entwicklungen der aktuellen
  Rechnerarchitektur sind.
- **Wittenbrink, C. M., Kilgariff, E., & Prabhu, A. (2011).** *Fermi GF100
  GPU Architecture.* IEEE Micro, 31(2). Die technische Beschreibung
  einer der ersten für allgemeine Berechnungen ausgelegten NVIDIA-GPUs.
- Lighterra. (2016 ff.). *Modern Microprocessors — A 90-Minute Guide.*
  <http://www.lighterra.com/papers/modernmicroprocessors/>
  Eine bemerkenswert lesbare Web-Einführung, die praktisch alle Themen
  dieses Deep Dives behandelt, aber mit dem Fokus auf konkrete moderne
  Chips.

*→ zurück zum Kapitel-README: [`01_CPU/README.md`](../01_CPU/README.md)
oder weiter zum Nachfolge-Kapitel: [`05_GPU/README.md`](../05_GPU/README.md)*
