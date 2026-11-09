"""Write search_log_JAM.csv and manual_JAM.csv for job LAC_LOCAL_PRICES 20261109T085226Z.
Usage: py -I logs_jam.py <job_folder>
Each attempt is listed once with the fuels it covered; one CSV row is written per fuel."""
import csv, os, sys

OUT = os.path.join(sys.argv[1], 'country', 'JAM')
D = '2026-11-09'
ALL = ['COA', 'COK', 'NGS', 'FOI', 'DSL', 'GSL', 'LPG', 'KER', 'JET']
LIQ = ['FOI', 'DSL', 'GSL', 'LPG', 'KER', 'JET']

# (lead_id, lead, url_or_query, {fuel: (result, detail)} or (fuels, result, detail))
A = []
def add(lead_id, lead, url, fuels, result, detail):
    A.append((lead_id, lead, url, {f: (result, detail) for f in fuels}))
def addm(lead_id, lead, url, m):
    A.append((lead_id, lead, url, m))

# ---- petrojam
add('petrojam', 'Petrojam home page (weekly price index, annual reports)', 'https://www.petrojam.com/', LIQ, 'blocked HTTP 403',
    'nginx 403 Forbidden to a plain curl request; not retried by other means; on manual list')
add('petrojam', 'Petrojam weekly ex-refinery price index', 'https://www.petrojam.com/price-index', LIQ, 'blocked HTTP 403',
    'nginx 403 Forbidden; not retried; on manual list')
add('petrojam', 'Petrojam annual report on other public hosts (Parliament, Ministry of Finance)', 'web search: "Petrojam" "annual report" 2023/2024 OR 2024/2025 pdf japarliament.gov.jm OR mof.gov.jm',
    LIQ, 'not found', 'only press summaries of losses and volumes; no annual report file found')
add('petrojam', 'Petrojam refinery billing prices as republished by MSET (Jamaica Energy Statistics 2025, Table 4)', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/JAMAICA-ENERGY-STATISTICS-2025.pdf',
    ['DSL', 'GSL'], 'value found', '2024 mean billing prices E10-90 176.49, E10-87 168.73, ADO 171.05, ULSD 178.28 J$/L; include SCT and fees')
add('petrojam', 'Petrojam refinery billing prices as republished by MSET (Jamaica Energy Statistics 2025, Table 4)', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/JAMAICA-ENERGY-STATISTICS-2025.pdf',
    ['FOI', 'LPG', 'KER', 'JET'], 'no value', 'table covers only E10-90, E10-87, ADO and ULSD since the 2020 edition')
# ---- our_jps
addm('our_jps', "OUR investigation into JPS July 2024 fuel rate (appendix fuel prices by plant)", 'https://our.org.jm/wp-content/uploads/2024/12/Office-of-Utilities-Regulation-Investigation-Report_2024-12-19-Final.pdf',
     {**{f: ('value found', 'June and July 2024 fuel prices by plant in US$/MMBTU (JPS and IPPs); SCT rates for ADO page 21; heat content basis not stated') for f in ['NGS', 'FOI', 'DSL']},
      **{f: ('no value', 'report covers only fuels used for power generation (HFO, ADO, NG)') for f in ['COA', 'COK', 'GSL', 'LPG', 'KER', 'JET']}})
add('our_jps', 'OUR WordPress media library listing (search fuel, rate review, determination, heat rate, IPP, annual report; all PDFs since 2024)',
    'https://our.org.jm/wp-json/wp/v2/media?after=2024-01-01T00:00:00&mime_type=application/pdf&per_page=100&page=1', ['NGS', 'FOI', 'DSL'], 'value found',
    'listing led to the OUR annual reports; no monthly fuel charge determinations or JPS fuel cost filings are posted as separate documents; no JPS 2024-2029 rate review determination found')
addm('our_jps', 'OUR Annual Report 2024-2025, Tables 24 and 25 (average and monthly fuel prices to JPS)', 'https://our.org.jm/wp-content/uploads/2025/12/Annual-Report-2024-2025-low-res-compressed.pdf',
     {**{f: ('value found', '2024 HFO 12.97, ADO 25.85 (monthly mean 27.09), NG 13.54 US$/MMBTU; 12 monthly values; image-only PDF, values read from page images') for f in ['NGS', 'FOI', 'DSL']},
      **{f: ('no value', 'only fuels for power generation') for f in ['COA', 'COK', 'GSL', 'LPG', 'KER', 'JET']}})
