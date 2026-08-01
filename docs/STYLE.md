# STYLE.md — Visuelles System für „The Computational Minimum"

Dieses Dokument fasst zusammen, wie das Buch **visuell** gehalten wird —
Farben, Typografie, wiederkehrende Text- und Bild-Elemente. Ziel: eine
reduzierte, wiedererkennbare Handschrift, die zur inhaltlichen Haltung
des Buchs passt (*„machen statt beweisen"*, minimale Mittel, konsequente
Sprache).

Der visuelle Anker ist **kein bestimmtes Album eines bestimmten
Künstlers** — sondern die *strukturelle* Haltung minimalistischer,
konstruktivistischer, europäischer Elektronik-Ästhetik der 1970er/80er:
flache Farbflächen, geometrische Strenge, keine Gesichter, keine Textur.

──────────◆──────────◆──────────◆──────────◆──────────

## 1. Farbpalette: eine Regel, sechs Ausprägungen

Die visuelle Wiedererkennung dieses Buchs beruht **nicht** auf einer
einzigen Palette, die überall gleich bleibt, sondern auf einer
konsequenten **Regel**:

> **Jedes Kapitel bekommt genau vier flache Farben — Hintergrund,
> Struktur, Signal, Kontrast — ohne Verläufe, ohne Zwischentöne,
> ohne Texturen.**

Die konkreten Farben *variieren* pro Kapitel, thematisch angelehnt an
das jeweilige Album aus der Kraftwerk-Ära (1970–1983), ohne das Album
selbst zu zitieren. Das ist musikhistorisch stimmig — jedes Album hat
seine eigene Farbwelt — und didaktisch nützlich: jedes Kapitel bekommt
seine visuelle *Identität*, während die *Sprache* (flach, geometrisch,
konstruktiv) durchgehend gleich bleibt.

### Die Ziel-Paletten (definiert in `tools/palettes.py`)

| Kap. | Thema | Album-Anker (nur atmosphärisch) | Hintergrund | Struktur | Signal | Kontrast |
|---|---|---|---|---|---|---|
| 00 | Fundament | *Ralf & Florian* (1973) | `#EEE8DB` cream | `#302820` dunkle Erde | `#AC2E1E` Zinnoberrot | `#1C1C20` anthrazit |
| 01 | CPU | *Autobahn* (1974) | `#E8E9EC` grau-weiss | `#202C4E` Verkehrsblau | `#DA3C3C` marker-rot | `#64697380` mittelgrau |
| 02 | OS | *Radio-Aktivität* (1975) | `#F5F0E6` papier | `#101014` schwarz | `#F0BE28` warngelb | `#C83C28` alarm-rot |
| 03 | Compiler | *Trans Europa Express* (1977) | `#F5F0E8` papier | `#1E1E1E` schwarz | `#C62828` express-rot | `#646464` mittelgrau |
| 04 | Perceptron | *Die Mensch-Maschine* (1978) | `#EEEAE2` papier | `#18181C` schwarz | `#CC2020` neuron-rot | `#8C8C8C` mittelgrau |
| 05 | GPU | *Computerwelt* (1981) | `#F0EBE1` papier | `#121614` schwarz | `#2C8A3C` terminal-grün | `#78766C` mittelgrau |
| 06 | Netzwerk | *Tour de France* (1983/2003) | `#F5F0E8` papier | `#1A2A5C` tdf-blau | `#C62828` trikot-rot | `#1C1C20` anthrazit |

**Absichtlich nicht:** reines Schwarz `#000000` und reines Weiss
`#FFFFFF`. Alle Hintergründe sind warm gebrochen, alle Schwärzen sind
Anthrazit. Das ist der Unterschied zwischen einer Bildschirm-Ausgabe
und einem Buch-Cover.

**Automatische Anwendung auf AI-generierte Bilder:** siehe
`tools/recolor_cover.py`. Das Skript liest die Kapitel-Palette aus
`tools/palettes.py` (via `--chapter` oder automatisch aus dem
Bildpfad) und mappt jede Pixelfarbe per HSL-Klassifikation auf die
vier Zielfarben. Damit werden AI-Generatoren, die "gerne mal Gelb
einführen", diszipliniert.

──────────◆──────────◆──────────◆──────────◆──────────

