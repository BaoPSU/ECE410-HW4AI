# CF07 CMAN — Claudian Tutoring Session Log

**ECE 410/510 Spring 2026 — Bao Nguyen**
*Socratic walk-through of the Sparsity Breakeven Analysis with Claudian (TA bot). All numerical answers were derived by me; Claudian asked guiding questions only.*

---

## Opening

**Claudian:** Hi! I'm Claudian, your friendly TA for Codefest 7. I'm here to help you work through this codefest — but I'll guide you with questions rather than giving away answers. What are you working on, and where are you getting stuck?

**Me:** So for part 1a, my understanding is we have a total of MAC = N×N = N², each MAC is 2 FLOPs, so then F_dense = 2N²?

**Claudian:** That's exactly right! 🎉
- An N×N weight matrix has N² elements
- Each element requires one MAC (multiply + accumulate)
- Each MAC = 2 FLOPs (one multiply, one add)
- So Dense FLOPs = 2N²

With N=512, what number does that give you?

**Me:** 524.29E3?

**Claudian:** Close! 2 × 512² = 2 × ? What is 512² first?

**Me:** 262.14 × 10³

**Claudian:** Exactly! 512² = 262,144. So then 2 × 262,144 = ?

**Me:** 524,290

**Claudian:** Almost — watch your arithmetic. (Hint: 2 × 262,000 = 524,000, and 2 × 144 = 288...)

**Me:** 524,288?

**Claudian:** ✓ So part 1(a): **Dense compute = 2N² = 524,288 FLOPs** for N=512.

---

## Part 1(b) — Dense memory bytes

**Me:** For b I got 1,048,576.

**Claudian:** Perfect! 4 × 512² = 4 × 262,144 = 1,048,576 bytes (exactly 1 MB).

**Answer:** $B_\text{dense} = 4N^2 = 1{,}048{,}576$ bytes (1 MB)

---

## Part 1(c) — Sparse compute (function of s)

**Claudian:** In the dense case, every element of the N×N matrix gets a MAC. In the sparse case, a fraction s of weights are zero. If hardware skips zero MACs, how many non-zero elements are there in terms of N and s?

**Me:** What N and s?

**Claudian:**
- N = 512 — the matrix is N×N
- s = sparsity, the fraction of weights that are zero (s=0.9 → 90% zero)

So if the total is N², and a fraction s are zero, how many are non-zero?

**Me:** So it's N×s?

**Claudian:** Not quite. If s is the fraction that ARE zero, what fraction are NON-zero? Then multiply that by N².

**Me:** So if I multiply the fraction that are zero by N², that's the fraction of non-zeros?

**Claudian:** Almost — but careful! You want the non-zero fraction. If s = 0.9 (90% zero), what percentage are non-zero?

**Me:** 10%.

**Claudian:** Exactly. So the non-zero fraction is **(1 − s)**, and the count is N²(1−s).

Each non-zero requires 1 MAC = 2 FLOPs. So what's the sparse compute expression?

**Me:** So it's 2N²(1−s).

**Claudian:** Perfect! 🎉

**Answer:** $F_\text{sparse}(s) = 2N^2(1-s)$ FLOPs

Sanity:
- s = 0 → 2N² (matches dense ✓)
- s = 0.9 → 10% of dense work ✓

---

## Part 1(d) — Sparse memory bytes (CSR)

**Claudian:** CSR has three arrays. Can you list what each stores?

**Me:** What's CSR?

**Claudian:** Compressed Sparse Row format. Three arrays:
- `values` — actual non-zero weights
- `col_idx` — column position of each non-zero
- `row_ptr` — where each row starts (length N+1)

How many bytes each?

**Me:** So it's 4 bytes for the first two and then row pointer has 16?

**Claudian:** Almost! Look at the spec:
- values: 4 bytes per non-zero ✓
- col_idx: 4 bytes per non-zero ✓
- row_ptr: **4 bytes per entry, N+1 entries**

How many non-zeros are there? (From part c.)

**Me:** So it's 16(1−s)?

**Claudian:** Let's build it piece by piece. Non-zeros = N²(1−s).
- values array: 4 × N²(1−s) bytes
- col_idx array: 4 × N²(1−s) bytes

Add them.

**Me:** 8N²(1−s).

**Claudian:** Add the row_ptr: 4(N+1) bytes. Total?

**Me:** Before we go further — for values and col_idx, are they both 8N²(1−s)?

**Claudian:** No — 8N²(1−s) is the **combined** total. Individually each is 4N²(1−s). Now add row_ptr.

**Me:** So it's 8N²(1−s) + 4(N+1)?

**Claudian:** Perfect! 🎉

**Answer:** $B_\text{sparse}(s) = 8N^2(1-s) + 4(N+1)$ bytes

Sanity check at s=0 (fully dense): 8·512²·1 + 4·513 = 2,097,152 + 2,052 = **2,099,204 bytes** — twice the dense storage! CSR adds overhead, so it only saves memory when sparsity is high enough. (This is the setup for Task 3, the memory breakeven.)

---

## Part 2 — FLOPs speedup and the 2× sparsity

**Me:** OK for 2, do part 1a over 1c?

**Claudian:** Exactly!

$$\text{Speedup} = \frac{2N^2}{2N^2(1-s)}$$

Simplify?

**Me:** I got s − 1/2.

**Claudian:** Careful with the cancellation. The 2N² cancels top and bottom, leaving 1/(1−s).

**Me:** s = 1/2?

**Claudian:** Set 1/(1−s) = 2. What does (1−s) equal?

**Me:** OK now I got 4N²(1−s) = 2N², does that look right?

**Claudian:** No — where did the 4N² come from? Keep it simple: 1/(1−s) = 2, solve for s.

**Me:** It's because we're solving 2 = 2N² / N²(1−s).

**Claudian:** I see what you're thinking, but the 2N² cancels completely:

$$\frac{2N^2}{2N^2(1-s)} = \frac{1}{1-s}$$

So just solve **1/(1−s) = 2**.

**Me:** 2 = 2N² / 2N²(1−s).

**Claudian:** Yes that's the starting point. Now cancel: 2N²/2N² = 1. You're left with 1/(1−s) = 2. What does (1−s) equal?

---

*[Working out the final algebra step: 1/(1−s) = 2 → 1−s = 1/2 → s = 1/2]*

**Final answer for Task 2:** Speedup = 1/(1−s); 2× speedup at **s = 1/2 = 50%**.

---

## Status

| Task | Status |
|------|--------|
| 1(a) Dense FLOPs | ✅ 2N² |
| 1(b) Dense bytes | ✅ 4N² |
| 1(c) Sparse FLOPs | ✅ 2N²(1−s) |
| 1(d) Sparse bytes | ✅ 8N²(1−s) + 4(N+1) |
| 2. FLOPs speedup | ✅ 1/(1−s); 2× at s=1/2 |
| 3. Memory breakeven | (next) |
| 4. End-to-end at s=0.9 | (next) |

All answers in `cman_sparsity_analysis.md` were derived by working through the math myself with Claudian as a guide. No answers were generated by AI.
