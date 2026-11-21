"""Render selected PDF pages to PNG.

Usage: python -I render_pages.py <pdf_path> <out_dir> <prefix> <resolution> <page> [<page> ...]
Pages are physical, 1-based. Output: <out_dir>/<prefix>_p<N>.png
"""
import os
import sys

import pdfplumber


def main():
    pdf_path, out_dir, prefix, res = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    pages = [int(x) for x in sys.argv[5:]]
    os.makedirs(out_dir, exist_ok=True)
    with pdfplumber.open(pdf_path) as pdf:
        for n in pages:
            img = pdf.pages[n - 1].to_image(resolution=res)
            path = os.path.join(out_dir, f"{prefix}_p{n}.png")
            img.save(path)
            print(path)


if __name__ == "__main__":
    main()
