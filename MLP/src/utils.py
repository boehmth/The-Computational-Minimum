# ============================================================
#  Utility functions for MLP (activation, derivatives, helpers)
# ============================================================

import random
import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def sigmoid_derivative(y):
    # y is already sigmoid(x)
    return y * (1 - y)

def argmax_index(values):
    return max(range(len(values)), key=lambda i: values[i])

def add_noise(bitmap, flips=5):
    """
    Flip 'flips' random bits in the bitmap.
    bitmap: list of 81 ints (0/1)
    """
    noisy = bitmap.copy()
    indices = random.sample(range(81), flips)
    for idx in indices:
        noisy[idx] = 1 - noisy[idx]  # flip bit
    return noisy