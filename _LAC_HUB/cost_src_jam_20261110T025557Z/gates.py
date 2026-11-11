"""Step 9: gate checks 1, 4, 5, 6 and the file part of 7. Git-based checks (2, 3, 7 log) run in the shell; results go to gates_output.txt."""
import csv, re, sys
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
DL = HERE / "downloads"
out = []
def say(s):
    out.append(s); print(s)

# Gate 1: baseline hashes
b0 = pd.read_csv(HERE / "baseline_before.csv"); b1 = pd.read_csv(HERE / "baseline_after.csv")
g1 = b0.equals(b1)
say(f"GATE 1 read-only: {'PASS' if g1 else 'FAIL'} ({len(b0)} files, hashes {'equal' if g1 else 'differ'})")

# Gate 4: sourcing
P = pd.read_csv(HERE / "proposals.csv", keep_default_na=False)
S = pd.read_csv(HERE / "sources.csv", keep_default_na=False)
ids = set(S.id)
bad_rows = 0; nonassump = 0
for r in P.itertuples():
    if r.basis_class != "ASSUMPTION":
        nonassump += 1
        sids = [x for x in r.source_ids.split(";") if x]
        if not sids or any(s not in ids for s in sids):
            bad_rows += 1
say(f"GATE 4a proposals with basis other than ASSUMPTION citing only known source ids: {nonassump - bad_rows} of {nonassump} ({'PASS' if bad_rows == 0 else 'FAIL'})")
LOCAL = re.compile(r"([A-Za-z]:\\|/c/|\\Users\\|OneDrive|Dropbox|\.xlsx?\b.*A-O|A-O_Parametrization|_LAC_HUB|local_prices_2024|notes_)", re.I)
probs = []
for s in S.itertuples():
    if not re.match(r"https?://", s.url):
        probs.append((s.id, "url not http(s)"))
    if not s.page_or_table.strip():
        probs.append((s.id, "no page or table locator"))
    if not re.match(r"\d{4}-\d{2}-\d{2}", s.retrieval_date):
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
say(f"GATE 4b sources: {len(S)} sources; {len(S) - len({p[0] for p in probs})} pass every check; problems: {probs if probs else 'none'} ({'PASS' if not probs else 'FAIL'})")

# Gate 5: ASSUMPTION rows
A = P[P.basis_class == "ASSUMPTION"]
L = pd.read_csv(HERE / "search_log.csv", keep_default_na=False)
logged = set()
for r in L.itertuples():
    for t in re.split(r"[;,\s]+", r.row):
        logged.add(t)
no_leads = sorted({t for t in A.Tech if t not in logged and "ALL" not in logged})
BANNED = re.compile(r"\b(job|jobs|file|files|search|searched|searches|not found|could not|workbook|sheet|brief|ruling|handover|CSV|LAC_|we )", re.I)
bad_sent = sorted({r.Tech for r in A.itertuples() if not r.assumption_sentence.startswith("ASSUMPTION:") or BANNED.search(r.assumption_sentence)})
say(f"GATE 5 ASSUMPTION rows: {len(A)} rows over {A.Tech.nunique()} technologies ({', '.join(sorted(A.Tech.unique()))}); without logged leads: {no_leads or 'none'}; sentences failing the rule: {bad_sent or 'none'} ({'PASS' if not no_leads and not bad_sent else 'FAIL'})")
# also gas sentences
G = P[(P.assumption_sentence != "")]
bad_g = sorted({r.Tech for r in G.itertuples() if BANNED.search(r.assumption_sentence)})
say(f"GATE 5b all rows carrying an assumption sentence: {len(G)}; failing the wording rule: {bad_g or 'none'}")

# Gate 6: coverage
PLANTS = ["PPBGS","PPBIM","PPDSL","PPFOI","PPGEO","PPHDAM","PPHROR","PPNGS","PPPVD","PPPVDS","PPPVT","PPWNDON","PPWNDONS"]
SUPPLY = ["DIST_COA","DIST_COK","DIST_DSL","DIST_FOI","DIST_GSL","DIST_JET","DIST_KER","DIST_LPG","DIST_NGS","DIST_OPE","EXTT_CRU"]
YEARS = set(range(2021, 2056))
miss = []
cur = pd.read_csv(HERE / "cost_rows_current.csv")
for t in PLANTS:
    params = [p for p in ("CapitalCost", "FixedCost", "VariableCost")]
    for p in params:
        g = P[(P.Tech == t) & (P.Parameter == p)]
        if g.empty:
            mode = cur[(cur.Tech == t) & (cur.Parameter == p)]["Projection.Mode"].iloc[0]
            miss.append(f"{t} {p} (no proposal; current mode {mode})")
        elif set(g.year) != YEARS:
            miss.append(f"{t} {p} years {sorted(YEARS - set(g.year))}")
for t in SUPPLY:
    for sc in ("STEPS", "CPS", "NZE"):
        g = P[(P.Tech == t) & (P.Parameter == "VariableCost") & (P.fuel_scenario == sc)]
        if set(g.year) != YEARS:
            miss.append(f"{t} {sc}")
say(f"GATE 6 coverage: plants {len(PLANTS)}, supply rows {len(SUPPLY)}, years 2021 to 2055; gaps: {miss or 'none'}")

# Gate 7 (files): em dash and machine paths in output files
bad7 = []
for f in sorted(HERE.glob("*")):
    if f.is_dir() or f.suffix not in (".md", ".csv", ".txt", ".py"):
        continue
    if f.name.startswith("BRIEF_"):
        continue
    t = f.read_text(encoding="utf-8", errors="replace")
    if chr(0x2014) in t:
        bad7.append(f"{f.name}: em dash")
    if f.suffix in (".md", ".csv", ".txt", ".py"):
        t2 = re.sub(r"https?://\S+", "", t)
        if re.search(r"[A-Za-z]:\\\\?[A-Za-z_]|/c/[a-z_]", t2):
            bad7.append(f"{f.name}: machine path")
say(f"GATE 7 files: em dash or machine path in output files: {bad7 or 'none'}")
(HERE / "gates_output.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
