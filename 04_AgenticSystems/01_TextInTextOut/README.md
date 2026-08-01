# Kapitel 1 · Text-in / Text-out

**Was ein LLM aus API-Sicht wirklich ist — und was es *nicht* ist.**

Zwei sechs-Zeiler, die zusammen das erste Prinzip beweisen und gleichzeitig zeigen, warum wir überhaupt Kapitel 2 bis 6 brauchen.

---

## 📜 Historischer Kontext

**1950** — Alan Turing veröffentlicht *"Computing Machinery and Intelligence"* und formuliert die Frage: *"Can machines think?"* Er beantwortet sie nicht direkt, ersetzt sie aber durch etwas Präziseres — den "Imitation Game", heute als Turing-Test bekannt. Der Test operationalisiert Intelligenz als *sprachliches Verhalten*: eine Maschine gilt als denkend, wenn ihr Textverhalten nicht von menschlichem zu unterscheiden ist.

Diese Definition ist genau die, die die LLMs heute erfüllen — nicht weil sie denken (das wäre die falsche Frage), sondern weil ihre Schnittstelle mit dem Rest der Welt genau eine ist: **Text hinein, Text heraus**.

Von den Symbol-Systemen der 60er (SHRDLU, ELIZA) über die statistische NLP der 90er bis zu den Transformer-Modellen der 2020er hat sich das Format nie geändert. Was sich radikal geändert hat: die Qualität dessen, was zwischen Ein- und Ausgabe passiert.

**2017** — Vaswani et al. veröffentlichen *"Attention Is All You Need"* — der Transformer. Von hier zieht sich die Linie ohne Bruch bis heute: GPT-1 (2018), GPT-2 (2019), GPT-3 (2020), ChatGPT (Nov 2022), GPT-4/Claude/Gemini (2023–), bis zu den Reasoning-Modellen der Kapitel 4.

**Der API-Vertrag ist von der ersten bis zur heutigen Generation derselbe geblieben**: ein Prompt geht rein, Text kommt zurück. Alles was wir in den restlichen fünf Kapiteln bauen, ist Code, der genau *diese eine Operation* geschickt orchestriert.

---

## 🔬 Die zwei Miniaturen

### `src/01_hello_llm.py` — die kleinste mögliche Demonstration

Ein einziger `chat()`-Aufruf. Der Prompt fragt nach der Hauptstadt von Frankreich. Das Modell antwortet. Der Output druckt Modellname, Token-Counts und die Antwort — nichts weiter.

**Warum das eigenständig ist:** weil es das Fundament setzt, das der Rest des Repos benutzt. Wenn dieses Skript bei dir läuft, hast du:
- eine funktionierende SAP-GenAI-Hub-Konfiguration (oder eine Gemini-Fallback-Konfiguration),
- den `common/llm.py`-Wrapper im Zugriff,
- verstanden, dass ein LLM-Call *aus der Sicht des Codes* nichts Anderes ist als ein HTTP-POST mit einem JSON-Body.

### `src/02_math_breaks.py` — die Motivation für alles was folgt

Derselbe API-Vertrag, aber jetzt eine Aufgabe, die das Modell *nicht* lösen kann: das Produkt zweier fünfstelliger Zahlen (`43,177 × 14,694`).

Das Modell antwortet mit einer plausiblen Zahl. Python daneben rechnet die richtige. Das Skript zeigt beide und die Differenz.

**Was hier passiert:** Das Modell hat gelernt, plausible Ziffern-Sequenzen zu produzieren — es sagt Zeichen für Zeichen die *wahrscheinlichste nächste Ziffer* vorher. Es hat nicht gelernt, zu multiplizieren. Die Antwort hat ungefähr die richtige Anzahl Ziffern und beginnt oft mit den richtigen führenden Ziffern (die Größenordnung stimmt), aber die mittleren und späten Ziffern sind Rauschen.

---

## 💡 Wow-Moment

Das Modell produziert Zahlen wie `634,297,638` oder `6,343,522,638` oder `633,942,838`. Der wahre Wert ist `634,442,838`.

Manchmal ist der Fehler klein (weniger als ein Prozent). Manchmal ist er groß (Faktor 10, weil eine Ziffer zu viel eingeschoben wurde). Beim Wiederholen des Aufrufs siehst du: jeder Lauf gibt eine *andere* falsche Antwort. Es gibt kein "wahres" Ergebnis in den Gewichten des Modells — es gibt nur eine Wahrscheinlichkeitsverteilung über die nächste Ziffer.

Das ist der pädagogische Anker für alles, was folgt: **wenn du eine deterministische Rechnung brauchst, brauchst du eine deterministische Rechen-Maschine — nicht das Modell.**

Aber das Modell *weiß*, dass es multiplizieren muss. Es liest den Prompt richtig. Es identifiziert die Operation. Es produziert nur nicht das richtige Ergebnis. Genau diese Trennung — *das Modell versteht die Aufgabe, aber die Ausführung gehört woanders hin* — ist die zentrale Erkenntnis, aus der Kapitel 2 entsteht.

---

## 🚀 Ausführen

Voraussetzung: `.env` im `RPT Agent`-Root ist gesetzt (siehe `../../.env.example`).

```powershell
cd "C:\Users\<USERNAME>\Source\RPT Agent"
python "Agentic Systems/01_TextInTextOut/src/01_hello_llm.py"
python "Agentic Systems/01_TextInTextOut/src/02_math_breaks.py"
```

Erwartete Ausgabe von `02_math_breaks.py`:

```
┌── DIE AUFGABE ──────────────────────────────────────────────────
│  Was ist 43,177 × 14,694?  Antworte NUR mit der Zahl.
└─────────────────────────────────────────────────────────────────

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ▸  Das MODELL rät (predict-next-token)                        ┃
┃     46 Tokens · gpt-4o                                         ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  634,297,638                                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ▸  PYTHON rechnet (deterministisch)                           ┃
┃     0 Tokens · Python-Multiplikation                           ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  634,442,838                                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌── DIFFERENZ ─────────────────────────────────────────────────────
│  Modell − Python   =   -145,200
│  Fehler in Prozent =   -0.02 %
│
│  Interpretation:  Größenordnung stimmt, mittlere Ziffern falsch.
│  Das Modell hat die Aufgabe verstanden — nicht ausgeführt.
└──────────────────────────────────────────────────────────────────
```

---

## 🧭 Brücke zum nächsten Kapitel

Wenn du diese zwei Skripte gelaufen hast, hast du zwei Dinge:

1. **Ein Vertrauen** in die Infrastruktur (`common/llm.py` funktioniert bei dir).
2. **Eine Frage**, die Kapitel 2 beantwortet: *wie kommen wir vom "Modell weiß was zu tun ist" zum "richtigen Ergebnis"?*

Die Antwort: gib dem Modell ein Werkzeug. Nicht damit es rechnet — sondern damit es *sagt*, was gerechnet werden soll, und der deterministische Teil außerhalb des Modells die eigentliche Rechnung macht.

Das ist Kapitel 2.