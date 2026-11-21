"""Write sources.csv: every source id cited in proposals.csv (and the currency-year evidence),
with URL, title, publisher, date, accessed, SHA-256 and page or table.
Ids re-downloaded by this job point at downloads/; ids only reused from earlier jobs keep
that job's record (and the SHA-256 of that job's copy when the file is on disk)."""
import csv, glob, hashlib, os, re
import pandas as pd

JOB = 'C:/clw_fix/_LAC_HUB/fix_run_20261111T200825Z/'
HUB = 'C:/clw_fix/_LAC_HUB/'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


D = JOB + 'downloads/'
A = '2026-11-11'
mine = {
    'CSD-008': ('https://cne.gob.do/wp-admin/admin-ajax.php?action=outofthebox-download&OutoftheBoxpath=%2Fpen2022-2037.pdf&lastpath=%2F&account_id=dbid:AAAGpYR0ODh0f0jJZRlCsjhWYMYovXEms_Q&listtoken=255346f20b4341ea85f9ebf4917022f4&dl=1',
                'Plan Energetico Nacional 2022-2036 (file PEN2022-2037.pdf)', 'Comision Nacional de Energia, Republica Dominicana', '2022 (PDF created 2022-08-05)',
                'r4/PEN2022-2037.pdf', 'Tablas 220 (PDF p.345), 223 (p.347), 229 (p.350); no currency year stated anywhere in the document (searched)'),
    'CSD-009': ('https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2023/Aug/IRENA_Renewable_power_generation_costs_in_2022.pdf',
                'Renewable Power Generation Costs in 2022', 'IRENA', '2023-08', 'r4/IRENA_RPGC_2022.pdf', 'Table H.1 p.15 (header 2022 USD/kW); O&M p.162, p.173, p.183'),
    'PSJ-002': ('https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2026/Jul/IRENA_TEC_RPGC_in_2025_2026.pdf',
                'Renewable Power Generation Costs in 2025', 'IRENA', '2026-07', 'r4/IRENA_RPGC_2025.pdf', 'p.13 note 3 "All values in 2025 USD"; p.123 geothermal O&M 128 USD/kW/yr; p.133 bioenergy variable O&M 0.004 USD/kWh'),
    'NAT-001': ('https://mem.gob.gt/wp-content/uploads/2026/01/PEIG_2026_2050_MEM.pdf', 'Plan de Expansion Indicativo del Sistema de Generacion 2026-2050',
                'Ministerio de Energia y Minas, Guatemala', 'enero de 2026 (PDF created 2026-01-12)', 'r4/PEIG_2026_2050_MEM.pdf',
                'Tabla 6 PDF p.35; no currency year stated (only the 2024 exchange rate reference on p.15)'),
    'NAT-002': ('https://www.cnee.gob.gt/PlanesExpansion/2020-2050/PlanExpansionGeneracion2020-2050.pdf', 'Plan de Expansion del Sistema de Generacion 2020-2050',
                'MEM Guatemala (UPEM), hosted by CNEE', '2020 (PDF created 2020-04-29)', 'r4/PEG_2020_2050_CNEE.pdf', 'Tablas 4 and 5 PDF p.41-42; PDF p.8 "millones de dolares de 2020"'),
    'HON-018': ('https://cnd.enee.hn/wp-content/uploads/2024/07/G01-PIEG-2024-2033-Aprobado.pdf', 'Plan Indicativo de Expansion de la Generacion 2024-2033 (aprobado)',
                'Operador del Sistema (ODS) / CND, Honduras', '2024-07', 'r4/G01-PIEG-2024-2033-Aprobado.pdf',
                'Tabla 7 PDF p.42; text p.41-42: the set of values is referenced to 2023 prices'),
    'PSJ-004': ('https://www.mset.gov.jm/wp-content/uploads/2020/03/2018-Jamaica-Integrated-Resource-Feb-21-2020.pdf', '2018 Jamaica Integrated Resource Plan (IRP-1)',
                'MSET Jamaica (DNV GL)', '2020-02-21', 'r4/JAM_IRP_2018_mset_Feb2020.pdf',
                'PDF p.107 BESS "Capital Cost in 2018 US dollars: $816/kW", O&M $50/kW-yr; p.147 present worth in 2018 dollars; Appendix C p.182'),
    'PSJ-005': ('https://our.org.jm/wp-content/uploads/2021/01/generation_expansion_plan_2010_1.pdf', 'Generation Expansion Plan 2010', 'Office of Utilities Regulation, Jamaica',
                '2010', 'r4/OUR_generation_expansion_plan_2010.pdf', 'PDF p.147 combined cycle 1317 USD/kW; text: constant dollars at January 1, 2010 price levels'),
    'PMC-008': ('https://github.com/PLANMICC/OSeMOSYS_Ecuador/raw/7483e67a5a7a733b4a2697a950eda23a27929df7/Energia/Data_inputs/Calibracion%20y%20BAU/Requerimiento_Datos_Energia_Costos_Ecuador_v6.xlsx',
                'Requerimiento_Datos_Energia_Costos_Ecuador_v6.xlsx (PLANMICC energy cost data workbook)', 'PLANMICC, OSeMOSYS_Ecuador repository', '2024-09-24 (commit)',
                'r4/Requerimiento_Datos_Energia_Costos_Ecuador_v6.xlsx', 'all sheets searched: units Millones de US$ per PJ, GW or GW-ano; no currency year stated'),
    'BEN-004': ('https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2016&endyear=2025&annualaverage=true (and startyear=2010&endyear=2019)',
                'CPI for All Urban Consumers (CPI-U), all items, U.S. city average, not seasonally adjusted (CUUR0000SA0), annual averages', 'U.S. Bureau of Labor Statistics',
                'series as of 2026-11-11', 'r4/bls_v2_cpiu_2016_2025.json; r4/bls_v2_cpiu_2010_2019.json',
                'period M13 (annual average): 2010 218.056, 2018 251.107, 2019 255.657, 2020 258.811, 2021 270.970, 2022 292.655, 2023 304.702, 2024 313.689, 2025 321.943'),
    'FXR-001': ('https://atb.nlr.gov/electricity/2023/index', '2023 Electricity ATB Technologies and Data Overview', 'NREL (served from atb.nlr.gov)', '2023 edition web page',
                'r4/atb2023_index.html', 'overview text "Monetary values are in 2021$" (twice; one older paragraph says 2020$); old host atb.nrel.gov did not resolve'),
    'FXR-002': ('https://atb.nlr.gov/electricity/2024/index', '2024 Electricity ATB Technologies and Data Overview', 'NREL (served from atb.nlr.gov)', '2024 edition web page',
                'r4/atb2024_index.html', 'overview text "Monetary values are in 2022$"'),
    'BEN-005': ('https://www.iea.org/files/9753df19-0a71-422a-b725-012c555763b3/WorldEnergyOutlook2025.pdf (from https://www.iea.org/reports/world-energy-outlook-2025)',
                'World Energy Outlook 2025', 'International Energy Agency (CC BY 4.0)', '2025-11', 'r3/WorldEnergyOutlook2025.pdf',
                'Table 2.3 PDF p.109: IEA crude oil USD (MER, 2024) per barrel 2024 79, STEPS 2035 80, 2050 76'),
    'BEN-001': ('https://www.eia.gov/dnav/pet/hist_xls/RBRTEa.xls', 'Europe Brent Spot Price FOB (Dollars per Barrel), annual', 'U.S. Energy Information Administration',
                'series as of 2026-11-11', 'r3/RBRTEa.xls', 'sheet Data 1: 2018 71.34, 2019 64.30, 2020 41.96, 2021 70.86, 2022 100.93, 2023 82.49, 2024 80.52, 2025 69.14'),
    'GEN-001': ('https://unstats.un.org/unsd/energystats/pubs/yearbook/2023/09ii.pdf', '2023 Energy Statistics Yearbook, Table II Selected conversion factors for crude oil and oil products',
                'United Nations Statistics Division', '2023 edition', 'r3/UNSD_EnergyYearbook2023_TableII.pdf', 'Table II: conventional crude oil 7.32 barrels per metric ton'),
    'GEN-002': ('https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_1_Ch1_Introduction.pdf', '2006 IPCC Guidelines, Volume 2 Energy, Chapter 1 Introduction',
                'IPCC TFI (IGES)', '2006', 'r3/IPCC2006_V2_Ch1.pdf', 'Table 1.2 p.1.18: crude oil net calorific value 42.3 TJ/Gg'),
    'CCG-002': ('https://zenodo.org/records/5498094/files/Ecuador%20Base%20SAND.xlsm?download=1', 'CCG Starter Data Kit: Ecuador v1.0, clicSAND workbook Ecuador Base SAND.xlsm',
                'Zenodo (Climate Compatible Growth), doi:10.5281/zenodo.5498094', '2021-09-09', 'ccg/Ecuador_Base_SAND.xlsm',
                'sheet Parameters rows 19789 (PWRSOL001), 19792 to 19794 (PWRHYD001 to 003), 19795 (PWRWND001), 48464 (MINOIL VariableCost); md5 equals the Zenodo record'),
    'CCG-001': ('https://zenodo.org/api/records/5498094', 'CCG Starter Data Kit: Ecuador v1.0, record metadata', 'Zenodo', '2021-09-09', 'ccg/zenodo_record_5498094.json',
                'files[] md5 of Ecuador Base SAND.xlsm 14490a63aa4680e04be760df625600cb'),
    'CRC-006': ('https://www.minae.go.cr/energia/ben/Informe%20Balance%20de%20Energia%202022.pdf', 'Balance Energetico Nacional de Costa Rica 2022 (Informe)', 'MINAE, Costa Rica', '2023',
                'cr/Informe_Balance_de_Energia_2022.pdf',
                'PDF p.40 Tabla 3: Carbon Mineral 6.67 TJ. A fresh download on 2026-11-11 returned HTTP 403; the file is the manual download of LAC_LOCAL_PRICES (same SHA-256)'),
}
for i in ['INT-001', 'PSJ-001']:
    mine[i] = mine['CSD-009']

