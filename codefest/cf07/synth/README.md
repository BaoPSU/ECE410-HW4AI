# CF07 CLLM — OpenLane 2 Synthesis

**Synthesis target:** Option A — K-Means distance core (`hdl/synth_top.sv`)

## How to run

1. Install OpenLane 2 (Docker required):
   ```bash
   git clone https://github.com/efabless/openlane2.git
   cd openlane2
   make
   ```

2. Run synthesis on `synth_top.sv`:
   ```bash
   openlane --dockerized run \
       --design-dir /home/bao/ECE410-HW4AI/codefest/cf07/hdl \
       --top kmeans_dist_core \
       --clock-period 10
   ```

3. After the run finishes, copy the key reports into this folder:
   - `final/reports/metrics.csv`
   - `final/reports/synthesis/*.rpt` (synthesis reports)
   - `final/reports/sta/*.rpt` (static timing analysis)

## What to look at first

After the run completes, open `metrics.csv` and grep for:

| Metric | Where it lives | What it tells you |
|--------|----------------|-------------------|
| `clock_period` | metrics.csv | What you actually achieved |
| `wns` (worst negative slack) | metrics.csv, STA report | Negative → critical path failed timing |
| `tns` (total negative slack) | metrics.csv | How many paths failed and by how much |
| `instance_count` | synth_stat.rpt | Total gate count |
| `cell_area` | metrics.csv | Total layout area in µm² |
| `setup_violation_count` | metrics.csv | How many timing constraints failed |

## Filling in the interpretation

Once you have the reports, edit `synth_interpretation.md` and replace every `<FILL IN>` placeholder with the actual number from your reports. Don't paste LLM generic commentary — anchor every claim to a specific number from your synthesis.
