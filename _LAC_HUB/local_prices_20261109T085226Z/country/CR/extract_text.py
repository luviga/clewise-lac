"""Extract text from PDFs page by page with PyMuPDF (reading order, one text span per line).
Usage: py -I extract_text.py <out_dir> <pdf> [<pdf> ...]
Writes <out_dir>/<pdf stem>.txt with '=====PAGE n=====' markers."""
import sys, os
import fitz
out_dir = sys.argv[1]
for p in sys.argv[2:]:
    d = fitz.open(p)
    stem = os.path.splitext(os.path.basename(p))[0]
    with open(os.path.join(out_dir, stem + '.txt'), 'w', encoding='utf-8') as f:
        for i, pg in enumerate(d):
            f.write(f'\n=====PAGE {i+1}=====\n' + pg.get_text())
    print(stem, len(d))
