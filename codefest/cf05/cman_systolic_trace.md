# CF05 CMAN — Weight-Stationary 2×2 Systolic Array Trace
Bao Nguyen

---

## Given

**Matrix A:**

|       | col 0 | col 1 |
|:-----:|:-----:|:-----:|
| row 0 |   1   |   2   |
| row 1 |   3   |   4   |

**Matrix B (weights):**

|       | col 0 | col 1 |
|:-----:|:-----:|:-----:|
| row 0 |   5   |   6   |
| row 1 |   7   |   8   |

**Expected C = A × B:**

|       | col 0 | col 1 |
|:-----:|:-----:|:-----:|
| row 0 |  19   |  22   |
| row 1 |  43   |  50   |

**Verification before tracing:**

C[0][0] = A[0][0]×B[0][0] + A[0][1]×B[1][0] = 1×5 + 2×7 = 5 + 14 = **19** ✓  
C[0][1] = A[0][0]×B[0][1] + A[0][1]×B[1][1] = 1×6 + 2×8 = 6 + 16 = **22** ✓  
C[1][0] = A[1][0]×B[0][0] + A[1][1]×B[1][0] = 3×5 + 4×7 = 15 + 28 = **43** ✓  
C[1][1] = A[1][0]×B[0][1] + A[1][1]×B[1][1] = 3×6 + 4×8 = 18 + 32 = **50** ✓

---

## Task 1: PE Diagram with Preloaded Weights

**Weight assignment rule:** PE[i][j] preloads weight B[i][j]

- PE[0][0] ← B[0][0] = **5**
- PE[0][1] ← B[0][1] = **6**
- PE[1][0] ← B[1][0] = **7**
- PE[1][1] ← B[1][1] = **8**

**Array layout:**

```
  A[m][0] ──►  ┌─────────────┐     ┌─────────────┐
               │   PE[0][0]  │ ──► │   PE[0][1]  │
  Row 0 (k=0) │  weight = 5 │     │  weight = 6 │
               └──────┬──────┘     └──────┬──────┘
                      │ ps↓               │ ps↓
  A[m][1] ──►  ┌──────▼──────┐     ┌──────▼──────┐
               │   PE[1][0]  │ ──► │   PE[1][1]  │
  Row 1 (k=1) │  weight = 7 │     │  weight = 8 │
               └─────────────┘     └─────────────┘
                      │                   │
                   C[m][0]             C[m][1]
```

- `──►` : input propagates left-to-right within each PE row
- `ps↓` : partial sum flows top-to-bottom between rows
- Outputs drain from the bottom row

**How each PE operates per cycle:**

```
partial_sum_out = partial_sum_in + (input × weight)
```

- PE[i][j] receives `partial_sum_in` from PE[i-1][j] above (0 for row 0)
- PE[i][j] receives `input` from the left edge of its row
- PE[i][j] sends `partial_sum_out` down to PE[i+1][j]

---

## Task 2: Cycle-by-Cycle Trace

**Dataflow rule:** Each row of A is streamed one element at a time. A[m][0] enters row 0; one cycle later A[m][1] enters row 1 while row 0's partial sums propagate downward. Partial sums in row 0 reset between output rows.

---

### Cycle 1 — Feed A[0][0] = 1 into Row 0

**Input to Row 0:** A[0][0] = 1  
**Input to Row 1:** bubble (0, no valid data yet)

**PE[0][0]:**
```
partial_sum_in  = 0   (top row always starts at 0)
input           = 1
weight          = 5
partial_sum_out = 0 + (1 × 5) = 0 + 5 = 5
```

**PE[0][1]:**
```
partial_sum_in  = 0
input           = 1   (same input broadcast across row 0)
weight          = 6
partial_sum_out = 0 + (1 × 6) = 0 + 6 = 6
```

**PE[1][0]:**
```
partial_sum_in  = 0   (nothing has flowed down yet)
input           = 0   (bubble)
weight          = 7
partial_sum_out = 0 + (0 × 7) = 0
```

**PE[1][1]:**
```
partial_sum_in  = 0
input           = 0   (bubble)
weight          = 8
partial_sum_out = 0 + (0 × 8) = 0
```

**Output this cycle:** none

---

