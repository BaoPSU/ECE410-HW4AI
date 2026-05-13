# Project Scope Assessment

**Bao Nguyen — ECE 410/510 Spring 2026**
*Updated for CF07 (pre-M3 synthesis check).*

---

## What I'm building

K-Means image color quantization accelerator with a near-memory PIM compute core. The synthesizable HDL is `project/hdl/kmeans_dist_core.sv` — a 1-cycle latency integer distance + argmin core for K=16, D=3, 8-bit RGB.

## Where I am right now

| Milestone | Status | Notes |
|-----------|--------|-------|
| M1 | Done | SW baseline (~9 s/image on i9-12900H), AI = 1.68 FLOP/byte (memory-bound on CPU) |
| M2 | Done | Behavioral `distance_engine.sv` (float32, simulation-only), `axil_slave.sv` AXI4-Lite wrapper |
| **M3 (CF07 prep)** | **In progress** | Synthesizable `kmeans_dist_core.sv` exists and passes cocotb tests; CF07 attempts first OpenLane synthesis |
| M3 (full) | Not started | Due May 24 — synthesis + reports + interpretation |

## CF07 synthesis target

I chose **Option A** (own project core). `codefest/cf07/hdl/synth_top.sv` is a copy of `project/hdl/kmeans_dist_core.sv` for OpenLane to operate on.

## Synthesis result (from RUN_2026-05-13_22-00-19)

- Target clock period: **10.0 ns** (100 MHz)
- Achieved WNS: **−31.53 ns** → critical path ~41.5 ns (would close at ~24 MHz)
- TNS: **−662.68 ns** across ~21 violating endpoints
- Total cell area (Yosys): **155,300 µm²** (~0.155 mm²)
- Instance count: **17,029 cells** (only 0.32% sequential — design is almost fully combinational)
- Top cell types: xnor2 (1,882), or2 (1,597), and2 (1,078), xor2 (922) — adder-tree dominated
- 27 fanout violations on input broadcast nets
- 2 unconstrained endpoints (`min_dist[18..19]`) — MSBs that math can never assert

## Scope decision

**My hypothesis was wrong.** I expected the design to close 10 ns timing without pipelining. The fully-unrolled 16-centroid argmin reduce + 48 parallel squared-difference paths blow past the budget by 3×.

**Scope adjustment for M3**:
- Add **one pipeline register** between `kdist[k]` accumulators and the argmin tree → cuts critical path roughly in half
- **Drop `DIST_W` from 20 → 18 bits** (synthesis flagged the unused MSBs)
- **Throughput unchanged** — still 1 sample per cycle in steady state, with a 1-cycle additional latency penalty
- **Clock target stays at 10 ns** (matches PIM chiplet I/O budget from M1)

**Scope unchanged from M2**: integer distance + argmin core, AXI4-Lite control, near-memory PIM target with 16 TB/s HBM3 bandwidth via UCIe.

## M3 plan (one line)

Pipeline + accumulator-width fix, re-synthesize, integrate `axil_slave.sv` on top, confirm timing closes at 100 MHz with positive slack. Due May 24.
