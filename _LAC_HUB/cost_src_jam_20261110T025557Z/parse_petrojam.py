"""Parse the saved Petrojam weekly price listing pages (J$ per litre) and summarise 2024 by product."""
import re, html, csv, datetime as dt
from pathlib import Path
HERE = Path(__file__).parent
SRC = HERE / "downloads" / "petrojam"
rows = {}
for p in sorted(SRC.glob("petrojam_price_p*.html")):
    t = p.read_text(encoding="utf-8", errors="replace")
    i = t.find("PETROLEUM PRODUCT PRICES")
    seg = t[i:]
    j = seg.find("wpv-filter-pagination"); seg = seg[:j] if j > 0 else seg
    txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", seg)))
    hdr = re.search(r"Date (.*?) (?=[A-Z][a-z]+ \d{1,2}, \d{4})", txt).group(1)
    for m in re.finditer(r"([A-Z][a-z]+ \d{1,2}, \d{4})((?: -?[\d.]+){9})", txt):
        d = dt.datetime.strptime(m.group(1), "%B %d, %Y").date()
        vals = [float(x) for x in m.group(2).split()]
        rows[d] = (p.name, vals)
cols = ["Gasolene 87","Gasolene 90","Auto Diesel","Kerosene","Propane","Butane","HFO","Asphalt","ULSD"]
with open(HERE / "petrojam_weekly.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["date","page_file"] + cols)
    for d in sorted(rows): w.writerow([d.isoformat(), rows[d][0]] + rows[d][1])
print("header seen:", hdr)
ds = sorted(rows); print("dates", ds[0], ds[-1], len(ds))
for y in (2023, 2024, 2025):
    yd = [d for d in ds if d.year == y]
    if not yd: continue
    gaps = [(a, b) for a, b in zip(yd, yd[1:]) if (b - a).days != 7]
    means = [sum(rows[d][1][k] for d in yd) / len(yd) for k in range(9)]
    print(y, len(yd), yd[0], yd[-1], "gaps:", gaps)
    print("   ", dict(zip(cols, [round(m, 3) for m in means])))
