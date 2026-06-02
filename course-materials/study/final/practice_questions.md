# ECE 410/510 — Final Practice Questions
**Bao Nguyen | Portland State University | Spring 2026**

Closed-book, then check. The final is interview-style (5 questions, ~1 min to think, answer
aloud), so practice *speaking* each answer in the 4-step structure: definition → mechanics →
concrete example → big picture. Aim for 45–60 s and a K-Means example in the first person.

Coverage maps 1:1 onto `cheat_sheet_official.md`: Section A = foundational concepts 1–13,
Section B = supporting glossary, Section C = synthesis/"reason-across-the-stack" questions that
combine concepts the way an oral examiner would.

---

## Section A — Foundational concepts

### A1 — What is hardware–software co-design, and why is it the organizing idea of this course?
<details><summary>Answer</summary>

It's the concurrent design of algorithm, compiler, and silicon together instead of freezing one
and optimizing around it. You profile the workload, then let that profile drive precision,
dataflow, and memory hierarchy at once — every choice a PPAC (performance/power/area/cost)
trade-off. Example: in my K-Means project I found the distance kernel was 46% of runtime *and*
memory-bound at AI = 1.68, so co-design said move compute next to memory (a PIM chiplet), not buy
a faster ALU. The point is you only capture the full speedup when all the layers are shaped to fit
each other.
</details>

### A2 — Distinguish Moore's law from Dennard scaling. Which one broke first, and why does it matter here?
<details><summary>Answer</summary>

Moore's law = transistor *density* doubles ~every 2 years. Dennard scaling = power density stays
constant as transistors shrink, because voltage/current scale with size. **Dennard scaling broke
first (~2005)** — leakage and a voltage floor stopped V from dropping, so shrinking no longer cut
power per transistor. That ended frequency scaling (the "power wall"). It matters because you can
no longer wait for a faster CPU — my 9 s/image baseline has to be rescued by *architecture*
(specialization), which is the entire premise of this course.
</details>

### A3 — State the memory-wall energy/latency ratios and explain what they imply for accelerator design.
<details><summary>Answer</summary>

Off-chip DRAM access ≈ **100× the latency and ~170× the energy** of an on-chip SRAM access. Implication:
data *movement*, not arithmetic, dominates — so nearly every accelerator is a scheme to keep data
close to compute (caches, scratchpads, weight reuse, or in-memory compute). My distance kernel
sitting far left of the roofline ridge point is the memory wall in one picture; the PIM fix raises
bandwidth rather than adding FLOPs.
</details>

### A4 — Define MAC, dot product, and GEMM, and explain "good at deep learning means good at GEMM."
<details><summary>Answer</summary>

A MAC is one multiply + one add (2 FLOPs); chained MACs = a dot product; a grid of dot products =
GEMM (general matrix-matrix multiply). FC layers are matrix-vector products, convolutions lower to
GEMM via im2col, and attention is three GEMMs — so almost every layer reduces to GEMM, and a chip's
deep-learning ability collapses to its GEMM throughput. My compute core uses the same MAC
discipline from CF04: squared distance is a dot product of a difference vector with itself.
</details>

### A5 — Arithmetic intensity: define it, and explain why it alone doesn't tell you the bottleneck.
<details><summary>Answer</summary>

AI = compute ops ÷ bytes moved (FLOP/byte). High AI → each byte is reused many times → compute
stays busy; low AI → compute starves. But AI *alone* names no bottleneck — you must compare it to
the hardware's ridge point on a roofline. My kernel is 1.68 FLOP/byte; only against the 18.23
ridge point do I know it's memory-bound.
</details>

### A6 — Draw/describe the roofline model. Where does my K-Means kernel land and what does that justify?
<details><summary>Answer</summary>

Log-log plot: y = achievable FLOP/s, x = arithmetic intensity. Two ceilings — sloped
`bandwidth × AI` (memory-bound) and flat peak-FLOP/s (compute-bound) — meet at the **ridge point**.
Left of ridge = memory-bound, right = compute-bound. My kernel: AI = 1.68, ridge = 18.23, so far
left → provably memory-bound → justifies a near-memory PIM architecture instead of a bigger ALU.
(Modern GPUs push the ridge rightward, which deepens the memory wall for low-AI kernels.)
</details>

### A7 — Explain SIMT and how a GPU hides memory latency. Name the two things that make a kernel fast.
<details><summary>Answer</summary>

SIMT = single instruction, multiple threads: thousands of lightweight threads in warps of 32
execute in lockstep; the warp scheduler swaps in a ready warp the instant one stalls, so latency
is *hidden* by occupancy, not avoided. Two levers: **occupancy** (enough resident warps) and
**coalesced memory access** (a warp's 32 loads hit one transaction). In CF03 my tiled CUDA GEMM
cut DRAM traffic by raising reuse — same lesson.
</details>

### A8 — What makes the TPU a domain-specific architecture, and where does its perf/watt advantage come from?
<details><summary>Answer</summary>

It's purpose-built for one workload — NN inference — around a 256×256 systolic MXU (65,536
MACs/cycle). A CPU spends silicon on caches/branch-predict/OOO to make one thread fast; the TPU
throws that out and spends area on MACs, fed by a Unified Buffer + Weight FIFO, running INT8.
Perf/watt (~83× over CPU) comes from: no general-purpose overhead, weight-stationary dataflow
(no weight re-fetch), and low precision (~10–20× cheaper multiplies). My K-Means accelerator is the
same idea in miniature.
</details>

