# Presentation 1 — Speaker Notes
K-Means Image Color Quantization Accelerator  
Bao Nguyen | ECE 410/510 | Spring 2026  
Duration: ~1 minute

---

**What am I doing?**
"I'm building a custom chip that takes any photo and compresses it down to just 16 colors — by grouping similar pixels together. Think of the Bliss photo on the right — that's the original, and that's what it looks like with only 16 colors."

**How is it done today?**
"Right now this runs on a regular CPU and takes about 9 seconds per image — but the CPU is barely doing any work. Less than 1% of its computing power is being used. The bottleneck is memory — the CPU spends almost half its time just waiting for data to load."

**What am I doing differently?**
"Instead of a CPU, I'm designing a chip where the memory and the math units sit right next to each other — so there's no waiting. You can see that in the roofline plot — on the CPU the kernel sits way down in the memory-bound zone, but on my accelerator it flips to compute-bound. That's where the 62× speedup comes from."

**What have I done so far?**
"I've measured the CPU baseline, confirmed where the bottleneck is, and written all the hardware — the distance engine, the memory interface, and the compute core — all passing simulation."

**What's next?**
"I need to connect all the pieces into a full system, verify timing, and then measure actual throughput to prove the speedup is real."

---

> Tip: Linger on the Bliss before/after when you first show it — it's your best visual hook.
