"""
02 · determinism_check  —  Kapitel 6, Miniatur 2

Slide-Anker :  P3 · "temperature=0" heißt NICHT reproduzierbar
Laufzeit    :  15-30 Sekunden
Kosten      :  ~1500-3000 Tokens (5 identische Aufrufe)

Wir schicken FÜNFMAL denselben Prompt mit temperature=0 an dasselbe
Modell.  Ideal wäre: fünfmal identische Antwort.  Real gemessen:
oft nicht.

Das Skript zählt:
  - identisch (zeichenweise)?
  - gleiche Struktur, gleiche Werte (semantisch)?
  - unterschiedliche Reihenfolge / Wörter (kosmetisch verschieden)?

Für einen regulierten Prozess ist Kosmetik nicht harmlos:
"gleicher Prompt, andere Antwort" ist ein Compliance-Defekt.

Ausführen:
    python "Agentic Systems/06_WhenNotToBuild/src/02_determinism_check.py"
"""

import hashlib
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS   = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat, extract_json
from common.ui  import hard_card, soft_frame, phase_break, wrap


SYSTEM = """Du bist ein Planer.  Für die gegebene Aufgabe gib einen
strukturierten Plan im folgenden JSON-Format zurück, sonst NICHTS:

  {
    "goal": "<eine Zeile>",
    "steps": [
      {"n": 1, "action": "<verb>", "detail": "<kurz>"},
      ...
    ]
  }
"""


TASK = ("Plane einen Tages-Ausflug für zwei Personen nach Heidelberg.  "
        "Genau 4 Schritte, chronologisch geordnet.")


N_RUNS = 5


def hash_of(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:12]


def semantic_signature(plan: dict) -> str:
    """Reduziere den Plan auf seine 'Wahrheit' — Reihenfolge und
    action-Verben.  Ignoriere Wortwahl in 'detail'."""
    steps = plan.get("steps") or []
    verbs = [str(s.get("action", "")).strip().lower() for s in steps]
    return " -> ".join(verbs)


def main():
    phase_break("determinism_check.py  ·  5x derselbe Prompt, temperature=0")

    soft_frame(
        "DIE PRÄMISSE",
        [
            "temperature=0 sollte 'greedy decoding' bedeuten:",
            "an jeder Position der wahrscheinlichste Token.  Deterministisch.",
            "",
            "In der Praxis nicht.  Server-side batching, Load-Balancing,",
            "internal Best-of-N, Floating-Point-Rundung — all das kann",
            "die Antwort zwischen zwei identischen Requests verändern.",
        ],
    )

    hard_card(
        title    = "DIE AUFGABE (5x IDENTISCH gesendet)",
        subtitle = "temperature=0, same prompt, same model",
        body     = TASK,
    )

    responses = []
    for i in range(1, N_RUNS + 1):
        print(f"  Run {i}/{N_RUNS} — sende Prompt an das Modell...", end=" ")
        r = chat(system=SYSTEM, user=TASK, want_json=True,
                 temperature=0.0, max_tokens=1024)
        text = r.text.strip()
        try:
            plan = extract_json(text)
        except Exception:
            plan = None
        responses.append({
            "run":    i,
            "text":   text,
            "plan":   plan,
            "hash":   hash_of(text),
            "sig":    semantic_signature(plan) if plan else "(unparsable)",
            "tokens": r.tokens,
        })
        print(f"hash={responses[-1]['hash']}  tokens={r.tokens}")

    # ---- Zusammenfassung: char-identisch? ----
    unique_hashes = sorted(set(r["hash"] for r in responses))
    unique_sigs   = sorted(set(r["sig"] for r in responses))

    lines = [
        f"{'Run':>4}  {'char-hash':<15}  {'sig (verb sequence)':<45}",
        "-" * 74,
    ]
    for r in responses:
        lines.append(
            f"{r['run']:>4}  {r['hash']:<15}  {r['sig'][:45]:<45}"
        )
    soft_frame("PRO RUN", lines)

    verdict = []
    if len(unique_hashes) == 1:
        verdict.append("✓ char-identisch:  alle 5 Runs zeichengleich.")
        verdict.append("  Für DIESEN Prompt gilt Determinismus.")
    else:
        verdict.append(
            f"✗ char-verschieden:  {len(unique_hashes)} unterschiedliche "
            f"Byte-Hashes bei 5 Runs.")
        verdict.append("  Zwei Runs mit demselben Prompt lieferten "
                       "unterschiedliche Antworten.")

    verdict.append("")
    if len(unique_sigs) == 1 and "unparsable" not in unique_sigs[0]:
        verdict.append(
            "✓ semantisch-identisch:  alle Runs mit gleicher Aktion-Sequenz.")
        verdict.append("  Die Kosmetik variiert, die Struktur bleibt.")
    else:
        verdict.append(
            f"✗ semantisch verschieden:  {len(unique_sigs)} unterschiedliche "
            f"Aktion-Sequenzen.")
        verdict.append("  Nicht nur Wortwahl unterscheidet sich — auch der")
        verdict.append("  Plan-Aufbau.  Das ist NICHT kosmetisch.")

    soft_frame("URTEIL", verdict)

    # ---- der Punkt ----
    soft_frame(
        "WARUM DAS FÜR REGULIERTE PROZESSE ZÄHLT",
        [
            "Nimm an, das ist ein Rechnungs-Freigabe-System und der Prompt",
            "enthält Rechnungsnummer und Betrag statt Heidelberg-Reise.",
            "",
            "Zwei IDENTISCHE Eingaben liefern zwei UNTERSCHIEDLICHE Pläne.",
            "Das heißt: der Prüfer, der die Rechnung ein zweites Mal",
            "einreicht (unbewusst, wegen Timeout, wegen Retry), kann eine",
            "ANDERE Empfehlung bekommen.  Und das Audit-Log zeigt es nicht.",
            "",
            "Der Ausweg ist NICHT 'wir setzen temperature=0 und hoffen'.",
            "Der Ausweg ist EINER von:",
            "  a)  ganz auf LLM verzichten für diese Klasse (siehe Miniatur 1)",
            "  b)  LLM-Ergebnisse cachen mit einem strikten Input-Hash",
            "      als Key — deterministisches Verhalten aus dem Cache",
            "  c)  jede LLM-Empfehlung durch DETERMINISTISCHE nachgelagerte",
            "      Regeln laufen lassen die 'entscheiden ob'",
            "  d)  menschliche Freigabe im Loop — kein autonomer Agent",
        ],
    )

    print()
    print("→ 'temperature=0' ist ein Hinweis, kein Vertrag.")
    print("→ Reproduzierbarkeit ist keine LLM-Eigenschaft — sie ist")
    print("  eine Architektur-Eigenschaft deines Systems drumherum.")


if __name__ == "__main__":
    main()