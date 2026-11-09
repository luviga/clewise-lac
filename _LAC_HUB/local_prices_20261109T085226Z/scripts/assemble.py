"""Assemble the job outputs from the per-country files in country/<CC>/ (and country/GEN/).
Usage: py -I assemble.py <job_folder>
Writes: local_prices_2024.csv, local_history.csv, sources.csv, constants.csv, search_log.csv,
manual_downloads.csv, calorific_basis.csv, coverage_after.csv."""
import sys, os, glob
import pandas as pd

job = sys.argv[1]
CC = ["CR", "DR", "ECU", "GUA", "HON", "JAM"]
CNAME = {"CR": "CostaRica", "DR": "DominicanRepublic", "ECU": "Ecuador", "GUA": "Guatemala", "HON": "Honduras",
         "JAM": "Jamaica"}
PRICE_COLS = ["country", "fuel", "model_code", "price_point", "year", "fob", "freight", "insurance", "port",
              "importer_terminal_margin", "wholesale_margin", "inland_freight", "retail_margin", "price_as_published",
              "currency", "unit", "period", "months_covered", "tax_treatment", "calorific_basis", "exchange_rate",
              "exchange_rate_constant", "conversion_constants", "value_usd_per_gj", "evidence_class", "source_id",
              "page_or_table", "downloaded_file", "derivation", "notes"]
SRC_COLS = ["id", "url", "title", "publisher", "date", "retrieval_date", "downloaded_file", "page_or_table",
            "rows_and_constants_supported"]
CON_COLS = ["name", "value", "unit", "source_id", "page_or_table", "derivation"]
LOG_COLS = ["country", "fuel", "lead_id", "lead", "url_or_query", "date", "result", "detail"]
MAN_COLS = ["url", "title", "publisher", "should_hold", "rows_it_closes", "why_needed", "how_failed", "save_as",
            "weight_rank"]
CAL_COLS = ["country", "balance", "publisher", "url", "net_or_gross", "factor_NGS", "factor_COA", "factor_COK",
            "factor_FOI", "factor_units", "page_or_table", "source_id"]


def load(pattern, cols, codes):
    frames = []
    for c in codes:
        for f in glob.glob(os.path.join(job, "country", c, pattern.format(c=c))):
            d = pd.read_csv(f, dtype=str, keep_default_na=False, encoding="utf-8")
            d.columns = [x.strip() for x in d.columns]
            missing = [x for x in cols if x not in d.columns]
            if missing:
                print(f"WARNING {f}: missing columns {missing}")
                for x in missing:
                    d[x] = ""
            extra = [x for x in d.columns if x not in cols]
            if extra:
                print(f"NOTE {f}: extra columns dropped {extra}")
            frames.append(d[cols])
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=cols)


prices = load("prices_{c}.csv", PRICE_COLS, CC)
hist = load("history_{c}.csv", PRICE_COLS, CC)
sources = load("sources_{c}.csv", SRC_COLS, ["GEN"] + CC)
consts = load("constants_{c}.csv", CON_COLS, ["GEN"] + CC)
log = load("search_log_{c}.csv", LOG_COLS, ["GEN"] + CC)
man = load("manual_{c}.csv", MAN_COLS, ["GEN"] + CC)
cal = load("calorific_{c}.csv", CAL_COLS, CC)

# exchange-rate and conversion constant sources, looked up from constants.csv
csrc = dict(zip(consts["name"], consts["source_id"]))


# rows that name a folder instead of files: replace by the files of the cited sources
sfile = dict(zip(sources["id"], sources["downloaded_file"]))
for d in (prices, hist):
    for i, r in d.iterrows():
        cell = str(r["downloaded_file"])
        if "/ (" in cell or cell.strip().endswith("/"):
            files = []
            for sid in [x.strip() for x in str(r["source_id"]).split(";") if x.strip()]:
                for fn in str(sfile.get(sid, "")).split(";"):
                    if fn.strip() and fn.strip() not in files:
                        files.append(fn.strip())
            d.at[i, "downloaded_file"] = "; ".join(files)
            print(f"NOTE {r['country']} {r['fuel']} {r['price_point']}: folder reference replaced by {len(files)} files")


