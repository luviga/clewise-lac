"""Render one PDF page (0-based) to PNG, optionally cropped to a fraction box of the page.
Usage: py -I dr_render_page.py <pdf> <page> <out_png> [x0 y0 x1 y1 as fractions] [resolution]"""
import sys, pdfplumber
pdf = pdfplumber.open(sys.argv[1])
page = pdf.pages[int(sys.argv[2])]
if len(sys.argv) >= 8:
    f = [float(x) for x in sys.argv[4:8]]
    W, H = page.width, page.height
    page = page.crop((f[0] * W, f[1] * H, f[2] * W, f[3] * H))
res = int(sys.argv[8]) if len(sys.argv) >= 9 else 150
page.to_image(resolution=res).save(sys.argv[3])
print('saved', sys.argv[3])
