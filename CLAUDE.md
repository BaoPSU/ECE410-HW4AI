# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

ECE 410/510 Spring 2026 — Bao Nguyen's course repo. Two parallel tracks:

1. **Codefest assignments** (`codefest/`) — weekly AI-assisted hardware/ML exercises that build skills directly applicable to the project
2. **Semester project** (`project/`) — K-Means image color quantization hardware accelerator

---

## Semester Project: K-Means Image Color Quantization Accelerator

### What it does
Reduces any RGB image to K=16 colors by clustering pixels in 3D RGB space. The CPU-only baseline (~9 sec/image on i9-12900H) is memory-bound (AI = 1.68 FLOP/byte, ridge point = 18.23 FLOP/byte). The solution offloads the distance kernel to a near-memory PIM chiplet (16 TB/s HBM3 bandwidth, 8 TFLOP/s) connected via UCIe, targeting a ~62× speedup.

### Precision
**Integer arithmetic** (not float) is used in the synthesizable core. RGB values are [0,255]; max squared distance = 3×255² = 195,075 < 2¹⁸. INT8/INT16/FP16/BF16 all overflow or lose precision; only FP32 or wider integer (≥18-bit) are correct. The final HDL core uses **18-bit integer accumulators** (`DIST_W=18`, dropped from 20 per CF07 STA after observing the top two bits were always zero) for exact results with no vendor FP IP needed. The M2 behavioral RTL used float32-encoded logic[31:0] with simulation-only `real` arithmetic as a reference model; M3 replaced it with the synthesizable integer core.

### Milestones

| Milestone | Location | Status | What it contains |
|-----------|----------|--------|-----------------|
| M1 | `project/m1/` | ✅ Done | SW baseline benchmark, UCIe interface selection justification |
| M2 | `project/m2/` | ✅ Done | Precision analysis, behavioral `distance_engine.sv` (float32 sim-only), `axil_slave.sv` AXI4-Lite wrapper (template for M3) |
| M3 | `project/m3/` | ✅ Done | Synthesizable integer `kmeans_dist_core_pipelined.sv` (3-stage), integrated `top.sv`, full OpenLane 2 synthesis run, timing closed at 100 MHz with +3.13 ns slack, 5.87 mW power, 92,689 µm² placed |
| M4 | `project/m4/` | ✅ **Submitted (tag `m4-submission` at `fe4ba1a`, 2026-05-25)** | Final package: M3 RTL renamed to canonical `top.sv`/`compute_core.sv`/`interface.sv`, end-to-end testbench, full synthesis reports, M1-vs-M4 benchmark, 9-section design justification PDF |

### Hardware Architecture

```
Host CPU (i9-12900H)
    │  UCIe (2.56 TB/s — 51× headroom over required 50 GB/s)
    ▼
axil_slave.sv          ← AXI4-Lite register map (CTRL/STATUS/PIX/CENT/RESULT)
    │
distance_engine.sv     ← Behavioral float32 compute core (M2, simulation only)
    │
kmeans_dist_core.sv    ← Synthesizable integer compute core (M3 target)
```

**`compute_core.sv`** (synthesizable, `project/m4/rtl/`, module name `kmeans_dist_core_pipelined`):
- Parameters: K=16, D=3, DATA_W=8, **DIST_W=18** (dropped from 20 per CF07 STA), LABEL_W=4
- 3-cycle latency, 1 sample/cycle throughput (Stage 1 kdist + Stage 2/3 argmin tournament)
- Flat 1D input arrays: `pixel[d]`, `centroids[k*D + d]`

**`interface.sv`** AXI4-Lite slave (synthesizable, `project/m4/rtl/`, module name `axil_slave_int`):
- `0x000` CTRL (write bit[0]=start), `0x004` STATUS (read bit[0]=done)
- `0x008` PIXEL (3 bytes packed in lower 24 bits, INT8 per channel)
- `0x010..0x04C` CENT[0..15] (3 bytes packed in lower 24 bits per centroid)
- `0x100` RESULT_LABEL, `0x104` RESULT_DIST (18-bit)

---

## Simulation Commands

