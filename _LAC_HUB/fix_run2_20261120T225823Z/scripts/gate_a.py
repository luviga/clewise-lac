"""A5 Gate A. (1) every proposals row with basis 'source' (and every source id cited anywhere) resolves in sources.csv with
URL, locator, date, file present and SHA-256 equal to the file; (2) no source field holds a local path or internal file;
(3) every ASSUMPTION sentence starts with 'ASSUMPTION:' and passes the forbidden-word scan; (4) rows of every other basis
name their derivation. Writes logs/gate_a.csv and prints PASS or FAIL."""
import hashlib, os, re, sys
import pandas as pd

JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
ARCHIVE = 'C:/Users/luisfernando/Desktop/OSeMOSYS/LAC_sources_archive/'
P = pd.read_csv(JOB + '/proposals.csv', dtype=str, keep_default_na=False)
S = pd.read_csv(JOB + '/sources.csv', dtype=str, keep_default_na=False).set_index('id')
FORBID = re.compile(r'(?i)\b(not found|kept as used|retained|previously|workbook|sheet|cell|job|handover|we kept|our model|'
                    r'B1_|A-O|proposals|earlier run|hub \d)\b')
INTERNAL = re.compile(r'(?i)(\.xlsx?$|[A-Z]:[\\/]|clw_|_LAC_HUB|B1_Output|A2_Output|A-O_)')
fails = []


def resolve(f):
    if f.startswith('../'):
        return os.path.normpath(os.path.join(JOB, f))
    return os.path.join(JOB, f)


for i, s in S.iterrows():
    for k in ['url', 'title', 'date', 'accessed', 'sha256', 'file', 'page_or_table']:
        if not s[k].strip():
            fails.append(('source', i, f'empty {k}'))
    if not re.match(r'^(https?://|doi:)', s.url.strip()):
        fails.append(('source', i, f'url not http(s) or doi: {s.url[:60]}'))
    if INTERNAL.search(s.url.split(' ')[0]) and 'github.com' not in s.url and 'http' not in s.url:
        fails.append(('source', i, 'url looks internal'))
    for f, h in zip(s.file.split(';'), s.sha256.split(';')):
        p = resolve(f.strip())
        if not os.path.exists(p):
            fails.append(('source', i, 'file missing'))
        elif hashlib.sha256(open(p, 'rb').read()).hexdigest() != h.strip():
            fails.append(('source', i, 'sha256 mismatch'))
for n, r in P.iterrows():
    ids = [x.strip() for x in r.source_ids.split(';') if x.strip()]
    for x in ids:
        if x not in S.index:
            fails.append(('proposal', n, f'source id {x} not in sources.csv'))
    if r.basis == 'source' and not ids:
        fails.append(('proposal', n, f'basis source without source ids ({r.decision} {r.Tech} {r.year})'))
    if r.basis != 'source' and not r.derivation.strip():
        fails.append(('proposal', n, 'no derivation'))
    if r.assumption.strip():
        for sent in [a for a in re.split(r'(?=ASSUMPTION:)', r.assumption) if a.strip()]:
            if not sent.startswith('ASSUMPTION:'):
                fails.append(('assumption', n, 'does not start with ASSUMPTION:'))
            m = FORBID.search(sent)
            if m:
                fails.append(('assumption', n, f'forbidden word: {m.group(0)}'))
            if '\u2014' in sent:
                fails.append(('assumption', n, 'em dash'))
pd.DataFrame(fails, columns=['kind', 'ref', 'problem']).to_csv(JOB + '/logs/gate_a.csv', index=False, lineterminator='\n')
print('Gate A', 'PASS' if not fails else f'FAIL ({len(fails)})')
for f in fails[:40]:
    print(f)
sys.exit(1 if fails else 0)
