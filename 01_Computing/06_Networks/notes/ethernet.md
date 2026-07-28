# Von ALOHA zu Ethernet zum Internet — der Weg der Skalierung

Diese Datei ist der Nachfolge-Ausblick für Kapitel 5 (`aloha.py`). Sie
zeigt, wie aus dem 18-Prozent-Kanal von 1970 in wenigen Schritten das
Netzwerk wurde, auf dem heute alles läuft — inklusive der Rechner, auf
denen die Sprachmodelle aus Teil 2 und Teil 3 trainiert werden.

## Die Kette der Verbesserungen

### 1. ALOHA (Abramson, 1970–71) — der Ur-Ahn

- Kontext: sieben Rechner auf verschiedenen Hawaii-Inseln, keine
  vermieteten Standleitungen, nur ein UHF-Funkkanal.
- Regel: „senden, wenn du willst; bei Kollision: zufällig warten und
  erneut senden."
- **Maximale Kanalauslastung: 18,4 %** (bewiesen: $S = G e^{-2G}$, Max bei
  $G = 0.5$).

Was wir in `test_aloha.py` reproduzieren.

### 2. Slotted ALOHA (Roberts, 1972) — die halbe Verdopplung

- Zusatzregel: Sendungen dürfen nur zum Beginn eines festen Zeitslots
  starten.
- **Maximale Kanalauslastung: 36,8 %** ($S = G e^{-G}$, Max bei $G = 1$).
- Die Verdopplung kommt daher, dass sich das „Gefährdungsintervall" für
  Kollisionen von *zwei Paketlängen* (Pure) auf *eine Paketlänge*
  (Slotted) halbiert.

Auch das steckt in `test_aloha.py`, direkt neben Pure ALOHA.

### 3. CSMA (Kleinrock & Tobagi, 1975) — vorher hören

- **Carrier Sense Multiple Access**: bevor du sendest, höre kurz zu, ob
  der Kanal frei ist. Klingt trivial, ist aber der entscheidende Sprung
  auf Kabelnetze, wo diese Detektion technisch möglich ist (bei Funk
  über weite Distanzen — Hawaii! — war das damals nicht praktikabel,
  Signal-Ausbreitungszeit zu lang).
- **Maximaler Durchsatz: 80–90 %**, wenn die Signal-Ausbreitungsdauer
  klein gegen die Paketdauer ist.

Konzeptioneller Kernpunkt: der Sender ist nicht mehr blind. Er hat eine
lokale Beobachtung des Kanals, bevor er handelt. Die Wahrscheinlichkeit
einer Kollision fällt drastisch.

### 4. CSMA/CD (Metcalfe & Boggs, 1973/1976) — Ethernet

- **Carrier Sense Multiple Access with Collision Detection**: höre nicht
  nur *vor* dem Senden, sondern auch *während*. Wenn dabei eine Kollision
  auftritt (deine gesendeten Bits kommen anders zurück, als du sie
  eingespeist hast), brich sofort ab und sende ein Jam-Signal, damit die
  andere Seite auch abbricht.
- **Backoff**: nach einer Kollision warte $k$ Slots, wobei $k$ zufällig
  aus $\{0, 1, \dots, 2^n - 1\}$ gezogen wird, mit $n$ = Zahl der bisher
  aufeinanderfolgenden Kollisionen. Der berühmte *binary exponential
  backoff* — mit dem Wissen, dass in Kollisions-Sturm-Situationen alle
  Sender sich statistisch entzerren müssen.
- Metcalfe hat sein System 1973 bei Xerox PARC gebaut, um die
  neuentwickelten Personal Computer (Alto) miteinander zu verbinden.
  Sein Doktor-Vater in Harvard hatte ihm gesagt: „Zeig, dass die
  ALOHA-Rechnungen mit deiner Änderung wirklich stimmen." Metcalfe
  zeigte es — und Ethernet war geboren.
- Erste Kommerzialisierung: 1980, IEEE 802.3 (1983).
- **Maximaler Durchsatz: 90 %+**, praktisch stabil bei sehr hohem
  Angebot.

Die Kernidee, mit der Metcalfe die 37 % von Slotted ALOHA
sprengt: **du siehst deine eigene Kollision und kannst aussteigen, bevor
du das ganze Paket verschwendest**.

### 5. Switched Ethernet (Kalpana, 1990) — Kollisionen werden abgeschafft

- Der Switch merkt sich, welcher Rechner an welchem Port hängt. Wenn
  Rechner A an Rechner B sendet, muss der Switch das Paket *nur* an
  Bs Port weiterleiten — nicht an alle Ports.
- **Kollisionen verschwinden fast völlig**, weil jeder Rechner seinen
  eigenen physischen Kanal zum Switch hat.
- Der ALOHA-Mechanismus lebt trotzdem weiter: für den Fall, dass
  Duplex-Kanäle nicht verfügbar sind (alte Hubs, Wireless).

### 6. WLAN 802.11 (1997) — ALOHA kehrt zurück

