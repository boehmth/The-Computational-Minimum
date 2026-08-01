# Kapitel 4 · Reasoning innen drin

**Der andere Loop — der, den nicht du geschrieben hast.**

Eine Miniatur. Sie schickt dieselbe Frage an zwei Modelle: ein normales gpt-4o und ein reasoning-fähiges Claude 4.5. Bei Claude siehst du zwei Textströme zurück — die privaten *thinking tokens* und die finale Antwort. Beides in einem einzigen HTTP-Aufruf.

---

## 📜 Historischer Kontext

Bis Kapitel 3 lebte der Loop in *deinem* Code. Jeder Turn war ein separater HTTP-Aufruf. Jede *"weiter oder fertig?"*-Entscheidung stand in einem `if` in deiner Python-Datei.

Das änderte sich im Herbst 2024.

**September 2024 · OpenAI o1.** Zum ersten Mal in einem kommerziellen Modell: das Modell "denkt" *bevor* es antwortet. Ein spezielles Training auf Reasoning-Traces (RLVR — Reinforcement Learning from Verifiable Rewards) hatte OpenAI ein Modell gegeben, das den Chain-of-Thought *nicht mehr im Prompt braucht* — es generiert ihn selbst, intern. Der User schickt eine Frage, wartet 10-60 Sekunden, und bekommt eine Antwort. Zwischen "Frage" und "Antwort" liegen Hunderte bis Tausende von Thinking-Tokens, für die er bezahlt, aber die er nicht sieht.

**Februar 2025 · Claude 3.7 extended-thinking.** Anthropic zieht nach — mit einem wichtigen Unterschied: die Thinking-Tokens sind für den Entwickler *sichtbar*, als eigenes Feld im API-Response. Man kann live zuschauen, wie das Modell mit sich selbst spricht, bevor es die finale Antwort formuliert.

**Frühjahr 2025 · DeepSeek-R1 open-weight.** Zum ersten Mal ein Reasoning-Modell zum Selbst-Hosten. Man kann jetzt die Gewichte herunterladen, das Modell auf eigener Hardware laufen lassen und die Thinking-Tokens im generierten Text direkt sehen (als `<think>...</think>`-Tags).

Zusammen ergaben diese drei Ereignisse eine neue Loop-Kategorie:

> **Der Loop lebt nicht mehr in deinem Code — er lebt im Modell selbst.**

Aus Sicht *deiner* API ist es weiterhin *ein* HTTP-Aufruf. Ein `chat()`-Call, ein Response-Objekt. Aber im Response-Objekt sind jetzt zwei Ströme statt einem — und für beide wird bezahlt.

---

## 🔬 Die eine Miniatur

### `src/01_thinking_visible.py` — der innere Loop, sichtbar gemacht

Dieselbe Aufgabe an zwei Modelle:

> *"Ein Tank fasst 240 Liter. Rohr 1 füllt mit 12 L/min, Rohr 2 mit 8 L/min, ein Abfluss leert mit 5 L/min. Alle laufen gleichzeitig. Wie lange bis der Tank voll ist?"*

**Modell A — gpt-4o (baseline):** ein normales one-shot Modell. Antwortet mit einem Rechenweg und einer Antwort, alles in einem Textstrom. Kein Thinking sichtbar. Der Rechenweg *ist* die Antwort.

**Modell B — Claude 4.5 Sonnet mit `thinking={"type": "enabled"}`:** das Modell produziert zwei getrennte Content-Blöcke:

- `content[type=thinking]` — der interne Chain-of-Thought (typisch 500-2000 Tokens für diese Aufgabe)
- `content[type=text]` — die finale, aufgeräumte Antwort (typisch 100-300 Tokens)

Das Skript zeigt beide Ströme in zwei getrennten `hard_card`s. Man sieht nebeneinander, was das Modell *denkt* und was es *sagt* — und wieviel Token jedes davon kostet.

Am Ende steht eine Provider-Matrix: welcher Anbieter zeigt die Thinking-Tokens im Response, wer versteckt sie, aber lässt dich dafür zahlen.

