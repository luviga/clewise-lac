"""List sheets and rows of an xlsx read-only. Usage: python -I dump_config.py <xlsx> [sheet] [maxrows] [grep]
Prints Excel row numbers (1-based) with the first columns."""
import sys

import openpyxl

path = sys.argv[1]
sheet = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
maxrows = int(sys.argv[3]) if len(sys.argv) > 3 else 40
grep = sys.argv[4].lower() if len(sys.argv) > 4 else None
wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
if sheet is None:
    for ws in wb.worksheets:
        print(ws.title, ws.max_row, ws.max_column)
    sys.exit(0)
ws = wb[sheet]
n = 0
for r_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
    vals = ["" if v is None else str(v) for v in row]
    line = " | ".join(vals[:40])
    if grep and grep not in line.lower() and r_idx > 1:
        continue
    print(f"R{r_idx}: {line}")
    n += 1
    if n >= maxrows:
        break
