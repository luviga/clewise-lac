"""Step 1.1: write config/gates/models.csv, one row per OSeMOSYS_Model.txt found in the tree (job folders excluded).
Scenario list from each model's own B1_Scenario_Config.xlsx sheet Scenarios (rows with Activated YES, column
Reference, as the B1 runners read it). Kind: energy for the six models of config/preparation/Config_country_codes.yaml
(those are the models stage3_apply.py patches), transport for a model whose folder name holds TRANSPORT, sector
otherwise. Runner scripts: the A2 compiler and B1 runner named in the country table for energy models, otherwise
the single A2_Compiler*.py and B1_*Parallel*.py of the folder (files with TESTEOS in the name are test copies)."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import hashlib
import importlib.util
import pandas as pd

ROOT = M.ROOT
spec = importlib.util.spec_from_file_location('lac_tables', str(ROOT / 'lac_tables.py'))
LT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(LT)
energy = {LT.model_path(c): c for c in LT.countries()}
rows = []
versions = {}
for mf in sorted(ROOT.rglob('OSeMOSYS_Model.txt')):
    rel = mf.parent.relative_to(ROOT).as_posix()
    if rel.startswith('_') or '/_' in rel:
        continue
    d = mf.parent
    if rel in energy:
        c = energy[rel]
        a2, b1, kind = LT.country_value(c, 'a2_script'), LT.country_value(c, 'b1_script'), 'energy'
    else:
        a2s = sorted(p.name for p in d.glob('A2_Compiler*.py') if p.name in ('A2_Compiler.py',) or 'UNROUND' not in p.name and '_ECU' not in p.name)
        a2 = 'A2_Compiler.py' if 'A2_Compiler.py' in a2s else a2s[0]
        b1s = sorted(p.name for p in d.glob('B1_*Parallel*.py') if 'TESTEOS' not in p.name)
        b1 = b1s[0]
        kind = 'transport' if 'TRANSPORT' in rel.upper() else 'sector'
    sc = pd.read_excel(d / 'B1_Scenario_Config.xlsx', sheet_name='Scenarios')
    scen = [str(r) for r, a in zip(sc['Reference'], sc['Activated']) if str(a).strip().upper() == 'YES' and r != 'based']
    base = [str(n) for n, b in zip(sc['Name'], sc['Base']) if str(b).strip().upper() == 'YES']
    h = hashlib.sha1(mf.read_bytes()).hexdigest()
    versions.setdefault(h, len(versions) + 1)
    model = rel.split('/')[1] if rel.count('/') >= 1 else rel
    rows.append(dict(model=model, path=rel, kind=kind, a2_compiler=a2, b1_runner=b1, scenarios='|'.join(scen),
                     base_scenario=base[0] if base else '', stage3=('yes' if kind == 'energy' else 'no'),
                     model_file_version=f'v{versions[h]}',
                     description=f'{kind} model {model}; scenarios from B1_Scenario_Config.xlsx sheet Scenarios'))
with open(ROOT / 'config' / 'gates' / 'models.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r['model'], r['kind'], r['a2_compiler'], r['b1_runner'], r['scenarios'], r['model_file_version'])
