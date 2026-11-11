"""Step 8: write proposals.csv, proposals_summary.csv, and assemble sources.csv, constants.csv, search_log.csv.

Usage: py -I step8_assemble.py <job_folder> <local_prices_folder>
"""
import sys, os, re, glob
import pandas as pd

job, lp = sys.argv[1], sys.argv[2]
X = os.path.join(job, 'downloads', '_extract')
D = os.path.join(job, 'downloads')
YEARS = list(range(2021, 2051))

cur = pd.read_csv(os.path.join(job, 'cost_rows_current.csv'))
pc = pd.read_csv(os.path.join(job, 'plant_costs.csv'))
key = cur[['sheet', 'Tech.ID', 'Tech', 'Parameter', 'Unit']].rename(columns={'Tech': 'technology', 'Parameter': 'parameter'})
pr = pc.merge(key, on=['technology', 'parameter'], how='left')
missing = pr[pr.sheet.isna()]
if len(missing):
    print('rows without a workbook row:', missing[['technology', 'parameter']].drop_duplicates().to_string())
pr = pr[pr.sheet.notna()]
prop = pd.DataFrame({
    'country': 'Ecuador', 'sheet': pr.sheet, 'Tech.ID': pr['Tech.ID'].astype(int), 'Tech': pr.technology, 'Parameter': pr.parameter,
    'fuel_scenario': pr.fuel_scenario, 'year': pr.year, 'current_value': pr.current_value, 'proposed_value': pr.proposed_value,
    'unit': pr.Unit, 'change_class': pr.change_class, 'basis_class': pr.basis_class, 'source_ids': pr.source_ids,
    'derivation': pr.derivation, 'assumption_sentence': pr.assumption_sentence.fillna('')})
prop = prop.sort_values(['sheet', 'Tech.ID', 'Tech', 'Parameter', 'fuel_scenario', 'year']).reset_index(drop=True)
prop.to_csv(os.path.join(job, 'proposals.csv'), index=False)

# summary: STEPS for fuel rows, ALL otherwise
summ = []
for (t, p), g in prop.groupby(['Tech', 'Parameter']):
    g = g[g.fuel_scenario.isin(['ALL', 'STEPS'])]
    rec = {'Tech': t, 'Parameter': p, 'fuel_scenario': g.fuel_scenario.iloc[0], 'unit': g.unit.iloc[0]}
    for y in (2024, 2030, 2050):
        r = g[g.year == y]
        c, v = (float(r.current_value.iloc[0]) if pd.notna(r.current_value.iloc[0]) else None), float(r.proposed_value.iloc[0])
        rec[f'current_{y}'] = c
        rec[f'proposed_{y}'] = round(v, 4)
        rec[f'change_pct_{y}'] = round(100 * (v - c) / c, 1) if c not in (None, 0) else ''
    rec['basis_classes'] = ';'.join(sorted(set(g.basis_class)))
    rec['change_classes'] = ';'.join(sorted(set(g.change_class)))
    summ.append(rec)
pd.DataFrame(summ).to_csv(os.path.join(job, 'proposals_summary.csv'), index=False)

# ---------- sources ----------
PATH_RE = re.compile(r'([A-Za-z]:\\[^,;"\)]*|/c/[^,;"\) ]*)')


def clean(s):
    if not isinstance(s, str):
        return s
    s = PATH_RE.sub(lambda m: 'local copy ' + os.path.basename(m.group(0).rstrip('\\/')), s)
    return s.replace(chr(0x2014), '-').replace(chr(0x2013), '-')


lps = pd.read_csv(os.path.join(lp, 'sources.csv'))
recs = {}
for f in ['sources_ben.csv', 'sources_ccg.csv', 'sources_pmc.csv', 'sources_ecx.csv', 'sources_atb.csv']:
    p = os.path.join(X, f)
    if not os.path.exists(p):
        continue
    s = pd.read_csv(p)
    for r in s.itertuples(index=False):
        rid = str(r.id).strip()
        if ' to ' in rid:
            continue  # range pseudo-row
        recs.setdefault(rid, []).append(r._asdict())
