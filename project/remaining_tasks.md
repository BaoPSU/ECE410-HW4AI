# Remaining Tasks (post-M4 priority list)

**Bao Nguyen | ECE 410/510 Spring 2026**

> **Context**: M4 was submitted and tagged `m4-submission` at commit `fe4ba1a` on 2026-05-25, before CF9 was assigned. The list below identifies the three highest-leverage changes that would land in a v2 of the accelerator. Per CF9 task 10 framing ("the three most important remaining changes before M4"), this captures the same priority ranking, retroactively scoped to the next milestone in a hypothetical continuation. Each task is specific: it names the file, the change, and the expected gain.

---

## 1. Convert the 480k-pixel batch projection to a measured benchmark

**File**: `project/m4/tb/tb_top.sv` (extend) + new `project/m4/sim/run_batch.sh`

**Specific change**: extend the existing AXI4-Lite testbench to drive 480,000 back-to-back pixel transactions through the slave with the same 16 centroids loaded once at the start. Replace the current single-pixel test loop with a Python-generated stimulus file containing 480k unique RGB triples derived from `bliss.jpg`. Add an assertion that `done` fires every cycle in steady state once the pipeline has filled (cycle 4 onward). Capture the resulting cycle count and divide by 480,000 to compute the realized cycles-per-pixel.

**Expected gain**: converts the 100 M pixels/sec headline in `cf09/benchmarks/benchmark_results.md` from **PROJECTED** to **MEASURED**, eliminating the dominant uncertainty in the CF9 roofline. If a stall is observed (likely candidates: AXI write-handshake delay between centroid update and pixel start), the measurement also tells me exactly what to fix.

**Effort**: ~3 hours (TB extension + ~5 min iverilog sim wall-clock + log parsing).

---

## 2. Replace the AXI4-Lite single-port pixel feeder with a streaming AXI4-Stream port driven from an HBM3-shaped feeder model

**File**: `project/m4/rtl/interface.sv` (modify the pixel-write decode block at lines 84–112) + new `project/m4/rtl/pixel_feeder.sv`

**Specific change**: introduce a separate AXI4-Stream slave port (`s_axis_pixel_tdata`, `s_axis_pixel_tvalid`, `s_axis_pixel_tready`) wired directly to `compute_core.pixel_flat`, bypassing the AXI4-Lite write-address-decode logic for the per-pixel path. The AXI4-Lite slave stays for CTRL/STATUS/centroid loads (low-frequency control plane), and the new AXI4-Stream feeder handles the high-frequency pixel data plane. Add a behavioral HBM3-shaped feeder model in the testbench that asserts `tvalid` every cycle with a new pixel, modeling the 16 TB/s HBM3 path from the M1 system diagram.

**Expected gain**: removes the AXI4-Lite write-handshake overhead on the per-pixel critical path, which is currently the only reason the cosim cycles-per-pixel is **>1** for the back-to-back case (estimated 2–3 cycles per pixel through AXI write, vs 1 cycle/pixel after this change). Conservative estimate: 2× improvement in measured (not projected) throughput, closing the gap between the 100 M sample/sec ceiling and what the back-to-back cosim from task 1 will actually measure.

**Effort**: ~8 hours (new feeder module + decoupling pixel write from AXI4-Lite decode + testbench updates + re-synthesis through OpenLane).

---

## 3. Accelerate the centroid-update step on the same chiplet to defeat Amdahl's 54% serial floor

**File**: new `project/v2/rtl/centroid_update.sv` + new top-level wrapper that owns both `compute_core.sv` (kdist + argmin) and the new centroid-update accumulator block

**Specific change**: implement the K-Means update phase as a second compute kernel on the accelerator. Per centroid k, accumulate sum-of-pixels and sum-of-counts indexed by the label output of `compute_core`, then divide at the end of the iteration. Three INT24 accumulators per centroid (one per RGB channel) plus one INT20 counter, 16 centroids total = 16 × (3×24 + 20) = 1,472 flops added. The divide can be done in software at the end of each iteration (just 16 divisions) or with a small unrolled iterative divider on-chip. Add it as a second pipeline behind the existing kdist+argmin pipeline so it ingests `(label, pixel)` pairs from the existing core's output port.

**Expected gain**: this is the highest-leverage change of the three. The CF9 benchmark shows end-to-end speedup is **Amdahl-limited at 1.77× because 54% of the work (centroid update + convergence check + Python overhead) still runs on the host CPU**. Accelerating the centroid update absorbs ~40% of that 54% (the math-heavy portion; the rest is I/O and Python that can't move). Projected end-to-end speedup after this change: `1 / ((1 - 0.86) + 0.86/17.66) = 1 / (0.14 + 0.049) = 1 / 0.189 = 5.3×` (vs current 1.77×). This single change is worth more than the other two combined.

**Effort**: ~20 hours (new RTL module + integration into top + testbench + re-synthesis + re-benchmark). Highest effort, also highest payoff.

---

## Priority ranking

| # | Task | Effort | Speedup gain | When to do it |
|---|------|--------|--------------|---------------|
| 1 | Back-to-back 480k cosim | 3 h | 0× (converts projected to measured) | First. Eliminates the biggest uncertainty in the CF9 numbers. |
| 2 | AXI4-Stream pixel feeder | 8 h | ~2× on the kernel, ~1.05× end-to-end | Second. Cleans up the interface bottleneck. |
| 3 | Centroid-update accelerator | 20 h | ~3× end-to-end on top of task 2 | Third. The Amdahl killer. |

If only one slot exists, do **task 3**. End-to-end speedup is what the user sees.
