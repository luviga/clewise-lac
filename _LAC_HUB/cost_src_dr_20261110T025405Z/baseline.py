"""Step 1 and gate 1: SHA-256 of the DR A-O workbook and BAU cost CSVs."""
import hashlib, csv, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILES = [
    r"DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx",
] + [f"DominicanRepublic/RD_ENERGY/A2_Output_Params/BAU/{n}.csv" for n in
     ["CapitalCost", "FixedCost", "VariableCost", "InputActivityRatio", "OutputActivityRatio"]]
out = sys.argv[1]
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["file", "sha256", "bytes"])
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        w.writerow([rel, h, os.path.getsize(p)])
print(open(out, encoding="utf-8").read())
