"""Step 3, fourth part: for every value check that is 'no' or 'not run', record the derivation and a likely cause
read from the derivation text (column cause). The cause is a reading of the derivation, not a verdict on the value."""
import re
import sys

sys.path.insert(0, ".")
from common import *  # noqa

V = pd.read_csv(out("value_checks.csv"), dtype=str, keep_default_na=False)
DER = {}
for cc in CCS:
    P = read(cc, "proposals.csv")
    for _, r in P.iterrows():
        DER.setdefault((cc, r["Tech"], r["Parameter"], r["year"]), r["derivation"])

RULES = [
    ("value is a sum of two published values (plant plus battery, or similar), not printed",
     r"(?i)plus ATB|plus the ATB|\+ battery|battery \d+ x ATB"),
    ("value is a mean of several published files (weekly, monthly or per-file prices), not printed in any one file",
     r"(?i)\bmean\b|average of|weeks|monthly|35 files|52 weekly"),
    ("year value built from a published anchor by an index or ratio path (ATB, IRENA decline, scaling), not printed",
     r"(?i)index|ratio|\(year y ?/|x ATB|ATB 20\d\d \w+ .*CAPEX\(y\)|path|scaled|times the ATB"),
    ("year value interpolated or held between published years, not printed",
     r"(?i)linear|interpolat|held (?:flat|at)|before 20\d\d take|values before"),
    ("value converted from the published one (currency year, units); the published input is in the note",
     r"(?i)CPI|x \d+\.\d+ /|/ 3\.6|x 0\.27778|deflat"),
    ("ASSUMPTION or rule value with no published number to search", r"(?i)ASSUMPTION|set to 0|see sentence|rule"),
]


def cause(der):
    for label, rx in RULES:
        if re.search(rx, der):
            return label
    return "not classified: the hub should open the file and locator"


ders, causes = [], []
for _, r in V.iterrows():
    y = r["year"].split("-")[0].split(" ")[0]
    d = DER.get((r["cc"], r["technology"], r["parameter"], y), "")
    if r["found"] == "yes":
        ders.append("")
        causes.append("")
        continue
    ders.append(d[:300])
    causes.append(cause(d) if d else ("price point: see note" if r["check_set"].startswith("fuel") else ""))
V["derivation_start"] = ders
V["likely_cause_if_not_found"] = causes
write(V, "value_checks.csv")
s = V[V["found"] != "yes"].groupby(["cc", "found", "likely_cause_if_not_found"]).size()
print(s.to_string())
