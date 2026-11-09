"""Build the Jamaica (JAM) CSV outputs for job LAC_LOCAL_PRICES 20261109T085226Z.

Usage: py -I build_jam.py <job_folder>
  <job_folder> is the folder that holds the downloads and country folders.

Values transcribed from documents are entered below with their source id and page.
Comtrade values are read from the saved JSON responses at run time.
No value is taken from any earlier job output.
"""
import csv, json, os, sys

JOB = sys.argv[1]
DL = os.path.join(JOB, 'downloads')
OUT = os.path.join(JOB, 'country', 'JAM')
RET = '2026-11-09'

# ---------------- shared constants (names only; values as given by the main session) ----------
L_PER_USGAL = 3.785411784
USGAL_PER_BBL = 42
GJ_PER_MMBTU = 1.055056
UN_GAL_PER_T = {'GSL': 357, 'DSL': 304, 'JET': 326, 'KER': 326, 'FOI': 278, 'LPG': 489}
IPCC_NCV = {'GSL': 44.3, 'DSL': 43.0, 'JET': 44.1, 'KER': 43.8, 'FOI': 40.4, 'LPG': 47.3,
            'COK': 32.5, 'COA_OTHER_BITUMINOUS': 25.8, 'NGS': 48.0}

# ---------------- Jamaica constants ----------------
# Bank of Jamaica annual weighted average USD selling rate (JMD per USD), table "Annual Weighted
# Average FX Rates" (wpDataTable 144), saved as JAM/boj_wdtable_144.json
FX = {}
_boj = json.load(open(os.path.join(DL, 'JAM', 'boj_wdtable_144.json'), encoding='utf-8'))['data']
for yr, cur, sell, buy in _boj:
    if cur == 'USD' and 2018 <= int(yr) <= 2025:
        FX[int(yr)] = float(sell)
assert abs(FX[2024] - 157.22) < 1e-9, FX[2024]

SCT_ADO_STD = 37.4845      # J$/L, OUR investigation report p.21 (JAM-012)
SCT_ADO_JUL = 4.5611       # J$/L, concessionary rate July 2024, same page
OUR_ADO_MMBTU_PER_BBL = round(175.37 / 30.16, 4)   # 5.8147, OUR AR 2023-24 Table 23, 2023 row (JAM-014)

# ---------------- sources ----------------
SRC = [
 # id, url, title, publisher, date, file, page_or_table, supports
 ('JAM-001', 'https://boj.org.jm/market/foreign-exchange/average-exchange-rates/',
  'Average Exchange Rates: Annual Weighted Average FX Rates and Monthly Weighted Average FX Rates', 'Bank of Jamaica',
  'data to 2026-10', 'JAM/boj_avg_fx_page.html; JAM/boj_wdtable_144.json; JAM/boj_wdtable_145.json',
  'Annual Weighted Average FX Rates table, row USD 2024 (sell 157.22); rows 2018 to 2025. The table loads from the page by POST to https://boj.org.jm/wp-admin/admin-ajax.php?action=get_wdtable&table_id=144 (saved JSON); monthly table id 145',
  'JAM_FX_2018 to JAM_FX_2025; all JMD prices'),
 ('JAM-002', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=388&period=2024&partnerCode=0&flowCode=M&cmdCode=2701,2713,2709,2710,2711',
  'UN Comtrade public preview API: Jamaica imports 2024, partner World, HS 2701, 2713, 2709, 2710, 2711', 'UN Comtrade (reported by Jamaica)',
  '2024 data', 'JAM/comtrade_JAM_2024_M_4digit.json', 'records cmdCode 2701 and 2713: cifvalue, netWgt, isNetWgtEstimated', 'COA and COK import CIF 2024'),
 ('JAM-003', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=388&period=2024&partnerCode=0&flowCode=M&cmdCode=270111,270112,270119,270120,270210,270400,271311,271312,271320,271390,270900,271012,271019,271020,271111,271112,271113,271114,271119,271121,271129',
  'UN Comtrade public preview API: Jamaica imports 2024, partner World, 6-digit HS codes', 'UN Comtrade (reported by Jamaica)',
  '2024 data', 'JAM/comtrade_JAM_2024_M_6digit.json', 'records cmdCode 271111, 271112, 271113, 271012, 271019, 271312, 270119',
  'NGS, LPG, GSL, DSL import CIF 2024; COK and COA detail'),
 ('JAM-004', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?period=2024&partnerCode=388&flowCode=X&cmdCode=270112,270119,2701,271311,271312,2713',
  'UN Comtrade public preview API: exports to Jamaica 2024 reported by partner countries (mirror), HS 2701 and 2713', 'UN Comtrade (reported by exporting countries)',
  '2024 data', 'JAM/comtrade_mirror_exports_to_JAM_2024.json', 'record reporterCode 842 (USA) cmdCode 270112: fobvalue 3030728, netWgt 37884000 kg',
  'COA export FOB to Jamaica 2024 (mirror)'),
]
_hist_years = [2018, 2019, 2020, 2021, 2022, 2023, 2025]
for i, y in enumerate(_hist_years):
    SRC.append((f'JAM-{5+i:03d}',
        f'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=388&period={y}&partnerCode=0&flowCode=M&cmdCode=2701,270112,270119,2713,271311,271312,271111,271112,271113,271012,271019',
        f'UN Comtrade public preview API: Jamaica imports {y}, partner World', 'UN Comtrade (reported by Jamaica)', f'{y} data',
        f'JAM/comtrade_hist/comtrade_JAM_{y}_M.json', 'records by cmdCode: cifvalue, netWgt', f'history {y}: COA, COK, NGS, LPG, GSL import CIF'))
