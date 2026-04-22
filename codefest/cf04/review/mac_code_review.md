# MAC Code Review — Codefest 4 CLLM

## LLM Identification

| File | LLM | Model Version |
|------|-----|---------------|
| `mac_llm_A.v` | Claude | Claude Sonnet 4.6 |
| `mac_llm_B.v` | GPT-4o | gpt-4o-2024-11-20 (simulated output) |

---

## Compilation Results

### mac_llm_A.v
```
iverilog -g2012 -o mac_a_sim mac_tb.v mac_llm_A.v
```
No errors. Compiled cleanly.

### mac_llm_B.v
```
iverilog -g2012 -o mac_b_sim mac_tb.v mac_llm_B.v
```
No compiler errors — the bug is a silent semantic error, not a syntax error.

---

## Simulation Results

### mac_llm_A.v — PASS
```
PASS [a=3,b=4 cyc1]: out = 12
PASS [a=3,b=4 cyc2]: out = 24
PASS [a=3,b=4 cyc3]: out = 36
PASS [rst]: out = 0
PASS [a=-5,b=2 cyc1]: out = -10
PASS [a=-5,b=2 cyc2]: out = -20
ALL TESTS PASSED
```

### mac_llm_B.v — FAIL
```
PASS [a=3,b=4 cyc1]: out = 12
PASS [a=3,b=4 cyc2]: out = 24
PASS [a=3,b=4 cyc3]: out = 36
PASS [rst]: out = 0
FAIL [a=-5,b=2 cyc1]: got 502, expected -10
FAIL [a=-5,b=2 cyc2]: got 1004, expected -20
2 TEST(S) FAILED
```

---

## Issue 1 — Wrong Process Type (`mac_llm_B.v`)

### Offending lines
```verilog
always @(posedge clk) begin
```

### Why it is wrong
The specification explicitly requires `always_ff`. Plain `always @(posedge clk)` is Verilog-2001 style and is not recognized by synthesis tools as a sequential process — some tools will not infer flip-flops correctly, and linters will flag it. `always_ff` is the SystemVerilog keyword that statically guarantees the block models a clocked register; it is required for safe, portable synthesizable RTL.

### Corrected version
```systemverilog
always_ff @(posedge clk) begin
```

---

## Issue 2 — Sign Extension Error: Missing `signed` on Ports and Intermediate Wire (`mac_llm_B.v`)

### Offending lines
```verilog
input [7:0] a,
input [7:0] b,
output reg [31:0] out

wire [15:0] product;
assign product = a * b;
```

### Why it is wrong
`a` and `b` are declared without the `signed` qualifier, so the compiler treats them as unsigned 8-bit values. The expression `a * b` performs **unsigned** multiplication. When `a = -5` (binary `0xFB = 251`), the result is `251 × 2 = 502` instead of the correct `-10`. The manual sign extension `{16{product[15]}}` then extends the wrong bit — since the multiplication was unsigned, `product[15]` is not the sign bit of the true signed product.

Simulation confirms: `a=-5, b=2` → output `502` (wrong) instead of `-10`.

### Corrected version
```systemverilog
input  logic signed [7:0]  a,
input  logic signed [7:0]  b,
output logic signed [31:0] out

logic signed [15:0] product;
always_comb product = a * b;  // signed * signed = signed 16-bit
```

With `signed` declared, `a * b` performs signed multiplication: `(-5) × 2 = -10 = 0xFFF6` in 16 bits. The sign extension `{16{product[15]}} = {16{1}}` then correctly extends to `0xFFFFFFF6 = -10` in 32 bits.

---

## Issue 3 — `reg` Instead of `logic` (`mac_llm_B.v`)

### Offending lines
```verilog
output reg [31:0] out
wire [15:0] product;
```

### Why it is wrong
The specification requires synthesizable **SystemVerilog**, not Verilog-2001. `reg` and `wire` are legacy Verilog types. SystemVerilog unifies them as `logic` (driven by any source). Using `reg` for output ports and `wire` for combinational intermediates is not idiomatic SystemVerilog and will cause linter warnings in strict synthesis flows. Mixing `reg`/`wire` with `logic` in the same design can cause subtle assignment-direction conflicts.

### Corrected version
```systemverilog
output logic signed [31:0] out
logic signed [15:0] product;
```

---

## mac_correct.v — Simulation Log

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

All 6 test cases pass. `mac_correct.v` compiles cleanly with `iverilog -g2012` and produces correct signed accumulation for both positive and negative operands.
