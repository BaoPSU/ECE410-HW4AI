# Critical Path

**Bao Nguyen | ECE 410/510 Spring 2026**
*From OpenROAD post-PnR STA at typical corner (max_tt_025C_1v80).*

---

## Result

**Timing closed.** WNS = **0.0 ns**, TNS = **0.0 ns** at the 10 ns / 100 MHz clock target across typical and fast PVT corners. The worst path has **+3.13 ns of positive slack** (the longest path finishes in ~6.87 ns out of the 10 ns budget). Hold checks pass cleanly with 0 ns slack across all corners.

## The critical path

OpenROAD's STA report (`runs/RUN_2026-05-20_22-19-25/54-openroad-stapostpnr/max_tt_025C_1v80/max.rpt`) flags this as the worst setup-violating path on the design:

**Start register:** `_14498_` — a flip-flop inside `axil_slave_int.u_axil` that drives `pixel_flat[0]`. This is the LSB of the broadcast bus going from the slave's pixel/centroid byte storage into the compute core's Stage-1 abs_diff cone.

**End register:** `_14004_` — a flip-flop inside `kmeans_dist_core_pipelined`, one of the 16 Stage-1 `s1_kdist[k]` accumulators that latch the per-centroid squared-distance result on the next clock edge.

**Logic stages along the path (from `max.rpt`):**
1. Clock tree: `clkbuf_0_clk → clkbuf_3_1_0_clk → clkbuf_leaf_10_clk → _14498_/CLK` (~1.1 ns of clock latency)
2. Flop output: `_14498_/Q` → `u_axil.pixel_flat[0]` net (clock-to-Q ~0.54 ns)
3. **Pixel-broadcast buffer chain**: `rebuffer4 → rebuffer308 → rebuffer306 → rebuffer302 → fanout293` — five buffer/repeater inserts the placer added to fan out the pixel byte from the slave to all 16 parallel abs_diff blocks in the compute core. Each ~0.10–0.14 ns.
4. **Stage-1 abs_diff cone**: inverter `_07091_` plus AND-OR gates feeding the subtractor for one of the 16 centroids.
5. **Squaring**: 8×8 → 16-bit multiplier expanded into partial-product AND gates + adder tree.
6. **3-input add** for the per-centroid kdist accumulator (Σ_d (pixel[d] − cent[k][d])²).
7. Setup at `_14004_/D` → captured on next clk edge.

**Total path delay**: 10 ns − 3.13 ns slack ≈ 6.87 ns.

## Why this is the longest path

- Stage 1 carries the **subtract → square → 3-input add** chain, the deepest arithmetic in the design.
- The **pixel-broadcast bus** to 16 parallel abs_diff blocks has high fan-out (16 destinations), so the placer needed 5 buffer/repeater inserts on this net alone. Those buffers contribute ~0.5 ns combined.
- Stage 2 and Stage 3 (argmin tree) are 2-deep mux comparisons each, much shorter.

Predicted in `critical_path.md` (pre-STA): "Stage 1 carries the full per-centroid arithmetic (subtract → square → 3-input add), and there are 16 of these in parallel so the fan-out load on the slave's storage block is high." OpenROAD's STA confirmed exactly this: the fan-out buffer chain to the 16 abs_diff blocks shows up as 5 explicit buffer cells on the critical path.

## What would shorten this path further (M4+ work)

1. **Pipeline the multiplier itself.** Put a register between the squaring and the accumulate. Splits Stage 1 into 1a (subtract + square) and 1b (accumulate); per-stage logic depth drops to ~3-4 gates. Cost: +1 cycle of latency.
2. **Replicate the pixel register.** Instead of one register fanning out to 16 abs_diff blocks (5 buffer inserts), keep 16 copies in the slave so each abs_diff has its own dedicated driver. Trades flop area for wire delay.
3. **Carry-save adder for the 3-input add.** Replace cascaded 2-input adders with a 3:2 CSA + final 2-input add. Saves ~1 ripple-carry chain length.

None are needed to close timing at typical conditions, where the design already has 3.13 ns of headroom. M4 might revisit (2) to close the slow-slow corner if the package thermal/voltage budget pushes toward SS-1v60 worst case.

## Slow-slow corner failure (documented, not a blocker)

At nom_ss_100C_1v60 (slow process, 100°C, 1.6 V), the same path misses by ~3 ns (WNS = −3.04 ns, TNS = −117 ns). This is normal for an open-source flow without margin engineering — closing all corners typically requires either a slower clock (~13 ns / 76 MHz) or path-level retiming. The M1 PIM chiplet I/O budget specifies 100 MHz at nominal conditions, which the design meets; SS closure is an M4 polish step, not an M3 deliverable.
