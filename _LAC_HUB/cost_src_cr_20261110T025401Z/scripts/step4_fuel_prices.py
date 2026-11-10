"""Step 4: fuel supply price series for Costa Rica (rules F1 to F6).

Usage: py -I step4_fuel_prices.py <repo root> <job folder>
Reads LAC_LOCAL_PRICES outputs from the repo and benchmark files from <job>/downloads.
Writes fuel_prices.csv, price_points_2024.csv and scripts/fuel_constants_part.csv (merged later).
"""
import json, os, sys
import pandas as pd

ROOT, JOB = sys.argv[1], sys.argv[2]
LP = os.path.join(ROOT, '_LAC_HUB', 'local_prices_20261109T085226Z')
DL = os.path.join(JOB, 'downloads')

# ---------- constants from sources ----------
cpi = {}
d = json.load(open(os.path.join(DL, 'bls_CUUR0000SA0_2017_2025_annualaverage.json')))
for x in d['Results']['series'][0]['data']:
    if x['period'] == 'M13':
        cpi[int(x['year'])] = float(x['value'])


def eia_annual(fname, key):
    x = pd.read_excel(os.path.join(DL, fname), 'Data 1', header=2)
    col = [c for c in x.columns if key in str(c)][0]
    x['Y'] = pd.to_datetime(x['Date']).dt.year
    return {int(r.Y): float(r[col]) for _, r in x.iterrows() if r.Y >= 2017}


brent = eia_annual('eia_PET_PRI_SPT_S1_A.xls', 'Brent')          # USD/bbl
hh = eia_annual('eia_NG_PRI_FUT_S1_A.xls', 'Henry Hub')           # USD/MMBtu gross
wb = pd.read_excel(os.path.join(DL, 'WB_CMO_Historical_Data_Annual.xlsx'), 'Annual Prices (Nominal)', header=None)
coal_sa = {int(wb.iloc[i, 0]): float(wb.iloc[i, 6]) for i in range(8, len(wb))
           if str(wb.iloc[i, 0]).strip().isdigit() and int(wb.iloc[i, 0]) >= 2017}  # USD/t, 6000 kcal/kg NAR

BBL_PER_T_CRU, NCV_CRU = 7.32, 42.3          # GEN-001, GEN-002
GJ_PER_MMBTU, NET_PER_GROSS = 1.055056, 0.9  # GEN-003, GEN-006
KCAL_TO_KJ = 4.1868                          # GEN-003
GJ_PER_T_COAL6000 = 6000 * KCAL_TO_KJ / 1000  # 25.1208 GJ/t

# WEO 2025 Table 2.3, page 109, USD (MER, 2024)
WEO = {
    'crude': {'CPS': {2024: 79, 2035: 89, 2050: 106}, 'STEPS': {2024: 79, 2035: 80, 2050: 76}, 'NZE': {2024: 79, 2035: 33, 2050: 25}},
    'gas_us': {'CPS': {2024: 2.2, 2035: 4.5, 2050: 5.0}, 'STEPS': {2024: 2.2, 2035: 3.9, 2050: 4.6}, 'NZE': {2024: 2.2, 2035: 2.1, 2050: 2.2}},
    'coal_eu': {'CPS': {2024: 112, 2035: 92, 2050: 82}, 'STEPS': {2024: 112, 2035: 78, 2050: 66}, 'NZE': {2024: 112, 2035: 47, 2050: 39}},
}
WEO_NAME = {'crude': 'WEO 2025 IEA crude oil (USD/barrel)', 'gas_us': 'WEO 2025 natural gas United States (USD/MBtu)',
            'coal_eu': 'WEO 2025 steam coal European Union (USD/tonne)'}


def weo(series, s, y):
    pts = WEO[series][s]
    ys = sorted(pts)
    if y >= ys[-1]:
        return pts[ys[-1]]
    for a, b in zip(ys, ys[1:]):
        if a <= y <= b:
            return pts[a] + (pts[b] - pts[a]) * (y - a) / (b - a)
    raise ValueError(y)


