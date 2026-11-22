"""Compact headline tables for the report: from parts/headlines.md keep economy-wide and energy
emission targets, renewable shares of generation and capacities; drop fleet, blend and loss rows."""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB

keep_kw = re.compile(r"share of [A-Za-z ]*generation|renewable share|capacity|against BAU|net emissions|net GHG|sector emissions|emission level|emissions in 20|clean share", re.I)
drop_kw = re.compile(r"vehicle|fleet|\bbus|blend|ethanol|loss|storage|distributed|self-gen|cumulative|per year|annual", re.I)
out = []
for line in open(os.path.join(JOB, "parts", "headlines.md"), encoding="utf-8"):
    l = line.rstrip("\n")
    if l.startswith("| ") and not l.startswith("| Scen."):
        cells = [c.strip() for c in l.split("|")]
        what = cells[3] if len(cells) > 3 else ""
        if not keep_kw.search(what) or drop_kw.search(what):
            continue
    out.append(l)
open(os.path.join(JOB, "parts", "headlines_compact.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print(len(out))
