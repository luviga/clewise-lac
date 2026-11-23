"""Self-check of the ECU outputs (adapted from the HON check) (run: python -I self_check_ECU.py)."""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CC_DIR = os.path.dirname(HERE)
JOB = os.path.dirname(CC_DIR)
problems = []


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


cells = read(os.path.join(CC_DIR, "cells_ECU.csv"))
props = read(os.path.join(CC_DIR, "proposals_ECU.csv"))
key = lambda r: (r["country"], r["model"], r["sheet"], r["tech"], r["parameter"], r["year"])
ck = {key(r): r for r in cells}
pk = {}
for r in props:
    if key(r) in pk:
        problems.append("duplicate proposal %s" % (key(r),))
    pk[key(r)] = r
if set(ck) != set(pk) or len(props) != len(cells):
    problems.append("cell/proposal key mismatch: %d cells, %d proposals" % (len(cells), len(props)))
for k, c in ck.items():
    p = pk.get(k)
    if p and p["current_value"] != c["current_value"]:
        problems.append("current_value differs %s" % (k,))

ids = set()
for f in ("sources_ECU.csv",):
    for r in read(os.path.join(CC_DIR, f)):
        ids.add(r["id"])
        for d in r["downloaded_file"].split(";"):
            if not d.strip().startswith("downloads/") or not os.path.exists(os.path.join(JOB, d.strip())):
                problems.append("missing downloaded_file %s" % d)
        if re.search(r"readthedocs|clg|[A-Za-z]:\\|file://|/c/|github.com/luviga", r["url"], re.I):
            problems.append("forbidden url %s" % r["url"])
for f in ("sources_GEN.csv", os.path.join("GEN", "sources_GEN_vehicles.csv"), os.path.join("GEN", "sources_GEN_sector.csv")):
    for r in read(os.path.join(JOB, f)):
        ids.add(r["id"])

forbidden = re.compile(r"\b(kept as used|retained|provisional|not found|could not be found|job|hub|commit|sheet|workbook|file|csv|xlsx|history)\b", re.I)
classes = {"confirmed", "replace", "assumption", "manual"}
for r in props:
    if r["change_class"] not in classes:
        problems.append("bad class %s" % (key(r),))
    if r["change_class"] == "assumption" and r["source_ids"]:
        for s in r["source_ids"].split(";"):
            if s not in ids:
                problems.append("unknown source id %s in %s" % (s, key(r)))
    if r["change_class"] in ("confirmed", "replace"):
        if not r["source_ids"]:
            problems.append("no source ids %s" % (key(r),))
        for s in r["source_ids"].split(";"):
            if s not in ids:
                problems.append("unknown source id %s in %s" % (s, key(r)))
        if r["source_currency_year"] and not r["cpi_factor"]:
            problems.append("currency year without cpi %s" % (key(r),))
    if r["change_class"] == "assumption":
        if not r["assumption_sentence"]:
            problems.append("assumption without sentence %s" % (key(r),))
        if forbidden.search(r["assumption_sentence"]):
            problems.append("forbidden word in assumption %s: %s" % (key(r), forbidden.search(r["assumption_sentence"]).group(0)))

for f in os.listdir(CC_DIR):
    path = os.path.join(CC_DIR, f)
    if os.path.isfile(path) and f.endswith((".csv", ".md")):
        b = open(path, "rb").read()
        if b"\r\n" in b:
            problems.append("CRLF in %s" % f)
        if chr(0x2014).encode("utf-8") in b:
            problems.append("em dash in %s" % f)
for f in os.listdir(HERE):
    if f.endswith(".py") and f != os.path.basename(__file__):
        t = open(os.path.join(HERE, f), encoding="utf-8").read()
        if re.search(r"[A-Za-z]:\\\\|/c/clw|Users\\\\", t):
            problems.append("machine path in %s" % f)

print("cells %d, proposals %d, source ids known %d" % (len(cells), len(props), len(ids)))
print("PASS" if not problems else "FAIL")
for p in problems[:50]:
    print(" -", p)