add('our_jps', 'OUR Annual Report 2023-24, Table 23 and 24', 'https://our.org.jm/wp-content/uploads/2024/11/OUR-Annual-Report-2023-24.pdf', ['NGS', 'FOI', 'DSL'], 'value found',
    '2019 to 2023 annual and 2022 to 2023 monthly prices; text-based; used for the ADO heat content constant and cross-checks')
add('our_jps', 'OUR Quarterly Performance Reports 2024 (Jan-Mar, Apr-Jun, Jul-Sep, Oct-Dec) and 2023 Oct-Dec', 'https://our.org.jm/wp-content/uploads/2025/04/Quarterly-Performance-Report-2024-Oct-Dec-FINAL.pdf',
    ['NGS', 'FOI', 'DSL'], 'no value', 'customer service and quality reports; no fuel prices (other three quarters checked too)')
add('our_jps', 'OUR Net Billing SOC rate public notice, August 2024', 'https://our.org.jm/wp-content/uploads/2024/10/Public-Notice-Net-Billing-SOC-Rate-2024-Aug.pdf', ['NGS', 'FOI', 'DSL'], 'no value',
    'avoided cost rate in US cents per kWh only')
add('our_jps', 'OUR fuel rate investigation executive summary 2024', 'https://our.org.jm/wp-content/uploads/2024/12/Office-of-Utilities-Regulation-_Fuel-Rate-Investigation_Executive-Summary_2024.pdf',
    ['NGS', 'FOI', 'DSL'], 'no value', 'percentage changes only')
add('our_jps', 'JPS website media library (fuel cost reports, annual report)', 'https://www.jpsco.com/wp-json/wp/v2/media?search=fuel&per_page=100&_fields=date,source_url',
    ['NGS', 'FOI', 'DSL'], 'blocked HTTP 200', 'Incapsula bot challenge page returned instead of content; not retried; on manual list')
add('our_jps', 'OUR and JPS publish no prices for non-power fuels', 'https://our.org.jm/wp-json/wp/v2/media?search=fuel&per_page=100&_fields=id,date,source_url,title',
    ['COA', 'COK', 'GSL', 'LPG', 'KER', 'JET'], 'no value', 'regulator covers electricity; no coal, petcoke, gasoline, LPG, kerosene or jet values')
# ---- mset_pcj
addm('mset_pcj', 'MSET Jamaica Energy Statistics 2025 (Tables 1, 4, 5)', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/JAMAICA-ENERGY-STATISTICS-2025.pdf',
     {'FOI': ('value found', 'Table 1 Bunker C imports by bauxite companies 2024: 2,598,438 bbl, US$210,340,422'),
      'COK': ('value found', 'Table 1 petcoke imports by cement company 2024: 161,660 bbl, US$3,835,212'),
      'NGS': ('value found', 'Table 1 natural gas imports 2024: 4,570,272 (BOE), US$262,065,988'),
      'DSL': ('value found', 'Table 4 billing prices ADO and ULSD 2024'), 'GSL': ('value found', 'Table 4 billing prices E10-87 and E10-90 2024'),
      'COA': ('no value', 'Table 5 gives coal consumption (19 kt in 2024) but no import value'),
      'LPG': ('no value', 'no LPG price or LPG import value by product'), 'KER': ('no value', 'no kerosene price; refined products imports not split by product'),
      'JET': ('no value', 'no jet fuel price; refined products imports not split by product')})
add('mset_pcj', 'MSET Jamaica Energy Statistics editions 2019 to 2024 (history)', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/Jamaica-Energy-Statistics-2021.pdf',
    ['FOI', 'DSL', 'GSL', 'LPG', 'KER'], 'value found', 'ex-refinery prices to 2021 (LPG, kerosene, fuel oil to 2019); billing prices; Bunker C imports 2018 to 2020')
add('mset_pcj', 'MSET Jamaica Energy Statistics editions 2019 to 2024 (history)', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/Jamaica-Energy-Statistics-2021.pdf',
    ['JET', 'COA', 'COK', 'NGS'], 'no value', 'no jet fuel, coal or petcoke prices in any edition')
add('mset_pcj', 'MSET document categories (statistics-data, petroleum, reports, energy-balances)', 'https://www.mset.gov.jm/document-category/statistics-data/', ALL, 'no value',
    'listing only; latest product-level price files (weekly Petrojam matrix) end in 2020; used to find the statistics editions above')
add('mset_pcj', 'MSET WordPress media API', 'https://www.mset.gov.jm/wp-json/wp/v2/media?search=petroleum&per_page=100&_fields=date,source_url', ALL, 'login required',
    'HTTP 401 (rest_forbidden); not retried')
