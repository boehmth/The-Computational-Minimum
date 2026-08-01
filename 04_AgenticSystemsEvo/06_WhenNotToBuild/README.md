# Kapitel 6 · Wann NICHT bauen

**Das Urteil.**

Bis hierhin hat jede Miniatur gezeigt *was möglich ist*. Dieses Kapitel zeigt *was nicht sinnvoll ist*. Zwei Miniaturen. Zwei Anti-Muster. Ein Zwei-Fragen-Test.

---

## 📜 Historischer Kontext

Nach Kapitel 5 stehst du am ungefährlichsten Punkt der Reise: alles ist möglich, alles skaliert, alles ist standardisiert. Das ist genau die Situation, in der die meisten schlechten Agenten-Systeme entstehen.

Zur Erinnerung, was wir gebaut haben:

- **Kapitel 1** — LLMs sind text-in / text-out. Aber sie rechnen nicht.
- **Kapitel 2** — Werkzeuge lösen das. Das Modell entscheidet zur Laufzeit welche Werkzeuge in welcher Reihenfolge.
- **Kapitel 3** — Wir bauen einen Loop drumherum. Er kostet 10× so viel wie ein one-shot Aufruf. Er kann fehlschlagen und muss retries können.
- **Kapitel 4** — Manche Modelle haben den Loop drin (reasoning). Auch das kostet.
- **Kapitel 5** — Werkzeuge und Agenten können standardisiert erreichbar sein. Skaliert wunderbar.

Jetzt kommt die unbequeme Frage: **wann lohnt sich das eigentlich?**

Anfang 2024 hat jeder Beratungspitch das Wort "Agent" enthalten. Anfang 2025 hat jede Enterprise-Roadmap "Agent-first" gesagt. Ende 2025 hat man in einigen dieser Projekte gemerkt, dass ein Batch-Job mit zwei `if`-Verzweigungen dieselbe Aufgabe billiger, schneller, deterministisch und auditbar erledigt.

Der Punkt dieses Kapitels: **die Agent-Architektur ist ein Werkzeug**, kein Standard-Layer. Wie jedes Werkzeug hat sie einen konkreten Einsatzbereich — und einen sehr großen Bereich außerhalb, in dem sie *schlechter* als die Alternative ist.

---

## 🔬 Die zwei Miniaturen

### `src/01_agent_vs_sum.py` — der maximal absurde Vergleich

Aufgabe: die Summe von `[1, 2, 3, 4, 5]`. Ergebnis: `15`. Kein Zweifel.

- **Weg A**: `sum([1, 2, 3, 4, 5])`. Fünf Zeichen Python. Läuft in ~1 Mikrosekunde. Kostet 0 Cent.
- **Weg B**: ein Agent, der einen `calculator`-Tool nutzt. Ein `chat()`-Aufruf, JSON-Parsing, Werkzeug-Dispatch, Response. Läuft in ~2 Sekunden. Kostet ~50-100 Tokens.

Die Miniatur führt beide durch und druckt die **Vergleichs-Tabelle**:

| | Latenz | Kosten (Tokens) | Determinismus | Auditbar |
|---|---|---|---|---|
| **A · Python `sum`** | 1 µs | 0 | ✓ | ✓ (Code) |
| **B · Agent** | ~2 s | ~80 | ✗ | teilweise |

Der Wow-Moment: der Faktor ~2.000.000 in der Latenz. Aber wichtiger: der Determinismus-Unterschied. Für `sum([1..5])` ist er im Kleinen absurd — für einen Batch-Job über eine Million Rechnungen wird er zur Existenzfrage.

### `src/02_determinism_check.py` — der harte Fall

Wir schicken **fünfmal denselben Prompt** an das Modell (`temperature=0`, was intuitiv "deterministisch" heißen sollte). Der Prompt: eine kleine mehrstufige Planungsaufgabe, die einen strukturierten Plan zurückgeben soll.

Wir vergleichen die fünf Antworten Zeichen für Zeichen:

- Sind alle fünf Antworten **identisch**?
- Wenn nicht: sind sie zumindest **semantisch gleich** (gleiche Struktur, gleiche Werte)?
- Wenn nicht einmal das: wo genau divergieren sie?

Empirisch: mit `gpt-4o` und `temperature=0` sind ~60-80% der Läufe zeichenidentisch, der Rest weicht in Reihenfolge, Formulierung oder Zwischenschritten ab. Bei komplexeren Aufgaben sinkt die Zeichenidentität schnell auf unter 50%.

**Der Punkt:** *"deterministisch"* im LLM-Kontext heißt nicht *"identische Antworten"*. Es heißt: *"identische Wahrscheinlichkeitsverteilung"* — aber die Server-Infrastruktur tut daran mit gebatchten Requests, Load-Balancing zwischen Regionen, und internem Best-of-N-Sampling. Selbst mit `temperature=0` sind Wiederholungen kein Vertrag.

Für einen Chatbot ist das egal. Für einen automatischen Freigabe-Prozess in einer regulierten Branche ist das ein Compliance-Defekt.

---

## 💡 Wow-Moment

Der eigentliche Wert dieses Kapitels ist **nicht** in den beiden Skripten. Er ist im **Zwei-Fragen-Test**, den du danach mitnimmst. Vor jedem Agent-Projekt frage:

1. **Braucht die Aufgabe Urteilsvermögen zur Laufzeit?**  
   Das heißt: gibt es einen Schritt, bei dem *ein Mensch* schauen würde, was das Ergebnis eines vorherigen Schritts war, und dann *entscheiden* würde, was als nächstes zu tun ist? Wenn ja, ist das ein Kandidat für einen Agenten. Wenn nein — wenn also die Ablauflogik vorher bekannt ist — dann sind `if`s und Funktionen billiger, schneller, deterministisch und auditbar.

2. **Kannst du eine falsche Antwort in zwanzig tolerieren?**  
   Das heißt: sind die Kosten eines Fehlers (finanziell, rechtlich, reputativ) so verkraftbar, dass ein 5% Fehlerraten-Modell akzeptabel ist? Wenn ja: guter Kandidat. Wenn nein — für einen Zahlungsfreigabe-Prozess, einen medizinischen Befund, eine Compliance-Prüfung — dann ist ein LLM-basierter Agent per Konstruktion falsch, und du brauchst deterministischen Code plus menschliche Freigabe.

**Nur wenn beide Fragen mit *Ja* beantwortet werden, war der Aufwand aus Kapiteln 1-5 gerechtfertigt.** Bei einem *Nein* auf Frage 1: `sum([1..5])`. Bei einem *Nein* auf Frage 2: `if regulated: refuse_agent`. Bei einem *Nein* auf beide: ein einfaches Python-Skript.

---

## 🚀 Ausführen

```powershell
cd "C:\Users\D041506\Source\RPT Agent"

python "Agentic Systems/06_WhenNotToBuild/src/01_agent_vs_sum.py"
python "Agentic Systems/06_WhenNotToBuild/src/02_determinism_check.py"
```

Erwartete Laufzeit: 5-20 Sekunden pro Skript. Miniatur 2 macht 5 LLM-Aufrufe, ist also teurer.

---

## 🧭 Zwischenbilanz — und die letzte Frage

Das war die eigentliche Reise. Sechs Meilensteine, gebaut aus insgesamt 11 kleinen ausführbaren Skripten:

| Kapitel | Miniaturen | Fokus |
|---|---|---|
| 1 · Text-in / Text-out | 2 | LLM als API-Objekt, warum Kalkulation nicht funktioniert |
| 2 · Werkzeuge & Pläne | 2 | dieselbe Aufgabe mit Werkzeug, drei Pläne für drei Prompts |
| 3 · Der Loop | 3 | echter Multi-Turn-Loop, Token-Wachstum, vier Retry-Strategien |
| 4 · Reasoning innen | 1 | thinking-Tokens sichtbar, Provider-Matrix |
| 5 · Protokolle & Skalierung | 2 | MCP-Server + Client, A2A-Client als Agent-Aufruf |
| 6 · Wann NICHT bauen | 2 | Agent vs. `sum`, Determinismus-Test |

