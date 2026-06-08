# Practice Final Exam Questions — K-Means Project
Bao Nguyen | ECE 410/510 Spring 2026

The real exam is 7 questions + 1 follow-up each. This file has 10 practice questions for extra coverage. Oral exam style.
Answer structure: definition/diagnosis → mechanism → concrete example → big picture close.
Open with "So..." or "I used..." — never start with "This is fundamentally..."
Use "I" for all project work. No dashes. No bullet dumps. Target 45–60 seconds.

---

## Q1. Your project diagnoses a memory-bound problem on the CPU. Walk me through how you arrived at that conclusion and what it means architecturally.

So I used hardware/software co-design to find where the bottleneck actually lives before I started designing anything, because accelerating the wrong part wastes hardware.

I started by profiling the CPU baseline with cProfile across multiple runs. That immediately flagged the pairwise distance computation as the dominant cost, close to half of total runtime. Then I computed the arithmetic intensity for that kernel, which is FLOPs divided by bytes moved from DRAM. The distance kernel does a small fixed number of multiply-adds per pixel-centroid pair but has to load the full pixel and write a full distance value each time, so the ratio comes out very low, about 1.68 operations per byte. The CPU's ridge point sits around 18 operations per byte, which is where compute and memory bandwidth are equally stressed. Since my kernel is at 1.68 it sits deep in the memory-bound region of the roofline, meaning the chip is spending most of its time waiting on data, not computing.

What that means architecturally is faster cores or more threads cannot help because the limit is how fast bytes come out of DRAM, not how fast the ALUs can process them. The only fix is to move computation closer to where the data lives.

The whole point is the roofline made the diagnosis concrete. It was not a guess. The number told me exactly where to intervene.

**Follow-up: How did you raise the arithmetic intensity in the accelerator?**

The main lever was centroid reuse. In the CPU baseline the 16 centroids get reloaded from DRAM on nearly every distance computation. In the accelerator I write the 16 centroids into on-chip registers once per K-Means iteration and hold them there while all the pixels stream through. Those 48 bytes of centroid data get amortized over hundreds of thousands of pixel computations instead of being loaded fresh each time. Combine that with the parallel pipeline producing many operations per cycle and the effective arithmetic intensity jumps from under 2 operations per byte up to around 42, which puts the kernel comfortably in the compute-bound region on the accelerator.

---

## Q2. Walk me through your precision choice. Why did you use 18-bit integer accumulators instead of floating point?

So I needed a format that represents the maximum value that can appear in the computation without overflow or rounding error. For K-Means over RGB pixels that means figuring out the worst-case squared distance first.

RGB values are integers in the range 0 to 255 by definition. There is no fractional information to preserve. The maximum squared distance across three channels is 3 times 255 squared, which works out to 195,075. I checked every candidate format against that bound. INT8 and INT16 both overflow because 255 squared already exceeds INT16's range. FP16 and BF16 cannot represent 195,075 exactly because their mantissa bits are too narrow for integers that large, so they introduce rounding error that corrupts the argmin result when two centroids are close together. FP32 represents it exactly but requires synthesizable floating point units, which cost significant area and add complexity I did not need.

The exact integer threshold for the result is 18 bits, since 2 to the 18th exceeds 195,075. So I used 18-bit unsigned integer accumulators. They are exact, cheap, and synthesize cleanly without any vendor IP.

Essentially the precision choice came down to correctness first and area second. INT18 is the tightest format that is provably correct for this specific workload.

**Follow-up: You mentioned DIST_W started at 20 and you dropped it to 18. How did you know it was safe?**

I found out from the CF07 synthesis run. When I ran the unpipelined version through OpenLane, the timing report flagged the top two bits of the distance accumulator as unconstrained endpoints, meaning those bits never switched during simulation. That is consistent with the math since the maximum value only needs 18 bits. Trimming the accumulator width saved area and reduced the delay through every comparator and adder across all 16 parallel distance computations, without changing any result.

---

## Q3. Describe the 3-stage pipeline in your compute core. Why three stages, and what is in each one?

So the reason I needed a pipeline at all is that the first version failed timing by about three times. The CF07 synthesis run showed a worst negative slack of around 31 nanoseconds at a 10 nanosecond clock target. The design was trying to do everything in one tick: compare the pixel to all 16 centroids, square the differences, sum them up, then find the winner. Think of it like one worker at a McDonald's trying to take your order, cook the burger, wrap it, and hand it to you all before the next customer walks in. At a certain pace that just is not possible.

