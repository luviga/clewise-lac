# Phase C step C3: the Stage 2 demand check tool reads its scenario list from the catalogue (applied with --target work).
V = "stage2_demand_verify.py"
EDITS = [
    (V, "from pathlib import Path\n", "from pathlib import Path\n\nimport lac_tables as LT  # scenario names from config/scenarios/scenario_catalogue.csv\n"),
    (V, 'SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]', "SCENARIOS = LT.scenarios()"),
    (V, "Reports any differences in SpecifiedAnnualDemand across BAU/NDCNEW/LTSNEW.", "Reports any differences in SpecifiedAnnualDemand across BAU/NDC/LTS."),
    (V, 'print(f"  Copy the BAU demand block to NDCNEW/LTSNEW for years', 'print(f"  Copy the BAU demand block to NDC/LTS for years'),
]
