"""Render selected PDF pages to PNG. Usage: py -I render_pages.py <pdf> <outdir> <scale> <page_idx0> [<page_idx0> ...]
Page indexes are zero based."""
import sys, os
import pypdfium2 as pdfium

pdf, outdir, scale = sys.argv[1], sys.argv[2], float(sys.argv[3])
os.makedirs(outdir, exist_ok=True)
doc = pdfium.PdfDocument(pdf)
stem = os.path.splitext(os.path.basename(pdf))[0]
for a in sys.argv[4:]:
    if '-' in a:
        lo, hi = map(int, a.split('-'))
        idxs = range(lo, hi + 1)
    else:
        idxs = [int(a)]
    for i in idxs:
        img = doc[i].render(scale=scale).to_pil()
        out = os.path.join(outdir, f"{stem}_p{i+1:03d}.png")
        img.save(out)
        print(out, img.size)