**Run end-to-end M4 testbench** (top + AXI4-Lite slave + compute core, drives a full read/write transaction through AXI):
```bash
bash project/m4/sim/run_iverilog.sh
```
Outputs `project/m4/sim/final_run.log` (PASS line at bottom) and `project/m4/sim/tb_top.vcd`. The TB writes 16 RGB centroids, writes 1 pixel, pulses CTRL.start, waits for STATUS.done, reads RESULT_LABEL + RESULT_DIST, compares against an independent SW reference, prints PASS.

**Run OpenLane 2 synthesis** (dockerized, sky130 PDK, 10 ns target clock):
```bash
cd project/m4/synth
sg docker -c 'openlane --dockerized config.json'
```
The `ERROR_ON_SYNTH_CHECKS: false` knob in `config.json` is required to work around a yosys false-positive on the AXI address-decode bits; see `project/m3/synth/HOW_TO_FIX_4C.md` for the investigation.

**Run M2 behavioral testbenches** (legacy, float32 sim-only reference model):
```bash
cd project/m2
bash sim/run_iverilog.sh
```
Compiles and runs `distance_engine_tb.sv` and `axil_slave_tb.sv` with Icarus Verilog.

**Run SW baseline benchmark** (M1 / CF9 rerun):
```bash
cd /home/bao/kmeans_project
source venv/bin/activate
python3 sw_baseline.py
```
Records 10 wall-clock runs on bliss.jpg 800×600, K=16, max_iters=20.

---

## Codefest Assignments

Each codefest (cf01–cf09) has a **CMAN** (analysis writeup) and usually a **CLLM** (LLM interaction log) that document the reasoning behind design choices. These are not just homework; the techniques directly inform the project:

| Codefest | Key skill | Project relevance |
|----------|-----------|-------------------|
| CF01 | Workload accounting, profiling (ResNet-18, cProfile) | Identified distance kernel as 46% of runtime |
| CF02 | Roofline analysis, quantization profiling | Justified PIM architecture, memory-bound diagnosis |
| CF03 | CUDA GEMM (naive + tiled), DRAM traffic analysis | GEMM tiling patterns inform centroid broadcast |
| CF04 | Fixed-point quantization, MAC HDL with cocotb | INT18 decision and MAC discipline |
| CF05 | 2×2 weight-stationary systolic trace | Output-stationary pipelining intuition for M3 |
| CF06 | Resistive crossbar sneak-path KCL | IMC analysis (peripheral to K-Means but core to W7 lectures) |
| **CF07** | **STA on v0 single-cycle prototype** | **Directly produced the M3 3-stage pipeline plan + DIST_W=18 trim** |
| CF08 | AER bandwidth, burst vs mean | Same methodology as M1 interface selection (mean-rate sizing is wrong, peak-rate is right) |
| CF09 | First-principles AI + accelerator benchmark vs SW baseline | Final benchmark + remaining-tasks v2 roadmap (post-M4) |

When working on a project milestone, check the corresponding codefest for analysis that supports the design decision. The `project/design_log.md` walks the full M1→M4 narrative with explicit lecture and codefest cross-references.

---

## Repository Layout

```
codefest/
  cf01–cf09/          Per-codefest: cman_*.md, CLLM session logs, profiling data, HDL/CUDA code
  presentation.md     Final project presentation outline

project/
  design_log.md       M1→M4 narrative with lecture + codefest cross-references
  heilmeier.md        Project proposal (Heilmeier questions, read this for full context)
  remaining_tasks.md  Post-M4 v2 priority list (3 specific changes)
  m1/                 SW baseline, interface selection
  m2/rtl/             distance_engine.sv (float32 sim-only), axil_slave.sv (template)
  m2/tb/              Testbenches for M2 RTL
  m2/sim/             run_iverilog.sh
  m3/                 Integrated top + 3-stage pipelined integer compute + AXI4-Lite, full OpenLane synth
  m3/rtl/             top.sv, kmeans_dist_core_pipelined.sv, axil_slave_int.sv
  m3/synth/           OpenLane config + logs + STA/area/power reports + 4c fix notes
  m4/                 Final submission package (canonical filenames, benchmark, 9-section PDF)
  m4/rtl/             top.sv, compute_core.sv, interface.sv (renamed M3 RTL, same content)
  m4/bench/           benchmark.md, benchmark_data.csv, roofline_final.png
  m4/report/          design_justification.pdf + figures/

course-materials/
  week01–week08/      slides/ and docs/ per week + weekXX_notes.md
  study/quiz1/        Quiz 1 cheatsheet, study guide, practice questions, results
  study/quiz2/        Quiz 2 cheatsheet, study guide, practice questions, real-attempt prep
  study/final/        Cumulative final (wks 1-8): official Teuscher cheat sheet + study guide, practice Qs, gap analysis
```

