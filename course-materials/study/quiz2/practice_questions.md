# ECE 410/510 — Quiz 2 Practice Questions
**Bao Nguyen | Portland State University | Spring 2026**

Work each question closed-book. Then check against the answer below. Aim to write formulas before numbers, just like in CMAN assignments.

---

## Section A — Systolic Arrays & TPUs

### A1
What is a systolic array, and why does the analogy to a heart make sense?

<details><summary>Answer</summary>

A systolic array is a 2D grid of Processing Elements (PEs) where data flows rhythmically — one operand per direction per clock cycle. The heart analogy: just like a heart pumps blood in pulses, data "pulses" through PEs synchronously. Each PE does one MAC per cycle and passes results to neighbors. The energy benefit is that one register read feeds many MACs (instead of reading registers per MAC as a CPU does).
</details>

### A2
For an N × N systolic matrix multiplication, how many cycles total? Break it down.

<details><summary>Answer</summary>

**Total: 3N − 2 cycles**.
- Fill pipeline: N cycles (first result emerges after N cycles)
- Output phase: N cycles (N results stream out, one per cycle)
- Drain pipeline: N − 2 cycles

Steady state after fill: 1 result per cycle.
</details>

### A3
The TPU v1 MXU has how many MACs per cycle? Why does this matter for the perf/watt advantage?

<details><summary>Answer</summary>

**256 × 256 = 65,536 MACs per cycle.** At 700 MHz, that's 92 TOPS (INT8).

The perf/watt advantage (83× vs CPU) comes from:
1. No cache hierarchy, branch predictor, or OOO logic — all silicon spent on MACs
2. Weight-stationary dataflow eliminates re-fetching weights from off-chip
3. Tight Unified Buffer + Weight FIFO pipelining keeps the array fed at 100% utilization
4. INT8 (vs FP32) cuts energy per multiply ~10–20×
</details>

### A4
Name the three systolic dataflows and which wins on energy. Why doesn't everyone use it?

<details><summary>Answer</summary>

- **Weight-stationary** (TPU v1–v4): weights stay in PEs, activations stream through
- **Output-stationary** (ShiDianNao): partial sums stay in PEs
- **Row-stationary** (Eyeriss): a filter row + its reuse maximize all-data reuse

**Row-stationary wins on energy** — ~10× fewer DRAM accesses than weight-stationary. But it's harder to implement (more complex scheduler, more state per PE), so most production hardware (TPU) uses weight-stationary.
</details>

---

## Section B — Precision Formats & Transformers

### B1
Draw the bit layouts of FP32, FP16, and BF16. Why is BF16 safer for training?

<details><summary>Answer</summary>

```
FP32:  1 sign | 8 exponent | 23 mantissa  (32 bits)
FP16:  1 sign | 5 exponent | 10 mantissa  (16 bits)
BF16:  1 sign | 8 exponent | 7  mantissa  (16 bits)
```

BF16 is safer because it has the **same 8 exponent bits as FP32**, so the dynamic range is identical. FP16's 5 exponent bits give a narrow range — gradients during training can easily overflow or underflow. BF16 trades mantissa precision (7 bits) for range, which rarely hurts training accuracy. Bonus: trivial conversion FP32 ↔ BF16 (just drop/add the last 16 mantissa bits).
</details>

### B2
Write the self-attention formula and explain each part.

<details><summary>Answer</summary>

```
Attention(Q, K, V) = softmax(Q·Kᵀ / √d_k) · V
```

- **Q (Query)**: "What am I looking for?" — Q = X · W_Q
- **K (Key)**: "What do I offer?" — K = X · W_K
- **V (Value)**: "What do I contribute if selected?" — V = X · W_V
- **Q·Kᵀ**: dot product of every query with every key → attention scores
- **/ √d_k**: scaling prevents dot products from blowing up, stops softmax saturation
- **softmax**: converts scores into a probability distribution (sums to 1)
- **· V**: weighted sum of values using attention probabilities
</details>

### B3
Why are transformers NOT recurrent? What replaces recurrence?

<details><summary>Answer</summary>

RNN/LSTM processes one token at a time, with hidden state passing step t to t+1. This:
1. Cannot be parallelized over time during training
2. Compresses all prior context into one fixed-size vector
3. Suffers vanishing gradients on long sequences

