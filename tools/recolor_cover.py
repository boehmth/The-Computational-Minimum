"""
recolor_cover.py - Farbtausch fuer die Kapitel-Cover in Teil 1

Ziel: das AI-generierte Cover, das oft Nebenfarben (Gelb, Beige,
Zwischentoene) einbringt, konsequent auf die vier-farbige Serien-
Palette abbilden - Weiss, Rot, Blau, Schwarz - inspiriert von der
minimalistischen 1980er-Elektronik-Album-Aesthetik, ohne dass wir
neu generieren muessen.

Vorgehen:
    1. Wir clustern die Pixelfarben des Bildes in K Farb-Gruppen
       (K klein, z. B. 5-8).
    2. Fuer jedes Cluster suchen wir die naechstgelegene Farbe aus der
       Zielpalette. "Naechstgelegen" heisst hier: kleinster Euklidischer
       Abstand im RGB-Raum, mit *leichter* Gewichtung auf Helligkeit
       (Y-Kanal), damit ein helles Gelb nicht faelschlich als Rot
       klassifiziert wird.
    3. Jedes Pixel wird durch die entsprechende Zielfarbe ersetzt.

Voraussetzung: `pillow` (`pip install pillow`).

Aufruf:
    python tools/recolor_cover.py 01_Computing/06_Networks/assets/cover.png
    # -> schreibt daneben cover_v2.png
"""

from __future__ import annotations

import argparse
import math
import os
import random
from typing import List, Tuple

try:
    from PIL import Image
except ImportError as e:
    raise SystemExit(
        "Dieses Skript braucht Pillow: pip install pillow"
    ) from e


# -------------------------------------------------------------------------
# Zielpalette: kapitel-spezifisch, importiert aus palettes.py
# -------------------------------------------------------------------------
# Default: 06_networks (Tour de France - Weiss/Rot/Blau/Anthrazit).
# Ueber die CLI (--chapter oder --palette) kann eine andere Palette
# gewaehlt werden, siehe palettes.CHAPTER_PALETTES.

from palettes import (
    CHAPTER_PALETTES,
    get_palette_as_list,
    get_palette,
)

# Wird zur Laufzeit gesetzt (siehe main())
TARGET_PALETTE: List[Tuple[int, int, int]] = get_palette_as_list("06_networks")
PALETTE_NAMES: List[str] = ["background", "structure", "signal", "contrast"]


