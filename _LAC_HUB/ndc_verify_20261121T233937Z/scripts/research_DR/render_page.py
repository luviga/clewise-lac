"""Render one PDF page to PNG for a visual check. Usage: python -I render_page.py <pdf> <page from 1> <out png> [resolution]"""
import sys

import pdfplumber

pdf, page, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
res = int(sys.argv[4]) if len(sys.argv) > 4 else 100
with pdfplumber.open(pdf) as p:
    p.pages[page - 1].to_image(resolution=res).save(out)
print("saved", out)