Transformers replace recurrence **entirely with self-attention**:
- All tokens processed in parallel
- Every token connects directly to every other token (no propagation)
- No hidden state — order encoded via **positional encoding (sin/cos at different frequencies)**

Result: full training parallelism, direct long-range dependencies, scales to billions of parameters.
</details>

### B4
What is RLHF and what are its three stages?

<details><summary>Answer</summary>

**Reinforcement Learning from Human Feedback** aligns a pre-trained LLM with human preferences.

1. **SFT (Supervised Fine-Tuning)**: fine-tune the pre-trained LLM on human-written prompt+response demonstrations. Output: an initialized policy that knows what "good" looks like.
2. **Reward Model Training**: the SFT model generates response pairs; humans rank A vs B; train a Reward Model on those rankings via cross-entropy. Output: a scalar score r(x, y).
3. **PPO RL Fine-Tuning**: the policy LLM generates a response; the RM scores it; PPO updates the policy to maximize **E[r(x,y)] − β · KL(policy, SFT)**. The KL penalty prevents reward hacking by keeping the policy near the SFT baseline.
</details>

---

## Section C — Algorithm Acceleration & NFL

### C1
List 5 ways to accelerate an algorithm. Pick the technique with the highest speedup but lowest applicability and justify.

<details><summary>Answer</summary>

Any 5 of: technology scaling, cache optimization, code optimization, parallelism, GPUs, TPUs, fancier CPUs, HW/SW co-design, algorithm improvement, emerging technology.

**Highest speedup, lowest applicability: FPGA/ASIC implementation** (10×–1000× speedup, Very High difficulty, Low applicability). It wins only when the algorithm's structure perfectly matches the custom silicon. Anything outside its target domain runs poorly or not at all.
</details>

### C2
State the No Free Lunch theorem and one hardware implication.

<details><summary>Answer</summary>

**NFL theorem (Wolpert & Macready, 1997)**: Averaged over all possible problems, every optimization algorithm performs equally well. No algorithm consistently outperforms random search across all problems.

**Hardware implication**: specialized architectures (TPU, GPU, neuromorphic) excel in their domain but fail outside it. Any claim that "X is better than Y" must specify the problem class. This is why ASIC has the highest possible speedup AND the lowest applicability — it wins only when the algorithm's structure matches the custom silicon exactly.
</details>

### C3
The emerging technology table lists Memristors with 10–100× speedup and 100–1000× energy gain. Which other tech beats memristors on energy efficiency, and what's the trade-off?

<details><summary>Answer</summary>

**Protein-based nanowires**: 10,000–100,000× energy gain (theoretical). But the trade-off is **Very Low TRL** — early research stage with major manufacturing scalability problems. Memristors at Med-High TRL are the practical choice today.

(Also: neuromorphic chips at 1000–10,000× energy gain edge out memristors.)
</details>

---

## Section D — In-Memory Computing & Crossbars

### D1
Why is in-memory computing motivated by an energy argument?

<details><summary>Answer</summary>

At 45-nm, accessing one 64-bit word from DRAM costs ~2 nJ (2000 pJ). An INT4 multiply costs ~0.1 pJ. **Moving data from DRAM is ~20,000× more expensive than computing on it.** The moment a model's weights don't fit in SRAM, energy is dominated by data movement.

IMC eliminates the bulk transfer: send a command "perform f on D" to the memory, and the memory array itself returns f(D). The crossbar does this for matrix-vector multiplication via Ohm's and Kirchhoff's laws in a single read cycle.
</details>

### D2
Write the equation for the current at column j in a resistive crossbar. Which laws is it derived from?

<details><summary>Answer</summary>

```
I(j) = Σᵢ G(i,j) · V(i)
```

Derivation:
- **Ohm's law**: each cell's current is I(i,j) = G(i,j) · V(i)
- **Kirchhoff's current law**: currents sum at the bitline j → I(j) = Σᵢ I(i,j)

In matrix form: **I = G·V**. One column current = one dot product. Whole MVM in **one read cycle**.
</details>

### D3
Name the four crosspoint cell structures and which one solves sneak paths.

<details><summary>Answer</summary>

