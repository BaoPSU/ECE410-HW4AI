# DRAM Traffic Analysis
N=32, FP32=4B, T=8

---

**(a) Naive DRAM Traffic**

Each element of A and B is accessed N=32 times (B once per i, A once per j).

Traffic = (2N^3 + N^2) x 4 = (65536 + 1024) x 4 = **266,240 bytes**

---

**(b) Tiled DRAM Traffic**

Each tile is loaded once per k-tile sweep, so reads drop by factor of T.

Traffic = (2N^3/T + N^2) x 4 = (8192 + 1024) x 4 = **36,864 bytes**

---

**(c) Traffic Ratio**

2N^3 / (2N^3/T) = T = **8**

Each element is reused T times within a tile, so DRAM fetches drop by a factor of T.

---

**(d) Execution Time**

FLOPs = 2N³ = 65,536

Naive:
- t_mem = 266,240 / 320e9 = **0.832 μs** ← bottleneck
- t_compute = 65,536 / 10e12 = **0.00655 μs**
- → memory-bound (mem is 127× slower)

Tiled:
- t_mem = 36,864 / 320e9 = **0.115 μs** ← bottleneck
- t_compute = 65,536 / 10e12 = **0.00655 μs**
- → memory-bound (mem is 17.6× slower)
