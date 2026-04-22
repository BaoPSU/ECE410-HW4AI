# ECE410 HW4 AI

## Author
Bao Nguyen

## Course
ECE 410/510 Spring 2026

## Description
This repository contains my ECE410 homework assignments using AI tools.

---

## Repository Structure

```
codefest/cf04/          Codefest 4 deliverables
  hdl/                  RTL source files (mac_llm_A.v, mac_llm_B.v, mac_correct.v)
  cocotb_mac/           cocotb testbench for mac_correct.v (COPT Part A)
  review/               Code review comparing Claude vs Gemini MAC implementations
  gemini_session.md     Full Gemini 3 Fast conversation transcript

course-materials/week04/ Week 4 AI summary (GPU/CUDA, VLSI/EDA tools)

project/                K-Means image color quantization accelerator
  hdl/                  Synthesizable RTL compute core (COPT Part B)
  m1/                   Milestone 1: interface selection, SW baseline
  m2/                   Milestone 2: precision choice, behavioral RTL, AXI4-Lite slave
```

---

## Project: K-Means Image Color Quantization Accelerator

### Compute Core (project/hdl/kmeans_dist_core.sv)

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
| `centroids[k*D+d]` | 8 | in | Centroid k channel d (flat 1D, K*D elements) |
| `done` | 1 | out | High for one cycle when outputs are valid |
| `min_dist` | 20 | out | Minimum squared distance (integer) |
| `label` | 4 | out | Nearest centroid index (0..K-1) |

**Parameters:** K=16, D=3, DATA_W=8, DIST_W=20, LABEL_W=4

**Precision choice — integer arithmetic (zero quantization error)**

RGB pixel values are integers in [0, 255]. The maximum possible squared distance
over D=3 dimensions is 3 x 255^2 = 195,075, which fits in 18 bits. Integer
arithmetic gives exact results with no rounding error. This is equivalent to the
FP32 choice documented in `project/m2/precision_choice.md`: FP32 is exact for
integers up to 2^24, and since 195,075 < 2^24 every computation is exact in both
formats. The synthesizable core uses integer arithmetic to avoid requiring vendor
FP IP and to be directly implementable with standard synthesizable RTL.

The M1 software baseline (`project/m1/sw_baseline.md`) measured 1.38 GFLOP per
image (N=480,000 pixels, K=16, D=3, 20 iterations) against ~69 MB of memory
traffic per iteration, giving an arithmetic intensity of approximately 1 FLOP/byte.
This places the kernel well below the compute-bound ridge point on the roofline,
confirming it is memory-bound. At this arithmetic intensity, using wider precision
(FP64) would not improve throughput but would double memory bandwidth — the wrong
tradeoff. INT8 and INT16 would overflow on squared differences (max diff^2 = 65,025
exceeds INT16 range of 32,767), causing wrong centroid assignments. Integer 18-bit
arithmetic (implemented here in 20-bit accumulators) is the minimum exact-correct
format, directly justified by the M1 intensity analysis.

**UCIe interface justification**

Documented in `project/m1/interface_selection.md`. UCIe provides 51x more
bandwidth than required for streaming 1080p at 30 fps, guaranteeing the compute
core is never bandwidth-starved.

**Verified with cocotb 2.0.1**
- `test_kmeans_nearest`: black pixel (0,0,0) assigns to centroid at origin, min_dist=0
- `test_kmeans_midpoint`: gray pixel (128,128,128) assigns to centroid at (128,128,128), min_dist=0

---

## Codefest 4 — CLLM (AI-Permitted)

Two LLMs (Claude Sonnet 4.6 and Gemini 3 Fast) each generated a synthesizable
SystemVerilog MAC module from the same prompt. Both pass all 6 simulation tests.
Review in `codefest/cf04/review/mac_code_review.md`.

## Codefest 4 — COPT (Bonus)

**Part A:** cocotb testbench on `mac_correct.v`
- `test_mac_basic`: 6 assertions (positive accumulation, reset, negative operands)
- `test_mac_overflow`: 150,000-cycle stress test confirms 32-bit two's complement
  wrap at cycle 133,146 (2147479576 -> -2147471591)

**Part B:** Synthesizable K-Means compute core stub — see `project/hdl/` above.
