# ============================================================
#  Hauptexperiment fuer Meilenstein 4 (Word2Vec):
#  Skip-Gram + Negative Sampling auf Grimms Maerchen
#
#  Ablauf:
#    1) Korpus laden und tokenisieren
#    2) Vokabular aufbauen (haeufige Woerter)
#    3) Skip-Gram + NS trainieren (~1-3 Minuten auf CPU)
#    4) Semantische Erkundung:
#         - Nachbarwoerter zu ausgewaehlten Beispielen
#         - Analogien (koenig - mann + frau ~= koenigin)
#         - 2D-PCA-Visualisierung ausgewaehlter Woerter
# ============================================================

import numpy as np

from corpus import load_grimm
from preprocessing import tokenize, build_vocab
from word2vec import SkipGramNS


# ------------------------------------------------------------
# Hyperparameter
# ------------------------------------------------------------
EMBED_DIM = 64
WINDOW = 5
NEG_SAMPLES = 5
EPOCHS = 4
BATCH_SIZE = 1024
LR_START = 0.025
LR_END = 0.001
MIN_COUNT = 5
SEED = 42


# ============================================================
#  Semantische Werkzeuge
# ============================================================

def normalize(mat):
    """Zeilenweise L2-Normalisierung (fuer Kosinusaehnlichkeit)."""
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    return mat / np.clip(norms, 1e-9, None)


def nearest_words(model, word2id, id2word, target_word, topn=8):
    """Findet die topn semantisch aehnlichsten Woerter zu target_word."""
    if target_word not in word2id:
        print(f"  Wort '{target_word}' nicht im Vokabular.")
        return
    W = normalize(model.W_in)
    idx = word2id[target_word]
    sims = W @ W[idx]
    sims[idx] = -1.0
    top = np.argsort(-sims)[:topn]
    print(f"  {target_word:>12s} -> {[id2word[i] for i in top]}")


def analogy(model, word2id, id2word, a, b, c, topn=5):
    """
    Loest die Analogie 'a ist zu b wie c ist zu ?'.
    Beispiel: king - man + woman = queen  ->  analogy('man', 'king', 'woman').
    """
    for w in (a, b, c):
        if w not in word2id:
            print(f"  '{w}' nicht im Vokabular.")
            return
    W = normalize(model.W_in)
    va, vb, vc = W[word2id[a]], W[word2id[b]], W[word2id[c]]
    query = vb - va + vc
    query /= max(np.linalg.norm(query), 1e-9)
    sims = W @ query
    for w in (a, b, c):
        sims[word2id[w]] = -1.0
    top = np.argsort(-sims)[:topn]
    print(f"  {a} : {b} :: {c} : ?   ->   {[id2word[i] for i in top]}")


# ============================================================
#  2D-Visualisierung per PCA (ASCII)
# ============================================================

def pca_2d(mat):
    """Einfache PCA: Mittelwert abziehen, dann SVD, zwei staerkste Achsen."""
    X = mat - mat.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    return X @ Vt[:2].T


def draw_ascii_scatter(coords_2d, labels, width=80, height=22):
    """Zeichnet eine 2D-Punktwolke als ASCII-Bild in die Konsole."""
    xs, ys = coords_2d[:, 0], coords_2d[:, 1]
    x_min, x_max = xs.min(), xs.max()
    y_min, y_max = ys.min(), ys.max()

    def to_col(x):
        return int((x - x_min) / (x_max - x_min + 1e-9) * (width - 1))

    def to_row(y):
        return int((y_max - y) / (y_max - y_min + 1e-9) * (height - 1))

    grid = [[" "] * width for _ in range(height)]
    label_at = {}
    for (x, y), lab in zip(coords_2d, labels):
        r, c = to_row(y), to_col(x)
        if grid[r][c] == " ":
            grid[r][c] = "o"
            label_at[(r, c)] = lab
        else:
            grid[r][c] = "*"

    print()
    print("2D-PCA-Projektion der wichtigsten Woerter (ASCII):")
    print("+" + "-" * width + "+")
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "-" * width + "+")
    print()
    print("Legende (Zeile,Spalte -> Wort):")
    items = sorted(label_at.items())
    per_row = 3
    for i in range(0, len(items), per_row):
        chunk = items[i:i + per_row]
        print("  " + "   ".join(f"({r:2d},{c:2d}) {lab:<12s}" for (r, c), lab in chunk))


# ============================================================
#  Hauptprogramm
# ============================================================

def main():
    text = load_grimm()
    tokens = tokenize(text)
    word2id, id2word, counts, token_ids = build_vocab(tokens, min_count=MIN_COUNT)
    print()
    print(f"Tokens gesamt: {len(tokens):,}   "
          f"Vokabular: {len(id2word):,}   "
          f"Trainings-IDs: {len(token_ids):,}")

    model = SkipGramNS(vocab_size=len(id2word), embed_dim=EMBED_DIM, seed=SEED)
    model.train(
        token_ids, counts,
        epochs=EPOCHS, window=WINDOW, k=NEG_SAMPLES,
        batch_size=BATCH_SIZE,
        lr_start=LR_START, lr_end=LR_END,
        seed=SEED,
    )

    print()
    print("Nachbarwoerter (nach Kosinusaehnlichkeit):")
    for w in [
        "king", "queen", "wolf", "forest", "father", "mother",
        "prince", "gold", "castle", "night", "fish", "witch",
    ]:
        nearest_words(model, word2id, id2word, w, topn=8)

    print()
    print("Analogien  a : b :: c : ?")
    analogy(model, word2id, id2word, "man", "king", "woman")
    analogy(model, word2id, id2word, "boy", "prince", "girl")
    analogy(model, word2id, id2word, "father", "son", "mother")
    analogy(model, word2id, id2word, "day", "sun", "night")

    # 2D-PCA-Plot fuer eine kuratierte Wortliste
    candidates = [
        # koenigliche Familie
        "king", "queen", "prince", "princess", "father", "mother",
        "son", "daughter", "man", "woman", "boy", "girl",
        # Natur / Tiere
        "wolf", "fox", "bird", "fish", "cat", "dog", "horse",
        "forest", "tree", "wood", "stone", "river", "sea",
        # Orte / Objekte
        "castle", "house", "door", "window", "gold", "silver",
        # Grimm-typische Figuren
        "witch", "dwarf", "giant", "hunter", "shepherd",
        # Zeit / Adjektive
        "night", "day", "morning", "beautiful", "poor",
    ]
    picks = []
    seen = set()
    for w in candidates:
        if w in word2id and w not in seen:
            picks.append(w)
            seen.add(w)

    if len(picks) >= 6:
        W_norm = normalize(model.W_in)
        vectors = np.stack([W_norm[word2id[w]] for w in picks])
        coords = pca_2d(vectors)
        draw_ascii_scatter(coords, picks)
    else:
        print("Zu wenige der Referenzwoerter im Vokabular fuer den PCA-Plot.")

    # ---- Embeddings + Vokabular fuer nachfolgende Meilensteine speichern ----
    import os
    out_dir = os.path.dirname(os.path.abspath(__file__))
    np.savez(
        os.path.join(out_dir, "embeddings.npz"),
        W_in=model.W_in,
        id2word=np.array(id2word, dtype=object),
    )
    print(f"\n[Save] Embeddings + Vokabular -> {os.path.join(out_dir, 'embeddings.npz')}")


if __name__ == "__main__":
    main()
