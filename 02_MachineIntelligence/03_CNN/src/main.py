# ============================================================
#  Hauptexperiment fuer Meilenstein 3 (CNN):
#  MNIST-Lite (14x14) - MLP vs. CNN
#
#  Ablauf:
#    1) MNIST laden, auf 14x14 verkleinern
#    2) MLP und CNN mit vergleichbarer Groesse trainieren
#    3) Beide auf drei Testszenarien vergleichen:
#         - Original (unveraendert)
#         - Verschoben (dx, dy im Bereich +-2)
#         - Verschoben + Rauschen
#    4) Ein paar Beispiele + einige gelernte CNN-Filter zeigen
# ============================================================

import time

import numpy as np

from datasets import load_mnist_lite, print_ascii
from utils import shift_batch, add_noise_batch, batches
from cnn import MiniCNN
from mlp import SmallMLP


# ------------------------------------------------------------
# Hyperparameter
# ------------------------------------------------------------
N_TRAIN = 5000
N_TEST = 1000
EPOCHS = 8
BATCH_SIZE = 64
LR = 0.1

SEED = 42


# ------------------------------------------------------------
# Trainingsschleife (Mini-Batch SGD)
# ------------------------------------------------------------

def train_model(model, X, y, X_val, y_val, epochs=EPOCHS,
                batch_size=BATCH_SIZE, lr=LR, name="Model", rng=None):
    print(f"\n--- Training {name} ({model.num_parameters()} Parameter) ---")
    n = len(X)
    for epoch in range(1, epochs + 1):
        # Einfache Lernraten-Absenkung: nach Epoch 4 halbieren
        cur_lr = lr if epoch <= 4 else lr * 0.5
        t0 = time.time()
        for idx in batches(n, batch_size, rng=rng, shuffle=True):
            model.forward(X[idx])
            model.backward(y[idx], lr=cur_lr)
        train_acc = model.accuracy(X[:1000], y[:1000])
        val_acc = model.accuracy(X_val, y_val)
        print(f"[{name}] Epoch {epoch}/{epochs} "
              f"lr={cur_lr:.3f}  "
              f"train_acc={train_acc*100:5.2f}%  "
              f"val_acc={val_acc*100:5.2f}%  "
              f"time={time.time()-t0:4.1f}s")


# ------------------------------------------------------------
# Robustheits-Auswertung
# ------------------------------------------------------------

def evaluate_robustness(mlp, cnn, X_test, y_test, rng):
    print("\n==== Robustheitsvergleich (Testdaten, 1000 Bilder) ====")

    # 1) Original
    m_acc = mlp.accuracy(X_test, y_test)
    c_acc = cnn.accuracy(X_test, y_test)
    print(f"  Original:                MLP {m_acc*100:5.2f}%   CNN {c_acc*100:5.2f}%")

    # 2) Zufaellige Verschiebungen +-2 Pixel
    shifted = np.stack([
        shift_batch(X_test[i:i+1],
                    dx=int(rng.integers(-2, 3)),
                    dy=int(rng.integers(-2, 3)))[0]
        for i in range(len(X_test))
    ])
    m_acc_s = mlp.accuracy(shifted, y_test)
    c_acc_s = cnn.accuracy(shifted, y_test)
    print(f"  Verschoben (+-2 Pixel):  MLP {m_acc_s*100:5.2f}%   CNN {c_acc_s*100:5.2f}%")

    # 3) Verschoben + Rauschen
    noisy = add_noise_batch(shifted, sigma=0.3, rng=rng)
    m_acc_n = mlp.accuracy(noisy, y_test)
    c_acc_n = cnn.accuracy(noisy, y_test)
    print(f"  Verschoben + Rauschen:   MLP {m_acc_n*100:5.2f}%   CNN {c_acc_n*100:5.2f}%")


def show_examples(mlp, cnn, X_test, y_test, n=5):
    print("\n==== Ein paar Testbilder ====")
    for i in range(n):
        img = X_test[i]
        true = y_test[i]
        m_pred = int(mlp.predict(img[None])[0])
        c_pred = int(cnn.predict(img[None])[0])
        print(f"\n  Wahres Label: {true}   MLP: {m_pred}   CNN: {c_pred}")
        print_ascii(img)


def show_filters(cnn):
    print("\n==== Gelernte CNN-Filter (3x3) ====")
    for k in range(cnn.K):
        F = cnn.W_conv[k, 0]
        print(f"  Filter {k}:")
        for row in F:
            line = "    "
            for v in row:
                if v > 0.3:
                    line += " ++"
                elif v > 0.08:
                    line += "  +"
                elif v < -0.3:
                    line += " --"
                elif v < -0.08:
                    line += "  -"
                else:
                    line += "  ."
            print(line)


# ------------------------------------------------------------
# Hauptprogramm
# ------------------------------------------------------------

def main():
    rng = np.random.default_rng(SEED)

    # ---- Datensatz ----
    X_train, y_train, X_test, y_test = load_mnist_lite(
        n_train=N_TRAIN, n_test=N_TEST, seed=SEED
    )

    print("\nBeispielbild aus dem Trainingsdatensatz:")
    print(f"  Label = {y_train[0]}")
    print_ascii(X_train[0])

    # ---- MLP ----
    mlp = SmallMLP(input_size=14 * 14, hidden_size=32, num_classes=10, seed=SEED)
    train_model(mlp, X_train, y_train, X_test, y_test,
                name="MLP", rng=rng)

    # ---- CNN ----
    cnn = MiniCNN(num_filters=8, filter_size=3, num_classes=10,
                  input_size=14, seed=SEED)
    train_model(cnn, X_train, y_train, X_test, y_test,
                name="CNN", rng=rng)

    # ---- Vergleich ----
    print(f"\nParameterzahl:  MLP = {mlp.num_parameters()}   CNN = {cnn.num_parameters()}")
    evaluate_robustness(mlp, cnn, X_test, y_test, rng)

    show_examples(mlp, cnn, X_test, y_test, n=3)
    show_filters(cnn)


if __name__ == "__main__":
    main()