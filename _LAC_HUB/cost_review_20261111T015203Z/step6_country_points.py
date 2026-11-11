"""Step 6: evidence for the country points the hub asked about. Writes country_points.txt."""
import io
import re
import sys

import openpyxl

sys.path.insert(0, ".")
from common import *  # noqa

L = []


def p(*a):
    L.append(" ".join(str(x) for x in a))


def bau(cc, name):
    b = git("show", f"{BASE}:{ENERGY[cc]}/A2_Output_Params/BAU/{name}.csv", binary=True)
    return pd.read_csv(io.BytesIO(b), dtype=str, keep_default_na=False)


# ---------------- Costa Rica ----------------
p("## Costa Rica")
cc = "cr"
wb = openpyxl.load_workbook(os.path.join(SCRATCH, "AO_cr.xlsx"), read_only=True, data_only=True)
hits = []
for sh in ["Primary Techs", "Secondary Techs"]:
    it = wb[sh].iter_rows(values_only=True)
    hdr = list(next(it))
    for r in it:
        d = dict(zip(hdr, r))
        t = str(d.get("Tech") or "")
        if re.search(r"IMP.*ELE|ELE.*IMP", t, re.I):
            hits.append((sh, d.get("Tech.ID"), t, d.get("Tech.Name"), d.get("Parameter"), d.get("Projection.Mode"),
                         d.get(2021), d.get(2024), d.get(2025), d.get(2050)))
p(f"A-O at 2ddd560, Primary and Secondary Techs, rows whose Tech matches IMP..ELE: {len(hits)}")
for h in hits:
    p("  ", " | ".join(str(x) for x in h))
for name in ["OutputActivityRatio", "InputActivityRatio", "TotalTechnologyAnnualActivityUpperLimit",
             "TotalTechnologyAnnualActivityLowerLimit", "ResidualCapacity", "TotalAnnualMaxCapacity",
             "TotalAnnualMaxCapacityInvestment", "CapitalCost", "FixedCost", "VariableCost"]:
    try:
        d = bau(cc, name)
    except RuntimeError:
        p(f"  BAU {name}.csv: file absent")
        continue
    q = d[d["TECHNOLOGY"] == "IMPELE"]
    vals = sorted(set(q["Value"]), key=lambda x: num(x) or 0)
    extra = f", FUEL {sorted(set(q['FUEL']))}" if "FUEL" in q.columns and len(q) else ""
    p(f"  BAU {name}.csv: {len(q)} IMPELE rows{extra}; values {vals[:6]}")
p("Commit 7e8dd76 'price electricity imports (IMPELE)':", git("show", "--stat", "--format=%h %an %ad", "7e8dd76").splitlines()[-1].strip())
P = read(cc, "proposals.csv")
q = P[P["Tech"] == "IMPELE"]
p(f"  proposals.csv IMPELE rows: {len(q)}; parameters {sorted(set(q['Parameter']))}; years {q['year'].min()}-{q['year'].max()}; "
  f"basis {q['basis_class'].value_counts().to_dict()}; proposed values {sorted(set(q['proposed_value']))}; current values {sorted(set(q['current_value']))}")
p("  derivation:", q.iloc[0]["derivation"][:400])
S = read(cc, "structure_proposals.csv")
p(f"structure_proposals.csv: {len(S)} rows")
for _, r in S.iterrows():
    p(f"  [{r['status']}] {r['file'].split('/')[-1]} {r['sheet']} {r['row_identifiers']} col {r['column']}: "
      f"{r['current_value']} -> {r['proposed_value']}; balance: {r['balance_page']}")

# ---------------- Ecuador ----------------
p("\n## Ecuador")
cc = "ecu"
C = read(cc, "cost_rows_current.csv")
P = read(cc, "proposals.csv")
years = [c for c in C.columns if re.fullmatch(r"20\d\d", c)]
ones = []
for _, r in C.iterrows():
    for y in years:
        if num(r[y]) == 1.0:
            ones.append((r["sheet"], r["Tech"], r["Parameter"], y))
idx = {(r["sheet"], r["Tech"], r["Parameter"], r["year"]): r for _, r in P.iterrows()}
idx2 = {}
for _, r in P.iterrows():
    idx2.setdefault((r["Tech"], r["Parameter"], r["year"]), []).append(r["proposed_value"])
missing, still1 = [], []
for (sh, t, prm, y) in ones:
    v = idx2.get((t, prm, y))
    if v is None:
        missing.append(f"{t}/{prm}/{y}")
    elif any(num(x) == 1.0 for x in v):
        still1.append(f"{t}/{prm}/{y}")
