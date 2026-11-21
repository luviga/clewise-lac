"""B3 spot check for DR: reopen chosen rows and look for the printed value on the cited page,
both in the pdfplumber text cache and in an independent pypdf extraction of the same PDF page.

Usage (from the job folder): python -I scripts/DR/spot_check_DR.py <round>
Writes/extends parts/spot_checks_DR.csv.
"""
import csv
import os
import re
import sys

from pypdf import PdfReader

JOB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {r["id"]: r["file"] for r in csv.DictReader(open(os.path.join(JOB, "parts/sources_DR.csv"), encoding="utf-8"))}

# (file, row_id, source_id, page, value, unit, year, printed forms to look for)
ROUNDS = {
    "1": [
        ("targets_DR.csv", "DR-T002", "DR-01", 62, "14732.1", "kt CO2eq", "2030", ["14,732.10", "14,732.1"]),
        ("targets_DR.csv", "DR-T011", "DR-01", 148, "1429", "MW", "2030", ["1,429 MW"]),
        ("targets_DR.csv", "DR-T013", "DR-01", 149, "1529", "MW (nominal)", "2030", ["1,529 MWn"]),
        ("targets_DR.csv", "DR-T018", "DR-01", 150, "1005400", "MWh per year", "2029", ["1,005,400 MWh"]),
        ("targets_DR.csv", "DR-T043", "DR-02", 5, "27", "percent", "2030", ["27 % de las emisiones"]),
        ("targets_DR.csv", "DR-T055", "DR-02", 158, "15", "percent", "2030", ["15% de autos el"]),
        ("targets_DR.csv", "DR-T059", "DR-03", 2, "25", "percent", "2030", ["Reduction of 25% of base year emissions by 2030"]),
        ("targets_DR.csv", "DR-T062", "DR-04", 174, "30", "percent", "2030", ["30% para 2030"]),
        ("targets_DR.csv", "DR-T065", "DR-06", 78, "2.8", "t CO2 per capita", "2030", ["3.6 3.4 3.2 3.0 2.8"]),
        ("projections_DR.csv", "DR-04 p.173 Energy 2035", "DR-04", 173, "38200", "kt CO2eq", "2035", ["38,200 ktCO"]),
    ],
}


def norm(s):
    return re.sub(r"\s+", " ", s)


def main():
    rnd = sys.argv[1]
    out = os.path.join(JOB, "parts/spot_checks_DR.csv")
    header = ["country", "round", "file", "row_id", "source_id", "page", "value", "unit", "year", "confirmed", "how_checked", "correction"]
    rows = []
    if os.path.exists(out):
        rows = [r for r in csv.reader(open(out, encoding="utf-8"))][1:]
        rows = [r for r in rows if r[1] != rnd]
    readers = {}
    for f, rid, sid, page, val, unit, yr, forms in ROUNDS[rnd]:
        cache = open(os.path.join(JOB, f"downloads/DR/text/{sid}/p{page}.txt"), encoding="utf-8").read()
        if sid not in readers:
            readers[sid] = PdfReader(os.path.join(JOB, FILES[sid]))
        alt = readers[sid].pages[page - 1].extract_text() or ""
        in_cache = any(norm(x) in norm(cache) for x in forms)
        in_alt = any(norm(x) in norm(alt) for x in forms)
        ok = in_cache and in_alt
        how = (f"printed form {forms[0]!r} searched on physical p.{page}: pdfplumber text cache {'found' if in_cache else 'NOT found'}, "
               f"pypdf extraction of the PDF page {'found' if in_alt else 'NOT found'}; unit and year read on the same page by hand")
        rows.append(["Dominican Republic", rnd, f, rid, sid, f"p.{page}", val, unit, yr, "yes" if ok else "no", how, ""])
        print(rid, ok, in_cache, in_alt)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


if __name__ == "__main__":
    main()
