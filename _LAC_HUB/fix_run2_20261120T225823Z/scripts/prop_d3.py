"""D3: history emission factors of the 39 BAU rows copied into NDCNEW and LTSNEW (F6).
- Where research/d3_ef.md (values checked in the files) gives a comparable source value that differs from the model value, the
  source value is written in the BAU row and its two copies, that history year only (kind cfg_num).
- Every other row-year gets an ASSUMPTION sentence per (country, tech, emission) with the IPCC 2006 default range as check
  (kind doc: documentation only, no cell written).
Applied (differs and comparable): Honduras 2019 PPFOI, PPGTDSL, PPICEDSL, PPCOK, PPBIM (BEN 2019 Cuadro 5 efficiency with the
inventory factors); Dominican Republic 2018-2022 PPCOA, PPCCTNGS, PPCCTNGSDSL, PPICEGASFOI, PPICEFOI (NID 1.A.1.a.i fuel x
inventory factor / CNE gross generation by fuel), only if the CNE file has a public URL (DR_CNE_URL_OK); Ecuador PROCRU 2022
CO2 and CO2e (NID Tabla 13 / BCE crude processed). Not comparable: Dominican diesel (inventory fuel includes autoproducers
and isolated systems, generation is SENI only). Writes proposals_parts/d3.csv."""
import os, re, sys
import openpyxl
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, EARLIER
from common_props import BASEDIR, write_part

DR_CNE_URL_OK = os.path.exists(JOB + '/logs/dr_cne_url_ok.flag')
CFG = {'Honduras': 'Honduras/HON_ENERGY/B1_Scenario_Config.xlsx', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY/B1_Scenario_Config.xlsx',
       'Ecuador': 'Ecuador/ECU_Energy/B1_Scenario_Config.xlsx'}
SHEET = {'Honduras': 'EmissionsActivityRatio', 'DominicanRepublic': 'EmissionsActivityRatio', 'Ecuador': 'SmartGrid'}
# IPCC 2006 V2 Ch2 Table 2.2 defaults (low, default, high) kg/TJ; AR5 GWP CH4 28, N2O 265
IP = {'RFO': ('residual fuel oil', (75500, 77400, 78800), (1, 3, 10), (0.2, 0.6, 2)),
      'DSL': ('gas/diesel oil', (72600, 74100, 74800), (1, 3, 10), (0.2, 0.6, 2)),
      'LPG': ('liquefied petroleum gases', (61600, 63100, 65600), (0.3, 1, 3), (0.03, 0.1, 0.3)),
      'OBC': ('other bituminous coal', (89500, 94600, 99700), (0.3, 1, 3), (0.5, 1.5, 5)),
      'SBC': ('sub-bituminous coal', (92800, 96100, 100000), (0.3, 1, 3), (0.5, 1.5, 5)),
      'NGS': ('natural gas', (54300, 56100, 58300), (0.3, 1, 3), (0.03, 0.1, 0.3)),
      'CRU': ('crude oil', (71100, 73300, 75500), (1, 3, 10), (0.2, 0.6, 2)),
      'BIO': ('other primary solid biomass', (0, 0, 0), (10, 30, 100), (1.5, 4, 15))}
FUEL = {('Honduras', 'PPBIM'): 'BIO', ('Honduras', 'PPCOK'): 'OBC', ('Honduras', 'PPFOI'): 'RFO', ('Honduras', 'PPGTDSL'): 'DSL',
        ('Honduras', 'PPICEDSL'): 'DSL', ('Honduras', 'PPGTGLP'): 'LPG', ('DominicanRepublic', 'PPCOA'): 'SBC',
        ('DominicanRepublic', 'PPCCTDSL'): 'DSL', ('DominicanRepublic', 'PPCCTNGS'): 'NGS', ('DominicanRepublic', 'PPCCTNGSDSL'): 'NGS',
        ('DominicanRepublic', 'PPICEGASFOI'): 'NGS', ('DominicanRepublic', 'PPICEFOI'): 'RFO', ('Ecuador', 'PPCRU'): 'CRU',
        ('Ecuador', 'PPDSL'): 'DSL', ('Ecuador', 'PPRDSL'): 'DSL', ('Ecuador', 'PPFOI'): 'RFO', ('Ecuador', 'PPNGS'): 'NGS',
        ('Ecuador', 'PPRNGS'): 'NGS'}
