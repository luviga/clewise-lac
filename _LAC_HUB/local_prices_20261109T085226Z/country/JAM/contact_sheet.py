"""Make a labelled contact sheet of PNGs. Usage: py -I contact_sheet.py <out.png> <ncols> <png> [<png> ...]"""
import sys, os
from PIL import Image, ImageDraw
out, ncols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
ims = [Image.open(f).convert('RGB') for f in files]
w = max(i.size[0] for i in ims); h = max(i.size[1] for i in ims) + 14
nrows = (len(ims) + ncols - 1) // ncols
sheet = Image.new('RGB', (w * ncols, h * nrows), 'white')
d = ImageDraw.Draw(sheet)
for k, (f, im) in enumerate(zip(files, ims)):
    x, y = (k % ncols) * w, (k // ncols) * h
    d.text((x + 2, y), os.path.basename(f)[-8:], fill='red')
    sheet.paste(im, (x, y + 14))
sheet.save(out); print(out, sheet.size)
