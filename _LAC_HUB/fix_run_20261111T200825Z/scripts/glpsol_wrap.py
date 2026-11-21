"""Pass-through wrapper for glpsol (GLPK 4.65) that records each solve.

glpsol.bat in scripts/glpsol_wrap/ calls this file; the folder is put first
on PATH only for the B1 runs of this job, so B1's own `glpsol ...` command
reaches the real solver unchanged. After the solve, the header of the -o
output file (Status and Objective lines) is appended as one JSON line to the
file named by GLPSOL_WRAP_LOG, before B1 parses and deletes that output.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

REAL = r"C:\glpk-4.65\w64\glpsol.exe"

args = sys.argv[1:]
t0 = time.time()
rc = subprocess.call([REAL] + args)
dt = time.time() - t0
out = data = None
for i, a in enumerate(args):
    if a == "-o" and i + 1 < len(args):
        out = args[i + 1]
    if a == "-d" and i + 1 < len(args):
        data = args[i + 1]
try:
    status = objective = None
    if out and os.path.exists(out):
        with open(out, errors="replace") as fh:
            for _ in range(15):
                line = fh.readline()
                if line.startswith("Status:"):
                    status = line.split(":", 1)[1].strip()
                if line.startswith("Objective:"):
                    objective = line.split(":", 1)[1].strip()
    rec = dict(time_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), data=data, output=out,
               returncode=rc, seconds=round(dt, 1), status=status, objective=objective)
    log = os.environ.get("GLPSOL_WRAP_LOG")
    if log:
        with open(log, "a", newline="\n") as fh:
            fh.write(json.dumps(rec) + "\n")
except Exception as exc:  # logging must never change the solver's result
    sys.stderr.write(f"glpsol_wrap: could not log the solve: {exc}\n")
sys.exit(rc)
