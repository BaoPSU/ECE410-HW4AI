"""
K-Means PIM Accelerator Block Diagram
ECE 410/510 Spring 2026 — Bao Nguyen
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(16, 10))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
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
ax.text(8, 9.5, 'K-Means PIM Accelerator — Block Diagram\nBao Nguyen  |  ECE 410/510 Spring 2026',
        ha='center', va='center', fontsize=12, fontweight='bold', color='#1A5276')

# ── Outer accelerator boundary ──
outer = FancyBboxPatch((3.2, 0.4), 10.5, 8.5,
                        boxstyle="round,pad=0.15",
                        linewidth=2, edgecolor='#1A5276',
                        facecolor='#F8F9FA', zorder=1)
ax.add_patch(outer)
ax.text(8.45, 8.7, 'PIM Accelerator Chip', ha='center', va='center',
        fontsize=10, fontweight='bold', color='#1A5276', zorder=3)

# ── External Memory (DRAM) ──
box(ax, 0.2, 4.5, 2.6, 3.2,
    'External\nMemory\n(DRAM)\n\n480K pixels\n16 centroids\nfloat32',
    color='#FADBD8', fontsize=8)

# ── Bus Interface ──
box(ax, 3.3, 3.8, 1.0, 4.5,
    'B\nu\ns\n\nI\nn\nt\ne\nr\nf\na\nc\ne\n\nA\nX\nI\n4',
    color='#D5D8DC', fontsize=7)

# ── Input Buffer ──
box(ax, 4.6, 6.5, 2.8, 1.8,
    'Input Buffer (SRAM)\nPixel Tile: N×3 float32\nCentroids: 16×3 float32',
    color='#D6EAF8', fontsize=8)

# ── Output Buffer ──
box(ax, 4.6, 4.5, 2.8, 1.6,
    'Output Buffer (SRAM)\nMin distances + Labels\nN × int32',
    color='#D6EAF8', fontsize=8)

# ── Distance Engine (MAC Array) ──
box(ax, 8.0, 5.8, 3.2, 2.8,
    'Distance Engine\n(MAC Array)\n\ndist = Σ(pᵢ − cⱼ)²\n\nD=3 lanes (RGB)\nK=16 parallel units\nfloat32',
    color='#D5F5E3', fontsize=8, bold=False)

# ── Accumulator ──
box(ax, 8.0, 4.2, 3.2, 1.3,
    'Accumulator\nPartial sums across D=3 dims',
    color='#FEF9E7', fontsize=8)

# ── Min Selector ──
box(ax, 8.0, 2.8, 3.2, 1.1,
    'Min Selector\nArgmin over K=16 centroids',
    color='#FEF9E7', fontsize=8)

# ── Controller / FSM ──
box(ax, 4.6, 1.0, 2.8, 2.8,
    'Controller\n(FSM)\n\nTile iteration\nCentroid streaming\nInterface transactions',
    color='#E8DAEF', fontsize=8)

# ── Instr Decode ──
box(ax, 8.0, 1.0, 3.2, 1.5,
    'Instr. Decode\nHost commands → internal ops',
    color='#E8DAEF', fontsize=8)

# ── To Host ──
box(ax, 12.0, 1.0, 1.5, 1.5,
    'To\nHost\n(CPU)',
    color='#FADBD8', fontsize=8)

# ── Arrows ──
# DRAM → Bus
arrow(ax, 2.8, 6.1, 3.3, 6.1, '16 TB/s')
# Bus → Input Buffer
arrow(ax, 4.3, 7.0, 4.6, 7.4)
# Bus → Output Buffer
arrow(ax, 4.3, 5.3, 4.6, 5.3)
# Input Buffer → Distance Engine
arrow(ax, 7.4, 7.4, 8.0, 7.2)
# Distance Engine → Accumulator
arrow(ax, 9.6, 5.8, 9.6, 5.5)
# Accumulator → Min Selector
arrow(ax, 9.6, 4.2, 9.6, 3.9)
# Min Selector → Output Buffer
arrow(ax, 8.0, 3.35, 7.4, 5.1)
# Controller → Bus
arrow(ax, 4.6, 2.4, 4.3, 4.5)
# Instr Decode → Controller
arrow(ax, 8.0, 1.75, 7.4, 2.0)
# To Host ↔ Bus (via bottom)
arrow(ax, 12.0, 1.75, 8.0+3.2, 1.75)
# Bus → DRAM (write back)
ax.annotate('', xy=(2.8, 5.5), xytext=(3.3, 5.5),
            arrowprops=dict(arrowstyle='<-', color='#2C3E50', lw=1.5), zorder=4)

# ── Legend / Notes ──
ax.text(12.0, 8.5, 'Key Design Choices:', fontsize=9, fontweight='bold', color='#1A5276')
notes = [
    '• Algorithm: K-Means (image color quantization)',
    '• Kernel: pairwise distance (AI = 1.68 FLOP/byte)',
    '• Bottleneck: memory-bound on CPU (ridge = 18.23)',
    '• Accelerator BW: 16 TB/s → ridge = 0.5 → compute-bound',
    '• Precision: float32 (4 bytes/element)',
    '• Interface: AXI4-Stream (data), AXI4-Lite (control)',
    '• Required BW: ~5 TB/s → needs on-die SRAM/HBM',
]
for i, note in enumerate(notes):
    ax.text(12.0, 8.1 - i*0.42, note, fontsize=7.5, color='#2C3E50', va='top')

plt.tight_layout()
plt.savefig('kmeans_accelerator_block_diagram.png', dpi=150, bbox_inches='tight',
            facecolor='white')
print("Saved: kmeans_accelerator_block_diagram.png")
