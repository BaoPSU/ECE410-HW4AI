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

> The x-axis is arithmetic intensity, which is how many FLOPs the kernel does per byte it pulls from DRAM, and the y-axis is how much performance you can actually get out of the hardware. There are two ceilings that form the roof shape. The diagonal one is your memory bandwidth limit, so if you're not doing enough math per byte, that's your wall. The flat one at the top is peak compute, and nothing gets past that no matter what.
>
> Where they meet is the ridge point, which is just peak compute divided by peak bandwidth. Any kernel with an arithmetic intensity above that is compute-bound, anything below is memory-bound. If you're memory-bound, attainable performance is AI times bandwidth. If you're compute-bound, you're capped at peak compute.
>
> The important thing to remember is that arithmetic intensity is a property of the algorithm, not the hardware. You can't change it by buying a faster chip. Hardware only shifts where the ridge point lands.
>
> From my K-Means project, the distance kernel had an AI of 1.68 FLOP/byte against a ridge point of 18.23, so it was deeply memory-bound. The fix was moving it to a near-memory PIM chiplet, which pushed the ridge point down until the kernel cleared it.

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

> A Streaming Multiprocessor is the fundamental execution unit of an NVIDIA GPU — the whole GPU is really just a collection of these working in parallel, and every computation I run happens inside one.
>
> Inside each SM, the CUDA cores handle basic scalar math — FP32 and INT32 operations. Sitting alongside them are the Tensor cores, which are purpose-built for MMA, Matrix Multiply Accumulate, running a 4×4 matrix operation in a single clock cycle. Those are what make deep learning workloads feasible on a GPU.
>
> To keep those cores fed, each SM has warp schedulers managing warps — groups of 32 threads running the same instruction in lockstep under SIMT, Single Instruction Multiple Threads. When a warp stalls waiting on a DRAM load, the scheduler instantly switches to another ready warp. That's zero-overhead context switching, and it's how the GPU hides memory latency without any of the prediction logic a CPU uses.
>
> Each SM also has a register file private to each thread — the fastest storage on chip — and shared memory, a programmer-managed on-chip SRAM scratchpad that all threads in a block can use together to reuse data without going back out to slow global memory. Load/store units move data between the SM and the rest of the memory hierarchy, and Special Function Units handle transcendental math like sin, cos, and exp.
>
> The main takeaway is the whole design is built around one idea: keep the CUDA cores and Tensor cores busy at all times by switching warps to cover for inevitable memory stalls.

**Q30b.** What does an SM do when a warp is stalled waiting for memory?

> So when a warp issues a load from DRAM, it gets marked as not ready and the warp scheduler immediately switches to another warp that already has its data and can keep going. That's zero-overhead context switching — and the reason it costs nothing is that every active warp's registers are permanently live in the register file the whole time, so the scheduler just points at a different warp on the next clock cycle.
>
> That's completely different from a CPU where switching threads means saving registers out to memory and loading the next thread's state back in. The GPU never has to do any of that — it just keeps the CUDA cores busy instead of freezing and waiting.
>
> And that's actually why occupancy matters — the more active warps you have, the more options the scheduler has when one stalls. If occupancy is low, the scheduler runs out of ready warps and the execution units just sit idle waiting on memory.

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

> So HW/SW co-design is the idea that you design your hardware and software at the same time, because each one shapes the other. You don't build the chip first and figure out the algorithm later, or write the algorithm first and hope the hardware can handle it.
>
> The reason that matters is if I design a chip without knowing what algorithm is running on it, I'm going to get things wrong — the memory hierarchy, the datapath width, how much on-chip SRAM I need. And if I write the algorithm without knowing what the hardware looks like, I'm going to be bottlenecked by things I didn't have to be bottlenecked by.
>
> Where it pays off the most is memory. Moving data off-chip is way more expensive than doing actual computation — energy-wise, latency-wise, bandwidth-wise. So the algorithm needs to be structured to minimize those trips, and the hardware needs to be sized to actually support that.
>
> From my K-Means project — the distance kernel was memory-bound at an arithmetic intensity of 1.68 FLOP/byte against a ridge point of 18.23. The fix wasn't better software or a faster chip in isolation. The fix was co-design: offload the kernel to a near-memory PIM chiplet where the bandwidth clears the ridge point. That's co-design in practice.
>
> The best systems are the ones where the hardware and the algorithm were designed around each other from the start.

