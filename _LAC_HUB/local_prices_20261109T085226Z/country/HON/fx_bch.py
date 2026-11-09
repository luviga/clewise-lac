"""Annual means of the BCH daily reference rate (Precio Promedio del Dolar, Compra and Venta).

Usage: py -I fx_bch.py <BCH_Precio_Promedio_Diario_del_Dolar.xlsx> <out_csv>
Mean of all daily observations in each calendar year 2018 to 2025 (monthly average rows,
whose first cell is text, are skipped).
"""
import csv
import datetime as dt
import sys
from collections import defaultdict

import openpyxl


def main():
    wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
    ws = wb.worksheets[0]
    comp, vent = defaultdict(list), defaultdict(list)
    for r in ws.iter_rows(values_only=True):
        d = r[0]
        if isinstance(d, dt.datetime) and isinstance(r[1], (int, float)):
            comp[d.year].append(float(r[1]))
            if isinstance(r[2], (int, float)):
                vent[d.year].append(float(r[2]))
    with open(sys.argv[2], "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "n_days", "mean_compra", "mean_venta", "mean_mid"])
        for y in range(2018, 2026):
            c, v = comp[y], vent[y]
            mc = sum(c) / len(c)
            mv = sum(v) / len(v)
            w.writerow([y, len(c), round(mc, 4), round(mv, 4), round((mc + mv) / 2, 4)])
            print(y, len(c), round(mc, 4), round(mv, 4))


if __name__ == "__main__":
    main()
