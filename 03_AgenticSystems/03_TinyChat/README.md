# 📖 3.3 Präferenz-Ausrichtung — TinyChat

## 🎯 Das Problem des Vorgängers

Kapitel 3.2 (TinyInstruct) hat gezeigt, dass ein Sprachmodell durch
maskiertes Fine-Tuning zum *Instruction-Follower* wird: Es beantwortet
Fragen, statt sie zu vervollständigen. Aber SFT hat eine subtile Grenze,
die man erst sieht, wenn man das Modell länger benutzt.

Wenn zu einer Instruktion **mehrere plausible Antworten** möglich sind —
etwa eine kurze und eine lange, eine höfliche und eine schroffe, eine
hilfreiche und eine ausweichende, eine faktisch korrekte und eine
oberflächlich-schöne — dann kann SFT nur *eine* davon als „richtig"
verwenden. Alle anderen zählen als „falsch", obwohl sie ebenfalls
plausibel wären. Das Modell lernt also *einen bestimmten Stil*, den zufällig
die Trainingsdaten hatten — nicht eine allgemeine Präferenz „was ist eine
gute Antwort".

Die Frage, die dieses Kapitel beantwortet: **Wie bringt man einem Modell
bei, aus mehreren plausiblen Antworten die *bessere* zu wählen — nach
menschlichem Maßstab?**

## 📜 Historischer Kontext: RLHF, aus der Robotik zur Sprache und zurück zur Einfachheit

Die Idee, Modelle nach *menschlichen Präferenzen* statt nach einer festen
Ground-Truth zu trainieren, kommt nicht ursprünglich aus dem NLP-Bereich.
Sie kommt aus dem Reinforcement Learning — genauer: aus einer Reihe von
Arbeiten, die zunächst Spiel- und Robotik-Aufgaben lösen sollten und dann
schrittweise auf Sprache übertragen wurden.

| Jahr | Paper / Modell | Beitrag |
|---|---|---|
| 2017 | Christiano et al., *Deep RL from Human Preferences* (OpenAI, DeepMind) | Führt **RLHF als Methode** überhaupt ein: statt einer festen Belohnung wird ein Reward-Modell aus paarweisen Menschen-Präferenzen gelernt. Ursprünglich für Atari und Robotik, nicht für Sprache. |
| 2019 | Ziegler et al., *Fine-Tuning Language Models from Human Preferences* (OpenAI) | Überträgt RLHF **erstmals auf Sprachmodelle** — zunächst für Stil-Steuerung, noch weit weg von Chat. |
| 2020 | Stiennon et al., *Learning to Summarize from Human Feedback* (OpenAI) | Erste überzeugende Sprachanwendung: **Zusammenfassungen**, die von Menschen als besser als die Referenz bewertet werden. Direkte methodische Vorlage für InstructGPT. |
| 2022 | Ouyang et al., *InstructGPT* (OpenAI) | Verbindet SFT (aus 3.2) mit RLHF: **zuerst SFT auf Instruction-Daten, dann RLHF auf menschlichen Präferenzen zwischen Modell-Antworten**. Das ist das Rezept, aus dem später ChatGPT wird. |
| 2022 | *ChatGPT* (OpenAI, kein Paper) | Produktifizierung von InstructGPT: gleiches Rezept, dazu Multi-Turn-Chat-Format und kontinuierliche Nutzer-Feedback-Schleife. **Der Punkt, an dem breite Öffentlichkeit erstmals mit einem Sprachmodell interagiert.** |
| 2023 | Bai et al., *Constitutional AI / RLAIF* (Anthropic) | Ersetzt menschliche Präferenzen teilweise durch **KI-generierte Präferenzen anhand einer schriftlichen Verfassung** — RLHF wird selbstversorgend. Klaudius/Claude ist das darauf aufbauende Produkt. |
| 2023 | Rafailov et al., *Direct Preference Optimization (DPO)* | **Der Vereinfachungssprung.** Zeigt: Man braucht das Reward-Modell und das PPO gar nicht. Präferenz-Ausrichtung lässt sich als *einfaches Supervised-Learning-Ziel* auf Paaren (bevorzugte Antwort, abgelehnte Antwort) formulieren. **DPO ist heute der Standard in Open-Source-Chatmodellen.** |
| 2024 | Zephyr, Nemotron, LLaMA-Instruct u. v. m. | Alle offenen Chatmodelle der letzten zwei Jahre folgen dem Rezept: **SFT (aus 3.2) → DPO (aus diesem Kapitel)** — die ursprüngliche PPO-basierte RLHF-Pipeline ist außerhalb der großen Labs faktisch verschwunden. |

Der rote Faden hier ist bemerkenswert und passt exakt zum Grundmotiv aus
`00_Fundament` und `PREFACE.md`:

- **Christiano 2017 bis Ouyang 2022** ist eine Kette von Experimenten, die
  RLHF Schritt für Schritt von Spielen über Zusammenfassungen zu vollen
  Chatmodellen tragen. Jede Stufe wird durch Ausprobieren gefunden, keine
  Theorie sagt vorher „so muss es aussehen".
