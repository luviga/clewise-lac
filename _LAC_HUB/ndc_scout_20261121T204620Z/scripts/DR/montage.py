"""Combine PNG pages into one grid image for a quick look.

Usage: python -I montage.py <out_png> <cols> <width_per_page> <png> [<png> ...]
"""
import sys

from PIL import Image


def main():
    out, cols, w = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    ims = []
    for p in sys.argv[4:]:
        im = Image.open(p).convert("RGB")
        h = int(im.height * w / im.width)
        ims.append(im.resize((w, h)))
    rows = (len(ims) + cols - 1) // cols
    hmax = max(i.height for i in ims)
    sheet = Image.new("RGB", (cols * w, rows * hmax), "white")
    for k, im in enumerate(ims):
        sheet.paste(im, ((k % cols) * w, (k // cols) * hmax))
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
