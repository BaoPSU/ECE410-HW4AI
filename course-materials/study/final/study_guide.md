# ECE 410/510 — Final Study Guide
**Bao Nguyen | Portland State University | Spring 2026**

Built directly from Teuscher's official cheat sheet (`cheat_sheet_official.md`). This is the
**cumulative final** — it spans the whole term, bridging my quiz1 material (weeks 1–4) and quiz2
material (weeks 5–8).

## How to use this guide

Each of the 13 foundational concepts is written in the **4-step oral-exam structure** from
`../answer_method.md`, because the final is interview-style:

1. **Definition** — one sentence on what it *is* (spell out acronyms).
2. **Components / mechanics** — the moving parts, each with a role, flowing not listed.
3. **Concrete example** — something specific, ideally from my K-Means project or a codefest.
4. **Big picture** — one sentence opened with "The point is" / "Essentially" / "Basically".

The **xref** line under each concept tells you where in my existing notes to go deeper.
Target: 8/10. Hit all four steps, say the concrete example out loud, then stop.

> **One number that changed since quiz materials:** the final synthesizable core uses
> **18-bit** integer accumulators (`DIST_W=18`), dropped from 20 after the CF07 STA showed the
> top two bits were always zero. Older study files still say "20-bit" — use **18** on the final.

---

# Part 1 — The 13 foundational concepts

## 1. Hardware–software co-design [1]
*xref: `quiz1/cheatsheet.md` §13–15, `definition_guide.md` (HW/SW Co-design, PPAC), `project/design_log.md`*

1. **Definition.** Hardware–software co-design is the concurrent design of the algorithm,
   compiler, and silicon together across the whole stack, instead of freezing one and optimizing
   the others around it.
2. **Mechanics.** You start from the workload, profile where the time and energy actually go, and
   then let that profile drive every layer at once — the numeric precision the algorithm needs,
   the dataflow the compiler emits, and the memory hierarchy the silicon provides. Each decision
   is a PPAC trade-off (performance, power, area, cost), so co-design is really the discipline of
   moving the bottleneck, not just locally optimizing a layer that wasn't the limiter.
3. **Example.** In my K-Means project I profiled the baseline and found the distance kernel was
   46% of runtime *and* memory-bound at AI = 1.68 FLOP/byte. Co-design said the fix isn't a faster
   ALU — it's moving compute next to memory, so I offloaded that one kernel to a near-memory PIM
   chiplet while leaving the rest on the host CPU.
4. **Big picture.** The point is co-design is the organizing idea of the whole course: you only
   capture the full speedup when the algorithm, the numerics, and the chip are shaped to fit each
   other.

## 2. Moore's law, Dennard scaling, and their end [2]
*xref: thin in my notes — see `gap_analysis.md`; Moore mentioned in `quiz2/study_guide.md`*

1. **Definition.** Moore's law is the historical doubling of transistor density about every two
   years; Dennard scaling was the companion rule that power density stayed constant as transistors
   shrank, because voltage and current scaled down with size.
2. **Mechanics.** While both held, every generation gave you more *and* faster transistors at the
   same power budget — a free lunch. Dennard scaling broke around 2005 (leakage and voltage
   floors stopped voltage from dropping further), so shrinking transistors no longer cut power per
   transistor; that's the origin of the "power wall" and the end of frequency scaling. Moore's law
   itself has since slowed and gotten far more expensive per transistor.
3. **Example.** This is exactly why the course exists: my CPU-only K-Means baseline is ~9 s/image
   on an i9-12900H and can't be rescued by waiting for a faster clock. The gain has to come from
   specialization — a PIM chiplet — not from raw scaling.
4. **Big picture.** Essentially, when you can't get speed from the process node anymore, you get it
   from architecture, which is why specialized AI hardware replaced "just wait for next year's CPU."

## 3. The memory wall and data locality [3]
*xref: `quiz1/cheatsheet.md` §1, `definition_guide.md` (memory wall), `quiz2/study_guide.md` Unit 5*

1. **Definition.** The memory wall is the widening gap between how fast a processor can compute and
   how fast memory can feed it, so data *movement*, not arithmetic, dominates both time and energy.
