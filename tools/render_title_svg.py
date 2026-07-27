"""
render_title_svg.py - erzeugt eine SVG-Titelgrafik fuer ein Kapitel

Zweck: In GitHub-Markdown werden Custom-Fonts NICHT gerendert. Ein
`<img>`-Tag mit einer SVG-Datei aber schon - und in dieser SVG-Datei
koennen wir jede beliebige Web-Font einbinden (Google Fonts o. ae.).
Damit bekommt jeder Kapitel-Titel im README seine gewuenschte Schrift,
Farbe und typografische Klarheit, ohne dass wir auf ein spezielles
Publikations-Setup warten muessen.

Ausgabe: eine `title.svg` neben dem Kapitel-Cover in `assets/`.

Aufruf:
    python tools/render_title_svg.py \
        --chapter 06_networks \
        --number "06" \
        --title "Netzwerk" \
        --subtitle "Le Tour de Bit" \
        --output 01_Computing/06_Networks/assets/title.svg

Alle Argumente sind optional; ohne Angabe gibt es sinnvolle Defaults.

Kein Python-Grafik-Framework, reines SVG.
"""

from __future__ import annotations

import argparse
import os
import sys

# Palettes-Modul importieren (liegt im selben Ordner)
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from palettes import get_palette  # noqa: E402


# -------------------------------------------------------------------------
# SVG-Vorlage
# -------------------------------------------------------------------------
# Wir zeichnen:
#   * einen breiten Hintergrund in Papier-Weiss (bg-Farbe der Palette)
#   * eine dünne Signaturlinie in Struktur-Farbe unterhalb
#   * die Kapitel-Nummer gross links (Papier-Farbe auf Signal-Hintergrund,
#     analog zu einer Trikot-Nummer)
#   * den Titel in grosser konstruktiver Schrift daneben
#   * einen Untertitel in kleinerer, kursiver Schrift darunter
#
# Verwendete Web-Font (SIL OFL): Space Grotesk. Wir laden sie per
# `<style>` innerhalb der SVG - GitHub rendert das korrekt.

SVG_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 1200 240"
     preserveAspectRatio="xMidYMid meet"
     role="img"
     aria-label="{aria_label}">
  <defs>
    <style type="text/css">
      @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&amp;family=Chakra+Petch:ital@0;1&amp;display=swap');
      .bg      {{ fill: {bg}; }}
      .rule    {{ stroke: {structure}; stroke-width: 2; }}
      .num-bg  {{ fill: {signal}; }}
      .num-txt {{ fill: {bg};
                  font-family: 'Space Grotesk', system-ui, sans-serif;
                  font-weight: 700;
                  font-size: 96px;
                  letter-spacing: -0.02em; }}
      .title   {{ fill: {structure};
                  font-family: 'Space Grotesk', system-ui, sans-serif;
                  font-weight: 500;
                  font-size: 72px;
                  letter-spacing: -0.01em; }}
      .sub     {{ fill: {signal};
                  font-family: 'Chakra Petch', 'Space Grotesk', sans-serif;
                  font-style: italic;
                  font-weight: 400;
                  font-size: 34px;
                  letter-spacing: 0.02em; }}
      .mark    {{ fill: {structure};
                  font-family: 'Space Grotesk', system-ui, sans-serif;
                  font-size: 24px;
                  letter-spacing: 0.4em; }}
    </style>
  </defs>

  <!-- Papier-Hintergrund -->
  <rect class="bg" x="0" y="0" width="1200" height="240"/>

  <!-- Trikot-Nummer links: Kreis oder Rechteck als Halterahmen? -->
  <!-- Rechteck-Variante: passt zu einer Startnummer -->
  <rect class="num-bg" x="30" y="40" width="180" height="160" rx="6" ry="6"/>
  <text class="num-txt" x="120" y="164" text-anchor="middle">{number}</text>

  <!-- Titel und Untertitel rechts daneben -->
  <text class="title" x="250" y="120">{title}</text>
  <text class="sub"   x="252" y="170">{subtitle}</text>

  <!-- Dezente Struktur-Signatur ganz unten -->
  <line class="rule" x1="30" y1="215" x2="1170" y2="215"/>
  <text class="mark" x="30"   y="235">◆</text>
  <text class="mark" x="1140" y="235" text-anchor="end">◆</text>
</svg>
"""


def _to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def render(chapter: str, number: str, title: str, subtitle: str,
           output: str) -> None:
    p = get_palette(chapter)

    svg = SVG_TEMPLATE.format(
        bg=_to_hex(p["background"]),
        structure=_to_hex(p["structure"]),
        signal=_to_hex(p["signal"]),
        contrast=_to_hex(p["contrast"]),
        number=number,
        title=title,
        subtitle=subtitle,
        aria_label=f"Kapitel {number} · {title} — {subtitle}",
    )

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"[title-svg] Kapitel-Palette : {chapter}")
    print(f"[title-svg] Nummer          : {number}")
    print(f"[title-svg] Titel           : {title}")
    print(f"[title-svg] Untertitel      : {subtitle}")
    print(f"[title-svg] Gespeichert     : {output}")


def main():
    parser = argparse.ArgumentParser(
        description="Generiert eine SVG-Titelgrafik fuer ein Kapitel."
    )
    parser.add_argument("--chapter", default="06_networks",
                        help="Kapitel-Schluessel (siehe palettes.py)")
    parser.add_argument("--number", default="06",
                        help="Kapitel-Nummer (2-stellig als String)")
    parser.add_argument("--title", default="Netzwerk",
                        help="Kapitel-Titel")
    parser.add_argument("--subtitle", default="Le Tour de Bit",
                        help="Kapitel-Untertitel (das 'coole' Motto)")
    parser.add_argument("--output", required=True,
                        help="Zieldatei (SVG)")
    args = parser.parse_args()

    render(args.chapter, args.number, args.title, args.subtitle, args.output)


if __name__ == "__main__":
    main()