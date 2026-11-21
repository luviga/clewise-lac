"""B3 spot check for Ecuador: reopen ten values and confirm them on the cited page.

Usage: python -I spot_check_ECU.py <job_folder>
For each chosen row the printed form is searched in the pdfplumber text cache and, independently, in the
pypdf extraction of the same physical PDF page. Unit and year were read by hand on the same page.
Writes parts/spot_checks_ECU.csv.
"""
import csv
import os
import re
import sys

from pypdf import PdfReader

JOB = sys.argv[1]
SRC = {r["id"]: r["file"] for r in csv.DictReader(open(os.path.join(JOB, "parts", "sources_ECU.csv"), encoding="utf-8"))}

# (file, row_id, source, page, value, unit, year, printed form searched)
CHECKS = [
    ("targets_ECU.csv", "ECU-T001", "ECU-01", 55, "7", "percent", "2035", "del 7%"),
    ("targets_ECU.csv", "ECU-T004", "ECU-01", 56, "10600", "kt CO2eq", "2035", "10.600"),
    ("targets_ECU.csv", "ECU-T013", "ECU-02", 22, "9", "percent", "2025", "un 9%"),
    ("targets_ECU.csv", "ECU-T020", "ECU-03", 102, "39200", "Gg CO2eq", "2035", "39.200"),
    ("targets_ECU.csv", "ECU-T026", "ECU-03", 104, "64", "percent", "2035", "64%"),
    ("targets_ECU.csv", "ECU-T042", "ECU-03", 107, "22", "percent", "2050", "22%"),
    ("targets_ECU.csv", "ECU-T063", "ECU-04", 222, "4400", "kt CO2eq", "2025", "4400"),
    ("targets_ECU.csv", "ECU-T069", "ECU-07", 159, "4034", "MW", "2032", "4034"),
    ("targets_ECU.csv", "ECU-T075", "ECU-08", 67, "8.3", "percent", "2035", "8,3%"),
    ("projections_ECU.csv", "Tabla 31 Energy 2025", "ECU-04", 234, "51100", "kt CO2eq", "2025", "51.100"),
]


def norm(t):
    return re.sub(r"\s+", " ", t or "")


rows = []
readers = {}
for f, rid, src, page, value, unit, year, form in CHECKS:
    cache = os.path.join(JOB, "downloads", "ECU", "text", src, f"p{page}.txt")
    c_ok = form in norm(open(cache, encoding="utf-8").read())
    if src not in readers:
        readers[src] = PdfReader(os.path.join(JOB, SRC[src]))
    p_ok = form in norm(readers[src].pages[page - 1].extract_text())
    ok = c_ok or p_ok
    rows.append({"country": "Ecuador", "round": 1, "file": f, "row_id": rid, "source_id": src, "page": f"p.{page}",
                 "value": value, "unit": unit, "year": year, "confirmed": "yes" if ok else "no",
                 "how_checked": f"printed form '{form}' searched on physical p.{page}: pdfplumber text cache "
                                f"{'found' if c_ok else 'not found'}, pypdf extraction of the PDF page {'found' if p_ok else 'not found'}; "
                                "unit and year read on the same page by hand",
                 "correction": ""})
with open(os.path.join(JOB, "parts", "spot_checks_ECU.csv"), "w", encoding="utf-8", newline="\n") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r["row_id"], r["confirmed"], r["how_checked"][:140])
