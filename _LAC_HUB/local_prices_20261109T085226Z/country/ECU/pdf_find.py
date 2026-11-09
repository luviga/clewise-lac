"""Find PDF pages containing keywords. Usage: py -I pdf_find.py <pdf> <kw1> [<kw2> ...]"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pypdf

pdf = sys.argv[1]
kws = [k.lower() for k in sys.argv[2:]]
r = pypdf.PdfReader(pdf)
for i, p in enumerate(r.pages, start=1):
    try:
        t = (p.extract_text() or "").lower()
    except Exception as e:
        t = ""
    hits = [k for k in kws if k in t]
    if hits:
        first = t.strip().splitlines()[:3]
        print(i, hits, " | ".join(first)[:160])
