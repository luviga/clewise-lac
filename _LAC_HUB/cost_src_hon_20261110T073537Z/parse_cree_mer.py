"""Electricity imports: parse the MER rows (contract and spot) of the CREE quarterly tariff reports
(Tabla 2 or 3, Costos reales de generacion) and sum them by calendar year. Writes cree_mer_monthly.csv.
A MER row is assigned to contracts or spot by the section total that follows it, and to a month by the
'Total <mes> <year>' line that closes the month."""
import re, csv
from pathlib import Path
import fitz
import pandas as pd

HERE = Path(__file__).parent
IMP = HERE / "downloads" / "imp"
MES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
       "septiembre": 9, "setiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
num = re.compile(r"^-?[\d,]+\.\d+$")
rows = {}
for f in sorted(IMP.glob("cree_Informe-*.pdf")):
    d = fitz.open(f)
    last = None
    cur = {}
    for i in range(d.page_count):
        L = [x.strip() for x in d[i].get_text().split("\n") if x.strip()]
        for j, l in enumerate(L):
            low = l.lower()
            if l == "MER":
                vals = []
                k = j + 1
                while k < len(L) and len(vals) < 5 and num.match(L[k]):
                    vals.append(float(L[k].replace(",", "")))
                    k += 1
                last = (vals, i + 1) if len(vals) >= 4 else None
            elif low.startswith("total transacciones de contratos"):
                if last:
                    cur["contract"] = last
                last = None
            elif low.startswith("total transacciones de oportunidad"):
                if last:
                    cur["spot"] = last
                last = None
            m = re.match(r"^Total (\w+) (\d{4})$", l, re.I)
            if m and m.group(1).lower() in MES:
                y, mo = int(m.group(2)), MES[m.group(1).lower()]
                for mk, (vals, pg) in cur.items():
                    key = (y, mo, mk)
                    if key not in rows:
                        rows[key] = dict(year=y, month=mo, market=mk, gwh=vals[0], capacity_usd=vals[1], energy_usd=vals[2],
                                         total_usd=vals[3], usd_mwh_printed=vals[4] if len(vals) > 4 else "",
                                         file=f.name, pdf_page=pg)
                cur = {}
                last = None
out = sorted(rows.values(), key=lambda r: (r["year"], r["month"], r["market"]))
with open(HERE / "cree_mer_monthly.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)
d = pd.DataFrame(out)
g = d.groupby("year").agg(months=("month", "nunique"), rows=("month", "count"), gwh=("gwh", "sum"), energy=("energy_usd", "sum"), total=("total_usd", "sum"))
g["usd_mwh_total"] = g.total / g.gwh / 1000
g["usd_mwh_energy"] = g.energy / g.gwh / 1000
print(g.round(3).to_string())
