# ECE 410/510 — Quiz 1 Practice Questions & Answers

---

## Section A: CMAN — DRAM Traffic & Arithmetic Intensity

**Q1.** For naive GEMM with N=64, FP32, what is the total DRAM traffic in bytes?
> Traffic = 2N³ × 4 = 2 × 262,144 × 4 = **2,097,152 bytes (2 MB)**

**Q2.** For tiled GEMM with N=64, T=8, FP32, what is the total DRAM traffic in bytes?
> Traffic = 2N² × 4 = 2 × 4,096 × 4 = **32,768 bytes (32 KB)**

**Q3.** What is the traffic ratio for Q1 vs Q2? Why?
> Ratio = 2N³ / 2N² = **N = 64**. In tiled GEMM each element is loaded from DRAM exactly once; in naive each element is loaded N times, so tiling removes N-fold redundancy.

**Q4.** What is the arithmetic intensity of naive GEMM with N=64, FP32?
> FLOPs = 2N³ = 524,288; Bytes = 2N³×4 = 2,097,152; **AI = 0.25 FLOP/byte**

**Q5.** What is the arithmetic intensity of tiled GEMM with N=64, T=8, FP32?
> FLOPs = 2N³ = 524,288; Bytes = 2N²×4 = 32,768; **AI = N/4 = 16 FLOP/byte**

**Q6.** Hardware: Peak = 10 TFLOPS, BW = 320 GB/s. What is the ridge point?
> Ridge = 10,000 / 320 = **31.25 FLOP/byte**

**Q7.** Using hardware from Q6: is naive GEMM (N=64) memory-bound or compute-bound?
> AI = 0.25 << 31.25 → **memory-bound**. Attainable = 0.25 × 320 = **80 GFLOP/s**

**Q8.** Using hardware from Q6: is tiled GEMM (N=64, T=8) memory-bound or compute-bound?
> AI = 16 < 31.25 → still **memory-bound**. Attainable = 16 × 320 = **5,120 GFLOP/s**

**Q9.** Using hardware from Q6: what N would make tiled GEMM compute-bound?
> Need AI = N/4 > 31.25 → N > 125 → **N ≥ 128** makes tiled GEMM compute-bound

**Q10.** For naive GEMM (N=64, BW=320 GB/s, Peak=10 TFLOPS), compute execution times and identify bottleneck.
> t_mem = 2,097,152 / 320e9 = **6.55 μs**; t_compute = 524,288 / 10e12 = **0.052 μs**; bottleneck = **memory** (126× slower)

**Q11.** For tiled GEMM (N=64, T=8, same hardware), compute execution times.
> t_mem = 32,768 / 320e9 = **0.102 μs**; t_compute = 524,288 / 10e12 = **0.052 μs**; bottleneck = **memory** (2× slower, near ridge)

**Q12.** FC network [512 → 256 → 10], batch=1, FP32, no bias. Compute total MACs, weight memory, activation memory, and AI.
> MACs: 512×256 + 256×10 = 131,072 + 2,560 = **133,632 MACs**
> Weights: 133,632 × 4 = **534,528 bytes**
> Activations: (512 + 256 + 10) × 4 = **3,112 bytes**
> AI = (2 × 133,632) / (534,528 + 3,112) = 267,264 / 537,640 = **0.497 FLOP/byte → memory-bound**

**Q13.** What does the N² term represent and should it be included in GEMM traffic?
> N²×4 bytes = writes to output matrix C. The assignment counts only **reads of A and B**, so the N² write term is excluded. For large N it's negligible anyway (N² << 2N³).

**Q14.** Simplify AI = 2N³ / (2N² × 4) step by step.
> 2s cancel → N³ / (N² × 4); N³/N² = N → **N/4**

---

## Section B: Roofline Model

**Q15.** What are the two axes of the roofline model?
> X-axis: **Arithmetic Intensity (FLOP/byte)**; Y-axis: **Performance (GFLOP/s)**

