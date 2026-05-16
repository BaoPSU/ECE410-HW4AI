# CF07 — OpenLane 2 Synthesis Interpretation

**Target:** `synth_top.sv` (K-Means distance core, Option A)
**PDK:** sky130_fd_sc_hd · **Tool:** OpenLane 2.3.10 (Dockerized)
**Bao Nguyen — ECE 410/510 Spring 2026**

## (a) Clock period and slack
Target clock period **10.0 ns** (100 MHz). Post-route STA reports **WNS = −31.53 ns** and **TNS = −662.68 ns** across **22 violating endpoints**.

Negative slack means the critical path is longer than the target period by |WNS|, so actual path delay = 10.0 ns + 31.53 ns = **41.53 ns**. For timing closure without pipelining, the clock period must be at least 41.53 ns, i.e., max frequency ≈ 1 / 41.53 ns ≈ **24 MHz**.

## (b) Critical path
The dominant path runs from `centroids_flat` input → 48 parallel squared-difference units (K=16 × D=3 absolute-difference + squarer + 18-bit accumulator) → 16-way argmin comparator tree → `min_dist` / `label` output registers. Dominant cell types along the path: `xnor2_2` (1,882 instances), `or2_2` (1,597), `and2_2` (1,078), `xor2_2` (922). The argmin reduce is 4 levels deep — too long to fit in one cycle alongside the distance computation.

## (c) Total cell area and top contributors
**155,300 µm²** (~0.155 mm²) across **17,029 cells**. Only **0.32%** is sequential (489 µm² of flops) — almost the entire design is combinational logic. The three largest cell counts (xnor2/or2/and2) all build the same compute structure: subtractors, squarers, and the carry-propagate chain of the 20-bit accumulator.

## (d) Failed constraints and warnings
- Setup violations: **22 endpoints**, TNS = −662.68 ns
- Hold violations: **0**, slew/cap violations: **0**
- Max fanout violations: **27** on input broadcast nets (centroid bus driving 16 lanes in parallel)
- **2 unconstrained endpoints**: `min_dist[18:19]` — the two MSBs that can never assert because max kdist = 3·255² = 195,075 < 2¹⁸. Trim `DIST_W` to 18 for M3.
- Flow ran 43/63 stages, aborted at the final KLayout DRC step with a tool-side `FileNotFoundError` after synthesis/PnR/STA all completed.