SRC += [
 ('JAM-012', 'https://our.org.jm/wp-content/uploads/2024/12/Office-of-Utilities-Regulation-Investigation-Report_2024-12-19-Final.pdf',
  "OUR's Investigation into Jamaica Public Service Company Limited's 2024 July Fuel Rate (Document 2024/GEN/021/REP.001)", 'Office of Utilities Regulation (OUR)',
  '2024-12-19', 'JAM/OUR_Investigation_JPS_July2024_FuelRate_2024-12-19.pdf; JAM/our/png/OUR_inv_p024_fuelprices.png',
  'Appendix, Fuel Prices table, page 23 of 23 (PDF page 24); SCT Concession, page 21; abbreviations list (HHV, LHV defined but not applied to prices)',
  'NGS and FOI generator delivered (IPP plants, June and July 2024); JAM_SCT_ADO_2024; JAM_SCT_ADO_CONCESSION_JUL2024'),
 ('JAM-013', 'https://our.org.jm/wp-content/uploads/2025/12/Annual-Report-2024-2025-low-res-compressed.pdf',
  'Office of Utilities Regulation Annual Report 2024-2025', 'Office of Utilities Regulation (OUR)', '2025-12-29 (upload date)',
  'JAM/our/Annual-Report-2024-2025-low-res-compressed.pdf; JAM/our/png/Annual-Report-2024-2025-low-res-compressed_p058.png; JAM/our/png/Annual-Report-2024-2025-low-res-compressed_p059.png',
  'page 58, Table 24 Average Price of Fuels used for Electricity Generation (2019-2024); page 59, Table 25 Variation in Fuel Prices and Rates 2022-2024 (monthly). Image-only PDF; values read from page images',
  'NGS, FOI, DSL generator delivered 2024 (12 months); history 2019 to 2024'),
 ('JAM-014', 'https://our.org.jm/wp-content/uploads/2024/11/OUR-Annual-Report-2023-24.pdf',
  'Office of Utilities Regulation Annual Report 2023-2024', 'Office of Utilities Regulation (OUR)', '2024-11-07 (upload date)',
  'JAM/our/OUR-Annual-Report-2023-24.pdf', 'page 52, Table 23 Average Price of Fuels Used for Electricity Generation (2019-2023), 2023 row ADO 175.37 US$/BBL and 30.16 US$/MMBTU',
  'JAM_OUR_ADO_MMBTU_PER_BBL; cross-check of 2019 to 2023 values in JAM-013'),
 ('JAM-015', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/JAMAICA-ENERGY-STATISTICS-2025.pdf',
  'Jamaica Energy Statistics 2025 (data 2021 to 2025p)', 'Ministry of Energy, Transport and Telecommunications, Energy Division, Energy Economics and Planning Unit',
  'July 2026', 'JAM/mset/JAMAICA-ENERGY-STATISTICS-2025.pdf; JAM/mset/png/JAMAICA-ENERGY-STATISTICS-2025_p002.png; JAM/mset/png/JAMAICA-ENERGY-STATISTICS-2025_p013.png',
  'Table 1 Total Petroleum Imports (page 2); Table 4 Petroleum Prices for Selected Products, Refinery Billing Price (J$/litre, mean values, source Petrojam); Table 5 Total Energy Consumption (page 13)',
  'FOI import CIF (Bunker C, bauxite companies), COK import (cement petcoke), NGS import value per BOE, DSL and GSL refinery billing prices 2024; history 2021 to 2025'),
 ('JAM-016', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/JAMAICA-ENERGY-STATISTICS-2024.pdf',
  'Jamaica Energy Statistics 2024 (data 2020 to 2024p)', 'Ministry of Science, Energy, Telecommunications and Transport, Energy Division',
  'July 2025', 'JAM/mset/JAMAICA-ENERGY-STATISTICS-2024.pdf; JAM/mset/png/JAMAICA-ENERGY-STATISTICS-2024_p002.png',
  'Table 1 Total Petroleum Imports 2020-2024 (page 2); Table 4 Refinery Billing Price', 'history 2020 (Bunker C); cross-check of 2024 values'),
 ('JAM-017', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/JAMAICA-ENERGY-STATISTICS-2023-Revised-August-2024.pdf',
  'Jamaica Energy Statistics 2023 (revised August 2024)', 'Ministry of Science, Energy, Telecommunications and Transport, Energy Division', 'May 2024 (revised August 2024)',
  'JAM/mset/JAMAICA-ENERGY-STATISTICS-2023-Revised-August-2024.pdf', 'Table 4 Refinery Billing Price', 'cross-check of billing price history'),
 ('JAM-018', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/JAMAICA-ENERGY-STATISTICS-2022.pdf',
  'Jamaica Energy Statistics 2022 (data 2018 to 2022p)', 'Ministry of Science, Energy and Technology, Energy Division', 'May 2023',
  'JAM/mset/JAMAICA-ENERGY-STATISTICS-2022.pdf', 'Table 1 Total Petroleum Imports 2018-2022, row Bunker C (bauxite companies)', 'history 2018 and 2019 (Bunker C import value per bbl)'),
 ('JAM-019', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/Jamaica-Energy-Statistics-2021.pdf',
  'Jamaica Energy Statistics 2021 (data 2017 to 2021p)', 'Ministry of Science, Energy and Technology, Energy Division', 'May 2022',
  'JAM/mset/Jamaica-Energy-Statistics-2021.pdf', 'Table 4 Petroleum Prices for Selected Products: Ex-refinery Price, Refinery Billing Price, Retail Price (J$/litre, mean values)',
  'history 2018 to 2021: ex-refinery (pre-tax) and billing prices for E10-90, E10-87, ADO, ULSD'),
 ('JAM-020', 'https://www.mset.gov.jm/wp-content/uploads/2020/06/Jamaica-Energy-Statistics-2019.pdf',
  'Jamaica Energy Statistics 2019 (data 2015 to 2019)', 'Ministry of Science, Energy and Technology, Energy Division', 'May 2022 (as printed)',
  'JAM/mset/Jamaica-Energy-Statistics-2019.pdf', 'Table 4 Petroleum Prices for Selected Products (J$/litre) and notes 3 to 5 (definitions of ex-refinery, billing and retail prices)',
  'history 2018 and 2019 ex-refinery prices for LPG, kerosene, fuel oil; price definitions'),
 ('JAM-021', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/MSETT-National-Energy-Balance-2024_Update.pdf',
  'National Energy Balance, Year 2024', 'Ministry of Science, Energy, Telecommunications and Transport, Energy Division', '2025-09-16',
  'JAM/mset/MSETT-National-Energy-Balance-2024_Update.pdf', 'single page; units thousand barrels of oil equivalent (KBOE); notes 1 to 5',
  'calorific basis (not stated); cement fuels list'),
 ('JAM-022', 'https://www.mset.gov.jm/wp-content/uploads/2019/06/PETROLEUM-PRICES-2018.pdf',
  'Petroleum Prices for Selected Products (J$/litre) 2014-2018', 'Ministry of Science, Energy and Technology, Energy Division', 'May 2019',
  'JAM/mset/PETROLEUM-PRICES-2018.pdf', 'notes 3 to 5: ex-refinery price = US Gulf reference price + freight + insurance + premium factor + other charges and fees; billing price = ex-refinery price + taxes (SCT) and fees; retail = billing + industry margin',
  'tax treatment of the refinery billing price'),
 ('JAM-023', 'https://www.wto.org/english/tratop_e/tpr_e/s457_e.pdf',
  'Trade Policy Review: Jamaica, Report by the Secretariat (WT/TPR/S/457)', 'World Trade Organization', '2024-06-05',
  'JAM/other/WTO_TPR_S457_Jamaica_2024.pdf', 'paragraphs 3.32 and 3.34 (SCT on petroleum products: specific per litre plus ad valorem; diesel for public electricity generation exempt by end use)',
  'tax treatment notes only'),
]

