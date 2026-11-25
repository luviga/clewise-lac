"""Step 1.1: sources.csv of the job (id, title, publisher, year, URL, retrieval date, local copy, SHA-256, what it
supports) for every source this job cites: the published-value documents (NDC jobs), the cost sources (cost
sources job and GEN packages), the vehicle price sources, and the documents downloaded in this job.
Local copies are looked up in the read-only archives and download folders; the SHA-256 is computed from the file.
Writes sources.csv in the job folder and work/source_cites.csv (source id, register, rows citing it)."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import glob
import hashlib
import re
from collections import defaultdict
from pathlib import Path

HUB = M.ROOT / '_LAC_HUB'
ARCH = M.ARCHIVE
SCOUT = M.SCOUT
FIELDS = ['id', 'title', 'publisher', 'year', 'url', 'retrieval_date', 'local_copy', 'sha256', 'supports', 'register']


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def year_of(s):
    m = re.search(r'(19|20)\d\d', str(s))
    return m.group(0) if m else ''


recs = {}
# 1. published values (NDC verify register)
for r in csv.DictReader(open(HUB / 'ndc_verify_20261121T233937Z' / 'sources.csv', encoding='utf-8')):
    f = r.get('file', '')
    cands = [HUB / 'ndc_verify_20261121T233937Z' / f, SCOUT / 'ndc_verify_20261121T233937Z' / f,
             SCOUT / 'ndc_scout_20261121T204620Z' / f.replace('../ndc_scout_20261121T204620Z/', '')]
    recs[r['id']] = dict(id=r['id'], title=r['title'], publisher=r['publisher'], year=year_of(r['date']), url=r['URL'],
                         retrieval_date=r['accessed'], local=[c for c in cands], sha_reg=r.get('SHA-256', ''),
                         register='NDC verify (#13)')
# 2. cost sources job and 3. vehicle prices job
for job, arch in [('cost_sources_20261122T234333Z', 'cost_sources_20261122T234333Z'),
                  ('vehicle_prices_20261123T163210Z', 'vehicle_prices_20261123T163210Z')]:
    for p in glob.glob(str(HUB / job / '**' / 'sources*.csv'), recursive=True):
        for r in csv.DictReader(open(p, encoding='utf-8')):
            if not r.get('id') or r['id'] in recs:
                continue
            f = r.get('downloaded_file', '') or ''
            rel = re.sub(r'^downloads/', '', f)
            cands = [ARCH / arch / rel, ARCH / arch / Path(p).parent.name / Path(rel).name, HUB / job / f]
            recs[r['id']] = dict(id=r['id'], title=r['title'], publisher=r['publisher'], year=year_of(r['date']),
                                 url=r['url'], retrieval_date=r['retrieval_date'], local=cands, sha_reg='',
                                 register=job.split('_2026')[0])
# 4. documents downloaded in this job (research_R1.csv) and the inventory used for the GWP
D = M.JOB / 'downloads' / 'R1'
NEW = [('ALN-UNA-2024', 'A_discount/CRI_UNA_thesis.pdf'), ('ALN-CEPAL-ECU-2021', 'A_discount/ECU_CEPAL_tasa_social_descuento.pdf'),
       ('ALN-JAM-PIMS-2016', 'A_discount/JAM_PIMS_Guidelines_2016.pdf'),
       ('ALN-IMF-2023', 'B_imf/extract_externalfuelsubsidiestemplate2023new_data_sheet.csv'),
       ('ALN-IPCC2006-V2C2', 'C_ipcc/V2_2_Ch2_Stationary_Combustion.pdf'),
       ('ALN-EOR-MEX-2021', 'D_interconnect/CND_083_Anexo_I.pdf'),
       ('ALN-EOR-MCTP-2025', 'D_interconnect/EOR_MCTP_Noviembre_2025_Anexo_I.pdf'),
       ('ALN-CNEE-2024', 'D_interconnect/GTM_CNEE_Compendio_Estadistico_2024.pdf')]
r1 = list(csv.DictReader(open(M.JOB / 'work' / 'research_R1.csv', encoding='utf-8')))
for sid, lf in NEW:
    row = next((r for r in r1 if r['local_file'].replace('\\', '/').startswith(lf)), None)
    if row is None:
        continue
    recs[sid] = dict(id=sid, title=row['source_title'], publisher=row['publisher'], year=year_of(row['year']),
                     url=row['url'], retrieval_date=row['retrieval_date'], local=[D / lf],
                     sha_reg=row['sha256'] if sid == 'ALN-IMF-2023' else '', register='this job')
recs['JAM-GLEANER-2022-10-01'] = dict(
    id='JAM-GLEANER-2022-10-01', title='Pan Caribbean shelves bio-energy project', publisher='The Gleaner (Jamaica)',
    year='2022', url='https://past.jamaica-gleaner.com/article/news/20221001/pan-caribbean-shelves-bio-energy-project',
    retrieval_date='2026-11-24', local=[M.JOB / 'downloads' / 'JAM' / 'Gleaner_20221001_pan_caribbean_shelves_bio_energy.html'],
    sha_reg='', register='this job')
# citations
cites = defaultdict(set)
regs = {p.name: p for p in (M.JOB / 'work').glob('register_*.csv')}
regs['value_register_vehicles.csv'] = M.JOB / 'work' / 'value_register_vehicles.csv'
for name, p in regs.items():
    if name.endswith('_write_log.csv') or not p.exists():
        continue
    for r in csv.DictReader(open(p, encoding='utf-8')):
        for s in re.split(r'[|;, ]+', r.get('source_id', '') or ''):
            if s:
                cites[s].add(name.replace('.csv', ''))
for r in csv.DictReader(open(M.ROOT / 'inputs' / 'scenarios' / 'scenario_values.csv', encoding='utf-8')):
    if r['source_id']:
        cites[r['source_id']].add('scenario_values')
out, missing = [], []
for sid in sorted(cites):
    rec = recs.get(sid)
    if rec is None:
        missing.append(sid)
        continue
    lc = next((c for c in rec['local'] if Path(c).is_file()), None)
    h = sha(lc) if lc else rec['sha_reg']
    out.append(dict(id=sid, title=rec['title'], publisher=rec['publisher'], year=rec['year'], url=rec['url'],
                    retrieval_date=rec['retrieval_date'],
                    local_copy=(Path(lc).name if lc else ''), sha256=h,
                    supports='; '.join(sorted(cites[sid])), register=rec['register']))
with open(M.JOB / 'sources.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
    w.writeheader()
    w.writerows(out)
with open(M.JOB / 'work' / 'source_paths.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['id', 'local_path'])
    for sid in sorted(cites):
        rec = recs.get(sid)
        if rec:
            lc = next((c for c in rec['local'] if Path(c).is_file()), '')
            w.writerow([sid, str(lc)])
print(len(out), 'sources;', sum(1 for o in out if not o['local_copy']), 'without local copy; not in any register:', missing)
