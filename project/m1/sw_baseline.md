# Software Baseline Benchmark — K-Means Image Color Quantization
Bao Nguyen  
ECE 410/510 Spring 2026

---

## Platform and Configuration

| Parameter | Value |
|-----------|-------|
| CPU | Intel Core i9-12900H (6 P-cores + 8 E-cores, up to 5.0 GHz) |
| RAM | 16 GB DDR5-4800 |
| OS | Ubuntu 24.04.3 LTS (Linux 6.17.0-20-generic) |
| Python | 3.12.3 |
| NumPy | 2.4.4 |
| Input image | bliss.jpg resized to 800×600 (N = 480,000 pixels) |
| K (clusters) | 16 |
| max_iters | 20 |
| Precision | float32 |
| Batch size | 1 image per run |

---

## Execution Time (Wall-Clock, 10 Runs)

| Run | Time (s) |
|-----|----------|
| 1 | 8.798 |
| 2 | 8.528 |
| 3 | 8.508 |
| 4 | 8.872 |
| 5 | 9.057 |
| 6 | 8.751 |
| 7 | 9.098 |
| 8 | 8.737 |
| 9 | 8.848 |
| 10 | 8.888 |

| Metric | Value |
|--------|-------|
| **Median** | **8.848 s** |
| Mean | 8.808 s |
| Min | 8.508 s |

---

## Throughput

| Metric | Value |
|--------|-------|
| Pixels per second | 54,251 pixels/sec |
| Compute throughput | 0.16 GFLOP/s |

Throughput computed as: N pixels / median wall-clock time.  
Compute throughput: (3 ops × N × K × D × max_iters) / median_time / 1e9  
= (3 × 480,000 × 16 × 3 × 20) / 8.848 / 1e9 = 0.16 GFLOP/s

---

## Memory Usage

| Metric | Value |
|--------|-------|
| Peak RSS (tracemalloc) | 161.3 MB |

Breakdown: input pixel array (5.76 MB) + distance matrix N×K float32 (30.72 MB) + labels array (1.92 MB) + centroid arrays + Python overhead.

---

## Reproducibility

To reproduce this benchmark:
```bash
cd /home/bao/kmeans_project
source venv/bin/activate
python3 sw_baseline.py
```

The dominant bottleneck is the pairwise distance computation, which accounts for **46% of total runtime** (from cProfile). The 0.16 GFLOP/s achieved throughput is only **0.011%** of the CPU's theoretical 1,400 GFLOP/s peak — confirming deep memory-bound behavior.
