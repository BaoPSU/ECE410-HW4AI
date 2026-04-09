# Heilmeier Questions
Bao Nguyen  
ECE 410/510 Spring 2026

---

## 1. What are you trying to do?

I am building a K-Means image color quantization system and analyzing its hardware performance characteristics to understand what limits its speed and how a custom hardware accelerator could improve it. The goal is to take any input image and reduce it to K distinct colors by clustering pixels in RGB space — and to determine whether this can be done faster with specialized hardware rather than a general-purpose CPU.

---

## 2. How is it done today, and what are the limits of the current approach?

Today, K-Means image quantization is run on general-purpose CPUs using NumPy. Profiling with `cProfile` across 10 runs on a real image (bliss.jpg, 800×600, N=480,000 pixels, D=3 RGB, K=16 colors) on an Intel Core i9-12900H reveals that the **pairwise distance computation dominates at 46% of total runtime** (42.5s out of 91.9s).

The fundamental limit is memory bandwidth. The distance kernel has an arithmetic intensity of only **1.68 FLOP/byte** — for every floating point operation, nearly 0.6 bytes must be transferred from DRAM. This places the kernel deep in the memory-bound region of the CPU roofline (ridge point = 18.23 FLOP/byte), with an attainable performance ceiling of only ~129 GFLOP/s — less than 10% of the CPU's peak compute of 1,400 GFLOP/s. The low AI is a structural property of image K-Means: with D=3 dimensions, there are only 8 floating point operations per pixel-centroid pair but requires loading a full pixel and writing a full distance value. Making the CPU faster or adding more cores does not help — the bottleneck is purely how fast data can be moved from memory.

---

## 3. What is your approach and why is it better?

My approach is a HW/SW partition where the distance computation kernel is offloaded to a near-memory Processing-In-Memory (PIM) accelerator with 16 TB/s bandwidth and 8 TFLOP/s compute, while the CPU handles image I/O, centroid initialization, convergence checks, and centroid updates.

The roofline analysis directly motivates this design. With 16 TB/s bandwidth, the ridge point drops to 0.5 FLOP/byte — well below the kernel's AI of 1.68. The kernel becomes **compute-bound** on the accelerator, allowing near-peak 8 TFLOP/s throughput. This represents a ~62× improvement over the CPU attainable ceiling of 129 GFLOP/s. The required interface bandwidth of ~5 TB/s confirms that only near-memory or on-die SRAM architectures can sustain this workload — conventional DDR or PCIe buses would remain the bottleneck.

This approach is better than the CPU baseline because it targets the actual bottleneck (memory bandwidth) rather than compute throughput, and co-locating compute with memory is the only architectural change that fundamentally shifts the kernel from memory-bound to compute-bound.
