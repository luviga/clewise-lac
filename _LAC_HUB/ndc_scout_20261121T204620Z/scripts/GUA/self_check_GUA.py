"""Self-check of targets_GUA.csv and projections_GUA.csv before the hub check: for every row,
look for the value on the cited pages (text cache, then pypdf). Prints only; writes nothing.

Usage (from the job folder): python -I scripts/GUA/self_check_GUA.py
"""
import csv
import importlib.util
import os

JOB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
spec = importlib.util.spec_from_file_location("hc", os.path.join(JOB, "scripts", "hub_check_values.py"))
hc = importlib.util.module_from_spec(spec)
import sys
sys.argv = ["x", JOB]
spec.loader.exec_module(hc)

src = {r["id"]: r for r in csv.DictReader(open(os.path.join(JOB, "parts/sources_GUA.csv"), encoding="utf-8"))}
for sid, r in src.items():
    ok = hc.sha256(os.path.join(JOB, r["file"])) == r["SHA-256"]
    print(sid, "sha ok" if ok else "SHA MISMATCH")
for kind in ["targets", "projections"]:
    for i, r in enumerate(csv.DictReader(open(os.path.join(JOB, f"{kind}_GUA.csv"), encoding="utf-8")), start=2):
        forms = hc.variants(r["value"])
        rid = r.get("target_id") or f"line{i}"
        if not forms:
            print(kind, rid, "no_value")
            continue
        hit = None
        for n in hc.pages_of(r["page"]):
            tp = os.path.join(JOB, "downloads", "GUA", "text", r["source_id"], f"p{n}.txt")
            if os.path.exists(tp):
                hit = hc.find_in(open(tp, encoding="utf-8").read(), forms)
            if not hit:
                hit = hc.find_in(hc.pdf_page_text(os.path.join(JOB, src[r["source_id"]]["file"]), n), forms)
            if hit:
                break
        if not hit:
            print(kind, rid, r["source_id"], r["page"], r["value"], "NOT FOUND")
print("done")
