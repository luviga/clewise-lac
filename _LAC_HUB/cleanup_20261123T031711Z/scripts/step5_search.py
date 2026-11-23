"""Step 5.1: prove per candidate that no script the pipeline runs names it.

Search set: every script the pipeline runs and the tables it reads:
  - A1, A2 and B1 scripts of the six energy models (A1: the country's A1_Model_Structure script; A2 and B1: the
    scripts named in config/preparation/Config_country_codes.yaml) and the local modules they import;
  - Stages 0 to 3 (stage*.py, stage0_run_all.bat/.sh, stage3_run_all.bat), their tests, the two unit tests and
    ao_safe_save.py, the loader lac_tables.py, every table under config/ and inputs/;
  - one level more: any tracked text file (yaml, yml, csv, txt, py) of a model folder whose name a file above holds.
Tokens per candidate: the file or folder name (exact, between non-name characters); for files also the name
without extension, and that stem without a trailing run number (for names built in code, such as
'Blend_Shares_' + str(n) + '.pickle').
Writes work/step5_search.csv: one row per candidate with size, the reason it is a candidate, and every hit
(file, line, text) or "no hit".

Usage: python step5_search.py <candidates.csv>   (columns: path, why)
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import machine as M  # noqa: E402

ROOT = M.ROOT
sys.path.insert(0, str(ROOT))
import lac_tables as LT  # noqa: E402

tracked = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8').stdout.splitlines()
tracked_set = set(tracked)
A1 = {'CostaRica': 'A1_Model_Structure.py', 'DominicanRepublic': None, 'Ecuador': 'A1_Model_Structure_Energy.py',
      'Guatemala': 'A1_Model_Structure.py', 'Honduras': 'A1_Model_Structure_HON.py', 'Jamaica': 'A1_Model_Structure_JAM.py'}
search = []
for c in LT.countries():
    mp = LT.model_path(c)
    for name in (A1[c], LT.country_value(c, 'a2_script'), LT.country_value(c, 'b1_script'), 'setup_utils.py'):
        if name and f'{mp}/{name}' in tracked_set:
            search.append(f'{mp}/{name}')
search += [f for f in tracked if '/' not in f and (re.match(r'stage\d', f) or f in (
    'lac_tables.py', 'test_ao_safe_save.py', 'test_ao_cost_repair_manager.py', 'ao_safe_save.py'))]
search += [f for f in tracked if f.startswith(('config/', 'inputs/'))]
# one level more: text files of the model folders named by the files above
models = [LT.model_path(c) for c in LT.countries()]
units = ['/'.join(m.split('/')[:2]) for m in models]  # energy folders (Costa Rica: CR_ENERGY, above t1_confection)
texts = {}


def text(rel):
    if rel not in texts:
        try:
            texts[rel] = (ROOT / rel).read_text(encoding='utf-8', errors='replace')
        except OSError:
            texts[rel] = ''
    return texts[rel]


blob = '\n'.join(text(f) for f in search)
with open(sys.argv[1], encoding='utf-8', newline='') as fh:
    cands = list(csv.DictReader(fh))
cand_paths = [c['path'] for c in cands]


def is_candidate(f):
    return any(f == c or f.startswith(c.rstrip('/') + '/') for c in cand_paths)


def model_of(rel):
    return next((m for m in units if rel.startswith(m + '/')), None)


extra = []
for f in tracked:
    if f in search or is_candidate(f) or not f.startswith(tuple(m + '/' for m in units)):
        continue
    if not f.lower().endswith(('.yaml', '.yml', '.csv', '.txt', '.py')) or '/A2_Output_Params/' in f or '/B1_Output_Params/' in f:
        continue
    base = f.rsplit('/', 1)[-1]
    if re.search(r'(?<![\w.])' + re.escape(base) + r'(?![\w])', blob):
        extra.append(f)
search += extra


def tokens(path):
    name = path.rstrip('/').rsplit('/', 1)[-1]
    out = [name]
    if '.' in name and not path.endswith('/'):
        stem = name.rsplit('.', 1)[0]
        out.append(stem)
        bare = re.sub(r'[_\-]?\d+$', '', stem)
        if bare != stem and len(bare) >= 6:
            out.append(bare)
    return out


ENERGY = tuple('/'.join(m.split('/')[:2]) + '/' for m in models)
others = [f for f in tracked if f not in search and f.lower().endswith(('.py', '.yaml', '.yml', '.bat', '.sh', '.ipynb'))
          and (f.startswith(ENERGY) or '/' not in f)]
rows = []
for cand in cands:
    p = cand['path']
    full = ROOT / p.rstrip('/')
    if full.is_dir():
        size = sum(f.stat().st_size for f in full.rglob('*') if f.is_file())
        nfiles = sum(1 for f in tracked if f.startswith(p.rstrip('/') + '/'))
    elif full.exists():
        size, nfiles = full.stat().st_size, 1
    else:
        size, nfiles = 0, 0
    hits = []
    for tok in tokens(p):
        rx = re.compile(r'(?<![\w])' + re.escape(tok) + r'(?![\w])')
        for f in search:
            if f == p or f.startswith(p.rstrip('/') + '/'):
                continue
            # a model-folder script opens names relative to its own folder: a hit counts only in the same model
            # folder, or in a file outside the model folders (root scripts and tables)
            if model_of(f) is not None and model_of(f) != model_of(p):
                continue
            for i, line in enumerate(text(f).splitlines(), 1):
                if rx.search(line):
                    hits.append(f'{f}:{i}: [{tok}] {line.strip()[:160]}')
    # second pass: any other script or configuration kept in the same energy folder (or at the root) that names
    # the candidate, so that no kept tool loses a file it reads
    other = []
    unit = '/'.join(p.split('/')[:2])
    for f in others:
        if f == p or f.startswith(p.rstrip('/') + '/') or is_candidate(f):
            continue
        if '/' in f and '/'.join(f.split('/')[:2]) != unit:
            continue
        for tok in tokens(p)[:2]:
            rx = re.compile(r'(?<![\w])' + re.escape(tok) + r'(?![\w])')
            for i, line in enumerate(text(f).splitlines(), 1):
                if rx.search(line):
                    other.append(f'{f}:{i}: [{tok}] {line.strip()[:160]}')
    rows.append(dict(path=p, files=nfiles, bytes=size, why=cand['why'], hits=len(hits),
                     search_result='no hit' if not hits else ' || '.join(hits[:12]),
                     other_hits=len(other), other_result='no hit' if not other else ' || '.join(other[:8])))
out = M.JOB / 'work' / 'step5_search.csv'
with open(out, 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['path', 'files', 'bytes', 'why', 'hits', 'search_result', 'other_hits',
                                       'other_result'], lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
(M.JOB / 'work' / 'step5_search_set.txt').write_text('\n'.join(search) + '\n', encoding='utf-8')
print(f'search set {len(search)} files ({len(extra)} named by them); candidates {len(rows)}; with hits {sum(1 for r in rows if r["hits"])}')
for r in rows:
    print(f'{r["hits"]:4d}  {r["path"]}')
