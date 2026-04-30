# Answer Method for Practice & Oral Exams

Based on quiz feedback (scored 2.3/10 on first attempt) and refined on 2026-04-29.
Target: 8/10 to pass. Students typically score 5-6, so 8 is above average and is the realistic goal. 10/10 is the ideal — same structure, just a more specific or insightful concrete example.

---

## What Got Points Taken Off Last Time

- Q1 (3/10): Named components but never defined what an SM is or explained how the pieces fit together. Word dump.
- Q2 (4/10): Got the one-sentence definition but stopped. No WHY, no examples, no big picture.
- Q3 (0/10): No interpretation at all. Did not name the axes, did not find the ridge point, did not classify the kernel.

Every lost point came from the same root cause: surface vocabulary with no explanation of roles, no structure, and no big picture.

---

## The Core Problem to Avoid

Listing words without explaining them. Saying "CUDA cores, tensor cores, shared memory" is not an answer — it is a word dump. Every component, concept, or term needs a role attached to it, and every answer needs a concrete example to show you actually understand it.

---

## How Claude Should Look Up Information

Before answering any question, Claude should check the following sources in this order:

1. **`/home/bao/course_notes.md`** — the compiled reference notes extracted from all slide decks for weeks 1–5. Check here first for any topic.
2. **Slide PDFs at `/tmp/`** — if the notes do not have enough detail, grep or read the relevant slide PDF directly:
   - `/tmp/w3_mon_gpu_r2.pdf` — GPU architecture, SM, warps, SIMT, memory hierarchy
   - `/tmp/w4_mon_gpu_cnn_dnn.pdf` — SIMT vs SIMD, CUDA, tiled GEMM, precision, systolic arrays, TPU
   - `/tmp/w5_mon_tpu_gpu_transformers.pdf` — TPU, transformers, BF16, Blackwell
   - `/tmp/w2_mon_hw4ai_overview_codesign.pdf` — co-design, arithmetic intensity, roofline
   - `/tmp/w1_mon_3_hw4ai_topic_overview.pdf` — overview, neural networks, GEMM
3. **Flag it** if the answer cannot be found in either source. Do not fill in from general knowledge.

---

## Slide Accuracy Rule

Every answer must be grounded in the course slides (weeks 1–5). Do not add new facts from general knowledge. Simple logical conclusions that follow directly from slide-defined concepts are fine without needing a citation — if the slides define the ridge point as where the two ceilings meet, it follows logically that sitting at the ridge point is optimal. The rule is no new facts or numbers, but applying logic to what the slides teach is expected and encouraged.

---

## What a 10/10 Answer Looks Like

A full-credit answer has four things:

1. **A clear definition** — one sentence that says what the thing IS, not just what it contains. Spell out any acronym here.
2. **Components with roles** — each key part explained in terms of what it actually does, in plain spoken language, with each bullet building on the one before.
3. **A concrete example** — something specific from the course that shows you understand it, not just a restatement of the definition. This is what separates a 4/10 from a 10/10.
4. **A big picture close** — one sentence on why it all matters or how it fits together.

---

## Answer Structure (use for any question)

### 1. Open with a definition
One clear sentence that defines what the thing IS, not just what it contains.

> "A Streaming Multiprocessor (SM) is the fundamental execution unit of an NVIDIA GPU..."

### 2. Bullet out the key components or ideas — line by line, flowing
Each bullet = one term + its role, and each line should continue the thought from the one before. Write like each bullet is the next sentence in a spoken explanation, not a list of isolated facts.

> - Inside each SM, the **CUDA cores** handle the basic scalar math, your FP32 and INT32 operations.
> - Sitting alongside them are the **Tensor cores**, purpose-built for MMA (Matrix Multiply Accumulate) on a 4×4 matrix per clock cycle.
> - To keep those cores busy, the SM has **warp schedulers** that manage groups of 32 threads and instantly switch to a ready warp whenever the current one stalls on memory.

### 3. Give a concrete example
One specific example from the course that grounds the answer. This is the piece most answers are missing.

> "A good example is tiled GEMM — the tile size is chosen specifically to fit into shared memory, so data gets loaded from DRAM once and reused many times instead of going back to DRAM for every operation."

### 4. Close with the big picture
One sentence on how it all fits together or why it matters.

> "The whole system is designed around one idea — always keep the math units busy by switching between warps instead of ever waiting on slow memory."

---

## Style Rules