def src_file(sid):
    for s in SRC:
        if s[0] == sid:
            return s[5].split(';')[0].strip()
    raise KeyError(sid)

# ---------------- helpers ----------------
HDR = ['country','fuel','model_code','price_point','year','fob','freight','insurance','port','importer_terminal_margin',
       'wholesale_margin','inland_freight','retail_margin','price_as_published','currency','unit','period','months_covered',
       'tax_treatment','calorific_basis','exchange_rate','exchange_rate_constant','conversion_constants','value_usd_per_gj',
       'evidence_class','source_id','page_or_table','downloaded_file','derivation','notes']
MC = {'COA':'DIST_COA','COK':'DIST_COK','NGS':'DIST_NGS','FOI':'DIST_FOI','DSL':'DIST_DSL','GSL':'DIST_GSL',
      'LPG':'DIST_LPG','KER':'DIST_KER','JET':'DIST_JET'}

def row(fuel, pp, year, pap, cur, unit, period, months, tax, cal, val, ev, sid, page, deriv, notes,
        fx='', fxc='', cc='', comp=None, dfile=None):
    r = dict.fromkeys(HDR, '')
    r.update(country='Jamaica', fuel=fuel, model_code=MC[fuel], price_point=pp, year=year,
             price_as_published=pap, currency=cur, unit=unit, period=period, months_covered=months,
             tax_treatment=tax, calorific_basis=cal, exchange_rate=fx, exchange_rate_constant=fxc,
             conversion_constants=cc, value_usd_per_gj=('' if val is None else round(val, 3)),
             evidence_class=ev, source_id=sid, page_or_table=page,
             downloaded_file=dfile or src_file(sid.split(';')[0]), derivation=deriv, notes=notes)
    if comp:
        r.update(comp)
    return r

def per_l_to_gj(usd_per_l, f):
    return usd_per_l * L_PER_USGAL * UN_GAL_PER_T[f] / IPCC_NCV[f]

def per_bbl_to_gj(usd_per_bbl, f):
    return usd_per_bbl / USGAL_PER_BBL * UN_GAL_PER_T[f] / IPCC_NCV[f]

def ct(path):
    d = json.load(open(os.path.join(DL, path), encoding='utf-8'))
    return {(r['reporterCode'], r['cmdCode']): r for r in d['data']}

P, H = [], []

# ================= 2024 rows =================
# ---- Comtrade 2024
c4 = ct('JAM/comtrade_JAM_2024_M_4digit.json'); c6 = ct('JAM/comtrade_JAM_2024_M_6digit.json')
mir = ct('JAM/comtrade_mirror_exports_to_JAM_2024.json')

r = c4[(388, '2701')]; uv = r['cifvalue'] / (r['netWgt'] / 1000)
P.append(row('COA', 'import CIF', 2024, round(uv, 2), 'USD', 'USD/t', '2024', 12, 'customs value CIF, before duties and taxes', 'not stated',
    uv / IPCC_NCV['COA_OTHER_BITUMINOUS'], 'international customs (Comtrade)', 'JAM-002', 'cmdCode 2701, flow M, partner World',
    f"cifvalue {r['cifvalue']} USD / netWgt {r['netWgt']} kg = {uv:.2f} USD/t; / 25.8 GJ/t (IPCC_NCV_COA_OTHER_BITUMINOUS, net) = {uv/25.8:.3f} USD/GJ",
    f"Net weight is flagged as estimated by Comtrade (isNetWgtEstimated true); the 6-digit record 270119 (USD {c6[(388,'270119')]['cifvalue']}) has no weight. Coal type not stated; with IPCC_NCV_COA_SUBBITUMINOUS (18.9 GJ/t) the value would be {uv/18.9:.3f} USD/GJ. MSET Energy Statistics 2025 Table 5 reports 2024 coal consumption of 19 thousand tonnes, close to the Comtrade estimated weight (20,806 t), while the USA mirror export weight is 37,884 t.",
    cc='IPCC_NCV_COA_OTHER_BITUMINOUS'))

r = mir[(842, '270112')]; uv = r['fobvalue'] / (r['netWgt'] / 1000)
P.append(row('COA', 'export FOB', 2024, round(uv, 2), 'USD', 'USD/t', '2024', 12, 'export value FOB at US port, no Jamaican taxes', 'not stated',
    uv / IPCC_NCV['COA_OTHER_BITUMINOUS'], 'international customs (Comtrade)', 'JAM-004', 'reporterCode 842 (USA), cmdCode 270112 (bituminous coal), flow X, partner 388',
    f"fobvalue {r['fobvalue']} USD / netWgt {r['netWgt']} kg = {uv:.2f} USD/t; / 25.8 GJ/t (IPCC_NCV_COA_OTHER_BITUMINOUS) = {uv/25.8:.3f} USD/GJ",
    "Mirror record: USA exports of bituminous coal to Jamaica as reported by the USA. FOB, so ocean freight and insurance to Jamaica are not included. Its value (USD 3.03 million) is close to Jamaica's reported CIF (USD 3.09 million) but its weight is 1.8 times the Comtrade estimated weight for Jamaica's imports.",
    cc='IPCC_NCV_COA_OTHER_BITUMINOUS'))

r = c4[(388, '2713')]; uv = r['cifvalue'] / (r['netWgt'] / 1000)
P.append(row('COK', 'import CIF', 2024, round(uv, 2), 'USD', 'USD/t', '2024', 12, 'customs value CIF, before duties and taxes', 'not stated',
    uv / IPCC_NCV['COK'], 'international customs (Comtrade)', 'JAM-002', 'cmdCode 2713, flow M, partner World',
    f"cifvalue {r['cifvalue']} USD / netWgt {r['netWgt']} kg = {uv:.2f} USD/t; / 32.5 GJ/t (IPCC_NCV_COK, net) = {uv/32.5:.3f} USD/GJ",
    f"Almost all under 6-digit 271312 (calcined petroleum coke, 33,078 t at {c6[(388,'271312')]['cifvalue']/(c6[(388,'271312')]['netWgt']/1000):.2f} USD/t); the unit value is that of fuel-grade (non-calcined) coke, so the 6-digit split is probably a classification error. MSET reports the cement company as the only petcoke importer in 2024.",
    cc='IPCC_NCV_COK'))

