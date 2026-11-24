"""
Stage 3 emission cap step: yearly energy emission limits of the scenarios that carry an
energy_emission_reduction_vs_bau row in inputs/scenarios/scenario_values.csv, built from the solved BAU and NDC
results of the same run, then the capped scenario is solved again.

Rule (values from the tables; this file holds the rule only):
  E_from  = solved NDC energy emissions in cap_from_year (stage_controller.csv)
  E_to    = solved BAU energy emissions in cap_target_year times (1 - r), r from scenario_values.csv
  cap(y)  = E_from + (E_to - E_from) * (y - cap_from_year) / (cap_target_year - cap_from_year),
            for y from cap_start_year to cap_target_year
on each label of group energy_cap of config/scenarios/emission_labels.csv for the country (one label: the
emissions of the fuels supplied to the energy system), written through AnnualEmissionLimit into the
{scenario}_FINAL_0 data file. Stage 3 apply has already released the power plant share pins of that scenario
from cap_start_year (frozen output and committed builds keep their lower limits).

Run after stage3_run_all.bat and before stage3_results.py:
    py stage3_emission_cap.py --root .
Writes _STAGE3_RESULTS/EMISSION_CAPS.csv (country, scenario, label, year, cap and its inputs).
"""
import argparse
import csv
import os
import subprocess
from pathlib import Path

import lac_tables as LT
import scenario_rules as SR
from stage3_results import parse_glpk_output

LEVER = "energy_emission_reduction_vs_bau"


def solved_emissions(out_file, region, labels):
    res = parse_glpk_output(Path(out_file), ["AnnualEmissions"])["AnnualEmissions"]
    out = {}
    for idx, v in res:
        if len(idx) == 3 and idx[0] == region and idx[1] in labels:
            out[(idx[1], int(idx[2]))] = out.get((idx[1], int(idx[2])), 0.0) + v
    return out


def status_of(out_file):
    with open(out_file, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("Status:"):
                return line.split(":", 1)[1].strip()
    return "NO OUTPUT"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--glpsol", default="glpsol")
    ap.add_argument("--no-solve", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    y_from = LT.controller("cap_from_year", "3")
    y_start = LT.controller("cap_start_year", "3")
    y_to = LT.controller("cap_target_year", "3")
    base, ndc = LT.scenario("base"), LT.scenario("ndc")
    runs = {lab: (m, d, o) for lab, m, d, o in LT.solver_runs("FINAL")}
    rows = []
    for r in LT._value_rows():
        if r["lever"] != LEVER:
            continue
        c, sc, red = r["country"], r["scenario"], float(r["value"])
        region = LT.country_value(c, "code")
        labels = LT.emissions("energy_cap", c)
        lab = {s: f"{c} {s}_FINAL" for s in (base, ndc, sc)}
        if any(lab[s] not in runs for s in lab):
            print(f"[SKIP] {c} {sc}: a data file of {sorted(lab.values())} is missing")
            continue
        e_base = solved_emissions(root / runs[lab[base]][2], region, labels)
        e_ndc = solved_emissions(root / runs[lab[ndc]][2], region, labels)
        caps = {}
        for e in labels:
            e1 = e_ndc.get((e, y_from), 0.0)
            e2 = e_base.get((e, y_to), 0.0) * (1.0 - red)
            for y in range(y_start, y_to + 1):
                v = e1 + (e2 - e1) * (y - y_from) / (y_to - y_from)
                caps.setdefault(e, {})[y] = round(v, 6)
                rows.append([c, sc, e, y, round(v, 6), r.get("value_id", ""), red, round(e1, 6),
                             round(e_base.get((e, y_to), 0.0), 6), round(e2, 6)])
        data = root / runs[lab[sc]][1]
        with open(data, "r", encoding="utf-8", errors="replace", newline="") as fh:
            content = fh.read()
        crlf = "\r\n" in content
        content = content.replace("\r\n", "\n")
        yrs = SR.years_of(content)
        # data files written by Stage 3 hold no AnnualEmissionLimit rows of these labels; the cap years are set,
        # the others keep the block default
        content, n = SR.set_rows(content, "AnnualEmissionLimit", caps, yrs, SR.region_of(content))
        if crlf:
            content = content.replace("\n", "\r\n")
        with open(data, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
        print(f"{c} {sc}: {n} cap values on {labels}, {y_start}-{y_to}; "
              f"{y_from} NDC {e1:.4f}, {y_to} BAU x (1 - {red}) = {e2:.4f}")
        if not a.no_solve:
            m, d, o = runs[lab[sc]]
            subprocess.run([a.glpsol, "-m", m, "-d", d, "-o", o], cwd=root, check=False,
                           stdout=subprocess.DEVNULL)
            print(f"  solved again: {status_of(root / o)}")
    out = root / "_STAGE3_RESULTS" / "EMISSION_CAPS.csv"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["country", "scenario", "emission", "year", "cap", "value_id", "r", "ndc_from_year_emissions",
                    "bau_target_year_emissions", "target_year_cap"])
        w.writerows(rows)
    print(f"[Wrote] {out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
