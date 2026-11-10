"""Step 4: fuel supply price series for Guatemala (rules F1 to F6).

Inputs (read only): LAC_LOCAL_PRICES local_prices_2024.csv and local_history.csv,
benchmark files saved in downloads/bench, WEO 2025 Table 2.3 values typed below
(page 109 of downloads/weo/WorldEnergyOutlook2025.pdf).
Outputs: fuel_prices.csv, price_points_2024.csv, work/fuel_constants.csv,
work/fuel_summary.csv in the job folder.
"""
import json, os, sys
import pandas as pd

ROOT, JOB = sys.argv[1], sys.argv[2]
LP = os.path.join(ROOT, '_LAC_HUB/local_prices_20261109T085226Z')
DL = os.path.join(JOB, 'downloads')
YEARS = list(range(2018, 2051))
SCEN = ['STEPS', 'CPS', 'NZE']

# ---------- constants ----------
cpi_json = json.load(open(os.path.join(DL, 'bench/bls_CUUR0000SA0_2017_2025.json')))
CPI = {int(d['year']): float(d['value']) for d in cpi_json['Results']['series'][0]['data'] if d['period'] == 'M13'}
DEF = {y: CPI[2024] / CPI[y] for y in CPI}  # multiply nominal y by this to get real 2024

def eia_annual(fname):
    x = pd.read_excel(os.path.join(DL, 'bench', fname), sheet_name='Data 1', skiprows=2)
    x['year'] = pd.to_datetime(x['Date']).dt.year
    return dict(zip(x['year'], x.iloc[:, 1]))

BRENT = eia_annual('RBRTEa.xls')          # USD/bbl nominal
HH = eia_annual('RNGWHHDa.xls')            # USD/MMBtu nominal, gross
wb = pd.read_excel(os.path.join(DL, 'bench/CMO-Historical-Data-Annual.xlsx'),
                   sheet_name='Annual Prices (Nominal)', header=None)
hdr = wb.iloc[6].tolist()
ci = hdr.index('Coal, South African')
wbr = wb[wb[0].astype(str).str.fullmatch(r'\d{4}')]
COAL_SA = {int(r[0]): float(r[ci]) for _, r in wbr.iterrows() if str(r[ci]) not in ('nan', '..', '…')}

# WEO 2025 Table 2.3, USD (MER, 2024)
WEO = {
    'IEA crude oil': {'unit': 'USD/barrel', 2024: {'ALL': 79}, 2035: {'CPS': 89, 'STEPS': 80, 'NZE': 33}, 2050: {'CPS': 106, 'STEPS': 76, 'NZE': 25}},
    'Natural gas United States': {'unit': 'USD/MBtu', 2024: {'ALL': 2.2}, 2035: {'CPS': 4.5, 'STEPS': 3.9, 'NZE': 2.1}, 2050: {'CPS': 5.0, 'STEPS': 4.6, 'NZE': 2.2}},
    'Steam coal European Union': {'unit': 'USD/tonne', 2024: {'ALL': 112}, 2035: {'CPS': 92, 'STEPS': 78, 'NZE': 47}, 2050: {'CPS': 82, 'STEPS': 66, 'NZE': 39}},
}

def weo(series, s, y):
    t = WEO[series]
    v24, v35, v50 = t[2024]['ALL'], t[2035][s], t[2050][s]
    if y <= 2024:
        return v24
    if y <= 2035:
        return v24 + (v35 - v24) * (y - 2024) / 11
    if y <= 2050:
        return v35 + (v50 - v35) * (y - 2035) / 15
    return v50

BENCH = {
    'brent': {'name': 'EIA Europe Brent Spot Price FOB (RBRTE), annual average', 'unit': 'USD/bbl', 'obs': BRENT, 'src': 'FUE-002', 'weo': 'IEA crude oil'},
    'hh': {'name': 'EIA Henry Hub Natural Gas Spot Price (RNGWHHD), annual average', 'unit': 'USD/MMBtu (gross)', 'obs': HH, 'src': 'FUE-003', 'weo': 'Natural gas United States'},
    'coal': {'name': 'World Bank Pink Sheet Coal, South African (fob Richards Bay, 6000 kcal/kg NAR), annual average', 'unit': 'USD/t', 'obs': COAL_SA, 'src': 'FUE-004', 'weo': 'Steam coal European Union'},
}
SRC_CPI, SRC_WEO = 'FUE-001', 'FUE-005'