---

## Study Material Coverage Tracker

This section tracks which slide files have been processed into notes or the cheatsheet. When new slides are uploaded, check this table first — anything marked **NOT covered** needs to be summarized before the cheatsheet/notes are up to date.

### Week 1 — `course-materials/week01/slides/`

| Slide file | Topics | Covered in |
|-----------|--------|------------|
| `w1_mon_1_introduction_motivation.pdf` | Memory wall, energy cost of data movement, architecture evolution (CPU→GPU→NPU) | `quiz1_cheatsheet.md` §1, `quiz1_study_guide.md` Unit 1 |
| `w1_mon_2_course_details.pdf` | Course logistics, assignment structure | `week01_notes.md` |
| `w1_mon_3_hw4ai_topic_overview.pdf` | HW/SW codesign overview, PPAC trade-offs | `quiz1_cheatsheet.md` §13–15 |
| `w1_wed_codefest_1.pdf` | Codefest 1 challenge problems (FC network workload accounting) | `quiz1_cheatsheet.md` §17 (CMAN CF01 example) |
| `w1_wed_llm_tips_and_tricks.pdf` | LLM usage for coursework | ❌ **NOT covered** in cheatsheet or notes |

### Week 2 — `course-materials/week02/slides/`

| Slide file | Topics | Covered in |
|-----------|--------|------------|
| *(no slides in repo)* | Roofline model, arithmetic intensity, ridge point, HW/SW partitioning | Topics covered via `week02_notes.md` summary + `quiz1_cheatsheet.md` §2–3, §13 |

### Week 3 — `course-materials/week03/slides/`

| Slide file | Topics | Covered in |
|-----------|--------|------------|
| *(no slides in repo)* | GPU architecture: SIMT, warps, memory hierarchy, CUDA programming model | Topics covered via `week03_notes.md` summary + `quiz1_cheatsheet.md` §6–10 |

### Week 4 — `course-materials/week04/slides/` and `docs/`

| Slide file | Topics | Covered in |
|-----------|--------|------------|
| `w4_mon_gpu_cnn_dnn.pdf` | SIMD vs SIMT, tensor cores, tiled GEMM on GPU, precision formats (FP4/NVFP4/INT8), ResNet-18, CNN/DNN ops | `week04_ai_summary.md` §1, `quiz1_cheatsheet.md` §10–12 |
| `w4_mon_vlsi_design.pdf` | VLSI abstraction levels, EDA tools, cocotb, Tiny Tapeout, Python HDLs | `week04_ai_summary.md` §2, `quiz1_cheatsheet.md` §14 |
| `w4_mon_recap.pdf` | Agentic co-processor trends, M2 milestone requirements, Quiz 1 prep advice | `week04_ai_summary.md` §3 |
| `codefest_presentation_instructions_spring26.pdf` | How to present at codefest | ❌ **NOT covered** in cheatsheet or notes |

### Week 5 — `course-materials/week05/slides/`

| Slide file | Topics | Covered in |
|-----------|--------|------------|
| `w5_mon_recap.pdf` | GPU power trends (A100→Vera Rubin), PUE, data center scale, AI/EDA tools, Quiz 1 info | `week05_notes.md` §1, `quiz2_cheatsheet.md` §1 |
| `w5_mon_tpu_gpu_transformers.pdf` | CPU/GPU/TPU comparison, systolic arrays (3 dataflows), TPU roadmap v4→v7, BF16, transformers (non-recurrent, self-attention Q/K/V), NVIDIA Transformer Engine, Blackwell B200, neuromorphic/SNN, No Free Lunch, CUDA MLP | `week05_notes.md` §2–12, `quiz2_cheatsheet.md` §2–16 |

### Week 6 — `course-materials/week06/`

| Slide file | Topics | Covered in |
|-----------|--------|------------|
| `w6_mon_recap.pdf` | Week 5 recap, Quiz 1 reminder, Google TPU 8 (8t vs 8i), week plan | `week06_notes.md` §0 |
| `w6_mon_transformers_in_memory.pdf` | Algorithm acceleration (traditional + emerging tech tables), processor evolution, NFL theorem, TPU/systolic recap, transformer (what is it, learning, RLHF, recurrence, math ops, learned vs fixed, GPU mapping) | `week06_notes.md` §1–5 |

