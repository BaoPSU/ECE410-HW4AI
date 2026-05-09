# CF06 CLLM — Spoken Script (No Slides)
**Prompt:** "Explain your codefest 6 CLLM design, the testbench, and the simulation results."
~5 minutes, verbal only

---

## The Design

For CF06 CLLM I had Claude Sonnet 4.6 generate a 4-by-4 binary-weight crossbar MAC unit in SystemVerilog.

So about the design. The module takes four 8-bit signed inputs, a 4-by-4 weight matrix where each weight is either plus-one or minus-one, and produces four 10-bit signed outputs. Each clock cycle, every output computes a dot product, so basically you multiply each input by its weight at that row-column intersection and add them up. That's what the crossbar does, a grid of wires where rows carry inputs, columns carry outputs, and the weights sit at the intersections.

The module has three stages. First stage is the weight register, it's a flip-flop that latches the full weight matrix when you pulse weight_load high. Claude packed the entire 4-by-4 matrix into a single 16-bit flat register, where bit 4i plus j holds weight[i][j]. For an example, bit zero is weight[0][0], bit four would be weight[1][0], and so on. I asked Claude why it went with a flat register and it said it actually loads the entire matrix in exactly one clock cycle. Like if you loaded row by row, that would've taken four cycles and you'd need an address counter to track which row you're on, so the flat register just keeps it simple. That's actually a co-design decision, the hardware was structured around what the algorithm needed.

The second stage is the combinational MAC, those are just wires, no clock, which sign-extends the inputs to 10 bits and computes all four dot products at the same time. Then the third stage is the output register, which latches the results on the next rising edge.

As for the output bit width, worst case is four inputs at plus or minus 127, so 4 times 127 is 508. And 10-bit signed goes up to 511, which clears the threshold we need.

---

## The Testbench

So about the testbench. Claude loaded the weight matrix from the assignment spec, which is plus-one, minus-one, plus-one, minus-one on row zero, plus-one, plus-one, minus-one, minus-one on row one, and so on, and then it applied inputs of 10, 20, 30, and 40.

Before running the simulation I hand-calculated the expected outputs, so for example, column zero, you get plus-ten from row 0, plus-twenty from row 1, and then minus-thirty and minus-forty from rows 2 and 3, and so that adds up to minus-40. I did the same for all four columns and got minus-40, zero, minus-20, and minus-20.

One thing about the timing Claude had to get right, and the output shows up two cycles after you assert weight_load, not one. Basically here's why, so on the first rising edge after weight_load, the weight register latches the new weights, but the output register clocks on that same edge and it's still using the old weights. And so the correct output only appears one cycle later. The testbench explicitly waits two cycles before reading the outputs.

---

## The Simulation Results

All four outputs match what I expected. Out-zero is minus-40, out-one is zero, out-two and out-three are both minus-20, exactly what my hand calculation said. So 4 out of 4, that's pretty good. Thanks.
