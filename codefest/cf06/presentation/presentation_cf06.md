# CF06 CLLM — 4×4 Binary-Weight Crossbar MAC Unit
### Shine Presentation Script — ~5 minutes
**ECE 410/510 Spring 2026 | Bao Nguyen**

---

## Slide 1 — Title (0:00–0:20)

**Content:**
- Title: *CF06 CLLM: 4×4 Binary-Weight Crossbar MAC in SystemVerilog*
- Subtitle: ECE 410/510 Spring 2026 — Bao Nguyen
- Image: `slide_crossbar.png` (full slide background or inset)

**Say:**
> "Hi everyone — for CF06 CLLM I used Claude Sonnet 4.6 to generate a
> 4-by-4 binary-weight crossbar MAC unit in SystemVerilog. I'll walk you
> through the design, the testbench, and the simulation results."

**Mouse:** No pointer needed yet — just introduce yourself.

---

## Slide 2 — What is a Crossbar MAC? (0:20–1:20)

**Image: `slide_crossbar.png`**

**Say:**
> "A crossbar is a grid of wires — rows carry inputs, columns carry
> outputs, and at each intersection sits a weight that is either plus-one
> or minus-one.
>
> The computation is simple: for each output column j, you multiply every
> input by its weight at that row-column intersection, and sum them all up.
> That's the formula you see at the top — out[j] equals the sum over i of
> weight[i][j] times in[i].
>
> For our test case, inputs are 10, 20, 30, 40. The green cells are +1
> weights and the red cells are −1. You can trace column zero — it gets
> plus-ten, plus-twenty, minus-thirty, minus-forty — which gives minus-forty
> at the bottom. I'll verify that with simulation in a moment."

**Mouse:**
- Point to the **formula** at the top of the diagram when you say it
- Point to **col 0** heading and trace **down the column** through the circles
- Point to **out0 = −40** box at the bottom when you say "minus-forty"
- Briefly point to a green cell and a red cell when you say "+1 / −1"

---

## Slide 3 — Module Architecture (1:20–2:20)

**Image: `slide_module.png`**

**Say:**
> "Here's the internal architecture of crossbar_mac.sv. There are three
> stages.
>
> On the left, we have the input ports: weight_in is a 16-bit flat register
> that encodes the entire weight matrix, and weight_load is a one-cycle
> pulse that latches it. The four activations — in-zero through in-three —
> are 8-bit signed integers.
>
> The top block is the weight register, a simple flip-flop that stores
> the weights after weight_load pulses. Below that is the combinational
> crossbar MAC — it sign-extends the inputs to 10 bits and computes
> the four dot products in parallel using continuous wire assignments.
> Finally, the output register latches the result on the next clock edge.
>
> The outputs — out-zero through out-three — are 10-bit signed to handle
> the worst-case range: four inputs times 127 is about 500, which fits in
> 10 bits."

**Mouse:**
- Point to **weight_in / weight_load** labels on the left when you name them
- Point to the **purple weight register block** when you describe it
- Point to the **orange MAC block** when you say "combinational"
- Point to the **green output register** when you say "output register"
- Point to **out0–out3** on the right when you give bit-width reasoning

---

## Slide 4 — Weight Encoding (2:20–3:05)

**Image: `slide_encoding.png`**

**Say:**
> "The weight matrix is packed into a single 16-bit value using a simple
> rule: bit 4-times-i plus j encodes weight[i][j]. Green bits are plus-one,
> red bits are minus-one.
>
> The four row groups are color-coded at the bottom — row zero in the low
> four bits, row one in the next four, and so on. For our test case, row
> zero's weights are plus-one, minus-one, plus-one, minus-one — so bits
> zero through three are 1, 0, 1, 0. In the testbench I just pass a single
> 16-bit hex value and the RTL decodes it automatically."

