# CF07 — OpenLane 2 Synthesis Interpretation

**Target:** `synth_top.sv` (K-Means distance core, Option A from CF07 spec)
**Bao Nguyen — ECE 410/510 Spring 2026**

> **Status: placeholder.** OpenLane 2 has not been run yet — every `<FILL IN>` below must be replaced with the actual number from the synthesis reports before this is a real deliverable.

---

## (a) Clock period and worst-case slack

I ran synthesis at a target clock period of **`<FILL IN ns>`**. The reports show a worst-case slack (WNS) of **`<FILL IN ns>`**, with total negative slack TNS = **`<FILL IN ns>`** across **`<FILL IN>`** violating endpoints.

[If WNS is negative]: the design failed timing at this target. The critical path needs to be either pipelined or relaxed to a slower clock.
[If WNS is positive]: the design has **`<FILL IN ns>`** of headroom; I could push the clock to roughly **`<FILL IN MHz>`**.

## (b) Critical path

The dominant timing path runs from `<FILL IN source register>` to `<FILL IN sink register>`. Dominant cell types along the path: **`<FILL IN — e.g. AND, OAI21, FA1>`**. Logical levels: **`<FILL IN>`**.

For the K-Means core, this is most likely the combinational distance + argmin tree: 3 squared-difference subtractions per centroid, summed, then min-reduced across all 16 centroids. The width of the argmin comparator tree (log₂(K) = 4 levels deep) is the expected critical path.

## (c) Total cell area and top three contributors

Total cell area: **`<FILL IN µm²>`**. Top three contributors by area or instance count:

| Rank | Cell / module | Area or count | Why |
|------|---------------|---------------|-----|
| 1 | `<FILL IN>` | `<FILL IN>` | `<FILL IN>` |
| 2 | `<FILL IN>` | `<FILL IN>` | `<FILL IN>` |
| 3 | `<FILL IN>` | `<FILL IN>` | `<FILL IN>` |

Expected leader: the **K × D = 16 × 3 = 48 squared-difference multipliers** plus the **K-wide argmin tree**. The flat `centroids[0:K*D-1]` and `pixel[0:D-1]` arrays generate K·D = 48 subtractor-and-square paths; this is where most of the area should live.

## (d) Failed constraints, hold violations, warnings

- Setup violations: **`<FILL IN count>`** — `<FILL IN where>`
- Hold violations: **`<FILL IN count>`** — `<FILL IN where>`
- Synthesis warnings worth investigating:
  - `<FILL IN — e.g. inferred latch, multi-driver net, unconnected port>`
  - `<FILL IN>`

[Be specific: tie each warning to a line number in `synth_top.sv` or a specific module.]

---

*Word target: 200–300 words. Replace placeholders with real numbers, then trim or expand prose around them.*