**Q16.** What are the two ceilings on a roofline plot?
> **Memory bandwidth ceiling** (diagonal line, slope = BW); **Peak compute ceiling** (horizontal line)

**Q17.** A kernel has AI = 50 FLOP/byte on hardware with ridge = 31.25. Is it compute-bound? What is attainable performance?
> AI > ridge → **compute-bound**; attainable = **peak compute** (10,000 GFLOP/s)

**Q18.** A kernel has AI = 5 FLOP/byte, BW = 320 GB/s, Peak = 10 TFLOPS. What is attainable performance?
> AI < ridge (31.25) → memory-bound; attainable = 5 × 320 = **1,600 GFLOP/s**

**Q19.** If you double peak compute but BW stays the same, what happens to the ridge point?
> Ridge = Peak/BW doubles → **harder to be compute-bound**; memory-bound region grows

**Q20.** If you double memory bandwidth but peak compute stays the same, what happens?
> Ridge = Peak/BW halves → **easier to be compute-bound**; more kernels become compute-bound

**Q21.** Does increasing memory bandwidth make a kernel compute-bound?
> **No** — bandwidth shifts the ridge point but does not change the kernel's AI. A kernel becomes compute-bound only if its AI exceeds the (new, lower) ridge point.

**Q22.** Vector addition (N=1M, FP32): FLOPs = N, Bytes = 3N×4 (2 reads + 1 write). Compute AI.
> AI = N / (12N) = **1/12 ≈ 0.083 FLOP/byte → deeply memory-bound**

**Q22b.** [ORAL EXAM STYLE] You are shown a roofline plot. Walk me through how you interpret it.
> **Step 1 — Identify the axes**: X-axis = Arithmetic Intensity (FLOP/byte, log scale). Y-axis = Attainable Performance (GFLOP/s, log scale).
>
> **Step 2 — Identify the two ceilings**:
> - **Diagonal line** rising left-to-right = memory bandwidth ceiling (slope = Peak_BW). Kernels on this line are memory-bound.
> - **Horizontal line** flat at the top = peak compute ceiling. Kernels on this line are compute-bound.
>
> **Step 3 — Find the ridge point**: Where the diagonal meets the horizontal. Ridge point I* = Peak_Compute / Peak_BW. This is the minimum AI needed to be compute-bound.
>
> **Step 4 — Read each kernel dot**:
> - Dot is **left of ridge** → memory-bound. Attainable performance = AI × Peak_BW. Fix: reduce DRAM traffic (tile, fuse, increase data reuse).
> - Dot is **right of ridge** → compute-bound. Attainable performance = Peak_Compute. Fix: more arithmetic units or better ILP.
> - Dot is **below its ceiling** → not hitting the roof — another bottleneck (occupancy, synchronization, etc.).
>
> **Critical insight to state**: "AI is a property of the algorithm, not the hardware. Hardware only moves the ridge point. You cannot make a kernel compute-bound by adding memory bandwidth — you can only lower the ridge point threshold."
>
> **Example (CF02: Peak = 10 TFLOP/s, BW = 320 GB/s, I* = 31.25)**:
> - GEMM (AI = 170.67) → right of ridge → compute-bound → ceiling = 10,000 GFLOP/s
> - Vector Add (AI = 0.083) → left of ridge → memory-bound → ceiling = 26.67 GFLOP/s

---

## Section C: GPU Architecture

**Q23.** What is SIMT?
> **Single Instruction, Multiple Threads** — all 32 threads in a warp execute the same instruction simultaneously on different data.

**Q24.** What is a warp?
> A group of **32 threads** that execute lockstep on NVIDIA GPUs; the basic scheduling unit.

**Q25.** What is warp divergence and why is it bad?
> When threads in a warp take different if/else branches, the GPU **serializes both paths**, masking idle threads. Throughput drops up to 2× per branch level.

**Q26.** Give a code example that causes warp divergence.
> `if (threadIdx.x % 2 == 0) { ... } else { ... }` — odd and even threads within the same warp take different paths.

**Q27.** What is occupancy?
> **Active warps / maximum warps per SM**. Higher occupancy lets the warp scheduler hide memory latency by switching to ready warps.

