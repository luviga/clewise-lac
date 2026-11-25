"""Step 3.3: stale_compiled.csv from stale_compare.csv: one row per regenerated compiled file whose differences are
staleness (model, scenario, parameter, cells changed, example cell with before and after, the cause), and
stale_nondeterminism.csv for the files whose differences are row order, formatting or float noise only (restored,
not committed). Causes come from CAUSES below, keyed by model and folder (found in step 3.2).
Usage: py -I stale_table.py"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv

JOB = M.JOB
CAUSES = {
    ("DominicanRepublic/RD_AFOLU", "A2_Output_Params", "BAU"):
        "A2_Compiler.py wrote the policy folders only and never BAU; the BAU tables kept values older than the "
        "workbooks (code fixed: the base tables are written as in JAM_AFOLU's compiler)",
    ("DominicanRepublic/RD_AFOLU", "B1_Output_Params", "BAU"):
        "B1 runner reads the stale A2_Output_Params/BAU; regenerated with it",
    ("Ecuador/ECU_USCUSS", "A2_Output_Params", "NDC"):
        "A2_Compiler.py wrote only Other_Scenarios (NDCINC) besides BAU; NDC and NDCCON kept tables older than the "
        "workbooks (code fixed: every policy scenario of the B1 configuration is written)",
    ("Ecuador/ECU_USCUSS", "A2_Output_Params", "NDCCON"): "as NDC",
    ("Ecuador/ECU_USCUSS", "B1_Output_Params", "NDC"): "B1 runner reads the stale A2_Output_Params/NDC; regenerated with it",
    ("Ecuador/ECU_USCUSS", "B1_Output_Params", "NDCCON"): "B1 runner reads the stale A2_Output_Params/NDCCON; regenerated with it",
}


def split(path):
    parts = path.split("/")
    i = next(k for k, p in enumerate(parts) if p in ("A2_Output_Params", "B1_Output_Params"))
    return "/".join(parts[:i]), parts[i], parts[i + 1], parts[-1][:-4]


rows = list(csv.DictReader(open(JOB / "stale_compare.csv", encoding="utf-8")))
stale, noise = [], []
for r in rows:
    model, folder, scen, param = split(r["path"])
    rec = dict(model=model, folder=folder, scenario=scen, parameter=param,
               cells_changed=int(r["values_changed"] or 0) + int(r["keys_only_tracked"] or 0) + int(r["keys_only_new"] or 0),
               values_changed=r["values_changed"], rows_only_tracked=r["keys_only_tracked"],
               rows_only_new=r["keys_only_new"], scenario_label=r.get("scenario_label", ""),
               example=r["example"] or (f"scenario label {r.get('scenario_label')}" if r.get("scenario_label") else ""),
               cause=CAUSES.get((model, folder, scen), "difference without a cause found in the compile code"))
    if r["kind"] == "staleness" and not rec["cells_changed"] and r.get("scenario_label"):
        rec["cause"] = (f"scenario label only: the tracked table carries {r['scenario_label'].split(' -> ')[0]}, the "
                        f"compiler writes the folder's own name; every value is identical")
    if r.get("git_status") == "??":
        rec["cause"] = "new folder for a scenario the model does not have (A2 compiler writes Other_Scenarios); not committed"
    (stale if r["kind"] == "staleness" else noise).append(rec)
for name, data in (("stale_compiled.csv", stale), ("stale_nondeterminism.csv", noise)):
    with open(JOB / name, "w", newline="", encoding="utf-8") as fh:
        fields = ["model", "folder", "scenario", "parameter", "cells_changed", "values_changed", "rows_only_tracked",
                  "rows_only_new", "scenario_label", "example", "cause"]
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(data)
    print(name, len(data))
for r in stale:
    print(r["model"], r["folder"], r["scenario"], r["parameter"], r["cells_changed"], r["example"][:80])
