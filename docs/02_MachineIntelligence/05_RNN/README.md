# KI-Meilenstein 5: Das Recurrent Neural Network (RNN)

> **🎯 Warum ist das cool?**
> Wir bauen ein Netz, das **Grimm-Sätze wortweise weiterschreibt**. Es nutzt dazu die **Wortvektoren aus Meilenstein 4** und lernt, welches Wort typischerweise auf welches folgt. Genau dieses Prinzip — *„sag das nächste Wort vorher"* — ist die Aufgabe, mit der jedes moderne Sprachmodell trainiert wird, von Mikolov 2010 bis GPT-4.

## 🌉 Von „Wortbedeutung" zu „Wortreihenfolge"

Im letzten Meilenstein (Word2Vec) haben wir Wörter als Vektoren dargestellt. Semantisch ähnliche Wörter sind einander nah. Das ist ein großer Fortschritt — aber es fehlt eine entscheidende Eigenschaft von Sprache:

> *„Der Wolf frisst das Schaf"* ist nicht dasselbe wie *„Das Schaf frisst den Wolf"*.

Beide Sätze enthalten **exakt dieselben Wörter**. Für Word2Vec sind sie ununterscheidbar — es kennt keine *Reihenfolge*.

Das ist der Kern dieses Meilensteins: Wir bauen ein Netz, das **eine Folge von Wortvektoren** verarbeitet — eines nach dem anderen, mit einem **Gedächtnis**, das sich merkt, was vorher kam. Damit trainieren wir zum ersten Mal ein **echtes Sprachmodell**: es lernt, welches Wort im Kontext als Nächstes kommen sollte. Genau diese Aufgabe treibt heute noch GPT und Claude an — nur die Architektur hat sich geändert.

---

## 🕰️ Historischer Kontext

| Jahr | Ereignis | Bedeutung |
|------|----------|-----------|
| **1986** | Jordan Networks | Erste rekurrente Idee: Ausgabe zurück in die nächste Zeitscheibe |
| **1990** | **Elman: *Finding Structure in Time*** | Der Klassiker — Hidden-State-Rekurrenz, wie wir sie hier bauen |
| **1997** | **Hochreiter & Schmidhuber: LSTM** | Rettet RNNs vor dem *Vanishing-Gradient-Problem* mit Zellzuständen und Gates |
| **2010** | **Mikolov: RNN-based Language Model** | Erstes RNN als vollwertiges Sprachmodell |
| **2015** | Karpathys *„The Unreasonable Effectiveness of RNNs"* | Blogpost zeigt der Öffentlichkeit char-RNNs, die Shakespeare & LaTeX generieren |
| **2016** | Google Translate (GNMT) läuft ein Jahr auf LSTMs | Der letzte große Auftritt vor der Ablösung |
| **2017** | **Vaswani et al.: Transformer** | Rekurrenz weg, nur noch Attention — RNNs verlieren ihren Thron in NLP |
| **heute** | Zeitreihen, Wake-Words, On-Device | RNNs leben weiter, aber selten in Sprache |

Wir bauen ein **Vanilla-Wort-RNN** ganz im Geiste von **Mikolov 2010**, mit einer wichtigen modernen Ergänzung: **vortrainierte Wortvektoren aus Word2Vec als Eingabe**. So kombinieren wir zwei Ideen, wie es viele NLP-Teams zwischen 2013 und 2017 taten (GloVe/Word2Vec + LSTM darüber — genau die Architektur, mit der wir zwischen 2014 und 2017 in der Industrie täglich gearbeitet haben).

**Hinweis — Character-Level statt Word-Level?** Karpathys berühmter Blogpost (2015) zeigt ein Zeichen-für-Zeichen-RNN, das Shakespeare, LaTeX und C-Code aus dem Nichts generiert. Für den Erzählfluss dieser Reihe (*Bedeutung → Reihenfolge*) bleiben wir bewusst **auf Wortebene**, weil wir dort die Word2Vec-Embeddings direkt weiterbenutzen können.

---

## 🧠 Die Aufgabe: Das nächste Grimm-Wort vorhersagen

