# HW/SW Partition Proposal — K-Means Clustering
Bao Nguyen  
ECE 410/510 Spring 2026

---

## (a) Which kernel(s) to accelerate in hardware and why

The kernel selected for hardware acceleration is the **pairwise distance computation** in K-Means:

```python
distances = np.sum((points[:, np.newaxis] - centroids) ** 2, axis=2)
```

The `cProfile` output identifies this as the dominant bottleneck — `numpy.ufunc.reduce` accounts for **5.57 seconds out of 39.3 seconds total** across 10 runs (N=50,000, D=64, K=8). It is called every iteration and scales as O(N × K × D), making it the clear compute target.

The roofline analysis supports this choice. With an arithmetic intensity of **2.67 FLOP/byte**, the kernel sits deep in the memory-bound region on the i9-12900H (ridge point = 9.11 FLOP/byte). The attainable performance ceiling is only ~205 GFLOP/s, far below peak compute. A near-memory accelerator with HBM3-class bandwidth (4 TB/s) shifts the ridge point to 2.5 FLOP/byte, placing the kernel just above the ridge point and making it **compute-bound** — meaning the accelerator can reach near-peak throughput for this kernel.

## (b) What the software baseline will continue to handle

The software baseline on the CPU will handle: centroid initialization, the convergence check (`np.allclose`), centroid update (`mean` per cluster), and overall loop control. These operations are infrequent or operate on small data (K × D centroid arrays), so accelerating them would yield negligible benefit.

## (c) Interface bandwidth required

Per iteration, the kernel transfers approximately **28.8 MB** of data. At a target accelerator throughput of 10 TFLOP/s, one distance computation completes in:

```
time = FLOPs / throughput = 76,800,000 / (10 × 10^12) ≈ 7.7 μs
```

Required interface bandwidth to avoid becoming interface-bound:

```
BW_needed = 28,804,096 bytes / 7.7 μs ≈ 3.74 TB/s
```

This confirms the accelerator needs **≥ 3.74 TB/s** of memory bandwidth — consistent with the HBM3 target of 4 TB/s in the design. Standard PCIe (64 GB/s) would be a severe bottleneck; HBM or on-chip SRAM with DMA is required.

## (d) Bound classification and expected change with accelerator

On the i9-12900H, the distance kernel is **memory-bound** (AI = 2.67 < ridge 9.11). The CPU cannot feed data fast enough to keep compute units busy.

On the hypothetical HBM3 accelerator (10 TFLOP/s, 4 TB/s), the ridge point drops to 2.5 FLOP/byte. Since AI = 2.67 > 2.5, the kernel becomes **compute-bound** on the accelerator. This is the key advantage: by pairing high-bandwidth memory with dedicated MAC units, the accelerator eliminates the memory bottleneck and allows the distance computation to run at near-peak arithmetic throughput — a fundamental shift in the performance limiting factor.
