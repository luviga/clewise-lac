"""Step 7: merged files across the six countries."""
import re
import sys

sys.path.insert(0, ".")
from common import *  # noqa

ORDER = ["ecu", "cr", "jam", "dr", "gua", "hon"]

# proposals_all.csv: the six proposals.csv stacked, same columns (country-specific extras appended at the end)
frames = [read(cc, "proposals.csv") for cc in ORDER]
base = list(frames[0].columns)
extra = [c for f in frames for c in f.columns if c not in base]
cols = base + list(dict.fromkeys(extra))
PA = pd.concat([f.reindex(columns=cols) for f in frames], ignore_index=True).fillna("")
write(PA, "proposals_all.csv")
print("proposals_all", PA.shape, PA["country"].value_counts().to_dict())

# summary_all.csv: the six proposals_summary.csv stacked; column names kept as each job wrote them (union)
frames = []
for cc in ORDER:
    s = read(cc, "proposals_summary.csv")
    s.insert(0, "country", COUNTRY[cc])
    frames.append(s)
cols = list(dict.fromkeys(c for f in frames for c in f.columns))
SA = pd.concat([f.reindex(columns=cols) for f in frames], ignore_index=True).fillna("")
write(SA, "summary_all.csv")
print("summary_all", SA.shape)

# paper_trace_all.csv: stacked, last column normalised, de-duplicated by passage, sorted by document and section
frames = []
for cc in ORDER:
    t = read(cc, "paper_trace.csv")
    t.columns = list(t.columns[:6]) + ["needs_to_say"]
    t.insert(0, "country", COUNTRY[cc])
    frames.append(t)
T = pd.concat(frames, ignore_index=True)


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


T["_k"] = T["document"].map(norm) + "|" + T["first_eight_words"].map(norm) + "|" + T["statement_as_written"].map(lambda s: norm(s)[:200])
rows = []
for k, g in T.groupby("_k", sort=False):
    r = g.iloc[0].to_dict()
    r["countries"] = ";".join(dict.fromkeys(g["country"]))
    if len(g) > 1:
        r["model_rows"] = " | ".join(f"{c}: {m}" for c, m in zip(g["country"], g["model_rows"]) if m)
        r["needs_to_say"] = " | ".join(f"{c}: {m}" for c, m in zip(g["country"], g["needs_to_say"]) if m)
    r["records_merged"] = len(g)
    rows.append(r)
PT = pd.DataFrame(rows).drop(columns=["_k", "country"])
PT = PT[["countries", "records_merged", "document", "section_heading", "table_or_figure", "first_eight_words",
         "statement_as_written", "model_rows", "needs_to_say"]]
PT = PT.sort_values(["document", "section_heading", "table_or_figure"], key=lambda s: s.str.lower()).reset_index(drop=True)
write(PT, "paper_trace_all.csv")
print("paper_trace_all", len(T), "records ->", len(PT), "passages; merged", (PT["records_merged"] > 1).sum())

# decisions_raised.csv: the six GAPS and REPORT files, one row per item (extracted per country, see GAPS of this pack)
frames = [pd.read_csv(os.path.join(SCRATCH, f), dtype=str, keep_default_na=False)
          for f in ["decisions_ecu_cr.csv", "decisions_jam_dr.csv", "decisions_gua_hon.csv"]]
DR = pd.concat(frames, ignore_index=True)
DR["country"] = pd.Categorical(DR["country"], [COUNTRY[c] for c in ORDER])
DR = DR.sort_values(["topic", "country", "type"]).reset_index(drop=True)
DR["country"] = DR["country"].astype(str)
for c in DR.columns:
    DR[c] = DR[c].str.replace(chr(0x2014), ", ").str.replace(chr(0x2013), "-")  # em and en dash
write(DR, "decisions_raised.csv")
print("decisions_raised", DR.shape, DR.groupby("country").size().to_dict())

# assumptions_all.csv: every ASSUMPTION row with its sentence (plus non-ASSUMPTION rows that carry a sentence, marked)
A = PA[(PA["basis_class"] == "ASSUMPTION") | (PA["assumption_sentence"].str.strip() != "")].copy()
A["row_kind"] = A["basis_class"].map(lambda b: "ASSUMPTION row" if b == "ASSUMPTION" else f"sentence on a {b} row")
A = A[["country", "row_kind", "sheet", "Tech", "Parameter", "fuel_scenario", "year", "current_value", "proposed_value",
       "unit", "basis_class", "source_ids", "assumption_sentence"]]
write(A, "assumptions_all.csv")
print("assumptions_all", A.shape, A.groupby(["country", "row_kind"]).size().to_dict())
