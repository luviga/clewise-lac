"""Step 9: gates. Usage: py -I step9_gates.py <repo root> <job folder relative to repo> [post-commit]"""
import csv, hashlib, os, re, subprocess, sys
import pandas as pd

ROOT, JREL = sys.argv[1], sys.argv[2]
POST = len(sys.argv) > 3
JOB = os.path.join(ROOT, JREL)
out = []


def g(name, ok, detail):
    out.append('%s: %s. %s' % (name, 'PASS' if ok else 'FAIL', detail))


# 1 read-only
b = pd.read_csv(os.path.join(JOB, 'baseline_before.csv'))
rows = []
for f in b.file:
    rows.append(dict(file=f, sha256=hashlib.sha256(open(os.path.join(ROOT, f), 'rb').read()).hexdigest()))
a = pd.DataFrame(rows)
a.to_csv(os.path.join(JOB, 'baseline_after.csv'), index=False, lineterminator=chr(10))
g('Gate 1 read-only', list(a.sha256) == list(b.sha256), '%d files hashed, %d equal' % (len(a), int((a.sha256.values == b.sha256.values).sum())))

# 2, 3 git (post-commit)
if POST:
    names = subprocess.run(['git', '-C', ROOT, 'diff', '--name-only', '2ddd560', 'HEAD'], capture_output=True, text=True).stdout.split()
    outside = [n for n in names if not n.startswith(JREL.replace('\\', '/') + '/')]
    g('Gate 2 diff scope', not outside, '%d files changed, %d outside the job folder %s' % (len(names), len(outside), outside[:5]))
    tracked = subprocess.run(['git', '-C', ROOT, 'ls-files', JREL], capture_output=True, text=True).stdout.split()
    bad_ext = [t for t in tracked if os.path.splitext(t)[1] not in ('.md', '.csv', '.py', '.txt')]
    in_dl = [t for t in tracked if '/downloads/' in t]
    g('Gate 3 tracked types', not bad_ext and not in_dl, '%d tracked files; %d with other extensions; %d under downloads/' % (len(tracked), len(bad_ext), len(in_dl)))

# 4 sourcing
prop = pd.read_csv(os.path.join(JOB, 'proposals.csv'))
src = pd.read_csv(os.path.join(JOB, 'sources.csv'))
ids = set(src.id)
na = prop[prop.basis_class != 'ASSUMPTION']
miss = 0
for v in na.source_ids:
    if pd.isna(v) or any(x.strip() not in ids for x in str(v).split(';') if x.strip()):
        miss += 1
bad = []
pathpat = re.compile(r'([A-Za-z]:\\|/c/|\\Users\\|/Users/|\.xlsx|\.csv|_LAC_HUB|OneDrive)', re.I)
for _, s in src.iterrows():
    probs = []
    if not str(s.url).startswith(('http://', 'https://')):
        probs.append('url')
    if pd.isna(s.page_or_table) or not str(s.page_or_table).strip():
        probs.append('locator')
    if pd.isna(s.retrieval_date):
        probs.append('date')
    if pd.isna(s.downloaded_file) or not os.path.exists(os.path.join(JOB, 'downloads', str(s.downloaded_file))):
        probs.append('file')
    for col in ('url', 'title', 'publisher', 'page_or_table'):
        val = str(s[col])
        if col == 'url':
            continue
        if pathpat.search(val) and 'xlsx' not in col:
            # spreadsheet names inside a page locator are allowed when they are the published file (url ends with it)
            if not (str(s.url).lower().endswith(('.xlsx', '.xls', '.csv')) or 'sheet' in val.lower()):
                probs.append('path in ' + col)
    if probs:
        bad.append('%s:%s' % (s.id, ','.join(probs)))
g('Gate 4 sourcing', miss == 0 and not bad, '%d proposal rows not ASSUMPTION, %d with a missing source id; %d sources, %d with problems %s' % (len(na), miss, len(src), len(bad), bad[:8]))

