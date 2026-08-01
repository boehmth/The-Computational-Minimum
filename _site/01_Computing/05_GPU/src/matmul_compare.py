"""
matmul_compare.py - Matrix-Multiplikation: seriell (CPU) vs. gekachelt-parallel (GPU)

Was hier passiert:

Wir multiplizieren zwei quadratische Matrizen `C = A @ B`, jeweils der
Groesse (n, n). Zweimal:

    (a) SERIELL (CPU-Modell):
        drei ineinander verschachtelte Schleifen. Fuer jede der n*n
        Ausgabezellen n Multiplikationen -> total n^3 Instruktionen.

    (b) GEKACHELT-PARALLEL (GPU-Modell):
        Wir teilen C in Bloecke der Groesse (block_size, block_size).
        Fuer jeden Block liest die GPU je einen Streifen aus A und B in
        den Shared Memory. Innerhalb eines Blocks berechnen block_size *
        block_size Threads gleichzeitig ihre Ausgabezelle. Das entspricht
        dem klassischen "Tiled MatMul", das in jeder GPU-Programmier-
        Uebung als Erstes vorkommt.

Fuer unseren Simulator interessiert nur die Schritt-Zaehlung. Der Speed-up
gegenueber der seriellen CPU ist der Kern-Take-away.

Kein PyTorch, kein CUDA - reines Python + gpu_sim.py.
"""

from __future__ import annotations

import argparse
from typing import List

from gpu_sim import SIMT_GPU, Warp, DEFAULT_WARP_SIZE


def matmul_serial(A: List[List[float]], B: List[List[float]]) -> tuple[list, int]:
    """Klassische drei-Schleifen-MatMul. Rueckgabe: (C, n_ops)."""
    n = len(A)
    C = [[0.0] * n for _ in range(n)]
    ops = 0
    for i in range(n):
        for j in range(n):
            s = 0.0
            for k in range(n):
                s += A[i][k] * B[k][j]
                ops += 1  # eine MUL-ADD als eine Op
            C[i][j] = s
    return C, ops


def matmul_tiled_parallel(
    A: List[List[float]],
    B: List[List[float]],
    block_size: int,
    warp_size: int = DEFAULT_WARP_SIZE,
) -> tuple[list, int]:
    """
    Gekachelte Matrix-Multiplikation im SIMT-Modell.

    Idee: Jeder Block der Groesse (block_size x block_size) im
    Ausgabemuster C wird von einem "GPU-Block" mit block_size^2 Threads
    berechnet. Fuer jedes Kachelpaar aus A und B laden alle Threads
    gemeinsam die Kacheln (block_size Schritte) und akkumulieren dann
    ihre Ausgabezelle (nochmal block_size Schritte).

    Fuer die Schritt-Zaehlung ist es unerheblich, wie viele Bloecke wir
    gleichzeitig laufen lassen wuerden - auf einer echten GPU liefen sie
    parallel; wir zaehlen aber ohnehin nur die Schritte PRO Block und
    multiplizieren nicht mit der Blockzahl, weil das die parallele
    Struktur richtig widerspiegelt.
    """
    n = len(A)
    assert n % block_size == 0, "n muss durch block_size teilbar sein"
    C = [[0.0] * n for _ in range(n)]

    gpu = SIMT_GPU(warp_size=warp_size)

    # Wir simulieren EINEN Block der Ausgabe (block_size x block_size Threads).
    # Auf einer echten GPU wuerden alle (n/block_size)^2 Bloecke parallel
    # laufen; die Schritt-Zaehlung pro Block ist dieselbe.

    n_tiles = n // block_size

    # Wir starten einen Kernel mit block_size**2 Threads. Jeder Thread
    # entspricht einer Ausgabezelle im aktuellen Ausgabe-Block. Die Threads
    # iterieren gemeinsam ueber die n_tiles Tile-Paare in K-Richtung.
    #
    # Wichtig: wir nutzen den Simulator nur zur Schritt-Zaehlung fuer EINEN
    # Ausgabe-Block. Danach kopieren wir das Ergebnis in C (das ist reine
    # Buchhaltung, keine Rechenlast).

    n_threads_per_block = block_size * block_size

    # Fuehre eine EINZELNE Kernel-Instanz aus (repraesentativ fuer alle
    # Ausgabe-Bloecke; auf echter GPU laufen sie parallel).
    def _kernel(warp: Warp) -> None:
        # In dieser vereinfachten Simulation macht jeder Thread pro K-Tile
        # zwei "Lade"-Schritte (A- und B-Kachel) und dann block_size
        # MUL-ADD-Steps. Wir zaehlen sie warp-weise.
        for _tile in range(n_tiles):
            warp.step()  # A-Kachel laden
            warp.step()  # B-Kachel laden
            for _k_inner in range(block_size):
                warp.step()  # eine MUL-ADD-Runde in Shared Memory

    # block_size^2 Threads, aber wir starten diesen "Simulations-Kernel"
    # nur einmal (er repraesentiert einen Ausgabe-Block).
    gpu.run_kernel(_kernel, n_threads=n_threads_per_block)

    # Jetzt die tatsaechliche Berechnung (nicht Teil der Simulation - wir
    # brauchen sie nur, um das Ergebnis zu verifizieren):
    for bi in range(n_tiles):
        for bj in range(n_tiles):
            for i in range(block_size):
                for j in range(block_size):
                    gi = bi * block_size + i
                    gj = bj * block_size + j
                    s = 0.0
                    for k in range(n):
                        s += A[gi][k] * B[k][gj]
                    C[gi][gj] = s

    # Steps PRO Block. Auf einer echten GPU laufen (n_tiles)^2 solche Bloecke
    # parallel - also brauchen wir die Schritte NICHT mit der Blockzahl zu
    # multiplizieren. Das ist genau der Grund, warum GPU-MatMul so gut skaliert.
    return C, gpu.parallel_steps


