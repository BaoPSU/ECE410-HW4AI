// axil_slave_int.v
// Verilog-2005 port of project/m3/rtl/axil_slave_int.sv
// ECE 410/510 Spring 2026 - Bao Nguyen
//
// Differences vs SV source:
//   - logic         -> wire / reg
//   - always_ff/comb -> always @(posedge clk) / always @(*)
//   - typedef enum  -> localparam constants + reg state
//   - unpacked array ports of compute core -> flat packed buses
//   - task automatic do_write -> task do_write (no automatic in V-2005)

`timescale 1ns/1ps

module axil_slave_int #(
    parameter ADDR_W  = 12,
    parameter K       = 16,
    parameter D       = 3,
    parameter DATA_W  = 8,
    parameter DIST_W  = 18,
    parameter LABEL_W = 4
)(
    input  wire               clk,
    input  wire               rst_n,

    input  wire [ADDR_W-1:0]  awaddr,
    input  wire               awvalid,
    output reg                awready,

    input  wire [31:0]        wdata,
    input  wire [3:0]         wstrb,
    input  wire               wvalid,
    output reg                wready,

    output reg  [1:0]         bresp,
    output reg                bvalid,
    input  wire               bready,

    input  wire [ADDR_W-1:0]  araddr,
    input  wire               arvalid,
    output reg                arready,

    output reg  [31:0]        rdata,
    output reg  [1:0]         rresp,
    output reg                rvalid,
    input  wire               rready
);

    // Internal storage as unpacked arrays (yosys handles these inside)
    reg [DATA_W-1:0] reg_pixel     [0:D-1];
    reg [DATA_W-1:0] reg_centroids [0:K*D-1];

    // Flat-pack the storage into buses for the compute-core ports
    wire [D*DATA_W-1:0]   pixel_flat;
    wire [K*D*DATA_W-1:0] centroids_flat;

    genvar gd, gk;
    generate
        for (gd = 0; gd < D; gd = gd + 1) begin : g_pix
            assign pixel_flat[gd*DATA_W +: DATA_W] = reg_pixel[gd];
        end
        for (gk = 0; gk < K*D; gk = gk + 1) begin : g_cen
            assign centroids_flat[gk*DATA_W +: DATA_W] = reg_centroids[gk];
        end
    endgenerate

    // Compute-core wires
    wire               eng_start;
    wire               eng_done;
    wire [DIST_W-1:0]  eng_min_dist;
    wire [LABEL_W-1:0] eng_label;

    reg                status_done;
    reg                busy;

    kmeans_dist_core_pipelined #(
        .K       (K),
        .D       (D),
        .DATA_W  (DATA_W),
        .DIST_W  (DIST_W),
        .LABEL_W (LABEL_W)
    ) u_core (
        .clk            (clk),
        .rst_n          (rst_n),
        .start          (eng_start),
        .pixel_flat     (pixel_flat),
        .centroids_flat (centroids_flat),
        .done           (eng_done),
        .min_dist       (eng_min_dist),
        .label          (eng_label)
    );

    // status_done: latched until next start
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)         status_done <= 1'b0;
        else if (eng_done)  status_done <= 1'b1;
        else if (eng_start) status_done <= 1'b0;
    end

    // busy: from start pulse until done rises
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)         busy <= 1'b0;
        else if (eng_start) busy <= 1'b1;
        else if (eng_done)  busy <= 1'b0;
    end

    // ── Write FSM (state encoded as localparams) ──────────────────────────
    localparam [1:0]
        WR_IDLE    = 2'd0,
        WR_WAIT_W  = 2'd1,
        WR_WAIT_AW = 2'd2,
        WR_RESP    = 2'd3;

    reg [1:0]          wr_state;
    reg [ADDR_W-1:0]   wr_addr_latch;
    reg [31:0]         wr_data_latch;

    assign eng_start = (wr_state == WR_IDLE &&
                        awvalid && awready && wvalid && wready &&
                        awaddr == 12'h000 && wdata[0]) ||
                       (wr_state == WR_WAIT_W && wvalid &&
                        wr_addr_latch == 12'h000 && wdata[0]) ||
                       (wr_state == WR_WAIT_AW && awvalid &&
                        awaddr == 12'h000 && wr_data_latch[0]);

    // ── Write strobe + chosen address/data ────────────────────────────────
    // wr_fire pulses when a write transaction completes in this cycle.
    // wr_addr / wr_data are the address+data captured for the completing write.
    wire               wr_fire;
    wire [ADDR_W-1:0]  wr_addr;
    wire [31:0]        wr_data;

    assign wr_fire =
        (wr_state == WR_IDLE    && awvalid && awready && wvalid && wready) ||
        (wr_state == WR_WAIT_W  && wvalid) ||
        (wr_state == WR_WAIT_AW && awvalid);

    assign wr_addr =
        (wr_state == WR_IDLE)    ? awaddr       :
        (wr_state == WR_WAIT_W)  ? wr_addr_latch :
        (wr_state == WR_WAIT_AW) ? awaddr        : {ADDR_W{1'b0}};

    assign wr_data =
        (wr_state == WR_IDLE)    ? wdata          :
        (wr_state == WR_WAIT_W)  ? wdata          :
        (wr_state == WR_WAIT_AW) ? wr_data_latch  : 32'h0;

    integer wi;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_state      <= WR_IDLE;
            awready       <= 1'b1;
            wready        <= 1'b1;
            bvalid        <= 1'b0;
            bresp         <= 2'b00;
            wr_addr_latch <= {ADDR_W{1'b0}};
            wr_data_latch <= 32'h0;
            for (wi = 0; wi < D;   wi = wi + 1) reg_pixel[wi]     <= {DATA_W{1'b0}};
            for (wi = 0; wi < K*D; wi = wi + 1) reg_centroids[wi] <= {DATA_W{1'b0}};
        end else begin
            // Address-decoded register writes (flat case for synthesis-friendly decode).
            // Pixel @ 0x008. Centroids @ 0x010..0x04C, stride 4 bytes (16 centroids).
            if (wr_fire) begin
                case (wr_addr[11:0])
                    12'h008: begin reg_pixel[0]      <= wr_data[23:16]; reg_pixel[1]      <= wr_data[15:8]; reg_pixel[2]      <= wr_data[7:0]; end
                    12'h010: begin reg_centroids[0]  <= wr_data[23:16]; reg_centroids[1]  <= wr_data[15:8]; reg_centroids[2]  <= wr_data[7:0]; end
                    12'h014: begin reg_centroids[3]  <= wr_data[23:16]; reg_centroids[4]  <= wr_data[15:8]; reg_centroids[5]  <= wr_data[7:0]; end
                    12'h018: begin reg_centroids[6]  <= wr_data[23:16]; reg_centroids[7]  <= wr_data[15:8]; reg_centroids[8]  <= wr_data[7:0]; end
                    12'h01C: begin reg_centroids[9]  <= wr_data[23:16]; reg_centroids[10] <= wr_data[15:8]; reg_centroids[11] <= wr_data[7:0]; end
                    12'h020: begin reg_centroids[12] <= wr_data[23:16]; reg_centroids[13] <= wr_data[15:8]; reg_centroids[14] <= wr_data[7:0]; end
                    12'h024: begin reg_centroids[15] <= wr_data[23:16]; reg_centroids[16] <= wr_data[15:8]; reg_centroids[17] <= wr_data[7:0]; end
                    12'h028: begin reg_centroids[18] <= wr_data[23:16]; reg_centroids[19] <= wr_data[15:8]; reg_centroids[20] <= wr_data[7:0]; end
                    12'h02C: begin reg_centroids[21] <= wr_data[23:16]; reg_centroids[22] <= wr_data[15:8]; reg_centroids[23] <= wr_data[7:0]; end
                    12'h030: begin reg_centroids[24] <= wr_data[23:16]; reg_centroids[25] <= wr_data[15:8]; reg_centroids[26] <= wr_data[7:0]; end
                    12'h034: begin reg_centroids[27] <= wr_data[23:16]; reg_centroids[28] <= wr_data[15:8]; reg_centroids[29] <= wr_data[7:0]; end
                    12'h038: begin reg_centroids[30] <= wr_data[23:16]; reg_centroids[31] <= wr_data[15:8]; reg_centroids[32] <= wr_data[7:0]; end
                    12'h03C: begin reg_centroids[33] <= wr_data[23:16]; reg_centroids[34] <= wr_data[15:8]; reg_centroids[35] <= wr_data[7:0]; end
                    12'h040: begin reg_centroids[36] <= wr_data[23:16]; reg_centroids[37] <= wr_data[15:8]; reg_centroids[38] <= wr_data[7:0]; end
                    12'h044: begin reg_centroids[39] <= wr_data[23:16]; reg_centroids[40] <= wr_data[15:8]; reg_centroids[41] <= wr_data[7:0]; end
                    12'h048: begin reg_centroids[42] <= wr_data[23:16]; reg_centroids[43] <= wr_data[15:8]; reg_centroids[44] <= wr_data[7:0]; end
                    12'h04C: begin reg_centroids[45] <= wr_data[23:16]; reg_centroids[46] <= wr_data[15:8]; reg_centroids[47] <= wr_data[7:0]; end
                    default: ;  // CTRL (0x000) handled by eng_start; other addresses ignored
                endcase
            end

            case (wr_state)
                WR_IDLE: begin
                    if (awvalid && awready && wvalid && wready) begin
                        awready  <= 1'b0;
                        wready   <= 1'b0;
                        bvalid   <= 1'b1;
                        bresp    <= 2'b00;
                        wr_state <= WR_RESP;
                    end else if (awvalid && awready) begin
                        wr_addr_latch <= awaddr;
                        awready       <= 1'b0;
                        wr_state      <= WR_WAIT_W;
                    end else if (wvalid && wready) begin
                        wr_data_latch <= wdata;
                        wready        <= 1'b0;
                        wr_state      <= WR_WAIT_AW;
                    end
                end
                WR_WAIT_W: begin
                    if (wvalid) begin
                        wready   <= 1'b0;
                        bvalid   <= 1'b1;
                        bresp    <= 2'b00;
                        wr_state <= WR_RESP;
                    end
                end
                WR_WAIT_AW: begin
                    if (awvalid) begin
                        awready  <= 1'b0;
                        bvalid   <= 1'b1;
                        bresp    <= 2'b00;
                        wr_state <= WR_RESP;
                    end
                end
                WR_RESP: begin
                    if (bready && bvalid) begin
                        bvalid   <= 1'b0;
                        awready  <= 1'b1;
                        wready   <= 1'b1;
                        wr_state <= WR_IDLE;
                    end
                end
                default: wr_state <= WR_IDLE;
            endcase
        end
    end

    // ── Read FSM ──────────────────────────────────────────────────────────
    localparam RD_IDLE = 1'b0, RD_RESP = 1'b1;
    reg rd_state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rd_state <= RD_IDLE;
            arready  <= 1'b1;
            rvalid   <= 1'b0;
            rdata    <= 32'h0;
            rresp    <= 2'b00;
        end else begin
            case (rd_state)
                RD_IDLE: begin
                    if (arvalid && arready) begin
                        arready <= 1'b0;
                        rvalid  <= 1'b1;
                        rresp   <= 2'b00;
                        case (araddr)
                            12'h004: rdata <= {30'h0, busy, status_done};
                            12'h100: rdata <= {28'h0, eng_label};
                            12'h104: rdata <= {{(32 - DIST_W){1'b0}}, eng_min_dist};
                            default: rdata <= 32'hDEADBEEF;
                        endcase
                        rd_state <= RD_RESP;
                    end
                end
                RD_RESP: begin
                    if (rvalid && rready) begin
                        rvalid   <= 1'b0;
                        arready  <= 1'b1;
                        rd_state <= RD_IDLE;
                    end
                end
                default: rd_state <= RD_IDLE;
            endcase
        end
    end

endmodule