## 2. Typografie

Ziel: **konstruktiv, geometrisch, technisch klar, ohne Serifen**. Anlehnung
an frühe Bauhaus-Konstruktivismus und 1970er-Wissenschafts-Buchsatz.

### 2.1 Empfohlene Fonts (alle frei nutzbar unter SIL Open Font License)

| Rolle | Font | Wozu |
|---|---|---|
| Kapitel-Überschriften | **Space Grotesk** | geometrisch, konstruktiv, klar; sehr gute Balance aus Struktur und Lesbarkeit |
| Fliesstext | **Inter** (oder System-Sans-Serif) | sehr gute Lesbarkeit über lange Passagen, neutral |
| Code, ASCII-Ausgaben | **JetBrains Mono** (oder Fira Code) | Monospaced mit tabellarischer Klarheit |
| Sekundär-Titel (Kapitel-Untertitel, Klein-Caps) | **Chakra Petch** | etwas technischer, mit leicht kondensierten Formen |
| Extreme Reduktion (Cover-Textelemente falls gewünscht) | **Krona One** | fast Bauhaus, sehr rund, sehr wenig Buchstaben |

Alle diese Fonts sind über **Google Fonts** oder direkt auf GitHub
verfügbar (SIL OFL). Keine urheberrechtliche Reibung, keine
Kraftwerk-nahen kommerziellen Fonts.

### 2.2 Layout-Vorschlag (später bei Publikation)

- Fliesstext: 16 pt bei Bildschirm, 11 pt bei Druck
- Zeilenhöhe: 1.55
- Zeilenlänge: 60–70 Zeichen
- Kapitel-Überschriften: Space Grotesk 32 pt, `#1A2A5C` (TdF-Blau)
- Abschnitts-Überschriften: Space Grotesk 22 pt, `#1A2A5C`
- Inline-Code: JetBrains Mono 90 %, `#1C1C20` (Anthrazit) auf Papier-Weiss

### 2.3 Wie das in Markdown-Rendering funktioniert

Reines GitHub-Markdown rendert diese Fonts **nicht direkt**. Solange die
READMEs auf GitHub liegen, sehen sie die Standard-Font des Repos.

Sobald wir das Buch als **statische Site** (MkDocs Material, Quarto,
Astro Starlight, Docusaurus) veröffentlichen, greifen die Fonts. Alle
oben genannten Systeme unterstützen Google-Fonts-Einbindung mit einer
einzigen Konfigurationszeile. Für den Anfang genügt es, die Fonts als
Empfehlung in dieser Datei festzuhalten.

──────────◆──────────◆──────────◆──────────◆──────────

## 3. Wiederkehrende Text-Elemente

Diese Zeichen kehren im Buch als visuelle Signatur wieder. Sie
funktionieren *auch in reinem GitHub-Markdown*, ohne dass ein Font-Setup
nötig wäre.

### 3.1 Der Knoten `◆`

Das Diamant-Symbol `◆` ist unser wiederkehrender Knotenpunkt. Er taucht
in vier Rollen auf:

1. **In Bild-Untertiteln** als Aufzählungs-Trennzeichen zwischen
   Metaphern-Elementen:

   > *Straßennetz = Kanal ◆ Fahrer = Sendungen ◆ Kreuzung mit Zusammenprall = Kollision*

2. **Als Serien-Trenner** anstelle des Standard-`---`:

   ```
   ──────────◆──────────◆──────────◆──────────◆──────────
   ```

   Fünf Diamanten, jeweils durch 10 Bindestriche getrennt. Das trennt
   Abschnitte innerhalb eines Kapitels visuell ruhiger als `---` (das im
   Markdown-Rendering als harte horizontale Linie erscheint).

3. **Als Bullet-Point** für Kern-Aussagen (statt `-` oder `*`):

   ```
   ◆ Erster Kernpunkt.
   ◆ Zweiter Kernpunkt.
   ```

   Verwendung bewusst *sparsam* — nur da, wo eine Liste **konzeptionell**
   eine Aufzählung von Meilensteinen oder Kern-Beobachtungen ist. Für
   normale Aufzählungen bleibt es bei `-`.

4. **Als Ende-Marker** eines Kapitels:

   ```
   ◆ ◆ ◆
   ```

   Drei zentrierte Diamanten. Der letzte Bogen des Kapitels endet damit.

