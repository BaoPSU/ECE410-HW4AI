// crossbar_mac.sv — LLM-generated (Claude Sonnet 4.6) for ECE 410/510 CF06
// 4×4 binary-weight crossbar MAC unit
// out[j] = Σ_i weight[i][j] × in[i],  weight ∈ {+1, −1}
//
// weight_in is a flat 16-bit register: bit (4*i + j) encodes weight[i][j]
//   bit = 1  →  weight = +1
//   bit = 0  →  weight = −1
//
// Outputs are registered; result appears one cycle after inputs and weights are stable.

`timescale 1ns/1ps
module crossbar_mac (
    input  logic              clk,
    input  logic              rst_n,
    input  logic              weight_load,   // assert to latch weight_in
    input  logic [15:0]       weight_in,     // flat weight matrix, bit 4*i+j = w[i][j]
    input  logic signed [7:0] in0, in1, in2, in3,   // 8-bit signed activations
    output logic signed [9:0] out0, out1, out2, out3 // 10-bit signed accumulators
);

    logic [15:0] wreg;

    // Weight register
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) wreg <= 16'h0;
        else if (weight_load) wreg <= weight_in;
    end

    // Sign-extend 8-bit inputs to 10 bits (continuous assigns, no always block)
    wire signed [9:0] e0 = {{2{in0[7]}}, in0};
    wire signed [9:0] e1 = {{2{in1[7]}}, in1};
    wire signed [9:0] e2 = {{2{in2[7]}}, in2};
    wire signed [9:0] e3 = {{2{in3[7]}}, in3};

    // Combinational crossbar MAC — fully unrolled
    // out[j] = w[0][j]*e0 + w[1][j]*e1 + w[2][j]*e2 + w[3][j]*e3
    wire signed [9:0] sum0 = (wreg[ 0] ? e0 : -e0) + (wreg[ 4] ? e1 : -e1)
                           + (wreg[ 8] ? e2 : -e2) + (wreg[12] ? e3 : -e3);
    wire signed [9:0] sum1 = (wreg[ 1] ? e0 : -e0) + (wreg[ 5] ? e1 : -e1)
                           + (wreg[ 9] ? e2 : -e2) + (wreg[13] ? e3 : -e3);
    wire signed [9:0] sum2 = (wreg[ 2] ? e0 : -e0) + (wreg[ 6] ? e1 : -e1)
                           + (wreg[10] ? e2 : -e2) + (wreg[14] ? e3 : -e3);
    wire signed [9:0] sum3 = (wreg[ 3] ? e0 : -e0) + (wreg[ 7] ? e1 : -e1)
                           + (wreg[11] ? e2 : -e2) + (wreg[15] ? e3 : -e3);

    // Output register
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out0 <= '0; out1 <= '0; out2 <= '0; out3 <= '0;
        end else begin
            out0 <= sum0; out1 <= sum1; out2 <= sum2; out3 <= sum3;
        end
    end

endmodule
