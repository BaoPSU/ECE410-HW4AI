# Interface Selection — K-Means Image Color Quantization Accelerator
Bao Nguyen  
ECE 410/510 Spring 2026

---

## Host Platform

**Host:** Intel Core i9-12900H laptop CPU (x86-64, Ubuntu 24.04)  
**Accelerator:** Near-memory PIM chiplet with HBM3 (8 TFLOP/s FP32, 16 TB/s on-chip bandwidth)  
**Integration:** Chiplet-to-host interface using advanced packaging

---

## Selected Interface: UCIe (Universal Chiplet Interconnect Express)

UCIe is selected from the allowed interface options (SPI, I²C, AXI4-Lite, AXI4 Stream, PCIe, UCIe).

**Rated bandwidth:** UCIe Advanced Packaging — up to **2.56 TB/s** per die-to-die link  
**Source:** UCIe 1.1 specification, UCIe Consortium (2023)

UCIe is chosen because it is designed specifically for chiplet-to-chiplet communication in advanced packaging (2.5D/3D integration), which is the assumed physical integration for a near-memory PIM accelerator co-packaged with HBM3.

---

## Bandwidth Requirement Calculation

The accelerator processes one image (800×600 = 480,000 pixels) per K-Means invocation.  
Data transferred per image over the host-to-accelerator interface:

| Transfer | Size |
|----------|------|
| Input pixels (480,000 × 3 × 4 bytes float32) | 5,760,000 bytes = 5.76 MB |
| Input centroids (16 × 3 × 4 bytes, initial) | 192 bytes |
| Output labels (480,000 × 4 bytes int32) | 1,920,000 bytes = 1.92 MB |
| **Total per image** | **7,680,192 bytes ≈ 7.68 MB** |

At the target accelerator throughput of 8 TFLOP/s, the full K-Means computation (20 iterations × 61,440,000 FLOPs) completes in:

```
time = (20 × 61,440,000) / (8 × 10^12) = 153.6 μs per image
```

Required interface bandwidth:

```
BW_required = 7,680,192 bytes / 153.6 μs ≈ 50 GB/s
```

---

## Bottleneck Status

| Interface | Rated Bandwidth | Required | Interface-Bound? |
|-----------|----------------|----------|-----------------|
| SPI | ~0.05 GB/s | 50 GB/s | ❌ Yes — severely |
| I²C | ~0.0004 GB/s | 50 GB/s | ❌ Yes — severely |
| AXI4-Lite | ~1 GB/s | 50 GB/s | ❌ Yes |
| AXI4 Stream | ~32 GB/s | 50 GB/s | ❌ Yes — marginal |
| PCIe 5.0 x16 | 64 GB/s | 50 GB/s | ✅ No — adequate |
| **UCIe Advanced** | **2,560 GB/s** | **50 GB/s** | **✅ No — 51× headroom** |

**The design is NOT interface-bound with UCIe.** The 2.56 TB/s rated bandwidth provides 51× more headroom than the 50 GB/s required. The bottleneck remains on-chip compute and HBM3 bandwidth, not the host interface.

Note: PCIe 5.0 x16 would technically suffice, but UCIe is preferred for chiplet integration as it avoids the PCIe PHY overhead and supports die-to-die distances below 1 mm with much lower latency.