def bench(kind, y):
    """Observed benchmark, nominal USD/GJ net."""
    if kind == 'brent':
        return brent[y] * BBL_PER_T_CRU / NCV_CRU
    if kind == 'hh':
        return hh[y] / GJ_PER_MMBTU / NET_PER_GROSS
    if kind == 'coal_sa':
        return coal_sa[y] / GJ_PER_T_COAL6000


def real(v, y):
    return v * cpi[2024] / cpi[y]


BENCH_NAME = {'brent': 'EIA Europe Brent Spot Price FOB (RBRTE), annual average',
              'hh': 'EIA Henry Hub Natural Gas Spot Price (RNGWHHD), annual average',
              'coal_sa': 'World Bank Pink Sheet Coal, South African (fob Richards Bay, 6000 kcal/kg), annual average'}
BENCH_SRC = {'brent': 'CRC-002;GEN-001;GEN-002', 'hh': 'CRC-003;GEN-003;GEN-006', 'coal_sa': 'CRC-004;GEN-003'}
BENCH_FORMULA = {'brent': 'Brent USD/bbl x 7.32 bbl/t (UN_BBL_PER_T_CRU, GEN-001) / 42.3 GJ/t (IPCC_NCV_CRU, GEN-002)',
                 'hh': 'Henry Hub USD/MMBtu / 1.055056 GJ/MMBtu (GEN-003) / 0.9 net/gross (GEN-006)',
                 'coal_sa': 'South African coal USD/t / 25.1208 GJ/t (6000 kcal/kg x 4.1868 kJ/kcal, GEN-003)'}

# ---------- row definitions (rule F2 choice; product per brief section 5) ----------
ROWS = {
    'IMPAVG': dict(fuel='aviation gasoline', point='wholesale import parity', prod='Av-Gas', bench='brent', weo='crude', cif_prod='Av-Gas'),
    'IMPCOA': dict(fuel='coal (anthracite)', point='import CIF', prod='anthracite', src_filter='CR-017;CR-018', bench='coal_sa', weo='coal_eu', cif_prod='anthracite'),
    'IMPCOK': dict(fuel='petroleum coke', point='import CIF', prod='petroleum coke', src_filter='CR-016;CR-018', bench='brent', weo='crude', cif_prod='petroleum coke'),
    'IMPFOI': dict(fuel='fuel oil', point='wholesale import parity', prod='Bunker (fuel oil)', bench='brent', weo='crude', cif_prod='Bunker (fuel oil)'),
    'IMPKJF': dict(fuel='jet fuel and kerosene', point='wholesale import parity', prod='jet fuel', bench='brent', weo='crude', cif_prod='jet fuel'),
    'IMPLPG': dict(fuel='LPG', point='wholesale import parity', prod='LPG', bench='brent', weo='crude', cif_prod='LPG'),
    'IMPNGS': dict(fuel='natural gas', point='import CIF', prod='Costa Rica imported no natural gas', bench='hh', weo='gas_us', cif_prod=None),
    'IMPPURDSL': dict(fuel='diesel', point='wholesale import parity', prod='diesel 50 ppm', bench='brent', weo='crude', cif_prod='diesel 50 ppm'),
    'IMPPURGSL': dict(fuel='gasoline', point='wholesale import parity', prod='gasoline RON 91', bench='brent', weo='crude', cif_prod='gasoline RON 91'),
}

lp = pd.read_csv(os.path.join(LP, 'local_prices_2024.csv'))
lp = lp[lp.country == 'CostaRica'].copy()
lh = pd.read_csv(os.path.join(LP, 'local_history.csv'))
lh = lh[lh.country == 'CostaRica'].copy()

