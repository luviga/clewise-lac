"""Write the text of each PDF page to downloads/JAM/text/<source_id>/p<N>.txt.

Usage: python -I text_cache.py <source_id> <pdf_path> <out_root>
"""
import os
import sys

import pdfplumber


def main():
    sid, pdf_path, out_root = sys.argv[1], sys.argv[2], sys.argv[3]
    out_dir = os.path.join(out_root, sid)
    os.makedirs(out_dir, exist_ok=True)
    empty = []
    with pdfplumber.open(pdf_path) as pdf:
        n = len(pdf.pages)
        for i, page in enumerate(pdf.pages, start=1):
            try:
                txt = page.extract_text() or ""
            except Exception as exc:  # keep going on a broken page
                txt = ""
                print("page", i, "error", exc)
            if len(txt.strip()) < 30:
                empty.append(i)
            with open(os.path.join(out_dir, "p%d.txt" % i), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(txt)
    print(sid, "pages", n, "near-empty pages", empty)


if __name__ == "__main__":
    main()
