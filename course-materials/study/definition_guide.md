# Ultimate Definition Guide — ECE 410/510

All definitions are grounded in course slides weeks 1 through 5. Relationships between concepts are noted under each entry.

---

## Foundational Concepts

**AI (Artificial Intelligence)**
The broad field of making machines perform tasks that require human intelligence. The ultimate goal is AGI, Artificial General Intelligence. All ML is AI, but not all AI is ML.

**ML (Machine Learning)**
A subset of AI focused on algorithms that improve through experience, such as neural networks. Related to AI as a more specific category.

**HW/SW Co-design**
Concurrent design of hardware and software across all layers of the compute stack. The core idea is that hardware and algorithm decisions shape each other, so designing them separately leads to avoidable bottlenecks. Started in the 1990s. Connects to PPAC, roofline, arithmetic intensity, and memory hierarchy.

**PPAC (Performance, Power, Area, Cost)**
The four axes of every hardware design tradeoff. Improving one typically hurts another. Every architectural decision in this course, from precision formats to dataflow strategies, is a PPAC tradeoff.

**No Free Lunch Theorem**
Formalized by Wolpert and Macready, 1997. Averaged across all possible problems, all optimization algorithms perform equally. Specialized hardware works well for specific domains but fails in others. Justifies domain-specific accelerators like the TPU.

---

## Compute Fundamentals

**MAC (Multiply-Accumulate)**
One multiply plus one add. This equals 2 FLOPs. It is the fundamental operation in neural networks. Every dot product, every matrix multiply, every convolution breaks down into MACs. Connects to CUDA cores, Tensor cores, systolic array PEs, and the MXU.

**GEMM (General Matrix-Matrix Multiply)**
The dominant operation in neural networks. Fully connected layers, convolutions, attention projections, embeddings, and LSTM gates all reduce to GEMM. "When someone says a GPU is good at deep learning, what they really mean is it is good at GEMM." Connects to Tensor cores, tiled GEMM, systolic arrays, and TPU MXU.

**Compute Kernel**
A single computational routine that runs on a processor or GPU. It is the unit of work submitted to hardware: takes inputs, performs a defined computation, produces outputs. A neural network is a sequence of kernel launches. Examples include matrix multiply, convolution, and softmax.

**FLOPs (Floating Point Operations)**
The count of floating point operations a kernel performs. One MAC is 2 FLOPs. Used in the numerator of arithmetic intensity.

---

## Roofline and Performance Analysis

**Arithmetic Intensity (AI)**
AI = FLOPs divided by bytes transferred to and from memory. Unit is FLOP/byte. Characterizes whether a workload is bottlenecked by compute throughput or memory bandwidth. By itself it says nothing about bottlenecks — you need the roofline for that. K-Means distance kernel AI is 1.68 FLOP/byte.

**Roofline Model**
Introduced by Williams, Waterman, and Patterson, 2009. A visual and analytical framework for predicting achievable performance of a kernel on given hardware. Y-axis is achievable performance in GFLOP/s. X-axis is arithmetic intensity in FLOP/byte. Two ceilings: peak compute (horizontal) and peak memory bandwidth (diagonal). Connects to arithmetic intensity, ridge point, memory-bound, compute-bound.

**Ridge Point**
Where the memory bandwidth ceiling and compute ceiling meet on the roofline. Calculated as peak compute divided by peak memory bandwidth. The minimum arithmetic intensity a kernel needs to be compute-bound. K-Means ridge point is 18.23 FLOP/byte. A kernel to the left of the ridge point is memory-bound. A kernel to the right is compute-bound.

**Memory-bound**
A kernel whose performance is limited by memory bandwidth, not compute throughput. It sits to the left of the ridge point on the roofline. The fix is to increase arithmetic intensity, improve data reuse, or move computation closer to memory. K-Means distance kernel at 1.68 FLOP/byte is memory-bound.

**Compute-bound**
A kernel whose performance is limited by peak compute throughput, not memory bandwidth. It sits to the right of the ridge point. If it is below the compute ceiling, the fix is to improve occupancy, instruction-level parallelism, or Tensor core utilization.

