"""Step 6.4 gate: scenario_difference_register.csv, every compiled input (B1_Output_Params) that differs between BAU
and NDC or LTS in an energy model, grouped by model, parameter, scenario, technology, fuel, emission and year group
(from scen_diff.py), with the policy measure and the source that explain it. A difference without a policy
measure is marked 'no policy measure' and is a failure of the gate. History differences are listed with the rule
that equalises them in the solved data (scenario_rules.py).
Usage: python -I scen_register.py <scen_diff csv>"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import sys

src = sys.argv[1]
TARGET_IDS = {}
for r in csv.DictReader(open(M.ROOT / 'inputs' / 'scenarios' / 'scenario_values.csv', encoding='utf-8')):
    TARGET_IDS.setdefault((r['country'], r['scenario']), set()).update(x for x in r['value_id'].split('|') if x)
TRANSPORT_IDS = {}
for r in csv.DictReader(open(M.JOB / 'work' / 'transport_targets.csv', encoding='utf-8')):
    if r['result'] == 'loaded':
        TRANSPORT_IDS.setdefault((r['model'], r['scenario']), set()).add(r['value_id'])
COUNTRY = {'CostaRica/CR_ENERGY/t1_confection': 'CostaRica', 'DominicanRepublic/RD_ENERGY': 'DominicanRepublic',
           'Ecuador/ECU_Energy': 'Ecuador', 'Guatemala/GUA_ENERGY': 'Guatemala', 'Honduras/HON_ENERGY': 'Honduras',
           'Jamaica/JAM_ENERGY': 'Jamaica'}
LIMITS = {'TotalTechnologyAnnualActivityLowerLimit', 'TotalTechnologyAnnualActivityUpperLimit', 'TotalAnnualMaxCapacity',
          'TotalAnnualMinCapacity', 'TotalAnnualMaxCapacityInvestment', 'TotalAnnualMinCapacityInvestment'}


def classify(r):
    m, p, t, f, sc = r['model'], r['parameter'], r['technology'], r['fuel'], r['scenario']
    c = COUNTRY[m]
    if r['year_group'] == 'history':
        return ('history equalised in the solved data', 'scenario_rules.py history rule (years up to 2024 take the BAU value)')
    if t.startswith(('PP', 'PWR')) and p in LIMITS | {'CapitalCost'}:
        ids = sorted(TARGET_IDS.get((c, sc), []))
        return ('renewable share of generation (Stage 3 replaces power plant limits from 2025 with the controller built '
                'from the published targets)', '|'.join(ids) if ids else 'no published target: policy shares equal BAU')
    if t.startswith(('TR', 'Techs_', 'T4')) or (f.startswith('E6') and p == 'SpecifiedAnnualDemand'):
        ids = sorted(TRANSPORT_IDS.get((m, sc), []))
        if p == 'EmissionActivityRatio' or (t.startswith(('T4GSL', 'DIST_GSL'))):
            return ('ethanol blend of gasoline (configured blend path)', 'no published source: stylised measure')
        return ('transport measures of the scenario workbook (adoption, mode shift, occupancy, distance)',
                '|'.join(ids) if ids else 'no published source: stylised measure')
    if t.startswith('DIST_GSL') or (p == 'EmissionActivityRatio' and 'GSL' in t):
        return ('ethanol blend of gasoline (configured blend path)', 'no published source: stylised measure')
    if p == 'SpecifiedAnnualDemand':
        return ('demand measures of the scenario workbook (efficiency, electrification, transport electricity)',
                'no published source: stylised measure')
    if p in ('InputActivityRatio', 'OutputActivityRatio'):
        return ('efficiency measures of the scenario workbook', 'no published source: stylised measure')
    if t == 'IMP_ELE':
        return ('no policy measure', '')
    if p in LIMITS:
        return ('limits of the scenario workbook (Electrical rows)', 'no published source: stylised measure')
    return ('no policy measure', '')


rows = []
for r in csv.DictReader(open(src, encoding='utf-8')):
    measure, source = classify(r)
    r.update(policy_measure=measure, source=source)
    rows.append(r)
cols = list(rows[0].keys()) if rows else ['model']
with open(M.JOB / 'scenario_difference_register.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
from collections import Counter  # noqa: E402
print(len(rows), 'groups;', Counter(r['policy_measure'] for r in rows))
