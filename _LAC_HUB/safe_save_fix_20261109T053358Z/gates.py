"""Step 5 gates: Ecuador 451 year cells, backups, six A-O hashes."""
import csv, hashlib, json
from pathlib import Path
from openpyxl import load_workbook
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
def sha(p):
    h = hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()
res = {}
# Ecuador 451 deliberate plain-number year cells
wb = load_workbook(ROOT / "Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx")
rows = list(csv.DictReader(open(ROOT / "_LAC_HUB/formula_check_20261109T003529Z/step6_ecuador_451.csv", encoding="utf-8")))
bad = []
for r in rows:
    c = wb[r["sheet"]][r["cell"]]
    if c.data_type != "n" or c.value is None or float(c.value) != float(r["current_value"]):
        bad.append((r["sheet"], r["cell"], c.data_type, c.value, r["current_value"]))
res["ecuador_451_rows"] = len(rows); res["ecuador_451_still_plain_and_equal"] = len(rows) - len(bad); res["ecuador_451_bad"] = bad
# Backups
man = list(csv.DictReader(open(OUT / "backups/backup_manifest.csv", encoding="utf-8")))
res["backups"] = [{"backup": Path(m["backup"]).name, "sha_before": m["sha256_source_before_change"],
                   "sha_backup_now": sha(m["backup"]), "equal": m["sha256_source_before_change"] == sha(m["backup"])} for m in man]
# Six A-O hashes
hb = list(csv.DictReader(open(OUT / "ao_hashes_before.csv", encoding="utf-8")))
res["ao_hashes"] = [{"workbook": h["workbook"], "before": h["sha256_before"], "after": sha(ROOT / h["workbook"]),
                     "changed": h["sha256_before"] != sha(ROOT / h["workbook"])} for h in hb]
json.dump(res, open(OUT / "gates_result.json", "w"), indent=2)
print(json.dumps(res, indent=2))