---

## GPU Architecture

**SM (Streaming Multiprocessor)**
The fundamental execution unit of an NVIDIA GPU. The whole GPU is a collection of SMs working in parallel. Each SM contains CUDA cores, Tensor cores, warp schedulers, a register file, and shared memory. Every computation runs inside an SM. Connects to warp, SIMT, shared memory, register file, and CUDA programming model.

**CUDA Core**
The scalar compute unit inside an SM. Handles FP32 and INT32 arithmetic — additions, multiplications, divisions, comparisons, bitwise operations. Also includes SFUs, Special Function Units, for transcendental functions like sine, cosine, and exponential. Contrast with Tensor cores which operate on matrices.

**Tensor Core**
Purpose-built for MMA, Matrix Multiply Accumulate. Computes D = A times B plus C on small matrices in a single clock cycle. Makes deep learning throughput feasible on a GPU. Requires matrix dimensions to be multiples of 16 to activate, otherwise the hardware falls back to scalar CUDA cores. Connects to GEMM, tiled GEMM, and reduced precision formats.

**Warp**
A group of 32 threads that execute the same instruction simultaneously under SIMT. The fundamental scheduling unit on the GPU. When a warp stalls on a DRAM load, the warp scheduler instantly switches to another ready warp at zero overhead. This is how the GPU hides memory latency. AMD calls the equivalent grouping a wavefront.

**Warp Scheduler**
Decides which warps are ready, allocates compute resources, and manages zero-overhead warp context switching. The mechanism that hides memory latency on a GPU without any prediction logic. Connects to warp, occupancy, and SIMT.

**Warp Divergence**
When threads in a warp take different branches, the GPU serializes both paths and masks off idle threads. Throughput can drop significantly per branch level. Avoid control flow that depends on thread ID. Connects to SIMT and performance optimization.

**Occupancy**
Active warps divided by maximum warps per SM. Low occupancy means the warp scheduler has few ready warps to switch to, so memory latency is not hidden and compute units sit idle. Occupancy is limited by register count, shared memory usage, and block size. Connects to warp, SM, and performance optimization.

**SIMT (Single Instruction Multiple Threads)**
Coined by NVIDIA, Lindholm et al., ISCA 2008. The GPU execution model where 32 threads in a warp execute the same instruction in lockstep, but each thread has its own program counter, register state, and stack. Threads can diverge at branches, with divergent paths serialized. More flexible than SIMD because of per-thread state. Connects to warp, SIMD, and Flynn's taxonomy.

**SIMD (Single Instruction Multiple Data)**
The CPU vector execution model. All lanes execute the same operation on a fixed vector width determined by the ISA, such as SSE or AVX. No per-lane program counter or register state. Less flexible than SIMT but simpler hardware. Connects to SIMT, Flynn's taxonomy, and CPU architecture.

---

## GPU Memory Hierarchy

**Register File**
The fastest storage on the GPU, private per thread. Located inside the SM. Every thread's local variables live here. High register usage per thread reduces occupancy by limiting how many warps can be active simultaneously.

**Shared Memory**
On-chip SRAM scratchpad inside the SM, programmer-managed, shared within a thread block. Much faster than global memory. Used to stage tiles of data for tiled GEMM, enabling data reuse within a block without going back to HBM. Connects to tiled GEMM, thread block, and roofline.

**L1 Cache**
Unified with shared memory on modern NVIDIA GPUs, hardware-managed. Faster than L2 but not programmer-controlled like shared memory.

**L2 Cache**
Shared across all SMs on the GPU. Sits between the SMs and HBM. Used as the staging level for thread-block tiles in tiled GEMM.

**HBM (High Bandwidth Memory)**
High Bandwidth Memory. The large off-chip DRAM on the GPU, accessible by all threads but slow relative to on-chip memory. The memory bandwidth ceiling on the roofline comes from HBM bandwidth. Avoiding repeated HBM accesses is the core goal of tiled GEMM and data reuse strategies.

---

## CUDA Programming Model

