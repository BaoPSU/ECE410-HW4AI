# Milestone 3 — Integrated K-Means Accelerator + OpenLane Synthesis

**Bao Nguyen | ECE 410/510 Spring 2026**

This folder contains the M3 deliverables: an integrated top module that wires the AXI4-Lite control interface to the pipelined integer compute core, an end-to-end co-simulation testbench that drives the whole stack through the interface, and the OpenLane 2 synthesis results.

---

## File catalog

| Path | What it is |
|------|------------|
| `README.md` | This file — index of every M3 deliverable |
| `hw4ai_ece510_project_milestone_3_spring26_r1.pdf` | Instructor's M3 deliverables and checklist (reference) |
| `rtl/top.sv` | Integrated top module. Instantiates `axil_slave_int` only (slave instantiates the compute core directly); external ports are AXI4-Lite + clk/rst_n |
| `rtl/axil_slave_int.sv` | AXI4-Lite slave with integer register map (RGB packed in 32-bit words, 18-bit RESULT_DIST). M3 evolution of `project/m2/rtl/axil_slave.sv`, which was wired for float32 |
| `rtl/kmeans_dist_core_pipelined.sv` | 3-stage pipelined integer compute core: kdist compute → argmin levels 1-2 → argmin levels 3-4. DIST_W=18 (dropped from 20 per CF07 STA — `min_dist[18:19]` always zero) |
| `tb/tb_top.sv` | End-to-end testbench. Drives ENTIRELY through AXI4-Lite (no direct compute-core poking). K=16 RGB centroids. Independent SW reference computed in the testbench |
| `sim/run_iverilog.sh` | Compile + run script. Resolves paths from `${BASH_SOURCE[0]}` so it works from any cwd (lesson learned from the M2 path bug — see `project/m2/README.md`) |
| `sim/cosim_run.log` | Captured stdout of the iverilog run. Single unambiguous PASS line at the bottom |
| `sim/tb_top.vcd` | VCD dump of the full simulation |
| `sim/make_waveform.py` | VCD → PNG renderer (uses `vcdvcd` + matplotlib) |
| `sim/cosim_waveform.png` | Annotated end-to-end waveform with the 5 phases labeled |
| `synth/config.json` | OpenLane 2 configuration: clock 10 ns, source list of all 3 RTL files |
| `synth/openlane_run.log` | Full OpenLane 2 stdout/stderr |
| `synth/yosys_synthesis.log` | Full yosys synthesis log (cell mapping, optimization passes) |
| `synth/timing_report.txt` | **Post-PnR STA report (OpenROAD).** WNS = 0.0 ns / TNS = 0.0 ns at typical+fast corners with +3.13 ns positive slack. Slow-slow corner misses by ~3 ns (documented inside). |
| `synth/area_report.txt` | **Post-PnR area** 92,689 µm² (~0.093 mm²) in a 600×600 µm die. Yosys + sky130 cell breakdown also included. |
| `synth/critical_path.md` | Critical path: start register, end register, logic stages, why it's the longest |
| `synth/power_report.txt` | **OpenROAD post-PnR power: 5.87 mW** at typical 100 MHz (47% sequential, 51% clock tree, 2% combinational). |
| `synth/metrics.csv` | OpenLane curated metrics (one metric per row) |
| `synth/metrics.json` | OpenLane curated metrics (JSON form, includes `design__instance__area` etc.) |
| `synth/top.nl.v` | Post-techmap netlist (synthesized gate-level Verilog) |
| `synth/pre_techmap_stat.txt` | Yosys cell counts before sky130 mapping (raw gate stats) |
| `synth/v2005/top.v` | Verilog-2005 port of `rtl/top.sv` (yosys default frontend can't ingest the SystemVerilog version's unpacked-array ports — same lesson as CF07) |
| `synth/v2005/axil_slave_int.v` | Verilog-2005 port of `rtl/axil_slave_int.sv`. Uses a flat `case` over `wr_addr[11:0]` for the address decode instead of a `task` + loop (cleaner for yosys) |
| `synth/v2005/kmeans_dist_core_pipelined.v` | Verilog-2005 port of `rtl/kmeans_dist_core_pipelined.sv` with flat packed buses (`pixel_flat`, `centroids_flat`) instead of unpacked array ports |
| `synth/.gitignore` | Excludes the bulky `runs/` directory (only curated reports are committed) |
| `synth/HOW_TO_FIX_4C.md` | How the OpenLane post-synth checker was overridden (`ERROR_ON_SYNTH_CHECKS: false`) so the full PnR + STA + power flow could run — playbook for M4 and future codefests |
| `synthesis_notes.md` | ≥500-word narrative: what synthesized, what didn't, scope adjustments, M4 forward plan |

