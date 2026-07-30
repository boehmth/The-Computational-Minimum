# 📖 3.2 Instruktions-Feinjustierung — TinyInstruct

## 🎯 Das Problem des Vorgängers

Kapitel 3.1 (TinyGPT) hat gezeigt, wie ein reines Sprachmodell Text
plausibel fortsetzt — flüssig, grammatikalisch, oft sogar stilsicher, aber
**ohne jede Vorstellung davon, was der Nutzer eigentlich will**. Fragt man
es *„Was ist die Hauptstadt von Frankreich?"*, erfindet es mit hoher
Wahrscheinlichkeit weitere Fragen dazu, statt zu antworten. Denn genau das
war es beim Training gewohnt: das *nächste* Token vorherzusagen, egal ob
es zu einer Frage, einer Aussage oder einer Aufzählung gehört.

Der Sprung, der in diesem Kapitel geschieht, ist der **wichtigste
konzeptionelle Bruch in der gesamten LLM-Geschichte**: aus einem
*Textvervollständiger* wird ein *Instruction-Follower*. Und dieser Sprung
geschieht — überraschend — ohne Änderung der Architektur, ohne
Reinforcement Learning, ohne menschliches Feedback. Er geschieht durch
eine einzige, kleine Modifikation des Trainings-Verfahrens: der Loss wird
nur noch auf einem *Teil* der Sequenz berechnet.

## 📜 Historischer Kontext: „Nur die Antwort lernen, nicht die Frage"

### Die Beobachtung, aus der alles folgt

Zwischen 2020 und 2021 experimentieren mehrere Gruppen — Google Research
mit **FLAN**, das BigScience-Konsortium mit **T0**, und andere — mit einer
Idee, die im Nachhinein fast schon selbstverständlich klingt:

> **Wenn ein Sprachmodell lernen soll, Anweisungen zu befolgen, dann sollte
> es nur die *Antwort* lernen — nicht die *Anweisung*.**

