"""Print selected rows of B1_Scenario_Config.xlsx (read-only) with year values.

Usage: python -I config_rows.py <workbook> <sheet> <row1,row2,...> [years comma list]
Header row 1 gives column names; year columns are those whose header is a 4-digit year.
"""
import sys

import openpyxl


def main():
    wb_path, sheet, rows = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")]
    years = sys.argv[4].split(",") if len(sys.argv) > 4 else ["2025", "2030", "2035", "2040", "2050"]
    wb = openpyxl.load_workbook(wb_path, read_only=True, data_only=True)
    ws = wb[sheet]
    allrows = list(ws.iter_rows(values_only=True))
    header = [str(h) if h is not None else "" for h in allrows[0]]
    idx = {h: i for i, h in enumerate(header)}
    for r in rows:
        row = allrows[r - 1]
        lead = [str(v) for v in row[:12] if v is not None and str(v).strip() != ""]
        vals = []
        for y in years:
            i = idx.get(y)
            v = row[i] if i is not None and i < len(row) else None
            vals.append("%s=%s" % (y, v if not isinstance(v, float) else round(v, 5)))
        print("%s!%d | %s | %s" % (sheet, r, " | ".join(lead)[:260], " ".join(vals)))


if __name__ == "__main__":
    main()
