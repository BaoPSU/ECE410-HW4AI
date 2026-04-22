# Manual INT8 Symmetric Quantization Assignment

## Original Matrix W (FP32)
```
[  0.85, -1.20,  0.34,  2.10 ]
[ -0.07,  0.91, -1.88,  0.12 ]
[  1.55,  0.03, -0.44, -2.31 ]
[ -0.18,  1.03,  0.77,  0.55 ]
```

---

## Task 1: Scale Factor
**Question:** Compute $S$ using symmetric per-tensor quantization: $S = 	ext{max}(|W|) / 127$. Show the max value and the computed $S$.

**Hand Calculation:**
1. Identify all absolute values: $\{0.85, 1.20, 0.34, 2.10, 0.07, 0.91, 1.88, 0.12, 1.55, 0.03, 0.44, 2.31, 0.18, 1.03, 0.77, 0.55\}$
2. **Max Absolute Value:** $2.31$ (Row 3, Col 4)
3. **Scale Factor Calculation:** $S = 2.31 / 127 = 0.018188976...$
4. **Final S:** **0.018189**

---

## Task 2: Quantize
**Question:** Quantize each element: $W_q = 	ext{round}(W / S)$. Clamp to $[-128, 127]$. Write out the full 4×4 INT8 matrix.

**Original Equation:** $W_q = 	ext{clamp}(	ext{round}(W / S), -128, 127)$

**Full 4x4 INT8 Matrix ($W_q$):**
| | Col 1 | Col 2 | Col 3 | Col 4 |
| :--- | :---: | :---: | :---: | :---: |
| **Row 1** | 47 | -66 | 19 | 115 |
| **Row 2** | -4 | 50 | -103 | 7 |
| **Row 3** | 85 | 2 | -24 | -127 |
| **Row 4** | -10 | 57 | 42 | 30 |

*Verification:*
- R1C1: $	ext{round}(0.85 / 0.018189) = 	ext{round}(46.73) = 47$
- R3C4: $	ext{round}(-2.31 / 0.018189) = 	ext{round}(-127.00) = -127$

---

## Task 3: Dequantize
**Question:** Compute $W_{deq} = W_q 	imes S$. Write out the 4×4 FP32 dequantized matrix.

**Original Equation:** $W_{deq} = W_q 	imes S$

**Full 4x4 FP32 Matrix ($W_{deq}$):**
| | Col 1 | Col 2 | Col 3 | Col 4 |
| :--- | :---: | :---: | :---: | :---: |
| **Row 1** | 0.8549 | -1.2005 | 0.3456 | 2.0917 |
| **Row 2** | -0.0728 | 0.9095 | -1.8735 | 0.1273 |
| **Row 3** | 1.5461 | 0.0364 | -0.4365 | -2.3100 |
| **Row 4** | -0.1819 | 1.0368 | 0.7639 | 0.5457 |

---

## Task 4: Error Analysis
**Question:** Compute the per-element absolute error $|W − W_{deq}|$. Identify the element with the largest error and compute the Mean Absolute Error (MAE).

**Original Equations:**
- $	ext{Error} = |W - W_{deq}|$
- $	ext{MAE} = rac{1}{n} \sum |W - W_{deq}|$

**Analysis:**
- **Largest Error:** $0.0083$ at $W[0][3]$ (Original $2.10$ vs Dequantized $2.0917$)
- **Sum of Absolute Errors:** $0.0692$
- **MAE:** $0.0692 / 16 = \mathbf{0.0043}$

---

## Task 5: Bad Scale Experiment
**Question:** Use $S_{bad} = 0.01$ (too small). Repeat quantization and dequantization. Compute the MAE. Explain in one sentence what goes wrong when $S$ is too small.

**Hand Calculation ($S = 0.01$):**
1. **Quantization with Clipping:**
   - $2.10 / 0.01 = 210 
ightarrow$ **Clamped to 127**
   - $-1.88 / 0.01 = -188 
ightarrow$ **Clamped to -128**
   - $1.55 / 0.01 = 155 
ightarrow$ **Clamped to 127**
   - $-2.31 / 0.01 = -231 
ightarrow$ **Clamped to -128**
2. **MAE Calculation:** Errors at clipped positions are massive (e.g., $|2.10 - 1.27| = 0.83$).
3. **MAE_bad:** **0.1713**

**Explanation:**
When $S$ is too small, large-magnitude weights exceed INT8's $[-128, 127]$ range and get hard-clamped, introducing severe clipping error that cannot be recovered during dequantization.
