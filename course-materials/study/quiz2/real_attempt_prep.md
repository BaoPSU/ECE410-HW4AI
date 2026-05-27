# Quiz 2 Real Attempt — Focused Prep

**Bao Nguyen | ECE 410/510 Spring 2026**
**Real window: 2026-05-25 → 2026-05-31 (week 9) | oral on Shine!, closed book, no AI | retakeable, 2 tokens**

This file is the night-before / morning-of doc. The comprehensive 9-unit reference is `study_guide.md`. This one cuts straight to **what to drill before you hit Start on Shine**, based on the 2026-05-22 practice attempt that scored 6.8/10 Not Yet.

---

## 0. The 4 things to nail cold (from practice-attempt feedback)

### 1. CF5 systolic no-reset trace (Q1 weak spot, 5.0/10)

Memorize this table. Walk it out loud. **Twice.**

For A=[[1,2],[3,4]], B=[[5,6],[7,8]], weight-stationary 2×2 systolic, PE[i][j] preloads B[i][j].

| Cycle | Event | PE[0][0] partial sum |
|------:|-------|---------------------:|
| 1 | A[0][0]=1 enters Row 0 | 0 + 1×5 = **5** |
| 2 | 5 drains to PE[1][0]; A[0][1]=2 enters Row 1 | used, then **reset to 0** |
| 3 | A[1][0]=3 enters Row 0 | 0 + 3×5 = **15** ✓ correct |
| 4 | 15 drains to PE[1][0], A[1][1]=4 enters Row 1 | PE[1][0] = 15 + 4×7 = **43** ✓ |

**Without reset between cycle 2 and cycle 3:**
- Cycle 3 PE[0][0] = 5 + 3×5 = **20** (kept the leftover instead of clearing)
- Cycle 4 PE[1][0] = 20 + 4×7 = **48** → C[1][0]=48 (corrupted)
- Error = 48 − 43 = +5 = **exactly the leftover partial sum**

**One-line answer for the oral**: "The reset isolates output rows so PE[0][0]'s accumulator doesn't carry the 5 from cycle 2 into cycle 3. Without reset, C[1][0] computes 48 instead of 43, and that +5 error is exactly the leftover partial sum."

### 2. CF6 sneak path: WHY KCL at V_row1 and V_col1 specifically (Q4 weak spot, 4.0/10)

The prof asked "why those two nodes, not somewhere else." Answer:

> Every other node is **pinned** by an external source. V_row0 = 1 V is driven. V_col0 = 0 V is held at the sense amp's virtual ground. The only **floating** nodes are V_row1 and V_col1, so they are the two unknowns. KCL at each floating node gives one equation per unknown, so two equations is the minimum sufficient system. Writing KCL at a pinned node gives a redundant equation (the voltage is already known). Writing KCL elsewhere adds no new information.

Memorize that paragraph. Numerical part stays the same: solve to V_row1 = 0.4 V, V_col1 = 0.6 V, sneak current = 0.2 mA, I_col0 = 1.2 mA (20% error).

### 3. Ask for paper before answering trace / circuit questions

Practice attempt transcript shows arithmetic falls apart without it ("Man, I need to write this on a piece of paper", "Ah, fuck", "Yeah, I have no idea"). Asking for paper is not penalized. Freezing is.

### 4. Keep the Q2/Q3 cadence (the 9.0/10 style)

That cadence:
1. **Lead with the number or bit layout.** ("BF16 is 1 sign, 8 exponent, 7 mantissa.")
2. **Name the rule.** ("Same dynamic range as FP32 at half the memory cost.")
3. **End punchy.** ("That's why Google picked it for the TPU.")

Avoid: restarting clauses, topic-hopping mid-sentence, "umm", "let's see", reading equations like a robot. The keyword_definitions.md style rules are strict on this.

---

## 1. The 4 likely topic areas (based on practice questions)

Quiz 2 covers **Week 5–8 lectures + codefests**. The practice hit one question per major bucket. The real attempt will probably mirror it.

### Bucket A — Systolic arrays + TPU (Week 5)
- 3N − 2 total cycles for N×N matmul
- Three dataflows: weight-stationary (TPU v1-v4), output-stationary (ShiDianNao), row-stationary (Eyeriss, **wins on energy**, 10× fewer DRAM accesses)
- TPU v1: 256×256 = 65,536 MACs/cycle, 92 TOPS INT8, 83× perf/watt over CPU
- **CF5 trace question is the likely Bucket A oral question.** See §0.1.

### Bucket B — Precision formats + Transformers (Week 5)
- FP32: 1/8/23. FP16: 1/5/10 (narrow exponent risk). BF16: 1/8/7 (FP32 range, half memory).
- Mixed-precision training: forward+backward in BF16, gradient accumulation in FP32, master weights in FP32. Avoids gradient swamping when small updates round away.
- Self-attention: `softmax(Q·Kᵀ / √d_k) · V`. NOT recurrent. Replaces hidden state with attention over all tokens at once. Positional encoding (sin/cos) replaces time order.

### Bucket C — Sparse representations (Week 7 / CF07)
- CSR has three arrays: `values` (size = nnz), `col_index` (size = nnz), `row_pointer` (size = n+1).
- Each row_pointer entry tells you where that row starts in values + col_index. Row i runs from row_pointer[i] to row_pointer[i+1].
- Last row_pointer entry = nnz, acts as sentinel so the last row reads the same as any other.
- Sparse-on-crossbar break-even: **~70% sparsity**. Below that, dense crossbar wins because index decoder + scheduler overhead exceeds the skipped zeros.

