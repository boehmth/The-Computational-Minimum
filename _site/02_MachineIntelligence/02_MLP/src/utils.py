# ============================================================
#  Hilfsfunktionen fuer das MLP
#  (Aktivierungen, Ableitungen, Argmax, Rauschen)
# ============================================================

import math
import random


def sigmoid(x):
    """Sigmoid-Aktivierungsfunktion."""
    return 1 / (1 + math.exp(-x))


def sigmoid_derivative(y):
    """Ableitung der Sigmoid-Funktion.
    Achtung: y ist bereits sigmoid(x), nicht das rohe x."""
    return y * (1 - y)


def argmax_index(werte):
    """Gibt den Index des groessten Wertes in einer Liste zurueck."""
    return max(range(len(werte)), key=lambda i: werte[i])


def add_noise(bitmap, flips=5):
    """
    Kippt `flips` zufaellige Bits in der Bitmap um.

    bitmap: Liste von 81 int-Werten (0/1)
    """
    verrauscht = bitmap.copy()
    indizes = random.sample(range(81), flips)
    for idx in indizes:
        verrauscht[idx] = 1 - verrauscht[idx]   # Bit umkippen
    return verrauscht