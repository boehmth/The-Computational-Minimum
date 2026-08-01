# ============================================================
#  Kleines MLP in NumPy (Vergleichsmodell zum CNN)
#
#  Architektur:
#     Eingabe (N, 196)       -- 14x14 flach
#         -> Dense 196 -> H  (ReLU)
#         -> Dense H -> 10   (Softmax)
#
#  H wird so gewaehlt, dass die Parameterzahl ungefaehr
#  zur CNN-Parameterzahl passt - damit der Vergleich fair
#  ist. So sieht man: gleicher Aufwand, aber der Bias
#  ("Bilder haben Struktur") macht den Unterschied.
# ============================================================

import numpy as np

from utils import relu, relu_grad, softmax


class SmallMLP:
    def __init__(self, input_size=196, hidden_size=32, num_classes=10, seed=0):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0.0, np.sqrt(2.0 / input_size),
                             size=(input_size, hidden_size)).astype(np.float32)
        self.b1 = np.zeros(hidden_size, dtype=np.float32)
        self.W2 = rng.normal(0.0, np.sqrt(2.0 / hidden_size),
                             size=(hidden_size, num_classes)).astype(np.float32)
        self.b2 = np.zeros(num_classes, dtype=np.float32)

    # --------------------------------------------------------
    def forward(self, X):
        """X: (N, 14, 14) oder (N, 196). Rueckgabe: probs (N, 10)."""
        if X.ndim == 3:
            X = X.reshape(X.shape[0], -1)
        z1 = X @ self.W1 + self.b1
        a1 = relu(z1)
        logits = a1 @ self.W2 + self.b2
        probs = softmax(logits)
        self._cache = {"X": X, "z1": z1, "a1": a1, "probs": probs}
        return probs

    # --------------------------------------------------------
    def backward(self, y_int, lr=0.05):
        c = self._cache
        n = c["X"].shape[0]

        d_logits = c["probs"].copy()
        d_logits[np.arange(n), y_int] -= 1.0
        d_logits /= n

        d_W2 = c["a1"].T @ d_logits
        d_b2 = d_logits.sum(axis=0)
        d_a1 = d_logits @ self.W2.T

        d_z1 = d_a1 * relu_grad(c["z1"])
        d_W1 = c["X"].T @ d_z1
        d_b1 = d_z1.sum(axis=0)

        self.W2 -= lr * d_W2
        self.b2 -= lr * d_b2
        self.W1 -= lr * d_W1
        self.b1 -= lr * d_b1

    # --------------------------------------------------------
    def predict(self, X):
        return self.forward(X).argmax(axis=1)

    def accuracy(self, X, y_int):
        return float((self.predict(X) == y_int).mean())

    def num_parameters(self):
        return self.W1.size + self.b1.size + self.W2.size + self.b2.size