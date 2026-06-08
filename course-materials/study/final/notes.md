# Final Exam Notes
Bao Nguyen | ECE 410/510 Spring 2026

---

## Schedule

| Event | Date / Deadline |
|-------|----------------|
| M4 submission | Sun Jun 7 2026, 11:59pm |
| Final exam practice closes | Sun Jun 7 2026, 11:59pm |
| Final exam opens | Mon Jun 8 2026 |
| Final exam closes | Sun Jun 14 2026, 11:59pm |

**Platform:** https://teuscher-lab.ece.pdx.edu/shine

---

## Format

- 7 questions, each with one follow-up question to probe deeper
- All questions are about the K-Means project
- Typical completion: 30–40 min; reserve a 1-hour block

---

## Scope: all project milestones

| Milestone | Key topics likely to be tested |
|-----------|-------------------------------|
| M1 | Roofline, AI = 1.68 FLOP/byte, memory-bound diagnosis, UCIe interface selection (51× headroom over 50 GB/s), why near-memory PIM |
| M2 | Precision choice (INT18 exact, FP16/BF16 overflow, INT8/INT16 overflow), behavioral float32 RTL, AXI4-Lite register map |
| M3 | 3-stage pipeline design, CF07 → M3 timing closure story, synthesis results (100 MHz, WNS = 0, +3.13 ns slack, 0.093 mm², 5.87 mW), what did not work (SV frontend, synth checker, slow corner) |
| M4 | Kernel speedup (~1,843× throughput, 42.4× kernel time), Amdahl end-to-end 1.81×, why Amdahl caps it (centroid update 54% unaccelerated), roofline shift (AI 1.68 → 42.7), energy comparison |

---

## High-probability question topics

1. Why is the distance kernel memory-bound and what does that dictate about the fix?
2. Walk through your precision choice — why not FP32, why not FP16/BF16, why INT18?
3. What is weight-stationary dataflow and why does it apply to K-Means?
4. Why did CF07 fail timing and what specifically did you change for M3?
5. What does Amdahl's law say about your end-to-end speedup and what is the new bottleneck?
6. Walk through your 3-stage pipeline — what is in each stage?
7. What interface did you choose and why, given the bandwidth requirement?
8. What did not work and how did you fix it?
9. Where does your accelerator sit on the roofline compared to M1?
10. Why is the end-to-end speedup only 1.81× when the kernel is 42× faster?

---

## Key numbers to know (ratios, not exact figures)

- CPU baseline: ~9 s/image, distance kernel = 46% of runtime
- AI = 1.68 FLOP/byte (kernel), CPU ridge point ~18 FLOP/byte → memory-bound
- Accelerator AI = ~42.7 ops/byte → compute-bound
- Kernel speedup: ~1,800× throughput / ~42× on kernel time
- Amdahl end-to-end: ~1.81× (p = 0.46, s = 42.4)
- Pipeline: 3 stages, 1 sample/cycle steady state, 3-cycle latency
- Synthesis: timing closed at 100 MHz, ~6,000 cells, sub-mm² die, ~6 mW
- Interface: UCIe, 51× headroom over required bandwidth
- INT18 because 3 × 255² = 195,075 fits in 18 bits exactly