### Week 7 — `course-materials/week07/slides/`

| Slide file | Topics | Covered in |
|-----------|--------|------------|
| `w7_mon_recap.pdf` | Week 6 recap questions, inference vs training in systolic array (weight-stationary, 3 matmuls/layer for training), Quiz 1 results scatter | `week07_notes.md` §0 |
| `w7_mon_neuromorphic_chips.pdf` | IMC fundamentals (energy of memory access, DRAM 2nJ vs INT4 mult 0.1pJ), crossbar primitive (Ohm + Kirchhoff for MVM), memory types (RRAM/PCM/STT-MRAM), sneak paths + solutions (diodes, 1T1R), IMC maturity (TRL 7–8), sparse MVM and sparse-on-crossbar (permute & pack, CSR format, 70% sparsity crossover), neuromorphic chips: characteristics + approaches, AER protocol, NoC, major chips (SpiNNaker, TrueNorth, NorthPole 10 axioms, BrainScaleS-2 AdEx, Loihi/Loihi 2 LIF + Lava, Akida TENNs), LLM on Loihi 2, current limitations, "AlexNet moment", feature maturation, autonomous vehicle applications | `week07_notes.md` §1–12 |
| `w7_wed_codefest_7.pdf` | CF7 lecture: CSR Compressed Sparse Row (values/col_idx/row_ptr), CSR 4×4 example with 2 NZ per row (worked storage), reconstructing A from CSR (walk-by-row_ptr trace), ASIC design flow (front-end / back-end), OpenLane 2 tools overview. 3 QUIZ-marked slides (CSR fundamentals + 4×4 example + reconstruction). | `week07_notes.md` §4 (CSR already covered); `study/quiz2/quiz_marked_slides.md` §Q7.15–Q7.17 |

### Week 8 — `course-materials/week08/slides/`

| Slide file | Topics | Covered in |
|-----------|--------|------------|
| `w8_mon_recap.pdf` | Week 7 recap | (recap deck — content already covered) |
| `w8_mon_neuromorphic_chips.pdf` | Neuromorphic chips deep dive (~61 slides): NM chip definitions, Cerebras NOT neuromorphic, key characteristics, flexibility↔performance trade-off, NN acceleration ecosystem, inference vs training, neuromorphic processor architecture, crossbar building block, why-CPU-in-NM, commercialisation comparison tables, academic+commercial chip tables, AER spike protocol, NoC topologies (crossbar/star/ring/tree/mesh/torus), AER-over-NoC routing example, source-routing tables, Neuromorphic Commons (THOR), SpiNNaker / SpiNNaker2 deep dive, memristors + STDP, IBM TrueNorth (65 mW, 5.4 B transistors, 1 M neurons), IBM NorthPole (dense INT2/4/8 inference, not truly neuromorphic), BrainScaleS / BrainScaleS-2 (10,000× real-time, AdEx, PPU), Loihi / Loihi 2 (LIF + RF + Hopf resonator), LLM on Loihi 2 paper critique, Akida (TENNs), brain-like HW critique, industry timeline, neuron-count progression, feature maturation, gaps in NM software ecosystem, are spikes the future for LLMs?, NM design choices recap. 5 QUIZ stickers (pp.8, 19, 20, 22, 23) + 4 red-font instructor questions (pp.2, 5, 10, 53). | `study/quiz2/quiz_marked_slides.md` §Q8.1–Q8.4 + Week 8 QUIZ slides; `study/quiz2/quiz_marked_slides/quiz_marked_combined.pdf` (regenerated, now 37 slides) |

### What to do when new slides are uploaded

1. Add a row to the table above for the new file
2. Mark it ❌ NOT covered
3. Read the slide and update the relevant `weekXX_notes.md` or `quiz1_cheatsheet.md`
4. Change the status to the file it was added to

---

## Tool Versions
- Python 3.12.3, NumPy 2.4.4
- cocotb 2.0.1 with Icarus Verilog (icarus sim backend)
- iverilog ≥ 11 required for SystemVerilog 2012 (`-g2012`)