### Bucket D — In-memory computing + crossbars (Week 7-8)
- Crossbar computes MVM in one cycle via Ohm's law (I = G·V) + Kirchhoff's current law summing currents at each column.
- **Sneak paths** corrupt the read by adding parallel current paths through floating cells. 1S1R or 1T1R selectors fix it without losing density. **CF6 KCL is the likely Bucket D oral question.** See §0.2.
- Crosspoint cell options: 1R (sneak paths), 1D1R (diode rectifies), 1S1R (selector), 1T1R (transistor gate, used by TrueNorth).
- IMC energy argument: DRAM access ≈ 2 nJ, INT4 multiply ≈ 0.1 pJ. **Moving the bit costs 20,000× more than computing on it.**

---

## 2. Neuromorphic chips quick-reference (Week 7-8)

Most likely cold-callable facts:

| Chip | Year | Power | Neurons | Approach |
|------|------|-------|---------|----------|
| IBM TrueNorth | 2014 | 65 mW | 1 M | digital, 5.4 B transistors, 256 axons/core |
| IBM NorthPole | 2023 | ~74 W | dense INT2/4/8 | **not truly neuromorphic** (closer to inference accel) |
| Intel Loihi 2 | 2021 | <1 W | 1 M | LIF neurons, Lava framework, programmable |
| BrainScaleS-2 | 2022 | analog | mixed | **10,000× real-time**, AdEx neurons, on-chip PPU |
| SpiNNaker-2 | 2022 | ~700 mW | many | ARM-based, AER NoC |
| Akida | 2020 | low | TENNs | commercial, edge inference |

Key neuromorphic facts:
- **AER (Address Event Representation)**: spike protocol. Packet = neuron address + timestamp + framing. Asynchronous, event-driven.
- **NoC topologies**: mesh (most common), torus, ring, tree, butterfly. Mesh wins for 2D physical layout.
- Cerebras is **NOT** neuromorphic. Big wafer-scale chip, but dense matmul, not spike-based.
- **"AlexNet moment" for neuromorphic**: hasn't happened yet. Hardware mature (TRL 7-8), software stack and killer app missing.

---

## 3. CUDA MLP / training-on-systolic (Week 7 recap question pool)

Systolic array training: weight-stationary, 3 matmuls per layer (forward, backward through activation, backward through weight). The Quiz 1 retroactively-marked slide mentioned this; could resurface.

CUDA MLP: standard CUDA kernel for fully-connected forward pass. Memory layout (row-major), shared memory tiling, thread block sizing. The MLP example was shown end-to-end in the Week 5 deck.

---

## 4. CMAN-style problem checklist (oral version)

Before answering any quantitative question:
- [ ] **Ask for paper.** Out loud. "Can I take a minute on paper?"
- [ ] **Write the formula first**, then plug in numbers. Prof's grading rubric values formula > number.
- [ ] **State what you're computing** before you compute. "I'm computing the partial sum at PE[0][0] in cycle 3, which is partial_sum_in plus A[1][0] times the loaded weight B[0][0]."
- [ ] **Walk the arithmetic out loud.** Don't read equations like a robot, but do narrate.
- [ ] **End with the answer and one sentence on what it means.**

---

## 5. Wording rules from `keyword_definitions.md` (the prof's style screen)

These are explicit do/don't from your style file. Sticking to them moved Q2/Q3 to 9.0/10.

**Don't say**:
- "essentially"
- "the notion of"
- "fans out" (use "sends" or "drives")
- "infeasible" (use "not viable")
- "primitive" alone (use "building block")
- "I equals G times V" robotic equation reading

**Do say**:
- Inline parenthetical definitions: "the sense amp (the column read circuit at the bottom of the crossbar)"
- Excitatory/inhibitory connections (with "positive/negative" as alternates)
- "I = G × V" as written, then explain in natural words: "current is conductance times voltage at every cell"
- Close with "the point is" or "basically" or "essentially" as closers (max one per answer, no doubles)
- First person "I" when referencing the K-Means project

---

## 6. Token strategy

You have 2 retake tokens. Quiz 2 itself consumes 2 tokens if retaken.

**Recommended plan**:
1. Take the real attempt within the first 2-3 days (Mon-Wed). Treat it as graded but knowing you can retake.
2. If you score ≥ 7.0, hold the tokens for the final week if needed.
3. If you score < 7.0, retake within the week, after one drill round on whatever specifically went wrong.

Final exam is NOT retakeable. Tokens are best spent on Quiz 2.

---

## 7. 60-minute pre-attempt warm-up

If you have an hour right before:

1. **15 min**: reread §0 of this file out loud. Twice.
2. **10 min**: skim `cheatsheet.md` §3a (systolic reset table) and §10a (KCL node logic). [Note: §10a may not exist; see practice_questions.md §D4 instead.]
3. **15 min**: pick 3 questions from `practice_questions.md` at random and answer them out loud, timed (2 min each).
4. **10 min**: review the 6 banned words in §5. Practice substitutes.
5. **10 min**: water, deep breath, paper + pen + pencil ready, headphones on.

---

## 8. After the attempt

Paste the Shine! scorecard into the chat and I'll save it to `quiz2_real_2026-05-XX.md` and patch any new weak spots into the cheatsheet, same as I did for the practice.

Good luck.