mset_cok_v, mset_cok_q = 3835212, 161660
P.append(row('COK', 'import CIF', 2024, round(mset_cok_v / mset_cok_q, 3), 'USD', 'USD/bbl', '2024', 12, 'import value as reported by the importer (basis CIF or FOB not stated), before taxes', 'not stated',
    None, 'local customs or statistics', 'JAM-015', 'Table 1 Total Petroleum Imports, Cement Company, Petcoke, 2024 (page 2)',
    f"{mset_cok_v} USD / {mset_cok_q} bbl = {mset_cok_v/mset_cok_q:.3f} USD/bbl. Not converted to USD/GJ: MSET gives no tonnage or energy factor for petcoke barrels",
    "Imports by the cement company (Caribbean Cement). Volume is stated in barrels; the publisher gives no conversion to tonnes or energy. Against the Comtrade weight for HS 2713 (33,095 t) the volume implies 4.9 bbl per tonne, and the value is 15 percent above the Comtrade CIF value.",
    ))

# ---- natural gas
r = c6[(388, '271111')]; uv = r['cifvalue'] / (r['netWgt'] / 1000)
P.append(row('NGS', 'import CIF', 2024, round(uv, 2), 'USD', 'USD/t', '2024', 12, 'customs value CIF, before duties and taxes', 'not stated',
    uv / IPCC_NCV['NGS'], 'international customs (Comtrade)', 'JAM-003', 'cmdCode 271111 (LNG), flow M, partner World',
    f"cifvalue {r['cifvalue']} USD / netWgt {r['netWgt']} kg = {uv:.2f} USD/t; / 48.0 GJ/t (IPCC_NCV_NGS, net) = {uv/48.0:.3f} USD/GJ net; gross equivalent {uv/(48.0/0.9):.3f} USD/GJ using UN_NGS_NET_PER_GROSS",
    "LNG imports (New Fortress Energy terminals). Value converted on a net basis with the IPCC factor; the gross-basis equivalent is in the derivation.",
    cc='IPCC_NCV_NGS;UN_NGS_NET_PER_GROSS'))

ng_v, ng_q = 262065988, 4570272
P.append(row('NGS', 'import CIF', 2024, round(ng_v / ng_q, 3), 'USD', 'USD/BOE', '2024', 12, 'import value as reported (basis CIF or FOB not stated), before taxes', 'not stated',
    None, 'local customs or statistics', 'JAM-015', 'Table 1 Total Petroleum Imports, Natural Gas, 2024 (page 2)',
    f"{ng_v} USD / {ng_q} = {ng_v/ng_q:.3f} USD per unit. Volume column is headed bbl; the National Energy Balance 2024 (JAM-021) shows natural gas imports of 4,569.0 KBOE, so the unit is barrels of oil equivalent. Not converted: MSET states no energy content for its BOE",
    "Published by the energy ministry from New Fortress Energy and importer returns. Left without a USD/GJ value because the BOE factor is not published.",
    ))

our_months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
# OUR Annual Report 2024-2025, Table 25 (page 59), 2024 rows: HFO, ADO, NG prices to JPS, US$/MMBTU (read from image)
HFO = [12.29,12.34,13.14,13.70,13.51,13.39,13.55,12.77,12.45,13.43,12.48,12.64]
ADO = [29.23,30.56,29.78,29.25,27.91,27.65,21.91,26.38,25.52,25.51,25.51,25.85]
NG  = [14.05,13.49,12.58,12.91,12.67,12.80,14.23,12.71,13.34,13.54,14.53,15.64]
mon = 'Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec 2024'
def mean(a): return sum(a) / len(a)

ng = mean(NG)
P.append(row('NGS', 'generator delivered', 2024, 13.54, 'USD', 'USD/MMBtu', '2024', 12, 'not stated (plant gate price to JPS)', 'not stated',
    13.54 / GJ_PER_MMBTU, 'local regulator or operator', 'JAM-013', 'Table 24 (page 58) 2024 row NG 13.54 US$/MMBTU; Table 25 (page 59) monthly NG prices to JPS',
    f"Annual mean 13.54 USD/MMBtu (Table 24); check: mean of the 12 monthly values in Table 25 ({', '.join(str(x) for x in NG)}) = {ng:.3f}; 13.54 / 1.055056 (GJ_PER_MMBTU) = {13.54/GJ_PER_MMBTU:.3f} USD/GJ",
    "Price of natural gas to JPS plants (Bogue). Values read from page images of an image-only PDF. Heat content basis not stated by OUR; per-MMBtu gas prices are treated as gross and kept on that basis. The June value in the OUR July 2024 investigation (JAM-012) is 13.28, against 12.80 in this table. IPP gas plants pay less (see the next rows).",
    cc='GJ_PER_MMBTU'))
sj = mean([8.59, 8.73])
P.append(row('NGS', 'generator delivered', 2024, round(sj, 3), 'USD', 'USD/MMBtu', '2024-06 to 2024-07', 2, 'not stated', 'not stated',
    sj / GJ_PER_MMBTU, 'local regulator or operator', 'JAM-012', 'Appendix Fuel Prices table, page 23 (PDF page 24), rows SJPC and NFE 94MW',
    f"mean(8.59 June, 8.73 July) = {sj:.3f} USD/MMBtu (SJPC and NFE 94MW have identical values); / 1.055056 (GJ_PER_MMBTU) = {sj/GJ_PER_MMBTU:.3f} USD/GJ",
    "Gas price to the IPP plants SJPC (Old Harbour) and NFE 94 MW, June and July 2024 only. No 12-month series for IPP plants was found.",
    cc='GJ_PER_MMBTU'))
hr = mean([10.41, 10.55])
P.append(row('NGS', 'generator delivered', 2024, round(hr, 3), 'USD', 'USD/MMBtu', '2024-06 to 2024-07', 2, 'not stated', 'not stated',
    hr / GJ_PER_MMBTU, 'local regulator or operator', 'JAM-012', 'Appendix Fuel Prices table, page 23 (PDF page 24), row CB - Hill Run',
    f"mean(10.41 June, 10.55 July) = {hr:.3f} USD/MMBtu; / 1.055056 (GJ_PER_MMBTU) = {hr/GJ_PER_MMBTU:.3f} USD/GJ",
    "Gas price to the Hill Run plant, June and July 2024 only.", cc='GJ_PER_MMBTU'))

