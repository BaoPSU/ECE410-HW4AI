#!/usr/bin/env python3
"""
Build design_justification.pdf from design_justification.md via headless chromium.

Path: md -> python-markdown -> styled HTML -> chromium --print-to-pdf -> PDF.
"""

import re
import subprocess
import sys
from pathlib import Path

import markdown

HERE = Path(__file__).parent
MD_PATH   = HERE / 'design_justification.md'
HTML_PATH = HERE / '_design_justification.html'
PDF_PATH  = HERE / 'design_justification.pdf'

# Render markdown to HTML
md_text = MD_PATH.read_text(encoding='utf-8')

# Crude image-path normalisation so chromium can find figures/*.png
# (the markdown uses relative paths like figures/foo.png from the md's directory)
md_text = re.sub(r'\]\(figures/', f']({HERE}/figures/', md_text)

html_body = markdown.markdown(
    md_text,
    extensions=['extra', 'tables', 'fenced_code', 'toc'],
)

css = """
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
    max-width: 8in;
    margin: 0.5in auto;
    line-height: 1.45;
    font-size: 10.5pt;
    color: #1a1a1a;
}
h1 { font-size: 18pt; color: #1a3d6b; border-bottom: 2px solid #1a3d6b; padding-bottom: 4pt; margin-top: 20pt; }
h2 { font-size: 14pt; color: #1a3d6b; margin-top: 18pt; border-bottom: 1px solid #ccc; padding-bottom: 2pt; }
h3 { font-size: 11.5pt; color: #2a4d7b; margin-top: 12pt; }
p  { margin: 6pt 0; }
table { border-collapse: collapse; margin: 8pt 0; font-size: 9.5pt; }
th, td { border: 1px solid #aaa; padding: 4pt 8pt; }
th { background: #e8eef7; }
code { background: #f0f0f0; padding: 1pt 4pt; border-radius: 3px; font-size: 9pt; }
pre { background: #f6f8fa; padding: 8pt; border-radius: 4px; overflow-x: auto; font-size: 9pt; }
pre code { background: none; padding: 0; }
img { max-width: 7in; display: block; margin: 8pt auto; }
strong { color: #111; }
hr { border: none; border-top: 1px solid #ccc; margin: 16pt 0; }
blockquote { border-left: 3px solid #1a3d6b; padding-left: 10pt; color: #555; margin: 8pt 0; }
"""

html_full = f"""<!doctype html>
<html><head>
<meta charset="utf-8">
<title>M4 Design Justification - Bao Nguyen</title>
<style>{css}</style>
</head>
<body>
{html_body}
</body></html>"""

HTML_PATH.write_text(html_full, encoding='utf-8')

# Run chromium headless to print to PDF
cmd = [
    'chromium',
    '--headless=new',
    '--disable-gpu',
    '--no-sandbox',
    '--no-pdf-header-footer',
    '--virtual-time-budget=10000',
    f'--print-to-pdf={PDF_PATH}',
    HTML_PATH.as_uri(),
]
print('Running:', ' '.join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
if res.returncode != 0:
    print('STDERR:', res.stderr, file=sys.stderr)
    sys.exit(res.returncode)
print(f'Saved: {PDF_PATH}')
print(f'Size : {PDF_PATH.stat().st_size:,} bytes')