### 3.2 Kapitel-Titel im Serien-Format

Kapitel-Titel sind konsistent im Format:

```
# 0X · Thema — Kernbegriff
```

Beispiel:

- `# 06 · Netzwerk — ALOHA`
- `# 05 · GPU — SIMT`
- `# 01 · CPU — Von Neumann`

Der Mittel-Punkt `·` und der Gedankenstrich `—` (Halbgeviert, nicht
Bindestrich!) sind Teil der Signatur.

### 3.3 Kern-Zitat-Block

Jedes Kapitel beginnt nach dem Cover-Bild und dem Metaphern-Untertitel
mit einem *Ein-Absatz-Motto* als Zitat-Block. Der Motto-Absatz ist
zwischen 3 und 6 Zeilen lang, ohne Aufzählungspunkte, ohne
Zwischenüberschrift. Er soll den zentralen Wow-Moment des Kapitels in
seiner *Sprache* schon einmal andeuten — nicht als Kraftwerk-Zitat,
sondern in einem konstruktiv-schlichten Ton.

Beispiel (aus 06 Netzwerk):

> Ein einziges Blechkisten-Netz auf sieben Hawaii-Inseln, 1970. Sieben
> Rechner, ein UHF-Funkkanal, keine Absprache. Und eine Regel, die so
> simpel klingt, dass man sie beim ersten Hören für einen Scherz hält:
> *„Sende, wenn du etwas hast. Wenn's kollidiert — warte zufällig, dann
> nochmal."*

──────────◆──────────◆──────────◆──────────◆──────────

## 4. Bild-Elemente

### 4.1 Kapitel-Cover

Jedes Kapitel bekommt ein einziges Cover-Bild, unter dem Kapitel-Titel.
Format: **16:9 landscape**, PNG. Dateiname immer `assets/cover.png` (oder
`cover_v2.png` nach der Rekolorierung). Prompts für die Generierung
stehen in `01_Computing/assets_prompts.md`.

Nach Generierung: **immer** `tools/recolor_cover.py` durchlaufen lassen.
Damit sind alle Cover automatisch auf die verbindliche 4-Farben-Palette
normiert — auch dann, wenn Copilot Designer einen Gelbstich einführt.

### 4.2 Der Bild-Untertitel

Direkt unter dem Cover-Bild steht *ein einziger Satz kursiv*, der die
Bild-Metapher wörtlich auflöst — mit `◆` als Trenner zwischen den
Metaphern-Bausteinen. Beispiel:

```markdown
![Alt-Text](assets/cover_v2.png)

*Straßennetz = Kanal ◆ Fahrer = Sendungen ◆ Kreuzung = Kollision.*
```

Zweck: der Leser sieht das Bild, liest den einen Zeile, und weiß sofort,
was das Bild *inhaltlich* mit dem Kapitel zu tun hat. Das Bild wird zum
Merk-Anker für das Kapitel-Konzept.

### 4.3 ASCII-Diagramme im Text

ASCII-Diagramme (siehe z. B. `test_aloha.py`, `test_moe.py`) sind
ausdrücklich Teil der visuellen Sprache des Buchs. Sie sind:

- **monospaced** (JetBrains Mono im späteren Layout, Standard-Monospace
  im GitHub-Rendering)
- **reduziert**: nur `= X ! * . |` und ähnlich reduzierte Zeichen
- **selbst-erklärend**: eine Legende darunter (`Legende: '=' erfolgreich, 'X' kollidiert, ...`)
- konsistent in der Breite: alle ASCII-Blöcke in einem Kapitel sind
  gleich breit, damit sie visuell als Familie erscheinen.

──────────◆──────────◆──────────◆──────────◆──────────

## 5. Später: MkDocs / Quarto / HTML-Publikation

Wenn das Buch als statische Site oder PDF ausgerollt wird, kommen zwei
zusätzliche Dinge dazu, die in reinem GitHub-Markdown noch nicht wirken:

### 5.1 CSS-Snippet für die Serien-Palette