### Cycle 2 — Feed A[0][1] = 2 into Row 1; Row 0 partial sums drain down

**Input to Row 0:** bubble (0)  
**Input to Row 1:** A[0][1] = 2

**PE[0][0]:** holds partial_sum = **5** (passed down to PE[1][0])

**PE[0][1]:** holds partial_sum = **6** (passed down to PE[1][1])

**PE[1][0]:**
```
partial_sum_in  = 5   (received from PE[0][0] this cycle)
input           = 2
weight          = 7
partial_sum_out = 5 + (2 × 7) = 5 + 14 = 19  → C[0][0]
```

**PE[1][1]:**
```
partial_sum_in  = 6   (received from PE[0][1] this cycle)
input           = 2   (same input broadcast across row 1)
weight          = 8
partial_sum_out = 6 + (2 × 8) = 6 + 16 = 22  → C[0][1]
```

**Output this cycle:** **C[0] = [19, 22]** ✓

*Row 0 partial sums reset to 0 for the next output row.*

---

### Cycle 3 — Feed A[1][0] = 3 into Row 0

**Input to Row 0:** A[1][0] = 3  
**Input to Row 1:** bubble (0)

**PE[0][0]:**
```
partial_sum_in  = 0   (reset)
input           = 3
weight          = 5
partial_sum_out = 0 + (3 × 5) = 0 + 15 = 15
```

**PE[0][1]:**
```
partial_sum_in  = 0   (reset)
input           = 3
weight          = 6
partial_sum_out = 0 + (3 × 6) = 0 + 18 = 18
```

**PE[1][0]:**
```
partial_sum_in  = 0   (reset)
input           = 0   (bubble)
weight          = 7
partial_sum_out = 0 + (0 × 7) = 0
```

**PE[1][1]:**
```
partial_sum_in  = 0   (reset)
input           = 0   (bubble)
weight          = 8
partial_sum_out = 0 + (0 × 8) = 0
```

**Output this cycle:** none

---

### Cycle 4 — Feed A[1][1] = 4 into Row 1; Row 0 partial sums drain down

**Input to Row 0:** bubble (0)  
**Input to Row 1:** A[1][1] = 4

**PE[0][0]:** holds partial_sum = **15** (passed down to PE[1][0])

**PE[0][1]:** holds partial_sum = **18** (passed down to PE[1][1])

**PE[1][0]:**
```
partial_sum_in  = 15  (received from PE[0][0] this cycle)
input           = 4
weight          = 7
partial_sum_out = 15 + (4 × 7) = 15 + 28 = 43  → C[1][0]
```

**PE[1][1]:**
```
partial_sum_in  = 18  (received from PE[0][1] this cycle)
input           = 4
weight          = 8
partial_sum_out = 18 + (4 × 8) = 18 + 32 = 50  → C[1][1]
```

**Output this cycle:** **C[1] = [43, 50]** ✓

---

### Summary Table

| Cycle | Input → Row 0 | Input → Row 1 | PE[0][0] ps | PE[0][1] ps | PE[1][0] ps | PE[1][1] ps | Output C |
|:-----:|:-------------:|:-------------:|:-----------:|:-----------:|:-----------:|:-----------:|:--------:|
| 1 | A[0][0] = 1 | bubble (0) | 0+1×5 = **5** | 0+1×6 = **6** | 0+0×7 = **0** | 0+0×8 = **0** | — |
| 2 | bubble (0) | A[0][1] = 2 | holds **5** | holds **6** | 5+2×7 = **19** | 6+2×8 = **22** | C[0] = [19, 22] |
| 3 | A[1][0] = 3 | bubble (0) | 0+3×5 = **15** | 0+3×6 = **18** | 0+0×7 = **0** | 0+0×8 = **0** | — |
| 4 | bubble (0) | A[1][1] = 4 | holds **15** | holds **18** | 15+4×7 = **43** | 18+4×8 = **50** | C[1] = [43, 50] |

---

## Task 3: Counts

### (a) Total MAC Operations

**Formula:** each PE executes one MAC per active cycle: `partial_sum_out = partial_sum_in + (input × weight)`

**PE[0][0]:**
- Cycle 1: 0 + (1 × 5) = 5 → **MAC #1**
- Cycle 3: 0 + (3 × 5) = 15 → **MAC #2**
- Subtotal: 2 MACs

