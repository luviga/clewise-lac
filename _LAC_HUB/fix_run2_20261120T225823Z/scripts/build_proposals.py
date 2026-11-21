"""A1: proposals.csv = all parts in proposals_parts/, with a 'basis' column:
  source          : value read from or computed with sourced inputs (source_ids must resolve in sources.csv)
  assumption      : carries an ASSUMPTION sentence (it may also cite sources as its check)
  unit_conversion : a unit conversion only (D13, D1 CAU, D2f)
  decision_value  : a value fixed by the decision text itself (D-ECU2 a and d: 0 and 999,999; D12 layout row)
  alignment_rule  : D2 history alignment to BAU and the scenario's own 4ba69d6 values (rule of decision D2)
"""
import glob, os
import pandas as pd

JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
parts = sorted(glob.glob(JOB + '/proposals_parts/*.csv'))
P = pd.concat([pd.read_csv(p, dtype=str, keep_default_na=False).assign(part=os.path.basename(p)[:-4]) for p in parts],
              ignore_index=True)


def basis(r):
    if r.assumption.strip():
        return 'assumption'
    if 'unit conversion' in r.derivation and not r.source_ids:
        return 'unit_conversion'
    if r.decision.startswith('D-ECU2a') or r.decision.startswith('D-ECU2d'):
        return 'decision_value'
    if r.part in ('d2_config', 'd2c') and not r.source_ids and 'D2a' in r.decision:
        return 'alignment_rule'
    if r.Tech == 'PRONGS' and r.Parameter == 'CapacityToActivityUnit':
        return 'decision_value'
    return 'source'


P['basis'] = P.apply(basis, axis=1)
P.drop(columns=['part']).to_csv(JOB + '/proposals.csv', index=False, lineterminator='\n')
print(len(P))
print(P.groupby(['decision', 'basis']).size().to_string())
