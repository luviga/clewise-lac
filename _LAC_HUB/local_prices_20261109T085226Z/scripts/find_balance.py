"""Scan tracked text and xlsx files in the six energy folders for energy balance names (leads for Step 3).
Usage: py -I find_balance.py <repo_root> <out_txt>
Output lists file, sheet and matching text; it is a lead list only, never a citation."""
import sys, re, subprocess, os
import openpyxl

root, out = sys.argv[1], sys.argv[2]
DIRS = ["CostaRica/CR_ENERGY", "DominicanRepublic/RD_ENERGY", "Ecuador/ECU_Energy", "Guatemala/GUA_ENERGY",
        "Honduras/HON_ENERGY", "Jamaica/JAM_ENERGY"]
PAT = re.compile(r"(?i)(sielac|olade|balance energ|balance nacional|energy balance|\bBEN\b|poder calor|calorific"
                 r"|heat content|\bIEA\b|STATIN|MSET|\bPCJ\b|\bSEN\b|MINEM|\bMEM\b|\bCNE\b|Secretar[ií]a|SEPSE|MINAE)")
files = subprocess.run(["git", "-C", root, "ls-files"] + DIRS, capture_output=True, text=True).stdout.split("\n")
hits = []
for f in files:
    if not f or "/Executables/" in f:
        continue
    p = os.path.join(root, f)
    if f.endswith((".txt", ".md", ".py", ".csv")) and os.path.getsize(p) < 3e6:
        for n, line in enumerate(open(p, encoding="utf-8", errors="ignore"), 1):
            if PAT.search(line) and "EnergyBalance" not in line:
                hits.append(f"{f}:{n}: {line.strip()[:200]}")
    elif f.endswith(".xlsx") and os.path.getsize(p) < 3e7:
        try:
            wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        except Exception as e:
            hits.append(f"{f}: open failed {e}")
            continue
        for ws in wb.worksheets:
            if PAT.search(ws.title):
                hits.append(f"{f}[{ws.title}] sheet title")
            for r in ws.iter_rows(values_only=True):
                for v in r:
                    if isinstance(v, str) and PAT.search(v):
                        hits.append(f"{f}[{ws.title}]: {v.strip()[:200]}")
seen, uniq = set(), []
for h in hits:
    if h not in seen:
        seen.add(h)
        uniq.append(h)
open(out, "w", encoding="utf-8").write("\n".join(uniq))
print(len(uniq), "unique hits")