# ---- fuel oil
hfo = mean(HFO)
P.append(row('FOI', 'generator delivered', 2024, 12.97, 'USD', 'USD/MMBtu', '2024', 12, 'not stated (plant gate price to JPS)', 'not stated',
    12.97 / GJ_PER_MMBTU, 'local regulator or operator', 'JAM-013', 'Table 24 (page 58) 2024 row HFO (JPS plants) 81.87 US$/BBL and 12.97 US$/MMBTU; Table 25 (page 59) monthly HFO prices to JPS',
    f"Annual mean 12.97 USD/MMBtu (Table 24); check: mean of the 12 monthly values in Table 25 ({', '.join(str(x) for x in HFO)}) = {hfo:.3f}; 12.97 / 1.055056 (GJ_PER_MMBTU) = {12.97/GJ_PER_MMBTU:.3f} USD/GJ. Also published as 81.87 USD/bbl",
    "Values read from page images. Heat content basis not stated; the published pair 81.87 USD/bbl and 12.97 USD/MMBtu implies 6.312 MMBtu/bbl (6.286 in 2019 to 2023), the usual gross heat content of residual fuel oil, so the per-MMBtu price is most likely gross.",
    cc='GJ_PER_MMBTU'))
ipp = [12.64, 13.24, 15.26, 15.91, 11.46, 12.36]
P.append(row('FOI', 'generator delivered', 2024, round(mean(ipp), 3), 'USD', 'USD/MMBtu', '2024-06 to 2024-07', 2, 'not stated', 'not stated',
    mean(ipp) / GJ_PER_MMBTU, 'local regulator or operator', 'JAM-012', 'Appendix Fuel Prices table, page 23 (PDF page 24), rows WKPP, JPPC, JEP',
    f"unweighted mean of WKPP (12.64, 13.24), JPPC (15.26, 15.91), JEP (11.46, 12.36) for June and July = {mean(ipp):.3f} USD/MMBtu; / 1.055056 (GJ_PER_MMBTU) = {mean(ipp)/GJ_PER_MMBTU:.3f} USD/GJ",
    "HFO price to the IPP plants, June and July 2024 only; plant range 11.46 to 15.91 USD/MMBtu.", cc='GJ_PER_MMBTU'))
bc_v, bc_q = 210340422, 2598438
P.append(row('FOI', 'import CIF', 2024, round(bc_v / bc_q, 3), 'USD', 'USD/bbl', '2024', 12, 'import value as reported (basis CIF or FOB not stated), before taxes', 'not stated',
    per_bbl_to_gj(bc_v / bc_q, 'FOI'), 'local customs or statistics', 'JAM-015', 'Table 1 Total Petroleum Imports, Bauxite Companies, Bunker C, 2024 (page 2)',
    f"{bc_v} USD / {bc_q} bbl = {bc_v/bc_q:.3f} USD/bbl; / 42 (USGAL_PER_BBL) x 278 gal/t (UN_GAL_PER_T_FOI) / 40.4 GJ/t (IPCC_NCV_FOI) = {per_bbl_to_gj(bc_v/bc_q,'FOI'):.3f} USD/GJ net",
    "Direct imports of heavy fuel oil by the alumina companies. Same publisher series 2018 to 2025 in history file.",
    cc='USGAL_PER_BBL;UN_GAL_PER_T_FOI;IPCC_NCV_FOI'))

# ---- diesel
ado = mean(ADO)
P.append(row('DSL', 'generator delivered', 2024, round(ado, 3), 'USD', 'USD/MMBtu', '2024', 12, 'includes SCT at the standard rate (37.4845 J$/L) except July 2024 (concessionary 4.5611 J$/L), per OUR (JAM-012 page 21)', 'not stated',
    ado / GJ_PER_MMBTU, 'local regulator or operator', 'JAM-013', 'Table 25 (page 59) monthly ADO prices to JPS, 2024 rows',
    f"mean of 12 monthly values ({', '.join(str(x) for x in ADO)}) = {ado:.3f} USD/MMBtu; / 1.055056 (GJ_PER_MMBTU) = {ado/GJ_PER_MMBTU:.3f} USD/GJ",
    "Automotive diesel oil to JPS plants. Table 24 of the same report gives the 2024 annual ADO price as 158 US$/BBL and 25.85 US$/MMBTU, which equals the December monthly value and not the mean of the months; the monthly mean is used. Values read from page images.",
    cc='GJ_PER_MMBTU'))
sct_std = SCT_ADO_STD / FX[2024] * L_PER_USGAL * USGAL_PER_BBL / OUR_ADO_MMBTU_PER_BBL
sct_jul = SCT_ADO_JUL / FX[2024] * L_PER_USGAL * USGAL_PER_BBL / OUR_ADO_MMBTU_PER_BBL
ex = [p - (sct_jul if m == 'Jul' else sct_std) for p, m in zip(ADO, our_months)]
P.append(row('DSL', 'generator delivered', 2024, round(mean(ex), 3), 'USD', 'USD/MMBtu', '2024', 12, 'excludes SCT (derived); other taxes not stated', 'not stated',
    mean(ex) / GJ_PER_MMBTU, 'built from published components', 'JAM-013;JAM-012;JAM-014;JAM-001', 'JAM-013 Table 25; JAM-012 page 21; JAM-014 Table 23; JAM-001 annual table',
    f"SCT per MMBtu = 37.4845 J$/L (JAM_SCT_ADO_2024, JAM-012) / 157.22 J$/USD (JAM_FX_2024, JAM-001) x 3.785411784 (L_PER_USGAL) x 42 (USGAL_PER_BBL) / {OUR_ADO_MMBTU_PER_BBL} MMBtu/bbl (JAM_OUR_ADO_MMBTU_PER_BBL, JAM-014) = {sct_std:.3f} USD/MMBtu; July uses 4.5611 J$/L (JAM_SCT_ADO_CONCESSION_JUL2024) = {sct_jul:.3f}; monthly ADO price (JAM-013) minus SCT, mean of 12 months = {mean(ex):.3f} USD/MMBtu; / 1.055056 (GJ_PER_MMBTU) = {mean(ex)/GJ_PER_MMBTU:.3f} USD/GJ",
    "Ex-SCT price of diesel delivered to JPS. Assumes the SCT on JPS diesel is the specific rate stated by OUR only (WTO 2024 describes the petroleum SCT as specific plus ad valorem and says diesel for public electricity generation is exempt by end use; OUR states JPS paid the standard rate in 2024).",
    fx=FX[2024], fxc='JAM_FX_2024', cc='JAM_SCT_ADO_2024;JAM_SCT_ADO_CONCESSION_JUL2024;JAM_OUR_ADO_MMBTU_PER_BBL;L_PER_USGAL;USGAL_PER_BBL;GJ_PER_MMBTU'))

