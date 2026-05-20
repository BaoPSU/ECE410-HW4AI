#!/usr/bin/env bash
# run_iverilog.sh
# Compile and simulate M2 testbenches with Icarus Verilog (iverilog)
# ECE 410/510 Spring 2026 — Bao Nguyen
#
# Usage: bash sim/run_iverilog.sh   (run from project/m2/)
#    or: bash run_iverilog.sh       (run from project/m2/sim/)
# Requires: iverilog >= 11 (SystemVerilog 2012 support)

set -euo pipefail

# Resolve paths from the script's own location, not the caller's cwd.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
M2_DIR="$(dirname "$SCRIPT_DIR")"
RTL="$M2_DIR/rtl"
TB="$M2_DIR/tb"

echo "==========================================="
echo " M2 Simulation — K-Means Distance Engine"
echo "==========================================="

# ── Test 1: distance_engine standalone ──────────────────────────────────────
echo ""
echo ">>> Compiling distance_engine_tb..."
iverilog -g2012 -o sim_dist \
    $RTL/distance_engine.sv \
    $TB/distance_engine_tb.sv

echo ">>> Running distance_engine_tb..."
vvp sim_dist

# ── Test 2: AXI4-Lite slave (includes distance_engine) ──────────────────────
echo ""
echo ">>> Compiling axil_slave_tb..."
iverilog -g2012 -o sim_axil \
    $RTL/distance_engine.sv \
    $RTL/axil_slave.sv \
    $TB/axil_slave_tb.sv

echo ">>> Running axil_slave_tb..."
vvp sim_axil

# ── Cleanup ──────────────────────────────────────────────────────────────────
rm -f sim_dist sim_axil

echo ""
echo "==========================================="
echo " Simulation complete."
echo "==========================================="