def _rgb_to_hsl(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """RGB (0..255) -> HSL (H in [0,360), S in [0,1], L in [0,1])."""
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    L = (mx + mn) / 2.0
    if mx == mn:
        return 0.0, 0.0, L
    d = mx - mn
    S = d / (1 - abs(2 * L - 1)) if 0 < L < 1 else 0.0
    if mx == r:
        H = ((g - b) / d) % 6
    elif mx == g:
        H = ((b - r) / d) + 2
    else:
        H = ((r - g) / d) + 4
    H *= 60
    return H, S, L


def _classify(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """
    Robuste Klassifikation nach HSL relativ zur *aktuellen* Zielpalette
    (TARGET_PALETTE, gesetzt in main()):
      * Unbunt (S <= 0.20)  -> Hintergrund (hell) oder Kontrast (dunkel)
      * Bunt                -> die naechstliegende bunte Farbe der Palette
                               (Struktur oder Signal, je nach Farbton)

    So funktioniert dasselbe Skript fuer alle Kapitel; wir setzen einfach
    TARGET_PALETTE via --chapter um.
    """
    H, S, L = _rgb_to_hsl(rgb)

    # Palette entpacken (Reihenfolge: background, structure, signal, contrast)
    bg, structure, signal, contrast = TARGET_PALETTE

    # 0) Sehr hell (fast weiss): immer Hintergrund, auch bei minimaler Faerbung.
    if L > 0.88:
        return bg
    # 0b) Sehr dunkel: immer Kontrast.
    if L < 0.15:
        return contrast

    # 1) Unbunt (mittlere Helligkeit): nach Helligkeit -> Hintergrund oder Kontrast
    if S < 0.25:
        return bg if L > 0.55 else contrast

    # 2) Bunt: waehle die naechstliegende der beiden BUNTEN Palettenfarben
    #    (structure und signal). Wir vergleichen im HSL-Raum mit Fokus auf
    #    Farbton (H) und Saettigung.
    def _hsl_dist(rgb_a: Tuple[int, int, int], rgb_b: Tuple[int, int, int]) -> float:
        Ha, Sa, La = _rgb_to_hsl(rgb_a)
        Hb, Sb, Lb = _rgb_to_hsl(rgb_b)
        # zirkulaerer Abstand fuer H
        dH = abs(Ha - Hb)
        if dH > 180:
            dH = 360 - dH
        return math.sqrt(2.5 * dH * dH + 60 * (Sa - Sb) ** 2 + 30 * (La - Lb) ** 2)

    d_structure = _hsl_dist(rgb, structure)
    d_signal = _hsl_dist(rgb, signal)

    return structure if d_structure <= d_signal else signal


def _rgb_distance(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> float:
    """Standard-Euklid, wird nur noch fürs k-Means-Clustering benutzt."""
    dR = a[0] - b[0]
    dG = a[1] - b[1]
    dB = a[2] - b[2]
    return math.sqrt(dR * dR + dG * dG + dB * dB)


def _nearest_palette_color(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Klassifiziert eine Farbe robust ueber HSL statt Euklid im RGB."""
    return _classify(rgb)


# -------------------------------------------------------------------------
# Sehr einfaches k-Means, damit wir nicht scikit-learn brauchen
# -------------------------------------------------------------------------

def _kmeans(pixels: List[Tuple[int, int, int]], k: int = 6,
            iters: int = 15, seed: int = 42) -> List[Tuple[int, int, int]]:
    """Ein naives k-Means auf RGB-Pixeln."""
    rng = random.Random(seed)
    centers = [pixels[rng.randrange(len(pixels))] for _ in range(k)]
    for _ in range(iters):
        # Zuweisung
        buckets: List[List[Tuple[int, int, int]]] = [[] for _ in range(k)]
        for p in pixels:
            best_i = 0
            best_d = _rgb_distance(p, centers[0])
            for i in range(1, k):
                d = _rgb_distance(p, centers[i])
                if d < best_d:
                    best_d = d
                    best_i = i
            buckets[best_i].append(p)
        # Neue Zentren
        new_centers = []
        for i in range(k):
            if not buckets[i]:
                new_centers.append(centers[i])
            else:
                r = sum(p[0] for p in buckets[i]) // len(buckets[i])
                g = sum(p[1] for p in buckets[i]) // len(buckets[i])
                b = sum(p[2] for p in buckets[i]) // len(buckets[i])
                new_centers.append((r, g, b))
        if new_centers == centers:
            break
        centers = new_centers
    return centers


# -------------------------------------------------------------------------
# Kern: Bild neu einfaerben
# -------------------------------------------------------------------------

def recolor(image_path: str, output_path: str, k: int = 6,
            sample_size: int = 20000) -> None:
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    px = img.load()

    # 1) Stichprobe von Pixeln sammeln (fuer schnelleres k-Means)
    rng = random.Random(42)
    n_total = w * h
    n_sample = min(sample_size, n_total)
    sample: List[Tuple[int, int, int]] = []
    for _ in range(n_sample):
        x = rng.randrange(w)
        y = rng.randrange(h)
        sample.append(px[x, y])  # type: ignore

    # 2) Cluster finden
    centers = _kmeans(sample, k=k)

    # 3) Jedes Cluster auf die naechste Zielfarbe abbilden
    center_to_target = {c: _nearest_palette_color(c) for c in centers}

    print("[recolor] Cluster -> Zielfarbe:")
    for c, t in center_to_target.items():
        tname = PALETTE_NAMES[TARGET_PALETTE.index(t)]
        print(f"   {c}  -->  {t}   ({tname})")

    # 4) Alle Pixel: pro Pixel wieder das naechste Cluster suchen, dann
    #    das gemappte Ziel benutzen.
    center_list = list(center_to_target.keys())
    target_list = [center_to_target[c] for c in center_list]

    out = Image.new("RGB", (w, h))
    out_px = out.load()
    for y in range(h):
        for x in range(w):
            p = px[x, y]  # type: ignore
            # nearest center
            best_i = 0
            best_d = _rgb_distance(p, center_list[0])
            for i in range(1, len(center_list)):
                d = _rgb_distance(p, center_list[i])
                if d < best_d:
                    best_d = d
                    best_i = i
            out_px[x, y] = target_list[best_i]  # type: ignore

    out.save(output_path)
    print(f"[recolor] Gespeichert: {output_path}")


# -------------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------------

def main():
    global TARGET_PALETTE
    parser = argparse.ArgumentParser(
        description="Faerbe ein Kapitel-Cover auf die kapitel-spezifische "
                    "4-Farben-Serien-Palette (siehe tools/palettes.py)."
    )
    parser.add_argument("image", help="Pfad zum Ausgangs-Bild (PNG/JPG)")
    parser.add_argument(
        "-o", "--output", default=None,
        help="Ausgabedatei (Default: neben dem Input als *_v2.png)"
    )
    parser.add_argument("-k", "--clusters", type=int, default=6,
                        help="Anzahl Farb-Cluster im Zwischenschritt (Default: 6)")
    parser.add_argument(
        "--chapter", default=None,
        help=(
            "Kapitel-Schluessel fuer die Zielpalette. Wenn nicht angegeben, "
            "wird versucht, ihn aus dem Bildpfad zu inferieren (z. B. "
            "'01_Computing/06_Networks/...' -> '06_networks'). "
            f"Verfuegbar: {', '.join(sorted(CHAPTER_PALETTES.keys()))}"
        )
    )
    args = parser.parse_args()

    # Palette wählen: --chapter > Pfad-Inferenz > Default
    chapter_key = args.chapter
    if chapter_key is None:
        # Versuche aus dem Pfad zu erraten - suche nach einem der bekannten Keys
        norm = args.image.replace("\\", "/").lower()
        for key in CHAPTER_PALETTES.keys():
            # 06_networks -> suche nach '06_networks' oder '06_network'
            candidate = key.replace("_", "").lower()
            path_pieces = norm.replace("_", "").lower()
            if candidate in path_pieces:
                chapter_key = key
                break

    if chapter_key is None:
        chapter_key = "06_networks"
        print(f"[recolor] Keine Kapitel-Palette aus Pfad ableitbar, nutze Default: {chapter_key}")
    else:
        print(f"[recolor] Kapitel-Palette: {chapter_key}")

    TARGET_PALETTE = get_palette_as_list(chapter_key)
    p = get_palette(chapter_key)
    print(f"[recolor] Ziel-Farben:")
    for name, rgb in p.items():
        hex_ = "#{:02X}{:02X}{:02X}".format(*rgb)
        print(f"    {name:10s} = rgb{rgb}  {hex_}")

    if args.output is None:
        base, _ = os.path.splitext(args.image)
        args.output = base + "_v2.png"

    recolor(args.image, args.output, k=args.clusters)


if __name__ == "__main__":
    main()