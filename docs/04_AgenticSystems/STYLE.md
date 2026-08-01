# Style-Guide

Kurzform: **schreibe so, als ob du einem interessierten Kollegen etwas erklärst, der nicht dumm ist, aber deinen Kontext nicht kennt.**

Konkreter:

## Sprache

- **Deutsch als Grundton, englische Fachbegriffe unübersetzt.** *"Der Loop kostet Tokens"* ist besser als *"Die Schleife kostet Wortstücke"*. Wo das Konzept im Englischen entstanden ist, bleibt es dort.
- **Erste Person Plural.** *"Wir schicken den Prompt an das Modell."* — nicht *"der Autor schickt"* und nicht Passiv. Der Leser sitzt neben dem Autor am gleichen Terminal.
- **Kurze Absätze.** Ein Gedanke, ein Absatz. Wenn der Absatz drei verschiedene Themen streift, ist er zu lang.

## Struktur eines Kapitel-READMEs

1. **Ein-Satz-Zusammenfassung** direkt unter der Überschrift, fett. Was ist der einzelne wichtige Punkt?
2. **Historischer Kontext.** Woher kommt die Idee? Welches Paper, welche Ära, welcher Zwang der Zeit? Ohne diesen Rahmen ist die Miniatur nur Code.
3. **Die Miniaturen.** Ein Absatz pro Skript. Was passiert, welche Beobachtung ist wichtig, welche Zeile im Skript ist die Pointe?
4. **Wow-Moment.** Ein separater Abschnitt, der den *einen* Effekt herausstellt, wegen dem das Kapitel überhaupt existiert. Ohne Wow-Moment ist ein Kapitel überflüssig.
5. **Ausführen.** Genau die Kommandos, die man in ein Terminal tippt. Nicht Pseudocode.
6. **Brücke zum nächsten Kapitel.** Welche Frage hat das aktuelle Kapitel aufgeworfen, die das nächste beantwortet? Der rote Faden lebt von diesen Brücken.

## Code-Style

- **Kein Framework, wenn irgend möglich.** Wir schreiben `while not done: ...` selbst, nicht `agent.run()`.
- **Kommentare erklären das *Warum*, nicht das *Was*.** Der Leser sieht, dass `if tokens_in > 5000:` ein Kosten-Cutoff ist — er will wissen, *warum* 5000 und nicht 10000.
- **Docstrings mit Slide-Anker + Laufzeit + Kosten** am Anfang jedes Skripts (siehe die bestehenden Miniaturen als Vorlage). Das hilft dem Leser, das Skript einzuordnen, bevor er den Code liest.
- **Ein Skript = eine Idee.** Wenn du ein zweites Konzept erklären willst, schreib ein zweites Skript. Nicht ein Skript mit zwei ineinander verschachtelten Ideen.
- **Deterministische Werkzeuge.** Alle Werkzeuge im Repo sind ohne API, ohne Netz, ohne Zufall. Damit man beim Wiederholen dieselbe Ausgabe sieht — außer wo Nicht-Determinismus *die Pointe* ist (siehe Kap. 6).

## Sprache in den Skripten

- **Print statt Log.** Alle Miniaturen drucken in ASCII-Rahmen auf den Terminal. Wir laufen im Terminal, wir lesen im Terminal. Ein Logger wäre Verschleierung.
- **Freundliche Trennlinien.** `┌── SYSTEM PROMPT ───` und `└─────` sind hübsch und rhythmisch. Nicht `======` — das ist zu laut.
- **Eine Zeile am Ende, die den nächsten Schritt sagt.** *"→ Step F: was passiert, wenn das JSON kaputt ist?"* Der Leser soll wissen, wohin er als Nächstes klickt.

## Übungen

- **Immer Modifikationen der Miniatur**, nie neue Skripte von Grund auf. Der Zweck ist, dass der Leser sich mit *deinem* Code beschäftigen muss.
- **Ergebnis der Übung ist eine Beobachtung, nicht ein "richtiger" Wert.** *"Zähle die Tokens vor und nach deiner Änderung. Was hat sich verändert?"* — nicht *"das erwartete Ergebnis ist 4321 Tokens"*.
- **Bonus-Übungen dürfen offen sein.** Am Ende jedes `EXERCISES.md` steht eine "Bonus"-Übung, die keine feste Lösung hat — die soll den Leser über die Miniatur hinaustragen.

## Was wir nicht tun

- **Keine Emoji-Explosion.** Ein bis drei pro README (an semantischen Ankerpunkten: 📜 für Historisches, 🔬 für Miniaturen, 💡 für Wow, 🚀 für Ausführen, 🧭 für Brücken). Nicht bei jedem Absatz.
- **Kein Marketing-Sprech.** *"Revolutionär", "leistungsstark", "modernster"* — nie. Der Leser will die Sache verstehen, nicht sie kaufen.
- **Keine Zukunftsversprechen.** Was das Repo tut, steht im Präsens. Was es *nicht* tut, wird im `ROADMAP.md` gesammelt.