def billing(fuel, name, jmd, f):
    usd_l = jmd / FX[2024]
    return row(fuel, 'wholesale import parity', 2024, jmd, 'JMD', 'JMD/L', '2024', 12,
        'includes SCT (specific and ad valorem) and fees; excludes marketing and retail margins (MSET definition, JAM-022 note 4)', 'not stated',
        per_l_to_gj(usd_l, f), 'local regulator or operator', 'JAM-015', f'Table 4 Petroleum Prices for Selected Products, Refinery Billing Price, {name}, 2024 (mean values; source Petrojam Limited)',
        f"{jmd} JMD/L / 157.22 JMD/USD (JAM_FX_2024) = {usd_l:.5f} USD/L x 3.785411784 (L_PER_USGAL) x {UN_GAL_PER_T[f]} gal/t (UN_GAL_PER_T_{f}) / {IPCC_NCV[f]} GJ/t (IPCC_NCV_{f}) = {per_l_to_gj(usd_l, f):.3f} USD/GJ",
        f"Petrojam refinery billing price (annual mean) as published by the energy ministry. It is NOT pre-tax: billing price = ex-refinery (import parity) price + SCT and fees. No 2024 ex-refinery price or SCT schedule was retrievable, so no pre-tax value is derived.{' E10 blend; gasoline factors used.' if fuel=='GSL' else ''}",
        fx=FX[2024], fxc='JAM_FX_2024', cc=f'L_PER_USGAL;UN_GAL_PER_T_{f};IPCC_NCV_{f}')
P.append(billing('DSL', 'A.D.O', 171.05, 'DSL'))
P.append(billing('DSL', 'ULSD', 178.28, 'DSL'))

r = c6[(388, '271019')]; uv = r['cifvalue'] / (r['netWgt'] / 1000)
P.append(row('DSL', 'import CIF', 2024, round(uv, 2), 'USD', 'USD/t', '2024', 12, 'customs value CIF, before duties and taxes', 'not stated',
    uv / IPCC_NCV['DSL'], 'international customs (Comtrade)', 'JAM-003', 'cmdCode 271019, flow M, partner World',
    f"cifvalue {r['cifvalue']} USD / netWgt {r['netWgt']} kg = {uv:.2f} USD/t; / 43.0 GJ/t (IPCC_NCV_DSL) = {uv/43.0:.3f} USD/GJ",
    "HS 271019 mixes diesel, jet fuel, kerosene, heavy fuel oil and lubricating oils, so this is not a diesel price. MSET reports 2,598,438 bbl of Bunker C imported by alumina companies in 2024, a large share of this code, which pulls the unit value down.",
    cc='IPCC_NCV_DSL'))

# ---- gasoline
P.append(billing('GSL', 'E10-87', 168.73, 'GSL'))
P.append(billing('GSL', 'E10-90', 176.49, 'GSL'))
r = c6[(388, '271012')]; uv = r['cifvalue'] / (r['netWgt'] / 1000)
P.append(row('GSL', 'import CIF', 2024, round(uv, 2), 'USD', 'USD/t', '2024', 12, 'customs value CIF, before duties and taxes', 'not stated',
    uv / IPCC_NCV['GSL'], 'international customs (Comtrade)', 'JAM-003', 'cmdCode 271012 (light oils), flow M, partner World',
    f"cifvalue {r['cifvalue']} USD / netWgt {r['netWgt']} kg = {uv:.2f} USD/t; / 44.3 GJ/t (IPCC_NCV_GSL) = {uv/44.3:.3f} USD/GJ",
    "HS 271012 is mainly motor gasoline blendstock (ethanol is imported separately); it may also hold naphtha and other light oils.",
    cc='IPCC_NCV_GSL'))

# ---- LPG
p, b = c6[(388, '271112')], c6[(388, '271113')]
v = p['cifvalue'] + b['cifvalue']; w = (p['netWgt'] + b['netWgt']) / 1000; uv = v / w
P.append(row('LPG', 'import CIF', 2024, round(uv, 2), 'USD', 'USD/t', '2024', 12, 'customs value CIF, before duties and taxes', 'not stated',
    uv / IPCC_NCV['LPG'], 'international customs (Comtrade)', 'JAM-003', 'cmdCode 271112 (propane) and 271113 (butane), flow M, partner World',
    f"(propane {p['cifvalue']} + butane {b['cifvalue']}) USD / ({p['netWgt']} + {b['netWgt']}) kg = {uv:.2f} USD/t; / 47.3 GJ/t (IPCC_NCV_LPG) = {uv/47.3:.3f} USD/GJ",
    f"Propane {p['cifvalue']/(p['netWgt']/1000):.2f} USD/t, butane {b['cifvalue']/(b['netWgt']/1000):.2f} USD/t. No published LPG margin was found.",
    cc='IPCC_NCV_LPG'))

# ---- kerosene and jet: ASSUMPTION candidates
uvm = c6[(388, '271019')]['cifvalue'] / (c6[(388, '271019')]['netWgt'] / 1000)
for f, ncv, name in (('KER', 43.8, 'Kerosene'), ('JET', 44.1, 'Jet fuel')):
    lo = uvm / ncv; hi = mean(ex) / GJ_PER_MMBTU
    val = 18.0
    P.append(row(f, 'wholesale import parity', 2024, val, 'USD', 'USD/GJ', '2024', 12, 'pre-tax', 'net', val,
        'ASSUMPTION candidate', 'JAM-003;JAM-013;JAM-012;JAM-014;JAM-001', 'JAM-003 cmdCode 271019; JAM-013 Table 25',
        f"lower check: 271019 CIF unit value {uvm:.2f} USD/t / {ncv} GJ/t (IPCC_NCV_{f}) = {lo:.2f} USD/GJ; upper check: ex-SCT diesel delivered to JPS {hi:.2f} USD/GJ (row above); value set at 18.0 USD/GJ",
        f"{name} supply cost in Jamaica in 2024, before taxes, taken as 18.0 USD/GJ (net calorific basis), all 12 months, because Jamaica prices {name.lower()} at import parity with US Gulf Coast middle distillates, on the same basis as diesel; check: the 2024 Jamaican customs unit value for medium oils (HS 271019, 712.97 USD/t, about {lo:.1f} USD/GJ) is a lower bound because it includes heavy fuel oil, and diesel delivered to the power utility net of consumption tax (about {hi:.1f} USD/GJ, OUR) is an upper bound; range {lo:.1f} to {hi:.1f} USD/GJ.",
        cc=f'IPCC_NCV_{f};GJ_PER_MMBTU', dfile='JAM/comtrade_JAM_2024_M_6digit.json; JAM/our/Annual-Report-2024-2025-low-res-compressed.pdf'))

# ================= history rows =================
# OUR Table 24 (JAM-013), annual: HFO US$/bbl, HFO US$/MMBtu, ADO US$/bbl, ADO US$/MMBtu, NG US$/MMBtu
T24 = {2019: (67.19, 10.69, 96.35, 16.54, 12.66), 2020: (47.65, 7.58, 64.87, 11.14, 11.82),
       2021: (72.99, 11.61, 95.09, 16.33, 14.25), 2022: (91.59, 14.57, 195.29, 33.53, 16.65),
       2023: (80.33, 12.78, 175.37, 30.16, 13.76), 2024: (81.87, 12.97, 158, 25.85, 13.54)}
