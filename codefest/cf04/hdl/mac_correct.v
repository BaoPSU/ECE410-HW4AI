// mac_correct.v — corrected synthesizable SystemVerilog MAC unit
// Fixes applied vs mac_llm_B.v:
//   1. always_ff instead of always @(posedge clk)
//   2. signed qualifier on all ports and intermediate wire
//   3. logic instead of reg/wire

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
