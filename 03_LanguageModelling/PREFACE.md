# Vorwort zu Teil 3 — Die Entwicklung der Sprachmodelle

## Der rote Faden, jetzt als Regel eines ganzen Feldes

`00_Fundament` hat die These aufgestellt, `02_MachineIntelligence` hat sie an
einzelnen Meilensteinen belegt: Perceptron, Backpropagation, Transformer —
jeder von ihnen wurde zuerst beobachtet, dann verstanden, nicht umgekehrt.

In Teil 3 ist diese Haltung kein Merkmal einzelner Durchbrüche mehr, sondern
die **Betriebsweise des gesamten Feldes**. Die zehn Jahre von LLMs bis zu
reasoning-fähigen Modellen, die dieser Teil nachzeichnet, sind geprägt von
einer Forschungskultur, die konsequent experimentiert, bevor sie erklärt:

- **Scaling Laws** (Kaplan et al., 2020) — dass mehr Parameter, mehr Daten
  und mehr Rechenleistung vorhersagbar bessere Modelle ergeben, wurde
  empirisch vermessen, nicht aus einer Theorie des Lernens abgeleitet.
- **Emergente Fähigkeiten** — Modelle beginnen bei bestimmten Größen
  plötzlich, Aufgaben zu lösen, für die sie nie explizit trainiert wurden.
  Bis heute gibt es keine geschlossene Theorie, die vorhersagt, *wann* das
  passiert — man beobachtet es, Modell für Modell.
- **Instruction-Tuning durch maskierten Loss** (Kapitel 3.2) — dass ein
  Sprachmodell zum *Instruction-Follower* wird, wenn man nur die Antwort
  in den Loss aufnimmt und die Frage maskiert, ist eine Beobachtung, die
  bei FLAN und T0 zunächst mit erheblicher Skepsis aufgenommen wurde. Erst
  die Wirkung — Zero-Shot-Generalisierung auf ungesehene Aufgabenfamilien
  — brachte den Durchbruch, nicht eine Theorie darüber, *warum* Maskierung
  reicht.
- **Direct Preference Optimization** (Kapitel 3.3) — dass die
  komplizierte RLHF-Pipeline (Reward-Modell + PPO + KL-Constraint) sich
  als *einfacher Klassifikations-Loss auf Präferenzpaaren* schreiben
  lässt, wurde erst 2023 in aller Deutlichkeit gezeigt, obwohl die
  mathematischen Zutaten seit Jahren dalagen. Ein Beispiel dafür, dass
  Vereinfachungen oft *nach* der komplizierten Version kommen, nicht
  vorher.
- **Mixture of Experts** (Kapitel 3.4) — dass sich spärlich aktivierte
  Experten von selbst sinnvoll spezialisieren, wenn man nur die
  Trainingsanreize richtig setzt, ist ein Befund aus der Praxis, keine
  vorab bewiesene Eigenschaft.

Den bisher radikalsten Beleg dieser Kultur liefert dieser Teil in Kapitel
3.5, **TinyReason**: Bei DeepSeek-R1-Zero wurde Reasoning-Verhalten nicht
konstruiert, sondern **entdeckt** — als Nebenprodukt eines simplen,
ergebnisbasierten Trainingsanreizes, den niemand mit dieser Konsequenz
vorhergesagt hatte. Von Zuses Blechstreifen 1941 bis zu selbstentdecktem
Reasoning-Verhalten 2025 trägt genau dasselbe Prinzip: bauen, beobachten,
verstehen — in dieser Reihenfolge.

Dieser Teil ist damit nicht nur die Fortsetzung der Zeitachse aus Teil 2,
sondern der Beweis, dass der in `00_Fundament` benannte Grundsatz kein
Merkmal der Vergangenheit ist, sondern die Arbeitsweise der Gegenwart.