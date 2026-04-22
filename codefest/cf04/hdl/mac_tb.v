`timescale 1ns/1ps
module mac_tb;
    logic       clk, rst;
    logic signed [7:0]  a, b;
    logic signed [31:0] out;

    mac dut (.clk(clk), .rst(rst), .a(a), .b(b), .out(out));

    initial clk = 0;
    always #5 clk = ~clk;

    integer fail = 0;

    task check;
        input signed [31:0] expected;
        input [127:0] label;
        begin
            if (out !== expected) begin
                $display("FAIL [%0s]: got %0d, expected %0d", label, out, expected);
                fail = fail + 1;
            end else
                $display("PASS [%0s]: out = %0d", label, out);
        end
    endtask

    initial begin
        $dumpfile("mac_tb.vcd");
        $dumpvars(0, mac_tb);

        // Reset for one cycle
        rst = 1; a = 0; b = 0;
        @(posedge clk); #1;

        // a=3, b=4 for 3 cycles
        rst = 0; a = 8'sd3; b = 8'sd4;
        @(posedge clk); #1; check(32'sd12,  "a=3,b=4 cyc1");
        @(posedge clk); #1; check(32'sd24,  "a=3,b=4 cyc2");
        @(posedge clk); #1; check(32'sd36,  "a=3,b=4 cyc3");

        // Synchronous reset
        rst = 1;
        @(posedge clk); #1; check(32'sd0, "rst");

        // a=-5, b=2 for 2 cycles
        rst = 0; a = -8'sd5; b = 8'sd2;
        @(posedge clk); #1; check(-32'sd10, "a=-5,b=2 cyc1");
        @(posedge clk); #1; check(-32'sd20, "a=-5,b=2 cyc2");

        if (fail == 0)
            $display("ALL TESTS PASSED");
        else
            $display("%0d TEST(S) FAILED", fail);

        $finish;
    end
endmodule
