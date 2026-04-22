# Manual INT8 Symmetric Quantization: Full Step-by-Step Assignment

This report includes the original questions, formal equations, every 4x4 matrix, and the exhaustive hand-calculations for every single element.

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
1.  **Identify max absolute value:** Compare all $|w_{i,j}|$. The largest is $|-2.31| = 2.31$.
2.  **Equation:** $S = \frac{\max(|W|)}{127}$
3.  **Math:** $2.31 / 127 = 0.018188976...$
4.  **Result:** **S = 0.018189**

---

## Task 2: Quantize
**Question:** Quantize each element: $W_q = \text{round}(W / S)$. Clamp to $[-128, 127]$. Write out the full 4×4 INT8 matrix.

**Equation:** $W_q = \text{clamp}(\text{round}(W / S), -128, 127)$

**Step-by-Step Calculations Table:**
| Element | Weight ($W$) | $W \div 0.018189$ | Rounding Step | **INT8 ($W_q$)** |
| :--- | :--- | :--- | :--- | :--- |
| R1, C1 | 0.85 | 46.73 | 46.7 $\rightarrow$ 47 | **47** |
| R1, C2 | -1.20 | -65.97 | -66.0 $\rightarrow$ -66 | **-66** |
| R1, C3 | 0.34 | 18.69 | 18.7 $\rightarrow$ 19 | **19** |
| R1, C4 | 2.10 | 115.45 | 115.5 $\rightarrow$ 115 | **115** |
| R2, C1 | -0.07 | -3.85 | -3.9 $\rightarrow$ -4 | **-4** |
| R2, C2 | 0.91 | 50.03 | 50.0 $\rightarrow$ 50 | **50** |
| R2, C3 | -1.88 | -103.36 | -103.4 $\rightarrow$ -103 | **-103** |
| R2, C4 | 0.12 | 6.60 | 6.6 $\rightarrow$ 7 | **7** |
| R3, C1 | 1.55 | 85.22 | 85.2 $\rightarrow$ 85 | **85** |
| R3, C2 | 0.03 | 1.65 | 1.7 $\rightarrow$ 2 | **2** |
| R3, C3 | -0.44 | -24.19 | -24.2 $\rightarrow$ -24 | **-24** |
| R3, C4 | -2.31 | -127.00 | -127.0 $\rightarrow$ -127 | **-127** |
| R4, C1 | -0.18 | -9.90 | -9.9 $\rightarrow$ -10 | **-10** |
| R4, C2 | 1.03 | 56.63 | 56.6 $\rightarrow$ 57 | **57** |
| R4, C3 | 0.77 | 42.33 | 42.3 $\rightarrow$ 42 | **42** |
| R4, C4 | 0.55 | 30.24 | 30.2 $\rightarrow$ 30 | **30** |

**Full 4x4 INT8 Matrix ($W_q$):**
| 47 | -66 | 19 | 115 |
| :---: | :---: | :---: | :---: |
| -4 | 50 | -103 | 7 |
| 85 | 2 | -24 | -127 |
| -10 | 57 | 42 | 30 |

---

## Task 3: Dequantize
**Question:** Compute $W_{deq} = W_q \times S$. Write out the 4×4 FP32 dequantized matrix.

**Equation:** $W_{deq} = W_q \times S$

**Hand Calculation Table:**
| INT8 ($W_q$) | $\times 0.018189$ | **Dequantized ($W_{deq}$)** |
| :--- | :--- | :--- |
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

**Full 4x4 Dequantized Matrix ($W_{deq}$):**
| 0.8549 | -1.2005 | 0.3456 | 2.0917 |
| :---: | :---: | :---: | :---: |
| -0.0728 | 0.9095 | -1.8735 | 0.1273 |
| 1.5461 | 0.0364 | -0.4365 | -2.3100 |
| -0.1819 | 1.0368 | 0.7639 | 0.5457 |

---

## Task 4: Error Analysis
**Question:** Compute the per-element absolute error $|W − W_{deq}|$. Identify the element with the largest error and compute the Mean Absolute Error (MAE).

**Equation:** $|W - W_{deq}|$

**Per-Element Absolute Error Matrix:**
| 0.0049 | 0.0005 | 0.0056 | **0.0083** |
| :---: | :---: | :---: | :---: |
| 0.0028 | 0.0005 | 0.0065 | 0.0073 |
| 0.0039 | 0.0064 | 0.0035 | 0.0000 |
| 0.0019 | 0.0068 | 0.0061 | 0.0043 |

**Hand-Sum Calculation:**
$0.0049 + 0.0005 + 0.0056 + 0.0083 + 0.0028 + 0.0005 + 0.0065 + 0.0073 + 0.0039 + 0.0064 + 0.0035 + 0.0000 + 0.0019 + 0.0068 + 0.0061 + 0.0043 = 0.0693$

- **Largest Error:** **0.0083** (at Row 1, Col 4)
- **Mean Absolute Error (MAE):** $0.0693 / 16 = \mathbf{0.0043}$

---

## Task 5: Bad Scale Experiment
**Question:** Use $S_{bad} = 0.01$ (too small). Repeat quantization and dequantization. Compute the MAE. Explain in one sentence what goes wrong when $S$ is too small.

**Calculation for Clipping:**
- $W = 2.10 \rightarrow 2.10 / 0.01 = 210 \rightarrow$ **Clamped to 127**
- $W = -1.88 \rightarrow -1.88 / 0.01 = -188 \rightarrow$ **Clamped to -128**
- $W = 1.55 \rightarrow 1.55 / 0.01 = 155 \rightarrow$ **Clamped to 127**
- $W = -2.31 \rightarrow -2.31 / 0.01 = -231 \rightarrow$ **Clamped to -128**

**Full 4x4 Dequantized Matrix ($S=0.01$):**
| 0.85 | -1.20 | 0.34 | **1.27** |
| :---: | :---: | :---: | :---: |
| -0.07 | 0.91 | **-1.28** | 0.12 |
| **1.27** | 0.03 | -0.44 | **-1.28** |
| -0.18 | 1.03 | 0.77 | 0.55 |

- **MAE (Bad Scale):** **0.1713**

**Explanation:**
When $S$ is too small, large-magnitude weights exceed INT8's $[-128, 127]$ range and get hard-clamped, introducing severe clipping error that cannot be recovered during dequantization.
