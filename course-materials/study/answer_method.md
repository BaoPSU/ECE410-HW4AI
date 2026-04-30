# Answer Method for Practice & Oral Exams

Based on quiz feedback (scored 2.3/10) and the approach refined on 2026-04-29.

---

## The Core Problem to Avoid

Listing words without explaining them. Saying "CUDA cores, tensor cores, shared memory" is not an answer — it's a word dump. Every component, concept, or term needs a role attached to it.

---

## Answer Structure (use for any question)

### 1. Open with a definition
One clear sentence that defines what the thing IS, not just what it contains.

> "A Streaming Multiprocessor is the fundamental execution unit of an NVIDIA GPU..."

### 2. Bullet out the key components or ideas
Each bullet = one term + its role. No orphan terms.

> - **CUDA cores** handle scalar FP32/INT32 arithmetic — the basic math units
> - **Warp schedulers** manage groups of 32 threads and switch between them to hide memory latency

### 3. Close with the big picture
One sentence on how it all fits together or why it matters.

> "The whole system is designed around one idea: always keep the math units busy by switching between warps instead of ever waiting on slow memory."

---

## Style Rules

- **Use the technical vocabulary** — SIMT, warp, DRAM, arithmetic intensity, FLOP/byte, ridge point, MAC, etc. These words signal you know the material.
- **No parentheses unless necessary** — fold the extra detail into the sentence instead.
- **Streamlined and friendly** — not robotic, not stiff. Write like you're explaining to a smart classmate.
- **Bullet points over paragraphs** — easier to follow out loud and easier to grade.
- **Minimum filler** — skip "I think", "basically", "kind of". Be direct.

---

## For Each Question Type

### Definition question ("What is X?")
1. Define X in one sentence
2. List key components/properties with roles
3. Close with why it matters or the big picture insight

### "Why" or motivation question ("Why do we use X?")
1. State the core problem X solves
2. Give the numbers if you have them (e.g., "DRAM costs 170× more energy than a multiply")
3. Give a concrete example from the course

### Interpretation question ("Interpret this plot / diagram")
1. Name the axes and what they represent
2. Identify the regions (memory-bound, compute-bound, ridge point)
3. Locate the specific kernel/dot and classify it
4. State what optimization that implies

### Compare/contrast question ("X vs Y")
1. One sentence on what each one is
2. Table or paired bullets on the key differences
3. State when you'd use each one

---

## Red Flags to Avoid

| Bad | Good |
|-----|------|
| "CUDA cores is basic math" | "CUDA cores handle scalar FP32/INT32 arithmetic" |
| "shared RAM" | "shared memory — on-chip SRAM scratchpad shared within a thread block" |
| "design algorithm and hardware together" (stop there) | Add WHY + example |
| No roofline interpretation | Name axes → find ridge → classify kernel → state fix |

---

## Example: SM Answer Done Right

- A Streaming Multiprocessor is the core execution unit of an NVIDIA GPU — the H100 has 132 of them, and every computation runs through one.
- The hardware assigns one thread block per SM, and all threads in that block share its resources.
- **CUDA cores** handle scalar arithmetic — FP32 and INT32 operations.
- **Tensor cores** are specialized matrix-multiply accelerators built for the MACs that dominate deep learning.
- **Warp schedulers** manage warps — groups of 32 threads executing lockstep under SIMT — and switch to a ready warp whenever the current one stalls waiting on memory.
- The **register file** is the fastest per-thread storage on the chip.
- **Shared memory** is a fast on-chip scratchpad that lets threads in the same block reuse data without going to slow DRAM.
- **Load/store units** move data between the SM and the memory hierarchy.
- **Special Function Units** handle transcendentals like sin, cos, and exp.
- An **L1 cache** is unified with shared memory but hardware-managed.
- The big picture: warp schedulers keep math units busy by switching between warps every cycle, hiding the ~100× latency gap between on-chip SRAM and off-chip DRAM.