# ---------- local data ----------
p = pd.read_csv(os.path.join(LP, 'local_prices_2024.csv'))
p = p[p.country == 'Guatemala'].copy()
h = pd.read_csv(os.path.join(LP, 'local_history.csv'))
h = h[h.country == 'Guatemala'].copy()

# chosen point per row (rule F2). Selector: price_point, and a substring of notes or source to
# disambiguate duplicates.
ROWS = {
    'DIST_COA': dict(fuel='COA', point='import CIF', pick=lambda d: d[d.source_id.str.startswith('GUA-002')], bench='coal',
                      why='import CIF is the first published point in rule F2 order (no wholesale import parity published); Banco de Guatemala customs line chosen over the identical UN Comtrade value because it is the national publisher and carries the history.'),
    'DIST_COK': dict(fuel='COK', point='import CIF', pick=lambda d: d[d.source_id.str.startswith('GUA-002')], bench='brent',
                      why='import CIF is the first published point in rule F2 order; Banco de Guatemala customs line chosen over the identical UN Comtrade value.'),
    'DIST_DSL': dict(fuel='DSL', point='wholesale import parity', pick=lambda d: d, bench='brent',
                      why='wholesale import parity, pre-tax (MEM price structure up to the importer margin) is the first point in rule F2 order.'),
    'DIST_FOI': dict(fuel='FOI', point='wholesale import parity', pick=lambda d: d, bench='brent',
                      why='wholesale import parity (MEM bunker structure ex-rack at Puerto San Jose, IVA removed, IDP zero) is the first point in rule F2 order.'),
    'DIST_GSL': dict(fuel='GSL', point='wholesale import parity', pick=lambda d: d[d.notes.str.contains('regular', case=False)], bench='brent',
                      why='wholesale import parity, pre-tax, is the first point in rule F2 order; the regular gasoline structure is the first published row and the larger import volume; superior is listed in price_points_2024.csv.'),
    'DIST_KER': dict(fuel='KER', point='final consumer pre-tax', pick=lambda d: d, bench='brent',
                      why='the only import CIF line (51.23 USD/GJ) covers 14.8 t in the year, a sample volume and not a market price, so it is set aside; no wholesale or export point is published; the closest pre-tax point is the MEM Guatemala City consumer price with IDP and IVA removed.'),
    'DIST_LPG': dict(fuel='LPG', point='wholesale import parity', pick=lambda d: d[d.unit == 'GTQ/cylinder'], bench='brent',
                      why='wholesale import parity, pre-tax, is the first point in rule F2 order; the 25 lb residential cylinder structure is chosen because residential cylinders are the main LPG use (8 demand consumers); the automotive structure is listed in price_points_2024.csv.'),
    'DIST_NGS': dict(fuel='NGS', point='generator delivered', pick=lambda d: d, bench='hh',
                      why='Guatemala imported no natural gas in 2024 and publishes no import, wholesale or export gas price; the only point is the generator-delivered ASSUMPTION value, converted from gross to net under rule F5.'),
}

NGS_F5 = ("ASSUMPTION: natural gas prices published per MMBtu are on a gross calorific basis and are converted to the models' net basis "
          "by dividing by 0.9 (net = 0.9 x gross for natural gas, UN Statistics Division), for all six countries and all years. Reason: natural "
          "gas in the Americas, Henry Hub included, is priced on a gross basis, and the energy balances behind the models follow the UN "
          "recommendation to use net values (IRES, UN 2018). Check: EIA reports US natural gas at 1,037 Btu per cubic foot, a gross value. "
          "Range: a source already on a net basis would be overstated by about 11 percent.")
NGS_LEVEL = ("ASSUMPTION: natural gas delivered to a power plant in Guatemala costs 7.763 USD/GJ on a gross calorific basis in 2024 "
             "(8.626 USD/GJ net, real 2024 USD), for all model years before scaling with the Henry Hub benchmark. Reason: Guatemala imports "
             "no natural gas, so a plant would buy US liquefied natural gas priced on Henry Hub: the 2024 Henry Hub average of 2.19 USD/MMBtu "
             "(2.076 USD/GJ gross at 1.055056 GJ/MMBtu) plus about 5.69 USD/GJ for liquefaction, shipping and regasification. Check: the "
             "Guatemalan PEG-5 tender bases price contracted gas as Henry Hub plus a bidder adder for liquefaction and transport, and EIA "
             "reports the 2024 price of US LNG exported to Panama at 7.21 USD/Mcf (6.59 USD/GJ gross at 1.037 MMBtu/Mcf) before shipping "
             "and regasification. Range: 6.5 to 10 USD/GJ gross.")

