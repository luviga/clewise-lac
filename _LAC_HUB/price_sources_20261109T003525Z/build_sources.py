"""Build sources.csv: core sources (sources_core.csv, opened in the main session) plus every source_url in the country extraction CSVs
(opened and downloaded by the country sub-tasks in this session; see downloads/<CC>/<CC>_notes.md). Run: py -I build_sources.py <output_folder>"""
import sys, os, pandas as pd
OUT = sys.argv[1]
core = pd.read_csv(os.path.join(OUT, "sources_core.csv"))
core["opened_by"] = "main session"
rows = []
for cc in ["CR", "DR", "GUA", "HON", "JAM", "ECU"]:
    d = pd.read_csv(os.path.join(OUT, "downloads", cc, f"{cc}_regulator_2024.csv"))
    g = d.groupby("source_url").agg(title=("document_title", "first"), publisher=("publisher", "first"),
                                    date=("date_or_period", lambda s: f"{min(map(str, s))} to {max(map(str, s))}"),
                                    local_file=("local_file", lambda s: "; ".join(sorted(set(map(str, s))))[:300]), n=("value", "size")).reset_index()
    for _, r in g.iterrows():
        rows.append(dict(id=f"{cc}_{len(rows)+1:03d}", url=r.source_url, title=r.title, publisher=r.publisher,
                         date=f"data period {r.date}", retrieval_date="2026-11-09", local_file=f"downloads/{cc}/ {r.local_file}",
                         used_for=f"{cc} 2024 regulator data ({r.n} values in downloads/{cc}/{cc}_regulator_2024.csv)", opened_by="country sub-task (downloaded file kept)"))
s = pd.concat([core, pd.DataFrame(rows)], ignore_index=True)
s.to_csv(os.path.join(OUT, "sources.csv"), index=False)
print(len(core), "core +", len(rows), "country sources")
print(s.groupby(s.id.str.split("_").str[0]).size())
