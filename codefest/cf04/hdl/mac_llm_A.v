// LLM A: Claude Sonnet 4.6
// Prompt: Generate a synthesizable SystemVerilog MAC module.
//   Module name: mac
//   Inputs: clk (1-bit), rst (1-bit, active-high synchronous reset),
//           a (8-bit signed), b (8-bit signed)
//   Output: out (32-bit signed accumulator)
//   Behavior: On each rising clock edge: if rst is high, set out to 0;
//             else add a*b to out.
//   Constraints: Synthesizable SystemVerilog only. No initial blocks,
//                no $display, no delays (#). Use always_ff.

module mac (
    input  logic        clk,
    input  logic        rst,
    input  logic signed [7:0]  a,
    input  logic signed [7:0]  b,
    output logic signed [31:0] out
);
    logic signed [15:0] product;

    always_comb product = a * b;

    always_ff @(posedge clk) begin
        if (rst)
            out <= 32'sd0;
        else
            out <= out + {{16{product[15]}}, product};
    end
endmodule