def lookup(names):
    out = []
    for n in [x.strip() for x in str(names).split(";") if x.strip()]:
        out.append(f"{n}={csrc.get(n, 'MISSING')}")
    return "; ".join(out)


for d in (prices, hist):
    d.insert(d.columns.get_loc("exchange_rate_constant") + 1, "exchange_rate_source_id",
             d["exchange_rate_constant"].map(lookup))
    d.insert(d.columns.get_loc("conversion_constants") + 1, "conversion_constants_source_ids",
             d["conversion_constants"].map(lookup))

prices.to_csv(os.path.join(job, "local_prices_2024.csv"), index=False, lineterminator="\n")
hist.to_csv(os.path.join(job, "local_history.csv"), index=False, lineterminator="\n")
sources.to_csv(os.path.join(job, "sources.csv"), index=False, lineterminator="\n")
consts.to_csv(os.path.join(job, "constants.csv"), index=False, lineterminator="\n")
log.to_csv(os.path.join(job, "search_log.csv"), index=False, lineterminator="\n")
man["weight_rank_num"] = pd.to_numeric(man["weight_rank"], errors="coerce").fillna(9)
man = man.sort_values(["weight_rank_num", "rows_it_closes"]).drop(columns="weight_rank_num")
man.to_csv(os.path.join(job, "manual_downloads.csv"), index=False, lineterminator="\n")
nr = cal[cal["source_id"].str.strip() == ""]
cal = cal[cal["source_id"].str.strip() != ""]
cal.to_csv(os.path.join(job, "calorific_basis.csv"), index=False, lineterminator="\n")
nr.to_csv(os.path.join(job, "calorific_not_retrieved.csv"), index=False, lineterminator="\n")

# coverage_after
cov = pd.read_csv(os.path.join(job, "coverage_before.csv"), dtype=str, keep_default_na=False)
RANK = {"local regulator or operator": 1, "local customs or statistics": 2, "built from published components": 3,
        "international customs (Comtrade)": 4, "ASSUMPTION candidate": 5}
rev = {v: k for k, v in CNAME.items()}
POINTS = ["generator delivered", "wholesale import parity", "final consumer pre-tax", "import CIF", "export FOB"]
rows = []
for _, r in cov.iterrows():
    cc = rev[r["country"]]
    fuel = r["fuel"]
    p = prices[(prices.country.isin([cc, r["country"]])) & (prices.fuel == fuel)]
    classes = sorted(set(p.evidence_class), key=lambda x: RANK.get(x, 9))
    new = classes[0] if classes else "not found in this job"
    rec = {"country": r["country"], "fuel": fuel, "model_code": r["model_code"], "old_method": r["method"],
           "old_status": r["status_before"], "new_evidence_class": new,
           "all_evidence_classes_found": "; ".join(classes),
           "old_observed_import_cost_usd_per_gj": r["observed_import_cost_usd_per_gj"],
           "old_pre_tax_price_2024_usd_per_gj": r["pre_tax_price_2024_usd_per_gj"]}
    for pt in POINTS:
        q = p[p.price_point == pt]
        vals = pd.to_numeric(q.value_usd_per_gj, errors="coerce").dropna()
        key = "new_" + pt.replace(" ", "_").replace("-", "_") + "_usd_per_gj"
        rec[key] = "; ".join(f"{v:.3f} ({s})" for v, s in zip(vals, q.loc[vals.index, "source_id"])) if len(vals) else ""
    rows.append(rec)
pd.DataFrame(rows).to_csv(os.path.join(job, "coverage_after.csv"), index=False, lineterminator="\n")

print("prices", len(prices), "history", len(hist), "sources", len(sources), "constants", len(consts),
      "log", len(log), "manual", len(man), "calorific", len(cal), "calorific_not_retrieved", len(nr), "coverage", len(rows))
print(pd.DataFrame(rows).groupby(["new_evidence_class"]).size().to_string())
