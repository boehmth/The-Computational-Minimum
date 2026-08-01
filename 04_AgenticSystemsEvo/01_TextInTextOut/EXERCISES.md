# Übungen · Kapitel 1

Drei Übungen. Jede zwingt dich, die Miniatur zu variieren — und das ist der einzige Weg, den Punkt wirklich zu verstehen.

---

## Übung 1 · Wie klein ist "klein"?

`01_hello_llm.py` ist etwa 25 Zeilen — die meisten davon sind Bootstrapping (import path, dotenv). Der eigentliche Nutz-Code ist ein einziger Aufruf.

**Aufgabe:** Baue ein *einzelnes* Skript `hello_smallest.py`, das mit **maximal zehn Zeilen** (Leerzeilen und Kommentare zählen nicht) einen LLM-Aufruf macht und die Antwort druckt. Wenn du `common/llm.py` verwendest, ist das leicht. Wenn du direkt gegen die SAP-GenAI-Hub-API gehst, ist das *hart* — du wirst OAuth, Deployment-Auflösung und JSON-Parsing selbst implementieren müssen.

**Was du lernst:** wie viel Infrastruktur unter dem `chat()`-Einzeiler wirklich steckt.

**Bonus:** Versuche das Ganze in **einer einzigen Zeile Python**. (Hinweis: mit `requests.post(...).json()["choices"][0]["message"]["content"]` und einem gültigen Bearer-Token in `AUTHORIZATION` als Environment-Variable geht es. Aber der Token muss vorher besorgt werden — das ist der Trick.)

---

## Übung 2 · Wie oft ist das Modell falsch?

`02_math_breaks.py` macht einen einzigen Aufruf. Aber das Modell antwortet bei jedem Aufruf leicht anders — wir sehen das nicht, weil wir nur einen Lauf zeigen.

**Aufgabe:** Modifiziere `02_math_breaks.py` so, dass es **20 Mal** dieselbe Frage stellt (mit `temperature=0.7` statt dem Default) und dann eine Verteilung druckt:

- Wie viele Antworten waren *exakt* richtig?
- Wie viele hatten die richtige Anzahl Stellen aber falsche Ziffern?
- Wie viele hatten eine falsche Anzahl Stellen?
- Was war der maximale absolute Fehler? Der minimale?

**Was du lernst:** die *Verteilung* der Antworten des Modells, nicht nur eine Instanz. Das ist die Perspektive, aus der man in Kapitel 6 über Determinismus reden wird.

**Bonus:** Zeichne ein ASCII-Histogramm der Fehler-Beträge. Wo liegt der Median? Was ist der Modus?

---

## Übung 3 · Wo bricht die "Text-in / Text-out"-Regel?

Wir haben behauptet: ein LLM kennt nur Text-in und Text-out. Aber moderne Modelle nehmen auch Bilder als Input, und die Multimodal-Erweiterungen von OpenAI und Anthropic akzeptieren `{"type": "image", "source": {...}}` in derselben `messages`-Struktur.

**Aufgabe:** Recherchiere im Anthropic- oder OpenAI-API-Docs, wie ein Bild in einem `messages`-Array kodiert wird. Notiere in einem Kommentar in einer neuen Datei `notes/multimodal.md`:

1. In welchem Format kommt das Bild in den Request? (Base64? URL? Bytes?)
2. Was macht das Modell auf der Server-Seite *aus* dem Bild? (Hinweis: Vision-Modelle projizieren Bild-Patches durch einen Vision-Encoder in denselben Vektorraum wie Text-Tokens.)
3. **Argument-Frage:** Verletzt Multimodalität wirklich das "Text-in / Text-out"-Prinzip? Oder ist es nur eine Erweiterung — "Bytes-in / Text-out"?

**Was du lernst:** dass "Text-in / Text-out" nicht wörtlich zu nehmen ist. Das Prinzip meint eigentlich *"strukturierte Token-Sequenz-in / strukturierte Token-Sequenz-out"*. Text ist nur die häufigste Instantiierung. Der Output bleibt fast immer Text.

**Bonus:** Wo hört das Prinzip wirklich auf? Recherchiere "audio LLM" (z.B. Whisper + GPT-4o) oder "action LLM" (z.B. Robotik-Modelle wie RT-2). Was bricht dort?

---

## Wie du wissen kannst, dass du dieses Kapitel verstanden hast

Wenn du einer nicht-technischen Kollegin in **einem Satz** erklären kannst, warum ChatGPT bei `43,177 × 14,694` falsch liegt — und in **einem zweiten Satz**, was man dagegen tut — dann bist du fertig mit Kapitel 1.

Der zweite Satz ist Kapitel 2.