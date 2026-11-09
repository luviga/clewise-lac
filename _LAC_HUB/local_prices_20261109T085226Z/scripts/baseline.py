"""SHA-256 of the six energy A-O workbooks and BAU ratio files. Usage: py -I baseline.py <repo_root> <out_csv>"""
import hashlib, sys, csv, os
root, out = sys.argv[1], sys.argv[2]
FOLDERS = ["CostaRica/CR_ENERGY/t1_confection", "DominicanRepublic/RD_ENERGY", "Ecuador/ECU_Energy",
           "Guatemala/GUA_ENERGY", "Honduras/HON_ENERGY", "Jamaica/JAM_ENERGY"]
FILES = ["A1_Outputs/A-O_Parametrization.xlsx", "A2_Output_Params/BAU/InputActivityRatio.csv",
         "A2_Output_Params/BAU/OutputActivityRatio.csv"]
rows = []
for f in FOLDERS:
    for g in FILES:
        rel = f + "/" + g
        with open(os.path.join(root, rel), "rb") as fh:
            rows.append((rel, hashlib.sha256(fh.read()).hexdigest()))
with open(out, "w", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n"); w.writerow(["file", "sha256"]); w.writerows(rows)
print(len(rows), "files hashed")
