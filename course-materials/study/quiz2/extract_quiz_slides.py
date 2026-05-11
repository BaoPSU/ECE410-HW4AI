#!/usr/bin/env python3
"""
Extract QUIZ-stickered slides from week 6 & 7 source PDFs into one combined PDF.
Page numbers are 1-indexed and reflect the slides I visually confirmed have a
red "QUIZ" sticker.

Output:
  quiz_marked_slides/quiz_marked_combined.pdf
"""

from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path

ROOT = Path("/home/bao/ECE410-HW4AI/course-materials")
OUT_DIR = Path("/home/bao/ECE410-HW4AI/course-materials/study/quiz2/quiz_marked_slides")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Page numbers (1-indexed) with the red QUIZ sticker ---
# Verified by visually scanning each slide deck during note-taking.

W6_QUIZ_PAGES = {
    3:  "How can we accelerate an algorithm? (the 10 levers)",
    5:  "Traditional technology — speedup/difficulty/applicability table",
    6:  "Emerging technology — master table",
    8:  "No Free Lunch theorem (Wolpert & Macready, 1997)",
    10: "Systolic array — PE structure + neural computing unit",
    11: "How to map a deep neural net on a systolic array",
}

W7_QUIZ_PAGES = {
    4:  "How can we accelerate an algorithm? (recap)",
    5:  "Emerging technology — master table",
    8:  "Computing in processor vs computing in memory (memory types)",
    11: "MVM via crossbar — Ohm + Kirchhoff equation",
    14: "How can we map an NN onto a crossbar? (parallel mult + current sum)",
    15: "How can we map an NN onto a crossbar? (conductance + capacitance)",
    16: "Sneak paths (1) — 2×2 setup",
    17: "Sneak paths (2) — 4×4 array, draw the current flow",
    18: "Sneak paths (3) — read vs sneak current paths",
    19: "Sneak paths (4) — solutions: diodes or 1T1R",
    22: "Questions: primary advantage of IMC, where are synaptic weights, SNN benefits",
    24: "The crossbar primitive — analog MVM in O(1) time",
    26: "Efficient sparse mapping on a crossbar (permute & pack, gating, format-aware)",
    39: "Neural network acceleration ecosystem (GPU, TPU/NPU, FPGA, ASIC)",
    40: "Key building block: the crossbar (for neuromorphic chips)",
    48: "It's all about AER (Address Event Representation)",
    49: "Network-on-Chip (NoC) — 2D mesh",
    50: "Example: AER over NoC — concrete spike packet",
    51: "How does the source know the destination? (routing table at source core)",
}

W6_PDF = ROOT / "week06" / "w6_mon_transformers_in_memory.pdf"
W7_PDF = ROOT / "week07" / "slides" / "w7_mon_neuromorphic_chips.pdf"

def extract(src: Path, pages_dict: dict, writer: PdfWriter, label: str):
    reader = PdfReader(str(src))
    for p, desc in pages_dict.items():
        writer.add_page(reader.pages[p - 1])  # 1-indexed → 0-indexed
        print(f"  + [{label}] p.{p}: {desc}")

writer = PdfWriter()

print("Extracting from week 6:")
extract(W6_PDF, W6_QUIZ_PAGES, writer, "W6")

print("\nExtracting from week 7:")
extract(W7_PDF, W7_QUIZ_PAGES, writer, "W7")

out = OUT_DIR / "quiz_marked_combined.pdf"
with open(out, "wb") as f:
    writer.write(f)

total = len(W6_QUIZ_PAGES) + len(W7_QUIZ_PAGES)
print(f"\nSaved {total} slides to {out}")
print(f"  W6: {len(W6_QUIZ_PAGES)} slides")
print(f"  W7: {len(W7_QUIZ_PAGES)} slides")
