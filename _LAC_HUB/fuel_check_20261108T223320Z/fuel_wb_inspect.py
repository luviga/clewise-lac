"""Step 3.1: list every sheet of the fuel workbook with size, formula count, and a preview."""
import sys
from openpyxl import load_workbook
p = sys.argv[1]
wf = load_workbook(p, data_only=False)
wv = load_workbook(p, data_only=True)
for ws in wf.worksheets:
    vs = wv[ws.title]
    nform = 0; nval = 0; cached_missing = 0
    for row in ws.iter_rows():
        for c in row:
            if c.value is None: continue
            nval += 1
            if c.data_type == 'f' or (isinstance(c.value, str) and c.value.startswith('=')):
                nform += 1
                if vs[c.coordinate].value is None: cached_missing += 1
    print(f"\n##### SHEET '{ws.title}' dims={ws.dimensions} max_row={ws.max_row} max_col={ws.max_column} nonempty={nval} formulas={nform} formulas_without_cached_value={cached_missing}")
    for r in vs.iter_rows(min_row=1, max_row=min(ws.max_row, int(sys.argv[2]) if len(sys.argv)>2 else 8), values_only=True):
        print("  ", [x for x in r[:30]])
