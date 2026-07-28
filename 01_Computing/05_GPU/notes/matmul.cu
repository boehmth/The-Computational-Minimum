/*
 * matmul.cu - Tiled Matrix Multiplication in echtem CUDA-C
 * ========================================================
 *
 * Diese Datei wird NICHT kompiliert; sie steht hier als Brücke zwischen
 * unserem Python-SIMT-Simulator (gpu_sim.py, matmul_compare.py) und dem,
 * was auf einer echten NVIDIA-GPU tatsächlich passiert. Wer den Simulator
 * verstanden hat, versteht auch diese ~50 Zeilen echten CUDA-Code -
 * bis auf ein paar Syntax-Details.
 *
 * Kompilieren (auf einem System mit NVIDIA-Toolchain):
 *
 *     nvcc -O3 -o matmul matmul.cu
 *
 * Zeile-fuer-Zeile-Kommentare zeigen die Parallelen zu unserem Simulator.
 */

#include <cuda_runtime.h>
#include <cstdio>


// ---------------------------------------------------------------------
// Der Kernel: laeuft auf der GPU
// ---------------------------------------------------------------------
// `__global__` bedeutet: aufgerufen von der CPU, ausgefuehrt auf der GPU.
// Jede Aufruf-Instanz wird von einem Grid von Thread-Bloecken abgearbeitet;
// jeder Block enthaelt viele Threads (typisch 256 oder 512).
//
// Vergleich mit gpu_sim.py:
//   - blockIdx.{x,y}    <-> welchen Ausgabe-Block wir gerade berechnen
//   - threadIdx.{x,y}   <-> welcher Thread innerhalb des Blocks
//   - __shared__ Arrays <-> unser "Shared Memory" (im Simulator: normale
//                          Python-Variablen, die alle Threads sehen)
//   - __syncthreads()   <-> unser warp.step() zwischen zwei Phasen
//
// Der Kernel setzt sich exakt aus den fuenf Phasen zusammen, die wir im
// Simulator zaehlen:
//     1. A-Kachel in Shared Memory laden
//     2. B-Kachel in Shared Memory laden
//     3. K-Schleife: block_size MUL-ADD-Operationen pro Thread
//     4. (fuer jedes weitere K-Tile: zurueck zu 1)
//     5. Ergebnis nach C schreiben

#define BLOCK_SIZE 16   // Kachelgroesse; muss zur Grid-Konfiguration passen

__global__ void matmul_tiled(
    const float* __restrict__ A,
    const float* __restrict__ B,
    float* __restrict__ C,
    int n)
{
    // Shared Memory - fuer alle Threads in DIESEM Block sichtbar.
    // In gpu_sim.py entsprechen diese Arrays einer Zwischenspeicher-Liste,
    // die alle Threads einer Warp gemeinsam benutzen.
    __shared__ float As[BLOCK_SIZE][BLOCK_SIZE];
    __shared__ float Bs[BLOCK_SIZE][BLOCK_SIZE];

    // Globale Position dieses Threads in der Ausgabematrix C.
    int row = blockIdx.y * BLOCK_SIZE + threadIdx.y;
    int col = blockIdx.x * BLOCK_SIZE + threadIdx.x;

    float acc = 0.0f;

    // Ueber alle K-Tiles iterieren
    int n_tiles = n / BLOCK_SIZE;
    for (int t = 0; t < n_tiles; ++t) {

        // Phase 1: A-Kachel laden (jeder Thread laedt ein Element)
        As[threadIdx.y][threadIdx.x] = A[row * n + (t * BLOCK_SIZE + threadIdx.x)];
        // Phase 2: B-Kachel laden
        Bs[threadIdx.y][threadIdx.x] = B[(t * BLOCK_SIZE + threadIdx.y) * n + col];

        // Warte, bis ALLE Threads in diesem Block ihre Kachel geladen haben.
        // Ohne diese Barriere wuerde manch ein Thread schon rechnen, waehrend
        // die andere Kachel noch nicht komplett gelesen ist.
        __syncthreads();

        // Phase 3: die eigentliche Rechnung - BLOCK_SIZE MUL-ADDs pro Thread.
        // Alle Threads eines Warps machen diese Operationen synchron
        // (SIMT), nur auf ihren jeweiligen Zeilen/Spalten.
        for (int k = 0; k < BLOCK_SIZE; ++k) {
            acc += As[threadIdx.y][k] * Bs[k][threadIdx.x];
        }

        // Warte, bis ALLE Threads fertig gerechnet haben - dann darf die
        // naechste Kachel die Shared-Memory-Slots ueberschreiben.
        __syncthreads();
    }

    // Phase 5: Ergebnis in globalen Speicher schreiben.
    if (row < n && col < n) {
        C[row * n + col] = acc;
    }
}


