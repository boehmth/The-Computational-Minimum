# Vorwort zu Teil 3 — Milestones in Agentic Systems

## Skalierung als durchgehende Herausforderung — jetzt als Regel eines ganzen Feldes

`00_Fundament` hat die Frage gestellt, `02_MachineIntelligence` hat sie am
Lernprinzip durchdekliniert: ein Neuron, dann immer mehr davon, bis
einfaches Skalieren an eine Grenze stößt und eine neue Struktur nötig wird
— CNN, RNN, Transformer, jeweils als Antwort auf eine konkrete
Skalierungsgrenze.

In Teil 3 ist dieselbe Frage nicht mehr Merkmal einzelner Kapitel, sondern
die **Betriebsweise des gesamten Feldes**. Die zehn Jahre von LLMs bis zu
autonomen Agenten, die dieser Teil nachzeichnet, lassen sich fast
vollständig als eine Suche nach neuen Skalierungsachsen lesen:

- **Scaling Laws** (Kaplan et al., 2020) zeigen zuerst die naheliegendste
  Achse: mehr Parameter, mehr Daten, mehr Rechenleistung — mit
  vorhersagbarem Ertrag. Diese Kurve wurde empirisch vermessen, nicht aus
  einer Theorie des Lernens abgeleitet.
- **Mixture of Experts** (Kapitel 3.3) findet eine zweite Achse: Kapazität
  wächst, ohne dass die Rechenkosten pro Token proportional mitwachsen —
  eine Antwort auf die Grenze, dass dichte Modelle irgendwann schlicht zu
  teuer werden, um sie weiter zu vergrößern.
- **Trainiertes Reasoning** (Kapitel 3.4, TinyReason) findet eine dritte,
  neuartige Achse: Statt beim Training mehr Parameter zu investieren,
  investiert man beim **Antworten** mehr Rechenzeit — "Test-Time Scaling"
  statt "Train-Time Scaling". Ein Modell, das länger nachdenkt, wird
  zuverlässiger, ganz ohne größer zu werden.

Jede dieser drei Achsen wurde gefunden, nicht hergeleitet. Den bisher
radikalsten Beleg dieser Kultur liefert dieser Teil in TinyReason: Bei
DeepSeek-R1-Zero wurde die dritte Skalierungsachse nicht konstruiert,
sondern **entdeckt** — als Nebenprodukt eines simplen, ergebnisbasierten
Trainingsanreizes, den niemand mit dieser Konsequenz vorhergesagt hatte.
Von Zuses Blechstreifen 1941, über die Bit-Breite einer CPU, bis zur
Rechenzeit, die ein Modell sich beim Antworten selbst zugesteht, trägt
dieselbe Struktur: eine Skalierungsgrenze, überwunden durch Ausprobieren.

Dieser Teil ist damit nicht nur die Fortsetzung der Zeitachse aus Teil 2,
sondern der Beweis, dass das in `00_Fundament` benannte Muster — Skalierung
als Frage, Experiment als Methode — kein Merkmal der Vergangenheit ist,
sondern die Arbeitsweise der Gegenwart.