# EXTT_CRU: Guatemala crude oil export FOB from Banco de Guatemala exports by tariff line (KG-103),
# line 2709001000, annual value (USD) and volume (kg). IPCC crude NCV 42.3 GJ/t (GEN-002).
import openpyxl
CRU = {}
CRU_SRC = {2018: 'FUE-011', 2019: 'FUE-012', 2020: 'FUE-013', 2021: 'FUE-014', 2022: 'FUE-015', 2023: 'FUE-016', 2024: 'FUE-007', 2025: 'FUE-017'}
for y in range(2018, 2026):
    ws = openpyxl.load_workbook(os.path.join(DL, f'cru/KG-103_{y}.xlsx'), read_only=True, data_only=True).worksheets[0]
    for r in ws.iter_rows(values_only=True):
        r = list(r)
        hit = [j for j, v in enumerate(r) if v is not None and str(v).strip() == '2709001000']
        if hit:
            j = hit[0]
            usd_t = float(r[j + 1]) / float(r[j + 2]) * 1000
            CRU[y] = (usd_t, usd_t / 42.3)
            break
cru_rows = []
for y, (usd_t, v) in CRU.items():
    cru_rows.append({'country': 'Guatemala', 'model_code': 'EXTT_CRU', 'price_point': 'export FOB', 'year': y,
                     'value_usd_per_gj': v, 'source_id': f'{CRU_SRC[y]};GEN-002', 'usd_t': usd_t})
h = pd.concat([h, pd.DataFrame([c for c in cru_rows if c['year'] != 2024])], ignore_index=True)
c24 = [c for c in cru_rows if c['year'] == 2024][0]
p = pd.concat([p, pd.DataFrame([{'country': 'Guatemala', 'fuel': 'CRU', 'model_code': 'EXTT_CRU', 'price_point': 'export FOB',
                                 'price_as_published': round(c24['usd_t'], 4), 'unit': 'USD/t', 'tax_treatment': 'FOB, exports carry no tax',
                                 'value_usd_per_gj': c24['value_usd_per_gj'], 'source_id': 'FUE-007;FUE-008;GEN-002',
                                 'page_or_table': 'KG-103_2024 sheet Expo row 706, line 2709001000, columns C (value USD) and D (volume kg); IPCC crude NCV 42.3 GJ/t',
                                 'notes': 'Crude oil export unit value, Banco de Guatemala customs; FOB basis confirmed by Cuadro 1 (VALOR (FOB)), whose January 2024 total equals the KG-103 January total within 0.001 percent.'}])], ignore_index=True)
ROWS['EXTT_CRU'] = dict(fuel='CRU', point='export FOB', pick=lambda d: d, bench='brent',
                        why='Guatemala exports its crude oil and imports none for refining; no import or wholesale crude price exists, so export FOB is the point in rule F2 order (Banco de Guatemala customs unit value of line 2709001000).')

def history_row(code, point):
    d = h[(h.model_code == code) & (h.price_point == point)]
    return {int(r.year): (float(r.value_usd_per_gj), str(r.source_id)) for _, r in d.iterrows()}