### A9 — Systolic array: how does it compute a matmul, why is it energy-efficient, and what is weight- vs output-stationary?
<details><summary>Answer</summary>

A grid of PEs each doing one MAC and passing operands to neighbors each clock ("systolic" =
heartbeat). One value read from memory feeds many MACs as it propagates → that's the energy win,
since memory accesses dominate energy. Weight-stationary holds weights in the PEs, streams
activations; output-stationary holds the accumulating partial sum in place. N×N matmul = 3N−2
cycles. In CF05 I traced a 2×2 weight-stationary array and saw why Row 0 partial sums reset between
passes (C[1][0]=43).
</details>

### A10 — Why is reduced precision the "cheapest big efficiency win," and when does it bite you? Use my project.
<details><summary>Answer</summary>

Halving bits ~doubles throughput and halves bytes moved (relieving the memory wall), and a
low-precision multiplier is far cheaper in energy — so every modern chip advertises INT8/FP8/FP4.
It bites when range/accuracy break: in my project, max squared RGB distance is 3×255² = 195,075,
which overflows INT8/INT16 and loses precision in FP16/BF16 — so I deliberately used an **18-bit
integer** accumulator. Quantization is a budget you must check, not a free pass.
</details>

### A11 — Transformers: what did self-attention replace, what's the core formula, and why is it a hardware problem?
<details><summary>Answer</summary>

It replaced recurrence (RNN/LSTM). Each token → query/key/value; attention = `softmax(QKᵀ/√dₖ)·V`.
No recurrence → all tokens process in parallel (GPU-friendly), but QKᵀ is O(n²) in sequence length
→ GEMM-heavy *and* memory-hungry (big KV cache). So it drives demand for HBM bandwidth and tiling
like FlashAttention — a memory-bandwidth problem, same roofline logic as my project.
</details>

### A12 — In-memory computing: how does a resistive crossbar do MVM in one step, and what's the catch?
<details><summary>Answer</summary>

Weights = conductances at each crosspoint. Drive rows with input voltages → Ohm's law gives each
device a current V×G (multiply); Kirchhoff's current law sums currents down each column
(accumulate) → the whole matrix-vector multiply in one analog step, zero data movement. Catches:
sneak-path currents through unselected cells (fixed with 1T1R/diode selectors — I worked the KCL
in CF06), ADC/DAC overhead, and device variability.
</details>

### A13 — What defines neuromorphic computing, and why is it a No-Free-Lunch story?
<details><summary>Answer</summary>

Brain-inspired hardware that co-locates memory + compute and communicates via sparse, event-driven
spikes (SNNs) instead of clocked dense arithmetic. LIF neurons fire only on threshold crossing, so
energy scales with *activity* not a clock; spikes route as address-events (AER) over an on-chip
network. Loihi and TrueNorth (1M neurons, ~65 mW) are the vehicles. NFL angle: huge energy wins for
sparse event-driven workloads, but a poor fit for dense GEMM — great at exactly what it's built for,
bad elsewhere.
</details>

---

## Section B — Supporting glossary (rapid-fire)

### B1 — What does the universal approximation theorem actually claim, and what does it NOT claim?
<details><summary>Answer</summary>

Claims: a single-hidden-layer feedforward net can approximate any *continuous* function to
arbitrary accuracy (Hornik 1989) — why NNs are general-purpose. Does NOT claim: how *many* neurons
you need (could be huge), that it's *learnable* by gradient descent, or that one layer is
*efficient*. Existence, not a recipe.
</details>

### B2 — Why are CNNs "hardware-friendly" in arithmetic-intensity terms?
<details><summary>Answer</summary>

Weight sharing: one small filter is reused across the whole image, so each weight byte feeds many
MACs → high reuse → high arithmetic intensity → the convolution lands right of the roofline ridge,
keeping compute units busy instead of starved.
</details>

### B3 — Define tensor core / MMA and contrast it with a CUDA core.
<details><summary>Answer</summary>

A CUDA core does scalar FP32/INT32 ops. A tensor core does a whole small matrix multiply-accumulate
(MMA) in mixed precision per clock — purpose-built for GEMM, which is why it accelerates deep
learning far beyond scalar cores.
</details>

### B4 — When does sparsity/pruning actually pay off on hardware?
<details><summary>Answer</summary>

Only past a crossover sparsity, because skipping zeros costs indexing/control overhead (e.g. CSR
storage). CF07 noted ~70% sparsity as the crossover for a crossbar to beat dense. Below that, the
overhead of finding the nonzeros costs more than the multiplies you skip.
</details>

### B5 — What is a memristor and why does in-memory computing need it?
<details><summary>Answer</summary>

