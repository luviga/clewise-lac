"""Step 6 evidence for Ecuador: the 451 year-column formula cells in the pre-patch backup
A-O_Parametrization_BACKUP_20260514_111921.xlsx. For each, what does the current A-O hold in the same cell
(a number, empty, or a formula) and does it equal the backup's stored value? Read-only."""
import os, csv
from openpyxl import load_workbook
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
OUT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, r"Ecuador\ECU_Energy\A1_Outputs")
bf = load_workbook(os.path.join(A, "A-O_Parametrization_BACKUP_20260514_111921.xlsx"))
bv = load_workbook(os.path.join(A, "A-O_Parametrization_BACKUP_20260514_111921.xlsx"), data_only=True)
cf = load_workbook(os.path.join(A, "A-O_Parametrization.xlsx"))
rows = []
for ws in bf.worksheets:
    hdr = {c.column: c.value for c in ws[1] if c.value is not None}
    cols = {str(v): k for k, v in hdr.items()}
    for r in ws.iter_rows(min_row=2):
        for c in r:
            if c.data_type != "f" or not isinstance(hdr.get(c.column), int): continue
            cur = cf[ws.title][c.coordinate]; old = bv[ws.title][c.coordinate].value
            tech = ws.cell(c.row, cols["Tech"]).value if "Tech" in cols else None
            par = ws.cell(c.row, cols["Parameter"]).value if "Parameter" in cols else None
            cur_tech = cf[ws.title].cell(c.row, cols["Tech"]).value if "Tech" in cols else None
            cv = cur.value
            same = (isinstance(cv, (int, float)) and isinstance(old, (int, float)) and abs(cv - old) <= 1e-9 * max(1, abs(old)))
            rows.append({"sheet": ws.title, "cell": c.coordinate, "tech_backup": tech, "tech_current": cur_tech, "parameter": par,
                         "year": hdr[c.column], "backup_formula": c.value, "backup_stored_value": old,
                         "current_type": cur.data_type, "current_value": cv, "current_equals_backup_stored": same})
with open(os.path.join(OUT, "step6_ecuador_451.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
import collections
print(len(rows), collections.Counter((r["sheet"], r["parameter"], r["current_type"], r["current_equals_backup_stored"]) for r in rows))
print(collections.Counter(r["tech_backup"] for r in rows))
print(sum(r["tech_backup"] != r["tech_current"] for r in rows), "rows where tech differs")
