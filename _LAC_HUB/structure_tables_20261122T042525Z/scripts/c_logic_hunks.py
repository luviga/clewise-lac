"""For the OSTRAM layout job: every place where a country's A2 compiler or B1 runner differs from the Dominican
Republic's (the reference), after the values moved to the tables. Lines are compared without comments, blank
lines and spacing (tokenize), so only code differences remain.
Writes country_logic_hunks.csv: kind, country, lines in the reference, lines in the country, operation, the
first differing code line of each side (cut at 160 characters). Prints hunk counts per kind and country.
Usage: py -I c_logic_hunks.py <out.csv>
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv  # noqa: E402
import difflib  # noqa: E402
import io  # noqa: E402
import sys  # noqa: E402
import tokenize  # noqa: E402

import yaml  # noqa: E402

cc = yaml.safe_load(open(M.ROOT / 'config/preparation/Config_country_codes.yaml', encoding='utf-8'))['country_data']
REF = 'DominicanRepublic'


def norm_lines(path):
    src = open(path, encoding='utf-8').read()
    out = {}
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT,
                        tokenize.ENDMARKER):
            continue
        out.setdefault(tok.start[0], []).append(tok.string)
    return [(ln, ' '.join(t)) for ln, t in sorted(out.items())]


rows = []
for kind, key in (('A2', 'a2_script'), ('B1', 'b1_script')):
    lines = {c['name']: norm_lines(M.ROOT / c['country_folder'] / c['model_dir'] / c[key]) for c in cc}
    ref = lines[REF]
    for c in cc:
        n = c['name']
        if n == REF:
            continue
        other = lines[n]
        sm = difflib.SequenceMatcher(None, [t for _, t in ref], [t for _, t in other], autojunk=False)
        k = 0
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == 'equal':
                continue
            k += 1
            ra = f'{ref[i1][0]}-{ref[i2 - 1][0]}' if i2 > i1 else (f'after {ref[i1 - 1][0]}' if i1 else 'start')
            rb = f'{other[j1][0]}-{other[j2 - 1][0]}' if j2 > j1 else (f'after {other[j1 - 1][0]}' if j1 else 'start')
            rows.append([kind, n, ra, rb, op, i2 - i1, j2 - j1, ref[i1][1][:160].rstrip() if i2 > i1 else '',
                         other[j1][1][:160].rstrip() if j2 > j1 else ''])
        print(kind, n, 'hunks against', REF, k)
with open(sys.argv[1], 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['kind', 'country', 'lines_reference', 'lines_country', 'operation', 'code_lines_reference',
                'code_lines_country', 'first_line_reference', 'first_line_country'])
    w.writerows(rows)
