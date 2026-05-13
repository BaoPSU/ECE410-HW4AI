# CF07 — M3 Plan

**Bao Nguyen — ECE 410/510 Spring 2026**
*Grounded in numbers from `synth_interpretation.md`.*

Synthesis at 10 ns target: WNS = −31.53 ns, TNS = −662.68 ns, 17,029 cells, 0.155 mm². The fully-combinational 16-way dist+argmin is ~41.5 ns long — 3× over budget.

**For M3 I will:**

1. **Pipeline the critical path**: insert one register between the 48 squared-difference accumulators (`kdist[k]`) and the 16-way argmin tree. Expected new path ≈ 14 ns (halving the current ~42 ns) → closes 10 ns with ~4 ns of slack.
2. **Drop `DIST_W` from 20 → 18 bits**. The synthesis flagged `min_dist[18]` and `min_dist[19]` as unconstrained — math can never assert them (3·255² = 195,075 < 2¹⁸). ~10% accumulator-area savings.
3. **Keep clock target at 10 ns** to match the M1 PIM chiplet I/O budget.

Target date: synthesis re-run by **May 20**, M3 due **May 24**.
