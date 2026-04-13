"""
K-Means PIM Accelerator Block Diagram
ECE 410/510 Spring 2026 — Bao Nguyen
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(26, 13))
ax.set_xlim(-1, 25)
ax.set_ylim(0, 13)
ax.axis('off')
fig.patch.set_facecolor('white')

def box(ax, x, y, w, h, label, color='#D6EAF8', fontsize=9, bold=False):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.1",
                          linewidth=1.5, edgecolor='#2C3E50',
                          facecolor=color, zorder=2)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, label, ha='center', va='center',
            fontsize=fontsize, fontweight=weight, wrap=True,
            multialignment='center', zorder=3)

def arrow(ax, x1, y1, x2, y2, label='', color='#2C3E50'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5), zorder=4)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my+0.15, label, ha='center', va='bottom', fontsize=7,
                color='#7F8C8D', zorder=5)

# Title
ax.text(11, 12.4, 'K-Means PIM Accelerator — Block Diagram\nBao Nguyen  |  ECE 410/510 Spring 2026',
        ha='center', va='center', fontsize=13, fontweight='bold', color='#1A5276')

# ── Outer accelerator boundary ──
outer = FancyBboxPatch((4.0, 0.5), 13.5, 11.2,
                        boxstyle="round,pad=0.2",
                        linewidth=2, edgecolor='#1A5276',
                        facecolor='#F8F9FA', zorder=1)
ax.add_patch(outer)
ax.text(10.75, 11.4, 'PIM Accelerator Chip', ha='center', va='center',
        fontsize=11, fontweight='bold', color='#1A5276', zorder=3)

# ── External Memory (DRAM) ──
box(ax, 0.3, 5.5, 3.2, 4.0,
    'External\nMemory\n(DRAM)\n\n480K pixels\n16 centroids\nfloat32',
    color='#FADBD8', fontsize=9)

# ── Bus Interface ──
box(ax, 4.1, 4.5, 1.2, 5.5,
    'B\nu\ns\n \nI\nn\nt\ne\nr\nf\na\nc\ne\n \nA\nX\nI\n4',
    color='#D5D8DC', fontsize=8)

# ── Input Buffer ──
box(ax, 5.6, 8.2, 3.8, 2.2,
    'Input Buffer (SRAM)\nPixel Tile: N×3 float32\nCentroids: 16×3 float32',
    color='#D6EAF8', fontsize=9)

# ── Output Buffer ──
box(ax, 5.6, 5.6, 3.8, 2.2,
    'Output Buffer (SRAM)\nMin distances + Labels\nN × int32',
    color='#D6EAF8', fontsize=9)

# ── Distance Engine (MAC Array) ──
box(ax, 10.0, 7.5, 4.2, 3.5,
    'Distance Engine\n(MAC Array)\n\ndist = \u03a3(p\u1d62 \u2212 c\u2c7c)\u00b2\n\nD=3 lanes (RGB)\nK=16 parallel units\nfloat32',
    color='#D5F5E3', fontsize=9)

# ── Accumulator ──
box(ax, 10.0, 5.5, 4.2, 1.7,
    'Accumulator\nPartial sums across D=3 dims',
    color='#FEF9E7', fontsize=9)

# ── Min Selector ──
box(ax, 10.0, 3.5, 4.2, 1.7,
    'Min Selector\nArgmin over K=16 centroids',
    color='#FEF9E7', fontsize=9)

# ── Controller / FSM ──
box(ax, 5.6, 1.2, 3.8, 3.6,
    'Controller (FSM)\n\nTile iteration\nCentroid streaming\nInterface transactions',
    color='#E8DAEF', fontsize=9)

# ── Instr Decode ──
box(ax, 10.0, 1.2, 4.2, 2.0,
    'Instr. Decode\nHost commands\n\u2192 internal ops',
    color='#E8DAEF', fontsize=9)

# ── To Host ──
box(ax, 15.2, 1.2, 2.0, 2.0,
    'To\nHost\n(CPU)',
    color='#FADBD8', fontsize=9)

# ── Arrows ──
# DRAM → Bus
arrow(ax, 3.5, 7.5, 4.1, 7.5, '16 TB/s')
# Bus ← DRAM (bidirectional - write back)
ax.annotate('', xy=(3.5, 6.8), xytext=(4.1, 6.8),
            arrowprops=dict(arrowstyle='<-', color='#2C3E50', lw=1.5), zorder=4)
# Bus → Input Buffer
arrow(ax, 5.3, 9.0, 5.6, 9.0)
# Bus → Output Buffer
arrow(ax, 5.3, 6.7, 5.6, 6.7)
# Input Buffer → Distance Engine
arrow(ax, 9.4, 9.2, 10.0, 9.2)
# Distance Engine → Accumulator
arrow(ax, 12.1, 7.5, 12.1, 7.2)
# Accumulator → Min Selector
arrow(ax, 12.1, 5.5, 12.1, 5.2)
# Min Selector → Output Buffer
arrow(ax, 10.0, 4.3, 9.4, 6.3)
# Controller → Bus
arrow(ax, 5.6, 2.5, 5.3, 5.0)
# Instr Decode → Controller
arrow(ax, 10.0, 2.2, 9.4, 2.5)
# To Host → Instr Decode
arrow(ax, 15.2, 2.2, 14.2, 2.2)

# ── Legend / Notes ──
ax.text(0.3, 4.8, 'Key Design Choices:', fontsize=9, fontweight='bold', color='#1A5276')
notes = [
    '• Algorithm: K-Means',
    '  (image color quant.)',
    '• Kernel: pairwise dist.',
    '  AI = 1.68 FLOP/byte',
    '• CPU ridge = 18.23',
    '  → memory-bound',
    '• Accel BW: 16 TB/s',
    '  ridge = 0.5',
    '  → compute-bound',
    '• Precision: float32',
    '• Interface: AXI4',
    '• Req. BW: ~5 TB/s',
    '  needs HBM/on-die',
]
for i, note in enumerate(notes):
    ax.text(0.3, 4.3 - i*0.36, note, fontsize=8, color='#2C3E50', va='top')

plt.tight_layout()
plt.savefig('kmeans_accelerator_block_diagram.png', dpi=150, bbox_inches='tight',
            facecolor='white')
print("Saved: kmeans_accelerator_block_diagram.png")
