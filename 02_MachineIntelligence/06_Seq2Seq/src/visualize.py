# ============================================================
#  ASCII-Attention-Heatmap
#
#  Der Star dieses Kapitels: eine Konsolen-Visualisierung
#  der Attention-Gewichte. Fuer jede Zahl-Uebersetzung
#  sehen wir eine kleine Matrix mit Werten von 0 bis 1,
#  die zeigt: "beim Erzeugen von 'drei' hat das Netz
#  hauptsaechlich auf die Ziffer '3' geschaut."
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


def render_attention(input_digits, output_tokens, attn_matrix, number=None):
    """
    input_digits:  z.B. ['0', '2', '3']
    output_tokens: z.B. ['drei', 'und', 'zwanzig']
    attn_matrix:   (T_out, T_in) - Zeile t enthaelt die Attention beim
                                    Erzeugen von output_tokens[t].
    """
    header = "  " + " " * 12 + " | " + "  ".join(f"{d:^3s}" for d in input_digits) + " |"
    # Breite des Innenraums = 5*n - 2 (n Zellen a 3 Zeichen, mit 2 Leerzeichen dazwischen)
    # plus 2 Rand-Leerzeichen links/rechts = 5*n
    sep    = "  " + " " * 12 + " +" + "-" * (len(input_digits) * 5) + "+"

    print()
    if number is not None:
        print(f"  Eingabe: {number}  ({''.join(input_digits)})")
    print(header)
    print(sep)
    for t, tok in enumerate(output_tokens):
        row = "  ".join(_cell(a) for a in attn_matrix[t])
        print(f"  {tok:>12s} | {row} |")
    print(sep)
    print("  Legende:  .  =  0.00..0.05   *  =  ..0.15   o  =  ..0.35   O  =  ..0.60   #  =  ..1.00")