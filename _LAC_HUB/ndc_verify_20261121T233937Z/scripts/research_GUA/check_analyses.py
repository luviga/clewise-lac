"""Check an analyses_<code>.csv against the page texts.

Usage: python -I check_analyses.py <JOB> <code>

For every row with a value: the page file text_all/<id>/p<N>.txt (or p1.txt for html) must
contain the value. Digits separated by commas or spaces in the page are joined before the
search, and a value like 13.0 also matches 13. Also checks the column set, the source ids
against parts/sources_D_<code>.csv, the class against that file, and that no em dash is used.
"""
import csv
import os
import re
import sys

COLS = ["source_id", "class", "model_or_method", "scenario", "scenario_definition", "indicator",
        "sector", "year", "value", "unit", "page", "note"]


def norm(t):
    t = t.replace(" ", " ")
    prev = None
    while prev != t:
        prev = t
        t = re.sub(r"(\d)(?:,| ,)(\d{3})(?!\d)", r"\1\2", t)
        t = re.sub(r"(?<![\d.,])(\d{1,3}) (\d{3})(?![\d.,%])", r"\1\2", t)
    return t


def main():
    job, code = sys.argv[1], sys.argv[2]
    src = {}
    with open(os.path.join(job, "parts", "sources_D_%s.csv" % code), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            src[r["id"]] = r
    path = os.path.join(job, "analyses_%s.csv" % code)
    raw = open(path, "rb").read()
    bad = 0
    if b"\r\n" in raw:
        print("CRLF line endings")
        bad += 1
    if chr(0x2014).encode("utf-8") in raw:
        print("em dash found")
        bad += 1
    with open(path, encoding="utf-8", newline="") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != COLS:
            print("columns differ", rd.fieldnames)
            bad += 1
        n = 0
        for i, r in enumerate(rd, start=2):
            n += 1
            sid = r["source_id"]
            if sid not in src:
                print(i, "unknown source", sid)
                bad += 1
                continue
            if src[sid]["class"] != r["class"]:
                print(i, "class differs", sid, r["class"], src[sid]["class"])
                bad += 1
            v = r["value"].strip()
            if not v:
                continue
            if not re.fullmatch(r"-?\d+(\.\d+)?", v):
                print(i, "value not plain", v)
                bad += 1
            pg = r["page"].strip()
            if pg == "html":
                pn = 1
            else:
                m = re.fullmatch(r"p\.(\d+)", pg)
                if not m:
                    print(i, "page format", pg)
                    bad += 1
                    continue
                pn = int(m.group(1))
            pf = os.path.join(job, "downloads", code, "text_all", sid, "p%d.txt" % pn)
            if not os.path.exists(pf):
                print(i, "no page file", pf)
                bad += 1
                continue
            raw_t = open(pf, encoding="utf-8").read().replace("–", "-").replace("−", "-")
            texts = [raw_t, norm(raw_t)]
            cands = {v}
            if "." in v:
                cands.add(v.rstrip("0").rstrip("."))
            ok = any(re.search(r"(?<![\d.])" + re.escape(c) + r"(?![\d])", t)
                     for c in cands for t in texts)
            if not ok:
                print(i, "value not on page", sid, pg, v, r["indicator"][:50])
                bad += 1
    print(code, "rows", n, "problems", bad)


if __name__ == "__main__":
    main()
