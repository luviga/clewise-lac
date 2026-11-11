"""Steps 1 and 9: SHA-256 of the Honduras A-O workbook and the BAU cost and activity ratio CSVs. Usage: py -I baseline.py before|after"""
import hashlib, sys
from pathlib import Path
HERE = Path(__file__).parent
ROOT = HERE.parents[1]
FILES = ["Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx"] + [f"Honduras/HON_ENERGY/A2_Output_Params/BAU/{n}.csv" for n in
         ("CapitalCost", "FixedCost", "VariableCost", "InputActivityRatio", "OutputActivityRatio")]
lines = ["file,sha256"] + [f"{f},{hashlib.sha256((ROOT / f).read_bytes()).hexdigest()}" for f in FILES]
(HERE / f"baseline_{sys.argv[1]}.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
