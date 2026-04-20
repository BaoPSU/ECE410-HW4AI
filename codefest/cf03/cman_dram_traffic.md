# DRAM Traffic Analysis
N=32, FP32=4B, T=8

---

**(a) Naive DRAM Traffic**

In the naive triple loop, each element of A is accessed N times (once per output column j),
and each element of B is accessed N times (once per output row i). Every access goes to DRAM.

Traffic = 2N^3 × 4 = 2 × 32768 × 4 = **262,144 bytes**

---

**(b) Tiled DRAM Traffic**

With tiling (T=8), each T×T tile of A and B is loaded exactly once across the full computation.
Total unique elements in A and B = 2N², each loaded once.

Traffic = 2N^2 × 4 = 2 × 1024 × 4 = **8,192 bytes**

---

**(c) Traffic Ratio**

2N^3 / 2N^2 = **N = 32**

Tiling allows each element of A and B to be loaded from DRAM exactly once and reused N times
within shared memory, eliminating the N-fold redundancy of the naive case.

---

**(d) Execution Time**

FLOPs = 2N^3 = 65,536

Naive:
- t_mem = 262,144 / 320e9 = **0.820 μs** ← bottleneck
- t_compute = 65,536 / 10e12 = **0.00655 μs**
- → memory-bound (mem is 125× slower)

Tiled:
- t_mem = 8,192 / 320e9 = **0.0256 μs** ← bottleneck
- t_compute = 65,536 / 10e12 = **0.00655 μs**
- → memory-bound (mem is 3.9× slower), but much closer to ridge point
- Note: tiling reduced the memory gap from ~125× to ~4×; to become compute-bound would
  require larger N (higher AI) or higher memory bandwidth.
