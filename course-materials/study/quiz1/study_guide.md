# ECE 410/510 — Quiz 1 Study Guide
**Bao Nguyen | Portland State University | Spring 2026**

---

## How to Use This Guide
Work through each section in order. For each concept: read the explanation, close the guide, and try to reproduce the key formula or definition from memory. Then check. For CMAN problems, always work through the full calculation — partial credit depends on showing formulas before numbers.

---

## Unit 1: Why Hardware for AI?

### The Core Problem
Modern AI workloads are **memory-bound**, not compute-bound. Processors got faster much quicker than memory got wider. The gap between what a chip can compute and how fast it can be fed data has grown for 30+ years — this is the **Memory Wall**.

### Energy Is the Real Constraint
Moving data costs far more than computing with it:
- FP32 multiply: ~**3.7 pJ**
- DRAM (Dynamic Random Access Memory) 64-bit read: ~**640 pJ** — 170× more expensive

This means the primary goal of hardware design for AI is to **minimize data movement**, not just maximize compute throughput.

### AI vs ML
- ML (Machine Learning) is a subset of AI focused on algorithms that improve through experience, such as neural networks.
- AI (Artificial Intelligence) is the broader concept: machines performing tasks requiring human intelligence. The ultimate goal is AGI (Artificial General Intelligence).
- All ML is AI, but not all AI is ML.

### Architecture Evolution
```
CPU → CPU + GPU → Heterogeneous → Extreme Heterogeneity
                                  (NPU, TPU, FPGA, ASIC, VPU)
```

### HW/SW Co-design
- Started in the 1990s. Core idea: concurrent design of hardware and software components in a single design effort.
- HW/SW co-design deals with the HW/SW interface directly.
- Broader definition: concurrent design across ALL layers of the compute stack.
- From a flexibility standpoint, as much as possible should stay in software since hardware is expensive and slow to change.
- Why it matters for AI/ML:
  - Performance: traditional HW assumes fixed SW, traditional SW assumes fixed HW. Co-design optimizes both simultaneously.
  - Specialized acceleration: AI algorithms like matrix multiply and convolutions benefit from custom hardware tailored to those operations.
  - Memory bottlenecks: co-designing memory hierarchies with software scheduling minimizes data movement.
  - Energy efficiency: tailoring hardware precisely to ML workloads dramatically reduces power consumption.

### Why Design New Hardware?
- Problem 1: Data locality — traditional architecture has high-latency, high-energy off-chip memory access.
- Problem 2: Need for parallelism — traditional architecture is insufficient for massively parallel AI workloads.
- Problem 3: Compute closer to the physics — bringing computation closer to memory reduces energy.

### Design Trade-offs (PPAC)
Performance, Power, Area, Cost — every hardware decision involves all four. Also includes flexibility, design complexity, scalability, and time-to-market.

---

## Unit 2: Performance Analysis — Roofline Model

### Arithmetic Intensity (AI)
```
AI = FLOPs / Bytes    [FLOP/byte]
```
Measures how compute-heavy a kernel is relative to its memory traffic. High AI = compute-bound candidate. **AI says nothing about bottlenecks on its own — you need the roofline for that.**

### Roofline Model
```
Attainable Performance = min(Peak_Compute, AI × Bandwidth)
```

**Ridge Point** — the boundary between memory-bound and compute-bound:
```
I* = Peak_Compute / Bandwidth    [FLOP/byte]
```

| If AI < I* | Memory-bound | attainable = AI × BW |
|---|---|---|
| If AI > I* | Compute-bound | attainable = Peak Compute |

The ridge point is the ideal place for a kernel to sit — it is the minimum arithmetic intensity needed to fully utilize peak compute without being held back by memory.

### Hardware Knobs vs Algorithm Knobs
- **Higher BW** → lower ridge point → more kernels become compute-bound
- **Higher Peak Compute** → higher ridge point → harder to be compute-bound
- **Higher AI** (via tiling/reuse) → operating point moves right → toward compute-bound
- You cannot change AI by changing hardware — AI is a property of the algorithm

### If Compute-bound But Below Roofline
1. Instruction-level parallelism — long dependency chains serialize execution, unrolling loops helps.
2. Occupancy — too few warps active due to high register usage or large shared memory, scheduler stalls.
3. Instruction mix — integer/address/branch ops mixed in reduce floating point unit utilization.
4. Precision mismatch — using FP64 peak vs FP32 roofline gives wrong ceiling.
5. Tensor core underutilization — matrix dims not multiples of 16 means scalar CUDA cores used instead.

