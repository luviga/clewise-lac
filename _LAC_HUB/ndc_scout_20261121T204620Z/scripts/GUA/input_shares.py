"""Renewable share implied by the compiled plant activity limits (Guatemala), and selected
yearly input rows. Read-only.

Usage: python -I input_shares.py <model_root>
"""
import os
import sys

import pandas as pd

ROOT = sys.argv[1]
P = os.path.join(ROOT, "Guatemala", "GUA_ENERGY", "B1_Output_Params")
REN = {"PPBGS", "PPBIM", "PPGEO", "PPHDAM", "PPHROR", "PPPVD", "PPPVDS", "PPPVT", "PPPVT2",
       "PPPVTS", "PPWNDON"}


def load(s, name):
    return pd.read_csv(os.path.join(P, s, name + ".csv"))


for s in ["BAU", "NDCNEW", "LTSNEW"]:
    lo = load(s, "TotalTechnologyAnnualActivityLowerLimit")
    up = load(s, "TotalTechnologyAnnualActivityUpperLimit")
    for y in [2025, 2030, 2035, 2040, 2050]:
        l = lo[(lo.YEAR == y) & lo.TECHNOLOGY.str.startswith("PP")].set_index("TECHNOLOGY").Value
        u = up[(up.YEAR == y) & up.TECHNOLOGY.str.startswith("PP")].set_index("TECHNOLOGY").Value
        techs = sorted(set(l.index) | set(u.index))
        mid = {}
        for t in techs:
            a = l.get(t)
            b = u.get(t)
            if a is not None and b is not None and b < 9000:
                mid[t] = (a + b) / 2
            elif a is not None:
                mid[t] = a
            else:
                mid[t] = 0.0
        ren_l = sum(v for t, v in l.items() if t in REN)
        tot_l = sum(l.values)
        ren_m = sum(v for t, v in mid.items() if t in REN)
        tot_m = sum(mid.values())
        print(f"{s} {y}: lower-limit total {tot_l:.3f} PJ, renewable share of lower limits "
              f"{ren_l / tot_l:.4f}; midpoint total {tot_m:.3f}, share {ren_m / tot_m:.4f}")

print()
for s in ["BAU", "NDCNEW", "LTSNEW"]:
    e = load(s, "EmissionActivityRatio")
    r = e[(e.TECHNOLOGY == "DIST_GSL") & (e.YEAR.between(2024, 2032))]
    print(s, "DIST_GSL EAR", [(int(a), round(b, 6)) for a, b in zip(r.YEAR, r.Value)])
    lo = load(s, "TotalTechnologyAnnualActivityLowerLimit")
    r = lo[(lo.TECHNOLOGY == "IMP_ELE") & (lo.YEAR.between(2024, 2032))]
    print(s, "IMP_ELE lower", [(int(a), round(b, 4)) for a, b in zip(r.YEAR, r.Value)])
    up = load(s, "TotalTechnologyAnnualActivityUpperLimit")
    r = up[(up.TECHNOLOGY == "IMP_ELE") & (up.YEAR.isin([2025, 2030, 2035, 2050]))]
    print(s, "IMP_ELE upper", [(int(a), round(b, 4)) for a, b in zip(r.YEAR, r.Value)])
