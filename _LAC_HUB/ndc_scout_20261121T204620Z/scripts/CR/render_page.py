"""Render PDF pages to PNG. Usage: python -I render_page.py <pdf> <outdir> <prefix> <page> [<page> ...] (1-based pages)."""
import os
import sys

import pdfplumber

pdf_path, outdir, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
pages = [int(p) for p in sys.argv[4:]]
os.makedirs(outdir, exist_ok=True)
with pdfplumber.open(pdf_path) as pdf:
    for p in pages:
        im = pdf.pages[p - 1].to_image(resolution=150)
        out = os.path.join(outdir, f"{prefix}_p{p}.png")
        im.save(out)
        print(out)
