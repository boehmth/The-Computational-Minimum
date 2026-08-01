# Übungen · Kapitel 6

Drei Übungen. Alle drei sind Fragen an *dich*, nicht ans Modell. Am Ende sollte dein Urteil belastbarer sein.

---

## Übung 1 · Wende den Zwei-Fragen-Test an

Für JEDE der folgenden real vorgeschlagenen "Agent-Projekte", entscheide anhand des Zwei-Fragen-Tests aus dem Kapitel-README: **Agent, deterministische Funktion, oder Mensch mit Assistent?** Begründe in ein bis zwei Sätzen.

1. Ein Bot, der automatisch **Urlaubsanträge** genehmigt: dauer < 5 Tage, kein Sperrfenster, Resturlaub reicht.
2. Ein System, das den **passendsten Support-Bearbeiter** für ein eingehendes Ticket auswählt (aus einem Team von 200 Personen).
3. Ein System, das eine eingehende **Kundenzuschrift automatisch beantwortet**.
4. Ein System, das aus einem **Vertragstext** die 5 wichtigsten Risiken extrahiert.
5. Ein System, das entscheidet, ob eine **Rechnung über 10.000 EUR** freigegeben wird.
6. Ein System, das die **monatliche Umsatzsteuervoranmeldung** vorbereitet und einreicht.
7. Ein System, das aus **Sales-Meetings** automatisch die vereinbarten nächsten Schritte extrahiert.
8. Ein System, das für einen Kunden mit einer **Reklamation** eine erste Rückantwort verfasst.

**Was du lernst:** dass die Antwort selten *"ja Agent"* oder *"nein Funktion"* ist. Meistens ist sie: *"Agent für Klasse A der Fälle, Funktion für Klasse B, Mensch mit Assistent für Klasse C, und die Klassifizierung selbst kann ein LLM übernehmen"*. Genau das ist der Router-Ansatz aus Kapitel 4 in einer neuen Verpackung.

---

## Übung 2 · Repariere den Determinismus

`02_determinism_check.py` zeigt: mit `temperature=0` bekommst du nicht garantiert dieselbe Antwort zweimal. In der Praxis brauchst du für regulierte Prozesse trotzdem *Wiederholbarkeit*.

**Aufgabe:** Baue einen `deterministic_chat()`-Wrapper um `chat()` aus `common/llm.py`, der:

1. Aus dem Prompt einen deterministischen Hash macht (SHA-1 über `system` + `user` + `model`).
2. Wenn ein cached Response für diesen Hash existiert (in `.llm_cache/<hash>.json`), lade und return.
3. Wenn nicht, mache den echten Aufruf, cache das Response, dann return.

Danach führe `02_determinism_check.py` mit deinem Wrapper aus. Alle fünf Runs sollten jetzt zeichengleich sein.

**Was du lernst:** dass *Determinismus* im LLM-Kontext praktisch immer *Caching* heißt — nicht ein Property des Modells, sondern ein Property deiner Architektur. Genau das ist der Punkt: *"Reproduzierbarkeit ist eine Architektur-Eigenschaft deines Systems drumherum"*.

**Bonus:** Wie lange sollte der Cache leben? Für ein Freigabe-System, das gestern eine Rechnung freigegeben hat — soll der Cache dem heute wieder freigegeben werden? Was, wenn zwischen den beiden Anfragen die Regel geändert wurde? (Hinweis: der Cache-Key sollte auch die *Version* der Regeln hashen, nicht nur den Eingabetext.)

---

## Übung 3 · Der ehrlichste Anti-Muster-Fall

Nimm einen Prozess aus deiner eigenen Arbeit — einen, den du selbst schon einmal überlegt hast zu "automatisieren mit einem Agenten". Sei ehrlich zu dir selbst.

Beantworte schriftlich:

1. **Was ist der eigentliche Business-Wert?** — Nicht das Feature, das ich bauen will, sondern das Outcome, das dahinter steht.
2. **Wie sähe die "unglamouröse Lösung" aus?** — Eine Kombination aus ein paar `if`-Verzweigungen, einer Datenbank-Query, und einer Freigabe-UI für Menschen. Ohne LLM.
3. **Woran WÜRDE ich merken, dass die unglamouröse Lösung nicht reicht?** — Was ist der konkrete Grenzfall, an dem der Prozess ein Modell wirklich braucht?
4. **Ist dieser Grenzfall häufig genug, dass er die Agent-Architektur rechtfertigt?** — Wenn er in 3% der Fälle vorkommt, könnte ein "unglamouröse-Lösung + Mensch-Freigabe für den Rest" reichen.
5. **Was ist der Fehlerkosten-Vergleich?** — 5% falsche Empfehlungen des LLM-Agents gegen 15% übergebene Fälle an einen Menschen bei der unglamourösen Lösung — was ist teurer für das Unternehmen?

Wenn du am Ende zu dem Schluss kommst, dass die unglamouröse Lösung reicht: **hast du gerade eine Menge Zeit gespart**. Wenn nicht: du hast jetzt eine viel bessere Begründung für dein Agent-Projekt als "wir wollen KI machen".

**Was du lernst:** dass die härteste Übung dieses ganzen Kapitels *nicht Kode-schreiben* ist. Sie ist *ehrliche Selbstauskunft*. Und sie ist zufällig genau die, die dich als Ingenieur oder Ingenieurin von einem Enthusiasten mit einem GitHub-Copilot-Abo unterscheidet.

---

## Wie du wissen kannst, dass du das ganze Repo verstanden hast

Wenn du in **einem Absatz** einer Kollegin erklären kannst,

- *was* ein LLM ist (Kapitel 1),
- *warum* du ihm Werkzeuge gibst (Kapitel 2),
- *wie* du einen Loop drumherum baust und was er kostet (Kapitel 3),
- *dass* manche Modelle den Loop drin haben (Kapitel 4),
- *warum* MCP und A2A die Werkzeug-Landschaft skalieren (Kapitel 5),
- und *wann* du all das nicht brauchst (Kapitel 6) —

...**alles ohne einen einzigen Framework-Namen zu nennen** — dann kannst du für den Rest deines Berufslebens fundierte Entscheidungen über Agent-Architekturen treffen. Und das ist der eigentliche Gewinn dieses Repos.

Der Rest sind Details, die sich alle 18 Monate ändern.