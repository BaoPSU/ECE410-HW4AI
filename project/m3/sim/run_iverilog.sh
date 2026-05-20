#!/usr/bin/env bash
# run_iverilog.sh
# Compile and simulate M3 end-to-end co-sim with Icarus Verilog
# ECE 410/510 Spring 2026 - Bao Nguyen
#
# Usage (from anywhere):
#   bash project/m3/sim/run_iverilog.sh
# Requires: iverilog >= 11 (SystemVerilog 2012 support)

set -euo pipefail

# Resolve paths from the script's own location (lesson from M2: see project/m2/README.md)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
M3_DIR="$(dirname "$SCRIPT_DIR")"
RTL="$M3_DIR/rtl"
TB="$M3_DIR/tb"

echo "==========================================="
echo " M3 End-to-End Co-Simulation"
echo "==========================================="

# Compile (file order matters: leaf modules before top)
iverilog -g2012 -o "$SCRIPT_DIR/sim_top" \
    "$RTL/kmeans_dist_core_pipelined.sv" \
    "$RTL/axil_slave_int.sv" \
    "$RTL/top.sv" \
    "$TB/tb_top.sv"

# Run, capture log
cd "$SCRIPT_DIR"
vvp sim_top | tee cosim_run.log

# Cleanup binary; keep vcd + log
rm -f sim_top

echo ""
echo "==========================================="
echo " Log saved to: $SCRIPT_DIR/cosim_run.log"
echo " VCD saved to: $SCRIPT_DIR/tb_top.vcd"
echo "==========================================="
