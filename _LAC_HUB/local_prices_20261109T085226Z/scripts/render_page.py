"""Render one PDF page to PNG. Usage: py -I render_page.py <pdf> <page_index_0based> <out_png> [resolution]"""
import sys, pdfplumber
pdf, i, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
res = int(sys.argv[4]) if len(sys.argv) > 4 else 110
with pdfplumber.open(pdf) as p:
    p.pages[i].to_image(resolution=res).save(out)
print("ok")
