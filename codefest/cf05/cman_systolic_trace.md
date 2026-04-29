# CF05 CMAN — Weight-Stationary Systolic Array Trace
Bao Nguyen

---

## Task 1: PE Diagram with Preloaded Weights

2×2 weight-stationary systolic array. Weights B are preloaded and fixed. Inputs (rows of A) stream in from the left; partial sums flow downward.

```
  A[m][0] ──►  ┌─────────────┐     ┌─────────────┐
               │   PE[0][0]  │ ──► │   PE[0][1]  │
Row 0 (k=0)   │  weight = 5 │     │  weight = 6 │
               └──────┬──────┘     └──────┬──────┘
                      │ ps↓               │ ps↓
  A[m][1] ──►  ┌──────▼──────┐     ┌──────▼──────┐
               │   PE[1][0]  │ ──► │   PE[1][1]  │
Row 1 (k=1)   │  weight = 7 │     │  weight = 8 │
               └─────────────┘     └─────────────┘
                      │                   │
                   C[m][0]             C[m][1]
```

- **PE[i][j]** preloads weight **B[i][j]**
- Arrows `──►` show input propagating left-to-right within each row
- Arrows `ps↓` show partial sums flowing top-to-bottom

---

## Task 2: Cycle-by-Cycle Trace

**Setup:**  A = [[1, 2], [3, 4]], B = [[5, 6], [7, 8]], expected C = [[19, 22], [43, 50]]

Each cycle: the active row receives one element of A; PE multiplies input × weight; partial sum from row above is added at row 1.

| Cycle | Input → Row 0 | Input → Row 1 | PE[0][0] partial sum | PE[0][1] partial sum | PE[1][0] partial sum | PE[1][1] partial sum | Output C |
|:-----:|:-------------:|:-------------:|:--------------------:|:--------------------:|:--------------------:|:--------------------:|:--------:|
| 1 | A[0][0] = **1** | — (bubble) | 0 + 1×5 = **5** | 0 + 1×6 = **6** | 0 | 0 | — |
| 2 | — (bubble) | A[0][1] = **2** | holds **5** | holds **6** | 5 + 2×7 = **19** | 6 + 2×8 = **22** | **C[0] = [19, 22]** |
| 3 | A[1][0] = **3** | — (bubble) | 0 + 3×5 = **15** | 0 + 3×6 = **18** | 0 (reset) | 0 (reset) | — |
| 4 | — (bubble) | A[1][1] = **4** | holds **15** | holds **18** | 15 + 4×7 = **43** | 18 + 4×8 = **50** | **C[1] = [43, 50]** |

**Partial sum detail:**

- **Cycle 1:** A[0][0]=1 feeds row 0. PE[0][0]: 1×5=5. PE[0][1]: 1×6=6. Row 1 gets a bubble; no accumulation.
- **Cycle 2:** A[0][1]=2 feeds row 1. Partial sums from row 0 (5 and 6) propagate down. PE[1][0]: 5 + 2×7 = 19. PE[1][1]: 6 + 2×8 = 22. Output row 0 of C.
- **Cycle 3:** Row-0 partial sums reset for next output row. A[1][0]=3 feeds row 0. PE[0][0]: 3×5=15. PE[0][1]: 3×6=18.
- **Cycle 4:** A[1][1]=4 feeds row 1. Partial sums 15 and 18 propagate down. PE[1][0]: 15 + 4×7 = 43. PE[1][1]: 18 + 4×8 = 50. Output row 1 of C.

---

## Task 3: Counts

### (a) Total MAC Operations

Each PE performs one MAC per active cycle. Four PEs × 2 active cycles each:

| PE | Cycle 1 | Cycle 2 | Cycle 3 | Cycle 4 | MACs |
|:--:|:-------:|:-------:|:-------:|:-------:|:----:|
| PE[0][0] | 1×5 | — | 3×5 | — | 2 |
| PE[0][1] | 1×6 | — | 3×6 | — | 2 |
| PE[1][0] | — | 5+2×7 | — | 15+4×7 | 2 |
| PE[1][1] | — | 6+2×8 | — | 18+4×8 | 2 |

**Total MAC operations = 8** (equals M×K×N = 2×2×2 = 8 — every element contributes)

---

### (b) Input Value Reuse

In weight-stationary dataflow, each A input element broadcasts across all N=2 column PEs in the same row:

- A[0][0]=1 → used by PE[0][0] and PE[0][1] → **2 uses**
- A[0][1]=2 → used by PE[1][0] and PE[1][1] → **2 uses**
- A[1][0]=3 → used by PE[0][0] and PE[0][1] → **2 uses**
- A[1][1]=4 → used by PE[1][0] and PE[1][1] → **2 uses**

**Each input value is reused 1 time after its initial load (2× reuse factor)** — each A element fetched once from off-chip is consumed by 2 PEs.

---

### (c) Off-Chip Memory Accesses

| Data | Direction | Count | Reasoning |
|:-----|:---------:|:-----:|:----------|
| A (inputs) | Read | 4 | 4 elements × 1 fetch each (streamed in one at a time) |
| B (weights) | Read | 4 | 4 weights × 1 preload into PEs before compute begins |
| C (outputs) | Write | 4 | 4 output elements × 1 write each |

**Total off-chip accesses = 12**

Note: B is loaded once at setup and never re-fetched during computation — this is the core advantage of weight-stationary dataflow.

---

## Task 4: Output-Stationary Comparison

In output-stationary dataflow, the partial sum for each output element C[i][j] stays fixed inside its dedicated PE while the A row elements and B column elements stream through — so the **accumulated output values** (partial sums) would be stationary rather than the weights.

---
