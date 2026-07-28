"""
gpu_sim.py - Ein Software-SIMT-Simulator (Kap. 5, Teil 1)

DIDAKTISCHE POINTE DIESES KAPITELS
==================================

Eine GPU besteht - fuer unsere Zwecke - aus drei Ideen:

    1. VIELE Threads laufen gleichzeitig ("massiv parallel").
    2. Die Threads sind in Gruppen (Warps, typisch 32 Threads) organisiert;
       innerhalb einer Warp fuehren alle Threads dieselbe Instruktion aus,
       nur auf verschiedenen Daten. Das nennt sich SIMT
       (Single Instruction, Multiple Threads).
    3. Verzweigungen innerhalb einer Warp (Warp Divergence) sind teuer:
       beide Pfade werden nacheinander abgearbeitet, waehrend die Threads
       auf dem "falschen" Pfad einfach nichts tun.

Dieser Simulator fuehrt Kernels tatsaechlich in Python aus (also seriell),
aber er ZAEHLT die Instruktions-Schritte so, als ob die Threads parallel
liefen. Genau dieses Zaehlen erlaubt es uns, den Unterschied zwischen
einer seriellen CPU-Rechnung (n Schritte) und einer parallelen GPU-Rechnung
(n / warp_size Schritte) sichtbar zu machen.

API-Idee
========

Ein Kernel bekommt beim Aufruf eine `Warp`-Referenz und benutzt sie so:

    def add_kernel(warp):
        for tid in warp.lanes():         # Iteriere ueber die Threads dieser Warp
            i = tid                       # Thread-Arbeit auf eigenem Datum
            if i < N:
                C[i] = A[i] + B[i]
        warp.step()                       # Eine warp-weite Instruktion abgeschlossen

Der Kernel-Code kann normale Python-Kontrollstrukturen verwenden. Die
zentrale Regel: `warp.step()` markiert das Ende einer warp-parallelen
Instruktion und zaehlt sie im Simulator einmal (nicht pro Thread).

Fuer Verzweigungen bietet die Warp einen Helfer `warp.diverge(condition_fn)`,
der die Warp in zwei Zweige aufspaltet und BEIDE nacheinander ausfuehrt -
genau das Verhalten einer echten GPU bei Warp Divergence.

Keine externen Abhaengigkeiten - reines Python.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional


DEFAULT_WARP_SIZE = 8  # NVIDIA verwendet 32; wir waehlen 8 fuer lesbare Ausgaben.


class Warp:
    """
    Repraesentiert eine Warp waehrend der Ausfuehrung.

    - `lanes()` iteriert ueber die globalen Thread-IDs dieser Warp.
    - `step()` schliesst eine warp-parallele Instruktion ab.
    - `diverge(cond_fn, body_if, body_else)` fuehrt beide Zweige aus,
      wenn die Threads uneinig sind, und zaehlt dabei die Divergenz-
      Kosten korrekt.
    """

    def __init__(self, thread_ids: List[int], gpu: "SIMT_GPU"):
        self.thread_ids = thread_ids
        self.gpu = gpu

    def size(self) -> int:
        return len(self.thread_ids)

    def lanes(self) -> List[int]:
        return list(self.thread_ids)

    def step(self, cost: float = 1.0) -> None:
        """Eine warp-parallele Instruktion abgeschlossen."""
        self.gpu._parallel_steps += cost

    def diverge(
        self,
        cond_fn: Callable[[int], bool],
        body_if: Callable[[List[int]], None],
        body_else: Optional[Callable[[List[int]], None]] = None,
    ) -> None:
        """
        Fuehrt eine bedingte Verzweigung im SIMT-Sinne aus:
        - `cond_fn(tid) -> bool` entscheidet pro Thread.
        - Alle Threads mit cond=True laufen `body_if`; die anderen warten.
        - Dann laufen alle Threads mit cond=False `body_else`.
        - Wenn die ganze Warp sich einig ist, gibt es KEINE Divergenz-Kosten.
        - Wenn sie sich uneinig ist, zaehlt jeder Zweig SEINEN Schritt separat.
        """
        yes = [tid for tid in self.thread_ids if cond_fn(tid)]
        no  = [tid for tid in self.thread_ids if not cond_fn(tid)]

        divergent = (len(yes) > 0 and len(no) > 0)

        if len(yes) > 0:
            body_if(yes)
            self.step()
            if divergent:
                self.gpu._divergent_steps += 1

        if len(no) > 0 and body_else is not None:
            body_else(no)
            self.step()
            if divergent:
                self.gpu._divergent_steps += 1


class SIMT_GPU:
    """Ein Software-SIMT-Simulator. Fuehrt Kernels aus und zaehlt parallele Steps."""

    def __init__(self, warp_size: int = DEFAULT_WARP_SIZE):
        self.warp_size = warp_size
        self._parallel_steps = 0.0
        self._divergent_steps = 0
        self._serial_ops_baseline = 0  # zum Vergleich gegen eine CPU

    @property
    def parallel_steps(self) -> int:
        """Anzahl warp-paralleler Instruktionen (aufgerundet auf ganze Steps)."""
        # Kernel duerfen fractional cost angeben; typisch ist step() = 1.
        return int(round(self._parallel_steps))

    @property
    def divergent_steps(self) -> int:
        """Anzahl der Zusatz-Steps, die durch Warp Divergence entstanden."""
        return self._divergent_steps

    def reset(self) -> None:
        self._parallel_steps = 0.0
        self._divergent_steps = 0
        self._serial_ops_baseline = 0

    def note_serial_ops(self, n: int) -> None:
        """Notiert die 'Kosten' einer aequivalenten seriellen CPU-Rechnung."""
        self._serial_ops_baseline += n

    def serial_baseline(self) -> int:
        return self._serial_ops_baseline

    def run_kernel(
        self,
        kernel_fn: Callable[[Warp], None],
        n_threads: int,
    ) -> None:
        """
        Startet einen Kernel fuer `n_threads` Threads. Die Threads werden
        in Warps zu je `warp_size` gruppiert und die Warps sequentiell
        abgearbeitet (in der Simulation - auf einer echten GPU parallel).
        Der Kernel bekommt jeweils eine `Warp`-Referenz.
        """
        n_warps = (n_threads + self.warp_size - 1) // self.warp_size
        for w in range(n_warps):
            start = w * self.warp_size
            end = min(start + self.warp_size, n_threads)
            warp = Warp(list(range(start, end)), self)
            kernel_fn(warp)


# -------------------------------------------------------------------------
# Beispiel-Kernels
# -------------------------------------------------------------------------

def kernel_vector_add(a: List[float], b: List[float], c: List[float]):
    """
    Erzeugt einen Kernel fuer `c[i] = a[i] + b[i]`.

    In echtem CUDA:
        __global__ void add(const float* a, const float* b, float* c, int n) {
            int i = blockIdx.x * blockDim.x + threadIdx.x;
            if (i < n) c[i] = a[i] + b[i];
        }
    """
    n = len(a)

    def _kernel(warp: Warp) -> None:
        # Warp-weite Instruktion: lade a[i], lade b[i], addiere, schreibe c[i].
        # Wir modellieren das als eine einzige Instruktion (typische
        # Vereinfachung; auf echter Hardware waeren es mehrere Ops, aber
        # sie liefen alle warp-parallel).
        for tid in warp.lanes():
            if tid < n:
                c[tid] = a[tid] + b[tid]
        warp.step()

    return _kernel


def kernel_relu(x: List[float], y: List[float]):
    """
    Erzeugt einen Kernel fuer `y[i] = max(0, x[i])`. Ideal zum
    Vergleichen mit einem divergent-schreibenden Kernel.
    """
    n = len(x)

    def _kernel(warp: Warp) -> None:
        for tid in warp.lanes():
            if tid < n:
                y[tid] = x[tid] if x[tid] > 0 else 0.0
        warp.step()

    return _kernel


def kernel_relu_divergent(x: List[float], y: List[float]):
    """
    Gleiche Aufgabe wie `kernel_relu`, aber mit expliziter Verzweigung -
    Warp Divergence sichtbar.
    """
    n = len(x)

    def _kernel(warp: Warp) -> None:
        def body_positive(tids):
            for tid in tids:
                y[tid] = x[tid]
        def body_negative(tids):
            for tid in tids:
                y[tid] = 0.0

        warp.diverge(
            cond_fn=lambda tid: tid < n and x[tid] > 0,
            body_if=body_positive,
            body_else=body_negative,
        )

    return _kernel


def kernel_dot_reduce(a: List[float], b: List[float], out: List[float]):
    """
    Skalarprodukt via Parallel-Reduktion (Baum-Summe in log n Schritten).

    Ansatz: Wir kopieren zuerst die punktweisen Produkte in `partial`,
    dann summieren wir mit einem Halbierungsschema:
        stride = n/2, n/4, n/8, ...
    Pro Halbierung braucht die Warp einen Step. Das Ergebnis landet in
    `partial[0]` und wird schliesslich nach `out[0]` geschrieben.

    Auf einer echten GPU:
        __shared__ float partial[BLOCK];
        partial[tid] = a[tid] * b[tid];
        __syncthreads();
        for (stride = blockDim.x/2; stride > 0; stride >>= 1) {
            if (tid < stride) partial[tid] += partial[tid + stride];
            __syncthreads();
        }
        if (tid == 0) out[0] = partial[0];
    """
    n = len(a)
    partial: List[float] = [0.0] * n

    def _kernel(warp: Warp) -> None:
        # Instruktion 1: punktweises Produkt
        for tid in warp.lanes():
            if tid < n:
                partial[tid] = a[tid] * b[tid]
        warp.step()

        # Baum-Reduktion: stride halbiert sich, bis stride = 0.
        stride = n // 2
        while stride > 0:
            for tid in warp.lanes():
                if tid < stride:
                    partial[tid] += partial[tid + stride]
            warp.step()
            stride //= 2

        # Thread 0 schreibt das Ergebnis raus.
        for tid in warp.lanes():
            if tid == 0:
                out[0] = partial[0]
        warp.step()

    return _kernel