for y, (hb, hm, ab, am, nm) in T24.items():
    H.append(row('FOI', 'generator delivered', y, hm, 'USD', 'USD/MMBtu', str(y), 12, 'not stated', 'not stated', hm / GJ_PER_MMBTU,
        'local regulator or operator', 'JAM-013', 'Table 24 (page 58), HFO (JPS plants)', f"{hm} / 1.055056 (GJ_PER_MMBTU) = {hm/GJ_PER_MMBTU:.3f} USD/GJ; also published {hb} USD/bbl",
        'Read from page image; 2019 to 2023 identical in the text-based OUR Annual Report 2023-24 Table 23 (JAM-014).', cc='GJ_PER_MMBTU'))
    H.append(row('DSL', 'generator delivered', y, am, 'USD', 'USD/MMBtu', str(y), 12, 'includes SCT (OUR, JAM-012)', 'not stated', am / GJ_PER_MMBTU,
        'local regulator or operator', 'JAM-013', 'Table 24 (page 58), ADO', f"{am} / 1.055056 (GJ_PER_MMBTU) = {am/GJ_PER_MMBTU:.3f} USD/GJ; also published {ab} USD/bbl",
        ('2024 annual value as published (25.85) equals the December value; the mean of the 12 monthly values is 27.09 (see the 2024 file).' if y == 2024 else 'Read from page image; cross-checked with JAM-014 Table 23.'), cc='GJ_PER_MMBTU'))
    H.append(row('NGS', 'generator delivered', y, nm, 'USD', 'USD/MMBtu', str(y), 12, 'not stated', 'not stated', nm / GJ_PER_MMBTU,
        'local regulator or operator', 'JAM-013', 'Table 24 (page 58), NG', f"{nm} / 1.055056 (GJ_PER_MMBTU) = {nm/GJ_PER_MMBTU:.3f} USD/GJ",
        'Plant gate price of gas to JPS; basis not stated, treated as gross.', cc='GJ_PER_MMBTU'))

# MSET Bunker C imports (bauxite companies): year: (bbl, USD, source)
BC = {2018: (1253126, 80329056, 'JAM-018'), 2019: (902596, 46499679, 'JAM-018'), 2020: (1248180, 38583484, 'JAM-016'),
      2021: (858899, 46843164, 'JAM-015'), 2022: (1264737, 85891918, 'JAM-015'), 2023: (1642218, 130794270, 'JAM-015'),
      2024: (2598438, 210340422, 'JAM-015'), 2025: (1087573, 77840125, 'JAM-015')}
for y, (q, v, s) in BC.items():
    u = v / q
    H.append(row('FOI', 'import CIF', y, round(u, 3), 'USD', 'USD/bbl', str(y) + ('p' if y == 2025 else ''), 12, 'import value as reported, before taxes', 'not stated',
        per_bbl_to_gj(u, 'FOI'), 'local customs or statistics', s, 'Table 1 Total Petroleum Imports, Bauxite Companies, Bunker C',
        f"{v} USD / {q} bbl = {u:.3f} USD/bbl; / 42 x 278 / 40.4 = {per_bbl_to_gj(u,'FOI'):.3f} USD/GJ", '2025 preliminary.' if y == 2025 else '',
        cc='USGAL_PER_BBL;UN_GAL_PER_T_FOI;IPCC_NCV_FOI'))

# MSET ex-refinery (pre-tax) and billing prices, J$/L
EXR = {  # JAM-019 Table 4 (2018-2021) for E10-90, E10-87, ADO, ULSD
    2018: (83.87, 81.55, 82.65, 87.77), 2019: (81.03, 78.87, 84.01, 87.93), 2020: (70.75, 68.57, 68.97, 73.06), 2021: (93.98, 90.27, 87.75, 91.95)}
BIL = {  # E10-90, E10-87, ADO, ULSD ; source
    2018: ((135.02, 132.07, 132.95, 137.84), 'JAM-019'), 2019: ((133.31, 130.67, 135.91, 139.53), 'JAM-019'),
    2020: ((121.48, 117.00, 116.96, 120.97), 'JAM-016'), 2021: ((144.92, 140.42, 137.11, 141.16), 'JAM-015'),
    2022: ((195.17, 190.52, 208.41, 213.75), 'JAM-015'), 2023: ((177.66, 173.08, 182.95, 191.88), 'JAM-015'),
    2024: ((176.49, 168.73, 171.05, 178.28), 'JAM-015'), 2025: ((162.69, 155.68, 162.53, 169.37), 'JAM-015')}
names = (('GSL', 'E10-90'), ('GSL', 'E10-87'), ('DSL', 'A.D.O'), ('DSL', 'ULSD'))
def lrow(f, nm, y, jmd, sid, kind):
    u = jmd / FX[y]
    if kind == 'ex':
        pp, tax, page, note = 'wholesale import parity', 'pre-tax (ex-refinery: US Gulf reference + freight + insurance + premium + other charges and fees)', f'Table 4, Ex-refinery Price, {nm}', ''
    else:
        pp, tax, page, note = 'wholesale import parity', 'includes SCT and fees; excludes marketing and retail margins', f'Table 4, Refinery Billing Price, {nm}', 'NOT pre-tax.'
    return row(f, pp, y, jmd, 'JMD', 'JMD/L', str(y) + ('p' if y == 2025 else ''), 12, tax, 'not stated', per_l_to_gj(u, f),
        'local regulator or operator', sid, page,
        f"{jmd} / {FX[y]} (JAM_FX_{y}) = {u:.5f} USD/L x 3.785411784 x {UN_GAL_PER_T[f]} / {IPCC_NCV[f]} = {per_l_to_gj(u,f):.3f} USD/GJ",
        (note + (' E10 blend; gasoline factors used.' if f == 'GSL' else '')).strip(), fx=FX[y], fxc=f'JAM_FX_{y}',
        cc=f'L_PER_USGAL;UN_GAL_PER_T_{f};IPCC_NCV_{f}')
for y, vals in EXR.items():
    for (f, nm), jmd in zip(names, vals):
        H.append(lrow(f, nm, y, jmd, 'JAM-019', 'ex'))
for y, (vals, sid) in BIL.items():
    for (f, nm), jmd in zip(names, vals):
        H.append(lrow(f, nm, y, jmd, sid, 'bil'))
