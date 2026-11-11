"""Shared paths and loaders for LAC_COST_REVIEW_PACK. Read-only on everything outside this job folder."""
import glob
import os
import subprocess

import pandas as pd

STAMP = "20261111T015203Z"
BASE = "2ddd560"
REPO = r"C:\clw_cost_review"
JOB = os.path.join(REPO, "_LAC_HUB", f"cost_review_{STAMP}")
SCRATCH = os.path.join(JOB, "scratch")

CCS = ["ecu", "cr", "jam", "dr", "gua", "hon"]  # report order
COUNTRY = {"cr": "Costa Rica", "dr": "Dominican Republic", "ecu": "Ecuador",
           "gua": "Guatemala", "hon": "Honduras", "jam": "Jamaica"}
PR = {"jam": 2, "hon": 3, "ecu": 4, "dr": 5, "gua": 6, "cr": 7}
HEAD_BRIEF = {"jam": "789b36a", "hon": "79a3665", "ecu": "ddd8d31",
              "dr": "a0c2845", "gua": "0703ae2", "cr": "7e8dd76"}
ENERGY = {"cr": "CostaRica/CR_ENERGY/t1_confection", "dr": "DominicanRepublic/RD_ENERGY",
          "ecu": "Ecuador/ECU_Energy", "gua": "Guatemala/GUA_ENERGY",
          "hon": "Honduras/HON_ENERGY", "jam": "Jamaica/JAM_ENERGY"}
SECTION4 = ["BRIEF", "REPORT_*.md", "GAPS_*.md", "CHANGES_*.md", "proposals.csv",
            "proposals_summary.csv", "fuel_prices.csv", "price_points_2024.csv",
            "plant_costs.csv", "sources.csv", "constants.csv", "search_log.csv",
            "paper_trace.csv", "cost_rows_current.csv", "baseline_before.csv",
            "baseline_after.csv"]
EXTRA = {"ecu": ["mapping_ECU.csv"], "cr": ["structure_proposals.csv"]}


def branch(cc):
    return f"origin/job/cost-src-{cc}"


def git(*args, binary=False):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "replace"))
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def jobdir(cc):
    """Job folder of the branch, extracted read-only copy under scratch."""
    return glob.glob(os.path.join(SCRATCH, f"br_{cc}", "_LAC_HUB", f"cost_src_{cc}_*"))[0]


def jobname(cc):
    return os.path.basename(jobdir(cc))


def downloads(cc):
    return glob.glob(rf"C:\clw_cost_{cc}\_LAC_HUB\cost_src_{cc}_*\downloads")[0]


def read(cc, name):
    p = os.path.join(jobdir(cc), name)
    if not os.path.exists(p):
        return None
    return pd.read_csv(p, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def text(cc, pattern):
    ps = glob.glob(os.path.join(jobdir(cc), pattern))
    if not ps:
        return ""
    with open(ps[0], encoding="utf-8-sig", errors="replace") as f:
        return f.read()


def num(x):
    try:
        return float(str(x).replace(",", ""))
    except (TypeError, ValueError):
        return None


def out(name):
    return os.path.join(JOB, name)


def write(df, name):
    df = df.apply(lambda c: c.str.strip() if c.dtype == object or str(c.dtype).startswith("str") else c)
    df.to_csv(out(name), index=False, encoding="utf-8", lineterminator="\n")
