# Answer Method for Practice & Oral Exams

Based on quiz feedback (scored 2.3/10) and the approach refined on 2026-04-29.

---

## The Core Problem to Avoid

Listing words without explaining them. Saying "CUDA cores, tensor cores, shared memory" is not an answer — it's a word dump. Every component, concept, or term needs a role attached to it.

---

## Slide Accuracy Rule

Every answer must be grounded in the course slides (weeks 1–5). Do not add facts from general knowledge that are not in the slides. If something is not in the slides, either leave it out or flag it clearly as outside the course material.

---

## Answer Structure (use for any question)

### 1. Open with a definition
One clear sentence that defines what the thing IS, not just what it contains.

> "A Streaming Multiprocessor is the fundamental execution unit of an NVIDIA GPU..."

### 2. Bullet out the key components or ideas — line by line, flowing
Each bullet = one term + its role, and each line should continue the thought from the one before. Don't write isolated facts — write like each bullet is the next sentence in a spoken explanation.

> - Inside each SM, the **CUDA cores** handle the basic scalar math, your FP32 and INT32 operations.
> - Sitting alongside them are the **Tensor cores**, purpose-built for MMA on a 4×4 matrix per clock cycle.
> - To keep those cores busy, the SM has **warp schedulers** that manage groups of 32 threads and instantly switch to a ready warp whenever the current one stalls on memory.

### 3. Close with the big picture
One sentence on how it all fits together or why it matters.

> "The whole system is designed around one idea — always keep the math units busy by switching between warps instead of ever waiting on slow memory."

---

## Style Rules

- **Use the technical vocabulary** — SIMT, warp, DRAM, arithmetic intensity, FLOP/byte, ridge point, MAC, etc. These words signal you know the material.
- **No parentheses unless necessary** — fold the extra detail into the sentence instead.
- **No dashes mid-sentence** — write complete sentences that flow naturally when spoken aloud. If a dash is tempting, either end the sentence and start a new one, or fold the detail in directly.
- **No colons mid-sentence** — same rule as dashes. Write it out as a full natural sentence instead.
- **Streamlined and friendly** — not robotic, not stiff. Write like you're explaining to a smart classmate.
- **Bullet points over paragraphs** — easier to follow out loud and easier to grade.
- **Bullets should flow into each other** — each line continues the thought from the one before, like a spoken explanation broken into lines. Not a list of disconnected facts.
- **Minimum filler** — skip "I think", "basically", "kind of". Be direct.
- **Slides only** — only include content covered in the course slides. Do not add outside knowledge.

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
| "shared RAM" | "shared memory, an on-chip SRAM scratchpad shared within a thread block" |
| "design algorithm and hardware together" (stop there) | Add WHY + example |
| No roofline interpretation | Name axes, find ridge, classify kernel, state fix |
| Adding facts not in the slides | Flag it or leave it out |
| Using colons or dashes mid-sentence | Rewrite as a full natural sentence |

---

## Example: SM Answer Done Right

- A Streaming Multiprocessor is the fundamental execution unit of an NVIDIA GPU. The entire GPU is a collection of these, and the H100 has 132 of them.
- Every computation you run on a GPU happens inside an SM, and the hardware scheduler decides which thread block goes to which one.
- Inside each SM, the **CUDA cores** handle the basic scalar math, your FP32 and INT32 operations.
- Sitting alongside them are the **Tensor cores**, purpose-built for MMA, running D = A×B + C on a 4×4 matrix in a single clock cycle.
- To keep all of those cores busy, the SM has 4 processing blocks, each with its own **warp scheduler** managing warps. A warp is a group of 32 threads executing the same instruction lockstep under SIMT.
- When one warp stalls waiting on memory, the scheduler immediately swaps in another ready warp. That is how the GPU hides the latency gap between on-chip SRAM and off-chip DRAM.
- Each SM also has a massive **register file** with 65,536 32-bit registers, which is the fastest storage on the chip and private to each thread.
- Then there is **shared memory**, a programmer-managed on-chip SRAM scratchpad of about 228 KB on the H100. All threads in the same block can use it together to reuse data without going out to slow global memory.
- **Load/store units** handle moving data between the SM and the rest of the memory hierarchy, and **Special Function Units** take care of transcendental math like sin, cos, and exp.
- Finally, an **L1 cache** sits physically unified with shared memory but is managed automatically by the hardware rather than the programmer.
- The whole design comes down to one idea — keep the math units fed and busy at all times, using warp switching to cover for the inevitable memory stalls.
