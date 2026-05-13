// synth_top.v
// Verilog-2005 port-compatible version of kmeans_dist_core.sv
// Converted from SystemVerilog for OpenLane 2 / yosys default frontend.
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
    parameter K       = 16,
    parameter D       = 3,
    parameter DATA_W  = 8,
    parameter DIST_W  = 20,
    parameter LABEL_W = 4
)(
    input  wire                       clk,
    input  wire                       rst_n,
    input  wire                       start,

    // Packed flat arrays (port-compatible with Verilog-2005)
    // pixel[d]        = pixel_flat    [d*DATA_W +: DATA_W]
    // centroids[k][d] = centroids_flat[(k*D + d)*DATA_W +: DATA_W]
    input  wire [D*DATA_W-1:0]        pixel_flat,
    input  wire [K*D*DATA_W-1:0]      centroids_flat,

    output reg                        done,
    output reg  [DIST_W-1:0]          min_dist,
    output reg  [LABEL_W-1:0]         label
);

    localparam SQ_W  = 2 * DATA_W;
    localparam PAD_W = DIST_W - SQ_W;

    // -- Internal arrays (unpacked allowed inside the module body) ------------
    reg [DATA_W-1:0] abs_diff [0:K-1][0:D-1];
    reg [SQ_W-1:0]   sq_diff  [0:K-1][0:D-1];
    reg [DIST_W-1:0] kdist    [0:K-1];

    reg [DIST_W-1:0]  comb_min;
    reg [LABEL_W-1:0] comb_lbl;

    // Bit-slice helpers
    wire [DATA_W-1:0] pix_d [0:D-1];
    wire [DATA_W-1:0] cen_kd [0:K-1][0:D-1];

    genvar gd, gk;
    generate
        for (gd = 0; gd < D; gd = gd + 1) begin : G_PIX
            assign pix_d[gd] = pixel_flat[gd*DATA_W +: DATA_W];
        end
        for (gk = 0; gk < K; gk = gk + 1) begin : G_CEN_K
            for (gd = 0; gd < D; gd = gd + 1) begin : G_CEN_D
                assign cen_kd[gk][gd] =
                    centroids_flat[(gk*D + gd)*DATA_W +: DATA_W];
            end
        end
    endgenerate

    // -- Combinational distance + argmin --------------------------------------
    integer k, d;
    always @(*) begin
        for (k = 0; k < K; k = k + 1) begin
            kdist[k] = {DIST_W{1'b0}};
            for (d = 0; d < D; d = d + 1) begin
                abs_diff[k][d] = (pix_d[d] >= cen_kd[k][d])
                               ? (pix_d[d] - cen_kd[k][d])
                               : (cen_kd[k][d] - pix_d[d]);
                sq_diff[k][d]  = abs_diff[k][d] * abs_diff[k][d];
                kdist[k]       = kdist[k] + {{PAD_W{1'b0}}, sq_diff[k][d]};
            end
        end

        comb_min = kdist[0];
        comb_lbl = {LABEL_W{1'b0}};
        for (k = 1; k < K; k = k + 1) begin
            if (kdist[k] < comb_min) begin
                comb_min = kdist[k];
                comb_lbl = k[LABEL_W-1:0];
            end
        end
    end

    // -- Sequential output register -------------------------------------------
    always @(posedge clk) begin
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