A two-terminal device whose resistance encodes state (Strukov 2008). It's the analog synapse: a
programmable conductance at each crossbar crosspoint, which is what lets Ohm + Kirchhoff perform
the multiply-accumulate physically.
</details>

### B6 — Reservoir computing in one breath — what's fixed, what's trained, and why is it cheap?
<details><summary>Answer</summary>

A high-dimensional dynamical reservoir is left *fixed* (random); only a linear readout is *trained*.
Cheap because you skip training the recurrent core, and the reservoir can be a physical substrate.
Good for temporal/sequence tasks.
</details>

### B7 — Name the EDA flow stages I ran for M3/M4 and the tools.
<details><summary>Answer</summary>

Write RTL (SystemVerilog) → **synthesis** (Yosys) → **place-and-route** (OpenROAD) → STA/verification,
all orchestrated by **OpenLane 2** on the **sky130** PDK, 10 ns target clock. CF07's STA on the
single-cycle prototype is what produced my 3-stage pipeline plan and the DIST_W trim from 20→18.
</details>

### B8 — Why is TOPS/W the headline metric instead of raw TOPS?
<details><summary>Answer</summary>

Because *energy*, not raw throughput, is the binding constraint at every scale — from a battery
edge device to a data-center power budget. Two chips can hit the same TOPS, but the one that does it
at lower watts wins on cost and deployability. Optimize for joules, not FLOPs.
</details>

---

## Section C — Synthesis / reason-across-the-stack

### C1 — Trace a PyTorch `nn.Linear(1024,1024)` call down to memory accesses and MACs. Is it compute- or memory-bound?
<details><summary>Answer</summary>

`nn.Linear` → a GEMM (y = xWᵀ + b) → dispatched to cuBLAS → a tiled kernel on tensor cores → each
tile is a stack of dot products → each dot product is 1024 MACs. For a single 1024-vector input:
~1M MACs (2 MFLOP) but you must read the full 1024×1024 weight matrix (~2 MB at FP16). AI ≈ 1
FLOP/byte → **memory-bound** (you read each weight once). Batch it: amortize the weight read across
B inputs → AI rises ~B× → eventually crosses the ridge into **compute-bound**. That's the whole
reason inference batches — it's a roofline move.
</details>

### C2 — A vendor says their new chip is 4× faster. The cheat sheet's Part 3 says be an "evaluator." What do you check?
<details><summary>Answer</summary>

(1) 4× on *what* — peak TOPS or end-to-end on a real model? (2) At what *precision* — FP4 vs FP32
isn't apples-to-apples. (3) At what *power* — is it 4× TOPS/W or just 4× TOPS at 4× the watts?
(4) On what *workload AI* — does it help my memory-bound kernel or only compute-bound GEMM? (5)
Utilization — peak vs achieved. The evaluator mindset: a speedup claim is meaningless without the
workload, precision, and energy it's measured under.
</details>

### C3 — My K-Means kernel is memory-bound. Compare three fixes: bigger ALU, GPU/SIMT, near-memory PIM. Which and why?
<details><summary>Answer</summary>

Bigger ALU: useless — I'm left of the ridge, adding FLOPs moves the flat ceiling I'm not touching.
GPU/SIMT: helps throughput via parallelism but the access pattern is scattered/low-reuse, so I'd
still be bandwidth-limited and pay host↔GPU transfer. **Near-memory PIM**: directly raises the
sloped bandwidth ceiling (HBM3-class) right where my kernel lives, and kills the data-movement
energy — so it's the roofline-correct fix, targeting ~62× speedup. The principle: fix the wall
you're actually against.
</details>

### C4 — Connect three "memory wall" responses across the course: caching, systolic dataflow, and in-memory computing. How do they differ in *how far* data moves?
<details><summary>Answer</summary>

All three attack data movement, at increasing radicalism. **Caching/scratchpad**: keep data
on-chip near compute (cut DRAM trips). **Systolic dataflow**: read a value once and let it feed
many PEs as it flows (reuse in motion — weight-stationary). **In-memory computing**: don't move
data at all — compute *inside* the memory array via Ohm/Kirchhoff. The trend is shrinking the
distance between bytes and MACs to zero, because that distance is the energy.
</details>

### C5 — The cheat sheet ends with "the tools change; the foundations don't." Argue this with one concrete example from your own work.
<details><summary>Answer</summary>

OpenLane 2 / sky130 will be obsolete in a few years — but the *foundations* I used them to apply
won't be. CF07's STA taught me to read a critical path and trim accumulator width (20→18 bits)
because the top bits were provably always zero; that's PPAC reasoning that transfers to any tool or
node. Same with the roofline: it predicted my kernel was memory-bound regardless of which
simulator drew it. The durable skill is reasoning across the stack — the GUI is disposable.
</details>

---

### Self-scoring (from `../answer_method.md`)
- **8/10** = all 4 steps + a concrete example said out loud.
- **4/10** = definition only, no why/example (the trap).
- **0/10** = word dump, no interpretation (what cost me Q3 on quiz 2).
Write the formula before the number. Always tie back to K-Means in the first person.
