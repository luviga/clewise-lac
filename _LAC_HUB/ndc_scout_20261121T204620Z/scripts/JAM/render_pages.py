"""Render PDF pages to PNG with pdfplumber.

Usage: python -I render_pages.py <pdf> <out_dir> <prefix> <page1,page2,...> [resolution]
Pages are physical, 1-based.
"""
import os
import sys

import pdfplumber


def main():
    pdf_path, out_dir, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
    pages = [int(x) for x in sys.argv[4].split(",")]
    res = int(sys.argv[5]) if len(sys.argv) > 5 else 150
    os.makedirs(out_dir, exist_ok=True)
    with pdfplumber.open(pdf_path) as pdf:
        for n in pages:
            img = pdf.pages[n - 1].to_image(resolution=res)
            out = os.path.join(out_dir, "%s_p%d.png" % (prefix, n))
            img.save(out)
            print(out)


if __name__ == "__main__":
    main()
