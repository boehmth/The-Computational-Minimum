# ============================================================
#  Word2Vec: Skip-Gram mit Negative Sampling
#
#  Grundidee (Mikolov et al., 2013):
#     Fuer jedes "Zentrumswort" c im Text sagt das Modell voraus,
#     welche anderen Woerter in seiner Umgebung (Kontextfenster)
#     auftauchen. Dabei lernt es zwei Vektor-Sets:
#         W_in [V, D] : ein Vektor pro Zentrumswort
#         W_out[V, D] : ein Vektor pro Kontext-/negativem Wort
#     Nach dem Training verwenden wir W_in als "Wort-Embedding".
#
#  Verlustfunktion (Negative Sampling):
#     Fuer jedes positive Paar (c, o) - "c und o standen nebeneinander" -
#     ziehen wir K "negative" Woerter n1..nK zufaellig aus dem Vokabular.
#     Ziel:  Sigmoid(W_in[c] . W_out[o])            -> 1
#            Sigmoid(W_in[c] . W_out[n_j])          -> 0    fuer alle j
#
#     Log-Verlust:
#        L = -log sig(<c,o>) - sum_j log sig(-<c,n_j>)
#
#  Warum "Negative Sampling"? Weil eine echte Softmax ueber alle V
#  Woerter (hier V ~ 1600) pro Trainingsschritt sehr teuer waere.
#  Mit K Negativen (typisch 5-15) wird der Aufwand konstant klein.
# ============================================================

import math
import time

import numpy as np


