"""Phase C scan: every place in a set of tracked files where one of the scenario names occurs, by the method of
LAC_NDC_VERIFY f2_scenario_names.py (a name is a whole token after splitting on non-alphanumeric characters
and on underscores): code string literals (Python, not inside message calls) and lines of batch, shell, YAML
and text files, folder and file names, workbook sheet names and cells, CSV cells.

Usage: py -I c_scan.py <scope|outside> <out.csv>
  scope:   the six energy model folders, the stage pipeline files at the root, config/, inputs/ and the stage
           folders (_STAGE0_OUTPUT, _STAGE1_OUTPUT, _STAGE2_INPUTS, _STAGE2_OUTPUT, _STAGE3_RESULTS)
  outside: every other tracked file outside _LAC_HUB/
Writes one row per (name, place kind, file, place) with a count.
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import ast
import csv
import html
import io
import os
import re
import subprocess
import sys
import zipfile
from collections import Counter

ROOT = M.ROOT_S
NAMES = {"BAU", "NDCNEW", "LTSNEW", "NDC", "LTS", "NDCcond", "NDCincond", "NDP", "NDPAMB", "NDCINC", "LTSOPT", "Default"}
MODELS = ['CostaRica/CR_ENERGY/', 'DominicanRepublic/RD_ENERGY/', 'Ecuador/ECU_Energy/',
          'Guatemala/GUA_ENERGY/', 'Honduras/HON_ENERGY/', 'Jamaica/JAM_ENERGY/']
STAGE_DIRS = ['_STAGE0_OUTPUT/', '_STAGE1_OUTPUT/', '_STAGE2_INPUTS/', '_STAGE2_OUTPUT/', '_STAGE3_RESULTS/',
              'config/', 'inputs/']
ROOT_FILES = {'stage0_run.py', 'stage0_recommend_shares.py', 'stage0_collect_outputs.py', 'stage0_capacity_check.py',
              'stage1_share_analyzer_v16.py', 'stage2_apply_v2.py', 'stage3_apply.py', 'stage3_results.py',
              'stage0_run_all.bat', 'stage0_run_all.sh', 'stage3_run_all.bat', 'stage2_post_clean.py', 'stage0_clean.py',
              'stage1_clean.py', 'ao_safe_save.py', 'lac_tables.py', 'stage0_test.py', 'stage1_test_v16.py',
              'stage2_test_v2.py', 'stage3_test.py', 'stage2_demand_verify.py', 'snapshot_stage.py'}
MSG = {"print", "info", "warning", "warn", "error", "debug", "write", "critical", "exception", "log"}


def in_scope(f):
    return any(f.startswith(m) for m in MODELS) or any(f.startswith(d) for d in STAGE_DIRS) or f in ROOT_FILES


def toks(s):
    out = Counter()
    for t in re.split(r"[^A-Za-z0-9_]+", str(s)):
        if not t:
            continue
        parts = {t} | set(t.split('_'))
        for n in parts & NAMES:
            out[n] += 1
    return out


def scan_py(src):
    hits = Counter()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return toks(src)
    parents = {}
    for p in ast.walk(tree):
        for c in ast.iter_child_nodes(p):
            parents[c] = p
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            p = parents.get(n)
            if isinstance(p, ast.Expr):
                continue  # docstring or code kept as text
            q, d, msg = p, 0, False
            while q is not None and d < 5:
                if isinstance(q, ast.Call):
                    fn = q.func
                    nm = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else '')
                    if nm in MSG:
                        msg = True
                        break
                q, d = parents.get(q), d + 1
            if not msg:
                for k, v in toks(n.value).items():
                    hits[(k, n.lineno)] += v
    return hits


def main():
    which, out = sys.argv[1], sys.argv[2]
    files = subprocess.run(['git', '-C', ROOT, 'ls-files'], capture_output=True, text=True, encoding='utf-8').stdout.splitlines()
    files += subprocess.run(['git', '-C', ROOT, 'ls-files', '--others', '--exclude-standard'], capture_output=True,
                            text=True, encoding='utf-8').stdout.splitlines()
    files = sorted(set(f for f in files if not f.startswith('_LAC_HUB/') and os.path.exists(os.path.join(ROOT, f))))
    files = [f for f in files if in_scope(f) == (which == 'scope')]
    rows = Counter()
    for f in files:
        full = os.path.join(ROOT, f)
        for k, v in toks('/'.join(f.split('/'))).items():
            rows[(k, 'path name', f, f)] += v
        low = f.lower()
        try:
            if low.endswith('.py'):
                src = open(full, encoding='utf-8', errors='replace').read()
                for (k, ln), v in scan_py(src).items():
                    rows[(k, 'code literal', f, f'line {ln}')] += v
            elif low.endswith(('.bat', '.sh', '.yaml', '.yml')):
                for i, ln in enumerate(open(full, encoding='utf-8', errors='replace').read().splitlines(), 1):
                    for k, v in toks(ln).items():
                        rows[(k, 'code or config line', f, f'line {i}')] += v
            elif low.endswith('.csv'):
                rd = csv.reader(io.StringIO(open(full, encoding='utf-8', errors='replace').read()))
                for i, r in enumerate(rd, 1):
                    for j, c in enumerate(r, 1):
                        for k, v in toks(c).items():
                            rows[(k, 'csv cell', f, 'cells')] += v
            elif low.endswith(('.xlsx', '.xlsm')):
                with zipfile.ZipFile(full) as z:
                    names = z.namelist()
                    wb = z.read('xl/workbook.xml').decode('utf-8', 'replace')
                    for s in [html.unescape(s) for s in re.findall(r'<sheet [^>]*name="([^"]+)"', wb)]:
                        for k, v in toks(s).items():
                            rows[(k, 'workbook sheet', f, s)] += v
                    ss = []
                    if 'xl/sharedStrings.xml' in names:
                        x = z.read('xl/sharedStrings.xml').decode('utf-8', 'replace')
                        for si in re.findall(r'<si>(.*?)</si>', x, re.S):
                            ss.append(html.unescape(''.join(re.findall(r'<t[^>]*>(.*?)</t>', si, re.S))))
                    hit = {i: toks(s) for i, s in enumerate(ss)}
                    hit = {i: t for i, t in hit.items() if t}
                    for sf in sorted(n for n in names if re.match(r'xl/worksheets/sheet\d+\.xml$', n)):
                        x = z.read(sf).decode('utf-8', 'replace')
                        if hit:
                            for idx in re.findall(r'<c [^>]*t="s"[^>]*>\s*<v>(\d+)</v>', x):
                                for k, v in hit.get(int(idx), {}).items():
                                    rows[(k, 'workbook cell', f, 'cells')] += v
                        for s in re.findall(r'<c [^>]*t="inlineStr"[^>]*>.*?<t[^>]*>(.*?)</t>', x, re.S):
                            for k, v in toks(html.unescape(s)).items():
                                rows[(k, 'workbook cell', f, 'cells')] += v
            elif low.endswith(('.pickle', '.pkl')):
                b = open(full, 'rb').read().decode('latin-1')
                for k, v in toks(b).items():
                    rows[(k, 'binary (pickle) text', f, 'bytes')] += v
        except Exception as e:  # unreadable file: report
            rows[('?', 'unreadable: ' + type(e).__name__, f, '')] += 1
    with open(out, 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(['name', 'place_kind', 'file', 'place', 'count'])
        for (n, kind, f, place), c in sorted(rows.items()):
            w.writerow([n, kind, f, place, c])
    tot = Counter()
    for (n, kind, f, place), c in rows.items():
        tot[n] += c
    print(which, 'files', len(files), 'names', dict(sorted(tot.items())))


if __name__ == '__main__':
    main()
