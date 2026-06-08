# Practice Final Exam Questions — K-Means Project
Bao Nguyen | ECE 410/510 Spring 2026

Format: 7 questions + 1 follow-up each. Oral exam style.
Answer structure: definition → components/mechanism → concrete example → big picture close.
Always use "I" when referencing the project. Target 45–60 seconds per answer.

---

## Q1. Your project diagnoses a memory-bound problem on the CPU. Walk me through how you arrived at that conclusion and what it means architecturally.

**Answer:**

The main problem is that moving data off DRAM costs far more than computing on it, which makes the bottleneck bandwidth rather than processing speed.

I profiled the K-Means distance kernel with cProfile and found it accounts for 46% of total runtime. Then I computed the arithmetic intensity (AI = FLOPs / Bytes) for that kernel. For each pixel-centroid pair, the inner loop does 8 floating point operations but has to load the pixel and write a distance value, giving an AI of about 1.68 operations per byte. The CPU's ridge point sits around 18 operations per byte, which is the threshold where compute and memory bandwidth are equally stressed. Since my kernel is at 1.68, it sits far into the memory-bound region of the roofline, meaning I am using less than 10% of the CPU's peak compute throughput.

What that means architecturally is faster cores or more cores will not help because the limit is how fast bytes come out of DRAM, not how fast the ALUs can process them. The only fix is to either increase reuse (raise AI) or move compute closer to memory.

The point is the roofline made the problem concrete. It was not a guess that the kernel was memory-bound. The number told me exactly where to intervene.

**Follow-up: How did you raise the arithmetic intensity from 1.68 to 42.7 in the accelerator?**

The main lever was centroid reuse. In the CPU baseline, the 16 centroids are loaded fresh from DRAM on nearly every distance computation. In the accelerator, I write the 16 centroids (48 bytes total) once per K-Means iteration into on-chip registers and hold them there while all 480,000 pixels in that iteration stream through. That means the 48 bytes of centroid data are loaded once and reused across roughly 30,000 pixels, so those loads get amortized over a much larger number of operations. Combine that with the pipelined parallel compute producing 128 integer ops per cycle, and the effective AI jumps to around 42 operations per byte, which puts the kernel comfortably compute-bound on the accelerator.

---

## Q2. Walk me through your precision choice. Why did you use 18-bit integer accumulators instead of floating point?

**Answer:**

A precision format needs to represent the maximum value that can appear in the computation without overflow or rounding error. For K-Means over RGB pixels, that is the worst-case squared distance.

RGB values are integers in the range 0 to 255 by definition. There is no fractional information to preserve. The maximum squared distance across three channels is 3 times 255 squared, which equals 195,075. I checked each candidate format against that bound. INT8 and INT16 both overflow because 255 squared is 65,025, which already exceeds INT16's range. FP16 and BF16 cannot represent 195,075 exactly because their mantissa bits are too narrow for integers that large, so they introduce rounding error that corrupts the argmin result when two centroids are close together. FP32 represents it exactly but requires synthesizable IEEE-754 floating point units, which cost significant area and add timing path complexity.

The exact integer threshold for the result is 18 bits, since 2 to the 18th is 262,143 which exceeds 195,075. So I used 18-bit unsigned integer accumulators, which are exact, cheap, and synthesize cleanly without any vendor IP.

Essentially the precision choice came down to correctness first and area second. INT18 is the tightest format that is provably correct for this specific workload.

**Follow-up: You mentioned DIST_W started at 20 and you dropped it to 18. How did you know it was safe to trim?**

I found out from the CF07 synthesis run. When I ran the unpipelined version through OpenLane, the STA report flagged `min_dist[18]` and `min_dist[19]` as unconstrained endpoints, meaning those bits never switched during the simulation. That is consistent with the math: the maximum value is 195,075, which only needs 18 bits, so the top two bits of a 20-bit accumulator are structurally always zero. Trimming them to 18 bits saved width on every accumulator and comparator across all 16 parallel distance computations, which reduced area and timing-path delay without changing any result.

---

## Q3. Describe the 3-stage pipeline in your compute core. Why three stages specifically, and what is in each one?

**Answer:**

A pipeline stage is a registered boundary that breaks a long combinational path into shorter segments so each one can meet a tighter timing constraint.

The CF07 synthesis run on the original single-stage design showed a worst negative slack of about 31.5 nanoseconds at a 10 nanosecond clock target. The critical path was the full distance computation followed by a four-level argmin tree all in one combinational cone, totaling around 41.5 nanoseconds. I split that at two natural boundaries to get roughly equal thirds.

