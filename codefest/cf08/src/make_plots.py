#!/usr/bin/env python3
"""
Generate the three Python-rendered visuals for the CF08 CMAN write-up.

Outputs (saved next to this script):
  1. headroom_bars.png  — interface capacity bars vs the 1.024 Mbit/s mean need
  2. burst_timing.png   — 1 ms burst + I²C drain + FIFO fill curve
  3. crossover_plot.png — B_AER vs B_frame vs firing rate f, with crossover marked

Run with:  python3 make_plots.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).parent

# ---------------------------------------------------------------- problem givens
N = 1024
f_mean = 50          # Hz per neuron
BITS = 20            # bits per AER packet
B_MEAN = N * f_mean * BITS / 1e6   # 1.024 Mbit/s

# ============================================================================
# 1) Headroom bars
# ============================================================================
interfaces = ['I²C', 'SPI', 'AXI4-Lite']
caps = [3.4, 50.0, 100.0]  # Mbit/s
headroom = [c / B_MEAN for c in caps]

fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.barh(interfaces, caps, color=['#4C9F70', '#3274A1', '#7E57C2'])

# Mark the 1.024 Mbit/s mean need
ax.axvline(B_MEAN, color='red', linestyle='--', linewidth=2,
           label=f'Mean need = {B_MEAN:.3f} Mbit/s')

# Annotate each bar with cap value + headroom multiplier
for bar, cap, hr in zip(bars, caps, headroom):
    ax.text(cap + 1.5, bar.get_y() + bar.get_height() / 2,
            f'{cap:g} Mbit/s  ({hr:.1f}× headroom ✓)',
            va='center', fontsize=10)

ax.set_xlabel('Bandwidth (Mbit/s)')
ax.set_title('Interface capacity vs CF08 AER mean need (1.024 Mbit/s)\nAll three sustain; I²C is the lowest-complexity option')
ax.set_xlim(0, 115)
ax.legend(loc='lower right')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / 'headroom_bars.png', dpi=150)
plt.close()

# ============================================================================
# 2) Burst timing + FIFO fill
# ============================================================================
# Time axis: 0 to 2 ms in 1 µs steps
t_ms = np.linspace(0, 2.0, 2001)

# Spike-arrival bandwidth: 5.12 Mbit/s during [0,1] ms, then back to 1.024 mean
B_in = np.where(t_ms <= 1.0, 5.12, B_MEAN)   # Mbit/s

# I²C drain rate: constant 3.4 Mbit/s
B_drain = np.full_like(t_ms, 3.4)

# FIFO fill = integral of (arrive - drain), clipped at 0
dt_s = (t_ms[1] - t_ms[0]) * 1e-3        # 1 µs in seconds
net_bits_per_s = (B_in - B_drain) * 1e6  # bit/s
fifo_bits = np.maximum.accumulate(
    np.clip(np.cumsum(net_bits_per_s * dt_s), 0, None)
)
# Reset clamping above only forward; do proper fill-and-drain:
fifo_bits = np.zeros_like(t_ms)
for i in range(1, len(t_ms)):
    delta = (B_in[i] - B_drain[i]) * 1e6 * dt_s
    fifo_bits[i] = max(0.0, fifo_bits[i - 1] + delta)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True,
                                gridspec_kw={'height_ratios': [1, 1.2]})

# Top: arrival vs drain bandwidths
ax1.fill_between(t_ms, 0, B_in, alpha=0.4, color='#E74C3C',
                 label='Spike arrival rate (Mbit/s)')
ax1.plot(t_ms, B_in, color='#E74C3C', linewidth=2)
ax1.plot(t_ms, B_drain, color='#3274A1', linewidth=2, linestyle='--',
         label='I²C drain rate (3.4 Mbit/s cap)')
ax1.axhline(B_MEAN, color='gray', linestyle=':', linewidth=1,
            label=f'Mean = {B_MEAN:.3f} Mbit/s')
ax1.axvspan(0, 1, color='yellow', alpha=0.1, label='1 ms burst window')
ax1.set_ylabel('Bandwidth (Mbit/s)')
ax1.set_title('CF08 burst analysis: 256 spikes in 1 ms → 5.12 Mbit/s peak vs 3.4 Mbit/s I²C cap')
ax1.set_ylim(0, 6)
ax1.legend(loc='upper right', fontsize=9)
ax1.grid(alpha=0.3)

# Bottom: FIFO fill curve
ax2.plot(t_ms, fifo_bits, color='#7E57C2', linewidth=2.5)
ax2.fill_between(t_ms, 0, fifo_bits, alpha=0.25, color='#7E57C2')
peak_idx = int(np.argmax(fifo_bits))
ax2.annotate(f'Peak fill = {fifo_bits[peak_idx]:.0f} bits = {fifo_bits[peak_idx] / 20:.0f} packets',
             xy=(t_ms[peak_idx], fifo_bits[peak_idx]),
             xytext=(1.2, 1500), fontsize=10,
             arrowprops=dict(arrowstyle='->', color='black'))
ax2.axhline(1720, color='red', linestyle=':', linewidth=1.5,
            label='Theoretical peak = 1,720 bits (86 packets)')
ax2.axhline(2560, color='green', linestyle='--', linewidth=1.5,
            label='Design FIFO = 128 packets (2,560 bits, 50% safety)')
ax2.set_xlabel('Time (ms)')
ax2.set_ylabel('FIFO fill (bits)')
ax2.set_xlim(0, 2.0)
ax2.set_ylim(0, 3000)
ax2.legend(loc='upper right', fontsize=9)
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT / 'burst_timing.png', dpi=150)
plt.close()

# ============================================================================
# 3) Crossover plot: B_AER(f) vs B_frame at varying f
# ============================================================================
fs = np.linspace(0, 150, 301)
B_aer = N * fs * BITS / 1e6   # Mbit/s, slope = N * 20 / 1e6 = 0.02048 per Hz
B_frame = N * 1000 * 1 / 1e6  # 1.024 Mbit/s, flat
f_cross = 1000 / BITS          # = 50 Hz

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(fs, B_aer, color='#E74C3C', linewidth=2.5,
        label=r'$B_{AER} = N \cdot f \cdot 20$ bits/s')
ax.axhline(B_frame, color='#3274A1', linewidth=2.5,
           label=r'$B_{frame} = N \cdot (1/T_{frame}) \cdot 1$ bit = 1.024 Mbit/s')

# Shade winner regions
ax.fill_between(fs, 0, np.minimum(B_aer, B_frame),
                where=(fs <= f_cross), alpha=0.15, color='#4C9F70',
                label='AER wins (sparse)')
ax.fill_between(fs, 0, np.minimum(B_aer, B_frame),
                where=(fs > f_cross), alpha=0.15, color='#D35400',
                label='Frame wins (dense)')

# Mark crossover
ax.scatter([f_cross], [B_frame], color='black', s=100, zorder=5)
ax.annotate(f'Crossover at f = {f_cross:.0f} Hz\nB = {B_frame:.3f} Mbit/s',
            xy=(f_cross, B_frame),
            xytext=(70, 1.3), fontsize=10,
            arrowprops=dict(arrowstyle='->', color='black'))

# Mark biological-rate regime
ax.axvspan(1, 10, alpha=0.2, color='blue', label='Biological rate (1–10 Hz)')

ax.set_xlabel('Mean firing rate f (Hz)')
ax.set_ylabel('Bandwidth (Mbit/s)')
ax.set_title('AER vs frame-based bandwidth\nAER wins below 50 Hz, frame wins above')
ax.set_xlim(0, 150)
ax.set_ylim(0, 3)
ax.legend(loc='upper left', fontsize=9)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / 'crossover_plot.png', dpi=150)
plt.close()

print('Wrote:')
print(' ', OUT / 'headroom_bars.png')
print(' ', OUT / 'burst_timing.png')
print(' ', OUT / 'crossover_plot.png')
