# Heilmeier Questions
Bao Nguyen  
ECE 410/510 Spring 2026

---

## 1. What are you trying to do?

I am analyzing the hardware performance characteristics of ResNet-18, a widely used convolutional neural network, to understand what limits its execution speed and how a custom hardware accelerator could improve it. Specifically, I am using roofline analysis and profiling to identify the computationally dominant kernel, quantify its arithmetic intensity, and propose a HW/SW partition that targets the real bottleneck rather than optimizing blindly.

---

## 2. How is it done today, and what are the limits of the current approach?

Today, ResNet-18 inference is typically run on general-purpose CPUs or GPUs using frameworks like PyTorch. Profiling with `torch.profiler` across 10 forward passes on an Intel Core i9-12900H reveals that the **3×3 Conv2d layer in layer4 (512→512 channels, 7×7 spatial)** dominates runtime at **19.13% of total CPU time**, accounting for ~11.4 ms per forward pass.

The limit of the current CPU-based approach is clear from the roofline: the kernel has an arithmetic intensity of **23.99 FLOP/byte**, placing it in the compute-bound region (ridge point = 18.23 FLOP/byte). However, the CPU only achieves ~61 GFLOP/s of actual throughput against a theoretical ceiling of 1,400 GFLOP/s — a utilization of under 5%. This gap is caused by poor SIMD efficiency on the small 7×7 spatial maps, frequent memory round-trips for weights, and overhead from the general-purpose execution model. The CPU cannot keep its vector units fed efficiently for this kernel shape.

---

## 3. What is your approach and why is it better?

My approach is to design a hardware/software partition where the dominant Conv2d kernel is offloaded to a custom systolic array accelerator (targeting 50 TFLOP/s with 2 TB/s on-chip SRAM bandwidth), while the CPU handles preprocessing, normalization, and control flow.

The roofline analysis directly informs this choice: the kernel's arithmetic intensity of 23.99 FLOP/byte sits close to the ridge point of a well-designed accelerator (25 FLOP/byte at the target specs), meaning the accelerator can be kept near full utilization with appropriate weight tiling. By holding the 512×512 weight tensor on-chip across multiple spatial tiles, the effective data reuse increases, pushing the kernel into the compute-bound region where the accelerator's peak throughput is fully utilized.

This is better than the CPU baseline because a systolic array eliminates the SIMD scheduling overhead, maximizes MAC unit utilization for the exact kernel shape, and reduces DRAM traffic through on-chip weight buffering — directly attacking the bottleneck identified by profiling rather than relying on a general-purpose execution model.
