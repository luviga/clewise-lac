"""Phase C3 and C4 (LAC_OVERNIGHT_COST_RUN).

  backup        copy the six A-O_Parametrization.xlsx and Costa Rica A-O_Demand.xlsx to
                backups/ (gitignored) and write a SHA-256 manifest
  apply C       run ao_cost_repair_manager.py apply (then verify) for country C
  d9            write D9 (Costa Rica A-O_Demand.xlsx, Demand_Projection!M25) with
                openpyxl and save_ao_safely, after checking the row label and value
  check         gates C4(1) to C4(4); writes write_check.csv
"""
from __future__ import annotations

import csv
import hashlib
import math
import shutil
import subprocess
import sys
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(r"C:\clw_overnight")
JOB = ROOT / "_LAC_HUB" / "cost_write_run_20261111T071733Z"
BK = JOB / "backups"
sys.path.insert(0, str(ROOT))
MODEL = {"CostaRica": "CostaRica/CR_ENERGY/t1_confection", "DominicanRepublic": "DominicanRepublic/RD_ENERGY",
         "Ecuador": "Ecuador/ECU_Energy", "Guatemala": "Guatemala/GUA_ENERGY", "Honduras": "Honduras/HON_ENERGY",
         "Jamaica": "Jamaica/JAM_ENERGY"}
WBS = {c: f"{d}/A1_Outputs/A-O_Parametrization.xlsx" for c, d in MODEL.items()}
DEMAND = "CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Demand.xlsx"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def backup_name(rel):
    return rel.replace("/", "__")


