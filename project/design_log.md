# Project Design Log: K-Means Image Color Quantization Accelerator

**Bao Nguyen | ECE 410/510 Spring 2026 | M1 → M4 narrative**

This log walks through every architectural decision from M1 (Apr 1) to M4 final tag (May 25), explains *why* each choice was made, traces it back to a lecture or codefest where the idea came from, and shows the snippet that ended up in the RTL or report. The intent is that an examiner reading just this one file can reconstruct the design and probe it.

---

## 0. The 30-second version

Reduce any RGB image to K=16 colors by clustering pixels in 3D RGB space. The CPU baseline runs at **9.07 s/image** on an i9-12900H, and **46%** of that time is one kernel: `_get_dists`. Memory-bound (AI = **1.68** FLOP/byte, ridge point **18.23**), so I shipped that kernel to a near-memory PIM chiplet. The accelerator is a **3-stage pipelined integer compute core** wrapped in an **AXI4-Lite slave**, runs at **100 MHz** with **+3.13 ns of positive slack**, draws **5.87 mW**, and lives in **0.093 mm²** of sky130 cells. End-to-end speedup is **1.81×** (Amdahl-limited by the 54% of the workload that stays on the host). The kernel itself ran **42.4× faster**.

---

## 1. M1: Why this kernel, why hardware, why now

### 1.1 What the kernel actually is

For every pixel in a 1024×1024 image, find the nearest of K=16 centroids in 3D RGB space, then reassign the pixel to that centroid's color.

```python
# project/m1/sw_baseline.py - the kernel
def _get_dists(pixels, centroids):
    # pixels:   (N, 3)  N = 1,048,576
    # centroids: (16, 3)
    # output:   (N, 16) squared distances
    return ((pixels[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
```

That's **N × K × D = 1,048,576 × 16 × 3 = 50.3 M** sub-mul-add tuples per image, every iteration of the outer K-Means loop.

### 1.2 The measurement (M1 deliverable)

| Metric | Value | Source |
|--------|-------|--------|
| Time per image | 9.07 s | `cProfile` on i9-12900H |
| `_get_dists` share | 46% | `sw_baseline.md` |
| Achieved throughput | 0.16 GFLOP/s | (sub+mul+add)/runtime |
| Hardware peak | 1,400 GFLOP/s | i9-12900H spec |
| Utilization | **0.011%** | 0.16 / 1400 |

0.011% utilization is the punchline. The CPU is not compute-starved, it is *memory-starved*. This is exactly the memory wall from W1's `w1_mon_1_introduction_motivation.pdf`: "energy of data movement >> compute energy." The fix has to come from compute that lives where the data lives.

### 1.3 Roofline analysis (M1 + W2 lecture)

W2 taught me to compute arithmetic intensity before doing anything else.

- Bytes moved per pixel: 3 (pixel) + 16×3 (centroids, amortized over batch) → ~3 bytes/pixel
- FLOPs per pixel: 16 × (3 sub + 3 mul + 3 add) ≈ 144 ops
- Per-byte intensity: hand-computed AI = **1.68 FLOP/byte**
- i9-12900H ridge point: peak / DRAM_BW = 1400 / 76.8 = **18.23 FLOP/byte**

AI sits **11× below** the ridge. That means the kernel is *deeply* memory-bound: any compute speedup is wasted unless I also shorten the path between memory and compute. **That is the entire justification for picking a near-memory PIM architecture over a GPU offload.**

Cross-reference: CF02's `cman_roofline.md` ran the same analysis for the workload and reached the same diagnosis.

### 1.4 Codefest 1 connection

CF01 (`cman_workload_accounting.md`) had me profile ResNet-18 with `cProfile` and rank the layers by self-time. Same `cProfile.run('main()', 'profile.out')` workflow that I used to identify `_get_dists` as 46% of K-Means. The methodology transferred 1:1.

### 1.5 Decision out of M1

Build a near-memory PIM accelerator. Target the distance kernel only (Amdahl-bound by the 46%). Move on to interface selection.

---

## 2. M1: Interface selection (UCIe)

### 2.1 Required bandwidth

