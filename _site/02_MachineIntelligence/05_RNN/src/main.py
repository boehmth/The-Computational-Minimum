# ============================================================
#  Hauptexperiment fuer Meilenstein 5 (RNN):
#  Word-Level RNN auf Grimms Maerchen - baut direkt auf den
#  Wort-Embeddings aus Meilenstein 4 (Word2Vec) auf.
#
#  Idee:
#    1) Wir laden die Word2Vec-Embeddings aus Meilenstein 4.
#    2) Das RNN bekommt als Eingabe fuer Zeit t den Embedding-
#       Vektor des Wortes an Position t.
#    3) Es soll die Wahrscheinlichkeits­verteilung ueber das
#       naechste Wort ausgeben.
#    4) Wir samplen Grimm-artige Saetze wortweise.
#
#  Damit erben wir die Semantik aus Word2Vec und trainieren
#  nur noch die Sequenz-Struktur - genau der Aufbau, den viele
#  von uns 2015-2017 fuer NLP-Aufgaben benutzt haben, mit
#  GloVe- oder Word2Vec-Embeddings als "warm start".
#
#  (Wer stattdessen ein Character-Level-RNN sehen moechte:
#  Andrej Karpathys legendaerer Blog-Post "The Unreasonable
#  Effectiveness of Recurrent Neural Networks" von 2015 zeigt
#  genau das - Zeichen-fuer-Zeichen-Generation mit vielen
#  eindrucksvollen Beispielen. Fuer den Fluss der Reihe hier
#  bleiben wir aber auf Wortebene.)
# ============================================================

import os
import time

import numpy as np

from corpus import load_grimm
# preprocessing.py stammt aus dem Word2Vec-Kapitel; wir laden es via sys.path.
import sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_W2V_SRC = os.path.abspath(os.path.join(_HERE, "..", "..", "Word2Vec", "src"))
if _W2V_SRC not in sys.path:
    sys.path.insert(0, _W2V_SRC)
from preprocessing import tokenize   # noqa: E402
from rnn import WordRNN


# ------------------------------------------------------------
# Hyperparameter
# ------------------------------------------------------------
HIDDEN_SIZE = 128
SEQ_LEN = 20         # BPTT-Fensterlaenge (in Woertern!)
LR = 0.1
NUM_STEPS = 3000     # ein Trainingsschritt = SEQ_LEN Woerter
SAMPLE_EVERY = 500
SAMPLE_LEN = 50      # generierte Anzahl Woerter
SEED = 42


# ============================================================

def _load_embeddings():
    """Laedt Word2Vec-Embeddings + Vokabular aus Meilenstein 4."""
    path = os.path.join(_W2V_SRC, "embeddings.npz")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Embeddings nicht gefunden: {path}\n"
            "Bitte zuerst Meilenstein 4 (Word2Vec) laufen lassen:\n"
            "  cd ../../Word2Vec/src && python main.py"
        )
    npz = np.load(path, allow_pickle=True)
    W = npz["W_in"].astype(np.float32)   # (V, D)
    id2word = list(npz["id2word"])
    word2id = {w: i for i, w in enumerate(id2word)}
    return W, word2id, id2word


def _tokens_to_ids(text, word2id):
    """Tokenisiert Text (englisch) und liefert nur die IDs bekannter Woerter."""
    tokens = tokenize(text)
    ids = [word2id[t] for t in tokens if t in word2id]
    return np.array(ids, dtype=np.int64)


def _sample_from_prompt(model, prompt, embed_lookup, word2id, id2word,
                        length, temperature, rng):
    """Generiert `length` neue Woerter nach einem Prompt."""
    tokens = [t for t in tokenize(prompt) if t in word2id]
    if not tokens:
        tokens = ["once"]
    h = np.zeros((model.H,), dtype=np.float32)
    # Prompt zuerst durchs Netz laufen lassen (ohne zu samplen)
    for t in tokens[:-1]:
        e = embed_lookup[word2id[t]]
        h = np.tanh(model.Wxh @ e + model.Whh @ h + model.bh)
    seed_embed = embed_lookup[word2id[tokens[-1]]]
    ids, _ = model.sample(h, seed_embed, embed_lookup,
                          length=length, temperature=temperature, rng=rng)
    return " ".join(tokens + [id2word[i] for i in ids])


def main():
    # ---- Embeddings + Text laden ----
    W_emb, word2id, id2word = _load_embeddings()
    V, D = W_emb.shape
    print(f"[Embeddings] V={V}, D={D}")

    text = load_grimm()
    token_ids = _tokens_to_ids(text, word2id)
    print(f"[Corpus] {len(token_ids):,} Woerter (nur im Vokabular)")

    # ---- Modell ----
    rng = np.random.default_rng(SEED)
    model = WordRNN(vocab_size=V, embed_dim=D,
                    hidden_size=HIDDEN_SIZE, seed=SEED)

    print(f"[Model] WordRNN  V={V}  D={D}  H={HIDDEN_SIZE}  "
          f"Parameter: ~{HIDDEN_SIZE*(D+HIDDEN_SIZE+V):,}")

    # ---- Training (Karpathy-Stil, linear durch den Text) ----
    p = 0
    h = np.zeros((HIDDEN_SIZE,), dtype=np.float32)
    smooth_loss = -np.log(1.0 / V) * SEQ_LEN

    t0 = time.time()
    for step in range(1, NUM_STEPS + 1):
        if p + SEQ_LEN + 1 >= len(token_ids):
            p = 0
            h = np.zeros((HIDDEN_SIZE,), dtype=np.float32)

        input_ids = token_ids[p:p + SEQ_LEN]
        target_ids = token_ids[p + 1:p + SEQ_LEN + 1]
        embeds = W_emb[input_ids]     # (T, D)

        loss, grads, h = model.forward_backward(embeds, target_ids, h)
        model.step(grads, lr=LR)

        smooth_loss = 0.999 * smooth_loss + 0.001 * loss

        if step == 1 or step % SAMPLE_EVERY == 0:
            print()
            print("=" * 70)
            print(f"Schritt {step}/{NUM_STEPS}  "
                  f"loss={smooth_loss:.2f}  "
                  f"({smooth_loss/SEQ_LEN:.3f} pro Wort)  "
                  f"time={time.time()-t0:.1f}s")
            gen = _sample_from_prompt(
                model, "the king", W_emb, word2id, id2word,
                length=SAMPLE_LEN, temperature=1.0, rng=rng,
            )
            print("---- Sample (Prompt: 'the king') ----")
            print(gen)
            print("-------------------------------------")

        p += SEQ_LEN

    # ---- Ende: mehrere finale Samples mit verschiedenen Prompts ----
    print()
    print("=" * 70)
    print("FINALE SAMPLES (Temperature = 0.7):")
    for prompt in ["once upon a time", "the king said", "the wolf",
                   "in the forest"]:
        gen = _sample_from_prompt(
            model, prompt, W_emb, word2id, id2word,
            length=40, temperature=0.7, rng=rng,
        )
        print(f"\n  [{prompt}]  -> ")
        print(f"    {gen}")


if __name__ == "__main__":
    main()