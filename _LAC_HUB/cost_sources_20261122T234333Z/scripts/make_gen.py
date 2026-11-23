"""Build sources_GEN.csv (GEN-001 US CPI-U from BLS) and cpi_u.csv (factor to real 2024 USD)."""
import os, sys, csv, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import JOB

vals = {}
files = ["bls_CUUR0000SA0_2005_2014_annualaverage.json", "bls_CUUR0000SA0_2015_2024_annualaverage.json",
         "bls_CUUR0000SA0_2016_2025_annualaverage.json"]
for f in files:
    j = json.load(open(os.path.join(JOB, "downloads", "GEN", f)))
    for d in j["Results"]["series"][0]["data"]:
        if d["period"] == "M13":
            vals[int(d["year"])] = float(d["value"])
table = "; ".join("%d=%s" % (y, ("%g" % vals[y])) for y in sorted(vals))
rows = [dict(id="GEN-001",
             url="https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2005&endyear=2014&annualaverage=true (and startyear=2015&endyear=2024, startyear=2016&endyear=2025)",
             title="Consumer Price Index for All Urban Consumers (CPI-U), All items in U.S. city average, not seasonally adjusted, series CUUR0000SA0, annual averages",
             publisher="U.S. Bureau of Labor Statistics", date="data as published to 2026-11", retrieval_date="2026-11-22",
             downloaded_file="downloads/GEN/" + files[0] + "; downloads/GEN/" + files[1] + "; downloads/GEN/" + files[2],
             page_or_table="JSON Results.series[0].data, records with period M13 (Annual)",
             notes="CPI-U annual average, index 1982-84=100: " + table + ". Factor to real 2024 USD = CPI(2024) / CPI(source year).")]
with open(os.path.join(JOB, "sources_GEN.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
    w.writeheader(); w.writerows(rows)
with open(os.path.join(JOB, "cpi_u.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["year", "cpi_u_annual_average", "factor_to_2024", "source_id"])
    for y in sorted(vals):
        w.writerow([y, "%g" % vals[y], "%.6f" % (vals[2024] / vals[y]), "GEN-001"])
print(table)
