"""Sourcing check for the DR outputs (steer gate 4).
Usage: py -I dr_check_sources.py <country_DR_dir> <downloads_dir>
Checks: every row of prices, history, calorific and constants that is not an ASSUMPTION candidate names source ids
that exist in sources_DR.csv; every source has an http(s) url, page_or_table, retrieval_date and an existing file;
no field in any DR csv holds a machine path or an em dash."""
import sys, os, csv, re, glob

C, DL = sys.argv[1], sys.argv[2]
src = {r['id']: r for r in csv.DictReader(open(os.path.join(C, 'sources_DR.csv'), encoding='utf-8'))}
fail = []
counts = {}
for fn, col in (('prices_DR.csv', 'source_id'), ('history_DR.csv', 'source_id'), ('calorific_DR.csv', 'source_id'), ('constants_DR.csv', 'source_id')):
    n = 0
    for i, r in enumerate(csv.DictReader(open(os.path.join(C, fn), encoding='utf-8'))):
        n += 1
        if r.get('evidence_class', '') == 'ASSUMPTION candidate':
            continue
        ids = [x for x in r[col].split(';') if x]
        if not ids:
            fail.append('%s row %d: no source id' % (fn, i + 2))
        for x in ids:
            if x not in src:
                fail.append('%s row %d: unknown source id %s' % (fn, i + 2, x))
    counts[fn] = n
for sid, r in src.items():
    if not re.match(r'https?://', r['url']):
        fail.append('%s: url not http(s)' % sid)
    for k in ('page_or_table', 'retrieval_date', 'downloaded_file'):
        if not r[k].strip():
            fail.append('%s: empty %s' % (sid, k))
    for f in r['downloaded_file'].split(';'):
        if not os.path.exists(os.path.join(DL, f.strip().replace('/', os.sep))):
            fail.append('%s: file missing %s' % (sid, f))
bad = re.compile(r'((?<![A-Za-z])[A-Za-z]:[\\/]|/c/Users|\\Users\\|clw_local_prices|MODELS_LAC)')
for fn in glob.glob(os.path.join(C, '*.csv')) + glob.glob(os.path.join(C, '*.md')):
    t = open(fn, encoding='utf-8').read()
    if '\u2014' in t:
        fail.append('%s: em dash' % os.path.basename(fn))
    for m in bad.finditer(t):
        fail.append('%s: machine path near "%s"' % (os.path.basename(fn), t[max(0, m.start() - 20):m.end() + 20]))
        break
print('rows checked:', counts, 'sources:', len(src))
print('failures:', len(fail))
for f in fail[:50]:
    print(' ', f)
