# Heilmeier Questions
Bao Nguyen  
ECE 410/510 Spring 2026

---

## 1. What are you trying to do?

I am analyzing the hardware performance characteristics of K-Means clustering to understand what limits its execution speed and how a custom hardware accelerator could improve it. Specifically, I am using roofline analysis and profiling to identify the computationally dominant kernel, quantify its arithmetic intensity, and propose a HW/SW partition that targets the real bottleneck.

---

## 2. How is it done today, and what are the limits of the current approach?

Today, K-Means is typically run on general-purpose CPUs using NumPy or similar libraries. Profiling with `cProfile` across 10 runs on an Intel Core i9-12900H (N=50,000 points, D=64 dimensions, K=8 clusters) reveals that the **pairwise distance computation** dominates runtime, accounting for the majority of the 39.3 seconds total — with `numpy.ufunc.reduce` alone at 5.57 seconds.

The limit is clear from the roofline: the distance kernel has an arithmetic intensity of only **2.67 FLOP/byte**, placing it deep in the memory-bound region (ridge point = 9.11 FLOP/byte on this CPU). For every floating point operation, ~0.37 bytes of useful data are processed, meaning the compute units sit idle most of the time waiting for data from DRAM. The attainable performance ceiling is only ~205 GFLOP/s — far below the CPU's 700 GFLOP/s peak compute. Making the CPU faster would not help; the bottleneck is memory bandwidth.

---

## 3. What is your approach and why is it better?

My approach is to design a hardware/software partition where the distance computation kernel is offloaded to a near-memory accelerator with HBM3-class bandwidth (10 TFLOP/s, 4 TB/s), while the CPU handles centroid updates, convergence checks, and control flow.

The roofline analysis directly informs this choice: with 4 TB/s bandwidth, the ridge point drops to 2.5 FLOP/byte — just below the kernel's AI of 2.67. This shifts the kernel from memory-bound to **compute-bound**, allowing the accelerator's MAC units to operate at near-peak efficiency. The required interface bandwidth of ~3.74 TB/s is achievable with HBM3 but not with standard DDR or PCIe, confirming that memory architecture — not compute throughput — is the design-critical parameter.

This approach is better than the CPU baseline because it eliminates the memory bandwidth bottleneck that prevents the current implementation from using even 30% of available compute, replacing it with a design where arithmetic throughput is the limiting factor.
