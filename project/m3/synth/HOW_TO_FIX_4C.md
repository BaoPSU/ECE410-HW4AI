# How I fixed M3 4c (timing report)

**Problem:** OpenLane 2.3.10 ran yosys synthesis fine but then quit at
`08-checker-yosyssynthchecks` with `"2 Yosys check errors found"`. The
errors are `Warning: Drivers conflicting with a constant` on yosys-internal
address-decode registers (Q[0..12] of a 13-bit DFF tied to value `13'h010`,
Q[2] of a 32-bit DFF tied to value `4`). They are **NOT real design bugs.**
Yosys's own final-check pass (after optimization) reports `Found and reported
0 problems.`

Without the fix: flow stops at synthesis. No floorplan, no PnR, no STA,
no power. M3 4c becomes "synth-stage only" instead of post-PnR timing.

## The fix (1 line in `config.json`)

Add this to `project/m3/synth/config.json`:

```json
"ERROR_ON_SYNTH_CHECKS": false
```

That's it. The full flow then runs cleanly through synthesis → floorplan
→ placement → routing → STA → power → DRC, producing real post-PnR
reports.

## How I found it

1. Grep the OpenLane source for the failing step:
   ```bash
   grep -rn "QUIT_ON_SYNTH" /home/bao/lib/python3.12/site-packages/openlane
   ```
2. Hit `openlane/steps/checker.py:173` — the `YosysSynthChecks` step has a
   variable `ERROR_ON_SYNTH_CHECKS` (deprecated alias `QUIT_ON_SYNTH_CHECKS`)
   with `default=True`.
3. Setting it to `false` demotes the failure to a warning.

## What the warning is actually about

The yosys check fires when a register's bits can be statically determined
to be constant after combinational propagation. In my case, the 16
centroid-address case labels (`12'h010, 12'h014, ..., 12'h04C`) create
intermediate logic where specific bits are predictable. Yosys flags this
as "double drivers" (the register driver + the constant driver), even
though the design works correctly. It's the kind of warning that helps
catch real bugs (like accidental tie-offs) but here it's false-positive
noise.

## Confirmed clean numbers after the fix

| Metric | Value |
|--------|-------|
| WNS (typical) | **0.0 ns** |
| TNS (typical) | **0.0 ns** |
| Worst slack | **+3.13 ns** |
| Placed area | 92,689 µm² |
| Total power @ 100 MHz | 5.87 mW |

Vs CF07 unpipelined: −31.53 ns / −662 ns / 22 failing endpoints / 0.155 mm².

## Lessons for M4 / future codefests

- **First-pass synthesis failures often come from the flow's safety
  checks, not the design.** Read the actual yosys log before refactoring
  RTL — the optimization passes after the failed check usually report
  "0 problems."
- **OpenLane config has knobs for every checker** (search `checker.py`
  for `error_on_var = Variable(...)`). The pattern is `ERROR_ON_*`,
  default `True`. Demote them deliberately when the failure is benign
  and you understand why.
- **Don't refactor first.** Try the override, see if the post-PnR
  numbers are sane, then decide if the underlying warning is worth
  cleaning up. For me it wasn't — the design closes timing with 3+ ns
  of slack regardless.