TECHNAME = {'PPBIM': 'biomass (bagasse) power plants', 'PPCOK': 'coke-fired power plants', 'PPFOI': 'fuel-oil power plants',
            'PPGTDSL': 'diesel gas turbines', 'PPICEDSL': 'diesel engines', 'PPGTGLP': 'LPG gas turbines', 'PPCOA': 'coal power plants',
            'PPCCTDSL': 'diesel-fired combined cycles', 'PPCCTNGS': 'gas combined cycles', 'PPCCTNGSDSL': 'gas and diesel combined cycles',
            'PPICEGASFOI': 'gas and fuel-oil engines', 'PPICEFOI': 'fuel-oil engines', 'PPCRU': 'crude-oil power plants',
            'PPDSL': 'diesel power plants', 'PPRDSL': 'isolated diesel plants at oil facilities', 'PPNGS': 'gas power plants',
            'PPRNGS': 'isolated gas plants at oil facilities', 'PROCRU': 'crude refining'}
GAS = lambda e: e.split('_')[0]
SRC = {'Honduras': 'FR2-D3-IPCC;FR2-D3-AR5;FR2-D3-HONNIR;FR2-D3-HONBEN19',
       'DominicanRepublic': 'FR2-D3-IPCC;FR2-D3-AR5;FR2-D3-DRNID;FR2-D3-CNEGEN',
       'Ecuador': 'FR2-D3-ECUNID;ECUF-01;GEN-001;GEN-002'}


def factor_range(fuel, gas):
    _, c, m, n = IP[fuel]
    if gas == 'CO2':
        return c[0], c[1], c[2]
    if gas == 'CH4':
        return m
    if gas == 'N2O':
        return n
    cc = (0, 0, 0) if fuel == 'BIO' else c
    return tuple(cc[k] + 28 * m[k] + 265 * n[k] for k in range(3))


# parse the research table
rows = []
for line in open(JOB + '/research/d3_ef.md', encoding='utf-8'):
    if not line.startswith('| ') or line.startswith('| country') or line.startswith('|---'):
        continue
    f = [x.strip() for x in line.strip().strip('|').split('|')]
    if len(f) < 9 or f[0] not in CFG:
        continue
    rows.append(dict(country=f[0], tech=f[1], emission=f[2], year=int(f[3]), model=float(f[4]),
                     source=None if f[5] in ('-', '') else float(f[5].split()[0]), inputs=f[6], loc=f[7], verdict=f[8]))
T = pd.DataFrame(rows)
assert len(T) == 243, len(T)


def apply(r):
    if not r.verdict.startswith('differs') or r.source is None:
        return False
    if r.country == 'Honduras':
        return r.year == 2019
    if r.country == 'Ecuador':
        return r.tech == 'PROCRU' and r.year == 2022 and GAS(r.emission) in ('CO2', 'CO2e')
    if r.country == 'DominicanRepublic':
        return DR_CNE_URL_OK and r.tech != 'PPCCTDSL' and r.year <= 2022
    return False


T['apply'] = T.apply(apply, axis=1)
r6 = pd.read_csv(EARLIER + '/scripts/r6_ear_rows_Honduras_DominicanRepublic_Ecuador_Jamaica.csv')
copies = r6[['country', 'scenario', 'tech', 'emission', 'row', 'bau_row']].drop_duplicates()
out = []
wbs = {c: openpyxl.load_workbook(f'{BASEDIR}/{CFG[c]}') for c in CFG}
for _, r in T[T['apply']].iterrows():
    ws = wbs[r.country][SHEET[r.country]]
    hdr = {str(ws.cell(1, j).value): j for j in range(1, ws.max_column + 1)}
    j = hdr[str(r.year)]
    cp = copies[(copies.country == r.country) & (copies.tech == r.tech) & (copies.emission == r.emission)]
    targets = [('BAU', int(cp.bau_row.iloc[0]))] + [(s, int(x)) for s, x in zip(cp.scenario, cp.row)]
    assert len(targets) == 3, (r.country, r.tech, r.emission)
    for scen, rr in targets:
        cur = ws.cell(rr, j).value
        assert ws.cell(rr, 1).value == scen and r.tech in str(ws.cell(rr, 3).value), (r.country, rr, ws.cell(rr, 3).value)
        assert abs(float(cur) - r.model) <= 1e-5 * max(abs(r.model), 1e-9) or abs(float(cur) - r.model) < 5e-5, (r.country, rr, cur, r.model)
        out.append(dict(country=r.country, workbook=CFG[r.country], sheet=SHEET[r.country], row=rr,
                        column=openpyxl.utils.get_column_letter(j), year=r.year, Tech=r.tech, Parameter='EmissionActivityRatio ' + r.emission,
                        scenario=scen, current_value=cur, new_value=repr(r.source), kind='cfg_num', decision='D3',
                        source_ids=SRC[r.country], derivation=f'{r.inputs} ({r.loc})', assumption=''))
