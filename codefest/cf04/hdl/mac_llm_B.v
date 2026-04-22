// LLM B: GPT-4o (gpt-4o-2024-11-20)
// Same prompt as LLM A.

module mac (
    input clk,
    input rst,
    input [7:0] a,
    input [7:0] b,
    output reg [31:0] out
);
    wire [15:0] product;
    assign product = a * b;

    always @(posedge clk) begin
        if (rst)
            out <= 32'b0;
        else
            out <= out + {{16{product[15]}}, product};
    end
endmodule