### If Memory-bound But Below Roofline
- Non-coalesced access — threads not accessing consecutive addresses collapses bandwidth.
- Cache thrashing — working set slightly larger than cache, data evicted and re-fetched.
- Too few in-flight memory requests — DRAM pipeline stays empty.
- Atomic operations — many threads writing same location serializes.

---

## Unit 3: GEMM and Tiling — The Most Important CMAN Topic

### What is N?
N is the **dimension of the square matrix**. If N=32, you have a 32×32 matrix:
- A is N×N, B is N×N, C (output) is N×N
- Total elements in one matrix = **N²**
- Total multiply-adds to compute C = **N³** (each of the N² output elements needs N multiply-adds)

### Naive GEMM
Triple loop, no data reuse. Every access goes to DRAM.
```
Traffic_naive = 2N³ × 4 bytes
AI_naive      = 2N³ / (2N³ × 4) = 1/4 = 0.25 FLOP/byte
```
Always deeply memory-bound regardless of N.

### Tiled GEMM
Tiles loaded into shared memory (SRAM). Each element of A and B loaded from DRAM **exactly once**.
```
Traffic_tiled = 2N² × 4 bytes
AI_tiled      = 2N³ / (2N² × 4) = N/4 FLOP/byte
```

### Traffic Ratio
```
Traffic_naive / Traffic_tiled = 2N³ / 2N² = N
```
**Ratio = N, not T.** T cancels because ideal tiling loads each element once regardless of tile size.

### AI Formula Derivation (know this cold)
```
AI = 2N³ / (2N² × 4)
   → 2s cancel: N³ / (N² × 4)
   → N³/N² = N: N / 4
   = N/4
```

### Tile Size Tradeoff
- Small tile: low SRAM usage, high occupancy, but low AI — memory-bound.
- Medium tile: balanced, sweet spot for most GPUs.
- Large tile: high AI, but low occupancy (few blocks per SM) and register spills.
- Tile size is programmer-controlled and empirically determined. There is no single universally optimal size.

### Execution Time
```
t_memory  = Bytes / Bandwidth
t_compute = FLOPs / Peak_Compute
Bottleneck = whichever is larger
```

### Common Kernels and their AI
| Kernel | AI | Bound |
|---|---|---|
| Vector add | 0.083 FLOP/byte | Memory |
| Naive GEMM | 0.25 FLOP/byte | Memory |
| Tiled GEMM (N=64) | 16 FLOP/byte | Depends on hardware |
| Tiled GEMM (N=1024) | 256 FLOP/byte | Compute |
| Conv layers | 10–100 FLOP/byte | Often Compute |

---

## Unit 4: What Is a Kernel?

A **kernel** in this context is a single computational routine that runs on a processor or GPU. It is the unit of work submitted to the hardware — a self-contained function that takes some inputs, performs a defined computation, and produces outputs.

Examples: matrix multiplication, vector addition, convolution, softmax. When you run a neural network, it is broken down into a sequence of kernel launches, each handling one operation.

You find the bottleneck kernel by **profiling** — timing every function and finding what consumes more than 10% of runtime. That is what you build hardware to accelerate.

---

## Unit 5: GPU Architecture

### SIMT (Single Instruction Multiple Threads) Execution Model
- **Warp**: 32 threads executing the same instruction in lockstep — the basic scheduling unit. AMD calls similar groupings wavefronts.
- **SM (Streaming Multiprocessor)**: fundamental execution unit containing CUDA cores, Tensor cores, SRAM, and warp schedulers. The H100 has 132 SMs.
- **Thread Block**: group of threads assigned to one SM. Shares that SM's shared memory. Up to 1024 threads.
- **Grid**: all thread blocks for a kernel, distributed across all SMs.

### SM Internal Components
| Component | Role |
|---|---|
| CUDA cores | Scalar FP32/INT32 arithmetic |
| Tensor cores | 4×4 MMA (Matrix Multiply Accumulate) in one clock cycle |
| Warp schedulers (×4) | Manage warps, switch to ready warp when another stalls |
| Register file | 65,536 × 32-bit registers per SM, private per thread, fastest storage |
| Shared memory | ~228 KB on H100, on-chip SRAM, programmer-managed scratchpad |
| L1 cache | Unified with shared memory, hardware-managed |
| Load/store units | Move data between SM and memory hierarchy |
| SFUs (Special Function Units) | Transcendental math — sin, cos, exp |

