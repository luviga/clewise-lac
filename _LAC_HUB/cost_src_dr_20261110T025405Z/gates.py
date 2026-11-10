"""Step 9 gates. Usage: py -I gates.py pre | post. Writes gate_results_<mode>.txt."""
import os, sys, re, csv, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import *

mode = sys.argv[1]
out = []
def res(name, ok, detail): out.append(f"{name}: {'PASS' if ok else 'FAIL'} - {detail}")

if mode == "pre":
    # 1 read-only
    subprocess.run([sys.executable, "-I", os.path.join(JOB, "baseline.py"), os.path.join(JOB, "baseline_after.csv")], check=True, capture_output=True)
    b0 = pd.read_csv(os.path.join(JOB, "baseline_before.csv")); b1 = pd.read_csv(os.path.join(JOB, "baseline_after.csv"))
    res("Gate 1 read-only", b0.equals(b1), f"{len(b0)} files, hashes equal: {b0.equals(b1)}")
    # 4 sourcing
    P = pd.read_csv(os.path.join(JOB, "proposals.csv")); S = pd.read_csv(os.path.join(JOB, "sources.csv"))
    sid = set(S.id)
    bad_rows = 0; ids_used = set()
    for r in P.itertuples():
        if r.basis_class == "ASSUMPTION": continue
        ids = [t for t in re.split(r"[;\s]+", str(r.source_ids)) if t]
        ids_used |= set(ids)
        if not ids or any(i not in sid for i in ids): bad_rows += 1
    res("Gate 4a proposals cite existing sources", bad_rows == 0, f"{len(P)} rows, {bad_rows} rows with a missing or unknown source id; {len(ids_used)} distinct ids cited")
    probs = []
    path_pat = re.compile(r"([A-Za-z]:\\|/c/|\\Users\\|/Users/|clw_|OneDrive|\.xlsx!|A-O_|_LAC_HUB)")
    for r in S.itertuples():
        if not re.match(r"^https?://", str(r.url)): probs.append(f"{r.id} url")
        if not str(r.page_or_table).strip() or str(r.page_or_table) == "nan": probs.append(f"{r.id} locator")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(r.retrieval_date)): probs.append(f"{r.id} date")
        for f in [x.strip() for x in str(r.downloaded_file).split(";") if x.strip()]:
            if not os.path.exists(os.path.join(DL, f)): probs.append(f"{r.id} file {f}")
        for col in ("url", "title", "page_or_table"):
            v = str(getattr(r, col))
            if col == "url": continue
            if path_pat.search(v): probs.append(f"{r.id} {col} has a local or internal reference")
    res("Gate 4b source records complete", not probs, f"{len(S)} sources; {len(probs)} problems" + (": " + "; ".join(probs[:10]) if probs else ""))
    # 5 assumptions
    A = P[P.basis_class == "ASSUMPTION"]
    sents = P[P.assumption_sentence.fillna("") != ""]
    SL = pd.read_csv(os.path.join(JOB, "search_log.csv"))
    banned = re.compile(r"\b(job|jobs|file|files|search|searched|not found|could not|LAC_|workbook|brief|ruling|handover)\b", re.I)
    missing_leads = sorted({t for t in A.Tech if not SL.row.astype(str).str.contains(t).any()})
    bad_sent = sorted({s for s in sents.assumption_sentence.unique() if banned.search(s)})
    sent_techs = sorted(sents.Tech.unique())
    missing_leads_s = sorted({t for t in sent_techs if not SL.row.astype(str).str.contains(t).any()})
    res("Gate 5 ASSUMPTION rows", not missing_leads and not bad_sent and not missing_leads_s,
        f"{len(A)} rows with basis ASSUMPTION; {len(sents)} rows carry an ASSUMPTION sentence ({', '.join(sent_techs)}), {sents.assumption_sentence.nunique()} distinct sentences; leads missing for {missing_leads + missing_leads_s}; sentences with banned words {len(bad_sent)}")
    # 6 coverage
    YEARS = set(range(2018, 2051)); gaps = []
    for t in PLANTS:
        for p in COST_PARAMS:
            ys = set(P[(P.Tech == t) & (P.Parameter == p) & (P.fuel_scenario == "ALL")].year)
            if ys != YEARS: gaps.append(f"{t} {p}")
    fuel_rows = [t for t in SUPPLY if t.startswith("DIST_")]
    for t in fuel_rows:
        for s in ("STEPS", "CPS", "NZE"):
            ys = set(P[(P.Tech == t) & (P.fuel_scenario == s)].year)
            if ys != YEARS: gaps.append(f"{t} {s}")
    res("Gate 6 coverage", not gaps, f"{len(PLANTS)} plants x 3 parameters x 33 years; {len(fuel_rows)} supply rows x 3 scenarios x 33 years; EXTT_CRU, EXTT_NGS, PRO_COA and IMP_ELE exempt by the country notes; gaps: {gaps}")
    # 7 (files part): em dash and machine paths
    em = []; mp = []
    mpat = re.compile(r"((?<![A-Za-z])[A-Za-z]:[\\/](?!/)|(?<![A-Za-z0-9.])/c/|\\Users\\|(?<![A-Za-z0-9.])/Users/)")
    for fn in sorted(os.listdir(JOB)):
        fp = os.path.join(JOB, fn)
        if not os.path.isfile(fp) or fn.startswith("BRIEF_") or fn.startswith("gate_results"): continue
        txt = open(fp, encoding="utf-8").read()
        if chr(0x2014) in txt: em.append(fn)
        for line in txt.splitlines():
            if fn.endswith(".py") and "re.compile(" in line: continue  # the gate's own patterns
            for m in mpat.finditer(line):
                before = line[:m.start()]
                if re.search(r"https?://\S*$", before): continue
                mp.append(fn); break
    res("Gate 7a no em dash, no machine path", not em and not mp, f"files with em dash: {sorted(set(em))}; files with a machine path: {sorted(set(mp))}")
else:
    os.chdir(ROOT)
    def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True).stdout
    names = [n for n in git("diff", "--name-only", "2ddd560", "HEAD").splitlines() if n]
    rel = "_LAC_HUB/cost_src_dr_" + STAMP + "/"
    outside = [n for n in names if not n.startswith(rel)]
    res("Gate 2 diff only in job folder", not outside and bool(names), f"{len(names)} files changed; outside: {outside}")
    tracked = [n for n in git("ls-files", rel).splitlines() if n]
    badext = [n for n in tracked if not re.search(r"\.(md|csv|py|txt)$", n)]
    dl = [n for n in tracked if "/downloads/" in n]
    res("Gate 3 tracked file types", not badext and not dl, f"{len(tracked)} tracked; bad extensions {badext}; under downloads {dl}")
    chk = subprocess.run(["git", "diff", "--check", "2ddd560", "HEAD"], capture_output=True, text=True)
    res("Gate 7b git diff --check", chk.returncode == 0 and not chk.stdout.strip(), (chk.stdout.strip()[:300] or "clean"))
    log = git("log", "-3", "--format=%B")
    res("Gate 7c commit messages", "Co-Authored-By" not in log and "Generated with" not in log, "no trailer lines in the last 3 messages" if "Co-Authored-By" not in log and "Generated with" not in log else log[:300])
open(os.path.join(JOB, f"gate_results_{mode}.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("\n".join(out))
