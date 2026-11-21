"""Updated currency_conversion.csv (brief R4): the PR #10 table with the 109 groups it left unconverted now resolved.

Input: PR #10 _LAC_HUB/cost_write_run_20261111T071733Z/currency_conversion.csv, scripts/r4_groups_scratch.csv (the 109
groups), scripts/r4r5_cells.csv (currency year and CPI-U factor per cell), proposals.csv (ASSUMPTION sentences).
For a resolved group: stated_year = the dollar year(s) used; where_stated = the source statement or the ASSUMPTION
sentence; factor = CPI-U annual-average factor to 2024 USD with the number of years it applies to; left = '';
resolved_by = 'LAC_FIX_RUN R4'. Rows PR #10 had already converted stay as they were (resolved_by empty).
Run: py -I scripts/build_currency.py
"""
from collections import Counter
from pathlib import Path
import pandas as pd

JOB = Path(r'C:\clw_fix\_LAC_HUB\fix_run_20261111T200825Z')
PR10 = JOB.parent / 'cost_write_run_20261111T071733Z' / 'currency_conversion.csv'
cc = pd.read_csv(PR10, dtype=str, keep_default_na=False)
groups = pd.read_csv(JOB / 'scripts' / 'r4_groups_scratch.csv', dtype=str, keep_default_na=False)
cells = pd.read_csv(JOB / 'scripts' / 'r4r5_cells.csv', dtype=str, keep_default_na=False)
P = pd.read_csv(JOB / 'proposals.csv', dtype=str, keep_default_na=False)
gk = {(r.country, r.tech, r.parameter) for r in groups.itertuples()}
assume = {}
for r in P[P.assumption != ''].itertuples():
    assume.setdefault((r.country, r.Tech, r.Parameter), r.assumption)

cc['resolved_by'] = ''
done = set()
for i, r in cc.iterrows():
    k = (r.country, r.tech, r.parameter)
    if k not in gk:
        continue
    c = cells[(cells.country == r.country) & (cells.tech == r.tech) & (cells.parameter == r.parameter)]
    if c.empty:
        cc.at[i, 'left'] = r.left + ' | LAC_FIX_RUN: no cell of this group in the workbook (nothing to convert)'
        continue
    yrs = Counter(c.currency_year)
    fac = Counter(f'{float(f):.6f}' for f in c.factor if f not in ('', 'nan'))
    cc.at[i, 'stated_year'] = ','.join(sorted(yrs))
    basis = sorted(set(c.basis_class))
    src = c.derivation_src.iloc[0]
    txt = assume.get(k, '')
    cc.at[i, 'where_stated'] = ('LAC_FIX_RUN R4: ' + (txt if txt else f'dollar year stated by the source ({"; ".join(basis)}): {src}'))[:600]
    cc.at[i, 'factor'] = '; '.join(f'{f} ({n} years)' for f, n in sorted(fac.items()))
    cc.at[i, 'left'] = ''
    cc.at[i, 'keep_rows'] = '0'
    cc.at[i, 'resolved_by'] = 'LAC_FIX_RUN R4'
    done.add(k)
missing = gk - done
for k in sorted(missing):
    c = cells[(cells.country == k[0]) & (cells.tech == k[1]) & (cells.parameter == k[2])]
    print('group not in the PR #10 table:', k, len(c))
cc.to_csv(JOB / 'currency_conversion.csv', index=False, lineterminator='\n')
print('rows', len(cc), 'resolved groups', len(done), 'of', len(gk), 'still left', (cc.left != '').sum())
