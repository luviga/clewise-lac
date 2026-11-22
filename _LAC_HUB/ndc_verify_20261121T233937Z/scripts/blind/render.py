"""Render one PDF page (physical, 1-based) to PNG, or a crop of it.

Usage:
  render.py <pdf_file> <page> <out.png> [resolution] [x0 top x1 bottom as fractions 0-1]
  render.py --batch <blind_csv> <code>   (renders every listed page at 150 dpi)
"""
import csv
import os
import sys

import pdfplumber

JOB = "C:/clw_scout/_LAC_HUB/ndc_verify_20261121T233937Z"


def render(pdf_path, page, out, res=150, frac=None):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with pdfplumber.open(pdf_path) as pdf:
        p = pdf.pages[page - 1]
        if frac:
            w, h = float(p.width), float(p.height)
            bbox = (frac[0] * w, frac[1] * h, frac[2] * w, frac[3] * h)
            p = p.crop(bbox)
        p.to_image(resolution=res).save(out)
    print(out)


def batch(blind_csv, code):
    done = set()
    with open(blind_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for pg in row["pages"].split(";"):
                pg = pg.strip()
                if not pg:
                    continue
                n = int(pg.replace("p.", ""))
                key = (row["pdf_file"], n)
                if key in done:
                    continue
                done.add(key)
                out = f"{JOB}/downloads/{code}/img_blind/{row['source_id']}_p{n}.png"
                if os.path.exists(out):
                    continue
                try:
                    render(row["pdf_file"], n, out)
                except Exception as e:  # noqa: BLE001
                    print("ERROR", key, e)


if __name__ == "__main__":
    if sys.argv[1] == "--batch":
        batch(sys.argv[2], sys.argv[3])
    else:
        res = int(sys.argv[4]) if len(sys.argv) > 4 else 150
        frac = [float(x) for x in sys.argv[5:9]] if len(sys.argv) > 8 else None
        render(sys.argv[1], int(sys.argv[2]), sys.argv[3], res, frac)