add('mset_pcj', 'Petroleum Corporation of Jamaica website', 'https://www.pcj.com/', ALL, 'not found',
    'host does not resolve; WTO TPR 2024 states PCJ closed and its functions moved to the ministry')
add('mset_pcj', 'Jamaica open data portal, MSET energy tables', 'https://data.gov.jm/node/626', ALL, 'not found',
    'HTTP 404; search results show the energy-tables dataset covers 2011 to 2015 only')
# ---- statin_boj
add('statin_boj', 'STATIN international merchandise trade tables', 'https://statinja.gov.jm/Trade-Econ%20Statistics/InternationalMerchandiseTrade/newtrade.aspx', ALL, 'no value',
    'SITC section aggregates by value only, served through ASP.NET postbacks; the HS search form (InternationalMerchandiseTradeTable7.aspx) needs a browser session; on manual list')
add('statin_boj', 'Bank of Jamaica average exchange rates', 'https://boj.org.jm/market/foreign-exchange/average-exchange-rates/', ['DSL', 'GSL', 'LPG', 'KER', 'FOI'], 'value found',
    'USD annual weighted average selling rate 2024 157.22 JMD (and 2018 to 2025)')
add('statin_boj', 'Bank of Jamaica external sector statistics', 'https://boj.org.jm/statistics/external-sector/', ALL, 'no value',
    'balance of payments, debt, FDI, reserves, remittances; no imports by commodity with quantities')
# ---- gazette
add('gazette', 'Jamaica Gazette: petroleum margins and LPG price orders', 'web search: Jamaica Gazette petroleum marketing margin LPG price order 2024', LIQ, 'not found',
    'no gazetted margins found; results are press items on weekly Petrojam prices and other countries gazettes')
add('gazette', 'SCT order and rates for petroleum products (Gazette, Parliament)', 'web search: japarliament.gov.jm Special Consumption Tax order petroleum products ex-refinery price per litre ad valorem regulations 2022', LIQ, 'not found',
    'only a 2022 draft order reported by the press and a 2022 budget presentation; no 2024 schedule of specific and ad valorem rates')
add('gazette', 'SCT rate figures for fuels', 'web search: "37.4845" OR "37.7761" Jamaica special consumption tax litre', LIQ, 'not found', 'no official schedule found')
add('gazette', 'Gazette has no coal, petcoke or natural gas price instruments', 'web search: Jamaica Gazette petroleum marketing margin LPG price order 2024', ['COA', 'COK', 'NGS'], 'no value', 'none found')
# ---- customs_national
add('customs_national', 'Jamaica Customs Agency website (trade statistics)', 'https://jca.gov.jm/', ALL, 'no value', 'no trade statistics by HS code published on the site')
add('customs_national', 'MSET import statistics compiled from importer returns (Table 1)', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/JAMAICA-ENERGY-STATISTICS-2025.pdf',
    ['FOI', 'COK', 'NGS'], 'value found', 'see mset_pcj rows; used as local statistics')
add('customs_national', 'MSET import statistics compiled from importer returns (Table 1)', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/JAMAICA-ENERGY-STATISTICS-2025.pdf',
    ['COA', 'DSL', 'GSL', 'LPG', 'KER', 'JET'], 'no value', 'refined products are not split by product; no coal')
# ---- comtrade
addm('comtrade', 'UN Comtrade Jamaica imports 2024, 4-digit', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=388&period=2024&partnerCode=0&flowCode=M&cmdCode=2701,2713,2709,2710,2711',
     {'COA': ('value found', '2701: US$3,085,158, 20,806 t (weight estimated)'), 'COK': ('value found', '2713: US$3,319,980, 33,095 t'),
      'NGS': ('value found', '2711 total (LNG and LPG) - see 6-digit'), 'FOI': ('no value', '2710 total mixes all refined products'),
      'DSL': ('no value', '2710 total mixes all refined products'), 'GSL': ('no value', '2710 total'), 'LPG': ('no value', '2711 total mixes LNG and LPG'),
      'KER': ('no value', '2710 total'), 'JET': ('no value', '2710 total')})
