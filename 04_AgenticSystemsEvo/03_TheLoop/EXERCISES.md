# Übungen · Kapitel 3

Drei Übungen. Sie erfordern, dass du den Loop nicht nur läufst, sondern *modifizierst*. Da liegt die Substanz.

---

## Übung 1 · Kontext-Hygiene

`02_token_growth.py` zeigt: `tokens_in` wächst mit jedem Turn, weil die gesamte Konversation neu mitgeschickt wird. Bei einem 5-Turn-Loop kann `tokens_in` in Turn 5 leicht 4× so groß sein wie in Turn 1.

**Aufgabe:** Modifiziere `02_token_growth.py`, sodass **zwischen den Turns die Werkzeug-Ergebnisse verdichtet werden**. Konkret:

1. Nach jedem Werkzeug-Aufruf, statt das ganze rohe Ergebnis in die History zu schreiben (z.B. `[observation] fetch_news({...}) = {"headlines": [3 lange Sätze]}`), schreibe nur eine ein-Satz-Zusammenfassung (z.B. `"news: 3 headlines about SAP SE"`).
2. Lauf das Skript wieder. Vergleiche die Token-Kurve mit dem Original.

**Was du lernst:** *Kontext-Hygiene* ist eine der billigsten und wirkungsvollsten Optimierungen im Agent-Loop. Sie ist genau das, was `docs/03-principle-3-loop.md` unter "Punkt 4" listet. Und sie ist immer *dein* Job, kein Framework macht sie richtig.

**Bonus:** Statt nach jedem Turn zu verdichten, sammle die letzten drei rohen Observations und verdichte den *Rest*. Warum ist das besser als "verdichte alles"? (Hinweis: das Modell braucht die frischen Details für die Entscheidung im aktuellen Turn.)

---

## Übung 2 · Ein zweiter Loop-Guard

`01_basic_loop.py` hat einen Loop-Guard, der bricht, wenn dieselbe Werkzeug-Signatur (Name + Args) dreimal in Folge kommt. Aber es gibt eine subtile Variante, die er *nicht* fängt: was, wenn das Modell zwischen zwei Werkzeug-Calls hin- und herflippt?

```
Turn 1: calculator(multiply, 100, 5) = 500
Turn 2: calculator(divide, 500, 5)   = 100
Turn 3: calculator(multiply, 100, 5) = 500
Turn 4: calculator(divide, 500, 5)   = 100
...
```

Der Modell dreht sich im Kreis, aber keiner der Einzel-Calls wiederholt sich sofort.

**Aufgabe:** Erweitere den Loop-Guard so, dass er **auch kurze Zyklen** erkennt (Länge 2 oder 3). Konkret:

1. Führe eine Liste der letzten N Werkzeug-Signaturen (z.B. N=6).
2. Prüfe bei jedem Turn: bilden die letzten K Einträge ein wiederholtes Muster (K ∈ {2,3})?
3. Wenn ja: brich ab und drucke welche Sequenz erkannt wurde.

**Was du lernst:** dass "es gibt keinen offensichtlichen Fehler" nicht dasselbe ist wie "der Agent macht Fortschritte". Loop-Guards in Produktion sind nie so einfach wie "ist der letzte Call der gleiche wie der davor". Zyklen-Erkennung ist ein eigenes Problem.

**Bonus:** Recherchiere den *"budget"* Ansatz — statt Turns zu zählen, zähle die kumulativen Kosten (in Tokens oder EUR). Warum ist das für einen kommerziellen Agent oft die *einzige* wirklich verlässliche Stop-Bedingung?

---

## Übung 3 · Retry der fünften Sorte

`03_retry_strategies.py` zeigt vier Strategien. Aber in der Praxis nutzt man selten nur eine — man *kombiniert*. Und es gibt eine fünfte Strategie, die im Skript fehlt:

> **E · "hedged" requests** — mach ZWEI Aufrufe *gleichzeitig*, an das primäre und an das Fallback-Backend. Nimm die erste Antwort, die zurückkommt. Wirf die zweite weg.

**Aufgabe:** Baue eine `strategy_hedged()` Funktion.

1. Nutze `concurrent.futures.ThreadPoolExecutor` oder `asyncio`.
2. Starte gleichzeitig `TOOL.price_lookup(SKU)` und `TOOL.fallback_lookup(SKU)`.
3. Nimm den ersten erfolgreichen Response.
4. Miss die Latenz.

Diskutiere danach:

- Wann ist Strategie E besser als D? (Hinweis: Latenz.)
- Wann ist sie schlechter als D? (Hinweis: Kosten.)
- Wann sollte man E *nicht* verwenden? (Hinweis: bei Seiteneffekten — z.B. wenn der Aufruf Datenbank-Schreiboperationen enthält.)

**Was du lernst:** dass Retry-Strategien keine Blackbox-Wahl sind — jede hat einen konkreten Trade-off (Latenz vs. Kosten vs. Sicherheit), und die richtige Wahl hängt vom Kontext ab. Große Cloud-Anbieter verwenden hedged requests routinemäßig für Read-Only-Operationen; für Write-Operationen fast nie.

---

## Wie du wissen kannst, dass du dieses Kapitel verstanden hast

Wenn du in **einem Satz** erklären kannst, warum der Satz *"the loop is yours to write"* für alle Agent-Systeme gilt — auch für die, die auf LangChain oder Semantic Kernel basieren — dann bist du fertig mit Kapitel 3.

In zwei Sätzen: das Framework schreibt dir den Loop, aber es entscheidet nicht für dich, welche Stop-Bedingungen du willst, welche Retry-Strategie zu welchem Fehler passt, oder wieviel Kontext du zwischen den Turns tragen willst. All das ist immer deine Entscheidung — und wenn du sie nicht bewusst triffst, hast du den Default gewählt.