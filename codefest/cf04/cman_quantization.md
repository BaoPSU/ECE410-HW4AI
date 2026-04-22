# Manual INT8 Symmetric Quantization: Full Hand Calculations

## 1. Scale Factor (Task 1)
**Original Equation:**
$$S = \frac{\max(|W|)}{127}$$

* **Max Absolute Value:** $\max(|0.85|, |-1.20|, \dots, |-2.31|) = 2.31$
* **Calculation:** $2.31 / 127 = 0.018188976...$
* **Result (S):** **0.018189**

---

## 2. Quantization (Task 2)
**Original Equation:**
$$W_q = \text{clamp}(\text{round}(W / S), -128, 127)$$



| Row/Col | Weight ($W$) | $W / S$ | $\text{round}(W / S)$ | $W_q$ (INT8) |
| :--- | :--- | :--- | :--- | :--- |
| **R1,C1** | 0.85 | 46.731 | 47 | **47** |
| **R1,C2** | -1.20 | -65.974 | -66 | **-66** |
| **R1,C3** | 0.34 | 18.693 | 19 | **19** |
| **R1,C4** | 2.10 | 115.454 | 115 | **115** |
| **R2,C1** | -0.07 | -3.848 | -4 | **-4** |
| **R2,C2** | 0.91 | 50.030 | 50 | **50** |
| **R2,C3** | -1.88 | -103.359 | -103 | **-103** |
| **R2,C4** | 0.12 | 6.597 | 7 | **7** |
| **R3,C1** | 1.55 | 85.216 | 85 | **85** |
| **R3,C2** | 0.03 | 1.649 | 2 | **2** |
| **R3,C3** | -0.44 | -24.190 | -24 | **-24** |
| **R3,C4** | -2.31 | -127.000 | -127 | **-127** |
| **R4,C1** | -0.18 | -9.896 | -10 | **-10** |
| **R4,C2** | 1.03 | 56.628 | 57 | **57** |
| **R4,C3** | 0.77 | 42.333 | 42 | **42** |
| **R4,C4** | 0.55 | 30.238 | 30 | **30** |

---

## 3. Dequantization (Task 3)
**Original Equation:**
$$W_{deq} = W_q \times S$$

| $W_q$ | $\times 0.018189$ | $W_{deq}$ |
| :--- | :--- | :--- |
| 47 | $\times S$ | **0.8549** |
| -66 | $\times S$ | **-1.2005** |
| 19 | $\times S$ | **0.3456** |
| 115 | $\times S$ | **2.0917** |
| -4 | $\times S$ | **-0.0728** |
| 50 | $\times S$ | **0.9095** |
| -103 | $\times S$ | **-1.8735** |
| 7 | $\times S$ | **0.1273** |
| 85 | $\times S$ | **1.5461** |
| 2 | $\times S$ | **0.0364** |
| -24 | $\times S$ | **-0.4365** |
| -127 | $\times S$ | **-2.3100** |
| -10 | $\times S$ | **-0.1819** |
| 57 | $\times S$ | **1.0368** |
| 42 | $\times S$ | **0.7639** |
| 30 | $\times S$ | **0.5457** |

---

## 4. Error Analysis (Task 4)
**Original Equations:**
$$\text{Error} = |W - W_{deq}|$$
$$\text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |W_i - W_{deq,i}|$$

* **Absolute Error Sum:** 0.0692
* **Calculation:** $0.0692 / 16 = \mathbf{0.0043}$

---

## 5. Bad Scale Experiment (Task 5)
**Scale Used:** $S_{bad} = 0.01$

* **The Overflow/Clipping Issue:**
    * For $W = 2.10$: $2.10 / 0.01 = 210 \rightarrow$ **Clamped to 127**
    * For $W = -2.31$: $-2.31 / 0.01 = -231 \rightarrow$ **Clamped to -128**
* **Resulting MAE:** **0.1713**
