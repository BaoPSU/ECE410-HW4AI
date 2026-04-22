// LLM B: Gemini 2.5 Flash (Google Workspace / PSU Enterprise)
// Same prompt as LLM A.

module mac (
    input  logic              clk,
    input  logic              rst,
    input  logic signed [7:0] a,
    input  logic signed [7:0] b,
    output logic signed [31:0] out
);
    // Intermediate 16-bit signed product
    logic signed [15:0] product;
    assign product = a * b;

    always_ff @(posedge clk) begin
        if (rst) begin
            out <= 32'sd0;
        end else begin
            // Sign-extension happens automatically: 16-bit signed product
            // is sign-extended to 32 bits before addition.
            out <= out + product;
        end
    end

endmodule
