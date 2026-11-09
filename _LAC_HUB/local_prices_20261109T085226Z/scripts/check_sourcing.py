"""Gate 4 (as replaced by STEER_1) and Gate 5 checks.
Usage: py -I check_sourcing.py <job_folder> <out_txt>
Gate 4: every row of local_prices_2024.csv, local_history.csv, calorific_basis.csv and constants.csv whose
evidence class is not ASSUMPTION candidate names a source id that exists in sources.csv; every source in
sources.csv has an http(s) URL, a page or table, a retrieval date and a file that exists in downloads/;
no source field holds a local path, a file in this repository or an internal document.
Gate 5: every ASSUMPTION candidate row has a search_log entry for each lead of its country and fuel."""
import sys, os, re
import pandas as pd

job, out = sys.argv[1], sys.argv[2]
rd = lambda f: pd.read_csv(os.path.join(job, f), dtype=str, keep_default_na=False)
src = rd("sources.csv")
ids = set(src["id"])
lines, fails = [], 0


def ids_of(s):
    return [x.strip() for x in re.split(r"[;,]", str(s)) if x.strip()]


# --- Gate 4a: rows name existing source ids
for f, idcol, clscol in [("local_prices_2024.csv", "source_id", "evidence_class"),
                         ("local_history.csv", "source_id", "evidence_class"),
                         ("calorific_basis.csv", "source_id", None),
                         ("constants.csv", "source_id", None)]:
    d = rd(f)
    n = len(d)
    if clscol:
        d = d[d[clscol] != "ASSUMPTION candidate"]
    bad = [i for i, s in d[idcol].items() if not ids_of(s) or any(x not in ids for x in ids_of(s))]
    lines.append(f"G4a {f}: {n} rows, {len(d)} needing a source, {len(d) - len(bad)} pass, {len(bad)} fail")
    for i in bad:
        lines.append(f"  FAIL {f} row {i + 2}: source_id '{d.loc[i, idcol]}'")
    fails += len(bad)

# --- Gate 4b: each source complete, file exists
LOCAL = re.compile(r"((?:^|[\s;\"'(])[A-Za-z]:[\\/]|^/c/|\\|_LAC_HUB|MODELS_LAC|clw_|workbook|handover|adders_2024"
                   r"|price_sources_2026|A-O_Parametrization)", re.I)
bad = 0
for i, r in src.iterrows():
    probs = []
    if not re.match(r"^https?://", r["url"].strip()):
        probs.append("url not http(s)")
    if not r["page_or_table"].strip():
        probs.append("no page_or_table")
    if not re.match(r"^\d{4}-\d{2}-\d{2}", r["retrieval_date"].strip()):
        probs.append("no retrieval_date")
    files = [x.strip() for x in r["downloaded_file"].split(";") if x.strip()]
    if not files:
        probs.append("no downloaded_file")
    for fn in files:
        if not os.path.isfile(os.path.join(job, "downloads", fn)):
            probs.append(f"file missing: {fn}")
    for col in ["url", "title", "publisher", "page_or_table"]:
        if LOCAL.search(r[col]):
            probs.append(f"local or internal reference in {col}")
    if probs:
        bad += 1
        lines.append(f"  FAIL sources.csv {r['id']}: {'; '.join(probs)}")
lines.insert(len(lines) - bad, f"G4b sources.csv: {len(src)} sources, {len(src) - bad} pass, {bad} fail")
fails += bad
dup = src["id"][src["id"].duplicated()].tolist()
lines.append(f"G4c duplicate source ids: {len(dup)} {dup[:10]}")
fails += len(dup)

# --- Gate 4d (original brief gate 4): price rows name a downloaded file that exists
for f in ["local_prices_2024.csv", "local_history.csv"]:
    d = rd(f)
    d = d[d["evidence_class"] != "ASSUMPTION candidate"]
    bad = []
    for i, s in d["downloaded_file"].items():
        fl = [x.strip() for x in str(s).split(";") if x.strip()]
        if not fl or any(not os.path.isfile(os.path.join(job, "downloads", x)) for x in fl):
            bad.append(i)
    lines.append(f"G4d {f}: {len(d)} rows needing a file, {len(d) - len(bad)} pass, {len(bad)} fail")
    for i in bad:
        lines.append(f"  FAIL {f} row {i + 2}: downloaded_file '{d.loc[i, 'downloaded_file']}'")
    fails += len(bad)

# --- Gate 5: ASSUMPTION rows have every lead logged
LEADS_ALL = ["customs_national", "comtrade", "energy_balance"]
LEADS = {"CR": ["aresep_recope", "procomer_bccr_hacienda", "ice_aresep_generation", "minae_balance"],
         "DR": ["mem_bulletins", "ocseni", "sie_cne_micm", "dga_one_refidomsa"],
         "ECU": ["petroecuador", "arcernnr", "mem_cenace", "bce_senae"],
         "GUA": ["mem_gua", "amm", "cnee_peg", "banguat"],
         "HON": ["sen_weekly", "sen_annual", "cree", "enee_ods_cnd", "gaceta_lng", "bch"],
         "JAM": ["petrojam", "our_jps", "mset_pcj", "statin_boj", "gazette"]}
log = rd("search_log.csv")
p = rd("local_prices_2024.csv")
a = p[p.evidence_class == "ASSUMPTION candidate"][["country", "fuel"]].drop_duplicates()
ok5 = 0
for _, r in a.iterrows():
    need = LEADS_ALL + LEADS.get(r.country, [])
    have = set(log[(log.country == r.country) & (log.fuel == r.fuel)].lead_id)
    miss = [x for x in need if x not in have]
    if miss:
        lines.append(f"  FAIL G5 {r.country} {r.fuel}: leads not logged {miss}")
        fails += 1
    else:
        ok5 += 1
lines.append(f"G5 ASSUMPTION candidate rows (country, fuel): {len(a)}, {ok5} pass, {len(a) - ok5} fail")
lines.append(f"TOTAL FAILURES: {fails}")
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(l for l in lines if not l.startswith("  FAIL")))
