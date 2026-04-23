# Presentation 1 — Speaker Notes
K-Means Image Color Quantization Accelerator  
Bao Nguyen | ECE 410/510 | Spring 2026  
Duration: ~1 minute

---

**What am I doing?**
"I'm building a custom chip that takes any photo and compresses it down to just 16 colors — by grouping similar pixels together. Think of the Bliss photo on the right — that's the original, and that's what it looks like with only 16 colors."

**How is it done today?**
"Right now this runs on a regular CPU — scikit-learn with OpenBLAS — and takes about 9 seconds per image, using less than 1% of its computing power. GPUs like NVIDIA with CUDA or cuML can do it faster, but they're general-purpose, not built for K-Means. There are FPGA designs too, like on AMD Artix-7, but those are rigid and device-specific. And there's no dedicated near-memory chiplet for K-Means image quantization with HBM3 and UCIe — that's the gap I'm filling."

**What am I doing differently?**
"Instead of a CPU, I'm designing a chip where the memory and the math units sit right next to each other — so there's no waiting. You can see that in the roofline plot — on the CPU the kernel sits way down in the memory-bound zone, but on my accelerator it flips to compute-bound. That's where the 62× speedup comes from."

**What have I done so far?**
"I've measured the CPU baseline, confirmed where the bottleneck is, and written the key hardware — the distance engine and AXI4-Lite control interface are both passing simulation, and UCIe is selected as the host interface to the chiplet."

**What's next?**
"I need to connect all the pieces into a full system, verify timing, and then measure actual throughput to prove the speedup is real."

---

> Tip: Linger on the Bliss before/after when you first show it — it's your best visual hook.

---

## Definitions

**PIM (Processing-In-Memory)** — a chip design where the compute units are placed physically next to the memory, instead of the usual CPU→bus→RAM setup. Normally the CPU fetches pixel data across a slow memory bus, does a tiny bit of math, then waits for more data — that's why K-Means is memory-bound on CPU (46% of runtime is just waiting). With a PIM chiplet, the distance math (subtract, square, accumulate) happens right where the pixels already live in HBM3 memory. No bus trip, no waiting. That's where the 16 TB/s bandwidth and the 62× speedup come from. In the diagram it's the pink dashed box — the Compute Engine and On-Chip Memory are co-located on the same chiplet, connected to the CPU via UCIe.
