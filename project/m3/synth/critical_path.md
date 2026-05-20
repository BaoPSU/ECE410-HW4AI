# Critical Path

**Bao Nguyen | ECE 410/510 Spring 2026**
*Identified from the RTL pipeline structure; post-PnR confirmation deferred to M4.*

---

## The critical path

**Start register:** `axil_slave_int.reg_pixel[d]` (or `reg_centroids[k*D + d]`) — any of the 51 byte registers in the AXI slave's storage block (D=3 pixel bytes + K*D=48 centroid bytes), all written by the same AXI write FSM.

**End register:** `kmeans_dist_core_pipelined.s1_kdist[k]` — any of the 16 distance accumulators after Stage 1.

**Logic stages (Stage 1 combinational cone):**
1. **Routing fan-out from the slave's storage block** into the compute core's `pixel_flat` and `centroids_flat` packed buses (combinational `generate`-loop wires in the slave).
2. **Absolute-difference computation per (k, d):**
   - 3 parallel subtracts per centroid: `pixel[d] - centroid[k][d]` and the reverse
   - 8-bit signed-comparison mux: `(pixel[d] >= centroid[k][d]) ? a-b : b-a`
3. **Squaring:** `abs_diff * abs_diff` → 16-bit product. 8×8 → 16 multiplier expanded via partial products + Wallace tree.
4. **Three-way add:** sum of 3 squared differences per centroid k. Two adders cascaded (16-bit → 18-bit DIST_W).
5. **Stage-1 register write enable:** kdist[k] latched on the next posedge.

**Why it's the longest:**
- Stage 2 is only an 8-comparator wide × 2-deep argmin tournament — short.
- Stage 3 is only a 4-input argmin (2 deep) — shorter.
- Stage 1 carries the full per-centroid arithmetic (subtract → square → 3-input add), and there are **16 of these in parallel** so the fan-out load on the slave's storage block is high. The longest cone is the AND tree feeding the carry propagate of the 3-input adder.

**Comparison to CF07 (unpipelined):**

| | CF07 (unpipelined) | M3 Stage 1 (pipelined) |
|---|---|---|
| Combinational depth | abs_diff → sq → 3-input add → 4-level argmin tree | abs_diff → sq → 3-input add (only) |
| Logic stages | ~12-14 | ~6-7 |
| Measured WNS (CF07 STA) | −31.53 ns at 10 ns target | (not measured — PnR blocked) |
| Estimated post-PnR delay | 41.53 ns | ~13.8 ns (CF07 path ÷ 3) → ≤ 10 ns after PnR balancing |

## What would shorten this path further (M4+ work)

1. **Pipeline the multiplier itself.** Currently the 8×8 → 16 multiplier sits in the same Stage 1 cone as the 3-input add. Putting a register between the squaring and the accumulate would split Stage 1 into 1a (subtract + square) and 1b (accumulate), at the cost of one more cycle of latency. Throughput stays at 1 sample/cycle, and the per-stage logic depth drops to ~3-4 stages.
2. **Carry-save adders for the 3-input add.** Replace the cascaded 2-input adders with a 3:2 carry-save compressor followed by a final 2-input add. Saves ~1 ripple-carry chain length on the longest path.
3. **Brent-Kung / Kogge-Stone for the final add.** The 18-bit add tree at the end of Stage 1 is currently using whatever ripple-carry adder yosys infers. A prefix-tree adder is logarithmic-depth instead of linear and would shave another 2-3 ns at the 18-bit width.

None of these are needed for M3 timing closure if the 3-stage partition already hits ≤ 10 ns per stage. They are M4 levers if Fmax has to push past 100 MHz, which the M1 PIM chiplet I/O budget does not require (the 16 TB/s HBM3 link sits at the 100 MHz interface clock already).
