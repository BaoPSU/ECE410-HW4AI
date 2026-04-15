# GEMM Analysis — Naive vs. Tiled CUDA Kernels

**GPU:** NVIDIA GeForce RTX 3050 Ti Laptop GPU  
**Peak FP32:** 8,680 GFLOP/s | **Peak memory bandwidth:** 192 GB/s | **Ridge point:** ~45 FLOP/byte

## Measured Results

| Kernel       | Time (ms) | GFLOP/s | Arith. Intensity (FLOP/byte) | Bound  |
|--------------|-----------|---------|------------------------------|--------|
| gemm_naive   | 6.600     | 325.4   | 0.250                        | Memory |
| gemm_tiled T=8 | 6.446   | 333.1   | 30.12                        | Memory |

## (a) Why the Naive Kernel Is Memory-Bound

The naive kernel assigns one thread per output element `C[i][j]` and streams through all `N` elements of a row of A and a column of B with no data reuse between threads. Each of the N² output elements independently fetches N floats from A and N floats from B directly from DRAM. For N=1024 this amounts to roughly 8 GB of DRAM reads, yielding an arithmetic intensity of only 0.25 FLOP/byte — far below the ridge point of ~45 FLOP/byte on this GPU. At that intensity the roofline ceiling is `0.25 × 192 = 48 GFLOP/s`, but the observed 325 GFLOP/s suggests the L2 cache is absorbing significant reuse across the wavefronts, partially masking the naive access pattern.

## (b) How Tiling Reduces DRAM Traffic

The tiled kernel partitions A and B into T×T tiles (T=8) that are loaded cooperatively into shared memory. Each tile is loaded once from DRAM and reused T times across the inner accumulation loop, reducing the total DRAM reads by a factor of T (8×). Across the full N×N computation there are (N/T)² tile pairs, and each pair loads T² elements from both A and B — giving a traffic reduction of N/T = 128× compared to the naive case and an arithmetic intensity of ~30 FLOP/byte.

## (c) Whether the Tiled Kernel Achieved the Expected Improvement

The tiled kernel improved only marginally over naive (333 vs. 325 GFLOP/s, ~2.4%), which is far short of the theoretical 128× traffic reduction. Two bottlenecks explain this. First, T=8 gives thread blocks of only 64 threads (8×8), resulting in low occupancy on Ampere — the SM can host many more resident warps, so latency cannot be fully hidden by warp switching. Second, at N=1024 the working set for the naive kernel (two 4 MB matrices) largely fits in the L2 cache (2 MB last-level), meaning repeated column accesses to B are partially served from cache rather than DRAM, narrowing the advantage of explicit tiling. Both kernels remain memory-bound and sit well below the compute ceiling; increasing T to 16 or 32 would significantly raise occupancy and arithmetic intensity, pushing the tiled kernel closer to the ridge point.
