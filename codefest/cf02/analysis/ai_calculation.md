# Arithmetic Intensity Calculation — Dominant Kernel
Bao Nguyen  
ECE 410/510 Spring 2026

---

## Dominant Kernel Identified

From `torch.profiler` output (`project_profile.txt`), the dominant kernel across 10 forward passes is:

**`aten::mkldnn_convolution` — Conv2d layer with:**
- Input shape: `[1, 512, 7, 7]`
- Weight shape: `[512, 512, 3, 3]`
- Output shape: `[1, 512, 7, 7]`
- Self CPU %: **19.13%** (highest of all ops)
- Total CPU time: ~114 ms across 10 runs

This corresponds to the 3×3 convolutions in **ResNet-18 layer4** (the final residual block stage).

---

## FLOPs Calculation

For a Conv2d layer, the FLOP formula (one multiply + one accumulate per MAC):

```
FLOPs = 2 × C_in × k_h × k_w × C_out × H_out × W_out
```

Substituting values (batch=1, C_in=512, k=3, C_out=512, H_out=W_out=7):

```
FLOPs = 2 × 512 × 3 × 3 × 512 × 7 × 7
      = 2 × 512 × 9 × 512 × 49
      = 2 × 115,605,504
      = 231,211,008 FLOPs
```

---

## Bytes Transferred (No Reuse)

Assuming all operands loaded fresh from DRAM (FP32 = 4 bytes each):

| Operand | Shape | Elements | Bytes |
|---------|-------|----------|-------|
| Input feature map | 1 × 512 × 7 × 7 | 25,088 | 100,352 |
| Weight tensor | 512 × 512 × 3 × 3 | 2,359,296 | 9,437,184 |
| Output feature map | 1 × 512 × 7 × 7 | 25,088 | 100,352 |
| **Total** | | | **9,637,888 bytes** |

---

## Arithmetic Intensity

```
AI = FLOPs / Bytes
   = 231,211,008 / 9,637,888
   ≈ 23.99 FLOP/byte
```

---

## Bound Classification

Hardware: Intel Core i9-12900H
- Peak FP32 compute: ~1,400 GFLOP/s (AVX2 FMA, all cores)
- Peak DRAM bandwidth: ~76.8 GB/s (DDR5-4800, dual channel)
- Ridge point: 1,400 / 76.8 ≈ **18.23 FLOP/byte**

Since **AI (23.99) > Ridge point (18.23)**, the dominant kernel is **compute-bound** on this hardware.

Attainable performance ceiling = P_peak = **1,400 GFLOP/s**
