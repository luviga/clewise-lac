"""Phase E (LAC_OVERNIGHT_COST_RUN): Stages 0 to 3 with the commands of the brief, in order.

Each command runs from the clone root with Anaconda Python (the brief's `py`), output to
stage_logs/<nn>_<name>.log; a failing test or an infeasible solve is recorded and the run
continues. The batch files run glpsol 4.65 from PATH (status and
objective are read afterwards from the headers of the -o output files by solve_headers.py).

  py -I phase_e.py <stage>     stage in {0, 1, 2, 3}
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\clw_overnight")
JOB = ROOT / "_LAC_HUB" / "cost_write_run_20261111T071733Z"
LOGS = JOB / "stage_logs"
WRAP = JOB / "scripts" / "glpsol_wrap"
PY = r"C:\Users\luisfernando\anaconda3\python.exe"

STAGES = {
    "0": [("stage0_clean", [PY, "stage0_clean.py", "--confirm"]),
          ("stage0_run", [PY, "stage0_run.py"]),
          ("stage0_run_all", ["cmd", "/c", str(ROOT / "stage0_run_all.bat")]),
          ("stage0_collect_outputs", [PY, "stage0_collect_outputs.py"]),
          ("stage0_capacity_check", [PY, "stage0_capacity_check.py"]),
          ("stage0_recommend_shares", [PY, "stage0_recommend_shares.py"]),
          ("stage0_test", [PY, "stage0_test.py"])],
    "1": [("stage1_share_analyzer_v16", [PY, "stage1_share_analyzer_v16.py"]),
          ("stage1_test_v16", [PY, "stage1_test_v16.py"])],
    "2": [("stage2_apply_v2", [PY, "stage2_apply_v2.py", "--root", ".", "--stage0-denom",
                               r"_STAGE0_OUTPUT\STAGE0_DENOMINATORS.xlsx"]),
          ("stage2_test_v2", [PY, "stage2_test_v2.py", "--stage0-denom", r"_STAGE0_OUTPUT\STAGE0_DENOMINATORS.xlsx"])],
    "3": [("stage3_apply", [PY, "stage3_apply.py", "--root", ".", "--clean", "--uncap-pp-maxcap",
                            "--skip-orphan-cap", "Guatemala"]),
          ("stage3_test", [PY, "stage3_test.py", "--root", "."]),
          ("stage3_run_all", ["cmd", "/c", str(ROOT / "stage3_run_all.bat")]),
          ("stage3_results", [PY, "stage3_results.py", "--root", "."])],
}


def main(stage):
    LOGS.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    # the batch files call glpsol directly; a .bat wrapper on PATH would end the calling batch after the
    # first solve (batch-to-batch without CALL), so status and objective are read from the -o files instead
    env["PYTHONIOENCODING"] = "utf-8"
    status_file = LOGS / "stage_status.jsonl"
    for n, (name, cmd) in enumerate(STAGES[stage], 1):
        log = LOGS / f"s{stage}_{n:02d}_{name}.log"
        t0 = time.time()
        start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(log, "w", newline="\n", encoding="utf-8", errors="replace") as fh:
            fh.write(f"$ {' '.join('python' if c == PY else c for c in cmd)}\n")
            fh.flush()
            p = subprocess.run(cmd, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env)
        dt = time.time() - t0
        rec = dict(stage=stage, step=n, name=name, start_utc=start, seconds=round(dt, 1), exit=p.returncode,
                   log=log.name)
        with open(status_file, "a", newline="\n") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)
        # disk rule: below 80 GB free, delete finished solver outputs (>500 MB) of stage runs
        free = __import__("shutil").disk_usage("C:\\").free / 1e9
        if free < 80:
            print(f"free disk {free:.1f} GB < 80", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
