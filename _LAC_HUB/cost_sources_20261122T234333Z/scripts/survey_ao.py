"""Survey sheets of every live A-O workbook: sheet names, header, count of cost rows."""
import os, sys, openpyxl
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import ROOT, MODELS

COST = {"CapitalCost", "FixedCost", "VariableCost", "EmissionsPenalty"}
for m in MODELS:
    if not m.get("ao"):
        continue
    p = os.path.join(ROOT, m["ao"])
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    print("#####", m["cc"], m["model"], m["ao"])
    for ws in wb.worksheets:
        rows = ws.iter_rows(values_only=True)
        hdr = next(rows, None)
        if hdr is None:
            continue
        hdr = list(hdr)
        try:
            pi = hdr.index("Parameter")
        except ValueError:
            print("  ", ws.title, "(no Parameter col)", hdr[:10])
            continue
        c = Counter()
        for r in rows:
            if r and len(r) > pi and r[pi] in COST:
                c[r[pi]] += 1
        print("  ", ws.title, ws.max_row, "hdr:", [h for h in hdr[:10] if not isinstance(h, int)], dict(c))