def cmd_backup():
    BK.mkdir(parents=True, exist_ok=True)
    rows = []
    for rel in list(WBS.values()) + [DEMAND]:
        src = ROOT / rel
        dst = BK / backup_name(rel)
        shutil.copy2(src, dst)
        h1, h2 = sha(src), sha(dst)
        assert h1 == h2
        rows.append((rel, backup_name(rel), h1, src.stat().st_size))
    with open(BK / "SHA256SUMS.txt", "w", newline="\n") as fh:
        for rel, name, h, _ in rows:
            fh.write(f"{h}  {name}\n")
    with open(JOB / "backup_manifest.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["workbook", "backup_file", "sha256", "bytes"])
        for r in rows:
            w.writerow(r)
    print("backed up", len(rows))


def cmd_apply(country):
    man = JOB / f"manifest_{country}.csv"
    log = JOB / f"apply_{country}.log"
    with open(log, "w", newline="\n") as fh:
        for args in (["apply", "--manifest", str(man), "--apply", "--output-dir", str(JOB)],
                     ["verify", "--manifest", str(man), "--expect", "applied"]):
            fh.write(f"$ py -I ao_cost_repair_manager.py {' '.join(a if not a.startswith('C:') else Path(a).name for a in args)}\n")
            fh.flush()
            p = subprocess.run([sys.executable, "-I", "ao_cost_repair_manager.py", *args], cwd=ROOT,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            out = p.stdout.replace(str(ROOT), "<clone>").replace(str(ROOT).replace("\\", "/"), "<clone>")
            fh.write(out)
            fh.write(f"[exit {p.returncode}]\n")
            print(out)
            if p.returncode != 0:
                raise SystemExit(f"{args[0]} failed for {country}")


def cmd_d9():
    from ao_safe_save import save_ao_safely
    path = ROOT / DEMAND
    wb = openpyxl.load_workbook(path, data_only=False)
    ws = wb["Demand_Projection"]
    assert ws["M1"].value == 2021, ws["M1"].value
    assert ws["B25"].value == "E5INDCOA", ws["B25"].value
    assert ws["A25"].value == "Demand", ws["A25"].value
    assert abs(float(ws["M25"].value) - 0.675) < 1e-12, ws["M25"].value
    ws["M25"].value = 0.00667
    save_ao_safely(wb, path)
    wv = openpyxl.load_workbook(path, data_only=True)
    assert abs(wv["Demand_Projection"]["M25"].value - 0.00667) < 1e-15
    with open(JOB / "apply_D9.log", "w", newline="\n") as fh:
        fh.write("D9: CostaRica A-O_Demand.xlsx Demand_Projection row 25 (Demand, E5INDCOA, Demand Industrial Coal), "
                 "column 2021 (M25): 0.675 -> 0.00667 PJ (CRC-006); saved through save_ao_safely\n")
    print("D9 written")


def _cells(path):
    wf = openpyxl.load_workbook(path, data_only=False)
    wv = openpyxl.load_workbook(path, data_only=True)
    out = {}
    for ws in wf.worksheets:
        v = wv[ws.title]
        for row in ws.iter_rows():
            for c in row:
                raw = c.value
                val = v[c.coordinate].value
                if raw is None and val is None:
                    continue
                out[(ws.title, c.coordinate)] = (raw, val, c.data_type == "f")
    return out


def _same(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        if a == b:
            return True
        return abs(a - b) <= 1e-12 * max(abs(a), abs(b))
    return a == b


def cmd_check():
    from ao_safe_save import find_blank_formula_cells
    ws_ = pd.read_csv(JOB / "write_set.csv", keep_default_na=False)
    rows_out = []
    summary = []
    # C4(1)
    g1_bad = 0
    for c, rel in WBS.items():
        sub = ws_[ws_.country == c]
        wv = openpyxl.load_workbook(ROOT / rel, data_only=True)
        wf = openpyxl.load_workbook(ROOT / rel, data_only=False)
        for r in sub.itertuples():
            got = wv[r.sheet][f"{r.column}{r.row_index}"].value
            raw = wf[r.sheet][f"{r.column}{r.row_index}"].value
            want = float(r.value_to_write)
            ok = isinstance(got, (int, float)) and (got == want or abs(got - want) <= 1e-9 * max(abs(want), abs(got)))
            if not ok:
                g1_bad += 1
            rows_out.append(dict(gate="C4(1) written value", country=c, workbook=rel, sheet=r.sheet,
                                 cell=f"{r.column}{r.row_index}", tech=r.tech, parameter=r.parameter, year=r.year,
                                 expected=repr(want), found=repr(got), raw=repr(raw)[:60],
                                 result="pass" if ok else "FAIL"))
    summary.append(("C4(1) every written cell equals write_set.csv to 1e-9 relative",
                    f"{len(ws_) - g1_bad} of {len(ws_)} pass", "pass" if g1_bad == 0 else "FAIL"))
    # C4(2) before/after
    man_cells = {(r.country, r.sheet, f"{r.column}{r.row_index}") for r in ws_.itertuples()}
    mode_cells = set()
    for c, rel in WBS.items():
        wf = openpyxl.load_workbook(BK / Path(rel).as_posix().replace("/", "__"), data_only=False, read_only=True)
        for sh in ("Primary Techs", "Secondary Techs"):
            ws = wf[sh]
            hdr = [x.value for x in next(ws.iter_rows(min_row=1, max_row=1))]
            mcol = openpyxl.utils.get_column_letter(hdr.index("Projection.Mode") + 1)
            for r in ws_[(ws_.country == c) & (ws_.sheet == sh) & (ws_.projection_mode_new != "")].row_index.unique():
                mode_cells.add((c, sh, f"{mcol}{r}"))
        wf.close()
    counts = {"manifest value": 0, "D8 mode": 0, "D9": 0, "formula recalculated (text unchanged)": 0,
              "formula text normalised by Excel (value unchanged)": 0, "other": 0}
    for c, rel in list(WBS.items()) + [("CostaRica-demand", DEMAND)]:
        before = _cells(BK / backup_name(rel))
        after = _cells(ROOT / rel)
        cc = "CostaRica" if c == "CostaRica-demand" else c
        for k in sorted(set(before) | set(after)):
            b = before.get(k, (None, None, False))
            a = after.get(k, (None, None, False))
            raw_same = _same(b[0], a[0])
            val_same = _same(b[1], a[1])
            if raw_same and val_same:
                continue
            sheet, cell = k
            if c == "CostaRica-demand" and sheet == "Demand_Projection" and cell == "M25":
                cls = "D9"
            elif (cc, sheet, cell) in man_cells:
                cls = "manifest value"
            elif (cc, sheet, cell) in mode_cells:
                cls = "D8 mode"
            elif raw_same and a[2]:
                cls = "formula recalculated (text unchanged)"
            elif (b[2] and a[2] and isinstance(b[0], str) and isinstance(a[0], str)
                  and b[0].replace(" ", "") == a[0].replace(" ", "") and val_same):
                cls = "formula text normalised by Excel (value unchanged)"
            else:
                cls = "other"
            counts[cls] += 1
            if cls in ("manifest value", "D8 mode", "D9"):
                continue  # covered by C4(1) rows or listed below in summary
            rows_out.append(dict(gate="C4(2) cell changed", country=cc, workbook=rel, sheet=sheet, cell=cell,
                                 tech="", parameter="", year="", expected=repr(b[0])[:60] + " / " + repr(b[1])[:40],
                                 found=repr(a[0])[:60] + " / " + repr(a[1])[:40], raw="",
                                 result=cls if cls != "other" else "FAIL other change"))
    summary.append(("C4(2) changes only at manifest cells, D8 mode cells and D9 cell M25",
                    "; ".join(f"{k}: {v}" for k, v in counts.items()),
                    "pass" if sum(v for k, v in counts.items() if k not in ("manifest value", "D8 mode", "D9")) == 0
                    else "FAIL (strict reading): formula cells outside the manifest changed, see write_check.csv"))
    # C4(3)
    blanks_total = 0
    for rel in list(WBS.values()) + [DEMAND]:
        b = find_blank_formula_cells(ROOT / rel)
        blanks_total += len(b)
        rows_out.append(dict(gate="C4(3) blank formula cells", country="", workbook=rel, sheet="", cell="",
                             tech="", parameter="", year="", expected="0", found=str(len(b)), raw="",
                             result="pass" if not b else "FAIL"))
    summary.append(("C4(3) zero formula cells without a stored value in every changed workbook",
                    f"{blanks_total} blank in 7 workbooks", "pass" if blanks_total == 0 else "FAIL"))
    # C4(4) every other tracked A-O workbook byte-identical to HEAD
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    ao = [f for f in files if Path(f).name.startswith("A-O_") and f.endswith(".xlsx")
          and f not in set(WBS.values()) | {DEMAND}]
    all_changed = set(subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, capture_output=True,
                                     text=True).stdout.splitlines())
    changed = [f for f in ao if f in all_changed]
    aop = [f for f in ao if Path(f).name == "A-O_Parametrization.xlsx"]
    summary.append(("C4(4) other A-O workbooks byte-identical",
                    f"{len(ao) - len(changed)} of {len(ao)} other tracked A-O_*.xlsx files identical to HEAD "
                    f"(including {len(aop)} other A-O_Parametrization.xlsx: {len(aop) - len(set(changed) & set(aop))} "
                    f"identical)", "pass" if not changed else "FAIL"))
    for f in changed:
        rows_out.append(dict(gate="C4(4) other workbook changed", country="", workbook=f, sheet="", cell="",
                             tech="", parameter="", year="", expected="identical", found="changed", raw="",
                             result="FAIL"))
    fields = ["gate", "country", "workbook", "sheet", "cell", "tech", "parameter", "year", "expected", "found", "raw",
              "result"]
    with open(JOB / "write_check.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows_out:
            w.writerow(r)
    with open(JOB / "write_check_summary.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["gate", "count", "result"])
        for s in summary:
            w.writerow(s)
    for s in summary:
        print(s)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "backup":
        cmd_backup()
    elif cmd == "apply":
        cmd_apply(sys.argv[2])
    elif cmd == "d9":
        cmd_d9()
    elif cmd == "check":
        cmd_check()
