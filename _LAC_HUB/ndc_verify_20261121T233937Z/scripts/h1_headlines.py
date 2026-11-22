"""Headline tables for the report: per country, the economy-wide, energy, renewable, capacity, vehicle,
blend and loss values of scenario_values.csv with the model quantity of model_comparison.csv.
Writes parts/headlines.md and parts/counts.md.
"""
import collections
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, CODES, COUNTRY, read_csv

sv = read_csv(os.path.join(JOB, "scenario_values.csv"))
mc = {r["value_id"]: r for r in read_csv(os.path.join(JOB, "model_comparison.csv"))}


def headline(r):
    k = r["kind_of_quantity"]
    lv = r["lever"].lower()
    if k == "share of generation":
        return True
    if k in ("capacity", "blend", "losses", "vehicles"):
        return True
    if k == "emissions" and ("economy-wide" in lv or lv.startswith("energy")) and not re.search(r"cumulative|per year|annual", lv) \
            and "projected" not in lv:
        return True
    return False


out = []
for code in CODES:
    rows = [r for r in sv if r["country"] == COUNTRY[code] and r["value_id"] and headline(r)]
    out.append(f"\n### {COUNTRY[code]}\n")
    if not rows:
        out.append("No headline rows.\n")
        continue
    out.append("| Scen. | Value id | What | Year | Document (standard) | Model NDCNEW 2030 / 2035 / 2050 | Model LTSNEW 2035 / 2050 | Same kind |")
    out.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        m = mc[r["value_id"]]
        what = re.sub(r"^[^:]+: ", "", r["lever"])[:60]
        sk = m["same_kind"].split(":")[0]
        nd = " / ".join(m[f"NDCNEW_{y}"] or "-" for y in (2030, 2035, 2050)) if sk not in ("different quantity", "not compared", "not computed") else "-"
        lt = " / ".join(m[f"LTSNEW_{y}"] or "-" for y in (2035, 2050)) if sk not in ("different quantity", "not compared", "not computed") else "-"
        out.append(f"| {r['scenario']} | {r['value_id']} | {what} | {r['year']} | {r['value_standard']} {r['unit_standard']} ({r['conditionality']}) | {nd} {m['model_unit'] if nd != '-' else ''} | {lt} | {sk} |")
open(os.path.join(JOB, "parts", "headlines.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")

# counts
lines = ["| Country | Values | 3 of 3 | 2 of 3 | conflict |", "|---|---|---|---|---|"]
tot = collections.Counter()
for code in CODES:
    c = collections.Counter(r["status"] for r in read_csv(os.path.join(JOB, f"verification_{code}.csv")))
    n = sum(c.values())
    tot.update(c)
    tot["n"] += n
    lines.append(f"| {COUNTRY[code]} | {n} | {c['3 of 3']} | {c['2 of 3']} | {c['conflict']} |")
lines.append(f"| All | {tot['n']} | {tot['3 of 3']} | {tot['2 of 3']} | {tot['conflict']} |")
miss = collections.Counter()
for code in CODES:
    for r in read_csv(os.path.join(JOB, f"verification_{code}.csv")):
        if r["status"] == "2 of 3":
            miss[(code, r["status_note"].split(":")[0])] += 1
lines.append("\nMissing check among the 2 of 3 rows:\n")
lines.append("| Country | missing check 2 | missing check 3 |")
lines.append("|---|---|---|")
for code in CODES:
    lines.append(f"| {COUNTRY[code]} | {miss[(code, 'missing check 2')]} | {miss[(code, 'missing check 3')]} |")
open(os.path.join(JOB, "parts", "counts.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print("\n".join(lines))
