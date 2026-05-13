# CF07 — M3 Plan (post-synthesis)

**Bao Nguyen — ECE 410/510 Spring 2026**
*Grounded in `synth_interpretation.md` numbers from RUN_2026-05-13_22-00-19.*

---

**Synthesized**: K-Means distance core (Option A). At 10 ns target → WNS = −31.53 ns, TNS = −662.68 ns. 17,029 cells, 155,300 µm², 0.32% sequential. The current design is a fully-combinational 16×3 squared-difference fan-out feeding a 16-way argmin tree — too long for one cycle.

**For M3 I will:**

1. **Pipeline the critical path** by inserting one register stage between the 48 squared-difference accumulators (`kdist[k]`) and the 16-way argmin tree. Expected new critical path ≈ 14 ns (half of the current ~42 ns), closing 10 ns target with ~4 ns slack.
2. **Drop `DIST_W` from 20 → 18 bits**. The synthesis flagged `min_dist[18]` and `min_dist[19]` as unconstrained — they can never assert (3·255² = 195,075 < 2¹⁸). Expected savings: roughly 10% of accumulator area.
3. **Keep clock target at 10 ns** (100 MHz) — matches the PIM chiplet I/O budget and the 16 TB/s HBM3 bandwidth in the M1 design.
4. **Investigate the 27 fanout violations** — likely the input bus broadcast. Insert buffer stage on `centroids_flat` if it's still flagged post-pipeline.

**Target date**: complete by May 20 (M3 due May 24).