for y, (lpg, ker, foi) in {2018: (47.32, 85.97, 70.83), 2019: (38.73, 84.79, 67.25)}.items():
    for f, nm, jmd in (('LPG', 'L.P.G', lpg), ('KER', 'Kerosene', ker), ('FOI', 'Fuel Oil', foi)):
        H.append(lrow(f, nm, y, jmd, 'JAM-020', 'ex'))

# Comtrade history (Jamaica imports), years with more than 1,000 t
CT_FILES = {y: f'JAM/comtrade_hist/comtrade_JAM_{y}_M.json' for y in _hist_years}
CT_FILES[2024] = None
for y in [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]:
    sid = 'JAM-002' if y == 2024 else f'JAM-{5+_hist_years.index(y):03d}'
    d = ct(CT_FILES[y]) if CT_FILES[y] else {**c4, **c6}
    sid6 = 'JAM-003' if y == 2024 else sid
    def add(fuel, codes, ncv_key, s):
        recs = [d.get((388, c)) for c in codes]
        if any(r is None or not r.get('netWgt') for r in recs):
            return
        v = sum(r['cifvalue'] for r in recs); w = sum(r['netWgt'] for r in recs) / 1000
        if w < 1000:
            return
        u = v / w; est = any(r.get('isNetWgtEstimated') for r in recs)
        H.append(row(fuel, 'import CIF', y, round(u, 2), 'USD', 'USD/t', str(y), 12, 'customs value CIF, before duties and taxes', 'not stated',
            u / IPCC_NCV[ncv_key], 'international customs (Comtrade)', s, 'cmdCode ' + ' + '.join(codes),
            f"{v:.2f} USD / {w*1000:.0f} kg = {u:.2f} USD/t; / {IPCC_NCV[ncv_key]} GJ/t (IPCC_NCV_{ncv_key}) = {u/IPCC_NCV[ncv_key]:.3f} USD/GJ",
            'Net weight estimated by Comtrade.' if est else '', cc=f'IPCC_NCV_{ncv_key}'))
    coal_code = ['2701'] if d.get((388, '2701'), {}).get('netWgt') else ['270119']
    add('COA', coal_code, 'COA_OTHER_BITUMINOUS', sid)
    add('COK', ['2713'], 'COK', sid)
    add('NGS', ['271111'], 'NGS', sid6)
    add('LPG', ['271112', '271113'], 'LPG', sid6)
    add('GSL', ['271012'], 'GSL', sid6)
# drop petcoke years where the code held non-fuel coke (unit value above 500 USD/t, below 1 kt already removed)
H = [h for h in H if not (h['fuel'] == 'COK' and h['evidence_class'].startswith('international') and float(h['price_as_published']) > 500)]

# ================= constants =================
CONST = [('JAM_FX_%d' % y, FX[y], 'JMD per USD', 'JAM-001', f'Annual Weighted Average FX Rates, USD, {y}, sell rate',
          'annual weighted average selling rate as published by Bank of Jamaica' + ('; confirms the earlier value 157.22' if y == 2024 else ''))
         for y in sorted(FX)]
CONST += [
 ('JAM_SCT_ADO_2024', SCT_ADO_STD, 'JMD per litre', 'JAM-012', 'page 21, SCT Concession', 'standard Special Consumption Tax rate for ADO as stated by OUR (2024)'),
 ('JAM_SCT_ADO_CONCESSION_JUL2024', SCT_ADO_JUL, 'JMD per litre', 'JAM-012', 'page 21, SCT Concession', 'concessionary SCT rate for ADO purchases in July 2024'),
 ('JAM_OUR_ADO_MMBTU_PER_BBL', OUR_ADO_MMBTU_PER_BBL, 'MMBtu per bbl', 'JAM-014', 'page 52, Table 23, 2023 row ADO', '175.37 US$/BBL / 30.16 US$/MMBTU = 5.8147; heat content implied by OUR for diesel (2019 to 2022 rows give 5.82 to 5.83)'),
]

# ================= calorific =================
CAL = [
 dict(country='Jamaica', balance='National Energy Balance 2024 (MSETT)', publisher='Ministry of Science, Energy, Telecommunications and Transport',
      url='https://www.mset.gov.jm/wp-content/uploads/2021/07/MSETT-National-Energy-Balance-2024_Update.pdf', net_or_gross='not stated',
      factor_NGS='', factor_COA='', factor_COK='', factor_FOI='', factor_units='balance in thousand barrels of oil equivalent (KBOE); no conversion factors published',
      page_or_table='single page, header (Caloric Units: Thousand of Barrels of Oil Equivalent) and notes 1 to 5', source_id='JAM-021'),
 dict(country='Jamaica', balance='Jamaica Energy Statistics 2025, Table 5 Total Energy Consumption (MSET)', publisher='Ministry of Energy, Transport and Telecommunications',
      url='https://www.mset.gov.jm/wp-content/uploads/2021/07/JAMAICA-ENERGY-STATISTICS-2025.pdf', net_or_gross='not stated',
      factor_NGS='', factor_COA='5.16', factor_COK='', factor_FOI='', factor_units='factor_COA derived: 98 thousand BOE / 19 thousand tonnes (2024 row); BOE energy content not stated',
      page_or_table='Table 5 (page 13), Coal rows 000 TONNES and 000 BOE, 2024', source_id='JAM-015'),
]

# ================= write =================
def w(name, rows, hdr):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as fh:
        cw = csv.DictWriter(fh, fieldnames=hdr); cw.writeheader()
        for r in rows: cw.writerow(r)
w('prices_JAM.csv', P, HDR)
w('history_JAM.csv', sorted(H, key=lambda r: (r['fuel'], r['price_point'], r['source_id'], r['year'], r['page_or_table'])), HDR)
w('sources_JAM.csv', [dict(id=s[0], url=s[1], title=s[2], publisher=s[3], date=s[4], retrieval_date=RET, downloaded_file=s[5],
                           page_or_table=s[6], rows_and_constants_supported=s[7]) for s in SRC],
  ['id','url','title','publisher','date','retrieval_date','downloaded_file','page_or_table','rows_and_constants_supported'])
w('constants_JAM.csv', [dict(name=c[0], value=c[1], unit=c[2], source_id=c[3], page_or_table=c[4], derivation=c[5]) for c in CONST],
  ['name','value','unit','source_id','page_or_table','derivation'])
w('calorific_JAM.csv', CAL, ['country','balance','publisher','url','net_or_gross','factor_NGS','factor_COA','factor_COK','factor_FOI','factor_units','page_or_table','source_id'])
print('prices', len(P), 'history', len(H), 'sources', len(SRC), 'constants', len(CONST))
for r in P:
    print(r['fuel'], '|', r['price_point'], '|', r['price_as_published'], r['unit'], '|', r['value_usd_per_gj'], '|', r['evidence_class'])
