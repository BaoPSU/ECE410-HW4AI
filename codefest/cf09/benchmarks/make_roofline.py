#!/usr/bin/env python3
"""Generate CF9 CLLM roofline plot.

Plots both platform rooflines (M1 CPU host + sky130 ASIC accelerator) on the
same axes, marks the M1 baseline point (measured today) and the M4 accelerator
point (PROJECTED from synthesis frequency * pipeline parallelism * arithmetic
intensity).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).parent / 'roofline_plot.png'

fig, ax = plt.subplots(figsize=(10, 6.5))

ai_range = np.logspace(-1, 2.3, 500)  # 0.1 to ~200 FLOP/byte


def roofline(ai, peak_flops, peak_bw):
    return np.minimum(peak_flops, peak_bw * ai)


# Platform 1: i9-12900H host (M1 baseline platform)
CPU_PEAK = 1400.0      # GFLOP/s theoretical peak
CPU_BW = 76.8          # GB/s DDR5 dual-channel
cpu_roof = roofline(ai_range, CPU_PEAK, CPU_BW)
ax.plot(ai_range, cpu_roof, 'C0-', lw=2.5, label=f'i9-12900H roofline (peak {CPU_PEAK:.0f} GFLOP/s, BW {CPU_BW:.1f} GB/s)')

# Platform 2: sky130 accelerator (M4 target)
# Peak compute: K parallel kdist computes/cycle × ops/kdist × clock
#   = 16 × (3 sub + 3 mul + 3 add) × 100 MHz = 14.4 GOPS theoretical peak
ACC_PEAK = 14.4        # GOPS
# On-chip BW (for kdist inputs): 3 bytes/pixel × 100 MHz = 0.3 GB/s for single feeder
# Use AXI4-Lite peak (single-shot 4-byte writes at 100 MHz) = 0.4 GB/s as on-chip BW ceiling
ACC_BW = 0.4
acc_roof = roofline(ai_range, ACC_PEAK, ACC_BW)
ax.plot(ai_range, acc_roof, 'C3-', lw=2.5, label=f'sky130 accelerator roofline (peak {ACC_PEAK:.1f} GOPS, AXI4-Lite BW {ACC_BW:.1f} GB/s)')

# Optional reference: HBM3 streaming target (M1 system diagram)
HBM3_BW = 16000.0      # GB/s
hbm3_roof = roofline(ai_range, ACC_PEAK, HBM3_BW)
ax.plot(ai_range, hbm3_roof, 'C3--', lw=1.5, alpha=0.5, label=f'sky130 + HBM3 feeder (peak {ACC_PEAK:.1f} GOPS, BW {HBM3_BW/1000:.0f} TB/s)')

# Points
# M1 baseline (MEASURED today, fresh rerun)
M1_AI = 1.68
M1_THROUGHPUT = 0.38       # GFLOP/s fresh rerun
ax.scatter([M1_AI], [M1_THROUGHPUT], s=180, c='C0', zorder=5, edgecolor='black', lw=1.5)
ax.annotate(f'  M1 baseline (MEASURED 2026-05-25)\n  AI={M1_AI}, {M1_THROUGHPUT:.2f} GFLOP/s',
            xy=(M1_AI, M1_THROUGHPUT), xytext=(M1_AI*1.5, M1_THROUGHPUT*0.4),
            fontsize=9, color='C0', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='C0', lw=1))

# M4 accelerator (PROJECTED from synth)
M4_AI = 42.7
M4_THROUGHPUT = 12.8       # GOPS projected
ax.scatter([M4_AI], [M4_THROUGHPUT], s=180, c='C3', zorder=5, edgecolor='black', lw=1.5, marker='D')
ax.annotate(f'  M4 accelerator (PROJECTED)\n  AI={M4_AI}, {M4_THROUGHPUT:.1f} GOPS',
            xy=(M4_AI, M4_THROUGHPUT), xytext=(M4_AI*0.18, M4_THROUGHPUT*2.0),
            fontsize=9, color='C3', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='C3', lw=1))

# Ridge points
cpu_ridge = CPU_PEAK / CPU_BW
acc_ridge = ACC_PEAK / ACC_BW
ax.axvline(cpu_ridge, color='C0', linestyle=':', alpha=0.4, lw=1)
ax.text(cpu_ridge*1.05, 2200, f'CPU ridge\n{cpu_ridge:.1f}', fontsize=8, color='C0')
ax.axvline(acc_ridge, color='C3', linestyle=':', alpha=0.4, lw=1)
ax.text(acc_ridge*1.05, 25, f'sky130 ridge\n{acc_ridge:.1f}', fontsize=8, color='C3')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Arithmetic Intensity (FLOP/byte or INT-ops/byte)', fontsize=11)
ax.set_ylabel('Attainable performance (GFLOP/s or GINT-ops/s)', fontsize=11)
ax.set_title('CF9 CLLM Roofline: M1 baseline (measured) vs M4 accelerator (projected)\n'
             'K-Means image color quantization, K=16, D=3, INT8 pixels',
             fontsize=11)
ax.legend(loc='lower right', fontsize=9, framealpha=0.95)
ax.grid(True, which='both', alpha=0.3)
ax.set_xlim(0.1, 200)
ax.set_ylim(0.05, 5000)

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches='tight')
plt.close()
print(f'Saved: {OUT}')
print(f'M1 baseline    (measured): AI={M1_AI:5.2f}, {M1_THROUGHPUT:7.3f} GFLOP/s')
print(f'M4 accelerator (projected): AI={M4_AI:5.2f}, {M4_THROUGHPUT:7.3f} GOPS')
print(f'CPU ridge point: {cpu_ridge:.2f} FLOP/byte')
print(f'sky130 ridge point: {acc_ridge:.2f} OP/byte')
