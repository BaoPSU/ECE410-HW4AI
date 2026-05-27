# ECE410 HW4 AI

## Author
Bao Nguyen

## Course
ECE 410/510 Spring 2026

## Description
This repository contains my ECE410/510 Codefest homework assignments using AI tools, plus the semester project.

---

## 📌 M4 Final Submission (submitted, tagged `m4-submission` at `fe4ba1a`)

**M4 deliverables → [`project/m4/`](project/m4/README.md)**
**Design justification report → [`project/m4/report/design_justification.pdf`](project/m4/report/design_justification.pdf)**
**End-to-end design log (M1 to M4 narrative) → [`project/design_log.md`](project/design_log.md)**

The semester project is a **K-Means image color quantization accelerator**, a 3-stage pipelined integer compute core wrapped in an AXI4-Lite slave, synthesizable through OpenLane 2 on sky130. Post-PnR results: timing closed at 100 MHz with +3.13 ns of positive slack, 5.87 mW power, 0.093 mm² placed area, end-to-end PASS via AXI4-Lite.

---

## Repository Structure

```
codefest/
  cf01/                       Codefest 1: workload accounting, ResNet-18 profiling
  cf02/                       Codefest 2: roofline analysis, quantization profiling
  cf03/                       Codefest 3: GEMM CUDA, DRAM traffic analysis
  cf04/                       Codefest 4: quantization, MAC HDL, LLM comparison
  cf05/                       Codefest 5: 2x2 weight-stationary systolic trace
  cf06/                       Codefest 6: resistive crossbar sneak-path KCL
  cf07/                       Codefest 7: STA + sparsity analysis (drove M3 pipeline plan)
  cf08/                       Codefest 8: AER bandwidth analysis (mean vs burst, SPI vs I2C)
  cf09/                       Codefest 9: AI from first principles + benchmark vs SW baseline

course-materials/             Weekly slides, docs, and notes (weeks 1-8)
  week01/ - week08/           slides/, docs/ per week + weekXX_notes.md
  study/                      Quiz 1 + Quiz 2 cheat sheets, study guides, practice questions

project/                      K-Means image color quantization accelerator
  design_log.md               M1 to M4 narrative with lecture + codefest cross-references
  heilmeier.md                Project proposal (Heilmeier questions)
  m1/                         Milestone 1: SW baseline + UCIe interface selection
  m2/                         Milestone 2: precision choice + behavioral RTL + AXI4-Lite slave
  m3/                         Milestone 3: integrated top + OpenLane 2 synthesis (timing closed)
  m4/                         Milestone 4: final package + benchmark + 9-section design justification PDF
  remaining_tasks.md          Post-M4 priority list (3 specific v2 changes)
```

---

## Project: K-Means Image Color Quantization Accelerator

![Algorithm Diagram](project/algorithm_diagram.png)

### Compute Core (`project/m4/rtl/compute_core.sv`)

Synthesizable K-Means squared-distance engine. For each input pixel, computes the squared Euclidean distance to all K centroids in parallel and outputs the nearest centroid label through a 3-stage pipeline (one sample per cycle in steady state).

**Pipeline stages:**
1. Stage 1: 16 parallel kdist computes (sub + mul + add tree per centroid), registered
2. Stage 2: argmin tournament 16 → 8 → 4
3. Stage 3: argmin tournament 4 → 2 → 1, registers label + min_dist + done

**Interface (top-level `project/m4/rtl/top.sv`)**

The top exposes an AXI4-Lite slave only. Pixels and centroids go in via byte-packed registers; label and distance come out via read registers. Internal compute-core ports:

| Port | Width | Direction | Description |
|------|-------|-----------|-------------|
| `clk` | 1 | in | Clock |
| `rst_n` | 1 | in | Active-low synchronous reset |
| `start` | 1 | in | Pulse high for one cycle to begin (asserted by AXI CTRL write) |
| `pixel[d]` | 8 | in | Pixel channel d (0=R, 1=G, 2=B) |
| `centroids[k*D+d]` | 8 | in | Centroid k channel d (flat 1D, K×D elements) |
| `done` | 1 | out | High for one cycle when outputs are valid (3 cycles after start) |
| `min_dist` | 18 | out | Minimum squared distance (integer) |
| `label` | 4 | out | Nearest centroid index (0..K-1) |

**Parameters:** K=16, D=3, DATA_W=8, **DIST_W=18** (dropped from 20 per CF07 STA: top two bits always zero since 3×255²=195,075 < 2^18), LABEL_W=4

**Precision: integer arithmetic (zero quantization error)**

RGB values are integers in [0, 255]. Max squared distance over D=3 dimensions is 3×255²=195,075, fits in 18 bits exactly. INT8/INT16/FP16/BF16 all overflow or lose precision; only FP32 or wider integer (≥18-bit) are correct. The HDL core uses 18-bit integer accumulators for exact results without vendor FP IP.

The M1 SW baseline measured AI = 1.68 FLOP/byte against a ridge point of 18.23, placing the kernel firmly in the memory-bound regime. The M4 accelerator point sits at AI = 48.0 ops/byte (full-reuse, first-principles per CF9 CMAN), moving the kernel from memory-bound to compute-bound.

**UCIe interface justification**

Documented in `project/m1/interface_selection.md`. UCIe provides 51× more bandwidth than the required 50 GB/s for streaming 1080p at 30 fps, ensuring the compute core is never bandwidth-starved.

**Verified with iverilog**
- `project/m4/sim/run_iverilog.sh` runs `project/m4/tb/tb_top.sv` end-to-end through AXI4-Lite
- Test loads 16 RGB centroids + 1 pixel, asserts `done` 3 cycles after `start`, reads `RESULT_LABEL` and `RESULT_DIST` back, checks against an independent SW reference, prints `PASS`
- Output transcript at `project/m4/sim/final_run.log`

### Milestones

| Milestone | Location | Status |
|-----------|----------|--------|
| M1: Interface selection + SW baseline | `project/m1/` | ✅ Done |
| M2: Precision choice + behavioral RTL + AXI4-Lite slave | `project/m2/` | ✅ Done |
| M3: Integrated top + OpenLane synthesis (timing closed +3.13 ns) | `project/m3/` | ✅ Done |
| M4: Final package + benchmark + 9-section design justification PDF | [`project/m4/`](project/m4/README.md) | ✅ **Submitted (tag `m4-submission` at `fe4ba1a`)** |

![System Diagram](project/m1/system_diagram.png)
