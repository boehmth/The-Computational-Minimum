# ============================================================
#  ASCII-Attention-Heatmap fuer Multi-Head-Attention
#
#  Beim Seq2Seq (Meilenstein 6) hatten wir EINEN Attention-
#  Vektor pro Zeitschritt. Beim Transformer hat der Decoder in
#  jeder Cross-Attention n_heads davon - parallel. Wir zeichnen
#  fuer jeden Kopf eine eigene Heatmap, nebeneinander.
# ============================================================


def _cell(a):
    """Uebersetzt ein Attention-Gewicht (0..1) in ein ASCII-Symbol."""
    if a < 0.05:
        return " . "
    if a < 0.15:
        return " * "
    if a < 0.35:
        return " o "
    if a < 0.60:
        return " O "
    return " # "


def _render_single_head(input_digits, output_tokens, attn_matrix):
    """
    Baut die Zeilen einer einzelnen Kopf-Heatmap als Liste von Strings.
    Alle Zeilen haben dieselbe Breite.
    """
    header = " | " + "  ".join(f"{d:^3s}" for d in input_digits) + " |"
    sep = " +" + "-" * (len(input_digits) * 5) + "+"

    label_w = max(len(tok) for tok in output_tokens)
    lines = []
    # Kopfzeile: Label-Spalte leer, dann Ziffern
    lines.append(" " * (label_w + 1) + header)
    lines.append(" " * (label_w + 1) + sep)
    for t, tok in enumerate(output_tokens):
        row = "  ".join(_cell(a) for a in attn_matrix[t])
        lines.append(f"{tok:>{label_w}s} | {row} |")
    lines.append(" " * (label_w + 1) + sep)
    return lines


def render_multi_head_attention(input_digits, output_tokens, attn_matrix,
                                 number=None):
    """
    Zeigt alle Koepfe der Cross-Attention nebeneinander.

    input_digits:   Liste der Eingangs-Ziffern, z.B. ['1', '9', '9']
    output_tokens:  Liste der Ausgabe-Woerter, z.B. ['einhundert', ...]
    attn_matrix:    (n_heads, T_out, T_in) - Attention-Gewichte pro Kopf
    """
    n_heads = attn_matrix.shape[0]
    # min(len(output_tokens), T_out) — die letzte Zeile ist evtl. <eos>-Vorhersage
    T_out = min(len(output_tokens), attn_matrix.shape[1])

    if number is not None:
        print()
        print(f"  Eingabe: {number}  ({''.join(input_digits)})")

    # Fuer jeden Kopf eigene Heatmap-Zeilen bauen
    head_blocks = []
    for h in range(n_heads):
        block = _render_single_head(input_digits,
                                     output_tokens[:T_out],
                                     attn_matrix[h, :T_out])
        head_blocks.append(block)

    # Ueberschrift ueber jeder Heatmap
    max_width = max(max(len(l) for l in block) for block in head_blocks)
    print()
    header_line = "   ".join(
        f"Kopf {h}".center(max_width) for h in range(n_heads)
    )
    print("  " + header_line)

    # Zeilenweise nebeneinander drucken
    max_lines = max(len(block) for block in head_blocks)
    for i in range(max_lines):
        parts = []
        for block in head_blocks:
            line = block[i] if i < len(block) else ""
            parts.append(line.ljust(max_width))
        print("  " + "   ".join(parts))

    print("  Legende:  .  =  0.00..0.05   *  =  ..0.15   o  =  ..0.35   "
          "O  =  ..0.60   #  =  ..1.00")


def render_single_head_attention(input_digits, output_tokens, attn_matrix,
                                 number=None):
    """
    Fuer den direkten Vergleich mit Seq2Seq: EINE Heatmap, wie in
    Meilenstein 6. Bekommt eine (T_out, T_in)-Matrix.
    """
    if number is not None:
        print()
        print(f"  Eingabe: {number}  ({''.join(input_digits)})")

    header = "  " + " " * 12 + " | " + "  ".join(f"{d:^3s}" for d in input_digits) + " |"
    sep = "  " + " " * 12 + " +" + "-" * (len(input_digits) * 5) + "+"

    print()
    print(header)
    print(sep)
    T_out = min(len(output_tokens), attn_matrix.shape[0])
    for t, tok in enumerate(output_tokens[:T_out]):
        row = "  ".join(_cell(a) for a in attn_matrix[t])
        print(f"  {tok:>12s} | {row} |")
    print(sep)
    print("  Legende:  .  =  0.00..0.05   *  =  ..0.15   o  =  ..0.35   "
          "O  =  ..0.60   #  =  ..1.00")


# ------------------------------------------------------------
# Sanity-Test
# ------------------------------------------------------------
if __name__ == "__main__":
    import numpy as np

    # Zufaellige Attention-Matrix mit 4 Koepfen, 4 Ausgangs-Woertern, 3 Ziffern
    rng = np.random.default_rng(0)
    fake = rng.uniform(size=(4, 4, 3))
    fake = fake / fake.sum(axis=-1, keepdims=True)   # normieren

    render_multi_head_attention(
        input_digits=["1", "9", "9"],
        output_tokens=["einhundert", "neun", "und", "neunzig"],
        attn_matrix=fake,
        number=199,
    )