Wir verwenden denselben **englischen Grimm-Korpus** wie in Meilenstein 4 (Project Gutenberg #2591, ~100 000 Wörter, Vokabular ~1 600). Der Loader nutzt automatisch den Word2Vec-Cache. Aus diesem Text soll das RNN lernen, das jeweils *nächste* Wort vorherzusagen — Wort für Wort. Der Trainings­verlust wird dann als **Cross-Entropy pro Wort** gemessen: *wie überrascht ist das Modell vom tatsächlichen nächsten Wort?*

**Warum diese Aufgabe?** Sie ist genau das minimalistische Setup, das seit 2010 alle Sprachmodelle antreibt:

1. **Self-Supervised** — jeder Text ist automatisch sein eigenes Trainingslabel. Der Text sagt dem Modell, welches Wort als nächstes kommt.
2. **Reihenfolge zählt** — anders als bei Word2Vec ist die Sequenz jetzt zentral. „Wolf frisst Schaf" muss anders behandelt werden als „Schaf frisst Wolf".
3. **Direkter Vergleich mit modernen LLMs** — dasselbe *Next-Token-Prediction*-Objective läuft in GPT-4. Nur ist dort die Architektur ein Transformer statt eines RNN.
4. **Grimm-Charme als sichtbares Ergebnis** — nach dem Training soll das Modell *„grimm-ähnlich"* weiterschreiben. Wenn Figuren wie *Marleen* oder *Frederick* im generierten Text auftauchen, wissen wir: es hat wirklich etwas gelernt.

---

## 🧩 Modellarchitektur

Für jedes Wort an Position `t` bekommt das RNN dessen **Word2Vec-Embedding** `e_t` (Größe D = 64) und berechnet:

```
h_t = tanh( W_xh @ e_t  +  W_hh @ h_{t-1}  +  b_h )     ← Gedächtnis
y_t = W_hy @ h_t + b_y                                   ← Logits (V-dim)
p_t = softmax(y_t)                                       ← Wahrscheinlichkeit pro Wort
```

Das Diagramm dazu:

```
   e_1 ──▶ [ RNN ] ──▶ h_1 ──▶ softmax ──▶ p_1  (nächstes Wort?)
             │
   e_2 ──▶ [ RNN ] ──▶ h_2 ──▶ softmax ──▶ p_2
             │
   e_3 ──▶ [ RNN ] ──▶ h_3 ──▶ softmax ──▶ p_3
             │
            ...
```

Wichtig: Es ist **dasselbe RNN** in jedem Zeitschritt — dieselben Gewichte `W_xh`, `W_hh`, `W_hy`. Wir nennen das **Weight Sharing über die Zeit**, analog zum Weight Sharing über den Raum beim CNN.

**Größenordnungen:**
- Vokabular: V = **1 636** (identisch mit Word2Vec)
- Embedding-Dim: D = **64** (vortrainiert und **festgehalten**)
- Hidden-State: H = **128**
- Parameter im RNN: H·D + H·H + V·H ≈ **234 000**
- Zusätzlich: ~100 000 Embedding-Parameter (kommen fertig aus Word2Vec und werden nicht mehr angepasst)

Die Embeddings selbst passen wir *nicht* mehr an — das RNN lernt nur die Sequenz-Struktur, die Semantik kommt aus Word2Vec. Genauso hat man 2013–2017 in der Praxis gearbeitet.

---

## ⚙️ Training: Backpropagation Through Time (BPTT)

Weil das Modell in der Zeit aufgefaltet ist, muss der Backprop-Algorithmus **rückwärts durch die Zeit** laufen. Für jede Sequenz der Länge T:

1. **Forward:** Berechne `h_1, ..., h_T` und `p_1, ..., p_T`.
2. **Backward:** Beginne bei t=T, propagiere den Fehler durch alle Zeitscheiben.
3. **Update:** Adagrad-Schritt.

Wir verwenden **Sequence Length = 20 Wörter** (etwa eine Grimm-typische Satzhälfte). Der Hidden-State läuft *zwischen* den Sequenzen weiter — das Netz vergisst nicht am Batch-Ende.

**Wichtig:** Gradient Clipping (`np.clip(g, -5, 5)`) gegen explodierende Gradienten. Ohne Clipping wachsen die Gradienten bei tiefer Zeitfaltung exponentiell — der Effekt ist so bekannt, dass er als „exploding gradients" ein Standard-Kapitel in Deep-Learning-Lehrbüchern hat.

**Hyperparameter:**
- Trainings­schritte: 3 000
- Batch-/Sequenz-Länge: 20
- Optimierer: Adagrad
- Gradient Clipping: ±5

---

## ▶️ So startest du das Programm

**Wichtig:** Meilenstein 4 (Word2Vec) muss einmal gelaufen sein — die Datei `Word2Vec/src/embeddings.npz` wird geladen. Falls sie fehlt:

```bash
cd Word2Vec/src
python main.py
```

Dann:

```bash
cd RNN/src
python main.py
```

Das Programm trainiert 3 000 Schritte (~1 Minute auf CPU) und gibt am Ende vier Fortsetzungen zu verschiedenen Prompts aus.

---

## 📈 Beispielausgabe (echter Trainingslauf, 67 s auf CPU)

```
[Embeddings] V=1636, D=64
[Model] WordRNN  V=1636  D=64  H=128  Parameter: ~234,000

Schritt    1  loss=148.0 (7.40/Wort)
  the king safely stop remain loudly son stall murderers tune make ...
  -> komplett zufaellige Wortsuppe

Schritt 1000  loss=142.1 (7.11/Wort)
  the king saw there she gate now go so it a goose they said she into
  of or now took they what into all to so ...
  -> das Netz "traut" sich haeufige Woerter (the, a, to)

Schritt 2000  loss=124.2 (6.21/Wort)
  the king in food he to the never the miller and but as you in him
  cried went the man table and the its there wine and why the miller ...
  -> Wortpaare wie "the miller", "the man", "the water" erkennbar

Schritt 3000  loss=111.9 (5.59/Wort)
  the king at the fire said well as she ran a little tree so she went
  so a beautiful woman was play singing her me my marleen son fell ...
  -> fast Grammatik. "little marleen" ist eine Figur aus dem
     Grimm-Maerchen "The Juniper Tree" - das Netz hat gelernt,
     in welchem Kontext sie steht!
```

**Finale Samples nach dem Training (Temperature = 0.7):**

```
[once upon a time] ->
  once upon a time but the poor went of the air in the fire were the
  little and is it little marleen and now me and a little and and ran
  to the sun and fell my wife was burning little marleen and took

[the king said] ->
  the king said i but not see the head but the bird and the marleen
  tree and case were a middle and rejoiced but that the marleen and
  the shoes and cried to the i is gone the juniper the frederick

[the wolf] ->
  the wolf is well if away the father and that they were others and
  then the father but passed she and when the roof and the little and
  passed and at the bird and sat and she took she ate the bird

[in the forest] ->
  in the forest and said the little of the bird and then the house and
  with the of the bird and they were well he were her head and she
  were her so when his spot and his servant and were her and
```

**Und der Star des Kapitels — Grimm-Figuren tauchen auf:**

*marleen*, *juniper*, *frederick*, *miller*, *wolf*, *bird* — genau die Namen und Figuren, die auch in den originalen Grimm-Märchen vorkommen. Das RNN hat gelernt, in welchen Kontexten diese Wörter stehen. Es kann noch keine perfekten Sätze bilden, aber es *klingt* schon deutlich grimm-ähnlich.

Zusätzliche Beobachtungen:

- **Alle Wörter sind echte Grimm-Wörter.** Das Modell wählt aus einem 1636-Wörter-Vokabular — es kann keine erfundenen Wörter erzeugen. Damit sieht der Text sofort „grimm-artig" aus.
- **Grammatik wackelt**: Kein perfekter englischer Satz, aber Subjekt-Verb-Objekt kommt oft vor (*„she ran a little tree"*, *„my wife was burning"*).
- **Der Loss fällt sichtbar** von ~7.4 (Zufall) auf ~5.6 nach 3 000 Schritten.

Ein perfektes Sprachmodell für Grimm-Englisch läge bei einem Verlust von ~3.0–3.5. Wir sind also **auf halbem Weg zwischen Zufall und Perfektion** — solide für ein Vanilla-RNN nach einer Minute Training.

---

## ❗ Ehrliche Diskussion: Zwei tiefe Grenzen

Unser Wort-RNN funktioniert erstaunlich gut für so wenig Aufwand. Aber es hat zwei fundamentale Probleme, die sich sofort in der Ausgabe zeigen.

### Grenze 1: Vanishing Gradient (langer Kontext)

Bei BPTT wird der Gradient in jedem Zeitschritt mit `W_hh` multipliziert. Nach 30 Zeitschritten ist `W_hh` 30 Mal durchmultipliziert — wenn seine Eigenwerte kleiner als 1 sind, schrumpft der Gradient exponentiell gegen null. Das RNN kann Information über weite Distanzen **nicht mehr propagieren**. Der Anfang eines Satzes ist am Ende „vergessen".

Konkret in unserer Ausgabe: *„the wolf is well if away the father and that they were others..."* — der *„wolf"* am Anfang hat keinerlei Einfluss mehr auf das, was 8 Wörter später generiert wird. Das Netz plappert lokale Wahrscheinlichkeiten aneinander.

### Grenze 2: Sequenzielle Verarbeitung (nicht parallelisierbar)

RNNs müssen Wörter **strikt nacheinander** verarbeiten. Man kann sie nicht parallelisieren. Auf einer modernen GPU mit Tausenden Kernen ist das eine massive Verschwendung — das Modell nutzt nur einen Bruchteil der verfügbaren Rechenleistung.

### Rettungsversuche

**LSTM** (Hochreiter & Schmidhuber 1997) löst Grenze 1 mit Gates und einem separaten Zell-Zustand, durch den der Gradient fast unverändert fließen kann. LSTMs haben RNNs 15 Jahre lang beherrscht (Google Translate 2016 lief darauf).

**Aber Grenze 2 blieb.** Und deshalb kam 2017 der Transformer und ersetzte alles.

Wir sprechen beides in Meilenstein 6 (Seq2Seq + Attention) und Meilenstein 7 (Transformer) an.

---

## 📝 Übungen

**1. Temperature spielen lassen.** In `main.py` beim Final-Sample `temperature=0.3` — der Text wird „sicherer", stur. Bei `temperature=1.5` wird er kreativ, aber wilder. Der Regler existiert bei jedem Sprachmodell, auch bei ChatGPT.

**2. Länger trainieren.** Setze `NUM_STEPS = 10_000`. Der Loss fällt weiter — irgendwann setzt Overfitting ein. Wo ist der Kipppunkt?

**3. Eigenen Prompt nutzen.** Ergänze in `main.py` eigene Prompts wie *„the poor man had"*, *„long ago"*, *„my daughter"*. Welche Fortsetzungen entstehen?

**4. Hidden-Size variieren.** `HIDDEN_SIZE = 64` (klein) vs. `256` (groß). Bei 64 wird der Text stumpfer, bei 256 dauert das Training deutlich länger — der Gewinn ist begrenzt, weil unsere Trainingsdaten klein sind.

**5. Wortkette messen.** Zähle im Sample, wie oft dasselbe Wort direkt hintereinander vorkommt (*„and and"*, *„the the"*). Ein gutes Modell tut das kaum — bei uns passiert es öfter, weil der Kontext zu kurz ist.

---

## 🧭 Wo stehen RNNs heute?

**Kurz gesagt:** Aus der Sprachverarbeitung sind sie fast komplett verschwunden. Aber ihre Ideen leben weiter.

- **In der Praxis verdrängt.** Zwischen 2010 und 2017 waren LSTMs (Hochreiter & Schmidhuber 1997) der Standard für alles rund um Sprache: Übersetzung, Textklassifikation, Named-Entity-Erkennung, Chatbots. Ab 2017/2018 haben **Transformer** sie in fast allen Sprach-Aufgaben überholt — meist deutlich. Google Translate lief nur etwa ein Jahr auf LSTMs (2016–2017), dann wurde die Architektur auf Transformer umgestellt.
- **Warum genau der Wechsel?** Nicht primär wegen des Vanishing-Gradient-Problems — das hatten LSTMs schon weitgehend gelöst. Der entscheidende Punkt war die **Nicht-Parallelisierbarkeit**. Transformer verarbeiten die ganze Sequenz auf einmal parallel — daher lassen sie sich viel größer trainieren.
- **Wo RNNs heute noch leben**: Zeitreihen­analyse (Aktien, Sensorik), kleine On-Device-Modelle (Wake-Word-Erkennung „Hey Siri"), einfache Signalverarbeitung, viele Embedded-Systeme. Immer dann, wenn die Daten wirklich zeitlich fließen und der Speicher knapp ist, sind LSTMs/GRUs eine gute Wahl.
- **Konzeptioneller Erbe**: Die Aufgabe *„sag das nächste Wort vorher"*, die du hier gerade trainiert hast, ist **wortgleich** die Aufgabe, mit der GPT trainiert wird. Nur benutzt GPT keine Rekurrenz mehr, sondern Attention über ein festes Kontextfenster. Das Objective ist dasselbe geblieben, die Architektur nicht.

Karpathys „char-RNN"-Blogpost (2015) markiert bis heute den didaktischen Höhepunkt der RNN-Ära — und war für viele der erste Moment, in dem sichtbar wurde, dass neuronale Netze eigenständig Text erzeugen können.

---

## 🧠 Abschließende Bemerkungen

Wenn du dir dieses Kapitel angesehen hast, hast du drei zentrale Ideen der Sprachmodellierung in Aktion gesehen:

1. **Weight Sharing über die Zeit.** Dasselbe RNN wird an jedem Zeitschritt angewandt — genauso wie beim CNN derselbe Filter über jede Bildposition gleitet. Weight Sharing ist der Kern aller Architekturen, die mit *variablen* Eingabegrößen umgehen können.
2. **Selbstüberwachtes Lernen aus Text.** Wir mussten keine Labels vergeben — der Grimm-Text hat sich selbst gelabelt. Dieselbe Idee steckt in Word2Vec, in GPT, in BERT. Es ist *das* zentrale Trainings-Objective der modernen KI.
3. **Cross-Entropy pro Wort** ist der Standard-Messwert eines Sprachmodells. Ab hier wird er uns bis zu Mini-GPT begleiten.

Und eine subtile, aber wichtige Einsicht: **Das RNN hat kein Bewusstsein für Bedeutung, nur Wahrscheinlichkeit.** Es sagt nicht „ich glaube, es geht um einen König", sondern nur „nach *the* kommt oft *king*". Aus dieser einfachen Zutat ergibt sich alles Weitere — auch die Illusion von Verständnis, die moderne LLMs erzeugen. Wer hier scharf hinsieht, versteht besser, was Sprachmodelle *tatsächlich* tun.

---

## 🚀 Nächstes Kapitel: Seq2Seq mit Attention

Unser RNN kann *„das nächste Wort vorhersagen"* — das ist bereits eine echte Sprachmodell-Aufgabe. Aber viele wichtige Anwendungen brauchen mehr, allen voran die **maschinelle Übersetzung**:

> Erst den kompletten Satz auf Deutsch verstehen, **dann** einen kompletten Satz auf Englisch erzeugen.

Ein einzelnes RNN kann das nicht sauber — es müsste beim ersten deutschen Wort schon anfangen, Englisch zu produzieren. Was dazu fehlt, ist eine **Encoder-Decoder-Struktur**: ein RNN liest die Eingabe komplett und komprimiert sie zu einem *Bedeutungsvektor*; ein zweites RNN erzeugt daraus die Ausgabe Wort für Wort.

Genau dieser Aufbau — **Seq2Seq** (Sutskever, Vinyals, Le 2014; Cho et al. 2014) — war der Durchbruch der neuronalen maschinellen Übersetzung. **Google Translate** wechselte im November 2016 auf ein solches System („GNMT", Google Neural Machine Translation) und übertraf damit erstmals die jahrzehntelang dominierenden statistischen Systeme deutlich.

Ein Jahr später kam **Bahdanau et al. (2015)** mit dem entscheidenden Zusatz: **Attention**. Der Decoder muss sich nicht mehr auf einen einzigen Bedeutungsvektor verlassen — er darf jederzeit auf jede Stelle der Eingabe zurückblicken. Das war der Baustein, der 2017 zum Transformer wurde.

Als Übungsaufgabe wählen wir eine kleine Übersetzung mit sichtbarer Struktur: **Zahlen (z. B. `23`) → Wortform (`twenty-three`)**. Dort können wir die Attention-Matrix wunderschön visualisieren.

---

## 📚 Referenzen

- Elman, J. L. (1990). *Finding Structure in Time*. Cognitive Science, 14(2).
- Hochreiter, S., & Schmidhuber, J. (1997). *Long Short-Term Memory*. Neural Computation, 9(8).
- Bengio, Y., Ducharme, R., Vincent, P., & Jauvin, C. (2003). *A Neural Probabilistic Language Model*. JMLR.
- Mikolov, T., Karafiát, M., Burget, L., Černocký, J., & Khudanpur, S. (2010). *Recurrent Neural Network Based Language Model*. Interspeech.
- Sutskever, I., Vinyals, O., & Le, Q. V. (2014). *Sequence to Sequence Learning with Neural Networks*. NeurIPS. arXiv:1409.3215.
- Cho, K. et al. (2014). *Learning Phrase Representations using RNN Encoder-Decoder for Statistical Machine Translation*. EMNLP. arXiv:1406.1078.
- Bahdanau, D., Cho, K., & Bengio, Y. (2015). *Neural Machine Translation by Jointly Learning to Align and Translate*. ICLR. arXiv:1409.0473.
- Karpathy, A. (2015). *The Unreasonable Effectiveness of Recurrent Neural Networks*. karpathy.github.io/2015/05/21/rnn-effectiveness/
- Wu, Y. et al. (2016). *Google's Neural Machine Translation System*. arXiv:1609.08144.
