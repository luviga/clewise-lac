"""Self-check of the Costa Rica outputs (run: python -I selfcheck_CR.py)."""
import csv
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.path.dirname(HERE)
JOB = os.path.dirname(CC)
problems = []

cells = list(csv.DictReader(open(os.path.join(CC, "cells_CR.csv"), encoding="utf-8")))
props = list(csv.DictReader(open(os.path.join(CC, "proposals_CR.csv"), encoding="utf-8")))
key = lambda r: (r["country"], r["model"], r["sheet"], r["tech"], r["parameter"], r["year"])
ck = [key(r) for r in cells]
pk = [key(r) for r in props]
if len(set(pk)) != len(pk):
    problems.append("duplicate proposal keys")
if sorted(ck) != sorted(pk):
    problems.append("cell keys and proposal keys differ")
cur = {key(r): r["current_value"] for r in cells}
for r in props:
    if r["current_value"] != cur.get(key(r)):
        problems.append("current_value mismatch %s" % (key(r),))
    if r["change_class"] not in ("confirmed", "replace", "assumption", "manual"):
        problems.append("bad class %s" % (key(r),))
    if r["change_class"] == "assumption" and not r["assumption_sentence"]:
        problems.append("assumption without sentence %s" % (key(r),))
    if r["change_class"] != "assumption" and not r["source_ids"]:
        problems.append("sourced row without source ids %s" % (key(r),))
    if r["proposed_value"] == "":
        problems.append("empty proposed value %s" % (key(r),))

ids = set()
for f in [os.path.join(CC, "sources_CR.csv"), os.path.join(JOB, "sources_GEN.csv")] + glob.glob(os.path.join(JOB, "GEN", "sources_GEN_*.csv")):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        ids.add(r["id"])
for r in props:
    for s in filter(None, r["source_ids"].split(";")):
        if s not in ids:
            problems.append("unknown source id %s" % s)

srcs = list(csv.DictReader(open(os.path.join(CC, "sources_CR.csv"), encoding="utf-8")))
for s in srcs:
    for p in s["downloaded_file"].split(";"):
        if not os.path.exists(os.path.join(JOB, p.strip())):
            problems.append("missing downloaded file %s" % p)
    if re.search(r"readthedocs|clg|^[A-Za-z]:\\|file://", s["url"], re.I):
        problems.append("forbidden url %s" % s["id"])

bad_words = re.compile(r"\b(job|hub|commit|sheet|workbook|file|kept as used|retained|provisional|not found|could not)\b", re.I)
for r in props:
    if bad_words.search(r["assumption_sentence"]):
        problems.append("forbidden word in assumption %s: %s" % (key(r), bad_words.search(r["assumption_sentence"]).group(0)))

for f in glob.glob(os.path.join(CC, "*.csv")) + glob.glob(os.path.join(CC, "*.md")) + glob.glob(os.path.join(HERE, "*.py")):
    t = open(f, encoding="utf-8").read()
    if "\u2014" in t:
        problems.append("em dash in %s" % os.path.basename(f))
    if "\r\n" in t:
        problems.append("CRLF in %s" % os.path.basename(f))
    if re.search(r"C:\\\\|C:/Users|/c/clw|C:\\clw", t) and not f.endswith(".py"):
        problems.append("machine path in %s" % os.path.basename(f))

print("cells", len(cells), "proposals", len(props), "source ids known", len(ids))
print("PASS" if not problems else "FAIL")
for p in problems[:50]:
    print(" -", p)
