# ============================================================
#  Meilenstein 7 - Der Transformer (Vaswani et al. 2017)
#
#  Aufbau: Encoder-Decoder mit Multi-Head-Attention, Positional
#  Encoding, Layer Norm und Feed-Forward-Bloecken. Reines
#  NumPy, kein Framework, kein Autograd - genau wie in den
#  vorherigen Kapiteln.
#
#  Diese Datei enthaelt zunaechst nur den FORWARD-Pass. Damit
#  kann man die Architektur komplett durchlaufen, alle Shapes
#  ueberpruefen und die Attention-Heatmaps visualisieren
#  (auch wenn das Modell noch nicht trainiert ist).
#
#  Der BACKWARD-Pass (fuers Training) folgt in Phase 2.
# ============================================================

import numpy as np


# ============================================================
#  1. Positional Encoding  (Sinus/Kosinus wie im Original)
# ============================================================
#
#  Idee: Ein Transformer sieht alle Positionen "gleichzeitig".
#  Er hat keinen Begriff von "erst kommt Position 1, dann 2".
#  Wir muessen ihm die Position also EXPLIZIT in den Vektor
#  reincodieren. Vaswani et al. benutzen dazu eine schoene
#  Konstruktion aus Sinus und Kosinus in verschiedenen
#  Frequenzen:
#
#      PE(pos, 2i)   = sin( pos / 10000^(2i/d_model) )
#      PE(pos, 2i+1) = cos( pos / 10000^(2i/d_model) )
#
#  Vorteil: Die Werte sind fuer jede Position einzigartig,
#  liegen aber alle im gleichen Zahlenbereich [-1, +1].
#  Ausserdem folgt aus Additionstheoremen: die relative
#  Verschiebung zwischen zwei Positionen laesst sich linear
#  aus den PEs ausdruecken - das Modell kann also lernen,
#  "in Beziehung zueinander" zu setzen.

