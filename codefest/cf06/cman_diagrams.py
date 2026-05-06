"""Generate CMAN sneak path diagrams — ideal read vs sneak path."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import matplotlib.patheffects as pe

def draw_crossbar(ax, title,
                  row1_grounded=True, col1_grounded=True,
                  show_sneak=False):
    """Draw the 2x2 resistive crossbar with current flow annotations."""
    ax.set_xlim(-1.5, 5.5)
    ax.set_ylim(-2.2, 4.5)
    ax.set_facecolor('#F8F9FA')
    ax.axis('off')

    # ── grid positions ──────────────────────────────────────
    # cols at x=1, x=3  /  rows at y=2, y=0
    COL0_X, COL1_X = 1.0, 3.0
    ROW0_Y, ROW1_Y = 2.0, 0.0

    # ── draw column wires ────────────────────────────────────
    for x in [COL0_X, COL1_X]:
        ax.plot([x, x], [-1.2, 3.5], color='#555', lw=2, zorder=1)

    # ── draw row wires ────────────────────────────────────────
    # row 0 — solid (driven)
    ax.plot([-0.8, 4.5], [ROW0_Y, ROW0_Y], color='#555', lw=2, zorder=1)
    # row 1 — dashed if floating
    ls = '-' if row1_grounded else '--'
    ax.plot([-0.8, 4.5], [ROW1_Y, ROW1_Y], color='#555', lw=2, ls=ls, zorder=1)

    # ── resistor boxes ───────────────────────────────────────
    cells = [
        (COL0_X, ROW0_Y, '1 kΩ\non',  '#2ecc71'),
        (COL1_X, ROW0_Y, '2 kΩ\noff', '#e74c3c'),
        (COL0_X, ROW1_Y, '2 kΩ\noff', '#e74c3c'),
        (COL1_X, ROW1_Y, '1 kΩ\non',  '#2ecc71'),
    ]
    for (cx, cy, lbl, col) in cells:
        r = FancyBboxPatch((cx-0.38, cy-0.38), 0.76, 0.76,
                           boxstyle='round,pad=0.05',
                           fc=col, ec='white', lw=2, zorder=3)
        ax.add_patch(r)
        ax.text(cx, cy, lbl, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color='white', zorder=4)

    # ── voltage source labels ────────────────────────────────
    # V_row0
    ax.annotate('', xy=(-0.5, ROW0_Y), xytext=(-1.2, ROW0_Y),
                arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=2))
    src = FancyBboxPatch((-1.45, ROW0_Y-0.3), 0.9, 0.6,
                         boxstyle='round,pad=0.05', fc='#3498db', ec='white', lw=2, zorder=3)
    ax.add_patch(src)
    ax.text(-1.0, ROW0_Y, '1 V\nrow0', ha='center', va='center',
            fontsize=9, fontweight='bold', color='white', zorder=4)

    # row 1 label
    if row1_grounded:
        ax.text(4.7, ROW1_Y, '0 V\n(gnd)', ha='left', va='center',
                fontsize=9, color='#7f8c8d')
    else:
        box = FancyBboxPatch((4.3, ROW1_Y-0.28), 1.1, 0.56,
                             boxstyle='round,pad=0.05', fc='#f39c12', ec='white', lw=2, zorder=3)
        ax.add_patch(box)
        ax.text(4.85, ROW1_Y, 'float\nrow1', ha='center', va='center',
                fontsize=9, fontweight='bold', color='white', zorder=4)
        if show_sneak:
            ax.text(4.85, ROW1_Y-0.55, '= 0.4 V', ha='center',
                    fontsize=8.5, color='#e67e22', fontstyle='italic')

    # col 0 bottom — sense (0V)
    ax.text(COL0_X, -1.6, '0 V\n(sense)', ha='center', va='top',
            fontsize=9, color='#7f8c8d')
    ax.annotate('', xy=(COL0_X, -1.1), xytext=(COL0_X, -1.55),
                arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=1.5))

    # col 1 bottom label
    if col1_grounded:
        ax.text(COL1_X, -1.6, '0 V\n(gnd)', ha='center', va='top',
                fontsize=9, color='#7f8c8d')
        ax.annotate('', xy=(COL1_X, -1.1), xytext=(COL1_X, -1.55),
                    arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=1.5))
    else:
        box2 = FancyBboxPatch((COL1_X-0.55, -2.05), 1.1, 0.56,
                              boxstyle='round,pad=0.05', fc='#f39c12', ec='white', lw=2, zorder=3)
        ax.add_patch(box2)
        ax.text(COL1_X, -1.77, 'float\ncol1', ha='center', va='center',
                fontsize=9, fontweight='bold', color='white', zorder=4)
        if show_sneak:
            ax.text(COL1_X, -2.15, '= 0.6 V', ha='center',
                    fontsize=8.5, color='#e67e22', fontstyle='italic')

    # ── current arrows ────────────────────────────────────────
    INTENDED_COLOR = '#2980b9'
    SNEAK_COLOR    = '#e74c3c'
    AW = dict(arrowstyle='->', lw=3, mutation_scale=18)

    # Intended path: row0 → R[0][0] → col0
    # Arrow down from row0 wire into R[0][0], then down to col0
    ax.annotate('', xy=(COL0_X, ROW0_Y-0.42), xytext=(COL0_X, ROW0_Y+0.55),
                arrowprops=dict(**AW, color=INTENDED_COLOR))
    ax.annotate('', xy=(COL0_X, -0.9), xytext=(COL0_X, ROW0_Y-0.82),
                arrowprops=dict(**AW, color=INTENDED_COLOR))
    ax.text(COL0_X+0.15, 1.1, '1 mA', color=INTENDED_COLOR,
            fontsize=11, fontweight='bold')

    # Sneak path arrows
    if show_sneak:
        # row0 → R[0][1] (right along row 0, then down into R[0][1])
        ax.annotate('', xy=(COL1_X, ROW0_Y+0.55), xytext=(COL0_X+0.6, ROW0_Y+0.55),
                    arrowprops=dict(**AW, color=SNEAK_COLOR))
        ax.annotate('', xy=(COL1_X, ROW0_Y-0.42), xytext=(COL1_X, ROW0_Y+0.55),
                    arrowprops=dict(**AW, color=SNEAK_COLOR))
        # col1 → R[1][1] (down col1 wire)
        ax.annotate('', xy=(COL1_X, ROW1_Y+0.42), xytext=(COL1_X, ROW0_Y-0.82),
                    arrowprops=dict(**AW, color=SNEAK_COLOR))
        # R[1][1] → row1 (down into row1)
        ax.annotate('', xy=(COL1_X, ROW1_Y-0.42), xytext=(COL1_X, ROW1_Y+0.42),
                    arrowprops=dict(**AW, color=SNEAK_COLOR))
        # row1 → R[1][0] (left along row1)
        ax.annotate('', xy=(COL0_X+0.6, ROW1_Y-0.55), xytext=(COL1_X-0.6, ROW1_Y-0.55),
                    arrowprops=dict(**AW, color=SNEAK_COLOR))
        ax.annotate('', xy=(COL0_X, ROW1_Y-0.42), xytext=(COL0_X+0.6, ROW1_Y-0.55),
                    arrowprops=dict(**AW, color=SNEAK_COLOR))
        # R[1][0] → col0
        ax.annotate('', xy=(COL0_X, -0.9), xytext=(COL0_X, ROW1_Y-0.82),
                    arrowprops=dict(**AW, color=SNEAK_COLOR))

        ax.text(COL1_X+0.15, 1.1, '0.2 mA', color=SNEAK_COLOR,
                fontsize=11, fontweight='bold')
        ax.text(COL1_X+0.15, 0.7, '(sneak)', color=SNEAK_COLOR,
                fontsize=9)

        # total at col0
        ax.text(COL0_X-0.55, -0.7, 'I_col0\n= 1.2 mA', color='#8e44ad',
                fontsize=11, fontweight='bold', ha='right')

    else:
        ax.text(COL0_X-0.55, -0.7, 'I_col0\n= 1 mA', color=INTENDED_COLOR,
                fontsize=11, fontweight='bold', ha='right')

    # ── legend ───────────────────────────────────────────────
    handles = [mpatches.Patch(color=INTENDED_COLOR, label='Intended current (1 mA)')]
    if show_sneak:
        handles.append(mpatches.Patch(color=SNEAK_COLOR, label='Sneak path (0.2 mA)'))
    ax.legend(handles=handles, loc='upper right', fontsize=10,
              framealpha=0.9, edgecolor='#bdc3c7')

    ax.set_title(title, fontsize=14, fontweight='bold', color='#2c3e50', pad=6)


# ── Figure 1: Ideal read ─────────────────────────────────────
fig1, ax1 = plt.subplots(figsize=(6, 7))
fig1.patch.set_facecolor('#F8F9FA')
draw_crossbar(ax1,
              'Task 1 — Ideal Read\nrow1=0V, col1=0V (grounded)',
              row1_grounded=True, col1_grounded=True,
              show_sneak=False)
plt.tight_layout()
plt.savefig('/home/bao/ECE410-HW4AI/codefest/cf06/cman_ideal.png',
            dpi=150, bbox_inches='tight')
plt.close()
print('saved cman_ideal.png')

# ── Figure 2: Sneak path ─────────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(6, 7))
fig2.patch.set_facecolor('#F8F9FA')
draw_crossbar(ax2,
              'Task 2 — Sneak Path Read\nrow1=float, col1=float',
              row1_grounded=False, col1_grounded=False,
              show_sneak=True)
plt.tight_layout()
plt.savefig('/home/bao/ECE410-HW4AI/codefest/cf06/cman_sneak.png',
            dpi=150, bbox_inches='tight')
plt.close()
print('saved cman_sneak.png')
