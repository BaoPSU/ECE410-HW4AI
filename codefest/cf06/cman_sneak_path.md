# CMAN CF06 — Sneak Paths in a Resistive Crossbar

**ECE 410/510 Spring 2026 — Bao Nguyen**

## Circuit parameters

| Cell | Resistance | State |
|------|-----------|-------|
| R[0][0] | 1 kΩ | on  |
| R[0][1] | 2 kΩ | off |
| R[1][0] | 2 kΩ | off |
| R[1][1] | 1 kΩ | on  |

---

## (a) Ideal read — compute I_col0

**Conditions:** V_row0 = 1 V, V_row1 = 0 V (grounded), V_col0 = 0 V (virtual ground), V_col1 = 0 V (grounded).

Both row 1 and col 1 are held at 0 V, so no sneak path can form.

$$I_{col0} = \frac{V_{row0} - V_{col0}}{R[0][0]} + \frac{V_{row1} - V_{col0}}{R[1][0]}$$

$$I_{col0} = \frac{1\,\text{V} - 0\,\text{V}}{1\,\text{k}\Omega} + \frac{0\,\text{V} - 0\,\text{V}}{2\,\text{k}\Omega} = 1\,\text{mA} + 0\,\text{mA}$$

$$\boxed{I_{col0}^{\text{ideal}} = 1.000\,\text{mA}}$$

This correctly encodes the dot product: only the on-cell R[0][0] contributes.

---

## (b) Sneak-path read — KCL for V_row1 and V_col1

**Conditions:** V_row0 = 1 V, V_col0 = 0 V (virtual ground). **Row 1 and col 1 are floating** (undriven).

Because row 1 and col 1 are floating, no external current enters or leaves those nodes. Applying KCL (net current = 0 at each floating node):

### KCL at V_row1

$$\frac{V_{row1} - V_{col0}}{R[1][0]} + \frac{V_{row1} - V_{col1}}{R[1][1]} = 0$$

$$\frac{V_{row1}}{2000} + \frac{V_{row1} - V_{col1}}{1000} = 0$$

Multiplying through by 2000:

$$V_{row1} + 2(V_{row1} - V_{col1}) = 0 \implies 3V_{row1} - 2V_{col1} = 0$$

$$\therefore \quad V_{col1} = \frac{3}{2}\,V_{row1} \tag{1}$$

### KCL at V_col1

$$\frac{V_{row0} - V_{col1}}{R[0][1]} + \frac{V_{row1} - V_{col1}}{R[1][1]} = 0$$

$$\frac{1 - V_{col1}}{2000} + \frac{V_{row1} - V_{col1}}{1000} = 0$$

Multiplying through by 2000:

$$(1 - V_{col1}) + 2(V_{row1} - V_{col1}) = 0 \implies 1 + 2V_{row1} - 3V_{col1} = 0 \tag{2}$$

### Solving equations (1) and (2)

Substituting (1) into (2):

$$1 + 2V_{row1} - 3 \cdot \frac{3}{2}V_{row1} = 0 \implies 1 - \frac{5}{2}V_{row1} = 0$$

$$\boxed{V_{row1} = 0.4\,\text{V}}$$

$$\boxed{V_{col1} = \frac{3}{2}(0.4) = 0.6\,\text{V}}$$

### Verification

| Branch | Calculation | Current |
|--------|------------|---------|
| R[0][1]: row0→col1 | (1 − 0.6) / 2000 | 0.20 mA |
| R[1][1]: col1→row1 | (0.6 − 0.4) / 1000 | 0.20 mA |
| R[1][0]: row1→col0 | (0.4 − 0) / 2000 | 0.20 mA |

KCL at V_col1: 0.20 mA in (from row0) − 0.20 mA out (to row1) = 0 ✓  
KCL at V_row1: 0.20 mA in (from col1) − 0.20 mA out (to col0) = 0 ✓

---

## (c) Actual I_col0 with sneak path itemized

$$I_{col0}^{\text{actual}} = \frac{V_{row0} - V_{col0}}{R[0][0]} + \frac{V_{row1} - V_{col0}}{R[1][0]}$$

| Contribution | Path | Value |
|-------------|------|-------|
| Intended signal | row0 → R[0][0] → col0 | **1.000 mA** |
| Sneak path | row0 → R[0][1] → col1 → R[1][1] → row1 → R[1][0] → col0 | **0.200 mA** |

$$\boxed{I_{col0}^{\text{actual}} = 1.200\,\text{mA}}$$

The sneak path adds **+0.2 mA** (20% error) to the intended 1 mA signal.

---

## (d) Why sneak paths corrupt MVM results

When unselected row and column lines are left floating rather than grounded, a low-resistance path forms through multiple "off" cells (here: R[0][1]→R[1][1]→R[1][0]), routing extra current into the sensed column. This phantom current adds to the true dot-product signal, making the output read higher than the correct weight–input product. In large crossbar arrays the effect multiplies: every combination of floating rows and columns creates additional sneak paths, causing the total error to grow roughly as O(N²) with array size N, quickly making MVM results unreliable without mitigation such as grounding unselected lines or using selector devices (diodes/transistors) at each cell.
