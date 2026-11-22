"""For the OSTRAM layout job: where the six A2 compilers and the six B1 runners differ in logic.

Each script is cut into top-level units (each function, and each top-level statement block between functions);
a unit's logic is its syntax tree with string and number constants kept and comments dropped. Units with the
same name (functions) or the same position (top-level blocks, numbered) are compared across the six countries
and grouped by identical logic.
Writes country_logic_differences.csv: kind (A2 or B1), unit, line in each script, groups of countries with
identical logic (countries in one group share the logic; a unit missing in a country is listed as absent).
Usage: py -I c_logic_diff.py <out.csv>
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import ast  # noqa: E402
import csv  # noqa: E402
import sys  # noqa: E402
import warnings  # noqa: E402

import yaml  # noqa: E402

warnings.simplefilter('ignore')
cc = yaml.safe_load(open(M.ROOT / 'config/preparation/Config_country_codes.yaml', encoding='utf-8'))['country_data']


def units(path):
    tree = ast.parse(open(path, encoding='utf-8').read())
    out = {}
    block, start, k = [], None, 0
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if block:
                k += 1
                out[f'top-level block {k}'] = (start, '\n'.join(ast.dump(b) for b in block))
                block = []
            out[f'def {node.name}'] = (node.lineno, ast.dump(node))
        else:
            if not block:
                start = node.lineno
            block.append(node)
    if block:
        k += 1
        out[f'top-level block {k}'] = (start, '\n'.join(ast.dump(b) for b in block))
    return out


rows = []
for kind, key in (('A2', 'a2_script'), ('B1', 'b1_script')):
    per = {}
    for c in cc:
        p = M.ROOT / c['country_folder'] / c['model_dir'] / c[key]
        per[c['name']] = units(p)
    names = []
    for c in cc:
        for u in per[c['name']]:
            if u not in names:
                names.append(u)
    for u in names:
        groups = {}
        lines = []
        for c in cc:
            n = c['name']
            if u in per[n]:
                groups.setdefault(per[n][u][1], []).append(n)
                lines.append(f"{n}:{per[n][u][0]}")
            else:
                groups.setdefault('absent', []).append(n)
        if len(groups) == 1 and 'absent' not in groups:
            continue
        g = ' / '.join(('absent: ' if d == 'absent' else '') + '+'.join(v) for d, v in groups.items())
        rows.append([kind, u, ' '.join(lines), len([d for d in groups if d != 'absent']), g])
with open(sys.argv[1], 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['kind', 'unit', 'line_in_each_script', 'distinct_versions', 'countries_with_identical_logic'])
    w.writerows(rows)
for kind in ('A2', 'B1'):
    print(kind, 'units that differ', sum(1 for r in rows if r[0] == kind))
