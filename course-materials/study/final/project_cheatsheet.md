# Project Cheat Sheet — K-Means PIM Accelerator
Bao Nguyen | ECE 410/510 Spring 2026

---

## The Problem (M1)

| Item | Value |
|------|-------|
| Workload | K-Means image color quantization |
| Image | bliss.jpg, 800×600 = 480,000 pixels |
| Parameters | K=16 colors, D=3 (RGB), 20 iterations |
| CPU baseline | ~9 s/image, 0.16 GFLOP/s achieved |
| Hot kernel | Pairwise distance — 46% of runtime (cProfile) |
| Arithmetic intensity | 1.68 FLOP/byte (8 ops / ~4.8 bytes per pixel-centroid pair) |
| CPU ridge point | ~18 FLOP/byte |
| Diagnosis | Deep memory-bound — DRAM bandwidth, not compute, is the limit |
| Fix | Near-memory PIM chiplet; co-locate compute with HBM3 |

**Why PIM fixes it:** Moving compute next to memory drops the effective ridge point below 1.68, making the kernel compute-bound. Faster CPU cores or more threads cannot help a memory-bound workload.

---

## Interface Selection (M1)

| Interface | Bandwidth | Needed | Verdict |
|-----------|-----------|--------|---------|
| SPI / I²C | ~0.05 GB/s | 50 GB/s | nowhere close |
| AXI4-Lite | ~1 GB/s | 50 GB/s | no |
| PCIe 5.0 x16 | 64 GB/s | 50 GB/s | marginal |
| **UCIe Advanced** | **2,560 GB/s** | **50 GB/s** | **51× headroom** |

Required BW = 7.68 MB image / 154 µs compute time ≈ 50 GB/s.
UCIe chosen: designed for chiplet-to-chiplet advanced packaging, low latency, no PCIe PHY overhead.

---

## Precision Choice (M2)

| Format | Max exact integer | Max K-Means dist (3×255²=195,075) | Result |
|--------|-------------------|-----------------------------------|--------|
| INT8 | 255 | overflow | wrong |
| INT16 | 65,535 | overflow (255²=65,025 per channel) | wrong |
| FP16 | 2,048 | can't represent | wrong |
| BF16 | 256 | can't represent | wrong |
| FP32 | 16,777,216 | fits exactly | correct but costly |
| **INT18** | **262,143** | **fits exactly** | **correct + cheap** |

RGB is already integers [0,255] — no fractional information exists. INT18 is exact with no vendor FP units needed.
DIST_W dropped 20 → 18 after CF07 STA showed top 2 bits always zero (math confirms: ⌈log₂(195,075)⌉ = 18).

---

## RTL Architecture (M2 → M3)

**M2 (behavioral, not synthesizable):**
- `distance_engine.sv`: float32 compute using simulation-only `real` arithmetic
- `axil_slave.sv`: AXI4-Lite wrapper, float32 register map

**M3/M4 (synthesizable integer):**
```
Host CPU
  │ UCIe
  ▼
interface.sv (axil_slave_int)     ← AXI4-Lite register map
  │
compute_core.sv (kmeans_dist_core_pipelined)
  │ 3-stage pipeline
  ▼
(min_dist [17:0], label [3:0])
```

**AXI4-Lite register map:**
| Address | Name | Dir | Contents |
|---------|------|-----|----------|
| 0x000 | CTRL | W | bit[0]=start (self-clearing) |
| 0x004 | STATUS | R | bit[0]=done, bit[1]=busy |
| 0x008 | PIXEL | W | [23:16]=R, [15:8]=G, [7:0]=B |
| 0x010–0x04C | CENT[0..15] | W | RGB packed, 4 bytes each |
| 0x100 | RESULT_LABEL | R | [3:0] nearest centroid |
| 0x104 | RESULT_DIST | R | [17:0] min squared distance |

---

## 3-Stage Pipeline (M3)

**Why pipeline?** CF07 unpipelined: WNS = −31.53 ns (fails timing by 3×). One long combinational chain: 16 parallel kdist computations → 4-level argmin tree = ~41.5 ns. Splitting into 3 stages cuts each to ~14 ns → closes 10 ns.

| Stage | What happens | Output |
|-------|-------------|--------|
| Stage 1 | 16 parallel kdist: abs_diff(8b) → square(16b) → sum(18b), all in parallel | 16 kdist values, registered |
| Stage 2 | Argmin levels 1+2: 16→8→4 (pairwise compare) | 4 (dist, label) pairs, registered |
| Stage 3 | Argmin levels 3+4: 4→2→1 winner | final (min_dist, label), registered |

