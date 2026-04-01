# Codefest 1 – CF01 CMAN Workload Accounting  
**Name:** Bao Nguyen  

---

## (a) Per-Layer MACs

Formula:  
\[
\text{MACs} = \text{input size} \times \text{output size}
\]

| Layer        | Calculation        | MACs   |
|-------------|------------------|--------|
| Layer 1     | 784 × 256        | 200,704 |
| Layer 2     | 256 × 128        | 32,768  |
| Layer 3     | 128 × 10         | 1,280   |

---

## (b) Total MACs

\[
200,704 + 32,768 + 1,280 = 234,752
\]

**Total MACs = 234,752**

---

## (c) Total Parameters (Weights Only)

Same as MACs for fully connected layers:

\[
200,704 + 32,768 + 1,280 = 234,752
\]

**Total Parameters = 234,752**

---

## (d) Weight Memory (FP32)

Each weight = 4 bytes

\[
234,752 \times 4 = 939,008 \text{ bytes}
\]

**Weight Memory = 939,008 bytes**

---

## (e) Activation Memory (FP32)

Total activations stored simultaneously:

\[
784 + 256 + 128 + 10 = 1,178
\]

\[
1,178 \times 4 = 4,712 \text{ bytes}
\]

**Activation Memory = 4,712 bytes**

---

## (f) Arithmetic Intensity

Formula:

\[
\frac{2 \times \text{Total MACs}}{\text{Weight Memory} + \text{Activation Memory}}
\]

\[
\frac{2 \times 234,752}{939,008 + 4,712} = 0.4975
\]

**Arithmetic Intensity ≈ 0.4975 FLOP/byte**

---
