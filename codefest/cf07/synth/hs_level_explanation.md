# Synthesis — Explained at High School Level

*Companion to `synth_interpretation.md` for when I want the plain-English version.*

---

## What you wrote vs what gets built

I wrote **Verilog** — a high-level description of what the chip should do, like:

> `output = (a − b) × (a − b)`

But a real chip is just **gates** — tiny on/off switches that compute AND, OR, XOR, NOT. You can't fab `(a − b) × (a − b)` directly. The whole thing has to be built from billions of those gates wired together.

**Synthesis** is the program (OpenLane → Yosys) that translates Verilog into a specific arrangement of gates that does the same thing.

It's like converting "turn left at the post office, drive 2 miles, look for the red barn" into actual GPS coordinates and exact street-by-street directions.

---

## The clock — the heartbeat of the chip

Every chip has a **clock** that ticks at a fixed rate. My target is **10 nanoseconds per tick = 100 MHz** (100 million ticks per second).

Between each tick, all the work has to happen:
1. Signals come out of one flip-flop (memory cell)
2. Travel through chains of gates
3. Arrive at the next flip-flop **before the next tick**

If signals arrive late → wrong data gets stored → chip is broken.

---

## The critical path — your longest road

Inside the chip, signals travel through chains of gates. Some paths are short (a couple of gates), some are long (hundreds of gates).

The **critical path** = the longest one in the whole chip.

For my CF07 design:
- Critical path = **41.5 ns**
- Clock period = **10 ns**
- Signal is **late by 31.5 ns** every tick

That's the WNS (Worst Negative Slack) of **−31.5 ns**.

**Analogy:** the school bell rings every 10 minutes for class change. If walking between classes takes me 41 minutes, I'm 31 minutes late every period. No amount of effort fixes that — the walk is just too long.

---

## Why is my path so long?

My K-Means chip tries to do this in **one tick**:
1. Compare an input pixel to 16 stored colors (48 subtractions in parallel)
2. Square each difference (16-bit squarers)
3. Add the 3 RGB-channel results into 16 "distances"
4. Compare all 16 distances and pick the smallest
5. Output the answer (the closest color's index)

All of that in series = 41.5 ns of gate-delay. Way too much for one 10-ns tick.

---

## The fix — pipelining

The fix is to **break the work into stages**, with a flip-flop between each stage to hold partial results. Like a McDonald's assembly line:

**Bad way (my current chip):**
- One worker takes your order, makes the burger, wraps it, hands it over.
- 41 minutes per customer.

**Good way (pipelined chip):**
- Worker 1: takes orders (10 min)
- Worker 2: cooks burgers (10 min)
- Worker 3: wraps + hands over (10 min)
- Each customer's burger takes 30 min from start to finish, **but a finished burger comes out every 10 min** once the line is full.

In my chip:
- Stage 1: do the 48 subtractions + squares → save partial results in flops
- Stage 2: do half of the argmin (find smallest of 8 pairs) → save
- Stage 3: finish argmin + output → done

Each stage now does ~14 ns of work. Still over 10 ns, so I might need a 4th stage. The goal is to get **every** stage under 10 ns so the design closes timing.

---

## What synthesis reports tell me

When OpenLane finishes, it gives me a "report card":

| Metric | Meaning |
|---|---|
| **WNS** | Worst grade — the single worst-failing path |
| **TNS** | Total points missed across all failing paths |
| **Setup violations** | How many paths failed (count) |
| **Hold violations** | Did anything race ahead too fast? (separate problem) |
| **Cell area** | How big the chip is in µm² |
| **Cell count** | How many gates total |
| **Fanout violations** | Are any wires driving too many destinations? |

---

## My CF07 report card

| Metric | Value | Verdict |
|---|---:|---|
| WNS | −31.53 ns | ❌ failed by 31.5 ns |
| TNS | −662.68 ns | ❌ across 22 paths |
| Setup violations | 22 | ❌ |
| Hold violations | 0 | ✓ |
| Slew / cap violations | 0 / 0 | ✓ |
| Cell area | 0.155 mm² | ✓ (tiny) |
| Cell count | 17,029 | ✓ |
| Sequential fraction | 0.32% | (almost all combinational — that's the problem) |

**Timing failed; area and count are fine.** Diagnostic: the design is the right size, just structured wrong — too much work piled into one tick.

---

## Why CF07 makes me do this *before* M3

The professor's point: **first-attempt synthesis almost always fails timing**. You're supposed to discover that *now* (CF07) so there's time to fix it (M3), instead of finding out the night before the deadline.

I did discover it. WNS = −31.5 ns means **pipelining is mandatory, not optional**. That's the whole CF07 lesson.

---

## What success in M3 looks like

| Metric | CF07 (now) | M3 target |
|---|---:|---|
| WNS | −31.53 ns | **≥ 0 ns** (ideally +1 to +3) |
| TNS | −662.68 ns | **0 ns** |
| Setup violations | 22 | **0** |
| Clock period | 10 ns | 10 ns (keep) |

When my re-synthesized M3 chip shows **WNS ≥ 0 and TNS = 0** — that's "timing closed." That's the goalpost.
