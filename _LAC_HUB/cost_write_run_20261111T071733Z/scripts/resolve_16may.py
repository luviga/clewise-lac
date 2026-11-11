"""Solve the main copy's 16 May Stage 3 data files (Executables/<scen>_FINAL_0/<scen>_FINAL_0.txt, read only)
again with the same OSeMOSYS_Model.txt and glpsol 4.65, to recover the 16 May solve status and objective
value, which the tracked results workbook does not record. The solver output goes to a temporary folder
and is deleted after its header is read. Writes resolve_16may.jsonl in the job folder.
"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

MAIN = Path(r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5")
ROOT = Path(r"C:\clw_overnight")
JOB = ROOT / "_LAC_HUB" / "cost_write_run_20261111T071733Z"
TMP = Path(sys.argv[1])
GLPSOL = r"C:\glpk-4.65\w64\glpsol.exe"
MODEL = {"CostaRica": "CostaRica/CR_ENERGY/t1_confection", "DominicanRepublic": "DominicanRepublic/RD_ENERGY",
         "Ecuador": "Ecuador/ECU_Energy", "Guatemala": "Guatemala/GUA_ENERGY", "Honduras": "Honduras/HON_ENERGY",
         "Jamaica": "Jamaica/JAM_ENERGY"}

TMP.mkdir(parents=True, exist_ok=True)
log = JOB / "resolve_16may.jsonl"
for c, d in MODEL.items():
    m_main = MAIN / d / "OSeMOSYS_Model.txt"
    m_clone = ROOT / d / "OSeMOSYS_Model.txt"
    same_model = hashlib.sha256(m_main.read_bytes()).hexdigest() == hashlib.sha256(m_clone.read_bytes()).hexdigest()
    for s in ("BAU", "NDCNEW", "LTSNEW"):
        data = MAIN / d / "Executables" / f"{s}_FINAL_0" / f"{s}_FINAL_0.txt"
        out = TMP / f"{c}_{s}_FINAL_0_output.txt"
        t0 = time.time()
        rc = subprocess.call([GLPSOL, "-m", str(m_clone), "-d", str(data), "-o", str(out)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        status = obj = None
        if out.exists():
            with open(out, errors="replace") as fh:
                for _ in range(15):
                    ln = fh.readline()
                    if ln.startswith("Status:"):
                        status = ln.split(":", 1)[1].strip()
                    if ln.startswith("Objective:"):
                        obj = ln.split(":", 1)[1].strip()
            out.unlink()
        rec = dict(data=f"{d}/Executables/{s}_FINAL_0/{s}_FINAL_0.txt (main copy, 16 May)".replace("/", "\\"),
                   status=status, objective=obj, returncode=rc, seconds=round(time.time() - t0, 1),
                   model_identical_to_clone=same_model)
        with open(log, "a", newline="\n") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(c, s, status, obj, flush=True)
