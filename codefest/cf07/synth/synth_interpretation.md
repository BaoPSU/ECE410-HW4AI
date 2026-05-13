# CF07 — OpenLane 2 Synthesis Interpretation

**Target:** `synth_top.v` (K-Means distance core, Option A — converted from `kmeans_dist_core.sv` to Verilog-2005 for Yosys default frontend)
**PDK:** sky130_fd_sc_hd
**Tool:** OpenLane 2.3.10, run via Docker
**Run ID:** RUN_2026-05-13_22-00-19
**Bao Nguyen — ECE 410/510 Spring 2026**

---

## (a) Clock period and worst-case slack

I ran synthesis at a target clock period of **10.0 ns** (100 MHz). The post-route STA reports a worst-case setup slack (WNS) of **−31.53 ns** with total negative slack TNS = **−662.68 ns** across many violating endpoints — the design **fails timing badly** at this target.

Critical path delay ≈ 10.0 + 31.5 = **~41.5 ns**, so the design will only close timing at a clock period of ~42 ns (≈ 24 MHz) without pipelining. One sample path that does meet (slack +7.33 ns) is a short input-to-DFF route, but the longest combinational path through the 16-centroid argmin tree is the limiting factor.

## (b) Critical path

The dominant timing path runs from the **input port `centroids_flat`** through the **48 squared-difference compute paths** (K=16 × D=3 absolute-difference + squarer + 18-bit accumulator) and into the **K=16-way argmin comparator tree** ending at the `min_dist` / `label` output registers. Dominant cell types along the path: `xnor2_2` (1,882 instances), `or2_2` (1,597), `and2_2` (1,078), `xor2_2` (922), and `a21oi_2` (766) — the multiplier and adder-tree cells that build up each (pixel−centroid)² term and the 16-way reduction. There are 2 unconstrained endpoints (`min_dist[18]` and `min_dist[19]`), the two upper accumulator bits that the math can never assert (max distance = 3·255² = 195,075 < 2¹⁸).

## (c) Total cell area and top three contributors

Total chip area (Yosys gate-area estimate): **155,300 µm²** (~0.155 mm²) across **17,029 cells**. Only 489 µm² (**0.32%**) is sequential — almost everything is combinational logic for the parallel dist+argmin tree.

| Rank | Cell type | Instance count | What it builds |
|------|-----------|----------------|----------------|
| 1 | `xnor2_2` | 1,882 | XOR/XNOR carry-save adders inside the 48 squared-difference units and the 16-way subtractor in argmin |
| 2 | `or2_2` | 1,597 | OR-tree carry propagation across the 20-bit accumulator |
| 3 | `and2_2` | 1,078 | AND-gate reductions inside the (a≥b) comparators and partial-product squarers |

This matches expectations — for K=16, D=3 with 8-bit inputs, the synthesis builds 48 parallel subtractor + squarer paths feeding into 16 20-bit accumulators that then reduce through a 4-level argmin tree.

## (d) Failed constraints and warnings

- **Setup violations**: many — TNS = −662.68 ns indicates ~21 endpoints failed on average by ~31 ns each.
- **Hold violations**: none flagged in post-PnR.
- **Max fanout violations**: **27** on internal nets — typically the broadcast of the input bus to 16 parallel compute lanes.
- **Unconstrained endpoints**: 2 (`min_dist[18]`, `min_dist[19]`) — the two MSBs of the distance output that never assert because 3·255² < 2¹⁸. Trim the accumulator to `DIST_W=18` for M3.
- **Slew/cap violations**: 0 / 0.

The flow ran through synthesis → floorplan → placement → CTS → routing successfully (43 stages out of ~63), then aborted at the very last KLayout DRC stage with a `FileNotFoundError` (PDK/tool-side, not RTL).

---

*Bottom line: synthesis succeeded, but the fully-unrolled 16-way parallel distance+argmin needs either a pipeline stage between distance compute and argmin reduce, or a slower clock target around 24 MHz. M3 plan covers the pipelining option, which keeps single-cycle throughput while cutting critical path ~3×.*
