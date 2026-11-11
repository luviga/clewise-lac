"""Steps 1 and 2: inventory of the six branches and the eight gates rerun independently."""
import fnmatch
import hashlib
import re
import sys

import openpyxl

sys.path.insert(0, ".")
from common import *  # noqa

COST = ["CapitalCost", "FixedCost", "VariableCost"]

# ---------- brief section 5 parsing ----------

def brief_section5(cc):
    t = text(cc, "BRIEF_LAC_COST_SRC_*.md")
    s5 = t.split("## 5.")[1].split("## 6.")[0]
    plant_part = s5.split("Power plants in scope")[1].split("Fuel supply rows")[0]
    fuel_part = s5.split("Fuel supply rows")[1].split("Country notes")[0]
    plants = re.findall(r"^\| `([^`]+)`", plant_part, re.M)
    fuels = re.findall(r"^\| `([^`]+)`", fuel_part, re.M)
    return plants, fuels


# Import technology where the brief's Step 6 applied (from each brief's country notes)
IMPORT = {"ecu": "IMPELE", "gua": "IMP_ELE", "hon": "IMP_ELE"}
# Rows the country brief allowed to be left without a proposal (quoted in gates note)
ALLOWED_ABSENT = {
    "dr": {"EXTT_CRU": "brief: if they cannot run, leave them and record it",
           "EXTT_NGS": "brief: if they cannot run, leave them and record it",
           "PRO_COA": "brief: if they cannot run, leave them and record it"},
    "gua": {"EXTT_CRU": "brief: record it; propose nothing unless a published Guatemala crude export price is easy to source"},
}


def ao_years(cc):
    wb = openpyxl.load_workbook(os.path.join(SCRATCH, f"AO_{cc}.xlsx"), read_only=True, data_only=True)
    hdr = next(wb["Primary Techs"].iter_rows(max_row=1, values_only=True))
    return [str(h) for h in hdr if isinstance(h, int) or (isinstance(h, str) and h.isdigit())]


def ao_cost_rows(cc):
    """Every cost row of Primary and Secondary Techs at 2ddd560: {(tech, param): {year: value}} plus mode."""
    wb = openpyxl.load_workbook(os.path.join(SCRATCH, f"AO_{cc}.xlsx"), read_only=True, data_only=True)
    rows = {}
    for sh in ["Primary Techs", "Secondary Techs"]:
        it = wb[sh].iter_rows(values_only=True)
        hdr = list(next(it))
        for r in it:
            d = dict(zip(hdr, r))
            if d.get("Parameter") in COST and d.get("Tech"):
                yrs = {str(k): v for k, v in d.items() if isinstance(k, int)}
                rows[(sh, str(d["Tech"]), d["Parameter"])] = {"mode": d.get("Projection.Mode"), "years": yrs,
                                                             "Tech.ID": d.get("Tech.ID")}
    return rows


# ---------- Step 1 inventory ----------

def exists_map(cc):
    files = os.listdir(jobdir(cc))
    res = {}
    for pat in SECTION4 + EXTRA.get(cc, []):
        p = "BRIEF_LAC_COST_SRC_*.md" if pat == "BRIEF" else pat
        res[pat] = any(fnmatch.fnmatch(f, p) for f in files)
    return res


inv = []
for cc in CCS:
    head = git("rev-parse", branch(cc)).strip()
    log = git("log", "--format=%h %s", f"{BASE}..{branch(cc)}").strip().splitlines()
    ex = exists_map(cc)
    missing = [k for k, v in ex.items() if not v]
    inv.append({"country": COUNTRY[cc], "cc": cc, "pr": PR[cc], "branch": f"job/cost-src-{cc}",
                "head": head, "head_in_brief": HEAD_BRIEF[cc],
                "head_matches_brief": head.startswith(HEAD_BRIEF[cc]),
                "commits_since_2ddd560": len(log), "commit_messages": " | ".join(log),
                "job_folder": f"_LAC_HUB/{jobname(cc)}/",
                **{f"has_{k}": "yes" if v else "no" for k, v in ex.items()},
                "missing_files": ";".join(missing) if missing else "none",
                "flag": "missing file" if missing else ""})
inv_df = pd.DataFrame(inv)
# put the extra-file columns at the end, empty where not applicable
write(inv_df, "inventory.csv")

