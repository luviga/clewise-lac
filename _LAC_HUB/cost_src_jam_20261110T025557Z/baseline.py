"""Record SHA-256 of the Jamaica model files this job must leave untouched."""
import csv, hashlib, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
FILES = ["Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx"] + [
    f"Jamaica/JAM_ENERGY/A2_Output_Params/BAU/{n}.csv" for n in
    ["CapitalCost", "FixedCost", "VariableCost", "InputActivityRatio", "OutputActivityRatio"]]
out = Path(__file__).parent / sys.argv[1]
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["file", "sha256", "bytes"])
    for rel in FILES:
        p = REPO / rel; b = p.read_bytes()
        w.writerow([rel, hashlib.sha256(b).hexdigest(), len(b)])
print(out.read_text())