recs, summ, ppoints = [], [], []
for code, cfg in ROWS.items():
    cand = p[(p.model_code == code) & (p.price_point == cfg['point'])]
    ch = cfg['pick'](cand)
    assert len(ch) == 1, (code, len(ch))
    ch = ch.iloc[0]
    v24 = float(ch.value_usd_per_gj)
    src24 = str(ch.source_id)
    is_gas = code == 'DIST_NGS'
    if is_gas:
        v24 = v24 / 0.9  # gross to net, F5
    b = BENCH[cfg['bench']]
    Bobs = b['obs']
    Breal = {y: Bobs[y] * DEF[y] for y in range(2018, 2026)}
    # local history of the chosen point (nominal) -> real 2024
    hist = history_row(code, cfg['point'])
    hist_real = {y: (v * DEF[y] / (0.9 if is_gas else 1), s) for y, (v, s) in hist.items()}
    hist_real[2024] = (v24, src24)  # 2024 observed from the 2024 file
    # r
    own_years = sorted(y for y in hist_real if y in Breal)
    if len(own_years) > 1:
        rs = [hist_real[y][0] / Breal[y] for y in own_years]
        r = sum(rs) / len(rs)
        rcase = f'case 1: mean over {own_years[0]} to {own_years[-1]} ({len(rs)} years) of chosen point / benchmark, both real 2024'
    else:
        cif = history_row(code, 'import CIF')
        cif_real = {y: v * DEF[y] for y, (v, s) in cif.items()}
        if cif_real:
            yrs = sorted(y for y in cif_real if y in Breal)
            rs = [cif_real[y] / Breal[y] for y in yrs]
            r_cif = sum(rs) / len(rs)
            k = v24 / cif_real[2024]
            r = r_cif * k
            cif_src = ';'.join(sorted({s for (v, s) in cif.values()}))
            rcase = (f'case 2: mean over {yrs[0]} to {yrs[-1]} ({len(yrs)} years) of import CIF / benchmark = {r_cif:.6f}, '
                     f'times 2024 ratio chosen point / import CIF = {v24:.4f} / {cif_real[2024]:.4f} = {k:.6f} (import CIF history {cif_src})')
        else:
            r = v24 / Breal[2024]
            rcase = f'case 3: no history; 2024 ratio alone = {v24:.4f} / {Breal[2024]:.4f}'
    hsrc = ';'.join(sorted({s for (v, s) in hist_real.values()}))
    base_src = f"{hsrc};{b['src']};{SRC_CPI}"
    last_obs = None
    vals = {}
    for y in YEARS:
        for s in SCEN:
            if y <= 2025:
                if y in hist_real:
                    v, srcs = hist_real[y]
                    case = 'observed'
                    der = (f"observed {cfg['point']} {y}" + (f" nominal {hist[y][0]:.4f} USD/GJ x CPI-U 2024/{y} {CPI[2024]}/{CPI[y]}" if y != 2024 and y in hist else '')
                           + (f" / 0.9 gross to net" if is_gas and y != 2024 else '') + f" = {v:.4f} USD/GJ real 2024")
                    if y == 2024:
                        der = f"observed {cfg['point']} 2024 = {float(ch.value_usd_per_gj):.4f} USD/GJ" + (" gross / 0.9 = %.4f net" % v24 if is_gas else '')
                    sids = f"{srcs};{SRC_CPI}" if y != 2024 else srcs
                else:
                    v = r * Breal[y]
                    case = 'history from ratio'
                    der = (f"r {r:.6f} x {b['name'].split(',')[0]} {y} {Bobs[y]:.2f} {b['unit']} x CPI-U {CPI[2024]}/{CPI[y]} = {v:.4f} USD/GJ real 2024")
                    sids = f"{b['src']};{SRC_CPI};{src24}"
            else:
                w = weo(b['weo'], s, y)
                v = r * Breal[2024] * w / WEO[b['weo']][2024]['ALL']
                case = 'projected'
                der = (f"r {r:.6f} x B(2024) {Bobs[2024]:.2f} {b['unit']} x WEO 2025 {s} {b['weo']} {y} {w:.4f} / 2024 {WEO[b['weo']][2024]['ALL']} "
                       f"(linear between 2024, 2035, 2050) = {v:.4f} USD/GJ real 2024")
                sids = f"{src24};{b['src']};{SRC_WEO}"
            if is_gas:
                sids = sids + ';GEN-005;GEN-006;GEN-008;GUA-006;FUE-006'
            vals[(y, s)] = v
            recs.append({'row': code, 'fuel': cfg['fuel'], 'year': y, 'scenario': s, 'value_usd_per_gj_net_real2024': round(v, 4),
                         'case': case, 'r': round(r, 6), 'r_method': rcase, 'benchmark': b['name'],
                         'weo_series': f"WEO 2025 Table 2.3 {b['weo']} ({WEO[b['weo']]['unit']}, USD MER 2024)",
                         'source_ids': ';'.join(dict.fromkeys(x for x in sids.split(';') if x)), 'derivation': der,
                         'assumption_sentence': (NGS_LEVEL + ' ' + NGS_F5) if is_gas else '', 'chosen_point': cfg['point'],
                         'chosen_point_reason': cfg['why']})
    step = {s: (vals[(2026, s)] / vals[(2025, s)] - 1) * 100 for s in SCEN}
    summ.append({'row': code, 'chosen_point': cfg['point'], 'value_2024': round(v24, 4), 'r': round(r, 6), 'r_case': rcase.split(':')[0],
                 'STEPS_2030': round(vals[(2030, 'STEPS')], 4), 'STEPS_2050': round(vals[(2050, 'STEPS')], 4),
                 'CPS_2050': round(vals[(2050, 'CPS')], 4), 'NZE_2050': round(vals[(2050, 'NZE')], 4),
                 'value_2025': round(vals[(2025, 'STEPS')], 4), 'case_2025': [x for x in recs if x['row'] == code and x['year'] == 2025][0]['case'],
                 'STEPS_2026': round(vals[(2026, 'STEPS')], 4), 'step_2025_2026_pct_STEPS': round(step['STEPS'], 2),
                 'step_pct_CPS': round(step['CPS'], 2), 'step_pct_NZE': round(step['NZE'], 2), 'benchmark': cfg['bench']})
    # price points 2024 (rule F2): all other published points for the row
    for _, q in p[p.model_code == code].iterrows():
        val = float(q.value_usd_per_gj) / (0.9 if is_gas else 1)
        chosen = (q.name == ch.name)
        ppoints.append({'row': code, 'price_point': q.price_point, 'chosen': 'yes' if chosen else 'no',
                        'value_usd_per_gj_net': round(val, 4), 'diff_vs_chosen_pct': round((val / v24 - 1) * 100, 2),
                        'price_as_published': q.price_as_published, 'unit_as_published': q.unit, 'tax_treatment': q.tax_treatment,
                        'source_id': q.source_id, 'page_or_table': q.page_or_table,
                        'note': (cfg['why'] if chosen else (q.notes if isinstance(q.notes, str) else ''))[:400]})

