# ============================================================
#  Mini-CNN in NumPy (fuer 14x14 MNIST-Lite)
#
#  Architektur:
#     Eingabe (N, 1, 14, 14)
#         -> Conv 8 Filter, 3x3, stride 1, valid  -> (N, 8, 12, 12)
#         -> ReLU
#         -> MaxPool 2x2, stride 2                -> (N, 8, 6, 6)
#         -> Flatten                              -> (N, 8*6*6=288)
#         -> Dense 288 -> 10                      -> (N, 10)
#         -> Softmax
#
#  Wir schreiben Faltung und Pooling selbst, damit die
#  Mechanik sichtbar bleibt. Zur Beschleunigung nutzen wir
#  den "im2col"-Trick, der die Faltung als grosse
#  Matrixmultiplikation formuliert - so wie es auch in
#  professionellen Frameworks intern gemacht wird.
# ============================================================

import numpy as np

from utils import relu, relu_grad, softmax, cross_entropy_loss


# ============================================================
#  im2col: schneidet aus jedem Bild alle KxK-Patches heraus
# ============================================================

def im2col(images, kh, kw):
    """
    images: (N, C, H, W)
    Rueckgabe: (N, out_h * out_w, C * kh * kw)
       -- jeder Patch wird zu einer Zeile "flach gemacht"
    """
    n, c, h, w = images.shape
    out_h = h - kh + 1
    out_w = w - kw + 1

    # Wir bauen einen Puffer und kopieren jeden 3x3-Ausschnitt hinein.
    cols = np.empty((n, out_h, out_w, c, kh, kw), dtype=images.dtype)
    for i in range(kh):
        for j in range(kw):
            cols[:, :, :, :, i, j] = images[:, :, i:i + out_h, j:j + out_w].transpose(0, 2, 3, 1)
    return cols.reshape(n, out_h * out_w, c * kh * kw)


def col2im(cols, images_shape, kh, kw):
    """
    Rueckgabe der Gradienten in Bildform (fuer Rueckwaertspfad).
    cols: (N, out_h*out_w, C*kh*kw)
    images_shape: (N, C, H, W)
    """
    n, c, h, w = images_shape
    out_h = h - kh + 1
    out_w = w - kw + 1
    cols_r = cols.reshape(n, out_h, out_w, c, kh, kw)
    d_images = np.zeros(images_shape, dtype=cols.dtype)
    for i in range(kh):
        for j in range(kw):
            d_images[:, :, i:i + out_h, j:j + out_w] += cols_r[:, :, :, :, i, j].transpose(0, 3, 1, 2)
    return d_images


# ============================================================
#  Mini-CNN
# ============================================================