- **Talk like a person, not a textbook** — explain concepts the way you would say them out loud to a smart classmate. If the sentence would sound unnatural spoken aloud, rewrite it.
- **Use the technical vocabulary** — SIMT, warp, DRAM, arithmetic intensity, FLOP/byte, ridge point, MAC, etc. These words signal you know the material.
- **Spell out acronyms on first use** — write the full name in parentheses the first time you use an acronym. For example, SIMT (Single Instruction Multiple Threads), SM (Streaming Multiprocessor), DRAM (Dynamic Random Access Memory), MAC (Multiply Accumulate). After that, use the acronym freely.
- **No parentheses for anything else** — fold extra detail into the sentence instead. Parentheses are only for spelling out acronyms.
- **No dashes mid-sentence** — write complete sentences that flow naturally when spoken aloud. End the sentence and start a new one instead.
- **No colons mid-sentence** — same rule as dashes. Write it out as a full natural sentence.
- **Bullet points over paragraphs** — easier to follow out loud and easier to grade.
- **Bullets should flow into each other** — each line continues the thought from the one before, like a spoken explanation broken into lines. Not a list of disconnected facts.
- **Minimum filler** — skip "I think", "basically", "kind of". Be direct.
- **Slides only for facts, logic is fine** — only include facts and numbers from the course slides, but logical conclusions drawn from those facts do not need a citation.
- **Include equations for concept-level formulas** — formulas that define the concept should be included: `AI = FLOPs / Bytes`, ridge point = Peak / BW, tiled GEMM traffic = 2N², `AI = N/4`. These are small and show understanding.
- **Skip hardware-specific chip numbers** — do not cite specific TFLOPS ratings, exact bandwidth figures, or die-level specs for any chip. No one can memorize those. For precision formats, explain the principle and ratio instead: "halving bits roughly doubles throughput" rather than citing exact throughput numbers.

---

## For Each Question Type

### Definition question ("What is X?")
1. Define X in one sentence, spelling out any acronym
2. List key components/properties with roles, in plain spoken language, each bullet flowing into the next
3. Give one concrete example from the course
4. Close with why it matters or the big picture insight

### "Why" or motivation question ("Why do we use X?")
1. State the core problem X solves
2. Give the numbers if you have them (e.g., "DRAM costs 170× more energy than a multiply")
3. Give a concrete example from the course that shows it working
4. Close with the big picture

### Interpretation question ("Interpret this plot / diagram")
1. Name the axes and what they represent
2. Identify the regions — memory-bound on the left, compute-bound on the right, ridge point where they meet
3. Locate the specific kernel, classify it, and state what that means for performance
4. State what optimization that implies and why

### Compare/contrast question ("X vs Y")
1. One sentence on what each one is
2. Paired bullets on the key differences, each one explained not just named
3. State when you would use each one and why

---

## Red Flags to Avoid

| Bad | Good |
|-----|------|
| "CUDA cores is basic math" | "CUDA cores handle scalar FP32/INT32 arithmetic" |
| "shared RAM" | "shared memory, an on-chip SRAM scratchpad shared within a thread block" |
| "design algorithm and hardware together" and stop | Add WHY, then add a concrete example |
| No roofline interpretation | Name axes, find ridge, classify the kernel, state the fix |
| Answer with no concrete example | Every answer needs at least one specific example from the course |
| Adding facts or numbers not in the slides | Flag it or leave it out |
| Citing specific TFLOPS/GB/s numbers for a chip | Explain the principle and ratio instead ("halving bits doubles throughput") |
| Skipping the formula for arithmetic intensity | AI = FLOPs / Bytes is small, testable, and shows understanding — include it |
| Using colons or dashes mid-sentence | Rewrite as a full natural sentence |
| Using an acronym without spelling it out first | Write the full name in parentheses on first use |
| Answering without checking course_notes.md first | Always check notes before answering |
| Writing like a textbook definition | Write like you are explaining it out loud to someone |

---

## Example: SM Answer Done Right (targets 10/10)

- A Streaming Multiprocessor (SM) is the fundamental execution unit of an NVIDIA GPU. The entire GPU is a collection of these, and the H100 has 132 of them.
- Every computation you run on a GPU happens inside an SM, and the hardware scheduler decides which thread block goes to which one.
- Inside each SM, the **CUDA (Compute Unified Device Architecture) cores** handle the basic scalar math, your FP32 and INT32 operations.
- Sitting alongside them are the **Tensor cores**, purpose-built for MMA (Matrix Multiply Accumulate), running D = A×B + C on a 4×4 matrix in a single clock cycle.
- To keep all of those cores busy, the SM has 4 processing blocks, each with its own **warp scheduler** managing warps. A warp is a group of 32 threads executing the same instruction lockstep under SIMT (Single Instruction Multiple Threads).
- When one warp stalls waiting on memory, the scheduler immediately swaps in another ready warp. That is how the GPU hides the latency gap between on-chip SRAM and off-chip DRAM (Dynamic Random Access Memory).
- Each SM also has a massive **register file** with 65,536 32-bit registers, which is the fastest storage on the chip and private to each thread.
- Then there is **shared memory**, a programmer-managed on-chip SRAM scratchpad of about 228 KB on the H100. All threads in the same block can use it together to reuse data without going out to slow global memory.
- A concrete example of this is tiled GEMM, where the tile is loaded into shared memory once and every thread in the block reads from there instead of going back to DRAM, which is what pushes arithmetic intensity from 0.25 up to N/4 FLOP/byte.
- **Load/store units** handle moving data between the SM and the rest of the memory hierarchy, and **SFUs (Special Function Units)** take care of transcendental math like sin, cos, and exp.
- Finally, an **L1 cache** sits physically unified with shared memory but is managed automatically by the hardware rather than the programmer.
- The whole design comes down to one idea — keep the math units fed and busy at all times, using warp switching to cover for the inevitable memory stalls.
