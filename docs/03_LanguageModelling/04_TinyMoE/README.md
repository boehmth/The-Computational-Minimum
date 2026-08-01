# 📖 3.4 Mixture of Experts — TinyMoE

## 🎯 Das Problem des Vorgängers

TinyChat (3.3) ist ein **dichtes** Modell: Jedes einzelne Token durchläuft
bei jedem Forward-Pass alle Parameter des Netzes. Will man die Fähigkeiten
des Modells vergrößern, muss man das gesamte Netz vergrößern — und die
Rechenkosten wachsen dabei proportional mit. Ab einer gewissen Größe wird
das wirtschaftlich und praktisch unhaltbar: doppelte Kapazität heißt
doppelte Kosten, für jedes einzelne Token, ob es die zusätzliche Kapazität
gerade braucht oder nicht.

Die Frage, die dieses Kapitel beantwortet: Lässt sich die Kapazität eines
Modells vergrößern, ohne dass die Rechenkosten pro Token im gleichen Maß
mitwachsen?

## 📜 Historischer Kontext: Von der Experten-Idee zum modernen MoE-LLM

| Jahr | Paper | Beitrag |
|---|---|---|
| 1991 | Jacobs, Jordan, Nowlan, Hinton, *Adaptive Mixtures of Local Experts* | Grundidee: mehrere spezialisierte "Experten"-Netze plus ein "Gating"-Netz, das entscheidet, welcher Experte für welche Eingabe zuständig ist — ursprünglich für kleine, klassische neuronale Netze |
| 2017 | Shazeer et al., *Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer* | Überträgt die Idee erstmals auf tiefe, große Netze: ein spärlich (sparse) aktiviertes Gating wählt pro Token nur wenige von tausenden Experten aus — Kapazität wächst, Rechenkosten pro Token bleiben klein |
| 2020 | Lepikhin et al., *GShard* | Zeigt, wie sich MoE-Schichten über tausende Beschleuniger hinweg parallelisieren lassen — die technische Voraussetzung für MoE in Modellen mit hunderten Milliarden Parametern |
| 2021 | Fedus et al., *Switch Transformer* | Vereinfacht das Routing auf genau einen Experten pro Token (statt mehrerer) und skaliert damit erstmals auf über eine Billion Parameter bei vertretbaren Kosten |
| 2023/24 | Mistral AI, *Mixtral 8x7B* | Erstes breit genutztes, offenes MoE-Sprachmodell — macht das Prinzip erstmals praktisch greifbar und zeigt: ein MoE-Modell mit wenigen aktiven Milliarden Parametern pro Token kann mit deutlich größeren dichten Modellen mithalten |
| 2024 | DeepSeek-AI, *DeepSeek-MoE / DeepSeek-V2* | Verfeinert das Routing weiter: viele kleine, feingranulare Experten plus einige immer aktive "Shared Experts" für gemeinsames Grundwissen — die Linie, die auch in aktuellen Coding-Modellen wie Qwen3-Coder-30B-A3B steckt |

Der rote Faden: **Jacobs 1991** liefert die Grundidee (spezialisierte
Teilnetze + Gating), **Shazeer 2017** macht sie für tiefes Lernen praktikabel
(spärliche Aktivierung bei riesigen Netzen), **GShard/Switch Transformer**
lösen das Verteilungs- und Skalierungsproblem, und **Mixtral/DeepSeek**
zeigen, dass das Prinzip nicht nur theoretisch funktioniert, sondern echte,
weit verbreitete Modelle trägt.

*(Randnotiz für den Text, falls passend: Genau dieses Prinzip — wenige
aktive von vielen Gesamt-Parametern — ist der Grund, warum sich Modelle wie
`Qwen3-Coder-30B-A3B` trotz 30 Milliarden Gesamtparametern auf
Consumer-Hardware mit begrenztem VRAM betreiben lassen: Pro Token sind nur
rund 3 Milliarden Parameter aktiv.)*

## 😮 Der Wow-Effekt: Kapazität vs. Rechenaufwand

*[Platzhalter — Vergleich TinyChat (dicht) vs. TinyMoE bei gleicher
Trainingszeit/gleichem Rechenbudget: z. B. Parameteranzahl gesamt vs. aktiv
pro Token, sowie ein qualitativer Vergleich der Ausgabequalität bei
gleichem Rechenbudget]*

