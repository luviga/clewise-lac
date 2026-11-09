"""Checks for the JAM outputs. Usage: py -I check_jam.py <job_folder>"""
import csv, os, sys, re
J = sys.argv[1]; O = os.path.join(J, 'country', 'JAM'); DL = os.path.join(J, 'downloads')
rd = lambda n: list(csv.DictReader(open(os.path.join(O, n), encoding='utf-8')))
src = {s['id']: s for s in rd('sources_JAM.csv')}
bad = 0
for s in src.values():
    if not s['url'].startswith('http'): print('no url', s['id']); bad += 1
    for f in s['downloaded_file'].split(';'):
        if not os.path.exists(os.path.join(DL, f.strip())): print('missing file', s['id'], f); bad += 1
    if not s['page_or_table'] or not s['retrieval_date']: print('missing page/date', s['id']); bad += 1
n = 0
for name in ('prices_JAM.csv', 'history_JAM.csv', 'constants_JAM.csv', 'calorific_JAM.csv'):
    for r in rd(name):
        n += 1
        if r.get('evidence_class') == 'ASSUMPTION candidate': continue
        for sid in r['source_id'].split(';'):
            if sid.strip() not in src: print('bad source id', name, sid); bad += 1
        if 'downloaded_file' in r:
            for f in r['downloaded_file'].split(';'):
                if not os.path.exists(os.path.join(DL, f.strip())): print('missing file', name, f); bad += 1
log = rd('search_log_JAM.csv')
leads = ['petrojam', 'our_jps', 'mset_pcj', 'statin_boj', 'gazette', 'customs_national', 'comtrade', 'energy_balance']
for r in rd('prices_JAM.csv'):
    if r['evidence_class'] == 'ASSUMPTION candidate':
        miss = [l for l in leads if not any(x['fuel'] == r['fuel'] and x['lead_id'] == l for x in log)]
        print('ASSUMPTION', r['fuel'], 'missing leads:', miss); bad += len(miss)
for fn in os.listdir(O):
    t = open(os.path.join(O, fn), encoding='utf-8').read()
    if '\u2014' in t: print('em dash in', fn); bad += 1
    if fn.endswith(('.csv', '.md')) and re.search(r'(?<![A-Za-z])[A-Za-z]:\\|/c/Users|clw_local_prices|AppData', t): print('machine path in', fn); bad += 1
print('rows checked', n, 'sources', len(src), 'problems', bad)
