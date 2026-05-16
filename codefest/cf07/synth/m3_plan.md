# CF07 — M3 Plan

**Bao Nguyen — ECE 410/510 Spring 2026**

CF07 result at 10 ns target: **WNS = −31.53 ns** → critical path 41.53 ns → ~24 MHz no-pipeline ceiling. 17,029 cells, 0.155 mm², 0.32% sequential. 22 endpoints fail on the same combinational dist + 4-level argmin chain.

**For M3:**

1. **Pipeline dist→argmin.** Register the 16 `kdist[k]` outputs before the 4-level argmin tree, plus a second register after level 2 → 3-stage pipeline, expected critical path ≈ 41.5/3 ≈ 14 ns per stage → closes 10 ns. Throughput unchanged at 1 sample/cycle; latency +2 cycles.
2. **Drop `DIST_W` 20 → 18.** `min_dist[18:19]` are unconstrained — max kdist 195,075 < 2¹⁸. ~10% accumulator-area savings.
3. **Keep 10 ns target** — matches M1 PIM chiplet I/O budget (16 TB/s HBM3 via UCIe).

**Dates:** synthesis re-run by **May 20**; M3 due **May 24**.
