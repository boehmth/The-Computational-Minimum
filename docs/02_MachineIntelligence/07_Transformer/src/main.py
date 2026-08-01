# ============================================================
#  Meilenstein 7 - Der Transformer: Forward-Only Demo
#
#  Phase 1 dieses Kapitels: Wir zeigen die komplette Encoder-
#  Decoder-Architektur, laden Beispieldaten und rendern die
#  Multi-Head-Cross-Attention-Heatmaps.
#
#  Achtung: Das Modell ist NICHT trainiert. Die Vorhersagen
#  sind zufaellig - der Zweck ist, die ARCHITEKTUR sichtbar
#  zu machen: parallele Verarbeitung, Multi-Head-Attention,
#  Encoder/Decoder-Datenfluss.
#
#  Phase 2 (Backward + Training) folgt spaeter.
# ============================================================

import numpy as np

from data import (
    make_dataset, train_test_split,
    INPUT_V, OUTPUT_V, INPUT_ITOS, OUTPUT_ITOS,
    SOS_ID, EOS_ID, INPUT_LEN,
)
from transformer import Transformer, count_parameters
from visualize import render_multi_head_attention


# ------------------------------------------------------------
# Hyperparameter (siehe README)
# ------------------------------------------------------------
D_MODEL = 64
N_HEADS = 4
D_FF = 128
N_LAYERS = 2
MAX_LEN = 16
SEED = 42


def _decode_output(ids):
    return [OUTPUT_ITOS[i] for i in ids]


def main():
    # ---- Daten ----
    X, Y = make_dataset()
    print(f"Datensatz: {len(X)} Paare  |  Eingabe-Vokabular {INPUT_V}  "
          f"|  Ausgabe-Vokabular {OUTPUT_V}")

    # ---- Modell ----
    model = Transformer(
        src_vocab=INPUT_V,
        tgt_vocab=OUTPUT_V,
        d_model=D_MODEL,
        n_heads=N_HEADS,
        d_ff=D_FF,
        n_layers=N_LAYERS,
        max_len=MAX_LEN,
        seed=SEED,
    )
    n_params = count_parameters(model)
    print(f"Modell:   d_model={D_MODEL}, n_heads={N_HEADS}, "
          f"n_layers={N_LAYERS}, d_ff={D_FF}")
    print(f"Parameter: {n_params:,}")
    print()

    print("=" * 66)
    print("PHASE 1: Forward-Only Demo (Modell ist NICHT trainiert)")
    print("=" * 66)
    print()
    print("Der Zweck dieser Demo ist nicht die Genauigkeit der Vorhersage,")
    print("sondern die *Architektur*: Encoder-Decoder-Datenfluss,")
    print("Multi-Head-Attention, parallele Verarbeitung.")
    print()

    # ---- Ein paar Beispiele ----
    demo_numbers = [7, 42, 199, 342, 999]

    for n in demo_numbers:
        src = X[n]
        tgt_full = Y[n]
        true_tokens = _decode_output([int(t) for t in tgt_full[1:-1]])

        pred_ids, cross = model.predict(src, SOS_ID, EOS_ID, max_len=8)
        pred_tokens = _decode_output(pred_ids)

        print()
        print(f"  n={n:3d}  Ziel: {' '.join(true_tokens):40s}  "
              f"Vorhersage (untrainiert): {' '.join(pred_tokens)}")

        # Zeige nur die "echten" Ausgabe-Zeitschritte, ohne evtl. <eos>
        rows = min(len(pred_tokens), cross.shape[1])
        if rows > 0:
            render_multi_head_attention(
                input_digits=[INPUT_ITOS[i] for i in src],
                output_tokens=pred_tokens[:rows],
                attn_matrix=cross[:, :rows, :],
                number=n,
            )
        print()

    print("=" * 66)
    print("Beobachtung:")
    print("=" * 66)
    print()
    print("- Alle Attention-Zeilen sind ZUFAELLIG. Das ist erwartet -")
    print("  das Modell ist untrainiert. Nach dem Training werden")
    print("  klare Muster sichtbar (siehe Phase 2).")
    print("- Die Vorhersage produziert Wortmuell. Das ist auch erwartet.")
    print("- Aber: Alle Shapes stimmen, die Architektur laeuft, alle")
    print("  Koepfe zeigen unterschiedliche zufaellige Muster - genau")
    print("  das Multi-Head-Verhalten, das nach dem Training sinnvoll")
    print("  werden wird.")


if __name__ == "__main__":
    main()