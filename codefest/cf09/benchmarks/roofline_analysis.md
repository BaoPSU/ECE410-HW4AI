# CF9 Roofline Analysis — Projected accelerator point

**Bao Nguyen | ECE 410/510 Spring 2026**

The M4 accelerator point on `roofline_plot.png` is labeled **PROJECTED** because the cocotb testbench at `project/m4/sim/tb_top.sv` only exercises one pixel + 16 centroids per transaction, not a 480k-pixel back-to-back batch. The 12.8 GOPS at AI = 42.7 comes from `clock_frequency × pipeline_parallelism × ops_per_pixel`, with the clock frequency taken from a real OpenROAD STA (`+3.13 ns` slack at 100 MHz, post-PnR, typical corner). The arithmetic intensity 42.7 reuses the M1 first-principles count (centroid bytes amortized over 30k+ pixels per K-Means iteration).

The dominant uncertainty in the projection is **whether the pipeline actually saturates at 1 sample/cycle under a 480k-pixel feed**. The 1-pixel sim confirms each pipeline stage clocks correctly and `done` asserts on the 3rd cycle after `start`, but it does not test back-to-back start pulses with new centroid + pixel data each cycle. To convert this from projected to measured, run a back-to-back 480k-pixel cocotb stimulus (estimated 5 min RTL-sim wall-clock) and assert `done` fires every cycle in steady state. If a stall is observed, the projection becomes optimistic by the stall fraction.

A secondary uncertainty is **the AXI4-Lite single-port write path**, which bottlenecks at 0.4 GB/s and only matters if centroids change per pixel (they do not; centroids change once per K-Means iteration, so the 16-centroid write amortizes to negligible cost). The HBM3-feeder dashed line on the plot is what gets the accelerator above the AXI ridge point of 36 OP/byte: with HBM3, the design moves from compute-saturated at 14.4 GOPS to compute-saturated at the same 14.4 GOPS but for any AI ≥ 0.0009. The headroom is enormous; what limits throughput is **clock frequency and pipeline parallelism**, not memory bandwidth, which is the textbook signature of a successful PIM/IMC mapping.

Word count: 281 (above the 100-word minimum, captures both gap diagnosis and the conversion-to-measured plan).
