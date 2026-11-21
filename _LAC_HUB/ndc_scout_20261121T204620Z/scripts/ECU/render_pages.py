"""Render PDF pages to PNG with pdfplumber.

Usage: python -I render_pages.py <pdf> <outdir> <prefix> <page> [<page> ...] [--res N]
Pages are 1-based physical page numbers. Output: <outdir>/<prefix>_p<N>.png
"""
import os
import sys

import pdfplumber

args = sys.argv[1:]
res = 150
if "--res" in args:
    i = args.index("--res")
    res = int(args[i + 1])
    del args[i:i + 2]
pdf_path, outdir, prefix = args[0], args[1], args[2]
pages = [int(x) for x in args[3:]]
os.makedirs(outdir, exist_ok=True)
with pdfplumber.open(pdf_path) as pdf:
    for n in pages:
        img = pdf.pages[n - 1].to_image(resolution=res)
        out = os.path.join(outdir, f"{prefix}_p{n}.png")
        img.save(out)
        print(out)
