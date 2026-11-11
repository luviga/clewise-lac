"""Gates 1, 3, 5 and the em dash part of gate 7 (gates 2, 6 and git diff --check run in git)."""
import glob, json, os, re, subprocess, sys
import pandas as pd
sys.path.insert(0, ".")
from step1_scope import select

res = {}
# Gate 1: read-only
b, a = pd.read_csv("baseline_before.csv"), pd.read_csv("baseline_after.csv")
m = b.merge(a, on="file", how="outer", suffixes=("_before", "_after"))
diff = m[m.sha256_before != m.sha256_after]
res["gate1"] = {"result": "pass" if len(diff) == 0 and len(b) == len(a) else "fail", "files": len(b), "changed": len(diff)}

# Gate 3: sources
P = pd.read_csv("regional_proposals.csv", dtype=str)
S = pd.read_csv("sources.csv", dtype=str).fillna("")
ids = set(x for v in P.source_ids for x in v.split(";"))
missing = sorted(ids - set(S.source_id))
bad = []
for _, r in S.iterrows():
    if not re.match(r"^https?://", r.url): bad.append((r.source_id, "url"))
    if not r.page_or_table.strip(): bad.append((r.source_id, "locator"))
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", r.retrieval_date): bad.append((r.source_id, "retrieval_date"))
    if not os.path.isfile(os.path.join("downloads", r.downloaded_file)): bad.append((r.source_id, "file"))
    for col in S.columns:
        v = r[col]
        if re.search(r"[A-Za-z]:\\|/c/|\\\\|_LAC_HUB|MODELS_LAC|A-O_Parametrization|proposals_all|\.md\b|Dropbox|OneDrive", v):
            bad.append((r.source_id, f"internal reference in {col}"))
res["gate3"] = {"result": "pass" if not missing and not bad else "fail", "proposal_source_ids": len(ids), "missing_in_sources": missing,
                "sources": len(S), "problems": bad}

# Gate 5: coverage
d, s = select()
cov = []
for (c, t, p), g in P.groupby(["country", "Tech", "Parameter"]):
    want = set(s[(s.country == c) & (s.Tech == t) & (s.Parameter == p)].year)
    have = set(g.year)
    allyears = set(d[(d.fuel_scenario == "ALL") & (d.country == c) & (d.Tech == t) & (d.Parameter == p)].year)
    cov.append({"group": f"{c}|{t}|{p}", "scoped_years": len(want), "proposal_rows": len(g), "missing": sorted(want - have),
                "proposals_all_years_outside_scope": sorted(allyears - want), "duplicates": int(g.duplicated("year").sum())})
miss = [x for x in cov if x["missing"] or x["duplicates"]]
res["gate5"] = {"result": "pass" if not miss else "fail", "groups": len(cov), "rows": len(P), "groups_with_gaps": miss,
                "years_outside_scope": [x for x in cov if x["proposals_all_years_outside_scope"]]}

# Gate 7 (dash part): no em dash in any job file that will be tracked
EXT = (".md", ".csv", ".py", ".txt")
hits = []
for f in sorted(glob.glob("*")):
    if os.path.isfile(f) and f.endswith(EXT):
        txt = open(f, encoding="utf-8").read()
        if chr(0x2014) in txt:
            hits.append(f)
res["gate7_emdash"] = {"result": "pass" if not hits else "fail", "files_with_em_dash": hits}
json.dump(res, open("scratch/gates.json", "w"), indent=1)
print(json.dumps(res, indent=1)[:3000])
