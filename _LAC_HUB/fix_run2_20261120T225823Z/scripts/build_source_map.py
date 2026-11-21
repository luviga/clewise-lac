"""A0: source_map.csv from research/map_*_map.csv (Read the Docs leads -> cited external documents), with the matching model
row (A-O workbook, sheet, row) and its current base value where the map names a model tech and parameter."""
import glob, os
import openpyxl
import pandas as pd

JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
BASE = 'C:/clw_base_4ba69d6/'
AO = {'CostaRica': 'CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
      'Ecuador': 'Ecuador/ECU_Energy', 'Guatemala': 'Guatemala/GUA_ENERGY', 'Honduras': 'Honduras/HON_ENERGY',
      'Jamaica': 'Jamaica/JAM_ENERGY'}
frames = [pd.read_csv(f, dtype=str, keep_default_na=False) for f in sorted(glob.glob(JOB + '/research/map_*_map.csv'))]
M = pd.concat(frames, ignore_index=True)
idx = {}
for c in set(M.country):
    if c not in AO:
        continue
    p = BASE + AO[c] + '/A1_Outputs/A-O_Parametrization.xlsx'
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue
        h = list(rows[0])
        if 'Tech' not in h or 'Parameter' not in h:
            continue
        ti, pi = h.index('Tech'), h.index('Parameter')
        vi = h.index('Value') if 'Value' in h else next((k for k, x in enumerate(h) if str(x) in ('2021', '2021.0')), None)
        for n, r in enumerate(rows[1:], start=2):
            idx.setdefault((c, str(r[ti]), str(r[pi])), (ws.title, n, r[vi] if vi is not None else None))
out = []
for _, r in M.iterrows():
    hit = idx.get((r.country, r.get('model_tech', ''), r.get('model_parameter', '')))
    out.append(dict(country=r.country, documentation_page=r.doc_page_url, parameter_or_technology=r.parameter_or_technology,
                    cited_title=r.cited_document_title, cited_publisher=r.cited_publisher, cited_year=r.cited_year,
                    cited_url_or_doi=r.cited_url_or_doi, downloaded=r.downloaded, file=r.file, sha256=r.sha256,
                    page_or_table=r.page_or_table, value_printed=r.value_printed,
                    model_workbook=(AO[r.country] + '/A1_Outputs/A-O_Parametrization.xlsx') if hit else '',
                    model_sheet=hit[0] if hit else '', model_row=hit[1] if hit else '',
                    model_value_base=(hit[2] if hit else ''), model_tech=r.get('model_tech', ''),
                    model_parameter=r.get('model_parameter', ''), note=r.get('note', '')))
pd.DataFrame(out).to_csv(JOB + '/source_map.csv', index=False, lineterminator='\n')
print(len(out), pd.DataFrame(out).groupby('country').size().to_dict())