MODEL_YEARS = list(range(2021, 2051))
out, pp, summ = [], [], []
for code, R in ROWS.items():
    cand = lp[(lp.model_code == code) & (lp.price_point == R['point']) & lp.notes.astype(str).str.startswith(R['prod'])]
    if 'src_filter' in R:
        cand = cand[cand.source_id == R['src_filter']]
    assert len(cand) == 1, (code, len(cand))
    ch = cand.iloc[0]
    v24 = float(ch.value_usd_per_gj)
    gross = str(ch.calorific_basis).strip() == 'gross'
    if gross:
        v24 = v24 / NET_PER_GROSS
    src_chosen = str(ch.source_id)
    # ---- price points 2024 (F2) ----
    for _, o in lp[lp.model_code == code].iterrows():
        val = float(o.value_usd_per_gj) / (NET_PER_GROSS if str(o.calorific_basis).strip() == 'gross' else 1)
        pp.append(dict(row=code, fuel=R['fuel'], price_point=o.price_point, product_and_scope=str(o.notes)[:160],
                       tax_treatment=o.tax_treatment, value_usd_per_gj_net=round(val, 3),
                       chosen='yes' if o.name == ch.name else 'no',
                       diff_vs_chosen_pct=round(100 * (val - v24) / v24, 1), source_ids=o.source_id,
                       note='natural gas gross value divided by 0.9 (F5)' if str(o.calorific_basis).strip() == 'gross' else ''))
    # ---- history and r (F3, F4) ----
    B = R['bench']
    hist_chosen, hist_cif = {}, {}
    if R['cif_prod']:
        hrows = lh[(lh.model_code == code) & (lh.price_point == 'import CIF') & lh.notes.astype(str).str.startswith(R['cif_prod'])]
        for _, h in hrows.iterrows():
            hist_cif[int(h.year)] = float(h.value_usd_per_gj)
    if R['point'] == 'import CIF' and hist_cif:
        hist_chosen = dict(hist_cif)
        ratios = {y: real(v, y) / real(bench(B, y), y) for y, v in hist_cif.items()}
        r = sum(ratios.values()) / len(ratios)
        case = 'A: chosen point has history'
        rmeth = 'mean over %s of (import CIF real 2024 / benchmark real 2024): %s' % (
            ','.join(map(str, sorted(ratios))), '; '.join('%d %.4f' % (y, ratios[y]) for y in sorted(ratios)))
    elif hist_cif:
        ratios = {y: real(v, y) / real(bench(B, y), y) for y, v in hist_cif.items()}
        rc = sum(ratios.values()) / len(ratios)
        k = v24 / hist_cif[2024]
        r = rc * k
        case = 'B: chosen point has no history; import CIF history used'
        rmeth = ('r = mean CIF ratio %.4f (years %s: %s) x 2024 ratio chosen/CIF %.3f/%.3f = %.4f'
                 % (rc, ','.join(map(str, sorted(ratios))), '; '.join('%d %.4f' % (y, ratios[y]) for y in sorted(ratios)),
                    v24, hist_cif[2024], k))
        hist_chosen = {2024: v24}
    else:
        r = v24 / bench(B, 2024)
        case = 'C: no history; 2024 ratio alone'
        rmeth = 'r = chosen 2024 %.3f / benchmark 2024 %.3f' % (v24, bench(B, 2024))
        hist_chosen = {2024: v24}
    if R['point'] == 'import CIF' and hist_cif:
        hist_chosen[2024] = v24
    B24 = bench(B, 2024)
    srcs = ';'.join(dict.fromkeys(src_chosen.split(';') + BENCH_SRC[B].split(';') + ['CRC-001', 'CRC-005']))
    if gross:
        srcs += ';GEN-005;GEN-008;HON-016'
    vals = {}
    for s in ['STEPS', 'CPS', 'NZE']:
        for y in MODEL_YEARS:
            if y <= 2025:
                if y in hist_chosen:
                    v = real(hist_chosen[y], y) if y != 2024 else v24
                    if y != 2024 and gross:
                        v = v / NET_PER_GROSS
                    cs = 'observed'
                    der = ('%s %d nominal %.3f USD/GJ x CPI 2024 %.3f / CPI %d %.3f (CRC-001)' % (R['point'], y, hist_chosen[y], cpi[2024], y, cpi[y])
                           if y != 2024 else '%s 2024 %.3f USD/GJ%s' % (R['point'], v24, ' (gross 7.763 / 0.9, F5)' if gross else ''))
                else:
                    bn = bench(B, y)
                    v = r * real(bn, y)
                    cs = 'history from ratio'
                    der = 'r %.4f x benchmark %d %.3f USD/GJ nominal x CPI 2024 %.3f / CPI %d %.3f; benchmark = %s' % (
                        r, y, bn, cpi[2024], y, cpi[y], BENCH_FORMULA[B])
            else:
                w = weo(R['weo'], s, y)
                v = r * B24 * w / WEO[R['weo']][s][2024]
                cs = 'projected'
                der = 'r %.4f x B(2024) %.3f USD/GJ x WEO_%s(%d) %.2f / WEO_%s(2024) %.2f (linear between 2024, 2035, 2050)' % (
                    r, B24, s, y, w, s, WEO[R['weo']][s][2024])
            vals[(s, y)] = v
            out.append(dict(row=code, fuel=R['fuel'], year=y, scenario=s, value_usd_per_gj_net_real2024=round(v, 4), case=cs,
                            r=round(r, 4), r_case=case, r_method=rmeth, chosen_point=R['point'], benchmark=BENCH_NAME[B],
                            weo_series=WEO_NAME[R['weo']], source_ids=srcs, derivation=der))
    summ.append(dict(row=code, chosen_point=R['point'], v2024=round(v24, 3), r=round(r, 4), r_case=case[:1],
                     steps2030=round(vals[('STEPS', 2030)], 3), steps2050=round(vals[('STEPS', 2050)], 3),
                     cps2050=round(vals[('CPS', 2050)], 3), nze2050=round(vals[('NZE', 2050)], 3),
                     v2025=round(vals[('STEPS', 2025)], 3), steps2026=round(vals[('STEPS', 2026)], 3),
                     join_step=round(vals[('STEPS', 2026)] - vals[('STEPS', 2025)], 3),
                     join_step_pct=round(100 * (vals[('STEPS', 2026)] / vals[('STEPS', 2025)] - 1), 1)))

