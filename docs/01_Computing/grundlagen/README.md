# Grundlagen — Deep Dives für Teil 1

Dieser Ordner enthält **vertiefende Lehrtexte** zu den Konzepten, die in
Teil 1 („Computing") auftauchen. Sie sind bewusst *zusätzlich* zu den
Kapitel-READMEs: die READMEs geben **Überblick, Kontext und den Wow-
Moment**, hier landet die **Theorie, Notation und formale Präzision**.

## 📖 Warum eine zweite Ebene?

Jede Kapitel-README beantwortet eine Frage im Stil:

> *„Warum sollte ich das lernen wollen, und was ist das eine Aha-Bild,
> das ich mitnehmen soll?"*

Dieser Grundlagen-Bereich beantwortet die *nachfolgende* Frage:

> *„Ich habe den Aha-Moment. Jetzt möchte ich verstehen, warum das
> mathematisch, physikalisch, technisch funktioniert."*

Wer nur den Überblick will, bleibt bei den READMEs. Wer selbst
implementieren, prüfen oder weiterbauen will, springt hier hinein. Die
Deep Dives ersetzen keine README — sie erweitern sie.

Der Ton entspricht dem klassischen deutschen Universitäts-Lehrtext:
ruhig, definitorisch, mit Sätzen und Beweis-Skizzen, aber ohne
Übertreibung. Wo der Kap1-Ursprungstext (die didaktische Vorlage
dieses Buchs von 2019) durch neue Beispiele geschärft werden kann —
Deep Learning, GPUs, TCP-Congestion — ist das mit einem Absatz *„Der
Bogen zurück ..."* am Ende jedes Abschnitts explizit gemacht.

## 📚 Die Deep Dives (Teil 1)

| Datei | Themen | Verlinkt aus |
|-------|--------|--------------|
| [`schaltnetze.md`](schaltnetze.md) | Boolesche Grundoperationen (UND/ODER/NICHT), Halb- und Volladdierer, ALU-Konstruktion, Flip-Flops, Tri-State-Gatter, Bus-Konstruktion | Kap. 01 CPU |
| [`von_neumann.md`](von_neumann.md) | Automatenbegriff, EVA-Prinzip, Fetch/Execute-Zyklus, Mikrocode am 4-Bit-Beispiel, Von-Neumann-Flaschenhals | Kap. 01 CPU |
| [`moderne_prozessoren.md`](moderne_prozessoren.md) | Pipelining, Flynn-Klassifikation (SISD/SIMD/MIMD), Mooresches Gesetz, Cache-Hierarchien, der Weg zu Multicore und GPU | Kap. 01 CPU, Kap. 05 GPU |

*Weitere Deep Dives (Zahlendarstellung, Algorithmen-Komplexität,
Informationstheorie, OSI-Schichten) sind vorbereitet, aber noch nicht
fertig geschrieben; sie folgen, wenn die Kapitel-READMEs sie
inhaltlich anfordern.*

## 🔗 Wie ein Deep-Dive-Absprung aussieht

In den Kapitel-READMEs sieht die Verlinkung so aus (Beispiel aus Kap. 01):

```markdown
> **Wie funktioniert der Bus mathematisch — und warum darf immer nur
> ein Sender darauf schreiben?**
> [→ Deep Dive: Tri-State-Gatter und Bus-Konstruktion](../grundlagen/schaltnetze.md#tri-state-gatter-und-bus-konstruktion)
```

Das heißt: **die README bleibt lesefreundlich**, und wer tiefer will,
klickt einmal. Wir vermeiden es, jedes Detail schon in der README zu
erklären — sonst wird sie unlesbar.

## 🧭 Beziehung zum ursprünglichen Kap1-Text

Der ursprüngliche didaktische Text („Kap1.docx", 2019) ist der Grund,
warum in Teil 1 überhaupt eine 4-Bit-CPU steht: sie stammt genau aus
diesem Text. Die Deep Dives übernehmen die Substanz, aktualisieren die
Beispiele auf den heutigen Stand (2026) und schließen jeden Abschnitt
mit einem Bogen zurück zu den README-Wow-Momenten. Wer den
ursprünglichen Kap1 kennt, wird viele Formulierungen und Diagramme
wiedererkennen; wer ihn nicht kennt, verpasst nichts.

──────────◆──────────◆──────────◆──────────◆──────────

*Diese Deep Dives sind Teil des Buchprojekts „The Computational
Minimum". Fehler oder Ergänzungswünsche gerne als Issue oder Pull
Request ins Repository.*