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

## Synthesis result (placeholder — to be filled in after running OpenLane)

- Target clock period: `<FILL IN ns>`
- Achieved WNS: `<FILL IN ns>`
- Total cell area: `<FILL IN µm²>`
- Instance count: `<FILL IN>`

## Scope decision

> *Confirm or adjust here once the synthesis numbers are in.*

**Working hypothesis** (pending real numbers): the design is small enough (K=16, D=3, 20-bit accumulators) that OpenLane should close timing comfortably at a ~10 ns clock period without pipelining. If WNS comes back negative, the argmin tree across 16 centroids is the likely culprit, and pipelining one register stage between distance compute and argmin reduce should fix it.

**Scope remains unchanged from M2**: integer distance + argmin core, AXI4-Lite control, target a PIM chiplet with 16 TB/s HBM3 bandwidth via UCIe. No new features added; CF07 is purely about confronting the actual synthesis numbers.

## M3 plan (one line)

Run the same OpenLane flow at the project level, integrate `axil_slave.sv` on top, target the chiplet I/O constraints. Report results in M3 due May 24.
