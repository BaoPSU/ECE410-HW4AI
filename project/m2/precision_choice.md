# Precision Choice — K-Means Distance Engine
Bao Nguyen  
ECE 410/510 Spring 2026

---

## Selected Precision: float32 (IEEE 754 single-precision)

---

## Justification

The dominant kernel computes squared Euclidean distances over RGB pixel values:

```
dist[k] = Σ_d ( pixel[d] − centroid[d] )²      d ∈ {R, G, B}
```

Pixel channel values are integers in [0, 255]. The maximum possible squared distance
per dimension is 255² = 65,025. Summing over D = 3 dimensions:

```
dist_max = 3 × 65,025 = 195,075
```

---

## Float32 Exact-Integer Coverage

IEEE 754 float32 has a 23-bit mantissa, giving exact representation of all integers up to:

```
2^24 = 16,777,216
```

Since dist_max = 195,075 ≪ 16,777,216, **every possible squared distance for 8-bit
RGB pixels is representable exactly as a float32 integer.**  
There is zero rounding error in the distance computation.

---

## Quantization Error Analysis

| Step | Value range | Float32 exact? |
|------|------------|----------------|
| `pixel[d]` | 0 – 255 | ✓ (fits in 8 bits) |
| `centroid[d]` | 0.0 – 255.0 | ✓ |
| `diff = pixel − centroid` | −255 – 255 | ✓ |
| `diff²` | 0 – 65,025 | ✓ (< 2²⁴) |
| `dist = Σ diff²` | 0 – 195,075 | ✓ (< 2²⁴) |
| Argmin comparison | — | ✓ (exact integers always ordered correctly) |

**Quantization error: 0 for integer pixel inputs.**

---

## Comparison with Alternative Formats

| Format | Mantissa bits | Max exact int | Sufficient? | Notes |
|--------|--------------|---------------|-------------|-------|
| INT8   | —            | 127           | ✗ | Overflow on diff², cannot hold distances |
| INT16  | —            | 32,767        | ✗ | dist_max = 195,075 > 32,767; overflow |
| BF16   | 7            | 256           | ✗ | Resolution too coarse; wrong assignments |
| FP16   | 10           | 2,048         | ✗ | dist_max = 195,075 > 2,048; inexact |
| **FP32** | **23**   | **16,777,216**| **✓** | **Zero error; chosen format** |
| FP64   | 52           | 2^53          | ✓ | Exact but wastes bandwidth; FP32 sufficient |

**INT8 / INT16 / BF16 / FP16 all produce rounding or overflow errors that would cause
incorrect centroid assignments for typical RGB images. Float64 is unnecessarily wide.**

---

## Hardware Cost Justification

Float32 arithmetic units are standard in modern ASIC and FPGA designs (e.g., Xilinx
DSP48E2, Intel hardened FP). For the K-Means accelerator:

- **3 FP32 subtractors + 3 FP32 multipliers** per dimension lane (D = 3 lanes)
- **3-input FP32 adder tree** per centroid (accumulates 3 squares)
- **K = 16** such compute units in parallel → 48 FP32 sub/mul + 16 adder trees total
- Area is dominated by the adder trees; FP32 vs FP16 difference is ~2× for adders,
  acceptable given the correctness guarantee

Using FP16 would save area but require an analysis of worst-case rounding propagation
across 10 iterations of centroid update — complexity not justified when FP32 gives
exact results with no additional design risk.

---

## Conclusion

Float32 is the optimal precision for this application: it provides **mathematically exact
arithmetic for integer pixel inputs**, maps directly to standard synthesizable FP32 units,
and avoids the bandwidth overhead of float64. The precision choice is fully validated by
the simulation testbench in `tb/distance_engine_tb.sv`.
