"""Step 3.1: per-sheet size and formula counts of the fuel workbook, plus a full text dump
(values, with the formula text where a cell holds one) for reading. Read-only."""
import sys, csv
from openpyxl import load_workbook
p, outdir = sys.argv[1], sys.argv[2]
wf = load_workbook(p, data_only=False)
wv = load_workbook(p, data_only=True)
rows = []
with open(f"{outdir}/fuel_wb_dump.txt", "w", encoding="utf-8") as fh:
    for ws in wf.worksheets:
        vs = wv[ws.title]
        nform = nval = nocache = 0
        fh.write(f"\n##### SHEET '{ws.title}' dims={ws.dimensions}\n")
        for row in ws.iter_rows():
            parts = []
            for c in row:
                if c.value is None: continue
                nval += 1
                v = vs[c.coordinate].value
                if c.data_type == 'f':
                    nform += 1
                    if v is None: nocache += 1
                    parts.append(f"{c.coordinate}={v!r} [{c.value}]")
                else:
                    parts.append(f"{c.coordinate}={v!r}")
            if parts: fh.write(" | ".join(parts) + "\n")
        rows.append([ws.title, ws.max_row, ws.max_column, nval, nform, nocache])
with open(f"{outdir}/fuel_wb_sheets.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["sheet", "max_row", "max_col", "nonempty_cells", "formula_cells", "formula_cells_without_cached_value"]); w.writerows(rows)
for r in rows: print(r)