p(f"cost_rows_current.csv cells equal to 1: {len(ones)} on {len({(a, b, c) for a, b, c, _ in ones})} rows; "
  f"with no proposal: {len(missing)}; with a proposal still equal to 1: {len(still1)}")
if missing:
    miss_rows = sorted({m.rsplit('/', 1)[0] for m in missing})
    p("  rows with no proposal:", "; ".join(miss_rows[:40]))
if still1:
    p("  still 1:", "; ".join(still1[:20]))
PC = read(cc, "plant_costs.csv")
f25 = PC[PC["flag_over_25pct"].str.lower().isin(["yes", "true", "1", "y"])]
pairs = f25.groupby(["technology", "parameter"]).agg(
    years=("year", lambda s: f"{min(s)}-{max(s)}"), proposed_2024=("proposed_value", "first"),
    planmicc=("planmicc_value", "first"), code=("planmicc_code", "first"), diff=("diff_vs_planmicc_pct", "first")).reset_index()
p(f"plant_costs.csv rows flagged over 25 percent against PLANMICC: {len(f25)} cells, {len(pairs)} technology-parameter pairs")
for _, r in pairs.iterrows():
    v24 = PC[(PC["technology"] == r["technology"]) & (PC["parameter"] == r["parameter"]) & (PC["year"] == "2024")]
    pv = v24.iloc[0]["proposed_value"] if len(v24) else r["proposed_2024"]
    pm = v24.iloc[0]["planmicc_value"] if len(v24) else r["planmicc"]
    dd = v24.iloc[0]["diff_vs_planmicc_pct"] if len(v24) else r["diff"]
    p(f"  {r['technology']} {r['parameter']}: proposed 2024 {pv} vs PLANMICC {pm} ({r['code']}), diff {dd} percent")
ccg = P[(P["Parameter"].isin(["CapitalCost", "FixedCost"])) & P["source_ids"].str.contains("CCG-002") & P["Tech"].str.startswith("PP")]
ccg_t = sorted(set(ccg["Tech"]))
vc = P[(P["Parameter"] == "VariableCost") & P["Tech"].isin(ccg_t)]
non0 = vc[vc["proposed_value"].map(num) != 0]
p(f"plants with CapitalCost or FixedCost from the CCG kit (CCG-002): {len(ccg_t)}: {', '.join(ccg_t)}")
p(f"  their VariableCost cells: {len(vc)}; not 0: {len(non0)}" + (f" ({sorted(set(non0['Tech']))})" if len(non0) else ""))

# ---------------- Guatemala ----------------
p("\n## Guatemala")
cc = "gua"
P = read(cc, "proposals.csv")
u = P[P["change_class"] == "unit_fix"]
p(f"unit_fix rows: {len(u)} on {sorted(set(u['Tech']))}, parameter {sorted(set(u['Parameter']))}")
for t, g in u.groupby("Tech"):
    r = g.iloc[0]
    p(f"  {t}: current {r['current_value']} -> proposed {r['proposed_value']}; sources {r['source_ids']}; derivation: {r['derivation']}")
for fn in ["GAPS_*.md", "REPORT_*.md"]:
    tx = text(cc, fn)
    for para in re.split(r"\n\s*\n", tx):
        if re.search(r"(?i)USD/kWh|unit slip|unit evidence|277\.78|kWh", para) and re.search(r"(?i)variable", para):
            p(f"  [{fn.split('_')[0]}] " + " ".join(para.split())[:1500])

# ---------------- Honduras ----------------
p("\n## Honduras")
cc = "hon"
C = read(cc, "cost_rows_current.csv")
P = read(cc, "proposals.csv")
imp = C[C["Tech"] == "IMP_ELE"]
years = [c for c in C.columns if re.fullmatch(r"20\d\d", c)]
for _, r in imp.iterrows():
    nn = [y for y in years if num(r[y]) == 99999]
    p(f"cost_rows_current IMP_ELE {r['Parameter']} ({r['Projection.Mode']}): 99999 in {len(nn)} years {nn[0] + '-' + nn[-1] if nn else ''}; "
      f"2018 {r['2018']}, 2024 {r['2024']}, 2029 {r['2029']}, 2030 {r['2030']}")
    q = P[(P["Tech"] == "IMP_ELE") & (P["Parameter"] == r["Parameter"]) & P["year"].isin(nn)]
    changed = q[q["proposed_value"].map(num) != 99999]
    p(f"  proposals.csv rows in those years: {len(q)}; of which proposed value differs from 99999: {len(changed)}")
q = P[P["Tech"] == "IMP_ELE"]
p(f"proposals.csv IMP_ELE rows: {len(q)}; by parameter and year: " +
  "; ".join(f"{prm} {g['year'].min()}-{g['year'].max()} ({len(g)})" for prm, g in q.groupby("Parameter")))
