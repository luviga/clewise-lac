"""Step 8 (outputs): writes REPORT, GAPS and CHANGES of the review pack from the CSVs of steps 1 to 7
and the hand-written text in report_text.py."""
import re
import sys

sys.path.insert(0, ".")
from common import *  # noqa
import report_text as RT

ORDER = ["ecu", "cr", "jam", "dr", "gua", "hon"]
G = pd.read_csv(out("gates.csv"), dtype=str, keep_default_na=False)
INV = pd.read_csv(out("inventory.csv"), dtype=str, keep_default_na=False)
V = pd.read_csv(out("value_checks.csv"), dtype=str, keep_default_na=False)
F = pd.read_csv(out("review_flags.csv"), dtype=str, keep_default_na=False)
X = pd.read_csv(out("cross_country.csv"), dtype=str, keep_default_na=False)
DR = pd.read_csv(out("decisions_raised.csv"), dtype=str, keep_default_na=False)
RS = pd.read_csv(out("derivation_recompute_summary.csv"), dtype=str, keep_default_na=False)
RC = pd.read_csv(out("derivation_recompute.csv"), dtype=str, keep_default_na=False)


def md_table(df):
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(str(r[c]).replace("|", "/").replace("\n", " ") for c in cols) + " |")
    return "\n".join(lines)


def fmt(x, d=2):
    v = num(x)
    return "" if v is None else f"{v:,.{d}f}"


L = []
w = L.append
w(f"# REPORT LAC_COST_REVIEW_PACK {STAMP}")
w("")
w("Checked review pack for the six country cost jobs (draft pull requests 2 to 7 of luviga/clewise-lac). "
  "Everything below was rerun or re-read in this job from the fetched branches, the local `downloads/` folders "
  "and the A-O workbooks at `2ddd560`. Counts are of what was checked; a check that could not run says so. "
  "No proposal, model file, branch or job folder of the six was changed.")
w("")
w("## 1. Pull request")
w("")
w(RT.PR_BLOCK)
w("")
# ---- 2. country table
w("## 2. The six jobs at a glance")
w("")
rows = []
for cc in ORDER:
    inv = INV[INV["cc"] == cc].iloc[0]
    g = G[G["cc"] == cc].sort_values("gate", key=lambda s: s.astype(int))
    gates = " ".join(f"{r['gate']}:{r['result']}" for _, r in g.iterrows())
    P = read(cc, "proposals.csv")
    v = V[V["cc"] == cc]
    fl = F[F["cc"] == cc]["severity"].value_counts()
    rows.append({"Country": COUNTRY[cc], "PR": f"#{inv['pr']}", "Head": inv["head"][:7],
                 "Commits": inv["commits_since_2ddd560"], "Gates 1 to 8": gates,
                 "Proposal rows": f"{len(P):,}", "ASSUMPTION rows": f"{(P['basis_class'] == 'ASSUMPTION').sum():,}",
                 "Value checks found / not found / not run": f"{(v['found'] == 'yes').sum()} / {(v['found'] == 'no').sum()} / {(v['found'] == 'not run').sum()}",
                 "Flags high / medium / low": f"{fl.get('high', 0)} / {fl.get('medium', 0)} / {fl.get('low', 0)}"})
w(md_table(pd.DataFrame(rows)))
w("")
w(RT.TABLE_NOTES)
w("")
w("Gate failures and notes:")
w("")
for _, r in G[(G["result"] != "pass") | (G["note"].str.strip() != "")].iterrows():
    w(f"- {COUNTRY[r['cc']]}, gate {r['gate']} ({r['check']}): {r['result']}. {r['count']}. {r['note'].strip()}")
w("")
w("Value checks by set (found / not found / not run):")
w("")
vs = V.groupby(["cc", "check_set"])["found"].value_counts().unstack(fill_value=0)
vrows = []
for (cc, cs), r in vs.iterrows():
    vrows.append({"Country": COUNTRY[cc], "Set": cs, "Found": r.get("yes", 0), "Not found": r.get("no", 0), "Not run": r.get("not run", 0)})
