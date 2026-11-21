"""Task self-check for Honduras: same rules as scripts/hub_check_values.py (value searched on the cited
page in the text cache, then in a fresh pypdf extraction), but the result goes to an output path outside
the job folder. Read-only for the job files.

Usage: python -I self_check_HON.py <job_folder> <out_csv>
"""
import csv
import importlib.util
import os
import sys

JOB, OUT = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("hcv", os.path.join(JOB, "scripts", "hub_check_values.py"))
hcv = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0], JOB]  # the module reads JOB from argv at import
spec.loader.exec_module(hcv)

src = hcv.load_sources("HON")
out = []
for kind in ["targets", "projections"]:
    with open(os.path.join(JOB, f"{kind}_HON.csv"), encoding="utf-8", newline="") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            sid, page = r["source_id"], r["page"]
            fpath = os.path.join(JOB, src[sid]["file"])
            forms = hcv.variants(r.get("value", ""))
            if not forms:
                out.append([kind, r.get("target_id", f"line{i}"), sid, page, r.get("value", ""), "no_value", ""])
                continue
            hit = None
            for n in hcv.pages_of(page):
                tp = os.path.join(JOB, "downloads", "HON", "text", sid, f"p{n}.txt")
                with open(tp, encoding="utf-8", errors="replace") as tf:
                    hit = hcv.find_in(tf.read(), forms)
                if not hit:
                    hit = hcv.find_in(hcv.pdf_page_text(fpath, n), forms)
                if hit:
                    hit = f"'{hit}' on p.{n}"
                    break
            out.append([kind, r.get("target_id", f"line{i}"), sid, page, r["value"], "found" if hit else "not_found",
                        hit or ""])
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["file", "row_id", "source_id", "page", "value", "status", "how"])
    w.writerows(out)
c = {}
for r in out:
    c[r[5]] = c.get(r[5], 0) + 1
print(c)
for r in out:
    if r[5] != "found":
        print(r)
