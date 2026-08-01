# ============================================================
#  Tokenisierung und Vokabelbildung
#
#  Aus dem rohen Maerchentext machen wir eine Liste von
#  Kleinbuchstaben-Woertern (Tokens). Alles, was keine
#  Buchstaben sind, wird als Trenner behandelt.
# ============================================================

import re
from collections import Counter

# Wir erlauben ASCII-Buchstaben plus die typografischen Apostrophe
# (die im Gutenberg-Text vorkommen: don't, it's, ...).
_TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?", re.IGNORECASE)


def tokenize(text):
    """Zerlegt den Text in eine Liste von Kleinbuchstaben-Woertern."""
    text = text.replace("\u2019", "'")   # typografisches durch normales Apostroph ersetzen
    return _TOKEN_RE.findall(text.lower())


def build_vocab(tokens, min_count=5, max_vocab=None):
    """
    Baut das Vokabular aus einer Tokenliste auf.

    Woerter, die seltener als `min_count`-mal vorkommen, fliegen raus.
    `max_vocab` begrenzt zusaetzlich die Groesse (die haeufigsten werden behalten).

    Rueckgabe:
        word2id:   dict, Wort -> Index (0 .. V-1)
        id2word:   list, Index -> Wort
        counts:    list, Haeufigkeit pro Index
        token_ids: list, Alle Trainings-Tokens, unbekannte Woerter entfernt
    """
    counter = Counter(tokens)
    # Nach Haeufigkeit sortieren, dann alphabetisch als Tie-Breaker
    items = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    items = [(w, c) for w, c in items if c >= min_count]
    if max_vocab is not None:
        items = items[:max_vocab]

    id2word = [w for w, _ in items]
    counts = [c for _, c in items]
    word2id = {w: i for i, w in enumerate(id2word)}

    # Nur bekannte Woerter in die Trainings-Tokens
    token_ids = [word2id[t] for t in tokens if t in word2id]

    return word2id, id2word, counts, token_ids


if __name__ == "__main__":
    from corpus import load_grimm

    text = load_grimm()
    tokens = tokenize(text)
    print(f"Tokens gesamt: {len(tokens):,}")
    print(f"Erste 20 Tokens: {tokens[:20]}")

    word2id, id2word, counts, token_ids = build_vocab(tokens, min_count=5)
    print(f"Vokabular:      {len(id2word):,} Woerter (min_count=5)")
    print(f"Trainings-IDs:  {len(token_ids):,}")
    print("\nHaeufigste 20 Woerter:")
    for w, c in zip(id2word[:20], counts[:20]):
        print(f"  {w:15s} {c}")