class SkipGramNS:
    """
    Skip-Gram-Modell mit Negative Sampling.
    """

    def __init__(self, vocab_size, embed_dim=64, seed=0):
        self.V = vocab_size
        self.D = embed_dim
        rng = np.random.default_rng(seed)

        # He-artige, kleine Initialisierung
        scale = 0.5 / embed_dim
        self.W_in = (rng.standard_normal((vocab_size, embed_dim)) * scale).astype(np.float32)
        self.W_out = np.zeros((vocab_size, embed_dim), dtype=np.float32)

    # --------------------------------------------------------
    # Trainings-Paare erzeugen (Skip-Gram-Fenster)
    # --------------------------------------------------------
    @staticmethod
    def generate_pairs(token_ids, window=5, rng=None):
        """
        Erzeugt Skip-Gram-Paare (center, context) aus einer Token-ID-Sequenz.
        Fuer jedes Wort waehlen wir zufaellig ein Fenster in [1..window],
        um nahe Nachbarn staerker zu gewichten (Mikolov-Trick).
        """
        if rng is None:
            rng = np.random.default_rng()
        n = len(token_ids)
        centers = []
        contexts = []
        for i in range(n):
            w = int(rng.integers(1, window + 1))
            lo = max(0, i - w)
            hi = min(n, i + w + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                centers.append(token_ids[i])
                contexts.append(token_ids[j])
        return np.array(centers, dtype=np.int64), np.array(contexts, dtype=np.int64)

    # --------------------------------------------------------
    # Negative-Sampling-Tabelle
    # --------------------------------------------------------
    @staticmethod
    def build_negative_table(counts, power=0.75, table_size=1_000_000):
        """
        Baut eine Nachschlage-Tabelle, aus der wir Negativ-Beispiele
        proportional zu (count^power) ziehen (Standard-Trick).
        """
        probs = np.array(counts, dtype=np.float64) ** power
        probs /= probs.sum()
        table = np.zeros(table_size, dtype=np.int64)
        # kumulative Verteilung
        cum = np.cumsum(probs)
        # Punkte im Einheitsintervall gleichmaessig verteilen
        pts = np.linspace(0.0, 1.0 - 1e-12, table_size)
        table = np.searchsorted(cum, pts).astype(np.int64)
        return table

    # --------------------------------------------------------
    # Ein Trainingsschritt (Batch)
    # --------------------------------------------------------
    def train_batch(self, centers, contexts, neg_table, k=5, lr=0.025, rng=None):
        if rng is None:
            rng = np.random.default_rng()
        B = centers.shape[0]

        # K Negative pro positivem Paar
        neg = neg_table[rng.integers(0, len(neg_table), size=(B, k))]  # (B, K)

        # Vektoren einholen
        v_c = self.W_in[centers]                  # (B, D)
        u_pos = self.W_out[contexts]              # (B, D)
        u_neg = self.W_out[neg]                   # (B, K, D)

        # Positive Skalarprodukte
        pos_score = np.einsum("bd,bd->b", v_c, u_pos)   # (B,)
        pos_sig = _sigmoid(pos_score)                   # (B,)

        # Negative Skalarprodukte
        neg_score = np.einsum("bd,bkd->bk", v_c, u_neg) # (B, K)
        neg_sig = _sigmoid(neg_score)                   # (B, K)

        # Gradienten fuers Negative-Sampling-Loss:
        #    dL/dpos_score =  (pos_sig - 1)     -> "sollte 1 sein"
        #    dL/dneg_score =   neg_sig          -> "sollte 0 sein"
        grad_pos = (pos_sig - 1.0)[:, None]             # (B, 1)
        grad_neg = neg_sig[:, :, None]                  # (B, K, 1)

        # Gradienten auf die einzelnen Vektoren
        d_v_c_from_pos = grad_pos * u_pos                            # (B, D)
        d_v_c_from_neg = (grad_neg * u_neg).sum(axis=1)              # (B, D)
        d_v_c = d_v_c_from_pos + d_v_c_from_neg                      # (B, D)

        d_u_pos = grad_pos * v_c                                     # (B, D)
        d_u_neg = grad_neg * v_c[:, None, :]                         # (B, K, D)

        # Parameter-Updates (SGD, mit np.add.at fuer wiederholte Indizes)
        np.add.at(self.W_in, centers, -lr * d_v_c)
        np.add.at(self.W_out, contexts, -lr * d_u_pos)
        np.add.at(self.W_out, neg.reshape(-1),
                  -lr * d_u_neg.reshape(-1, self.D))

        # Fuer Logging: mittlerer Log-Loss
        eps = 1e-9
        loss = -(np.log(pos_sig + eps).mean()
                 + np.log(1.0 - neg_sig + eps).sum(axis=1).mean())
        return float(loss)

    # --------------------------------------------------------
    # Kompletter Trainingslauf
    # --------------------------------------------------------
    def train(self, token_ids, counts, epochs=5, window=5, k=5,
              batch_size=1024, lr_start=0.025, lr_end=0.001,
              seed=0, log_every=100):
        rng = np.random.default_rng(seed)
        neg_table = self.build_negative_table(counts)

        for epoch in range(1, epochs + 1):
            t0 = time.time()
            centers, contexts = self.generate_pairs(token_ids, window=window, rng=rng)
            perm = rng.permutation(len(centers))
            centers = centers[perm]
            contexts = contexts[perm]

            n_batches = (len(centers) + batch_size - 1) // batch_size
            total_loss = 0.0
            for b in range(n_batches):
                s = b * batch_size
                e = s + batch_size
                # Lineare LR-Absenkung ueber Epoche und Batch
                progress = (epoch - 1 + b / n_batches) / epochs
                lr = lr_start * (1 - progress) + lr_end * progress
                total_loss += self.train_batch(
                    centers[s:e], contexts[s:e],
                    neg_table, k=k, lr=lr, rng=rng
                )
            avg_loss = total_loss / n_batches
            print(f"[W2V] Epoche {epoch}/{epochs}  Loss={avg_loss:.4f}  "
                  f"Zeit={time.time()-t0:.1f}s  Paare={len(centers):,}")

    # --------------------------------------------------------
    # Embedding fuer ein einzelnes Wort (per Index)
    # --------------------------------------------------------
    def embedding(self, word_id):
        return self.W_in[word_id]


def _sigmoid(x):
    # Numerisch stabil
    out = np.empty_like(x)
    pos = x >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-x[pos]))
    neg = ~pos
    ex = np.exp(x[neg])
    out[neg] = ex / (1.0 + ex)
    return out