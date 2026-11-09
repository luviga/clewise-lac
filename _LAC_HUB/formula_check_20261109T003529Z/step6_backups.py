"""Step 6 evidence: for each A-O workbook and its backups in Jamaica and Ecuador A1_Outputs, count formula cells,
formula cells with a stored value, formula cells in year columns, and read document properties. Read-only."""
import os, glob, csv, hashlib, datetime
from openpyxl import load_workbook
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
OUT = os.path.dirname(os.path.abspath(__file__))
files = sorted(glob.glob(os.path.join(ROOT, r"Jamaica\JAM_ENERGY\A1_Outputs\A-O_Parametrization*.xlsx")) +
               glob.glob(os.path.join(ROOT, r"Ecuador\ECU_Energy\A1_Outputs\A-O_Parametrization*.xlsx")))
rows = []
for p in files:
    if "COMPLETED" in p: continue
    wf = load_workbook(p, read_only=True); wv = load_workbook(p, data_only=True, read_only=True)
    n = ncache = nyear = 0
    for ws in wf.worksheets:
        hdr = {}
        sv = {c.coordinate: c.value for r in wv[ws.title].iter_rows() for c in r if hasattr(c, "coordinate") and c.value is not None}
        for r in ws.iter_rows():
            for c in r:
                if not hasattr(c, "coordinate"): continue
                if c.row == 1 and c.value is not None: hdr[c.column] = c.value
                if c.data_type == "f":
                    n += 1; ncache += c.coordinate in sv; nyear += isinstance(hdr.get(c.column), int)
    st = os.stat(p); pr = wf.properties
    rows.append({"file": os.path.relpath(p, ROOT), "size": st.st_size,
                 "mtime_utc": datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "creator": pr.creator, "lastModifiedBy": pr.lastModifiedBy, "modified_prop": pr.modified,
                 "formula_cells": n, "with_stored_value": ncache, "formula_cells_in_year_columns": nyear})
with open(os.path.join(OUT, "step6_backups.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
