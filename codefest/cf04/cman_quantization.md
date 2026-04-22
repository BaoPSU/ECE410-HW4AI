# Manual INT8 Symmetric Quantization: Full Assignment Report

This report contains the original questions, formal equations, and complete 4x4 matrices for every stage of the process.

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

**Calculation:**
- **Max Absolute Value:** $|-2.31| = 2.31$
- **Equation:** $S = \frac{2.31}{127}$
- **Result:** **S = 0.018189**

---

## Task 2: Quantize
**Question:** Quantize each element: $W_q = \text{round}(W / S)$. Clamp to $[-128, 127]$. Write out the full 4×4 INT8 matrix.

**Equation:** $W_q = \text{clamp}(\text{round}(W / S), -128, 127)$

**Full 4x4 INT8 Matrix ($W_q$):**
| | Col 1 | Col 2 | Col 3 | Col 4 |
| :--- | :---: | :---: | :---: | :---: |
| **Row 1** | 47 | -66 | 19 | 115 |
| **Row 2** | -4 | 50 | -103 | 7 |
| **Row 3** | 85 | 2 | -24 | -127 |
| **Row 4** | -10 | 57 | 42 | 30 |

---

## Task 3: Dequantize
**Question:** Compute $W_{deq} = W_q \times S$. Write out the 4×4 FP32 dequantized matrix.

**Equation:** $W_{deq} = W_q \times S$

**Full 4x4 FP32 Dequantized Matrix ($W_{deq}$):**
| | Col 1 | Col 2 | Col 3 | Col 4 |
| :--- | :---: | :---: | :---: | :---: |
| **Row 1** | 0.8549 | -1.2005 | 0.3456 | 2.0917 |
| **Row 2** | -0.0728 | 0.9095 | -1.8735 | 0.1273 |
| **Row 3** | 1.5461 | 0.0364 | -0.4365 | -2.3100 |
| **Row 4** | -0.1819 | 1.0368 | 0.7639 | 0.5457 |

---

## Task 4: Error Analysis
**Question:** Compute the per-element absolute error $|W − W_{deq}|$. Identify the element with the largest error and compute the Mean Absolute Error (MAE).

**Per-Element Absolute Error Matrix:**
| | Col 1 | Col 2 | Col 3 | Col 4 |
| :--- | :---: | :---: | :---: | :---: |
| **Row 1** | 0.0049 | 0.0005 | 0.0056 | **0.0083** |
| **Row 2** | 0.0028 | 0.0005 | 0.0065 | 0.0073 |
| **Row 3** | 0.0039 | 0.0064 | 0.0035 | 0.0000 |
| **Row 4** | 0.0019 | 0.0068 | 0.0061 | 0.0043 |

- **Largest Error:** **0.0083** (at Row 1, Col 4)
- **MAE:** **0.0043**

---

## Task 5: Bad Scale Experiment
**Question:** Use $S_{bad} = 0.01$ (too small). Repeat quantization and dequantization. Compute the MAE. Explain in one sentence what goes wrong when $S$ is too small.

**Full 4x4 INT8 Matrix (Bad Scale $W_q$):**
| | Col 1 | Col 2 | Col 3 | Col 4 |
| :--- | :---: | :---: | :---: | :---: |
| **Row 1** | 85 | -120 | 34 | **127** |
| **Row 2** | -7 | 91 | **-128** | 12 |
| **Row 3** | **127** | 3 | -44 | **-128** |
| **Row 4** | -18 | 103 | 77 | 55 |

**Full 4x4 FP32 Dequantized Matrix (Bad Scale $W_{deq}$):**
| | Col 1 | Col 2 | Col 3 | Col 4 |
| :--- | :---: | :---: | :---: | :---: |
| **Row 1** | 0.85 | -1.20 | 0.34 | **1.27** |
| **Row 2** | -0.07 | 0.91 | **-1.28** | 0.12 |
| **Row 3** | **1.27** | 0.03 | -0.44 | **-1.28** |
| **Row 4** | -0.18 | 1.03 | 0.77 | 0.55 |

- **MAE (Bad Scale):** **0.1713**

**Explanation:**
When $S$ is too small, large-magnitude weights exceed INT8's $[-128, 127]$ range and get hard-clamped, introducing severe clipping error that cannot be recovered during dequantization.
