# Manual INT8 Symmetric Quantization: Detailed Hand Calculations

This document provides the exhaustive "by-hand" math for every element in the 4x4 matrix for both the correct scale and the bad scale experiment.

---

## Task 1: Scale Factor Calculation
**Matrix W:**
```
[  0.85, -1.20,  0.34,  2.10 ]
[ -0.07,  0.91, -1.88,  0.12 ]
[  1.55,  0.03, -0.44, -2.31 ]
[ -0.18,  1.03,  0.77,  0.55 ]
```

1.  **Find Absolute Maximum:** Compare all $|w|$: $\{0.85, 1.20, 0.34, 2.10, 0.07, 0.91, 1.88, 0.12, 1.55, 0.03, 0.44, 2.31, 0.18, 1.03, 0.77, 0.55\}$.  
    Max is **2.31**.
2.  **Compute S:** $S = 2.31 / 127 = 0.018188976...$  
    **Used for calculations: 0.018189**

---

## Task 2: Quantization (Hand Calculations)
**Formula:** $W_q = 	ext{round}(W / S)$

| Row | Col | Weight ($W$) | $W / 0.018189$ | Round Result ($W_q$) |
|:---:|:---:|:------------:|:--------------:|:--------------------:|
| 1 | 1 | 0.85 | 46.7315 | **47** |
| 1 | 2 | -1.20 | -65.9739 | **-66** |
| 1 | 3 | 0.34 | 18.6926 | **19** |
| 1 | 4 | 2.10 | 115.4544 | **115** |
| 2 | 1 | -0.07 | -3.8485 | **-4** |
| 2 | 2 | 0.91 | 50.0302 | **50** |
| 2 | 3 | -1.88 | -103.3592 | **-103** |
| 2 | 4 | 0.12 | 6.5974 | **7** |
| 3 | 1 | 1.55 | 85.2163 | **85** |
| 3 | 2 | 0.03 | 1.6493 | **2** |
| 3 | 3 | -0.44 | -24.1904 | **-24** |
| 3 | 4 | -2.31 | -127.0000 | **-127** |
| 4 | 1 | -0.18 | -9.8961 | **-10** |
| 4 | 2 | 1.03 | 56.6276 | **57** |
| 4 | 3 | 0.77 | 42.3333 | **42** |
| 4 | 4 | 0.55 | 30.2381 | **30** |

---

## Task 3: Dequantization (Hand Calculations)
**Formula:** $W_{deq} = W_q 	imes S$

| $W_q$ | $	imes 0.018189$ | Result ($W_{deq}$) |
|:---:|:---:|:---:|
| 47 | $	imes S$ | **0.8549** |
| -66 | $	imes S$ | **-1.2005** |
| 19 | $	imes S$ | **0.3456** |
| 115 | $	imes S$ | **2.0917** |
| -4 | $	imes S$ | **-0.0728** |
| 50 | $	imes S$ | **0.9095** |
| -103 | $	imes S$ | **-1.8735** |
| 7 | $	imes S$ | **0.1273** |
| 85 | $	imes S$ | **1.5461** |
| 2 | $	imes S$ | **0.0364** |
| -24 | $	imes S$ | **-0.4365** |
| -127 | $	imes S$ | **-2.3100** |
| -10 | $	imes S$ | **-0.1819** |
| 57 | $	imes S$ | **1.0368** |
| 42 | $	imes S$ | **0.7639** |
| 30 | $	imes S$ | **0.5457** |

---

## Task 4: Error Analysis
**Mean Absolute Error (MAE):** $\sum |W - W_{deq}| / 16$

1. **Sum of Abs Errors:** $|0.85 - 0.8549| = 0.0049$  
   $|-1.20 - (-1.2005)| = 0.0005$  
   ... (continuing for all 16) ...  
   **Total Sum $ pprox$ 0.0692**
2. **MAE:** $0.0692 / 16 = \mathbf{0.004325}$

---

## Task 5: Bad Scale Experiment ($S_{bad} = 0.01$)
**Formula:** $	ext{clamp}(	ext{round}(W / 0.01), -128, 127)$

**Step 1: Quantize with Clipping**
* $W=2.10$: $2.10/0.01 = 210 
ightarrow$ **Clamp to 127**
* $W=-1.88$: $-1.88/0.01 = -188 
ightarrow$ **Clamp to -128**
* $W=1.55$: $1.55/0.01 = 155 
ightarrow$ **Clamp to 127**
* $W=-2.31$: $-2.31/0.01 = -231 
ightarrow$ **Clamp to -128**

**Step 2: Reconstruct clipped values**
* $127 	imes 0.01 = \mathbf{1.27}$
* $-128 	imes 0.01 = \mathbf{-1.28}$

**Step 3: Large Error calculation (MAE)**
* Error at 2.10: $|2.10 - 1.27| = 0.83$
* Error at -2.31: $|-2.31 - (-1.28)| = 1.03$
* **MAE_bad = 0.17125** (Significant jump due to clipping).
