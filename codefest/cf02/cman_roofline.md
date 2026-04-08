## CMAN Part 1 Calculations

Using the hardware spec from the assignment:

- Peak compute = 10 TFLOP/s = 10,000 GFLOP/s  
- Peak DRAM bandwidth = 320 GB/s  
- Ridge point = 31.25 FLOP/byte  

---

### Kernel A: Dense GEMM

For square matrix multiply (N = 1024):

- GEMM FLOPs  
  = 2 × 1024^3  
  = 2 × 1,073,741,824  
  = 2,147,483,648 FLOPs  

- GEMM bytes  
  = 3 matrices × 1024^2 elements × 4 bytes  
  = 3 × 1,048,576 × 4  
  = 12,582,912 bytes  

- Arithmetic Intensity (AI)  
  = FLOPs / bytes  
  = 2,147,483,648 / 12,582,912  
  ≈ 170.67 FLOP/byte  

- Compare to ridge point  
  170.67 > 31.25  
  → GEMM is compute-bound  

---

### Kernel B: Vector Addition

For vector length = 4,194,304:

- Vector add FLOPs  
  = 4,194,304 FLOPs  

- Vector add bytes  
  = (2 reads + 1 write) × 4,194,304 × 4 bytes  
  = 3 × 4,194,304 × 4  
  = 50,331,648 bytes  

- Arithmetic Intensity (AI)  
  = FLOPs / bytes  
  = 4,194,304 / 50,331,648  
  ≈ 0.0833 FLOP/byte  

- Compare to ridge point  
  0.0833 < 31.25  
  → Vector add is memory-bound  

---

## Summary

| Kernel        | FLOPs          | Bytes        | AI (FLOP/byte) | Bound          |
|--------------|----------------|--------------|----------------|----------------|
| GEMM         | 2,147,483,648  | 12,582,912   | 170.67         | Compute-bound  |
| Vector Add   | 4,194,304      | 50,331,648   | 0.0833         | Memory-bound   |
