"""Write the text of each PDF page to <outdir>/p<N>.txt (N 1-based, not padded) with pdfplumber.

Usage: python -I text_cache.py <pdf> <outdir>
Prints page count, SHA-256 and the pages with little text (candidates for image reading).
"""
import hashlib
import os
import sys

import pdfplumber

pdf_path, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
h = hashlib.sha256()
with open(pdf_path, "rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
        h.update(chunk)
low = []
with pdfplumber.open(pdf_path) as pdf:
    n = len(pdf.pages)
    for i, page in enumerate(pdf.pages, start=1):
        try:
            txt = page.extract_text() or ""
        except Exception as e:  # keep going on a bad page
            txt = ""
            print(f"page {i}: error {e}")
        with open(os.path.join(outdir, f"p{i}.txt"), "w", encoding="utf-8", newline="\n") as g:
            g.write(txt)
        if len(txt.strip()) < 200:
            low.append(i)
print(f"pages={n} sha256={h.hexdigest()}")
print("low-text pages:", low)