# ---------- Step 2 gates ----------

FORBIDDEN = ["job", "hub", "agent", "brief", "PR", "pull request", "commit", "workbook", "sheet", "cell",
             "CSV", "not found", "could not", "unable", "no source", "unrecovered", "retained", "kept as",
             "previously", "earlier", "pending"]


def forbidden_hits(sentence):
    s = sentence.replace("(pending correction)", "")
    # "Henry Hub" is the proper name of the gas benchmark and is part of the gas sentence the
    # country briefs prescribe (rule F5); it is not a reference to the hub. Recorded in GAPS.
    s = re.sub(r"Henry Hub", "Henry H_b", s)
    hits = []
    for w in FORBIDDEN:
        # whole word or phrase, case-insensitive, plural s allowed
        if re.search(r"(?<![A-Za-z])" + re.escape(w) + r"s?(?![A-Za-z])", s, re.I):
            hits.append(w)
    return hits


LOCAL = re.compile(r"([A-Za-z]:\\|[A-Za-z]:/|/c/|\\\\|OneDrive|Users\\|_LAC_HUB|\.xlsx\b|\.xlsm\b|\.md\b|"
                   r"handover|paper draft|CLEWISE_|A-O_|proposals\.csv|local_prices_2024\.csv|local_history\.csv)", re.I)

gates = []


def gate(cc, n, name, result, count, note):
    gates.append({"country": COUNTRY[cc], "cc": cc, "gate": n, "check": name, "result": result,
                  "count": count, "note": note})


