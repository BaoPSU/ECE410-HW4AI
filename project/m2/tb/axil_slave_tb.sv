// axil_slave_tb.sv
// AXI4-Lite interface testbench for axil_slave.sv
// ECE 410/510 Spring 2026 — Bao Nguyen
//
// Exercises ≥1 complete write transaction and ≥1 complete read/response transaction.
// Full flow: load pixel → load centroid[0] → write CTRL.start → poll STATUS → read results.

`timescale 1ns/1ps

module axil_slave_tb;

    localparam int ADDR_W  = 12;
    localparam int K       = 16;
    localparam int D       = 3;
    localparam int LABEL_W = 4;

    logic              clk, rst_n;
    logic [ADDR_W-1:0] awaddr;
    logic              awvalid, awready;
    logic [31:0]       wdata;
    logic [3:0]        wstrb;
    logic              wvalid, wready;
    logic [1:0]        bresp;
    logic              bvalid, bready;
    logic [ADDR_W-1:0] araddr;
    logic              arvalid, arready;
    logic [31:0]       rdata;
    logic [1:0]        rresp;
    logic              rvalid, rready;

    axil_slave #(.ADDR_W(ADDR_W), .K(K), .D(D), .LABEL_W(LABEL_W)) dut (.*);

    initial clk = 1'b0;
    always  #5 clk = ~clk;

    // ── IEEE 754 helpers ──────────────────────────────────────────────────
    function automatic real f32_to_real(input logic [31:0] f);
        logic [63:0] f64;
        int e32, e64;
        if (f[30:23] == 8'h00) return 0.0;
        if (f[30:23] == 8'hFF) return (f[31] ? -1.0e38 : 1.0e38);
        e32 = int'({1'b0, f[30:23]});
        e64 = e32 - 127 + 1023;
        f64 = {f[31], 11'(e64), {f[22:0], 29'b0}};
        return $bitstoreal(f64);
    endfunction

    function automatic logic [31:0] real_to_f32(input real r);
        logic [63:0] f64;
        int e64, e32;
        if (r == 0.0) return 32'h0000_0000;
        f64 = $realtobits(r);
        e64 = int'(f64[62:52]);
        e32 = e64 - 1023 + 127;
        return {f64[63], 8'(e32), f64[51:29]};
    endfunction

    // ── AXI4-Lite tasks ───────────────────────────────────────────────────
    // Write: slave starts with awready=wready=1 (WR_IDLE).
    // Present AW+W simultaneously; handshake on the first posedge.
    // Slave sets bvalid on the same posedge; response seen the next posedge.
    task automatic axil_write(input logic [ADDR_W-1:0] addr,
                               input logic [31:0]       data);
        @(negedge clk);
        awaddr  = addr;  wdata = data;  wstrb = 4'hF;
        awvalid = 1'b1;  wvalid = 1'b1; bready = 1'b1;
        @(posedge clk);               // Cycle 1: slave latches AW+W, sets bvalid
        @(negedge clk);
        awvalid = 1'b0;  wvalid = 1'b0;
        @(posedge clk);               // Cycle 2: slave sees bready→clears bvalid
        @(negedge clk);
        bready = 1'b0;
    endtask

    // Read: slave starts with arready=1 (RD_IDLE).
    // Present AR; data valid one posedge after arready handshake.
    task automatic axil_read(input  logic [ADDR_W-1:0] addr,
                              output logic [31:0]       data);
        @(negedge clk);
        araddr  = addr;  arvalid = 1'b1; rready = 1'b1;
        @(posedge clk); #1;           // Cycle 1: slave latches AR, rdata/rvalid set
        data    = rdata;              // capture (rvalid=1 here)
        @(negedge clk);
        arvalid = 1'b0;
        @(posedge clk);               // Cycle 2: slave sees rready→clears rvalid
        @(negedge clk);
        rready  = 1'b0;
    endtask

    // ── Test sequence ─────────────────────────────────────────────────────
    logic [31:0] rd_val;
    int          errors;
    integer      poll_cnt;

    initial begin
        awaddr = '0; awvalid = 0; wdata = '0; wstrb = 4'hF; wvalid = 0; bready = 0;
        araddr = '0; arvalid = 0; rready = 0;
        errors = 0;
        rst_n  = 0;
        repeat(4) @(posedge clk);
        rst_n = 1;
        repeat(2) @(posedge clk);

        $display("=== AXI4-Lite interface test ===");

        // ── WRITE TRANSACTIONS ────────────────────────────────────────────
        $display("[W] Pixel R=200.0  G=100.0  B=50.0");
        axil_write(12'h008, real_to_f32(200.0));  // PIX_R
        axil_write(12'h00C, real_to_f32(100.0));  // PIX_G
        axil_write(12'h010, real_to_f32(50.0));   // PIX_B

        $display("[W] Centroid[0] = (199.0, 99.0, 51.0)  expected dist=3.0");
        axil_write(12'h014, real_to_f32(199.0));  // CENT[0][R]
        axil_write(12'h018, real_to_f32(99.0));   // CENT[0][G]
        axil_write(12'h01C, real_to_f32(51.0));   // CENT[0][B]

        $display("[W] CTRL.start = 1");
        axil_write(12'h000, 32'h0000_0001);

        // ── READ TRANSACTIONS ─────────────────────────────────────────────
        // Poll STATUS.done up to 20 times (engine has 1-cycle latency,
        // so should be set within 2-3 poll cycles)
        $display("[R] Polling STATUS...");
        rd_val   = 32'h0;
        poll_cnt = 0;
        for (poll_cnt = 0; (poll_cnt < 20) && (!rd_val[0]); poll_cnt = poll_cnt + 1)
            axil_read(12'h004, rd_val);

        $display("[R] STATUS = 0x%08h  done=%0b  polls=%0d",
                 rd_val, rd_val[0], poll_cnt);
        if (!rd_val[0]) begin
            $error("STATUS.done never set after %0d polls", poll_cnt);
            errors = errors + 1;
        end

        // Read RESULT_LABEL
        axil_read(12'h100, rd_val);
        $display("[R] RESULT_LABEL = %0d", rd_val[LABEL_W-1:0]);
        if (rd_val[LABEL_W-1:0] !== 4'd0) begin
            $error("  LABEL  got=%0d  expected=0", rd_val[LABEL_W-1:0]);
            errors = errors + 1;
        end else
            $display("  label = 0  PASS");

        // Read RESULT_DIST
        axil_read(12'h104, rd_val);
        $display("[R] RESULT_DIST = 0x%08h  (%.4f)", rd_val, f32_to_real(rd_val));
        if (rd_val !== real_to_f32(3.0)) begin
            $error("  DIST  got=%.4f  expected=3.0", f32_to_real(rd_val));
            errors = errors + 1;
        end else
            $display("  min_dist = 3.0  PASS");

        // ── Summary ───────────────────────────────────────────────────────
        repeat(2) @(posedge clk);
        if (errors == 0)
            $display("=== ALL AXI4-Lite TESTS PASSED ===");
        else
            $display("=== %0d TEST(S) FAILED ===", errors);
        $finish;
    end

    initial begin #500000; $error("WATCHDOG timeout"); $finish; end

endmodule
