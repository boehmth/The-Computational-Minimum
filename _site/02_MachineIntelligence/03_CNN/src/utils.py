# ============================================================
#  Hilfsfunktionen fuer das CNN (NumPy-Version)
#
#  Alle Bilder sind entweder als (H, W) oder als Batch (N, H, W)
#  in float32 gespeichert. Werte in [0, 1].
# ============================================================

import numpy as np


# --------------------------------------------------------
# Aktivierungsfunktionen (vektorisiert)
# --------------------------------------------------------

def relu(x):
    return np.maximum(0.0, x)


def relu_grad(x):
    """Ableitung an der ROHEN Voraktivierung x (nicht am ReLU-Output)."""
    return (x > 0).astype(x.dtype)


def softmax(logits):
    """
    Numerisch stabile Softmax entlang der letzten Achse.
    logits: (N, C)
    """
    shifted = logits - logits.max(axis=-1, keepdims=True)
    exps = np.exp(shifted)
    return exps / exps.sum(axis=-1, keepdims=True)


# --------------------------------------------------------
# Verlust: Cross-Entropy fuer Softmax
# --------------------------------------------------------

def cross_entropy_loss(probs, y_int):
    """
    Mittlere Cross-Entropy.
    probs: (N, C) Softmax-Wahrscheinlichkeiten
    y_int: (N,)   ganzzahlige Labels
    """
    n = len(y_int)
    eps = 1e-12
    return -np.mean(np.log(probs[np.arange(n), y_int] + eps))


# --------------------------------------------------------
# Bild-Operationen (Batch-tauglich)
# --------------------------------------------------------

def shift_batch(images, dx, dy, fill=0.0):
    """
    Verschiebt (N, H, W)-Bilder um (dx, dy).
    dx > 0: nach rechts, dy > 0: nach unten.
    Rand wird mit `fill` aufgefuellt.
    """
    n, h, w = images.shape
    out = np.full_like(images, fill)
    # Zielbereiche
    src_row_start = max(0, -dy)
    src_row_end = min(h, h - dy)
    src_col_start = max(0, -dx)
    src_col_end = min(w, w - dx)
    dst_row_start = max(0, dy)
    dst_row_end = dst_row_start + (src_row_end - src_row_start)
    dst_col_start = max(0, dx)
    dst_col_end = dst_col_start + (src_col_end - src_col_start)
    if src_row_end > src_row_start and src_col_end > src_col_start:
        out[:, dst_row_start:dst_row_end, dst_col_start:dst_col_end] = \
            images[:, src_row_start:src_row_end, src_col_start:src_col_end]
    return out


def add_noise_batch(images, sigma=0.2, rng=None):
    """Additives Gauss-Rauschen, danach clip in [0, 1]."""
    if rng is None:
        rng = np.random.default_rng()
    noisy = images + rng.normal(0.0, sigma, size=images.shape).astype(images.dtype)
    return np.clip(noisy, 0.0, 1.0)


# --------------------------------------------------------
# Kleine Helfer
# --------------------------------------------------------

def batches(n, batch_size, rng=None, shuffle=True):
    """Erzeugt Index-Batches (fuer Mini-Batch-Training)."""
    if rng is None:
        rng = np.random.default_rng()
    idx = np.arange(n)
    if shuffle:
        rng.shuffle(idx)
    for start in range(0, n, batch_size):
        yield idx[start:start + batch_size]