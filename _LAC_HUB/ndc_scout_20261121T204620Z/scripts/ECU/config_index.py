"""Index the rows of B1_Scenario_Config.xlsx (read-only) for given scenarios.

Usage: python -I config_index.py <workbook> <out_txt> [SCEN ...]
Writes one line per row: sheet, row number, scenario, parameter, tech set, unit, multiplier,
and a short view of the exact years/values (values at 2025, 2030, 2035, 2050 when exact values exist).
"""
import sys

import openpyxl

wb_path, out = sys.argv[1], sys.argv[2]
scens = set(sys.argv[3:]) or {"BAU", "NDCNEW", "LTSNEW"}
wb = openpyxl.load_workbook(wb_path, read_only=True, data_only=True)
lines = []
for ws in wb.worksheets:
    header = None
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if i == 1:
            header = [str(c) if c is not None else "" for c in row]
            lines.append(f"## {ws.title} header: {header}")
            continue
        if not row or row[0] not in scens:
            continue
        d = dict(zip(header, row))
        ey, ev = d.get("Exact_Years"), d.get("Exact_Values")
        view = ""
        if isinstance(ey, str) and isinstance(ev, str) and ";" in ey:
            ys = [y.strip() for y in ey.split(";")]
            vs = [v.strip() for v in ev.split(";")]
            m = dict(zip(ys, vs))
            view = " ".join(f"{y}={m.get(y, '')}" for y in ["2025", "2030", "2035", "2040", "2050"])
        else:
            view = f"exact={ey}/{ev}"
        short = [str(c)[:30] for c in row[:4]]
        extra = {k: d.get(k) for k in ("y_ini", "Milestone_Years", "Milestone_Value", "Unit", "Security_Multiplier", "Method") if k in d}
        lines.append(f"{ws.title}\t{i}\t{short}\t{view}\t{extra}")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")
print(len(lines))
