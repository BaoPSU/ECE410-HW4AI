# CF07 — M3 Plan (post-synthesis)

**Bao Nguyen — ECE 410/510 Spring 2026**

> **Status: placeholder.** Fill in once OpenLane has run and `synth_interpretation.md` has real numbers.

---

## Synthesis target: Option A (K-Means distance core)

### What I'm changing for M3

[Pick from: pipeline the critical path, drop precision, reduce unrolling, change clock target, or keep as-is. Ground each decision in a specific number from your synthesis report.]

- **Clock target**: I achieved WNS = `<FILL IN ns>` at a `<FILL IN ns>` target. For M3 I will `<keep / relax / tighten>` the target to `<FILL IN ns>` because `<reason grounded in WNS / TNS>`.

- **Critical path**: the dominant path is the `<FILL IN — e.g. argmin tree across 16 centroids>`. To shorten it I will `<pipeline by inserting a register at level N / tree-reduce in pairs / keep as-is>` — this should cut path delay by roughly `<FILL IN ns>`.

- **Precision / unrolling**: current `DIST_W = 20`. The reports show `<FILL IN>` µm² in the accumulators. Dropping to `DIST_W = 18` (exact for 8-bit RGB at K=16) would save `<FILL IN>` µm² with no accuracy loss.

- **Other**: `<FILL IN — anything specific the synthesis flagged>`

---

*Word target: 100–150 words.*
