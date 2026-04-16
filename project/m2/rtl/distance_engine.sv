// distance_engine.sv
// K-Means pairwise squared-distance compute core
// ECE 410/510 Spring 2026 — Bao Nguyen
//
// Computes dist[k] = Σ_d (pixel[d] − centroid[k][d])²  for all K centroids,
// then outputs argmin(dist) as the cluster label and the minimum distance.
//
// Precision : IEEE 754 float32, packed as logic[31:0].
// Simulation: uses 'real' (64-bit double) for intermediate computation.
//             Inputs/outputs are converted via manual IEEE 754 bit manipulation.
//             Synthesizable FP sub-units replace this behavioral block in M3.
// Latency   : 1 clock cycle (start → done on the very next posedge).

`timescale 1ns/1ps

module distance_engine #(
    parameter int K       = 16,   // number of centroids
    parameter int D       = 3,    // dimensions (RGB)
    parameter int LABEL_W = 4     // ceil(log2(K)) = 4 for K=16
)(
    input  logic               clk,
    input  logic               rst_n,
    input  logic               start,    // pulse high for exactly one cycle

    // Float32 inputs packed as logic[31:0]
    input  logic [31:0]        pixel     [0:D-1],
    input  logic [31:0]        centroids [0:K-1][0:D-1],

    // Outputs (valid while done=1)
    output logic               done,
    output logic [31:0]        min_dist,          // float32 minimum squared distance
    output logic [LABEL_W-1:0] label              // winning centroid index  0..K-1
);

    // ── IEEE 754 conversion helpers ───────────────────────────────────────
    // Convert float32 (logic[31:0]) → real by re-encoding as float64 (logic[63:0])
    // and using the supported $bitstoreal system function.
    function automatic real f32_to_real(input logic [31:0] f);
        logic [63:0] f64;
        int          e32, e64;
        if (f[30:23] == 8'h00) return 0.0;                        // zero / denormal
        if (f[30:23] == 8'hFF) return (f[31] ? -1.0e38 : 1.0e38); // inf / NaN
        e32 = int'({1'b0, f[30:23]});
        e64 = e32 - 127 + 1023;
        f64 = {f[31], 11'(e64), {f[22:0], 29'b0}};
        return $bitstoreal(f64);
    endfunction

    // Convert real → float32 (logic[31:0]) for non-negative values in [0, 2^24).
    // Uses $realtobits (float64) then truncates mantissa 52 → 23 bits.
    // Exact for any real value representable in float32 in this range.
    function automatic logic [31:0] real_to_f32(input real r);
        logic [63:0] f64;
        int          e64, e32;
        if (r == 0.0) return 32'h0000_0000;
        f64 = $realtobits(r);
        e64 = int'(f64[62:52]);
        e32 = e64 - 1023 + 127;
        return {f64[63], 8'(e32), f64[51:29]};
    endfunction

    // ── Behavioral temporaries (simulation-only, not synthesizable FFs) ──
    real  r_px   [0:D-1];
    real  r_cn   [0:K-1][0:D-1];
    real  r_dist [0:K-1];
    real  r_diff;
    real  r_best_d;
    int   r_best_k;

    // ── Sequential pipeline register (1-cycle latency) ────────────────────
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            done     <= 1'b0;
            min_dist <= 32'h0000_0000;
            label    <= {LABEL_W{1'b0}};
        end else if (start) begin

            // 1) Bit-cast float32 inputs to real
            for (int d = 0; d < D; d++)
                r_px[d] = f32_to_real(pixel[d]);
            for (int k = 0; k < K; k++)
                for (int d = 0; d < D; d++)
                    r_cn[k][d] = f32_to_real(centroids[k][d]);

            // 2) Squared Euclidean distances
            for (int k = 0; k < K; k++) begin
                r_dist[k] = 0.0;
                for (int d = 0; d < D; d++) begin
                    r_diff      = r_px[d] - r_cn[k][d];
                    r_dist[k]   = r_dist[k] + r_diff * r_diff;
                end
            end

            // 3) Argmin
            r_best_d = r_dist[0];
            r_best_k = 0;
            for (int k = 1; k < K; k++) begin
                if (r_dist[k] < r_best_d) begin
                    r_best_d = r_dist[k];
                    r_best_k = k;
                end
            end

            // 4) Register outputs (non-blocking → flip-flop semantics)
            done     <= 1'b1;
            min_dist <= real_to_f32(r_best_d);
            label    <= r_best_k[LABEL_W-1:0];

        end else begin
            done <= 1'b0;
        end
    end

endmodule