- **DPO 2023** ist die vielleicht schönste didaktische Pointe des ganzen
  Themas: Die zunächst hochkomplizierte RLHF-Pipeline (Reward-Modell +
  PPO + KL-Constraint) stellt sich, wenn man die Mathematik sauber
  aufschreibt, als *äquivalent zu einem einfachen Klassifikations-Loss auf
  Präferenzpaaren* heraus. Was jahrelang als „RL auf Sprache" galt, war in
  Wahrheit eine verkleidete Supervised-Learning-Aufgabe.

> **Ein wichtiger Punkt zur Einordnung**: „ChatGPT" ist kein
> wissenschaftlicher Beitrag mit eigenem Paper. Es ist eine
> **Produktversion aus GPT-3.5 + InstructGPT-Rezept + Chat-Format +
> laufendem Nutzer-Feedback**. Der wissenschaftliche Sprung, den ChatGPT
> populär gemacht hat, geschah in den vier Papers **FLAN + InstructGPT +
> DPO + (RLAIF)** — die drei Zutaten dieses Kapitels plus der SFT-Sprung
> aus 3.2.

## 😮 Der Wow-Effekt: Selbes Modell, andere Präferenzen

Der Vergleich in diesem Kapitel geht *nicht* wieder gegen das Base-Modell
aus 3.1, sondern gegen das schon *instruktionsfähige* SFT-Modell aus 3.2:

```
Prompt: "Erkläre mir, wie eine CPU funktioniert."

3.2 (SFT):
   "Eine CPU führt Instruktionen aus. Sie hat Register, eine ALU und
    einen Programmzähler. Sie liest Instruktionen aus dem Speicher."
   → korrekt, aber knapp, sprunghaft, wenig didaktisch

3.3 (SFT + DPO):
   "Eine CPU ist wie ein sehr eifriger, aber sturer Arbeiter, der eine
    Liste von Anweisungen der Reihe nach abarbeitet. Er hat: ein
    Notizbuch (die Register), einen Taschenrechner (die ALU), und einen
    Zeigefinger auf der aktuellen Zeile (den Programmzähler). Bei jeder
    Anweisung ..."
   → dieselben Fakten, aber strukturiert, verständlich, hilfreich —
     weil Menschen (oder eine Verfassung) diese Formulierungen bevorzugt
     haben, als sie Präferenzpaare erstellten
```

*[Platzhalter — konkrete Beispielausgaben einfügen]*

## 🧠 Was du baust

Wir bauen bewusst **die didaktisch einfachste Variante — DPO — und nicht
das historische RLHF/PPO-Rezept**. Der Grund: DPO ist mathematisch
transparent, hat keine separate Reward-Modell-Trainingsphase, keine PPO-
Rollout-Infrastruktur, und ist heute der de-facto-Standard im Open-Source-
Bereich. Das RLHF/PPO-Rezept aus InstructGPT wird als *historisch* und
*konzeptionell* erklärt, aber nicht implementiert.

Konkret:

- Ein **Präferenzdatensatz** aus Tripeln `(prompt, chosen, rejected)` —
  entweder aus einem öffentlichen Datensatz (z. B. `HH-RLHF` von Anthropic,
  `UltraFeedback`) oder synthetisch generiert (RLAIF-Stil, mit einer
  einfachen Verfassung).
- Der **DPO-Loss** — implementiert von Hand in wenigen Zeilen, als Beweis,
  dass er tatsächlich nur ein maskiertes Log-Ratio auf Präferenzpaaren
  ist.
- Ein **Referenzmodell-Anker** (das SFT-Modell aus 3.2, eingefroren): die
  Log-Wahrscheinlichkeiten des trainierten Modells werden mit ihm ins
  Verhältnis gesetzt, damit das Modell nicht zu weit vom instruktionsfähigen
  Ausgangspunkt driftet.
- Ein **Evaluierungsblock**, in dem dieselben Prompts durch das SFT-Modell
  aus 3.2 und das DPO-Modell aus diesem Kapitel geschickt werden — und
  ausgewählte Paare in einer kleinen menschlichen (oder KI-basierten)
  Rangordnung landen.

**Konzeptioneller Anhang (kein Code)**: Ein Abschnitt, in dem gezeigt
wird, wie das *ursprüngliche* RLHF/PPO-Rezept aus InstructGPT aussieht
(Reward-Modell + PPO + KL-Penalty), warum es funktioniert, und warum die
DPO-Vereinfachung mathematisch äquivalent ist. Das ist die *historische
Ehrlichkeit*: DPO ist eleganter, aber ohne den RLHF-Umweg wäre es nie
gefunden worden.

> ⚠️ Wie in 3.1 und 3.2 gilt: Wir bauen auf einem PyTorch-Grundgerüst auf.
> Was in diesem Kapitel neu ist, ist der **DPO-Loss** — buchstäblich eine
> Handvoll Zeilen, deren Einfachheit die eigentliche Pointe ist.

## 🚀 Schnelleinstieg

Die Struktur in `src/`:

```
src/
├── config.json         Trainings-Profile (test | laptop) inkl. DPO_BETA
├── data.py             Praeferenzdatensatz (chosen/rejected) - HH-RLHF oder Fallback
├── train_dpo.py        Trainings-Loop mit DPO-Loss
├── evaluate.py         Vorher/Nachher-Vergleich SFT-Modell vs. DPO-Modell
└── test_dpo_loss.py    Standalone-Beweis der DPO-Formel (laeuft OHNE PyTorch)
```

**Schritt 0 — die Idee ohne Training verstehen** *(kein PyTorch noetig, kein Netz):*

```bash
python 03_AgenticSystems/03_TinyChat/src/test_dpo_loss.py
```

Zeigt in drei synthetischen Szenarien, wie sich der DPO-Loss verhaelt:
- Policy bevorzugt schon `chosen` -> Loss ist am *kleinsten* (verifiziert: 0.5981).
- Policy neutral (== Referenz) -> Loss ist genau `ln 2 ≈ 0.693` (verifiziert: 0.6931).
- Policy bevorzugt `rejected` -> Loss ist am *groessten* (verifiziert: 0.7981).

Das ist der ganze DPO-Trainings-Mechanismus - eine Rechnung, viele
Wiederholungen.

**Schritt 1 — DPO trainieren:**

```bash
python 03_AgenticSystems/03_TinyChat/src/train_dpo.py --profile test
```

Setze **unbedingt** `SFT_MODEL_CKPT` in `config.json` auf den Pfad zum
SFT-Modell aus Kapitel 3.2. Ohne diesen Anker startet DPO von zufaelligen
Gewichten und die Rewards bleiben nahe 0 (das Skript warnt in diesem
Fall).

**Schritt 2 — Vorher/Nachher-Vergleich (SFT vs. DPO):**

```bash
python 03_AgenticSystems/03_TinyChat/src/evaluate.py \
    --sft-ckpt ../../02_TinyInstruct/checkpoints/tinyinstruct_sft.pt \
    --dpo-ckpt ../checkpoints/tinychat_dpo.pt \
    --profile  laptop
```

Voraussetzungen: `torch`, `transformers`, `datasets`, `tqdm`.

## 📚 Quellen

- Christiano, P. et al. (2017). *Deep Reinforcement Learning from Human Preferences.*
- Ziegler, D. et al. (2019). *Fine-Tuning Language Models from Human Preferences.*
- Stiennon, N. et al. (2020). *Learning to Summarize from Human Feedback.*
- Ouyang, L. et al. (2022). *Training Language Models to Follow Instructions with Human Feedback.* (InstructGPT)
- Bai, Y. et al. (2022). *Constitutional AI: Harmlessness from AI Feedback.* (Anthropic, RLAIF)
- Rafailov, R. et al. (2023). *Direct Preference Optimization: Your Language Model is Secretly a Reward Model.* (DPO)

## ✏️ Übungen

**1. DPO vs. reines SFT — der Unterschied in Zahlen.** Nimm zehn Prompts,
lass dir vom SFT-Modell (3.2) und vom DPO-Modell (3.3) je fünf Antworten
generieren. Lass eine Testperson (oder ein starkes externes Modell) je
zwei Antworten paarweise vergleichen. In wie viel Prozent der Vergleiche
gewinnt DPO?

**2. Was passiert bei zu vielen DPO-Schritten?** Trainiere DPO absichtlich
zu lange. Beobachtung? *(Erwartung: Das Modell driftet vom SFT-Anker weg,
antwortet stereotyp, verliert die Vielseitigkeit. Das ist der Grund für
den KL-Term im DPO-Loss — er hält das Modell nahe am SFT-Startpunkt.)*

**3. RLAIF selbst ausprobieren.** Formuliere eine kleine Verfassung von
5 Regeln (z. B. „Antworte klar strukturiert", „Nenne unsichere Angaben als
solche"). Lass ein größeres Modell für Prompt-Antworten anhand dieser
Regeln paarweise Präferenzen erstellen und trainiere DPO darauf. Wie
weit trägt reine KI-Präferenz?

**4. Konzeptionell: DPO als vereinfachtes RLHF.** Rekonstruiere aus dem
DPO-Paper die Argumentation, warum der DPO-Loss algebraisch äquivalent
zum Optimum der ursprünglichen RLHF-Formulierung ist. Wo geht die
Vereinfachung genau ein? *(Hinweis: Die entscheidende Umformung ist, dass
das optimale Policy-Reward-Modell-Paar bei Bradley-Terry-Präferenzen eine
geschlossene Form hat.)*

## ➡️ Grenzen dieses Meilensteins

TinyChat folgt Instruktionen zuverlässig und antwortet in einem
präferenz-ausgerichteten Stil — aber es ist immer noch ein **dichtes**
Modell: Jedes einzelne Token durchläuft alle Parameter. Für mehr
Kapazität muss das ganze Modell größer werden, und die Rechenkosten pro
Token wachsen mit. Kapitel 3.4 (TinyMoE) zeigt, wie sich diese
Skalierungsachse aufbrechen lässt: Kapazität wächst, ohne dass die Kosten
pro Token proportional mitwachsen — die zweite große Skalierungsachse,
die in `PREFACE.md` als roter Faden des ganzen Teils benannt ist.
