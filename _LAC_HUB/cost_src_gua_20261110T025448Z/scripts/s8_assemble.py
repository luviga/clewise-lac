"""Step 8: build proposals.csv, proposals_summary.csv and the merged sources.csv,
constants.csv and search_log.csv from the step outputs.
Usage: py -I s8_assemble.py <clone root> <job folder>"""
import os, sys
import pandas as pd

ROOT, J = sys.argv[1], sys.argv[2]
LP = os.path.join(ROOT, '_LAC_HUB/local_prices_20261109T085226Z')
BAU = os.path.join(ROOT, 'Guatemala/GUA_ENERGY/A2_Output_Params/BAU')
YEARS = list(range(2018, 2051))
COLS = ['country', 'sheet', 'Tech.ID', 'Tech', 'Parameter', 'fuel_scenario', 'year', 'current_value', 'proposed_value', 'unit',
        'change_class', 'basis_class', 'source_ids', 'derivation', 'assumption_sentence', 'current_effective_bau']

cur = pd.read_csv(os.path.join(J, 'cost_rows_current.csv'))
curd = {(r.Tech, r.Parameter): r for _, r in cur.iterrows()}
bau = {}
for p in ['CapitalCost', 'FixedCost', 'VariableCost']:
    x = pd.read_csv(os.path.join(BAU, p + '.csv'))
    for _, r in x.iterrows():
        bau[(r.TECHNOLOGY, p, int(r.YEAR))] = r.Value

def cell(t, p, y):
    r = curd[(t, p)]
    v = r[str(y)]
    return '' if pd.isna(v) else v

def eff(t, p, y):
    v = bau.get((t, p, y))
    return '' if v is None else v

rows = []
# ---- fuel supply rows
f = pd.read_csv(os.path.join(J, 'fuel_prices.csv'))
for _, r in f.iterrows():
    t = r.row
    c = curd[(t, 'VariableCost')]
    cv = cell(t, 'VariableCost', r.year)
    ev = eff(t, 'VariableCost', r.year)
    if t == 'EXTT_CRU':
        cc = 'fill_empty'
    elif t in ('DIST_COK', 'DIST_KER'):
        cc = 'fill_placeholder'
    else:
        cc = 'replace'
    basis = 'ASSUMPTION' if t == 'DIST_NGS' else r.case
    rows.append({'country': 'Guatemala', 'sheet': c.sheet, 'Tech.ID': c['Tech.ID'], 'Tech': t, 'Parameter': 'VariableCost',
                 'fuel_scenario': r.scenario, 'year': r.year, 'current_value': cv, 'proposed_value': r.value_usd_per_gj_net_real2024,
                 'unit': 'M US$ / PJ (= USD/GJ, net calorific basis, real 2024 USD)', 'change_class': cc, 'basis_class': basis,
                 'source_ids': r.source_ids, 'derivation': f'{r.chosen_point}; {r.derivation}; r method: {r.r_method}',
                 'assumption_sentence': r.assumption_sentence if isinstance(r.assumption_sentence, str) else '',
                 'current_effective_bau': ev})

# ---- plants and electricity imports
pc = pd.read_csv(os.path.join(J, 'plant_costs.csv'))
for _, r in pc.iterrows():
    t, p = r.technology, r.parameter
    c = curd[(t, p)]
    rows.append({'country': 'Guatemala', 'sheet': c.sheet, 'Tech.ID': c['Tech.ID'], 'Tech': t, 'Parameter': p, 'fuel_scenario': 'ALL',
                 'year': int(r.year), 'current_value': cell(t, p, int(r.year)), 'proposed_value': r.proposed_value, 'unit': r.unit,
                 'change_class': r.change_class, 'basis_class': r['class'], 'source_ids': r.source_ids if isinstance(r.source_ids, str) else '',
                 'derivation': r.derivation, 'assumption_sentence': r.assumption_sentence if isinstance(r.assumption_sentence, str) else '',
                 'current_effective_bau': eff(t, p, int(r.year))})
prop = pd.DataFrame(rows)[COLS]
prop.to_csv(os.path.join(J, 'proposals.csv'), index=False)
print('proposals rows', len(prop)); print(prop.groupby(['change_class', 'basis_class']).size().to_string())