rows = []
for k, (url, title, pub, date, f, page) in mine.items():
    fs = [D + x.strip() for x in f.split(';')]
    rows.append(dict(id=k, url=url, title=title, publisher=pub, date=date, accessed=A, local_file='; '.join('downloads/' + x.strip() for x in f.split(';')),
                     sha256='; '.join(sha(x) for x in fs), page_or_table=page, origin='downloaded by this job'))


def parse_md(path, prefix):
    out = []
    for ln in open(path, encoding='utf-8'):
        s = ln.strip().lstrip('-').strip()
        if not s.startswith(('| ' + prefix, prefix)): continue
        parts = [x.strip() for x in s.strip('|').split('|')]
        if not parts[0].startswith(prefix) or len(parts) < 6 or not parts[1].startswith('http'): continue
        out.append(parts)
    return out


for path, prefix in [(JOB + 'research/jam_hydro.md', 'JAMF-'), (JOB + 'research/r1_sources.md', 'R1F-'), (JOB + 'research/ecu_crude.md', 'ECUF-')]:
    if not os.path.exists(path): continue
    for parts in parse_md(path, prefix):
        pid = parts[0]
        shav = next((x for x in parts if re.fullmatch(r'(SHA-256 )?[0-9a-f]{64}', x)), '')
        shav = shav.replace('SHA-256 ', '')
        loc = next((x.strip('`') for x in parts if 'downloads/' in x), '')
        rows.append(dict(id=pid, url=parts[1], title=parts[2] if len(parts) > 2 else '', publisher=parts[3] if len(parts) > 3 else '',
                         date=parts[4] if len(parts) > 4 else '', accessed=A, local_file=loc, sha256=shav,
                         page_or_table=parts[-1] if len(parts) > 8 else '', origin='downloaded by this job (research notes ' + os.path.basename(path) + ')'))

