// top.sv
// M3 integrated top module - K-Means PIM accelerator
// ECE 410/510 Spring 2026 - Bao Nguyen
//
// Wires axil_slave_int (AXI4-Lite control interface) directly to the
// pipelined integer compute core (kmeans_dist_core_pipelined).
//
// External ports: clock + reset + the AXI4-Lite slave channels only. The
// host sees the chip as a single AXI4-Lite slave.
//
// ─── Glue logic / inter-module signals ───────────────────────────────────
// All AXI<->core wiring lives INSIDE axil_slave_int. The slave instantiates
// the compute core directly, so this top module has no extra glue logic.
// The interface module already handles:
//   - RGB unpacking from 32-bit AXI words into the core's per-channel inputs
//   - start pulse generation from CTRL[0] write
//   - done latch and busy tracking across the 3-cycle pipeline
//   - DIST_W=18 -> 32-bit zero-extension on the RESULT_DIST read
//
// ─── Port list ─────────────────────────────────────────────────────────────
//   clk        in  1   system clock (target 100 MHz / 10 ns)
//   rst_n      in  1   active-low synchronous reset
//   awaddr     in  12  AXI4-Lite write address
//   awvalid    in  1   write address valid
//   awready    out 1   write address ready
//   wdata      in  32  AXI4-Lite write data
//   wstrb      in  4   write strobe (unused, accepts any)
//   wvalid     in  1   write data valid
//   wready     out 1   write data ready
//   bresp      out 2   write response (always 2'b00 OKAY)
//   bvalid     out 1   write response valid
//   bready     in  1   master ready for response
//   araddr     in  12  AXI4-Lite read address
//   arvalid    in  1   read address valid
//   arready    out 1   read address ready
//   rdata      out 32  AXI4-Lite read data
//   rresp      out 2   read response (always 2'b00 OKAY)
//   rvalid     out 1   read data valid
//   rready     in  1   master ready for read data

`timescale 1ns/1ps

module top #(
    parameter int ADDR_W  = 12,
    parameter int K       = 16,
    parameter int D       = 3,
    parameter int DATA_W  = 8,
    parameter int DIST_W  = 18,
    parameter int LABEL_W = 4
)(
    input  logic               clk,
    input  logic               rst_n,

    input  logic [ADDR_W-1:0]  awaddr,
    input  logic               awvalid,
    output logic               awready,

    input  logic [31:0]        wdata,
    input  logic [3:0]         wstrb,
    input  logic               wvalid,
    output logic               wready,

    output logic [1:0]         bresp,
    output logic               bvalid,
    input  logic               bready,

    input  logic [ADDR_W-1:0]  araddr,
    input  logic               arvalid,
    output logic               arready,

    output logic [31:0]        rdata,
    output logic [1:0]         rresp,
    output logic               rvalid,
    input  logic               rready
);

    axil_slave_int #(
        .ADDR_W  (ADDR_W),
        .K       (K),
        .D       (D),
        .DATA_W  (DATA_W),
        .DIST_W  (DIST_W),
        .LABEL_W (LABEL_W)
    ) u_axil (
        .clk     (clk),
        .rst_n   (rst_n),
        .awaddr  (awaddr),
        .awvalid (awvalid),
        .awready (awready),
        .wdata   (wdata),
        .wstrb   (wstrb),
        .wvalid  (wvalid),
        .wready  (wready),
        .bresp   (bresp),
        .bvalid  (bvalid),
        .bready  (bready),
        .araddr  (araddr),
        .arvalid (arvalid),
        .arready (arready),
        .rdata   (rdata),
        .rresp   (rresp),
        .rvalid  (rvalid),
        .rready  (rready)
    );

endmodule