**PE[0][1]:**
- Cycle 1: 0 + (1 × 6) = 6 → **MAC #3**
- Cycle 3: 0 + (3 × 6) = 18 → **MAC #4**
- Subtotal: 2 MACs

**PE[1][0]:**
- Cycle 2: 5 + (2 × 7) = 19 → **MAC #5**
- Cycle 4: 15 + (4 × 7) = 43 → **MAC #6**
- Subtotal: 2 MACs

**PE[1][1]:**
- Cycle 2: 6 + (2 × 8) = 22 → **MAC #7**
- Cycle 4: 18 + (4 × 8) = 50 → **MAC #8**
- Subtotal: 2 MACs

**Total = 2 + 2 + 2 + 2 = 8 MAC operations**

*Cross-check: M × K × N = 2 × 2 × 2 = 8 ✓ (every element of A×B contributes exactly one MAC)*

---

### (b) Number of Times Each Input Value Is Reused

**Rule:** In weight-stationary dataflow, each input element A[m][k] is broadcast to all N=2 column PEs in its row (PE[k][0] and PE[k][1]). One off-chip fetch → two PE uses → reuse count = 1 additional use after initial load.

**A[0][0] = 1:**
- Used by PE[0][0] (Cycle 1): 1 × 5 = 5
- Used by PE[0][1] (Cycle 1): 1 × 6 = 6
- Total uses = 2, **reused 1 time**

**A[0][1] = 2:**
- Used by PE[1][0] (Cycle 2): 2 × 7 = 14
- Used by PE[1][1] (Cycle 2): 2 × 8 = 16
- Total uses = 2, **reused 1 time**

**A[1][0] = 3:**
- Used by PE[0][0] (Cycle 3): 3 × 5 = 15
- Used by PE[0][1] (Cycle 3): 3 × 6 = 18
- Total uses = 2, **reused 1 time**

**A[1][1] = 4:**
- Used by PE[1][0] (Cycle 4): 4 × 7 = 28
- Used by PE[1][1] (Cycle 4): 4 × 8 = 32
- Total uses = 2, **reused 1 time**

**Each input value is reused 1 time (2× reuse factor) — one off-chip fetch serves two PEs.**

---

### (c) Off-Chip Memory Accesses

**A (inputs) — reads during streaming:**

| Element | Value | Fetched at Cycle | PE(s) that use it |
|:-------:|:-----:|:----------------:|:-----------------:|
| A[0][0] | 1 | Cycle 1 | PE[0][0], PE[0][1] |
| A[0][1] | 2 | Cycle 2 | PE[1][0], PE[1][1] |
| A[1][0] | 3 | Cycle 3 | PE[0][0], PE[0][1] |
| A[1][1] | 4 | Cycle 4 | PE[1][0], PE[1][1] |

A off-chip reads = 4 elements × 1 fetch each = **4 reads**

**B (weights) — preloaded into PEs before compute begins:**

| Element | Value | Loaded into |
|:-------:|:-----:|:-----------:|
| B[0][0] | 5 | PE[0][0] |
| B[0][1] | 6 | PE[0][1] |
| B[1][0] | 7 | PE[1][0] |
| B[1][1] | 8 | PE[1][1] |

B off-chip reads = 4 weights × 1 preload each = **4 reads** (never re-fetched during computation — this is weight-stationary's defining property)

**C (outputs) — written after bottom row produces each result:**

| Element | Value | Written at Cycle |
|:-------:|:-----:|:----------------:|
| C[0][0] | 19 | Cycle 2 |
| C[0][1] | 22 | Cycle 2 |
| C[1][0] | 43 | Cycle 4 |
| C[1][1] | 50 | Cycle 4 |

C off-chip writes = 4 elements × 1 write each = **4 writes**

**Total off-chip accesses = 4 (A reads) + 4 (B preload reads) + 4 (C writes) = 12**

---

## Task 4: Output-Stationary Comparison

In output-stationary dataflow, the partial sum for each output element C[i][j] stays fixed inside its assigned PE while both the A row elements and B column elements stream through — so the **accumulated output values (partial sums) stay stationary** instead of the weights.

---
