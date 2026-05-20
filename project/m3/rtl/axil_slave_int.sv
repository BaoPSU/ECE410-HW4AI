// axil_slave_int.sv
// AXI4-Lite slave - integer K-Means accelerator control interface
// ECE 410/510 Spring 2026 - Bao Nguyen
//
// M3 evolution of project/m2/rtl/axil_slave.sv. The M2 version was wired
// for the float32 behavioral distance_engine; this version drives the
// synthesizable integer kmeans_dist_core_pipelined and uses a simpler
// 32-bit packed register layout for the 8-bit RGB pixel and centroids.
//
// Register map (32-bit aligned, byte address):
//   0x000  CTRL          W  bit[0] = start (self-clearing 1-cycle pulse)
//   0x004  STATUS        R  bit[0] = done, bit[1] = busy
//   0x008  PIXEL         W  [23:16]=R, [15:8]=G, [7:0]=B  (8-bit per channel)
//   0x010  CENT[0]       W  same RGB packing
//   0x014  CENT[1]       W
//   ...    (stride 4 bytes per centroid)
//   0x04C  CENT[15]      W
//   0x100  RESULT_LABEL  R  [3:0]   nearest centroid index
//   0x104  RESULT_DIST   R  [17:0]  minimum squared distance (DIST_W=18)

`timescale 1ns/1ps

module axil_slave_int #(
    parameter int ADDR_W  = 12,
    parameter int K       = 16,
    parameter int D       = 3,
    parameter int DATA_W  = 8,
    parameter int DIST_W  = 18,
    parameter int LABEL_W = 4
)(
    input  logic               clk,
    input  logic               rst_n,

    // Write address channel
    input  logic [ADDR_W-1:0]  awaddr,
    input  logic               awvalid,
    output logic               awready,

    // Write data channel
    input  logic [31:0]        wdata,
    input  logic [3:0]         wstrb,
    input  logic               wvalid,
    output logic               wready,

    // Write response channel
    output logic [1:0]         bresp,
    output logic               bvalid,
    input  logic               bready,

    // Read address channel
    input  logic [ADDR_W-1:0]  araddr,
    input  logic               arvalid,
    output logic               arready,

    // Read data channel
    output logic [31:0]        rdata,
    output logic [1:0]         rresp,
    output logic               rvalid,
    input  logic               rready
);

    // ── Internal storage ──────────────────────────────────────────────────
    // Pixel and centroids stored as 8-bit per channel (unpacked arrays).
    // The compute core consumes a 1-D flat centroid vector centroids[k*D + d].
    logic [DATA_W-1:0] reg_pixel     [0:D-1];
    logic [DATA_W-1:0] reg_centroids [0:K*D-1];

    // ── Compute-core wires ────────────────────────────────────────────────
    logic               eng_start;
    logic               eng_done;
    logic [DIST_W-1:0]  eng_min_dist;
    logic [LABEL_W-1:0] eng_label;
    logic               status_done;  // latched until next start
    logic               busy;          // 1 while pipeline has data in flight

    kmeans_dist_core_pipelined #(
        .K       (K),
        .D       (D),
        .DATA_W  (DATA_W),
        .DIST_W  (DIST_W),
        .LABEL_W (LABEL_W)
    ) u_core (
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
        if (!rst_n)        status_done <= 1'b0;
        else if (eng_done) status_done <= 1'b1;
        else if (eng_start) status_done <= 1'b0;
    end

    // Busy flag: high from start pulse until done rises
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)         busy <= 1'b0;
        else if (eng_start) busy <= 1'b1;
        else if (eng_done)  busy <= 1'b0;
    end

    // ── Write FSM ─────────────────────────────────────────────────────────
    typedef enum logic [1:0] {
        WR_IDLE, WR_WAIT_W, WR_WAIT_AW, WR_RESP
    } wr_state_t;
    wr_state_t          wr_state;
    logic [ADDR_W-1:0]  wr_addr_latch;
    logic [31:0]        wr_data_latch;

    // Combinational start pulse: rises when CTRL (0x000) write completes
    assign eng_start = (wr_state == WR_IDLE &&
                        awvalid && awready && wvalid && wready &&
                        awaddr == 12'h000 && wdata[0]) ||
                       (wr_state == WR_WAIT_W && wvalid &&
                        wr_addr_latch == 12'h000 && wdata[0]) ||
                       (wr_state == WR_WAIT_AW && awvalid &&
                        awaddr == 12'h000 && wr_data_latch[0]);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_state      <= WR_IDLE;
            awready       <= 1'b1;
            wready        <= 1'b1;
            bvalid        <= 1'b0;
            bresp         <= 2'b00;
            wr_addr_latch <= '0;
            wr_data_latch <= '0;
            for (int d = 0; d < D;     d++) reg_pixel[d]     <= '0;
            for (int i = 0; i < K*D; i++)   reg_centroids[i] <= '0;
        end else begin
            case (wr_state)

                WR_IDLE: begin
                    if (awvalid && awready && wvalid && wready) begin
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

                WR_WAIT_W: begin
                    if (wvalid) begin
                        do_write(wr_addr_latch, wdata);
                        wready   <= 1'b0;
                        bvalid   <= 1'b1;
                        bresp    <= 2'b00;
                        wr_state <= WR_RESP;
                    end
                end

                WR_WAIT_AW: begin
                    if (awvalid) begin
                        do_write(awaddr, wr_data_latch);
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

    // Register-write task — unpacks RGB-packed words into the per-channel arrays
    task automatic do_write(
        input logic [ADDR_W-1:0] addr,
        input logic [31:0]       data
    );
        if (addr == 12'h008) begin
            // PIXEL: [23:16]=R, [15:8]=G, [7:0]=B
            reg_pixel[0] = data[23:16];   // R
            reg_pixel[1] = data[15:8];    // G
            reg_pixel[2] = data[7:0];     // B
        end else begin
            // Centroid writes at 0x010 + k*4
            for (int k = 0; k < K; k++) begin
                if (addr == (ADDR_W)'(12'h010 + k * 4)) begin
                    reg_centroids[k*D + 0] = data[23:16];   // R
                    reg_centroids[k*D + 1] = data[15:8];    // G
                    reg_centroids[k*D + 2] = data[7:0];     // B
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
                        arready <= 1'b0;
                        rvalid  <= 1'b1;
                        rresp   <= 2'b00;
                        case (araddr)
                            12'h004: rdata <= {30'h0, busy, status_done};
                            12'h100: rdata <= {28'h0, eng_label};
                            12'h104: rdata <= {{(32 - DIST_W){1'b0}}, eng_min_dist};
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
