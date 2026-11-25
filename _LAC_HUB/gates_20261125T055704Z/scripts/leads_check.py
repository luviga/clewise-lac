"""Step 1.3: every entry of report_cited_sources_leads.csv classified by whether it bears on a value this job writes
(vehicle prices, lives, distances, fleet, discount rate, externality factors, crop costs, capacity history,
emission factors). Relevant entries with a URL are downloaded (normal browser user agent, Windows curl) into
downloads/leads/ and the result recorded. Writes leads_checked.csv (index, title, url, topic, result, local copy,
sha256, note)."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import hashlib
import subprocess
from pathlib import Path

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
OUT = M.JOB / 'downloads' / 'leads'
OUT.mkdir(parents=True, exist_ok=True)
# index -> (topic, note on use); every other index is not relevant to a value this job writes
REL = {19: ('vehicle fleet', 'DGII vehicle fleet statistics page (Dominican Republic)'),
       33: ('emission factors', 'Dominican energy industries inventory update; national factors for power plants'),
       39: ('vehicle fleet', 'DGII vehicle fleet bulletin 2022'),
       44: ('crop costs', 'Dominican Ministry of Agriculture production costs 2021'),
       51: ('vehicle prices, lives, distances', 'World Bank Dominican CCDR Annex 4 transport deep dive'),
       69: ('capacity history', 'OC-SENI annual report 2023'),
       75: ('emission factors', 'Dominican inventory base year 2010'),
       88: ('capacity history', 'Dominican national energy plan 2022'),
       89: ('vehicle prices, lives, distances', 'Dominican national electric mobility plan (source GEN-104 of the register)'),
       91: ('vehicle distances', 'PMUS Gran Santo Domingo 2019'),
       99: ('capacity history', 'OC-SENI long-term operation programme 2024-2027'),
       101: ('vehicle distances, fleet age', 'RITEVE annual report 2018 (Costa Rica)'),
       114: ('capacity history', 'Ecuador national energy balance 2023'),
       124: ('capacity history', 'Honduras national energy balance 2024'),
       145: ('emission factors', 'Honduras national inventory report 2016-2020'),
       172: ('emission factors', 'IPCC 2006 Vol. 2 Ch. 2 (source ALN-IPCC2006-V2C2 of the register)'),
       178: ('emission factors', 'IPCC 2006 Vol. 2 Ch. 3 Spanish (mobile combustion)'),
       185: ('externality factors', 'IMF fossil fuel subsidies working paper 2019 (the 2023 template is used)'),
       190: ('vehicle fleet', 'INE Honduras vehicle fleet 2018-2022'),
       191: ('capacity history', 'Honduras generation expansion plan 2024-2033'),
       194: ('vehicle fleet', 'SEN Honduras electromobility outlook 2019-2050')}
USED = {89: 'used (GEN-104)', 172: 'used (ALN-IPCC2006-V2C2)'}
rows = []
leads = list(csv.DictReader(open(M.JOB / 'report_cited_sources_leads.csv', encoding='utf-8', errors='replace')))
for i, r in enumerate(leads):
    url = (r.get('url') or '').strip()
    if i not in REL:
        rows.append([i, r.get('title', ''), url, '', 'not relevant', '', '', 'bears on no value written by this job'])
        continue
    topic, note = REL[i]
    if not url.startswith('http'):
        rows.append([i, r.get('title', ''), url, topic, 'not reachable', '', '', note + '; no URL'])
        continue
    name = f'lead_{i:03d}_' + ''.join(ch if ch.isalnum() else '_' for ch in url.split('/')[-1])[:60]
    dst = OUT / name
    res = subprocess.run(['curl.exe', '-s', '-L', '--max-time', '60', '-A', UA, '-o', str(dst), '-w', '%{http_code}', url],
                         capture_output=True, text=True)
    code = res.stdout.strip()
    ok = dst.exists() and dst.stat().st_size > 2000 and code.startswith('2')
    h = hashlib.sha256(dst.read_bytes()).hexdigest() if ok else ''
    if not ok and dst.exists():
        dst.unlink()
    result = USED.get(i, 'downloaded; checked' if ok else f'not reachable (HTTP {code or "none"})')
    rows.append([i, r.get('title', ''), url, topic, result, name if ok else '', h, note])
    print(i, result, name if ok else '')
with open(M.JOB / 'leads_checked.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['index', 'title', 'url', 'topic', 'result', 'local_copy', 'sha256', 'note'])
    w.writerows(rows)
