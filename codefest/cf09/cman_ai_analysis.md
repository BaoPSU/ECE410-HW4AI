# CF09 CMAN — Arithmetic Intensity Analysis

**Bao Nguyen | ECE 410/510 Spring 2026**

---

## Item 1 — Dominant Kernel, Dimensions, and Data Types

The dominant kernel inside my K-Means accelerator is the squared-difference accumulation in the distance engine. For every input pixel, the core computes the squared Euclidean distance from that pixel to each of K=16 centroids across D=3 color channels. The inner loop of `compute_core.sv` (Stage 1, lines 46–57) does three things per (k, d) pair: subtract the pixel channel from the centroid channel, square the difference, and add it into a running accumulator for that centroid. That subtract-square-accumulate sequence is what repeats K × D = 48 times per pixel, and the multiply is the expensive operation in hardware terms.

**Operand widths from the RTL:**

| Operand | Width | Why |
|---|---|---|
| `pixel[d]`, `centroids[k*D+d]` | 8-bit unsigned (`DATA_W=8`) | RGB values are in [0, 255] |
| `abs_diff[k][d]` | 8-bit | subtraction stays in range after absolute value |
| `sq_diff[k][d]` | 16-bit (`SQ_W = 2 × DATA_W`) | exact product of two 8-bit values |
| `kdist_c[k]` accumulator | 18-bit (`DIST_W=18`) | max value is 3 × 255² = 195,075, which fits in 18 bits but not 16 |

These are integer operations throughout. There is no floating point anywhere in the synthesizable core, which is why I say "ops" rather than "FLOPs" in the rest of this analysis.

---

## Item 2 — Total Ops Per Invocation

**Convention.** I count one squared-difference as three integer ops: one subtraction, one multiply, and one accumulate. This counts each arithmetic operation separately rather than collapsing the pair into a single MAC, which keeps the accounting transparent.

**What counts as one invocation.** One `start` pulse to the hardware produces one label output — one pixel's nearest centroid. That is the hardware boundary: the AXI4-Lite CTRL register triggers a single pixel-vs-all-centroids computation. The accelerator has no awareness of the 480,000-pixel batch or the 20-iteration loop; those live in software. So one invocation = one start pulse = one pixel.

**Distance kernel:**

```
ops_dist = K × D × 3
         = 16 × 3 × 3
         = 144 ops per pixel
```

**Argmin reduction.** Stage 2 and Stage 3 of the pipeline reduce 16 candidates to 1 winner through a 4-level tournament tree with K − 1 = 15 comparisons total (8 + 4 + 2 + 1). I count these separately because they are architecturally distinct from the distance compute.

```
ops_argmin = K − 1 = 15 compares per pixel
```

**Total:**

```
ops_total = 144 + 15 = 159 integer ops per pixel
```

For the AI analysis below I use 144 ops (the distance kernel alone) because the brief asks to identify the dominant kernel, and the 15-compare reduction is a secondary stage. Both numbers are honest and I will note the distinction where it matters.

---

## Item 3 — Arithmetic Intensity: Both Bounds

Arithmetic intensity (AI) is the ratio of computation to data movement, measured in ops per byte (AI = ops / bytes). The two bounds come from different assumptions about how much of the centroid data gets reused.

**Which operand is the weight and which streams.**
Looking at the AXI4-Lite register map in `interface.sv`: the pixel is written fresh to register `0x008 PIXEL` before every start pulse — it streams through. The 16 centroids are written once to registers `0x010–0x04C CENT[0..15]` and held in the register file across start pulses — they are the weights. Within one K-Means assignment pass over N pixels, the centroids never change. Only the pixel changes per invocation.

**Lower bound — no reuse.**

Assume every pixel invocation triggers a fresh fetch of everything it touches: D bytes of pixel data and K × D bytes of centroid data.

```
bytes_no_reuse = D + K × D
               = 3 + (16 × 3)
               = 3 + 48
               = 51 bytes per pixel

AI_lower = 144 ops / 51 bytes = 2.82 ops/byte
```

**Upper bound — full centroid reuse.**

Centroids load once and amortize over a batch of N pixels. Each pixel is unique so the pixel fetch never amortizes, but the centroid cost spreads across the batch.

```
bytes_full_reuse = D + (K × D) / N
                 = 3 + 48 / N

AI_upper(N) = 144 / (3 + 48/N)
```

At N = 480,000 (one 800×600 image):

```
bytes = 3 + 48 / 480,000 = 3 + 0.0001 ≈ 3.0001 bytes/pixel

AI_upper(480k) = 144 / 3.0001 ≈ 48.0 ops/byte
```

As N → ∞, the centroid term vanishes and the bound approaches:

