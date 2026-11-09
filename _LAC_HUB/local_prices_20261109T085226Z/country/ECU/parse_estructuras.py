"""Parse EP Petroecuador monthly terminal price structures (PRECIOS DE VENTA EN TERMINAL).

Usage: py -I parse_estructuras.py <folder_with_pdfs> <out_csv>
Writes one row per file, sector block, product: file, period_text, vat_pct, sector, product, unit, price_incl_vat.
"""
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pdfplumber

folder, out = sys.argv[1], sys.argv[2]
rows = []
line_re = re.compile(r"^(.*?)\s+(Galones|Kilogramos|Millón de BTUs|Millon de BTUs|Toneladas|Barriles)\s+\$\s*([0-9.,]+)\s*$")
for fn in sorted(os.listdir(folder)):
    if not fn.lower().endswith(".pdf"):
        continue
    with pdfplumber.open(os.path.join(folder, fn)) as d:
        text = "\n".join((p.extract_text() or "") for p in d.pages)
    period = ""
    m = re.search(r"PERIODO DE VIGENCIA:\s*(.*)", text)
    if m:
        period = m.group(1).strip()
    vat = ""
    sector = ""
    for ln in text.splitlines():
        ln = ln.strip()
        mv = re.search(r"Incluye el\s*(\d+)\s*%", ln)
        if mv:
            vat = mv.group(1)
        if ln.startswith("SECTOR") and "$" not in ln:
            sector = ln
            continue
        mm = line_re.match(ln)
        if mm:
            price = float(mm.group(3).replace(".", "").replace(",", "."))
            rows.append([fn, period, vat, sector, mm.group(1).strip(), mm.group(2), price])
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["file", "period_text", "vat_pct", "sector", "product", "unit", "price_incl_vat"])
    w.writerows(rows)
print(len(rows), "rows")