2. **Mechanics.** Compute throughput grew far faster than DRAM bandwidth and latency, so modern
   kernels spend most of their cycles waiting on memory. The energy side is even starker: an
   off-chip DRAM access costs on the order of 100× the latency and ~170× the energy of an on-chip
   SRAM access. So nearly every accelerator is fundamentally a scheme to keep data close to compute
   — caches, scratchpads, weight reuse, or moving compute into memory entirely.
3. **Example.** My distance kernel's roofline puts it well left of the ridge point (1.68 vs
   18.23 FLOP/byte) — it's starved for bytes, the memory wall in one diagram. The PIM fix doesn't
   add FLOPs; it raises bandwidth (HBM3-class) so the same arithmetic finally has data to chew on.
4. **Big picture.** The point is the memory wall is *the* reason AI hardware looks the way it does:
   the whole game is minimizing how far data has to travel.

## 4. Matrix multiply: MAC, dot product, GEMM [4]
*xref: `definition_guide.md` (MAC, GEMM, Compute Kernel), `quiz1/cheatsheet.md`, CF04 (MAC HDL)*

1. **Definition.** A multiply-accumulate (MAC) is one multiply plus one add (2 FLOPs); a string of
   MACs forms a dot product, and a grid of dot products forms a general matrix-matrix multiply
   (GEMM), which sits under nearly every neural-network layer.
2. **Mechanics.** A fully connected layer *is* a matrix-vector product; a convolution lowers to a
   GEMM (im2col); attention is three big GEMMs (QKᵀ, softmax-weighting, ×V). So "is this chip good
   at deep learning?" collapses to "is it good at GEMM?" — which is why accelerators put a big
   matrix engine at their center and surround it with memory to keep it fed.
3. **Example.** My compute core is built on the same MAC discipline I practiced in CF04 — it
   computes a squared Euclidean distance, which is itself a dot product of the difference vector
   with itself, accumulated in an 18-bit integer accumulator.
4. **Big picture.** Basically, deep learning is a mountain of MACs, so the MAC and its scaled-up
   form GEMM are the atom and the molecule that all this hardware is built to execute fast.

## 5. Arithmetic intensity [5]
*xref: `quiz1/cheatsheet.md` §2–3, `definition_guide.md` (Arithmetic Intensity), CF02*

1. **Definition.** Arithmetic intensity (AI) is the ratio of compute operations to bytes moved from
   memory, in FLOP/byte — it characterizes whether a kernel is fundamentally compute-limited or
   memory-limited.
2. **Mechanics.** High-AI kernels reuse each byte many times, so the compute units stay busy and
   the chip approaches its peak FLOP/s. Low-AI kernels touch each byte once or twice, so the
   compute units sit idle waiting on the memory bus. Crucially, AI by itself doesn't name the
   bottleneck — you compare it against the hardware's ridge point to do that.
3. **Example.** My distance kernel is AI = 1.68 FLOP/byte: for every pixel it streams in, it does
   only a handful of subtract-square-add ops before moving on. That's why it's bandwidth-starved
   and why bolting on a faster ALU would do nothing.
4. **Big picture.** The point is AI is the single number that tells you whether to spend your
   budget on more compute or more bandwidth — get it wrong and you optimize the wrong wall.

## 6. The roofline model [5]
*xref: `quiz1/cheatsheet.md` §2–3, `quiz1/study_guide.md` Unit on roofline, `project/m4/bench/`*

1. **Definition.** The roofline model is a single log-log plot of achievable performance (FLOP/s)
   versus arithmetic intensity, capped by two ceilings: a flat peak-compute line and a sloped
   peak-memory-bandwidth line that meet at the ridge point.
2. **Mechanics.** The sloped part is `performance = bandwidth × AI` — bandwidth-limited; the flat
   part is the chip's peak FLOP/s — compute-limited. Where they cross is the ridge point, the AI at
   which the machine becomes balanced. Plot your kernel's AI as a vertical line: land left of the
   ridge and you're memory-bound (buy bandwidth or raise reuse); land right and you're compute-bound
   (buy FLOPs or reduce precision). Modern GPUs keep pushing the ridge point rightward, which
   actually *deepens* the memory wall for low-AI kernels.
3. **Example.** For my K-Means kernel the ridge point is 18.23 FLOP/byte and my AI is 1.68, so I
   sit far left — provably memory-bound. That one diagram is the entire justification for choosing a
   near-memory PIM architecture instead of a bigger compute unit.
