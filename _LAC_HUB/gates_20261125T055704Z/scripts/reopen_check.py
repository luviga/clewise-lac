"""Step 1.2 reopen gate: for every source in sources.csv, open the local copy and confirm one value it supplies
(number as printed, unit, year, page). Candidate values come from the registers that cite the source:
NDC verify value table (value_printed, page), cost-sources proposals (source_value), vehicle-price unit values,
research_R1.csv (value_printed). The number is searched in the text of the copy (PDF pages with pdftotext, HTML,
CSV, JSON, XLSX cells). Writes reopen_check.csv."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import glob
import html
import io
import re
import subprocess
from pathlib import Path

HUB = M.ROOT / '_LAC_HUB'
PDFTOTEXT = r'C:\Program Files\Git\mingw64\bin\pdftotext.exe'
paths = {r['id']: r['local_path'] for r in csv.DictReader(open(M.JOB / 'work' / 'source_paths.csv', encoding='utf-8'))}
ARCH = M.ARCHIVE
# API responses saved as JSON by the earlier jobs (one file per period); the first period is opened
paths.setdefault('COMTRADE-JAM', '')
paths['COMTRADE-JAM'] = paths['COMTRADE-JAM'] or str(ARCH / 'vehicle_prices_20261123T163210Z' / 'comtrade' / 'comtrade_JAM_imports_2019.json')
paths['GEN-001'] = paths.get('GEN-001') or str(ARCH / 'cost_sources_20261122T234333Z' / 'GEN' / 'bls_CUUR0000SA0_2015_2024_annualaverage.json')
srcs = list(csv.DictReader(open(M.JOB / 'sources.csv', encoding='utf-8')))

cand = {}
for r in csv.DictReader(open(HUB / 'ndc_verify_20261121T233937Z' / 'scenario_values.csv', encoding='utf-8')):
    cand.setdefault(r['source_id'], []).append((r['value_printed'], r['unit_printed'], r['year'], r['page'], r['value_id']))
for p in glob.glob(str(HUB / 'cost_sources_20261122T234333Z' / '*' / 'proposals_*.csv')):
    for r in csv.DictReader(open(p, encoding='utf-8')):
        for s in re.split(r'[;|, ]+', r.get('source_ids', '') or ''):
            if s and r.get('source_value'):
                cand.setdefault(s, []).append((r['source_value'], r.get('source_unit', ''), r.get('year', ''), '', f"{r['model']} {r['tech']} {r['parameter']}"))
for r in csv.DictReader(open(M.JOB / 'work' / 'research_R1.csv', encoding='utf-8')):
    sid = {'CRI_UNA': 'ALN-UNA-2024', 'ECU_CEPAL': 'ALN-CEPAL-ECU-2021', 'JAM_PIMS': 'ALN-JAM-PIMS-2016', 'B_imf': 'ALN-IMF-2023',
           'C_ipcc': 'ALN-IPCC2006-V2C2', 'CND_083': 'ALN-EOR-MEX-2021', 'EOR_MCTP': 'ALN-EOR-MCTP-2025',
           'GTM_CNEE': 'ALN-CNEE-2024'}
    for k, v in sid.items():
        if k in r['local_file'] and r['value_printed']:
            cand.setdefault(v, []).append((r['value_printed'], r['unit_printed'], r['year'], r['page_or_table'], r['item']))
cand.setdefault('ECU-05', []).insert(0, ('PCG - AR5', 'GWP table (CH4 28, N2O 265)', '2024', 'p.50', 'AR5 global warming potentials used by the inventory'))
cand.setdefault('GEN-001', []).insert(0, ('2024', 'CPI-U annual average', '2024', 'series CUUR0000SA0', 'BLS CPI-U series'))
cand.setdefault('JAM-GLEANER-2022-10-01', []).append(('15 megawatts', 'MW', '2022', 'article body', 'Frome factory own generating capacity, grid sale plans failed'))


def pages(p):
    p = Path(p)
    if p.suffix.lower() == '.pdf':
        out = subprocess.run([PDFTOTEXT, '-layout', str(p), '-'], capture_output=True)
        return out.stdout.decode('utf-8', 'replace').split('\f')
    if p.suffix.lower() in ('.html', '.htm'):
        t = p.read_text(encoding='utf-8', errors='replace')
        t = re.sub(r'<script.*?</script>', ' ', t, flags=re.S)
        return [html.unescape(re.sub(r'<[^>]+>', ' ', t))]
    if p.suffix.lower() in ('.xlsx', '.xls'):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(p.read_bytes()), read_only=True, data_only=True)
        return [' '.join(str(c) for row in ws.iter_rows(values_only=True) for c in row if c is not None) for ws in wb.worksheets]
    return [p.read_text(encoding='utf-8', errors='replace')]


def variants(v):
    s = str(v).strip()
    m = re.search(r'-?\d[\d,]*\.?\d*', s)
    if not m:
        return [s] if s else []
    n = m.group(0)
    out = {n, n.replace(',', ''), n.replace(',', '.')}
    try:
        f = float(n.replace(',', ''))
        out |= {f'{f:,.0f}', f'{f:.0f}', f'{f:,.2f}', f'{f:.2f}', f'{f:g}', f'{f:,.1f}', f'{f:.1f}'}
        out |= {x.replace(',', 'X').replace('.', ',').replace('X', '.') for x in list(out)}
    except ValueError:
        pass
    return [x for x in out if len(x.replace(',', '').replace('.', '')) >= 2]


rows = []
for s in srcs:
    sid, p = s['id'], paths.get(s['id'], '')
    if not p or not Path(p).is_file():
        rows.append([sid, '', '', '', '', '', 'copy not opened: no local file (API response)', s['url']])
        continue
    try:
        pg = pages(p)
    except Exception as e:
        rows.append([sid, '', '', '', '', '', f'copy not opened: {e}', Path(p).name])
        continue
    done = False
    for v, unit, yr, page, what in cand.get(sid, [])[:40]:
        for k, t in enumerate(pg):
            dig = re.sub(r'[^0-9]', '', str(v).split(';')[0])
            if any(x in t for x in variants(v)) or (len(dig) >= 5 and dig in re.sub(r'[ ,. ]', '', t)):
                rows.append([sid, v, unit, yr, page or '', f'p.{k + 1}' if len(pg) > 1 else 'file', 'confirmed', what])
                done = True
                break
        if done:
            break
    if not done:
        rows.append([sid, cand.get(sid, [('', '', '', '', '')])[0][0], '', '', '', '', 'opened; value not found by text search', Path(p).name])
with open(M.JOB / 'reopen_check.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['source_id', 'value_printed', 'unit', 'year', 'page_in_register', 'page_found', 'result', 'what'])
    w.writerows(rows)
from collections import Counter  # noqa: E402
print(Counter(r[6] for r in rows))
