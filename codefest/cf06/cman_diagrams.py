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


# ── Equivalent circuit diagrams ──────────────────────────────

def draw_resistor(ax, x0, y0, x1, y1, label, color='#2c3e50'):
    """Draw a resistor as a labeled rectangle between two points."""
    mx, my = (x0+x1)/2, (y0+y1)/2
    is_horiz = abs(x1-x0) > abs(y1-y0)

    # wire segments to resistor box
    if is_horiz:
        ax.plot([x0, mx-0.55], [y0, y0], color='#444', lw=2)
        ax.plot([mx+0.55, x1], [y1, y1], color='#444', lw=2)
        r = FancyBboxPatch((mx-0.55, my-0.22), 1.1, 0.44,
                           boxstyle='round,pad=0.04', fc='#ecf0f1',
                           ec=color, lw=2.5, zorder=3)
    else:
        ax.plot([x0, x0], [y0, my-0.3], color='#444', lw=2)
        ax.plot([x1, x1], [my+0.3, y1], color='#444', lw=2)
        r = FancyBboxPatch((mx-0.45, my-0.3), 0.9, 0.6,
                           boxstyle='round,pad=0.04', fc='#ecf0f1',
                           ec=color, lw=2.5, zorder=3)

    ax.add_patch(r)
    ax.text(mx, my, label, ha='center', va='center',
            fontsize=9, fontweight='bold', color=color, zorder=4)

def gnd(ax, x, y):
    """Draw a ground symbol."""
    ax.plot([x, x], [y, y-0.25], color='#555', lw=2)
    for i, w in enumerate([0.35, 0.22, 0.1]):
        ax.plot([x-w, x+w], [y-0.25-i*0.12, y-0.25-i*0.12], color='#555', lw=2)

def vsrc(ax, x, y, label='1 V'):
    """Draw a voltage source circle."""
    circ = plt.Circle((x, y), 0.32, fc='#3498db', ec='white', lw=2, zorder=3)
    ax.add_patch(circ)
    ax.text(x, y, label, ha='center', va='center',
            fontsize=9, fontweight='bold', color='white', zorder=4)

def node_label(ax, x, y, label, color='#2c3e50', side='left'):
    offset = -0.15 if side == 'left' else 0.15
    ha = 'right' if side == 'left' else 'left'
    ax.text(x+offset, y, label, ha=ha, va='center',
            fontsize=9.5, color=color, fontweight='bold')


# ── Task 1 equivalent circuit ─────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
ax.set_xlim(-1, 8); ax.set_ylim(-1.5, 4)
ax.axis('off'); ax.set_facecolor('#F8F9FA')
fig.patch.set_facecolor('#F8F9FA')

BLUE = '#2980b9'
GRAY = '#95a5a6'

# nodes
# row0 node at (1, 3), col0 node at (1, 0.5), gnd at bottom
# Just showing the two parallel paths from row0 to col0

# Top wire (row 0 = 1V)
ax.plot([0.5, 7], [3, 3], color='#444', lw=2)
# Bottom wire (col 0 = 0V sense)
ax.plot([0.5, 7], [0.5, 0.5], color='#444', lw=2)

# Voltage source on left
vsrc(ax, 0.5, 1.75, '1 V')
ax.plot([0.5, 0.5], [0.5, 1.43], color='#444', lw=2)
ax.plot([0.5, 0.5], [2.07, 3.0], color='#444', lw=2)
ax.text(0.1, 1.75, 'V_row0', ha='right', va='center', fontsize=9, color='#3498db', fontweight='bold')

# Path 1: R[0][0] = 1kΩ (active, blue)
draw_resistor(ax, 2.0, 3.0, 2.0, 0.5, 'R[0][0]\n1 kΩ', color=BLUE)
ax.annotate('', xy=(2.0, 1.4), xytext=(2.0, 1.9),
            arrowprops=dict(arrowstyle='->', color=BLUE, lw=2.5, mutation_scale=16))
ax.text(2.35, 1.65, '1 mA', color=BLUE, fontsize=10, fontweight='bold')