### SIMT vs SIMD (Single Instruction Multiple Data)
SIMT is a more flexible, programmable evolution of SIMD. It is not in Flynn's original taxonomy — coined by NVIDIA.

| Dimension | SIMD (CPU) | SIMT (GPU) |
|---|---|---|
| Parallelism unit | Vector lane, fixed width 4/8/16 | Thread within warp, 32 threads |
| Control flow | All lanes must execute identical op | Threads can branch, divergent paths serialized |
| Register file | Shared vector regs mapped to scalar | Per-thread private regs, 65k 32-bit per SM |
| Memory model | Shared cache/L1, no scratchpad control | Shared memory scratchpad + L1/L2 + HBM, programmer-managed |
| Latency tolerance | Out-of-order exec + large caches | Zero-overhead warp switching, 1000s of threads hide latency |
| Scalability | Fixed width, limited by ISA | Scales to 1000s of SMs, same code runs on any GPU size |

### Warp Divergence
When threads in a warp take **different branches**, the GPU serializes both paths:
```c
// BAD — causes divergence within a warp
if (threadIdx.x % 2 == 0) { ... } else { ... }
```
Throughput drops up to **2× per branch level**. Fix: ensure all 32 threads in a warp take the same path.

### Occupancy
```
Occupancy = Active warps / Max warps per SM
```
Higher occupancy means the warp scheduler has more ready warps and better latency hiding. Limited by registers per thread, shared memory per block, and thread block size.

### CUDA (Compute Unified Device Architecture) Memory Hierarchy
| Memory | Scope | Speed | Size |
|---|---|---|---|
| Registers | per-thread | fastest | 65,536 × 32-bit per SM |
| Shared Memory | per-block (SM) | ~1 TB/s | 228 KB/SM (H100) |
| L2 Cache | GPU-wide | medium | 40 MB (A100) |
| Global Memory | all threads | slow | GBs (DRAM) |

### CUDA Kernel Launch
```cuda
kernel<<<M, T>>>(args)   // M blocks, T threads per block
// Total threads = M × T
// Threads per block T should be multiple of 32 (warp size)
```
If more blocks are requested than available, the GPU queues and schedules them over time. CUDA programs can be written without knowing the exact hardware configuration.

### Tensor Cores
Perform small matrix multiplications in one operation. Mixed precision: FP16 inputs with FP32 accumulation. The V100 has 640 first-gen Tensor Cores. The A100 has 432 third-gen Tensor Cores with higher performance due to architectural improvements and mixed precision support including TF32, FP64, and BF16.

---

## Unit 6: CNN/DNN Fundamentals

### Neural Networks as Matrix Operations
A whole layer of neurons is just one matrix-vector multiply, which is why GPUs accelerate neural nets so effectively. One MAC (Multiply Accumulate) = one multiply + one add = 2 FLOPs. One layer with m neurons and n inputs = 2mn FLOPs.

### GEMM (General Matrix Matrix Multiply) Is Everything
Virtually every operation in a neural network reduces to GEMM:
- Fully connected layers
- Convolutions
- Attention in transformers (Q, K, V projections and QKᵀ and AV)
- Recurrent gate computations

### Key Formula
```
FLOPs = 2 × MACs
Conv2D FLOPs = 2 × N × C_in × K² × H_out × W_out
```

### ResNet-18 Reference Numbers
11.69M parameters, **1.81B MACs**, 46.76 MB weights, 39.75 MB activations.

### Precision Formats
| Format | Bits | Key property |
|---|---|---|
| FP32 | 32 | Standard baseline, full dynamic range |
| FP16 | 16 | Narrow exponent range, overflow risk during training |
| BF16 | 16 | Same exponent range as FP32, safer for training, drop-in replacement |
| INT8 | 8 | 4× bandwidth reduction, inference only |
| FP4 (E2M1) | 4 | Only 16 distinct values, requires block scaling |

**BF16 (Brain Float 16)** was developed by Google Brain specifically for ML. It keeps the full 8-bit exponent from FP32, giving the same dynamic range. Converting between BF16 and FP32 is trivial — just add or drop the last 16 mantissa bits.