- Bei Funk ist Collision Detection wieder unmöglich (aus demselben
  Grund wie 1970 auf Hawaii). Deshalb: **CSMA/CA** — Collision Avoidance
  statt Detection. Vor dem Senden ein zufällig gewähltes Zeitfenster
  abwarten, damit sich die Kollisionswahrscheinlichkeit reduziert.
- Der ALOHA-Kern-Insight — probabilistischer Kanalzugriff, exponentielles
  Backoff — steckt bis heute in *jedem* WLAN-Chip.

### 7. TCP/IP darüber (1974, standardisiert 1983)

- Bis hierher ging es um den **physischen Kanal**: Kollisionen,
  Bitübertragung, Rahmen.
- **TCP/IP** legt darüber eine zweite Schicht: Adressierung (welcher
  Rechner spricht mit welchem?), Fragmentierung (grosse Nachrichten in
  Pakete zerlegen), Fehlerkorrektur (verlorene Pakete erneut senden),
  Reihenfolge-Wiederherstellung (Pakete kommen in falscher Reihenfolge
  an).
- Diese Trennung — *physischer Kanal* vs. *logisches Ende-zu-Ende-
  Protokoll* — ist die zweite grosse Idee der Netzwerkforschung. Sie
  erlaubt es, dass Ethernet-, WLAN-, LTE- und 5G-Kanäle unter demselben
  TCP/IP-Stack Platz finden.

### 8. Und was heute darauf läuft

- **10 000 GPUs synchronisieren sich** beim GPT-3-Training über
  InfiniBand oder Ethernet. Jeder AllReduce-Schritt sendet Gradienten
  über denselben Netzwerkstack — ALOHA + CSMA/CD + TCP/IP + darüber
  RDMA-Protokolle.
- **Ein API-Call an ChatGPT** ist HTTP(S) über TCP über IP über Ethernet
  über CSMA/CD über — im Kern — ein *Random-Access-Protokoll* dessen
  Grundprinzip 1970 auf Hawaii mit Blechkisten gebaut wurde.

## Was wir davon in unserem Kapitel simulieren

Nur den ersten Schritt: Pure und Slotted ALOHA. Bewusst.

Der Grund ist derselbe wie bei der 4-Bit-CPU in Kapitel 1: der *einfache
Fall* enthält bereits alle Grundideen, und Skalierung ist danach eine
*Verbesserung derselben Idee*, keine grundsätzlich neue Physik. Ein
CSMA/CD-Simulator wäre lehrreich, aber der Kernbegriff „probabilistischer
Zugriff auf ein geteiltes Medium mit exponentiellem Backoff bei
Kollisionen" ist mit ALOHA schon vollständig.

## Der Bogen zu Teil 2 und 3

Am Ende dieses Kapitels haben wir die klassische *Wie funktioniert ein
Computer*-Frage vollständig beantwortet: CPU, OS, Compiler, GPU,
Netzwerk. Wir können Rechner bauen, Programme schreiben, sie parallel
laufen lassen und über ein Kabel miteinander sprechen.

Was uns noch fehlt: ein Rechner kann jetzt Text **übertragen** —
aber er versteht ihn nicht. Kein einziger Byte, den wir hier gesendet
haben, wusste, ob er eine Frage, eine Antwort oder ein Wörterbucheintrag
ist. Um genau das zu ändern, brauchen wir eine ganz andere Art von
Programm — eines, das nicht *ausgeführt* wird, sondern *trainiert* wird.

Damit beginnt Teil 2 (`02_MachineIntelligence/`): 60 Jahre neuronale
Netze, in denen aus einem einzelnen Neuron (Perceptron 1958) über MLP,
CNN, Word2Vec, RNN, Seq2Seq, Transformer schrittweise die Fähigkeit
entsteht, Bedeutung aus Text zu extrahieren. Und danach in Teil 3
(`03_AgenticSystems/`) die letzten zehn Jahre: aus einem Sprachmodell
wird ein Assistent, aus dem Assistenten ein reasoning-fähiges Modell, aus
dem reasoning-fähigen Modell ein Agent.

Der ganze Bogen läuft ab hier — auf denselben Netzwerken, auf denen wir
gerade unser erstes Paket gesendet haben, nur mit deutlich mehr
Bandbreite.

## Quellen

- Abramson, N. (1970). *The ALOHA System — Another Alternative for
  Computer Communications*. AFIPS.
- Roberts, L. G. (1972). *ALOHA Packet System With and Without Slots and
  Capture*. ACM SIGCOMM Computer Communication Review.
- Kleinrock, L., & Tobagi, F. A. (1975). *Packet Switching in Radio
  Channels: Part I — Carrier Sense Multiple-Access Modes and Their
  Throughput-Delay Characteristics*. IEEE Transactions on Communications.
- Metcalfe, R. M., & Boggs, D. R. (1976). *Ethernet: Distributed Packet
  Switching for Local Computer Networks*. Communications of the ACM.
- Cerf, V., & Kahn, R. (1974). *A Protocol for Packet Network
  Intercommunication*. IEEE Transactions on Communications.
- Tanenbaum, A. S., & Wetherall, D. J. (2011). *Computer Networks*
  (5. Aufl.), Kap. 4.