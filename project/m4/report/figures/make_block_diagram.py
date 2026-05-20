#!/usr/bin/env python3
"""Generate the M4 top-level block diagram (Figure 2 in the report)."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).parent / 'block_diagram.png'

fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis('off')

def box(x, y, w, h, label, color, fontsize=10, fontweight='normal'):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.1",
                       linewidth=1.5,
                       facecolor=color,
                       edgecolor='black')
    ax.add_patch(p)
    ax.text(x + w/2, y + h/2, label,
            ha='center', va='center',
            fontsize=fontsize, fontweight=fontweight)

def arrow(x1, y1, x2, y2, label=None, label_offset=(0, 0.2), color='black'):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                 arrowstyle='->',
                                 mutation_scale=18,
                                 color=color, linewidth=1.5))
    if label:
        mx, my = (x1+x2)/2 + label_offset[0], (y1+y2)/2 + label_offset[1]
        ax.text(mx, my, label, ha='center', va='center', fontsize=8,
                color=color, style='italic')

# Host CPU
box(0.2, 7.8, 2.6, 1.6, "Host CPU\n(i9-12900H)\nK-Means outer loop\n+ centroid update", '#FFE4B5')

# UCIe interface (M1 architecture)
box(3.4, 7.8, 2.6, 1.6, "UCIe chiplet link\n2.56 TB/s\n(51× over 50 GB/s req)", '#E0F0FF')

# AXI4-Lite slave (interface.sv)
box(6.6, 7.8, 3.0, 1.6, "AXI4-Lite Slave\n(interface.sv)\n51-byte reg file\nWR FSM + RD FSM", '#C8E6C9', fontweight='bold')

# top.sv label
ax.text(8.0, 9.6, 'top.sv', fontsize=11, fontweight='bold', ha='center', style='italic')

# kmeans_dist_core_pipelined - 3 stages
box(10.4, 7.8, 5.2, 1.6, "Pipelined Compute Core (compute_core.sv)", '#FFF', fontweight='bold')
# Stage 1
box(10.6, 6.4, 1.6, 1.0, "Stage 1\nkdist[k]\n× 16 par", '#FFCDD2', fontsize=9)
# Stage 2
box(12.4, 6.4, 1.6, 1.0, "Stage 2\nargmin\n16→8→4", '#FFB347', fontsize=9)
# Stage 3
box(14.2, 6.4, 1.4, 1.0, "Stage 3\nargmin\n4→2→1", '#FFD89E', fontsize=9)
# Stage labels above
arrow(11.4, 6.4, 11.4, 6.0, '+register', color='gray')
arrow(13.2, 6.4, 13.2, 6.0, '+register', color='gray')
arrow(14.9, 6.4, 14.9, 6.0, '+register', color='gray')

# HBM3 memory (M1 target, dashed style)
box(0.2, 4.8, 2.6, 1.6, "HBM3 stack\n16 TB/s\n(M1 PIM target)", '#FFE4B5')
ax.text(1.5, 4.4, '(future: streaming\nfeeder bypasses AXI)', ha='center', fontsize=7,
        color='gray', style='italic')

# Result outputs
box(11.0, 2.8, 4.0, 1.6, "Outputs\n  RESULT_LABEL [3:0]\n  RESULT_DIST  [17:0]\n  STATUS.done", '#C8E6C9')

# Arrows host -> UCIe -> AXI -> core
arrow(2.8, 8.6, 3.4, 8.6, "AXI-Lite")
arrow(6.0, 8.6, 6.6, 8.6, "AXI-Lite")
arrow(9.6, 8.6, 10.4, 8.6, "pixel_flat,\ncentroids_flat", label_offset=(0.5, 0))
arrow(11.4, 7.8, 11.4, 7.4, color='#666')

# Core outputs back to slave -> host
arrow(13.0, 4.4, 13.0, 4.8, color='#666')
arrow(11.0, 3.6, 8.1, 3.6, "AXI read\n(label, dist)", label_offset=(0, 0.3))
arrow(8.1, 3.6, 8.1, 7.8, color='#666')

# HBM3 -> chiplet path (currently unwired)
arrow(2.8, 5.6, 7.8, 5.6, color='gray', label_offset=(0, 0.4))
ax.text(5.3, 6.0, "(M1 target: HBM3 → PIM chiplet streaming)\nnot in M4 scope",
        ha='center', fontsize=8, style='italic', color='gray')

# Title
ax.text(8, 9.8, 'M4 top.sv: AXI4-Lite slave + 3-stage pipelined integer compute core',
        ha='center', fontsize=11, fontweight='bold')

# Legend
ax.text(0.2, 1.3, "Legend:", fontsize=9, fontweight='bold')
ax.text(0.2, 0.9, "Color = module boundary | dashed arrows = M1 system-level (not in M4 RTL)", fontsize=8)
ax.text(0.2, 0.5, "All registers single-domain at clk (10 ns target, +3.13 ns slack)", fontsize=8)

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches='tight')
plt.close()
print(f'Saved: {OUT}')