addm('comtrade', 'UN Comtrade Jamaica imports 2024, 6-digit', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=388&period=2024&partnerCode=0&flowCode=M&cmdCode=270111,270112,270119,270120,270210,270400,271311,271312,271320,271390,270900,271012,271019,271020,271111,271112,271113,271114,271119,271121,271129',
     {'NGS': ('value found', '271111 LNG 668.31 USD/t'), 'LPG': ('value found', '271112 propane 427.47 and 271113 butane 425.82 USD/t'),
      'GSL': ('value found', '271012 light oils 759.29 USD/t'), 'DSL': ('value found', '271019 712.97 USD/t, mixed medium and heavy oils'),
      'FOI': ('no value', '271019 mixes fuel oil with diesel, jet, kerosene and lubricants'), 'KER': ('no value', 'kerosene inside 271019, not separable'),
      'JET': ('no value', 'jet fuel inside 271019, not separable'), 'COK': ('value found', '271312 33,078 t at 98.49 USD/t'),
      'COA': ('no value', '270119 has value but no weight')})
add('comtrade', 'UN Comtrade mirror: partner exports to Jamaica 2024, HS 2701 and 2713', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?period=2024&partnerCode=388&flowCode=X&cmdCode=270112,270119,2701,271311,271312,2713',
    ['COA', 'COK'], 'value found', 'USA 270112 to Jamaica 37,884 t at 80.00 USD/t FOB; USA 2713 10,620 t at 466 USD/t (not fuel grade)')
add('comtrade', 'UN Comtrade monthly data Jamaica 2024', 'https://comtradeapi.un.org/public/v1/preview/C/M/HS?reporterCode=388&period=202401,202402,202403,202404,202405,202406,202407,202408,202409,202410,202411,202412&partnerCode=0&flowCode=M&cmdCode=2701,2713',
    ['COA', 'COK'], 'no value', 'HTTP 400: preview allows one period per query; annual data used instead')
add('comtrade', 'UN Comtrade Jamaica imports 2018 to 2023 and 2025 (history)', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=388&period=2023&partnerCode=0&flowCode=M&cmdCode=2701,270112,270119,2713,271311,271312,271111,271112,271113,271012,271019',
    ['COA', 'COK', 'NGS', 'LPG', 'GSL'], 'value found', 'annual CIF and weight by code; 2025 LNG unit value 1378.6 USD/t looks anomalous (weight halved)')
# ---- energy_balance
add('energy_balance', 'MSET National Energy Balance 2024', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/MSETT-National-Energy-Balance-2024_Update.pdf', ALL, 'no value',
    'balance in KBOE; net or gross basis and conversion factors not stated; no prices')
add('energy_balance', 'MSET National Energy Balance 2023', 'https://www.mset.gov.jm/wp-content/uploads/2021/07/MSETT-National-Energy-Balance-2023-Updated-Sept-19-2025_FINAL.pdf', ALL, 'no value',
    'same layout; no basis or factors stated')
add('energy_balance', 'OLADE energy balance methodology (SIELAC second source)', 'https://biblioteca.olade.org/opac-tmpl/Documentos/old0382.pdf', ALL, 'blocked HTTP 403',
    'HTML 403 page instead of the PDF; not retried; on manual list')
# ---- other leads
add('other_wto_tpr', 'WTO Trade Policy Review Jamaica 2024 (SCT on petroleum)', 'https://www.wto.org/english/tratop_e/tpr_e/s457_e.pdf', LIQ, 'no value',
    'describes SCT as specific plus ad valorem and diesel for public electricity exempt by end use; gives no rates')
add('other_cac', 'Consumer Affairs Commission petrol price surveys (retail margins)', 'https://www.cac.gov.jm/portal/index.php/special-features/publications/category/10-survey-results', ['DSL', 'GSL', 'LPG', 'KER'], 'no value',
    'survey results list has no petrol or LPG files; the petrol price tool is an interactive app (cacresearchnow.shinyapps.io) without downloadable files')
add('other_tax_search', 'Special Consumption Tax rates for petroleum products 2024', 'web search: Jamaica Special Consumption Tax petroleum products rates per litre 2024 gasolene E10 87 diesel ad valorem TAJ',
    LIQ, 'no value', 'only the ADO rate stated by OUR (37.4845 J$/L) was found; no rates for gasoline, kerosene, LPG or jet')
add('other_essj', 'PIOJ Economic and Social Survey Jamaica 2024 energy chapter (imports by product)', 'web search: Jamaica petroleum imports 2024 by product value barrels gasolene auto diesel fuel oil LPG LNG coal petcoke Economic and Social Survey energy',
    ALL, 'not found', 'no 2024 product-level import table found online; press summaries only')

