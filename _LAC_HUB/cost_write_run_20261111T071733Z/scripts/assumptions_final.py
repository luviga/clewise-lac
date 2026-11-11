"""C5: assumptions_final.csv, every written row with an ASSUMPTION sentence, D7 applied.

D7: the gas sentence ("... converted to the models' net basis by dividing by 0.9 ...") is removed
from the Jamaica and Dominican Republic natural gas rows (DIST_NGS) whose value was never divided
(LNG import CIF per tonne / IPCC NCV, already net; review pack REPORT, Gas conversion). Text only.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

HUB = Path(r"C:\clw_overnight\_LAC_HUB")
JOB = HUB / "cost_write_run_20261111T071733Z"
GAS_START = "ASSUMPTION: natural gas prices published per MMBtu are on a gross calorific basis"


def strip_gas(sentence: str) -> tuple[str, bool]:
    i = sentence.find(GAS_START)
    if i == -1:
        return sentence, False
    # the F5 block runs to the end of its "Range:" sentence
    j = sentence.find("ASSUMPTION:", i + len(GAS_START))
    rest = sentence[j:] if j != -1 else ""
    return (sentence[:i] + rest).strip(), True


def main():
    P = pd.read_csv(HUB / "cost_review_20261111T015203Z" / "proposals_all.csv", dtype=str, keep_default_na=False)
    R = pd.read_csv(HUB / "cost_regional_20261111T050439Z" / "regional_proposals.csv", dtype=str,
                    keep_default_na=False)
    P = P[P.fuel_scenario.isin(["ALL", "STEPS"])]
    sent = {(r.country, r.sheet, r.Tech, r.Parameter, int(r.year)): r.assumption_sentence for r in P.itertuples()}
    for r in R.itertuples():
        sent[(r.country, r.sheet, r.Tech, r.Parameter, int(r.year))] = r.assumption_sentence
    W = pd.read_csv(JOB / "write_set.csv", dtype=str, keep_default_na=False)
    out = []
    n_d7 = 0
    for w in W.itertuples():
        k = (w.country, w.sheet, w.tech, w.parameter, int(w.year))
        s = sent.get(k, "")
        if w.rule == "D4":
            src = "DIST_CRU" if w.tech == "EXTT_CRU" else "DIST_COA"
            s = sent.get((w.country, w.sheet, src, w.parameter, int(w.year)), "")
        if "ASSUMPTION" not in s:
            continue
        final, d7 = s, False
        if w.country in ("Jamaica", "DominicanRepublic") and w.tech == "DIST_NGS":
            final, d7 = strip_gas(s)
            n_d7 += d7
        out.append(dict(country=w.country, sheet=w.sheet, tech=w.tech, parameter=w.parameter, year=w.year,
                        fuel_scenario=w.fuel_scenario, value_written=w.value_to_write, rule=w.rule,
                        source_ids=w.source_ids, assumption_sentence=final,
                        d7=("gas sentence removed: value never divided by 0.9 (already net)" if d7 else "")))
    with open(JOB / "assumptions_final.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(out[0].keys()), lineterminator="\n")
        wr.writeheader()
        for o in out:
            wr.writerow(o)
    df = pd.DataFrame(out)
    print(len(out), "rows with an ASSUMPTION sentence;", n_d7, "D7 removals")
    print(df.groupby("country").size().to_string())
    print("rows left without a sentence after D7:", (df.assumption_sentence == "").sum())


if __name__ == "__main__":
    main()
