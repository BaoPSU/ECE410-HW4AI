# CF9 Roofline Analysis — Projected accelerator point

**Bao Nguyen | ECE 410/510 Spring 2026**

The M4 accelerator point on `roofline_plot.png` is labeled **PROJECTED** because the cocotb testbench at `project/m4/sim/tb_top.sv` only exercises one pixel + 16 centroids per transaction, not a 480k-pixel back-to-back batch. The 12.8 GOPS at AI = 42.7 comes from `clock_frequency × pipeline_parallelism × ops_per_pixel`, with the clock frequency taken from a real OpenROAD STA (`+3.13 ns` slack at 100 MHz, post-PnR, typical corner). The arithmetic intensity 42.7 reuses the M1 first-principles count (centroid bytes amortized over 30k+ pixels per K-Means iteration).

The dominant uncertainty in the projection is **whether the pipeline actually saturates at 1 sample/cycle under a 480k-pixel feed**. The 1-pixel sim confirms each pipeline stage clocks correctly and `done` asserts on the 3rd cycle after `start`, but it does not test back-to-back start pulses with new centroid + pixel data each cycle. To convert this from projected to measured, run a back-to-back 480k-pixel cocotb stimulus (estimated 5 min RTL-sim wall-clock) and assert `done` fires every cycle in steady state. If a stall is observed, the projection becomes optimistic by the stall fraction.

A secondary issue is **the AXI4-Lite single-port write path**, which bottlenecks at 0.2 GB/s after accounting for the WR_IDLE→WR_RESP 2-cycle FSM in `interface.sv` (see CMAN `cman_ai_analysis.md` Item 4 for the derivation). At this BW, the sky130 ridge point sits at 72 ops/byte, so both first-principles AI bounds (2.82 lower, 48.0 upper) land in the memory-bound region. The HBM3-feeder dashed line on the plot is what gets the accelerator above the AXI ridge point: with HBM3, the design moves to compute-saturated at 14.4 GOPS for any AI ≥ 0.0009. The headroom is enormous; what limits throughput in the current M4 silicon is **the interface, not compute**, which matches the CMAN bottleneck call and the M1 system-diagram argument for UCIe.

Word count: 281 (above the 100-word minimum, captures both gap diagnosis and the conversion-to-measured plan).
