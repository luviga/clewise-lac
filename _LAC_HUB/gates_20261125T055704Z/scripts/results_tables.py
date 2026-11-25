"""Step 9.5 and 2.6 and 7.6 result tables from the Stage 3 results of a run (no model value is written):
  results_summary.csv       country, scenario, year: total discounted cost (M US$), energy emissions per report
                            label and their total (kt CO2 eq), renewable share of power plant generation,
                            generation by plant type (PJ), new capacity by plant type (GW)
  emission_targets_check.csv published energy emission levels against the model energy emissions
  external_costs.csv        fuel use (PJ) x IMF per-unit external cost (2023 template) per country and fuel
Usage: python -I results_tables.py <root> <out_dir>"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import sys
from pathlib import Path

import pandas as pd

root, out = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(root))
import lac_tables as LT  # noqa: E402

x = pd.ExcelFile(root / '_STAGE3_RESULTS' / 'stage3_results.xlsx')
act = pd.read_excel(x, 'TotalTechnologyAnnualActivity')
em = pd.read_excel(x, 'AnnualEmissions')
nc = pd.read_excel(x, 'NewCapacity')
tdc = pd.read_excel(x, 'TotalDiscountedCost') if 'TotalDiscountedCost' in x.sheet_names else pd.DataFrame()
pref = tuple(LT.techs('power_plant_prefix'))
H, R = LT.techs('hydro_token'), LT.techs('renewable_token')


def kind(t):
    u = t.upper()
    for k, toks in [('hydro', H), ('solar', ['SOL', 'SPV', 'PV']), ('wind', ['WND', 'WNO', 'WNS']),
                    ('geothermal', ['GEO']), ('bioenergy', ['BIM', 'BIO', 'BGS', 'SUG', 'BMS']),
                    ('natural gas', ['NGS', 'GAS']), ('coal and petcoke', ['COA', 'COK']),
                    ('oil products', ['DSL', 'FOI', 'HFO', 'CRU', 'GLP', 'LPG', 'GSL'])]:
        if any(tk in u for tk in toks):
            return k
    return 'other'


def is_re(t):
    u = t.upper()
    return any(k in u for k in H) or any(k in u for k in R)


rows = []
for (c, s), g in act[act['Technology'].str.upper().str.startswith(pref)].groupby(['Country', 'Scenario']):
    labels = LT.emissions('energy_report', c)
    for y, gy in g.groupby('Year'):
        tot = gy['Value'].sum()
        re_ = gy[gy['Technology'].map(is_re)]['Value'].sum()
        e = em[(em.Country == c) & (em.Scenario == s) & (em.Year == y) & em.Emission.isin(labels)]
        r = dict(country=c, scenario=s, year=int(y),
                 total_discounted_cost_musd=round(float(tdc[(tdc.Country == c) & (tdc.Scenario == s) & (tdc.Year == y)]['Value'].sum()), 4) if len(tdc) else '',
                 energy_emissions_kt=round(1000 * float(e['Value'].sum()), 1),
                 energy_labels='+'.join(labels), renewable_share=round(re_ / tot, 4) if tot else '')
        for lab in labels:
            r[f'emissions_kt_{lab}'] = round(1000 * float(e[e.Emission == lab]['Value'].sum()), 1)
        for k, v in gy.groupby(gy['Technology'].map(kind))['Value'].sum().items():
            r[f'gen_pj_{k}'] = round(float(v), 4)
        n = nc[(nc.Country == c) & (nc.Scenario == s) & (nc.Year == y) & nc.Technology.str.upper().str.startswith(pref)]
        for k, v in n.groupby(n['Technology'].map(kind))['Value'].sum().items():
            r[f'newcap_gw_{k}'] = round(float(v), 5)
        rows.append(r)
cols = sorted({k for r in rows for k in r}, key=lambda k: (not k in ('country', 'scenario', 'year'), k))
cols = ['country', 'scenario', 'year'] + [c for c in cols if c not in ('country', 'scenario', 'year')]
pd.DataFrame(rows)[cols].to_csv(out / 'results_summary.csv', index=False, lineterminator='\n')

# emission targets: published energy emission levels (NDC verify table, energy rows) against the model
pub = pd.read_csv(root / '_LAC_HUB' / 'ndc_verify_20261121T233937Z' / 'scenario_values.csv')
pub = pub[pub.model_quantity.fillna('').str.startswith('emissions, label') & pub.kind_of_quantity.eq('emissions')]
name = {'Costa Rica': 'CostaRica', 'Dominican Republic': 'DominicanRepublic'}
summ = pd.DataFrame(rows)
chk = []
for r in pub.itertuples():
    c = name.get(r.country, r.country)
    m = summ[(summ.country == c) & (summ.scenario == r.scenario) & (summ.year == int(r.year))]
    mv = float(m['energy_emissions_kt'].iloc[0]) if len(m) else None
    chk.append(dict(value_id=r.value_id, country=c, scenario=r.scenario, year=int(r.year), target_kt=r.value_standard,
                    model_kt=mv, result='' if mv is None else ('met' if mv <= r.value_standard * 1.0 + 1e-9 else 'missed'),
                    gap_kt=None if mv is None else round(mv - r.value_standard, 1),
                    labels_summed='+'.join(LT.emissions('energy_report', c)),
                    unit_comparison='target in kt CO2 eq as published; model labels in Mt CO2 eq x 1000; GWP set of the model factors not stated',
                    check_status=r.check_status, conditionality=r.conditionality, description=r.description))
pd.DataFrame(chk).to_csv(out / 'emission_targets_check.csv', index=False, lineterminator='\n')

# external costs of fuel use: IMF Energy Subsidy Template (January 2024 version), year 2022 values (the last year
# that is not a projection), real 2021 US$; liquid fuels per litre are turned into per GJ with an energy content
# per litre (ASSUMPTION: gasoline 34.2, diesel 38.6, LPG 25.3 MJ per litre, typical net values)
ISO = {'CostaRica': 'CRI', 'DominicanRepublic': 'DOM', 'Ecuador': 'ECU', 'Guatemala': 'GTM', 'Honduras': 'HND', 'Jamaica': 'JAM'}
MJ_L = {'gso': 34.2, 'die': 38.6, 'lpg': 25.3}
FUEL = {'GSL': 'gso', 'DSL': 'die', 'LPG': 'lpg', 'GLP': 'lpg', 'COA': 'coa', 'NGS': 'nga'}
imf = list(csv.DictReader(open(M.JOB / 'work' / 'research_R1.csv', encoding='utf-8')))
fac = {}
for r in imf:
    if r['topic'] != 'B' or r['year'] != '2022':
        continue
    import re as _re
    m = _re.search(r'mit\.(\w+)\.cost\.(\w+)\.(\w+)\.1', r['item'])
    if not m:
        continue
    kind_, f, scope = m.groups()
    if f in ('coa', 'nga') and scope not in ('tot',) and kind_ != 'scc':
        continue
    if kind_ == 'scc' and f in ('coa', 'nga') and scope != 'pow':
        continue
    v = float(r['value_standard'])
    if f in MJ_L:
        v = v / MJ_L[f] * 1000      # US$ per litre -> US$ per GJ
    fac.setdefault((r['country'], f), {}).setdefault('global' if kind_ == 'scc' else 'local', 0.0)
    fac[(r['country'], f)]['global' if kind_ == 'scc' else 'local'] += v
ext = []
dist = act[act['Technology'].str.startswith('DIST_')]
for r in dist.itertuples():
    tok = r.Technology.split('_', 1)[1]
    f = FUEL.get(tok)
    if f is None or (ISO.get(r.Country), f) not in fac:
        continue
    for k, v in fac[(ISO[r.Country], f)].items():
        ext.append(dict(country=r.Country, scenario=r.Scenario, year=int(r.Year), kind=k, fuel=tok,
                        quantity_pj=round(r.Value, 4), factor_usd2021_per_gj=round(v, 4), source='ALN-IMF-2023',
                        cost_musd2021=round(r.Value * v, 4)))
pd.DataFrame(ext).to_csv(out / 'external_costs.csv', index=False, lineterminator='\n')
print(len(rows), 'summary rows;', len(chk), 'target checks;', len(ext), 'external cost rows')
