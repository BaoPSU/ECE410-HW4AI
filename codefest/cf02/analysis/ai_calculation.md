# Arithmetic Intensity Calculation — Dominant Kernel
Bao Nguyen  
ECE 410/510 Spring 2026

---

## Dominant Kernel Identified

From `cProfile` output (`project_profile.txt`), profiling 10 runs of K-Means on:
- N = 50,000 points, D = 64 dimensions, K = 8 clusters, max_iters = 20

The dominant kernel is the **pairwise distance computation**:

```python
distances = np.sum((points[:, np.newaxis] - centroids) ** 2, axis=2)
```

This maps to `numpy.ufunc.reduce` in the profiler, accounting for **5.57s out of 39.3s total** (~14% of runtime), and is called 200 times (20 iterations × 10 runs). The outer `kmeans` function self-time (33.15s) is entirely driven by this loop.

---

## FLOPs Calculation (per iteration)

The distance computation performs three operations per element:

| Operation | Formula | Count |
|-----------|---------|-------|
| Subtract `(points - centroid)` | N × K × D | 50,000 × 8 × 64 = 25,600,000 |
| Square `(·)²` | N × K × D | 25,600,000 |
| Sum over D | N × K × (D−1) ≈ N × K × D | 25,600,000 |
| **Total FLOPs per iteration** | | **76,800,000** |

---

## Bytes Transferred (No Reuse, per iteration)

All operands assumed loaded fresh from DRAM (float64 = 8 bytes):

| Operand | Shape | Elements | Bytes |
|---------|-------|----------|-------|
| Read points | N × D | 3,200,000 | 25,600,000 |
| Read centroids | K × D | 512 | 4,096 |
| Write distances | N × K | 400,000 | 3,200,000 |
| **Total** | | | **28,804,096 bytes** |

---

## Arithmetic Intensity

```
AI = FLOPs / Bytes
   = 76,800,000 / 28,804,096
   ≈ 2.67 FLOP/byte
```

---

## Bound Classification

Hardware: Intel Core i9-12900H  
- Peak FP64 compute: ~700 GFLOP/s (AVX2 FMA, all cores)
- Peak DRAM bandwidth: ~76.8 GB/s (DDR5-4800, dual channel)
- Ridge point: 700 / 76.8 ≈ **9.11 FLOP/byte**

Since **AI (2.67) < Ridge point (9.11)**, the dominant kernel is **memory-bound** on this hardware.

Attainable performance ceiling = B_peak × AI = 76.8 × 2.67 ≈ **205 GFLOP/s**
