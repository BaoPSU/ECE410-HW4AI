import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np

OUT = "/home/bao/ECE410-HW4AI/codefest/cf06/presentation/"

BLUE  = "#1f4e79"
GREEN = "#1a7a4a"
RED   = "#c00000"
GRAY  = "#d9d9d9"
LGRAY = "#f2f2f2"

# ── 1. CROSSBAR GRID ──────────────────────────────────────────────────────────
weights = [
    [+1, -1, +1, -1],
    [+1, +1, -1, -1],
    [-1, +1, +1, -1],
    [-1, -1, -1, +1],
]

fig, ax = plt.subplots(figsize=(6, 5))
ax.set_xlim(-0.8, 4.5)
ax.set_ylim(-0.8, 4.5)
ax.set_aspect('equal')
ax.axis('off')

for r in range(4):
    ax.plot([-0.3, 3.7], [3 - r, 3 - r], color=BLUE, lw=1.5, zorder=1)
for c in range(4):
    ax.plot([c, c], [3.3, -0.3], color=BLUE, lw=1.5, zorder=1)

for r in range(4):
    for c in range(4):
        w = weights[r][c]
        color = GREEN if w == 1 else RED
        label = "+1" if w == 1 else "−1"
        circ = plt.Circle((c, 3 - r), 0.22, color=color, zorder=3)
        ax.add_patch(circ)
        ax.text(c, 3 - r, label, ha='center', va='center',
                fontsize=7, color='white', fontweight='bold', zorder=4)

for r in range(4):
    ax.text(-0.55, 3 - r, f"x{r}", ha='right', va='center',
            fontsize=10, color=BLUE, fontweight='bold')
for c in range(4):
    ax.text(c, 3.5, f"y{c}", ha='center', va='bottom',
            fontsize=10, color=BLUE, fontweight='bold')

ax.text(1.5, -0.65, "Outputs (columns)", ha='center', fontsize=9, color='gray')
ax.text(-0.75, 1.5, "Inputs\n(rows)", ha='center', va='center',
        fontsize=9, color='gray', rotation=90)

fig.tight_layout()
fig.savefig(OUT + "crossbar.png", dpi=150, bbox_inches='tight')
plt.close()
print("crossbar.png done")

# ── 2. PIPELINE BLOCK DIAGRAM ─────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 3))
ax.set_xlim(0, 10)
ax.set_ylim(0, 3)
ax.axis('off')

boxes = [
    (1.0, 1.0, 2.2, 1.2, "Weight\nRegister", "(flip-flop)"),
    (4.0, 1.0, 2.2, 1.2, "Combinational\nMAC", "(wires, no clock)"),
    (7.0, 1.0, 2.2, 1.2, "Output\nRegister", "(flip-flop)"),
]

for (x, y, w, h, title, sub) in boxes:
    rect = mpatches.FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0.05", linewidth=1.5,
        edgecolor=BLUE, facecolor=LGRAY)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h*0.62, title, ha='center', va='center',
            fontsize=9, fontweight='bold', color=BLUE)
    ax.text(x + w/2, y + h*0.28, sub, ha='center', va='center',
            fontsize=7.5, color='gray')

# arrows between stages
for x in [3.2, 6.2]:
    ax.annotate("", xy=(x + 0.8, 1.6), xytext=(x, 1.6),
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5))

# weight_load arrow into stage 1
ax.annotate("", xy=(2.1, 2.2), xytext=(2.1, 2.8),
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.5))
ax.text(2.1, 2.85, "weight_load", ha='center', fontsize=8, color=GREEN)

# clock arrows into stage 1 and 3
for x in [1.5, 8.1]:
    ax.annotate("", xy=(x, 1.0), xytext=(x, 0.4),
                arrowprops=dict(arrowstyle="<-", color="#7f7f7f", lw=1.2))
ax.text(4.8, 0.18, "clk", ha='center', fontsize=8, color='gray')

# input/output labels
ax.text(0.15, 1.6, "in[0..3]", ha='center', va='center', fontsize=8, color=BLUE)
ax.annotate("", xy=(1.0, 1.6), xytext=(0.5, 1.6),
            arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5))
ax.text(9.85, 1.6, "out[0..3]", ha='center', va='center', fontsize=8, color=BLUE)
ax.annotate("", xy=(9.7, 1.6), xytext=(9.2, 1.6),
            arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5))

fig.tight_layout()
fig.savefig(OUT + "pipeline.png", dpi=150, bbox_inches='tight')
plt.close()
print("pipeline.png done")

# ── 3. WEIGHT ENCODING ────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 2.8))
ax.set_xlim(-0.5, 16.5)
ax.set_ylim(-0.2, 2.4)
ax.axis('off')

bit_labels = {0: "w[0][0]", 1: "w[0][1]", 2: "w[0][2]", 3: "w[0][3]",
              4: "w[1][0]", 8: "w[2][0]", 12: "w[3][0]"}
