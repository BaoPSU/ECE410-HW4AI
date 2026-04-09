# HW/SW Partition Proposal — K-Means Image Color Quantization
Bao Nguyen  
ECE 410/510 Spring 2026

---

## (a) Which kernel(s) to accelerate in hardware and why

The kernel selected for hardware acceleration is the **pairwise distance computation** in K-Means:

```python
distances = np.sum((points[:, np.newaxis] - centroids) ** 2, axis=2)
```

The `cProfile` output on a real image (bliss.jpg, 800×600, N=480,000 pixels, D=3 RGB, K=16) identifies this as the dominant bottleneck — `numpy.ufunc.reduce` accounts for **42.53 seconds out of 91.96 seconds total (46% of runtime)** across 10 runs.

The roofline analysis strongly supports hardware acceleration. The arithmetic intensity is only **1.68 FLOP/byte** — the kernel sits deep in the memory-bound region on the i9-12900H (ridge point = 18.23 FLOP/byte). The attainable ceiling on the CPU is just ~129 GFLOP/s, barely 9% of peak compute. A near-memory Processing-In-Memory (PIM) accelerator with 16 TB/s bandwidth shifts the ridge point to 0.5 FLOP/byte, placing the kernel in the compute-bound region and allowing near-peak 8 TFLOP/s throughput.

## (b) What the software baseline will continue to handle

The CPU software baseline will handle: image loading and resizing, centroid initialization, the convergence check, centroid update (averaging pixels per cluster), and final pixel replacement to reconstruct the output image. These operations are either small (K × D centroid data) or not compute-intensive, and offloading them would yield negligible benefit.

## (c) Interface bandwidth required

Per iteration, the distance kernel transfers approximately **36.5 MB** of data. At a target accelerator throughput of 8 TFLOP/s, one distance computation completes in:

```
time = FLOPs / throughput = 61,440,000 / (8 × 10^12) ≈ 7.7 ns
```

Required interface bandwidth to avoid becoming interface-bound:

```
BW_needed = 36,480,192 bytes / 7.7 ns ≈ 4.7 TB/s
```

This confirms the accelerator needs at least **~5 TB/s of memory bandwidth**. The proposed 16 TB/s design provides comfortable headroom. Standard LPDDR5 (~68 GB/s) or PCIe 5.0 (~128 GB/s) would be completely inadequate — only HBM or on-die SRAM can sustain this bandwidth.

## (d) Bound classification and expected change with accelerator

On the i9-12900H, the kernel is **deeply memory-bound** (AI = 1.68 << ridge 18.23). The CPU's 76.8 GB/s DRAM bandwidth cannot feed the compute units fast enough — they sit idle >90% of the time.

On the hypothetical PIM accelerator (8 TFLOP/s, 16 TB/s), the ridge point drops to 0.5 FLOP/byte. Since AI = 1.68 > 0.5, the kernel becomes **compute-bound** on the accelerator. This is the fundamental advantage of near-memory processing for K-Means: by co-locating compute with memory, the data movement bottleneck is eliminated and arithmetic throughput becomes the limiting factor — improving attainable performance by roughly 62× (from ~129 GFLOP/s to ~8,000 GFLOP/s).
