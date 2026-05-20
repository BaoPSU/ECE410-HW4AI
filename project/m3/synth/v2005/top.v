// top.v
// Verilog-2005 port of project/m3/rtl/top.sv for OpenLane 2 / yosys.
// ECE 410/510 Spring 2026 - Bao Nguyen

`timescale 1ns/1ps

module top #(
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
    output wire               awready,

    input  wire [31:0]        wdata,
    input  wire [3:0]         wstrb,
    input  wire               wvalid,
    output wire               wready,

    output wire [1:0]         bresp,
    output wire               bvalid,
    input  wire               bready,

    input  wire [ADDR_W-1:0]  araddr,
    input  wire               arvalid,
    output wire               arready,

    output wire [31:0]        rdata,
    output wire [1:0]         rresp,
    output wire               rvalid,
    input  wire               rready
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