```
AI_limit = 144 / 3 = 48.0 ops/byte
```

At 480,000 pixels the asymptotic limit is already reached to four significant figures, so I report **AI_upper = 48.0 ops/byte** for both the concrete case and the limit.

**Important wrinkle.** At N = 1 (one pixel, one invocation), both bounds collapse to 51 bytes/pixel and AI = 2.82 ops/byte. The full-reuse upper bound only separates from the lower bound when more than one pixel shares the same loaded centroids. The reuse is real but it lives in the software loop, not inside the hardware boundary. The hardware enforces nothing about N — it just holds the centroid registers until the CPU overwrites them.

---

## Item 4 — Roofline Sketch

The sketch is saved at `codefest/cf09/cman_roofline_sketch.png`.

**Platform numbers used:**

| Platform | Peak compute | Peak BW | Ridge point |
|---|---|---|---|
| sky130 ASIC (M4, AXI4-Lite, 100 MHz) | 14.4 GOPS | 0.2 GB/s | 72 ops/byte |
| i9-12900H SW baseline (DDR5) | 1,400 GFLOP/s | 76.8 GB/s | 18.23 ops/byte |

**sky130 peak compute derivation.** Stage 1 computes all 16 kdist values in parallel in a single cycle, each requiring D × 3 = 9 ops, for 144 ops/cycle total. At 100 MHz (the TT-corner post-PnR clock, closed with +3.13 ns of positive slack): 144 × 10⁸ = 14.4 × 10⁹ ops/sec = 14.4 GOPS.

**sky130 peak BW derivation.** The AXI4-Lite write databus in `interface.sv` is 32 bits wide (`wdata [31:0]`), 4 bytes per transaction. The write FSM has a mandatory two-state path: WR_IDLE (write executes) then WR_RESP (wait for bready), so the minimum transaction cost is 2 cycles. Best-case throughput: 0.5 transactions/cycle × 4 bytes = 2 bytes/cycle. At 100 MHz: 2 × 10⁸ = 0.2 GB/s.

**Sky130 ridge point:** 14.4 GOPS / 0.2 GB/s = 72 ops/byte.

**Where the kernel lands.** Both AI bounds sit to the left of the sky130 ridge point (2.82 < 72, 48.0 < 72), so the kernel is memory-bound across its entire operating range on this interface. The attainable performance band is:

```
Attainable at AI = 2.82:  2.82 × 0.2 GB/s = 0.56 GOPS
Attainable at AI = 48.0: 48.0 × 0.2 GB/s = 9.6 GOPS
```

The 14.4 GOPS compute ceiling is real but unreachable through AXI4-Lite. No amount of centroid reuse crosses the ridge point at 72 ops/byte — you would need AI > 72 to reach it, and the kernel's theoretical maximum is 48.0. The interface is the bottleneck, not the compute core.

---

## Item 5 — Highest-Leverage Change

The compute core has 14.4 GOPS of headroom that the interface cannot deliver. The bottleneck is not the RTL arithmetic — it is the AXI4-Lite write-handshake overhead on the per-pixel path.

**Change:** Replace the per-pixel write decode block in `interface.sv` (lines 84–112) with a dedicated AXI4-Stream slave port (`s_axis_pixel_tvalid`, `s_axis_pixel_tready`, `s_axis_pixel_tdata`) wired directly to `compute_core.pixel_flat`. The AXI4-Lite slave stays for the CTRL/STATUS/centroid control plane (low frequency, fine as-is). The new AXI4-Stream port handles the pixel data plane at one 32-bit beat per cycle with no response-channel handshake.

**Before:**
- BW: 0.2 GB/s (4 B × 0.5 txn/cycle × 100 MHz, WR_RESP state mandatory)
- Ridge: 14.4 / 0.2 = **72 ops/byte**
- Attainable: 0.56 GOPS at AI=2.82, 9.6 GOPS at AI=48.0
- Both bounds memory-bound — compute ceiling unreachable

**After:**
- BW: 0.4 GB/s (4 B × 1 txn/cycle × 100 MHz, AXI4-Stream fires every cycle)
- Ridge: 14.4 / 0.4 = **36 ops/byte**
- Attainable at AI=2.82: 2.82 × 0.4 = 1.13 GOPS (still memory-bound)
- Attainable at AI=48.0: min(48.0 × 0.4, 14.4) = **14.4 GOPS** (crosses ridge, hits compute ceiling)

This is the highest-leverage change because it is the only one that lets the full-reuse bound reach the compute ceiling — the hardware was designed with 144 parallel ops per cycle and can only express that throughput when the pixel feeder can keep up with one pixel per cycle, which AXI4-Stream delivers and AXI4-Lite structurally cannot.
