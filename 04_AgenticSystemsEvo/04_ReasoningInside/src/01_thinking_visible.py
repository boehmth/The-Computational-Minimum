"""
01 · thinking_visible  —  Kapitel 4, Miniatur 1

Slide-Anker :  P2 · der Loop lebt im Modell, nicht im Code
Laufzeit    :  15-60 Sekunden (reasoning-Modelle sind absichtlich langsam)
Kosten      :  ~1500-4000 Tokens (davon 500-2000 unsichtbare Thinking-Tokens)

Dieselbe Frage an zwei Modelle:
  1. gpt-4o (baseline) — one-shot, ein Text-Strom
  2. anthropic--claude-4.5-sonnet mit thinking=enabled
     — zwei Text-Ströme: das Denken UND die Antwort

Beides in einem einzigen HTTP-Aufruf jeweils.  Der "Loop" bei Claude
lebt inside der Modell-Inferenz, nicht in unserem Code.

Setze LLM_REASONING_MODEL in .env auf ein deployed reasoning-Modell,
z.B. anthropic--claude-4.5-sonnet.

Ausführen:
    python "Agentic Systems/04_ReasoningInside/src/01_thinking_visible.py"
"""

import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS   = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat
from common.ui  import hard_card, soft_frame, phase_break, wrap


PROMPT = (
    "Ein Tank fasst 240 Liter. Rohr 1 füllt mit 12 L/min, "
    "Rohr 2 füllt mit 8 L/min, ein Abfluss leert mit 5 L/min. "
    "Alle drei laufen gleichzeitig.  Wie lange dauert es bis der Tank "
    "voll ist? Gib die Antwort in Minuten (und Sekunden falls nötig) "
    "und zeige deinen Rechenweg kurz."
)


def main():
    baseline_model  = os.getenv("SAP_GENAI_MODEL",
                                os.getenv("LLM_MODEL", "gpt-4o"))
    reasoning_model = os.getenv("LLM_REASONING_MODEL",
                                "anthropic--claude-4.5-sonnet")

    soft_frame(
        "DIE AUFGABE (identisch für beide Modelle)",
        wrap(PROMPT),
    )

    # -------- Modell A: Baseline (one-shot, kein sichtbares Thinking) --------
    phase_break(f"MODELL A · one-shot  ·  {baseline_model}")
    r1 = chat(
        system="Du bist ein sorgfältiger Rechner.",
        user=PROMPT,
        model=baseline_model,
        max_tokens=1024,
    )
    hard_card(
        title    = "▸  FINAL ANSWER  (was der Nutzer sieht)",
        subtitle = f"{r1.tokens_out} out-Tokens · {r1.tokens_in} in-Tokens"
                   f" · kein sichtbares Thinking",
        body     = r1.text,
    )

    # -------- Modell B: Reasoning (thinking=enabled) --------
    phase_break(f"MODELL B · reasoning='high'  ·  {reasoning_model}")
    try:
        r2 = chat(
            system="Du bist ein sorgfältiger Rechner.",
            user=PROMPT,
            model=reasoning_model,
            reasoning="high",
            max_tokens=4096,
        )
    except RuntimeError as e:
        if "No running SAP GenAI Hub deployment" in str(e):
            soft_frame(
                "REASONING-MODELL NICHT DEPLOYED",
                [
                    f"Modell {reasoning_model!r} ist in diesem",
                    "Resource-Group NICHT deployed.",
                    "",
                    "Erkunde verfügbare Modelle mit:",
                    "  python -m rpt_agent.list_rpt_deployments",
                    "",
                    "Dann setze LLM_REASONING_MODEL in ../.env",
                    "auf ein reasoning-fähiges Modell:",
                    "   anthropic--claude-4.5-sonnet   (empfohlen)",
                    "   anthropic--claude-4.5-opus     (teurer, tiefer)",
                    "   anthropic--claude-4.5-haiku    (schnell, günstig)",
                    "   o1 / o3 / o4                    (OpenAI-Serie)",
                ],
            )
            print("\n→ Baseline-Aufruf oben hat funktioniert; nur das")
            print("  reasoning-Modell fehlt.  Aufgabe ist gelaufen, aber")
            print("  der Vergleich fehlt.")
            return
        raise

    if r2.thinking:
        hard_card(
            title    = "▸  THINKING  (was das Modell sich selbst erzählt)",
            subtitle = f"~{r2.tokens_thinking} thinking-Tokens · für dich als"
                       f" Entwickler sichtbar über die API · in einer Chat-UI"
                       f" normalerweise ausgeblendet",
            body     = r2.thinking,
        )

    hard_card(
        title    = "▸  FINAL ANSWER  (was der End-Nutzer in einer UI sähe)",
        subtitle = f"~{r2.tokens_answer} answer-Tokens · {r2.tokens_in}"
                   f" in-Tokens · EIN HTTP-Call insgesamt",
        body     = r2.text,
    )

    # -------- Kosten-Vergleich --------
    cost_lines = [
        f"BASELINE   ({baseline_model})",
        f"    {r1.tokens} Tokens insgesamt   "
        f"({r1.tokens_in} in · 0 thinking · {r1.tokens_out} answer)",
        "",
        f"REASONING  ({reasoning_model})",
        f"    {r2.tokens} Tokens insgesamt   "
        f"({r2.tokens_in} in · {r2.tokens_thinking} thinking "
        f"· {r2.tokens_answer} answer)",
        f"    ← {r2.tokens_thinking} thinking-Tokens die der End-Nutzer",
        f"      nie sieht — für die du aber bezahlt hast",
    ]
    if r1.tokens_out and r2.tokens_answer:
        pct = round(100 * (1 - r2.tokens_answer / r1.tokens_out))
        if pct > 0:
            cost_lines.append("")
            cost_lines.append(
                f"Die reasoning-Antwort ist {pct}% kürzer als die baseline-"
                "Antwort —")
            cost_lines.append(
                "weil das Modell den Rechenweg im Thinking-Block macht,")
            cost_lines.append(
                "nicht in der finalen Antwort.")
    soft_frame("KOSTENVERGLEICH", cost_lines)

    # -------- Provider-Sichtbarkeitsmatrix --------
    soft_frame(
        "WERDEN DIE THINKING-TOKENS GEZEIGT?  ·  nach Anbieter",
        [
            "Anthropic Claude          ▸  JA,  als content[type='thinking']",
            "OpenAI o-Serie            ▸  NEIN, nur die Zahl in "
            "usage.reasoning_tokens",
            "Google Gemini 2.5+        ▸  NEIN standardmäßig; opt-in via",
            "                              thinking_config.include_thoughts=True",
            "DeepSeek-R1 (open-weight) ▸  JA,  als <think>...</think> im Text",
            "",
            "In JEDEM Fall bezahlst du für sie.  Ob du sie SIEHST",
            "ist eine IP-/Sicherheits-Entscheidung des Anbieters,",
            "keine architektonische.",
        ],
    )

    print()
    print("→ Ein HTTP-Call.  Ein `chat()`-Aufruf. Ein Response-Objekt.")
    print("→ Aber ZWEI Text-Ströme: das Denken und die Antwort.")
    print("→ Der Loop lebt im Modell — er kostet dich Zeit und Tokens,")
    print("  aber du hast ihn nicht geschrieben.")


if __name__ == "__main__":
    main()