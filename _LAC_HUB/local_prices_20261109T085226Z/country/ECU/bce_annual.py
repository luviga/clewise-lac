"""Annual volume-weighted values from BCE Cifras del Sector Petrolero (SerieCifrasPetroleras.xlsx, sheet Petroleo).

Usage: py -I bce_annual.py <xlsx> <out_csv>
For each year 2018-2025 sums monthly volume (kbbl) and value (kUSD) for:
  crude exports total (rows 94 volume, 96 value),
  crude exports public companies Oriente/Napo prices (rows 107, 108, simple mean only for reference),
  Fuel Oil No. 6 exports (rows 120 volume, 121 price; value = volume x price),
  imports: nafta de alto octano (141, 143), diesel (148, 150), GLP (155, 157),
  domestic sale (ingreso venta interna) for imported products: nafta (144 price, 145 income), diesel (151, 152), GLP (158, 159).
Rows are located by label text, not by fixed index, and the label row number is written out.
"""
import csv
import sys

import openpyxl

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
xlsx, out = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
ws = wb.worksheets[0]
rows = list(ws.iter_rows(values_only=True))

# Header: row 2 years (only first month of each year filled), row 3 months
years_row, months_row = rows[1], rows[2]
col_year = {}
cur = None
for j, (y, m) in enumerate(zip(years_row, months_row)):
    if isinstance(y, (int, float)) and y > 1990:
        cur = int(y)
    if cur and isinstance(m, str) and m.strip():
        col_year[j] = (cur, m.strip())


def label(i):
    r = rows[i]
    for c in r[:3]:
        if isinstance(c, str) and c.strip():
            return c.strip()
    return ""


def find(start_text, after=0):
    for i in range(after, len(rows)):
        if label(i).lower().startswith(start_text.lower()):
            return i
    raise KeyError(start_text)


def series(i):
    d = {}
    for j, (y, m) in col_year.items():
        v = rows[i][j] if j < len(rows[i]) else None
        if isinstance(v, (int, float)):
            d.setdefault(y, []).append((m, float(v)))
    return d


res = []
i_tot = find("TOTAL EXPORTACIONES DE PETR")
i_px = i_tot + 1
i_inc = i_tot + 2
i_fo6v = find("Exportaciones de Fuel oil # 6")
i_fo6p = i_fo6v + 1
i_naf = find("Nafta Alto Octano", find("COMERCIALIZACI"))
i_dsl = find("Diésel", i_naf + 1)
i_glp = find("Gas Licuado", i_dsl + 1)
specs = [
    ("crude_export_total", i_tot, i_inc, None),
    ("fo6_export", i_fo6v, None, i_fo6p),
]
for name, base in (("nafta_import", i_naf), ("diesel_import", i_dsl), ("glp_import", i_glp)):
    specs.append((name, base + 2, base + 4, None))  # volume, cost
for name, base in (("nafta_domestic_sale", i_naf), ("diesel_domestic_sale", i_dsl), ("glp_domestic_sale", i_glp)):
    specs.append((name, base + 2, base + 6, None))  # imported volume, domestic sale income

for name, iv, ival, iprice in specs:
    vol = series(iv)
    val = series(ival) if ival is not None else None
    pr = series(iprice) if iprice is not None else None
    for y in range(2018, 2026):
        vols = dict(vol.get(y, []))
        if val is not None:
            vals = dict(val.get(y, []))
        else:
            prs = dict(pr.get(y, []))
            vals = {m: vols[m] * prs[m] for m in vols if m in prs}
        months = sorted(set(vols) & set(vals))
        V = sum(vols[m] for m in months)
        X = sum(vals[m] for m in months)
        res.append([name, y, len(months), label(iv), iv + 1, (label(ival) if ival is not None else label(iprice)),
                    (ival if ival is not None else iprice) + 1, round(V, 3), round(X, 3), round(X / V, 4) if V else ""])
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["series", "year", "months", "volume_label", "volume_row", "value_label", "value_row", "volume_kbbl", "value_kusd", "usd_per_bbl"])
    w.writerows(res)
for r in res:
    print(r)
