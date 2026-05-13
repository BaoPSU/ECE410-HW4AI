// kmeans_dist_core.sv
// Synthesizable K-Means squared-distance compute core
// ECE 410/510 Spring 2026 - Bao Nguyen
//
// Computes kdist[k] = sum_d (pixel[d] - centroid[k][d])^2 for all K centroids
// using integer arithmetic, then registers argmin(kdist) as the cluster label.
//
// Precision : integer (exact for 8-bit RGB; max kdist = 3*255^2 = 195,075 < 2^18)
// Latency   : 1 clock cycle (start -> done on the very next posedge)
// Pipeline  : fully combinational distance+argmin, registered output stage

`timescale 1ns/1ps

module kmeans_dist_core #(
    parameter K       = 16,  // number of centroids
    parameter D       = 3,   // pixel dimensions (RGB)
    parameter DATA_W  = 8,   // bits per channel (unsigned, 0-255)
    parameter DIST_W  = 20,  // bits for distance accumulator (>=18 for 8-bit RGB)
    parameter LABEL_W = 4    // bits for label output (ceil(log2(K)) = 4 for K=16)
)(
    input  logic                    clk,
    input  logic                    rst_n,   // active-low synchronous reset
    input  logic                    start,   // pulse high one cycle to begin

    // Flat 1D unpacked arrays; pixel[d], centroids[k*D + d]
    input  logic [DATA_W-1:0]       pixel     [0:D-1],
    input  logic [DATA_W-1:0]       centroids [0:K*D-1],

    output logic                    done,
    output logic [DIST_W-1:0]       min_dist,
    output logic [LABEL_W-1:0]      label
);
    // Note: 'dist' is a reserved SV keyword; all distance signals use 'kdist' prefix.

    localparam SQ_W  = 2 * DATA_W;     // bits for squared difference (DATA_W=8 -> 16)
    localparam PAD_W = DIST_W - SQ_W;  // zero-padding bits for accumulator extension

    // -- Intermediate combinational signals -----------------------------------
    logic [DATA_W-1:0]  abs_diff  [0:K-1][0:D-1];
    logic [SQ_W-1:0]    sq_diff   [0:K-1][0:D-1];
    logic [DIST_W-1:0]  kdist     [0:K-1];

    logic [DIST_W-1:0]  comb_min;
    logic [LABEL_W-1:0] comb_lbl;

    // -- Combinational: abs diff, square, accumulate, argmin -----------------
    always_comb begin
        for (int k = 0; k < K; k++) begin
            kdist[k] = {DIST_W{1'b0}};
            for (int d = 0; d < D; d++) begin
                abs_diff[k][d] = (pixel[d] >= centroids[k*D + d])
                               ? pixel[d] - centroids[k*D + d]
                               : centroids[k*D + d] - pixel[d];
                sq_diff[k][d]  = abs_diff[k][d] * abs_diff[k][d];
                kdist[k]       = kdist[k] + {{PAD_W{1'b0}}, sq_diff[k][d]};
            end
        end

        comb_min = kdist[0];
        comb_lbl = {LABEL_W{1'b0}};
        for (int k = 1; k < K; k++) begin
            if (kdist[k] < comb_min) begin
                comb_min = kdist[k];
                comb_lbl = k[LABEL_W-1:0];
            end
        end
    end

    // -- Sequential: register outputs with 1-cycle latency -------------------
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            done     <= 1'b0;
            min_dist <= {DIST_W{1'b0}};
            label    <= {LABEL_W{1'b0}};
        end else if (start) begin
            done     <= 1'b1;
            min_dist <= comb_min;
            label    <= comb_lbl;
        end else begin
            done <= 1'b0;
        end
    end

endmodule