# 5 assumptions
sl = pd.read_csv(os.path.join(JOB, 'search_log.csv'))
asm = prop[prop.basis_class == 'ASSUMPTION']
forb = re.compile(r'\b(job|jobs|file|files|csv|workbook|sheet|search|searched|not found|could not|LAC_|brief|ruling|Luis|handover|our|we)\b', re.I)
techs = sorted(set(asm.Tech))
noleads = [t for t in techs if not (sl.row.astype(str).str.contains(t, regex=False)).any()]
badsent = sorted(set(t for t, s in zip(asm.Tech, asm.assumption_sentence) if pd.isna(s) or not str(s).startswith('ASSUMPTION') or forb.search(str(s))))
g('Gate 5 ASSUMPTION rows', not noleads and not badsent, '%d ASSUMPTION rows for %s; without leads %s; sentence problems %s' % (len(asm), techs, noleads, badsent))

# 6 coverage
plants = ['PP_SPV_DG', 'PWRBMS', 'PWRDSL', 'PWRFOI', 'PWRGEO', 'PWRHYDDAM', 'PWRHYDROR', 'PWRSPVDTR', 'PWRSPVTRN', 'PWRWNONS']
supply = ['IMPAVG', 'IMPCOA', 'IMPCOK', 'IMPFOI', 'IMPKJF', 'IMPLPG', 'IMPNGS', 'IMPPURDSL', 'IMPPURGSL']
gaps = []
for t in plants:
    for p in ('CapitalCost', 'FixedCost', 'VariableCost'):
        ys = set(prop[(prop.Tech == t) & (prop.Parameter == p)].year)
        if ys != set(range(2021, 2051)):
            gaps.append('%s %s %d years' % (t, p, len(ys)))
for t in supply:
    for s in ('STEPS', 'CPS', 'NZE'):
        ys = set(prop[(prop.Tech == t) & (prop.Parameter == 'VariableCost') & (prop.fuel_scenario == s)].year)
        if ys != set(range(2021, 2051)):
            gaps.append('%s %s %d years' % (t, s, len(ys)))
ys = set(prop[(prop.Tech == 'IMPELE') & (prop.Parameter == 'VariableCost')].year)
if ys != set(range(2021, 2051)):
    gaps.append('IMPELE %d years' % len(ys))
g('Gate 6 coverage', not gaps, '%d plants x 3 parameters x 30 years and %d supply rows x 3 scenarios x 30 years and IMPELE x 30 years checked; gaps %s' % (len(plants), len(supply), gaps[:6]))

# 7 hygiene
emd, paths = [], []
pp = re.compile(r'([A-Za-z]:\\\\?[A-Za-z]|/c/[A-Za-z]|\\Users\\|/Users/)')
for dp, dn, fn in os.walk(JOB):
    if 'downloads' in dp.split(os.sep):
        continue
    for f in fn:
        if os.path.splitext(f)[1] not in ('.md', '.csv', '.py', '.txt'):
            continue
        p = os.path.join(dp, f)
        t = open(p, encoding='utf-8', errors='replace').read()
        if chr(0x2014) in t:
            emd.append(f)
        if f.startswith('BRIEF_'):
            continue
        for m in pp.finditer(t):
            line = t[t.rfind('\n', 0, m.start()) + 1: t.find('\n', m.end())]
            if 'http' not in line and 're.compile' not in line:
                paths.append('%s: %s' % (f, line[:80]))
                break
dc = subprocess.run(['git', '-C', ROOT, 'diff', '--check', '2ddd560'] + (['HEAD'] if POST else []), capture_output=True, text=True).stdout
logb = subprocess.run(['git', '-C', ROOT, 'log', '-3', '--format=%B'], capture_output=True, text=True).stdout if POST else ''
trailer = ('Co-Authored-By' in logb) or ('Generated with' in logb)
g('Gate 7 hygiene', not emd and not paths and not dc.strip() and not trailer,
  'em dash files %s; machine paths %s; git diff --check output %d chars; trailer lines %s' % (emd, paths[:5], len(dc), trailer))
txt = '\n'.join(out)
open(os.path.join(JOB, 'gate_results%s.txt' % ('_post' if POST else '_pre')), 'w', encoding='utf-8', newline=chr(10)).write(txt + '\n')
print(txt)
