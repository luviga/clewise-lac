"""Register the FR2 source ids of D3 and D2 (scripts/sources_extra.csv) from the research tables. URL corrections found by
this session are applied here (Ecuador NID: Climate Policy Radar CDN copy, byte-identical to the saved file)."""
import csv
import pandas as pd

JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
FIELDS = ['id', 'url', 'title', 'publisher', 'date', 'accessed', 'sha256', 'file', 'page_or_table']
REG = {
    'FR2-D3-IPCC': ('d3_ef', 'IPCC2006_V2_Ch2_Stationary_Combustion.pdf', None),
    'FR2-D3-AR5': ('d3_ef', 'IPCC_AR5_WG1_Ch08.pdf', None),
    'FR2-D3-HONNIR': ('d3_ef', 'HON_NIR_2024.pdf', None),
    'FR2-D3-HONBEN19': ('d3_ef', 'HON_BEN_2019.pdf', None),
    'FR2-D3-DRNID': ('d3_ef', 'DR_NID_2025.pdf', None),
    'FR2-D3-CNEGEN': ('d2_dr', 'CNE_DataCNE_GeneracionFuenteSENI.xlsx', None),
    'FR2-D2-IRENA25': ('d2_dr', 'IRENA_DAT_RE_Statistics_2025.pdf', None),
    'FR2-D2-UNHYD': ('d2_dr', 'undata_EL_016HY_DR.html', None),
    'FR2-D3-ECUNID': ('d3_ef', 'ECU_NID_2024.pdf',
                      'https://cdn.climatepolicyradar.org/navigator/ECU/2024/ecuador-national-inventory-report-nir-2024_8c731b52bc1d6e93a107d2251cf6204a.pdf'
                      ' (Ecuador NID 2024, record https://climate-laws.org/document/ecuador-national-inventory-report-nir-2024_67ea; '
                      'UNFCCC copy https://unfccc.int/sites/default/files/resource/e.%202024.12.27_NID_5CN1RBT_v7_final.pdf returns a bot-check page)'),
}
EXTRA_ROWS = []   # D2 sources appended by later steps (same FIELDS)
out = []
tables = {}
for topic in set(v[0] for v in REG.values()):
    tables[topic] = pd.read_csv(f'{JOB}/research/{topic}_sources.csv', dtype=str, keep_default_na=False)
for i, (topic, fname, url) in REG.items():
    t = tables[topic]
    r = t[t.file.str.endswith(fname)].iloc[0]
    out.append(dict(id=i, url=url or r.url, title=r.title, publisher=r.publisher, date=r.date, accessed=r.accessed,
                    sha256=r.sha256, file=r.file, page_or_table=r.page_or_table))
try:
    for r in csv.DictReader(open(JOB + '/scripts/sources_extra_d2.csv', encoding='utf-8')):
        out.append({k: r.get(k, '') for k in FIELDS})
except FileNotFoundError:
    pass
with open(JOB + '/scripts/sources_extra.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
    w.writeheader()
    w.writerows(out)
print(len(out))