Stage 1 is the distance compute. All 16 centroid distances run in parallel, each computing three absolute differences, squaring them, and summing to an 18-bit result. The outputs of all 16 kdist blocks register at the end of this stage. Stage 2 is the first half of the argmin tree, levels 1 and 2, which reduce 16 candidates to 4 by comparing pairs. Those 4 winners register. Stage 3 finishes the tree, levels 3 and 4, reducing to 1 winner and registering the final label and distance.

The tradeoff is 3 cycles of latency instead of 1, but throughput stays at 1 sample per cycle once the pipeline is full because each stage accepts a new input every cycle. For a 480,000-pixel image that is 480,000 cycles of useful work with only a 3-cycle startup cost, so the latency is negligible.

The point is pipelining transformed a design that failed timing by 3 times into one that closes with positive slack and actually uses less area because shorter combinational cones let the synthesizer pick smaller cells.

**Follow-up: Your design is weight-stationary. What does that mean and why does it fit K-Means?**

Weight-stationary dataflow means the weights, in my case the 16 cluster centroids, are loaded once and held fixed while the inputs stream past them. The TPU uses the same idea with neural network weights. For K-Means the mapping is direct: the 16 centroid values are written into on-chip registers at the start of each iteration and stay there while all 480,000 pixels stream through the compute pipeline one per cycle. The centroids are reused 480,000 times per iteration across 20 iterations. Since centroids are much smaller than the pixel data, keeping them stationary maximizes the reuse of the more expensive-to-load data and minimizes DRAM traffic per useful computation.

---

## Q4. Your M4 benchmark shows roughly 1,800 times throughput speedup on the kernel but only 1.81 times end-to-end speedup. Why is there such a large gap?

**Answer:**

This is Amdahl's law, which says the end-to-end speedup is bounded by the fraction of the workload you did not accelerate.

I measured with cProfile that the distance kernel accounts for 46% of total runtime. The remaining 54%, which is centroid update, convergence check, and Python overhead, still runs on the host CPU. Amdahl's law says total speedup equals 1 over the quantity of one minus the accelerated fraction plus the accelerated fraction divided by the speedup. Plugging in 0.46 for the fraction and about 42 for the kernel speedup gives a total of 1.81 times. The 54% that I did not touch becomes the new bottleneck, and it caps the whole system no matter how fast the accelerator gets.

In practice that means I accelerated from 4 seconds of distance-kernel time down to about 96 milliseconds, but the 4.8 seconds of centroid update time barely moved. The per-image time goes from about 9 seconds to about 5 seconds instead of the sub-second result the kernel speedup alone might suggest.

Essentially the lesson is that profiling the whole workload, not just the hot kernel, is the only way to know what end-to-end improvement is actually achievable before investing in hardware.

**Follow-up: If you extended the accelerator to also handle the centroid update step, what would happen?**

The centroid update step computes the mean position of all pixels assigned to each centroid. It is also a memory-bound accumulation kernel, similar to the distance step but with additions instead of squared differences. Offloading it to the same PIM chiplet would push the accelerated fraction from 0.46 toward 1.0 and dramatically improve the Amdahl bound. At that point the only remaining overhead is image I/O and Python interpreter cost. The same HBM3 bandwidth that feeds the distance kernel could feed the update kernel since the same pixel data is already on the chiplet, so the interface cost would be small. I flagged this in section 9 of the design justification as the highest-value follow-on improvement.

---

## Q5. What interface did you choose to connect the host to the accelerator, and why?

**Answer:**

The interface has to deliver enough bandwidth to keep the accelerator fed without becoming the new bottleneck itself.

I calculated the required bandwidth by dividing the total data per image by the time the accelerator takes to process it. At 8 TFLOP/s on the PIM chiplet, the full 20-iteration computation finishes in about 154 microseconds, and the image plus label data is about 7.68 megabytes per frame, which requires roughly 50 gigabytes per second. I compared that against the allowed interface options and chose UCIe, Universal Chiplet Interconnect Express, in advanced packaging mode. UCIe is rated at 2.56 terabytes per second, which gives 51 times the headroom over the 50 gigabyte per second requirement.

The reason to prefer UCIe over PCIe, which would also technically meet the bandwidth requirement, is the integration model. UCIe is designed for chiplet-to-chiplet connections in 2.5D and 3D packaging with sub-millimeter die-to-die distances, very low latency, and no PCIe PHY overhead. Since the PIM accelerator is co-packaged with the HBM3 stack, that packaging model is the right fit.

The point is the interface selection is not about picking the highest number. It is about matching the physical integration model and confirming the required bandwidth with margin.

**Follow-up: You implemented AXI4-Lite inside the chip but chose UCIe at the system level. Are those in conflict?**

