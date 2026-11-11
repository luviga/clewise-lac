"""Step 9: gate checks 1, 4, 5, 6 and the file part of 7. Git-based checks (2, 3 and the log part of 7) run in the shell
and are appended to gates_output.txt."""
import re
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
DL = HERE / "downloads"
out = []
def say(s):
    out.append(s); print(s)

b0 = pd.read_csv(HERE / "baseline_before.csv"); b1 = pd.read_csv(HERE / "baseline_after.csv")
g1 = b0.equals(b1)
say(f"GATE 1 read-only: {'PASS' if g1 else 'FAIL'} ({len(b0)} files, hashes {'equal' if g1 else 'differ'})")

P = pd.read_csv(HERE / "proposals.csv", keep_default_na=False)
S = pd.read_csv(HERE / "sources.csv", keep_default_na=False)
ids = set(S.id)
nonassump = P[P.basis_class != "ASSUMPTION"]
bad_rows = sum(1 for r in nonassump.itertuples() if not [x for x in r.source_ids.split(";") if x] or any(x not in ids for x in r.source_ids.split(";") if x))
say(f"GATE 4a proposal rows with basis other than ASSUMPTION citing only ids in sources.csv: {len(nonassump) - bad_rows} of {len(nonassump)} ({'PASS' if bad_rows == 0 else 'FAIL'})")
SL, BS = "/", chr(92)
DRIVE = "[A-Za-z]:" + BS + BS
CPATH = SL + "c" + SL
USERS = BS + BS + "Users" + BS + BS
LOCAL = re.compile("(" + DRIVE + "|" + CPATH + "|" + USERS + r"|OneDrive|Dropbox|A-O_Parametrization|_LAC_HUB|local_prices_2024|local_history|notes_HON|\.md\b)", re.I)
probs = []
for s in S.itertuples():
    if not re.match(r"https?://", s.url):
        probs.append((s.id, "url not http(s)"))
    if not s.page_or_table.strip():
        probs.append((s.id, "no page or table locator"))
    if not re.match(r"\d{4}-\d{2}-\d{2}$", s.retrieval_date):
        probs.append((s.id, "no retrieval date"))
    files = [f.strip() for f in s.downloaded_file.split(";") if f.strip()]
    if not files:
        probs.append((s.id, "no downloaded file"))
    for f in files:
        if not (DL / f).exists():
            probs.append((s.id, f"file missing in downloads: {f}"))
    for fld in ("url", "title", "page_or_table", "downloaded_file"):
        v = getattr(s, fld)
        if fld == "url":
            v = re.sub(r"https?://\S+", "", v)
        if LOCAL.search(v):
            probs.append((s.id, f"local path or internal file in {fld}"))
say(f"GATE 4b sources: {len(S)} sources; {len(S) - len({p[0] for p in probs})} pass every check (http(s) URL, locator, retrieval date, file in downloads/, no local path or internal file); problems: {probs or 'none'} ({'PASS' if not probs else 'FAIL'})")

A = P[P.basis_class == "ASSUMPTION"]
L = pd.read_csv(HERE / "search_log.csv", keep_default_na=False)
logged = set()
for r in L.itertuples():
    logged |= set(re.split(r"[;,\s]+", r.row))
no_leads = sorted({t for t in A.Tech if t not in logged})
BANNED = re.compile(r"\b(job|jobs|file|files|search|searched|searches|not found|could not|cannot be found|no source|workbook|sheet|brief|ruling|handover|CSV|LAC_|we|our)\b", re.I)
bad_sent = sorted({r.Tech for r in A.itertuples() if not r.assumption_sentence.startswith("ASSUMPTION:") or BANNED.search(r.assumption_sentence)})
say(f"GATE 5 ASSUMPTION rows: {len(A)} rows over {A.Tech.nunique()} technologies ({', '.join(sorted(A.Tech.unique()))}); without logged leads: {no_leads or 'none'}; sentences failing the rule: {bad_sent or 'none'} ({'PASS' if not no_leads and not bad_sent else 'FAIL'})")
G = P[P.assumption_sentence != ""]
bad_g = sorted({r.Tech for r in G.itertuples() if BANNED.search(r.assumption_sentence)})
say(f"GATE 5b rows carrying an assumption sentence: {len(G)} (ASSUMPTION rows plus the natural gas sentence on every DIST_NGS row); failing the wording rule: {bad_g or 'none'}")

PLANTS = ["PPBIM", "PPCOK", "PPFOI", "PPGEO", "PPGTDSL", "PPGTGLP", "PPHDAM", "PPHROR", "PPICEDSL", "PPPVD", "PPPVT", "PPWNDON"]
SUPPLY = ["DIST_COA", "DIST_COK", "DIST_DSL", "DIST_FOI", "DIST_GSL", "DIST_KER", "DIST_LPG", "DIST_NGS"]
YEARS = set(range(2018, 2051))
miss = []
for t in PLANTS:
    for p in ("CapitalCost", "FixedCost", "VariableCost"):
        g = P[(P.Tech == t) & (P.Parameter == p)]
        if set(g.year) != YEARS or len(g) != len(YEARS):
            miss.append(f"{t} {p}")
for t in SUPPLY:
    for sc in ("STEPS", "CPS", "NZE"):
        g = P[(P.Tech == t) & (P.Parameter == "VariableCost") & (P.fuel_scenario == sc)]
        if set(g.year) != YEARS or len(g) != len(YEARS):
            miss.append(f"{t} {sc}")
IMPY = set(range(2018, 2025))
for p in ("VariableCost", "FixedCost"):
    g = P[(P.Tech == "IMP_ELE") & (P.Parameter == p)]
    if set(g.year) != IMPY:
        miss.append(f"IMP_ELE {p}")
dup = P.duplicated(["Tech", "Parameter", "fuel_scenario", "year"]).sum()
say(f"GATE 6 coverage: {len(PLANTS)} plants x 3 parameters x 33 years (2018 to 2050); {len(SUPPLY)} supply rows x 3 scenarios x 33 years; IMP_ELE VariableCost and FixedCost for the 7 years with a positive activity lower limit (2018 to 2024); gaps: {miss or 'none'}; duplicate keys: {dup} ({'PASS' if not miss and dup == 0 else 'FAIL'})")

bad7 = []
for f in sorted(HERE.glob("*")):
    if f.is_dir() or f.suffix not in (".md", ".csv", ".txt", ".py", ".json"):
        continue
    if f.name.startswith("BRIEF_"):
        continue
    t = f.read_text(encoding="utf-8", errors="replace")
    if chr(0x2014) in t:
        bad7.append(f"{f.name}: em dash")
    t2 = re.sub(r"https?://\S+", "", t)
    if re.search(DRIVE + "?[A-Za-z_]|" + CPATH + "[a-z_]|" + USERS, t2):
        bad7.append(f"{f.name}: machine path")
say(f"GATE 7a files: em dash or machine path in output files (the copied brief excepted): {bad7 or 'none'} ({'PASS' if not bad7 else 'FAIL'})")
(HERE / "gates_output.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