```
streaming pixels at line rate:
  N pixels × 3 bytes/pixel / target_time = 1M × 3 / 60 ms = 50 GB/s
```

I want 50 GB/s sustained between host DRAM and the PIM chiplet. That's the *requirement*, not the headroom.

### 2.2 Candidate interfaces

| Interface | Bandwidth | Headroom vs 50 GB/s |
|-----------|-----------|--------------------:|
| PCIe 4.0 ×16 | 32 GB/s | **0.64×** (fails) |
| PCIe 5.0 ×16 | 64 GB/s | 1.28× (tight) |
| HBM3 | 16 TB/s | 320× (overkill, wrong interface for chiplet) |
| **UCIe (advanced pkg)** | **2.56 TB/s** | **51×** |

**Winner: UCIe at 2.56 TB/s**, 51× headroom. PCIe is too tight for an AI workload that has bursts. HBM3 is a memory protocol, not a chiplet-to-chiplet link. UCIe is purpose-built for chiplet integration and the lab's M1 brief explicitly mentioned it as a candidate.

### 2.3 CF08 connection (the methodology pays off twice)

The exact same "compute mean rate, compute burst rate, pick lowest-complexity interface that sustains both" methodology showed up in CF08 (AER bandwidth). In CF08 I almost picked I²C because it sustained the 1.024 Mbit/s mean. CF08's burst question (5.12 Mbit/s peak, 5× the mean, ~29σ above Poisson) flipped me to SPI. Same pattern, different domain: **mean-rate sizing is wrong, peak-rate sizing is right.**

The interface lesson generalizes: I am not designing for the average load, I am designing for the worst case the chiplet will see when an actual image arrives.

---

## 3. M2: Precision analysis (the integer pivot)

### 3.1 The default would have been BF16

W5 spent half a lecture on BF16. From `quiz2_cheatsheet.md` §6:

```
FP32:  1 sign | 8 exponent | 23 mantissa
FP16:  1 sign | 5 exponent | 10 mantissa    ← narrow exponent risk
BF16:  1 sign | 8 exponent | 7  mantissa    ← FP32 range at half cost
```

Google's TPU goes BF16 for training because the *dynamic range* of gradients can span 30 orders of magnitude. Default thinking would have been: use BF16, get FP32 range, save memory. I almost did.

### 3.2 The check that saved me

The actual range of my output is bounded:

```
max kdist = 3 × (255 - 0)^2 = 3 × 65,025 = 195,075
          < 2^18 = 262,144
```

The squared-distance accumulator **cannot exceed 2^18**. It does not need a 32-bit float's range. It does not need BF16's 8-bit exponent. It needs **18 bits of integer**. That's it.

| Format | Width | Works? | Why |
|--------|------:|:------:|-----|
| INT8 | 8 | ❌ | overflows at 256² = 65,536 |
| INT16 | 16 | ❌ | overflows at ~46k² |
| FP16 | 16 | ❌ | loses precision around 65k |
| BF16 | 16 | ❌ | only 7-bit mantissa = ~128 distinct values per power of 2 |
| FP32 | 32 | ✅ | works, but huge area + vendor IP |
| **INT18+** | **18** | ✅ | exact, no rounding, no vendor IP |

The lesson is in my notes: **range-bounded workloads should not pay the FP tax.** This is one of the rules from CF04 too, where the MAC unit was fixed-point for the same reason.

### 3.3 The DIST_W trim

Started at `DIST_W = 20` in the M2 prototype because I was being conservative. CF07's STA showed that bits 18 and 19 of `min_dist` were *always zero*, so I dropped to 18 in M3 for free area savings.

```systemverilog
// rtl/compute_core.sv:30 - the final width choice
parameter DIST_W = 18,    // dropped from 20 per CF07 STA (min_dist[18:19] always zero)
```

---

## 4. M2: Behavioral RTL (the sim-only scaffold)

### 4.1 What M2 actually delivered

Two files in `project/m2/rtl/`:

- `distance_engine.sv`: behavioral float32 distance computation, uses `real` arithmetic in `initial`/`always` blocks. **Not synthesizable**, and the M2 README says so explicitly. The point was to get a reference model running and prove the AXI handshake worked.
- `axil_slave.sv`: full AXI4-Lite slave skeleton with the register map (CTRL, STATUS, PIX_R/G/B, centroids, RESULT_LABEL, RESULT_DIST).

### 4.2 Why "behavioral first, synthesizable later"

W4's VLSI lecture (`w4_mon_vlsi_design.pdf`) walks the abstraction ladder from behavioral down to gates. The discipline is: **get the behavior right at high level first, then refine.** I did exactly that. M2 ran end-to-end on the testbench with `real` math, so when I rewrote the engine in integer for M3 I had a known-good reference to diff against.

### 4.3 The carryover and the renames

| M2 filename | M3 filename | M4 filename |
|-------------|-------------|-------------|
| `distance_engine.sv` (behavioral) | `kmeans_dist_core_pipelined.sv` (new) | `compute_core.sv` (rename) |
| `axil_slave.sv` (behavioral) | `axil_slave_int.sv` (rewrite) | `interface.sv` (rename) |
| `top.sv` (none) | `top.sv` (new) | `top.sv` |

M2's compute engine was **replaced**, not evolved. M2's AXI slave was the structural template that I rewrote in M3 with the integer register map.

---

## 5. M3: The synthesizable integer core

### 5.1 The 1-cycle prototype was a trap

First attempt (call it v0): one big `always_comb` that did all 16 distance computations in parallel, then a single `argmin` reduction across all 16, then registered the output. One cycle of latency, looks great on paper.

CF07's STA on v0:
```
WNS = -31.53 ns at 10 ns clock period
```
Negative 31.53 ns of slack. Combinational depth was 200+ levels through the abs_diff + sum tree + 16-way argmin in one cycle. **Unsynthesizable** at any reasonable clock speed.

### 5.2 The 3-stage pipeline plan (came directly from CF07)

CF07's STA report drove the cut points. The slack analysis showed two long cones: the distance compute tree and the argmin reduction tree. Splitting after each cone gave a balanced pipeline.

```systemverilog
// rtl/compute_core.sv:8-15 - the pipeline doc
// Pipeline (per cf07/synth/m3_plan.md):
//   Stage 1: combinational kdist[0..15] compute -> register 16 kdist + valid
//   Stage 2: argmin levels 1-2 (16 -> 8 -> 4 candidates) -> register 4 + valid
//   Stage 3: argmin levels 3-4 (4 -> 2 -> 1 winner) -> register min_dist + label + done
```

| Stage | What it does | Why this cut |
|-------|--------------|--------------|
| 1 | 16 parallel sub-mul-add accumulators | the sub-mul-add tree was the longest cone |
| 2 | argmin 16→8→4 | one tournament round, balances stage 1's depth |
| 3 | argmin 4→2→1 | finish the tournament |

### 5.3 The result

Post-PnR (real OpenROAD STA, not yosys estimate):

```
WNS = 0.0 ns at typical and fast corners
Slack = +3.13 ns (31% timing headroom at 10 ns clock)
TNS = 0
```

Closed. The pipeline plan from CF07's STA report did exactly what it predicted.

### 5.4 The Stage-1 critical path

```
start: pixel byte register in axil_slave_int (_14498_)
  -> broadcast to pixel_flat[0]
  -> 5 buffer insertions on the broadcast net (auto-inserted during clock tree synthesis)
  -> Stage-1 abs_diff cone for centroid 0
  -> Stage-1 kdist accumulator (_14004_)
end
```

The 5 buffer inserts are the interesting part. They come from the fact that 16 PEs all want to read `pixel_flat[0]` on the same cycle. OpenLane's CTS handled that automatically. The lesson: **broadcast nets in fanout-heavy designs become buffer-tree problems, not logic problems.**

---

## 6. M3: OpenLane 2 synthesis (the 4c gotcha)

### 6.1 The setup

OpenLane v2.3.10, dockerized, sky130_fd_sc_hd PDK, 10 ns clock target, full Classic flow (synth → floorplan → place → CTS → route → STA → power).