**Q40b.** Why does co-design achieve better perf/watt than CPU for deep learning?

> CPUs are built for general-purpose workloads, branch prediction, out-of-order execution, big caches. And if you look at a Deep Neural Network (DNN) workload, all of that logic is just wasted area and wasted power, because DNN workloads are regular, data-parallel, and dominated by GEMM. There's no branching to predict, no irregular memory access. It's just matrix multiply over and over.
>
> Co-designed hardware like the TPU or GPU Tensor cores strips all that general-purpose stuff out and dedicates the silicon directly to matrix multiply. Every transistor is doing work that actually matters for the algorithm. You're not burning power on prediction logic that a neural network doesn't need.
>
> The result is you get dramatically more useful compute per watt because you're not paying for hardware that was never going to help you in the first place.

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

> So the roofline model is a performance tool that tells you the maximum performance a kernel can achieve on specific hardware, and which resource is actually the bottleneck.
>
> The x-axis is arithmetic intensity, which is FLOPs divided by bytes moved from DRAM, and the y-axis is attainable performance in GFLOP/s. There are two ceilings. The diagonal one is your memory bandwidth limit and the flat one at the top is peak compute. Where they meet is the ridge point, which is peak compute divided by peak bandwidth. That's the minimum arithmetic intensity you need to be compute-bound.
>
> The important thing to understand is that arithmetic intensity is a property of the algorithm, not the hardware. You can't change it by buying a faster chip. Hardware only moves the ridge point — higher bandwidth lowers it, higher peak compute raises it.
>
> If a kernel is left of the ridge point it's memory-bound, and attainable performance is AI times bandwidth. The fix is reducing DRAM traffic through tiling or data reuse. If it's right of the ridge point it's compute-bound and capped at peak compute, so the fix shifts to improving occupancy and reducing warp stalls.
>
> What makes the roofline powerful is it tells you not just how fast a kernel is running, but which resource is the bottleneck, and that decides which optimization is even worth trying.
>
> From my K-Means project, the distance kernel had an AI of 1.68 FLOP/byte against a ridge point of 18.23, so it was deeply memory-bound. The fix was offloading to a near-memory PIM chiplet, which raised the effective bandwidth enough to push the kernel past the ridge point.

---

**Q62.** What is a systolic array and how does it compute matrix multiplication?

> So a systolic array is a 2D grid of identical Processing Elements, or PEs, where each one does a single Multiply-Accumulate operation and passes data to its neighbors in a rhythmic pulse, kind of like a heartbeat moving through the grid.
>
> Each PE multiplies two values, adds the result to a running accumulator, and then passes one or both values to the next PE on the next clock cycle. In weight-stationary dataflow, which is what the Google TPU uses, weights get preloaded into each PE once and stay fixed for the entire computation. Activations flow in from the left, move across the array, and partial sums accumulate downward until the final results drain out at the bottom.
>
> The key advantage over a general-purpose processor is that each weight is loaded from DRAM exactly once and reused for many MACs. On a CPU or GPU you keep going back to memory for values, but the systolic array chains PEs together so data flows locally between neighbors with no repeated memory access.
>
> The example from the course is the Google TPU Matrix Multiply Unit, which is a 256 by 256 systolic array with 65,536 PEs. When multiplying two 256 by 256 matrices, all 65,536 PEs fire every clock cycle and no weight gets loaded from DRAM more than once for the entire operation.
>
> The whole point is near-zero memory traffic per MAC with every PE busy every cycle, which makes GEMM way more efficient than anything you can do on general-purpose hardware.

---

**Q63.** What is SIMT and how does it differ from SIMD?