pd.DataFrame(recs).to_csv(os.path.join(JOB, 'fuel_prices.csv'), index=False)
pd.DataFrame(ppoints).to_csv(os.path.join(JOB, 'price_points_2024.csv'), index=False)
pd.DataFrame(summ).to_csv(os.path.join(JOB, 'work', 'fuel_summary.csv'), index=False)

consts = []
for y in sorted(CPI):
    consts.append({'constant': f'CPI_U_{y}', 'value': CPI[y], 'unit': 'index 1982-84=100, annual average', 'source_id': SRC_CPI,
                   'locator': f'series CUUR0000SA0, year {y}, period M13 (Annual)'})
for k, b in BENCH.items():
    for y in range(2018, 2026):
        consts.append({'constant': f"{k.upper()}_{y}", 'value': b['obs'][y], 'unit': b['unit'] + ' nominal', 'source_id': b['src'],
                       'locator': b['name'] + f', year {y}'})
for sname, t in WEO.items():
    consts.append({'constant': f'WEO2025_{sname.replace(" ", "_")}_2024', 'value': t[2024]['ALL'], 'unit': t['unit'] + ' USD (MER, 2024)', 'source_id': SRC_WEO,
                   'locator': 'Table 2.3 Wholesale fossil fuel prices by scenario, page 109, column 2024'})
    for yy in (2035, 2050):
        for s in ('CPS', 'STEPS', 'NZE'):
            consts.append({'constant': f'WEO2025_{sname.replace(" ", "_")}_{s}_{yy}', 'value': t[yy][s], 'unit': t['unit'] + ' USD (MER, 2024)',
                           'source_id': SRC_WEO, 'locator': f'Table 2.3 Wholesale fossil fuel prices by scenario, page 109, column {s} {yy}'})
consts.append({'constant': 'UN_NGS_NET_PER_GROSS', 'value': 0.9, 'unit': 'ratio', 'source_id': 'GEN-006', 'locator': 'page xxv, natural gas paragraph'})
consts.append({'constant': 'GJ_PER_MMBTU', 'value': 1.055056, 'unit': 'GJ/MMBtu', 'source_id': 'GEN-003', 'locator': 'Appendix B.8, British thermal unit (IT)'})
consts.append({'constant': 'MMBTU_PER_MCF_EIA', 'value': 1.037, 'unit': 'MMBtu/Mcf', 'source_id': 'GEN-005', 'locator': 'answer text, 1,037 Btu/cf'})
consts.append({'constant': 'EIA_LNG_EXPORT_PRICE_PANAMA_2024', 'value': 7.21, 'unit': 'USD/Mcf', 'source_id': 'FUE-006',
               'locator': 'sheet Data 2, column Price of Liquefied U.S. Natural Gas Exports to Panama, row 2024'})
pd.DataFrame(consts).to_csv(os.path.join(JOB, 'work', 'fuel_constants.csv'), index=False)
print(pd.DataFrame(summ).to_string())
