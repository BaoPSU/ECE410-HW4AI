# CF9 CMAN — what YOU need to do (NO AI tag)

The CF9 brief explicitly tags the CMAN portion as **NO AI**. The five tasks below are yours to write up, by hand, with no AI assistance on the analysis itself. This file lists the reference numbers from your existing M4 work that you can legitimately *look up* (those are your prior measurements, not new AI output), and the framework the writeup needs.

Once you've written the CMAN, the file lives at `codefest/cf09/cman_ai_analysis.md` and the hand-drawn sketch lives at `codefest/cf09/cman_roofline_sketch.pdf` (or `.png`).

---

## What you have to produce (5 items, in `cman_ai_analysis.md`)

### Item 1 — Kernel dimensions and data type

The kernel is the **K-Means distance-and-argmin core**. Write down:
- N = 480,000 pixels (per image, 800×600 RGB)
- K = 16 centroids
- D = 3 dimensions (RGB)
- Operating point: 100 MHz post-PnR (from your M4 timing report)
- Data type: INT8 pixel + INT8 centroid bytes, INT18 accumulator
- One pixel per cycle in steady state (3-stage pipeline, throughput = 1/cycle)

### Item 2 — Total FLOPs (or INT-ops) per invocation, with formula

Write out the count. The framework:
- Per (pixel, centroid) pair: D subtractions + D multiplies + D adds = **3D ops**
- Per pixel: K × 3D ops for the distance compute, plus (K - 1) ops for the argmin tree = **K × 3D + K - 1 ops/pixel**
- Per invocation (one image, one iteration): **N × (3KD + K - 1) ops**
- Plug in N=480,000, K=16, D=3, write the value.
- For 20 iterations (one full K-Means run on the image): multiply by 20.

### Item 3 — Bytes transferred, two bounds

This is the part the brief wants you to think hardest about. Two bounds:

**Lower-bound AI (NO data reuse)**: every (pixel, centroid) pair triggers a fresh fetch of both.
- bytes_per_pair = D bytes (pixel) + D bytes (centroid) = 2D bytes
- total_bytes = N × K × 2D
- formula + value.

**Upper-bound AI (FULL weight reuse)**: centroids loaded once, pixels streamed.
- bytes_per_invocation = K × D (centroids, once) + N × D (each pixel once)
- total_bytes = K × D + N × D
- formula + value.

If you decide your reuse pattern is NOT GEMM-style weight-stationary, **name the pattern** you are using (your design is closer to a "broadcast-weight" or "streaming MVM with broadcast weight reuse" pattern). State which pattern your design realizes.

### Item 4 — AI for both bounds + hand-drawn roofline

```
AI_lower = ops / total_bytes_lower
AI_upper = ops / total_bytes_upper
```

Then draw the roofline **by hand** (the brief specifically says hand-drawn):
- X-axis: arithmetic intensity (FLOP/byte), log scale 0.1 to 100
- Y-axis: attainable performance (GOPS), log scale 0.1 to 1000
- Plot the **sky130 platform roofline**: peak compute = K parallel kdist computes × ops/kdist × clock = 16 × 9 × 100 MHz = 14.4 GOPS theoretical. Peak BW = your interface choice (AXI4-Lite ≈ 0.4 GB/s, or HBM3 streaming feeder 16 TB/s if you justify it).
- Plot the **i9-12900H roofline** for comparison: peak 1,400 GFLOP/s, peak BW 76.8 GB/s, ridge at 18.23 FLOP/byte.
- Mark **AI_lower** and **AI_upper** as vertical lines.
- Mark the attainable-performance band for your kernel between the two bounds.
- Photograph or scan it as `cman_roofline_sketch.pdf` (or `.png`).

### Item 5 — Bottleneck + highest-leverage change

State out loud:
- Which is the limiter right now: HW interface bandwidth, on-chip memory bandwidth, or compute units?
- The one change that moves the needle most.

**A reasonable answer (you can write your own)**: at AI ≥ 36 (your sky130 ridge with AXI4-Lite), the design is compute-bound. To improve, widen the per-cycle parallelism (process 2 pixels/cycle, costing ~2× cells but doubling throughput) OR raise the clock by retiming. The AXI4-Lite path is NOT the bottleneck once centroids are amortized.

---

## Reference numbers you can legitimately look up

These are YOUR prior measurements from earlier milestones. Looking them up is not AI assistance; they are facts of your design.

| Number | Where to find it | Notes |
|--------|------------------|-------|
| N = 480,000 pixels | `project/m4/bench/benchmark.md` | image is bliss.jpg 800×600 |
| K = 16, D = 3, INT8 | `project/m4/rtl/compute_core.sv:23-27` | parameter block |
| 100 MHz post-PnR | `project/m4/synth/timing_report.txt` | +3.13 ns slack |
| 5.87 mW power | `project/m4/synth/power_report.txt` | typical corner |
| sky130 PDK | `project/m4/synth/config.json` | nominal figures from PDK |
| i9-12900H peak 1400 GFLOP/s, BW 76.8 GB/s | `project/m1/sw_baseline.md` | M1 baseline platform |
| M1 baseline AI = 1.68 | `project/m1/sw_baseline.md` | first-principles count |
| M4 reference AI = 42.7 (with weight reuse) | `project/m4/bench/benchmark.md` | matches your upper-bound calc |

---

## What you do NOT need to write

The CLLM portion (tasks 6-10) is already done. The files:
- `codefest/cf09/benchmarks/benchmark_results.md` — speedup table
- `codefest/cf09/benchmarks/roofline_plot.png` — projected accelerator on the roofline
- `codefest/cf09/benchmarks/roofline_analysis.md` — gap diagnosis
- `project/remaining_tasks.md` — 3 specific tasks

---

## Once you finish CMAN, this file can be deleted.