**Mouse:**
- Point to the **formula** at the top "weight_in[4×i + j]"
- Sweep across the **bit cells left to right** when you describe the rows
- Point to the **row 0 green bracket** at the bottom
- Point to bits **0, 1, 2, 3** specifically and say their values

---

## Slide 5 — Testbench Strategy (3:05–4:00)

**Image: `slide_timing.png`**

**Say:**
> "The testbench has a two-cycle pipeline. You can see the timing here.
>
> First I assert reset to clear all registers. Then I release reset and
> apply the weight matrix and inputs simultaneously, with weight_load high
> for exactly one clock cycle — you can see that orange pulse around 20
> nanoseconds. The weight register latches on that rising edge.
>
> But the output register doesn't see the new weights until the NEXT cycle,
> because the MAC uses the just-latched register value. So the output only
> becomes valid two cycles after weight_load — you can see the green signal
> going high at 40 nanoseconds.
>
> The testbench reads the outputs right after that second rising edge and
> compares them against my hand-calculated expected values: minus-40, zero,
> minus-20, and minus-20."

**Mouse:**
- Point to the **rst_n signal going high** (purple waveform)
- Point to the **orange weight_load pulse** and say "one clock cycle"
- Trace the **dashed red line** at ~20ns down through the signals
- Point to the **green output signal** going high at ~40ns
- Point to the **dashed green line** at 40ns

---

## Slide 6 — Simulation Results (4:00–4:45)

**Image: `slide_results.png`**

**Say:**
> "And here are the simulation results from iverilog. All four outputs
> matched the hand-calculated values exactly.
>
> Out-zero is minus-40 — that was plus-10, plus-20, minus-30, minus-40 from
> column zero. Out-one is zero. Out-two and out-three are both minus-20.
>
> Four out of four tests pass. The green ALL TESTS PASSED at the bottom
> confirms the RTL is correct."

**Mouse:**
- Point to **out0 = −40   PASS** line when you say "minus-40"
- Point to **out1, out2, out3** lines in sequence
- Point to **"4/4 PASS"** and **"ALL TESTS PASSED"** at the bottom

---

## Slide 7 — Summary (4:45–5:00)

**Content:** (text slide — no diagram needed)

```
✓ LLM-generated crossbar_mac.sv (Claude Sonnet 4.6)
✓ 16-bit flat weight register, fully combinational MAC
✓ Testbench: weights [[1,-1,1,-1],[1,1,-1,-1],[-1,1,1,-1],[-1,-1,-1,1]]
             inputs  [10, 20, 30, 40]
✓ Simulation: 4/4 PASS — outputs [-40, 0, -20, -20]
```

**Say:**
> "To summarize: I used Claude Sonnet 4.6 to generate the crossbar MAC
> module. The key design choice was a flat 16-bit weight register decoded
> with a simple bit-index formula. The testbench confirmed all four outputs
> match hand calculations. Thanks."

**Mouse:** No pointer needed — just wrap up.

---

## Timing Guide

| Slide | Content | Duration |
|-------|---------|----------|
| 1 | Title | 0:20 |
| 2 | Crossbar concept | 1:00 |
| 3 | Module architecture | 1:00 |
| 4 | Weight encoding | 0:45 |
| 5 | Testbench timing | 0:55 |
| 6 | Simulation results | 0:45 |
| 7 | Summary | 0:15 |
| **Total** | | **~5:00** |

---

## Quick pointer cheat sheet

| When you say… | Point to… |
|--------------|-----------|
| "formula out[j] = Σ…" | top label on slide_crossbar.png |
| "column zero" | col 0 header, then trace down circles |
| "minus-forty" | out0 = −40 box |
| "weight register" | purple block on slide_module.png |
| "combinational MAC" | orange block |
| "weight_load pulse" | orange waveform spike, slide_timing.png |
| "two-cycle latency" | gap between orange and green signals going high |
| "4/4 PASS" | green text at bottom of slide_results.png |