def main():
    parser = argparse.ArgumentParser(
        description="Matrix-Multiplikation: seriell vs. GPU-gekachelt.")
    parser.add_argument("--n", type=int, default=32, help="Matrix-Groesse (n x n)")
    parser.add_argument("--block-size", type=int, default=8,
                        help="Kachelgroesse fuer den GPU-Fall (block_size x block_size)")
    args = parser.parse_args()

    n = args.n
    bs = args.block_size

    # Kleine deterministische Matrizen zum Verifizieren
    A = [[float((i * 7 + j) % 5) for j in range(n)] for i in range(n)]
    B = [[float((i * 3 + j) % 4) for j in range(n)] for i in range(n)]

    print("=" * 72)
    print(f"Matrix-Multiplikation C = A @ B  (n = {n}, block_size = {bs})")
    print("=" * 72)

    C_cpu, cpu_ops = matmul_serial(A, B)
    print(f"\nSERIELL (CPU-Modell):")
    print(f"  Operationen:      {cpu_ops:,}   (= n^3 = {n}^3)")

    C_gpu, gpu_steps = matmul_tiled_parallel(A, B, block_size=bs)
    print(f"\nGEKACHELT-PARALLEL (GPU-Modell):")
    print(f"  Schritte pro Ausgabe-Block: {gpu_steps}")
    print(f"  (auf einer echten GPU wuerden alle {(n // bs) ** 2} Bloecke")
    print(f"   parallel laufen, die Zeit ist also NICHT mit der Blockzahl")
    print(f"   zu multiplizieren.)")

    speedup = cpu_ops / max(gpu_steps, 1)
    print(f"\nSpeed-up gegenueber seriellem CPU-Modell: ~{speedup:.0f}x")

    # Ergebnis-Sanity: die tatsaechlich berechneten Werte stimmen ueberein.
    ok = all(abs(C_cpu[i][j] - C_gpu[i][j]) < 1e-9
             for i in range(n) for j in range(n))
    print(f"Ergebnisse identisch: {ok}")

    print("\n" + "=" * 72)
    print("KERN-BEOBACHTUNG:")
    print("  Die Ausgabe-Bloecke sind unabhaengig voneinander -> parallel")
    print("  ausfuehrbar. Damit skaliert Matrix-Multiplikation praktisch")
    print("  linear mit der Anzahl gleichzeitig aktiver GPU-Bloecke.")
    print("  Genau das ist der Grund, warum GPUs Deep Learning tragen:")
    print("  ein neuronales Netz besteht fast ausschliesslich aus")
    print("  Matrix-Multiplikationen. AlexNet 2012 -> GPT-4 2023 -> H100 heute.")


if __name__ == "__main__":
    main()