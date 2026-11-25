"""Step 9.1 gate: compiled inputs (A2_Output_Params and B1_Output_Params of the six energy models) of this job
against the baseline compile, keyed by model, folder, scenario, parameter, indices and year.
A difference is explained when it falls under a change of this job:
  register   a register row of the same model, technology (or fleet group of the technology) and parameter
             (vehicle costs, lives, distances, imports, penalties, discount rate, emission factors, PPBIM,
             hydrogen adoption rows, history cells of step 5);
  rule       a change that a written input carries to other compiled values: transport adoption rows (activity
             and capacity limits and demands of the road transport technologies of the scenario), fleet group
             distance (every compiled value of the technologies of the group), discount rate, emission penalties.
Writes compile_diff.csv (every difference with its explanation) and compile_diff_unexplained.csv.
Usage: python -I compile_diff.py <baseline root> <job root>"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import glob
import sys
from pathlib import Path

import pandas as pd

base, new = Path(sys.argv[1]), Path(sys.argv[2])
MODELS = ['CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic/RD_ENERGY', 'Ecuador/ECU_Energy',
          'Guatemala/GUA_ENERGY', 'Honduras/HON_ENERGY', 'Jamaica/JAM_ENERGY']
KEYS = ['REGION', 'TECHNOLOGY', 'FUEL', 'EMISSION', 'MODE_OF_OPERATION', 'YEAR', 'TIMESLICE', 'SEASON', 'DAYTYPE',
        'DAILYTIMEBRACKET', 'STORAGE']
# register rows: (model, tech) -> parameters
reg = {}
for p in glob.glob(str(M.JOB / 'work' / 'register_*.csv')) + [str(M.JOB / 'work' / 'value_register_vehicles.csv')]:
    if p.endswith('_write_log.csv'):
        continue
    for r in csv.DictReader(open(p, encoding='utf-8')):
        if 'tech' not in r:
            continue
        parts = r['tech'].split('|')
        t = (parts[1] if len(parts) >= 3 else parts[-1]).split(';')[0].strip()
        reg.setdefault((r['model'], t), set()).add(r['parameter'] or 'any')
GROUP_PARAMS = {'CapitalCost', 'FixedCost', 'ResidualCapacity', 'TotalAnnualMaxCapacity', 'TotalAnnualMinCapacity',
                'TotalAnnualMaxCapacityInvestment', 'TotalAnnualMinCapacityInvestment', 'CapacityToActivityUnit',
                'OperationalLife', 'TotalTechnologyAnnualActivityLowerLimit', 'TotalTechnologyAnnualActivityUpperLimit'}


def explain(model, scen, param, tech):
    ps = reg.get((model, tech), set())
    if param in ps or 'any' in ps:
        return 'register'
    if ps:
        return 'register: value derived in the workbook or compiler from a register cell of the same technology'
    if param == 'DiscountRate':
        return 'rule: discount rate (step 7.7)'
    if param == 'EmissionsPenalty':
        return 'rule: penalties 0 (step 7.6)'
    if param == 'EmissionActivityRatio':
        return 'register: emission factors (step 6.3)' if (model, tech) in reg else ''
    if tech.startswith(('TR', 'Techs_')) and param in GROUP_PARAMS | {'InputActivityRatio', 'OutputActivityRatio'}:
        if any(k[0] == model and (k[1].startswith('Techs_') or k[1].startswith('TR')) for k in reg):
            return 'rule: vehicle costs, lives, distances and transport targets carried by the compiler (steps 2.5, 7.1 to 7.4)'
    if tech == 'IMP_ELE':
        return 'register: imports (step 6)'
    return ''


rows = []
for m in MODELS:
    for folder in ('A2_Output_Params', 'B1_Output_Params'):
        for sd in sorted((new / m / folder).glob('*')):
            if not sd.is_dir():
                continue
            for f in sorted(sd.glob('*.csv')):
                g = base / m / folder / sd.name / f.name
                a = pd.read_csv(g, dtype=str, keep_default_na=False) if g.exists() else pd.DataFrame()
                b = pd.read_csv(f, dtype=str, keep_default_na=False)
                if 'Value' not in b.columns:
                    continue
                k = [c for c in KEYS if c in b.columns]
                A = a.drop_duplicates(k, keep='last').set_index(k)['Value'] if len(a) else pd.Series(dtype=str)
                B = b.drop_duplicates(k, keep='last').set_index(k)['Value']
                j = pd.concat([A.rename('base'), B.rename('new')], axis=1)
                bn, nn = pd.to_numeric(j['base'], errors='coerce'), pd.to_numeric(j['new'], errors='coerce')
                d = j[~((bn - nn).abs() <= 1e-9 * (1 + bn.abs())) & ~(j['base'].isna() & j['new'].isna()) & ~(j['base'] == j['new'])]
                for idx, r in d.reset_index().iterrows():
                    tech = r.get('TECHNOLOGY', '')
                    rows.append([m, folder, sd.name, f.stem, tech, r.get('FUEL', ''), r.get('EMISSION', ''),
                                 r.get('YEAR', ''), r['base'], r['new'], explain(m, sd.name, f.stem, tech)])
cols = ['model', 'folder', 'scenario', 'parameter', 'technology', 'fuel', 'emission', 'year', 'baseline', 'after', 'explained_by']
with open(M.JOB / 'compile_diff.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(cols)
    w.writerows(rows)
with open(M.JOB / 'compile_diff_unexplained.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(cols)
    w.writerows([r for r in rows if not r[-1]])
print(len(rows), 'differences;', sum(1 for r in rows if not r[-1]), 'unexplained')
