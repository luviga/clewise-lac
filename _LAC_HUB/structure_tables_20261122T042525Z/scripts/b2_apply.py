"""Apply text replacements to the draft copies of the code files.

A spec file is a Python file that defines EDITS = [(file or list of files, old text, new text, count), ...].
count: default 1 (old must occur exactly once); n (exactly n times); 0 (at least once, all replaced);
-1 (all occurrences on lines that are neither comment lines nor inside a bare string statement; single-line
texts only).
Line endings of the file are kept: old and new are written with LF and converted to CRLF for CRLF files.
An old text that starts with a space matches only at the start of a line (counts 1, n and 0).
Usage: py -I b2_apply.py <spec.py> [--target draft|work]   (draft: work on draft/<file>; work: the clone)
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import ast
import re
import runpy
import sys
from pathlib import Path

ROOT = M.ROOT
JOB = ROOT / '_LAC_HUB' / 'structure_tables_20261122T042525Z'
CR, LF = chr(13), chr(10)

spec = runpy.run_path(sys.argv[1])
target = sys.argv[sys.argv.index('--target') + 1] if '--target' in sys.argv else 'draft'
base = JOB / 'draft' if target == 'draft' else ROOT
failed = 0
for item in spec['EDITS']:
    files, old, new = item[0], item[1], item[2]
    count = item[3] if len(item) > 3 else 1
    if isinstance(files, str):
        files = [files]
    for f in files:
        p = base / f
        raw = p.read_bytes().decode('utf-8')
        nl = CR + LF if CR + LF in raw else LF
        if count == -1:
            lines = raw.split(nl)
            skip = set()
            if f.endswith('.py'):  # lines of bare string statements (docstrings, code kept as text)
                for nd in ast.walk(ast.parse(raw)):
                    if isinstance(nd, ast.Expr) and isinstance(nd.value, ast.Constant) and isinstance(nd.value.value, str):
                        skip.update(range(nd.lineno - 1, nd.end_lineno))
            k = 0
            for i, ln in enumerate(lines):
                if i not in skip and not ln.lstrip().startswith('#') and old in ln:
                    k += ln.count(old)
                    lines[i] = ln.replace(old, new)
            if k == 0:
                print(f'FAIL {f}: not found on a code line: {old[:80]!r}')
                failed += 1
                continue
            p.write_bytes(nl.join(lines).encode('utf-8'))
            continue
        o = old.replace(LF, nl)
        n = new.replace(LF, nl)
        pat = ('(?m)^' if o.startswith(' ') else '') + re.escape(o)
        k = len(re.findall(pat, raw))
        if (count and k != count) or (not count and k == 0):
            print(f'FAIL {f}: found {k} times (expected {count or ">=1"}): {old[:80]!r}')
            failed += 1
            continue
        raw = re.sub(pat, lambda m: n, raw)
        p.write_bytes(raw.encode('utf-8'))
print('failed', failed)
sys.exit(1 if failed else 0)
