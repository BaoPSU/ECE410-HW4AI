"""Build CF06 Shine presentation as a .pptx (importable into Google Slides)."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ── helpers ─────────────────────────────────────────────────
W, H = Inches(13.33), Inches(7.5)   # 16:9 widescreen

DARK    = RGBColor(0x1e, 0x22, 0x29)
TEAL    = RGBColor(0x00, 0x8B, 0x8B)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
LGRAY   = RGBColor(0xF2, 0xF4, 0xF6)
DKGRAY  = RGBColor(0x2C, 0x3E, 0x50)
GREEN   = RGBColor(0x27, 0xAE, 0x60)
ORANGE  = RGBColor(0xE6, 0x7E, 0x22)
PURPLE  = RGBColor(0x8E, 0x44, 0xAD)
BLUE    = RGBColor(0x34, 0x98, 0xDB)
RED     = RGBColor(0xE7, 0x4C, 0x3C)

def new_prs():
    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H
    return prs

def blank(prs):
    blank_layout = prs.slide_layouts[6]   # completely blank
    return prs.slides.add_slide(blank_layout)

def bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def textbox(slide, text, l, t, w, h,
            size=24, bold=False, color=WHITE,
            align=PP_ALIGN.LEFT, wrap=True):
    txb = slide.shapes.add_textbox(l, t, w, h)
    txb.word_wrap = wrap
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.color.rgb = color
    return txb

def rect(slide, l, t, w, h, fill_color, line_color=None, line_w=0):
    shape = slide.shapes.add_shape(
        1,   # MSO_SHAPE_TYPE.RECTANGLE
        l, t, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(line_w)
    else:
        shape.line.fill.background()
    return shape

def picture(slide, path, l, t, w, h):
    if os.path.exists(path):
        slide.shapes.add_picture(path, l, t, w, h)

def accent_bar(slide):
    rect(slide, 0, 0, W, Inches(0.09), TEAL)

def slide_number(slide, n, total=7):
    textbox(slide, f'{n} / {total}',
            W - Inches(1.1), H - Inches(0.45), Inches(1.0), Inches(0.38),
            size=13, color=RGBColor(0x99,0x99,0x99), align=PP_ALIGN.RIGHT)

# ── Slide 1 — Title ─────────────────────────────────────────
def slide_title(prs):
    sl = blank(prs)
    bg(sl, DARK)
    accent_bar(sl)

    # big gradient-ish rect behind title
    rect(sl, 0, Inches(1.6), W, Inches(3.0), RGBColor(0x25,0x2C,0x36))

    textbox(sl,
            'CF06 CLLM',
            Inches(1), Inches(1.7), Inches(11.3), Inches(0.85),
            size=46, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

    textbox(sl,
            '4×4 Binary-Weight Crossbar MAC Unit in SystemVerilog',
            Inches(1), Inches(2.55), Inches(11.3), Inches(0.75),
            size=28, bold=False, color=WHITE, align=PP_ALIGN.CENTER)

    textbox(sl,
            'ECE 410/510 Spring 2026  ·  Bao Nguyen  ·  LLM: Claude Sonnet 4.6',
            Inches(1), Inches(3.45), Inches(11.3), Inches(0.5),
            size=17, color=RGBColor(0xAA,0xAA,0xAA), align=PP_ALIGN.CENTER)

    # crossbar image bottom-right
    picture(sl, f'{HERE}/slide_crossbar.png',
            Inches(3.8), Inches(4.1), Inches(5.8), Inches(3.1))

    slide_number(sl, 1)

# ── Slide 2 — Crossbar concept ──────────────────────────────
def slide_concept(prs):
    sl = blank(prs)
    bg(sl, LGRAY)
    accent_bar(sl)
    slide_number(sl, 2)

    textbox(sl, 'What is a Crossbar MAC?',
            Inches(0.5), Inches(0.15), Inches(9), Inches(0.65),
            size=30, bold=True, color=DKGRAY)

    # main diagram
    picture(sl, f'{HERE}/slide_crossbar.png',
            Inches(0.3), Inches(0.9), Inches(7.2), Inches(6.2))

    # notes panel on right
    rect(sl, Inches(7.7), Inches(0.9), Inches(5.4), Inches(6.2),
         RGBColor(0xFF,0xFF,0xFF), TEAL, 1.5)

    notes = [
        ('Rows carry inputs, columns carry outputs', DKGRAY, 18, False),
        ('', DKGRAY, 10, False),
        ('Each intersection = a weight (+1 or −1)', DKGRAY, 18, False),
        ('', DKGRAY, 10, False),
        ('Formula:', DKGRAY, 18, True),
        ('out[j] = Σᵢ weight[i][j] × in[i]', TEAL, 20, True),
        ('', DKGRAY, 10, False),
        ('Inputs:  [10, 20, 30, 40]', DKGRAY, 17, False),
        ('', DKGRAY, 8, False),
        ('out0: +10+20−30−40 = −40', RGBColor(0xC0,0x39,0x2B), 16, False),
        ('out1: −10+20+30−40 =   0', RGBColor(0xC0,0x39,0x2B), 16, False),
        ('out2: +10−20+30−40 = −20', RGBColor(0xC0,0x39,0x2B), 16, False),
        ('out3: −10−20−30+40 = −20', RGBColor(0xC0,0x39,0x2B), 16, False),
    ]
    y = Inches(1.1)
    for (txt, col, sz, bd) in notes:
        textbox(sl, txt, Inches(7.85), y, Inches(5.1), Inches(0.42),
                size=sz, bold=bd, color=col)
        y += Inches(sz / 72 * 1.5)

# ── Slide 3 — Module architecture ───────────────────────────
def slide_module(prs):
    sl = blank(prs)
    bg(sl, LGRAY)
    accent_bar(sl)
    slide_number(sl, 3)

    textbox(sl, 'Module Architecture — crossbar_mac.sv',
            Inches(0.5), Inches(0.15), Inches(12), Inches(0.65),
            size=30, bold=True, color=DKGRAY)

    picture(sl, f'{HERE}/slide_module.png',
            Inches(0.3), Inches(0.9), Inches(8.8), Inches(5.8))

    # side notes
    rect(sl, Inches(9.3), Inches(0.9), Inches(3.8), Inches(5.8),
         WHITE, TEAL, 1.5)

    bullets = [
        ('Ports', TEAL, 19, True),
        ('in0–in3   8-bit signed', DKGRAY, 16, False),
        ('out0–out3  10-bit signed', DKGRAY, 16, False),
        ('weight_in  16-bit flat', DKGRAY, 16, False),
        ('weight_load  1-cycle pulse', DKGRAY, 16, False),
        ('', DKGRAY, 10, False),
        ('Pipeline', TEAL, 19, True),
        ('① Weight register (FF)', PURPLE, 16, False),
        ('② Comb. MAC (wires)', ORANGE, 16, False),
        ('③ Output register (FF)', GREEN, 16, False),
        ('', DKGRAY, 10, False),
        ('Bit width: 4 × 127 = 508', DKGRAY, 15, False),
        ('→ 10-bit signed is safe', DKGRAY, 15, False),
    ]
    y = Inches(1.1)
    for (txt, col, sz, bd) in bullets:
        textbox(sl, txt, Inches(9.45), y, Inches(3.5), Inches(0.38),
                size=sz, bold=bd, color=col)
        y += Inches(sz / 72 * 1.65)

# ── Slide 4 — Weight encoding ────────────────────────────────
def slide_encoding(prs):
    sl = blank(prs)
    bg(sl, LGRAY)
    accent_bar(sl)
    slide_number(sl, 4)

    textbox(sl, 'Weight Encoding — 16-bit Flat Register',
            Inches(0.5), Inches(0.15), Inches(12), Inches(0.65),
            size=30, bold=True, color=DKGRAY)

    picture(sl, f'{HERE}/slide_encoding.png',
            Inches(0.5), Inches(0.95), Inches(12.3), Inches(3.1))

    # formula box
    rect(sl, Inches(0.5), Inches(4.15), Inches(12.3), Inches(0.75),
         WHITE, TEAL, 1.5)
    textbox(sl, 'bit (4×i + j)  encodes  weight[i][j]        1 → +1      0 → −1',
            Inches(0.7), Inches(4.2), Inches(11.9), Inches(0.65),
            size=21, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

    # weight matrix table
    rect(sl, Inches(0.5), Inches(5.05), Inches(12.3), Inches(2.15),
         WHITE, RGBColor(0xCC,0xCC,0xCC), 1)

    textbox(sl, 'Testbench weight matrix:',
            Inches(0.7), Inches(5.1), Inches(4), Inches(0.4),
            size=17, bold=True, color=DKGRAY)

    rows = [
        'row 0  [+1, −1, +1, −1]   →   weight_in bits [3:0]  = 4\'b0101',
        'row 1  [+1, +1, −1, −1]   →   weight_in bits [7:4]  = 4\'b0011',
        'row 2  [−1, +1, +1, −1]   →   weight_in bits [11:8] = 4\'b0110',
        'row 3  [−1, −1, −1, +1]   →   weight_in bits [15:12]= 4\'b1000',
    ]
    row_colors = [PURPLE, BLUE, ORANGE, GREEN]
    for k, (row, col) in enumerate(zip(rows, row_colors)):
        textbox(sl, row, Inches(0.7), Inches(5.55 + k*0.38), Inches(11.9), Inches(0.36),
                size=16, color=col, bold=False)

# ── Slide 5 — Testbench timing ───────────────────────────────
def slide_timing(prs):
    sl = blank(prs)
    bg(sl, LGRAY)
    accent_bar(sl)
    slide_number(sl, 5)

    textbox(sl, 'Testbench Strategy — 2-Cycle Pipeline',
            Inches(0.5), Inches(0.15), Inches(12), Inches(0.65),
            size=30, bold=True, color=DKGRAY)

    picture(sl, f'{HERE}/slide_timing.png',
            Inches(0.4), Inches(0.9), Inches(9.0), Inches(4.5))

    # numbered steps
    rect(sl, Inches(9.55), Inches(0.9), Inches(3.55), Inches(6.0),
         WHITE, TEAL, 1.5)

    steps = [
        ('① Assert reset', PURPLE),
        ('   Clear all registers', DKGRAY),
        ('', DKGRAY),
        ('② weight_load pulse', ORANGE),
        ('   16-bit weight_in latched', DKGRAY),
        ('   into wreg on posedge', DKGRAY),
        ('', DKGRAY),
        ('③ Weight stable', BLUE),
        ('   MAC computes sum0–sum3', DKGRAY),
        ('', DKGRAY),
        ('④ Output registered', GREEN),
        ('   out0–out3 valid', DKGRAY),
        ('   2 cycles after load', DKGRAY),
    ]
    y = Inches(1.05)
    for (txt, col) in steps:
        textbox(sl, txt, Inches(9.7), y, Inches(3.2), Inches(0.36),
                size=15, color=col, bold='①②③④' in txt or txt.startswith('①②③④'))
        y += Inches(0.33)

    # code snippet at bottom
    rect(sl, Inches(0.4), Inches(5.55), Inches(9.0), Inches(1.65),
         DARK)
    code = ('weight_in   = {4\'b1000, 4\'b0110, 4\'b0011, 4\'b0101};\n'
            'weight_load = 1;   in0=10; in1=20; in2=30; in3=40;\n'
            '@(posedge clk); #1;  weight_load = 0;\n'
            '@(posedge clk); #1;  // read out0–out3 here')
    textbox(sl, code, Inches(0.6), Inches(5.6), Inches(8.6), Inches(1.55),
            size=14, color=RGBColor(0x2E,0xCC,0x71), bold=False)

# ── Slide 6 — Simulation results ────────────────────────────
def slide_results(prs):
    sl = blank(prs)
    bg(sl, LGRAY)
    accent_bar(sl)
    slide_number(sl, 6)

    textbox(sl, 'Simulation Results — iverilog -g2012',
            Inches(0.5), Inches(0.15), Inches(12), Inches(0.65),
            size=30, bold=True, color=DKGRAY)

    picture(sl, f'{HERE}/slide_results.png',
            Inches(0.4), Inches(0.9), Inches(7.8), Inches(5.8))

    # result cards on right
    cards = [
        ('out0', '−40', '+10+20−30−40'),
        ('out1', '  0', '−10+20+30−40'),
        ('out2', '−20', '+10−20+30−40'),
        ('out3', '−20', '−10−20−30+40'),
    ]
    for k, (port, val, calc) in enumerate(cards):
        y = Inches(1.05 + k * 1.5)
        rect(sl, Inches(8.4), y, Inches(4.65), Inches(1.3),
             WHITE, GREEN, 2)
        textbox(sl, f'{port} = {val}', Inches(8.55), y+Inches(0.08),
                Inches(4.35), Inches(0.55), size=26, bold=True, color=DKGRAY)
        textbox(sl, calc, Inches(8.55), y+Inches(0.62),
                Inches(4.35), Inches(0.5), size=15, color=RGBColor(0x7F,0x8C,0x8D))
        textbox(sl, '✓ PASS', Inches(10.6), y+Inches(0.08),
                Inches(2.3), Inches(0.55), size=22, bold=True, color=GREEN,
                align=PP_ALIGN.RIGHT)

# ── Slide 7 — Summary ───────────────────────────────────────
def slide_summary(prs):
    sl = blank(prs)
    bg(sl, DARK)
    accent_bar(sl)
    slide_number(sl, 7)

    textbox(sl, 'Summary', Inches(1), Inches(0.4), Inches(11.3), Inches(0.65),
            size=36, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

    items = [
        (TEAL,   '✓', 'LLM-generated crossbar_mac.sv using Claude Sonnet 4.6'),
        (ORANGE, '✓', '16-bit flat weight register — bit (4i+j) encodes weight[i][j]'),
        (BLUE,   '✓', 'Fully combinational MAC, registered outputs, 10-bit signed'),
        (PURPLE, '✓', 'Testbench loads [[1,−1,1,−1],[1,1,−1,−1],[−1,1,1,−1],[−1,−1,−1,1]]'),
        (GREEN,  '✓', 'Inputs [10,20,30,40] → Simulation: 4/4 PASS  [−40, 0, −20, −20]'),
    ]
    for k, (col, tick, text) in enumerate(items):
        y = Inches(1.45 + k * 0.98)
        rect(sl, Inches(0.8), y, Inches(11.7), Inches(0.8),
             RGBColor(0x25, 0x2C, 0x36))
        textbox(sl, tick, Inches(0.95), y+Inches(0.08), Inches(0.5), Inches(0.65),
                size=26, bold=True, color=col)
        textbox(sl, text, Inches(1.55), y+Inches(0.12), Inches(10.8), Inches(0.58),
                size=20, color=WHITE)

    textbox(sl, 'Thank you!', Inches(1), Inches(6.7), Inches(11.3), Inches(0.55),
            size=24, bold=True, color=RGBColor(0xAA,0xAA,0xAA),
            align=PP_ALIGN.CENTER)


# ── Build ────────────────────────────────────────────────────
def build():
    prs = new_prs()
    slide_title(prs)
    slide_concept(prs)
    slide_module(prs)
    slide_encoding(prs)
    slide_timing(prs)
    slide_results(prs)
    slide_summary(prs)
    out = f'{HERE}/cf06_presentation.pptx'
    prs.save(out)
    print(f'Saved: {out}')

if __name__ == '__main__':
    build()
