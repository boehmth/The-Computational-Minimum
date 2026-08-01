"""
model.py - Modell fuer TinyInstruct

Wir verwenden BEWUSST DIE GLEICHE Modell-Architektur wie in Kapitel 3.1
(TinyGPT). Das ist die zentrale Aussage dieses Kapitels: die Faehigkeit
"Instruktionen befolgen" entsteht NICHT durch eine neue Architektur, sondern
allein durch ein neues Trainingsverfahren (maskierter Loss auf
Response-Tokens, siehe `data.py`).

Deshalb importieren wir `GPTMini` aus dem Nachbar-Kapitel, statt eine eigene
Copy-Paste-Variante zu pflegen. Falls das Kapitel 3.1 einmal umgezogen
werden sollte, muss diese eine Import-Zeile angepasst werden.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

import torch

# -------------------------------------------------------------------------
# GPTMini aus Kapitel 3.1 (TinyGPT) importieren
# -------------------------------------------------------------------------
# Wir erweitern sys.path um den src-Ordner von 01_TinyGPT, damit `tinyGPT.py`
# als Modul importierbar wird, ohne dass wir ein separates Python-Package
# einrichten muessen. Das ist bewusst simpel gehalten - fuer ein Buch, in dem
# jedes Kapitel eigenstaendig sein soll, waere ein Setup-tools-Paket
# Overkill.
_HERE = os.path.dirname(os.path.abspath(__file__))
_TINYGPT_SRC = os.path.normpath(os.path.join(_HERE, "..", "..", "01_TinyGPT", "src"))
if _TINYGPT_SRC not in sys.path:
    sys.path.insert(0, _TINYGPT_SRC)

from tinyGPT import GPTMini  # noqa: E402  (Import nach sys.path-Aenderung)


def build_model(
    vocab_size: int,
    context_length: int,
    embed_dim: int,
    n_heads: int,
    n_layers: int,
    checkpoint_path: Optional[str] = None,
    device: Optional[torch.device] = None,
) -> GPTMini:
    """
    Baut eine `GPTMini`-Instanz und laedt optional einen Base-Modell-
    Checkpoint. Ohne Checkpoint startet das Training von einem
    zufaelligen Modell (nuetzlich fuer den Rauchtest); mit Checkpoint
    startet es von einem in Kapitel 3.1 vortrainierten Modell (der
    realistische Fall).
    """
    model = GPTMini(
        vocab_size=vocab_size,
        context_length=context_length,
        embed_dim=embed_dim,
        n_heads=n_heads,
        n_layers=n_layers,
    )

    if checkpoint_path:
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(
                f"Base-Modell-Checkpoint nicht gefunden: {checkpoint_path}. "
                f"Trainiere zuerst Kapitel 3.1 (TinyGPT) und lege den "
                f"gespeicherten state_dict dort ab, oder setze BASE_MODEL_CKPT "
                f"in der config.json auf null, um von zufaelligen Gewichten "
                f"aus zu starten."
            )
        state = torch.load(checkpoint_path, map_location="cpu")
        # Erlaubte Formate: entweder direkt ein state_dict oder ein Dict mit
        # dem Schluessel "model_state_dict".
        if isinstance(state, dict) and "model_state_dict" in state:
            state = state["model_state_dict"]
        missing, unexpected = model.load_state_dict(state, strict=False)
        if missing:
            print(f"[model] Warnung: fehlende Keys im Checkpoint: {missing[:5]}"
                  f"{'...' if len(missing) > 5 else ''}")
        if unexpected:
            print(f"[model] Warnung: unerwartete Keys im Checkpoint: {unexpected[:5]}"
                  f"{'...' if len(unexpected) > 5 else ''}")
        print(f"[model] Base-Modell geladen aus {checkpoint_path}.")
    else:
        print("[model] Kein Base-Checkpoint angegeben -> Training startet mit "
              "zufaelligen Gewichten. Fuer die didaktische Aussage 'derselbe "
              "Vor-Nach-Vergleich' waere ein echter TinyGPT-Checkpoint besser, "
              "aber der Trainings-Loop laeuft trotzdem.")

    if device is not None:
        model = model.to(device)
    return model