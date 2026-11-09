"""Parse page 3 (PRECIOS SEMANALES) of the SEN/DGHB monthly hydrocarbon reports for 2024.

Usage: py -I parse_sen_monthly.py <dir_with_pdfs> <out_csv>
Writes one row per report, label and week with the weekly maximum consumer price (L/gal,
with tax) and the weekly operational exchange rate (L/USD) as printed on page 3.
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

FILES = [
    ("2024-01", "INE7E21.pdf"),
    ("2024-02", "INA14F1.pdf"),
    ("2024-03", "Informe-Estadistico-Mensual-de-Comercializacion-de-Hidrocarburos-e.pdf"),
    ("2024-04", "IN15221.pdf"),
    ("2024-05", "Informe-Estadistico-Mensual-de-Comercializacion-mes-de-MAYO-2024.pdf"),
    ("2024-06", "Informe-Estadistico-Mensual-de-Comercializacion-de-Hidrocarburos-en-Honduras-Junio-2024.pdf"),
    ("2024-07", "Informe-Estadistico-Mensual-de-Comercializacion-de-Hidrocarburos-en-Honduras-Julio-2024-1.pdf"),
    ("2024-08", "IEMCH-2024-08.pdf"),
    ("2024-09", "Informe-Estadistico-Mensual-de-Comercializacion-de-Hidrocarburos-en-Honduras-Septiembre-2024.pdf"),
    ("2024-10", "IEMCHB-10-2024.pdf"),
    ("2024-11", "IEMCHB-11-2024.pdf"),
    ("2024-12", "IEMCHB-12-2024.pdf"),
]

LABELS = {
    "Superior L/Gal": "GSL_superior",
    "Regular L/Gal": "GSL_regular",
    "Di�sel L/Gal": "DSL",
    "Diésel L/Gal": "DSL",
    "Kerosene L/Gal": "KER",
    "GLPV L/Gal": "LPG_vehicular",
    "GLP 25 lbs L/Cilindro": "LPG_25lb",
    "Semanal L/US$": "FX_operativa",
}
NUM = re.compile(r"^[L$]?(\d{1,3}(?:\.\d+)?)$")


def page_text(pdf, page):
    out = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"],
                         capture_output=True)
    return out.stdout.decode("latin-1")


def parse(text):
    tokens = [t.strip() for t in re.split(r"\n", text) if t.strip()]
    res = {}
    current = None
    for tok in tokens:
        hit = None
        for k, v in LABELS.items():
            if tok.endswith(k) or tok == k:
                hit = v
        if hit:
            current = hit
            res.setdefault(current, [])
            continue
        m = NUM.match(tok)
        if m and current:
            val = float(m.group(1))
            # week counters 1..5 are small integers without decimals; skip them
            if "." not in m.group(1) and val <= 5:
                continue
            res[current].append(val)
        elif tok.upper() in ("SEMANA",) or tok.startswith("Precios Semanales") or tok.startswith("Precio Mensual") or tok.startswith("Tasa de Cambio"):
            continue
        elif not m:
            current = current if tok in ("L/US$",) else current
    return res


def main():
    d = Path(sys.argv[1])
    rows = []
    for month, fn in FILES:
        res = parse(page_text(d / fn, 3))
        for lab, vals in res.items():
            for i, v in enumerate(vals, 1):
                rows.append({"month": month, "file": fn, "series": lab, "week_in_month": i, "value": v})
    with open(sys.argv[2], "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["month", "file", "series", "week_in_month", "value"])
        w.writeheader()
        w.writerows(rows)
    # summary
    from collections import defaultdict
    agg = defaultdict(list)
    for r in rows:
        agg[(r["month"], r["series"])].append(r["value"])
    for k in sorted(agg):
        print(k, agg[k])


if __name__ == "__main__":
    main()