The fix is the same idea as the assembly line. You break the work into stages, put a register between each one to hold the partial result, and now each stage only has to finish its portion before the next clock tick. A finished result comes out every tick once the line is running.

Stage 1 computes all 16 distances in parallel. Each centroid block runs the absolute difference, squaring, and sum across three channels simultaneously. All 16 results register at the end of this stage. Stage 2 takes those 16 candidates and runs the first two levels of the argmin tournament, narrowing down to 4 finalists, then registers. Stage 3 finishes the tournament down to 1 winner and registers the final label and distance output.

The tradeoff is 3 cycles of latency instead of 1, but throughput stays at 1 pixel per cycle once the pipeline is full. For hundreds of thousands of pixels that startup cost is negligible.

The point is pipelining did not just fix timing. It actually reduced area compared to the unpipelined version because shorter paths per stage let the synthesizer pick smaller cells for the same function.

**Follow-up: Your design is weight-stationary. What does that mean and why does it fit K-Means?**

Weight-stationary dataflow means the weights stay fixed while inputs stream past them. The TPU uses the same idea for neural network weights. For K-Means the mapping is direct: the 16 centroid values get loaded into on-chip registers at the start of each iteration and stay there while all the pixels stream through the pipeline one per cycle. The centroids are far fewer bytes than the pixel data and they get reused for every pixel in the iteration, so keeping them stationary maximizes reuse of the most expensive data to load and minimizes DRAM traffic per useful computation.

---

## Q4. Your M4 benchmark shows a massive kernel speedup but only about 1.8 times end-to-end speedup. Why such a large gap?

So this is Amdahl's law in action, which says the end-to-end speedup is bounded by the fraction of the workload you did not accelerate.

I measured with cProfile that the distance kernel accounts for 46% of total runtime. The remaining 54%, centroid update, convergence check, and Python overhead, still runs on the host CPU. Amdahl's law says total speedup equals 1 over the quantity of one minus the accelerated fraction plus that fraction divided by the speedup on it. Plugging in 0.46 for the fraction and the kernel speedup gives a total of about 1.81 times. The 54% I did not touch becomes the new bottleneck and caps the system no matter how fast the accelerator gets.

In practice I accelerated the distance computation from several seconds down to under a tenth of a second, but the centroid update time barely moved. The per-image time goes from about 9 seconds to about 5 seconds instead of the sub-second result the kernel number alone might suggest.

The whole point is that profiling the whole workload is the only way to know what end-to-end improvement is actually achievable. Accelerating the wrong 54% and leaving the 46% on the CPU would have given even less than 1.81 times.

**Follow-up: If you also accelerated the centroid update step, what would happen?**

The centroid update step is also a memory-bound accumulation kernel, computing the mean position of all pixels assigned to each centroid. Offloading it to the same PIM chiplet would push the accelerated fraction from 0.46 toward the full workload and dramatically improve the Amdahl bound. The same HBM3 bandwidth that feeds the distance kernel could feed the update kernel since the pixel data is already on the chiplet. I flagged this in the design justification as the highest-value follow-on improvement.

---

## Q5. What interface did you choose to connect the host to the accelerator, and why?

So the interface needs to deliver enough bandwidth to keep the accelerator fed without becoming the new bottleneck itself.

I calculated the required bandwidth by dividing the total data per image by the time the accelerator takes to process it. That gives roughly 50 gigabytes per second as the minimum needed. I compared that against the allowed interface options and chose UCIe, Universal Chiplet Interconnect Express, in advanced packaging mode. UCIe is rated at over 2 terabytes per second, which gives more than 50 times the headroom over what I need.

The reason to prefer UCIe over PCIe, which would also technically meet the bandwidth requirement, is the integration model. UCIe is designed for chiplet-to-chiplet connections in advanced packaging with very low latency and no PCIe PHY overhead. Since the PIM accelerator is co-packaged with the HBM3 memory stack, that physical integration model is the right fit.

The point is the interface choice is not about picking the highest number on a spec sheet. It is about matching the physical packaging and confirming the required bandwidth with margin to spare.

**Follow-up: You implemented AXI4-Lite inside the chip but chose UCIe at the system level. Are those in conflict?**

They are at different layers. UCIe is the die-to-die physical interface between the host processor and the PIM chiplet. AXI4-Lite is the register protocol the host uses inside the chiplet to write pixel data, trigger computation, and read results. UCIe transports AXI-compatible packets, so AXI4-Lite is a natural mapping for register-level control. I chose AXI4-Lite over full AXI4 because the accelerator only needs single-shot register writes for 16 centroids and one pixel at a time, so burst management would add complexity without any benefit. The two choices operate at different abstraction levels and complement each other.

