"""Mean of Banco de Guatemala daily reference exchange rates (GTQ per USD).

Usage: py -I gua_fx.py <TipoCambioRango xml> [year]
The xml is the SOAP response of TipoCambioRango from
https://www.banguat.gob.gt/variables/ws/TipoCambio.asmx (moneda 2 = USD).
Prints the number of days, first and last date, mean of the reference rate
(the service returns the same value in <venta> and <compra>), and monthly means.
"""
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

NS = "{http://www.banguat.gob.gt/variables/ws/}"


def main(path, year=None):
    root = ET.parse(path).getroot()
    rows = []
    for var in root.iter(NS + "Var"):
        fecha = var.find(NS + "fecha").text
        venta = float(var.find(NS + "venta").text)
        compra = float(var.find(NS + "compra").text)
        d, m, y = fecha.split("/")
        if year and y != str(year):
            continue
        rows.append((y, m, d, venta, compra))
    n = len(rows)
    mean_v = sum(r[3] for r in rows) / n
    mean_c = sum(r[4] for r in rows) / n
    diff = sum(1 for r in rows if abs(r[3] - r[4]) > 1e-9)
    print(f"days={n} first={rows[0][2]}/{rows[0][1]}/{rows[0][0]} last={rows[-1][2]}/{rows[-1][1]}/{rows[-1][0]}")
    print(f"mean_venta={mean_v:.5f} mean_compra={mean_c:.5f} days_venta_ne_compra={diff}")
    by_m = defaultdict(list)
    for r in rows:
        by_m[r[1]].append(r[3])
    for m in sorted(by_m):
        v = by_m[m]
        print(f"month={m} days={len(v)} mean={sum(v)/len(v):.5f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