# check against the A-O itself
wb = openpyxl.load_workbook(os.path.join(SCRATCH, "AO_hon.xlsx"), read_only=True, data_only=True)
for sh in ["Primary Techs", "Secondary Techs"]:
    it = wb[sh].iter_rows(values_only=True)
    hdr = list(next(it))
    for r in it:
        d = dict(zip(hdr, r))
        if d.get("Tech") == "IMP_ELE" and d.get("Parameter") in ("VariableCost", "FixedCost", "CapitalCost"):
            nn = [y for y in hdr if isinstance(y, int) and d.get(y) == 99999]
            p(f"  A-O {sh} IMP_ELE {d['Parameter']} mode {d.get('Projection.Mode')}: 99999 in {nn[:1]}..{nn[-1:]} ({len(nn)} years); 2018 {d.get(2018)}, 2024 {d.get(2024)}")

# ---------------- Jamaica ----------------
p("\n## Jamaica")
cc = "jam"
PP = read(cc, "price_points_2024.csv")
for _, r in PP[PP["source_ids"].str.contains("JAM", na=False) & PP["page_or_table"].str.contains("(?i)petrojam|ex-refinery", na=False)].iterrows():
    p(f"  price point {r['row']} {r['price_point']} chosen={r['chosen']} {r['value_usd_per_gj']} USD/GJ; tax: {r['tax_treatment']}; {r['page_or_table'][:120]}")
for fn in ["GAPS_*.md", "REPORT_*.md"]:
    tx = text(cc, fn)
    for para in re.split(r"\n\s*\n", tx):
        if re.search(r"(?i)petrojam", para) and re.search(r"(?i)tax|SCT|pre-tax|excise", para):
            p(f"  [{fn.split('_')[0]}] " + " ".join(para.split())[:1500])
# cost_rows_current against the A-O at 2ddd560
C = read(cc, "cost_rows_current.csv")
wb = openpyxl.load_workbook(os.path.join(SCRATCH, "AO_jam.xlsx"), read_only=True, data_only=True)
ao = {}
for sh in ["Primary Techs", "Secondary Techs"]:
    it = wb[sh].iter_rows(values_only=True)
    hdr = list(next(it))
    for r in it:
        d = dict(zip(hdr, r))
        if d.get("Parameter") in ("CapitalCost", "FixedCost", "VariableCost"):
            ao[(sh, str(d["Tech"]), d["Parameter"])] = d
years = [c for c in C.columns if re.fullmatch(r"20\d\d", c)]
nrow, ncell, diff, absent = 0, 0, [], []
for _, r in C.iterrows():
    k = (r["sheet"], r["Tech"], r["Parameter"])
    if k not in ao:
        absent.append(k)
        continue
    nrow += 1
    for y in years:
        a = ao[k].get(int(y))
        b = num(r[y])
        ncell += 1
        if (a in (None, "") and b is None):
            continue
        if a in (None, "") or b is None or abs(float(a) - b) > 1e-6 * max(1, abs(b)):
            diff.append(f"{k[1]}/{k[2]}/{y}: csv {r[y]} A-O {a}")
p(f"cost_rows_current.csv vs A-O at 2ddd560 (cached values): {nrow} rows, {ncell} cells compared, {len(diff)} differ, {len(absent)} rows not in the A-O")
for x in diff[:15]:
    p("   ", x)
p(f"A-O cost rows not in cost_rows_current.csv: {len(set(ao) - {(r['sheet'], r['Tech'], r['Parameter']) for _, r in C.iterrows()})}")

# ---------------- Dominican Republic ----------------
p("\n## Dominican Republic")
cc = "dr"
PP = read(cc, "price_points_2024.csv")
for row in ["DIST_GSL", "DIST_LPG"]:
    for _, r in PP[PP["row"] == row].iterrows():
        p(f"  {row} {r['price_point']} chosen={r['chosen']} net {r['value_usd_per_gj_net']} USD/GJ; diff {r['diff_vs_chosen_pct']} percent; "
          f"LAC_LOCAL_PRICES row {r['lac_local_prices_row']}; evidence {r['evidence_class']}; tax {r['tax_treatment'][:60]}")
P = read(cc, "proposals.csv")
for row in ["DIST_GSL", "DIST_LPG"]:
    q = P[(P["Tech"] == row) & (P["year"] == "2024")]
    p(f"  proposals {row} 2024: " + "; ".join(f"{r['fuel_scenario']} {r['proposed_value']} ({r['basis_class']})" for _, r in q.iterrows()))

with open(out("country_points.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(x.rstrip() for x in L) + "\n")
print("\n".join(L))