pd.DataFrame(out).to_csv(os.path.join(JOB, 'fuel_prices.csv'), index=False)
pd.DataFrame(pp).to_csv(os.path.join(JOB, 'price_points_2024.csv'), index=False)
pd.DataFrame(summ).to_csv(os.path.join(JOB, 'scripts', 'fuel_summary.csv'), index=False)

# constants part
C = []
for y in sorted(cpi):
    C.append(dict(name='US_CPIU_%d' % y, value=cpi[y], unit='index 1982-84=100, annual average', source_id='CRC-001',
                  page_or_table='BLS API series CUUR0000SA0, period M13 (Annual), year %d' % y, derivation='as published'))
for y in range(2018, 2026):
    C.append(dict(name='BRENT_%d' % y, value=brent[y], unit='USD/bbl nominal', source_id='CRC-002',
                  page_or_table='sheet Data 1, column Europe Brent Spot Price FOB (Dollars per Barrel), row %d' % y, derivation='as published'))
    C.append(dict(name='HENRY_HUB_%d' % y, value=hh[y], unit='USD/MMBtu nominal (gross)', source_id='CRC-003',
                  page_or_table='sheet Data 1, column Henry Hub Natural Gas Spot Price (Dollars per Million Btu), row %d' % y, derivation='as published'))
    C.append(dict(name='COAL_SOUTH_AFRICA_%d' % y, value=coal_sa[y], unit='USD/t nominal, 6000 kcal/kg NAR', source_id='CRC-004',
                  page_or_table='sheet Annual Prices (Nominal), column Coal, South African, row %d' % y, derivation='as published'))
C.append(dict(name='GJ_PER_T_COAL_6000KCAL', value=round(GJ_PER_T_COAL6000, 4), unit='GJ per t', source_id='GEN-003',
              page_or_table='Appendix B.8, page 46', derivation='6000 kcal/kg x 4.1868 kJ/kcal (KCAL_TO_KJ) / 1000'))
for ser, d_ in WEO.items():
    for s, pts in d_.items():
        for y, v in pts.items():
            C.append(dict(name='WEO2025_%s_%s_%d' % (ser.upper(), s, y), value=v, unit=WEO_NAME[ser].split('(')[-1].rstrip(')') + ', USD (MER, 2024)',
                          source_id='CRC-005', page_or_table='Table 2.3 Wholesale fossil fuel prices by scenario, page 109',
                          derivation='as published'))
pd.DataFrame(C).to_csv(os.path.join(JOB, 'scripts', 'fuel_constants_part.csv'), index=False)
print(pd.DataFrame(summ).to_string())
