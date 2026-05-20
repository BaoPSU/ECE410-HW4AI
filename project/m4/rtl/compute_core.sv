// kmeans_dist_core_pipelined.sv
// 3-stage pipelined synthesizable K-Means squared-distance core
// ECE 410/510 Spring 2026 - Bao Nguyen
//
// Computes kdist[k] = sum_d (pixel[d] - centroid[k][d])^2 for all K centroids
// using integer arithmetic, then registers argmin(kdist) as the cluster label.
//
// Pipeline (per cf07/synth/m3_plan.md):
//   Stage 1: combinational kdist[0..15] compute -> register 16 kdist + valid
//   Stage 2: argmin levels 1-2 (16 -> 8 -> 4 candidates) -> register 4 + valid
//   Stage 3: argmin levels 3-4 (4 -> 2 -> 1 winner) -> register min_dist + label + done
//
// Latency   : 3 cycles (start pulse -> done asserts on the 3rd posedge after start)
// Throughput: 1 sample/cycle (fully pipelined)
// Precision : integer (exact for 8-bit RGB; max kdist = 3*255^2 = 195,075 < 2^18,
//             so DIST_W=18 is sufficient and saves area vs the M2 prototype's 20.)

`timescale 1ns/1ps

module kmeans_dist_core_pipelined #(
    parameter K       = 16,
    parameter D       = 3,
    parameter DATA_W  = 8,
    parameter DIST_W  = 18,    // dropped from 20 per CF07 STA (min_dist[18:19] always zero)
    parameter LABEL_W = 4
)(
    input  logic                    clk,
    input  logic                    rst_n,
    input  logic                    start,
    input  logic [DATA_W-1:0]       pixel     [0:D-1],
    input  logic [DATA_W-1:0]       centroids [0:K*D-1],
    output logic                    done,
    output logic [DIST_W-1:0]       min_dist,
    output logic [LABEL_W-1:0]      label
);
    localparam int SQ_W  = 2 * DATA_W;       // 16
    localparam int PAD_W = DIST_W - SQ_W;    // 2 when DIST_W=18

    // ==========================================================================
    // STAGE 1 combinational: per-centroid distance kdist[k]
    // ==========================================================================
    logic [DATA_W-1:0]  abs_diff [0:K-1][0:D-1];
    logic [SQ_W-1:0]    sq_diff  [0:K-1][0:D-1];
    logic [DIST_W-1:0]  kdist_c  [0:K-1];

    always_comb begin
        for (int k = 0; k < K; k++) begin
            kdist_c[k] = '0;
            for (int d = 0; d < D; d++) begin
                abs_diff[k][d] = (pixel[d] >= centroids[k*D + d])
                               ? pixel[d] - centroids[k*D + d]
                               : centroids[k*D + d] - pixel[d];
                sq_diff[k][d]  = abs_diff[k][d] * abs_diff[k][d];
                kdist_c[k]     = kdist_c[k] + {{PAD_W{1'b0}}, sq_diff[k][d]};
            end
        end
    end

    // STAGE 1 register
    logic [DIST_W-1:0]  s1_kdist [0:K-1];
    logic               s1_valid;

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            s1_valid <= 1'b0;
            for (int k = 0; k < K; k++) s1_kdist[k] <= '0;
        end else begin
            s1_valid <= start;
            for (int k = 0; k < K; k++) s1_kdist[k] <= kdist_c[k];
        end
    end

    // ==========================================================================
    // STAGE 2 combinational: argmin levels 1+2  (16 -> 8 -> 4)
    // ==========================================================================
    logic [DIST_W-1:0]  l1_d [0:7];
    logic [LABEL_W-1:0] l1_l [0:7];
    logic [DIST_W-1:0]  s2_d_c [0:3];
    logic [LABEL_W-1:0] s2_l_c [0:3];

    always_comb begin
        // Level 1: 16 -> 8  (compare adjacent pairs)
        for (int i = 0; i < 8; i++) begin
            if (s1_kdist[2*i+1] < s1_kdist[2*i]) begin
                l1_d[i] = s1_kdist[2*i+1];
                l1_l[i] = LABEL_W'(2*i + 1);
            end else begin
                l1_d[i] = s1_kdist[2*i];
                l1_l[i] = LABEL_W'(2*i);
            end
        end
        // Level 2: 8 -> 4
        for (int i = 0; i < 4; i++) begin
            if (l1_d[2*i+1] < l1_d[2*i]) begin
                s2_d_c[i] = l1_d[2*i+1];
                s2_l_c[i] = l1_l[2*i+1];
            end else begin
                s2_d_c[i] = l1_d[2*i];
                s2_l_c[i] = l1_l[2*i];
            end
        end
    end

    // STAGE 2 register
    logic [DIST_W-1:0]  s2_d [0:3];
    logic [LABEL_W-1:0] s2_l [0:3];
    logic               s2_valid;

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            s2_valid <= 1'b0;
            for (int i = 0; i < 4; i++) begin
                s2_d[i] <= '0;
                s2_l[i] <= '0;
            end
        end else begin
            s2_valid <= s1_valid;
            for (int i = 0; i < 4; i++) begin
                s2_d[i] <= s2_d_c[i];
                s2_l[i] <= s2_l_c[i];
            end
        end
    end

    // ==========================================================================
    // STAGE 3 combinational: argmin levels 3+4  (4 -> 2 -> 1)
    // ==========================================================================
    logic [DIST_W-1:0]  l3_d [0:1];
    logic [LABEL_W-1:0] l3_l [0:1];
    logic [DIST_W-1:0]  s3_d_c;
    logic [LABEL_W-1:0] s3_l_c;

    always_comb begin
        // Level 3: 4 -> 2
        if (s2_d[1] < s2_d[0]) begin l3_d[0] = s2_d[1]; l3_l[0] = s2_l[1]; end
        else                   begin l3_d[0] = s2_d[0]; l3_l[0] = s2_l[0]; end
        if (s2_d[3] < s2_d[2]) begin l3_d[1] = s2_d[3]; l3_l[1] = s2_l[3]; end
        else                   begin l3_d[1] = s2_d[2]; l3_l[1] = s2_l[2]; end
        // Level 4: 2 -> 1
        if (l3_d[1] < l3_d[0]) begin s3_d_c = l3_d[1]; s3_l_c = l3_l[1]; end
        else                   begin s3_d_c = l3_d[0]; s3_l_c = l3_l[0]; end
    end

    // STAGE 3 register (final output)
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            done     <= 1'b0;
            min_dist <= '0;
            label    <= '0;
        end else begin
            done     <= s2_valid;
            min_dist <= s3_d_c;
            label    <= s3_l_c;
        end
    end

endmodule
