# Manual INT8 Symmetric Quantization: Full Assignment Report

This report contains the original questions, formal equations, and a complete hand-calculated breakdown of every task.

---

## Task 1: Scale Factor
**Question:** Compute $S$ using symmetric per-tensor quantization: $S = \max(|W|) / 127$. Show the max value and the computed $S$.

**Original Weight Matrix W (FP32):**
| | Col 1 | Col 2 | Col 3 | Col 4 |
| :--- | :---: | :---: | :---: | :---: |
| **Row 1** | 0.85 | -1.20 | 0.34 | 2.10 |
| **Row 2** | -0.07 | 0.91 | -1.88 | 0.12 |
| **Row 3** | 1.55 | 0.03 | -0.44 | -2.31 |
| **Row 4** | -0.18 | 1.03 | 0.77 | 0.55 |

**Hand Calculation:**
- **Step 1:** Identify max absolute value. $|-2.31| = 2.31$.
- **Equation:** $$S = \frac{\max(|W|)}{127}$$
- **Step 2:** $2.31 / 127 = 0.018188976...$
- **Result:** **S = 0.018189**

---

## Task 2: Quantize
**Question:** Quantize each element: $W_q = \text{round}(W / S)$. Clamp to $[-128, 127]$. Write out the full 4×4 INT8 matrix.

**Equation:** $$W_q = \text{clamp}(\text{round}(W / S), -128, 127)$$

**Step-by-Step Table:**
| Weight ($W$) | $\div S$ (Calc) | Rounding | **INT8 ($W_q$)** |
| :--- | :--- | :--- | :--- |
| 0.85 | 46.73 | 47 | **47** |
| -1.20 | -65.97 | -66 | **-66** |
| 0.34 | 18.69 | 19 | **19** |
| 2.10 | 115.45 | 115 | **115** |
| -0.07 | -3.85 | -4 | **-4** |
| 0.91 | 50.03 | 50 | **50** |
| -1.88 | -103.36 | -103 | **-103** |
| 0.12 | 6.60 | 7 | **7** |
| 1.55 | 85.22 | 85 | **85** |
| 0.03 | 1.65 | 2 | **2** |
| -0.44 | -24.19 | -24 | **-24** |
| -2.31 | -127.00 | -127 | **-127** |
| -0.18 | -9.90 | -10 | **-10** |
| 1.03 | 56.63 | 57 | **57** |
| 0.77 | 42.33 | 42 | **42** |
| 0.55 | 30.24 | 30 | **30** |

---

## Task 3: Dequantize
**Question:** Compute $W_{deq} = W_q \times S$. Write out the 4×4 FP32 dequantized matrix.

**Equation:** $$W_{deq} = W_q \times S$$

**Hand Calculation Table:**
| INT8 ($W_q$) | $\times 0.018189$ | **Dequantized ($W_{deq}$)** |
| :---: | :---: | :---: |
| 47 | $47 \times S$ | **0.8549** |
| -66 | $-66 \times S$ | **-1.2005** |
| 19 | $19 \times S$ | **0.3456** |
| 115 | $115 \times S$ | **2.0917** |
| -4 | $-4 \times S$ | **-0.0728** |
| 50 | $50 \times S$ | **0.9095** |
| -103 | $-103 \times S$ | **-1.8735** |
| 7 | $7 \times S$ | **0.1273** |
| 85 | $85 \times S$ | **1.5461** |
| 2 | $2 \times S$ | **0.0364** |
| -24 | $-24 \times S$ | **-0.4365** |
| -127 | $-127 \times S$ | **-2.3100** |
| -10 | $-10 \times S$ | **-0.1819** |
| 57 | $57 \times S$ | **1.0368** |
| 42 | $42 \times S$ | **0.7639** |
| 30 | $30 \times S$ | **0.5457** |

---

## Task 4: Error Analysis
**Question:** Compute the per-element absolute error $|W − W_{deq}|$. Identify the element with the largest error and compute the Mean Absolute Error (MAE) across all 16 elements.

**Equations:**
- $\text{Per-element error} = |W - W_{deq}|$
- $\text{MAE} = \text{average of all 16 absolute errors}$

**Results:**
- **Largest Error:** **0.0083** (at Row 1, Col 4)
- **Total Absolute Error Sum:** 0.0692
- **MAE:** $0.0692 / 16 = \mathbf{0.0043}$

---

## Task 5: Bad Scale Experiment
**Question:** Use $S_{bad} = 0.01$ (too small). Repeat quantization and dequantization. Compute the MAE. Explain in one sentence what goes wrong when $S$ is too small.

**Hand Calculation ($S = 0.01$):**
- **Clipping Check:** For $W = 2.10$, $2.10 / 0.01 = 210$. Since $210 > 127$, $W_q$ is clamped to **127**.
- **MAE Calculation:** The sum of errors jumps to **2.74**.
- **Final MAE:** **0.1713** (roughly 40x higher than Task 4).

**Explanation:**
When $S$ is too small, large-magnitude weights exceed INT8's $[-128, 127]$ range and get hard-clamped, introducing severe clipping error that cannot be recovered during dequantization.
