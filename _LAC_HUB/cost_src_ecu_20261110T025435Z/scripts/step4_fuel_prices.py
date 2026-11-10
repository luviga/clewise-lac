"""Step 4: fuel supply price series for Ecuador (rules F1 to F6 of the brief).

Usage: py -I step4_fuel_prices.py <job_folder> <local_prices_folder> [<ngs_history_csv>]
Inputs (read-only):
  <local_prices_folder>/local_prices_2024.csv, local_history.csv
  <job>/downloads/_extract/ben_benchmarks_annual.csv, ben_cpi_annual.csv, weo2025_fuel_prices.csv
  optional NGS history: csv with year,value_usd_per_gj_gross_nominal,source_id
Outputs: <job>/fuel_prices.csv, <job>/price_points_2024.csv, <job>/downloads/_extract/constants_fuel.csv,
         <job>/downloads/_extract/fuel_summary.csv
"""
import sys, os
import pandas as pd

job, lp = sys.argv[1], sys.argv[2]
ngs_hist_path = sys.argv[3] if len(sys.argv) > 3 else None
X = os.path.join(job, 'downloads', '_extract')
YEARS = list(range(2021, 2051))
SCEN = {'STEPS': 'Stated Policies Scenario (STEPS)', 'CPS': 'Current Policies Scenario (CPS)',
        'NZE': 'Net Zero Emissions by 2050 Scenario (NZE)'}
NET_PER_GROSS = 0.9  # UN_NGS_NET_PER_GROSS, GEN-006

lp24 = pd.read_csv(os.path.join(lp, 'local_prices_2024.csv'))
lp24 = lp24[lp24.country == 'Ecuador'].reset_index(drop=True)
hist = pd.read_csv(os.path.join(lp, 'local_history.csv'))
hist = hist[hist.country == 'Ecuador']
ben = pd.read_csv(os.path.join(X, 'ben_benchmarks_annual.csv'))
cpi = pd.read_csv(os.path.join(X, 'ben_cpi_annual.csv')).set_index('year')['annual_average'].to_dict()
weo = pd.read_csv(os.path.join(X, 'weo2025_fuel_prices.csv'))

const = []  # name,value,unit,source_id,page_or_table,derivation
for y in range(2018, 2026):
    const.append((f'US_CPIU_{y}', cpi[y], 'index 1982-84=100, annual average', 'BEN-004',
                  'BLS CUUR0000SA0 annual average (period M13)', 'as published'))


def defl(v, y):
    return v * cpi[2024] / cpi[y]


def bench_series(name):
    b = ben[ben.series.str.contains(name, regex=False)]
    return {int(r.year): float(r.value) for r in b.itertuples()}, b.source_id.iloc[0], b.unit.iloc[0]


BENCH = {
    'Brent': ('EIA Brent spot FOB (RBRTE)', 'IEA crude oil'),
    'Coal AU': ('Coal, Australian', 'Steam coal Japan'),
}
bdata = {}
for k, (bname, _) in BENCH.items():
    ser, sid, unit = bench_series(bname)
    bdata[k] = (ser, sid, unit)
    for y in range(2018, 2026):
        const.append((f'BENCH_{k.replace(" ", "_").upper()}_{y}', ser[y], unit, sid, 'annual average', 'as published, nominal'))


def weo_path(series, s):
    w = weo[weo.series == series]
    v24 = float(w[w.year == 2024].value.iloc[0])
    ws = w[w.scenario == SCEN[s]]
    v35 = float(ws[ws.year == 2035].value.iloc[0]); v50 = float(ws[ws.year == 2050].value.iloc[0])
    out = {}
    for y in range(2024, 2051):
        if y <= 2035:
            out[y] = v24 + (v35 - v24) * (y - 2024) / 11
        else:
            out[y] = v35 + (v50 - v35) * (y - 2035) / 15
    return out, (v24, v35, v50), w.unit.iloc[0]


for series in ['IEA crude oil', 'Steam coal Japan']:
    for s in SCEN:
        _, (v24, v35, v50), unit = weo_path(series, s)
        for y, v in ((2024, v24), (2035, v35), (2050, v50)):
            if s != 'STEPS' and y == 2024:
                continue
            const.append((f'WEO2025_{series.replace(" ", "_").upper()}_{"HIST" if y == 2024 else s}_{y}', v,
                          unit + ', 2024 USD (MER)', 'BEN-005', 'WEO 2025 Table 2.3, page 109', 'as published'))

