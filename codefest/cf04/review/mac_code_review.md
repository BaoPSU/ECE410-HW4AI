# MAC Code Review — Codefest 4 CLLM

## LLM Identification

| File | LLM | Model Version |
|------|-----|---------------|
| `mac_llm_A.v` | Claude | Claude Sonnet 4.6 |
| `mac_llm_B.v` | Gemini | Gemini 2.5 Flash (Google Workspace / PSU Enterprise) |

---

## Compilation Results

### mac_llm_A.v
```
iverilog -g2012 -o sim_a mac_tb.v mac_llm_A.v
```
No errors. Compiled cleanly.

### mac_llm_B.v
```
iverilog -g2012 -o sim_b mac_tb.v mac_llm_B.v
```
No errors. Compiled cleanly.

---

## Simulation Results

### mac_llm_A.v — ALL PASS
```
PASS [a=3,b=4 cyc1]: out = 12
PASS [a=3,b=4 cyc2]: out = 24
PASS [a=3,b=4 cyc3]: out = 36
PASS [rst]: out = 0
PASS [a=-5,b=2 cyc1]: out = -10
PASS [a=-5,b=2 cyc2]: out = -20
ALL TESTS PASSED
```

### mac_llm_B.v — ALL PASS
```
PASS [a=3,b=4 cyc1]: out = 12
PASS [a=3,b=4 cyc2]: out = 24
PASS [a=3,b=4 cyc3]: out = 36
PASS [rst]: out = 0
PASS [a=-5,b=2 cyc1]: out = -10
PASS [a=-5,b=2 cyc2]: out = -20
ALL TESTS PASSED
```

Both LLMs produced functionally correct implementations that pass all 6 test cases, including the negative-operand case that catches sign extension bugs. This is a notable finding in itself — both LLMs correctly followed the synthesizable SystemVerilog constraints.

---

## Issue 1 — Sign Extension Approach: Implicit vs Explicit (Both Files)

### Offending / differing lines

**LLM A (Claude):**
```systemverilog
logic signed [15:0] product;
always_comb product = a * b;
// ...
out <= out + {{16{product[15]}}, product};
```

**LLM B (Gemini):**
```systemverilog
logic signed [15:0] product;
assign product = a * b;
// ...
out <= out + product;
```

### Analysis

LLM B relies on **implicit SystemVerilog sign extension**: when a `signed [15:0]` value is added to a `signed [31:0]` accumulator, the compiler automatically sign-extends the narrower operand. This is correct per the IEEE 1800 SystemVerilog standard and produces the same hardware.

LLM A uses **explicit bit-level sign extension** (`{16{product[15]}}, product}`), making the intent visible to any reader regardless of their SystemVerilog knowledge. It is more defensive — if the code were ever adapted to plain Verilog-2001, the explicit version would still work correctly whereas the implicit version might silently zero-extend depending on tool behavior.

**Both are correct**, but the explicit approach (LLM A) is safer for portability and easier to audit during code review.

### Preferred version
```systemverilog
out <= out + {{16{product[15]}}, product};  // explicit — portable and auditable
```

---

## Issue 2 — `assign` vs `always_comb` for Combinational Logic (LLM B)

### Offending lines (LLM B)
```systemverilog
assign product = a * b;
```

### Analysis

LLM B uses a continuous `assign` statement to compute the product, which is functionally correct. However, the SystemVerilog best practice for combinational logic inside a module is `always_comb`, not `assign`. `always_comb` has two advantages:

1. **Linting enforcement**: tools will flag incomplete sensitivity lists or latches at compile time.
2. **Consistency**: mixing `assign` and `always_ff` in the same module while having `always_comb` available is inconsistent style. The spec also emphasizes modern synthesizable SystemVerilog.

LLM A correctly uses `always_comb product = a * b`.

### Corrected version
```systemverilog
always_comb product = a * b;
```

---

## Issue 3 — Multiplication Width Ambiguity (Both Files — Latent Risk)

### Context

Both LLMs declare:
```systemverilog
logic signed [15:0] product;
assign/always_comb product = a * b;
```

### Analysis

In SystemVerilog, the width of an intermediate expression like `a * b` is determined by the **self-determined width** of the operands (8 bits each), giving a 16-bit result. This is then assigned to `product [15:0]`, which matches. However, if the bit-width of `product` were changed (e.g., to `[31:0]`) the multiplication would still only produce a 16-bit result internally before being zero/sign-padded — a subtle source of errors.

A safer pattern used in production RTL is to explicitly cast the multiplication to the desired width to make the intent unambiguous:

```systemverilog
// Makes the 32-bit context explicit — no reliance on implicit width rules
out <= out + 32'(signed'(a) * signed'(b));
```

This eliminates the intermediate `product` wire entirely and is unambiguous about precision at the accumulator width.

---

## mac_correct.v — Final Verified Implementation

`mac_correct.v` incorporates all best practices: `always_ff`, `always_comb`, explicit sign extension, `logic signed` on all ports.

### Simulation log
```
iverilog -g2012 -o mac_correct_sim mac_tb.v mac_correct.v
PASS [a=3,b=4 cyc1]: out = 12
PASS [a=3,b=4 cyc2]: out = 24
PASS [a=3,b=4 cyc3]: out = 36
PASS [rst]: out = 0
PASS [a=-5,b=2 cyc1]: out = -10
PASS [a=-5,b=2 cyc2]: out = -20
ALL TESTS PASSED
```

---

## Summary

| Check | LLM A (Claude) | LLM B (Gemini) |
|-------|---------------|---------------|
| `always_ff` used | ✓ | ✓ |
| `logic signed` on all ports | ✓ | ✓ |
| Sign extension correct | ✓ explicit | ✓ implicit |
| Combinational style | `always_comb` (preferred) | `assign` (functional, less strict) |
| Testbench: all 6 pass | ✓ | ✓ |

Both LLMs avoided the most common failure modes. The differences between them are stylistic rather than functional, with LLM A's explicit approach being slightly more defensively written.