// ---------------------------------------------------------------------
// Host-Code (laeuft auf der CPU): allokiert Speicher, kopiert Daten,
// startet den Kernel, holt das Ergebnis zurueck.
// ---------------------------------------------------------------------

int main() {
    const int n = 512;              // Matrix-Groesse
    const size_t bytes = n * n * sizeof(float);

    // Host-Speicher
    float* h_A = (float*)malloc(bytes);
    float* h_B = (float*)malloc(bytes);
    float* h_C = (float*)malloc(bytes);
    for (int i = 0; i < n * n; ++i) {
        h_A[i] = (float)(i % 5);
        h_B[i] = (float)((i * 3) % 4);
    }

    // Device-Speicher (auf der GPU)
    float *d_A, *d_B, *d_C;
    cudaMalloc(&d_A, bytes);
    cudaMalloc(&d_B, bytes);
    cudaMalloc(&d_C, bytes);

    // Daten von CPU nach GPU kopieren
    cudaMemcpy(d_A, h_A, bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, h_B, bytes, cudaMemcpyHostToDevice);

    // Grid- und Block-Konfiguration:
    //   Jeder Thread berechnet EINE Ausgabezelle.
    //   Jeder Block hat BLOCK_SIZE * BLOCK_SIZE Threads.
    //   Wir brauchen n/BLOCK_SIZE Bloecke in jeder Dimension.
    dim3 block(BLOCK_SIZE, BLOCK_SIZE);
    dim3 grid(n / BLOCK_SIZE, n / BLOCK_SIZE);

    // Kernel starten. Alle grid.x * grid.y Bloecke laufen SIMD-parallel
    // auf den SMs der GPU (Streaming Multiprocessors).
    matmul_tiled<<<grid, block>>>(d_A, d_B, d_C, n);

    // Ergebnis zurueck auf die CPU
    cudaMemcpy(h_C, d_C, bytes, cudaMemcpyDeviceToHost);

    printf("C[0][0] = %f\n", h_C[0]);

    // Aufraeumen
    cudaFree(d_A); cudaFree(d_B); cudaFree(d_C);
    free(h_A); free(h_B); free(h_C);
    return 0;
}


// ---------------------------------------------------------------------
// Beobachtungen fuer den Vergleich Simulator vs. echte GPU
// ---------------------------------------------------------------------
//
// 1. Unser Simulator (gpu_sim.py) zaehlt Instruktions-Schritte. Eine
//    echte GPU wandelt diese Schritte in Nanosekunden um. Die
//    Groessenordnung des Speed-ups aendert sich dabei nicht: was hier
//    5 Instruktionen sind, sind dort 5 * (Zykluszeit + Speicherlatenz).
//
// 2. Die __syncthreads()-Barrieren sind in unserem Simulator nicht
//    explizit modelliert - dort sind sie implizit, weil die Warp
//    ohnehin im Gleichschritt laeuft. Auf echter Hardware sind sie
//    entscheidend fuer die Korrektheit: ohne sie wuerde Thread A schon
//    aus einer Speicherstelle lesen, in die Thread B noch nicht
//    geschrieben hat.
//
// 3. Die Shared-Memory-Groesse (48 kB pro SM auf typischen GPUs)
//    begrenzt, wie gross BLOCK_SIZE sein kann. Bei BLOCK_SIZE=16 und
//    zwei Kacheln benoetigen wir 2 * 16 * 16 * 4 Byte = 2 kB - passt
//    locker. Bei BLOCK_SIZE=32 waeren es 8 kB - immer noch OK.
//
// 4. Ueber grid.x * grid.y = (n/BLOCK_SIZE)^2 Bloecke werden gleichzeitig
//    ausgefuehrt. Bei n=512 und BLOCK_SIZE=16 sind das 1024 Bloecke.
//    Eine moderne GPU hat ~100 SMs und kann pro SM mehrere Bloecke
//    gleichzeitig halten - typisch 8-16. Damit sind hunderte bis
//    tausende von Bloecken *echt* parallel unterwegs.
//
// Diese vier Beobachtungen sind der Grund, warum in matmul_compare.py
// der reine Blocktimings-Vergleich schon eine gute Naeherung ist:
// die Wall-Clock-Zeit einer GPU-MatMul ist im Wesentlichen die Zeit
// EINES Blocks, weil alle anderen Bloecke parallel liefen.