They are at different layers of the design. UCIe is the die-to-die physical interface between the host processor and the PIM chiplet. AXI4-Lite is the on-chiplet register protocol that the host uses to write pixel data, trigger computation, and read results. In practice the UCIe link transports AXI-compatible packets, so AXI4-Lite is a natural mapping for the register-level control path. I chose AXI4-Lite over full AXI4 because the accelerator only needs single-shot register writes for K equals 16 centroids and one pixel at a time, so burst transfer management would add complexity without benefit. The two choices operate at different abstraction levels and complement each other.

---

## Q6. Walk me through the synthesis results and what they tell you about the design.

**Answer:**

Synthesis takes register-transfer-level Verilog and maps it onto physical cells in a specific process technology, then runs static timing analysis and power estimation on the placed result.

I ran OpenLane v2.3.10 on sky130, targeting 100 megahertz, a 10 nanosecond clock. The headline result is that timing closed at the typical and fast corners with a worst negative slack of 0.0 nanoseconds and 3.13 nanoseconds of positive slack. That 31% headroom means I am not right on the edge. The slow corner at extreme temperature and voltage misses by about 3 nanoseconds, which is expected in an open-source flow without margin engineering. The placed cell area is about 0.093 square millimeters across roughly 7,700 sky130 cells with 693 flip-flops. Power at 100 megahertz is about 5.87 milliwatts, split roughly half clock tree and half flip-flops with only about 2% in combinational logic.

Compared to the CF07 unpipelined baseline, the pipelined M4 design has 40% less area and 55% fewer cells despite adding pipeline registers. The reason is that shorter combinational paths per stage let the synthesizer pick smaller, lower-drive cells for each function, which ends up more efficient overall.

Essentially the synthesis results validate the pipelining strategy and give me the Fmax I need to claim 100 million pixels per second kernel throughput in the M4 benchmark.

**Follow-up: What was the critical path in your design and how did you identify it?**

The critical path runs from a pixel byte register inside the AXI4-Lite slave, through five buffer and repeater cells that the placer inserted to handle the high-fanout broadcast from one register to 16 parallel abs_diff blocks, through the Stage 1 abs_diff, square, and sum computation, and ends at a Stage 1 kdist output register. The OpenROAD static timing analysis report identified it as the longest path at about 6.87 nanoseconds. The fan-out broadcast is the main contributor because each of the 16 parallel compute blocks needs to receive the same pixel byte, which creates a high-fanout net that requires repeater insertion to meet transition time requirements. Replicating the pixel input register, one per abs_diff block instead of one shared, would shave most of that and is the most direct fix if I needed more timing margin.

---

## Q7. What did not work in your project, and what did you learn from it?

**Answer:**

There were several concrete failures, and the honest answer is that each one taught me something I will not repeat.

The biggest time sink was the OpenLane synthesis flow failing to parse my SystemVerilog files. Yosys's default frontend in OpenLane 2 chokes on unpacked array port syntax, which I did not know until the first run died at the header-generation step with a syntax error. The fix was to maintain a parallel set of Verilog-2005 files with flat packed buses for synthesis only, keeping the SystemVerilog originals for simulation. That cost a day I did not budget for. The lesson is to port to the synthesis-compatible format before running the tool, not after.

The second problem was the OpenLane synth checker flagging two false-positive warnings as fatal errors and killing the run. Those were address-decode bits that Yosys correctly inferred as constant after optimization. Yosys's own final-check pass reported zero problems, but the OpenLane safety checker treated them as errors. The fix was one line in the config, setting `ERROR_ON_SYNTH_CHECKS` to false.

The third issue is structural and I am being honest about it in the report. The per-pixel AXI4-Lite transaction model adds about 5 cycles of handshake overhead per pixel. At scale, the compute core can produce one result per cycle but the interface can only drive one pixel every 5 cycles. The production system would need a streaming feeder that reads pixel batches directly from HBM3, which is the M1 system diagram but was out of M4 scope.

The point is every failure mode was fixable but each one required recognizing the root cause instead of treating the symptom.

---

## Answer Structure Reminder

For every answer, follow the 4-step method from `answer_method.md`:

1. **Definition / diagnosis** — what is the problem or concept, one clear sentence
2. **Mechanism** — how it works or why it matters, flowing prose with transitions
3. **Concrete example** — always from the K-Means project, using "I"
4. **Big picture close** — "The point is...", "Essentially...", or "Basically..."

Style rules:
- No dashes or colons in spoken answers
- Spell out acronyms on first use
- No bullet dumps — connect ideas with transitions
- Never list variable names like "G-plus and G-minus" — describe what they represent
- Include formulas in parentheses after the plain-English description, not standalone
- Always use "I" for project work: "I profiled...", "I chose...", "I found..."
