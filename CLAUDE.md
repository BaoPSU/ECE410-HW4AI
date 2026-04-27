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
**Integer arithmetic** (not float) is used in the synthesizable core. RGB values are [0,255]; max squared distance = 3×255² = 195,075 < 2¹⁸. INT8/INT16/FP16/BF16 all overflow or lose precision — only FP32 or wider integer (≥18-bit) are correct. The HDL core uses 20-bit integer accumulators (`DIST_W=20`) for exact results with no vendor FP IP needed. The behavioral M2 RTL uses float32-encoded logic[31:0] with simulation-only `real` arithmetic (not synthesizable; will be replaced with FP32 units in M3).

### Milestones

| Milestone | Location | Status | What it contains |
|-----------|----------|--------|-----------------|
| M1 | `project/m1/` | Done | SW baseline benchmark, UCIe interface selection justification |
| M2 | `project/m2/` | Done | Precision analysis, behavioral `distance_engine.sv` (float32), `axil_slave.sv` AXI4-Lite wrapper |
| M3+ | `project/hdl/` | In progress | Synthesizable integer `kmeans_dist_core.sv`, cocotb testbench |

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

**`kmeans_dist_core.sv`** (synthesizable, `project/hdl/`):
- Parameters: K=16, D=3, DATA_W=8, DIST_W=20, LABEL_W=4
- 1-cycle latency: fully combinational dist+argmin, registered output
- Flat 1D input arrays: `pixel[d]`, `centroids[k*D + d]`

**`axil_slave.sv`** register map (`project/m2/rtl/`):
- `0x000` CTRL (write bit[0]=start), `0x004` STATUS (read bit[0]=done)
- `0x008–0x010` PIX_R/G/B (float32), `0x014–0x0D0` centroid array
- `0x100` RESULT_LABEL, `0x104` RESULT_DIST

---

## Simulation Commands

**Run cocotb testbench** for `kmeans_dist_core.sv` (synthesizable integer core):
```bash
cd project/hdl
make
```
Tests: `test_kmeans_nearest` (black pixel → origin centroid, min_dist=0), `test_kmeans_midpoint` (gray pixel → matching centroid, min_dist=0).

**Run iverilog testbenches** for M2 behavioral RTL:
```bash
cd project/m2
bash sim/run_iverilog.sh
```
Compiles and runs `distance_engine_tb.sv` and `axil_slave_tb.sv` with Icarus Verilog.

**Run SW baseline benchmark:**
```bash
cd /home/bao/kmeans_project
source venv/bin/activate
python3 sw_baseline.py
```

---

## Codefest Assignments

Each codefest (cf01–cf04) has a **CMAN** (analysis writeup) and **CLLM** (LLM interaction log) that document the reasoning behind design choices. These are not just homework — the techniques directly inform the project:

| Codefest | Key skill | Project relevance |
|----------|-----------|-------------------|
| CF01 | Workload accounting, profiling (ResNet-18, cProfile) | Confirms distance kernel is 46% of runtime |
| CF02 | Roofline analysis, quantization profiling | Justifies PIM architecture; memory-bound diagnosis |
| CF03 | CUDA GEMM (naive + tiled), DRAM traffic analysis | GEMM tiling patterns apply to distance kernel optimization |
| CF04 | Fixed-point quantization, MAC HDL design with cocotb | MAC unit is the building block of the distance engine |

When working on a project milestone, check the corresponding codefest for analysis that supports the design decision.

---

## Repository Layout

```
codefest/
  cf01–cf04/          Per-codefest: cman_*.md, CLLM session logs, profiling data, HDL/CUDA code
  presentation.md     Final project presentation outline

project/
  heilmeier.md        Project proposal (Heilmeier questions — read this for full context)
  m1/                 SW baseline, interface selection
  m2/rtl/             distance_engine.sv, axil_slave.sv
  m2/tb/              Testbenches for M2 RTL
  m2/sim/             run_iverilog.sh
  hdl/                kmeans_dist_core.sv (synthesizable), cocotb test_kmeans.py

course-materials/
  week01–week05/      slides/ and docs/ per week + weekXX_notes.md
  study/              Quiz 1 cheatsheet, study guide, practice questions
```

---

## Tool Versions
- Python 3.12.3, NumPy 2.4.4
- cocotb 2.0.1 with Icarus Verilog (icarus sim backend)
- iverilog ≥ 11 required for SystemVerilog 2012 (`-g2012`)