**Q28.** What three things limit occupancy?
> **Register usage**, **shared memory size**, **thread block size** (too small = too few warps per SM)

**Q29.** What is the difference between shared memory and global memory?
> **Shared memory**: per-SM SRAM, ~1 TB/s bandwidth, low latency, shared within a thread block.
> **Global memory**: DRAM, ~192–3350 GB/s, high latency, accessible by all threads.

**Q30.** What is a Streaming Multiprocessor (SM)? Define it and list ALL key internal components with their roles.
> **Definition**: The SM is the fundamental execution unit of an NVIDIA GPU. A GPU consists of many SMs (H100: 132); the hardware assigns one thread block to one SM. All computation happens inside SMs.
>
> **Key components:**
> | Component | Role |
> |---|---|
> | **CUDA cores** | Scalar arithmetic — FP32/INT32 ALU operations |
> | **Tensor cores** | Matrix-multiply accelerators — one 4×4×4 FMA per cycle; built for GEMM in deep learning |
> | **Warp schedulers (×4)** | Each SM has 4 schedulers. A warp = 32 threads SIMT. Switch to a ready warp every cycle to **hide memory latency** |
> | **Register file** | ~16K 32-bit registers per SM — fastest storage, local to each thread |
> | **Shared memory / L1 SRAM** | On-chip SRAM shared by all threads in a block (~192–228 KB). Programmer-managed scratchpad (~1 TB/s) for data reuse |
> | **Load/Store units** | Handle memory traffic between SM and the cache/DRAM hierarchy |
> | **Special Function Units (SFUs)** | Hardware units for transcendentals: sin, cos, exp, reciprocal |
> | **L1 cache** | Physically unified with shared memory; hardware-managed portion |
>
> **How they fit together**: Warp schedulers issue instructions to CUDA or Tensor cores. When a warp stalls on a load, the scheduler swaps in another ready warp — this is latency hiding without branch prediction or OOO logic. Fast shared memory lets threads reuse data without going to slow DRAM.

**Q30b.** What does an SM do when a warp is stalled waiting for memory?
> The warp scheduler **switches to another ready warp** and issues its instructions. This is how GPUs hide DRAM latency — they keep the execution units busy by running other warps instead of stalling. This requires high occupancy (many active warps) to work.

**Q31.** What does `kernel<<<M, T>>>(args)` mean?
> Launch kernel with **M thread blocks**, each containing **T threads**. Total threads = M × T.

**Q32.** How many total threads in `kernel<<<256, 128>>>()`?
> 256 × 128 = **32,768 threads**

**Q33.** Can two thread blocks share data through shared memory?
> **No** — shared memory is per-SM and per-block. Cross-block communication requires global memory.

**Q34.** List CUDA memory spaces from fastest to slowest.
> Registers → Shared Memory → L1/L2 Cache → Global Memory (DRAM) → Local Memory (spills to DRAM)

---

## Section D: GPU Hardware

**Q35.** Compare V100 vs A100: key differences.
> A100: 3× SMEM/L1 BW, 6.7× larger L2 (40 MB), NVLink 3 (600 GB/s), async copies, 7nm vs 12nm

**Q36.** What are tensor cores and what do they do?
> Specialized hardware units that perform **small matrix multiplications** (4×4 or larger) in one operation. Use mixed precision: FP16 inputs → FP32 accumulation.

**Q37.** What precision formats does A100 support in tensor cores?
> **TF32, FP16, BF16, INT8, FP64**

**Q38.** What is the difference between FP16 and BF16?
> Both are 16-bit. BF16 has the **same exponent range as FP32** (8 exponent bits) → better dynamic range, less overflow risk. FP16 has more mantissa bits → higher precision but narrower range.

**Q39.** What is the energy cost of DRAM vs compute and why does it matter?
> DRAM read ≈ **640 pJ**; FP32 multiply ≈ **3.7 pJ** → 170× difference. Minimizing data movement is the primary optimization target for both performance and energy efficiency.

