"""Supporting check for Step 4: count rows with an empty Value or empty TECHNOLOGY in every A2_Output_Params
and B1_Output_Params CSV, and say how many of the empty-Value rows match a formula cell. Read-only."""
import os, glob
import pandas as pd
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
OUT = os.path.dirname(os.path.abspath(__file__))
ENERGY = {"CostaRica": r"CostaRica\CR_ENERGY\t1_confection", "DominicanRepublic": r"DominicanRepublic\RD_ENERGY",
          "Ecuador": r"Ecuador\ECU_Energy", "Guatemala": r"Guatemala\GUA_ENERGY",
          "Honduras": r"Honduras\HON_ENERGY", "Jamaica": r"Jamaica\JAM_ENERGY"}
fc = pd.read_csv(os.path.join(OUT, "formula_cells.csv"))
fkeys = {(r.country, r.parameter, r.tech, int(r.year)) for r in fc.itertuples() if pd.notna(r.year)}
rows = []
for c, d in ENERGY.items():
    for sub in ["A2_Output_Params", "B1_Output_Params"]:
        for p in sorted(glob.glob(os.path.join(ROOT, d, sub, "*", "*.csv"))):
            df = pd.read_csv(p, dtype={"TECHNOLOGY": str})
            if "Value" not in df.columns: continue
            ev = df[df.Value.isna()]
            et = df[df.TECHNOLOGY.isna()] if "TECHNOLOGY" in df.columns and df.PARAMETER.iloc[0:1].isin(
                ["CapitalCost", "FixedCost", "VariableCost", "ResidualCapacity", "TotalAnnualMaxCapacity", "CapacityFactor",
                 "AvailabilityFactor", "TotalTechnologyAnnualActivityLowerLimit", "TotalTechnologyAnnualActivityUpperLimit",
                 "TotalAnnualMinCapacityInvestment", "TotalAnnualMaxCapacityInvestment", "TotalAnnualMinCapacity",
                 "OperationalLife", "CapacityToActivityUnit"]).any() else df.iloc[0:0]
            if len(ev) or len(et):
                m = sum((c, r.PARAMETER, r.TECHNOLOGY, int(r.YEAR)) in fkeys for r in ev.itertuples() if pd.notna(r.YEAR))
                rows.append({"country": c, "folder": sub, "scenario": os.path.basename(os.path.dirname(p)), "file": os.path.basename(p),
                             "rows_empty_value": len(ev), "of_which_match_formula_cell": m, "rows_empty_technology": len(et),
                             "techs_with_empty_value": ";".join(sorted(set(ev.TECHNOLOGY.dropna())))})
r = pd.DataFrame(rows); r.to_csv(os.path.join(OUT, "empty_values_scan.csv"), index=False)
print(r.to_string() if len(r) else "no empty values")
