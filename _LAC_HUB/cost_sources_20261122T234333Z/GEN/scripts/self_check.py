"""Self-check of the GEN sector outputs."""
import os, csv, re
HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.dirname(HERE)
JOB = os.path.dirname(GEN)
problems = []
src = {r["id"]: r for r in csv.DictReader(open(os.path.join(GEN, "sources_GEN_sector.csv"), encoding="utf-8"))}
gen0 = {r["id"] for r in csv.DictReader(open(os.path.join(JOB, "sources_GEN.csv"), encoding="utf-8"))}
for sid, r in src.items():
    for f in r["downloaded_file"].split(";"):
        f = f.strip()
        if not f.startswith("downloads/") or not os.path.exists(os.path.join(JOB, f)):
            problems.append(f"{sid}: missing file {f}")
    if re.search(r"readthedocs|clg|file:|/c/", r["url"], re.I):
        problems.append(f"{sid}: forbidden url")
for r in csv.DictReader(open(os.path.join(GEN, "gen_sector_values.csv"), encoding="utf-8")):
    if r["value"] != "":
        for s in r["source_id"].split(";"):
            if s not in src and s not in gen0:
                problems.append(f"value row {r['tech']} {r['parameter']}: unknown source {s}")
        if r["source_currency_year"] and not r["cpi_factor"]:
            problems.append(f"value row {r['tech']}: missing cpi factor")
MINE = [f for f in os.listdir(GEN) if f.startswith(("faostat_", "gen_sector")) or f.endswith("_GEN_sector.csv") or f == "notes_GEN_sector.md"]
for fn in MINE:
    p = os.path.join(GEN, fn)
    if os.path.isfile(p):
        b = open(p, "rb").read()
        t = b.decode("utf-8")
        if chr(0x2014) in t: problems.append(f"{fn}: em dash")
        if b"\r\n" in b: problems.append(f"{fn}: CRLF")
        pat = r"/c/clw|clw_costsrc" if fn.startswith("search_log") else r"/c/clw|clw_costsrc|readthedocs[.]io/"
        if re.search(pat, t):
            problems.append(f"{fn}: machine path or readthedocs url")
for fn in ["faostat_trade_unit_values.csv", "faostat_producer_prices.csv", "faostat_yields.csv"]:
    n = sum(1 for _ in open(os.path.join(GEN, fn), encoding="utf-8")) - 1
    print(fn, n, "rows")
print("PROBLEMS:", problems if problems else "none")
