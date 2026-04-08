# HW/SW Partition Proposal
Bao Nguyen  
ECE 410/510 Spring 2026

---

## (a) Which kernel(s) to accelerate in hardware and why

The kernel selected for hardware acceleration is the **3×3 Conv2d layer with 512 input and 512 output channels at 7×7 spatial resolution**, which corresponds to the repeated convolutions in ResNet-18's layer4. The `torch.profiler` output identified this as the dominant bottleneck at **19.13% of total CPU time**, accounting for the largest single share of runtime across 10 forward passes.

The roofline analysis supports this choice. With an arithmetic intensity of **23.99 FLOP/byte** and a CPU ridge point of **18.23 FLOP/byte**, the kernel sits in the compute-bound region on the i9-12900H. Despite being compute-bound, the CPU only achieves ~61 GFLOP/s measured throughput against a theoretical ceiling of 1,400 GFLOP/s — a large efficiency gap caused by poor SIMD utilization on small 7×7 spatial maps. A dedicated systolic array accelerator can close this gap by keeping compute units fully utilized with data tiled on-chip.

## (b) What the software baseline will continue to handle

The software baseline running on the CPU will continue to handle all non-compute-intensive stages: data loading and preprocessing, batch normalization, ReLU activations, max pooling, the fully connected classifier layer, and the overall training loop including gradient computation and weight updates. These operations are either memory-bound with low arithmetic intensity or too small to justify dedicated hardware.

## (c) Interface bandwidth required

The dominant kernel moves **9,637,888 bytes** per forward pass inference. At a target accelerator throughput of 50 TFLOP/s, one forward pass completes in approximately:

```
time = FLOPs / throughput = 231,211,008 / (50 × 10^12) ≈ 4.6 μs
```

Required interface bandwidth to avoid becoming interface-bound:

```
BW_needed = 9,637,888 bytes / 4.6 μs ≈ 2.1 TB/s
```

This is on-chip SRAM bandwidth, not PCIe. The accelerator must have at least **2 TB/s of on-chip memory bandwidth** to sustain this throughput. The hypothetical design targets 2 TB/s, which sits right at the boundary — keeping weight buffers on-chip across multiple inference passes would relax this constraint significantly.

## (d) Bound classification and expected change with accelerator

On the current i9-12900H CPU, the dominant kernel is **compute-bound** (AI = 23.99 > ridge point = 18.23). The bottleneck is insufficient compute throughput for the dense 512×512 matrix multiplications.

On the hypothetical accelerator (50 TFLOP/s, 2 TB/s), the ridge point shifts to 25 FLOP/byte. Since AI = 23.99 < 25, the kernel becomes **slightly memory-bound** on the accelerator. This means adding on-chip weight caching (weights are reused across the input spatial positions) would push the effective AI above the ridge point and make the kernel compute-bound again — which is the ideal operating point for a systolic array design.
