"""Write the text of every page of every registered PDF to downloads/<code>/text_all/<id>/p<N>.txt.

Usage: python -I a1_extract_text.py <sources.csv> <base folder of the files> [ids...]
Uses pypdf (fast); the hub re-reads with pdfplumber where a value is not found.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, read_csv, CODE_OF
import pypdf

src_csv, base = sys.argv[1], sys.argv[2]
only = set(sys.argv[3:])
for r in read_csv(src_csv):
    if only and r["id"] not in only:
        continue
    f = os.path.join(base, r["file"])
    if not f.lower().endswith(".pdf") or not os.path.exists(f):
        continue
    code = r["id"].split("-")[0]
    out = os.path.join(JOB, "downloads", code, "text_all", r["id"])
    os.makedirs(out, exist_ok=True)
    try:
        rd = pypdf.PdfReader(f)
    except Exception as e:
        print("FAIL", r["id"], e, flush=True)
        continue
    n = len(rd.pages)
    for i in range(n):
        p = os.path.join(out, f"p{i + 1}.txt")
        if os.path.exists(p):
            continue
        try:
            t = rd.pages[i].extract_text() or ""
        except Exception as e:
            t = ""
        with open(p, "w", encoding="utf-8", newline="\n") as fo:
            fo.write(t)
    print("done", r["id"], n, flush=True)
