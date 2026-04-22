# Codefest Presentation — K-Means Image Color Quantization Accelerator
Bao Nguyen | ECE 410/510 | Spring 2026

---

## What am I doing?
- Custom chip that reduces any photo to 16 colors by grouping similar pixels

## How is it done today?
- Runs on CPU — ~9 sec/image, using less than 1% of CPU computing power
- Bottleneck is memory: CPU spends most of its time waiting for data, not doing math (46% of runtime)

## What am I doing differently?
- Memory and math units sit right next to each other — no waiting (near-memory PIM chiplet)
- 16 TB/s internal bandwidth vs CPU → **~62× projected speedup**

## What have I accomplished so far?
- Benchmarked CPU baseline and confirmed memory is the bottleneck
- Wrote and tested all hardware in simulation — distance engine, AXI4-Lite interface, and compute core — all passing testbenches

## What's next?
- Connect all pieces into a full system
- Verify timing, measure throughput, compare against the 9-second baseline → declare success

---

## Visuals (for slide)
- `codefest/cf02/profiling/roofline_project.png` — roofline: CPU vs PIM accelerator
- `bliss_before_after.png` — Bliss photo before and after K-Means (K=16 colors)
- `project/m1/system_diagram.png` — system architecture (CPU → UCIe → PIM chiplet)
