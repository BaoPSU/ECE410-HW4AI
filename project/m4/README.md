# Milestone 4 — K-Means Image Quantization Accelerator (Final Package)

**Bao Nguyen | ECE 410/510 Spring 2026**

Final M4 deliverable: synthesizable, verified, benchmarked K-Means image color quantization accelerator. Same architecture as M3, with the addition of measured throughput benchmarks against the M1 SW baseline, an updated roofline plot, and the 9-section design justification report.

---

## File catalog

| Path | What it is | Supports |
|------|------------|----------|
| `README.md` | This file — index of every M4 deliverable | §1 README catalog |
| `hw4ai_ece510_project_milestone_4_spring26_r1.pdf` | Instructor's M4 brief and checklist (reference) | — |
| `rtl/top.sv` | Integrated top module: AXI4-Lite slave + pipelined compute core | §2 source code |
| `rtl/compute_core.sv` | 3-stage pipelined integer K-Means distance core (renamed from M3's `kmeans_dist_core_pipelined.sv`, **no source diff** from M3) | §2 source code |
| `rtl/interface.sv` | AXI4-Lite slave with integer register map (renamed from M3's `axil_slave_int.sv`, **no source diff** from M3) | §2 source code |
| `tb/tb_top.sv` | End-to-end testbench. Drives entirely through AXI4-Lite. K=16 RGB centroids matches M1-defended kernel scope | §2 testbench |
| `sim/run_iverilog.sh` | Sim driver (resolves paths from `${BASH_SOURCE[0]}`) | §2 reproduction |
| `sim/final_run.log` | M4 sim transcript with **PASS** | §2 sim log |
| `sim/final_waveform.png` | End-to-end annotated waveform: reset → write → compute → read | §2 waveform |
| `sim/tb_top.vcd` | Raw VCD dump for re-rendering the waveform | — |
| `synth/config.json` | OpenLane 2 configuration (10 ns clock, source list, `ERROR_ON_SYNTH_CHECKS: false`) | §3 synth config |
| `synth/openlane_run.log` | Full OpenLane v2.3.10 stdout/stderr (dockerized run) | §3 synth log |
| `synth/timing_report.txt` | **Post-PnR OpenROAD STA**. WNS = 0.0 ns / TNS = 0.0 ns at typical, +3.13 ns slack | §3 timing |
| `synth/area_report.txt` | **Post-PnR area**: 92,689 µm² in a 600×600 µm die. 7,671 cells, 693 flops | §3 area |
| `synth/power_report.txt` | **Post-PnR power**: 5.87 mW @ 100 MHz typical (47% sequential, 51% clock, 2% combinational) | §3 power |
| `bench/benchmark.md` | Measured throughput + speedup vs M1 SW baseline | §4 benchmark |
| `bench/benchmark_data.csv` | Raw measurements behind the benchmark numbers | §4 raw data |
| `bench/roofline_final.png` | M4 roofline with measured accelerator point (not M1 hypothetical) | §4 roofline |
| `report/design_justification.pdf` | 9-section design justification report (2,000–5,000 words) | §5 report |
| `report/design_justification.md` | Markdown source for the PDF | §5 report source |
| `report/figures/` | Figures referenced from the PDF report | §5 figures |

---

## Source diff from M3

**No diff.** The M4 RTL is the exact same content as M3, only with the filenames renamed to the canonical names the M4 brief specifies:

| M3 filename | M4 filename | Module name (unchanged) |
|-------------|-------------|-------------------------|
| `rtl/top.sv` | `rtl/top.sv` | `top` |
| `rtl/kmeans_dist_core_pipelined.sv` | `rtl/compute_core.sv` | `kmeans_dist_core_pipelined` |
| `rtl/axil_slave_int.sv` | `rtl/interface.sv` | `axil_slave_int` |

Module names inside the files are unchanged so the testbench's instantiation by module name still works without modification. The compute core and the slave are the same versions that produced the M3 timing/area/power numbers, which are also the M4 final numbers.

## How to reproduce the co-simulation

**Tool**: Icarus Verilog ≥ 11 (SystemVerilog 2012 support via `-g2012`)

```bash
bash project/m4/sim/run_iverilog.sh
```

Outputs `sim/final_run.log` (PASS line near the bottom) and `sim/tb_top.vcd`.

## How to reproduce the OpenLane synthesis

**Tool**: OpenLane v2.3.10 (dockerized)

```bash
cd project/m4/synth
sg docker -c 'openlane --dockerized config.json'
```

The full Classic flow runs through synthesis → floorplan → placement → routing → STA → power → DRC. Reports drop into `runs/RUN_<timestamp>/`; the curated headline reports are committed at `synth/` root.

**Important config override**: `"ERROR_ON_SYNTH_CHECKS": false` is set in `synth/config.json` to demote yosys's "Drivers conflicting with a constant" warnings from fatal to warning. These are false-positive checks on yosys-internal address-decode bits; the design synthesizes correctly. See `project/m3/synth/HOW_TO_FIX_4C.md` for the full investigation that landed on this fix.

## Top-level numbers (final)

| Metric | Value | vs M1 baseline |
|--------|-------|----------------|
| Throughput @ 100 MHz | 100 M samples/sec (steady state) | see `bench/benchmark.md` |
| WNS / TNS | 0.0 / 0.0 ns at typical+fast | timing CLOSED |
| Worst slack | +3.13 ns | 31% timing headroom |
| Cell area (placed) | 92,689 µm² ≈ 0.093 mm² | — |
| Die area | 360,000 µm² (600×600 µm) | — |
| Power | 5.87 mW @ 100 MHz typical | — |
| Verification | end-to-end PASS via AXI4-Lite | independent SW reference |