vr = pd.DataFrame(vrows)
vr["o"] = vr["Country"].map({COUNTRY[c]: i for i, c in enumerate(ORDER)})
w(md_table(vr.sort_values(["o", "Set"]).drop(columns="o")))
w("")
w("Derivations recomputed from their stated inputs:")
w("")
rs = RS.copy()
rs["Country"] = rs["cc"].map(COUNTRY)
w(md_table(rs[["Country", "distinct_derivations", "expressions_recomputed", "equal_after_unit_scale_1000", "over_0_5pct",
               "projected_series_checked", "series_off_path"]].rename(columns={
    "distinct_derivations": "Distinct derivations", "expressions_recomputed": "Expressions recomputed",
    "equal_after_unit_scale_1000": "Equal after x1000 unit step", "over_0_5pct": "Above 0.5 percent (parser)",
    "projected_series_checked": "Projected fuel series checked", "series_off_path": "Off the WEO path"})))
w("")
w(RT.RECOMPUTE_NOTE.format(n=len(RC), m=RC["hand_review"].str.contains("matches").sum()))
w("")
# ---- 3. cross-country
w("## 3. Cross-country: shared inputs")
w("")
weo = X[X["item"] == "WEO 2025 Table 2.3"].copy()
cols = ["key", "published_value"] + [COUNTRY[c] for c in ORDER] + ["agree"]
weo = weo[cols].rename(columns={"key": "Series and year", "published_value": "Table 2.3 value", "agree": "Agree"})
w(md_table(weo))
w("")
w(RT.CROSS_TEXT)
w("")
gas = X[X["item"] == "gas conversion"]
w("Gas conversion, row by row:")
w("")
for _, r in gas.iterrows():
    val = next((r[COUNTRY[c]] for c in ORDER if r[COUNTRY[c]]), "")
    w(f"- {r['key']}: {val}. Agree: {r['agree']}. {r['note']}")