# reused ids from earlier jobs
have = {r['id'] for r in rows}
P = pd.read_csv(JOB + 'proposals.csv', dtype=str, keep_default_na=False)
cited = sorted(set(s for x in P.source_ids for s in x.split(';') if s))
earlier = {}
for f in glob.glob(HUB + 'cost_*/sources.csv'):
    d = pd.read_csv(f, dtype=str, keep_default_na=False)
    d.columns = [c.strip() for c in d.columns]
    idc = 'id' if 'id' in d.columns else 'source_id'
    for _, r in d.iterrows():
        earlier.setdefault(r[idc], (f, r))
for k in cited:
    if k in have: continue
    if k not in earlier:
        rows.append(dict(id=k, url='', title='', publisher='', date='', accessed='', local_file='', sha256='', page_or_table='', origin='NOT FOUND in earlier records'))
        continue
    f, r = earlier[k]
    job = f.replace('\\', '/').split('/')[-2]
    g = lambda *names: next((r[n] for n in names if n in r.index and r[n]), '')
    rows.append(dict(id=k, url=g('url'), title=g('title'), publisher=g('publisher'), date=g('date', 'edition_or_date'), accessed=g('retrieval_date'),
                     local_file=g('downloaded_file'), sha256='', page_or_table=g('page_or_table', 'locator'),
                     origin=f'reused: downloaded and read by {job} (value carried in the proposals_all derivation); not re-downloaded by this job'))
o = pd.DataFrame(rows).drop_duplicates('id')
o.to_csv(JOB + 'sources.csv', index=False, lineterminator='\n')
print(len(o), 'missing in cited:', [k for k in cited if k not in set(o.id)])
print(o[o.origin.str.startswith('reused') | o.origin.str.startswith('NOT')][['id', 'origin']].to_string())
