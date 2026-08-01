# ============================================================
#  Zahlenwoerter 0-999 - deutsche Ausgabe
#
#  Beispiel:
#     23  ->  ['drei', 'und', 'zwanzig']
#     107 ->  ['einhundert', 'sieben']
#     999 ->  ['neunhundert', 'neun', 'und', 'neunzig']
#
#  Die Eingabe ist eine Zifferfolge fester Laenge (3), links
#  mit '0' aufgefuellt: 23 -> "023", 5 -> "005".
#  So bleibt die Eingabelaenge konstant und die Attention-
#  Heatmap wird gut lesbar.
# ============================================================

import numpy as np

# Feste Eingabelaenge (Anzahl Ziffern)
INPUT_LEN = 3

# ---------- Eingabe-Vokabular: die 10 Ziffern ----------
INPUT_TOKENS = list("0123456789")
INPUT_STOI = {c: i for i, c in enumerate(INPUT_TOKENS)}
INPUT_ITOS = INPUT_TOKENS
INPUT_V = len(INPUT_TOKENS)


# ---------- Ausgabe-Vokabular: deutsche Zahlwortbausteine ----------
# Wir wollen es einfach halten, deshalb behandeln wir Zahlwoerter als
# eine Folge weniger Bausteine. Das entspricht in etwa der Art, wie ein
# Mensch die Zahl liest: "einhundert - drei - und - zwanzig".

_EINER = {
    0: "null", 1: "eins", 2: "zwei", 3: "drei", 4: "vier",
    5: "fuenf", 6: "sechs", 7: "sieben", 8: "acht", 9: "neun",
}
# Nach "und" und in Zusammensetzungen wird aus "eins" -> "ein"
_EINER_KOMB = dict(_EINER)
_EINER_KOMB[1] = "ein"

_TEENS = {
    10: "zehn", 11: "elf", 12: "zwoelf", 13: "dreizehn", 14: "vierzehn",
    15: "fuenfzehn", 16: "sechzehn", 17: "siebzehn", 18: "achtzehn", 19: "neunzehn",
}

_ZEHNER = {
    2: "zwanzig", 3: "dreissig", 4: "vierzig",
    5: "fuenfzig", 6: "sechzig", 7: "siebzig", 8: "achtzig", 9: "neunzig",
}


def number_to_words(n):
    """Wandelt eine ganze Zahl 0..999 in eine Liste deutscher Zahlworte um."""
    if n == 0:
        return ["null"]

    tokens = []

    # ---- Hunderter ----
    h = n // 100
    if h > 0:
        tokens.append(f"{_EINER_KOMB[h]}hundert")

    rest = n % 100

    # ---- 10..19 als eigene Woerter ----
    if 10 <= rest <= 19:
        tokens.append(_TEENS[rest])
        return tokens

    e = rest % 10
    z = rest // 10

    # ---- Einer + "und" + Zehner (klassisches Deutsch) ----
    if z >= 2 and e >= 1:
        # z.B. 21 -> "einundzwanzig"; hier steht "ein" (kombinierbar)
        tokens.append(_EINER_KOMB[e])
        tokens.append("und")
        tokens.append(_ZEHNER[z])
    elif z >= 2 and e == 0:
        tokens.append(_ZEHNER[z])
    elif z == 0 and e >= 1:
        # Einzelziffer 1-9 hinter (evtl.) Hunderter.
        # Bei alleinstehender 1 (z. B. 1 oder 101) sagt man "eins"
        # (nicht "ein"), im Gegensatz zu Zusammensetzungen wie
        # "einundzwanzig". Wir nehmen daher die reine Einer-Form.
        tokens.append(_EINER[e])

    return tokens


# ---------- Ausgabe-Vokabular sammeln ----------

_SPECIAL_TOKENS = ["<pad>", "<sos>", "<eos>"]


def build_output_vocab():
    """Sammelt alle Ausgabe-Tokens, die 0..999 vorkommen koennen."""
    seen = set()
    for n in range(1000):
        for tok in number_to_words(n):
            seen.add(tok)
    tokens = _SPECIAL_TOKENS + sorted(seen)
    stoi = {t: i for i, t in enumerate(tokens)}
    return tokens, stoi


OUTPUT_ITOS, OUTPUT_STOI = build_output_vocab()
OUTPUT_V = len(OUTPUT_ITOS)

PAD_ID = OUTPUT_STOI["<pad>"]
SOS_ID = OUTPUT_STOI["<sos>"]
EOS_ID = OUTPUT_STOI["<eos>"]


# ---------- Trainingsdaten erzeugen ----------

def encode_input(n):
    """Wandelt eine Zahl in einen (INPUT_LEN,)-Vektor von Ziffer-IDs um."""
    s = str(n).zfill(INPUT_LEN)
    return np.array([INPUT_STOI[c] for c in s], dtype=np.int64)


def encode_output(n):
    """Wandelt eine Zahl in eine Sequenz [<sos>, w1, w2, ..., <eos>]."""
    words = number_to_words(n)
    ids = [SOS_ID] + [OUTPUT_STOI[w] for w in words] + [EOS_ID]
    return np.array(ids, dtype=np.int64)


def make_dataset():
    """Erzeugt alle 1000 (input, output)-Paare fuer die Zahlen 0..999."""
    X = np.stack([encode_input(n) for n in range(1000)])
    Y = [encode_output(n) for n in range(1000)]     # unterschiedliche Laengen
    return X, Y


def train_test_split(X, Y, test_ratio=0.2, seed=42):
    """Splittet den 1000-Datensatz reproduzierbar in Training/Test."""
    rng = np.random.default_rng(seed)
    n = len(X)
    idx = np.arange(n)
    rng.shuffle(idx)
    n_test = int(n * test_ratio)
    test_idx = idx[:n_test]
    train_idx = idx[n_test:]
    return ([X[i] for i in train_idx], [Y[i] for i in train_idx],
            [X[i] for i in test_idx], [Y[i] for i in test_idx],
            train_idx, test_idx)


if __name__ == "__main__":
    print(f"Eingabe-Vokabular:  {INPUT_V} Zeichen: {INPUT_TOKENS}")
    print(f"Ausgabe-Vokabular:  {OUTPUT_V} Woerter")
    print(f"Special-Tokens:     {_SPECIAL_TOKENS}")
    print()
    for n in [0, 1, 7, 17, 23, 42, 100, 101, 199, 342, 999]:
        words = number_to_words(n)
        print(f"  {n:3d} -> {' '.join(words)}")

    X, Y = make_dataset()
    print(f"\n1000 Paare erzeugt. Beispiel:")
    print(f"  X[23] = {X[23]}  (Zifferfolge)")
    print(f"  Y[23] = {Y[23]}  = {[OUTPUT_ITOS[i] for i in Y[23]]}")