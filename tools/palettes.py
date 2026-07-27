"""
palettes.py - Kapitel-spezifische Farbpaletten für Teil 1

Die Kraftwerk-inspirierte Ästhetik lebt nicht von EINER Farbpalette,
sondern von einer *Regel*: 3-4 flache Farben pro Kapitel, keine Verlaufe,
keine Textur. Die konkreten Farben variieren pro Album/Kapitel.

Dieses Modul definiert die Ziel-Paletten fuer jedes Kapitel. Sie werden
von `recolor_cover.py` benutzt.

Historische Album-Anker (nur thematisch, niemals im Prompt genannt):

    Kap 00  Fundament             ~ Ralf & Florian (1973), warme Erdtoene
    Kap 01  CPU                   ~ Autobahn (1974), Grau/Blau/Schwarz auf Weiss
    Kap 02  OS                    ~ Radio-Aktivitaet (1975), Gelb/Schwarz
    Kap 03  Compiler              ~ Trans Europa Express (1977), Rot/Schwarz auf Weiss
    Kap 04  PerceptronOnCPU       ~ Die Mensch-Maschine (1978), Rot/Schwarz auf Weiss
    Kap 05  GPU                   ~ Computerwelt (1981), Gruen-Terminal auf Schwarz
    Kap 06  Netzwerk (ALOHA)      ~ Tour de France (1983/2003), Weiss/Rot/Blau/Anthrazit
"""

from __future__ import annotations
from typing import Dict, List, Tuple

RGB = Tuple[int, int, int]

# -------------------------------------------------------------------------
# Grundprinzipien der Paletten
# -------------------------------------------------------------------------
# Jede Palette besteht aus:
#   1. Einem Hintergrund (nicht rein weiss, nicht rein schwarz)
#   2. Einer dominanten Struktur-Farbe (dunkel, meist blau/schwarz)
#   3. Einer Signalfarbe (bunt, seltene Akzente)
#   4. Optional: einer vierten Farbe fuer Kontrast

CHAPTER_PALETTES: Dict[str, Dict[str, RGB]] = {

    # Kap 00 Fundament: Warme Erd-/Papiertoene, wie ein altes Manuskript
    "00_fundament": {
        "background": (238, 232, 219),   # gebrochenes Weiss, leicht warm
        "structure":  (48, 40, 32),       # dunkle Erde (fast schwarz-braun)
        "signal":     (172, 46, 30),      # gedaempftes Zinnoberrot
        "contrast":   (28, 28, 32),       # anthrazit fuer feinste Kontraste
    },

    # Kap 01 CPU: Kuehles Autobahn-Setup, Verkehrslinien-Blau + Grau
    "01_cpu": {
        "background": (232, 233, 236),   # sehr helles Grau-Weiss
        "structure":  (32, 44, 78),       # tiefes Verkehrsblau
        "signal":     (218, 60, 60),      # ein Rot-Marker
        "contrast":   (100, 105, 115),    # neutrales Mittelgrau
    },

    # Kap 02 OS: Gelb-Schwarz, Radio-/Warn-Aesthetik
    "02_os": {
        "background": (245, 240, 230),   # papier-hell
        "structure":  (16, 16, 20),       # sehr dunkles Schwarz-Anthrazit
        "signal":     (240, 190, 40),     # sattes, warmes Gelb (Warnfarbe)
        "contrast":   (200, 60, 40),      # rot fuer echte Alarm-Elemente
    },

    # Kap 03 Compiler: Trans-Europa-Express-Stil, Rot-Schwarz auf Weiss
    "03_compiler": {
        "background": (245, 240, 232),   # papier
        "structure":  (30, 30, 30),       # neutrales Schwarz
        "signal":     (198, 40, 40),      # trikot-rot / express-rot
        "contrast":   (100, 100, 100),    # mittleres Grau fuer sekundaere Linien
    },

    # Kap 04 PerceptronOnCPU: Mensch-Maschine-Stil, Rot-Schwarz mit Verspieltheit
    "04_perceptron": {
        "background": (238, 234, 226),
        "structure":  (24, 24, 28),
        "signal":     (204, 32, 32),      # kraeftiges Rot fuer das "Neuron"
        "contrast":   (140, 140, 140),
    },

    # Kap 05 GPU: Computerwelt-Aesthetik, Grün-Schwarz-Terminal auf Papier
    "05_gpu": {
        "background": (240, 235, 225),
        "structure":  (18, 22, 20),
        "signal":     (44, 138, 60),      # frueher-Terminal-Gruen (nicht neon)
        "contrast":   (120, 118, 108),
    },

    # Kap 06 Netzwerk: Tour de France, Weiss-Rot-Blau-Anthrazit
    "06_networks": {
        "background": (245, 240, 232),
        "structure":  (26, 42, 92),
        "signal":     (198, 40, 40),
        "contrast":   (28, 28, 32),
    },
}


def get_palette(chapter_key: str) -> Dict[str, RGB]:
    """Liefert die Palette eines Kapitels. Fällt auf 06_networks zurück."""
    return CHAPTER_PALETTES.get(chapter_key, CHAPTER_PALETTES["06_networks"])


def get_palette_as_list(chapter_key: str) -> List[RGB]:
    """Palette als flache Liste von 4 RGB-Farben (in fester Reihenfolge)."""
    p = get_palette(chapter_key)
    return [p["background"], p["structure"], p["signal"], p["contrast"]]


def format_palette_for_prompt(chapter_key: str) -> str:
    """
    Formatiert die Palette als String für Bild-Generator-Prompts.
    Ausgabe: 'background #RRGGBB, structure #RRGGBB, signal #RRGGBB, contrast #RRGGBB'
    """
    p = get_palette(chapter_key)

    def hex_(rgb: RGB) -> str:
        return "#{:02X}{:02X}{:02X}".format(*rgb)

    return (
        f"background {hex_(p['background'])}, "
        f"structure {hex_(p['structure'])}, "
        f"signal {hex_(p['signal'])}, "
        f"contrast {hex_(p['contrast'])}"
    )
