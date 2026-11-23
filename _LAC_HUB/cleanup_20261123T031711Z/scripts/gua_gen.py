"""Solar, wind and total power generation of one country before and after, from two snapshots of the Stage 3 results.

Power plants are the technologies with the power plant prefix of the tables; solar and wind plants are those whose
name holds a solar_wind_token of config/scenarios/technology_types.csv (a token that starts with W is wind, the
others solar). Values are TotalTechnologyAnnualActivity in PJ.
Usage: python gua_gen.py <snapA> <snapB> <country> <out.csv> [year ...]
"""
import csv
import sys
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import machine as M  # noqa: E402

sys.path.insert(0, str(M.ROOT))
import lac_tables as LT  # noqa: E402

snap_a, snap_b, country, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
years = [int(y) for y in sys.argv[5:]] or None
PREFIX = tuple(LT.techs('power_plant_prefix'))
TOKENS = [t.upper() for t in LT.techs('solar_wind_token')]


def kind(tech):
    t = tech.upper()
    hits = [k for k in TOKENS if k in t[2:]]
    if not hits:
        return 'other'
    return 'wind' if any(k.startswith('W') for k in hits) else 'solar'


def load(snap):
    wb = openpyxl.load_workbook(snap / 'tree' / '_STAGE3_RESULTS' / 'stage3_results.xlsx', read_only=True)
    ws = wb['TotalTechnologyAnnualActivity']
    agg = {}
    for c, s, _r, tech, y, v in ws.iter_rows(min_row=2, values_only=True):
        if c != country or not str(tech).upper().startswith(PREFIX) or (years and y not in years):
            continue
        for k in (kind(tech), 'total'):
            agg[(s, y, k)] = agg.get((s, y, k), 0.0) + (v or 0.0)
        agg.setdefault((s, y, 'solar'), 0.0)
        agg.setdefault((s, y, 'wind'), 0.0)
    wb.close()
    return agg


a, b = load(snap_a), load(snap_b)
rows = []
for key in sorted(set(a) | set(b)):
    s, y, k = key
    if k == 'other':
        continue
    va, vb = a.get(key, 0.0), b.get(key, 0.0)
    rows.append(dict(scenario=s, year=y, group=k, before_pj=round(va, 4), after_pj=round(vb, 4),
                     change_pj=round(vb - va, 4)))
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r)
