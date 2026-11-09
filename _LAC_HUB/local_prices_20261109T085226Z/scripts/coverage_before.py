"""coverage_before.csv: the 55 rows of the earlier adders_2024.csv with method, open/closed status and notes.
Usage: py -I coverage_before.py <earlier_adders_csv> <out_csv>"""
import sys, pandas as pd
src, out = sys.argv[1], sys.argv[2]
d = pd.read_csv(src)
cls = {
    "observed (regulator price structure)": "observed",
    "observed (regulator published delivered price)": "observed",
    "observed (regulator published importer price)": "observed",
    "ASSUMPTION candidate": "open: ASSUMPTION candidate",
    "built (regional published data)": "open: built from other countries",
    "built (published rates)": "open: built from published rates",
    "observed import cost; margin ASSUMPTION candidate": "open: observed import cost, assumed margin",
    "observed import cost (customs CIF); margin ASSUMPTION candidate": "open: observed import cost, assumed margin",
}
d["status_before"] = d["method"].map(cls)
notes = {
    ("Jamaica", "FOI"): "partial: OUR plant prices June and July 2024 only; extend to 12 months",
    ("Jamaica", "NGS"): "partial: OUR plant prices June and July 2024 only; extend to 12 months",
    ("Guatemala", "DSL"): "partial: 31 of 52 MEM weekly structures",
    ("Guatemala", "GSL"): "partial: 31 of 52 MEM weekly structures",
    ("Guatemala", "FOI"): "partial: 31 of 52 MEM weekly structures",
    ("Guatemala", "LPG"): "partial: 31 of 52 MEM weekly structures",
    ("Guatemala", "KER"): "partial: 31 of 52 MEM weekly structures",
    ("Honduras", "DSL"): "partial: SEN weekly bulletins January to July 2024 only",
    ("Honduras", "GSL"): "partial: SEN weekly bulletins January to July 2024 only",
    ("Honduras", "KER"): "partial: SEN weekly bulletins January to July 2024 only",
    ("Honduras", "LPG"): "partial: SEN weekly bulletins January to July 2024 only",
    ("DominicanRepublic", "GSL"): "open question: 2024 MICM import parity administrative under retail price freeze; find market-tracking 2024 import cost",
    ("DominicanRepublic", "LPG"): "open question: 2024 MICM import parity administrative under retail price freeze; find market-tracking 2024 import cost",
    ("Ecuador", "FOI"): "open question: exported in 2024 (EP Petroecuador export FOB 61.68 USD/bbl), no imports; record export and any import or delivered-to-generator value",
}
d["notes_before"] = [notes.get((c, f), "") for c, f in zip(d.country, d.fuel)]
cols = ["country", "fuel", "model_code", "method", "status_before", "benchmark", "benchmark_2024_usd_per_gj",
        "observed_import_cost_usd_per_gj", "import_adder_usd_per_gj", "margin_usd_per_gj", "adder_usd_per_gj",
        "pre_tax_price_2024_usd_per_gj", "notes_before"]
d[cols].to_csv(out, index=False, lineterminator="\n")
print(d.status_before.value_counts().to_string()); print("rows", len(d))
