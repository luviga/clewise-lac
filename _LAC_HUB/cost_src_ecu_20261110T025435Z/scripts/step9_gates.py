"""Step 9: gates. Usage: py -I step9_gates.py <repo_root> <job_rel_path> [post_commit]
Writes <job>/gate_results.txt and <job>/baseline_after.csv. Uses git for gates 2, 3 and 7 (post_commit only for 2 and the log check).
"""
import sys, os, re, hashlib, subprocess
import pandas as pd

repo, jrel = sys.argv[1], sys.argv[2]
post = len(sys.argv) > 3
job = os.path.join(repo, jrel)
out = []


def say(s):
    out.append(s)
    print(s)


def git(*a):
    return subprocess.run(['git', '-C', repo] + list(a), capture_output=True, text=True).stdout

# Gate 1
b = pd.read_csv(os.path.join(job, 'baseline_before.csv'))
rows = []
for f in b.file:
    h = hashlib.sha256(open(os.path.join(repo, f), 'rb').read()).hexdigest()
    rows.append((f, h))
a = pd.DataFrame(rows, columns=['file', 'sha256'])
a.to_csv(os.path.join(job, 'baseline_after.csv'), index=False)
eq = (a.sha256.values == b.sha256.values).all()
say(f'Gate 1 read-only: {len(a)} files hashed; equal to baseline_before: {"PASS" if eq else "FAIL"}')

# Gate 2
if post:
    names = [n for n in git('diff', '--name-only', '2ddd560', 'HEAD').splitlines() if n]
    bad = [n for n in names if not n.startswith(jrel.replace(os.sep, '/') + '/')]
    say(f'Gate 2 diff scope: {len(names)} files changed since 2ddd560; outside job folder: {len(bad)}: {"PASS" if not bad else "FAIL " + str(bad[:5])}')
else:
    say('Gate 2 diff scope: run after commit')

# Gate 3
tracked = [n for n in git('ls-files', jrel.replace(os.sep, '/')).splitlines() if n]
badext = [n for n in tracked if not n.lower().endswith(('.md', '.csv', '.py', '.txt'))]
dl = [n for n in tracked if '/downloads/' in n]
say(f'Gate 3 tracked types: {len(tracked)} tracked files; other extensions {len(badext)}; under downloads/ {len(dl)}: {"PASS" if not badext and not dl else "FAIL"}')

# Gate 4
prop = pd.read_csv(os.path.join(job, 'proposals.csv'))
src = pd.read_csv(os.path.join(job, 'sources.csv'))
ids = set(src.id)
na = prop[prop.basis_class != 'ASSUMPTION']
miss = set()
for s in prop.source_ids.astype(str):
    for x in s.split(';'):
        if x.strip() and x.strip() not in ids:
            miss.add(x.strip())
nosrc = (prop.source_ids.isna() | (prop.source_ids.astype(str).str.strip() == '')).sum()
say(f'Gate 4a proposals rows: {len(prop)} ({len(na)} non-ASSUMPTION); source ids not in sources.csv: {sorted(miss)}; rows without source ids: {nosrc}: {"PASS" if not miss and nosrc == 0 else "FAIL"}')
PATH = re.compile(r'(\b[A-Za-z]:\\|(?<![A-Za-z])/c/(Users|clw)|clw_|_LAC_HUB|handover|BRIEF_)')
probs = []
for r in src.itertuples():
    if not re.match(r'https?://', str(r.url)):
        probs.append((r.id, 'url'))
    if not str(r.page_or_table).strip() or str(r.page_or_table) == 'nan':
        probs.append((r.id, 'locator'))
    if not re.match(r'\d{4}-\d{2}-\d{2}$', str(r.retrieval_date)):
        probs.append((r.id, 'retrieval_date'))
    files = [f.strip() for f in str(r.downloaded_file).split(';') if f.strip()]
    if not files or not all(os.path.exists(os.path.join(job, 'downloads', f)) for f in files):
        probs.append((r.id, 'file ' + str(r.downloaded_file)))
    for col in ('url', 'title', 'publisher', 'date', 'retrieval_date', 'downloaded_file', 'page_or_table', 'rows_and_constants_supported'):
        v = str(getattr(r, col))
        if col != 'downloaded_file' and PATH.search(v):
            probs.append((r.id, 'internal or local path in ' + col))
say(f'Gate 4b sources: {len(src)} records; problems: {len(probs)} {probs[:10]}: {"PASS" if not probs else "FAIL"}')

# Gate 5
log = pd.read_csv(os.path.join(job, 'search_log.csv'))
asr = prop[prop.basis_class == 'ASSUMPTION']
FORBID = re.compile(r'\b(job|jobs|file|files|csv|workbook|spreadsheet|search|searched|not found|could not|unable|brief|ruling|Luis|handover|LAC_|earlier|previous run|we )\b', re.I)
techs = sorted(set(asr.Tech))
noleads = [t for t in techs if not log.row.astype(str).str.contains(t.replace('*', ''), regex=False).any()
           and not log.row.astype(str).str.contains('DIST_*', regex=False).any() if t.startswith('DIST')] + \
          [t for t in techs if not t.startswith('DIST') and not log.row.astype(str).str.contains(t, regex=False).any()]
