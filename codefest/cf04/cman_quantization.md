# Manual INT8 Symmetric Quantization Analysis

This document outlines the step-by-step process of symmetric quantization, dequantization, and error analysis for a 4x4 weight matrix.

## Task 1: Scale Factor Calculation
To find the optimal scale factor $S$ for symmetric quantization, we identify the maximum absolute value in the weight matrix $W$ and divide it by the maximum range of a signed 8-bit integer ($127$).

* **Max Absolute Value:** $\max(|W|) = 2.31$ (located at row 3, column 4)
* **Formula:** $S = rac{\max(|W|)}{127}$
* **Result:** $S = rac{2.31}{127} pprox 0.018189$

---

## Task 2: Quantization ($W_q$)
We convert the FP32 weights into INT8 using the formula: $W_q = 	ext{clamp}(	ext{round}(W / S), -128, 127)$.

**Quantized INT8 Matrix ($W_q$):**
| Col 1 | Col 2 | Col 3 | Col 4 |
| :---: | :---: | :---: | :---: |
| 47    | -66   | 19    | 115   |
| -4    | 50    | -103  | 7     |
| 85    | 2     | -24   | -127  |
| -10   | 57    | 42    | 30    |

*Note: No clamping was needed here as all values naturally fell within the [-128, 127] range.*

---

## Task 3: Dequantization ($W_{deq}$)
We reconstruct the FP32 values to see the loss of precision: $W_{deq} = W_q 	imes S$.

**Dequantized Matrix ($W_{deq}$):**
| Col 1 | Col 2 | Col 3 | Col 4 |
| :---: | :---: | :---: | :---: |
| 0.8549 | -1.2005 | 0.3456 | 2.0917 |
| -0.0728 | 0.9094 | -1.8735 | 0.1273 |
| 1.5461 | 0.0364 | -0.4365 | -2.3100 |
| -0.1819 | 1.0368 | 0.7641 | 0.5457 |

---

## Task 4: Error Analysis
We calculate the per-element absolute error: $|W - W_{deq}|$.

**Absolute Error Matrix:**
| Col 1 | Col 2 | Col 3 | Col 4 |
| :---: | :---: | :---: | :---: |
| 0.0049 | 0.0005 | 0.0056 | 0.0083 |
| 0.0028 | 0.0006 | 0.0065 | 0.0073 |
| 0.0039 | 0.0064 | 0.0035 | 0.0000 |
| 0.0019 | 0.0068 | 0.0059 | 0.0043 |

* **Largest Error:** 0.0083 (at $W[0][3]$)
* **Mean Absolute Error (MAE):** $rac{0.0692}{16} pprox \mathbf{0.0043}$

---

## Task 5: Bad Scale Experiment ($S_{bad} = 0.01$)
When the scale factor is too small, weights are forced to "clamp" at the INT8 limits.

**Quantized Matrix (Clamped):**
| Col 1 | Col 2 | Col 3 | Col 4 |
| :---: | :---: | :---: | :---: |
| 85    | -120  | 34    | **127*** |
| -7    | 91    | **-128*** | 12    |
| **127*** | 3    | -44   | **-128*** |
| -18   | 103   | 77    | 55    |
*\*Indicates value was clamped to the INT8 limit.*

**Dequantized Matrix (with Clipping):**
| Col 1 | Col 2 | Col 3 | Col 4 |
| :---: | :---: | :---: | :---: |
| 0.85 | -1.20 | 0.34 | **1.27** |
| -0.07 | 0.91 | **-1.28** | 0.12 |
| **1.27** | 0.03 | -0.44 | **-1.28** |
| -0.18 | 1.03 | 0.77 | 0.55 |

### Impact Summary:
* **Clipped Errors:** High errors at clipped positions (e.g., $|2.10 - 1.27| = 0.83$).
* **MAE_bad:** $pprox \mathbf{0.1713}$ (Roughly 40x higher than the correct scale).

**Explanation:** When $S$ is too small, large-magnitude weights exceed INT8's $[-128, 127]$ range and get hard-clamped, introducing severe clipping error that cannot be recovered during dequantization.
