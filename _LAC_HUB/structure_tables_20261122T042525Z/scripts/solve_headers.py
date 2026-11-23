"""Read Status and Objective from the headers of the Stage 0 or Stage 3 glpsol -o files.

  py -I solve_headers.py S0      ->  stage_logs/solves_stage0.jsonl
  py -I solve_headers.py FINAL   ->  stage_logs/solves_stage3.jsonl
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import json
import os
import sys
from pathlib import Path

ROOT = M.ROOT
JOB = ROOT / "_LAC_HUB" / "structure_tables_20261122T042525Z"
MODEL = {"CostaRica": "CostaRica/CR_ENERGY/t1_confection", "DominicanRepublic": "DominicanRepublic/RD_ENERGY",
         "Ecuador": "Ecuador/ECU_Energy", "Guatemala": "Guatemala/GUA_ENERGY", "Honduras": "Honduras/HON_ENERGY",
         "Jamaica": "Jamaica/JAM_ENERGY"}
import importlib.util as _ilu  # noqa: E402
_spec = _ilu.spec_from_file_location("lac_tables", str(ROOT / "lac_tables.py"))
LT = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(LT)
tag = sys.argv[1]
out = JOB / "stage_logs" / os.environ.get("LAC_RUN", "baseline") / ("solves_stage0.jsonl" if tag == "S0" else "solves_stage3.jsonl")
with open(out, "w", newline="\n") as fh:
    for c, d in MODEL.items():
        for s in LT.scenarios():
            f = ROOT / d / "Executables" / f"{s}_{tag}_0" / f"{s}_{tag}_0_output.txt"
            status = obj = None
            size = f.stat().st_size if f.exists() else 0
            if f.exists():
                with open(f, errors="replace") as g:
                    for _ in range(15):
                        ln = g.readline()
                        if ln.startswith("Status:"):
                            status = ln.split(":", 1)[1].strip()
                        if ln.startswith("Objective:"):
                            obj = ln.split(":", 1)[1].strip()
            rec = dict(country=c, scenario=s, data=f"{d}/Executables/{s}_{tag}_0/{s}_{tag}_0.txt".replace("/", "\\"),
                       status=status or "no output", objective=obj, output_bytes=size)
            fh.write(json.dumps(rec) + "\n")
            print(c, s, status, obj, size)
