# M3 Synthesis Notes

**Bao Nguyen | ECE 410/510 Spring 2026**
*Narrative of what synthesized, what didn't, what changed, and what M4 needs.*

---

## What worked in M3

Three things landed cleanly.

**Integrated top module.** `project/m3/rtl/top.sv` instantiates `axil_slave_int`, which instantiates `kmeans_dist_core_pipelined`. No floating ports, no stub modules. The slave is the only path between AXI4-Lite and the compute core. The brief's hardest requirement ("interface must be the only path between host and compute") falls out for free from this nested instantiation: the testbench cannot poke the compute core directly because it has no handle to it.

**3-stage pipeline.** The compute core is split into three registered stages per the CF07 plan in `codefest/cf07/synth/m3_plan.md`:
- Stage 1: per-centroid distance compute (16 parallel kdist computations, each is 3 abs_diff → 3 squares → 3-input add)
- Stage 2: argmin tree levels 1+2 (16 → 8 → 4 candidates)
- Stage 3: argmin tree levels 3+4 (4 → 2 → 1 winner) plus the registered output

Each stage's combinational depth is roughly 1/3 of the CF07 monolithic 41.5 ns path, so the target Fmax should now sit close to 100 MHz (10 ns clock target). Throughput is one sample per cycle once the pipeline is full; latency is 3 cycles per sample.

**DIST_W reduced from 20 to 18.** CF07's STA flagged `min_dist[18:19]` as constant zero — the math max distance is 3 × 255² = 195,075 which fits in 17.57 bits (so 18 bits is the tight upper bound). Trimming saved width on the accumulator and on the argmin tree. The simulator confirms the result is unchanged at the trimmed width.

## Co-simulation PASS

`sim/cosim_run.log` shows the end-to-end test passing:

- 16 RGB centroids and a (200, 100, 50) pixel written through AXI4-Lite
- `CTRL.start` pulsed through a register write to `0x000`
- `STATUS` polled until `done` asserted (one poll succeeds because the read FSM stalls long enough for the 3-stage pipeline to drain)
- `RESULT_LABEL = 7` and `RESULT_DIST = 0` — centroid 7 was placed exactly at the pixel, so the squared distance is zero
- Independent SW reference in the testbench computes the same answer, label and distance match, **PASS** prints

There was one testbench bug along the way that's worth flagging: `int dR = expr;` inside a for-loop body is treated as a static initializer (set once at time 0) under iverilog, not a per-iteration assignment. The fix was to declare `dR/dG/dB` in a named begin-end block scope and assign inside the loop. Same pattern would have caught me in synthesis if it had leaked into RTL, so it's a good "always assign, never declare-and-initialize inside a loop" lesson.

## What did NOT work the first time

**OpenLane SV ingestion.** Same problem CF07 hit: yosys's default Verilog-2005 frontend in the OpenLane 2 docker chokes on unpacked array ports (`input logic [DATA_W-1:0] pixel [0:D-1]`). The flow died at the "Generate JSON Header" step with a syntax error on line 30 of `kmeans_dist_core_pipelined.sv`.

**Fix.** Wrote Verilog-2005 ports in `synth/v2005/` with flat packed buses (`pixel_flat[D*DATA_W-1:0]` and `centroids_flat[K*D*DATA_W-1:0]`), converted `logic` → `wire`/`reg`, `always_ff/comb` → `always @`, `typedef enum` → `localparam`, and dropped `task automatic`. The slave generates the flat buses from its internal unpacked storage with a `generate` loop, so the internal logic stays identical between SV and V-2005 versions. `synth/config.json` now points at the v2005 files for synthesis only; the SV originals in `rtl/` are still the simulation source of truth.

**Local OpenLane wrapper.** The first attempt used `openlane` from `/home/bao/bin/openlane`, which failed with `FileNotFoundError: verilator`. The bare-metal Python wrapper expects yosys + verilator + OpenROAD in PATH; only the docker image has them all bundled. **Fix:** wrap in `script -qc "sg docker -c 'openlane --dockerized config.json'"` (same workaround as CF07).

**M2 cascade bug.** Caught during M3 setup when re-running M2 sims for regression: `project/m2/sim/run_iverilog.sh` used relative paths (`RTL=../rtl`) that only worked when invoked from `project/m2/sim/`, but the usage comment said to run from `project/m2/`. Fixed by resolving paths from `${BASH_SOURCE[0]}` so the script works from any cwd. Documented in `project/m2/README.md` under "Issues found and fixed". The same `BASH_SOURCE` pattern is used in `project/m3/sim/run_iverilog.sh` to prevent a repeat.

## Scope adjustments from CF07

CF07 ran OpenLane on the unpipelined integer core and got WNS = −31.53 ns / TNS = −662.68 ns across 22 setup-violating endpoints at the 10 ns target. That run failed timing by ~3×, all on the same combinational chain (16 kdist computations stacked under a 4-level argmin tree). M3's scope adjustment, all driven by that data:

1. **Pipeline registers between stages.** Splits the 41.5 ns path into three ~14 ns segments. Expected WNS to flip positive at 10 ns.
2. **DIST_W 20 → 18.** Smaller accumulators, smaller argmin tree, less routing.
3. **No algorithm change.** K=16, D=3, integer arithmetic, single-pass argmin. Project goals from M1 (62× speedup target on K-Means image color quantization via PIM) are unchanged.

What was removed: nothing. What remains: the entire M1-defended kernel scope. What was substituted: a pipelined version of the same compute, plus a register-map-adapted AXI4-Lite slave. The M4 benchmark will still measure the same kernel against the same M1 baseline.

## M4 prep — what carries forward

- **Files mapping.** M3's `rtl/kmeans_dist_core_pipelined.sv` becomes M4's `rtl/compute_core.sv`. `rtl/axil_slave_int.sv` becomes `rtl/interface.sv`. `rtl/top.sv` stays. The M4 README will state the rename explicitly.
- **Throughput measurement.** M4 needs measured (not hypothetical) throughput. From `cosim_run.log`: 3-cycle pipeline depth, 1 sample/cycle steady-state. At post-synth Fmax (will be read from M3's `timing_report.txt`), throughput = Fmax × 1 sample/cycle. Combine with M1 SW baseline (~9 s/image on i9-12900H) for the M4 speedup ratio.
- **Power.** M3 attempts power estimation as part of the OpenLane flow; the result goes in `synth/power_report.txt`. If OpenLane's power step fails (it sometimes does without a switching-activity file), the failure mode is documented there for M4 to either fix or carry forward as a known-skip with explanation.
- **Roofline.** The M4 roofline uses the measured accelerator point (M1 AI = 1.68 FLOP/byte, M4 throughput = Fmax × 1 sample/cycle × 6 ops/sample). Plot in M4 with the SW baseline + measured accelerator + HBM3 roofline.
- **Design justification report.** The "what worked / what didn't / scope adjustments" sections of this file are the seed for the M4 report's "Verification", "Synthesis results", and "What did not work" sections. Carry over verbatim and add the measured-throughput and report-PDF wrapper.
