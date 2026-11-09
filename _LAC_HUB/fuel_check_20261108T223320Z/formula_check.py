"""Step 4.4 support: per A-O workbook, count formula cells and formula cells with no cached value;
for every planned manifest cell, say whether the target cell holds a formula today. Read-only."""
import csv, os, sys
import pandas as pd
from openpyxl import load_workbook
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"; OUT = sys.argv[1]
res, hits = [], []
for c in ["CostaRica", "DominicanRepublic", "Ecuador", "Guatemala", "Honduras", "Jamaica"]:
    m = pd.read_csv(os.path.join(OUT, f"plan_{c}", "manifest.csv"), encoding="utf-8-sig")
    p = m.ao_path.iloc[0]
    wf = load_workbook(p, data_only=False); wv = load_workbook(p, data_only=True)
    tot = nocache = 0
    for ws in wf.worksheets:
        vs = wv[ws.title]
        for row in ws.iter_rows():
            for cell in row:
                if cell.data_type == 'f':
                    tot += 1
                    if vs[cell.coordinate].value is None: nocache += 1
    nform_target = 0
    hdrs = {}
    for _, r in m.iterrows():
        ws = wf[r.sheet]
        if r.sheet not in hdrs:
            hdrs[r.sheet] = {str(ws.cell(1, k).value).strip(): k for k in range(1, ws.max_column + 1) if ws.cell(1, k).value is not None}
        k = hdrs[r.sheet].get(str(int(r.year)))
        cell = ws.cell(int(r.row_index), k)
        if cell.data_type == 'f':
            nform_target += 1
            hits.append({"country": c, "sheet": r.sheet, "cell": cell.coordinate, "tech": r.tech, "parameter": r.parameter,
                         "year": r.year, "formula": cell.value, "cached_value": wv[r.sheet][cell.coordinate].value,
                         "manifest_old_value": r.old_value})
    res.append({"country": c, "ao_path": os.path.relpath(p, ROOT), "formula_cells_total": tot,
                "formula_cells_without_cached_value": nocache, "planned_cells": len(m), "planned_cells_that_are_formulas": nform_target})
pd.DataFrame(res).to_csv(os.path.join(OUT, "ao_formula_summary.csv"), index=False)
pd.DataFrame(hits).to_csv(os.path.join(OUT, "planned_formula_cells.csv"), index=False)
print(pd.DataFrame(res).to_string())