---

## Q6. Walk me through the synthesis results and what they tell you about the design.

So synthesis takes register-transfer-level Verilog and maps it onto physical cells in a specific process, then runs timing analysis and power estimation on the placed result. The report card it gives you tells you whether the design is actually buildable at your target clock.

I ran OpenLane on sky130, targeting 100 megahertz. The headline result is that timing closed at the typical and fast corners with positive slack to spare, meaning every signal arrives before the next clock tick with room to breathe. The slow corner at extreme temperature and low voltage misses by a few nanoseconds, which is expected in an open-source flow without margin engineering. Area comes out under a tenth of a square millimeter. Power at 100 megahertz is under 6 milliwatts, split roughly half to the clock tree and half to the flip-flops, with only about 2% in actual combinational logic.

That last number is interesting. Normally you would expect combinational logic to dominate power in a compute-heavy design. But because the pipeline registers gate each stage, logic only switches when new data is in flight, which keeps switching power very low.

Compared to the CF07 unpipelined baseline, the M4 pipelined design has about 40% less area and 55% fewer cells despite having added pipeline registers. The reason is shorter combinational paths per stage let the synthesizer pick smaller cells for the same function. The pipeline ended up more efficient, not just faster.

Essentially the synthesis numbers gave me the Fmax I needed to claim the kernel throughput in the M4 benchmark.

**Follow-up: What was the critical path and how did you identify it?**

The critical path runs from a pixel register inside the AXI4-Lite slave, through several buffer cells the placer inserted to handle the broadcast from one register to all 16 parallel distance computation blocks, through the Stage 1 compute, and ends at the Stage 1 output register. The OpenROAD timing report identified it as the longest path. The fan-out broadcast is the main contributor because one register has to drive 16 identical loads, which forces the placer to insert repeaters to meet signal quality requirements. Replicating that pixel register so each distance block has its own copy would remove most of that overhead and is the most direct timing improvement available.

---

## Q7. What did not work in your project, and what did you learn from it?

So there were several concrete failures, and I think being honest about each one is more useful than pretending everything went smoothly the first time.

The biggest time sink was the OpenLane synthesis flow failing to parse my SystemVerilog files. I had Claude generate the RTL using SystemVerilog, which is great for simulation, but the yosys frontend in OpenLane uses a Verilog-2005 parser that chokes on unpacked array port syntax. The flow died at the header generation step with a cryptic syntax error. The fix was to maintain a parallel set of Verilog-2005 files with flat packed buses for synthesis only, keeping the SystemVerilog originals for simulation. That cost a day I did not budget for. The lesson is to port to the synthesis-compatible format before running the tool, not after.

The second problem was the OpenLane synth checker flagging two false-positive warnings as fatal errors and stopping the run. Those were address-decode bits that yosys correctly inferred as constant during optimization. Yosys's own final-check pass reported zero problems on the same design. The checker was being overly conservative. The fix was one line in the configuration file.

The third issue I am being honest about in the design justification is that the per-pixel AXI4-Lite transaction model adds several cycles of handshake overhead per pixel. The compute core can produce one result per cycle but the interface can only drive one pixel every few cycles. The production system would need a streaming feeder that reads pixel batches directly from the HBM3 memory, which is the system-level architecture I described in M1 but was out of scope for M4.

The point is every failure mode was fixable once I understood the root cause. The synthesis tool failures both had specific documented solutions. The interface limitation is a real architectural gap that I documented honestly rather than glossing over.

---

## Q8. Where does your accelerator sit on the roofline compared to the CPU baseline?

So the roofline is just a chart that shows the most performance you can possibly get for a given workload. It has two ceilings, a slanted one for memory bandwidth and a flat one for peak compute, and where your kernel lands tells you which one is holding you back.

On the CPU baseline my distance kernel sat way over on the left, deep under the slanted memory ceiling, because its arithmetic intensity was low, under 2 operations per byte. That is the memory-bound region, where the chip finishes the math long before the next batch of data even arrives.

When I moved to the near-memory accelerator, two things changed at once. The centroid reuse pushed the arithmetic intensity up by a large factor, so the working point slides to the right. And the high-bandwidth memory lifts the slanted ceiling itself, so the whole roof rises. Together that moves the kernel out from under the memory ceiling and over into the compute-bound region, where the hardware is finally the limit instead of the memory bus.

The point is the roofline did not just diagnose the problem, it gave me the target. I was trying to move the working point up and to the right, and afterward I could check that I actually got there.

