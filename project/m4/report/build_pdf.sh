#!/usr/bin/env bash
# Build design_justification.pdf from design_justification.md via LaTeX.
#
# Pipeline: markdown -> pandoc -> LaTeX (.tex) -> pdflatex -> PDF.
# The .tex file is regenerated each run and is also committed so the LaTeX
# preamble (with DeclareUnicodeCharacter declarations) is reviewable on its
# own. Intermediate .aux/.log/.toc/.out files are cleaned at the end.
#
# Requires: pandoc, pdflatex (texlive-latex-base + texlive-latex-recommended).

set -e

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

MD="design_justification.md"
TEX="design_justification.tex"
PDF="design_justification.pdf"

echo "[1/4] pandoc: $MD -> $TEX"
pandoc "$MD" -o "$TEX" \
    --standalone \
    --toc \
    -V documentclass=article \
    -V geometry:margin=0.75in \
    -V fontsize=10pt \
    -V linkcolor=blue \
    -V title="K-Means Image Color Quantization Accelerator: Design Justification" \
    -V author="Bao Nguyen" \
    -V date="Spring 2026 -- ECE 410/510 Milestone 4"

# Inject Unicode handling so pdflatex (T1 encoding) renders the math/symbol
# characters used in the source (no xelatex/lualatex required).
python3 - <<'PYEOF'
from pathlib import Path
TEX = Path('design_justification.tex')
src = TEX.read_text(encoding='utf-8')
marker = r'  \usepackage{textcomp} % provide euro and other symbols'
declarations = r'''
  % Unicode chars that the markdown source uses outside math mode
  \DeclareUnicodeCharacter{2082}{\ensuremath{_2}}
  \DeclareUnicodeCharacter{2078}{\ensuremath{^8}}
  \DeclareUnicodeCharacter{2208}{\ensuremath{\in}}
  \DeclareUnicodeCharacter{2212}{\ensuremath{-}}
  \DeclareUnicodeCharacter{2248}{\ensuremath{\approx}}
  \DeclareUnicodeCharacter{2308}{\ensuremath{\lceil}}
  \DeclareUnicodeCharacter{2309}{\ensuremath{\rceil}}
  \DeclareUnicodeCharacter{0394}{\ensuremath{\Delta}}
  \DeclareUnicodeCharacter{00B2}{\ensuremath{^2}}
  \DeclareUnicodeCharacter{00B3}{\ensuremath{^3}}
  \DeclareUnicodeCharacter{00B9}{\ensuremath{^1}}
  \DeclareUnicodeCharacter{00B5}{\ensuremath{\mu}}'''
if marker not in src:
    raise SystemExit('Unicode marker line not found in generated .tex')
if r'\DeclareUnicodeCharacter{2082}' not in src:
    src = src.replace(marker, marker + declarations)
    TEX.write_text(src, encoding='utf-8')
    print('  injected Unicode declarations into preamble')
else:
    print('  Unicode declarations already present')
PYEOF

echo "[2/4] pdflatex pass 1"
pdflatex -interaction=nonstopmode "$TEX" > /tmp/build_pdf_pass1.log 2>&1
echo "[3/4] pdflatex pass 2 (for TOC + cross-refs)"
pdflatex -interaction=nonstopmode "$TEX" > /tmp/build_pdf_pass2.log 2>&1

unicode_errors=$(grep -c "Unicode character" /tmp/build_pdf_pass2.log || true)
if [ "$unicode_errors" -gt 0 ]; then
    echo "WARNING: $unicode_errors unicode chars not declared. See /tmp/build_pdf_pass2.log"
fi

echo "[4/4] cleaning intermediates"
rm -f design_justification.aux design_justification.log \
      design_justification.toc design_justification.out

if [ ! -f "$PDF" ]; then
    echo "ERROR: $PDF was not produced"
    exit 1
fi

size=$(stat -c "%s" "$PDF")
pages=$(pdfinfo "$PDF" 2>/dev/null | awk '/Pages/ {print $2}')
printf "\nDONE: %s (%d bytes, %s pages)\n" "$PDF" "$size" "$pages"
