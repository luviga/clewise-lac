"""Render PDF pages to PNG. Usage: py -I pdf_render.py <pdf> <outprefix> <resolution> <page1> [<page2> ...] (1-based pages)"""
import sys
import pdfplumber

pdf, outp, res = sys.argv[1], sys.argv[2], int(sys.argv[3])
pages = [int(x) for x in sys.argv[4:]]
with pdfplumber.open(pdf) as d:
    for n in pages:
        im = d.pages[n - 1].to_image(resolution=res)
        fn = f"{outp}_p{n}.png"
        im.save(fn)
        print(fn)
