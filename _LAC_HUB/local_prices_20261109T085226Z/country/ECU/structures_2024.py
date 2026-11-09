"""Day-weighted calendar-2024 averages of EP Petroecuador terminal prices, excluding VAT.

Usage: py -I structures_2024.py <estructuras_parsed.csv> <out_csv>

Each monthly structure file is valid from the 12th of its month to the 11th of the next month
(stated in each file as PERIODO DE VIGENCIA). Days of calendar 2024 (1 Jan to 31 Dec, 366 days)
are assigned to the file in force. The price excluding VAT is price_incl_vat / (1 + vat_pct/100),
with vat_pct as printed in the file header for the block holding the product.
Output: product, unit, days covered, months list, mean incl VAT, mean excl VAT, min and max excl VAT.
"""
import csv
import datetime as dt
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src, out = sys.argv[1], sys.argv[2]
d = pd.read_csv(src)
MONTHS = {"ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6, "JULIO": 7,
          "AGOSTO": 8, "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12}


def file_start(fn):
    stem = fn.replace("EPP_ESTRUCTURA-DE-PRECIOS-", "").replace(".pdf", "")
    mon, yr = stem.split("-")
    return dt.date(int(yr), MONTHS[mon], 12)


ALIASES = {
    "DIESEL 2 / DIESEL PREMIUM (AUTOMOTRIZ)": "DIESEL PREMIUM (AUTOMOTRIZ)",
}
d["product_std"] = d["product"].map(lambda p: ALIASES.get(p, p))
# keep first occurrence per file and product (some products repeat in the naviero internacional block)
d = d.drop_duplicates(["file", "product_std"], keep="first")
files = sorted(set(d["file"]), key=file_start)
starts = [file_start(f) for f in files]
day_file = {}
day = dt.date(2024, 1, 1)
while day <= dt.date(2024, 12, 31):
    cur = None
    for f, s in zip(files, starts):
        if s <= day:
            cur = f
    day_file[day] = cur
    day += dt.timedelta(days=1)

products = sorted(set(d["product_std"]))
rows = []
for p in products:
    sub = d[d["product_std"] == p].set_index("file")
    vals_in, vals_ex, used = [], [], []
    for day, f in day_file.items():
        if f in sub.index:
            r = sub.loc[f]
            pin = float(r["price_incl_vat"])
            vat = float(r["vat_pct"])
            if pin <= 0:
                continue
            vals_in.append(pin)
            vals_ex.append(pin / (1 + vat / 100.0))
            used.append(f)
    if not vals_ex:
        continue
    unit = sub["unit"].iloc[0]
    flist = sorted(set(used), key=file_start)
    rows.append([p, unit, len(vals_ex), ";".join(x.replace("EPP_ESTRUCTURA-DE-PRECIOS-", "").replace(".pdf", "") for x in flist),
                 round(sum(vals_in) / len(vals_in), 6), round(sum(vals_ex) / len(vals_ex), 6),
                 round(min(vals_ex), 6), round(max(vals_ex), 6)])
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["product", "unit", "days_2024", "structure_files", "mean_incl_vat", "mean_excl_vat", "min_excl_vat", "max_excl_vat"])
    w.writerows(rows)
for r in rows:
    print(r[0], "|", r[1], "|", r[2], "|", r[4], "|", r[5], "|", r[6], "|", r[7])
