# CF07 — OpenLane 2 Synthesis Interpretation

**Target:** `synth_top.sv` (K-Means distance core, Option A; Verilog-2005 port of `kmeans_dist_core` for stock Yosys)
**PDK:** sky130_fd_sc_hd · **Tool:** OpenLane 2.3.10 (Dockerized) · **Run:** RUN_2026-05-13_22-00-19

## (a) Clock period and slack

Synthesized at **10.0 ns target** (100 MHz). Post-route STA at `nom_tt_025C_1v80` (`metrics.csv`): **WNS = −31.53 ns**, **TNS = −662.68 ns**, **22 setup endpoints violating**; 0 hold/slew/cap violations.

Slack arithmetic: critical-path delay = 10.0 + 31.53 = **41.53 ns**. Max no-pipeline frequency = 1/41.53 ns ≈ **24.1 MHz**, ~4× under target. Average violation TNS/22 ≈ 30 ns/endpoint — one long combinational chain feeding many output flops.

## (b) Critical path

Source: **`centroids_flat` input port**. Path: 48 parallel squared-difference units (K=16 × D=3, each subtractor → 16-bit squarer → 20-bit accumulator) + 16-way argmin comparator tree (log₂16 = 4 levels). Sinks: `min_dist`/`label` output flops (representative `_34026_/D` in `sta/max.rpt`).

Dominant cells along the path (`stat.rpt`): **xnor2_2 (1,882), or2_2 (1,597), and2_2 (1,078), xor2_2 (922)** — XOR/AND/OR fabric of the subtractor + squarer + carry-propagate stages.

## (c) Total cell area and top contributors

**155,300 µm²** (~0.155 mm²) across **17,029 cells**; sequential = 489 µm² (**0.32%**) — design is almost entirely combinational. Top 3 by instance count: **xnor2_2 (1,882)** in 48 subtractor/squarer units; **or2_2 (1,597)** in 20-bit accumulator carry chains; **and2_2 (1,078)** in (a≥b) comparators and partial products.

## (d) Failed constraints and warnings

- **Setup:** 22 endpoints, TNS = −662.68 ns
- **Hold / slew / cap:** 0
- **Max-fanout:** 27 nets — input broadcast (centroid bus → 16 lanes)
- **Unconstrained endpoints:** `min_dist[18:19]`. Max kdist = 3·255² = 195,075 < 2¹⁸ → never assert. **Action for M3: drop `DIST_W` to 18**
- **Flow:** 43/63 stages ran (synthesis through detailed routing); aborted at final KLayout DRC with a tool-side `FileNotFoundError`, after all timing/area metrics were produced.
