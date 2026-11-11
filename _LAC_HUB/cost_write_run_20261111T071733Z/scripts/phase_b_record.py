"""Phase B record: pipeline_commands.csv, baseline_A2_diff.csv, baseline_B1_diff.csv
from the chosen candidate runs saved under baseline/<country>/{A2,B1}/."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

JOB = Path(r"C:\clw_overnight\_LAC_HUB\cost_write_run_20261111T071733Z")
A2C = {"CostaRica": "cand2_anaconda_pandas2", "DominicanRepublic": "cand2_anaconda_pandas2",
       "Ecuador": "cand2_anaconda_pandas2", "Guatemala": "cand2_anaconda_pandas2",
       "Honduras": "cand2_anaconda_pandas2", "Jamaica": "cand2_anaconda_pandas2"}
B1C = {c: "cand1_anaconda" for c in A2C}
MODEL = {"CostaRica": "CostaRica/CR_ENERGY/t1_confection", "DominicanRepublic": "DominicanRepublic/RD_ENERGY",
         "Ecuador": "Ecuador/ECU_Energy", "Guatemala": "Guatemala/GUA_ENERGY", "Honduras": "Honduras/HON_ENERGY",
         "Jamaica": "Jamaica/JAM_ENERGY"}

EXPL = {
    "Jamaica": "tracked value empty: the 12 May A2 run read the workbook before the 9 November safe-save fix "
               "restored its formula values; the regenerated value comes from the restored workbook (expected, "
               "brief section 3)",
    "DominicanRepublic": "transport: the current DR A1 workbooks give TRXBUSEFIELE (efficient bus) the input "
                         "E4ELE_PUB 0.3 where the tracked A2 output and the main copy's 26 January BAU_0.txt carry "
                         "E4DSL_PUB 0.243; the public passenger demand split (E6TDPASPUB, E6TDPASPRI) and the "
                         "transport group limits (Techs_*, TRMBS*, TRTAX*) follow from it. The tracked outputs "
                         "predate a transport edit of the workbooks",
    "Ecuador": "pre-patch hydro values: the tracked A2 NDCNEW and LTSNEW folders (and the B1 NDCNEW and LTSNEW "
               "built from them) were not recompiled after the 13 and 14 May A-O edits (patch_ao_ecuador_hydro.py, "
               "residual capacity, capacity factor and minimum capacity investment of the hydro and wind rows); "
               "BAU was",
}


JAM_B1_TRACKED = ("the tracked 12 May B1 files were written from the workbook with 764 blank formula values "
                  "(restored by the 9 November safe-save fix); the tracked NDCNEW folder holds BAU values with "
                  "Scenario label LTS (12 May, script not traced) where the runner writes a proper NDCNEW; the "
                  "tracked YearSplit rows carry the parameter name Yearsplit")
JAM_DATAFILE = ("the main copy's Jamaica data files are of 27 January (used by the 16 May Stage 3); "
                "TotalAnnualMinCapacityInvestment of PPPVT and PPWNDON in the workbook were edited on 12 May "
                "(JAM_AO_BAU_edits.xlsx, apply_ao_edits.py: BAU keeps only signed PPAs and awarded licences), "
                "and the PPPVT 2025 lower limit B1 derives from them")


def a2_rows():
    out = []
    for c, cand in A2C.items():
        d = pd.read_csv(JOB / "baseline" / c / "A2" / cand / "diff_rows.csv", dtype=str, keep_default_na=False)
        for r in d.itertuples():
            out.append(dict(country=c, scenario=r.scenario, file=r.file, key=r.key, kind=r.kind,
                            tracked_value=r.a, regenerated_value=r.b, overlay_source=r.source,
                            explanation=EXPL.get(c, "unexplained")))
    return out


def b1_rows():
    out = []
    for c, cand in B1C.items():
        base = JOB / "baseline" / c / "B1" / cand
        if not (base / "diff_rows.csv").exists():
            continue
        d = pd.read_csv(base / "diff_rows.csv", dtype=str, keep_default_na=False)
        for r in d.itertuples():
            ex = EXPL.get(c, "unexplained")
            if c == "Jamaica":
                ex = JAM_B1_TRACKED
            out.append(dict(country=c, scenario=r.scenario, compared="B1_Output_Params (tracked)", file=r.file,
                            key=r.key, kind=r.kind, reference_value=r.a, regenerated_value=r.b,
                            explanation=ex))
        d = pd.read_csv(base / "datafile_diff_rows.csv", dtype=str, keep_default_na=False)
        for r in d.itertuples():
            ex = JAM_DATAFILE if c == "Jamaica" else EXPL.get(c, "unexplained")
            out.append(dict(country=c, scenario=r.scenario, compared="Executables data file (main copy)",
                            file=r.param, key=r.key, kind=r.kind, reference_value=r.a, regenerated_value=r.b,
                            explanation=ex))
    return out


def commands():
    out = []
    for c in MODEL:
        a = json.loads((JOB / "baseline" / c / "A2" / A2C[c] / "summary.json").read_text())
        src = a["choice"]["NDCNEW"]["source"]
        a2cmd = f"cd {MODEL[c]} && python {'run_with_append_shim.py ' if 'shim' in a['command'] else ''}" \
                f"{a['command'].split()[-1]}"
        for scen in ["BAU", "NDCNEW", "LTSNEW"]:
            step = "compiler writes A2_Output_Params/BAU" if scen == "BAU" else \
                (f"copy the files the compiler writes to A2_Output_Params/{src} over A2_Output_Params/{scen} "
                 f"(other files left as they are)" if src != scen else
                 f"compiler writes A2_Output_Params/{scen} directly")
            if c == "Jamaica" and scen == "NDCNEW":
                step = "copy the files the compiler writes to A2_Output_Params/LTSNEW over A2_Output_Params/NDCNEW"
            out.append(dict(country=c, stage="A2", scenario=scen, interpreter="Anaconda Python 3.12.4, pandas 2.2.2",
                            command=a2cmd, extra_step=step,
                            driver=f"py -I _LAC_HUB/cost_write_run_20261111T071733Z/scripts/a2_driver.py {c}"
                                   + (" --shim" if "shim" in a["command"] else ""),
                            differing_values_vs_tracked=a["choice"][scen]["differing_rows"],
                            candidates_tried="python.org 3.12.0 + pandas 3.0.2 (cand1); Anaconda + pandas 2.2.2 "
                                             "(cand2, chosen); the second compiler file in the folder is byte "
                                             "identical", status="reproduced" if a["choice"][scen]["differing_rows"] == 0
                            else "reproduced except explained differences", seconds=a["seconds"]))
        bpath = JOB / "baseline" / c / "B1" / B1C[c] / "summary.json"
        if not bpath.exists():
            continue
        b = json.loads(bpath.read_text())
        for scen in ["BAU", "NDCNEW", "LTSNEW"]:
            n = b["b1_diffs"][scen]
            out.append(dict(country=c, stage="B1", scenario=scen, interpreter="Anaconda Python 3.12.4, pandas 2.2.2",
                            command=f"cd {MODEL[c]} && python {b['command'].split()[-1]}",
                            extra_step=("Executables/ created empty first; solver glpsol 4.65 on PATH"
                                        + ("; temporary A2_Output_Params/LTSOPT (copy of LTSNEW) and empty "
                                           "B1_Output_Params/LTSOPT for the LTSOPT scenario the config activates, "
                                           "removed after with every LTSOPT output" if c == "CostaRica" else "")),
                            driver=f"py -I _LAC_HUB/cost_write_run_20261111T071733Z/scripts/b1_driver.py {c}"
                                   + (" --temp-a2 LTSOPT=LTSNEW" if c == "CostaRica" else ""),
                            differing_values_vs_tracked=n,
                            candidates_tried=b.get("candidates", "one runner (the other file in the folder is "
                                                                 "byte identical or not a base runner)"),
                            status="reproduced" if n == 0 else "reproduced except explained differences",
                            seconds=b["seconds"]))
    return out


def write(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


if __name__ == "__main__":
    a = a2_rows()
    write(JOB / "baseline_A2_diff.csv", a, ["country", "scenario", "file", "key", "kind", "tracked_value",
                                             "regenerated_value", "overlay_source", "explanation"])
    b = b1_rows()
    write(JOB / "baseline_B1_diff.csv", b, ["country", "scenario", "compared", "file", "key", "kind",
                                             "reference_value", "regenerated_value", "explanation"])
    cmds = commands()
    write(JOB / "pipeline_commands.csv", cmds, ["country", "stage", "scenario", "interpreter", "command", "extra_step",
                                                 "driver", "differing_values_vs_tracked", "candidates_tried",
                                                 "status", "seconds"])
    print(len(a), "A2 diff rows;", len(b), "B1 diff rows;", len(cmds), "command rows")
    print(pd.DataFrame(a).groupby(["country", "scenario"]).size().to_string() if a else "")
    print(pd.DataFrame(b).groupby(["country", "compared", "scenario"]).size().to_string() if b else "")