4. **Big picture.** Essentially the roofline turns "compute or memory?" into one picture, and it
   tells the hardware designer and the software optimizer the same truth at the same time.

## 7. Parallelism and the GPU (SIMT) [6]
*xref: `quiz1/cheatsheet.md` §6–10, `quiz1/study_guide.md` (GPU/SM/warps), CF03 (CUDA GEMM)*

1. **Definition.** A GPU exploits data parallelism through the SIMT model — single instruction,
   multiple threads — running thousands of lightweight threads so that while some stall on memory,
   others compute, hiding latency rather than avoiding it.
2. **Mechanics.** Threads are grouped into warps (32) that execute one instruction in lockstep on
   the CUDA cores of a Streaming Multiprocessor; warp schedulers swap in a ready warp the instant
   the running one stalls, which is *latency hiding through occupancy*. Two things make or break
   speed: keeping enough warps resident (occupancy) and coalescing memory accesses so a warp's 32
   loads hit one contiguous transaction. Tensor cores add a dense matrix-MAC unit on top for GEMM.
3. **Example.** In CF03 I wrote naive then tiled CUDA GEMM and watched DRAM traffic drop when
   tiling raised reuse — the same coalescing/occupancy lessons that explain why a GPU is fast on
   GEMM but not on my scattered, low-AI distance kernel.
4. **Big picture.** The point is the GPU doesn't beat latency, it *outruns* it by always having
   another warp ready to run, which is why SIMT maps so naturally onto the massive parallelism of
   GEMM.

## 8. Domain-specific architecture and the TPU [7]
*xref: `quiz2/cheatsheet.md` §2, `quiz2/study_guide.md` Unit 1, `quiz2/practice_questions.md` §A*

1. **Definition.** A domain-specific architecture is a processor purpose-built for one workload
   class; Google's Tensor Processing Unit is the canonical example, built around a large systolic
   matrix unit (MXU) for neural-network inference.
2. **Mechanics.** A CPU spends most of its silicon on caches, branch predictors, and out-of-order
   logic to make *one* thread fast. The TPU throws all of that out and spends the area on a
   256×256 MXU — 65,536 MACs per cycle — fed by a Unified Buffer and Weight FIFO, running mostly
   INT8. No general-purpose overhead, weight-stationary dataflow to kill weight re-fetch, and low
   precision together give it order-of-magnitude better perf/watt (~83× over a CPU for inference).
3. **Example.** My K-Means accelerator is a tiny domain-specific architecture by the same logic: I
   don't build a general processor, I build exactly the distance-and-argmin datapath the workload
   needs and nothing else.
4. **Big picture.** Essentially, when Moore's law stops giving you gains for free, specialization
   buys them back — you trade flexibility for efficiency on the one workload that matters.

## 9. Systolic arrays and dataflow [8]
*xref: `quiz2/cheatsheet.md` §3 + §3a (CF5 trace), `quiz2/study_guide.md` Unit 1, CF05*

1. **Definition.** A systolic array is a grid of simple processing elements that rhythmically pass
   operands to their neighbors each clock, computing a matrix product with maximal data reuse — the
   name comes from the heartbeat-like pulse of data through the array.
2. **Mechanics.** Each PE does one MAC and forwards operands on, so a single value read from memory
   feeds many MACs as it propagates — that's the energy win, because memory accesses (not
   multiplies) dominate energy. The *dataflow* names which operand stays put: weight-stationary
   holds weights in the PEs and streams activations through; output-stationary holds the
   accumulating partial sum in place. For an N×N array, a matmul takes 3N−2 cycles (fill, stream,
   drain) at 1 result/cycle steady state.
3. **Example.** In CF05 I hand-traced a 2×2 weight-stationary array (A=[[1,2],[3,4]], B=[[5,6],
   [7,8]]) and saw exactly why Row 0's partial sums must reset between output passes to get
   C[1][0]=43 — that trace is the intuition behind the output-stationary pipelining I used in M3.
4. **Big picture.** The point is the systolic array minimizes the memory accesses that dominate
   energy, so the choice of dataflow directly sets a chip's energy efficiency.

