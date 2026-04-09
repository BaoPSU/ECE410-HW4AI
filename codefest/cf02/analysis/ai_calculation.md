# Arithmetic Intensity Calculation — Dominant Kernel
Bao Nguyen  
ECE 410/510 Spring 2026

---

## Project Algorithm

**K-Means Image Color Quantization** — given an input image, treat each pixel's RGB values as a point in 3D space and cluster pixels into K groups. Every pixel is replaced with its cluster's centroid color, producing a simplified image with only K distinct colors.

---

## Dominant Kernel Identified

From `cProfile` output (`project_profile.txt`), profiling 10 runs on `bliss.jpg` resized to 800×600:
- N = 480,000 pixels, D = 3 (RGB), K = 16 colors, max_iters = 20

The dominant kernel is the **pairwise distance computation**:

```python
distances = np.sum((points[:, np.newaxis] - centroids) ** 2, axis=2)
```

This maps to `numpy.ufunc.reduce` in the profiler:
- **42.53s out of 91.96s total = 46% of runtime**
- Called 7,210 times (once per dimension reduction per iteration per run)

---

## FLOPs Calculation (per iteration)

| Operation | Formula | Count |
|-----------|---------|-------|
| Subtract `(pixel - centroid)` | N × K × D | 480,000 × 16 × 3 = 23,040,000 |
| Square `(·)²` | N × K × D | 23,040,000 |
| Sum over D | N × K × (D−1) | 480,000 × 16 × 2 = 15,360,000 |
| **Total FLOPs per iteration** | | **61,440,000** |

---

## Bytes Transferred (No Reuse, per iteration)

Pixels stored as float32 (4 bytes):

| Operand | Shape | Elements | Bytes |
|---------|-------|----------|-------|
| Read pixels | N × D | 1,440,000 | 5,760,000 |
| Read centroids | K × D | 48 | 192 |
| Write distances | N × K | 7,680,000 | 30,720,000 |
| **Total** | | | **36,480,192 bytes** |

---

## Arithmetic Intensity

```
AI = FLOPs / Bytes
   = 61,440,000 / 36,480,192
   ≈ 1.68 FLOP/byte
```

---

## Bound Classification

Hardware: Intel Core i9-12900H (FP32)  
- Peak FP32 compute: ~1,400 GFLOP/s (AVX2 FMA, all cores — source: Intel ARK, ark.intel.com/content/www/us/en/ark/products/226953)
- Peak DRAM bandwidth: ~76.8 GB/s (DDR5-4800, dual channel — source: JEDEC JESD79-5 spec)
- Ridge point: 1,400 / 76.8 ≈ **18.23 FLOP/byte**

Since **AI (1.68) << Ridge point (18.23)**, the dominant kernel is **deeply memory-bound** on this hardware.

Attainable performance ceiling = B_peak × AI = 76.8 × 1.68 ≈ **129 GFLOP/s**

The low arithmetic intensity (D=3 means very little math per pixel loaded) is a fundamental property of image K-Means — each pixel needs 3 subtractions, 3 multiplications, and 2 additions per centroid, but requires loading the full pixel and writing a full distance value.
