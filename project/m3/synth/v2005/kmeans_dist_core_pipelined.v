// kmeans_dist_core_pipelined.v
// Verilog-2005 port of project/m3/rtl/kmeans_dist_core_pipelined.sv
// for the OpenLane 2 / stock yosys default Verilog frontend.
// ECE 410/510 Spring 2026 - Bao Nguyen
//
// Differences vs SV source:
//   - logic         -> wire / reg
//   - always_ff/comb -> always @(posedge clk) / always @(*)
//   - unpacked array ports -> flat packed buses (DATA_W-bit slices)
//   - localparam int -> localparam

`timescale 1ns/1ps

module kmeans_dist_core_pipelined #(
    parameter K       = 16,
    parameter D       = 3,
    parameter DATA_W  = 8,
    parameter DIST_W  = 18,
    parameter LABEL_W = 4
)(
    input  wire                          clk,
    input  wire                          rst_n,
    input  wire                          start,

    // Packed buses (each DATA_W-bit slice is one channel/centroid byte)
    //   pixel_flat[d*DATA_W +: DATA_W]              = pixel[d]
    //   centroids_flat[(k*D + d)*DATA_W +: DATA_W]  = centroids[k][d]
    input  wire [D*DATA_W-1:0]           pixel_flat,
    input  wire [K*D*DATA_W-1:0]         centroids_flat,

    output reg                           done,
    output reg  [DIST_W-1:0]             min_dist,
    output reg  [LABEL_W-1:0]            label
);
    localparam SQ_W  = 2 * DATA_W;
    localparam PAD_W = DIST_W - SQ_W;

    // ==========================================================================
    // STAGE 1 combinational: per-centroid distance kdist[k]
    // ==========================================================================
    integer ki, di;
    reg [DATA_W-1:0]  ad_kd  [0:K-1];   // abs_diff per (k, current d) reused
    reg [DATA_W-1:0]  pix_d  [0:D-1];   // unpacked view of pixel
    reg [DATA_W-1:0]  cen_kd [0:K-1][0:D-1];

    reg [DIST_W-1:0]  kdist_c [0:K-1];

    always @(*) begin
        // Unpack the packed buses into local arrays.
        for (di = 0; di < D; di = di + 1)
            pix_d[di] = pixel_flat[di*DATA_W +: DATA_W];
        for (ki = 0; ki < K; ki = ki + 1)
            for (di = 0; di < D; di = di + 1)
                cen_kd[ki][di] = centroids_flat[(ki*D + di)*DATA_W +: DATA_W];

        // kdist[k] = sum_d (pixel[d] - centroid[k][d])^2  (using abs_diff^2)
        for (ki = 0; ki < K; ki = ki + 1) begin
            kdist_c[ki] = {DIST_W{1'b0}};
            for (di = 0; di < D; di = di + 1) begin
                if (pix_d[di] >= cen_kd[ki][di])
                    ad_kd[ki] = pix_d[di] - cen_kd[ki][di];
                else
                    ad_kd[ki] = cen_kd[ki][di] - pix_d[di];
                kdist_c[ki] = kdist_c[ki] +
                              {{PAD_W{1'b0}}, ad_kd[ki] * ad_kd[ki]};
            end
        end
    end

    // STAGE 1 register
    reg [DIST_W-1:0]  s1_kdist [0:K-1];
    reg               s1_valid;

    always @(posedge clk) begin
        if (!rst_n) begin
            s1_valid <= 1'b0;
            for (ki = 0; ki < K; ki = ki + 1)
                s1_kdist[ki] <= {DIST_W{1'b0}};
        end else begin
            s1_valid <= start;
            for (ki = 0; ki < K; ki = ki + 1)
                s1_kdist[ki] <= kdist_c[ki];
        end
    end

    // ==========================================================================
    // STAGE 2 combinational: argmin levels 1+2  (16 -> 8 -> 4)
    // ==========================================================================
    integer i2;
    reg [DIST_W-1:0]  l1_d [0:7];
    reg [LABEL_W-1:0] l1_l [0:7];
    reg [DIST_W-1:0]  s2_d_c [0:3];
    reg [LABEL_W-1:0] s2_l_c [0:3];

    always @(*) begin
        // Level 1: 16 -> 8
        for (i2 = 0; i2 < 8; i2 = i2 + 1) begin
            if (s1_kdist[2*i2+1] < s1_kdist[2*i2]) begin
                l1_d[i2] = s1_kdist[2*i2+1];
                l1_l[i2] = (2*i2 + 1);
            end else begin
                l1_d[i2] = s1_kdist[2*i2];
                l1_l[i2] = (2*i2);
            end
        end
        // Level 2: 8 -> 4
        for (i2 = 0; i2 < 4; i2 = i2 + 1) begin
            if (l1_d[2*i2+1] < l1_d[2*i2]) begin
                s2_d_c[i2] = l1_d[2*i2+1];
                s2_l_c[i2] = l1_l[2*i2+1];
            end else begin
                s2_d_c[i2] = l1_d[2*i2];
                s2_l_c[i2] = l1_l[2*i2];
            end
        end
    end

    // STAGE 2 register
    reg [DIST_W-1:0]  s2_d [0:3];
    reg [LABEL_W-1:0] s2_l [0:3];
    reg               s2_valid;

    always @(posedge clk) begin
        if (!rst_n) begin
            s2_valid <= 1'b0;
            for (i2 = 0; i2 < 4; i2 = i2 + 1) begin
                s2_d[i2] <= {DIST_W{1'b0}};
                s2_l[i2] <= {LABEL_W{1'b0}};
            end
        end else begin
            s2_valid <= s1_valid;
            for (i2 = 0; i2 < 4; i2 = i2 + 1) begin
                s2_d[i2] <= s2_d_c[i2];
                s2_l[i2] <= s2_l_c[i2];
            end
        end
    end

    // ==========================================================================
    // STAGE 3 combinational: argmin levels 3+4  (4 -> 2 -> 1)
    // ==========================================================================
    reg [DIST_W-1:0]  l3_d0, l3_d1;
    reg [LABEL_W-1:0] l3_l0, l3_l1;
    reg [DIST_W-1:0]  s3_d_c;
    reg [LABEL_W-1:0] s3_l_c;

    always @(*) begin
        // Level 3: pairs (0,1) and (2,3)
        if (s2_d[1] < s2_d[0]) begin l3_d0 = s2_d[1]; l3_l0 = s2_l[1]; end
        else                   begin l3_d0 = s2_d[0]; l3_l0 = s2_l[0]; end
        if (s2_d[3] < s2_d[2]) begin l3_d1 = s2_d[3]; l3_l1 = s2_l[3]; end
        else                   begin l3_d1 = s2_d[2]; l3_l1 = s2_l[2]; end
        // Level 4: final
        if (l3_d1 < l3_d0) begin s3_d_c = l3_d1; s3_l_c = l3_l1; end
        else               begin s3_d_c = l3_d0; s3_l_c = l3_l0; end
    end

    // STAGE 3 register (final output)
    always @(posedge clk) begin
        if (!rst_n) begin
            done     <= 1'b0;
            min_dist <= {DIST_W{1'b0}};
            label    <= {LABEL_W{1'b0}};
        end else begin
            done     <= s2_valid;
            min_dist <= s3_d_c;
            label    <= s3_l_c;
        end
    end

endmodule