## 10. Quantization and reduced precision [9]
*xref: `quiz1/cheatsheet.md` §10–12, `quiz2/study_guide.md` Unit 2 (BF16/precision), CF04, `project/m2/`*

1. **Definition.** Quantization means representing weights and activations with fewer bits — FP16,
   BF16, INT8, FP8, FP4 — instead of FP32, trading numerical precision for speed, memory traffic,
   and energy.
2. **Mechanics.** Halving the bit width roughly doubles effective throughput and halves the bytes
   moved, which directly relieves the memory wall, and a low-precision multiplier is far smaller and
   cheaper in energy than an FP32 one. The catch is range and accuracy: BF16 keeps FP32's exponent
   range (good for training dynamics) at the cost of mantissa bits, while INT8 needs a scale factor.
   You quantize only as far as the accuracy budget allows.
3. **Example.** My project's precision analysis is the cautionary version: RGB distances need exact
   integers because max squared distance is 3×255² = 195,075, which overflows INT8/INT16 and loses
   precision in FP16/BF16 — so I deliberately used an 18-bit integer accumulator instead of a
   "smaller is always better" reflex. Quantization is a budget, not a free pass.
4. **Big picture.** Basically, reduced precision is the cheapest large efficiency win in the field —
   but only down to the point where the numerics still hold, which you have to actually check.

## 11. Transformers and self-attention [10]
*xref: `quiz2/cheatsheet.md` (attention), `quiz2/study_guide.md` Unit 3, `week06_notes.md` §5*

1. **Definition.** A transformer is a neural architecture that replaces recurrence with
   self-attention, where every token computes a weighted relevance to every other token via scaled
   dot-product attention over query, key, and value matrices.
2. **Mechanics.** For each token you project it into a query, key, and value; attention scores are
   `softmax(QKᵀ/√dₖ)·V`. Because there's no recurrence, all tokens are processed in parallel —
   great for GPUs — but the QKᵀ term is O(n²) in sequence length, so it's both GEMM-heavy and
   memory-hungry, which is what drives demand for big HBM and FlashAttention-style tiling. Multi-head
   attention runs several of these in parallel, and the block alternates attention with an MLP.
3. **Example.** This is the workload that's reshaping hardware budgets industry-wide — the same
   roofline thinking from my project applies: attention's KV-cache traffic is a memory-bandwidth
   problem, not a compute problem, so accelerators respond with more bandwidth and on-chip reuse.
4. **Big picture.** The point is transformers turned "fast at recurrence" into "fast at huge
   parallel GEMM with massive memory traffic," and that single shift now dictates accelerator and
   memory design.

## 12. In-memory and analog computing [11]
*xref: `quiz2/study_guide.md` Units 5–7, `quiz2/cheatsheet.md`, CF06 (sneak paths), `week07_notes.md` §1–3*

1. **Definition.** In-memory computing performs computation — especially matrix-vector multiply —
   inside the memory array itself using device physics, rather than shuttling data to a separate
   compute unit.
2. **Mechanics.** In a resistive crossbar, weights are stored as conductances at each crosspoint.
   Drive the rows with input voltages and Ohm's law makes each device output a current
   proportional to V×G (a multiply); Kirchhoff's current law sums those currents down each column
   (the accumulate) — so the whole MVM happens in *one* analog step with zero data movement. The
   hard parts are sneak-path currents through unselected cells (fixed with 1T1R or diode cells),
   ADC/DAC overhead, and device variability.
3. **Example.** In CF06 I worked the KCL on a 2×2 crossbar and saw how sneak paths corrupt the
   column current — the concrete reason real crossbars need a selector device per cell. It's the
   memory-wall fix taken to its logical extreme: compute *is* the memory.
4. **Big picture.** Essentially, in-memory computing attacks the memory wall at its root by
   deleting the data movement entirely — the leading "beyond von Neumann" bet, at the cost of
   analog noise and conversion overhead.

## 13. Neuromorphic computing and spiking neural networks [12]
*xref: `quiz2/study_guide.md` Unit 9, `week07_notes.md` §6–12, `week08` neuromorphic deep dive, `quiz2/quiz_marked_slides.md`*

1. **Definition.** Neuromorphic computing is hardware modeled on the brain that co-locates memory
   and compute and communicates with sparse, event-driven spikes instead of clocked dense
   arithmetic — spiking neural networks are the algorithmic model that runs on it.
