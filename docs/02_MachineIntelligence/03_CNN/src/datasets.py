# ============================================================
#  MNIST-Lite: MNIST auf 14x14 herunter­gerechnet
#
#  Historisch: Yann LeCun hat sein LeNet 1998 auf genau
#  dieser Aufgabe entwickelt - handgeschriebene Ziffern
#  klassifizieren. Wir laden hier MNIST via sklearn und
#  verkleinern die 28x28-Bilder durch 2x2-Blockmittelung
#  auf 14x14, damit das Training in reinem NumPy noch in
#  wenigen Minuten laeuft.
# ============================================================

import numpy as np
from sklearn.datasets import fetch_openml


def _downsample_2x2(images_28):
    """
    Verkleinert (N, 28, 28) auf (N, 14, 14) durch Blockmittelung.
    Jedes 2x2-Feld wird zu einem Pixel.
    """
    n = images_28.shape[0]
    # Umsortieren: (N, 14, 2, 14, 2) und dann ueber die 2er-Achsen mitteln
    reshaped = images_28.reshape(n, 14, 2, 14, 2)
    return reshaped.mean(axis=(2, 4))


def load_mnist_lite(n_train=5000, n_test=1000, seed=42):
    """
    Laedt MNIST (per sklearn, gecacht) und liefert ein kleineres
    14x14-Subset zurueck.

    Rueckgabe:
        X_train:  (n_train, 14, 14)  float32, Werte in [0, 1]
        y_train:  (n_train,)         int (0-9)
        X_test:   (n_test, 14, 14)   float32
        y_test:   (n_test,)          int
    """
    print("[MNIST] Lade Datensatz (beim ersten Aufruf ~10-30s, danach gecacht)...")
    mnist = fetch_openml("mnist_784", version=1, as_frame=False, cache=True)
    X = mnist.data.astype(np.float32) / 255.0   # normiert auf [0, 1]
    y = mnist.target.astype(np.int64)

    X = X.reshape(-1, 28, 28)
    X = _downsample_2x2(X).astype(np.float32)    # (70000, 14, 14)

    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(X))
    X = X[idx]
    y = y[idx]

    X_train = X[:n_train]
    y_train = y[:n_train]
    X_test = X[n_train:n_train + n_test]
    y_test = y[n_train:n_train + n_test]

    print(f"[MNIST] Training:  {X_train.shape}  Labels: {y_train.shape}")
    print(f"[MNIST] Test:      {X_test.shape}   Labels: {y_test.shape}")
    return X_train, y_train, X_test, y_test


def one_hot(y, num_classes=10):
    """Wandelt ein Label-Array (N,) in eine One-Hot-Matrix (N, num_classes)."""
    out = np.zeros((len(y), num_classes), dtype=np.float32)
    out[np.arange(len(y)), y] = 1.0
    return out


def print_ascii(image_14):
    """Gibt ein 14x14-Bild als ASCII-Kunstwerk aus (fuer Debug/Anschauung)."""
    ramp = " .:-=+*#%@"
    for row in image_14:
        line = "".join(ramp[min(len(ramp) - 1, int(v * len(ramp)))] for v in row)
        print(line)