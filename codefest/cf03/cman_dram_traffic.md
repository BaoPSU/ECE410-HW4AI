# DRAM Traffic Analysis — N=32, FP32 (4 B/elem), T=8

---

## (a) Naive DRAM Traffic

Each element of B is accessed **N = 32 times** (once per i-loop iteration).  
Each element of A is accessed **N = 32 times** (once per j-loop iteration).

```
Traffic = (2·N³ + N²) × 4
        = (2·32768 + 1024) × 4
        = 66,560 × 4
        = 266,240 bytes
```

---

## (b) Tiled DRAM Traffic

Each T×T tile is loaded once per k-tile sweep instead of N times.

```
Traffic = (2·N³/T + N²) × 4
        = (2·32768/8 + 1024) × 4
        = (8192 + 1024) × 4
        = 9,216 × 4
        = 36,864 bytes
```

---

## (c) Traffic Ratio

```
Ratio = 2·N³ / (2·N³/T) = T = 8
```

Tiling reduces DRAM traffic by **T = 8** because each element is reused T times within a shared-memory tile, replacing T separate DRAM fetches with a single tile load.

---

## (d) Execution Time

```
FLOPs        = 2·N³ = 65,536

Naive:
  t_mem      = 266,240 / 320e9  = 0.832 μs   ← bottleneck
  t_compute  =  65,536 / 10e12  = 0.00655 μs
  → MEMORY-BOUND (mem is 127× slower)

Tiled:
  t_mem      =  36,864 / 320e9  = 0.115 μs   ← bottleneck
  t_compute  =  65,536 / 10e12  = 0.00655 μs
  → MEMORY-BOUND (mem is 17.6× slower)
```