# Path 2: R[1][0] = 2kΩ (no current, gray)
draw_resistor(ax, 4.0, 3.0, 4.0, 0.5, 'R[1][0]\n2 kΩ', color=GRAY)
ax.text(4.4, 1.65, '0 mA', color=GRAY, fontsize=10)
ax.text(3.3, -0.3, 'row1 = 0V\n→ no ΔV across R[1][0]', ha='center',
        fontsize=8.5, color=GRAY, style='italic')

# Path 3: R[0][1] = 2kΩ col1 side (no contribution to col0)
draw_resistor(ax, 6.0, 3.0, 6.0, 0.5, 'R[0][1]\n2 kΩ', color=GRAY)
ax.text(6.4, 1.65, '→ col1', color=GRAY, fontsize=9)
ax.text(5.8, -0.3, 'col1 = 0V\n→ no effect on col0', ha='center',
        fontsize=8.5, color=GRAY, style='italic')

# Ground at bottom
gnd(ax, 3.5, 0.5)
ax.text(3.5, -0.05, '0 V  (col0 / sense)', ha='center', fontsize=9, color='#555')

# Node labels
node_label(ax, 1.1, 3.0, 'row0 = 1V', '#2c3e50', 'right')

# Result box
res = FancyBboxPatch((5.5, 2.2), 1.9, 0.7,
                     boxstyle='round,pad=0.08', fc='#2980b9', ec='white', lw=2)
ax.add_patch(res)
ax.text(6.45, 2.55, 'I_col0 = 1 mA', ha='center', va='center',
        fontsize=11, fontweight='bold', color='white')

ax.set_title('Task 1 — Equivalent Circuit (Ideal Read)', fontsize=13,
             fontweight='bold', color='#2c3e50')
plt.tight_layout()
plt.savefig('/home/bao/ECE410-HW4AI/codefest/cf06/cman_equiv_ideal.png',
            dpi=150, bbox_inches='tight')
plt.close()
print('saved cman_equiv_ideal.png')


# ── Task 2 equivalent circuit ─────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 6.5))
ax.set_xlim(-0.5, 10); ax.set_ylim(-1.8, 5.5)
ax.axis('off'); ax.set_facecolor('#F8F9FA')
fig.patch.set_facecolor('#F8F9FA')

RED  = '#e74c3c'
BLUE = '#2980b9'
PURP = '#8e44ad'

# ── Main rail wires ──
# row0 top rail  y=4.5
# col0 bottom    y=0.5
ax.plot([0.5, 9.5], [4.5, 4.5], color='#444', lw=2)   # row0 top
ax.plot([0.5, 2.5], [0.5, 0.5], color='#444', lw=2)   # col0 bottom left
ax.plot([7.5, 9.5], [0.5, 0.5], color='#444', lw=2)   # col0 bottom right (join)

# Voltage source
vsrc(ax, 0.5, 2.5, '1 V')
ax.plot([0.5, 0.5], [0.5, 2.18], color='#444', lw=2)
ax.plot([0.5, 0.5], [2.82, 4.5], color='#444', lw=2)
ax.text(0.08, 2.5, 'V_row0', ha='right', va='center', fontsize=9,
        color='#3498db', fontweight='bold')

# ── Path 1: Direct  row0 → R[0][0] → col0 (blue) ──
draw_resistor(ax, 2.0, 4.5, 2.0, 0.5, 'R[0][0]\n1 kΩ', color=BLUE)
ax.annotate('', xy=(2.0, 2.2), xytext=(2.0, 2.8),
            arrowprops=dict(arrowstyle='->', color=BLUE, lw=2.5, mutation_scale=16))
ax.text(2.35, 2.5, '1 mA', color=BLUE, fontsize=10.5, fontweight='bold')

# ── Sneak path: row0 → R[0][1] → col1 → R[1][1] → row1 → R[1][0] → col0 ──
# R[0][1] vertical  x=5  top to mid-col1 node
SNEAK_Y_COL1 = 3.0   # col1 floating node y
SNEAK_Y_ROW1 = 1.8   # row1 floating node y

