"""Step 8: assemble proposals.csv, proposals_summary.csv, sources.csv, constants.csv and search_log.csv.

Usage: py -I step8_build_outputs.py <repo root> <job folder>
Inputs in the job folder: cost_rows_current.csv, fuel_prices.csv, plant_costs.csv,
scripts/sources_fuel.csv, scripts/sources_plants.csv, scripts/search_log_fuel.csv,
scripts/search_log_plants.csv, scripts/fuel_constants_part.csv, scripts/plant_constants_part.csv.
"""
import os, sys
import pandas as pd

ROOT, JOB = sys.argv[1], sys.argv[2]
S = os.path.join(JOB, 'scripts')
LP = os.path.join(ROOT, '_LAC_HUB', 'local_prices_20261109T085226Z')
YEARS = [str(y) for y in range(2021, 2051)]

cur = pd.read_csv(os.path.join(JOB, 'cost_rows_current.csv'))
cur.columns = [str(c) for c in cur.columns]
fuel = pd.read_csv(os.path.join(JOB, 'fuel_prices.csv'))
plant = pd.read_csv(os.path.join(JOB, 'plant_costs.csv'))

F5 = ('ASSUMPTION: natural gas prices published per MMBtu are on a gross calorific basis and are converted to the models\' net basis by dividing by 0.9 '
      '(net = 0.9 x gross for natural gas, UN Statistics Division), for all six countries and all years. Reason: natural gas in the Americas, Henry Hub '
      'included, is priced on a gross basis, and the energy balances behind the models follow the UN recommendation to use net values (IRES, UN 2018). '
      'Check: EIA reports US natural gas at 1,037 Btu per cubic foot, a gross value. Range: a source already on a net basis would be overstated by about 11 percent.')
NGS = ('ASSUMPTION: the Costa Rica natural gas supply price is 7.763 USD/GJ gross (8.626 USD/GJ net) in 2024, real 2024 USD, at import level, and moves with '
       'Henry Hub before 2026 and with the IEA WEO 2025 United States gas price after 2025. Reason: Costa Rica has no natural gas imports, LNG terminal or gas '
       'network, so the price is the delivered cost of a first small-scale LNG supply from the US Gulf Coast: the 2024 Henry Hub average of 2.08 USD/GJ '
       '(2.19 USD/MMBtu / 1.055056 GJ/MMBtu) plus 4.26 USD/GJ for liquefaction and export plus 1.42 USD/GJ for small-scale shipping and regasification. '
       'Check: the Honduras system operator expansion plan 2026-2035 builds its delivered LNG price on Henry Hub plus 15 percent buyer costs, 2 USD/MMBtu '
       'liquefaction and 0.3 USD/MMBtu shipping and import, which gives about 5.5 USD/GJ for 2024. Range: 5.5 to 12 USD/GJ gross.')


def curval(sheet_tech, param, y):
    r = cur[(cur.Tech == sheet_tech) & (cur.Parameter == param)]
    if r.empty:
        return None, None, None
    r = r.iloc[0]
    v = r[y]
    return (None if pd.isna(v) else float(v)), r['sheet'], r['Tech.ID']


rows = []
# fuel rows
for _, f in fuel.iterrows():
    y = str(f.year)
    cv, sheet, tid = curval(f.row, 'VariableCost', y)
    basis = 'ASSUMPTION' if f.row == 'IMPNGS' else f.case
    rows.append(dict(country='CostaRica', sheet=sheet, **{'Tech.ID': tid}, Tech=f.row, Parameter='VariableCost', fuel_scenario=f.scenario,
                     year=int(f.year), current_value=cv, proposed_value=round(f.value_usd_per_gj_net_real2024, 4), unit='MUSD/PJ',
                     change_class='fill_empty' if cv is None else 'replace', basis_class=basis, source_ids=f.source_ids,
                     derivation='%s; r case %s; %s' % (f.derivation, f.r_case, f.r_method),
                     assumption_sentence=(NGS + ' ' + F5) if f.row == 'IMPNGS' else ''))
# plant rows
CC = {'matched': 'keep', 'matched, newer edition': 'upgrade', 'replace': 'replace', 'ASSUMPTION': 'replace'}
for _, p in plant.iterrows():
    y = str(p.year)
    cv, sheet, tid = curval(p.technology, p.parameter, y)
    pv = None if pd.isna(p.proposed_value) else float(p.proposed_value)
    cc = CC[p['class']]
    if cv is None and pv is not None:
        cc = 'fill_empty'
    elif p['class'] == 'ASSUMPTION' and cv is not None and pv is not None and abs(cv - pv) < 1e-9:
        cc = 'keep'
    unit = {'CapitalCost': 'MUSD/GW', 'FixedCost': 'MUSD/GW', 'VariableCost': 'MUSD/PJ'}[p.parameter]
    rows.append(dict(country='CostaRica', sheet=sheet, **{'Tech.ID': tid}, Tech=p.technology, Parameter=p.parameter, fuel_scenario='ALL',
                     year=int(p.year), current_value=cv, proposed_value=pv, unit=unit, change_class=cc, basis_class=p['class'],
                     source_ids=p.source_ids, derivation=p.derivation,
                     assumption_sentence='' if pd.isna(p.assumption_sentence) else p.assumption_sentence))
