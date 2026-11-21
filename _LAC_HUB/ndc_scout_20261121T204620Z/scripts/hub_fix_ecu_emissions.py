"""Hub fix of alignment_ECU.csv: the Ecuador task compared emission targets with a sum of four
emission labels. The brief forbids summing labels, so the five rows are recomputed from the single
label CO2e_sources (fuel combustion counted at the DIST_* technologies, the same label used for the
Dominican Republic). Usage: python -I hub_fix_ecu_emissions.py <job_folder>
"""
import os
import sys
import pandas as pd

JOB = sys.argv[1]
lev = pd.read_csv(os.path.join(JOB, "model_levers_ECU.csv"))
e = lev[(lev["quantity"] == "emissions by label") & (lev["technology"] == "CO2e_sources")].iloc[0]
row_no = int(e.name) + 2  # line number in the CSV file (header is line 1)

fn = os.path.join(JOB, "alignment_ECU.csv")
a = pd.read_csv(fn, dtype=str, keep_default_na=False)
ref = f"model_levers_ECU.csv line {row_no} (solved, emissions by label, CO2e_sources)"
LABEL_NOTE = ("Hub recomputed from the single label CO2e_sources (fuel combustion counted at the DIST_* "
              "technologies; it does not carry the known unintended EmissionActivityRatio differences of the "
              "power plants). The country task had added four labels (CO2e_DE, CO2e_FUG, CO2e_REF, CO2_PP); the "
              "brief forbids summing labels, so that build was dropped. CO2e_sources leaves out fugitive and "
              "refinery process emissions. Unit Mt CO2e assumed, converted to kt where the target is in kt or Gg.")


def status(ratio):
    if ratio is None:
        return ""
    if ratio < 0:
        return "opposite direction"
    if abs(ratio - 1) <= 0.10:
        return "matches"
    return "same direction, different size"


def setrow(tid, kind, target, year, keep_note):
    i = a.index[a["target_id"] == tid][0]
    bau = float(e[f"BAU_{year}"])
    vals = {}
    for s in ["NDCNEW", "LTSNEW"]:
        v = float(e[f"{s}_{year}"])
        if kind == "pct":
            vals[s] = 100 * (1 - v / bau)
        elif kind == "kt_red":
            vals[s] = 1000 * (bau - v)
        else:
            vals[s] = 1000 * v
    a.at[i, "model_reference"] = ref
    a.at[i, "NDCNEW_value"] = f"{vals['NDCNEW']:.4f}" if kind == "pct" else f"{vals['NDCNEW']:.2f}"
    a.at[i, "LTSNEW_value"] = f"{vals['LTSNEW']:.4f}" if kind == "pct" else f"{vals['LTSNEW']:.2f}"
    rn = vals["NDCNEW"] / target
    rl = vals["LTSNEW"] / target
    a.at[i, "ratio_NDCNEW"] = f"{rn:.3f}"
    a.at[i, "ratio_LTSNEW"] = f"{rl:.3f}"
    a.at[i, "status"] = status(rn)
    a.at[i, "note"] = (keep_note + " " if keep_note else "") + f"Model BAU {year} CO2e_sources {bau:.3f}. " + LABEL_NOTE


setrow("ECU-T001", "pct", 7.0, 2035, "Model covers energy and transport only; the NDC target is economy-wide against the NDC trend scenario (2010 base).")
setrow("ECU-T003", "pct", 15.0, 2035, "Target value used for the ratio is 15 percent (7 percent unconditional plus 8 percent additional), the task's reading of p.55 and p.56.")
setrow("ECU-T002", "kt_red", 8800.0, 2035, "The NDC 8,800 kt covers all five sectors including LULUCF.")
setrow("ECU-T020", "abs", 39200.0, 2035, "PLANMICC 2018 base 38,400 Gg.")
setrow("ECU-T021", "abs", 35800.0, 2050, "PLANMICC 2018 base 38,400 Gg.")
a.to_csv(fn, index=False, lineterminator="\n")
print(a[a["target_id"].isin(["ECU-T001", "ECU-T002", "ECU-T003", "ECU-T020", "ECU-T021"])][
    ["target_id", "target_value", "NDCNEW_value", "LTSNEW_value", "ratio_NDCNEW", "ratio_LTSNEW", "status"]].to_string())