**CUDA (Compute Unified Device Architecture)**
NVIDIA's parallel computing platform. Serial code runs on the host CPU, parallel code runs on the device GPU. A CUDA kernel is defined with the global keyword and launched with a grid and block configuration.

**GPGPU (General-Purpose computing on Graphics Processing Units)**
Using a GPU for non-graphics computation. CUDA enables GPGPU by exposing the GPU as a programmable parallel processor.

**Thread**
The smallest unit of execution in CUDA. Executes on a single CUDA core. Has its own register state and program counter under SIMT.

**Thread Block**
Up to 1024 threads grouped together, assigned to one SM. Shares that SM's shared memory. Composed of multiple warps. Threads within a block can synchronize with each other.

**Grid**
A collection of thread blocks distributed across all SMs on the GPU. The highest-level organization of a CUDA kernel launch. More SMs equals less time automatically because blocks are independent.

**Tiled GEMM**
An optimization of naive GEMM that uses shared memory to stage tiles of the input matrices. Naive GEMM reloads each element many times from HBM, resulting in high memory traffic. Tiled GEMM loads each element exactly once into shared memory and reuses it within the block, dramatically increasing arithmetic intensity. Three levels of tiling on GPU: HBM tile, L2 tile, shared memory tile, and register tile. Connects to arithmetic intensity, roofline, shared memory, and Tensor cores.

---

## Precision Formats

**FP32 (32-bit Floating Point)**
Full precision. 1 sign bit, 8 exponent bits, 23 mantissa bits. The standard format for training and a baseline for comparison. Lower throughput than reduced precision formats.

**FP16 (16-bit Floating Point)**
Half precision. Smaller exponent range than FP32, which can cause overflow and underflow during training, requiring loss scaling. Tensor core native format on NVIDIA GPUs. Higher throughput than FP32.

**BF16 (Brain Float 16)**
Developed by Google Brain. Keeps the full 8-bit exponent from FP32, giving it the same dynamic range, but sacrifices mantissa precision. Drop-in replacement for FP32 in most training workloads. Avoids the overflow instability of FP16. Converting BF16 to FP32 is just adding zeros to the mantissa. Connects to FP32, FP16, and training stability.

**INT8 (8-bit Integer)**
8-bit integer format used for inference only. Higher throughput than FP16 at the same die area. Not suitable for training because gradients require floating point range.

**FP4 / NVFP4**
4-bit floating point format using E2M1, 2 exponent bits and 1 mantissa bit. Only 16 distinct representable values. NVFP4 uses block scaling, grouping 16 values and assigning each block a shared FP8 scale factor, so the real value equals FP4 value times FP8 block scale times FP32 tensor scale. Used for LLM inference on Blackwell B200. Highest throughput, lowest precision. Connects to BF16, quantization, and Blackwell architecture.

---

## Systolic Arrays and TPU

**Systolic Array**
A 2D grid of identical Processing Elements that rhythmically compute and pass data to their neighbors. Named for the analogy to a heartbeat. Each PE performs one MAC per clock cycle and forwards data to the next PE. Data moves PE to PE locally, eliminating repeated DRAM reads. Connects to GEMM, MAC, TPU MXU, and memory bandwidth.

**PE (Processing Element)**
The individual compute unit inside a systolic array. Performs one MAC, adds to a running partial sum, and forwards both inputs to neighboring PEs. Identical across the array.

**Weight Stationary**
A systolic array dataflow where weights are held fixed in PEs while activations and partial sums stream through. Maximizes weight reuse. Used in Google TPU v1 through v4. Best for layers reused across many inputs.

**Output Stationary**
A systolic array dataflow where each PE holds and accumulates one output element. Weights and activations both stream through. Minimizes accumulator writes.

**Row Stationary**
A systolic array dataflow where one row of filter coefficients stays in each PE, activations slide through, and partial sums accumulate. Maximizes reuse of all data types. Best for diverse layer shapes. Used in MIT Eyeriss.

**TPU (Tensor Processing Unit)**
Google's custom ASIC for ML workloads. Only available through Google Cloud. Main component is the MXU. More power-efficient than a GPU but more specialized. Primary software framework is TensorFlow. Connects to systolic array, MXU, ASIC, and HW/SW co-design.