```css
:root {
  --paper:      #F5F0E8;
  --red:        #C62828;
  --blue:       #1A2A5C;
  --anthracite: #1C1C20;
}

body {
  background: var(--paper);
  color: var(--anthracite);
  font-family: "Inter", system-ui, sans-serif;
  line-height: 1.55;
}

h1, h2, h3 {
  font-family: "Space Grotesk", sans-serif;
  color: var(--blue);
  font-weight: 500;
  letter-spacing: -0.01em;
}

h1 { font-size: 2.0rem; }
h2 { font-size: 1.5rem; }
h3 { font-size: 1.2rem; }

code, pre {
  font-family: "JetBrains Mono", monospace;
  background: rgba(28, 28, 32, 0.05);
  border-radius: 3px;
}

strong { color: var(--blue); }
em { color: var(--red); font-style: normal; }

hr {
  border: none;
  border-top: 1px solid var(--blue);
  margin: 2rem 0;
}

blockquote {
  border-left: 3px solid var(--red);
  padding-left: 1rem;
  color: var(--anthracite);
  font-style: italic;
}
```

### 5.2 MkDocs-Material-Konfiguration (Ausschnitt)

```yaml
# mkdocs.yml
theme:
  name: material
  font:
    text: Inter
    code: JetBrains Mono
  palette:
    - scheme: default
      primary: custom
      accent: custom

extra_css:
  - stylesheets/computational-minimum.css
```

Mit einer solchen `mkdocs.yml` und der obigen CSS-Datei wird aus dem
GitHub-Repository ohne weitere Anpassungen eine layoutgetreue Site.

──────────◆──────────◆──────────◆──────────◆──────────

## 6. Was diese Datei bewusst *nicht* ist

- **Kein starres Regelwerk.** Alle oben genannten Regeln dienen der
  Wiedererkennung, nicht der Bürokratie. Wenn ein Kapitel triftig
  begründet abweicht (z. B. weil eine Metapher ein anderes Symbol
  natürlich verlangt), ist das kein Problem — solange die Abweichung im
  Kapitel selbst kurz erklärt wird.

- **Kein Kraftwerk-Klon.** Wir zitieren keinen Künstler wörtlich. Weder
  die Fonts, noch die Cover-Motive, noch die Farbwerte übernehmen ein
  konkretes existierendes Design. Wir übernehmen die *strukturellen
  Haltungen*: Reduktion, Geometrie, Konsequenz, keine Textur, keine
  Fotorealistik, keine Gesichter.

- **Kein Corporate-Style-Manual.** Dieses Buch ist ein Lehrtext, kein
  Marketing-Material. Die visuelle Klarheit soll dem *Verstehen* dienen,
  nicht der Marke.

──────────◆──────────◆──────────◆──────────◆──────────

## 7. Checkliste beim Kapitel-Fertigstellen

Wenn ein Kapitel-README als "fertig" markiert wird, sollte es folgende
Punkte erfüllen:

- [ ] SVG-Titelgrafik `assets/title.svg` erzeugt (via `render_title_svg.py`)
- [ ] Cover-Bild in `assets/cover.png` **oder** `assets/cover_v2.png` —
      welches der beiden im README verlinkt wird, entscheidet der Vergleich:
      wenn das Original bereits die Kapitel-Palette gut trifft, nimm es.
      Wenn das Original stark abweichende Farben hat (typisch: Gelb), lass
      `recolor_cover.py` drüberlaufen und nimm die `cover_v2.png`.
- [ ] Serien-Trenner `──────────◆──────────◆───...` zwischen grossen
      Abschnitten (nicht `---`)
- [ ] Kern-Zitat-Block (3–6 Zeilen, keine Aufzählung) direkt nach dem
      Untertitel
- [ ] Historische Tabelle (Jahr | Ereignis | Bedeutung) in jedem Kapitel
      mit historischem Fokus
- [ ] Ein "Was du baust"-Abschnitt, ein "Schnelleinstieg"-Abschnitt,
      und ein "Grenzen"-Abschnitt
- [ ] Am Ende: klarer Bogen zum nächsten Kapitel oder zum nächsten Teil
- [ ] `◆ ◆ ◆` als visuelles Kapitel-Ende, falls kein direkter
      "Nächstes Kapitel"-Übergang folgt

Diese Liste ist eine Selbst-Kontrolle vor dem Commit, keine
Prüfungsanforderung.

◆ ◆ ◆
