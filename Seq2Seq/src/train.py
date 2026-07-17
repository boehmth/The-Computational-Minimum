# ============================================================
#  Hauptexperiment fuer Meilenstein 6 (Seq2Seq + Attention):
#  Zahlen 0..999  ->  deutsche Zahlwoerter
#
#  Ablauf:
#    1) Datensatz erzeugen (1000 Paare)
#    2) 800/200 Train/Test-Split
#    3) Seq2Seq mit Bahdanau-Attention trainieren (~1-2 Min)
#    4) Test-Accuracy messen (exakter Match)
#    5) Ein paar Beispiele mit Attention-Heatmap anzeigen
# ============================================================

import time

import numpy as np

from data import (
    make_dataset, train_test_split,
    INPUT_V, OUTPUT_V, INPUT_ITOS, OUTPUT_ITOS,
    SOS_ID, EOS_ID, PAD_ID, INPUT_LEN,
)
from seq2seq import Seq2SeqAttn
from visualize import render_attention


# ------------------------------------------------------------
# Hyperparameter
# ------------------------------------------------------------
EMBED_DIM = 32
ENC_HIDDEN = 64
DEC_HIDDEN = 64
EPOCHS = 60
LR = 0.1
SEED = 42


# ============================================================

def _decode_output(ids):
    return [OUTPUT_ITOS[i] for i in ids]


def accuracy(model, X, Y):
    correct = 0
    for x, y in zip(X, Y):
        pred, _ = model.predict(x, SOS_ID, EOS_ID, max_len=8)
        target = [int(t) for t in y[1:-1]]   # ohne <sos>/<eos>
        if pred == target:
            correct += 1
    return correct / max(len(X), 1)


def main():
    # ---- Daten ----
    X, Y = make_dataset()
    X_tr, Y_tr, X_te, Y_te, tr_idx, te_idx = train_test_split(X, Y, test_ratio=0.2, seed=SEED)
    print(f"Daten:  Training {len(X_tr)}  Test {len(X_te)}")
    print(f"Vokabular: Eingabe {INPUT_V} (Ziffern), Ausgabe {OUTPUT_V} Wortformen")

    # ---- Modell ----
    model = Seq2SeqAttn(INPUT_V, OUTPUT_V,
                        embed_dim=EMBED_DIM,
                        enc_hidden=ENC_HIDDEN,
                        dec_hidden=DEC_HIDDEN,
                        seed=SEED)

    rng = np.random.default_rng(SEED)

    # ---- Training ----
    t0 = time.time()
    for epoch in range(1, EPOCHS + 1):
        # Zufaellige Trainings­reihenfolge
        order = rng.permutation(len(X_tr))
        total_loss = 0.0
        for idx in order:
            x = X_tr[idx]
            y = Y_tr[idx]
            loss, cache = model.forward(x, y)
            grads = model.backward(cache)
            model.step(grads, lr=LR)
            total_loss += loss
        avg_loss = total_loss / len(X_tr)

        if epoch == 1 or epoch % 5 == 0 or epoch == EPOCHS:
            train_acc = accuracy(model, X_tr[:100], Y_tr[:100])
            test_acc = accuracy(model, X_te, Y_te)
            print(f"Epoche {epoch:3d}/{EPOCHS}  loss={avg_loss:.4f}  "
                  f"train_acc={train_acc*100:5.1f}%  "
                  f"test_acc={test_acc*100:5.1f}%  "
                  f"time={time.time()-t0:5.1f}s")

    # ---- Finale Auswertung ----
    print()
    print("=" * 70)
    final_test = accuracy(model, X_te, Y_te)
    print(f"Finale Test-Genauigkeit: {final_test*100:.1f}%  ({int(final_test*len(X_te))} von {len(X_te)})")

    # ---- Beispiele mit Attention-Heatmap ----
    print()
    print("=" * 70)
    print("BEISPIELE mit Attention-Heatmap:")

    demo_numbers = [7, 42, 23, 100, 199, 342, 999]
    for n in demo_numbers:
        x = X[n]
        y_true = Y[n]
        pred_ids, attn = model.predict(x, SOS_ID, EOS_ID, max_len=8)
        pred_tokens = _decode_output(pred_ids)
        true_tokens = _decode_output([int(t) for t in y_true[1:-1]])
        ok = "OK" if pred_tokens == true_tokens else "FALSCH"
        print(f"\n  n={n:3d}  Ziel: {' '.join(true_tokens):40s}  Vorhersage: {' '.join(pred_tokens)}   [{ok}]")

        # Attention-Heatmap (nur die "echten" Ausgabe-Zeitschritte, ohne <eos>)
        rows = min(len(pred_tokens), attn.shape[0])
        if rows > 0:
            render_attention(
                input_digits=[INPUT_ITOS[i] for i in x],
                output_tokens=pred_tokens[:rows],
                attn_matrix=attn[:rows],
                number=n,
            )


if __name__ == "__main__":
    main()