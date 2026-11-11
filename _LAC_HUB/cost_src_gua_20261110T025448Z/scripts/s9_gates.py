"""Step 9 gates 4 to 7 (file-level checks). Gates 1 to 3 and the git parts of 7 are run
from the shell and their output appended to work/gates_output.txt.
Usage: py -I s9_gates.py <job folder>"""
import csv, os, re, sys
import pandas as pd

J = sys.argv[1]
DL = os.path.join(J, 'downloads')
out = []
def say(s):
    out.append(s); print(s)

src = pd.read_csv(os.path.join(J, 'sources.csv'), dtype=str).fillna('')
prop = pd.read_csv(os.path.join(J, 'proposals.csv'), dtype=str).fillna('')
log = pd.read_csv(os.path.join(J, 'search_log.csv'), dtype=str).fillna('')
ids = set(src.source_id)

# Gate 4: sourcing
bad_ids = []
for _, r in prop[prop.basis_class != 'ASSUMPTION'].iterrows():
    sids = [s for s in r.source_ids.split(';') if s]
    if not sids or any(s not in ids for s in sids):
        bad_ids.append((r.Tech, r.Parameter, r.year, r.source_ids))
say(f'Gate 4a: proposals rows not ASSUMPTION = {(prop.basis_class != "ASSUMPTION").sum()}; rows with missing or unknown source ids = {len(bad_ids)}')
for b in bad_ids[:10]:
    say(f'   {b}')
# ASSUMPTION rows that cite sources: check those ids exist too
bad_a = [r.source_ids for _, r in prop[prop.basis_class == 'ASSUMPTION'].iterrows()
         if any(s not in ids for s in r.source_ids.split(';') if s)]
say(f'Gate 4b: ASSUMPTION rows citing unknown source ids = {len(bad_a)}')
internal = re.compile(r'([A-Za-z]:\\|[A-Za-z]:/|/c/|\.xlsx!|A-O_Parametrization|_LAC_HUB|OneDrive|Dropbox|handover|CLEWISE_)', re.I)
probs = []
for _, s in src.iterrows():
    if not re.match(r'^https?://', s.url):
        probs.append((s.source_id, 'url not http(s)'))
    if not s.locator.strip():
        probs.append((s.source_id, 'no locator'))
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', s.retrieval_date.strip()):
        probs.append((s.source_id, 'no retrieval date'))
    files = [f.strip() for f in s.downloaded_file.split(';') if f.strip()]
    if not files:
        probs.append((s.source_id, 'no downloaded file'))
    for f in files:
        if not os.path.isfile(os.path.join(DL, f)):
            probs.append((s.source_id, f'file missing: {f}'))
    for col in ['url', 'title', 'publisher', 'locator', 'downloaded_file', 'notes']:
        v = s[col]
        if col == 'url':
            continue
        v2 = re.sub(r'https?://\S+', '', v)
        if internal.search(v2):
            probs.append((s.source_id, f'internal reference in {col}: {internal.search(v2).group(0)}'))
say(f'Gate 4c: sources = {len(src)}; with problems = {len(set(p[0] for p in probs))}')
for p in probs[:20]:
    say(f'   {p}')

# Gate 5: ASSUMPTION rows have leads and clean sentences
banned = re.compile(r'\b(job|jobs|file|files|search|searched|searches|not found|could not|couldn.t|unable|handover|workbook|LAC_|ruling|Luis|we |our |history of|sheet)\b', re.I)
arows = prop[prop.basis_class == 'ASSUMPTION']
techs = sorted(set(arows.Tech))
noleads = [t for t in techs if (log.row == t).sum() == 0]
sentences = sorted(set(arows.assumption_sentence))
badsent = [s[:80] for s in sentences if (not s.startswith('ASSUMPTION:')) or banned.search(s)]
say(f'Gate 5: ASSUMPTION rows = {len(arows)} over {len(techs)} technologies {techs}; technologies without search_log leads = {noleads}; distinct sentences = {len(sentences)}; failing sentences = {len(badsent)}')
for b in badsent:
    say(f'   failing: {b} ... match {banned.search(b) and banned.search(b).group(0)}')

# Gate 6: coverage
PLANTS = ['PPBGS', 'PPBIM', 'PPCOA', 'PPDSL', 'PPFOI', 'PPGEO', 'PPHDAM', 'PPHROR', 'PPNGS', 'PPPVD', 'PPPVDS', 'PPPVT', 'PPPVT2', 'PPPVTS', 'PPWNDON']
SUPPLY = ['DIST_COA', 'DIST_COK', 'DIST_DSL', 'DIST_FOI', 'DIST_GSL', 'DIST_KER', 'DIST_LPG', 'DIST_NGS', 'EXTT_CRU']
YEARS = [str(y) for y in range(2018, 2051)]
miss = []
for t in PLANTS:
    for p in ['CapitalCost', 'FixedCost', 'VariableCost']:
        yrs = set(prop[(prop.Tech == t) & (prop.Parameter == p)].year)
        if set(YEARS) - yrs:
            miss.append((t, p, len(set(YEARS) - yrs)))
for t in SUPPLY:
    for s in ['STEPS', 'CPS', 'NZE']:
        yrs = set(prop[(prop.Tech == t) & (prop.Parameter == 'VariableCost') & (prop.fuel_scenario == s)].year)
        if set(YEARS) - yrs:
            miss.append((t, s, len(set(YEARS) - yrs)))
yrs = set(prop[(prop.Tech == 'IMP_ELE') & (prop.Parameter == 'VariableCost')].year)
if set(YEARS) - yrs:
    miss.append(('IMP_ELE', 'VariableCost', len(set(YEARS) - yrs)))
dups = prop.duplicated(subset=['Tech', 'Parameter', 'fuel_scenario', 'year']).sum()
say(f'Gate 6: proposals rows = {len(prop)}; plants {len(PLANTS)} x 3 parameters, supply rows {len(SUPPLY)} x 3 scenarios, IMP_ELE; gaps = {miss}; duplicate cells = {dups}')

# Gate 7 (file part): em dash and machine paths in output files
emd, paths = [], []
pathre = re.compile(r'([A-Za-z]:\\|[A-Za-z]:/(?!/)|/c/[A-Za-z]|[\\]Users[\\]|[/]Users[/])')
for root, dirs, files in os.walk(J):
    if 'downloads' in root.split(os.sep):
        continue
    for f in files:
        if not f.endswith(('.md', '.csv', '.py', '.txt')):
            continue
        fp = os.path.join(root, f)
        txt = open(fp, encoding='utf-8', errors='replace').read()
        if chr(0x2014) in txt:
            emd.append(os.path.relpath(fp, J))
        if f.startswith('BRIEF_') or f == 'gates_output.txt':
            continue
        for line in txt.splitlines():
            line2 = re.sub(r'https?://\S+', '', line)
            if pathre.search(line2):
                paths.append((os.path.relpath(fp, J), line2[:100]))
                break
say(f'Gate 7a: files with em dash = {emd}; files with a machine path outside URLs = {paths}')
open(os.path.join(J, 'work', 'gates_output.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
