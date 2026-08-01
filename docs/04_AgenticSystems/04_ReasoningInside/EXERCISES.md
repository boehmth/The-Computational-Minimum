# Übungen · Kapitel 4

Zwei Übungen. Beide zwingen dich zu einem Perspektiv-Wechsel, der über die einzelne Miniatur hinausgeht.

---

## Übung 1 · Der Preis von "reasoning: high"

`01_thinking_visible.py` läuft mit `reasoning="high"`. In `common/llm.py` wird das für Anthropic in `budget_tokens=8192` übersetzt (siehe `_reasoning_budget`).

**Aufgabe:** Ändere den `reasoning`-Parameter im Aufruf des zweiten Modells auf `"minimal"`, dann auf `"medium"`. Lauf jeweils. Trage in einer Tabelle ein:

| Level | budget_tokens | thinking-Tokens tatsächlich | answer-Tokens | Wandzeit |
|---|---|---|---|---|
| minimal | 512 | ? | ? | ? |
| medium | 2048 | ? | ? | ? |
| high | 8192 | ? | ? | ? |

Beantworte danach:

1. Bekommt Claude für alle drei Level trotzdem die richtige Antwort auf die Tank-Aufgabe?
2. Ab welchem Level ändert sich die Antwort-**Qualität** hörbar (Zwischen-Schritte werden weggelassen, Zahlen sind gerundet, etc.)?
3. Wenn du einen Agenten baust, der Millionen Aufrufe pro Tag macht — wie würdest du entscheiden, welches Level du nimmst?

**Was du lernst:** dass `reasoning: high` kein "Qualitätsschalter" ist, sondern ein **Kosten-Latenz-Qualität-Trade-off**. Für die meisten produktiven Aufrufe reicht `minimal`. Für die knappen 5% harter Aufgaben lohnt sich `high`. Der Trick ist zu wissen, welche 5% das sind — oder ein Router-Modell einzusetzen, der die Aufrufe vor-sortiert (siehe Kapitel-Slide-19 des begleitenden Foliensatzes: *"small / fast" als Router*).

---

## Übung 2 · Was der Provider dir vorenthält

Das Skript zeigt, dass Anthropic Claude die Thinking-Tokens *sichtbar* macht, OpenAI's o-Serie hingegen nur die *Zahl* über `usage.reasoning_tokens` zurückgibt. In der Provider-Matrix am Ende des Outputs steht das schwarz auf weiß.

**Aufgabe · Denk-Übung, keine Programmier-Übung:**

Nimm an, du baust einen Agenten für den SAP-Kontext: einen Genehmigungsagenten, der Rechnungen prüft und *"annehmen / ablehnen / Klärung anfordern"* empfiehlt. Der Agent nutzt ein reasoning-Modell.

1. **Compliance-Frage:** Ein Auditor prüft dein System und will für jede Empfehlung des Agents den *Rechenweg* im Prüfprotokoll sehen. Kannst du dieselbe Anforderung mit OpenAI o3 erfüllen wie mit Claude 4.5? Wo ist das Problem, und wie könntest du es umgehen (Hinweis: du kannst das Modell im finalen `text`-Feld darum bitten, den Rechenweg noch einmal explizit zu wiederholen — was aber Tokens kostet und nicht garantiert *derselbe* Rechenweg ist, den das Modell intern hatte).
2. **Kosten-Frage:** o3 sampled intern N Reasoning-Traces und wählt die beste (siehe README). Ein Auditor fragt dich: *"Wenn ich denselben Fall zweimal einreiche, bekomme ich dann dieselbe Antwort?"* — Wie antwortest du präzise? (Hinweis: der Auditor stellt implizit die Frage nach Determinismus. In Kapitel 6 kommt diese Frage in einer eigenen Miniatur wieder.)
3. **IP-Frage:** Anthropic zeigt die Thinking-Tokens im Response. OpenAI verbirgt sie. Denk dir mindestens *einen* geschäftlichen Grund aus, warum ein Anbieter das eine oder das andere tut. Und einen Grund für einen SAP-Kunden, warum das eine oder das andere für ihn besser ist.

**Was du lernst:** dass die Wahl des reasoning-Modells nicht nur eine technische Entscheidung ist — sie ist auch eine Compliance-, Kosten- und Vertragsentscheidung. Für einen internen ChatBot ist das egal; für einen Genehmigungsagenten mit Audit-Anforderungen ist es kritisch.

---

## Wie du wissen kannst, dass du dieses Kapitel verstanden hast

Wenn du in **einem Satz** erklären kannst: *"Ein reasoning-Modell führt einen Loop *innerhalb* eines HTTP-Aufrufs aus — der Loop lebt in der autoregressiven Token-Generierung und liest sein eigenes Thinking als Kontext für die nächsten Tokens; der Entwickler kontrolliert nur `budget_tokens`, nicht die einzelnen Schritte."* — dann bist du fertig mit Kapitel 4.

Und wenn du dann noch weißt, dass es *drei* Loop-Kategorien gibt (deiner in Kapitel 3, das Modell in Kapitel 4, und der unsichtbare Best-of-N-Loop beim Provider) — dann bist du wirklich fertig.