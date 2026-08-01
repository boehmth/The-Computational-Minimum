# ============================================================
#  Grimm-Korpus (Project Gutenberg #2591)
#
#  Wir laden die englische Grimm-Ausgabe von Project Gutenberg
#  einmalig herunter, cachen sie lokal und entfernen die
#  Gutenberg-Header/Footer, sodass nur der eigentliche
#  Maerchentext uebrigbleibt.
# ============================================================

import os
import re
import urllib.request

GRIMM_URL = "https://www.gutenberg.org/cache/epub/2591/pg2591.txt"
CACHE_FILENAME = "grimm_en.txt"


def _cache_path():
    """Legt eine Datei im gleichen Ordner an (portabel und sichtbar)."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), CACHE_FILENAME)


def _strip_gutenberg_header_footer(raw):
    """Entfernt den Gutenberg-Vorspann und die Lizenz am Ende."""
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"

    i_start = raw.find(start_marker)
    if i_start >= 0:
        # Bis zum Ende der Markierungszeile
        i_start = raw.find("\n", i_start) + 1
    else:
        i_start = 0

    i_end = raw.find(end_marker)
    if i_end < 0:
        i_end = len(raw)

    return raw[i_start:i_end]


def load_grimm(refresh=False):
    """
    Laedt den Grimm-Maerchen-Korpus (Projekt Gutenberg, englisch).

    - Beim ersten Aufruf wird die Datei aus dem Netz geholt und lokal
      gespeichert (~550 kB).
    - Danach wird die lokale Kopie genutzt.
    - `refresh=True` erzwingt einen Neu-Download.

    Rueckgabe: reiner Maerchentext als String.
    """
    path = _cache_path()

    if refresh or not os.path.exists(path):
        print(f"[Grimm] Lade Korpus von {GRIMM_URL} ...")
        raw = urllib.request.urlopen(GRIMM_URL, timeout=60).read().decode("utf-8", "replace")
        text = _strip_gutenberg_header_footer(raw)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[Grimm] Gespeichert unter {path}  ({len(text):,} Zeichen)")
    else:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        print(f"[Grimm] Aus Cache geladen: {path}  ({len(text):,} Zeichen)")

    return text


if __name__ == "__main__":
    text = load_grimm()
    print("\n--- Anfang des Korpus ---")
    print(text[:500])
    print("...")
    print("\n--- Ende des Korpus ---")
    print(text[-500:])