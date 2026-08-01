"""
03 · retry_strategies  —  Kapitel 3, Miniatur 3

Slide-Anker :  P3 · Retry ist wo der Loop lebendig bleibt
Laufzeit    :  ~10-15 Sekunden
Kosten      :  ~300-500 Tokens (nur Strategie D braucht das LLM)

Vier Retry-Strategien, dieselbe Fehler-Sequenz:

    A · NAIVE                fixes sleep, dann retry
    B · EXPONENTIAL BACKOFF  0.5, 1, 2, 4 Sekunden
    C · CIRCUIT BREAKER      nach 3 Fehlern in Folge: aussteigen
    D · LLM-GUIDED RECOVERY  Fehler an das Modell schicken, Empfehlung holen,
                             dann eine ANDERE Aktion ausführen

Am Ende steht eine Vergleichs-Tabelle.

Ausführen:
    python "Agentic Systems/03_TheLoop/src/03_retry_strategies.py"
"""

import json
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve()
_AS   = _HERE.parent.parent.parent
if str(_AS) not in sys.path:
    sys.path.insert(0, str(_AS))

from common.llm import chat, extract_json
from common.ui  import soft_frame, phase_break, wrap


# ---- Simuliertes Werkzeug: schlägt N Mal fehl, dann OK ----

class FlakyTool:
    """Simuliert ein Werkzeug, das bei den ersten `fail_first` Aufrufen
    einen HTTP-503-artigen Fehler wirft und danach das erwartete Ergebnis
    liefert.  Wir bauen es hier lokal, um für alle Strategien exakt
    dieselbe Fehler-Sequenz zu bekommen (deterministischer Vergleich)."""

    def __init__(self, fail_first: int = 3):
        self.fail_first = fail_first
        self.reset()

    def reset(self):
        self.attempts = 0

    def price_lookup(self, sku: str):
        self.attempts += 1
        if self.attempts <= self.fail_first:
            raise RuntimeError(
                "HTTP 503 · service temporarily unavailable "
                "(price-lookup backend under maintenance)")
        return {"sku": sku, "price_eur": 42.00, "source": "primary"}

    def fallback_lookup(self, sku: str):
        # Fallback ist stabil.  Nur höhere Latenz.
        return {"sku": sku, "price_eur": 41.50, "source": "cache",
                "note": "cached value, up to 24h old"}


TOOL = FlakyTool(fail_first=3)
SKU  = "PROD-42"


# ---- Strategie A · naive ----

def strategy_naive():
    TOOL.reset()
    t0 = time.perf_counter()
    attempts = 0
    for _ in range(5):
        attempts += 1
        try:
            result = TOOL.price_lookup(SKU)
            latency = time.perf_counter() - t0
            return {"result": result, "attempts": attempts, "latency": latency,
                    "tokens": 0, "note": "OK — brute force worked"}
        except RuntimeError:
            time.sleep(0.4)   # konstantes sleep
    return {"result": None, "attempts": attempts,
            "latency": time.perf_counter() - t0,
            "tokens": 0, "note": "give up after 5 tries"}


# ---- Strategie B · exponential backoff ----

def strategy_backoff():
    TOOL.reset()
    t0 = time.perf_counter()
    attempts = 0
    delays = [0.2, 0.4, 0.8, 1.6]
    for delay in delays + [None]:
        attempts += 1
        try:
            result = TOOL.price_lookup(SKU)
            latency = time.perf_counter() - t0
            return {"result": result, "attempts": attempts, "latency": latency,
                    "tokens": 0, "note": "OK — classic exp backoff"}
        except RuntimeError:
            if delay is None:
                break
            time.sleep(delay)
    return {"result": None, "attempts": attempts,
            "latency": time.perf_counter() - t0,
            "tokens": 0, "note": "give up — retries exhausted"}


# ---- Strategie C · circuit breaker ----

def strategy_circuit_breaker(threshold: int = 3):
    TOOL.reset()
    t0 = time.perf_counter()
    attempts = 0
    consecutive_fails = 0
    for _ in range(5):
        attempts += 1
        try:
            result = TOOL.price_lookup(SKU)
            latency = time.perf_counter() - t0
            return {"result": result, "attempts": attempts, "latency": latency,
                    "tokens": 0, "note": "OK before breaker tripped"}
        except RuntimeError:
            consecutive_fails += 1
            if consecutive_fails >= threshold:
                latency = time.perf_counter() - t0
                return {"result": None, "attempts": attempts, "latency": latency,
                        "tokens": 0,
                        "note": f"circuit open after {threshold} fails — "
                                f"fail fast, escalate"}
            time.sleep(0.2)
    return {"result": None, "attempts": attempts,
            "latency": time.perf_counter() - t0,
            "tokens": 0, "note": "give up"}


# ---- Strategie D · LLM-guided recovery ----

RECOVERY_SYSTEM = """Du hilfst einem Programm bei der Fehlerbehandlung.
Du bekommst den Fehlertext eines Werkzeug-Aufrufs.  Du kennst diese
verfügbaren Werkzeuge:

  price_lookup(sku)      — primäres Backend, gerade instabil
  fallback_lookup(sku)   — Fallback aus dem Cache (bis 24h alt)

Antworte AUSSCHLIESSLICH mit einem JSON-Objekt:

  {"action": "retry"     , "reason": "..."}
  {"action": "fallback"  , "tool": "fallback_lookup", "reason": "..."}
  {"action": "give_up"   , "reason": "..."}
"""


