# ============================================================
#  Korpus-Loader fuer das RNN-Kapitel
#
#  Wir verwenden denselben Grimm-Korpus wie in Meilenstein 4
#  (englische Grimm-Ausgabe, Project Gutenberg #2591). Wenn
#  der Cache aus dem Word2Vec-Kapitel bereits existiert,
#  benutzen wir ihn direkt. Sonst laden wir ihn ins RNN-
#  Verzeichnis herunter.
# ============================================================

import os
import urllib.request

GRIMM_URL = "https://www.gutenberg.org/cache/epub/2591/pg2591.txt"
CACHE_FILENAME = "grimm_en.txt"


def _cache_paths():
    """Liefert moegliche Cache-Positionen (lokal + im Nachbar-Word2Vec-Ordner)."""
    here = os.path.dirname(os.path.abspath(__file__))
    local_cache = os.path.join(here, CACHE_FILENAME)
    w2v_cache = os.path.abspath(os.path.join(here, "..", "..", "Word2Vec", "src", CACHE_FILENAME))
    return local_cache, w2v_cache


def _strip_gutenberg(raw):
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
    i_start = raw.find(start_marker)
    if i_start >= 0:
        i_start = raw.find("\n", i_start) + 1
    else:
        i_start = 0
    i_end = raw.find(end_marker)
    if i_end < 0:
        i_end = len(raw)
    return raw[i_start:i_end]


def load_grimm(refresh=False):
    """
    Laedt den Grimm-Text. Sucht zuerst im lokalen Cache, dann im Word2Vec-Cache;
    laedt nur bei Bedarf neu.
    """
    local_cache, w2v_cache = _cache_paths()

    if not refresh:
        if os.path.exists(local_cache):
            with open(local_cache, "r", encoding="utf-8") as f:
                text = f.read()
            print(f"[Grimm] Aus lokalem Cache: {local_cache}  ({len(text):,} Zeichen)")
            return text
        if os.path.exists(w2v_cache):
            with open(w2v_cache, "r", encoding="utf-8") as f:
                text = f.read()
            print(f"[Grimm] Wiederverwendet aus Word2Vec-Cache: {w2v_cache}  ({len(text):,} Zeichen)")
            return text

    print(f"[Grimm] Lade Korpus von {GRIMM_URL} ...")
    raw = urllib.request.urlopen(GRIMM_URL, timeout=60).read().decode("utf-8", "replace")
    text = _strip_gutenberg(raw)
    with open(local_cache, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[Grimm] Gespeichert unter {local_cache}  ({len(text):,} Zeichen)")
    return text


if __name__ == "__main__":
    text = load_grimm()
    print("\n--- Anfang ---")
    print(text[:500])