Wenn du alle 11 Skripte einmal selbst gelaufen bist, hast du das Recht zu entscheiden, wann in deinem Kontext ein Agent das richtige Werkzeug ist — und wann eine Python-Funktion es besser tut. Das ist der eigentliche Skill. Nicht das Bauen. Das *Entscheiden ob*.

Aber jetzt kommt die letzte Frage. Der Foliensatz stellt sie in **Slide 44**: *"The question is no longer 'can it?' — it's 'should it?'"*. Wir haben in diesem Kapitel gelernt, sie zu beantworten. **Slide 45** stellt danach eine neue: *"Where are agents heading?"*.

---

## ↷ Wohin es geht — Kapitel 7

Slide 45 im Foliensatz zeichnet die Trajektorie in drei Stufen:

> **Fixed tools → Generated tools → Self-extending capability**

- **Heute** (Kapitel 1–6): Ein Ingenieur pflegt einen Werkzeug-Katalog. Das Modell wählt, sequenziert und ruft die Werkzeuge — kann aber nicht darüber hinausgehen, was ihm gegeben wurde. Joule, function-calling Agenten, MCP tool servers. Was du in diesem Repo gebaut hast.
- **Aufkommend**: Wenn das richtige Werkzeug nicht existiert, schreibt der Agent es zur Laufzeit — ein Python-Skript, ein SQL-Query, ein API-Client. Führt es aus, beobachtet, macht weiter. **Cline** arbeitet bereits so. **Der Foliensatz zu diesem Repo ist damit gebaut worden** (Slide 46: *"Every change was a script Cline wrote in the moment"*).
- **Als Nächstes**: Agents, die nicht nur Einweg-Skripte generieren, sondern neue Fähigkeiten *persistieren, testen und wiederverwenden* — die ihren Werkzeug-Katalog wachsen lassen und ihn über A2A anderen Agenten zur Verfügung stellen.

**Kapitel 7 ist die kleinstmögliche ehrliche Miniatur der mittleren Stufe.** Ein Agent ohne fest verdrahtete Werkzeuge. Wenn er etwas braucht, generiert ein zweites LLM den Python-Code, eine AST-Whitelist prüft ihn, eine Registry hält ihn. Die zweite Ausbaustufe persistiert den Katalog auf Platte — die dritte Stufe (Self-extending) im Kleinen.

Und der wichtigste Nachsatz gilt dann sofort: *"the boundary between using a tool and building one disappears — orchestration becomes where new capabilities are governed."* Das ist die zweite Ausprägung des Zwei-Fragen-Tests aus diesem Kapitel. Diesmal fragt sie nicht *"soll ich einen Agenten bauen?"*, sondern *"soll ich einem Agenten erlauben, selbst zu bauen?"* — und die Antwort hängt von einer neuen Sandbox-Politik ab, die es in Kap. 1-6 noch gar nicht gab.

→ Weiter in **[Kapitel 7 · Dynamic Tool Agent](../07_DynamicToolAgent/README.md)**.

---

## 📚 Zur weiteren Lektüre

- **Anthropic** — *Building Effective Agents* (2024). Der Klassiker über Agent-Muster.
- **Karpathy** — *Software 3.0* (2025 Talk). Die Framework-freie Perspektive.
- **Amodei** — *Machines of Loving Grace* (2024). Der ambitionierteste Ausblick.
- **Deutscher Bundesverband der Verbraucherzentralen** — *KI-Compliance-Leitfaden* (jährlich). Was in Deutschland tatsächlich gebaut werden darf.
- **EU AI Act** (2024, in Kraft ab 2026). Rechtsrahmen für hochriskante KI-Systeme — was ein *Agent* im rechtlichen Sinne ist, ist noch offen.