class MiniCNN:
    def __init__(self, num_filters=8, filter_size=3, num_classes=10,
                 input_size=14, seed=0):
        rng = np.random.default_rng(seed)
        self.K = num_filters
        self.kh = filter_size
        self.kw = filter_size
        self.in_h = input_size
        self.in_w = input_size
        self.conv_h = input_size - filter_size + 1   # 12
        self.conv_w = input_size - filter_size + 1
        self.pool_h = self.conv_h // 2                 # 6
        self.pool_w = self.conv_w // 2
        self.flat = self.K * self.pool_h * self.pool_w
        self.num_classes = num_classes

        # He-Initialisierung fuer ReLU
        self.W_conv = rng.normal(0.0, np.sqrt(2.0 / (filter_size * filter_size)),
                                 size=(self.K, 1, filter_size, filter_size)
                                 ).astype(np.float32)
        self.b_conv = np.zeros(self.K, dtype=np.float32)

        self.W_dense = rng.normal(0.0, np.sqrt(2.0 / self.flat),
                                  size=(self.flat, num_classes)).astype(np.float32)
        self.b_dense = np.zeros(num_classes, dtype=np.float32)

    # --------------------------------------------------------
    # Forward
    # --------------------------------------------------------
    def forward(self, X):
        """
        X: (N, 14, 14) oder (N, 1, 14, 14) float32 in [0, 1]
        Rueckgabe: (N, 10) Softmax-Wahrscheinlichkeiten
        Speichert Zwischenwerte in self._cache fuer backward.
        """
        if X.ndim == 3:
            X = X[:, None, :, :]     # (N, 1, H, W)
        n = X.shape[0]

        # ---- 1) Faltung als Matrixmultiplikation ----
        # cols: (N, 12*12, 1*3*3)  = (N, 144, 9)
        cols = im2col(X, self.kh, self.kw)

        # W_conv umformen: (K, 1, 3, 3) -> (9, K)
        W_flat = self.W_conv.reshape(self.K, -1).T   # (9, K)
        conv_pre = cols @ W_flat + self.b_conv       # (N, 144, K)
        conv_pre = conv_pre.transpose(0, 2, 1).reshape(n, self.K, self.conv_h, self.conv_w)

        # ---- 2) ReLU ----
        conv_relu = relu(conv_pre)

        # ---- 3) MaxPooling 2x2 ----
        # Wir reshapen zu (N, K, 6, 2, 6, 2) und nehmen das Max ueber die 2er-Achsen.
        pooled_reshape = conv_relu.reshape(n, self.K,
                                           self.pool_h, 2, self.pool_w, 2)
        pooled = pooled_reshape.max(axis=(3, 5))     # (N, K, 6, 6)
        # Fuer den Rueckweg brauchen wir die argmax-Positionen (als Maske).
        pool_mask = (pooled_reshape ==
                     pooled[:, :, :, None, :, None]).astype(np.float32)

        # ---- 4) Flatten ----
        flat = pooled.reshape(n, self.flat)          # (N, 288)

        # ---- 5) Dense + Softmax ----
        logits = flat @ self.W_dense + self.b_dense  # (N, 10)
        probs = softmax(logits)                      # (N, 10)

        self._cache = {
            "X": X, "cols": cols,
            "conv_pre": conv_pre, "conv_relu": conv_relu,
            "pooled": pooled, "pool_mask": pool_mask,
            "flat": flat, "logits": logits, "probs": probs,
        }
        return probs

    # --------------------------------------------------------
    # Backward + SGD-Update
    # --------------------------------------------------------
    def backward(self, y_int, lr=0.05):
        c = self._cache
        n = c["X"].shape[0]

        # ---- Softmax + Cross-Entropy: kombinierter Gradient ist einfach probs - y_onehot ----
        d_logits = c["probs"].copy()
        d_logits[np.arange(n), y_int] -= 1.0
        d_logits /= n                                # (N, 10)

        # Dense
        d_W_dense = c["flat"].T @ d_logits            # (288, 10)
        d_b_dense = d_logits.sum(axis=0)              # (10,)
        d_flat = d_logits @ self.W_dense.T            # (N, 288)

        # Rueck durch Flatten
        d_pooled = d_flat.reshape(n, self.K, self.pool_h, self.pool_w)

        # Rueck durch MaxPool: Gradient nur an die argmax-Positionen
        d_pool_expanded = d_pooled[:, :, :, None, :, None] * c["pool_mask"]
        d_conv_relu = d_pool_expanded.reshape(n, self.K, self.conv_h, self.conv_w)

        # Rueck durch ReLU
        d_conv_pre = d_conv_relu * relu_grad(c["conv_pre"])

        # Rueck durch die Faltung
        # d_conv_pre: (N, K, 12, 12) -> (N, 144, K)
        d_conv_flat = d_conv_pre.reshape(n, self.K, -1).transpose(0, 2, 1)
        # d_W_conv: sum ueber alle Patches -> (9, K)
        d_W_flat = np.einsum("npk,npj->jk", d_conv_flat, c["cols"])
        d_W_conv = d_W_flat.T.reshape(self.K, 1, self.kh, self.kw)
        d_b_conv = d_conv_pre.sum(axis=(0, 2, 3))     # (K,)

        # ---- SGD-Update ----
        self.W_dense -= lr * d_W_dense
        self.b_dense -= lr * d_b_dense
        self.W_conv -= lr * d_W_conv
        self.b_conv -= lr * d_b_conv

    # --------------------------------------------------------
    # Vorhersagen
    # --------------------------------------------------------
    def predict(self, X):
        probs = self.forward(X)
        return probs.argmax(axis=1)

    def accuracy(self, X, y_int):
        return float((self.predict(X) == y_int).mean())

    # --------------------------------------------------------
    # Parameterzahl (zur Vergleichbarkeit mit MLP)
    # --------------------------------------------------------
    def num_parameters(self):
        return (self.W_conv.size + self.b_conv.size
                + self.W_dense.size + self.b_dense.size)