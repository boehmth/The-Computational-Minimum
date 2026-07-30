# 📖 3.5 Reasoning — TinyReason

## 🎯 Das Problem des Vorgängers

TinyChat (3.3) und TinyMoE (3.4) folgen Instruktionen zuverlässig und
skalieren effizient — aber beide antworten direkt, ohne Zwischenschritte.
Bei mehrstufigen Problemen (Rechenaufgaben mit mehreren Schritten,
Fangfragen, logische Ableitungen) führt das reproduzierbar zu Fehlern: Das
Modell "rät" die plausibelste Oberflächenform der Antwort, statt das Problem
tatsächlich zu zerlegen.

## 📜 Historischer Kontext: Von der Prompting-Beobachtung zum trainierten Reasoning

### Kurzer Zwischenschritt: Chain-of-Thought-Prompting (2022)

Wei et al. (2022), *"Chain-of-Thought Prompting Elicits Reasoning in Large
Language Models"*, machten eine einfache, aber folgenreiche Beobachtung:
Fordert man ein ausreichend großes Modell explizit auf, Schritt für Schritt
zu denken, verbessert sich die Antwortqualität — **ganz ohne zusätzliches
Training**, allein durch die Formulierung des Prompts.

```
Ohne CoT:
"Ein Bauer hat 17 Schafe. Alle bis auf 9 sterben. Wie viele Schafe
bleiben übrig?"
→ Modell antwortet oft direkt und mitunter falsch (z. B. "8" statt "9"),
   weil es die Formulierung überliest statt sie zu zerlegen.

Mit CoT ("Denke Schritt für Schritt"):
→ Modell zerlegt die Frage explizit, erkennt "alle bis auf 9" bedeutet
   "9 bleiben übrig", kommt zuverlässiger zur richtigen Antwort.
```

Wichtig für die Einordnung: CoT-Prompting verändert **kein einziges
Gewicht** des Modells — es ist eine reine Interface-Technik. Genau das wirft
die Frage auf, die dieses Kapitel eigentlich beantwortet: *Wenn
Schritt-für-Schritt-Denken so zuverlässig hilft, warum bringen wir es dem
Modell nicht direkt bei, statt es bei jeder Anfrage neu im Prompt zu
erbetteln?*

### Die eigentliche Entwicklungslinie: trainiertes Reasoning

| Jahr | Paper | Beitrag |
|---|---|---|
| 2022 | Zelikman et al., *STaR: Self-Taught Reasoner* | Bootstrapping: Modell generiert eigene Begründungen, nur Beispiele mit korrektem Endergebnis werden zum Nachtrainieren verwendet — ein sich selbst verbessernder Kreislauf |
| 2023 | Lightman et al., *Let's Verify Step by Step* | Zeigt: Bewertung *jedes einzelnen Zwischenschritts* (Process Reward Model) statt nur des Endergebnisses liefert zuverlässigeres Reasoning als reine Ergebnis-Supervision |
| 2024 | OpenAI o1 (kein wissenschaftliches Paper, nur System Card/Blogpost) | Erstes großes Produkt, das trainiertes, verlängertes Reasoning vor der Antwort einsetzt — Methodik bleibt weitgehend unveröffentlicht |
| 2025 | DeepSeek-AI, *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning* | Zeigt öffentlich nachvollziehbar: Reasoning-Verhalten entsteht bereits durch **reines, ergebnisbasiertes Reinforcement Learning** (R1-Zero) — ganz ohne die teuren, schritt-annotierten Process Reward Models aus 2023 |

Der rote Faden: **STaR** zeigt das Prinzip des Selbstlernens aus eigenen
Begründungen, aber nur mit Blick auf das Endergebnis. (Dieser rote Faden ist
kein Zufall dieses einen Kapitels — er wird im Vorwort zu diesem Teil als
Prinzip des gesamten Feldes eingeführt: siehe `PREFACE.md`.) **Process Reward
Models** verbessern die Zuverlässigkeit, indem sie jeden Schritt bewerten —
erkaufen das aber mit teurer, menschlicher Schritt-Annotation. **o1** zeigt,
dass sich das produktiv skalieren lässt, bleibt aber eine Blackbox.
**DeepSeek-R1** schließt den Kreis: Es zeigt, dass ergebnisbasierte
Belohnung allein (kein Process Reward Model nötig) ausreicht, damit ein
Modell von selbst lernt, in längeren Denkschritten zu "planen", zu
überprüfen und zu korrigieren — und veröffentlicht Methodik und Gewichte
offen.

*(Randnotiz für den Text, falls passend: Genau dieses DeepSeek-R1-Prinzip
steckt destilliert auch im lokal lauffähigen `deepseek-r1-distill-qwen-7b`,
das in den vorherigen Kapiteln zum lokalen Ausprobieren genutzt wurde. Der
Sprung vom Miniaturmodell dieses Kapitels zu diesem realen, selbst
betriebenen Modell ist dabei kein Bruch, sondern dieselbe Skalierungslogik,
die sich als zweiter roter Faden durch die ganze Reihe zieht — von TinyMoE
(3.4), wo Kapazität erstmals effizient skalierbar wurde, bis zu den Scaling
Laws, die im Vorwort zu diesem Teil als eines der prägenden Prinzipien des
gesamten Feldes benannt werden.)*

