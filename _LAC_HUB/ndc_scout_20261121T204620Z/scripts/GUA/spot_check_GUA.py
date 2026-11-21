"""B3 spot check for Guatemala: reopen chosen rows and look for the printed value on the cited page,
both in the pdfplumber text cache and in an independent pypdf extraction of the same PDF page.

Usage (from the job folder): python -I scripts/GUA/spot_check_GUA.py <round>
Writes/extends parts/spot_checks_GUA.csv.
"""
import csv
import os
import re
import sys

from pypdf import PdfReader

JOB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {r["id"]: r["file"] for r in csv.DictReader(open(os.path.join(JOB, "parts/sources_GUA.csv"), encoding="utf-8"))}

# (file, row_id, source_id, page, value, unit, year, printed forms to look for)
ROUNDS = {
    "1": [
        ("targets_GUA.csv", "GUA-T001", "GUA-01", 28, "23.7", "percent", "2035", ["reducción del 23.7 % de las emisio", "23.7 %"]),
        ("targets_GUA.csv", "GUA-T008", "GUA-01", 40, "80", "percent", "2035", ["al menos el 80 % de la energ"]),
        ("targets_GUA.csv", "GUA-T016", "GUA-01", 47, "10000", "vehicles", "2035", ["10,000 vehículos eléctricos adicionales", "10,000 veh"]),
        ("projections_GUA.csv", "GUA-01 p.131 BAU 2030", "GUA-01", 131, "71838.6", "kt CO2eq", "2030", ["2030 71,838.6 63,975.1"]),
        ("targets_GUA.csv", "GUA-T039", "GUA-02", 70, "11.2", "percent", "2030", ["reducido el 11.2 % de las emisiones"]),
        ("targets_GUA.csv", "GUA-T044", "GUA-02", 77, "24.3", "percent", "2032", ["24.3 % de los veh"]),
        ("targets_GUA.csv", "GUA-T053", "GUA-03", 6, "11.2", "percent", "2030", ["11.2% de sus emisiones"]),
        ("targets_GUA.csv", "GUA-T056", "GUA-04", 58, "59", "percent", "2050", ["59% de las emisiones proyectadas"]),
        ("targets_GUA.csv", "GUA-T067", "GUA-05", 254, "15", "percent", "2030", ["15 % de mezcla para 2030"]),
        ("targets_GUA.csv", "GUA-T073", "GUA-07", 92, "29.2", "percent", "2032", ["29.2% para"]),
    ],
}


def norm(s):
    return re.sub(r"\s+", " ", s)


def main():
    rnd = sys.argv[1]
    out = os.path.join(JOB, "parts/spot_checks_GUA.csv")
    header = ["country", "round", "file", "row_id", "source_id", "page", "value", "unit", "year", "confirmed", "how_checked", "correction"]
    rows = []
    if os.path.exists(out):
        rows = [r for r in csv.reader(open(out, encoding="utf-8"))][1:]
        rows = [r for r in rows if r[1] != rnd]
    readers = {}
    for f, rid, sid, page, val, unit, yr, forms in ROUNDS[rnd]:
        cache = open(os.path.join(JOB, f"downloads/GUA/text/{sid}/p{page}.txt"), encoding="utf-8").read()
        if sid not in readers:
            readers[sid] = PdfReader(os.path.join(JOB, FILES[sid]))
        alt = readers[sid].pages[page - 1].extract_text() or ""
        hit_c = [x for x in forms if norm(x) in norm(cache)]
        hit_a = [x for x in forms if norm(x) in norm(alt)]
        ok = bool(hit_c) and bool(hit_a)
        form = (hit_c or forms)[0]
        how = (f"printed form {form!r} searched on physical p.{page}: pdfplumber text cache {'found' if hit_c else 'NOT found'}, "
               f"pypdf extraction of the PDF page {'found' if hit_a else 'NOT found'}; unit and year read on the same page by hand")
        rows.append(["Guatemala", rnd, f, rid, sid, f"p.{page}", val, unit, yr, "yes" if ok else "no", how, ""])
        print(rid, ok, bool(hit_c), bool(hit_a))
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


if __name__ == "__main__":
    main()
