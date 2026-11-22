"""Step E: scenario_values.csv and scenario_values_held_back.csv.

NDC rows: values of the NDC in force and of the plans it cites by name (HON-08 PIEG cited in
HON-01 p.26; JAM-07 IRP-2 cited in JAM-01 p.5; ECU-07 PME cited in ECU-01 p.14 and p.102).
LTS rows: the long-term strategy submitted to the UNFCCC (CR-02 and CR-03, GUA-04, JAM-02); where none
is submitted and the NDC names a national long-term plan, that plan, marked 'plan named by the NDC'
(DR-06 END 2030 named in DR-01 p.9 and p.26; ECU-03 PLANMICC named in ECU-01 p.10 and p.33);
Honduras has neither: one row 'no published long-term value'.
Only rows with status '3 of 3' or '2 of 3'. Conflicts, rows without a stated year and rows without a
number go to the held-back file with the reason. BAU projections are reference values, not NDC or LTS
values: they stay in verification_<code>.csv and are not written here.
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, CODES, COUNTRY, read_csv, write_csv

NDC_DOCS = {"CR": ["CR-01"], "DR": ["DR-01"], "ECU": ["ECU-01", "ECU-07"], "GUA": ["GUA-01"], "HON": ["HON-01", "HON-08"], "JAM": ["JAM-01", "JAM-07"]}
LTS_DOCS = {"CR": ["CR-02", "CR-03"], "GUA": ["GUA-04"], "JAM": ["JAM-02"]}
PLAN_DOCS = {"DR": ["DR-06"], "ECU": ["ECU-03"]}
CITED = {"ECU-07": "plan cited by the NDC (ECU-01 p.14, p.102)", "HON-08": "plan cited by the NDC (HON-01 p.26)",
         "JAM-07": "plan cited by the NDC (JAM-01 p.5)"}

units = {r["unit"]: r for r in read_csv(os.path.join(JOB, "units.csv"))}
comp = {r["value_id"]: r for r in read_csv(os.path.join(JOB, "model_comparison.csv"))}
vals = {r["value_id"]: r for r in read_csv(os.path.join(JOB, "values_to_verify.csv"))}


def lever(v, kind):
    t = (v["indicator"] + " " + v["description"]).lower()
    sec = v["sector"]
    if kind == "share of generation":
        return "renewable share of generation"
    if kind == "capacity":
        return "power plant capacity: " + v["indicator"]
    if kind == "emissions":
        if "economy-wide" in sec.lower():
            return "economy-wide emissions: " + v["indicator"]
        return f"{sec} emissions: " + v["indicator"]
    if kind == "vehicles":
        return "vehicle fleet: " + v["indicator"]
    if kind == "blend":
        return "fuel blend: " + v["indicator"]
    if kind == "losses":
        return "grid losses: " + v["indicator"]
    if kind == "efficiency":
        return "efficiency: " + v["indicator"]
    return v["indicator"]


def main():
    out, held = [], []
    for code in CODES:
        has_lts = False
        for r in read_csv(os.path.join(JOB, f"verification_{code}.csv")):
            v = vals[r["value_id"]]
            sid = v["source_id"]
            if sid in NDC_DOCS[code]:
                scen, basis = "NDC", ("NDC in force" if sid == NDC_DOCS[code][0] else CITED[sid])
            elif sid in LTS_DOCS.get(code, []):
                scen, basis = "LTS", "long-term strategy submitted to the UNFCCC"
            elif sid in PLAN_DOCS.get(code, []):
                scen, basis = "LTS", "plan named by the NDC"
            else:
                if r["status"] == "conflict":
                    held.append({"country": COUNTRY[code], "scenario": "none (document is neither the NDC in force nor the long-term strategy)",
                                 "lever": v["indicator"], "kind_of_quantity": comp[r["value_id"]]["kind"], "year": v["year"],
                                 "source_id": sid, "page": v["page"], "check_status": r["status"], "value_printed": v["value"],
                                 "unit_printed": v["unit"], "value_id": r["value_id"], "reason": "conflict: " + r["status_note"]})
                continue
            if v["origin"].startswith("projections") and re.search(r"bau|tendencial|base case|baseline|business", v["scenario_as_named"].lower()):
                continue
            c = comp[r["value_id"]]
            base = {"country": COUNTRY[code], "scenario": scen, "lever": lever(v, c["kind"]), "kind_of_quantity": c["kind"],
                    "year": v["year"], "source_id": sid, "page": v["page"], "check_status": r["status"],
                    "value_printed": v["value"], "unit_printed": v["unit"], "value_id": r["value_id"]}
            reason = ""
            if r["status"] == "conflict":
                reason = "conflict: " + r["status_note"]
            elif not re.search(r"(19|20)\d\d", v["year"] or ""):
                reason = "no year stated in the document"
            elif v["numeric"] == "False":
                reason = "no number stated (verbal target only)"
            if reason:
                held.append(dict(base, reason=reason))
                continue
            u = units.get(v["unit"])
            try:
                std_v = round(float(r["settled_value"]) * float(u["factor"]), 6)
            except (TypeError, ValueError):
                std_v = ""
            cond = v["conditionality"] or "not stated"
            note = [basis]
            if r["verbal_target"] == "yes":
                note.append("verbal target; the number encodes the wording: " + r["third_reading_value"])
            if v["scenario_as_named"]:
                note.append("projected series: " + v["scenario_as_named"])
            if "range" in v["unit"]:
                note.append("printed as a range")
            if r["status"] == "2 of 3":
                note.append(r["status_note"])
            out.append(dict(base, value_standard=std_v, unit_standard=u["standard_unit"] if u else "",
                            conditionality=cond if cond in ("conditional", "unconditional", "not stated") else cond,
                            model_quantity=c["model_quantity"] or "none", same_kind=c["same_kind"],
                            note="; ".join(note), description=v["description"]))
            if scen == "LTS":
                has_lts = True
        if not has_lts:
            out.append({"country": COUNTRY[code], "scenario": "LTS", "lever": "all", "kind_of_quantity": "",
                        "year": "", "value_standard": "", "unit_standard": "", "value_printed": "", "unit_printed": "",
                        "source_id": "HON-01", "page": "p.14;p.15", "check_status": "", "conditionality": "",
                        "model_quantity": "", "same_kind": "", "value_id": "",
                        "note": "no published long-term value: the NDC 3.0 says the long-term strategy (ENDRCH) is being consolidated and has not been submitted, and names no other national long-term plan with values",
                        "description": ""})
    fields = ["country", "scenario", "lever", "kind_of_quantity", "year", "value_standard", "unit_standard", "value_printed",
              "unit_printed", "source_id", "page", "check_status", "conditionality", "model_quantity", "same_kind", "note",
              "description", "value_id"]
    write_csv(os.path.join(JOB, "scenario_values.csv"), out, fields)
    write_csv(os.path.join(JOB, "scenario_values_held_back.csv"), held)
    import collections
    print("rows", len(out), collections.Counter((r["country"], r["scenario"]) for r in out))
    print("held back", len(held), collections.Counter(r["reason"].split(":")[0] for r in held))


if __name__ == "__main__":
    main()
