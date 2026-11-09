"""Monthly and annual unit import values from MEM (DGH) import cost and volume workbooks.

Usage: py -I gua_mem_imports.py <COSTO-IMPORTACION xlsx> <IMPORTACION-VOLUMEN xlsx> [first_year last_year]
Cost workbook unit: USD. Volume workbook unit: barrel (42 US gallons).
Prints, for each product present in both workbooks, monthly cost, volume and USD/bbl
for 2024, then annual totals and annual unit values (sum of cost / sum of volume)
for each year in the range.
"""
import sys
import datetime as dt
import openpyxl

SPANISH_MONTHS = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
                  "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11,
                  "diciembre": 12}


def norm(s):
    return " ".join(str(s).replace("\n", " ").split()).strip().lower()


def parse_date(v):
    if isinstance(v, dt.datetime):
        return v.year, v.month
    if isinstance(v, str):
        parts = v.split()
        if len(parts) == 2 and parts[0].lower() in SPANISH_MONTHS:
            return int(parts[1]), SPANISH_MONTHS[parts[0].lower()]
    return None


def read(path):
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    hdr_i = next(i for i, r in enumerate(rows) if r[0] in ("Mes", "Fecha"))
    hdr = [norm(x) if x is not None else None for x in rows[hdr_i]]
    data = {}
    for r in rows[hdr_i + 1:]:
        ym = parse_date(r[0])
        if not ym:
            continue
        for j, h in enumerate(hdr[1:], start=1):
            if h is None:
                continue
            v = r[j]
            try:
                v = float(v)
            except (TypeError, ValueError):
                v = 0.0
            data.setdefault(h, {})[ym] = v
    return data


ALIASES = {"bunker c o fuel oil": "bunker"}


def main(cost_path, vol_path, y0=2018, y1=2024):
    cost = {ALIASES.get(k, k): v for k, v in read(cost_path).items()}
    vol = read(vol_path)
    prods = [p for p in cost if p in vol and p not in ("total", "total importación")]
    print("products in both:", prods)
    for p in prods:
        print(f"\n## {p} monthly 2024 (USD, bbl, USD/bbl)")
        for m in range(1, 13):
            c = cost[p].get((2024, m), 0.0)
            v = vol[p].get((2024, m), 0.0)
            uv = c / v if v else float("nan")
            print(f"2024-{m:02d}\t{c:.2f}\t{v:.2f}\t{uv:.4f}")
        for y in range(y0, y1 + 1):
            cs = sum(cost[p].get((y, m), 0.0) for m in range(1, 13))
            vs = sum(vol[p].get((y, m), 0.0) for m in range(1, 13))
            nm = sum(1 for m in range(1, 13) if vol[p].get((y, m), 0.0) > 0)
            uv = cs / vs if vs else float("nan")
            print(f"annual\t{p}\t{y}\tcost_usd={cs:.2f}\tvol_bbl={vs:.2f}\tmonths_with_volume={nm}\tusd_per_bbl={uv:.4f}")


if __name__ == "__main__":
    a = sys.argv
    if len(a) > 4:
        main(a[1], a[2], int(a[3]), int(a[4]))
    else:
        main(a[1], a[2])