# Row definitions: chosen point per F2 and section 5 country notes
ROWS = {
    'DIST_COA': dict(fuel='coal (anthracite)', point='import CIF', bench='Coal AU', note='import CIF is the first published pre-tax point'),
    'DIST_COK': dict(fuel='petroleum coke', point='import CIF', bench='Brent', note='import CIF is the first published pre-tax point'),
    'DIST_CRU': dict(fuel='crude oil', point='export FOB', bench='Brent', src='ECU-001', note='Ecuador exports crude and imports none; export FOB per F2 and decision 6'),
    'DIST_DSL': dict(fuel='diesel', point='import CIF', bench='Brent', note='terminal prices are administered; market import unit value used (decision 2)'),
    'DIST_FOI': dict(fuel='fuel oil', point='export FOB', bench='Brent', note='fuel oil at export value (decision 6)'),
    'DIST_GSL': dict(fuel='gasoline', point='import CIF', bench='Brent', note='terminal prices are administered; market import unit value used (decision 2)'),
    'DIST_JET': dict(fuel='jet fuel', point='import CIF', bench='Brent', note='terminal prices are administered; market import unit value used (decision 2)'),
    'DIST_KER': dict(fuel='kerosene (Diesel 1)', point='wholesale import parity', bench='Brent', note='no import CIF or export FOB is published for kerosene; the industrial terminal price excluding VAT is the closest pre-tax point'),
    'DIST_LPG': dict(fuel='LPG', point='import CIF', bench='Brent', note='terminal prices are administered; market import unit value used (decision 2)'),
    'DIST_NGS': dict(fuel='natural gas', point='generator delivered', bench=None, note='Ecuador gas at its domestic price to generators (decision 6); no import benchmark'),
}

