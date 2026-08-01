# ============================================================
#  Seq2Seq mit Bahdanau-Attention (in NumPy, komplett von Hand)
#
#  Aufbau:
#    Encoder: einlagiges tanh-RNN, das die Zifferfolge von
#      links nach rechts liest. Pro Position i entsteht ein
#      Hidden-State h_i. Wir bleiben bewusst uni­direktional,
#      damit die Attention *sichtbar zwischen den Ziffern
#      wandert*. (Ein bidirektionaler Encoder waere maechtiger,
#      wuerde aber die Attention "kollabieren" lassen - siehe
#      die Diskussion "Warum unidirektional?" in der README.)
#
#    Decoder: einlagiges tanh-RNN, das Wort fuer Wort erzeugt.
#      Fuer Zeitschritt t:
#
#      score_i  = v · tanh( W_a @ h_i + U_a @ s_{t-1} )
#      alpha_i  = softmax(score_i)
#      c_t      = sum_i alpha_i * h_i
#
#      s_t      = tanh( W_ss @ s_{t-1} + W_sc @ c_t
#                       + W_sy @ emb(y_{t-1}) + b_s )
#      logits_t = W_out @ s_t + b_out
#
#  Training: Teacher Forcing, Cross-Entropy, Adagrad.
#  Backprop: komplett selbst hergeleitet.
# ============================================================

import numpy as np


def _softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)


def _init(rng, shape, scale=None):
    if scale is None:
        scale = np.sqrt(1.0 / shape[-1])
    return (rng.standard_normal(shape) * scale).astype(np.float32)