| Cell | Structure |
|------|-----------|
| **1R** | 1 resistor — simplest, but suffers from sneak paths |
| **1S1R** | 1 selector + 1 resistor — nonlinear selector blocks sneak paths without losing density |
| **1T1R** | 1 transistor + 1 resistor — best per-cell selectivity (raise only the selected row's gate voltage; transistors elsewhere are off), at the cost of lower density |
| **1C** | 1 capacitor — no static leakage during MVM (capacitive variant: Q(j) = Σᵢ C(i,j) · V(i)) |

**1S1R and 1T1R both solve sneak paths**, with different density/complexity trade-offs.
</details>

### D4 (CF06 walkthrough)
Given R[0][0] = 1 kΩ (on), R[0][1] = R[1][0] = 2 kΩ (off), R[1][1] = 1 kΩ (on), with V_row0 = 1 V, V_col0 = 0 V (virtual ground), and row 1 + col 1 floating. Compute V_row1, V_col1, and the actual current I_col0.

<details><summary>Answer</summary>

Apply KCL at the floating nodes (net current = 0).

**KCL at V_row1**: current in from col1 must equal current out to col0.
V_row1/(2k) + (V_row1 - V_col1)/(1k) = 0
Multiplying by 2000: V_row1 + 2(V_row1 - V_col1) = 0 → **3V_row1 - 2V_col1 = 0** → V_col1 = (3/2)V_row1 ... (1)

**KCL at V_col1**: current in from row0 must equal current out to row1.
(1 - V_col1)/(2k) + (V_row1 - V_col1)/(1k) = 0
Multiplying by 2000: (1 - V_col1) + 2(V_row1 - V_col1) = 0 → **1 + 2V_row1 - 3V_col1 = 0** ... (2)

Substitute (1) into (2): 1 + 2V_row1 - 3·(3/2)V_row1 = 0 → 1 - (5/2)V_row1 = 0 → **V_row1 = 0.4 V**, **V_col1 = 0.6 V**.

Sneak current = (V_row1 - 0)/2k = 0.4/2000 = **0.2 mA**

I_col0 actual = intended (1 mA from R[0][0]) + sneak (0.2 mA from R[1][0]) = **1.2 mA (20% error)**.
</details>

### D5
At what sparsity level does it stop making sense to use a sparse crossbar mapping? Why?

<details><summary>Answer</summary>

**Below ~70% sparsity, dense crossbar usually wins.** The digital overhead (index decoder for CSR/CSC, scheduler that routes non-zeros to tiles, irregular memory access that breaks locality, padding for partial tiles) costs more than the zeros you skipped.

Sparse mapping pays off when:
- **Sparsity ≥ 90%**
- **Structured sparsity** (block / N:M patterns) simplifies the decoder
- **Weight reuse** amortizes overhead
- **Large matrices** (overhead is O(NZ); savings are O(N²))
</details>

### D6
Describe CSR format. How does it compare to COO?

<details><summary>Answer</summary>

**Compressed Sparse Row (CSR)** stores a sparse matrix using three arrays:
- `values[]` — the non-zeros in row-major order
- `col_idx[]` — column index of each non-zero
- `row_ptr[]` — length N+1; row i's non-zeros sit at `values[row_ptr[i] .. row_ptr[i+1]]`

To read row i: slice `row_ptr[i] .. row_ptr[i+1]` gives all non-zeros in row i. Memory: ~2·nnz + N (instead of N² for dense). Walks rows in order → ideal for y = A·x.

**vs COO** (Coordinate format): COO stores (row, col, val) tuples for every non-zero — 3·nnz entries. CSR keeps `col_idx` and `values` the same but **run-length-encodes the row coordinate** into `row_ptr` (N+1 entries vs nnz). Same info, less memory.
</details>

---

## Section E — Neuromorphic Chips & Communication

### E1
Why is Cerebras WSE-3 not considered neuromorphic, despite being enormous?

<details><summary>Answer</summary>

Cerebras WSE-3 is a wafer-scale conventional accelerator for dense matrix multiplication on LLMs. It uses traditional von Neumann compute with separate memory and processing, synchronous clocked operation, and continuous-valued numerical computation. It is large but architecturally conventional.

**Neuromorphic chips** mimic brain structure: integrated memory and compute, event-driven spike-based communication, on-chip learning (synaptic plasticity), distributed memory in connection strengths, and fault tolerance through distributed processing. Cerebras has none of these characteristics.
</details>

### E2
What is AER and what does an AER packet contain?

<details><summary>Answer</summary>

**Address Event Representation (AER)** is a spike-event message-passing protocol for neuromorphic Network-on-Chip systems.

When a neuron spikes, the system sends only its **unique identifier** as an event packet. Almost all NM HW and SW sim environments use a variant.

**Packet format**: `| DEST_CORE | NEURON_ID | TIMESTAMP |`

Properties:
- Only active neurons generate messages — sparse, event-driven, asynchronous
- Timing information is **implicit** in when the message is sent
- Enables async sparse communication between NM cores
</details>

### E3
"Neurons are dumb — they only know their own ID." Explain how a spike actually reaches its targets.

<details><summary>Answer</summary>

Four-step routing process:

1. **Neuron spikes** — emits only its own address. The neuron has no idea where its outputs go.
2. **Routing lookup** — the source core has a local SRAM table mapping `src → [dest list]`. This is the synaptic fan-out, stored in memory not wires.
3. **Packet fan-out** — the network interface emits one AER packet per destination (1 spike → N packets).
4. **NoC delivers** — routers forward each packet by DEST coordinates (XY routing in a 2D mesh).

Why this matters:
- Connectivity = a table, so **rewriting the table rewires the network** (programmable topology)
- Fan-out at the source enables **on-line learning** (STDP — Spike-Timing-Dependent Plasticity)

Real chips: SpiNNaker (multicast routers), Loihi (axon table), TrueNorth (per-neuron destination list).
</details>

### E4
Name three components of a Network-on-Chip and three reasons to use one over a bus.

<details><summary>Answer</summary>

**Components**:
1. **Router** — does arbitration, buffering, switching
2. **Link** — physical wires between routers
3. **NI (Network Interface)** — packs/unpacks data into packets

**Reasons to use a NoC over a bus**:
1. **Scalability** — bandwidth grows with router count; buses don't
2. **Parallelism** — multiple concurrent transactions on different links
3. **Modularity** — drop-in IP blocks; standardized interfaces

Default topology: 2D mesh (each node = router + processing core). Others: torus, ring, tree, butterfly.
</details>

### E5
Compare Loihi and Loihi 2 on three specs.

<details><summary>Answer</summary>

| Spec | Loihi (2017) | Loihi 2 (2021) |
|------|--------------|----------------|
| Neurons per chip | ~130,000 | **Up to 1 million (~8× more)** |
| Spike events | 1-bit binary | **Up to 32-bit graded** |
| Spike processing speed | Baseline | **Up to 10× faster** |
| Neuron model | Fixed LIF | **Programmable via microcode** |
| Framework | None at launch | **Lava (open-source)** |

Loihi 2 is also smaller (31 mm² vs 60 mm² on Intel 4 vs 14 nm).
</details>

### E6
What are IBM NorthPole's 10 axioms (in summary)?

<details><summary>Answer</summary>

NorthPole's 10 axioms, paraphrased:

1. **Specialized for neural inference** — no data-dependent branching, no training
2. **Biological precision** — optimized for 8-, 4-, 2-bit math
3. **Distributed core array** — 16×16 cores, 8192 2-bit ops/cycle each
4. **Distributed memory near and intertwined with compute** — data locality for energy efficiency
5. **Dense NoCs** (gray-matter and white-matter inspired) for compute/memory interconnect
6. Two more NoCs for reconfiguring synaptic weights and programs
7. **Data-independent branching** — fully pipelined, stall-free, deterministic; no memory misses
8. **Co-optimized training** that bakes low-precision constraints into training
9. **Codesigned software** (compiler, validator, runtime)
10. **Frame-based usage** — write input frame, read output frame; runs independently of host

Performance: ResNet-50 at 42,460 FPS / 74 W on 12 nm — competitive with H100 (700 W) on energy/space metrics.
</details>

### E7
What does the Neuromorphic Transformer replace MACs with? Why is that energy-efficient?

<details><summary>Answer</summary>

**Replaces MAC (multiply-accumulate) with AAC (AND-accumulate)**:
- Q/K/V matrices become **binary** (spikes: 0 or 1)
- AND replaces multiplication; integer addition for accumulation
- Eliminates softmax, scaling by √d_k, and matrix transpose

**Energy savings**: a multiply is 10–100× more expensive than an AND gate in hardware. With Q/K/V as binary, each "multiplication" becomes a single AND gate, then sparse adds. The paper reports **99.96% reduction in multiplications** — 116M → 4,900 multiplications.

Based on Spiking Neural Networks: event-driven, sparse activity, only spike when active. Human brain analogy: ~20W for full intelligence, all spike-based.
</details>

---

## Section F — CUDA & Mapping

### F1
Why use separate CUDA kernels for each MLP layer instead of one kernel for the whole network?

<details><summary>Answer</summary>

Each layer has a different optimal thread configuration. For example:
- Layer 1 (input 784 → hidden 64): `threadsPerBlock(8, 5)` for 8 batches × 5 hidden neurons
- Layer 2 (hidden 64 → output 10): `threadsPerBlock(16, 1)` for 16 batches × 1 output neuron

A single mega-kernel forces one thread config across all layers, hurting occupancy or causing register spills. Separate kernels let each layer pick the right thread/block dim.

**Trade-off**: kernel launch overhead vs register pressure. Too many threads/block → register spills to local memory → terrible performance.

**Operations with the same data/parallelism pattern can be fused** (e.g., bias + activation), reducing launch overhead without compromising layer-specific tuning.
</details>

### F2
Walk through the GPU memory flow for inference: CPU → GPU → CPU.

<details><summary>Answer</summary>

```
1. cudaMalloc(&d_weights, ...) → allocate device memory for weights, inputs, outputs
2. cudaMemcpy(d_weights, h_weights, ..., H→D) → copy weights/inputs from CPU (host) to GPU (device)
3. kernel<<<M, T>>>(d_inputs, d_weights, d_outputs) → launch M blocks × T threads each
4. cudaMemcpy(h_outputs, d_outputs, ..., D→H) → copy results back to CPU
5. cudaFree(d_weights, d_inputs, d_outputs) → release device memory
```

Bottleneck for inference: **steps 2 and 4** (PCIe bandwidth). For batched inference, amortize this by sending many inputs per copy. For training, keep weights resident on the GPU across epochs.
</details>

---

## Section G — Quick Mixed Drills

### G1
Without looking: T or F — BF16 has the same exponent range as FP32.

<details><summary>Answer</summary>

**TRUE.** BF16 has 8 exponent bits, same as FP32. That's why it's safe for training.
</details>

### G2
Without looking: What's the systolic array cycle count for N=2 matmul?

<details><summary>Answer</summary>

3N − 2 = 3(2) − 2 = **4 cycles**. (Matches the CF05 trace: 4 cycles for 2×2 weight-stationary matmul.)
</details>

### G3
Without looking: What's the sparsity crossover where dense crossbar starts to beat sparse mapping?

<details><summary>Answer</summary>

**~70%.** Below 70% sparsity, the digital decoder + scheduler overhead beats the cells you skipped.
</details>

### G4
Without looking: What does AER stand for and what does the packet contain?

<details><summary>Answer</summary>

**Address Event Representation.** Packet: `| DEST_CORE | NEURON_ID | TIMESTAMP |`.
</details>

### G5
Without looking: At 45-nm, what's roughly the energy ratio between DRAM access and an INT4 multiply?

<details><summary>Answer</summary>

DRAM 64-bit: ~2 nJ = 2000 pJ. INT4 mult: ~0.1 pJ. Ratio: **~20,000×**. (Even FP32 mult at 5 pJ is 400× less than DRAM.)
</details>

### G6
Without looking: What does the Neuromorphic Transformer reduce by 99.96%?

<details><summary>Answer</summary>

**Multiplications** (116M → 4,900) by replacing MAC with AAC and using binary spikes for Q/K/V.
</details>

### G7
Without looking: Three solutions to sneak paths in a resistive crossbar?

<details><summary>Answer</summary>

1. **Diodes** at each cell (1S1R) — unidirectional current
2. **Transistor at each cell (1T1R)** — only the selected row's gate is on
3. **Capacitive cells (1C)** — no static leakage during MVM
</details>

### G8
Without looking: Name the four pillars of neuromorphic chips.

<details><summary>Answer</summary>

1. **Parallel processing** (integrated compute + memory)
2. **Event-driven** (spike-based, not clocked)
3. **Adaptability** (on-chip learning / plasticity)
4. **Distributed memory** (information in connection strengths, not centralized)
</details>
