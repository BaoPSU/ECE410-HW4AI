# GEMM Analysis — Naive vs. Tiled CUDA Kernels

**GPU:** NVIDIA GeForce RTX 3050 Ti Laptop GPU  
**Peak FP32:** 8,680 GFLOP/s | **Peak memory bandwidth:** 192 GB/s | **Ridge point:** ~45 FLOP/byte

## Measured Results

| Kernel       | Time (ms) | GFLOP/s | Arith. Intensity (FLOP/byte) | Bound   |
|--------------|-----------|---------|------------------------------|---------|
| gemm_naive   | 6.613     | 324.7   | 0.250                        | Memory  |
| gemm_tiled T=8 | 6.452   | 332.8   | 256.0                        | Compute |

## (a) Why the Naive Kernel Is Memory-Bound

The naive kernel assigns one thread per output element `C[i][j]` and streams through all `N` elements of a row of A and a column of B with no data reuse between threads. Each of the N² output elements independently fetches N floats from A and N floats from B directly from DRAM. For N=1024 this amounts to roughly 8 GB of DRAM reads, yielding an arithmetic intensity of only 0.25 FLOP/byte — far below the ridge point of ~45 FLOP/byte on this GPU. At that intensity the roofline ceiling is `0.25 × 192 = 48 GFLOP/s`, but the observed 325 GFLOP/s suggests the L2 cache is absorbing significant reuse across the wavefronts, partially masking the naive access pattern.

## (b) How Tiling Reduces DRAM Traffic

The tiled kernel partitions A and B into T×T tiles (T=8) loaded cooperatively into shared memory. Each element of A and B is loaded from DRAM exactly once across the full computation, giving total DRAM traffic of 2N²×4 = 8 MB vs. the naive 2N³×4 = 8 GB — a reduction of N = 1024×. This pushes the theoretical arithmetic intensity from 0.25 to N/4 = 256 FLOP/byte, well past the ridge point of 45.2 FLOP/byte, making the tiled kernel theoretically compute-bound.

## (c) Whether the Tiled Kernel Achieved the Expected Improvement

The tiled kernel improved only marginally over naive (333 vs. 325 GFLOP/s, ~2.4%), far short of the theoretical N=1024× traffic reduction. Despite being theoretically compute-bound (AI=256 >> ridge=45.2), the kernel is nowhere near the 8,680 GFLOP/s compute ceiling. Two bottlenecks explain this. First, T=8 gives thread blocks of only 64 threads (8×8), resulting in very low occupancy on Ampere — too few warps per SM to hide arithmetic latency through warp switching. Second, the naive kernel's working set (two 4 MB matrices) is partially served by the 4 MB L2 cache, meaning its effective DRAM traffic is lower than the theoretical worst case, narrowing the gap between the two kernels. Increasing T to 16 or 32 would raise both occupancy and tile reuse, allowing the tiled kernel to approach the compute ceiling.
