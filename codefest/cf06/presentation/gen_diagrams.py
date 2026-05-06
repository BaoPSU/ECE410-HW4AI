"""Generate CF06 presentation diagrams."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import matplotlib.patheffects as pe

OUT = "."

# ─────────────────────────────────────────────────────────────
# Diagram 1 — 4×4 crossbar weight matrix
# ─────────────────────────────────────────────────────────────
def diagram_crossbar():
    weights = np.array([
        [+1, -1, +1, -1],
        [+1, +1, -1, -1],
        [-1, +1, +1, -1],
        [-1, -1, -1, +1],
    ])
    inputs  = [10, 20, 30, 40]
    outputs = [-40, 0, -20, -20]

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.set_xlim(-1.2, 5.5)
    ax.set_ylim(-1.5, 5.2)
    ax.axis('off')
    ax.set_facecolor('#F8F9FA')
    fig.patch.set_facecolor('#F8F9FA')

    COL_X = [1, 2, 3, 4]
    ROW_Y = [4, 3, 2, 1]

    # column lines
    for x in COL_X:
        ax.plot([x, x], [0.4, 4.6], color='#555', lw=1.5, zorder=1)
    # row lines
    for y in ROW_Y:
        ax.plot([0.4, 4.6], [y, y], color='#555', lw=1.5, zorder=1)

    # weight nodes
    for i in range(4):
        for j in range(4):
            w = weights[i][j]
            color  = '#2ecc71' if w == 1 else '#e74c3c'
            label  = '+1' if w == 1 else '−1'
            circle = plt.Circle((COL_X[j], ROW_Y[i]), 0.32,
                                 color=color, ec='white', lw=2, zorder=3)
            ax.add_patch(circle)
            ax.text(COL_X[j], ROW_Y[i], label, ha='center', va='center',
                    fontsize=11, fontweight='bold', color='white', zorder=4)

    # input labels (left)
    for i, (y, v) in enumerate(zip(ROW_Y, inputs)):
        ax.text(-0.05, y, f'in{i} = {v}', ha='right', va='center',
                fontsize=12, fontweight='bold', color='#2c3e50')
        ax.annotate('', xy=(0.4, y), xytext=(-0.05, y),
                    arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.5))

    # output labels (bottom)
    for j, (x, v) in enumerate(zip(COL_X, outputs)):
        ax.annotate('', xy=(x, 0.1), xytext=(x, 0.42),
                    arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.5))
        box = FancyBboxPatch((x-0.42, -0.55), 0.84, 0.55,
                             boxstyle='round,pad=0.05', fc='#3498db', ec='white', lw=2)
        ax.add_patch(box)
        ax.text(x, -0.27, f'out{j}', ha='center', va='center',
                fontsize=11, fontweight='bold', color='white')
        ax.text(x, -1.05, f'= {v}', ha='center', va='center',
                fontsize=12, fontweight='bold',
                color='#27ae60' if v == 0 else '#c0392b')

    # column header
    for j, x in enumerate(COL_X):
        ax.text(x, 4.85, f'col {j}', ha='center', va='bottom',
                fontsize=11, color='#7f8c8d')

    # formula
    ax.text(2.5, 5.15,
            r'out$[j]$ = $\Sigma_i\;$weight$[i][j]\;\times\;$in$[i]$',
            ha='center', va='center', fontsize=13, color='#2c3e50',
            style='italic')

    # legend
    p1 = mpatches.Patch(color='#2ecc71', label='weight = +1')
    m1 = mpatches.Patch(color='#e74c3c', label='weight = −1')
    ax.legend(handles=[p1, m1], loc='lower right', fontsize=11,
              framealpha=0.9, edgecolor='#bdc3c7')

    ax.set_title('4×4 Binary-Weight Crossbar MAC', fontsize=15,
                 fontweight='bold', color='#2c3e50', pad=4)

    plt.tight_layout()
    plt.savefig(f'{OUT}/slide_crossbar.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('saved slide_crossbar.png')


# ─────────────────────────────────────────────────────────────
# Diagram 2 — Module block diagram
# ─────────────────────────────────────────────────────────────
def diagram_module():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8F9FA')

    def box(x, y, w, h, label, color='#3498db', fontsize=12):
        r = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.1',
                           fc=color, ec='white', lw=2.5, zorder=3)
        ax.add_patch(r)
        ax.text(x+w/2, y+h/2, label, ha='center', va='center',
                fontsize=fontsize, color='white', fontweight='bold', zorder=4,
                multialignment='center')

    def arr(x0, y0, x1, y1, label='', color='#555', lw=1.8):
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='->', color=color, lw=lw))
        if label:
            mx, my = (x0+x1)/2, (y0+y1)/2
            ax.text(mx, my+0.12, label, ha='center', fontsize=9.5,
                    color='#2c3e50', fontweight='bold')

    # ── blocks ──
    box(3.5, 3.5, 3, 0.9, 'weight register\n(16-bit wreg)', '#8e44ad')
    box(3.5, 2.1, 3, 0.9, 'crossbar MAC\n(combinational)', '#e67e22')
    box(3.5, 0.7, 3, 0.9, 'output register', '#27ae60')

    # ── input ports (left) ──
    inputs_left = [
        (0.1, 4.1, 'weight_in [15:0]'),
        (0.1, 3.7, 'weight_load'),
        (0.1, 2.5, 'in0–in3\n(8-bit signed)'),
        (0.1, 0.2, 'clk / rst_n'),
    ]
    for (x, y, lbl) in inputs_left:
        ax.text(x, y, lbl, ha='left', va='center', fontsize=10,
                color='#2c3e50', fontweight='bold')

    # arrows in
    arr(1.6, 4.1, 3.5, 3.95, '')
    arr(1.6, 3.7, 3.5, 3.72, '')
    arr(1.6, 2.55, 3.5, 2.55, '')
    ax.annotate('', xy=(5, 0.7), xytext=(5, 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.8))
    ax.text(5, 0.1, 'clk / rst_n', ha='center', fontsize=9, color='#2c3e50')

    # arrows between blocks
    arr(5, 3.5, 5, 3.0, 'wreg')
    arr(5, 2.1, 5, 1.6, 'sum0–sum3')

    # output ports (right)
    arr(6.5, 1.15, 8.5, 1.15, '')
    ax.text(8.6, 1.15, 'out0–out3\n(10-bit signed)', ha='left', va='center',
            fontsize=10, color='#2c3e50', fontweight='bold')

    ax.set_title('crossbar_mac.sv — Internal Architecture', fontsize=14,
                 fontweight='bold', color='#2c3e50', y=0.98)

    plt.tight_layout()
    plt.savefig(f'{OUT}/slide_module.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('saved slide_module.png')


# ─────────────────────────────────────────────────────────────
# Diagram 3 — Weight encoding (16-bit flat register)
# ─────────────────────────────────────────────────────────────
def diagram_encoding():
    weights = np.array([
        [+1, -1, +1, -1],
        [+1, +1, -1, -1],
        [-1, +1, +1, -1],
        [-1, -1, -1, +1],
    ])

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.set_xlim(-0.5, 16.5); ax.set_ylim(-1.8, 3.2)
    ax.axis('off')
    fig.patch.set_facecolor('#F8F9FA')

    bits = []
    for i in range(4):
        for j in range(4):
            bits.append(1 if weights[i][j] == 1 else 0)

    for bit_idx in range(16):
        x = 15 - bit_idx  # MSB left
        i = bit_idx // 4
        j = bit_idx % 4
        val = bits[bit_idx]
        color = '#2ecc71' if val == 1 else '#e74c3c'
        w_val = '+1' if val == 1 else '−1'

        rect = FancyBboxPatch((x+0.05, 0.8), 0.9, 0.9,
                              boxstyle='round,pad=0.05', fc=color, ec='white', lw=2)
        ax.add_patch(rect)
        ax.text(x+0.5, 1.25, str(val), ha='center', va='center',
                fontsize=13, fontweight='bold', color='white')

        # bit index label
        ax.text(x+0.5, 0.55, f'{bit_idx}', ha='center', va='top',
                fontsize=8.5, color='#7f8c8d')
        # w[i][j] label
        ax.text(x+0.5, 2.0, f'w[{i}][{j}]', ha='center', va='bottom',
                fontsize=8, color='#2c3e50')
        ax.text(x+0.5, 1.85, f'={w_val}', ha='center', va='bottom',
                fontsize=7.5, color='#7f8c8d')

    # row group brackets
    row_colors = ['#8e44ad','#3498db','#e67e22','#27ae60']
    row_labels = ['row 3', 'row 2', 'row 1', 'row 0']
    for r in range(4):
        x_start = (3-r)*4
        x_end   = x_start + 4
        ax.plot([15-x_end+1+0.05, 15-x_start+0.95], [-0.2, -0.2],
                color=row_colors[r], lw=3)
        ax.text((15-x_end+1 + 15-x_start+1)/2, -0.55,
                row_labels[r], ha='center', fontsize=10,
                color=row_colors[r], fontweight='bold')

    ax.text(8, 3.0,
            'weight_in[4×i + j]  →  weight[i][j]    (1 = +1,   0 = −1)',
            ha='center', fontsize=12, color='#2c3e50', fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{OUT}/slide_encoding.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('saved slide_encoding.png')


# ─────────────────────────────────────────────────────────────
# Diagram 4 — Timing diagram
# ─────────────────────────────────────────────────────────────
def diagram_timing():
    fig, axes = plt.subplots(5, 1, figsize=(11, 5.5),
                             gridspec_kw={'hspace': 0.1})
    fig.patch.set_facecolor('#F8F9FA')

    signals = [
        ('clk',         '#555'),
        ('rst_n',       '#8e44ad'),
        ('weight_load', '#e67e22'),
        ('in0–in3',     '#3498db'),
        ('out0–out3',   '#27ae60'),
    ]

    T = 16  # total time units
    clk_edges = list(range(0, T+1))

    clk_wave       = []
    rst_wave        = []
    wload_wave      = []
    in_wave         = []
    out_wave        = []

    for t in range(T):
        clk_wave.append(1 if t % 2 == 0 else 0)
        rst_wave.append(0 if t < 2 else 1)
        wload_wave.append(1 if 4 <= t < 6 else 0)
        in_wave.append(1 if t >= 4 else 0)
        out_wave.append(1 if t >= 8 else 0)   # 2 cycles latency after load

    def plot_digital(ax, wave, color, label, hi=0.8, lo=0.1):
        xs, ys = [0], [wave[0]*hi + (1-wave[0])*lo]
        for i in range(1, len(wave)):
            xs.extend([i, i])
            ys.extend([ys[-1], wave[i]*hi + (1-wave[i])*lo])
        xs.append(len(wave)); ys.append(ys[-1])
        ax.plot(xs, ys, color=color, lw=2)
        ax.fill_between(xs, lo, ys, alpha=0.15, color=color, step=None)
        ax.set_xlim(0, T); ax.set_ylim(-0.1, 1.1)
        ax.set_yticks([]); ax.set_xticks([])
        ax.set_ylabel(label, rotation=0, ha='right', va='center',
                      fontsize=10, fontweight='bold', color=color,
                      labelpad=65)
        ax.set_facecolor('#F8F9FA')
        for spine in ax.spines.values(): spine.set_visible(False)

    plot_digital(axes[0], clk_wave,   '#555',    'clk')
    plot_digital(axes[1], rst_wave,   '#8e44ad', 'rst_n')
    plot_digital(axes[2], wload_wave, '#e67e22', 'weight_load')
    plot_digital(axes[3], in_wave,    '#3498db', 'in0–in3\n(stable)')
    plot_digital(axes[4], out_wave,   '#27ae60', 'out0–out3\n(valid)')

    # annotation arrows
    for ax in axes:
        ax.axvline(4, color='#e74c3c', lw=1.2, ls='--', alpha=0.6)
        ax.axvline(6, color='#e74c3c', lw=1.2, ls='--', alpha=0.6)
        ax.axvline(8, color='#27ae60', lw=1.2, ls='--', alpha=0.6)

    axes[0].text(4.05, 0.95, 'weights\nloaded', fontsize=8.5, color='#e74c3c', va='top')
    axes[0].text(6.05, 0.95, 'wload\nclears', fontsize=8.5, color='#e74c3c', va='top')
    axes[0].text(8.05, 0.95, 'output\nvalid', fontsize=8.5, color='#27ae60', va='top')

    axes[4].set_xticks(range(0, T+1, 2))
    axes[4].set_xticklabels([f'{t*5}ns' for t in range(0, T//2+1)],
                             fontsize=9, color='#7f8c8d')
    axes[4].tick_params(bottom=True)

    fig.suptitle('Timing: weight load → 2-cycle output latency', fontsize=13,
                 fontweight='bold', color='#2c3e50', y=1.01)

    plt.savefig(f'{OUT}/slide_timing.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('saved slide_timing.png')


# ─────────────────────────────────────────────────────────────
# Diagram 5 — Simulation results
# ─────────────────────────────────────────────────────────────
def diagram_results():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axis('off')
    fig.patch.set_facecolor('#1e2229')

    terminal_text = (
        "=== CF06 CLLM — 4x4 Crossbar MAC Simulation ===\n"
        "Weight matrix (row=input, col=output):\n"
        "  row0=[+1,-1,+1,-1]  row1=[+1,+1,-1,-1]\n"
        "  row2=[-1,+1,+1,-1]  row3=[-1,-1,-1,+1]\n"
        "Inputs: [in0,in1,in2,in3] = [10, 20, 30, 40]\n"
        "Expected: [out0,out1,out2,out3] = [-40, 0, -20, -20]\n"
        "---\n"
        "out0 =  -40   PASS\n"
        "out1 =    0   PASS\n"
        "out2 =  -20   PASS\n"
        "out3 =  -20   PASS\n"
        "---\n"
        "Result: 4/4 PASS\n"
        "ALL TESTS PASSED"
    )

    lines = terminal_text.split('\n')
    for i, line in enumerate(lines):
        y = 0.95 - i * 0.065
        if 'PASS' in line and '===' not in line and 'Expected' not in line and 'Result' not in line:
            color = '#2ecc71'
        elif 'ALL TESTS PASSED' in line or '4/4 PASS' in line:
            color = '#2ecc71'
        elif '===' in line:
            color = '#3498db'
        elif '---' in line:
            color = '#7f8c8d'
        else:
            color = '#ecf0f1'
        ax.text(0.04, y, line, transform=ax.transAxes,
                fontsize=12.5, color=color, fontfamily='monospace',
                va='top')

    plt.tight_layout(pad=0.3)
    plt.savefig(f'{OUT}/slide_results.png', dpi=150, bbox_inches='tight',
                facecolor='#1e2229')
    plt.close()
    print('saved slide_results.png')


if __name__ == '__main__':
    diagram_crossbar()
    diagram_module()
    diagram_encoding()
    diagram_timing()
    diagram_results()
    print('All diagrams generated.')
