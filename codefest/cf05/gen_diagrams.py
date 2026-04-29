"""Generate CF05 systolic array diagrams."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

OUT_DIR = os.path.dirname(__file__)

PE_BLUE   = '#4472C4'
GREEN     = '#70AD47'
GRAY      = '#BFBFBF'
ORANGE    = '#ED7D31'
RED       = '#FF0000'
WHITE     = '#FFFFFF'
NAVY      = '#1F3864'


def draw_pe_box(ax, cx, cy, label, weight, ps_val, active, output_val=None):
    bw, bh = 2.2, 1.6
    color = GREEN if active else (GRAY if ps_val == 0 and not active else PE_BLUE)
    rect = mpatches.FancyBboxPatch(
        (cx - bw/2, cy - bh/2), bw, bh,
        boxstyle="round,pad=0.08",
        facecolor=color, edgecolor=NAVY, linewidth=1.5, zorder=3
    )
    ax.add_patch(rect)
    ax.text(cx, cy + 0.38, label,  ha='center', va='center', fontsize=8.5,
            fontweight='bold', color=WHITE, zorder=4)
    ax.text(cx, cy + 0.0,  f'w={weight}', ha='center', va='center', fontsize=8,
            color=WHITE, zorder=4)
    ps_text = f'ps={ps_val}' if output_val is None else f'→ {output_val}'
    ps_color = RED if output_val is not None else WHITE
    ax.text(cx, cy - 0.42, ps_text, ha='center', va='center', fontsize=7.5,
            color=ps_color, fontweight='bold' if output_val else 'normal', zorder=4)


def arrow(ax, x0, y0, x1, y1, color='black', lw=1.5):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw),
                zorder=2)


# ── Figure 1: static PE array ─────────────────────────────────────────────────
def make_pe_array():
    fig, ax = plt.subplots(figsize=(7, 5.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis('off')

    pos = {(0,0):(3,6), (0,1):(7,6), (1,0):(3,2.2), (1,1):(7,2.2)}
    weights = {(0,0):5, (0,1):6, (1,0):7, (1,1):8}
    bw, bh = 2.2, 1.6

    for (i,j),(cx,cy) in pos.items():
        rect = mpatches.FancyBboxPatch(
            (cx-bw/2, cy-bh/2), bw, bh,
            boxstyle="round,pad=0.08",
            facecolor=PE_BLUE, edgecolor=NAVY, linewidth=2, zorder=3
        )
        ax.add_patch(rect)
        ax.text(cx, cy+0.35, f'PE[{i}][{j}]', ha='center', va='center',
                fontsize=11, fontweight='bold', color=WHITE, zorder=4)
        ax.text(cx, cy-0.30, f'weight = {weights[(i,j)]}', ha='center', va='center',
                fontsize=10, color=WHITE, zorder=4)

    # Horizontal input arrows
    for row, label in [(0, 'A[m][0]'), (1, 'A[m][1]')]:
        cx, cy = pos[(row, 0)]
        arrow(ax, 0.8, cy, cx-bw/2, cy, color='black', lw=2)
        ax.text(0.4, cy+0.28, label, fontsize=9, ha='center', color='black')

    # Horizontal pass-through arrows (row 0 and row 1)
    for row in [0, 1]:
        x0 = pos[(row,0)][0] + bw/2
        x1 = pos[(row,1)][0] - bw/2
        cy = pos[(row,0)][1]
        arrow(ax, x0, cy, x1, cy, color='black', lw=2)

    # Vertical partial-sum arrows
    for col in [0, 1]:
        y0 = pos[(0,col)][1] - bh/2
        y1 = pos[(1,col)][1] + bh/2
        cx = pos[(0,col)][0]
        arrow(ax, cx, y0, cx, y1, color=ORANGE, lw=2)
        ax.text(cx+0.28, (y0+y1)/2, 'ps↓', fontsize=9, color=ORANGE, va='center')

    # Output arrows
    for col in [0, 1]:
        cx, cy = pos[(1,col)]
        arrow(ax, cx, cy-bh/2, cx, 0.6, color=RED, lw=2)
        ax.text(cx, 0.25, f'C[m][{col}]', fontsize=9, ha='center', color=RED,
                fontweight='bold')

    # Row labels
    ax.text(9.6, pos[(0,0)][1], 'Row 0\n(k=0)', fontsize=8.5, ha='center',
            va='center', color='gray')
    ax.text(9.6, pos[(1,0)][1], 'Row 1\n(k=1)', fontsize=8.5, ha='center',
            va='center', color='gray')

    ax.set_title('2×2 Weight-Stationary Systolic Array — Preloaded Weights',
                 fontsize=12, fontweight='bold', pad=10)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'pe_array_diagram.png'), dpi=150,
                bbox_inches='tight')
    plt.close(fig)
    print('Saved pe_array_diagram.png')


# ── Figure 2: 4-cycle trace ───────────────────────────────────────────────────
CYCLES = [
    {
        'title': 'Cycle 1 — Feed A[0][0]=1 → Row 0',
        'row0_input': ('A[0][0]=1', True),
        'row1_input': ('bubble (0)', False),
        'pes': {
            (0,0): (5,  5,  True,  None),
            (0,1): (6,  6,  True,  None),
            (1,0): (7,  0,  False, None),
            (1,1): (8,  0,  False, None),
        },
        'output': None,
    },
    {
        'title': 'Cycle 2 — Feed A[0][1]=2 → Row 1',
        'row0_input': ('bubble (0)', False),
        'row1_input': ('A[0][1]=2', True),
        'pes': {
            (0,0): (5,  5,  True,  None),
            (0,1): (6,  6,  True,  None),
            (1,0): (7, 19,  True,  'C[0][0]=19'),
            (1,1): (8, 22,  True,  'C[0][1]=22'),
        },
        'output': 'C[0] = [19, 22]',
    },
    {
        'title': 'Cycle 3 — Feed A[1][0]=3 → Row 0',
        'row0_input': ('A[1][0]=3', True),
        'row1_input': ('bubble (0)', False),
        'pes': {
            (0,0): (5, 15,  True,  None),
            (0,1): (6, 18,  True,  None),
            (1,0): (7,  0,  False, None),
            (1,1): (8,  0,  False, None),
        },
        'output': None,
    },
    {
        'title': 'Cycle 4 — Feed A[1][1]=4 → Row 1',
        'row0_input': ('bubble (0)', False),
        'row1_input': ('A[1][1]=4', True),
        'pes': {
            (0,0): (5, 15,  True,  None),
            (0,1): (6, 18,  True,  None),
            (1,0): (7, 43,  True,  'C[1][0]=43'),
            (1,1): (8, 50,  True,  'C[1][1]=50'),
        },
        'output': 'C[1] = [43, 50]',
    },
]


def make_cycle_trace():
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle('Cycle-by-Cycle Trace — Weight-Stationary 2×2 Systolic Array',
                 fontsize=13, fontweight='bold', y=1.01)

    for ax, cyc in zip(axes.flat, CYCLES):
        ax.set_xlim(0, 10); ax.set_ylim(0, 8.5); ax.axis('off')
        ax.set_title(cyc['title'], fontsize=9, fontweight='bold', pad=4)

        pos = {(0,0):(3,6.2), (0,1):(7,6.2), (1,0):(3,2.5), (1,1):(7,2.5)}
        bw, bh = 2.2, 1.6

        for (i,j),(cx,cy) in pos.items():
            weight, ps_val, active, out_val = cyc['pes'][(i,j)]
            draw_pe_box(ax, cx, cy, f'PE[{i}][{j}]', weight, ps_val, active, out_val)

        # Input labels
        for row_idx, key in enumerate(['row0_input', 'row1_input']):
            label, active = cyc[key]
            row = row_idx
            cx, cy = pos[(row, 0)]
            color = GREEN if active else GRAY
            ax.annotate('', xy=(cx-bw/2, cy), xytext=(0.8, cy),
                        arrowprops=dict(arrowstyle='->', color=color, lw=1.5), zorder=2)
            ax.text(0.35, cy+0.28, label, fontsize=7, ha='center', color=color,
                    fontweight='bold' if active else 'normal')

        # Horizontal pass-through arrows
        for row in [0, 1]:
            x0 = pos[(row,0)][0] + bw/2
            x1 = pos[(row,1)][0] - bw/2
            cy = pos[(row,0)][1]
            arrow(ax, x0, cy, x1, cy, color='black', lw=1.2)

        # Vertical partial-sum arrows
        for col in [0, 1]:
            y0 = pos[(0,col)][1] - bh/2
            y1 = pos[(1,col)][1] + bh/2
            cx = pos[(0,col)][0]
            _, ps0, _, _ = cyc['pes'][(0,col)]
            ps_active = ps0 > 0
            clr = ORANGE if ps_active else GRAY
            arrow(ax, cx, y0, cx, y1, color=clr, lw=1.5)

        # Output arrows
        for col in [0, 1]:
            cx, cy = pos[(1,col)]
            _, _, _, out_val = cyc['pes'][(1,col)]
            clr = RED if out_val else GRAY
            arrow(ax, cx, cy-bh/2, cx, 0.7, color=clr, lw=1.5)
            if out_val:
                ax.text(cx, 0.35, out_val, fontsize=7, ha='center', color=RED,
                        fontweight='bold')

        # Output banner
        if cyc['output']:
            ax.text(5, 8.1, f'Output: {cyc["output"]}', ha='center', va='center',
                    fontsize=9, fontweight='bold', color=RED,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFE0E0',
                              edgecolor=RED, linewidth=1.5))

    # Legend
    handles = [
        mpatches.Patch(color=GREEN,   label='Active / computing'),
        mpatches.Patch(color=PE_BLUE, label='Holding partial sum'),
        mpatches.Patch(color=GRAY,    label='Idle / bubble'),
    ]
    fig.legend(handles=handles, loc='lower center', ncol=3, fontsize=9,
               frameon=True, bbox_to_anchor=(0.5, -0.03))

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'cycle_trace.png'), dpi=150,
                bbox_inches='tight')
    plt.close(fig)
    print('Saved cycle_trace.png')


if __name__ == '__main__':
    make_pe_array()
    make_cycle_trace()
