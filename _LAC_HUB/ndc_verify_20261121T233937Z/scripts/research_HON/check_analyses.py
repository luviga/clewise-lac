"""Check JOB/analyses_<CODE>.csv against the page texts and the step D sources list.

Usage: python -I check_analyses.py <CODE>
For each row with a value, looks for the value as printed (several number formats) in
JOB/downloads/<CODE>/text_all/<id>/p<N>.txt. Also checks source ids, columns, and that no
em dash appears in the CSV files of the country.
"""
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.dirname(os.path.dirname(HERE))
FIELDS = ["source_id", "class", "model_or_method", "scenario", "scenario_definition", "indicator",
          "sector", "year", "value", "unit", "page", "note"]


def variants(v):
    out = {v}
    if v.startswith("-"):
        out.add(v[1:])
    try:
        x = float(v)
    except ValueError:
        return out
    a = abs(x)
    if a == int(a) and a >= 1000:
        n = int(a)
        out.add("{:,}".format(n))
        out.add("{:,}".format(n).replace(",", "."))
        out.add("{:,}".format(n).replace(",", " "))
    if "." in v:
        out.add(v.lstrip("-").replace(".", ","))
    return out


def main():
    code = sys.argv[1]
    src = os.path.join(JOB, "parts", "sources_D_%s.csv" % code)
    with open(src, encoding="utf-8", newline="") as f:
        sources = {r["id"]: r for r in csv.DictReader(f)}
    path = os.path.join(JOB, "analyses_%s.csv" % code)
    with open(path, encoding="utf-8", newline="") as f:
        rd = csv.DictReader(f)
        assert rd.fieldnames == FIELDS, rd.fieldnames
        rows = list(rd)
    bad = 0
    for i, r in enumerate(rows, 2):
        sid = r["source_id"]
        if sid not in sources:
            print("line", i, "unknown source", sid)
            bad += 1
            continue
        if sources[sid]["class"] != r["class"]:
            print("line", i, "class differs from sources", sid, r["class"], sources[sid]["class"])
            bad += 1
        if not r["value"]:
            continue
        m = re.match(r"^p\.(\d+)$", r["page"])
        if r["page"] == "html":
            pages = [1]
        elif m:
            pages = [int(m.group(1))]
        else:
            print("line", i, "bad page", r["page"])
            bad += 1
            continue
        txt = ""
        for p in pages:
            fp = os.path.join(JOB, "downloads", code, "text_all", sid, "p%d.txt" % p)
            if os.path.exists(fp):
                txt += open(fp, encoding="utf-8").read()
        flat = re.sub(r"\s+", " ", txt)
        if not any(re.search(r"(?<![\d.,])" + re.escape(x) + r"(?![\d])", flat) for x in variants(r["value"])):
            print("line", i, "value not found on page:", sid, r["page"], r["value"], "|", r["indicator"])
            bad += 1
    for name in ["analyses_%s.csv" % code, "parts/sources_D_%s.csv" % code, "parts/pending_D_%s.csv" % code]:
        fp = os.path.join(JOB, name)
        if os.path.exists(fp):
            raw = open(fp, "rb").read()
            if bytes([0xE2, 0x80, 0x94]) in raw or b"\r\n" in raw:
                print("em dash or CRLF in", name)
                bad += 1
    print(code, "rows", len(rows), "problems", bad)


if __name__ == "__main__":
    main()
