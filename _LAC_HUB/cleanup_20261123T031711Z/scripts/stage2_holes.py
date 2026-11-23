"""Scan for Stage 2 holes: a Stage 2 share of 0 where the Stage 1 share and every Stage 2 override for that
country, scenario, plant and year are above 0 (a plant and year with no override row counts as "every
override above 0").

Usage: python stage2_holes.py <stage1.xlsx> <stage2_before.xlsx> <stage2_after.xlsx|-> <overrides dir> <out.csv>
Writes one row per case with the shares and lower limits before and after the fix.
"""
import csv
import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings('ignore')
s1p, beforep, afterp, ovdir, out = sys.argv[1:6]
ZERO = 1e-12


def sheet(path, name):
    d = pd.read_excel(path, sheet_name=name)
    years = [c for c in d.columns if str(c).isdigit()]
    d = d.melt(id_vars=['Country', 'Scenario', 'Tech'], value_vars=years, var_name='Year', value_name='v')
    d['Year'] = d['Year'].astype(int)
    return {(r.Country, r.Scenario, r.Tech, r.Year): float(r.v) for r in d.itertuples(index=False)}


def overrides(folder):
    ov = {}
    for p in sorted(Path(folder).glob('STAGE2_OVERWRITES*.csv')):
        with open(p, encoding='utf-8-sig') as fh:
            for line in fh:
                if line.lstrip().startswith('#') or not line.strip() or line.startswith('Country'):
                    continue
                parts = line.split(',', 5)
                try:
                    k = (parts[0].strip(), parts[1].strip(), parts[2].strip(), int(float(parts[3])))
                    ov.setdefault(k, []).append((float(parts[4]), p.name))
                except (ValueError, IndexError):
                    continue
    return ov


s1 = sheet(s1p, 'CURRENT_SHARES')
b_sh, b_lo = sheet(beforep, 'CURRENT_SHARES'), sheet(beforep, 'CURRENT_LOWER')
a_sh = a_lo = None
if afterp != '-':
    a_sh, a_lo = sheet(afterp, 'CURRENT_SHARES'), sheet(afterp, 'CURRENT_LOWER')
ov = overrides(ovdir)
rows = []
for k, v in sorted(b_sh.items()):
    if abs(v) > ZERO:
        continue
    s1v = s1.get(k)
    if s1v is None or s1v <= ZERO:
        continue
    ovs = ov.get(k, [])
    if any(x <= 0 for x, _ in ovs):
        continue
    c, s, t, y = k
    rows.append(dict(country=c, scenario=s, tech=t, year=y, stage1_share=round(s1v, 6),
                     overrides_pct='|'.join(f'{x:g}' for x, _ in ovs), override_files='|'.join(sorted({f for _, f in ovs})),
                     stage2_share_before=v, stage2_lower_pj_before=round(b_lo.get(k, float('nan')), 6),
                     stage2_share_after='' if a_sh is None else round(a_sh.get(k, float('nan')), 6),
                     stage2_lower_pj_after='' if a_lo is None else round(a_lo.get(k, float('nan')), 6)))
with open(out, 'w', newline='', encoding='utf-8') as fh:
    fields = ['country', 'scenario', 'tech', 'year', 'stage1_share', 'overrides_pct', 'override_files',
              'stage2_share_before', 'stage2_lower_pj_before', 'stage2_share_after', 'stage2_lower_pj_after']
    w = csv.DictWriter(fh, fieldnames=fields, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print(f'{len(rows)} cases')
for r in rows:
    print(r['country'], r['scenario'], r['tech'], r['year'], r['stage1_share'], r['overrides_pct'], '->', r['stage2_share_after'])
