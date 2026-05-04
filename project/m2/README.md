# Milestone 2 — K-Means Distance Engine (Behavioral RTL)

**ECE 410/510 Spring 2026 — Bao Nguyen**

---

## Submitted Files

| File | What it does |
|------|-------------|
| `precision_choice.md` | Precision analysis. Justifies float32 as the correct format: max squared distance across 3 RGB channels is 3×255²=195,075, which fits exactly in float32's 23-bit mantissa (max exact integer 2²⁴=16,777,216). INT8/INT16/FP16/BF16 all overflow or lose precision. |
| `rtl/distance_engine.sv` | Behavioral SystemVerilog compute core. Accepts one float32-packed pixel and 16 float32-packed centroids; outputs the nearest centroid label (4-bit) and the minimum squared distance (float32). Uses simulation-only `real` arithmetic internally — not synthesizable; will be replaced with FP32 units in M3. **1-cycle latency** (start → done on the next posedge). |
| `rtl/axil_slave.sv` | AXI4-Lite slave wrapper around `distance_engine.sv`. Exposes a register-mapped interface so the host CPU can load pixel/centroid data, trigger a computation, and read results. Implements full write-channel (AW+W split-channel FSM) and read-channel FSMs. |
| `tb/distance_engine_tb.sv` | Standalone testbench for `distance_engine.sv`. Three test cases: (1) nearest centroid at index 0, dist=3.0; (2) exact pixel match at centroid 5, dist=0.0; (3) nearest centroid at index 15, dist=9.0. |
| `tb/axil_slave_tb.sv` | AXI4-Lite interface testbench. Full end-to-end flow: write pixel (R/G/B) → write centroid[0] → assert CTRL.start → poll STATUS.done → read RESULT_LABEL and RESULT_DIST. Verifies label=0, dist=3.0. |
| `sim/run_iverilog.sh` | Shell script that compiles and runs both testbenches with Icarus Verilog (`iverilog -g2012`). Run from the `m2/` directory: `bash sim/run_iverilog.sh`. |

---

## File Structure Note

The M2 folder uses three subdirectories (`rtl/`, `tb/`, `sim/`) rather than flat placement, to keep RTL, testbenches, and scripts separate as the project grows toward M3.

The synthesizable integer core (`kmeans_dist_core.sv`, `DIST_W=20` integer accumulators, cocotb-verified) lives in `project/hdl/` — that is an early M3 prototype and is **not** part of the M2 submission. M2 is entirely contained in this folder.

---

## How to Simulate

```bash
cd project/m2
bash sim/run_iverilog.sh
```

Requires iverilog ≥ 11 (SystemVerilog 2012 support).

---

## AXI4-Lite Register Map (`axil_slave.sv`)

| Address | Name | R/W | Description |
|---------|------|-----|-------------|
| `0x000` | CTRL | W | bit[0] = start (self-clearing 1-cycle pulse) |
| `0x004` | STATUS | R | bit[0] = done (latched until next start) |
| `0x008` | PIX_R | W | Pixel R channel (float32) |
| `0x00C` | PIX_G | W | Pixel G channel (float32) |
| `0x010` | PIX_B | W | Pixel B channel (float32) |
| `0x014–0x0D0` | CENT[0..15][R/G/B] | W | Centroid array, 12 bytes/centroid |
| `0x100` | RESULT_LABEL | R | Nearest centroid index [3:0] |
| `0x104` | RESULT_DIST | R | Minimum squared distance (float32) |