**MXU (Matrix Multiply Unit)**
The core compute block of a TPU. Implemented as a large systolic array of PEs each doing one MAC per cycle. Receives input from the unified buffer and weighted FIFO. Connects to systolic array, MAC, and TPU.

---

## Transformers

**Transformer**
Introduced by Vaswani et al., "Attention Is All You Need," 2017. A neural network architecture designed to model relationships between elements in a sequence. Explicitly non-recurrent. Replaces recurrence with self-attention. Made self-supervised learning possible. Connects to self-attention, GEMM, and GPU Tensor cores.

**Self-Attention**
Processes all tokens simultaneously in parallel. Connects every token directly to every other token in one operation with no hidden state. Uses three projections per token — Q, K, and V. Formula is softmax of QK-transpose divided by square root of d_k, then multiplied by V. All operations reduce to GEMM. Connects to transformer, Q/K/V, and GEMM.

**Q, K, V (Query, Key, Value)**
The three projections used in self-attention. Q is "what am I looking for," K is "what do I offer," and V is "what do I actually contribute if selected." Each is a linear projection of the input token. Computed via GEMM. Connects to self-attention and transformer.

**Positional Encoding**
Added to token embeddings to give the transformer a sense of order, since self-attention has no notion of position. Implemented using sine and cosine functions, computed via GPU SFUs.

---

## VLSI and EDA

**VLSI (Very Large Scale Integration)**
The field of placing billions of transistors on a chip. VLSI is the field; ASICs are the product.

**ASIC (Application-Specific Integrated Circuit)**
A chip designed for one specific function. More power-efficient than a GPU for that function but inflexible. The TPU is an ASIC. Connects to VLSI, TPU, and PPAC.

**RTL (Register Transfer Level)**
A level of hardware abstraction describing how data moves between registers each clock cycle. Written in HDL like Verilog or SystemVerilog. Sits between the algorithmic level and the gate level in the design hierarchy.

**EDA (Electronic Design Automation)**
Tools that automate synthesis, place-and-route, and verification of chip designs. Key tools in this course include Icarus Verilog and Verilator for simulation, Yosys for synthesis, and cocotb for Python-based testbenches.

**cocotb**
Coroutine-based Co-simulation Test Bench. Lets you write GPU testbenches in Python using async and await, interfacing with HDL simulators via VPI. Used in this course to verify the kmeans_dist_core.sv.

---

## K-Means Project Terms

**K-Means Image Quantization Accelerator**
The semester project. Reduces any RGB image to K equals 16 colors by clustering pixels in 3D RGB space. The bottleneck is the distance kernel, which computes squared Euclidean distance from each pixel to each centroid.

**Distance Kernel**
The dominant kernel in K-Means. Computes squared Euclidean distance between a pixel and all centroids to find the nearest one. Memory-bound at an arithmetic intensity of 1.68 FLOP/byte against a ridge point of 18.23. The fix is offloading to a near-memory PIM chiplet.

**PIM (Processing-in-Memory)**
Processing-in-Memory. Places compute logic near or inside the memory, dramatically increasing available memory bandwidth. Used in the K-Means project to clear the ridge point for the memory-bound distance kernel. Connects to roofline, arithmetic intensity, memory-bound, and HW/SW co-design.

**kmeans_dist_core.sv**
The synthesizable SystemVerilog integer distance core. Parameters include K equals 16 centroids, D equals 3 dimensions, 8-bit input data, and 20-bit integer accumulators. The wider accumulators prevent overflow during the squared distance summation, since the maximum squared distance of 3 times 255 squared fits in 18 bits. Fully combinational distance and argmin logic with registered output.

**20-bit Accumulator**
Used in kmeans_dist_core.sv because the maximum possible squared Euclidean distance in 8-bit RGB space is 3 times 255 squared, which requires at least 18 bits. INT8, INT16, FP16, and BF16 all overflow or lose precision. FP32 or 20-bit integer are the correct choices. This is the same precision tradeoff reasoning behind FP4 block scaling in LLM inference.