highlights = {0: GREEN, 1: GREEN, 2: GREEN, 3: GREEN,
              4: BLUE, 8: "#c55a11", 12: "#7030a0"}

for i in range(16):
    bit = 15 - i
    x = i
    fc = highlights.get(bit, LGRAY)
    rect = mpatches.FancyBboxPatch((x + 0.05, 1.1), 0.9, 0.7,
        boxstyle="square,pad=0.0", linewidth=1,
        edgecolor="#aaaaaa", facecolor=fc if fc != LGRAY else LGRAY)
    ax.add_patch(rect)
    ax.text(x + 0.5, 1.45, str(bit), ha='center', va='center',
            fontsize=7, color='white' if fc != LGRAY else '#555555',
            fontweight='bold')
    ax.text(x + 0.5, 0.9, str(15 - i), ha='center', va='top',
            fontsize=6.5, color='gray')

ax.text(8, 0.5, "bit index (4i + j  →  weight[i][j])", ha='center',
        fontsize=8.5, color='#444444')

ax.text(-0.5, 2.15, "16-bit wreg:", ha='left', fontsize=9,
        fontweight='bold', color=BLUE)

legend_items = [
    mpatches.Patch(color=GREEN,     label="row 0  (bits 3..0)"),
    mpatches.Patch(color=BLUE,      label="row 1  (bits 7..4)"),
    mpatches.Patch(color="#c55a11", label="row 2  (bits 11..8)"),
    mpatches.Patch(color="#7030a0", label="row 3  (bits 15..12)"),
]
ax.legend(handles=legend_items, loc='upper right', fontsize=7.5,
          framealpha=0.9, ncol=2)

fig.tight_layout()
fig.savefig(OUT + "encoding.png", dpi=150, bbox_inches='tight')
plt.close()
print("encoding.png done")

# ── 4. TIMING DIAGRAM ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(4, 1, figsize=(8, 4), sharex=True)
fig.subplots_adjust(hspace=0.15)

signals = ["clk", "weight_load", "wreg\n(weights)", "out[0..3]"]
colors  = [BLUE, GREEN, "#c55a11", "#7030a0"]

t = np.linspace(0, 6, 1000)

def clk(t):
    return 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * t / 1.0))

def pulse(t, start, end):
    return np.where((t >= start) & (t < end), 1.0, 0.0)

def step(t, at):
    return np.where(t >= at, 1.0, 0.0)

waves = [
    clk(t),
    pulse(t, 0.5, 1.5),
    step(t, 1.0),
    step(t, 2.0),
]

labels_at = [
    [],
    [(1.0, 1.15, "weight_load\nasserted")],
    [(1.05, 1.15, "wreg latches\non rising edge")],
    [(2.05, 1.15, "out valid\ncycle 2")],
]

for ax, sig, wave, color, lbl in zip(axes, signals, waves, colors, labels_at):
    ax.plot(t, wave, color=color, lw=2)
    ax.set_ylim(-0.3, 1.6)
    ax.set_yticks([])
    ax.set_ylabel(sig, fontsize=8, rotation=0, ha='right', va='center',
                  labelpad=55, color=color)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    for (xt, yt, txt) in lbl:
        ax.text(xt, yt, txt, fontsize=7, color=color, va='bottom')

axes[-1].set_xlabel("time (clock cycles)", fontsize=9)
axes[-1].set_xticks([0, 1, 2, 3, 4, 5, 6])
axes[-1].set_xticklabels(["0", "1", "2", "3", "4", "5", "6"], fontsize=8)

# vertical dashed lines at cycle boundaries
for ax in axes:
    for x in [1, 2]:
        ax.axvline(x, color='gray', lw=0.8, linestyle='--', alpha=0.6)

fig.savefig(OUT + "timing.png", dpi=150, bbox_inches='tight')
plt.close()
print("timing.png done")

# ── 5. RESULTS TABLE ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 2.8))
ax.axis('off')

cols = ["Output", "Hand Calc", "Simulation", "Match"]
rows = [
    ["out[0]", "−40", "−40", "✓"],
    ["out[1]", "  0", "  0", "✓"],
    ["out[2]", "−20", "−20", "✓"],
    ["out[3]", "−20", "−20", "✓"],
]

table = ax.table(cellText=rows, colLabels=cols,
                 loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.4, 2.0)

for (r, c), cell in table.get_celld().items():
    if r == 0:
        cell.set_facecolor(BLUE)
        cell.set_text_props(color='white', fontweight='bold')
    elif c == 3:
        cell.set_facecolor("#e2efda")
        cell.set_text_props(color=GREEN, fontweight='bold', fontsize=14)
    elif r % 2 == 0:
        cell.set_facecolor(LGRAY)
    cell.set_edgecolor('#cccccc')

ax.text(0.5, 0.93, "4 / 4 PASS", transform=ax.transAxes,
        ha='center', va='top', fontsize=16, fontweight='bold', color=GREEN)

fig.tight_layout()
fig.savefig(OUT + "results.png", dpi=150, bbox_inches='tight')
plt.close()
print("results.png done")
