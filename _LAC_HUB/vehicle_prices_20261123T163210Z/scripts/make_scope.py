"""Write scope_cells.csv: the vehicle CapitalCost cells in scope (parameter CapitalCost, model name
containing ENERGY or TRANSPORT) from the cost-sources proposal files, with their cell locators.

Usage: python -I make_scope.py <cost-sources folder>
The folder is _LAC_HUB/cost_sources_20261122T234333Z of the repository (or a copy of it taken from
the branch job/cost-sources while that pull request is open).
"""
import os
import sys

import pandas as pd

JOB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CCS = ["CR", "DR", "GUA", "HON", "JAM"]


def main():
    src = sys.argv[1]
    frames = []
    for cc in CCS:
        d = pd.read_csv(os.path.join(src, cc, f"proposals_{cc}.csv"), dtype=str, keep_default_na=False)
        d = d[(d.parameter == "CapitalCost") & d.model.str.contains("ENERGY|TRANSPORT")]
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    d.to_csv(os.path.join(JOB, "scope_cells.csv"), index=False, lineterminator="\n")
    print(len(d), "cells,", d.groupby(["model"]).tech.nunique().to_dict())


if __name__ == "__main__":
    main()