pp_rows, fp_rows, summ = [], [], []
for code, d in ROWS.items():
    sub = lp24[lp24.model_code == code]
    ch = sub[sub.price_point == d['point']]
    if 'src' in d:
        ch = ch[ch.source_id == d['src']]
    ch = ch.iloc[0]
    v24 = float(ch.value_usd_per_gj)
    srcs24 = str(ch.source_id)
    gross = code == 'DIST_NGS'
    v24n = v24 / NET_PER_GROSS if gross else v24
    # price points beside the chosen one
    for r in sub.itertuples():
        is_ch = (r.Index == ch.name)
        val = r.value_usd_per_gj / NET_PER_GROSS if gross else r.value_usd_per_gj
        pp_rows.append(dict(row=code, fuel=d['fuel'], price_point=r.price_point, chosen='yes' if is_ch else 'no',
                            price_as_published=r.price_as_published, unit_as_published=r.unit,
                            tax_treatment=r.tax_treatment, evidence_class=r.evidence_class,
                            value_usd_per_gj_as_recorded=round(r.value_usd_per_gj, 4),
                            value_usd_per_gj_net=round(val, 4),
                            diff_vs_chosen_percent='' if is_ch else round(100 * (val - v24n) / v24n, 1),
                            source_ids=r.source_id, reason=d['note'] if is_ch else ''))
    # observed history (chosen point) in real 2024 USD
    h = hist[(hist.model_code == code) & (hist.price_point == d['point'])]
    obs = {int(r.year): defl(float(r.value_usd_per_gj), int(r.year)) for r in h.itertuples()}
    hsrc = ';'.join(sorted(set(h.source_id.astype(str)))) if len(h) else ''
    if gross and ngs_hist_path:
        g = pd.read_csv(ngs_hist_path)
        obs = {int(r.year): defl(float(r.value_usd_per_gj_gross_nominal), int(r.year)) / NET_PER_GROSS for r in g.itertuples()}
        hsrc = ';'.join(sorted(set(g.source_id.astype(str))))
    obs_model = dict(obs)
    obs_model[2024] = v24n  # 2024 is the chosen published point
    if code == 'DIST_NGS':
        obs_model = {y: v for y, v in obs_model.items() if y <= 2025}
        flat = sum(v for y, v in obs_model.items()) / len(obs_model)
        for s in SCEN:
            for y in YEARS:
                if y in obs_model:
                    case, val, src = 'observed', obs_model[y], (srcs24 if y == 2024 else hsrc)
                elif y < 2024:
                    case, val, src = 'history from ratio', flat, srcs24 + (';' + hsrc if hsrc else '')
                else:
                    case, val, src = 'projected', flat, srcs24 + (';' + hsrc if hsrc else '')
                fp_rows.append(dict(row=code, fuel=d['fuel'], year=y, scenario=s, value_usd_per_gj=round(val, 4), case=case,
                                    r='', r_case='administered domestic price, no benchmark: held flat in real terms at the mean of observed real net values (%s)' % ','.join(str(k) for k in sorted(obs_model)),
                                    benchmark='none', weo_series='none',
                                    source_ids=src + ';BEN-004;GEN-005;GEN-006;GEN-008'))
        summ.append(dict(row=code, chosen_point=d['point'], v2024=round(v24n, 3), r='', r_case='flat at observed mean %.3f' % flat,
                         steps2030=round(flat, 3), steps2050=round(flat, 3), cps2050=round(flat, 3), nze2050=round(flat, 3),
                         join_step_pct=round(100 * (flat - obs_model[max(obs_model)]) / obs_model[max(obs_model)], 1)))
        continue
    bser, bsid, bunit = bdata[d['bench']]
    breal = {y: defl(v, y) for y, v in bser.items()}
    # r per F4
    if obs:
        ratios = {y: obs[y] / breal[y] for y in obs}
        r = sum(ratios.values()) / len(ratios)
        r_case = 'mean over %d history years %d-%d of chosen point / benchmark (real 2024 USD)' % (len(ratios), min(ratios), max(ratios))
    else:
        r = v24n / breal[2024]
        r_case = '2024 ratio alone (no history for the chosen point or for import CIF)'
    weo_series = BENCH[d['bench']][1]
    last_obs = max(obs_model)
    for s in SCEN:
        wp, _, _ = weo_path(weo_series, s)
        for y in YEARS:
            if y in obs_model:
                case, val = 'observed', obs_model[y]
                src = srcs24 if y == 2024 else hsrc
            elif y < 2024:
                case, val = 'history from ratio', r * breal[y]
                src = srcs24 + ';' + bsid
            else:
                case, val = 'projected', r * breal[2024] * wp[y] / wp[2024]
                src = srcs24 + (';' + hsrc if hsrc else '') + ';' + bsid + ';BEN-005'
            fp_rows.append(dict(row=code, fuel=d['fuel'], year=y, scenario=s, value_usd_per_gj=round(val, 4), case=case,
                                r=round(r, 6), r_case=r_case, benchmark='%s (%s, %s)' % (BENCH[d['bench']][0], bsid, bunit),
                                weo_series='WEO 2025 Table 2.3 %s, %s' % (weo_series, s),
                                source_ids=src + ';BEN-004'))
    get = lambda s, y: [x for x in fp_rows if x['row'] == code and x['scenario'] == s and x['year'] == y][0]['value_usd_per_gj']
    first_proj = last_obs + 1
    summ.append(dict(row=code, chosen_point=d['point'], v2024=round(v24n, 3), r=round(r, 6), r_case=r_case,
                     steps2030=get('STEPS', 2030), steps2050=get('STEPS', 2050), cps2050=get('CPS', 2050), nze2050=get('NZE', 2050),
                     join_step_pct=round(100 * (get('STEPS', first_proj) - get('STEPS', last_obs)) / get('STEPS', last_obs), 1)))

# DIST_OPE: no published point in local_prices_2024.csv; ASSUMPTION: follows the fuel oil export series
for x in [x for x in fp_rows if x['row'] == 'DIST_FOI']:
    y = dict(x); y['row'] = 'DIST_OPE'; y['fuel'] = 'other petroleum products'
    y['case'] = 'ASSUMPTION (fuel oil export value and path)'
    fp_rows.append(y)
const.append(('GJ_PER_MMBTU', 1.055056, 'GJ per MMBtu', 'GEN-003', 'Appendix B.8, page 45', 'Btu_IT = 1055.056 J'))
const.append(('UN_NGS_NET_PER_GROSS', 0.9, 'ratio net to gross calorific value for natural gas', 'GEN-006', 'Units of measurement and conversion page', 'as published'))
const.append(('USD_PER_GJ_PER_USD_PER_MWH', 0.27778, 'USD/GJ per USD/MWh', 'GEN-003', 'Appendix B.8, page 45', '1 MWh = 3.6 GJ'))
pd.DataFrame(fp_rows).to_csv(os.path.join(job, 'fuel_prices.csv'), index=False)
pd.DataFrame(pp_rows).to_csv(os.path.join(job, 'price_points_2024.csv'), index=False)
pd.DataFrame(const, columns=['name', 'value', 'unit', 'source_id', 'page_or_table', 'derivation']).to_csv(
    os.path.join(X, 'constants_fuel.csv'), index=False)
pd.DataFrame(summ).to_csv(os.path.join(X, 'fuel_summary.csv'), index=False)
print(pd.DataFrame(summ).to_string())