---

## Section E: HW/SW Codesign & Partitioning

**Q40.** What is HW/SW co-design? Define it, explain WHY it matters, and give examples.
> **Definition**: Designing hardware and algorithm/software **simultaneously and interdependently** — not sequentially (don't build the CPU first and then try to map a neural net onto it).
>
> **Why it matters:**
> 1. **Data movement dominates energy**: DRAM read = 640 pJ, FP32 multiply = 3.7 pJ → **170× more expensive** to move data than compute. An algorithm that ignores this will be bandwidth-limited regardless of hardware quality.
> 2. **Hardware can't be optimal without knowing the workload**: can't correctly size registers, SRAM, memory bandwidth, or datapath width without knowing the algorithm's access patterns.
> 3. **Sequential design wastes potential**: designing hardware first and then adapting software achieves a fraction of co-designed performance.
>
> **Concrete examples:**
> - **GEMM tiling**: Tile size T is chosen to match on-chip SRAM size → 64× DRAM traffic reduction. The algorithm is shaped by the hardware resource.
> - **Tensor cores**: NVIDIA added dedicated matrix-multiply HW because DNN training is dominated by GEMM. The hardware is shaped by the algorithm.
> - **Google TPU**: 256×256 systolic array built specifically for matrix multiply (dominant neural net op) → **83× perf/watt over CPU**.
>
> **The key sentence to say out loud**: "You cannot optimize hardware and software in isolation — the best systems co-optimize both simultaneously."

**Q40b.** Why does co-design achieve better perf/watt than CPU for deep learning?
> CPUs are designed for general-purpose workloads: branch prediction, out-of-order execution, large caches. These are wasted on DNN workloads which are regular, data-parallel, and dominated by GEMM. Co-designed hardware (TPU, GPU Tensor cores) eliminates that overhead and dedicates area/power to the specific operations DNN inference/training actually uses.

**Q41.** When should you accelerate a kernel in hardware?
> When it consumes **>10% of runtime** (Amdahl's law) AND is **compute-bound at the target tile size** with regular, predictable memory access patterns.

**Q42.** When should you keep a kernel in software (CPU)?
> When it has **irregular/data-dependent access patterns**, sparse operations, or pointer chasing — hardware fixed datapaths cannot handle these efficiently.

**Q43.** What are the four PPAC trade-offs in hardware design?
> **Performance · Power · Area · Cost** — every hardware decision involves all four.

**Q44.** What is the accelerator datapath template?
> Input Buffer (SRAM) → GEMM Engine → Output Buffer → DMA → DRAM, controlled via AXI4-Lite from CPU host.

---

## Section F: VLSI & Design Abstraction

**Q45.** List the four abstraction levels from algorithm to silicon.
> 1. Behavior/Algorithm (Python, MATLAB)
> 2. RTL (Verilog, SystemVerilog)
> 3. Gate Level (logic gates)
> 4. Transistor/Physical (silicon layout)

**Q46.** What is the difference between FPGA and ASIC?
> **FPGA**: reconfigurable after fabrication, flexible, medium power efficiency.
> **ASIC**: fixed function, maximum performance and power efficiency, very high design cost, no reconfiguration.

**Q47.** What tool converts RTL to a gate-level netlist?
> **Synthesis** tool — e.g., Yosys (open-source) or Synopsys Design Compiler (commercial).

**Q48.** What is cocotb?
> A **Python-based co-simulation testbench framework** for verifying hardware designs without writing testbenches in Verilog/VHDL.

---

## Section G: CNN/DNN

**Q49.** What is a MAC and how many FLOPs is it?
> **Multiply-Accumulate** operation: 1 multiply + 1 add = **2 FLOPs**

**Q50.** ResNet-18 stats from memory:
> 11.69M parameters, **1.81B MACs**, 46.76 MB weights, 39.75 MB activations

**Q51.** What is the Conv2D FLOPs formula?
> FLOPs = 2 × N × C_in × K × K × H_out × W_out
> (N=batch, C_in=input channels, K=kernel size, H/W_out=output spatial dims)

**Q52.** What is quantization and why use it?
> Reducing weight/activation precision (e.g., FP32 → INT8) to **reduce memory, bandwidth, and energy** with minimal accuracy loss.

**Q53.** PTQ vs QAT — what's the difference?
> **PTQ** (Post-Training Quantization): quantize after training; simple but less accurate.
> **QAT** (Quantization-Aware Training): simulate quantization during training; better accuracy, more expensive.

---

## Section H: Trap / Trick Questions

**Q54.** Does tiling a kernel always make it compute-bound?
> **No.** Tiling raises AI but the kernel is only compute-bound if AI > ridge point. For small N or small T, tiled may still be memory-bound.

**Q55.** Does increasing tile size T always improve performance?
> **No.** Larger T raises AI and reduces DRAM traffic, but too-large T reduces the number of thread blocks → **low occupancy** → poor latency hiding.

**Q56.** The traffic ratio for naive vs tiled GEMM equals T, right?
> **No.** Ratio = 2N³ / 2N² = **N**, not T. T cancels out because ideal tiling loads each element exactly once regardless of T.

**Q57.** Higher memory bandwidth makes kernels compute-bound, right?
> **No.** Higher BW lowers the ridge point (makes it easier to be compute-bound), but a kernel's AI is fixed by its algorithm. It only becomes compute-bound if AI > new ridge.

**Q58.** The AI formula for tiled GEMM simplifies to N/2, right?
> **No.** 2N³ / (2N²×4) → 2s cancel → N³/(N²×4) → **N/4**, not N/2.

**Q59.** Should the N²×4 write-to-C term be included in GEMM traffic?
> **No** — the assignment counts only reads of input matrices A and B. Writes to C are excluded.

**Q60.** If a kernel is theoretically compute-bound (AI >> ridge), will it always run near peak compute?
> **No.** Other bottlenecks can limit performance: low occupancy, insufficient parallelism, shared memory bank conflicts, or instruction-level bottlenecks. (e.g., tiled T=8 is theoretically compute-bound but achieves only 3.8% of peak due to low occupancy.)
---

## Section I: Oral Exam Style Q&A

**Q61.** What is the roofline model and how do you use it to optimize a kernel?

The roofline model is a visual performance framework that tells you the maximum achievable throughput for a kernel on a specific piece of hardware, and which hardware resource is actually holding it back.

- The X-axis is arithmetic intensity, measured in FLOP per byte, which is how much computation the kernel does per byte it reads from memory. The Y-axis is attainable performance in GFLOP/s.
- There are two ceilings that form the roof shape. The diagonal ceiling rising from left to right is peak memory bandwidth. The flat horizontal ceiling at the top is peak compute throughput.
- Where the two ceilings meet is the ridge point, calculated as peak FLOP/s divided by peak bandwidth. This is the minimum arithmetic intensity needed to fully saturate compute without being held back by memory.
- A kernel to the left of the ridge point is memory-bound. Its attainable performance is arithmetic intensity times bandwidth. The fix is reducing DRAM traffic through tiling, data reuse, or operation fusion.
- A kernel to the right is compute-bound. Its attainable performance is capped at peak compute. The fix shifts to improving occupancy and reducing warp stalls.

A concrete example: on hardware with peak compute of 10 TFLOPS and bandwidth of 320 GB/s, the ridge point is 31.25 FLOP per byte. Naive GEMM has arithmetic intensity of 0.25, which is far to the left of the ridge point, so it is completely memory-bound and only achieves about 80 GFLOP/s out of 10,000 possible. Switching to tiled GEMM raises arithmetic intensity to N/4. At N=128, that is 32 FLOP per byte, which crosses the ridge point and the kernel becomes compute-bound, unlocking full peak compute from the same hardware with no hardware changes at all.

The reason the roofline is so powerful is that it tells you not just how fast a kernel is running, but which resource is the bottleneck, and that is what decides which optimization is even worth trying.

---

**Q62.** What is a systolic array and how does it compute matrix multiplication?

A systolic array is a 2D grid of identical Processing Elements (PEs) that each perform one Multiply-Accumulate (MAC) and pass data rhythmically to their neighbors, similar to a heartbeat pulse moving through the grid.

- Each PE multiplies two values, adds the result to a running accumulator, and passes one or both values to adjacent PEs in the next clock cycle.
- In weight-stationary dataflow, which is what the Google TPU uses, weights are preloaded into each PE once and held fixed for the entire computation. Activations flow in from the left, move rightward through the array, and partial sums accumulate downward until final results drain out at the bottom.
- The key advantage over a general-purpose processor is that each weight is loaded once and reused for many MACs without ever going back to DRAM. On a CPU or GPU you re-fetch values from registers or cache for every operation, but the systolic array chains PEs together so data flows locally between neighbors with no repeated memory access.

The concrete example from the course is the Google TPU Matrix Multiply Unit (MXU), which is a 256 by 256 systolic array containing 65,536 PEs. When multiplying two 256 by 256 matrices, all 65,536 PEs fire simultaneously every clock cycle, and no weight gets loaded from DRAM more than once for the entire operation. The slides show that this design gives the TPU 83 times better performance per watt than a CPU on inference, and that advantage comes directly from the systolic structure eliminating memory traffic.

The whole point of the design is near-zero memory traffic per MAC with every PE busy every cycle, which makes GEMM dramatically more efficient than anything you can do on hardware built for general-purpose workloads.

---

**Q63.** What is SIMT and how does it differ from SIMD?

SIMT, Single Instruction Multiple Threads, is the execution model NVIDIA GPUs use where a single instruction is broadcast to a warp of 32 threads, and all 32 execute it simultaneously on their own private register state and their own data.

- A warp is the basic scheduling unit: 32 threads that run in lockstep. The warp scheduler issues one instruction per clock and all 32 threads execute it at the same time on different data. Each thread has its own program counter and its own registers, so from the programmer's perspective every thread is independent.
- SIMD, Single Instruction Multiple Data, is the CPU equivalent. A single instruction operates on a fixed-width vector of elements, such as 4, 8, or 16 lanes depending on the ISA, and all lanes do exactly the same operation with no independent state per lane.
- The key difference is what happens when code branches. In SIMD all lanes are forced to execute identically. In SIMT threads can branch independently, but when threads within the same warp take different paths, the hardware serializes both paths and masks off whichever side is not active. This is warp divergence, and it costs up to 2x throughput per branch level.
- For handling memory stalls, SIMD relies on out-of-order execution and large caches. SIMT uses zero-overhead warp switching: when one warp stalls waiting on a memory load, the scheduler instantly swaps in another ready warp and keeps the execution units busy without any idle cycles.
- SIMT was coined by NVIDIA and is not part of Flynn's original taxonomy. It extends SIMD by giving each thread its own program counter and register file.

A concrete example is matrix multiply on a GPU. All 32 threads in a warp each compute one output element of the same matrix, running the identical multiply-add instruction on different positions in the matrix. There is no branching, no divergence, and SIMT runs at full throughput. Now consider adding ReLU, which sets negative values to zero. That conditional causes threads with positive results and threads with negative results to diverge inside the same warp, the hardware runs the positive side then the negative side separately with half the threads idle each time, and throughput drops in half.

The bottom line is that SIMT gives you massive parallelism that scales to thousands of threads with the same code, while SIMD is fixed-width and limited to whatever vector width the ISA defines.

---

**Q64.** What is shared memory and why does it matter for GPU performance?

Shared memory is a programmer-managed on-chip scratchpad inside each Streaming Multiprocessor (SM) that all threads within the same thread block can read and write at very low latency.

- The problem it solves is that global memory lives off-chip in DRAM, which has latency hundreds of clock cycles long and finite bandwidth shared across the whole chip. When threads repeatedly fetch from DRAM, they spend most of their time waiting, not computing.
- Shared memory sits physically on the SM, so it operates at far lower latency and much higher per-SM bandwidth than DRAM. On the H100 each SM has about 228 KB of shared memory available.
- The key use case is data reuse across threads. If multiple threads in a block all need the same input values, you load that data once from DRAM into shared memory as a group, and then every thread reads from the fast on-chip copy rather than each thread going back to DRAM independently.
- Shared memory is per-block, so threads in different blocks running on different SMs cannot share data through it. Cross-block communication goes back through slow global memory, which is one of the core architectural constraints that shapes how GPU kernels are written.

The clearest example is tiled GEMM. In naive GEMM every element of matrices A and B gets loaded from DRAM N times over, once for every dot product it participates in, giving arithmetic intensity of just 0.25 FLOP per byte. With tiling, each thread block loads one tile into shared memory and all threads compute their partial results against that local copy. Each element is read from DRAM exactly once, which drops total traffic from 2N cubed bytes down to 2N squared bytes. For N=64, that is a 64 times reduction in DRAM traffic and raises arithmetic intensity from 0.25 up to 16 FLOP per byte, which is the difference between a completely memory-starved kernel and one approaching the ridge point.

The on-chip versus off-chip memory gap is so large that direct programmer control over what stays on chip is essential for performance, and shared memory is how the GPU gives you that control.
---

**Q66.** What is a warp and how does the GPU use it to hide memory latency?

A warp is a group of 32 threads that execute the same instruction simultaneously under the SIMT (Single Instruction Multiple Threads) model. It is the basic unit of scheduling on an NVIDIA GPU.

- Every SM has 4 warp schedulers. Each scheduler tracks a pool of active warps and issues one instruction per clock cycle to whichever warp is ready to run.
- When a warp issues a memory load from DRAM, it gets marked as not ready and the scheduler immediately switches to a different warp that has its data and can keep going. This is zero-overhead context switching (meaning the switch itself costs nothing — no registers are saved or loaded).
- On a CPU, switching threads requires saving the current thread's registers out to memory and loading the next thread's registers back in. The GPU never does this because every active warp's registers are permanently allocated in the register file at all times. Switching is just the scheduler pointing at a different warp on the next clock cycle.
- Occupancy is the ratio of active warps to the maximum possible warps on an SM. Higher occupancy gives the scheduler more warps to choose from, which means more opportunities to cover memory stalls with useful work.

A concrete example: imagine a GEMM kernel where every warp loads a tile from DRAM. The first warp fires off its load and stalls. The scheduler instantly switches to the second warp, which fires its load and stalls. By the time the scheduler cycles back to the first warp, the data has arrived and it can continue computing. Without this switching, every load would freeze the whole SM and most of the execution units would sit idle waiting on memory.

The whole design is built around one idea: instead of making memory faster or adding prediction logic like a CPU does, the GPU keeps thousands of threads in flight so the math units never have to wait.
---

**Q67.** Why does tiled GEMM perform so much better than naive GEMM?

The problem with naive GEMM is that every thread independently goes to DRAM every single time it needs a value from the input matrices. The same element gets loaded over and over again for every dot product it shows up in, so for a large matrix you end up with a huge amount of redundant memory traffic. DRAM is slow and far from the chip, so the kernel just sits there waiting on memory most of the time instead of doing useful math.

Tiled GEMM fixes this by using shared memory. Instead of every thread going to DRAM on its own, the whole thread block cooperates to load one tile into shared memory first, and then everyone does their math against that on-chip copy. Each element only makes the trip from DRAM once. Shared memory is right there on the chip so it is much faster, and because you reuse it many times before moving to the next tile, you are doing way more work per byte you actually move.

The result is that arithmetic intensity goes way up. You went from loading the same data over and over to loading it once and squeezing as much math out of it as possible. That is what moves the kernel from being stuck on the memory-bound side of the roofline toward the ridge point.

The one catch is tile size. Bigger tiles mean more reuse and less DRAM traffic, but they eat up more shared memory, which limits how many thread blocks fit on an SM at once. Fewer blocks means fewer warps, which means less ability to hide latency. So tile size is a balancing act between reuse and occupancy.