```
TinyChat (dicht):   [Platzhalter] Parameter, alle aktiv pro Token
TinyMoE:             [Platzhalter] Parameter gesamt,
                     nur [Platzhalter] aktiv pro Token
                     → [Platzhalter] höhere Kapazität bei
                       vergleichbaren Rechenkosten pro Token
```

## 🧠 Was du baust

- Ein **Gating-Netzwerk**, das pro Token die Top-k Experten auswählt (z. B.
  Top-2 von 8 kleinen Feed-Forward-Experten statt eines einzelnen großen
  Feed-Forward-Blocks wie in TinyChat)
- Eine **Load-Balancing-Loss-Komponente**, die verhindert, dass das Gating
  immer dieselben ein oder zwei Experten bevorzugt (ein reales Problem bei
  MoE-Training, ohne das die restlichen Experten nie lernen)
- Optional: ein immer aktiver **Shared Expert** analog zu DeepSeek-MoE, der
  Grundwissen unabhängig vom Routing bereitstellt

> ⚠️ Wie in den vorherigen Kapiteln bleibt der Umfang bewusst didaktisch:
> wenige, kleine Experten statt tausender, keine Multi-Device-Parallelisierung
> wie bei GShard. Das Prinzip des spärlichen Routings steht im Vordergrund,
> nicht die Infrastruktur für Modelle mit hunderten Milliarden Parametern.

## 🚀 Schnelleinstieg

Die Struktur in `src/`:

```
src/
├── config.json         Trainings-Profile (test | laptop) inkl. NUM_EXPERTS, TOP_K, LOAD_BALANCE_WEIGHT
├── moe_layer.py        die MoE-Schicht (Top-k-Gating + Experten + Load-Balancing-Loss)
├── model.py            GPTMiniMoE: TinyGPT-Architektur mit MoE statt dichter FFN
├── train_moe.py        Sprachmodell-Training auf FineWeb-Edu mit Aux-Loss
└── test_moe.py         Standalone-Beweis des Gating-Kollaps (laeuft OHNE PyTorch)
```

**Schritt 0 — die Idee ohne Training verstehen** *(kein PyTorch noetig, kein Netz):*

```bash
python 03_LanguageModelling/04_TinyMoE/src/test_moe.py
```

Zeigt in einer reinen Python-Simulation den Feedback-Loop des Gating-Kollaps:
- OHNE Load-Balancing: **100 % aller Tokens** landen bei einem einzigen Experten
  (bei Gleichverteilung waeren es 25 %). Die anderen drei Experten lernen nichts.
- MIT Load-Balancing: die Verteilung bleibt breit gestreut — alle vier Experten
  sind aktiv, keiner dominiert um mehr als etwa den Faktor 2.

Das ist der ganze Sinn des Zusatz-Loss aus Shazeer et al. 2017.

**Schritt 1 — MoE-Modell trainieren:**

```bash
python 03_LanguageModelling/04_TinyMoE/src/train_moe.py --profile test
```

Der Trainings-Loop ist bewusst FAST identisch zum TinyGPT-Loop aus Kap. 3.1.
Der einzige Unterschied ist der zusaetzliche Loss-Term:

```
total_loss = language_loss + LOAD_BALANCE_WEIGHT * aux_loss
```

Die beiden Loss-Anteile werden getrennt geloggt, damit man den Ruecklauf des
`aux_loss` ueber die Zeit beobachten kann — er faellt von einem hohen
Startwert (Anfangs kollaps-anfaellig) in Richtung 1.0 (Gleichverteilung).

Voraussetzungen: `torch`, `transformers`, `datasets`, `tqdm`.

## 📚 Quellen

- Jacobs, R. et al. (1991). *Adaptive Mixtures of Local Experts.*
- Shazeer, N. et al. (2017). *Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer.*
- Lepikhin, D. et al. (2020). *GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding.*
- Fedus, W. et al. (2021). *Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity.*
- Jiang, A. et al. (2024). *Mixtral of Experts.*
- DeepSeek-AI (2024). *DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model.*

## ✏️ Übungen

*[Platzhalter]*

## ➡️ Grenzen dieses Meilensteins

TinyMoE skaliert Kapazität effizienter, macht das Modell aber nicht
grundsätzlich "klüger" bei mehrstufigen Problemen — es antwortet weiterhin
direkt, ohne sichtbare Zwischenschritte. Kapitel 3.5 (TinyReason) zeigt, wie
ein Modell stattdessen lernt, vor der Antwort zu "denken".
