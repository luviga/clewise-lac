"""Inventory of every file under downloads/ with its origin URL (when cited in sources.csv).
Usage: py -I inventory.py <job_folder>
Writes downloads_inventory.csv: file, bytes, source_ids, origin_url, status."""
import os
import sys
import pandas as pd

job = sys.argv[1]
src = pd.read_csv(os.path.join(job, "sources.csv"), dtype=str, keep_default_na=False)
cited = {}
for _, r in src.iterrows():
    for fn in [x.strip() for x in r["downloaded_file"].split(";") if x.strip()]:
        cited.setdefault(fn, []).append((r["id"], r["url"]))
rows = []
base = os.path.join(job, "downloads")
for root, _, files in os.walk(base):
    for f in files:
        rel = os.path.relpath(os.path.join(root, f), base).replace(os.sep, "/")
        c = cited.get(rel, [])
        rows.append({"file": rel, "bytes": os.path.getsize(os.path.join(root, f)),
                     "source_ids": ";".join(sorted(set(i for i, _ in c))),
                     "origin_url": c[0][1] if c else "",
                     "status": "cited in sources.csv" if c else
                     "not cited (probe, rendered page image, parsed output, scratch, duplicate or superseded file)"})
d = pd.DataFrame(rows).sort_values("file")
d.to_csv(os.path.join(job, "downloads_inventory.csv"), index=False, lineterminator="\n")
print(len(d), "files;", (d.status == "cited in sources.csv").sum(), "cited;", round(d.bytes.sum() / 1e6, 1), "MB")
print("cited files per source check:", sum(len(v) for v in cited.values()), "references")
