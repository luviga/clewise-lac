"""Wrapper for glpsol (GLPK 4.65) put first on PATH for the compile runs of the job scripts.

Two modes.
  solve mode (default, as in LAC_ALIGN): pass every argument to the real glpsol unchanged and append the header
      of the -o output file (Status and Objective) as one JSON line to the file named by GLPSOL_WRAP_LOG.
  check mode (environment variable GLPSOL_CHECK=1): run `glpsol --check -m <model> -d <data>` instead, which
      translates the model and the data and generates the problem but never solves it. One JSON line per data
      file goes to the file named by GLPSOL_CHECK_LOG (check_log.jsonl): model, data, return code, status
      (translated or T0 failure), rows, columns, non-zeros, seconds, and the last error lines on failure.
      The wrapper exits with glpsol's return code. A translation error is a check failure (T0).
The runner that called the solver finds no solution file in check mode and may stop there; its data files are
already written by then.
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

REAL = M.GLPSOL


def _arg(args, flag):
    for i, a in enumerate(args):
        if a == flag and i + 1 < len(args):
            return args[i + 1]
    return None


def _abs(p):
    return os.path.abspath(p) if p else p


def check_mode(args):
    model, data = _arg(args, "-m"), _arg(args, "-d")
    t0 = time.time()
    proc = subprocess.run([REAL, "--check", "-m", model, "-d", data], capture_output=True, text=True,
                          errors="replace")
    dt = time.time() - t0
    text = proc.stdout + "\n" + proc.stderr
    rows = cols = nz = None
    m = re.search(r"Number of rows\s*=\s*(\d+)\s*Number of columns\s*=\s*(\d+)\s*Number of non-zeros \(matrix\)\s*=\s*(\d+)",
                  text)
    if m:
        rows, cols, nz = (int(x) for x in m.groups())
    ok = proc.returncode == 0 and "Model has been successfully generated" in text
    errors = [ln for ln in text.splitlines() if "error" in ln.lower() or "invalid" in ln.lower()
              or "out of domain" in ln.lower() or "no value" in ln.lower()][-5:]
    rec = dict(time_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), mode="check",
               model=_abs(model), data=_abs(data), returncode=proc.returncode,
               status="translated" if ok else "T0", rows=rows, columns=cols, nonzeros=nz,
               seconds=round(dt, 1), errors=errors)
    out = _arg(args, "-o")
    if out:
        # Several runners read the -o file in a loop until they meet the Karush-Kuhn-Tucker line; without a file
        # they never return. This stub holds no solution: the runner stops on it with an error, which is the
        # intended end of a check-mode compile. Stubs are removed after the compile.
        with open(out, "w", newline="\n") as fh:
            fh.write("Status:     NOT SOLVED (glpsol --check stub written by the check-mode wrapper)\n"
                     "Karush-Kuhn-Tucker optimality conditions: none, no solve was made\n")
        rec["stub_output"] = _abs(out)
    log = os.environ.get("GLPSOL_CHECK_LOG")
    if log:
        with open(log, "a", newline="\n") as fh:
            fh.write(json.dumps(rec) + "\n")
    sys.stdout.write(f"glpsol check: {rec['status']} rows={rows} columns={cols} ({dt:.1f}s) {data}\n")
    return proc.returncode


def solve_mode(args):
    t0 = time.time()
    rc = subprocess.call([REAL] + args)
    dt = time.time() - t0
    out, data = _arg(args, "-o"), _arg(args, "-d")
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
    return rc


if __name__ == "__main__":
    a = sys.argv[1:]
    if os.environ.get("GLPSOL_CHECK") == "1" and _arg(a, "-m") and _arg(a, "-d"):
        sys.exit(check_mode(a))
    sys.exit(solve_mode(a))