prop = pd.DataFrame(rows)
prop.to_csv(os.path.join(JOB, 'proposals.csv'), index=False)

# summary
summ = []
for (t, par), g in prop.groupby(['Tech', 'Parameter'], sort=False):
    gg = g[g.fuel_scenario.isin(['ALL', 'STEPS'])].set_index('year')
    d = dict(Tech=t, Parameter=par, scenario='STEPS' if t.startswith('IMP') else 'ALL', change_class=';'.join(sorted(set(g.change_class))),
             basis_class=';'.join(sorted(set(g.basis_class))))
    for y in (2024, 2030, 2050):
        c, p_ = gg.loc[y, 'current_value'], gg.loc[y, 'proposed_value']
        d['current_%d' % y] = c
        d['proposed_%d' % y] = p_
        d['change_pct_%d' % y] = (round(100 * (p_ - c) / c, 1) if (pd.notna(c) and pd.notna(p_) and c != 0) else '')
    summ.append(d)
pd.DataFrame(summ).to_csv(os.path.join(JOB, 'proposals_summary.csv'), index=False)

# sources: new ones plus reused LAC_LOCAL_PRICES ones that are cited
srcs = pd.concat([pd.read_csv(os.path.join(S, 'sources_fuel.csv')), pd.read_csv(os.path.join(S, 'sources_plants.csv'))])
cited = set()
for col in (prop.source_ids, pd.read_csv(os.path.join(JOB, 'price_points_2024.csv')).source_ids,
            pd.read_csv(os.path.join(JOB, 'structure_proposals.csv')).source_ids):
    for v in col.dropna():
        cited.update(x.strip() for x in str(v).split(';') if x.strip())
keep_c = ['GJ_PER_MMBTU', 'KCAL_TO_KJ', 'MMBTU_PER_MCF_EIA', 'UN_NGS_NET_PER_GROSS', 'UN_BBL_PER_T_CRU', 'IPCC_NCV_CRU', 'IPCC_NCV_COK', 'CR_FX_2024']
_lpc = pd.read_csv(os.path.join(LP, 'constants.csv'))
for v in list(_lpc[_lpc.name.isin(keep_c)].source_id) + list(pd.read_csv(os.path.join(S, 'fuel_constants_part.csv')).source_id) + list(pd.read_csv(os.path.join(S, 'plant_constants_part.csv')).source_id):
    cited.update(x.strip() for x in str(v).split(';') if x.strip())
lps = pd.read_csv(os.path.join(LP, 'sources.csv'))
reuse = lps[lps.id.isin(cited - set(srcs.id))].copy()
reuse['downloaded_file'] = 'reused/' + reuse['downloaded_file']
reuse['retrieval_date'] = reuse['retrieval_date'].astype(str) + ' (opened again 2026-11-10)'
reuse['title'] = reuse['title'] + ' [source id reused from LAC_LOCAL_PRICES]'
allsrc = pd.concat([srcs, reuse[srcs.columns]])
allsrc.to_csv(os.path.join(JOB, 'sources.csv'), index=False)
missing = cited - set(allsrc.id)
print('sources', len(allsrc), 'reused', len(reuse), 'missing', sorted(missing))

# constants: reused generic constants used here plus new ones
lpc = pd.read_csv(os.path.join(LP, 'constants.csv'))
keep = ['GJ_PER_MMBTU', 'KCAL_TO_KJ', 'MMBTU_PER_MCF_EIA', 'UN_NGS_NET_PER_GROSS', 'UN_BBL_PER_T_CRU', 'IPCC_NCV_CRU', 'IPCC_NCV_COK', 'CR_FX_2024']
con = pd.concat([lpc[lpc.name.isin(keep)], pd.read_csv(os.path.join(S, 'fuel_constants_part.csv')), pd.read_csv(os.path.join(S, 'plant_constants_part.csv'))])
con.to_csv(os.path.join(JOB, 'constants.csv'), index=False)
# search log
sl = pd.concat([pd.read_csv(os.path.join(S, 'search_log_fuel.csv')), pd.read_csv(os.path.join(S, 'search_log_plants.csv'))])
sl.to_csv(os.path.join(JOB, 'search_log.csv'), index=False)
print('proposals', len(prop), prop.groupby('change_class').size().to_dict(), prop.groupby('basis_class').size().to_dict())
