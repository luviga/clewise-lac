"""Blind reader 2 render script.

Single page:  render_2.py <pdf_file> <page> <out.png> [resolution]
Crop:         render_2.py <pdf_file> <page> <out.png> <resolution> <x0> <top> <x1> <bottom>
              (crop box given as fractions 0-1 of page width/height)
Batch:        render_2.py --batch <pdf_file> <out_dir> <prefix> <resolution> <page> [<page> ...]
              writes <out_dir>/<prefix>_p<N>.png
"""
import os
import sys

import pdfplumber


def render(pdf, page, out, res=150, crop=None):
    with pdfplumber.open(pdf) as doc:
        p = doc.pages[int(page) - 1]
        if crop:
            w, h = float(p.width), float(p.height)
            x0, t, x1, b = crop
            p = p.crop((x0 * w, t * h, x1 * w, b * h))
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        p.to_image(resolution=int(res)).save(out)
    print(out)


def main(argv):
    if argv and argv[0] == "--batch":
        pdf, out_dir, prefix, res = argv[1], argv[2], argv[3], int(argv[4])
        os.makedirs(out_dir, exist_ok=True)
        with pdfplumber.open(pdf) as doc:
            print("pages in pdf:", len(doc.pages))
            for pg in argv[5:]:
                n = int(pg)
                out = os.path.join(out_dir, f"{prefix}_p{n}.png")
                doc.pages[n - 1].to_image(resolution=res).save(out)
                print(out)
        return
    pdf, page, out = argv[0], argv[1], argv[2]
    res = int(argv[3]) if len(argv) > 3 else 150
    crop = tuple(float(x) for x in argv[4:8]) if len(argv) >= 8 else None
    render(pdf, page, out, res, crop)


if __name__ == "__main__":
    main(sys.argv[1:])