**Follow-up: Does raising arithmetic intensity alone move you off the memory ceiling, or do you also need more bandwidth?**

Both matter but they do different jobs. Raising arithmetic intensity slides you right toward the ridge point, which is where the two ceilings meet. If I only raised intensity and kept the same DRAM, I would eventually hit the ridge and then the flat compute ceiling would cap me. Adding the high-bandwidth memory tilts the slanted ceiling upward so the ridge point itself moves, which lets me stay compute-bound at a much higher level of performance. So the reuse and the memory choice work together, one moves the point and the other moves the roof.

---

## Q9. Why a near-memory PIM chiplet instead of just using a faster CPU or a GPU?

So this comes back to the bottleneck being memory bandwidth, not raw compute. Once I knew that, the real question was which architecture actually attacks the memory wall instead of throwing more math at it.

A faster CPU does not help, because the limit is how fast bytes come out of DRAM and a faster core just waits faster. A GPU is genuinely better since it has much higher memory bandwidth and tons of parallel lanes, so it would speed this up. But a GPU still keeps the data in separate memory that has to be hauled across a bus to the compute, so you are still paying for that long trip, and it is a power-hungry general-purpose part doing a very narrow job.

Near-memory processing-in-memory flips that. Instead of bringing the data to the compute, you put a small specialized compute block right next to the memory stack, so the distance computation happens basically where the pixels already live and the trip almost disappears. Because the compute is purpose-built for just this one kernel, it is tiny and sips power compared to a GPU doing the same work.

It is like the difference between driving across town to a giant warehouse every time you need one screwdriver, versus keeping a small toolbox right next to your workbench.

The point is this is a domain-specific architecture decision. I gave up the flexibility of a general-purpose chip on purpose, because for this one memory-bound kernel, putting cheap specialized compute next to the data beats throwing a big expensive processor at it.

**Follow-up: What did you give up by specializing this hard?**

Flexibility. My core only computes squared distances for K-Means over RGB, and that is all it will ever do. A GPU could run my kernel today and a completely different workload tomorrow. I traded that generality for efficiency, a tiny area and a few milliwatts of power, which is the classic specialization tradeoff. For a fixed production workload that runs the same operation constantly, that trade is worth it, but it would be the wrong call if the workload kept changing.

---

## Q10. Walk me through how the host actually controls the accelerator from the software side.

So I used a simple register-based control scheme over AXI4-Lite, which is a lightweight standard interface where the host talks to the accelerator by reading and writing specific addresses, like labeled mailboxes.

The flow is straightforward. First the host writes the 16 centroid values into their registers, once per K-Means iteration, since those stay put while pixels stream through. Then for each pixel it writes the RGB value into the pixel register and pulses a start bit in the control register to kick off the computation. The accelerator goes busy, runs the pixel through the pipeline, and flips a done bit in the status register when the result is ready. The host polls that done bit, and once it is set, reads back two things, which centroid won and the squared distance to it.

I deliberately chose the lite version of AXI instead of the full one, because the full version supports burst transfers and complex transaction management that I just did not need. I am moving one small pixel and reading two small results, so the simpler protocol keeps the hardware smaller and the control logic clean.

The point is the control interface is intentionally dumb and predictable. The host sets up the data, says go, waits for done, and reads the answer, which makes the whole thing easy to verify and easy to drive from software.

**Follow-up: You feed one pixel at a time and poll for done. Isn't that a bottleneck?**

It is, and I am honest about that in my design writeup. The compute core can finish a pixel every cycle, but the per-pixel handshake of writing the pixel, pulsing start, and polling done adds several cycles of overhead, so the interface throttles a core that is actually much faster. In a real production system I would replace this with a streaming feeder that pulls batches of pixels straight from the high-bandwidth memory and pushes them into the pipeline back to back, so the core stays full. The per-pixel register model was the right scope for proving the core works, but it is not the path you would ship.

---

## Style Reminder

For every answer, follow the 4-step method:

1. Open with "So..." or "I used..." — never "This is fundamentally..."
2. Mechanism — how it works or why it matters, flowing prose with transitions
3. Concrete example — always from the K-Means project, using "I"
4. Big picture close — "The point is...", "Essentially...", "The whole point is..."

Rules:
- No dashes anywhere in spoken answers
- No specific test case values or exact chip numbers — describe principles and ratios
- Use "hardware" not "silicon"
- Spell out acronyms on first use
- Use "I" for all project work: "I profiled...", "I chose...", "I found..."
- Mix in plain-language analogies where the concept benefits from it
