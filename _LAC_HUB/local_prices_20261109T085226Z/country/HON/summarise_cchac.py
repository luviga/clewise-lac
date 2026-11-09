"""Summarise the CCHAC Honduras values parsed by parse_cchac.py and parse_cchac_glp.py.

Usage: py -I summarise_cchac.py <cchac_hon_2024.csv> <cchac_hon_glp_2024.csv> <out_dir>
Adds the values read from images (bulletins 1, 30, 31) and writes weekly wide tables and
means. Bulletin 1 bars were misread by the text parser and are replaced by the image reading.
"""
import re
import sys
from pathlib import Path

import pandas as pd

# Read from rendered page images (downloads/HON/cchac/png), USD per gallon.
IMAGE_VALUES = [
    # week, series, pre_tax, tax, total
    ("31 diciembre 2023 al 06 enero 2024", "GSL_superior", 3.08, 0.99, 4.07),
    ("31 diciembre 2023 al 06 enero 2024", "GSL_regular", 2.81, 0.83, 3.64),
    ("31 diciembre 2023 al 06 enero 2024", "DSL", 3.15, 0.45, 3.60),
    ("21 al 27 de julio 2024", "GSL_superior", 3.36, 0.99, 4.35),
    ("21 al 27 de julio 2024", "GSL_regular", 2.93, 0.83, 3.76),
    ("21 al 27 de julio 2024", "DSL", 3.20, 0.45, 3.65),
    ("28 de julio al 03 de agosto 2024", "GSL_superior", 3.36, 0.99, 4.35),
    ("28 de julio al 03 de agosto 2024", "GSL_regular", 2.95, 0.83, 3.78),
    ("28 de julio al 03 de agosto 2024", "DSL", 3.19, 0.45, 3.64),
]

GLP_MAP = [("Precio FOB", "fob"), ("Transporte Terrestre", "inland_freight"), ("Flete", "freight"), ("Seguro", "insurance"),
           ("Operaci", "terminal"), ("Cargo Portuario", "port"), ("CIF+", "cif_plus_ppi"),
           ("Importador", "importer_margin"), ("Envasador", "envasador"),
           ("Margen Distribuidor", "distributor_margin"),
           ("Comercializador", "retail_margin"), ("Mantenimiento", "cylinder_maintenance"),
           ("Impuesto Otros", "tax")]


def glp_comp(s):
    s = str(s)
    for k, v in GLP_MAP:
        if k in s:
            return v
    if s.strip().startswith("Márgenes") and "Distribuidor" not in s:
        return "margins_total"
    return None


def num(s):
    m = re.findall(r"\$\s*(\d+[.,]\d+)", str(s))
    return float(m[0].replace(",", ".")) if m else None


def main():
    out = Path(sys.argv[3])
    b = pd.read_csv(sys.argv[1])
    b = b[(b.series != "LPG_25lb") & (~b.week.astype(str).str.startswith("31 diciembre"))]
    w = b.pivot_table(index=["file", "week"], columns=["series", "component"], values="value_usd",
                      aggfunc="first")
    w.columns = [f"{a}_{c}" for a, c in w.columns]
    w = w.reset_index()
    rows = []
    for week, s, pre, tax, tot in IMAGE_VALUES:
        rows.append({"file": "image", "week": week, f"{s}_pre_tax": pre, f"{s}_tax": tax, f"{s}_total": tot})
    img = pd.DataFrame(rows).groupby(["file", "week"], as_index=False).first()
    w = pd.concat([w, img], ignore_index=True)
    w.to_csv(out / "cchac_hon_liquids_weekly.csv", index=False)
    print(len(w), "weeks")
    print(w.drop(columns=["file", "week"]).mean().round(4).to_string())

    g = pd.read_csv(sys.argv[2])
    g["comp"] = g.row_label.map(glp_comp)
    g["v"] = g.honduras_column_text.map(num)
    g = g[g.comp.notna() & g.v.notna()]
    gw = g.pivot_table(index=["file", "week"], columns="comp", values="v", aggfunc="first").reset_index()
    gw.to_csv(out / "cchac_hon_glp_weekly.csv", index=False)
    print(len(gw), "LPG weeks")
    print(gw.drop(columns=["file", "week"]).agg(["count", "mean"]).round(4).T.to_string())


if __name__ == "__main__":
    main()
