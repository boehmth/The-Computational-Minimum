"""
test_simt.py - Standalone-Beweis: CPU-Seriell vs. GPU-Parallel

Was dieses Skript zeigt (ohne PyTorch, ohne CUDA, ohne echte GPU):

Wir loesen dieselbe Aufgabe zweimal:
    (a) CPU-Modell: eine Instruktion pro Element   -> n Schritte
    (b) GPU-Modell: warp-parallel                  -> n/warp_size Schritte

Der Vergleich zeigt den Kernpunkt des ganzen Kapitels: die GPU rechnet
NICHTS anderes als die CPU. Sie rechnet dasselbe in weniger Schritten,
weil sie Threads warp-weit gleichzeitig ausfuehrt.

Drei Vergleiche:
    1. Vektor-Addition (kein Divergenz-Problem)   -> ideale Beschleunigung
    2. ReLU mit `if` innerhalb einer Warp         -> Warp Divergence sichtbar
    3. Skalarprodukt mit Baum-Reduktion           -> log2(n)-Schritte statt n

Kein PyTorch, kein Netz - reines Python.
"""

from __future__ import annotations

import math

from gpu_sim import (
    DEFAULT_WARP_SIZE,
    SIMT_GPU,
    kernel_vector_add,
    kernel_relu,
    kernel_relu_divergent,
    kernel_dot_reduce,
)


def hr():
    print("-" * 72)


def run_vector_add():
    print("\n=== 1) Vektor-Addition: c[i] = a[i] + b[i] ===")
    n = 64
    a = list(range(n))
    b = list(range(n))
    c = [0.0] * n

    # ---- CPU (seriell): eine Addition pro Iteration
    cpu_steps = 0
    for i in range(n):
        c[i] = a[i] + b[i]
        cpu_steps += 1
    hr()
    print(f"CPU seriell:  n={n} Elemente -> {cpu_steps} Instruktionen")

    # ---- GPU (SIMT)
    c_gpu = [0.0] * n
    gpu = SIMT_GPU(warp_size=DEFAULT_WARP_SIZE)
    gpu.run_kernel(kernel_vector_add(a, b, c_gpu), n_threads=n)
    hr()
    print(f"GPU SIMT:     n={n} Elemente, warp_size={gpu.warp_size} "
          f"-> {gpu.parallel_steps} warp-parallele Instruktionen")

    speedup = cpu_steps / max(gpu.parallel_steps, 1)
    print(f"Speed-up:     ~{speedup:.1f}x  (theoretisch: warp_size = {gpu.warp_size})")

    # Sanity-Check: Ergebnisse identisch
    assert c == c_gpu, "CPU- und GPU-Resultate weichen ab!"
    print("Ergebnisse identisch. OK.")


def run_relu_divergence():
    print("\n=== 2) ReLU: y[i] = max(0, x[i]) - mit und ohne Warp Divergence ===")
    # 8 Werte, gemischtes Vorzeichen - garantiert Divergenz innerhalb der Warp
    x = [1.0, -2.0, 3.0, -4.0, 5.0, -6.0, 7.0, -8.0]
    n = len(x)

    # (a) unified branchless ReLU
    y1 = [0.0] * n
    gpu_a = SIMT_GPU(warp_size=DEFAULT_WARP_SIZE)
    gpu_a.run_kernel(kernel_relu(x, y1), n_threads=n)
    hr()
    print(f"branchless (max):     {gpu_a.parallel_steps} Schritte, "
          f"Divergenz-Zusatz: {gpu_a.divergent_steps}")

    # (b) explizit divergenter Kernel: if/else
    y2 = [0.0] * n
    gpu_b = SIMT_GPU(warp_size=DEFAULT_WARP_SIZE)
    gpu_b.run_kernel(kernel_relu_divergent(x, y2), n_threads=n)
    hr()
    print(f"divergent (if/else):  {gpu_b.parallel_steps} Schritte, "
          f"Divergenz-Zusatz: {gpu_b.divergent_steps}")

    print()
    print("Beobachtung: der divergent-Kernel braucht mehr Schritte, weil die")
    print("Warp beide Zweige nacheinander ausfuehrt. Genau das ist der Grund,")
    print("warum GPU-optimierter Code Verzweigungen wo moeglich vermeidet")
    print("(oder so anlegt, dass die ganze Warp denselben Zweig nimmt).")

    assert y1 == y2, "Ergebnisse muessen identisch sein!"


def run_dot_reduction():
    print("\n=== 3) Skalarprodukt: Baum-Reduktion in log2(n) Schritten ===")
    # n muss Zweier-Potenz und <= warp_size sein fuer diese einfache Reduktion
    n = 8
    a = [1.0] * n
    b = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    expected = sum(x * y for x, y in zip(a, b))  # = 36.0

    # ---- CPU (seriell)
    cpu_sum = 0.0
    cpu_steps = 0
    for i in range(n):
        cpu_sum += a[i] * b[i]  # eine MUL-ADD-Op pro Element
        cpu_steps += 1
    hr()
    print(f"CPU seriell:  n={n} -> {cpu_steps} Instruktionen "
          f"(Ergebnis: {cpu_sum})")

    # ---- GPU (SIMT, Baum-Reduktion)
    out = [0.0]
    gpu = SIMT_GPU(warp_size=DEFAULT_WARP_SIZE)
    gpu.run_kernel(kernel_dot_reduce(a, b, out), n_threads=n)
    log_steps = int(math.log2(n))
    hr()
    print(f"GPU SIMT:     n={n}, warp_size={gpu.warp_size} "
          f"-> {gpu.parallel_steps} warp-parallele Instruktionen "
          f"(Ergebnis: {out[0]})")
    print(f"              (theoretisch: 1 Produkt + log2({n})={log_steps} "
          f"Reduktions-Schritte + 1 Write = {log_steps + 2})")

    assert abs(out[0] - expected) < 1e-9, f"Falsches Ergebnis: {out[0]} vs {expected}"


def main():
    print("=" * 72)
    print("SIMT-Simulator: CPU-seriell vs. GPU-parallel")
    print(f"(warp_size = {DEFAULT_WARP_SIZE} - NVIDIA verwendet real 32)")
    print("=" * 72)

    run_vector_add()
    run_relu_divergence()
    run_dot_reduction()

    print("\n" + "=" * 72)
    print("KERN-BEOBACHTUNG:")
    print("  Die GPU rechnet nichts anderes als die CPU.")
    print("  Sie rechnet DASSELBE in weniger Schritten, weil Threads einer")
    print("  Warp warp-parallel dieselbe Instruktion auf verschiedenen Daten")
    print("  ausfuehren. Beschleunigung fast linear in der Warp-Groesse -")
    print("  ausser bei Divergenz (Warp-weite if-Aeste), wo beide Pfade")
    print("  nacheinander laufen muessen.")


if __name__ == "__main__":
    main()