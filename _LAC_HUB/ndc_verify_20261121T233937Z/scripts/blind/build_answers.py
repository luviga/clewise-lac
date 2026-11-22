"""Build JOB/blind_answers_<code>.csv from a pipe-separated staging file.

Staging lines (blank lines and lines starting with # are skipped):
  blind_id|page_read|value|unit|year|reference|note
  SERIES|blind_id|page_read|unit|reference|note|year:value,year:value,...
Usage: build_answers.py <staging.txt> <code>
"""
import csv
import sys

JOB = "C:/clw_scout/_LAC_HUB/ndc_verify_20261121T233937Z"
COLS = ["blind_id", "page_read", "value", "unit", "year", "reference", "note"]


def main(staging, code):
    rows = []
    with open(staging, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.rstrip("\r\n")
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("|")
            if parts[0] == "SERIES":
                if len(parts) != 7:
                    sys.exit(f"bad SERIES line {ln}: {line}")
                _, bid, page, unit, ref, note, series = parts
                for item in series.split(","):
                    y, v = item.split(":")
                    rows.append([bid, page, v.strip(), unit, y.strip(), ref, note])
            else:
                if len(parts) != 7:
                    sys.exit(f"bad line {ln} ({len(parts)} fields): {line}")
                rows.append([p.strip() for p in parts])
    for r in rows:
        for cell in r:
            if "\u2014" in cell or "\u2013" in cell:
                sys.exit(f"dash in {r}")
        if r[2]:
            float(r[2])
    out = f"{JOB}/blind_answers_{code}.csv"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLS)
        w.writerows(rows)
    ids = sorted({r[0] for r in rows})
    print(out, len(rows), "rows,", len(ids), "ids")
    with open(f"{JOB}/blind_{code}.csv", encoding="utf-8") as f:
        want = [r["blind_id"] for r in csv.DictReader(f)]
    missing = [b for b in want if b not in ids]
    print("missing ids:", missing)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
