#!/usr/bin/env bash
# run_iverilog.sh
# M4 final co-simulation: pipelined K-Means PIM via AXI4-Lite
# ECE 410/510 Spring 2026 - Bao Nguyen
#
# Usage (from anywhere):
#   bash project/m4/sim/run_iverilog.sh
# Requires: iverilog >= 11 (SystemVerilog 2012 support)

set -euo pipefail

# Resolve paths from the script's own location (avoids the cwd dependency
# that bit M2's run_iverilog.sh - see project/m2/README.md).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
M4_DIR="$(dirname "$SCRIPT_DIR")"
RTL="$M4_DIR/rtl"
TB="$M4_DIR/tb"

echo "==========================================="
echo " M4 Final Co-Simulation"
echo " (K-Means PIM accelerator end-to-end)"
echo "==========================================="

# File order matters: leaf modules before top
iverilog -g2012 -o "$SCRIPT_DIR/sim_top" \
    "$RTL/compute_core.sv" \
    "$RTL/interface.sv" \
    "$RTL/top.sv" \
    "$TB/tb_top.sv"

cd "$SCRIPT_DIR"
vvp sim_top | tee final_run.log

rm -f sim_top

echo ""
echo "==========================================="
echo " Log saved to: $SCRIPT_DIR/final_run.log"
echo " VCD saved to: $SCRIPT_DIR/tb_top.vcd"
echo "==========================================="
