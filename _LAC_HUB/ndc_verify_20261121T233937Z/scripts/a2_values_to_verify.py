"""Step A: build values_to_verify.csv from the scout tables.

Rules (brief 5A):
- every targets_ row cited by a class A or B row of proposed_scenario_changes.csv
  (same country, source id in the proposal's source list and a page in its page list);
- every targets_ row with a numeric value that states an emission target, a renewable
  share or a generation, capacity or retirement target, a vehicle share or number,
  a fuel blend, a grid loss target or an efficiency target (keyword rules below);
- the BAU and mitigation series of the NDC in force and of the long-term strategy
  (or the plan named by the NDC) from projections_.
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, SCOUT, CODES, COUNTRY, read_csv, write_csv, pages_of

NDC = {"CR": ["CR-01"], "DR": ["DR-01"], "ECU": ["ECU-01"], "GUA": ["GUA-01"], "HON": ["HON-01"], "JAM": ["JAM-01"]}
LTS = {"CR": ["CR-02", "CR-03"], "DR": ["DR-06"], "ECU": ["ECU-03"], "GUA": ["GUA-04"], "HON": [], "JAM": ["JAM-02"]}

KINDS = [
    ("emission", r"emisi|emission|ghg|gei|co2|carbon|neutral|removal|absorc|remocion|sink|reduction against|reducci[oó]n de emis"),
    ("renewable or generation", r"renewab|renovab|generation|generaci|clean share|limpi|coal|carb[oó]n|retire|retiro|phase.?out|hydro|solar|wind|e[oó]lic|geoterm|geotherm"),
    ("capacity", r"capacity|capacidad|\bmw\b|\bgw\b"),
    ("vehicle", r"vehic|fleet|flota|\bbus|train|tren|electric (car|vehic)|taxi|motorcycle|moto|sales|ventas|e-mobil|electromovil|zero-emission|cero emisi"),
    ("blend", r"blend|ethanol|etanol|biodiesel|biofuel|biocombust|\be10\b|mezcla|bioethanol"),
    ("grid loss", r"loss|p[eé]rdida|t&d"),
    ("efficiency", r"efficien|eficien|saving|saved|ahorro|intensity|intensidad"),
]
PROJ_EXCLUDE = r"histor|inventor|reference ghg|base year|common starting|estimadas al|common base|starting point"


def num(v):
    try:
        float(str(v).replace(",", ""))
        return True
    except ValueError:
        return False


def main():
    props = read_csv(os.path.join(SCOUT, "proposed_scenario_changes.csv"))
    cites = {}
    for p in props:
        if p["class"] not in ("A", "B"):
            continue
        code = [k for k, v in COUNTRY.items() if v == p["country"]][0]
        sids = [s.strip() for s in p["source_id"].split(";") if s.strip()]
        pgs = set(pages_of(p["page"]))
        cites.setdefault(code, []).append((sids, pgs, p["class"], p["scenario"], p["lever"]))
    out, counts, excluded = [], {}, []
    for code in CODES:
        n_t = n_p = 0
        for t in read_csv(os.path.join(SCOUT, f"targets_{code}.csv")):
            reasons = []
            tp = set(pages_of(t["page"]))
            for sids, pgs, cl, sc, lev in cites.get(code, []):
                if t["source_id"] in sids and tp & pgs:
                    r = f"cited by class {cl} proposal ({sc}, {lev})"
                    if r not in reasons:
                        reasons.append(r)
            text = " ".join([t["indicator"], t["description"], t["original_term"], t["unit"]]).lower()
            if num(t["value"]):
                for k, pat in KINDS:
                    if re.search(pat, text):
                        reasons.append(f"kind: {k}")
            if not reasons:
                excluded.append({"country": code, "target_id": t["target_id"], "source_id": t["source_id"],
                                 "indicator": t["indicator"], "value": t["value"], "unit": t["unit"],
                                 "numeric": num(t["value"])})
                continue
            role = "NDC in force" if t["source_id"] in NDC[code] else (
                "long-term strategy or plan" if t["source_id"] in LTS[code] else "other document")
            out.append({"value_id": t["target_id"], "country": code, "origin": f"targets_{code}.csv",
                        "source_id": t["source_id"], "document_role": role, "page": t["page"],
                        "table_or_figure": t["table_or_figure"], "sector": t["sector"],
                        "description": t["description"], "indicator": t["indicator"],
                        "scenario_as_named": "", "value": t["value"], "unit": t["unit"],
                        "year": t["target_year"], "conditionality": t["conditionality"],
                        "numeric": num(t["value"]), "why_included": "; ".join(reasons)})
            n_t += 1
        k = 0
        for r in read_csv(os.path.join(SCOUT, f"projections_{code}.csv")):
            k += 1
            if r["source_id"] not in NDC[code] + LTS[code]:
                continue
            if re.search(PROJ_EXCLUDE, r["scenario_as_named"].lower()):
                continue
            role = "NDC in force" if r["source_id"] in NDC[code] else "long-term strategy or plan"
            out.append({"value_id": f"{code}-P{k:03d}", "country": code, "origin": f"projections_{code}.csv line {k + 1}",
                        "source_id": r["source_id"], "document_role": role, "page": r["page"],
                        "table_or_figure": r["table_or_figure"], "sector": r["sector"],
                        "description": f"{r['scenario_as_named']}: {r['sector']} {r['gas']} emissions in {r['year']}",
                        "indicator": "projected emissions", "scenario_as_named": r["scenario_as_named"],
                        "value": r["value"], "unit": r["unit"], "year": r["year"], "conditionality": "",
                        "numeric": num(r["value"]), "why_included": "BAU or mitigation series of the NDC in force or long-term strategy"})
            n_p += 1
        counts[code] = (n_t, n_p)
    write_csv(os.path.join(JOB, "values_to_verify.csv"), out)
    write_csv(os.path.join(JOB, "parts", "values_not_selected.csv"), excluded)
    for c, (a, b) in counts.items():
        print(c, "targets", a, "projections", b, "total", a + b)
    print("total", len(out), "excluded targets", len(excluded))


if __name__ == "__main__":
    main()
