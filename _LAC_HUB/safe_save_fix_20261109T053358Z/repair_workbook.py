"""Steps 3 and 4: back up, recalculate in Excel, guard, and check one A-O workbook.

Usage: py -I -B repair_workbook.py <Country> [--check-only]
Writes <country>_*.csv/json into this folder. Never edits a cell by hand.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from openpyxl import load_workbook

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT))
from ao_safe_save import (  # noqa: E402
    BlankFormulaError, assert_no_blank_formula_cells, find_blank_formula_cells, recalc_in_excel,
)

STAMP = "20261109T053358Z"
WORKBOOKS = {
    "Jamaica": ROOT / "Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx",
    "Ecuador": ROOT / "Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx",
}
FORMULA_CSV = ROOT / "_LAC_HUB/formula_check_20261109T003529Z/formula_cells.csv"
ERRORS = {"#DIV/0!", "#N/A", "#NAME?", "#NULL!", "#NUM!", "#REF!", "#VALUE!"}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def snapshot(path: Path):
    """{(sheet, coord): (raw, cached)} for every non-empty cell, plus sheet list."""
    wf = load_workbook(path, data_only=False)
    wv = load_workbook(path, data_only=True)
    cells = {}
    for ws in wf.worksheets:
        wsv = wv[ws.title]
        for row in ws.iter_rows():
            for c in row:
                if c.value is None:
                    continue
                raw = c.value
                if c.data_type == "f" and not isinstance(raw, str):
                    raw = "ARRAY:" + str(getattr(raw, "text", raw))
                cells[(ws.title, c.coordinate)] = (raw, wsv[c.coordinate].value, c.data_type == "f")
    sheets = wf.sheetnames
    wf.close(); wv.close()
    return sheets, cells


def r4(x):
    """A2 rounding: numpy half-to-even at 4 decimals."""
    return float(np.round(float(x), 4))


def to_num(x):
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    try:
        return float(str(x).strip())
    except (TypeError, ValueError):
        return None


def same(a, b) -> bool:
    na, nb = to_num(a), to_num(b)
    if na is not None and nb is not None:
        return r4(na) == r4(nb)
    return str(a).strip() == str(b).strip()


def main():
    country = sys.argv[1]
    check_only = "--check-only" in sys.argv
    path = WORKBOOKS[country]
    tag = country.lower()
    result = {"country": country, "path": str(path), "check_only": check_only}

    # Before
    result["sha256_before"] = sha(path)
    sheets_b, cells_b = snapshot(path)
    blanks_before = find_blank_formula_cells(path)
    result["formula_cells_before"] = sum(1 for v in cells_b.values() if v[2])
    result["blank_formula_cells_before"] = len(blanks_before)

    if not check_only:
        # Backup (refuse to continue if the copy is not identical)
        r = subprocess.run([sys.executable, "-I", "-B", str(OUT / "backup.py"), f"--prefix={country}_", str(path)],
                           capture_output=True, text=True)
        print(r.stdout, r.stderr)
        if r.returncode != 0 or not r.stdout.strip().endswith("True"):
            raise SystemExit("backup failed, workbook not touched")
        # Both workbooks share a file name, so the backup name carries a country prefix.
        named = OUT / "backups" / f"{country}_{path.name}.pre_{STAMP}"
        result["backup"] = str(named)
        result["sha256_backup"] = sha(named)
        result["backup_equals_before"] = result["sha256_backup"] == result["sha256_before"]
        if not result["backup_equals_before"]:
            raise SystemExit("backup hash mismatch, workbook not touched")

        t0 = datetime.now(timezone.utc)
        recalc_in_excel(path)
        result["recalc_utc"] = t0.strftime("%Y-%m-%dT%H:%M:%SZ")
        result["excel_com_used"] = True

    result["sha256_after"] = sha(path)

    # Guard
    try:
        n, _ = assert_no_blank_formula_cells(path)
        result["blank_formula_cells_after"] = n
        result["guard"] = "PASS"
    except BlankFormulaError as exc:
        result["blank_formula_cells_after"] = len(exc.blanks)
        result["guard"] = "FAIL"
        result["guard_blanks_first_50"] = exc.blanks[:50]

    # Structure and preservation checks
    sheets_a, cells_a = snapshot(path)
    result["sheets_unchanged"] = sheets_a == sheets_b
    f_b = {k: v[0] for k, v in cells_b.items() if v[2]}
    f_a = {k: v[0] for k, v in cells_a.items() if v[2]}
    result["formula_cells_after"] = len(f_a)
    result["formula_cell_set_unchanged"] = set(f_b) == set(f_a)
    ftext_diff = [(k, f_b[k], f_a.get(k)) for k in f_b if f_a.get(k) != f_b[k]]
    result["formula_text_changed"] = len(ftext_diff)

    plain_b = {k: v[0] for k, v in cells_b.items() if not v[2]}
    plain_a = {k: v[0] for k, v in cells_a.items() if not v[2]}
    plain_diff = []
    for k in set(plain_b) | set(plain_a):
        a, b = plain_b.get(k), plain_a.get(k)
        if a == b:
            continue
        na, nb = to_num(a), to_num(b)
        if na is not None and nb is not None and na == nb:
            continue  # same number, only int/float type differs
        plain_diff.append((k, a, b))
    result["plain_cells_before"] = len(plain_b)
    result["plain_cells_after"] = len(plain_a)
    result["plain_cells_changed_exact"] = len(plain_diff)

    errors_after = [(k, v[1]) for k, v in cells_a.items() if v[2] and isinstance(v[1], str) and v[1] in ERRORS]
    result["formula_cells_with_excel_error"] = len(errors_after)

    # Intended-value check
    rows = [r for r in csv.DictReader(open(FORMULA_CSV, newline="", encoding="utf-8")) if r["country"] == country]
    result["intended_rows"] = len(rows)
    agree, mism = 0, []
    for r in rows:
        k = (r["sheet"], r["cell"])
        restored = cells_a.get(k, (None, None, False))
        if not restored[2]:
            mism.append({**{x: r[x] for x in ("sheet", "cell", "formula", "intended_value")},
                         "restored_value": restored[1], "why": "not a formula cell after recalc"})
            continue
        if restored[1] is not None and same(restored[1], r["intended_value"]):
            agree += 1
        else:
            mism.append({**{x: r[x] for x in ("sheet", "cell", "formula", "intended_value")},
                         "restored_value": restored[1], "why": "value differs"})
    result["intended_agree"] = agree
    result["intended_mismatch"] = len(mism)
    # Formula cells in the workbook that the CSV does not cover
    csv_keys = {(r["sheet"], r["cell"]) for r in rows}
    result["formula_cells_not_in_csv"] = len([k for k in f_a if k not in csv_keys])

    # Detail files
    with open(OUT / f"{tag}_intended_check.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sheet", "cell", "formula", "restored_value", "intended_value",
                    "restored_r4", "intended_r4", "equal"])
        for r in rows:
            k = (r["sheet"], r["cell"])
            v = cells_a.get(k, (None, None, False))[1]
            nv, ni = to_num(v), to_num(r["intended_value"])
            w.writerow([r["sheet"], r["cell"], r["formula"], v, r["intended_value"],
                        r4(nv) if nv is not None else "", r4(ni) if ni is not None else "",
                        v is not None and same(v, r["intended_value"])])
    with open(OUT / f"{tag}_mismatches.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["sheet", "cell", "formula", "restored_value", "intended_value", "why"])
        w.writeheader(); w.writerows(mism)
    with open(OUT / f"{tag}_preservation_diffs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kind", "sheet", "cell", "before", "after"])
        for k, a, b in ftext_diff:
            w.writerow(["formula_text", k[0], k[1], a, b])
        for k, a, b in sorted(plain_diff):
            w.writerow(["plain_value", k[0], k[1], repr(a), repr(b)])
        for k, v in errors_after:
            w.writerow(["excel_error", k[0], k[1], "", v])
    with open(OUT / f"{tag}_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