w("")
# ---- 4. per country
w("## 4. Country by country")
w("")
for cc in ORDER:
    w(f"### {COUNTRY[cc]}")
    w("")
    PP = read(cc, "price_points_2024.csv")
    P = read(cc, "proposals.csv")
    Fp = read(cc, "fuel_prices.csv")
    vcol = [c for c in Fp.columns if c.startswith("value_usd_per_gj")][0]
    fuel_rows = list(dict.fromkeys(Fp["row"]))
    t = []
    for row in fuel_rows:
        ch = PP[(PP["row"] == row) & (PP["chosen"] == "yes")]
        pt = ch["price_point"].iloc[0] if len(ch) else "(none in price_points_2024)"

        def pv(y, s):
            q = P[(P["Tech"] == row) & (P["Parameter"] == "VariableCost") & (P["year"] == y) & (P["fuel_scenario"] == s)]
            return q.iloc[0] if len(q) else None
        r24 = pv("2024", "STEPS")
        g = Fp[(Fp["row"] == row) & (Fp["scenario"] == "STEPS")].assign(y=lambda d: d["year"].astype(int)).sort_values("y")
        obs, pr = g[g["case"].str.startswith("observed")], g[g["case"].str.startswith("projected")]
        step = ""
        if len(obs) and len(pr[pr["y"] > obs["y"].max()]):
            a = num(obs.iloc[-1][vcol])
            b = num(pr[pr["y"] > obs["y"].max()].iloc[0][vcol])
            if a:
                step = f"{(b / a - 1) * 100:+.1f}% ({obs.iloc[-1]['year']} to {pr[pr['y'] > obs['y'].max()].iloc[0]['year']})"
        t.append({"Row": row, "Chosen point 2024": pt,
                  "2024 current": fmt(r24["current_value"], 3) if r24 is not None else "",
                  "2024 proposed": fmt(r24["proposed_value"], 3) if r24 is not None else "",
                  "STEPS 2030": fmt(pv("2030", "STEPS")["proposed_value"], 2) if pv("2030", "STEPS") is not None else "",
                  "STEPS 2050": fmt(pv("2050", "STEPS")["proposed_value"], 2) if pv("2050", "STEPS") is not None else "",
                  "CPS 2050": fmt(pv("2050", "CPS")["proposed_value"], 2) if pv("2050", "CPS") is not None else "",
                  "NZE 2050": fmt(pv("2050", "NZE")["proposed_value"], 2) if pv("2050", "NZE") is not None else "",
                  "Step at the join (STEPS)": step or "no observed-to-projected join"})
    w("Fuel supply rows (USD/GJ, net, real 2024 USD):")
    w("")
    w(md_table(pd.DataFrame(t)))
    w("")
    big = F[(F["cc"] == cc) & (F["screen"] == "proposed change above 25 percent from current") & (F["severity"] == "medium")]
    plants = set(re.findall(r"^\| `([^`]+)`", text(cc, "BRIEF_LAC_COST_SRC_*.md").split("Power plants in scope")[1].split("Fuel supply rows")[0], re.M))
    bp = big[~big["technology"].isin(fuel_rows)]
    w(f"Plant and other technology changes above 25 percent from a real current value ({len(bp)} technology-parameter pairs):")
    w("")
    if len(bp):
        tt = []
        for _, r in bp.iterrows():
            q = P[(P["Tech"] == r["technology"]) & (P["Parameter"] == r["parameter"])]
            q24 = q[q["year"] == "2024"]
            qq = q24.iloc[0] if len(q24) else q.iloc[0]
            tt.append({"Technology": r["technology"], "Parameter": r["parameter"],
                       "Year shown": qq["year"], "Current": fmt(qq["current_value"]), "Proposed": fmt(qq["proposed_value"]),
                       "Change range": r["detail"].split(";")[-2 if "placeholder" in r["detail"] else 0].split(" over ")[0].replace("change ", ""),
                       "Class": r["change_class"], "Sources": r["source_ids"][:60],
                       "Derivation (start)": qq["derivation"][:140]})
        w(md_table(pd.DataFrame(tt)))
    else:
        w("None.")
    w("")
    w("Answers to the hub's questions:")
    w("")
    s6 = RT.STEP6[cc]
    if "{gua_unit_check}" in s6:
        g = V[(V["cc"] == "gua") & V["technology"].isin(["PPFOI", "PPBGS"]) & (V["parameter"] == "VariableCost")]
        s6 = s6.replace("{gua_unit_check}", "; ".join(
            f"{r['technology']} {r['number_searched']}: found {r['found']}" + (f" at {r['file']} {r['location']}" if r["found"] == "yes" else "")
            for _, r in g.iterrows()) or "no value check row")
    w(s6)
    w("")
    fl = F[F["cc"] == cc]
    w(f"Flags ({len(fl)}: high {(fl['severity'] == 'high').sum()}, medium {(fl['severity'] == 'medium').sum()}, low {(fl['severity'] == 'low').sum()}; all in `review_flags.csv`). High and medium:")
    w("")
    hm = fl[fl["severity"].isin(["high", "medium"])]
    for _, r in hm.iterrows():
        w(f"- [{r['severity']}] {r['screen']}: {r['technology']} {r['parameter']} {r['fuel_scenario']} {r['years']}; "
          f"proposed {fmt(r['proposed_min'])} to {fmt(r['proposed_max'])}, current {r['current_values'][:40]}; {r['change_class']}; {r['detail'][:220]}")
    if not len(hm):
        w("- none")
    extra = RT.COUNTRY_FLAGS.get(cc)
    if extra:
        w("")
        w(extra)
    w("")
# ---- 5. decisions
w("## 5. Decisions raised by the six jobs")
w("")
w(RT.DECISIONS_INTRO.format(n=len(DR), k=", ".join(f"{t} {c}" for t, c in DR["type"].value_counts().items())))
w("")
w(RT.DECISIONS_SYNTHESIS)
w("")
TOPICS = ["fuel point choice", "fuel price method", "benchmark or WEO series", "natural gas", "coal and coke",
          "electricity imports", "plant capital cost", "plant fixed and variable cost", "source edition or currency year",
          "placeholders and units", "model structure", "paper trail", "process"]
