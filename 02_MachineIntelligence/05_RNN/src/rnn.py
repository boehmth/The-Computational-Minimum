# ============================================================
#  Vanilla Recurrent Neural Network (RNN) - Word Level
#
#  Eingabe:  Wort-Embedding e_t (aus Word2Vec, D-dim)
#  verborgen: h_t = tanh(W_xh @ e_t + W_hh @ h_{t-1} + b_h)
#  Ausgabe:   y_t = W_hy @ h_t + b_y                (Logits ueber V Woerter)
#  Softmax:   p_t = softmax(y_t)
#
#  Wichtiger Unterschied zum klassischen Char-RNN (Karpathy 2015):
#  - Der Eingaberaum ist nicht mehr One-Hot ueber V Zeichen,
#    sondern ein niedrigdimensionaler Embedding-Vektor.
#  - Damit ist der Input-Vektor 64-dim (statt V=1636-dim).
#  - Das Modell "erbt" die Semantik aus Word2Vec: Woerter, die
#    in der Bedeutung nahe sind, haben aehnliche Eingaben.
#
#  Das entspricht dem RNN-Language-Model von Mikolov (2010),
#  das den Weg fuer alle modernen Sprachmodelle bereitet hat.
# ============================================================

import numpy as np


class WordRNN:
    def __init__(self, vocab_size, embed_dim, hidden_size=128, seed=0):
        self.V = vocab_size
        self.D = embed_dim
        self.H = hidden_size
        rng = np.random.default_rng(seed)

        # Kleine Zufallsinit fuer die Gewichte
        self.Wxh = (rng.standard_normal((hidden_size, embed_dim)) * 0.01).astype(np.float32)
        self.Whh = (rng.standard_normal((hidden_size, hidden_size)) * 0.01).astype(np.float32)
        self.Why = (rng.standard_normal((vocab_size, hidden_size)) * 0.01).astype(np.float32)
        self.bh  = np.zeros((hidden_size,), dtype=np.float32)
        self.by  = np.zeros((vocab_size,), dtype=np.float32)

        # Adagrad-Akkumulatoren
        self._m = {
            "Wxh": np.zeros_like(self.Wxh),
            "Whh": np.zeros_like(self.Whh),
            "Why": np.zeros_like(self.Why),
            "bh":  np.zeros_like(self.bh),
            "by":  np.zeros_like(self.by),
        }

    # --------------------------------------------------------
    # Vorwaerts + Rueckwaerts (BPTT)
    # --------------------------------------------------------
    def forward_backward(self, embeds, targets, h_prev):
        """
        embeds:  (T, D) - Embedding-Vektoren fuer die Eingabe-Woerter
        targets: (T,)   - IDs der jeweils naechsten Woerter (Ziel)
        h_prev:  (H,)   - vorheriger Hidden-State
        Rueckgabe: (loss, gradients-dict, letzter Hidden-State)
        """
        T = len(targets)
        H = self.H
        V = self.V

        hs = np.zeros((T + 1, H), dtype=np.float32)
        ys = np.zeros((T, V), dtype=np.float32)
        ps = np.zeros((T, V), dtype=np.float32)
        hs[-1] = h_prev

        # ---- Forward ----
        loss = 0.0
        for t in range(T):
            hs[t] = np.tanh(self.Wxh @ embeds[t] + self.Whh @ hs[t - 1] + self.bh)
            ys[t] = self.Why @ hs[t] + self.by
            # Numerisch stabile Softmax
            e = np.exp(ys[t] - ys[t].max())
            ps[t] = e / e.sum()
            loss += -np.log(ps[t, targets[t]] + 1e-9)

        # ---- Backward (BPTT) ----
        dWxh = np.zeros_like(self.Wxh)
        dWhh = np.zeros_like(self.Whh)
        dWhy = np.zeros_like(self.Why)
        dbh  = np.zeros_like(self.bh)
        dby  = np.zeros_like(self.by)
        dh_next = np.zeros((H,), dtype=np.float32)

        for t in reversed(range(T)):
            dy = ps[t].copy()
            dy[targets[t]] -= 1.0

            dWhy += np.outer(dy, hs[t])
            dby  += dy

            dh = self.Why.T @ dy + dh_next
            dh_raw = (1.0 - hs[t] ** 2) * dh
            dbh += dh_raw
            dWxh += np.outer(dh_raw, embeds[t])
            dWhh += np.outer(dh_raw, hs[t - 1])
            dh_next = self.Whh.T @ dh_raw

        # Gradient Clipping (gegen exploding gradients)
        for g in (dWxh, dWhh, dWhy, dbh, dby):
            np.clip(g, -5.0, 5.0, out=g)

        return (loss, {"Wxh": dWxh, "Whh": dWhh, "Why": dWhy,
                       "bh": dbh, "by": dby},
                hs[T - 1])

    # --------------------------------------------------------
    # Adagrad-Update
    # --------------------------------------------------------
    def step(self, grads, lr=0.1):
        for name, g in grads.items():
            self._m[name] += g * g
            param = getattr(self, name)
            param -= lr * g / (np.sqrt(self._m[name]) + 1e-8)

    # --------------------------------------------------------
    # Sampling: aus dem trainierten Modell eine Sequenz erzeugen
    # --------------------------------------------------------
    def sample(self, h, seed_embed, embed_lookup, length,
               temperature=1.0, rng=None):
        """
        Erzeugt `length` Woerter (als IDs), beginnend mit seed_embed.

        seed_embed:    (D,) Startvektor
        embed_lookup:  (V, D) Matrix: gibt zu einem Wort-Index den Embedding-Vektor
        Rueckgabe:     Liste der generierten Wort-IDs
        """
        if rng is None:
            rng = np.random.default_rng()

        e = seed_embed
        ids = []
        for _ in range(length):
            h = np.tanh(self.Wxh @ e + self.Whh @ h + self.bh)
            y = self.Why @ h + self.by
            y = y / max(temperature, 1e-6)
            e_soft = np.exp(y - y.max())
            p = e_soft / e_soft.sum()
            idx = int(rng.choice(self.V, p=p))
            ids.append(idx)
            e = embed_lookup[idx]

        return ids, h