"""Write the text of every page of every registered PDF to downloads/<code>/text_all/<id>/p<N>.txt
with poppler pdftotext -layout (fast; keeps table rows on one line).

Usage: python -I a1b_extract_pdftotext.py <sources.csv> <base folder of the files> [ids...]
Pages already written by an earlier pypdf pass are overwritten so that one extractor is used.
"""
import os
import subprocess
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, read_csv

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
    if os.path.exists(os.path.join(out, "_pdftotext_done")):
        continue
    res = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", f, "-"], capture_output=True)
    txt = res.stdout.decode("utf-8", errors="replace")
    pages = txt.split("\f")
    if pages and pages[-1].strip() == "":
        pages = pages[:-1]
    for i, t in enumerate(pages, 1):
        with open(os.path.join(out, f"p{i}.txt"), "w", encoding="utf-8", newline="\n") as fo:
            fo.write(t)
    open(os.path.join(out, "_pdftotext_done"), "w").close()
    print("done", r["id"], len(pages), r.get("pages", ""), flush=True)