**Dataflow:** Weight-stationary. 16 centroids (48 bytes) loaded once per K-Means iteration. Pixels stream through one per cycle. Same idea as TPU MXU weight-stationary.

**Pipeline stats:**
- Latency: 3 cycles from start to done
- Throughput: 1 sample/cycle steady state (fully pipelined)

---

## Synthesis Results (M3/M4)

| Metric | Value |
|--------|-------|
| Tool | OpenLane v2.3.10, sky130_fd_sc_hd PDK |
| Clock target | 10 ns / 100 MHz |
| WNS (typical) | 0.0 ns — timing CLOSED |
| Worst slack | +3.13 ns (31% headroom) |
| Slow corner | Fails by ~3 ns (SS 100°C 1.6V — expected in open-source flow) |
| Cell area | 92,689 µm² ≈ 0.093 mm² |
| Die | 600×600 µm, ~26% utilization |
| Cells | ~7,700 sky130 cells, 693 flip-flops |
| Power | 5.87 mW @ 100 MHz typical |
| Power split | 50% clock tree, 47% flip-flops, 2% combinational |

**Critical path:** pixel register in AXI slave → 5-buffer broadcast to 16 abs_diff blocks → Stage 1 compute → s1_kdist register. ~6.87 ns. Fan-out broadcast is the dominant delay.

**CF07 vs M4 comparison:**
| | CF07 (unpipelined) | M4 (pipelined) |
|--|----|---|
| WNS | −31.53 ns | +3.13 ns |
| Area | 0.155 mm² | 0.093 mm² (−40%) |
| Cells | 17,029 | 7,671 (−55%) |

Pipeline added registers but let yosys pick smaller gates per stage → area went DOWN.

---

## Benchmark (M4)

| Metric | M1 CPU | M4 Accelerator | Ratio |
|--------|--------|----------------|-------|
| Throughput | 54,251 pixels/sec | 100,000,000 pixels/sec | **~1,843×** |
| Compute | 0.16 GFLOP/s | 12.8 GINT-ops/s | ~80× |
| AI | 1.68 ops/byte | ~42.7 ops/byte | 25× |
| Kernel time | 4.07 s | 0.096 s | **~42×** |
| End-to-end | 8.848 s | 4.89 s | **1.81×** |
| Power | ~20 W (CPU) | 5.87 mW | ~3,400× less |
| Energy/image | ~177 J | ~28 mJ (kernel) | ~2,900× |

**Amdahl analysis:**
- p = 0.46 (fraction accelerated)
- s = 42.4× (speedup on that fraction)
- Total = 1 / (0.54 + 0.46/42.4) = **1.81×**
- New bottleneck: centroid update step (54% of original runtime, still on CPU)

---

## What Did NOT Work (M4 Section 9)

| Problem | Fix |
|---------|-----|
| OpenLane yosys can't parse SV unpacked array ports | Maintain `synth/v2005/` with flat packed buses; SV files stay as sim source of truth |
| OpenLane synth checker false-positive ("Drivers conflicting with constant") | `"ERROR_ON_SYNTH_CHECKS": false` in config.json |
| Slow-slow corner timing miss (~3 ns) | Document and accept; close at nominal conditions per M1 target |
| iverilog static-init bug: `int x = expr` in for-loop body | Declare variables outside loop, assign inside |
| M2 run script relative path bug | Resolve paths from `${BASH_SOURCE[0]}` |
| Per-pixel AXI4-Lite not the streaming path | Compute core is the primitive; chiplet HBM3 feeder is system-level (M1 scope) |

---

## Cheat Sheet Concept → Project Connection

| Concept | Where it lives in the project |
|---------|-------------------------------|
| HW/SW co-design (#1) | CPU handles I/O + update; accelerator handles distance kernel |
| Memory wall (#3) | M1 diagnosis: DRAM is bottleneck, not ALUs |
| Arithmetic intensity (#5) | M1: 1.68 FLOP/byte → M4: 42.7 ops/byte |
| Roofline model (#6) | M1 → M4: working point moves up-and-right |
| Systolic arrays / dataflow (#9) | Weight-stationary: centroids fixed, pixels stream |
| Quantization / precision (#10) | M2: INT18 exact, FP16/BF16 overflow |
| In-memory computing (#12) | PIM chiplet on HBM3 eliminates data movement |
| VLSI / ASIC / EDA flow | M3/M4: Verilog → yosys → OpenROAD → sky130 |
| PPAC trade-offs | M3: timing closed, 0.093 mm², 5.87 mW |
| Domain-specific architecture (#8) | Custom integer pipeline beats general-purpose CPU by ~1,800× on kernel |