for cc in CCS:
    br = branch(cc)
    jf = f"_LAC_HUB/{jobname(cc)}/"
    # 1
    names = [x for x in git("diff", "--name-only", BASE, br).splitlines() if x]
    outside = [x for x in names if not x.startswith(jf)]
    gate(cc, 1, "diff only in job folder", "pass" if not outside else "fail",
         f"{len(names)} files changed, {len(outside)} outside", ";".join(outside[:10]))
    # 2
    tracked = [x for x in git("ls-tree", "-r", "--name-only", br, "--", jf).splitlines() if x]
    badext = [x for x in tracked if os.path.splitext(x)[1].lower() not in (".md", ".csv", ".py", ".txt")]
    dl = [x for x in tracked if "/downloads/" in x]
    gate(cc, 2, "tracked file types; nothing under downloads/", "pass" if not badext and not dl else "fail",
         f"{len(tracked)} tracked, {len(badext)} bad extension, {len(dl)} under downloads",
         ";".join((badext + dl)[:10]))
    # 3
    body = git("log", f"{BASE}..{br}", "--format=%B")
    ca = len(re.findall("Co-Authored-By", body, re.I))
    gw = len(re.findall("Generated with", body, re.I))
    gate(cc, 3, "no Co-Authored-By or Generated with in log", "pass" if ca == 0 and gw == 0 else "fail",
         f"{ca} Co-Authored-By, {gw} Generated with", "")
    # 4
    bb = read(cc, "baseline_before.csv")
    diffs, notes = [], []
    for f in bb["file"]:
        h0 = hashlib.sha256(git("show", f"{BASE}:{f}", binary=True)).hexdigest()
        h1 = hashlib.sha256(git("show", f"{br}:{f}", binary=True)).hexdigest()
        rec = bb.loc[bb["file"] == f, "sha256"].iloc[0]
        if h0 != h1:
            diffs.append(f)
        if rec != h0:
            notes.append(f"{os.path.basename(f)} recorded hash differs from git blob at 2ddd560")
    gate(cc, 4, "baseline files identical at 2ddd560 and head", "pass" if not diffs else "fail",
         f"{len(bb)} files, {len(diffs)} differ", "; ".join(diffs + notes))
    # 5
    P = read(cc, "proposals.csv")
    S = read(cc, "sources.csv")
    idc = S.columns[0]
    sid = set(S[idc])
    nonA = P[P["basis_class"] != "ASSUMPTION"]
    no_ids = nonA[nonA["source_ids"].str.strip() == ""]
    bad_ids = set()
    for x in nonA["source_ids"]:
        for i in [i.strip() for i in re.split(r"[;,]", x) if i.strip()]:
            if i not in sid:
                bad_ids.add(i)
    loccol = "page_or_table" if "page_or_table" in S.columns else "locator"
    dlroot = downloads(cc)
    probs = {"no_url": [], "no_locator": [], "no_retrieval": [], "no_file": [], "file_missing": [], "local_or_internal": []}
    external_wb = []
    for _, r in S.iterrows():
        i = r[idc]
        if not re.match(r"https?://", r["url"].strip()):
            probs["no_url"].append(i)
        if not r[loccol].strip():
            probs["no_locator"].append(i)
        if not r["retrieval_date"].strip():
            probs["no_retrieval"].append(i)
        fn = r["downloaded_file"].strip()
        if not fn:
            probs["no_file"].append(i)
        else:
            parts = [p.strip() for p in re.split(r";", fn) if p.strip()]
            if not all(os.path.exists(os.path.join(dlroot, p.replace("downloads/", "", 1))) for p in parts):
                probs["file_missing"].append(f"{i}:{fn}")
        for c in S.columns:
            if c in (idc, "notes", "rows_and_constants_supported", "origin", "cited_in_proposals"):
                continue
            v = r[c]
            vv = re.sub(r"https?://\S+", "", v)  # URLs are allowed to contain anything
            if c == "downloaded_file":
                vv = vv.replace("\\", "/")
                if re.search(r"[A-Za-z]:/|/c/|OneDrive|Users/", vv):
                    probs["local_or_internal"].append(f"{i}.{c}")
                continue
            if LOCAL.search(vv):
                # a published workbook named in the title is external when the URL is that same file
                from urllib.parse import unquote
                names = re.findall(r"[\w\-. ]+\.xls[xm]?", vv)
                u = unquote(r["url"])
                if names and all(n.split()[-1].strip("\"'(") in u for n in names) \
                        and not re.search(r"[A-Za-z]:\\|OneDrive|_LAC_HUB|\.md\b|handover|CLEWISE_", vv):
                    external_wb.append(f"{i}")
                    continue
                probs["local_or_internal"].append(f"{i}.{c}:{LOCAL.search(vv).group(0)}")
    ok = not no_ids.shape[0] and not bad_ids and not any(probs.values())
    cnt = (f"{len(nonA)} non-ASSUMPTION rows, {len(no_ids)} without ids, {len(bad_ids)} unknown ids; "
           f"{len(S)} sources: " + ", ".join(f"{k} {len(v)}" for k, v in probs.items()))
    gate(cc, 5, "sourcing", "pass" if ok else "fail", cnt,
         "; ".join([f"unknown ids {sorted(bad_ids)[:10]}"] if bad_ids else []) + " " +
         "; ".join(f"{k}: {v[:8]}" for k, v in probs.items() if v) +
         (f" published external workbook named in title and served at the cited URL (not internal): {sorted(set(external_wb))}" if external_wb else ""))
    # 6
    A = P[P["basis_class"] == "ASSUMPTION"]
    L = read(cc, "search_log.csv")
    logtext = [" ".join(r.values) for _, r in L.iterrows()]
    rowtext = list(L["row"])
    generic = [t for t in rowtext if re.fullmatch(r"(?i)\s*(all|all plants.*|all supply rows|all fuel rows|ALL fuel rows|ALL plants)\s*", t)]
    tech_ok, tech_generic, tech_none = set(), set(), set()
    for t in sorted(set(A["Tech"])):
        pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(t) + r"(?![A-Za-z0-9_])")
        if any(pat.search(x) for x in rowtext):
            tech_ok.add(t)
        elif any(pat.search(x) for x in logtext):
            tech_ok.add(t)
        elif t.startswith("DIST_") and any(re.search(r"DIST_\*", x) for x in logtext):
            tech_ok.add(t)
        elif generic:
            tech_generic.add(t)
        else:
            tech_none.add(t)
    bad_sent = []
    for _, r in A.drop_duplicates(["Tech", "Parameter", "assumption_sentence"]).iterrows():
        h = forbidden_hits(r["assumption_sentence"])
        if h or not r["assumption_sentence"].strip():
            bad_sent.append(f"{r['Tech']}/{r['Parameter']}: {h or 'empty'}")
    nrows_bad = sum(1 for _, r in A.iterrows() if forbidden_hits(r["assumption_sentence"]) or not r["assumption_sentence"].strip())
    res = "pass" if not tech_none and not bad_sent else "fail"
    gate(cc, 6, "ASSUMPTION leads logged and sentence words", res,
         f"{len(A)} ASSUMPTION rows on {A['Tech'].nunique()} technologies; leads by name {len(tech_ok)}, "
         f"only a generic all-rows log entry {len(tech_generic)}, none {len(tech_none)}; "
         f"{nrows_bad} rows ({len(bad_sent)} distinct sentences) with a listed word",
         ("no lead: " + ";".join(sorted(tech_none)) + " | " if tech_none else "") +
         ("generic only: " + ";".join(sorted(tech_generic)) + " | " if tech_generic else "") + " ; ".join(bad_sent[:25]))
    # 7
    plants, fuels = brief_section5(cc)
    years = ao_years(cc)
    ao = ao_cost_rows(cc)
    missing = []
    allowed = []
    def have(t, prm, scen=None, yrs=years):
        q = P[(P["Tech"] == t) & (P["Parameter"] == prm)]
        if scen:
            q = q[q["fuel_scenario"] == scen]
        got = set(q["year"])
        return [y for y in yrs if y not in got]
    for t in plants:
        for prm in COST:
            m = have(t, prm)
            if m:
                in_ao = any(k[1] == t and k[2] == prm for k in ao)
                missing.append(f"{t}/{prm} missing {len(m)} years (A-O row {'exists' if in_ao else 'absent'})")
    for t in fuels:
        for s in ["STEPS", "CPS", "NZE"]:
            m = have(t, "VariableCost", s)
            if m:
                if t in ALLOWED_ABSENT.get(cc, {}):
                    allowed.append(f"{t} ({ALLOWED_ABSENT[cc][t]})")
                else:
                    missing.append(f"{t}/VariableCost/{s} missing {len(m)} years")
    imp = IMPORT.get(cc)
    if imp:
        yrs = years
        if cc == "hon":
            # Step 6 applies only to years with a positive activity lower limit (BAU at 2ddd560)
            ll = pd.read_csv(io_bytes := __import__("io").BytesIO(git("show", f"{BASE}:{ENERGY[cc]}/A2_Output_Params/BAU/TotalTechnologyAnnualActivityLowerLimit.csv", binary=True)), dtype=str)
            tc = [c for c in ll.columns if c.upper() == "TECHNOLOGY"][0]
            yc = [c for c in ll.columns if c.upper() == "YEAR"][0]
            vc = [c for c in ll.columns if c.upper() == "VALUE"][0]
            q = ll[(ll[tc] == imp)]
            yrs = sorted(set(q[q[vc].astype(float) > 0][yc]))
        m = have(imp, "VariableCost", yrs=yrs)
        if m:
            missing.append(f"{imp}/VariableCost missing {len(m)} of {len(yrs)} years")
    gate(cc, 7, "coverage", "pass" if not missing else "fail",
         f"{len(plants)} plants x 3 parameters, {len(fuels)} supply rows x 3 scenarios, import {imp or 'n/a'}; "
         f"{len(years)} year columns {years[0]} to {years[-1]}; {len(missing)} gaps; {len(set(allowed))} brief-allowed absences",
         "; ".join(missing[:30]) + (" | allowed: " + "; ".join(sorted(set(allowed))) if allowed else ""))
    # 8
    em = []
    for f in tracked:
        b = git("show", f"{br}:{f}", binary=True).decode("utf-8", "replace")
        n = b.count(chr(0x2014))  # em dash
        if n:
            em.append(f"{os.path.basename(f)} ({n})")
    em_out = [e for e in em if not e.startswith("BRIEF_")]
    gate(cc, 8, "no em dash in tracked output files", "pass" if not em_out else "fail",
         f"{len(tracked)} files checked, {len(em_out)} output files with em dash",
         "; ".join(em) if em else "")

G = pd.DataFrame(gates)
write(G, "gates.csv")
print(G[["cc", "gate", "result", "count"]].to_string())
for _, r in G.iterrows():
    if r["result"] != "pass" or r["note"].strip():
        print(r["cc"], r["gate"], "NOTE:", r["note"][:1500])