Konkret: Man nimmt einen bestehenden, vortrainierten Sprachmodell-Zustand
(einen „Base Model"-Checkpoint wie GPT-1, T5 oder LLaMA), und trainiert
ihn auf Beispielen der Form

```
### Instruction:
Was ist die Hauptstadt von Frankreich?

### Response:
Die Hauptstadt von Frankreich ist Paris.
```

Der Trick sitzt in der Loss-Funktion: sie wird **maskiert**. Der
Instruction-Teil trägt gar nichts zum Gradientenupdate bei. Nur die
Response fließt in den Verlust ein. Aus der Perspektive des Modells wird
die Instruction dadurch zu einem *reinen Kontext*, den es *lesen*, aber
nicht *vervollständigen* muss. Was es vervollständigen lernt, ist
ausschließlich die Antwort — und zwar so, wie ein hilfsbereiter Mensch sie
formulieren würde, weil genau solche Antworten im Trainingsdatensatz
stehen.

### Warum das so gut funktioniert

Das Erstaunliche an dieser Methode ist nicht die technische Raffinesse —
sie ist trivial. Das Erstaunliche ist die *Wirkung*. Nach wenigen tausend
Beispielen SFT (Supervised Fine-Tuning) auf gut kuratierten Instruction-
Response-Paaren wechselt das Modell sein Verhalten grundlegend:

- Es erkennt Fragen *als* Fragen und beantwortet sie.
- Es folgt Formatierungsanweisungen („Antworte in Stichpunkten").
- Es kann Rollen übernehmen („Du bist ein Physiklehrer...").
- Es überträgt seine Instruktionsfähigkeit auf Aufgabentypen, die es im
  Instruction-Datensatz nie explizit gesehen hat — Zero-Shot-Generalisierung
  auf neue Task-Familien.

Das ist der Punkt, an dem aus einem *Language Model* ein *Assistant* wird.
Alles, was heute „Chatbot" heißt — ChatGPT, Claude, Gemini, LLaMA-Chat —
enthält als ersten und wichtigsten Trainingsschritt genau diese
Instruktions-Feinjustierung. Was danach folgt (Präferenz-Ausrichtung durch
RLHF/DPO, siehe Kapitel 3.3) ist Politur auf einem bereits funktionierenden
Instruction-Follower.

### Historische Meilensteine der SFT-Linie

| Jahr | Paper / Modell | Beitrag |
|---|---|---|
| 2020 | Brown et al., *GPT-3* | Zeigt, dass Skalierung + Few-Shot-Prompting weit trägt — löst aber das Grundproblem („folgt keiner Instruktion") nicht |
| 2021 | Wei et al., *FLAN* (Google) | **Erster systematischer Nachweis**, dass Instruction-Tuning mit maskiertem Loss Zero-Shot-Generalisierung auf neue Aufgaben ermöglicht |
| 2021 | Sanh et al., *T0* (BigScience) | Multitask-Prompted-Training auf viele Task-Familien; zeigt, dass das *Aufgabenlernen* gut skaliert |
| 2022 | Wang et al., *Super-NaturalInstructions* | Öffentlicher Datensatz mit >1600 Aufgaben — SFT wird als Methode reproduzierbar |
| 2023 | Taori et al., *Alpaca* (Stanford) | 52 000 Instruction-Response-Paare (per GPT-3.5 generiert) reichen aus, um LLaMA-7B zu einem passablen Assistant zu machen — SFT wird für Community-Modelle massentauglich |
| 2023 | Zhou et al., *LIMA* | **Weniger ist mehr:** Zeigt, dass 1000 sorgfältig kuratierte SFT-Beispiele ausreichen, um ein starkes Instruction-Following zu erzielen |
| 2024 | Zephyr, Nemotron-Instruct, u. v. m. | SFT auf öffentlichen, hochqualitativen Datensätzen ist heute der Standard-Startpunkt für alle Open-Source-Chatmodelle |

Der rote Faden: FLAN und T0 *entdecken* das Prinzip. Super-Natural­Instructions
und Alpaca machen es *reproduzierbar*. LIMA zeigt, dass es *überraschend
wenig Daten* braucht. Und heute ist SFT der erste, wichtigste, oft schon
allein ausreichende Schritt in jedem Open-Source-Chatmodell — RLHF ist
Politur, SFT ist das Fundament.

## 😮 Der Wow-Effekt: Vorher/Nachher am selben Modell

Der entscheidende Vergleich in diesem Kapitel ist *nicht* „großes Modell
vs. kleines Modell" — beide Antworten kommen vom **selben, gleich großen
Modell**, einmal *ohne* und einmal *mit* Instruction-Tuning.

```
Modell: dasselbe (kleines Base-LLM)

Prompt:  "Was ist die Hauptstadt von Frankreich?"

Vor SFT (aus Kap. 3.1):
   "Was ist die Hauptstadt von Deutschland? Was ist die Hauptstadt
    von Italien? Was ist die Hauptstadt von Spanien?"
   → das Modell "vervollständigt" den Frage-Stil, statt zu antworten

Nach SFT (dieses Kapitel):
   "Die Hauptstadt von Frankreich ist Paris."
   → dieselbe Architektur, dieselbe Parameteranzahl, andere
     Verhaltensdisposition — allein durch den maskierten Loss
```

*[Platzhalter — konkrete Beispielausgaben des lokal trainierten Modells
einfügen]*

## 🧠 Was du baust

- Ein **maskierter Cross-Entropy-Loss**: `loss_mask[i] = 0` für alle Tokens
  im Instruction-Teil, `1` für die Response — anhand eines
  Separator-Tokens automatisch aus dem Format abgeleitet.
- Ein **einfaches Chat-Format** mit expliziten Rollen (z. B. `### Instruction:`
  / `### Response:`, oder ein Minimal-ChatML), so dass das Modell die
  strukturelle Trennung im Eingabestrom erkennen kann.
- Eine **Trainings-Loop-Variante** von TinyGPT: dieselbe Modellklasse, aber
  mit dem obigen Loss und einem kleinen, kuratierten Instruction-Datensatz
  (z. B. ein 1000er-Sample aus Alpaca oder LIMA — bewusst klein gehalten,
  um die *„LIMA-Beobachtung"* selbst nachempfinden zu können: wie wenig
  reicht, damit sich das Verhalten kippt?).
- Ein **Evaluierungs-Notebook**, in dem dieselben zehn Prompts durch das
  Base-Modell (aus 3.1) und das SFT-Modell (aus diesem Kapitel) geschickt
  werden und die Ausgaben nebeneinander stehen.

> ⚠️ Wie in 3.1 gilt: Wir bauen auf einem PyTorch-Grundgerüst auf. Das
> Neue in diesem Kapitel ist **nicht** die Trainings-Infrastruktur, sondern
> **die eine Zeile im Loss**, in der die Instruction-Tokens maskiert
> werden. Das ist bewusst so — es zeigt, wie klein die technische Änderung
> ist, die diesen fundamentalen Verhaltenssprung auslöst.

## 🚀 Schnelleinstieg

Die Struktur in `src/`:

```
src/
├── config.json         Trainings-Profile (test | laptop | lima)
├── data.py             Instruction-Datensatz + maskierte Labels (Kern-Idee)
├── model.py            baut ein GPTMini (importiert aus Kap. 3.1) und laedt optional einen Base-Checkpoint
├── train_sft.py        Trainings-Loop mit maskiertem Loss
├── evaluate.py         Vorher/Nachher-Vergleich Base-Modell vs. SFT-Modell
└── test_masking.py     Standalone-Beweis der didaktischen Kern-Zeile (laeuft ohne PyTorch)
```

**Schritt 0 — die Idee ohne Training verstehen** *(kein PyTorch noetig, kein Netz):*

```bash
python 03_AgenticSystems/02_TinyInstruct/src/test_masking.py
```

Zeigt Token-fuer-Token, wie der Prompt-Teil auf `IGNORE_INDEX` gesetzt wird
und der Response-Teil als Lernziel stehen bleibt — die eine Zeile, die den
ganzen Kapitel-Sprung ausmacht. Ausgabe endet mit dem Satz:
*"Die 'eine Zeile', die den Kapitel-Sprung macht: labels[: len(prompt_ids)] = [IGNORE_INDEX] \* len(prompt_ids)"*.

**Schritt 1 — SFT trainieren:**

```bash
python 03_AgenticSystems/02_TinyInstruct/src/train_sft.py --profile test
```

Profile: `test` (Rauchtest, wenige Minuten CPU), `laptop` (Standard,
Alpaca-Sample) oder `lima` (1000 kuratierte Beispiele, 5 Epochen — die
"weniger ist mehr"-Beobachtung selbst nachvollziehen).

Um von einem in Kapitel 3.1 vortrainierten TinyGPT-Checkpoint zu starten
(deutlich sinnvollere Ergebnisse), setze `BASE_MODEL_CKPT` in der
`config.json` auf den Pfad zum gespeicherten TinyGPT-State-Dict.

**Schritt 2 — Vorher/Nachher-Vergleich:**

```bash
python 03_AgenticSystems/02_TinyInstruct/src/evaluate.py \
    --base-ckpt ../01_TinyGPT/checkpoints/tinygpt_base.pt \
    --sft-ckpt  ../02_TinyInstruct/checkpoints/tinyinstruct_sft.pt \
    --profile   laptop
```

Voraussetzungen: `torch`, `transformers`, `datasets`, `tqdm`.

## 📚 Quellen

- Brown, T. et al. (2020). *Language Models are Few-Shot Learners.* (GPT-3)
- Wei, J. et al. (2021). *Finetuned Language Models Are Zero-Shot Learners.* (FLAN)
- Sanh, V. et al. (2021). *Multitask Prompted Training Enables Zero-Shot Task Generalization.* (T0)
- Wang, Y. et al. (2022). *Super-NaturalInstructions.*
- Taori, R. et al. (2023). *Alpaca: A Strong, Replicable Instruction-Following Model.*
- Zhou, C. et al. (2023). *LIMA: Less Is More for Alignment.*

## ✏️ Übungen

**1. Die LIMA-Beobachtung selbst prüfen.** Trainiere dieselbe Modell-
Architektur einmal auf 100, einmal auf 1000 und einmal auf 10 000
Instruction-Response-Paaren. Ab wie vielen Beispielen kippt das Verhalten
von „vervollständigt Fragen" zu „beantwortet Fragen"?

**2. Was passiert, wenn die Maskierung *fehlt*?** Trainiere absichtlich
*ohne* Loss-Maskierung — also mit einem Loss, der auch die Instruction-
Tokens erfasst. Wie ändert sich das Verhalten? Kannst du an konkreten
Beispielen zeigen, dass das Modell die Instruction-Struktur „lernt zu
schreiben" statt „lernt zu befolgen"?

**3. Format-Robustheit.** Trainiere mit einem Format
(`### Instruction: ... ### Response: ...`) und teste anschließend mit einem
anderen Format (z. B. Frage-Doppelpunkt-Antwort). Wie eng ist die
Instruktionsfähigkeit an das exakte Trainingsformat gebunden?

**4. Themen-Übertragung.** Wähle einen Instruction-Datensatz, der z. B. nur
sprachliche Aufgaben (Übersetzung, Zusammenfassung) enthält. Fragt man
das SFT-Modell danach eine *Rechenaufgabe*, versucht es zu antworten? Und
wenn ja, wie? (Erwartung: Es versucht es, oft mit erstaunlich
strukturierter, wenn auch falscher, Antwort — genau die Zero-Shot-
Generalisierung, die FLAN und T0 zum Meilenstein macht.)

## ➡️ Grenzen dieses Meilensteins

Nach der Instruktions-Feinjustierung folgt das Modell Anweisungen und
antwortet dialogfähig. Aber es gibt noch keine Garantie, dass es aus
mehreren *plausiblen* Antworten die *bessere* (hilfreichere, ehrlichere,
weniger schädliche) wählt. Genau das schließt Kapitel 3.3 (TinyChat)
mit Präferenz-Ausrichtung: RLHF, DPO — die Politur, die aus einem
Instruction-Follower einen konsistenten Assistenten macht.
