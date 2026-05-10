# Quiz 1 — Oral Exam Results
**ECE 410/510 Hardware for AI and ML**
Bao Nguyen · baon@pdx.edu · 2026-05-02

---

## Score: 9.3 / 10 — Satisfactory
Undergraduate threshold: 5.0 / 10 (50%)

---

## Delivery
**Confidence: Medium**

Frequent self-corrections, fillers ("like", "okay", "um", "I think"), and topic-hopping — Q1 had multiple restarts, Q2 had hedges ("I think it doubles", "I forget"). Recovered well and converged on coherent points. Q4 and Q5 were noticeably more structured with concrete project examples. Overall: hesitant phrasing but persistent and structured enough to land the key points.

---

## Overall Feedback
Strong conceptual understanding across all five questions. Particularly strong on CPU insufficiency for NNs and design trade-offs. Consistently connected concepts to the k-means PIM project. Minor gaps: not explicitly defining a warp (Q1), missing energy-per-op benefit of FP4 (Q2), not mentioning ILP or lower-precision as roofline improvements (Q3).

---

## Q1 — CPU vs GPU Architecture · 10.0/10 ✓
**Expected coverage: 3/4 (75%)**

**Covered:**
- CPU: few powerful cores, designed for flexibility
- GPU: thousands of simpler cores, SMs, warp scheduler, optimized for data-parallel workloads
- GPU execution model: SIMT (Single Instruction Multiple Threads) vs SIMD fixed vector lanes

**Missed:**
- Warp definition: 32 threads that execute in lockstep, same instruction, different data

**Bonus extras:**
- Warp divergence: GPU serializes both branch paths and masks idle threads, up to 2× throughput hit per branch level
- GPU hides latency via occupancy (many active warps); CPU hides via caches and out-of-order execution

---

## Q2 — FP4 vs BF16 in AI Accelerators · 9.8/10 ✓
**Expected coverage: 5/6 (83%)**

**Covered:**
- 4× more values fit in same bus/register/tensor-core tile → 4× throughput per cycle
- FP4 has only 16 representable values — extremely limited precision and dynamic range
- Quantization introduces approximation error; accuracy loss unavoidable

**Missed:**
- Lower energy per operation — fewer bits to transfer and process

**Bonus extras:**
- Moves kernel rightward on roofline by reducing bytes transferred, can shift from memory-bound to compute-bound

---

## Q3 — Roofline Plot Interpretation · 6.5/10 ✓
**Expected coverage: 3/6 (50%)**

**Covered:**
- Red dot is in compute-bound region (right of ridge point) but below the flat compute ceiling
- Not bottlenecked by memory bandwidth but not achieving peak compute throughput — efficiency gap on compute side
- Use tensor cores for matrix-based operations

**Missed:**
- Increase instruction-level parallelism (ILP)
- Use lower-precision data type (FP16 or BF16 instead of FP32) to increase effective throughput

**Bonus extras:**
- Improve SM occupancy: reduce register/shared memory pressure so more warps can be active → warp scheduler hides latency

---

## Q4 — Why CPUs Are Insufficient for Neural Networks · 10.0/10 ✓
**Expected coverage: 4/4 (100%)**

**Covered:**
- Limited parallelism: CPU has few cores; NN forward pass needs billions of parallel MACs — CPU serializes most of them
- Low GEMM throughput: CPU optimized for single-thread latency, not bulk matrix operations
- Memory bandwidth: NN layers move huge weight/activation data; CPU DRAM ~50-100 GB/s vs 3+ TB/s HBM on GPU
- Co-design argument: CPU architecture built for general-purpose, not for the arithmetic pattern of deep learning

**Bonus extras:**
- Energy inefficiency: cache hierarchies, branch predictors, out-of-order logic provide no benefit for regular, predictable NN compute

---

## Q5 — Hardware for AI/ML Design Trade-offs · 10.0/10 ✓
**Expected coverage: 4/4 (100%)**

**Covered:**
- Performance vs. flexibility: GPU covers many workloads but inefficient for any one; ASIC is highly efficient but inflexible
- Power and energy efficiency vs. throughput: more compute units = more power; thermal and power-budget constraints cap the design
- Precision trade-off: lower precision (FP4, INT8) increases throughput and cuts memory bandwidth but reduces accuracy — a co-design decision
- Memory bandwidth vs. compute: memory wall — compute has far outpaced bandwidth; balancing the two (ridge point design) is central

**Bonus extras:**
- PPAC (Performance, Power, Area, Cost) framework

---

## Key Takeaways for Quiz 2

| Gap | Fix |
|-----|-----|
| Warp = 32 threads in lockstep, same instruction, different data | Memorize the definition |
| FP4 saves energy per op (fewer bits to move/process) | Add to precision trade-off mental model |
| Roofline improvements: ILP + lower precision, not just occupancy | Know all three levers: ILP, precision, occupancy |