# LAC_LOCAL_PRICES reuse: ECU-*, GEN-*
used_ids = set()
for col in prop.source_ids.astype(str):
    used_ids.update(x.strip() for x in col.split(';') if x.strip())
cons_parts = [pd.read_csv(os.path.join(X, f)) for f in ('constants_fuel.csv', 'constants_plant.csv')]
cons = pd.concat(cons_parts).drop_duplicates('name', keep='first')
for col in cons.source_id.astype(str):
    used_ids.update(x.strip() for x in col.split(';') if x.strip())
for rid in sorted(used_ids):
    if rid.startswith(('ECU-', 'GEN-')):
        m = lps[lps.id == rid]
        if len(m):
            d = m.iloc[0].to_dict()
            d['downloaded_file'] = 'LP/' + d['downloaded_file']
            d['retrieval_date'] = d['retrieval_date']
            d['note_reuse'] = 'reused from LAC_LOCAL_PRICES (opened and saved by that job); file copied into this job'
            if rid in recs:  # merge locators and files from this job's own record
                e = recs[rid][0]
                d['page_or_table'] = f"{d['page_or_table']}; {e['page_or_table']}"
                d['downloaded_file'] = d['downloaded_file'] + '; ' + str(e['downloaded_file']).split(' (')[0]
                d['rows_and_constants_supported'] = f"{d['rows_and_constants_supported']}; {e['rows_and_constants_supported']}"
            recs[rid] = [d]
# extra source: Comtrade partner query made in this job
recs['FUEL-001'] = [dict(id='FUEL-001', url='https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=218&period=2024&flowCode=M&cmdCode=270111,271311',
                         title='UN Comtrade public preview API: Ecuador imports 2024 of anthracite (HS 270111) and petroleum coke (HS 271311) by partner',
                         publisher='United Nations Statistics Division (UN Comtrade)', date='2024 data', retrieval_date='2026-11-10',
                         downloaded_file='FUEL/comtrade_ECU_2024_M_270111_271311_by_partner.json',
                         page_or_table='data[]: partnerCode 604 (Peru) 3,296,425 USD of 3,472,414 USD for HS 270111; partnerCode 842 (USA) 30,075,423 USD of 30,287,760 USD for HS 271311',
                         rows_and_constants_supported='DIST_COA benchmark choice (origin Peru); DIST_COK benchmark choice (origin USA)')]
out = []
for rid, lst in recs.items():
    d = lst[0]
    out.append({k: clean(d.get(k, '')) for k in ['id', 'url', 'title', 'publisher', 'date', 'retrieval_date', 'downloaded_file', 'page_or_table', 'rows_and_constants_supported']})
src = pd.DataFrame(out).sort_values('id')
# retrieval date must be a date only
src['downloaded_file'] = src.downloaded_file.astype(str).map(lambda v: '; '.join(x.split(' (')[0].strip() for x in v.split(';') if x.strip()))
src['retrieval_date'] = src.retrieval_date.astype(str).str.extract(r'(\d{4}-\d{2}-\d{2})')[0]
src.to_csv(os.path.join(job, 'sources.csv'), index=False)

cons['page_or_table'] = cons.page_or_table.map(clean)
cons.to_csv(os.path.join(job, 'constants.csv'), index=False)

# ---------- search log ----------
logs = []
for f in sorted(glob.glob(os.path.join(X, 'search_log_*.csv'))):
    tag = os.path.basename(f)[len('search_log_'):-4]
    s = pd.read_csv(f)
    for r in s.itertuples(index=False):
        logs.append(dict(row=str(r.row) if tag in ('atb',) else (str(r.row) if not str(r.row).isdigit() else f'{tag} lead {r.row}'),
                         lead=clean(r.lead), url_or_query=clean(r.url_or_query), date=r.date, result=clean(r.result)))
main = pd.read_csv(os.path.join(X, 'search_log_main_input.csv'))
for r in main.itertuples(index=False):
    logs.append(dict(row=r.row, lead=r.lead, url_or_query=r.url_or_query, date=r.date, result=r.result))
pd.DataFrame(logs).to_csv(os.path.join(job, 'search_log.csv'), index=False)
print('proposals', len(prop), 'summary', len(summ), 'sources', len(src), 'constants', len(cons), 'log', len(logs))
