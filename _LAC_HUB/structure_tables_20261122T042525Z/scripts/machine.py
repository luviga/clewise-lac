"""Paths of this machine for the job scripts. The repository root and the job folder follow from this file's
place; the Python interpreter of the pipeline and the solver come from `machine.json` beside this file, which
stays out of git (listed in .git/info/exclude). Without it, the names on PATH are used.

machine.json example: {"anaconda": "<path of the Anaconda python.exe>", "glpsol": "<path of glpsol.exe>"}
"""
import json
from pathlib import Path

JOB = Path(__file__).resolve().parents[1]
ROOT = JOB.parents[1]
ROOT_S = ROOT.as_posix()
JOB_S = JOB.as_posix()
DRIVE = ROOT.anchor
_cfg = {}
_f = Path(__file__).with_name('machine.json')
if _f.exists():
    _cfg = json.loads(_f.read_text(encoding='utf-8'))
ANACONDA = _cfg.get('anaconda', 'python')
GLPSOL = _cfg.get('glpsol', 'glpsol')