class Seq2SeqAttn:
    def __init__(self, in_vocab, out_vocab, embed_dim=32,
                 enc_hidden=64, dec_hidden=64, seed=0):
        self.V_in = in_vocab
        self.V_out = out_vocab
        self.D = embed_dim
        self.He = enc_hidden
        self.Hd = dec_hidden

        rng = np.random.default_rng(seed)

        # Encoder (unidirektional)
        self.enc_Wxh = _init(rng, (self.He, self.V_in))
        self.enc_Whh = _init(rng, (self.He, self.He))
        self.enc_bh  = np.zeros(self.He, dtype=np.float32)

        # Decoder-Embedding
        self.emb = _init(rng, (self.V_out, self.D))

        # Bahdanau-Attention
        self.att_W = _init(rng, (self.He, self.He))
        self.att_U = _init(rng, (self.He, self.Hd))
        self.att_v = _init(rng, (self.He,))

        # Decoder-Rekurrenz
        self.dec_Wss = _init(rng, (self.Hd, self.Hd))
        self.dec_Wsc = _init(rng, (self.Hd, self.He))
        self.dec_Wsy = _init(rng, (self.Hd, self.D))
        self.dec_bs  = np.zeros(self.Hd, dtype=np.float32)

        # Ausgabe
        self.W_out = _init(rng, (self.V_out, self.Hd))
        self.b_out = np.zeros(self.V_out, dtype=np.float32)

        self._param_names = [
            "enc_Wxh", "enc_Whh", "enc_bh",
            "emb",
            "att_W", "att_U", "att_v",
            "dec_Wss", "dec_Wsc", "dec_Wsy", "dec_bs",
            "W_out", "b_out",
        ]
        self._m = {n: np.zeros_like(getattr(self, n)) for n in self._param_names}

    # ---- Encoder ----
    def _encode(self, x_ids):
        T_in = len(x_ids)
        x_onehot = np.zeros((T_in, self.V_in), dtype=np.float32)
        x_onehot[np.arange(T_in), x_ids] = 1.0

        h_all = np.zeros((T_in, self.He), dtype=np.float32)
        h_prev = np.zeros(self.He, dtype=np.float32)
        for t in range(T_in):
            h_prev = np.tanh(
                self.enc_Wxh @ x_onehot[t]
                + self.enc_Whh @ h_prev
                + self.enc_bh
            )
            h_all[t] = h_prev
        return h_all, x_onehot

    # ---- Decoder-Schritt ----
    def _decode_step(self, h_all, s_prev, y_prev_id):
        Us = self.att_U @ s_prev                     # (He,)
        pre = np.tanh(h_all @ self.att_W.T + Us)     # (T_in, He)
        scores = pre @ self.att_v                    # (T_in,)
        alpha = _softmax(scores)                     # (T_in,)
        c = alpha @ h_all                            # (He,)

        e_y = self.emb[y_prev_id]                    # (D,)

        s_new = np.tanh(
            self.dec_Wss @ s_prev
            + self.dec_Wsc @ c
            + self.dec_Wsy @ e_y
            + self.dec_bs
        )
        logits = self.W_out @ s_new + self.b_out
        probs = _softmax(logits)

        cache = {
            "s_prev": s_prev,
            "y_prev_id": y_prev_id,
            "e_y": e_y,
            "Us": Us, "pre": pre, "scores": scores,
            "alpha": alpha, "c": c,
            "s_new": s_new, "logits": logits, "probs": probs,
        }
        return probs, s_new, alpha, cache

    # ---- Vorwaerts (Teacher Forcing) ----
    def forward(self, x_ids, y_ids):
        h_all, x_onehot = self._encode(x_ids)

        s_prev = np.zeros(self.Hd, dtype=np.float32)
        step_caches = []
        loss = 0.0
        T_out = len(y_ids) - 1

        for t in range(T_out):
            y_prev = int(y_ids[t])
            y_true = int(y_ids[t + 1])
            probs, s_new, alpha, cache = self._decode_step(h_all, s_prev, y_prev)
            loss += -np.log(probs[y_true] + 1e-9)
            cache["y_true"] = y_true
            step_caches.append(cache)
            s_prev = s_new

        cache_all = {
            "h_all": h_all, "x_onehot": x_onehot, "x_ids": x_ids,
            "y_ids": y_ids, "steps": step_caches,
        }
        return loss / max(T_out, 1), cache_all

    # ---- Rueckwaerts (BPTT) ----
    def backward(self, cache_all):
        grads = {n: np.zeros_like(getattr(self, n)) for n in self._param_names}

        h_all = cache_all["h_all"]
        x_onehot = cache_all["x_onehot"]
        steps = cache_all["steps"]
        T_out = len(steps)
        T_in = h_all.shape[0]

        loss_scale = 1.0 / max(T_out, 1)

        d_h_all = np.zeros_like(h_all)
        d_s_next = np.zeros(self.Hd, dtype=np.float32)

        for t in reversed(range(T_out)):
            c = steps[t]
            probs = c["probs"]
            y_true = c["y_true"]

            # Softmax + CE
            d_logits = probs.copy()
            d_logits[y_true] -= 1.0
            d_logits *= loss_scale

            grads["W_out"] += np.outer(d_logits, c["s_new"])
            grads["b_out"] += d_logits

            # Decoder-State
            d_s_new = self.W_out.T @ d_logits + d_s_next
            d_pre_s = (1.0 - c["s_new"] ** 2) * d_s_new

            grads["dec_Wss"] += np.outer(d_pre_s, c["s_prev"])
            grads["dec_Wsc"] += np.outer(d_pre_s, c["c"])
            grads["dec_Wsy"] += np.outer(d_pre_s, c["e_y"])
            grads["dec_bs"]  += d_pre_s

            d_s_prev_from_ss = self.dec_Wss.T @ d_pre_s
            d_c = self.dec_Wsc.T @ d_pre_s               # (He,)

            d_e_y = self.dec_Wsy.T @ d_pre_s
            grads["emb"][c["y_prev_id"]] += d_e_y

            # Attention
            d_alpha = h_all @ d_c                        # (T_in,)
            d_h_all += np.outer(c["alpha"], d_c)         # (T_in, He)

            d_scores = c["alpha"] * (d_alpha - (c["alpha"] * d_alpha).sum())

            grads["att_v"] += c["pre"].T @ d_scores
            d_pre = np.outer(d_scores, self.att_v)       # (T_in, He)

            d_pre_raw = (1.0 - c["pre"] ** 2) * d_pre    # (T_in, He)

            grads["att_W"] += d_pre_raw.T @ h_all
            d_h_all += d_pre_raw @ self.att_W

            d_Us = d_pre_raw.sum(axis=0)
            grads["att_U"] += np.outer(d_Us, c["s_prev"])
            d_s_prev_from_att = self.att_U.T @ d_Us

            d_s_next = d_s_prev_from_ss + d_s_prev_from_att

        # Encoder-BPTT
        d_h_prev = np.zeros(self.He, dtype=np.float32)
        for i in reversed(range(T_in)):
            dh = d_h_all[i] + d_h_prev
            d_pre_h = (1.0 - h_all[i] ** 2) * dh
            grads["enc_bh"] += d_pre_h
            grads["enc_Wxh"] += np.outer(d_pre_h, x_onehot[i])
            if i > 0:
                grads["enc_Whh"] += np.outer(d_pre_h, h_all[i - 1])
            d_h_prev = self.enc_Whh.T @ d_pre_h

        # Clipping
        for name, g in grads.items():
            np.clip(g, -5.0, 5.0, out=g)

        return grads

    # ---- Adagrad ----
    def step(self, grads, lr=0.05):
        for name, g in grads.items():
            self._m[name] += g * g
            param = getattr(self, name)
            param -= lr * g / (np.sqrt(self._m[name]) + 1e-8)

    # ---- Inferenz ----
    def predict(self, x_ids, sos_id, eos_id, max_len=8):
        h_all, _ = self._encode(x_ids)
        s_prev = np.zeros(self.Hd, dtype=np.float32)
        y_prev = sos_id

        out_ids = []
        attns = []
        for _ in range(max_len):
            probs, s_new, alpha, _ = self._decode_step(h_all, s_prev, y_prev)
            y_prev = int(np.argmax(probs))
            attns.append(alpha)
            if y_prev == eos_id:
                break
            out_ids.append(y_prev)
            s_prev = s_new
        return out_ids, np.stack(attns) if attns else np.zeros((0, len(x_ids)))