sents = asr.assumption_sentence.dropna().unique()
badw = [(s[:60], FORBID.findall(s)) for s in sents if FORBID.search(s)]
notass = [s[:40] for s in sents if not s.startswith('ASSUMPTION:')]
noparts = [s[:60] for s in sents if not all(k in s for k in ('Reason:', 'Range:'))]
say(f'Gate 5 ASSUMPTION: {len(asr)} rows, {len(techs)} technologies ({", ".join(techs)}); without logged leads: {noleads}; sentences {len(sents)}, with forbidden words {len(badw)} {badw[:3]}, missing Reason/Range {len(noparts)}: {"PASS" if not noleads and not badw and not noparts and not notass else "FAIL"}')

# Gate 6
PLANTS = ['PPBGS', 'PPBIM', 'PPCRU', 'PPDDSL', 'PPDFOI', 'PPDSL', 'PPFOI', 'PPHD', 'PPHDAMAB', 'PPHDAMAM', 'PPHDAMAS', 'PPHDAMPM',
          'PPHDAMPS', 'PPHRORAB', 'PPHRORAM', 'PPHRORAS', 'PPHRORPM', 'PPHRORPS', 'PPIBIM', 'PPIHD', 'PPILPG', 'PPNGS', 'PPPVD',
          'PPPVT', 'PPPVTS', 'PPRDSL', 'PPRNGS', 'PPWNDD', 'PPWNDON']
SUPPLY = ['DIST_COA', 'DIST_COK', 'DIST_CRU', 'DIST_DSL', 'DIST_FOI', 'DIST_GSL', 'DIST_JET', 'DIST_KER', 'DIST_LPG', 'DIST_NGS',
          'DIST_OPE', 'EXTT_CRU', 'EXTT_NGS']
YEARS = set(range(2021, 2051))
gaps = []
for t in PLANTS + ['IMPELE']:
    for p in ('CapitalCost', 'FixedCost', 'VariableCost'):
        g = prop[(prop.Tech == t) & (prop.Parameter == p) & (prop.fuel_scenario == 'ALL')]
        if set(g.year) != YEARS:
            gaps.append((t, p))
for t in SUPPLY:
    for s in ('STEPS', 'CPS', 'NZE'):
        g = prop[(prop.Tech == t) & (prop.Parameter == 'VariableCost') & (prop.fuel_scenario == s)]
        if set(g.year) != YEARS:
            gaps.append((t, s))
    for p in ('CapitalCost', 'FixedCost'):
        g = prop[(prop.Tech == t) & (prop.Parameter == p)]
        if set(g.year) != YEARS:
            gaps.append((t, p))
dup = prop.duplicated(['Tech', 'Parameter', 'fuel_scenario', 'year']).sum()
say(f'Gate 6 coverage: {len(PLANTS)} plants x 3 parameters, {len(SUPPLY)} supply rows x 3 scenarios, IMPELE; 30 year columns 2021-2050; gaps {gaps}; duplicate cells {dup}: {"PASS" if not gaps and dup == 0 else "FAIL"}')

# Gate 7
chk = subprocess.run(['git', '-C', repo, 'diff', '--check', '2ddd560' if post else 'HEAD'], capture_output=True, text=True)
EM = '\u2014'
MPATH = re.compile(r'([A-Za-z]:\\|/c/Users|/c/clw|C:/)')
hits = []
for root, dirs, files in os.walk(job):
    if 'downloads' in root.split(os.sep):
        continue
    for f in files:
        if f.startswith('BRIEF_'):
            continue
        p = os.path.join(root, f)
        try:
            txt = open(p, encoding='utf-8').read()
        except Exception:
            continue
        if EM in txt:
            hits.append((f, 'em dash'))
        for line in txt.splitlines():
            if f.endswith('.py') and line.lstrip().startswith(('#', 'Usage', '"""')):
                continue
            m = MPATH.search(line)
            if m and 'MPATH' not in line and not re.search(r'https?://\S*' + re.escape(m.group(0)), line):
                hits.append((f, 'path: ' + line[:80]))
                break
logtxt = git('log', '-3', '--format=%B') if post else ''
trail = ('Co-Authored-By' in logtxt) or ('Generated with' in logtxt)
say(f'Gate 7 hygiene: git diff --check output {len(chk.stdout.strip())} chars; em dash or machine path hits {len(hits)} {hits[:5]}; trailer lines in last 3 commits: {trail if post else "run after commit"}: {"PASS" if not chk.stdout.strip() and not hits and not trail else "FAIL"}')

open(os.path.join(job, 'gate_results.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
