"""Step 5.4 gate: every value of the solved data files (Executables/{scenario}_FINAL_0) for years up to
history_end_year is equal across BAU, NDC and LTS, in every energy model. Writes history_identity.csv (country,
parameter, slice, row, year, BAU, NDC, LTS) with one row per difference, and prints the counts.
An upper bound of OPEN or more (TotalAnnualMaxCapacity, activity upper limits, emission limits) is no limit: two such
values are equal (the Stage 3 writer opens a missing BAU row with 99999, the policy rows carry the block default).
Usage: python -I history_identity.py [root]"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else M.ROOT
sys.path.insert(0, str(M.ROOT))
import lac_tables as LT  # noqa: E402
import scenario_rules as SR  # noqa: E402

last = LT.controller('history_end_year')
scen = LT.scenarios()
OPEN = 99999.0
UPPER = ('TotalAnnualMaxCapacity', 'TotalAnnualMaxCapacityInvestment', 'TotalTechnologyAnnualActivityUpperLimit',
         'TotalTechnologyModelPeriodActivityUpperLimit', 'AnnualEmissionLimit', 'ModelPeriodEmissionLimit')
rows, n_cells, n_open = [], 0, 0
for c in LT.countries():
    ex = root / Path(*LT.model_path(c).split('/')) / 'Executables'
    data = {}
    for s in scen:
        p = ex / f'{s}_FINAL_0' / f'{s}_FINAL_0.txt'
        if not p.exists():
            continue
        txt = p.read_text(encoding='utf-8', errors='replace').replace('\r\n', '\n')
        vals = {}
        for param, (a, b, d) in SR.blocks(txt).items():
            for sl, yrs, rws in SR.parse_block(txt[a:b]):
                for k, v in rws.items():
                    for y, x in zip(yrs, v):
                        if y <= last:
                            vals[(param, sl, k, y)] = float(x)
        data[s] = (vals, {p: d for p, (a, b, d) in SR.blocks(txt).items()})
    if len(data) < 2:
        continue
    keys = set().union(*(v[0].keys() for v in data.values()))
    for k in sorted(keys):
        n_cells += 1
        got = [data[s][0].get(k, data[s][1].get(k[0], 0.0)) for s in scen if s in data]
        if max(got) - min(got) > 1e-9 * (1 + max(abs(g) for g in got)):
            if k[0] in UPPER and min(got) >= OPEN:
                n_open += 1
                continue
            rows.append([c, k[0], k[1], k[2], k[3]] + got)
with open(M.JOB / 'history_identity.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['country', 'parameter', 'slice', 'row', 'year'] + scen)
    w.writerows(rows)
print(n_cells, 'history cells compared;', len(rows), 'differences;', n_open, 'open upper bounds written as 99999 in one scenario and as the block default in another')
