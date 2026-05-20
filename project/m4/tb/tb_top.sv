// tb_top.sv
// M3 end-to-end co-simulation testbench
// ECE 410/510 Spring 2026 - Bao Nguyen
//
// Drives the integrated top module ENTIRELY through its AXI4-Lite interface.
// No direct probing of the compute core ports. The testbench:
//
//   1. Resets the design
//   2. Writes pixel + 16 centroids via AXI4-Lite writes
//   3. Pulses CTRL.start
//   4. Polls STATUS until done=1
//   5. Reads RESULT_LABEL and RESULT_DIST
//   6. Compares against a hand-computed reference (independent of the DUT)
//   7. Prints PASS / FAIL
//
// Kernel scale: K=16 RGB centroids matches the M1-profiled K-Means kernel.

`timescale 1ns/1ps

module tb_top;

    localparam int CLK_PERIOD = 10;   // 100 MHz
    localparam int K          = 16;
    localparam int D          = 3;
    localparam int DATA_W     = 8;
    localparam int DIST_W     = 18;
    localparam int LABEL_W    = 4;
    localparam int ADDR_W     = 12;

    // AXI4-Lite signals
    logic               clk = 0;
    logic               rst_n;

    logic [ADDR_W-1:0]  awaddr;
    logic               awvalid;
    logic               awready;
    logic [31:0]        wdata;
    logic [3:0]         wstrb;
    logic               wvalid;
    logic               wready;
    logic [1:0]         bresp;
    logic               bvalid;
    logic               bready;

    logic [ADDR_W-1:0]  araddr;
    logic               arvalid;
    logic               arready;
    logic [31:0]        rdata;
    logic [1:0]         rresp;
    logic               rvalid;
    logic               rready;

    // DUT
    top #(
        .ADDR_W  (ADDR_W),
        .K       (K),
        .D       (D),
        .DATA_W  (DATA_W),
        .DIST_W  (DIST_W),
        .LABEL_W (LABEL_W)
    ) dut (
        .clk(clk), .rst_n(rst_n),
        .awaddr(awaddr), .awvalid(awvalid), .awready(awready),
        .wdata(wdata), .wstrb(wstrb), .wvalid(wvalid), .wready(wready),
        .bresp(bresp), .bvalid(bvalid), .bready(bready),
        .araddr(araddr), .arvalid(arvalid), .arready(arready),
        .rdata(rdata), .rresp(rresp), .rvalid(rvalid), .rready(rready)
    );

    // Clock
    always #(CLK_PERIOD/2) clk = ~clk;

    // ── Test data: 1 pixel + 16 centroids (K=16, D=3, 8-bit RGB) ──────────
    // Pixel = (200, 100, 50)
    // Centroid 7 is exactly the pixel (distance = 0), so expected label = 7.
    logic [7:0] pixel_R = 8'd200, pixel_G = 8'd100, pixel_B = 8'd50;

    logic [7:0] cent_R [0:K-1];
    logic [7:0] cent_G [0:K-1];
    logic [7:0] cent_B [0:K-1];

    task automatic init_centroids;
        // K=16 RGB centroids. Centroid 7 = pixel exactly (kdist=0, expected winner).
        cent_R[0]  = 8'd10;   cent_G[0]  = 8'd20;   cent_B[0]  = 8'd30;
        cent_R[1]  = 8'd30;   cent_G[1]  = 8'd40;   cent_B[1]  = 8'd50;
        cent_R[2]  = 8'd50;   cent_G[2]  = 8'd60;   cent_B[2]  = 8'd70;
        cent_R[3]  = 8'd70;   cent_G[3]  = 8'd80;   cent_B[3]  = 8'd90;
        cent_R[4]  = 8'd90;   cent_G[4]  = 8'd100;  cent_B[4]  = 8'd110;
        cent_R[5]  = 8'd110;  cent_G[5]  = 8'd120;  cent_B[5]  = 8'd130;
        cent_R[6]  = 8'd130;  cent_G[6]  = 8'd140;  cent_B[6]  = 8'd150;
        cent_R[7]  = 8'd200;  cent_G[7]  = 8'd100;  cent_B[7]  = 8'd50;  // EXACT MATCH
        cent_R[8]  = 8'd170;  cent_G[8]  = 8'd180;  cent_B[8]  = 8'd190;
        cent_R[9]  = 8'd190;  cent_G[9]  = 8'd200;  cent_B[9]  = 8'd210;
        cent_R[10] = 8'd210;  cent_G[10] = 8'd220;  cent_B[10] = 8'd230;
        cent_R[11] = 8'd230;  cent_G[11] = 8'd240;  cent_B[11] = 8'd250;
        cent_R[12] = 8'd250;  cent_G[12] = 8'd10;   cent_B[12] = 8'd25;
        cent_R[13] = 8'd5;    cent_G[13] = 8'd15;   cent_B[13] = 8'd25;
        cent_R[14] = 8'd25;   cent_G[14] = 8'd35;   cent_B[14] = 8'd45;
        cent_R[15] = 8'd45;   cent_G[15] = 8'd55;   cent_B[15] = 8'd65;
    endtask

    // ── Independent reference (hand-computed in SW) ────────────────────────
    int                  ref_kdist [0:K-1];
    int                  ref_min;
    int                  ref_label;

    // ── Captured outputs ───────────────────────────────────────────────────
    int                  read_label_int;
    int                  read_dist_int;
    int                  start_cycle, done_cycle;

    // ── AXI helper tasks ───────────────────────────────────────────────────
    task automatic axi_write(input logic [ADDR_W-1:0] addr,
                             input logic [31:0] data);
        @(posedge clk);
        awaddr  <= addr;
        awvalid <= 1'b1;
        wdata   <= data;
        wstrb   <= 4'hF;
        wvalid  <= 1'b1;
        bready  <= 1'b1;
        @(posedge clk);
        // Wait for both handshakes
        while (!(awready && awvalid && wready && wvalid)) @(posedge clk);
        awvalid <= 1'b0;
        wvalid  <= 1'b0;
        // Wait for bresp
        while (!bvalid) @(posedge clk);
        @(posedge clk);
        bready  <= 1'b0;
    endtask

    task automatic axi_read(input  logic [ADDR_W-1:0] addr,
                            output logic [31:0]       data);
        @(posedge clk);
        araddr  <= addr;
        arvalid <= 1'b1;
        rready  <= 1'b1;
        @(posedge clk);
        while (!(arready && arvalid)) @(posedge clk);
        arvalid <= 1'b0;
        while (!rvalid) @(posedge clk);
        data = rdata;
        @(posedge clk);
        rready <= 1'b0;
    endtask

    // ── Main ───────────────────────────────────────────────────────────────
    initial begin
        $dumpfile("tb_top.vcd");
        $dumpvars(0, tb_top);

        // Init
        rst_n   = 0;
        awaddr  = 0; awvalid = 0;
        wdata   = 0; wstrb   = 0; wvalid = 0;
        bready  = 0;
        araddr  = 0; arvalid = 0; rready = 0;

        // Initialize centroid arrays (must happen before the SW reference compute)
        init_centroids();

        // Compute reference (independent SW model). dR/dG/dB declared at procedural
        // scope so the assignments run every iteration (initializer in the for-body
        // would be a one-time static init under iverilog).
        ref_min   = 32'h7FFFFFFF;
        ref_label = 0;
        begin : ref_compute
            int dR, dG, dB;
            for (int k = 0; k < K; k++) begin
                dR = $signed({1'b0, pixel_R}) - $signed({1'b0, cent_R[k]});
                dG = $signed({1'b0, pixel_G}) - $signed({1'b0, cent_G[k]});
                dB = $signed({1'b0, pixel_B}) - $signed({1'b0, cent_B[k]});
                ref_kdist[k] = dR*dR + dG*dG + dB*dB;
                if (ref_kdist[k] < ref_min) begin
                    ref_min   = ref_kdist[k];
                    ref_label = k;
                end
            end
        end

        $display("================================================================");
        $display(" M3 end-to-end co-simulation: top module via AXI4-Lite");
        $display("================================================================");
        $display(" Pixel = (R=%0d, G=%0d, B=%0d)", pixel_R, pixel_G, pixel_B);
        $display(" Independent SW reference:");
        for (int k = 0; k < K; k++) begin
            $display("   kdist[%2d] = %0d   centroid=(%0d,%0d,%0d)",
                     k, ref_kdist[k], cent_R[k], cent_G[k], cent_B[k]);
        end
        $display(" Expected label = %0d, min_dist = %0d", ref_label, ref_min);
        $display("----------------------------------------------------------------");

        // Reset
        repeat (5) @(posedge clk);
        rst_n <= 1;
        repeat (3) @(posedge clk);

        // Stage 1: write pixel (0x008)
        $display("[H->A] WRITE PIXEL @ 0x008");
        axi_write(12'h008, {8'h00, pixel_R, pixel_G, pixel_B});

        // Stage 2: write all 16 centroids (0x010 + k*4)
        $display("[H->A] WRITE 16 CENTROIDS @ 0x010..0x04C");
        for (int k = 0; k < K; k++) begin
            axi_write((ADDR_W)'(12'h010 + k * 4),
                      {8'h00, cent_R[k], cent_G[k], cent_B[k]});
        end

        // Stage 3: pulse CTRL.start
        $display("[H->A] WRITE CTRL.start @ 0x000");
        start_cycle = $time / CLK_PERIOD;
        axi_write(12'h000, 32'h0000_0001);

        // Stage 4: poll STATUS @ 0x004 until done
        $display("[H<-A] POLL STATUS until done");
        begin
            logic [31:0] sts;
            int polls = 0;
            sts = 0;
            while (sts[0] == 1'b0 && polls < 100) begin
                axi_read(12'h004, sts);
                polls++;
                if (sts[0]) begin
                    done_cycle = $time / CLK_PERIOD;
                    $display("       STATUS = 0x%08h  done=1  busy=%b  polls=%0d",
                             sts, sts[1], polls);
                end
            end
            if (sts[0] !== 1'b1) begin
                $display(" FAIL: STATUS.done never asserted after %0d polls", polls);
                $finish;
            end
        end

        // Stage 5: read RESULT_LABEL @ 0x100
        $display("[H<-A] READ RESULT_LABEL @ 0x100");
        begin
            logic [31:0] tmp;
            axi_read(12'h100, tmp);
            read_label_int = tmp[3:0];
            $display("       RESULT_LABEL = %0d", read_label_int);
        end

        // Stage 6: read RESULT_DIST @ 0x104
        $display("[H<-A] READ RESULT_DIST @ 0x104");
        begin
            logic [31:0] tmp;
            axi_read(12'h104, tmp);
            read_dist_int = tmp[DIST_W-1:0];
            $display("       RESULT_DIST  = %0d", read_dist_int);
        end

        // Stage 7: compare
        $display("----------------------------------------------------------------");
        $display(" DUT  label = %0d, dist = %0d", read_label_int, read_dist_int);
        $display(" REF  label = %0d, dist = %0d", ref_label,      ref_min);
        $display(" Cycles from start to done (approx) = %0d", done_cycle - start_cycle);

        if (read_label_int == ref_label && read_dist_int == ref_min) begin
            $display("================================================================");
            $display(" PASS");
            $display("================================================================");
        end else begin
            $display("================================================================");
            $display(" FAIL");
            $display("================================================================");
        end

        $finish;
    end

    // Watchdog
    initial begin
        #(CLK_PERIOD * 5000);
        $display(" FAIL: testbench watchdog timeout");
        $finish;
    end

endmodule
