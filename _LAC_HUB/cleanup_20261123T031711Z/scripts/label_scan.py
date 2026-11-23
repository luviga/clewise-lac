"""Scan the compiled files of the scenarios the pipeline runs for old scenario names.

Compiled files: <model>/A2_Output_Params/<scenario>/*.csv and <model>/B1_Output_Params/<scenario>/*.csv (column
Scenario), and the Stage 0 and Stage 3 data files of the scenario (folders named in the scenario catalogue),
searched for any old name. Scenarios come from config/scenarios/scenario_catalogue.csv (groups in_use); the models
are the six energy models of the country table (model_dir), so the sector models are left out; old names are given
on the command line. One row per file and label found.
Usage: python label_scan.py <tree root> <out.csv> <old name> [<old name> ...]
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import machine as M  # noqa: E402

sys.path.insert(0, str(M.ROOT))
import lac_tables as LT  # noqa: E402

root, out, olds = Path(sys.argv[1]), sys.argv[2], sys.argv[3:]
cat = list(csv.DictReader(open(M.ROOT / 'config' / 'scenarios' / 'scenario_catalogue.csv', encoding='utf-8')))
scen = {r['scenario']: r for r in cat if 'in_use' in r['groups'].split('|')}
rx = re.compile(r'(?<![A-Za-z0-9])(' + '|'.join(map(re.escape, olds)) + r')(?![A-Za-z0-9])')
MODELS = [root / c / v['model_dir'] for c, v in LT.country_table('model_dir').items()]
rows, nfiles = [], 0


def add(f, s, found):
    for lab, n in sorted(found.items()):
        rows.append(dict(file=str(f.relative_to(root)).replace('\\', '/'), scenario=s, label=lab, rows=n))


for m in MODELS:
    for kind in ('A2_Output_Params', 'B1_Output_Params'):
        for s in scen:
            for f in sorted((m / kind / s).glob('*.csv')):
                nfiles += 1
                found = {}
                with open(f, encoding='utf-8', errors='replace', newline='') as fh:
                    r = csv.reader(fh)
                    head = next(r, [])
                    col = head.index('Scenario') if 'Scenario' in head else None
                    for line in r:
                        if col is not None:
                            if len(line) > col and rx.fullmatch(line[col]):
                                found[line[col]] = found.get(line[col], 0) + 1
                        else:
                            for lab in rx.findall(','.join(line)):
                                found[lab] = found.get(lab, 0) + 1
                add(f, s, found)
    for s, r in scen.items():
        for key in ('stage0_folder', 'stage3_folder'):
            f = m / 'Executables' / r[key] / f'{r[key]}.txt'
            if not f.is_file():
                continue
            nfiles += 1
            found = {}
            with open(f, encoding='utf-8', errors='replace') as fh:
                for ln in fh:
                    for lab in rx.findall(ln):
                        found[lab] = found.get(lab, 0) + 1
            add(f, s, found)
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['file', 'scenario', 'label', 'rows'], lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print(f'files scanned {nfiles}; files with an old label {len({r["file"] for r in rows})}')
for r in rows:
    print(r)