| Anbieter | Thinking im Response? | Feld |
|---|---|---|
| **Anthropic Claude** | ✓ ja | `content[type=thinking]` |
| **OpenAI o1/o3/o4** | ✗ nein — nur die Zahl | `usage.reasoning_tokens` |
| **Google Gemini 2.5+** | ✗ opt-in | `thinking_config.include_thoughts=True` |
| **DeepSeek-R1** | ✓ ja | `<think>...</think>` inline |

---

## 💡 Wow-Moment

Wenn du das Skript zum ersten Mal laufen lässt, wirst du zwei Sachen bemerken:

**1. Der Thinking-Block ist länger als die Antwort.** Für die Tank-Aufgabe rechnet Claude sich vielleicht 800 Tokens durch, bevor es dann 150 Tokens Antwort liefert. Das ist eine ungefähre 5:1-Ratio. Bei komplexeren Aufgaben wird es noch extremer.

**2. Der Rechenweg im Thinking ist *besser* als der im gpt-4o-Response.** Nicht weil Claude schlauer ist — sondern weil Claude sich *selbst zuhört*. Es macht Zwischenschritte, verifiziert, korrigiert. Es rechnet: *"Netto-Fluss = 12 + 8 - 5 = 15 L/min. Zeit = 240 / 15 = 16. Prüfen: 16 min × 15 L/min = 240 ✓."* Das *"Prüfen"* am Ende ist der Kern — das Modell testet die eigene Antwort *vor* der Abgabe.

Das ist qualitativ dasselbe wie in Kapitel 3 Miniatur 3 Strategie D (LLM-guided recovery). Nur dass es hier automatisch passiert, in einem einzigen Aufruf, unsichtbar für alle außer denen, die genau danach fragen.

**Was du nicht siehst — und wofür du trotzdem zahlst:** wenn du OpenAI o3 mit `reasoning_effort="high"` nutzt, sampled der Provider intern *N* verschiedene Reasoning-Traces parallel und wählt die beste. Diese *N* Traces werden dir nicht gezeigt (auch nicht anonym) und du bekommst nur die eine gewählte Antwort — aber die Token-Rechnung ist für alle *N*. Das erklärt, warum "reasoning: high" 5-20× mehr kostet als "reasoning: minimal" ohne dass die sichtbare Antwort länger wird.

Deswegen: **drei Loop-Ebenen, drei Kontroll-Ebenen.** Dein Loop (Kapitel 3), der Loop im Modell (Kapitel 4 Miniatur 1), und der Loop beim Provider (unsichtbar). Für jeden zahlst du. Nur den ersten kontrollierst du.

---

## 🚀 Ausführen

```powershell
cd "C:\Users\<USERNAME>\Source\RPT Agent"
python "Agentic Systems/04_ReasoningInside/src/01_thinking_visible.py"
```

Voraussetzung: das reasoning-Modell muss in deinem GenAI Hub Resource Group deployed sein. Setze in `.env`:

```
LLM_REASONING_MODEL=anthropic--claude-4.5-sonnet
```

(Bei anderen Modellen wie `anthropic--claude-4.5-opus` oder o3 ändert sich das Level der Details, aber das Muster bleibt gleich.) Erwartete Laufzeit: 10-60 Sekunden pro Modell — reasoning-Modelle sind absichtlich langsam, das *ist* der Trade-off.

---

## 🧭 Brücke zum nächsten Kapitel

Kapitel 3 zeigt: **der Loop kann in deinem Code leben.** Kapitel 4 zeigt: **der Loop kann im Modell leben.** In beiden Fällen ist der Loop *lokal* — er lebt bei dir und dem Modell. Nur zwei Parteien sind beteiligt.

In Kapitel 5 kommt die dritte Partei dazu: **fremde Werkzeuge und fremde Agenten**, die über ein standardisiertes Protokoll erreichbar sind. Das ist der Punkt, an dem sich die Werkzeuge deiner Kollegen (oder eines fremden Anbieters) nahtlos in deinen Loop einklinken können — ohne dass du für jedes Werkzeug einen bespoke API-Wrapper schreibst.

Das Protokoll heißt **MCP** (Model Context Protocol, Anthropic, November 2024). Und weil auch Agenten miteinander sprechen sollen, gibt es seit Anfang 2025 die Erweiterung: **A2A** (Agent-to-Agent, Google).

Beide sind in Kapitel 5 als lauffähige Miniaturen.