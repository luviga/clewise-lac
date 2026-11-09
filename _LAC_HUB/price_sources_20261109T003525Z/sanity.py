"""Step 5: compare model 2025 VariableCost (ao_dsl_foi_2025.csv, read-only extract) with benchmark 2024 + adder (adders_2024.csv).
Run: py -I sanity.py <output_folder>"""
import sys, os, pandas as pd
OUT = sys.argv[1]
m = pd.read_csv(os.path.join(OUT, "ao_dsl_foi_2025.csv"))
a = pd.read_csv(os.path.join(OUT, "adders_2024.csv"))
rows = []
for _, r in m.iterrows():
    x = a[(a.country == r.country) & (a.fuel == r.fuel)].iloc[0]
    est = x.pre_tax_price_2024_usd_per_gj
    skip = r.country == "Ecuador"
    rows.append(dict(country=r.country, tech=r.tech, fuel=r.fuel, model_2025_usd_per_gj=r.v2025, model_value_basis=r.v2025_basis,
                     benchmark_2024=x.benchmark_2024_usd_per_gj, adder=x.adder_usd_per_gj, import_parity_2024=est, adder_method=x.method,
                     ratio_model_to_parity=None if skip else round(r.v2025 / est, 3),
                     note="placeholder value of 1 in the model; skipped" if skip else ""))
s = pd.DataFrame(rows)
s.to_csv(os.path.join(OUT, "sanity_check_2025.csv"), index=False)
print(s.drop(columns=["model_value_basis"]).to_string())
