"""B3 spot check for Honduras: reopen ten values across documents and confirm each printed form on the
physical page, in the pdfplumber text cache and in a fresh pypdf extraction of the PDF page.

Usage: python -I spot_check_HON.py <job_folder>
Writes parts/spot_checks_HON.csv. Unit and year were read on the same page by hand.
"""
import csv
import logging
import os
import sys

import pypdf

logging.disable(logging.CRITICAL)
JOB = sys.argv[1]
SRC = {r["id"]: r for r in csv.DictReader(open(os.path.join(JOB, "parts", "sources_HON.csv"), encoding="utf-8"))}

CHECKS = [
    ("targets_HON.csv", "HON-T001", "HON-01", 23, "12847.2", "Gg CO2e", "2035", "12,847.2 Gg CO"),
    ("targets_HON.csv", "HON-T018", "HON-01", 26, "70", "percent", "2030", "alcanzar el 70%"),
    ("targets_HON.csv", "HON-T027", "HON-01", 27, "7.5", "percent of fleet", "2035", "7.5% hacia el 2035"),
    ("projections_HON.csv", "HON-01 p.24 Energy BAU 2030", "HON-01", 24, "9161", "Gg CO2e", "2030", "2030 6,924 9,161"),
    ("targets_HON.csv", "HON-T059", "HON-02", 4, "4845.5", "Gg CO2e", "2030", "4845.5 Gg CO2-eq"),
    ("targets_HON.csv", "HON-T067", "HON-03", 33, "20", "percent", "2030", "Escenario de mitigación 1 9,734 20%"),
    ("targets_HON.csv", "HON-T070", "HON-04", 2, "15", "percent", "2030", "Reducción de un 15%"),
    ("targets_HON.csv", "HON-T073", "HON-05", 524, "80", "percent", "2038", "más del 80% de la generación"),
    ("targets_HON.csv", "HON-T087", "HON-07", 82, "110.67", "Gg CO2e per year", "2030", "110,67 Gg"),
    ("targets_HON.csv", "HON-T089", "HON-08", 83, "76", "percent", "2030", "76%, 75% y 71%"),
]
readers = {}
rows = []
for fname, rid, sid, page, val, unit, year, form in CHECKS:
    with open(os.path.join(JOB, "downloads", "HON", "text", sid, f"p{page}.txt"), encoding="utf-8") as fh:
        in_cache = form in fh.read()
    path = os.path.join(JOB, SRC[sid]["file"])
    if path not in readers:
        readers[path] = pypdf.PdfReader(path)
    txt = readers[path].pages[page - 1].extract_text() or ""
    in_pypdf = form in " ".join(txt.split())
    ok = in_cache and in_pypdf
    how = (f"printed form '{form}' searched on physical p.{page}: pdfplumber text cache "
           f"{'found' if in_cache else 'not found'}, pypdf extraction of the PDF page "
           f"{'found' if in_pypdf else 'not found'}; unit and year read on the same page by hand")
    rows.append(["Honduras", 1, fname, rid, sid, f"p.{page}", val, unit, year, "yes" if ok else "no", how, ""])
with open(os.path.join(JOB, "parts", "spot_checks_HON.csv"), "w", encoding="utf-8", newline="\n") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["country", "round", "file", "row_id", "source_id", "page", "value", "unit", "year", "confirmed",
                "how_checked", "correction"])
    w.writerows(rows)
print(sum(r[9] == "yes" for r in rows), "of", len(rows), "confirmed")
for r in rows:
    if r[9] != "yes":
        print(r)
