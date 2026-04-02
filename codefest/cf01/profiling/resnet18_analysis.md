# ResNet-18 Analysis
Bao Nguyen  
ECE 410/510 Spring 2026  

## Top 5 MAC-Intensive Layers

| Layer Name | MACs | Parameters |
|-----------|------|------------|
| Conv2d: 3-1 | 115,605,504 | 36,864 |
| Conv2d: 3-4 | 115,605,504 | 36,864 |
| Conv2d: 3-16 | 115,605,504 | 147,456 |
| Conv2d: 3-20 | 115,605,504 | 147,456 |
| Conv2d: 3-29 | 115,605,504 | 589,824 |

## Arithmetic Intensity

Selected layer: Conv2d: 3-29

MACs = 115,605,504  

Weight memory:
589,824 × 4 = 2,359,296 bytes  

Activation memory:
(256 × 14 × 14 × 2) × 4 = 401,408 bytes  

Total memory:
2,359,296 + 401,408 = 2,760,704 bytes  

Arithmetic Intensity:
(2 × 115,605,504) / 2,760,704 ≈ 83.76