**Why lower precision?** Halving precision doubles the number of operands that fit in a fixed data bus or register tile, giving 2× or 4× more MACs per cycle at the same silicon area and power budget.

**PTQ (Post-Training Quantization)** — quantize trained model; fast, less accurate.
**QAT (Quantization-Aware Training)** — simulate quantization during training; better accuracy, more expensive.

---

## Unit 7: Systolic Arrays

A systolic array is a 2D grid of identical PEs (Processing Elements) that rhythmically compute and pass data to their neighbors. The name comes from an analogy to the human heart — data pulses through the array in a synchronized fashion.

Each PE performs one MAC. It multiplies two inputs, adds to a running sum, and forwards data onward. All PEs operate in lockstep under a global clock.

The key advantage over a CPU or GPU is that data moves PE to PE locally each cycle with no repeated reads from slow DRAM. Each weight is read once but reused for many MACs.

### Three Dataflow Strategies
| Strategy | What stays | What streams | Best for | Example |
|---|---|---|---|---|
| Weight Stationary (WS) | Weights in PEs | Activations and partial sums | Layers reused across many inputs | Google TPU v1–v4 |
| Output Stationary (OS) | Output in PEs | Weights and activations | Small output matrices | ShiDianNao |
| Row Stationary (RS) | Filter row in PEs | Activations slide, partial sums accumulate | Diverse layer shapes, CNN/FC/LSTM | MIT Eyeriss |

Each dataflow minimizes movement of one data type at the cost of moving others more. The optimal choice depends on layer shape and batch size.

---

## Unit 8: TPU Architecture

The TPU (Tensor Processing Unit) was created by Google specifically for ML. It is only available through Google Cloud.

The main component is the MXU (Matrix Multiply Unit), which is a 256×256 systolic array performing 65,536 MACs per clock cycle using 8-bit operations. The MXU gets its input from the weighted FIFO and unified buffer.

TPU key features: the MXU, TensorCores (each containing a matrix multiply unit plus a vector unit plus a scalar unit), and an Activation Unit with hardwired activation functions.

### GPU vs TPU
| | GPU | TPU |
|---|---|---|
| Origin | Graphics | Created by Google for ML |
| Architecture | Thousands of smaller parallel cores | Specialized MXUs for tensor operations |
| Performance focus | Flexibility, broader applicability | Optimized for matrix ops and ML |
| Availability | NVIDIA, AMD | Proprietary, Google Cloud only |
| Software | CUDA and various frameworks | TensorFlow |
| Power efficiency | Less power-efficient, more flexible | More power-efficient |

---

## Unit 9: Transformers

A transformer is a neural network that learns context and meaning by tracking relationships in sequential data, processing all tokens simultaneously rather than one at a time.

Transformers are **explicitly non-recurrent**. The 2017 "Attention Is All You Need" paper was a direct response to RNNs/LSTMs, which process tokens one at a time and pass a hidden state from step to step. That sequential dependency makes RNNs slow to train and bad at long-range dependencies.

The transformer replaces recurrence with **self-attention**, which:
- Processes all tokens simultaneously in parallel
- Connects every token directly to every other token in a single operation with no hidden state
- Uses positional encodings to handle order instead of recurrence

### Self-Attention: Q, K, V
Each token gets three learned projections:
- Q (Query) — what the token is looking for
- K (Key) — what the token offers
- V (Value) — what the token contributes if selected

Attention queries are executed in parallel via multi-headed attention, computing a matrix of equations across all tokens at once.

### Main Mathematical Operations
- Matrix multiplication throughout, especially in attention and feed-forward networks
- Scaled dot-product attention using softmax
- Layer normalization using mean and variance
- Residual connections (skip connections) for gradient flow
- Position-wise feed-forward networks with ReLU
- Positional encoding via sine and cosine functions (handled by SFUs on GPU)

### Why Transformers Matter for Hardware
All the core operations reduce to GEMM. The Q, K, V projections are GEMM. The attention score matrix QKᵀ is GEMM. The weighted sum AV is GEMM. This is why the same GPU hardware that accelerates neural net training also accelerates transformer inference.

---

## Unit 10: HW/SW Partitioning

### Decision Framework
| Question | Yes → | No → |
|---|---|---|
| Kernel > 10% runtime? | Consider HW | Leave in SW |
| Compute-bound at tile size? | Build fixed datapath | Optimize memory access first |
| Regular access pattern? | Good HW candidate | Keep in SW |

