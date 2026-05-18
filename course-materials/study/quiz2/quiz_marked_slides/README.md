# QUIZ-Marked Slides — Combined PDF

**File**: `quiz_marked_combined.pdf` — 37 slides total

## What's in here

Every slide in weeks 6, 7, and 8 that has a red **QUIZ** sticker, plus week 8 slides with red-font instructor questions (Q8.1–Q8.4 in `../quiz_marked_slides.md`) — same study priority. Extracted from the source decks and merged into one PDF for focused review.

## Page-by-page index

### From `week06/w6_mon_transformers_in_memory.pdf` (6 slides)

| Source page | Topic |
|:-----------:|-------|
| 3 | How can we accelerate an algorithm? (the 10 levers) |
| 5 | Traditional technology — speedup/difficulty/applicability table |
| 6 | Emerging technology — master table |
| 8 | No Free Lunch theorem (Wolpert & Macready, 1997) |
| 10 | Systolic array — PE structure + neural computing unit |
| 11 | How to map a deep neural net on a systolic array |

### From `week07/slides/w7_mon_neuromorphic_chips.pdf` (19 slides)

| Source page | Topic |
|:-----------:|-------|
| 4 | How can we accelerate an algorithm? (recap) |
| 5 | Emerging technology — master table |
| 8 | Computing in processor vs computing in memory (memory types) |
| 11 | MVM via crossbar — Ohm + Kirchhoff equation |
| 14 | How can we map an NN onto a crossbar? (parallel mult + current sum) |
| 15 | How can we map an NN onto a crossbar? (conductance + capacitance) |
| 16 | Sneak paths (1) — 2×2 setup |
| 17 | Sneak paths (2) — 4×4 array, draw the current flow |
| 18 | Sneak paths (3) — read vs sneak current paths |
| 19 | Sneak paths (4) — solutions: diodes or 1T1R |
| 22 | Questions: IMC primary advantage, synaptic weights, SNN benefits |
| 24 | The crossbar primitive — analog MVM in O(1) time |
| 26 | Efficient sparse mapping on a crossbar (permute & pack, gating) |
| 39 | Neural network acceleration ecosystem (GPU, TPU/NPU, FPGA, ASIC) |
| 40 | Key building block: the crossbar (for neuromorphic chips) |
| 48 | It's all about AER (Address Event Representation) |
| 49 | Network-on-Chip (NoC) — 2D mesh |
| 50 | Example: AER over NoC — concrete spike packet |
| 51 | How does the source know the destination? (routing table at source core) |

### From `week07/slides/w7_wed_codefest_7.pdf` (3 slides — CF7 lecture)

| Source page | Topic |
|:-----------:|-------|
| 2 | CSR: Compressed Sparse Row — three arrays, how to read row i |
| 3 | CSR Example: 4×4 with 2 NZ per row (worked storage example) |
| 4 | Reconstructing A from CSR — walk-by-row_ptr trace on the 4×4 |

### From `week08/slides/w8_mon_neuromorphic_chips.pdf` (9 slides)

QUIZ-stickered slides + 4 red-font instructor questions (same priority).

| Source page | Topic | Why included |
|:-----------:|-------|--------------|
| 2 | What are neuromorphic chips? — Cerebras WSE-3 NOT neuromorphic | **Q8.1 (red label)** |
| 5 | The usual trade-offs — "Why not do everything in software?" | **Q8.2 (red text)** |
| 8 | Neural network acceleration ecosystem (GPU/TPU/FPGA/ASIC) | QUIZ sticker |
| 10 | Key building block: the crossbar — "What to do with negative weights?" | **Q8.3 (red text)** |
| 19 | AER (Address Event Representation) | QUIZ sticker |
| 20 | Network-on-Chip (NoC) — 2D mesh | QUIZ sticker |
| 22 | Example: AER over NoC (concrete spike packet) | QUIZ sticker |
| 23 | How does the source know the destination? (routing table) | QUIZ sticker |
| 53 | LLM on Loihi 2 — "Why is that gain performance not impressive?" | **Q8.4 (red text)** |

## How to regenerate

If the source decks change or more QUIZ slides get added:

```bash
cd course-materials/study/quiz2
python3 extract_quiz_slides.py
```

The script reads page lists from `extract_quiz_slides.py` and rebuilds `quiz_marked_combined.pdf` in this folder.

## Companion files

- `../quiz_marked_slides.md` — text notes on every QUIZ slide
- `../study_guide.md` — full conceptual depth
- `../cheatsheet.md` — one-page facts
- `../practice_questions.md` — Q&A drill set

> Week 5 slides aren't pulled into the combined PDF because the source PDF isn't in the repo (the `w5_mon_tpu_gpu_transformers.pdf` is in `week05/slides/` but wasn't visually re-scanned for QUIZ stickers as part of this batch). The week 5 quiz content is covered in `quiz_marked_slides.md` §Q5.
