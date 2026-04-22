# ECE410 HW4 AI

## Author
Bao Nguyen

## Course
ECE 410/510 Spring 2026

## Description
This repository contains my ECE410/510 Codefest homework assignments using AI tools, plus the semester project.

---

## Repository Structure

```
codefest/
  cf01/                       Codefest 1 — workload accounting, ResNet-18 profiling
    profiling/                resnet18_profile.txt + analysis
    cman_workload_accounting.md

  cf02/                       Codefest 2 — roofline analysis, quantization profiling
    analysis/                 arithmetic-intensity calculations, partition rationale
    profiling/                roofline plots, quantized-model profile
    cman_roofline.md / .png

  cf03/                       Codefest 3 — GEMM CUDA, DRAM traffic analysis
    cuda/                     gemm_naive.cu, gemm_tiled.cu
    copt/                     nn_forward_gpu.py, copt_output.txt
    analysis/                 gemm_analysis.md
    profiling/                roofline plot + run_and_plot.py
    cman_dram_traffic.md

  cf04/                       Codefest 4 — Quantization, MAC HDL, LLM comparison
    hdl/                      mac_llm_A.v (Claude), mac_llm_B.v (Gemini), mac_correct.v
    cocotb_mac/               cocotb testbench + results (COPT Part A)
    review/                   mac_code_review.md — Claude vs Gemini comparison
    gemini_session.md         Full Gemini 3 Fast conversation transcript
    cman_quantization.md      INT8 symmetric quantization worksheet (CMAN)
    Quantization_Final_Fixed.xlsx  Supporting calculations (CMAN)

  codefest_presentation_bao_nguyen.pptx

course-materials/             Weekly slides, docs, and notes (weeks 1–4)

project/                      K-Means image color quantization accelerator
  hdl/                        Synthesizable RTL distance core (COPT Part B)
  m1/                         Milestone 1: interface selection, SW baseline
  m2/                         Milestone 2: precision choice, behavioral RTL, AXI4-Lite slave
```

---

## Codefest 4 — CMAN (AI-Permitted)

Manual INT8 symmetric per-tensor quantization of a 4×4 FP32 weight matrix.
Full worksheet in `codefest/cf04/cman_quantization.md`; supporting Excel calculations in `Quantization_Final_Fixed.xlsx`.

**Tasks completed:**

| Task | Description | Key Result |
|------|-------------|------------|
| Scale factor | S = max(\|W\|) / 127 | max = 2.31 → **S = 0.018189** |
| Quantize | W_q = clamp(round(W / S), −128, 127) | Full 4×4 INT8 matrix |
| Dequantize | W_deq = W_q × S | Full 4×4 FP32 matrix |
| Error analysis | MAE = mean(\|W − W_deq\|) | Largest error = 0.0083 (R1C4); **MAE = 0.0043** |
| Bad scale | S_bad = 0.01 (too small) | 4 elements clip; **MAE = 0.1713** (40× worse) |

**Takeaway:** When S is too small, large-magnitude weights hard-clip to ±127/−128 and cannot be recovered on dequantization. The optimal S derived from max(\|W\|) minimizes this clipping at the cost of slightly coarser step size.

---

## Codefest 4 — CLLM (AI-Permitted)

Two LLMs (Claude Sonnet 4.6 and Gemini 3 Fast) each generated a synthesizable
SystemVerilog MAC module from the same prompt. Both pass all 6 simulation tests.
Full comparison in `codefest/cf04/review/mac_code_review.md`.

**Prompt spec:** `mac` module — 8-bit signed a, b; 32-bit signed accumulator `out`; active-high synchronous reset; `always_ff`; synthesizable SV only.

| Check | LLM A (Claude) | LLM B (Gemini) |
|-------|---------------|---------------|
| `always_ff` used | ✓ | ✓ |
| `logic signed` on all ports | ✓ | ✓ |
| Sign extension | explicit `{{16{product[15]}}, product}` | implicit (relies on SV standard) |
| Combinational style | `always_comb` (preferred) | `assign` (functional) |
| All 6 testbench cases pass | ✓ | ✓ |

The explicit sign-extension in LLM A is more portable to Verilog-2001; both are correct per IEEE 1800.
Gemini conversation transcript: `codefest/cf04/gemini_session.md`.

---

## Codefest 4 — COPT (Bonus)

**Part A — cocotb testbench on `mac_correct.v`** (`codefest/cf04/cocotb_mac/`)

`mac_correct.v` incorporates all best-practice fixes from the review: `always_ff`, `always_comb`, explicit sign extension, `logic signed` everywhere.

| Test | Description | Result |
|------|-------------|--------|
| `test_mac_basic` | 6 assertions: positive accumulation (×3 cycles), reset, negative operands (×2 cycles) | PASS |
| `test_mac_overflow` | 150,000-cycle stress test — 32-bit signed wraps at cycle 133,146 (2147479576 → −2147471591) | PASS |

**Part B — K-Means distance compute core** (`project/hdl/kmeans_dist_core.sv`)

See the Project section below.

---

## Project: K-Means Image Color Quantization Accelerator

### Compute Core (`project/hdl/kmeans_dist_core.sv`)

Synthesizable K-Means squared-distance engine. For each input pixel, computes
the squared Euclidean distance to all K centroids and outputs the nearest centroid
label in a single clock cycle.

**Interface**

| Port | Width | Direction | Description |
|------|-------|-----------|-------------|
| `clk` | 1 | in | Clock |
| `rst_n` | 1 | in | Active-low synchronous reset |
| `start` | 1 | in | Pulse high for one cycle to begin |
| `pixel[d]` | 8 | in | Pixel channel d (0=R, 1=G, 2=B) |
| `centroids[k*D+d]` | 8 | in | Centroid k channel d (flat 1D, K×D elements) |
| `done` | 1 | out | High for one cycle when outputs are valid |
| `min_dist` | 20 | out | Minimum squared distance (integer) |
| `label` | 4 | out | Nearest centroid index (0..K-1) |

**Parameters:** K=16, D=3, DATA_W=8, DIST_W=20, LABEL_W=4

**Precision — integer arithmetic (zero quantization error)**

RGB values are integers in [0, 255]. Max squared distance over D=3 dimensions is 3×255²=195,075, which fits in 18 bits. INT8/INT16 would overflow (max diff² = 65,025 exceeds INT16 range). Integer 20-bit accumulators give exact results without vendor FP IP.

The M1 SW baseline measured ~1 FLOP/byte arithmetic intensity, placing the kernel firmly in the memory-bound regime. This justifies avoiding wider FP formats that would only increase memory traffic.

**UCIe interface justification**

Documented in `project/m1/interface_selection.md`. UCIe provides 51× more bandwidth than required for streaming 1080p at 30 fps, ensuring the compute core is never bandwidth-starved.

**Verified with cocotb 2.0.1**
- `test_kmeans_nearest`: black pixel (0,0,0) → centroid at origin, min_dist=0
- `test_kmeans_midpoint`: gray pixel (128,128,128) → centroid at (128,128,128), min_dist=0

### Milestones

| Milestone | Location | Status |
|-----------|----------|--------|
| M1: Interface selection + SW baseline | `project/m1/` | Done |
| M2: Precision choice + behavioral RTL + AXI4-Lite slave | `project/m2/` | Done |
