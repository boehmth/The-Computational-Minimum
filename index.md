---
hide:
  - navigation
  - toc
---

# The Computational Minimum

**Ein Lehrbuch über Rechnerarchitektur, Machine Intelligence und Agentic Systems — vom 4-Bit-CPU-Simulator bis zum reasoning-fähigen Sprachmodell, alles selbst geschrieben ohne Frameworks.**

──────────◆──────────◆──────────◆──────────◆──────────

## Willkommen

Dieses Buch ist der Versuch, den gesamten Bogen der modernen Informatik — von einem einzelnen Transistor bis zu heutigen Sprachmodellen — in einer einzigen zusammenhängenden Erzählung darzustellen. Nicht als Referenzwerk zum Nachschlagen, sondern als Reise, in der jeder Schritt auf den vorherigen aufbaut.

Der rote Faden ist die These, dass die letzten 300 Jahre der Rechenkunst — von den nautischen Ephemeriden des 18. Jahrhunderts über Zuses Blechstreifen bis zu GPT-4 auf 10 000 GPUs — eine einzige, kontinuierliche **Antwortkette** sind: jede Ära hatte eine Notwendigkeit, jemand baute eine Maschine, und die Maschine wurde zur Grundlage des nächsten Schritts.

## Aufbau

Das Buch besteht aus drei Teilen. In der aktuellen Online-Fassung ist zunächst **Teil I (Computing)** vollständig verfügbar. Teile II und III sind im Repository bereits als Code und Rohtext vorhanden, werden aber erst schrittweise in die Online-Fassung überführt.

- **[Teil I · Computing](01_Computing/README.md)** — die zeitlos gültigen Bausteine: CPU, Betriebssystem, Compiler, GPU, Netzwerk. Sechs Meilensteine, jeweils mit einem lauffähigen Python-Simulator, den man selbst starten und Schritt für Schritt beobachten kann. Zusätzlich drei vertiefende [Grundlagen-Deep-Dives](01_Computing/grundlagen/README.md) für die formale Theorie.
- **Teil II · Machine Intelligence** *(im Repo, noch nicht in der Online-Fassung)* — die 60 Jahre neuronale Netze von Rosenblatts Perceptron 1958 bis zum ersten Transformer 2017.
- **Teil III · Agentic Systems** *(im Repo, noch nicht in der Online-Fassung)* — die aktuellsten zehn Jahre: aus einem Sprachmodell wird ein Assistent, aus dem Assistenten ein reasoning-fähiger Agent.

## Wie du dieses Buch lesen kannst

Zwei Ebenen, je nach Zweck:

- **Die Kapitel-READMEs** liefern *Überblick, Kontext und den Wow-Moment*. Wer nur ein Gefühl für den Aufbau der Informatik will, bleibt hier und liest die Kapitel wie Zeitungsartikel.
- **Die [Grundlagen-Deep-Dives](01_Computing/grundlagen/README.md)** liefern *Theorie, Notation und formale Präzision*. Wer selbst implementieren oder prüfen will, springt dort hinein.

Jedes Kapitel hat außerdem einen **lauffähigen Simulator** — die 4-Bit-CPU rechnet live, die Turing-Maschine bewegt ihren Kopf, die GPU zeigt SIMT-parallele Threads. Die Programme laufen mit Python 3.7+ ohne externe Abhängigkeiten. Wo sie liegen und wie man sie startet, steht in jedem Kapitel unter „Schnelleinstieg".

## Woher es kommt, wohin es will

Das Buchprojekt hat seine Wurzeln in einem klassischen Vorlesungs-Skript zur Grundlagen-Informatik (siehe [Vorwort](PREFACE.md) und [Roter Faden](ROADMAP.md)) und wurde nach und nach zu einer erzählenden Reise durch die *ganze* Informatik erweitert. Der visuelle Stil orientiert sich an der Reduktion und Klarheit der 1970er/80er-Jahre-Ästhetik europäischer Elektronik-Alben — Details dazu im [Style-Guide](STYLE.md).

Das Projekt ist Open Source: der [gesamte Quelltext](https://github.com/sritter/The-Computational-Minimum), inklusive aller Simulatoren, Bilder und Deep Dives, liegt auf GitHub. Fehler, Ergänzungen oder Diskussionen gerne als Issue oder Pull Request.

──────────◆──────────◆──────────◆──────────◆──────────

*Los geht's im [Vorwort](PREFACE.md) oder direkt in [Teil I · Computing](01_Computing/README.md).*