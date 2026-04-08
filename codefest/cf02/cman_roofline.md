## CMAN Part 1 Calculations

Using the hardware spec from the assignment:

- Peak compute = **10 TFLOP/s = 10,000 GFLOP/s**
- Peak DRAM bandwidth = **320 GB/s**
- Ridge point = **31.25 FLOP/byte**

### Kernel A: Dense GEMM
For square matrix multiply with \( N = 1024 \):

- **GEMM FLOPs**  
  \( 2 \times 1024^3 \)  
  \( = 2 \times 1,073,741,824 \)  
  \( = 2,147,483,648 \) FLOPs

- **GEMM bytes**  
  \( 3 \text{ matrices} \times 1024^2 \text{ elements} \times 4 \text{ bytes} \)  
  \( = 3 \times 1,048,576 \times 4 \)  
  \( = 12,582,912 \) bytes

- **GEMM arithmetic intensity**  
  \( \text{AI} = \frac{\text{FLOPs}}{\text{bytes}} \)  
  \( = \frac{2,147,483,648}{12,582,912} \)  
  \( \approx 170.67 \text{ FLOP/byte} \)

- **Compare to ridge point**  
  \( 170.67 > 31.25 \)  
  So GEMM is **compute-bound**.

---

### Kernel B: Vector Addition
For vectors of length \( 4,194,304 \):

- **Vector add FLOPs**  
  \( = 4,194,304 \) FLOPs

- **Vector add bytes**  
  \( (2 \text{ reads} + 1 \text{ write}) \times 4,194,304 \times 4 \text{ bytes} \)  
  \( = 3 \times 4,194,304 \times 4 \)  
  \( = 50,331,648 \) bytes

- **Vector add arithmetic intensity**  
  \( \text{AI} = \frac{\text{FLOPs}}{\text{bytes}} \)  
  \( = \frac{4,194,304}{50,331,648} \)  
  \( \approx 0.0833 \text{ FLOP/byte} \)

- **Compare to ridge point**  
  \( 0.0833 < 31.25 \)  
  So vector addition is **memory-bound**.

---

## Quick Comparison

| Kernel | FLOPs | Bytes | AI (FLOP/byte) | Compared to Ridge Point (31.25) | Bound |
|---|---:|---:|---:|---:|---|
| Dense GEMM | 2,147,483,648 | 12,582,912 | 170.67 | Above ridge point | Compute-bound |
| Vector Add | 4,194,304 | 50,331,648 | 0.0833 | Below ridge point | Memory-bound |
