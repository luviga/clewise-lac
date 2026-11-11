"""Read Status and Objective from the headers of the Stage 0 or Stage 3 glpsol -o files.

  py -I solve_headers.py S0      ->  stage_logs/solves_stage0.jsonl
  py -I solve_headers.py FINAL   ->  stage_logs/solves_stage3.jsonl
"""
import json
import sys
from pathlib import Path

ROOT = Path(r"C:\clw_overnight")
JOB = ROOT / "_LAC_HUB" / "cost_write_run_20261111T071733Z"
MODEL = {"CostaRica": "CostaRica/CR_ENERGY/t1_confection", "DominicanRepublic": "DominicanRepublic/RD_ENERGY",
         "Ecuador": "Ecuador/ECU_Energy", "Guatemala": "Guatemala/GUA_ENERGY", "Honduras": "Honduras/HON_ENERGY",
         "Jamaica": "Jamaica/JAM_ENERGY"}
tag = sys.argv[1]
out = JOB / "stage_logs" / ("solves_stage0.jsonl" if tag == "S0" else "solves_stage3.jsonl")
with open(out, "w", newline="\n") as fh:
    for c, d in MODEL.items():
        for s in ("BAU", "NDCNEW", "LTSNEW"):
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