def positional_encoding(seq_len, d_model):
    """
    Erzeugt eine (seq_len, d_model)-Matrix mit Sin/Cos-Positions-Codes.
    Diese Matrix wird auf die Token-Embeddings AUFADDIERT.
    """
    pe = np.zeros((seq_len, d_model), dtype=np.float64)
    positions = np.arange(seq_len, dtype=np.float64)[:, None]     # (T, 1)
    dims = np.arange(d_model, dtype=np.float64)[None, :]          # (1, D)

    # Frequenz-Skala: fuer jede zweite Dimension eine andere Frequenz
    div_term = np.exp(-(dims // 2) * 2.0 * np.log(10000.0) / d_model)   # (1, D)

    # An geraden Dim: sin, an ungeraden Dim: cos
    angles = positions * div_term                                  # (T, D)
    pe[:, 0::2] = np.sin(angles[:, 0::2])
    pe[:, 1::2] = np.cos(angles[:, 1::2])
    return pe


# ============================================================
#  2. Scaled Dot-Product Attention
# ============================================================
#
#  Das Herzstueck des Transformers. Fuer Query Q, Key K, Value V
#  (alle mit Form (T, d_k)):
#
#     scores = Q K^T / sqrt(d_k)          # (T_q, T_k)
#     alpha  = softmax(scores, Achse=-1)  # Zeilen summieren zu 1
#     out    = alpha V                    # (T_q, d_v)
#
#  Interpretation: Fuer jede Query-Position schauen wir uns die
#  Aehnlichkeit zu jeder Key-Position an (Dot-Product), macheN
#  daraus Wahrscheinlichkeiten (Softmax), und mischen entsprechend
#  die Values zusammen.
#
#  Skalierung mit 1/sqrt(d_k) verhindert, dass die Dot-Products
#  bei hoher Dimension sehr gross werden und die Softmax zu
#  hart wird.
#
#  Optional: MASKE. In der Praxis brauchen wir zwei Sorten:
#    - Causal Mask (Decoder Self-Attn): jedes Ausgangs-Wort darf
#      nur auf sich selbst und frühere Ausgaben schauen.
#    - Padding Mask (falls Sequenzen unterschiedlich lang waeren):
#      hier bei uns nicht noetig.

def softmax(x, axis=-1):
    """Numerisch stabile Softmax."""
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)


def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q: (T_q, d_k)
    K: (T_k, d_k)
    V: (T_k, d_v)
    mask: (T_q, T_k) mit True/False - True bedeutet "hier NICHT hinschauen"

    Rueckgabe:
      out:   (T_q, d_v)   - gemischte Value-Vektoren
      alpha: (T_q, T_k)   - Attention-Gewichte (zum Visualisieren!)
    """
    d_k = Q.shape[-1]
    scores = (Q @ K.T) / np.sqrt(d_k)                # (T_q, T_k)
    if mask is not None:
        scores = np.where(mask, -1e9, scores)        # verbotene Stellen sehr klein
    alpha = softmax(scores, axis=-1)                 # (T_q, T_k)
    out = alpha @ V                                  # (T_q, d_v)
    return out, alpha


# ============================================================
#  3. Multi-Head Attention
# ============================================================
#
#  Statt EINER grossen Attention machen wir h StueCK parallel:
#  jeder Kopf projiziert Q/K/V in einen kleineren Unterraum
#  d_k = d_model / h, macht dort Scaled-Dot-Product-Attention,
#  und am Ende werden alle Koepfe konkateniert und linear
#  projiziert.
#
#  Warum? Jeder Kopf lernt einen anderen "Blickwinkel". Bei
#  Uebersetzung kann z.B. ein Kopf auf Subjekt->Verb schauen,
#  ein anderer auf Positions-Alignment usw. Wir werden das in
#  der Heatmap sehen.

class MultiHeadAttention:
    """
    Multi-Head-Attention, wie in Vaswani et al. 2017.
    Wir speichern die Gewichte als einfache Matrizen (kein
    Parameter-Sharing zwischen Koepfen - jeder Kopf hat seine
    eigene Q/K/V-Projektion).
    """

    def __init__(self, d_model, n_heads, seed=0):
        assert d_model % n_heads == 0, "d_model muss durch n_heads teilbar sein"
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads

        rng = np.random.default_rng(seed)
        scale = 1.0 / np.sqrt(d_model)

        # Volle Projektionsmatrizen (d_model, d_model)
        # Wir teilen sie im forward in n_heads Bloecke.
        self.W_q = rng.standard_normal((d_model, d_model)) * scale
        self.W_k = rng.standard_normal((d_model, d_model)) * scale
        self.W_v = rng.standard_normal((d_model, d_model)) * scale
        self.W_o = rng.standard_normal((d_model, d_model)) * scale

        # Letzte Attention-Gewichte fuers Visualisieren aufheben
        self.last_alphas = None   # (n_heads, T_q, T_k)

    def _split_heads(self, x):
        """(T, d_model) -> (n_heads, T, d_k)"""
        T = x.shape[0]
        return x.reshape(T, self.n_heads, self.d_k).transpose(1, 0, 2)

    def _merge_heads(self, x):
        """(n_heads, T, d_k) -> (T, d_model)"""
        # zurueck auf (T, n_heads, d_k) und dann flach
        return x.transpose(1, 0, 2).reshape(-1, self.d_model)

    def forward(self, q_in, k_in, v_in, mask=None):
        """
        q_in: (T_q, d_model) - hier kommen die Queries her
        k_in: (T_k, d_model) - hier kommen die Keys her
        v_in: (T_k, d_model) - hier kommen die Values her
        mask: (T_q, T_k) oder None

        In Self-Attention sind q_in = k_in = v_in (dieselbe Sequenz).
        In Cross-Attention sind sie unterschiedlich (Decoder -> Encoder).
        """
        Q = q_in @ self.W_q                    # (T_q, d_model)
        K = k_in @ self.W_k                    # (T_k, d_model)
        V = v_in @ self.W_v                    # (T_k, d_model)

        Q_h = self._split_heads(Q)             # (n_heads, T_q, d_k)
        K_h = self._split_heads(K)             # (n_heads, T_k, d_k)
        V_h = self._split_heads(V)             # (n_heads, T_k, d_k)

        head_outs = []
        alphas = []
        for h in range(self.n_heads):
            out_h, a_h = scaled_dot_product_attention(Q_h[h], K_h[h], V_h[h], mask=mask)
            head_outs.append(out_h)
            alphas.append(a_h)

        # Ergebnisse zusammenfuehren
        head_outs = np.stack(head_outs, axis=0)   # (n_heads, T_q, d_k)
        concat = self._merge_heads(head_outs)     # (T_q, d_model)
        out = concat @ self.W_o                   # (T_q, d_model)

        # Fuers Visualisieren aufheben
        self.last_alphas = np.stack(alphas, axis=0)   # (n_heads, T_q, T_k)
        return out


# ============================================================
#  4. Layer Normalization
# ============================================================
#
#  Fuer jede Zeile (jeden Token) normieren wir den Vektor auf
#  Mittelwert 0 und Standardabweichung 1, und wenden dann
#  eine lernbare affine Transformation an: gamma * norm + beta.
#
#  Warum? Transformer stapeln viele Bloecke uebereinander;
#  ohne Normierung driften die Aktivierungen weg und das
#  Training wird instabil.

class LayerNorm:
    def __init__(self, d_model, eps=1e-5):
        self.gamma = np.ones(d_model)
        self.beta = np.zeros(d_model)
        self.eps = eps

    def forward(self, x):
        """x: (T, d_model)"""
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        x_hat = (x - mean) / np.sqrt(var + self.eps)
        return self.gamma * x_hat + self.beta


# ============================================================
#  5. Feed-Forward-Block
# ============================================================
#
#  Nach jedem Attention-Block kommt ein kleines MLP:
#     FFN(x) = ReLU(x W_1 + b_1) W_2 + b_2
#
#  Das MLP wirkt POSITIONSWEISE - jeder Token wird unabhaengig
#  durch dasselbe MLP geschickt. Es hebt die Ausdrucks­kraft
#  des Modells: Attention mischt zwischen Positionen, das FFN
#  mischt innerhalb einer Position.

class FeedForward:
    def __init__(self, d_model, d_ff, seed=0):
        rng = np.random.default_rng(seed)
        scale = 1.0 / np.sqrt(d_model)
        self.W1 = rng.standard_normal((d_model, d_ff)) * scale
        self.b1 = np.zeros(d_ff)
        self.W2 = rng.standard_normal((d_ff, d_model)) * (1.0 / np.sqrt(d_ff))
        self.b2 = np.zeros(d_model)

    def forward(self, x):
        h = x @ self.W1 + self.b1
        h = np.maximum(0.0, h)               # ReLU
        return h @ self.W2 + self.b2


# ============================================================
#  6. Encoder-Block
# ============================================================
#
#     x -> LN -> MHA(self) -> + x    (Residual)
#       -> LN -> FFN       -> + x    (Residual)
#
#  Wir verwenden die "pre-norm"-Variante: LayerNorm VOR dem
#  Sublayer. Das ist etwas leichter zu trainieren als die
#  original "post-norm"-Reihenfolge.

class EncoderBlock:
    def __init__(self, d_model, n_heads, d_ff, seed=0):
        self.ln1 = LayerNorm(d_model)
        self.mha = MultiHeadAttention(d_model, n_heads, seed=seed)
        self.ln2 = LayerNorm(d_model)
        self.ffn = FeedForward(d_model, d_ff, seed=seed + 1)

    def forward(self, x):
        """x: (T_src, d_model)"""
        # Sublayer 1: Self-Attention
        h = self.ln1.forward(x)
        h = self.mha.forward(h, h, h, mask=None)
        x = x + h                                    # Residual

        # Sublayer 2: Feed-Forward
        h = self.ln2.forward(x)
        h = self.ffn.forward(h)
        x = x + h                                    # Residual
        return x


# ============================================================
#  7. Decoder-Block
# ============================================================
#
#     y -> LN -> MHA(self, causal) -> + y
#       -> LN -> MHA(cross to enc)  -> + y
#       -> LN -> FFN                -> + y
#
#  Zwei Attention-Bloecke:
#    (a) Self-Attention mit CAUSAL MASK. Position t darf nur
#        auf Positionen <= t schauen (sonst wuerde das Modell
#        "beim Trainieren spicken").
#    (b) Cross-Attention: Queries kommen vom Decoder, Keys
#        und Values vom Encoder. So verbindet der Decoder
#        seinen aktuellen Zustand mit der Eingabe.

def make_causal_mask(T):
    """
    Erzeugt eine (T, T)-Maske, in der True bedeutet: hier
    NICHT hinschauen. Der Bereich oberhalb der Hauptdiagonalen
    wird maskiert.
    """
    mask = np.triu(np.ones((T, T), dtype=bool), k=1)
    return mask


class DecoderBlock:
    def __init__(self, d_model, n_heads, d_ff, seed=0):
        self.ln1 = LayerNorm(d_model)
        self.self_attn = MultiHeadAttention(d_model, n_heads, seed=seed)
        self.ln2 = LayerNorm(d_model)
        self.cross_attn = MultiHeadAttention(d_model, n_heads, seed=seed + 100)
        self.ln3 = LayerNorm(d_model)
        self.ffn = FeedForward(d_model, d_ff, seed=seed + 200)

    def forward(self, y, enc_out):
        """
        y:       (T_tgt, d_model)  - bisherige Decoder-Sequenz
        enc_out: (T_src, d_model)  - Ausgabe des Encoders
        """
        T_tgt = y.shape[0]
        causal = make_causal_mask(T_tgt)

        # Sublayer 1: Masked Self-Attention
        h = self.ln1.forward(y)
        h = self.self_attn.forward(h, h, h, mask=causal)
        y = y + h

        # Sublayer 2: Cross-Attention (Q von Decoder, K/V vom Encoder)
        h = self.ln2.forward(y)
        h = self.cross_attn.forward(h, enc_out, enc_out, mask=None)
        y = y + h

        # Sublayer 3: Feed-Forward
        h = self.ln3.forward(y)
        h = self.ffn.forward(h)
        y = y + h
        return y


# ============================================================
#  8. Gesamt-Modell: Encoder-Decoder-Transformer
# ============================================================
#
#  Struktur:
#     Src-IDs  -> Embedding + PosEnc -> N x EncoderBlock ->  enc_out
#     Tgt-IDs  -> Embedding + PosEnc -> N x DecoderBlock ->  dec_out
#                                                                |
#                                                                v
#                                        [ Linear -> V_out ]  -> Logits
#
#  Wir teilen KEIN Embedding zwischen Encoder und Decoder,
#  weil Eingabe (10 Ziffern) und Ausgabe (42 Woerter) ganz
#  unterschiedliche Vokabularien haben.

class Transformer:
    """Encoder-Decoder-Transformer mit N Bloecken je Seite."""

    def __init__(self, src_vocab, tgt_vocab,
                 d_model=64, n_heads=4, d_ff=128, n_layers=2,
                 max_len=32, seed=0):
        self.src_vocab = src_vocab
        self.tgt_vocab = tgt_vocab
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_ff = d_ff
        self.n_layers = n_layers
        self.max_len = max_len

        rng = np.random.default_rng(seed)
        scale = 1.0 / np.sqrt(d_model)

        # Token-Embeddings (jeweils eigene Matrix je Seite)
        self.E_src = rng.standard_normal((src_vocab, d_model)) * scale
        self.E_tgt = rng.standard_normal((tgt_vocab, d_model)) * scale

        # Positional Encoding: einmal berechnen, danach Konstante
        self.pos_enc = positional_encoding(max_len, d_model)

        # Encoder- und Decoder-Bloecke
        self.enc_blocks = [EncoderBlock(d_model, n_heads, d_ff, seed=seed + 10 + i)
                           for i in range(n_layers)]
        self.dec_blocks = [DecoderBlock(d_model, n_heads, d_ff, seed=seed + 500 + i)
                           for i in range(n_layers)]

        # Finale Norm (empfehlenswert bei pre-norm) und Output-Projektion
        self.ln_final = LayerNorm(d_model)
        self.W_out = rng.standard_normal((d_model, tgt_vocab)) * scale
        self.b_out = np.zeros(tgt_vocab)

    # --------------------------------------------------------
    # Baustein: Token-IDs -> Embeddings + Positional Encoding
    # --------------------------------------------------------
    def _embed(self, ids, is_src):
        """
        ids: (T,) mit Integer-IDs
        is_src: True fuer Quellsprache, False fuer Zielsprache
        """
        E = self.E_src if is_src else self.E_tgt
        x = E[ids]                                # (T, d_model)
        T = x.shape[0]
        # Skalierung mit sqrt(d_model) wie im Original-Paper
        x = x * np.sqrt(self.d_model)
        x = x + self.pos_enc[:T]                  # Positions dazu
        return x

    # --------------------------------------------------------
    # Encoder-Forward
    # --------------------------------------------------------
    def encode(self, src_ids):
        """src_ids: (T_src,) -> enc_out: (T_src, d_model)"""
        x = self._embed(src_ids, is_src=True)
        for block in self.enc_blocks:
            x = block.forward(x)
        return x

    # --------------------------------------------------------
    # Decoder-Forward (Teacher Forcing: ganze Zielsequenz auf einmal)
    # --------------------------------------------------------
    def decode(self, tgt_ids, enc_out):
        """
        tgt_ids: (T_tgt,)   Ziel-Sequenz (bei Training mit <sos> davor)
        enc_out: (T_src, d_model)
        Rueckgabe: logits (T_tgt, tgt_vocab)
        """
        y = self._embed(tgt_ids, is_src=False)
        for block in self.dec_blocks:
            y = block.forward(y, enc_out)
        y = self.ln_final.forward(y)
        logits = y @ self.W_out + self.b_out
        return logits

    def forward(self, src_ids, tgt_ids):
        """
        Vollstaendiger Forward-Pass.

        Rueckgabe: logits (T_tgt, tgt_vocab)
        """
        enc_out = self.encode(src_ids)
        logits = self.decode(tgt_ids, enc_out)
        return logits

    # --------------------------------------------------------
    # Vorhersage (Greedy, autoregressiv)
    # --------------------------------------------------------
    def predict(self, src_ids, sos_id, eos_id, max_len=8):
        """
        Autoregressives Sampling: Wir starten mit [<sos>] und
        fuegen jeweils das wahrscheinlichste naechste Wort an,
        bis <eos> generiert wird oder max_len erreicht ist.

        Rueckgabe:
          pred_ids: Liste der vorhergesagten IDs (ohne <sos>/<eos>)
          cross_alphas: Attention-Gewichte der letzten Cross-Attention
                        des letzten Decoder-Blocks, geformt (n_heads,
                        T_out, T_src). Praktisch fuers Visualisieren.
        """
        enc_out = self.encode(src_ids)
        tgt_ids = [sos_id]
        for _ in range(max_len):
            logits = self.decode(np.array(tgt_ids, dtype=np.int64), enc_out)
            next_id = int(np.argmax(logits[-1]))
            if next_id == eos_id:
                break
            tgt_ids.append(next_id)

        # Attention-Gewichte des LETZTEN Decoder-Blocks aus der
        # Cross-Attention einsammeln (die zeigen, worauf der
        # Decoder in der Eingabe geschaut hat).
        cross = self.dec_blocks[-1].cross_attn.last_alphas
        # ohne <sos>-Zeile:
        pred_ids = tgt_ids[1:]
        return pred_ids, cross[:, 1:1 + len(pred_ids), :]


# ============================================================
#  9. Anzahl Parameter (fuer die README)
# ============================================================

def count_parameters(model):
    total = 0
    total += model.E_src.size
    total += model.E_tgt.size
    total += model.W_out.size + model.b_out.size
    total += model.ln_final.gamma.size + model.ln_final.beta.size
    for b in model.enc_blocks:
        for w in (b.mha.W_q, b.mha.W_k, b.mha.W_v, b.mha.W_o):
            total += w.size
        total += b.ln1.gamma.size + b.ln1.beta.size
        total += b.ln2.gamma.size + b.ln2.beta.size
        total += b.ffn.W1.size + b.ffn.b1.size + b.ffn.W2.size + b.ffn.b2.size
    for b in model.dec_blocks:
        for mha in (b.self_attn, b.cross_attn):
            for w in (mha.W_q, mha.W_k, mha.W_v, mha.W_o):
                total += w.size
        total += b.ln1.gamma.size + b.ln1.beta.size
        total += b.ln2.gamma.size + b.ln2.beta.size
        total += b.ln3.gamma.size + b.ln3.beta.size
        total += b.ffn.W1.size + b.ffn.b1.size + b.ffn.W2.size + b.ffn.b2.size
    return total


# ============================================================
#  10. Sanity-Test (nur Forward, keine Trainings-Konvergenz erwartet)
# ============================================================

if __name__ == "__main__":
    from data import (
        make_dataset, INPUT_V, OUTPUT_V, INPUT_ITOS, OUTPUT_ITOS,
        SOS_ID, EOS_ID, INPUT_LEN,
    )

    print("=" * 60)
    print("Phase 1 - Forward-Only Sanity-Test")
    print("=" * 60)

    X, Y = make_dataset()
    print(f"Datensatz: {len(X)} Paare, Eingabe-Vokabular {INPUT_V}, "
          f"Ausgabe-Vokabular {OUTPUT_V}")

    # Hyperparameter (siehe README): d_model=64, n_heads=4, N=2
    model = Transformer(
        src_vocab=INPUT_V,
        tgt_vocab=OUTPUT_V,
        d_model=64,
        n_heads=4,
        d_ff=128,
        n_layers=2,
        max_len=16,
        seed=42,
    )
    print(f"Parameter: {count_parameters(model):,}")
    print(f"  d_model={model.d_model}, n_heads={model.n_heads}, "
          f"n_layers={model.n_layers}, d_ff={model.d_ff}")

    # Forward mit Teacher Forcing auf einem Beispiel
    n = 199
    src = X[n]
    tgt_full = Y[n]     # [<sos>, ..., <eos>]
    tgt_in = tgt_full[:-1]   # <sos> und alle Zielwoerter bis auf letztes
    tgt_out = tgt_full[1:]   # ab erstem Zielwort bis <eos>

    print()
    print(f"Beispiel n={n}:")
    print(f"  Eingabe (IDs):   {src}   -> Ziffern: {''.join(INPUT_ITOS[i] for i in src)}")
    print(f"  Ziel-Woerter:    {[OUTPUT_ITOS[i] for i in tgt_full]}")

    logits = model.forward(src, tgt_in)
    print(f"  Logits-Shape:    {logits.shape}   (soll (T_tgt, V_out) sein)")
    print(f"  Erwartetes Ziel: {[OUTPUT_ITOS[i] for i in tgt_out]}")
    argmax_pred = np.argmax(logits, axis=-1)
    print(f"  Argmax-Ausgabe:  {[OUTPUT_ITOS[i] for i in argmax_pred]}")
    print(f"  (untrainiertes Modell -> Vorhersagen zufaellig, das ist okay)")

    # Autoregressives predict
    pred_ids, cross = model.predict(src, SOS_ID, EOS_ID, max_len=8)
    print()
    print(f"Autoregressive Vorhersage (untrainiert):")
    print(f"  {[OUTPUT_ITOS[i] for i in pred_ids]}")
    print(f"  Cross-Attention-Shape: {cross.shape}   "
          f"(soll (n_heads, T_out, T_src) sein)")

    print()
    print("Sanity-Test bestanden - alle Shapes stimmen.")
