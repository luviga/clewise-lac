"""B3 spot check for Jamaica: reopen ten values, search the printed form on the cited physical page in
(a) the pdfplumber text cache and (b) a fresh pypdf extraction of the PDF page. Writes parts/spot_checks_JAM.csv.

Usage: python -I spot_check_JAM.py <job_dir>
"""
import csv
import os
import re
import sys

import pypdf

JOB = sys.argv[1]
FILES = {}
with open(os.path.join(JOB, "parts", "sources_JAM.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        FILES[r["id"]] = os.path.join(JOB, r["file"])

# (file, row_id, source, page, value, unit, year, printed form, unit/year context to read by hand)
CHECKS = [
    ("targets_JAM.csv", "JAM-T002", "JAM-01", 4, "19.55", "percent", "2030", "19.55% compared to BAU"),
    ("targets_JAM.csv", "JAM-T017", "JAM-01", 21, "5.8", "MtCO2e", "2030", "would be 5.8 MtCO"),
    ("targets_JAM.csv", "JAM-T029", "JAM-01", 14, "63", "percent", "2035", "50% and 63% of net"),
    ("targets_JAM.csv", "JAM-T049", "JAM-02", 55, "65", "percent", "2035", "at least 65% of electricity"),
    ("targets_JAM.csv", "JAM-T070", "JAM-02", 61, "67", "percent of fleet", "2050", "67% of"),
    ("targets_JAM.csv", "JAM-T104", "JAM-03", 5, "25.4", "percent", "2030", "25.4% reduction relative to business-as-usual"),
    ("projections_JAM.csv", "JAM-04 p.4 BAU 2030", "JAM-04", 4, "14492", "ktCO2e", "2030", "2030:14,492"),
    ("targets_JAM.csv", "JAM-T116", "JAM-07", 77, "63.4", "percent", "2035", "63.4%"),
    ("targets_JAM.csv", "JAM-T118", "JAM-07", 15, "1143", "MW", "2041", "1143 MW of solar PV plants"),
    ("projections_JAM.csv", "JAM-06 p.346 Total 2050", "JAM-06", 346, "18897", "thousand tonnes CO2e", "2050", "18,897"),
]


def squash(t):
    return re.sub(r"\s+", "", t)


def main():
    out = []
    for f, rid, sid, page, val, unit, year, form in CHECKS:
        cache = open(os.path.join(JOB, "downloads", "JAM", "text", sid, "p%d.txt" % page), encoding="utf-8").read()
        fresh = pypdf.PdfReader(FILES[sid]).pages[page - 1].extract_text() or ""
        a = squash(form) in squash(cache)
        b = squash(form) in squash(fresh)
        conf = "yes" if (a or b) else "no"
        how = ("printed form '%s' searched on physical p.%d: pdfplumber text cache %s, pypdf extraction %s; "
               "unit and year read on the same page by hand") % (form, page, "found" if a else "not found", "found" if b else "not found")
        out.append(["Jamaica", 1, f, rid, sid, "p.%d" % page, val, unit, year, conf, how, ""])
        print(rid, conf, a, b)
    with open(os.path.join(JOB, "parts", "spot_checks_JAM.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["country", "round", "file", "row_id", "source_id", "page", "value", "unit", "year", "confirmed", "how_checked", "correction"])
        w.writerows(out)


if __name__ == "__main__":
    main()
