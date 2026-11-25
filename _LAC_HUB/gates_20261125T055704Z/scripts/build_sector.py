"""Register rows of step 7.5: the cost proposals of the cost-sources job (classes confirmed, replace, assumption) for
the sector models CR_AFOLU, CR_WASTE, RD_AFOLU, RD_WASTE, ECU_WASTE, GUA_WASTE, HON_AFOLU, HON_WASTE, JAM_AFOLU,
JAM_WASTE (ECU_AGR unchanged). EmissionsPenalty proposals are left out: step 7.6 sets every penalty to 0.
The cell is named in the proposal column ao_row_at_b51f24b (path, sheet, row of tech, column). Writes
work/register_sector.csv."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import glob
import re

import pandas as pd

FIELDS = ['model', 'file', 'sheet', 'tech', 'parameter', 'year', 'before', 'after', 'unit', 'source_id', 'page',
          'derivation', 'assumption_sentence', 'range_low', 'range_high']
SECTOR = {'CR_AFOLU', 'CR_WASTE', 'RD_AFOLU', 'RD_WASTE', 'ECU_WASTE', 'GUA_WASTE', 'HON_AFOLU', 'HON_WASTE',
          'JAM_AFOLU', 'JAM_WASTE'}
src = M.ROOT / '_LAC_HUB' / 'cost_sources_20261122T234333Z'
d = pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False) for f in glob.glob(str(src / '*' / 'proposals_*.csv'))])
d = d[d['model'].isin(SECTOR) & d['change_class'].isin(['confirmed', 'replace', 'assumption'])]
d = d[~d['sheet'].str.startswith('EmissionsPenalty')]
rows, skipped = [], []
for r in d.itertuples(index=False):
    m = re.match(r'^(.*?/[^/]*?)/(A1_Outputs/[^,]+|[^/,]+\.xlsx), sheet ([^,]+), row', r.ao_row_at_b51f24b)
    if not m:
        skipped.append((r.model, r.tech, r.parameter, r.year, r.ao_row_at_b51f24b))
        continue
    path, file, sheet = m.group(1), m.group(2), m.group(3).strip()
    rows.append(dict(model=path, file=file, sheet=sheet, tech=r.tech, parameter=r.parameter,
                     year='' if r.year in ('', 'BY') else r.year, before=r.current_value, after=r.proposed_value,
                     unit=r.unit, source_id=r.source_ids, page='', derivation=r.derivation,
                     assumption_sentence=r.assumption_sentence, range_low='', range_high=''))
with open(M.JOB / 'work' / 'register_sector.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print(len(rows), 'rows;', len(skipped), 'skipped')
for s in skipped[:10]:
    print('  skipped', s)
