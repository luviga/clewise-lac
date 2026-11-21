"""Dump the sheets of Guatemala B1_Scenario_Config.xlsx (read-only) with Excel row numbers.

Usage: python -I config_dump.py <xlsx> <out_txt> [max_cols]
"""
import sys

import openpyxl

path, out = sys.argv[1], sys.argv[2]
maxc = int(sys.argv[3]) if len(sys.argv) > 3 else 14
wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    for ws in wb.worksheets:
        fh.write(f"##### SHEET {ws.title} dims={ws.max_row}x{ws.max_column}\n")
        for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
            vals = ["" if v is None else str(v) for v in row[:maxc]]
            if any(vals):
                fh.write(f"{i}\t" + "\t".join(vals) + "\n")
print("done")