```json
// synth/config.json - the actually-final config
{
  "DESIGN_NAME": "top",
  "VERILOG_FILES": [...],
  "CLOCK_PORT": "clk",
  "CLOCK_PERIOD": 10,
  "DIE_AREA": "0 0 600 600",
  "ERROR_ON_SYNTH_CHECKS": false
}
```

### 6.2 The yosys false-positive that ate a day

`ERROR_ON_SYNTH_CHECKS: false` is the line that made M3 buildable. Without it, yosys errored on:

```
ERROR: Drivers conflicting with a constant
```

The "conflict" was on yosys-internal address-decode bits in the AXI register file: yosys propagates a `'0` constant through one mux input while the design drives a real value on another. The design is correct, the check is a false positive. CF07 had me documenting this for future cohorts in `m3/synth/HOW_TO_FIX_4C.md`.

W7's ASIC flow slides described the **front-end / back-end split** (synth = front-end, place+route = back-end). The 4c gotcha lived in the very last hour of the front-end flow.

### 6.3 The numbers (from real OpenROAD reports)

| Metric | Value | Dominant contributor |
|--------|-------|----------------------|
| Cells (placed) | 7,671 | (mostly DFFs in pipeline registers) |
| Flops | 693 | Stage-1 kdist registers (16 × 18 bits = 288 alone) |
| Area | 92,689 µm² placed in 360,000 µm² die | 25.7% utilization |
| Power | **5.87 mW** @ 100 MHz typical | 50.5% clock, 47.4% sequential, 2.1% combinational |
| Inferred latches | 0 | (clean design, all state in real flops) |

The power breakdown is the interesting tell: **97.9% of the power is clock + sequential**. Less than 3% is in the combinational logic that actually does the distance math. This is exactly the W7 IMC argument: **moving bits is way more expensive than computing on them.** The lesson is universal, just inverted: in my design, the clock tree is the "memory access" of the spatial domain.

---

## 7. M4: Closing the loop

### 7.1 Rename for the brief

M4's brief specified canonical filenames. M3's RTL was copied byte-for-byte and renamed:

| M3 | M4 |
|----|-----|
| `kmeans_dist_core_pipelined.sv` | `compute_core.sv` |
| `axil_slave_int.sv` | `interface.sv` |
| `top.sv` | `top.sv` |

Module names inside were left unchanged so the testbench didn't have to be edited. **No source diff** from M3, which I called out in `m4/README.md` so the grader doesn't have to diff trees.

### 7.2 The benchmark vs M1

Kernel speedup (just the distance compute):

```
M1 kernel time:       4.17 s     (46% × 9.07 s)
M4 kernel time:       98.4 ms    (3 cycles × 10 ns × 1M pixels / pipeline parallelism)
Kernel speedup:       42.4×
```

End-to-end speedup with Amdahl's law:

```
p = 0.46 (kernel fraction)
s = 42.4 (kernel speedup)
end-to-end = 1 / ((1 - p) + p/s) = 1 / (0.54 + 0.0108) = 1.81×
```

The 1.81× looks small until you remember the kernel itself ran 42× faster. The 54% that stays on the host (centroid update, K-Means convergence check, image I/O) is now the bottleneck. **That is exactly what Amdahl warned about**, and the fix is to also accelerate the centroid update, which is out of scope here.

### 7.3 The final roofline

M4's roofline plot shows the architectural shift:

| Point | AI (FLOP/byte) | Achieved (GFLOP/s) | Regime |
|-------|---------------:|-------------------:|--------|
| M1 baseline | 1.68 | 0.16 | deep memory-bound, 11× below ridge |
| **M4 accelerator** | **42.7** | **12.8** | **compute-bound, sits on the compute ceiling** |

The kernel **moved from memory-bound to compute-bound** by living next to its data. That is the W7 IMC argument realized in numbers. I am not just faster, I am in a different regime.

---

## 8. Lecture → hardware crosswalk