rows = []
for lead_id, lead, url, m in A:
    for f in ALL:
        if f in m:
            res, det = m[f]
            rows.append(dict(country='Jamaica', fuel=f, lead_id=lead_id, lead=lead, url_or_query=url, date=D, result=res, detail=det))
with open(os.path.join(OUT, 'search_log_JAM.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['country','fuel','lead_id','lead','url_or_query','date','result','detail']); w.writeheader(); w.writerows(rows)

MAN = [
 ('https://statinja.gov.jm/InternationalMerchandiseTradeTable7.aspx', 'STATIN International Merchandise Trade Statistics search (imports by HS code, 2024)', 'Statistical Institute of Jamaica',
  'Jamaica imports 2024 by HS 8-digit with CIF value and quantity for 2701, 2713, 2710 (gasoline, diesel, jet, kerosene, fuel oil separately) and 2711',
  'DIST_COA; DIST_COK; DIST_KER; DIST_JET; DIST_DSL; DIST_GSL; DIST_LPG', 'national customs unit values; would replace the estimated Comtrade coal weight and split HS 271019',
  'search form works only through browser postbacks (no file URL)', 'statin_imports_hs_2024.xlsx', 2),
 ('https://www.jpsco.com/', 'JPS Annual Report 2024 and monthly fuel rate filings', 'Jamaica Public Service Company Limited',
  'fuel cost by fuel type and plant, 2024; heat content basis of fuel prices', 'DIST_NGS; DIST_FOI; DIST_DSL', 'second local source for generator prices and for IPP plant prices beyond June and July',
  'Incapsula bot challenge (HTTP 200 with challenge page)', 'jps_annual_report_2024.pdf', 3),
 ('https://our.org.jm/wp-content/uploads/2025/12/Annual-Report-2024-2025-low-res-compressed.pdf', 'OUR Annual Report 2024-2025 (full-resolution or text version)', 'Office of Utilities Regulation',
  'Tables 24 and 25 (pages 58 and 59): 2024 annual and monthly HFO, ADO and NG prices to JPS', 'DIST_NGS; DIST_FOI; DIST_DSL', 'values were read from low-resolution page images; a text copy would confirm them and the 2024 ADO annual value',
  'image only (low-resolution compressed PDF)', 'our_annual_report_2024_2025_full.pdf', 3),
 ('https://biblioteca.olade.org/opac-tmpl/Documentos/old0382.pdf', 'OLADE energy balance methodology', 'OLADE',
  'statement of net or gross calorific basis and conversion factors used in SIELAC balances', 'calorific basis for all Jamaica rows', 'national balance states neither basis nor factors',
  'blocked HTTP 403', 'olade_methodology_old0382.pdf', 3),
 ('https://www.petrojam.com/price-index', 'Petrojam weekly price index (ex-refinery and billing prices by product)', 'Petrojam Limited',
  'weekly 2024 ex-refinery (pre-tax import parity) prices for HFO, ADO, ULSD, E10-87, E10-90, kerosene, jet (turbo), propane, butane, and the SCT per product',
  'DIST_FOI; DIST_DSL; DIST_GSL; DIST_LPG; DIST_KER; DIST_JET', 'only source of pre-tax product prices in Jamaica for 2024; closes kerosene and jet ASSUMPTION candidates',
  'blocked HTTP 403', 'petrojam_price_index_2024.pdf', 4),
 ('https://www.petrojam.com/', 'Petrojam annual reports 2023/24 and 2024/25 (from the site menu)', 'Petrojam Limited',
  'sales volumes and revenue by product; import costs of crude and products', 'DIST_FOI; DIST_DSL; DIST_GSL; DIST_LPG; DIST_KER; DIST_JET', 'average refinery realisations by product',
  'blocked HTTP 403', 'petrojam_annual_report_2024_25.pdf', 5),
 ('https://cacresearchnow.shinyapps.io/PetrolApp/', 'Consumer Affairs Commission petrol price comparison tool', 'Consumer Affairs Commission',
  '2024 retail pump prices of E10-87, E10-90, diesel, ULSD, kerosene and LPG by station', 'DIST_GSL; DIST_DSL; DIST_LPG; DIST_KER', 'retail margin = retail price minus Petrojam billing price',
  'interactive app without downloadable files', 'cac_petrol_prices_2024.csv', 6),
]
with open(os.path.join(OUT, 'manual_JAM.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['url','title','publisher','should_hold','rows_it_closes','why_needed','how_failed','save_as','weight_rank'])
    for m in sorted(MAN, key=lambda r: r[-1]): w.writerow(m)
print('search log rows', len(rows), 'manual', len(MAN))
