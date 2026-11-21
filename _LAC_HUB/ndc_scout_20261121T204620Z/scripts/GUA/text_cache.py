"""Write the text of each page of a PDF to <out_dir>/p<N>.txt (N 1-based, not padded).

Usage: python -I text_cache.py <pdf_path> <out_dir>
Prints the page count and the pages with little text (possible scans).
"""
import os
import sys

import pdfplumber


def main():
    pdf_path, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    low = []
    with pdfplumber.open(pdf_path) as pdf:
        n = len(pdf.pages)
        for i, page in enumerate(pdf.pages, start=1):
            try:
                txt = page.extract_text() or ""
            except Exception as exc:  # keep going on a bad page
                txt = ""
                print(f"page {i}: extract error {exc}")
            with open(os.path.join(out_dir, f"p{i}.txt"), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(txt)
            if len(txt.strip()) < 80:
                low.append(i)
    print(f"pages={n}")
    print(f"low_text_pages={low}")


if __name__ == "__main__":
    main()