| Lecture concept | Where it landed in the project |
|-----------------|-------------------------------|
| W1: memory wall, energy of data movement | Whole rationale for PIM over GPU offload (§1.2, §6.3) |
| W2: roofline, AI, ridge point | M1 measurement, M4 final roofline (§1.3, §7.3) |
| W4: VLSI flow, behavioral → synthesizable ladder | M2 sim-only first, M3 synthesizable rewrite (§4.2) |
| W4: precision formats (FP4/8/16, BF16) | Rejected BF16 *because of W5's lecture*, picked INT18 (§3) |
| W5: systolic array, dataflow types | Output-stationary 3-stage pipeline (§5.2) |
| W5: BF16 dynamic range | The exact reason I checked my range and went integer (§3.1) |
| W7: ASIC flow front/back-end | Yosys 4c gotcha lived in the front-end synth check (§6.2) |
| W7: IMC, energy of memory access | Power breakdown shows 98% in clock+state (§6.3) |

## 9. Codefest → project crosswalk

| Codefest | Skill | Where it became project work |
|----------|-------|------------------------------|
| CF01 | `cProfile` workload accounting | Identified `_get_dists` as 46% (§1.4) |
| CF02 | Roofline, AI computation | M1 ridge analysis, M4 final roofline (§1.3) |
| CF03 | CUDA GEMM, DRAM traffic | Tiling intuition for the centroid broadcast (§5.4) |
| CF04 | Fixed-point quant, MAC HDL | INT18 decision + the MAC discipline (§3.2) |
| CF05 | 2×2 systolic trace | Output-stationary pipelining intuition (§5.2) |
| CF06 | Sneak path KCL | (Not on this design's critical path, but informed M2 floating-node debug) |
| **CF07** | **STA on the v0 prototype** | **Directly produced the 3-stage pipeline plan (§5.2)** |
| CF08 | AER bandwidth, burst vs mean | Same methodology as M1 interface selection (§2.3) |

CF07 is the codefest with the highest weight on the project. The STA report on the unpipelined v0 is literally the document that told me how to cut the pipeline. Without CF07 I would have shipped an unsynthesizable design.

---

## 10. What I'd do differently

1. **M2's float32 detour was useful, not wasted.** It was the reference model for M3 sim diff. But I should have committed to integer earlier instead of carrying two engines.
2. **Start DIST_W at the right width.** I burned a CF07 STA round on `DIST_W=20` only to drop to 18. The 195,075 < 2^18 inequality was sitting right there from M2.
3. **Read the yosys 4c error before assuming the design was broken.** I spent two hours suspecting my RTL when the issue was a checker false-positive. `ERROR_ON_SYNTH_CHECKS: false` was a one-line fix once I read the actual error string.
4. **Pipeline the v0 design from day one.** CF07's STA showed that no single-cycle 16-PE distance core was ever going to close at 100 MHz on sky130. I should have planned for 3 stages before writing any v0 RTL.

---

## 11. Where this design goes next (outside M4 scope)

- **Wider K**: K=16 was M1-scoped. K=256 would force argmin from 4 levels to 8 levels and probably add a 4th pipeline stage.
- **HBM3 streaming feeder**: M4's block diagram (see `report/figures/block_diagram.png`) shows the dashed HBM3 path. Wiring that up bypasses AXI entirely and turns the design into a true near-memory feeder, which is the W7 IMC ideal.
- **Centroid update on-chip**: the 54% that stays on the host. Accelerating it would push end-to-end speedup from 1.81× toward the kernel's 42×.

---

## Pointers

| Concept | File |
|---------|------|
| M1 baseline measurements | `project/m1/sw_baseline.md` |
| M1 interface selection | `project/m1/interface_selection.md` |
| M2 precision argument | `project/m2/precision_choice.md` |
| M3 pipeline plan | `project/m3/synthesis_notes.md` §"Pipeline cuts" |
| M3 4c workaround | `project/m3/synth/HOW_TO_FIX_4C.md` |
| M4 9-section justification | `project/m4/report/design_justification.pdf` |
| M4 benchmark | `project/m4/bench/benchmark.md` |
| CF07 STA that drove the pipeline | `codefest/cf07/cman_*.md` |
| CF02 roofline methodology | `codefest/cf02/cman_roofline.md` |

End.