---

## How to reproduce the co-simulation

**Tool**: Icarus Verilog ≥ 11 (SystemVerilog 2012 support via `-g2012`)

```bash
bash project/m3/sim/run_iverilog.sh
```

The script compiles `rtl/{kmeans_dist_core_pipelined,axil_slave_int,top}.sv` plus `tb/tb_top.sv`, runs `vvp`, writes the transcript to `sim/cosim_run.log`, and emits a VCD at `sim/tb_top.vcd`. Look for the line `PASS` near the bottom of the log.

**To regenerate the waveform PNG**:

```bash
python3 project/m3/sim/make_waveform.py
```

Requires `vcdvcd` (`pip install vcdvcd`) and `matplotlib`. Reads `sim/tb_top.vcd`, picks the AXI4-Lite handshake signals + internal `eng_start/eng_done/busy`, renders them as a step plot with the 5 test phases annotated.

---

## How to reproduce the OpenLane synthesis

**Tool**: OpenLane v2.3.10 (matches CF07 — see `codefest/cf07/synth/`)

```bash
cd project/m3/synth
sg docker -c 'openlane --dockerized config.json'
```

The `--dockerized` flag pulls the official OpenLane 2 container with `yosys`, `OpenROAD`, `verilator`, etc. preinstalled. (The bare-metal `openlane` binary on this machine is missing those tools in PATH; the docker image bundles them.)

The run writes to `runs/RUN_<timestamp>/` inside `synth/`; the curated reports (`timing_report.txt`, `area_report.txt`, `power_report.txt`) and the full `openlane_run.log` are copied up into `synth/` so the grader doesn't have to chase the run hash.

---

## Glue logic between interface and compute core

The `axil_slave_int` module is the only glue between AXI4-Lite and the compute core. It does three things the core can't do on its own:

1. **RGB unpacking.** AXI writes deliver 32-bit words; the compute core wants per-channel 8-bit unpacked arrays. The slave's `do_write` task unpacks `data[23:16]/[15:8]/[7:0]` into `reg_pixel[d]` and `reg_centroids[k*D + d]`.
2. **Start pulse.** A write to `CTRL` (`0x000`) with bit[0]=1 fires `eng_start` for exactly one clock. The handshake is combinational on the AXI write completion (3-way path covering all 3 wr_state branches).
3. **Done latching + busy tracking.** The core's `done` pulses high for one cycle when the pipeline drains. `status_done` latches it until the next start. `busy` rises on `eng_start`, clears on `eng_done`, and is reported in `STATUS[1]` so the host can avoid back-to-back starts.

The DIST_W=18 → 32-bit zero-extension on `RESULT_DIST` reads is also handled in the read FSM.

No FIFOs, no clock-domain crossings, no width converters. Everything is in the same `clk` domain. This is the "no glue beyond the slave" path noted in `top.sv`.

---

## M4 mapping (forward reference, see `project/m4/milestone_4_brief.pdf`)

M4 expects this layout in `project/m4/rtl/`:

| M3 file | M4 path |
|---------|---------|
| `rtl/top.sv` | `project/m4/rtl/top.sv` (unchanged) |
| `rtl/kmeans_dist_core_pipelined.sv` | `project/m4/rtl/compute_core.sv` (rename) |
| `rtl/axil_slave_int.sv` | `project/m4/rtl/interface.sv` (rename) |

M4 also needs:
- A benchmark folder with measured throughput vs M1 SW baseline (the cycle count from `sim/cosim_run.log` plus the synthesis-achieved Fmax gives the M4 measured throughput)
- A power estimate (attempted in M3; carry the result or the documented failure forward)
- A 9-section design justification PDF (uses M2's precision analysis + M3's synthesis numbers)

The M3 synthesis_notes.md is the seed for the "Synthesis results" and "What did not work" sections of the M4 report.