# ---- summary
summ = []
for (t, p, s), g in prop.groupby(['Tech', 'Parameter', 'fuel_scenario'], sort=False):
    g = g.set_index('year')
    def cv(y):
        v = g.loc[y, 'current_effective_bau']
        if v == '' or pd.isna(v):
            v = g.loc[y, 'current_value']
        return None if v == '' or pd.isna(v) else float(v)
    rec = {'Tech': t, 'Parameter': p, 'fuel_scenario': s, 'unit': g.unit.iloc[0]}
    for y in (2024, 2030, 2050):
        a, b = cv(y), float(g.loc[y, 'proposed_value'])
        rec[f'current_{y}'] = a
        rec[f'proposed_{y}'] = round(b, 4)
        rec[f'change_pct_{y}'] = (round((b / a - 1) * 100, 1) if a not in (None, 0) else ('new value' if b != 0 else 0.0))
    if p == 'VariableCost' and t.startswith('PP') and rec['current_2024'] not in (None, 0):
        a = rec['current_2024'] * 1000 / 3.6  # current value read as USD/kWh, in USD/GJ
        rec['note'] = (f'current value read as USD/kWh is {a:.4f} USD/GJ; change after that unit conversion '
                       f'{(rec["proposed_2024"] / a - 1) * 100:.1f} percent in 2024')
    else:
        rec['note'] = ''
    rec['change_class'] = ';'.join(sorted(set(g.change_class)))
    rec['basis_class'] = ';'.join(sorted(set(g.basis_class)))
    summ.append(rec)
pd.DataFrame(summ).to_csv(os.path.join(J, 'proposals_summary.csv'), index=False)
print(pd.DataFrame(summ)[['Tech', 'Parameter', 'fuel_scenario', 'current_2024', 'proposed_2024', 'change_pct_2024', 'proposed_2050', 'change_class']].to_string())

# ---- sources: reused ids from LAC_LOCAL_PRICES + new ones
used = set()
for s in prop.source_ids:
    used |= {x.strip() for x in str(s).split(';') if x.strip()}
pp = pd.read_csv(os.path.join(J, 'price_points_2024.csv'), dtype=str)
for s in pp.source_id:
    used |= {x.strip() for x in str(s).split(';') if x.strip()}
const = pd.concat([pd.read_csv(os.path.join(J, 'work', 'fuel_constants.csv'))] +
                  [pd.read_csv(os.path.join(J, 'work', f)) for f in ('plant_constants.csv',) if os.path.isfile(os.path.join(J, 'work', f))],
                  ignore_index=True)
used |= set(const.source_id.dropna())
used |= {'GEN-001', 'GEN-003', 'GUA-001'}  # constants inside the reused 2024 price rows (gallons per tonne, NIST, exchange rate)
lp = pd.read_csv(os.path.join(LP, 'sources.csv'), dtype=str).drop_duplicates('id')
lp = lp[lp.id.isin(used)]
reused = pd.DataFrame({'source_id': lp.id, 'url': lp.url, 'title': lp.title, 'publisher': lp.publisher, 'edition_or_date': lp.date,
                       'retrieval_date': lp.retrieval_date,
                       'downloaded_file': lp.downloaded_file.str.replace(r'^GUA/', 'lp_GUA/', regex=True).str.replace(r'^GEN/', 'lp_GEN/', regex=True)
                                          .str.replace(r';\s*GUA/', ';lp_GUA/', regex=True),
                       'locator': lp.page_or_table,
                       'notes': 'Reused from LAC_LOCAL_PRICES (same id and downloaded file); supports: ' + lp.rows_and_constants_supported.fillna('')})
new = [pd.read_csv(os.path.join(J, 'work', f), dtype=str) for f in ('fuel_sources.csv', 'intl_sources.csv', 'nat_sources.csv', 'plant_sources_extra.csv')
       if os.path.isfile(os.path.join(J, 'work', f))]
allsrc = pd.concat([reused] + new, ignore_index=True).fillna('')
allsrc = allsrc.drop_duplicates('source_id')
allsrc['cited_in_proposals'] = allsrc.source_id.isin(used).map({True: 'yes', False: 'no (consulted, logged in search_log.csv)'})
allsrc.to_csv(os.path.join(J, 'sources.csv'), index=False)
missing = sorted(used - set(allsrc.source_id))
print('sources', len(allsrc), 'cited', (allsrc.cited_in_proposals == 'yes').sum(), 'missing ids', missing)

# ---- constants
const.to_csv(os.path.join(J, 'constants.csv'), index=False)
# ---- search log
logs = [pd.read_csv(os.path.join(J, 'work', f), dtype=str) for f in ('fuel_search_log.csv', 'intl_search_log.csv', 'nat_search_log.csv', 'plant_search_log_extra.csv')
        if os.path.isfile(os.path.join(J, 'work', f))]
pd.concat(logs, ignore_index=True)[['row', 'lead', 'url_or_query', 'date', 'result']].to_csv(os.path.join(J, 'search_log.csv'), index=False)
