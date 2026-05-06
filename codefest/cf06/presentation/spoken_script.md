# CF06 CLLM — Spoken Script (No Slides)
~5 minutes, verbal only

---

So for CF06 CLLM I had Claude Sonnet 4.6 generate a 4-by-4 binary-weight crossbar MAC unit in SystemVerilog, and then I wrote the testbench myself and ran the simulation. All four outputs came out exactly right. I'll walk you through the design, the choices I made, and why I know it's working.

---

**The design**

So about the module — the idea is pretty simple. You have four 8-bit signed inputs, a 4-by-4 weight matrix where every weight is either plus-one or minus-one, and four output accumulators. Each clock cycle, every output computes a dot product — you multiply each input by its weight and sum them up. That's it.

I structured it as three stages. First is the weight register — a flip-flop that latches the weight matrix when you pulse weight_load. Second is the combinational MAC — just wires, no clock, computes all four dot products simultaneously. And then the output register latches the results on the next rising edge.

---

**The choices I made**

For example, the weight encoding — I packed the entire 4-by-4 matrix into one 16-bit flat register. The rule is bit 4i plus j holds weight[i][j], where 1 means plus-one and 0 means minus-one. I chose this because it loads the entire weight matrix in exactly one clock cycle with one signal. The alternative would be loading row by row — like, that's four cycles and you need an address counter on top of it. The flat register keeps it simple.

And then about the output bit width — I chose 10-bit signed. For example, the worst case is four inputs at plus or minus 127, so 4 times 127 is roughly 508. 10-bit signed goes up to 511, so basically that's exactly enough. Not too wide, not overflowing.

And one choice I had to make that wasn't in the spec — iverilog 12 doesn't support variable bit-selects on unpacked arrays inside always blocks. And so I switched to individual scalar ports and wires instead. For example, instead of in_data[0][7] for the sign bit, I pulled each input out to its own wire and did the sign extension there. It actually made the interface cleaner — each port is explicit, nothing is hidden in an array.

---

**Why I know it's working**

So about the testbench — before I ran anything I hand-calculated the expected outputs. The weight matrix from the assignment is plus-one, minus-one, plus-one, minus-one on row zero, and so on. Inputs are 10, 20, 30, 40. For example, column zero — plus-ten, plus-twenty, minus-thirty, minus-forty — that's exactly minus-40. I did that for all four columns before touching the simulator.

And then about the timing — the output shows up two cycles after weight_load, not one. Basically here's why: the weight register and output register both clock on the same rising edge. And so on the first edge after weight_load, the weights latch — but the output register is still sampling the MAC with the old weights. One cycle later the MAC is using the new weights, and then the output register captures the correct result. If I hadn't accounted for that, I would've read zeros and thought the design was broken. The testbench explicitly waits two cycles.

The simulation confirmed it — out-zero came out minus-40, out-one zero, out-two and out-three both minus-20. Exactly what the hand calculation said. 4 out of 4.

---

**Wrap up**

So basically — the design works because the choices were made for specific reasons. Flat weight register for single-cycle loading. Scalar ports for iverilog compatibility. 10-bit outputs for correct range. 2-cycle testbench timing because that's what the pipeline actually does. Every output matches the hand calculation. Thanks.