2. **Mechanics.** Neurons (e.g. leaky integrate-and-fire) only emit a spike when their membrane
   potential crosses threshold, so most of the array is silent most of the time — energy scales
   with activity, not with a clock. Spikes are routed as address-events (the AER protocol) over an
   on-chip network, and memory sits right next to each neuron, so there's no von-Neumann shuttle.
   On-chip learning rules like STDP update weights locally.
3. **Example.** Intel's Loihi and IBM's TrueNorth are the exploration vehicles — TrueNorth runs a
   million neurons at ~65 mW. The trade-off mirrors my whole course: huge energy wins *for the
   right, sparse, event-driven workload*, but a hard fit for dense GEMM — the No Free Lunch theorem
   in silicon.
4. **Big picture.** The point is neuromorphic hardware bets that for edge intelligence, event-driven
   sparsity beats dense clocked arithmetic on energy — which is exactly true when the data is sparse
   and exactly wrong when it isn't.

---

# Part 2 — Supporting glossary (one-liners with a hook)

- **Universal function approximation [14]** — A single-hidden-layer feedforward net can approximate
  any continuous function (Hornik 1989); it's *why* NNs are general-purpose, but says nothing about
  how many neurons or how to train them.
- **CNN [15]** — Weight-sharing convolutional layers exploit spatial locality; reusing each filter
  across the image *raises arithmetic intensity*, which is what makes CNNs hardware-friendly.
- **CUDA programming model [22]** — Threads → blocks → grids; work is launched as kernels. The
  mental model behind my CF03 GEMM.
- **Tensor cores / MMA [6]** — GPU units doing a small mixed-precision matrix MAC per clock; this is
  how a GPU does GEMM far faster than its scalar CUDA cores.
- **Compute kernel [22]** — One self-contained routine (matmul, conv, softmax) handed to the
  hardware; a network is just a sequence of kernel launches.
- **Sparsity and pruning [9]** — Drop near-zero weights/activations so hardware skips work; only
  pays off past a crossover sparsity (CF07 noted ~70% for crossbars) because of indexing overhead.
- **Memristor [16]** — Two-terminal device whose resistance stores state (Strukov 2008); the analog
  synapse that makes crossbar in-memory computing physically possible.
- **Reservoir computing [17]** — Fix a random high-dim dynamical reservoir, train only a linear
  readout; cheap temporal processing, realizable in physical substrates.
- **VLSI / ASIC / RTL / EDA flow [18]** — Write RTL Verilog, run synthesis → place-and-route →
  verification. Exactly the OpenLane 2 / sky130 flow I ran for M3/M4.
- **Loihi [13]** — Intel's research neuromorphic chip; async spiking cores + on-chip learning.
- **PPAC [21]** — Performance, Power, Area, Cost; the four axes every architectural decision trades
  against. The frame for every co-design call.
- **TOPS/W [19]** — Tera-ops per watt; the headline figure of merit because *energy*, not raw FLOPs,
  is the binding constraint (Sze 2017).
- **Tensor [4]** — Multi-dimensional array generalizing scalar/vector/matrix; the basic data object
  frameworks map onto hardware.
- **DL frameworks [4]** — PyTorch/TensorFlow lower high-level graphs onto vendor libraries (cuDNN);
  they hide device detail — which is exactly the black box a HW4AI engineer must see through.
- **Emerging / beyond-CMOS devices [20]** — Photonic, spintronic, phase-change, superconducting
  devices as transistor successors; e.g. the 2025 self-training superconducting SNN.

---

# Likely exam framing (from the cheat sheet's Part 3)

The instructor's "staying current" advice is a strong hint about the *philosophy* questions:
- "Master the foundations, not the tools" → be ready to argue *why* a principle outlives a tool.
- "Reason across the stack" → expect a trace-it-down question (PyTorch op → MACs → memory accesses).
- "Optimize for joules, not FLOPs" → energy-first thinking; tie any speedup claim to TOPS/W.
- "AI-assisted EDA as evaluator" → be able to say what you'd *check* in a tool's output, not just run it.

When in doubt, answer in the 4-step structure and **always ground it in the K-Means project in the
first person** ("I profiled…", "I offloaded…", "I used an 18-bit accumulator because…").
