# ResNet-18 Analysis  
Bao Nguyen  
ECE 410/510 Spring 2026  

---

## Top-5 Layers by MAC Count

| Rank | Layer Name   | Layer Type | MACs        | Parameters |
|------|-------------|-----------|------------:|-----------:|
| 1    | Conv2d: 1-1 | Conv2d    | 118,013,952 | 9,408      |
| 2    | Conv2d: 3-1 | Conv2d    | 115,605,504 | 36,864     |
| 3    | Conv2d: 3-4 | Conv2d    | 115,605,504 | 36,864     |
| 4    | Conv2d: 3-7 | Conv2d    | 115,605,504 | 36,864     |
| 5    | Conv2d: 3-10| Conv2d    | 115,605,504 | 36,864     |

---

## Arithmetic Intensity — Most MAC-Intensive Layer

**Selected Layer:** Conv2d: 1-1  

**Layer Configuration:**  
- Kernel: 7 × 7  
- Input Channels: 3  
- Output Channels: 64  
- Output Size: 112 × 112  
- Precision: FP32 (4 bytes per element)  

---

### Compute

- MACs = 118,013,952  
- FLOPs = 2 × MACs = 236,027,904  

---

### Memory

**Weights:**
- Parameters = 9,408  
- Weight Memory = 9,408 × 4 = 37,632 bytes  

**Input Activations:**
- Size = 3 × 224 × 224  
- Bytes = 602,112  

**Output Activations:**
- Size = 64 × 112 × 112  
- Bytes = 3,211,264  

**Total Activation Memory:**
- 602,112 + 3,211,264 = 3,813,376 bytes  

**Total Memory Traffic:**
- 37,632 + 3,813,376 = 3,851,008 bytes  

---

### Arithmetic Intensity

\[
AI = \frac{\text{FLOPs}}{\text{Total Bytes}} = \frac{236,027,904}{3,851,008} \approx 61.29 \ \text{FLOP/byte}
\]

---

### Interpretation

This layer has moderate arithmetic intensity (~61 FLOP/byte). Under the no-reuse assumption, it is likely memory-bandwidth bound on modern hardware. In practice, data reuse (tiling and caching) can increase effective arithmetic intensity and shift execution toward the compute-bound regime.
