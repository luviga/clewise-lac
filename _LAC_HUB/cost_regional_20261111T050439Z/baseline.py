"""Hash the six A-O workbooks and every BAU A2_Output_Params CSV (read-only gate 1)."""
import hashlib, sys, os, glob, csv
ROOT = sys.argv[1]; OUT = sys.argv[2]
DIRS = ["CostaRica/CR_ENERGY/t1_confection", "DominicanRepublic/RD_ENERGY", "Ecuador/ECU_Energy",
        "Guatemala/GUA_ENERGY", "Honduras/HON_ENERGY", "Jamaica/JAM_ENERGY"]
rows = []
for d in DIRS:
    files = [d + "/A1_Outputs/A-O_Parametrization.xlsx"]
    files += sorted(os.path.relpath(p, ROOT).replace("\\", "/") for p in glob.glob(os.path.join(ROOT, d, "A2_Output_Params", "BAU", "*.csv")))
    for f in files:
        h = hashlib.sha256(open(os.path.join(ROOT, f), "rb").read()).hexdigest()
        rows.append((f, h))
with open(OUT, "w", newline="\n") as fh:
    w = csv.writer(fh, lineterminator="\n"); w.writerow(["file", "sha256"]); w.writerows(rows)
print(len(rows), "files hashed")