# ASSUMPTION sentences for the rest (per country, tech, emission)
for (c, t, e), g in T[~T['apply']].groupby(['country', 'tech', 'emission']):
    gas = GAS(e)
    yrs = sorted(g.year)
    vals = g.sort_values('year').model.tolist()
    span = f'{yrs[0]}' if len(yrs) == 1 else (f'{yrs[0]} to {yrs[-1]}' if yrs == list(range(yrs[0], yrs[-1] + 1)) else ', '.join(map(str, yrs)))
    unit = 'Mt per PJ of crude processed' if t == 'PROCRU' else 'Mt per PJ of electricity'
    vtxt = f'{min(vals):.4g}' if abs(max(vals) - min(vals)) < 1e-12 else f'{min(vals):.4g} to {max(vals):.4g}'
    gname = {'CO2': 'CO2', 'CH4': 'methane', 'N2O': 'nitrous oxide', 'CO2e': 'CO2-equivalent (AR5 GWP)'}[gas]
    if t == 'PROCRU':
        a = (f'ASSUMPTION: the {gname} factor of crude refining in {span} is {vtxt} {unit}; the national inventory reports '
             f'refinery emissions only for 2022 (1,245.5 kt CO2 and 1,248.9 kt CO2-equivalent over 325.7 PJ of crude processed, '
             f'0.00382 and 0.00383 Mt/PJ, with methane and nitrous oxide printed as 0.0 kt), so the other years carry the factor '
             f'of the national refinery balance; the 2022 inventory value is the check, within 5 percent of these values for CO2 '
             f'and CO2-equivalent and above them for methane and nitrous oxide only as a bound below 1.5e-7 Mt/PJ.')
        src = 'FR2-D3-ECUNID;ECUF-01'
    else:
        fuel = FUEL[(c, t)]
        lo, de, hi = factor_range(fuel, gas)
        if de == 0:
            continue
        hr = [v / (de * 1e-6) for v in vals]
        hrtxt = f'{min(hr):.2f}' if max(hr) - min(hr) < 0.005 else f'{min(hr):.2f} to {max(hr):.2f}'
        rlo, rhi = min(h * lo * 1e-6 for h in hr), max(h * hi * 1e-6 for h in hr)
        why = {'Honduras': 'the national energy balance publishes fuel input per unit of electricity by fuel only for 2019',
               'DominicanRepublic': ('the national inventory ends in 2022 and its diesel use includes autoproducers and isolated '
                                     'systems, so no series of fuel input per unit of electricity by plant type is published'
                                     if t == 'PPCCTDSL' else
                                     ('the national inventory ends in 2022' if DR_CNE_URL_OK else
                                      'the national inventory ends in 2022 and no public series of fuel input per unit of '
                                      'electricity by plant type is published')),
               'Ecuador': 'national statistics publish fuel use by fuel and generation by technology, but not fuel input per '
                          'unit of electricity by fuel'}[c]
        if c == 'Honduras' and yrs == [2019]:
            why = 'the 2019 national efficiency for this fuel gives a value within 1 percent of it'
        a = (f'ASSUMPTION: the {gname} factor of {TECHNAME[t]} in {span} is {vtxt} {unit}, the IPCC 2006 default for '
             f'{IP[fuel][0]} ({de:,.1f} kg per TJ of fuel) times a fuel input of {hrtxt} PJ per PJ of electricity, because '
             f'{why}; with the IPCC 2006 default range ({lo:,.1f} to {hi:,.1f} kg per TJ) the factor would be {rlo:.4g} to '
             f'{rhi:.4g} {unit}.')
        src = 'FR2-D3-IPCC;FR2-D3-AR5'
    out.append(dict(country=c, workbook=CFG[c], sheet=SHEET[c], row='', column='', year=';'.join(map(str, yrs)), Tech=t,
                    Parameter='EmissionActivityRatio ' + e, scenario='BAU;NDCNEW;LTSNEW', current_value=vtxt, new_value='',
                    kind='doc', decision='D3', source_ids=src,
                    derivation='value unchanged; verdicts and inputs in research/d3_ef.md: ' +
                               '; '.join(sorted(set(v.split('(')[0].strip() for v in g.verdict))), assumption=a))
write_part('d3', out)
print('cells', sum(1 for o in out if o['kind'] == 'cfg_num'), 'assumption rows', sum(1 for o in out if o['kind'] == 'doc'),
      'DR applied', DR_CNE_URL_OK)
