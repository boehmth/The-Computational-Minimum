# Vorwort zu Teil 2 — Milestones in Machine Intelligence

## Der rote Faden, zum ersten Mal bewiesen

`00_Fundament` hat eine Behauptung aufgestellt: dass der belastbarste
Erkenntnisgewinn in diesem Feld durch Experiment entsteht, nicht durch
reine Ableitung am Reißbrett — und Konrad Zuse als den Ahnherrn dieser
Haltung benannt. Teil 1 hat diese Haltung dann *gebaut*: eine CPU, ein
Betriebssystem, einen Compiler — Ingenieurskunst, kein Beweis.

Teil 2 ist der Ort, an dem sich diese Behauptung zum ersten Mal nicht nur
wiederholt, sondern **beweist**. Die 60-jährige Geschichte neuronaler Netze,
die in den folgenden acht Kapiteln erzählt wird, ist selbst eine
ununterbrochene Kette von Beobachtungen, die der Theorie vorausliefen:

- Rosenblatts Perceptron (1958) wurde gefeiert, bevor irgendjemand seine
  Grenzen verstand — und genau diese Grenze (das XOR-Problem) wurde nicht
  hergeleitet, sondern **entdeckt**, indem man das Ding einfach benutzte.
- Backpropagation (1986) war schon Jahre vor Rumelhart, Hinton und
  Williams in verschiedenen Formen bekannt — was fehlte, war nicht die
  Formel, sondern die *empirische Erfahrung*, dass sie bei mehrschichtigen
  Netzen tatsächlich praktikabel trainiert.
- Selbst der Transformer (2017), der Endpunkt dieses Teils, wurde nicht aus
  einer Theorie der Sprache abgeleitet, sondern aus der Beobachtung, dass
  parallele Attention schneller trainiert und besser skaliert als
  rekurrente Architekturen — ein Ingenieursbefund, keine mathematische
  Notwendigkeit.

Jeder der acht Meilensteine in diesem Teil folgt demselben Muster: nicht
"was müsste theoretisch funktionieren", sondern "was funktioniert, wenn man
es tatsächlich baut und laufen lässt — und was lernen wir aus der Lücke
zwischen Erwartung und Ergebnis?" Das ist kein Zufall, sondern die
Fortsetzung des in `00_Fundament` benannten Prinzips mit anderen Mitteln.

Teil 3 wird zeigen, dass sich daran bis heute nichts geändert hat.