#!/usr/bin/env python3
"""
Render the M3 end-to-end co-sim waveform as an annotated PNG.

Reads tb_top.vcd, picks key AXI4-Lite and internal signals, and plots them
on a shared time axis. Annotates the three phases of the test:
  1. Host-side WRITE phase  (pixel + 16 centroids + CTRL.start)
  2. Internal compute phase (3-stage pipeline)
  3. Host-side READ phase   (poll STATUS, read LABEL, read DIST)

Run:  python3 make_waveform.py
Outputs: cosim_waveform.png in this folder.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from vcdvcd import VCDVCD

SIM_DIR  = Path(__file__).parent
VCD_PATH = SIM_DIR / 'tb_top.vcd'
OUT_PATH = SIM_DIR / 'cosim_waveform.png'

vcd = VCDVCD(str(VCD_PATH), store_tvs=True)

# Find signals of interest from the testbench hierarchy.
# vcd.references_to_ids maps full name -> identifier.
def find(suffix):
    matches = [name for name in vcd.references_to_ids if name.endswith(suffix)]
    if not matches:
        return None
    # Prefer the shortest match (closer to top scope)
    return min(matches, key=len)

signal_specs = [
    ('clk',       'tb_top.clk'),
    ('rst_n',     'tb_top.rst_n'),
    ('awvalid',   'tb_top.awvalid'),
    ('awready',   'tb_top.awready'),
    ('wvalid',    'tb_top.wvalid'),
    ('wready',    'tb_top.wready'),
    ('bvalid',    'tb_top.bvalid'),
    ('arvalid',   'tb_top.arvalid'),
    ('rvalid',    'tb_top.rvalid'),
    ('eng_start', 'tb_top.dut.u_axil.eng_start'),
    ('eng_done',  'tb_top.dut.u_axil.eng_done'),
    ('busy',      'tb_top.dut.u_axil.busy'),
]

# Helper: extract (time, 0|1) pairs from vcdvcd
def trace(name):
    if name not in vcd.references_to_ids:
        return [], []
    tv = vcd[name].tv
    if not tv:
        return [], []
    ts = [t for t, _ in tv]
    vs = []
    for _, raw in tv:
        # Strip leading 'b' on multi-bit values
        v = raw[1:] if isinstance(raw, str) and raw.startswith('b') else raw
        try:
            vs.append(1 if int(str(v), 2) != 0 else 0)
        except (ValueError, TypeError):
            vs.append(0)
    return ts, vs

# Resolve all signals
resolved = {}
for label, vcd_name in signal_specs:
    ts, vs = trace(vcd_name)
    if ts:
        resolved[label] = (ts, vs, vcd_name)
    else:
        print(f'  skip: could not find {vcd_name}')

# End time = last event in any trace
end_time = max(ts[-1] for ts, _, _ in resolved.values())

# Plot
fig, ax = plt.subplots(figsize=(14, 7))
yspacing = 1.6
labels = list(resolved.keys())
labels.reverse()  # so first signal in list appears at top

for i, label in enumerate(labels):
    ts, vs, name = resolved[label]
    y_base = i * yspacing
    # Step plot
    times = list(ts) + [end_time]
    vals  = [v + y_base for v in vs] + [vs[-1] + y_base]
    ax.step(times, vals, where='post', linewidth=1.5)
    # Fill under the curve for clearer "high" visualization
    ax.fill_between(times, y_base, vals, step='post', alpha=0.2)
    # Label on the right
    ax.text(-end_time * 0.01, y_base + 0.5, label,
            ha='right', va='center', fontsize=10, family='monospace')

# Phase annotations (from cosim_run.log timing)
# Approximate phase boundaries; transitions visible in the trace.
phases = [
    (0,             80,      '1. Reset',            '#888888'),
    (80,            720,     '2. WRITE pixel+16 centroids (via AXI)', '#3274A1'),
    (720,           780,     '3. WRITE CTRL.start', '#4C9F70'),
    (780,           830,     '4. Pipeline compute (3 cycles)', '#E74C3C'),
    (830,           end_time,'5. READ STATUS / LABEL / DIST', '#7E57C2'),
]

ymax = len(labels) * yspacing + 0.5
for t0, t1, name, color in phases:
    if t0 >= end_time:
        continue
    t1 = min(t1, end_time)
    ax.axvspan(t0, t1, alpha=0.1, color=color)
    ax.text((t0 + t1) / 2, ymax - 0.2, name,
            ha='center', va='top', fontsize=9, color=color, fontweight='bold')

ax.set_xlim(0, end_time)
ax.set_ylim(-0.5, ymax + 0.3)
ax.set_xlabel('Time (ps)')
ax.set_title('M3 end-to-end AXI4-Lite co-simulation waveform\n'
             'host -> AXI write -> pipeline compute -> AXI read -> PASS',
             fontsize=11)
ax.set_yticks([])
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(OUT_PATH, dpi=150)
plt.close()

print(f'Saved: {OUT_PATH}')