def strategy_llm_guided():
    TOOL.reset()
    t0 = time.perf_counter()
    attempts = 0
    tokens_total = 0

    # Erster Versuch
    attempts += 1
    try:
        result = TOOL.price_lookup(SKU)
        return {"result": result, "attempts": attempts,
                "latency": time.perf_counter() - t0,
                "tokens": 0, "note": "OK on first try (kein LLM nötig)"}
    except RuntimeError as e:
        error_text = str(e)

    # Fehler → LLM fragen was jetzt
    user_msg = (
        f"Werkzeug-Aufruf `price_lookup(sku='{SKU}')` hat gerade "
        f"folgenden Fehler geworfen:\n\n{error_text}\n\n"
        f"Was schlägst du vor?"
    )
    r = chat(system=RECOVERY_SYSTEM, user=user_msg,
             want_json=True, max_tokens=256)
    tokens_total += r.tokens

    try:
        advice = extract_json(r.text)
    except Exception:
        return {"result": None, "attempts": attempts,
                "latency": time.perf_counter() - t0,
                "tokens": tokens_total,
                "note": f"LLM-Antwort nicht parsbar: {r.text[:100]}"}

    soft_frame(
        "  LLM-EMPFEHLUNG",
        [
            f"action : {advice.get('action')}",
            f"reason : {advice.get('reason', '(kein Grund angegeben)')}",
        ],
    )

    action = advice.get("action")
    if action == "fallback":
        # Alternatives Werkzeug ausführen (nicht das kaputte)
        attempts += 1
        result = TOOL.fallback_lookup(SKU)
        return {"result": result, "attempts": attempts,
                "latency": time.perf_counter() - t0,
                "tokens": tokens_total,
                "note": "OK — LLM empfahl den fallback"}
    elif action == "retry":
        attempts += 1
        try:
            result = TOOL.price_lookup(SKU)
            return {"result": result, "attempts": attempts,
                    "latency": time.perf_counter() - t0,
                    "tokens": tokens_total,
                    "note": "OK auf zweitem Versuch (LLM sagte retry)"}
        except RuntimeError:
            return {"result": None, "attempts": attempts,
                    "latency": time.perf_counter() - t0,
                    "tokens": tokens_total,
                    "note": "LLM sagte retry, aber Werkzeug bleibt kaputt"}
    else:  # give_up
        return {"result": None, "attempts": attempts,
                "latency": time.perf_counter() - t0,
                "tokens": tokens_total,
                "note": "LLM sagte aufgeben — Fehler wird eskaliert"}


# ---- Ausführung ----

def main():
    phase_break("retry_strategies.py  ·  vier Ansätze im Vergleich")

    soft_frame(
        "DIE SITUATION",
        [
            "Werkzeug `price_lookup(sku)` schlägt die ersten 3 Aufrufe fehl",
            "  (HTTP 503 — Backend im Wartungsfenster).",
            "Beim 4. Aufruf funktioniert es wieder.",
            "",
            "Vier Strategien laufen gegen exakt dieselbe Fehler-Sequenz.",
        ],
    )

    strategies = [
        ("A · naive",              strategy_naive),
        ("B · exp. backoff",       strategy_backoff),
        ("C · circuit breaker",    strategy_circuit_breaker),
        ("D · LLM-guided",         strategy_llm_guided),
    ]

    results = []
    for label, fn in strategies:
        phase_break(f"Strategie {label}")
        r = fn()
        results.append((label, r))
        soft_frame(
            "  Ergebnis",
            [
                f"attempts : {r['attempts']}",
                f"latency  : {r['latency']:.2f} s",
                f"tokens   : {r['tokens']}",
                f"result   : {r['result']}",
                f"note     : {r['note']}",
            ],
        )

    # ---- Vergleichs-Tabelle ----
    lines = [
        f"{'Strategie':<22}  {'Versuche':>8}  {'Latenz':>8}"
        f"  {'Tokens':>6}  {'Ergebnis'}",
        "-" * 74,
    ]
    for label, r in results:
        got_result = "✓ OK" if r["result"] else "✗ Abbruch"
        lines.append(
            f"{label:<22}  {r['attempts']:>8}  {r['latency']:>7.2f}s"
            f"  {r['tokens']:>6}  {got_result}   ({r['note']})"
        )
    soft_frame("VERGLEICH", lines)

    soft_frame(
        "DER WOW-MOMENT",
        [
            "Strategie D ist die einzige, die den Fehler VERSTEHT.",
            "Statt blind zu warten, schickt sie den Fehlertext ans Modell",
            "und bekommt eine begründete Empfehlung zurück — nutze den",
            "fallback statt weiter auf das kaputte Backend zu hämmern.",
            "",
            "Preis dafür: ein zusätzlicher LLM-Call pro Fehler.",
            "Für seltene, semantisch komplexe Fehler ist das billig.",
            "Für Massen-Timeouts wäre es ruinös.",
            "",
            "Wähle die Strategie nach FEHLER-ART, nicht nach Werkzeug:",
            "  transiente Netz-Fehler   → B oder C",
            "  Anwendungsfehler mit     → D",
            "  variabler Semantik",
        ],
    )

    print()
    print("→ Retry ist keine Fehlerbehandlung.  Retry ist wie der Loop lebt.")
    print("→ Und wenn der Fehler klug ist, darf der Retry auch klug sein.")


if __name__ == "__main__":
    main()