### Accelerator Template
```
DRAM → [Input Buffer SRAM] → [GEMM Engine] → [Output Buffer] → DRAM
                ↑
         AXI4-Lite (CPU control)
         AXI4-Stream (data)
         Controller FSM + Vector Engine
```

---

## Unit 11: VLSI Design Basics

VLSI (Very Large Scale Integration) places billions of transistors on a chip. An ASIC (Application-Specific Integrated Circuit) is a specific type designed for a custom dedicated function. VLSI is the field; ASICs are the end product.

### Abstraction Levels (top to bottom)
1. Algorithm — Python, MATLAB
2. RTL (Register Transfer Level) — Verilog, SystemVerilog
3. Gate — AND, OR, flip-flops (netlist)
4. Physical — transistors, silicon layout (GDSII)

### Tool Chain
| Tool | Type | Role |
|---|---|---|
| Yosys / Synopsys DC | Synthesis | RTL → gates |
| OpenROAD / Cadence | Place and Route | gates → layout |
| Icarus / Verilator | Simulation | verify behavior |
| cocotb | Testbench | Python-driven verification |

cocotb (Coroutine-based Co-simulation Test Bench) allows writing hardware testbenches in Python using async/await. It interfaces with HDL simulators via VPI/VHPI.

### Hardware Types
| Type | Flexible | Performance | Power Efficiency | Cost |
|---|---|---|---|---|
| CPU | high | low | low | low |
| GPU | medium | high | medium | medium |
| FPGA | low | high | medium | medium |
| ASIC | none | highest | highest | very high |

---

## Unit 12: No Free Lunch Theorem

Formalized by Wolpert and Macready in 1997. When averaged across all possible problems, all optimization algorithms perform equally well. No algorithm consistently outperforms random search.

Implications for hardware:
- Specialized architectures work well for specific domains but fail in others.
- Domain knowledge is essential when selecting algorithms and architectures.
- Claims about architecture superiority must specify the context and problem class.

---

## Unit 13: The Codefest Problems — What Was Tested

### CF01 — FC Network Workload Accounting
- Count MACs layer by layer: input_dim × output_dim per layer
- Weight bytes = total params × 4; activation bytes = total neurons × 4
- AI = 2×MACs / (weight_bytes + activation_bytes) → typically ~0.5 FLOP/byte (memory-bound)

### CF02 — Roofline Classification
- Given hardware (Peak, BW), compute ridge point
- For each kernel: compute FLOPs, Bytes, AI; compare to ridge; find attainable performance
- Dense GEMM → compute-bound; vector add → memory-bound

### CF03 — DRAM Traffic Analysis
- Naive: 2N³×4; Tiled: 2N²×4; Ratio = N
- Show formula first, then numbers — rubric checks both
- Both naive and tiled can still be memory-bound; crossing ridge requires AI > ridge point

---

## Quick-Reference: Numbers to Memorize

| Fact | Value |
|---|---|
| FP32 multiply energy | 3.7 pJ |
| DRAM 64-bit read energy | 640 pJ (170× multiply) |
| Warp size | 32 threads |
| Naive GEMM AI | 0.25 FLOP/byte (always) |
| Tiled GEMM AI | N/4 FLOP/byte |
| Traffic ratio (naive/tiled) | N |
| ResNet-18 MACs | 1.81 billion |
| H100 shared memory per SM | 228 KB |
| H100 SM count | 132 |
| TPU MXU size | 256×256 = 65,536 MACs |
| Register file per SM | 65,536 × 32-bit registers |

---

## Last-Minute Checklist

- [ ] Can I compute naive and tiled DRAM traffic for any N and T?
- [ ] Can I derive AI = N/4 step by step without looking?
- [ ] Do I know why the ratio equals N and not T?
- [ ] Can I classify a kernel as memory/compute-bound given AI and hardware specs?
- [ ] Do I know what limits occupancy?
- [ ] Can I explain warp divergence with a code example?
- [ ] Do I know the CUDA memory spaces and their speeds?
- [ ] Do I know the VLSI abstraction levels?
- [ ] Do I know PPAC and the accelerator datapath template?
- [ ] Can I explain what a systolic array is and the three dataflow strategies?
- [ ] Can I explain how a transformer differs from an RNN?
- [ ] Can I explain SIMT vs SIMD?
- [ ] Do I know the trap: higher BW does NOT make a kernel compute-bound?