# wire: row0 rail to R[0][1] top
ax.plot([5.0, 5.0], [4.5, 4.5], color='#444', lw=1.5)
draw_resistor(ax, 5.0, 4.5, 5.0, SNEAK_Y_COL1, 'R[0][1]\n2 kΩ', color=RED)
ax.annotate('', xy=(5.0, 3.7), xytext=(5.0, 4.1),
            arrowprops=dict(arrowstyle='->', color=RED, lw=2.5, mutation_scale=14))

# col1 floating node
circ1 = plt.Circle((5.0, SNEAK_Y_COL1), 0.12, fc=RED, zorder=5)
ax.add_patch(circ1)
ax.text(5.55, SNEAK_Y_COL1, 'V_col1\n= 0.6 V', ha='left', va='center',
        fontsize=9.5, color=RED, fontweight='bold')

# R[1][1] below col1 node
draw_resistor(ax, 5.0, SNEAK_Y_COL1, 5.0, SNEAK_Y_ROW1, 'R[1][1]\n1 kΩ', color=RED)
ax.annotate('', xy=(5.0, 2.3), xytext=(5.0, 2.7),
            arrowprops=dict(arrowstyle='->', color=RED, lw=2.5, mutation_scale=14))

# row1 floating node
circ2 = plt.Circle((5.0, SNEAK_Y_ROW1), 0.12, fc=RED, zorder=5)
ax.add_patch(circ2)
ax.text(5.55, SNEAK_Y_ROW1, 'V_row1\n= 0.4 V', ha='left', va='center',
        fontsize=9.5, color=RED, fontweight='bold')

# wire from row1 node left to R[1][0]
ax.plot([3.5, 5.0], [SNEAK_Y_ROW1, SNEAK_Y_ROW1], color='#444', lw=1.5)
draw_resistor(ax, 3.5, SNEAK_Y_ROW1, 1.5, SNEAK_Y_ROW1, 'R[1][0]  2 kΩ', color=RED)
ax.annotate('', xy=(2.1, SNEAK_Y_ROW1), xytext=(2.7, SNEAK_Y_ROW1),
            arrowprops=dict(arrowstyle='->', color=RED, lw=2.5, mutation_scale=14))
ax.text(2.4, SNEAK_Y_ROW1+0.2, '0.2 mA', color=RED, fontsize=10, fontweight='bold', ha='center')

# wire down from R[1][0] to col0 bottom rail
ax.plot([1.5, 1.5], [SNEAK_Y_ROW1, 0.5], color='#444', lw=1.5)

# sneak label
ax.text(3.0, 0.1, '← sneak path', ha='center', fontsize=9.5,
        color=RED, style='italic', fontweight='bold')

# Ground
gnd(ax, 2.0, 0.5)
ax.text(2.0, -0.1, '0 V  (col0 / sense)', ha='center', fontsize=9, color='#555')

# Labels
ax.text(1.0, 4.7, 'row0 = 1 V', fontsize=9.5, color='#3498db', fontweight='bold')

# current labels with arrows for clarity
ax.text(5.15, 3.9, '0.2 mA', color=RED, fontsize=10, fontweight='bold')

# Result box
res = FancyBboxPatch((6.8, 3.6), 2.6, 1.6,
                     boxstyle='round,pad=0.1', fc=PURP, ec='white', lw=2.5)
ax.add_patch(res)
ax.text(8.1, 4.6, 'I_col0', ha='center', va='center',
        fontsize=12, fontweight='bold', color='white')
ax.text(8.1, 4.15, '= 1 + 0.2', ha='center', va='center',
        fontsize=11, color='#ddd')
ax.text(8.1, 3.75, '= 1.2 mA', ha='center', va='center',
        fontsize=13, fontweight='bold', color='white')

ax.set_title('Task 2 — Equivalent Circuit (Sneak Path)', fontsize=13,
             fontweight='bold', color='#2c3e50')
plt.tight_layout()
plt.savefig('/home/bao/ECE410-HW4AI/codefest/cf06/cman_equiv_sneak.png',
            dpi=150, bbox_inches='tight')
plt.close()
print('saved cman_equiv_sneak.png')
