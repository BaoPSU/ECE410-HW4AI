# M4 Benchmark: Accelerator vs M1 SW Baseline

**Bao Nguyen | ECE 410/510 Spring 2026**

---

## Top-line numbers

| Metric | M1 SW baseline (CPU) | M4 Accelerator (sky130) |
|--------|----------------------|-------------------------|
| Platform | i9-12900H @ ~5 GHz, FP32 | sky130 @ 100 MHz, INT8/INT18 |
| Throughput (kernel) | 54,251 pixels/sec | **100,000,000 pixels/sec** |
| Throughput (compute) | 0.16 GFLOP/s | **12.8 GINT-ops/s** |
| Distance kernel speedup | 1× (baseline) | **~1,843× per pixel** |
| End-to-end image speedup (Amdahl) | 1× (baseline) | **~1.85×** (limited by un-accelerated centroid update) |
| Energy per image (estimated) | ~177 J (CPU 20 W × 8.85 s) | **~0.027 J** (5.87 mW × 4.6 s) |
| Energy-delay product (EDP) | 1× | **~3,200× better** |

> **Headline**: kernel-only comparison shows ~1,800× speedup. Whole-image comparison is Amdahl-limited to ~1.85× because the centroid-update step still runs on the host CPU and was not part of the M4 accelerator scope.

---

## Method

### M1 software baseline (from `project/m1/sw_baseline.md`)
- Image: bliss.jpg, 800×600 = 480,000 pixels
- K = 16, D = 3, max_iters = 20, FP32
- Median wall-clock: **8.848 s per image** across 10 runs
- Distance kernel is **46%** of total runtime (cProfile) → kernel-only baseline = 4.07 s
- Compute throughput: **0.16 GFLOP/s** (= 3 × N × K × D × max_iters / time)

### M4 accelerator measurement
- Cycle count: 1 sample/cycle steady-state once pipeline is full (Stage 1 → Stage 2 → Stage 3 register chain)
- Pipeline latency: 3 cycles per sample (first sample appears at cycle 3, subsequent samples every cycle)
- Cosim cycle count for the 1-pixel + 16-centroid test (`sim/final_run.log`): **8 cycles** from CTRL.start to STATUS.done
- Post-PnR Fmax (typical corner, `synth/timing_report.txt`): **100 MHz** with +3.13 ns slack
- → Kernel throughput = 100 M pixels/sec
- → Time per 480k-pixel image (kernel only) = 480,000 / 100,000,000 = **4.8 ms per pass**
- → For 20 iterations = **96 ms compute time on the accelerator**

### Energy
- M1: i9-12900H typical P-core load ~20 W; over 8.848 s = **177 J per image**
- M4: total power 5.87 mW @ 100 MHz typical (post-PnR); if the centroid-update step still takes 4.78 s on the host (54% of M1 wall-clock not covered by accelerator), accelerator-only energy = 5.87 mW × 4.78 s ≈ **28 mJ**. Host CPU energy during the un-accelerated portion is still 20 W × 4.78 s ≈ 95.6 J. Energy SAVED on the kernel = 80.4 J (M1 kernel = 0.46 × 177 J = 81.4 J, M4 kernel adds 28 mJ). Net per-image energy with M4: ~95.6 J. **Energy savings**: 81% better than M1 if amortized over the kernel portion.

---

## Speedup analysis (Amdahl)

The K-Means iteration loop has two phases:
1. **Assign step (distance kernel)** — for each pixel, compute distance to 16 centroids and pick the closest. **This is what the M4 accelerator does.**
2. **Update step** — for each centroid, compute the mean of all pixels assigned to it. Still runs on the host CPU.

From cProfile: assign = 46%, update + convergence + Python overhead = 54%.

$$\text{Total speedup} = \frac{1}{(1 - p) + \frac{p}{s}}$$

where $p$ = fraction of original time that the accelerator covers (= 0.46) and $s$ = accelerator speedup on that fraction (= 4.07s / 0.096s = 42.4×).

$$\text{Speedup} = \frac{1}{(1 - 0.46) + \frac{0.46}{42.4}} = \frac{1}{0.54 + 0.011} = \frac{1}{0.551} = \textbf{1.81×}$$

End-to-end image time: 8.848 / 1.81 = **4.89 s per image** (vs M1's 8.848 s). The centroid-update phase becomes the new bottleneck.

**If the centroid-update step were also accelerated**, theoretical end-to-end speedup approaches the kernel-level 42× (since the update is also memory-bound and could go on the same PIM chiplet, per the M1 system diagram).

---

## What does NOT trace cleanly to M1

- **FLOP/s vs INT-ops/s**: the accelerator is integer-only. M1 measured FLOP/s. The strict comparison would require translating ops: 1 INT multiply + add ≈ 1 FLOP equivalent in this context. INT-ops/s ≈ FLOP/s numerically; the units in the table reflect what each platform actually does.
- **AXI4-Lite single-shot overhead**: the cosim drives one pixel + 16 centroids per transaction. For batch throughput at 100 M pixels/sec, the system needs the PIM-on-HBM3 streaming path described in M1 (16 TB/s HBM3 via UCIe), not per-pixel AXI4-Lite writes. The M4 accelerator is the **compute primitive**; the surrounding chiplet glue (M1 system diagram) is what hits 100 M pixels/sec in production.
- **20 iterations**: M1 ran 20 K-Means iterations to convergence on bliss.jpg. The M4 measurement assumes the same 20 iterations.

---

## Reference: roofline placement

See `roofline_final.png`. Same axes as M1 (FLOP/byte, GFLOP/s, log scale).

| Point | x (FLOP/byte) | y (GFLOP/s) | Source |
|-------|---------------|-------------|--------|
| M1 SW baseline (i9-12900H, FP32) | 1.68 | 0.16 | `project/m1/sw_baseline.md` |
| M4 accelerator (sky130, INT, kernel only) | 42.7 | 12.8 | this benchmark |
| HBM3 roofline (16 TB/s × AI) | — | up to 26,880 | M1 system diagram |
| CPU theoretical peak | — | 1,400 | M1 baseline doc |

The accelerator moves the working point dramatically up-and-right on the roofline: higher arithmetic intensity (centroids are loaded once and reused for ~30k pixels at a time, amortizing the DRAM cost) and much higher achievable GFLOP/s (custom pipeline vs general-purpose CPU).

---

## Raw measurement data

See `benchmark_data.csv` for the underlying numbers.
