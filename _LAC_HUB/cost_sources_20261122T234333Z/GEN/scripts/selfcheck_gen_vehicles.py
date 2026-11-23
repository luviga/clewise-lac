"""Self-check for the GEN vehicle package."""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.dirname(HERE)
JOB = os.path.dirname(GEN)
problems = []


def read(name):
    with open(os.path.join(GEN, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


files = ["gen_vehicle_factors.csv", "sources_GEN_vehicles.csv", "search_log_GEN_vehicles.csv",
         "manual_downloads_GEN_vehicles.csv", "notes_GEN_vehicles.md"]
for fn in files:
    raw = open(os.path.join(GEN, fn), "rb").read()
    if b"\r\n" in raw:
        problems.append(f"{fn}: CRLF line endings")
    txt = raw.decode("utf-8")
    if "\u2014" in txt:
        problems.append(f"{fn}: em dash")
    for bad in ["readthedocs.io", "C:\\", "/c/", "clw_", "Dropbox"]:
        if bad in txt and fn not in ("search_log_GEN_vehicles.csv", "notes_GEN_vehicles.md"):
            problems.append(f"{fn}: contains {bad}")
    if fn == "notes_GEN_vehicles.md":
        for bad in ["C:\\", "/c/", "clw_"]:
            if bad in txt:
                problems.append(f"{fn}: machine path {bad}")

src = read("sources_GEN_vehicles.csv")
ids = {r["id"] for r in src}
for r in src:
    for p in r["downloaded_file"].split(";"):
        p = p.strip()
        if not p.startswith("downloads/") or not os.path.exists(os.path.join(JOB, p)):
            problems.append(f"{r['id']}: downloaded_file missing {p}")
    if re.search(r"readthedocs|github\.com/clg|EPERLab", r["url"], re.I):
        problems.append(f"{r['id']}: forbidden url")

fac = read("gen_vehicle_factors.csv")
cols = "item,vehicle_class,powertrain,year,value,unit,source_currency_year,value_2024usd,cpi_factor,source_id,page_or_table,derivation".split(",")
if list(fac[0].keys()) != cols:
    problems.append("factor columns differ")
for i, r in enumerate(fac):
    for s in r["source_id"].split(";"):
        if s.strip() not in ids:
            problems.append(f"row {i}: unknown source {s}")
    if r["unit"].startswith(("US$", "M US$")) and (not r["cpi_factor"] or not r["source_currency_year"] or not r["value_2024usd"]):
        problems.append(f"row {i}: currency row without cpi data")
    if not r["derivation"]:
        problems.append(f"row {i}: empty derivation")

# trajectory completeness: 2024..2050, ratio 1 in 2024
traj = {}
for r in fac:
    if r["item"] == "price_trajectory":
        traj.setdefault((r["vehicle_class"], r["powertrain"]), {})[int(r["year"])] = float(r["value"])
for k, v in traj.items():
    if sorted(v) != list(range(2024, 2051)) or abs(v[2024] - 1) > 1e-9:
        problems.append(f"trajectory {k} incomplete or not 1 in 2024")

print("rows:", len(fac), "trajectory series:", len(traj), "sources:", sorted(ids))
print("PASS" if not problems else "FAIL:\n" + "\n".join(problems))
