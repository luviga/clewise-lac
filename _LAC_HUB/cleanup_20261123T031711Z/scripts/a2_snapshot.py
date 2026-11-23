"""Copy the compiled inputs, stage outputs, objectives and test results of a run to a snapshot folder, and move
the bulky run logs (A2 produced/installed folders, B1 output copies, B1 data files) out of the job folder.

Usage: py -I a2_snapshot.py <run name> <snapshot folder>
  <snapshot>/tree/<model>/{A2_Output_Params,B1_Output_Params}, <snapshot>/tree/_STAGE*  (files as in the tree)
  <snapshot>/logs/   the run's stage_logs folder (bulky parts moved here, not copied)
Also: py -I a2_snapshot.py --main <snapshot folder>   [ref]  writes the same paths of git ref [ref] (default HEAD) to <snapshot>/tree
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import shutil
import subprocess
import sys
import tarfile
import io
from pathlib import Path

ROOT = M.ROOT
JOB = M.JOB
MODELS = ['CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic/RD_ENERGY', 'Ecuador/ECU_Energy',
          'Guatemala/GUA_ENERGY', 'Honduras/HON_ENERGY', 'Jamaica/JAM_ENERGY']
STAGES = ['_STAGE0_OUTPUT', '_STAGE1_OUTPUT', '_STAGE2_INPUTS', '_STAGE2_OUTPUT', '_STAGE3_RESULTS']
PATHS = [f'{m}/{d}' for m in MODELS for d in ('A2_Output_Params', 'B1_Output_Params')] + STAGES

if sys.argv[1] == '--main':
    dest = Path(sys.argv[2]) / 'tree'
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    data = subprocess.run(['git', '-C', str(ROOT), 'archive', (sys.argv[3] if len(sys.argv) > 3 else 'HEAD'), *PATHS], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tf:
        tf.extractall(dest)
    print('main tree written to', dest)
    sys.exit(0)

run, snap = sys.argv[1], Path(sys.argv[2])
tree = snap / 'tree'
if tree.exists():
    shutil.rmtree(tree)
for p in PATHS:
    src = ROOT / p
    if src.exists():
        shutil.copytree(src, tree / p)
logs = JOB / 'stage_logs' / run
moved = 0
for d in list(logs.glob('a2b1/*/a2/produced')) + list(logs.glob('a2b1/*/a2/installed')) + \
        list(logs.glob('a2b1/*/b1/B1_Output_Params')) + list(logs.glob('a2b1/*/b1/data_files')):
    target = snap / 'logs' / d.relative_to(logs)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(d), str(target))
    moved += 1
shutil.copytree(logs, snap / 'logs', dirs_exist_ok=True)
print('snapshot', snap, 'paths', len(PATHS), 'bulky log folders moved', moved)
# Stage 3 input data files (patched by stage3_apply.py; Executables/ is not tracked)
nfinal = 0
for m in MODELS:
    for f in (ROOT / m / 'Executables').glob('*_FINAL_0/*_FINAL_0.txt'):
        target = snap / 'final_data' / m / f.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
        nfinal += 1
print('Stage 3 input data files copied', nfinal)