> So SIMT stands for Single Instruction Multiple Threads, and it's the execution model NVIDIA GPUs use where a single instruction gets broadcast to a warp of 32 threads and all 32 execute it simultaneously on their own private data and their own registers.
>
> A warp is that basic group of 32 threads running in lockstep. The warp scheduler issues one instruction per clock and every thread in the warp executes it at the same time on different data. Each thread has its own program counter and its own register file, so from the programmer's perspective every thread is completely independent.
>
> SIMD, Single Instruction Multiple Data, is the CPU version of this. A single instruction operates on a fixed-width vector, like 4, 8, or 16 lanes depending on the ISA (Instruction Set Architecture), and all lanes do exactly the same thing with no independent state per lane.
>
> The key difference is what happens at a branch. In SIMD all lanes are forced to do the same thing. In SIMT threads can branch independently, but if threads in the same warp take different paths the hardware serializes both paths and masks off whichever side isn't active. That's warp divergence and it costs up to 2x throughput per branch level.
>
> The other big difference is how they handle memory stalls. SIMD relies on out-of-order execution and caches. SIMT uses zero-overhead warp switching — when one warp stalls the scheduler instantly swaps in another ready warp and keeps the execution units busy.

---

**Q64.** What is shared memory and why does it matter for GPU performance?

> So shared memory is a programmer-managed on-chip scratchpad inside each SM that all threads within the same thread block can read and write at very low latency.
>
> The problem it solves is that global memory lives off-chip in DRAM, which has latency hundreds of clock cycles long and limited bandwidth shared across the whole chip. When threads keep going back to DRAM for data, they spend most of their time waiting, not computing.
>
> Shared memory sits physically on the SM, so it's much faster and has way higher bandwidth than DRAM. The key use case is data reuse across threads — if multiple threads in a block all need the same values, you load that data once from DRAM into shared memory as a group, and then every thread reads from the fast on-chip copy instead of each thread making its own trip to DRAM.
>
> One important constraint is that shared memory is per-block. Threads in different blocks on different SMs can't share data through it. Cross-block communication has to go back through slow global memory, which is one of the core architectural constraints that shapes how GPU kernels are written.
>
> The clearest example is tiled GEMM. In naive GEMM the same element gets loaded from DRAM over and over for every dot product it shows up in. With tiling, the thread block loads one tile into shared memory once, everyone computes against that on-chip copy, and each element only makes the trip from DRAM once. That's what drops traffic from 2N cubed bytes down to 2N squared bytes and pushes arithmetic intensity from 0.25 up to N/4.
---

**Q66.** What is a warp and how does the GPU use it to hide memory latency?

> So a warp is a group of 32 threads that execute the same instruction at the same time under SIMT, Single Instruction Multiple Threads. It's the basic scheduling unit on an NVIDIA GPU.
>
> Every SM has warp schedulers that each track a group of active warps and issue one instruction per clock to whichever warp is ready to run. When a warp issues a memory load from DRAM, it gets marked as not ready and the scheduler immediately switches to a different warp that has its data and can keep going. That's zero-overhead context switching — the switch itself costs nothing because every active warp's registers are permanently allocated in the register file at all times. The scheduler just points at a different warp on the next clock cycle.
>
> That's completely different from a CPU where switching threads means saving the current thread's registers out to memory and loading the next thread's back in. The GPU never has to do any of that.
>
> Occupancy is the ratio of active warps to the maximum possible warps on an SM. Higher occupancy gives the scheduler more warps to choose from, which means more opportunities to cover memory stalls with useful work. If occupancy is low, the scheduler runs out of ready warps and the execution units just sit idle.
---

**Q67.** Why does tiled GEMM perform so much better than naive GEMM?

> So the problem with naive GEMM is that every thread independently goes to DRAM every single time it needs a value from the input matrices. Think of it like going to your locker every single time you need a number — your locker is far away, so most of your time is spent walking back and forth instead of actually doing math. The same element gets loaded over and over for every dot product it shows up in, which means a huge amount of redundant memory traffic.
>
> Tiled GEMM fixes this with shared memory. Instead of every thread making its own trip to DRAM, the whole thread block cooperates to grab a chunk of values and bring them on-chip first, then everyone does their math against that local copy. Way less walking, way more math. Each element only makes the trip from DRAM once, and you squeeze as many calculations out of it as possible before going back for more.
>
> The result is arithmetic intensity goes from 0.25 FLOP/byte in naive up to N/4 in tiled. The bigger N is, the more math you can squeeze out of each tile before going back — so the advantage of tiling grows with N.
>
> The one tradeoff is tile size. Bigger tiles mean more reuse and less DRAM traffic, but they eat up more shared memory, which limits how many thread blocks fit on an SM at once and hurts occupancy.