## 😮 Der Wow-Effekt: Direkte Antwort vs. Reasoning-Spur

*[Platzhalter — Beispielausgabe: dieselbe (mehrstufige) Aufgabe einmal mit
TinyChat aus 3.3 (direkte, ggf. falsche Antwort) und einmal mit
TinyReason (sichtbare Denkschritte, korrekte Antwort) gegenüberstellen]*

```
Aufgabe:  [Platzhalter — mehrstufige Aufgabe, z. B. eine kleine
           Textaufgabe mit mehreren Rechenschritten]

TinyChat (3.3):  [Platzhalter — direkte Antwort, ggf. fehlerhaft]

TinyReason (3.5):
<think>
[Platzhalter — sichtbare Zwischenschritte]
</think>
[Platzhalter — korrekte Endantwort]
```

## 🧠 Was du baust

- Eine **regelbasierte Belohnungsfunktion**: für Aufgaben mit eindeutig
  prüfbarem Endergebnis (z. B. Rechenaufgaben) wird automatisch bewertet,
  ob die Antwort korrekt ist — kein menschlich annotiertes Process Reward
  Model nötig (im Sinne von R1-Zero)
- Eine vereinfachte RL-Trainingsschleife: TinyChat generiert mehrere
  Lösungsversuche mit sichtbarer Denkspur, nur Versuche mit korrektem
  Endergebnis werden verstärkt (didaktische Annäherung an das
  Belohnungsprinzip hinter STaR/R1 — kein vollständiges GRPO/PPO-Setup)
- Ein Trainingsformat mit expliziter `<think>...</think>`-Struktur, damit
  die Denkspur von der eigentlichen Antwort sichtbar getrennt ist

> ⚠️ Wie in den vorherigen Kapiteln gilt: Wir implementieren das *Prinzip*
> von ergebnisbasiertem RL-Reasoning in vereinfachter Form, nicht die
> vollständige, rechenintensive RL-Infrastruktur (GRPO, große
> Rollout-Batches) aus dem echten DeepSeek-R1-Training.

## 🚀 Schnelleinstieg

Die Struktur in `src/`:

```
src/
├── config.json         Trainings-Profile (test | laptop)
├── data.py             Synthetische Rechenaufgaben mit pruefbarem Endergebnis
├── reward.py           Regelbasierte Belohnungsfunktion (Kern)
├── train_rl.py         STaR-artiger Trainings-Loop (Rollout -> Filter -> SFT)
└── test_reward.py      Standalone-Beweis der Belohnungslogik (OHNE PyTorch)
```

**Schritt 0 — die Idee ohne Training verstehen** *(kein PyTorch, kein Netz):*

```bash
python 03_AgenticSystems/05_TinyReason/src/test_reward.py
```

Zeigt an sechs synthetischen Modell-Ausgaben, wie die Belohnung zwischen
1.0 (Denkspur + korrekte Antwort), 0.1 (Format ok, Antwort falsch) und
0.0 (Format oder Antwort fehlt) unterscheidet — verifiziert. Genau diese
scharfe Unterscheidung *ist* der ganze DeepSeek-R1-Zero-Anreiz.

**Schritt 1 — Reasoning-Training:**

```bash
python 03_AgenticSystems/05_TinyReason/src/train_rl.py --profile test
```

Der Trainings-Loop macht in jeder Iteration:
1. **Rollout**: das Modell erzeugt fuer jede Aufgabe mehrere Antworten
   (Temperatur-Sampling fuer Diversitaet).
2. **Reward**: `compute_reward()` bewertet jede Antwort deterministisch.
3. **Filter + SFT**: nur Antworten mit `reward >= 0.5` werden behalten
   und mit maskiertem Loss (wie in Kap. 3.2) nachtrainiert.

**Wichtig:** Setze `SFT_MODEL_CKPT` in `config.json` auf den TinyInstruct-
Checkpoint aus Kap. 3.2 — sonst hat das Startmodell keine Instruktions-
faehigkeit und produziert im ersten Rollout praktisch nie eine
regelkonforme Antwort.

Voraussetzungen: `torch`, `transformers`, `tqdm`.

## 📚 Quellen

- Wei, J. et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models.*
- Zelikman, E. et al. (2022). *STaR: Bootstrapping Reasoning With Reasoning.*
- Lightman, H. et al. (2023). *Let's Verify Step by Step.*
- OpenAI (2024). *Learning to Reason with LLMs* (o1 System Card / Blogpost).
- DeepSeek-AI (2025). *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning.*

## ✏️ Übungen

*[Platzhalter]*

## ➡️ Grenzen dieses Meilensteins

TinyReason denkt in Schritten, bleibt aber rein textuell — es kann nicht auf
die Welt zugreifen, keine Werkzeuge nutzen, keine Datei lesen oder ein
Ergebnis extern überprüfen. Ein späteres Kapitel (Agenten) zeigt, wie aus
einem reasoning-fähigen Modell ein erster handelnder Agent wird.
