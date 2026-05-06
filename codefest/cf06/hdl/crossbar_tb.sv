// crossbar_tb.sv — Testbench for CF06 CLLM crossbar MAC unit
//
// Weight matrix (row=input i, col=output j):
//   [[+1,-1,+1,-1],
//    [+1,+1,-1,-1],
//    [-1,+1,+1,-1],
//    [-1,-1,-1,+1]]
//
// Inputs: in0=10, in1=20, in2=30, in3=40
//
// Hand-calculated expected outputs:
//   out0 = (+1)(10)+(+1)(20)+(-1)(30)+(-1)(40) = 10+20-30-40 = -40
//   out1 = (-1)(10)+(+1)(20)+(+1)(30)+(-1)(40) = -10+20+30-40 =  0
//   out2 = (+1)(10)+(-1)(20)+(+1)(30)+(-1)(40) = 10-20+30-40  = -20
//   out3 = (-1)(10)+(-1)(20)+(-1)(30)+(+1)(40) = -10-20-30+40 = -20

`timescale 1ns/1ps
module crossbar_tb;

    logic              clk, rst_n, weight_load;
    logic [15:0]       weight_in;
    logic signed [7:0] in0, in1, in2, in3;
    logic signed [9:0] out0, out1, out2, out3;

    crossbar_mac dut (
        .clk(clk), .rst_n(rst_n),
        .weight_load(weight_load), .weight_in(weight_in),
        .in0(in0), .in1(in1), .in2(in2), .in3(in3),
        .out0(out0), .out1(out1), .out2(out2), .out3(out3)
    );

    // 10 ns period clock
    initial clk = 0;
    always #5 clk = ~clk;

    integer pass_cnt, fail_cnt;

    initial begin
        $dumpfile("crossbar_tb.vcd");
        $dumpvars(0, crossbar_tb);
        pass_cnt = 0; fail_cnt = 0;

        // Reset
        rst_n = 0; weight_load = 0; weight_in = 16'h0;
        in0 = 8'sd0; in1 = 8'sd0; in2 = 8'sd0; in3 = 8'sd0;
        @(posedge clk); #1;
        rst_n = 1;
        @(posedge clk); #1;

        // Load weight matrix and apply inputs.
        //
        // weight_in bit encoding:  bit (4*i + j) = weight[i][j],  1=+1 / 0=−1
        //   row 0: [+1,-1,+1,-1]  -> bits [3:0]   = 4'b0101  (j3=0,j2=1,j1=0,j0=1)
        //   row 1: [+1,+1,-1,-1]  -> bits [7:4]   = 4'b0011  (j3=0,j2=0,j1=1,j0=1)
        //   row 2: [-1,+1,+1,-1]  -> bits [11:8]  = 4'b0110  (j3=0,j2=1,j1=1,j0=0)
        //   row 3: [-1,-1,-1,+1]  -> bits [15:12] = 4'b1000  (j3=1,j2=0,j1=0,j0=0)
        weight_in   = {4'b1000, 4'b0110, 4'b0011, 4'b0101};
        weight_load = 1;
        in0 = 8'sd10; in1 = 8'sd20; in2 = 8'sd30; in3 = 8'sd40;

        @(posedge clk); #1;   // weights captured into wreg; out latches old value
        weight_load = 0;

        @(posedge clk); #1;   // out latches MAC result with new weights and current inputs

        $display("=== CF06 CLLM — 4x4 Crossbar MAC Simulation ===");
        $display("Weight matrix (row=input, col=output):");
        $display("  row0=[+1,-1,+1,-1]  row1=[+1,+1,-1,-1]");
        $display("  row2=[-1,+1,+1,-1]  row3=[-1,-1,-1,+1]");
        $display("Inputs: [in0,in1,in2,in3] = [10, 20, 30, 40]");
        $display("Expected: [out0,out1,out2,out3] = [-40, 0, -20, -20]");
        $display("---");

        if ($signed(out0) == -40) begin
            $display("out0 = %4d   PASS", $signed(out0)); pass_cnt = pass_cnt + 1;
        end else begin
            $display("out0 = %4d   FAIL (expected -40)", $signed(out0)); fail_cnt = fail_cnt + 1;
        end

        if ($signed(out1) == 0) begin
            $display("out1 = %4d   PASS", $signed(out1)); pass_cnt = pass_cnt + 1;
        end else begin
            $display("out1 = %4d   FAIL (expected 0)", $signed(out1)); fail_cnt = fail_cnt + 1;
        end

        if ($signed(out2) == -20) begin
            $display("out2 = %4d   PASS", $signed(out2)); pass_cnt = pass_cnt + 1;
        end else begin
            $display("out2 = %4d   FAIL (expected -20)", $signed(out2)); fail_cnt = fail_cnt + 1;
        end

        if ($signed(out3) == -20) begin
            $display("out3 = %4d   PASS", $signed(out3)); pass_cnt = pass_cnt + 1;
        end else begin
            $display("out3 = %4d   FAIL (expected -20)", $signed(out3)); fail_cnt = fail_cnt + 1;
        end

        $display("---");
        $display("Result: %0d/4 PASS", pass_cnt);
        if (fail_cnt == 0)
            $display("ALL TESTS PASSED");
        else
            $display("%0d TEST(S) FAILED", fail_cnt);

        $finish;
    end

endmodule
