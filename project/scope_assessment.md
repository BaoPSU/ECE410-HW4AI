# Project Scope Assessment

**Bao Nguyen — ECE 410/510 Spring 2026**
*Updated after CF07 synthesis attempt.*

---

## Project at a glance
K-Means image color quantization accelerator. Near-memory PIM compute core with AXI4-Lite control, targeting a 16 TB/s HBM3 chiplet over UCIe. M1 SW baseline ~9 s/image on i9-12900H, AI = 1.68 FLOP/byte (memory-bound on CPU); M2 behavioral RTL done; **M3 = first synthesizable + timing-closed integer core**.

## CF07 synthesis result (RUN_2026-05-13_22-00-19)

| Metric | Value | What it says |
|---|---|---|
| Clock target | 10.0 ns (100 MHz) | matches PIM I/O budget |
| WNS / TNS | **−31.53 ns / −662.68 ns** | design fails by ~3× |
| Critical path | 41.53 ns → 24 MHz max | no-pipeline ceiling |
| Cell area (Yosys) | 155,300 µm² (~0.155 mm²) | small, fits easily |
| Cells | 17,029 | 0.32% sequential — almost fully combinational |
| Setup-violating endpoints | 22 | all on the same combinational chain |
| Max-fanout violations | 27 | input broadcast bus |
| Unconstrained endpoints | 2 (`min_dist[18:19]`) | dead MSBs — narrowable |

## Scope decision

**My pre-synthesis hypothesis was wrong.** I expected the K=16, D=3, 20-bit core to close 10 ns timing as a single-cycle combinational block. It misses by 31.5 ns — the 4-level argmin tree stacked on top of the 48 parallel squared-difference paths is one long combinational chain.

**Scope adjustment for M3** (per `codefest/cf07/synth/m3_plan.md`):
- **Pipeline** the dist → argmin boundary (3-stage; +2 cycles latency, throughput unchanged at 1 sample/cycle)
- **Drop `DIST_W` 20 → 18** (synthesis confirmed MSBs never assert)
- **Keep 10 ns clock target** (locked to M1 chiplet I/O budget)

**Scope unchanged from M2:** integer distance + argmin, AXI4-Lite, PIM target. No change to algorithm, K, D, or precision strategy.

## Confidence

High that the M3 changes will close timing:
- Expected new critical path: 41.5 / 3 ≈ 14 ns per stage with conservative balancing → drop to ≤10 ns after register placement optimization
- Area cost of pipeline: negligible (0.32% → maybe 1% sequential after two new stages)
- `DIST_W` reduction is free — math proves the trim is lossless

## M3 deliverable plan

Re-synthesize the pipelined design by **May 20** to leave 4 days of buffer before M3's **May 24** deadline. Integrate `axil_slave.sv` on top, confirm timing at 100 MHz with positive slack.
