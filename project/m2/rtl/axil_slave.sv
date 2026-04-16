// axil_slave.sv
// AXI4-Lite slave — K-Means accelerator control interface
// ECE 410/510 Spring 2026 — Bao Nguyen
//
// Wraps distance_engine.sv and exposes a register-mapped AXI4-Lite port
// so the host can load pixel/centroid data, trigger computation, and read results.
//
// Register map  (32-bit aligned, byte address):
//   0x000  CTRL          W    bit[0]=start (self-clearing, 1-cycle pulse)
//   0x004  STATUS        R    bit[0]=done  (latched until next start)
//   0x008  PIX_R         W    pixel R  (float32)
//   0x00C  PIX_G         W    pixel G  (float32)
//   0x010  PIX_B         W    pixel B  (float32)
//   0x014  CENT[0][R]    W    centroid 0, R  (float32)
//   0x018  CENT[0][G]    W    centroid 0, G
//   0x01C  CENT[0][B]    W    centroid 0, B
//   ...    (stride 12 bytes per centroid, 3 regs × K centroids)
//   0x0D0  CENT[15][B]   W    centroid 15, B
//   0x100  RESULT_LABEL  R    cluster label  [3:0]
//   0x104  RESULT_DIST   R    min squared distance  (float32)
//
// AXI4-Lite constraints:
//   - Data width  : 32 bits
//   - Address width: ADDR_W bits (default 12)
//   - Assumes master presents AWVALID and WVALID simultaneously (typical for
//     software-driven AXI4-Lite; split-channel case handled via wr_state FSM)

`timescale 1ns/1ps

module axil_slave #(
    parameter int ADDR_W = 12,
    parameter int K      = 16,
    parameter int D      = 3,
    parameter int LABEL_W = 4
)(
    input  logic               clk,
    input  logic               rst_n,

    // ── Write address channel ──────────────────────────────────────────────
    input  logic [ADDR_W-1:0]  awaddr,
    input  logic               awvalid,
    output logic               awready,

    // ── Write data channel ────────────────────────────────────────────────
    input  logic [31:0]        wdata,
    input  logic [3:0]         wstrb,
    input  logic               wvalid,
    output logic               wready,

    // ── Write response channel ────────────────────────────────────────────
    output logic [1:0]         bresp,
    output logic               bvalid,
    input  logic               bready,

    // ── Read address channel ──────────────────────────────────────────────
    input  logic [ADDR_W-1:0]  araddr,
    input  logic               arvalid,
    output logic               arready,

    // ── Read data channel ─────────────────────────────────────────────────
    output logic [31:0]        rdata,
    output logic [1:0]         rresp,
    output logic               rvalid,
    input  logic               rready
);

    // ── Internal register file ────────────────────────────────────────────
    logic [31:0] reg_pixel     [0:D-1];
    logic [31:0] reg_centroids [0:K-1][0:D-1];

    // ── Distance engine wires ─────────────────────────────────────────────
    logic               eng_start;
    logic               eng_done;
    logic [31:0]        eng_min_dist;
    logic [LABEL_W-1:0] eng_label;
    logic               status_done;    // latched done flag

    distance_engine #(
        .K       (K),
        .D       (D),
        .LABEL_W (LABEL_W)
    ) u_eng (
        .clk       (clk),
        .rst_n     (rst_n),
        .start     (eng_start),
        .pixel     (reg_pixel),
        .centroids (reg_centroids),
        .done      (eng_done),
        .min_dist  (eng_min_dist),
        .label     (eng_label)
    );

    // Latch done until next start clears it
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)             status_done <= 1'b0;
        else if (eng_done)      status_done <= 1'b1;
        else if (eng_start)     status_done <= 1'b0;
    end

    // ── Write FSM ─────────────────────────────────────────────────────────
    typedef enum logic [1:0] {
        WR_IDLE, WR_WAIT_W, WR_WAIT_AW, WR_RESP
    } wr_state_t;
    wr_state_t              wr_state;
    logic [ADDR_W-1:0]      wr_addr_latch;
    logic [31:0]            wr_data_latch;

    assign eng_start = (wr_state == WR_IDLE &&
                        awvalid && awready && wvalid && wready &&
                        awaddr == 12'h000 && wdata[0]) ||
                       (wr_state == WR_WAIT_W && wvalid &&
                        wr_addr_latch == 12'h000 && wdata[0]) ||
                       (wr_state == WR_WAIT_AW && awvalid &&
                        awaddr == 12'h000 && wr_data_latch[0]);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_state     <= WR_IDLE;
            awready      <= 1'b1;
            wready       <= 1'b1;
            bvalid       <= 1'b0;
            bresp        <= 2'b00;
            wr_addr_latch <= '0;
            wr_data_latch <= '0;
            for (int d = 0; d < D; d++) reg_pixel[d] <= 32'h0;
            for (int k = 0; k < K; k++)
                for (int d = 0; d < D; d++) reg_centroids[k][d] <= 32'h0;
        end else begin
            case (wr_state)

                // ── IDLE: both channels ready ──────────────────────────────
                WR_IDLE: begin
                    if (awvalid && awready && wvalid && wready) begin
                        // Both presented simultaneously — execute right away
                        do_write(awaddr, wdata);
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

                // ── WAIT_W: have address, waiting for data ─────────────────
                WR_WAIT_W: begin
                    if (wvalid) begin
                        do_write(wr_addr_latch, wdata);
                        wready   <= 1'b0;
                        bvalid   <= 1'b1;
                        bresp    <= 2'b00;
                        wr_state <= WR_RESP;
                    end
                end

                // ── WAIT_AW: have data, waiting for address ────────────────
                WR_WAIT_AW: begin
                    if (awvalid) begin
                        do_write(awaddr, wr_data_latch);
                        awready  <= 1'b0;
                        bvalid   <= 1'b1;
                        bresp    <= 2'b00;
                        wr_state <= WR_RESP;
                    end
                end

                // ── RESP: wait for master to accept response ───────────────
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

    // Register-write task (called from always_ff — blocking assignments)
    task automatic do_write(
        input logic [ADDR_W-1:0] addr,
        input logic [31:0]       data
    );
        // CTRL register (0x000) — eng_start handled combinationally above
        if (addr == 12'h008) reg_pixel[0] = data;
        else if (addr == 12'h00C) reg_pixel[1] = data;
        else if (addr == 12'h010) reg_pixel[2] = data;
        else begin
            // Centroid registers: 0x014 + (k*D + d)*4
            for (int k = 0; k < K; k++) begin
                for (int d = 0; d < D; d++) begin
                    if (addr == (ADDR_W)'(12'h014 + (k * D + d) * 4))
                        reg_centroids[k][d] = data;
                end
            end
        end
    endtask

    // ── Read FSM ──────────────────────────────────────────────────────────
    typedef enum logic { RD_IDLE, RD_RESP } rd_state_t;
    rd_state_t rd_state;

    always_ff @(posedge clk or negedge rst_n) begin
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
                        arready  <= 1'b0;
                        rvalid   <= 1'b1;
                        rresp    <= 2'b00;
                        // Register-read decode
                        case (araddr)
                            12'h004: rdata <= {30'h0, 1'b0, status_done};
                            12'h100: rdata <= {28'h0, eng_label};
                            12'h104: rdata <= eng_min_dist;
                            default: rdata <= 32'hDEAD_BEEF;
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
