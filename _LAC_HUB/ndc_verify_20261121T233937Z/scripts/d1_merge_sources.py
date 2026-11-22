"""Write the job's sources.csv: the 46 scout documents (files under the scout job folder) plus the
documents the research tasks registered (parts/sources_D_<code>.csv), with class and SHA-256 checked.
Also writes sources_pending.csv from parts/pending_D_<code>.csv. Writes the text cache of any new PDF
that lacks one.
"""
import os
import subprocess
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, SCOUT, CODES, read_csv, write_csv, sha256

FIELDS = ["id", "country", "kind", "class", "URL", "title", "publisher", "author", "date", "accessed", "SHA-256", "file", "pages", "language"]
rows = []
for r in read_csv(os.path.join(SCOUT, "sources.csv")):
    rows.append(dict(r, **{"class": "official", "author": r.get("publisher", ""),
                           "file": "../ndc_scout_20261121T204620Z/" + r["file"]}))
problems = []
for code in CODES:
    p = os.path.join(JOB, "parts", f"sources_D_{code}.csv")
    if not os.path.exists(p):
        problems.append(f"{code}: no sources_D file")
        continue
    for r in read_csv(p):
        f = os.path.join(JOB, r["file"])
        if not os.path.exists(f):
            problems.append(f"{r['id']}: file missing {r['file']}")
        elif sha256(f) != r["SHA-256"].strip().lower():
            problems.append(f"{r['id']}: SHA-256 mismatch")
        if r.get("class") not in ("official", "external", "lead"):
            problems.append(f"{r['id']}: class {r.get('class')}")
        tdir = os.path.join(JOB, "downloads", code, "text_all", r["id"])
        if f.lower().endswith(".pdf") and os.path.exists(f) and not os.path.isdir(tdir):
            os.makedirs(tdir, exist_ok=True)
            txt = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", f, "-"], capture_output=True).stdout.decode("utf-8", "replace")
            for i, t in enumerate([x for x in txt.split("\f")], 1):
                with open(os.path.join(tdir, f"p{i}.txt"), "w", encoding="utf-8", newline="\n") as fo:
                    fo.write(t)
        rows.append(r)
ids = [r["id"] for r in rows]
dups = {i for i in ids if ids.count(i) > 1}
if dups:
    problems.append(f"duplicate ids {sorted(dups)}")
write_csv(os.path.join(JOB, "sources.csv"), rows, FIELDS)
pend = []
for code in CODES:
    p = os.path.join(JOB, "parts", f"pending_D_{code}.csv")
    if os.path.exists(p):
        pend += read_csv(p)
write_csv(os.path.join(JOB, "sources_pending.csv"), pend)
import collections
print("sources", len(rows), collections.Counter(r["class"] for r in rows))
print("pending rows", len(pend), collections.Counter(r.get("result", "") for r in pend))
for p in problems:
    print("PROBLEM", p)
