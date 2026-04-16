// distance_engine_tb.sv
// Testbench for distance_engine.sv
// ECE 410/510 Spring 2026 — Bao Nguyen

`timescale 1ns/1ps

module distance_engine_tb;

    localparam int K       = 16;
    localparam int D       = 3;
    localparam int LABEL_W = 4;

    logic               clk, rst_n, start;
    logic [31:0]        pixel     [0:D-1];
    logic [31:0]        centroids [0:K-1][0:D-1];
    logic               done;
    logic [31:0]        min_dist;
    logic [LABEL_W-1:0] label;

    distance_engine #(.K(K), .D(D), .LABEL_W(LABEL_W)) dut (
        .clk, .rst_n, .start,
        .pixel, .centroids,
        .done, .min_dist, .label
    );

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

    // ── Helpers ───────────────────────────────────────────────────────────
    task automatic set_pixel(input real r, g, b);
        pixel[0] = real_to_f32(r);
        pixel[1] = real_to_f32(g);
        pixel[2] = real_to_f32(b);
    endtask

    task automatic set_centroid(input int k, input real r, g, b);
        centroids[k][0] = real_to_f32(r);
        centroids[k][1] = real_to_f32(g);
        centroids[k][2] = real_to_f32(b);
    endtask

    task automatic clear_centroids();
        for (int k = 0; k < K; k++)
            for (int d = 0; d < D; d++)
                centroids[k][d] = 32'h0;
    endtask

    // Drive start=1 for one cycle then check outputs.
    // The DUT has 1-cycle latency: done=1 and outputs valid on the posedge
    // that captures start=1.
    task automatic run_and_check(input int exp_label, input real exp_dist);
        @(negedge clk);
        start = 1'b1;
        @(posedge clk); #1; // done, min_dist, label registered on this edge
        if (!done) begin
            $error("  done never asserted");
        end else begin
            if (label !== LABEL_W'(exp_label))
                $error("  LABEL  got=%0d  expected=%0d", label, exp_label);
            else
                $display("  label    = %0d  PASS", label);

            if (min_dist !== real_to_f32(exp_dist))
                $error("  DIST   got=%.4f (0x%08h)  expected=%.4f (0x%08h)",
                       f32_to_real(min_dist), min_dist,
                       exp_dist, real_to_f32(exp_dist));
            else
                $display("  min_dist = %.2f  PASS", f32_to_real(min_dist));
        end
        @(negedge clk); start = 1'b0;
    endtask

    // ── Tests ─────────────────────────────────────────────────────────────
    initial begin
        rst_n = 0; start = 0;
        clear_centroids();
        pixel[0] = 0; pixel[1] = 0; pixel[2] = 0;
        repeat(4) @(posedge clk);
        rst_n = 1;
        repeat(2) @(posedge clk);

        // Test 1: pixel=(200,100,50)  cent[0]=(199,99,51)→dist=3  rest=(0,0,0)→dist=52500
        $display("=== Test 1: nearest=centroid[0], dist=3.0 ===");
        clear_centroids();
        set_pixel(200.0, 100.0, 50.0);
        set_centroid(0, 199.0, 99.0, 51.0);
        run_and_check(0, 3.0);

        // Test 2: pixel=(10,10,10)  cent[5]=(10,10,10)→dist=0  rest=(0,0,0)→dist=300
        $display("=== Test 2: exact match at centroid[5], dist=0.0 ===");
        clear_centroids();
        set_pixel(10.0, 10.0, 10.0);
        set_centroid(5, 10.0, 10.0, 10.0);
        run_and_check(5, 0.0);

        // Test 3: pixel=(128,128,128)  cent[15]=(130,126,129)→dist=9  rest=(0,0,0)→dist=49152
        $display("=== Test 3: nearest=centroid[15], dist=9.0 ===");
        clear_centroids();
        set_pixel(128.0, 128.0, 128.0);
        set_centroid(15, 130.0, 126.0, 129.0);
        run_and_check(15, 9.0);

        repeat(2) @(posedge clk);
        $display("=== distance_engine_tb DONE ===");
        $finish;
    end

    initial begin #50000; $error("WATCHDOG"); $finish; end

endmodule