for tp in TOPICS + sorted(set(DR["topic"]) - set(TOPICS)):
    d = DR[(DR["topic"] == tp) & (DR["type"] != "incident")]
    if not len(d):
        continue
    w(f"### {tp[0].upper() + tp[1:]} ({len(d)})")
    w("")
    for _, r in d.iterrows():
        rows_ = f" Rows: {r['rows_affected']}." if r["rows_affected"] else ""
        eff = f" Effect: {r['effect_size']}." if r["effect_size"] else ""
        w(f"- {r['country']} [{r['type']}; {r['file']}, {r['section']}]: {r['text']}{rows_}{eff}")
    w("")
REPORT = "\n".join(L) + "\n"

# ---------------- GAPS ----------------
nr = []
for cc in ORDER:
    v = V[(V["cc"] == cc) & (V["found"] == "not run")]
    if len(v):
        reasons = v["note"].str.extract(r"(no number to search[^|;]*|no searchable file[^|]*)")[0].fillna("other").str[:160]
        top = reasons.value_counts().head(4)
        nr.append(f"- {COUNTRY[cc]}: {len(v)} value checks not run. " + "; ".join(f"{k} ({n})" for k, n in top.items()) + ".")
    nf = V[(V["cc"] == cc) & (V["found"] == "no")]
    mean = nf["note"].str.contains("mean over several").sum()
    causes = nf["likely_cause_if_not_found"].value_counts() if "likely_cause_if_not_found" in nf.columns else pd.Series(dtype=int)
    nr.append(f"- {COUNTRY[cc]}: {len(nf)} value checks not found (files searchable, number absent). Likely cause read from the derivation: "
              + ("; ".join(f"{k} ({n})" for k, n in causes.items()) if len(causes) else "not classified")
              + ". Each is listed in `value_checks.csv` with its derivation, the other inputs and whether they were found.")
nr.append("- Derivations with no arithmetic chain the parser could read (text-only derivations, or chains broken by words) were not recomputed. Counts of distinct derivations against expressions recomputed are in REPORT section 2.")
nr.append("- No model was run. Whether Costa Rica's `IMPELE` or the Dominican Republic's `EXTT_CRU` and `PRO_COA` are used in a least-cost solution was judged from their limits and costs only.")
nr.append("- Images and scanned pages in the downloads (PNG captures of Petrojam, MSET and other pages) were not searched. Every value check had at least one searchable text file among its sources, so none ended `not run` for that reason; a number printed only in an image would show as `no`.")
nr.append("- The decisions list was checked against its source text only for the items named in GAPS section 2, item 12.")
GAPS = RT.GAPS.replace("{notrun}", "\n".join(nr)) + "\n"
# ---------------- CHANGES ----------------
files = sorted(f for f in os.listdir(JOB) if os.path.isfile(os.path.join(JOB, f)))
C = [f"# CHANGES LAC_COST_REVIEW_PACK {STAMP}", "",
     f"All files are new, in `_LAC_HUB/cost_review_{STAMP}/` on branch `job/cost-review` (from `2ddd560`). "
     "Nothing else in the repository was added, changed or removed.", ""]
for f in files + [f"REPORT_LAC_COST_REVIEW_PACK_{STAMP}.md", f"GAPS_LAC_COST_REVIEW_PACK_{STAMP}.md", f"CHANGES_LAC_COST_REVIEW_PACK_{STAMP}.md"]:
    if f in RT.FILE_DESC or f.startswith(("REPORT_", "GAPS_", "CHANGES_")):
        desc = RT.FILE_DESC.get(f) or RT.FILE_DESC.get(f.split("_LAC")[0], "")
        line = f"- `{f}`: {desc}"
        if line not in C:
            C.append(line)
C += ["", "Not tracked: `scratch/` (branch extracts, the six A-O copies, cached text of the downloaded files); it is left out of the commit.", "",
      RT.CONFIRM]
CHANGES = "\n".join(C) + "\n"

for name, body in [("REPORT", REPORT), ("GAPS", GAPS), ("CHANGES", CHANGES)]:
    body = body.replace(chr(0x2014), ", ").replace(chr(0x2013), "-")  # em and en dash
    body = "\n".join(line.rstrip() for line in body.split("\n")).rstrip("\n") + "\n"
    with open(out(f"{name}_LAC_COST_REVIEW_PACK_{STAMP}.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    print(name, len(body.splitlines()), "lines")
