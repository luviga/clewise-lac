"""
apply_ao_edits.py — Apply A-O Parametrization edits from a control workbook.

Reads JAM_AO_BAU_edits.xlsx (or any compatibly-structured edits workbook),
locates the matching rows in A-O_Parametrization.xlsx "Primary Techs" sheet
by (Tech, Parameter), and overwrites the year-column values. A timestamped
backup of the A-O file is created before any writes. A before/after diff is
printed for every cell that changes.

USAGE:
    python apply_ao_edits.py \
        --ao-file "C:\\Users\\luisfernando\\Dropbox\\2_WORK\\MODELS_LAC_4\\Jamaica\\JAM_ENERGY\\A1_Outputs\\A-O_Parametrization.xlsx" \
        --edits-file JAM_AO_BAU_edits.xlsx

    # Dry run (no write, just show diff):
    python apply_ao_edits.py --ao-file ... --edits-file ... --dry-run

    # Skip backup (NOT recommended):
    python apply_ao_edits.py --ao-file ... --edits-file ... --no-backup

The script is idempotent: running it twice produces the same result.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # MODELS_LAC_5 root
from ao_safe_save import save_ao_safely  # Excel recalc + blank-formula guard

DEFAULT_AO_SHEET = "Primary Techs"
DEFAULT_EDITS_SHEET = "Edits"
ID_COLS = ["Country", "Tech", "Parameter",
           "Projection_Mode_Expected", "Unit_Expected", "Action"]


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Apply edits from a control workbook to A-O_Parametrization.xlsx.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--ao-file", required=True, type=Path,
                   help="Path to A-O_Parametrization.xlsx")
    p.add_argument("--edits-file", required=True, type=Path,
                   help="Path to the edits control workbook (e.g. JAM_AO_BAU_edits.xlsx)")
    p.add_argument("--ao-sheet", default=DEFAULT_AO_SHEET,
                   help=f"Sheet name in A-O file (default: {DEFAULT_AO_SHEET!r})")
    p.add_argument("--edits-sheet", default=DEFAULT_EDITS_SHEET,
                   help=f"Sheet name in edits file (default: {DEFAULT_EDITS_SHEET!r})")
    p.add_argument("--dry-run", action="store_true",
                   help="Print diff but do not modify the A-O file.")
    p.add_argument("--no-backup", action="store_true",
                   help="Skip making a backup of the A-O file. NOT recommended.")
    return p.parse_args()


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def make_backup(ao_path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = ao_path.with_name(f"{ao_path.stem}.bak_{stamp}{ao_path.suffix}")
    shutil.copy2(ao_path, bak)
    return bak


def read_edits(edits_path: Path, sheet: str) -> pd.DataFrame:
    df = pd.read_excel(edits_path, sheet_name=sheet)
    for col in ID_COLS:
        if col not in df.columns:
            fail(f"Edits sheet missing required column: {col!r}")
    # Year columns can be int or str; normalize to int.
    year_cols_raw = [c for c in df.columns if c not in ID_COLS and c != "Rationale"]
    year_cols = {}
    for c in year_cols_raw:
        try:
            y = int(c)
            year_cols[c] = y
        except (TypeError, ValueError):
            continue
    if not year_cols:
        fail("Edits sheet has no year columns (expected integer-named columns like 2021..2055).")
    df = df.rename(columns=year_cols)
    return df


def find_header_row(ws) -> int:
    """Return the 1-based row index that holds the column headers in Primary Techs.

    A-O Primary Techs has headers on row 1. We confirm by looking for 'Tech' and 'Parameter'.
    """
    for row_idx in range(1, 6):
        row_vals = [ws.cell(row=row_idx, column=c).value for c in range(1, 12)]
        if "Tech" in row_vals and "Parameter" in row_vals:
            return row_idx
    fail("Could not find header row in A-O Primary Techs (expected 'Tech' and 'Parameter' columns).")


def header_map(ws, header_row: int) -> dict:
    """Return a {column_name: column_index_1based} map for the AO sheet."""
    out = {}
    col = 1
    while True:
        v = ws.cell(row=header_row, column=col).value
        if v is None and col > 50:
            break
        if v is not None:
            out[v] = col
        col += 1
        if col > 200:
            break
    return out


def find_target_row(ws, header_row: int, hmap: dict, tech: str, parameter: str) -> int | None:
    tech_col = hmap.get("Tech")
    param_col = hmap.get("Parameter")
    if tech_col is None or param_col is None:
        fail("A-O Primary Techs missing Tech/Parameter columns.")
    for r in range(header_row + 1, ws.max_row + 1):
        if (ws.cell(row=r, column=tech_col).value == tech
                and ws.cell(row=r, column=param_col).value == parameter):
            return r
    return None


# --------------------------------------------------------------------------- #
# Apply
# --------------------------------------------------------------------------- #

def apply_edits(ws, hmap: dict, header_row: int, edits_df: pd.DataFrame,
                dry_run: bool) -> tuple[int, int, list]:
    """Apply each edit row. Returns (rows_changed, cells_changed, warnings)."""
    warnings = []
    rows_changed = 0
    cells_changed = 0

    year_cols = sorted(c for c in edits_df.columns if isinstance(c, int))
    if not year_cols:
        fail("No year columns found in edits dataframe after parsing.")

    proj_col = hmap.get("Projection.Mode")
    unit_col = hmap.get("Unit")

    for _, e in edits_df.iterrows():
        tech = e["Tech"]
        parameter = e["Parameter"]
        expected_mode = str(e["Projection_Mode_Expected"]).strip()
        expected_unit = str(e["Unit_Expected"]).strip()

        r = find_target_row(ws, header_row, hmap, tech, parameter)
        if r is None:
            warnings.append(f"NOT FOUND: ({tech}, {parameter}) — skipped.")
            continue

        # Sanity-check Projection.Mode and Unit
        if proj_col is not None:
            actual_mode = ws.cell(row=r, column=proj_col).value
            if str(actual_mode).strip() != expected_mode:
                warnings.append(
                    f"WARN: {tech} {parameter} Projection.Mode is "
                    f"{actual_mode!r}, expected {expected_mode!r}. "
                    f"Proceeding but verify intent."
                )
        if unit_col is not None:
            actual_unit = ws.cell(row=r, column=unit_col).value
            if actual_unit is not None and str(actual_unit).strip() != expected_unit:
                warnings.append(
                    f"WARN: {tech} {parameter} Unit is "
                    f"{actual_unit!r}, expected {expected_unit!r}."
                )

        any_cell_changed = False
        for y in year_cols:
            target_col = hmap.get(y)
            if target_col is None:
                continue  # AO doesn't have this year column
            new_v = e[y]
            try:
                new_v = float(new_v) if new_v is not None and not pd.isna(new_v) else 0.0
            except (TypeError, ValueError):
                new_v = 0.0
            old_v = ws.cell(row=r, column=target_col).value
            try:
                old_f = float(old_v) if old_v is not None else 0.0
            except (TypeError, ValueError):
                old_f = 0.0
            if abs(old_f - new_v) > 1e-12:
                arrow = "→"
                print(f"  {tech:>10s} {parameter:<32s} {y}: "
                      f"{old_f:>8.4f} {arrow} {new_v:>8.4f}")
                if not dry_run:
                    ws.cell(row=r, column=target_col).value = new_v
                cells_changed += 1
                any_cell_changed = True
            else:
                pass  # silent no-op
        if any_cell_changed:
            rows_changed += 1

    return rows_changed, cells_changed, warnings


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> int:
    args = parse_args()

    if not args.ao_file.exists():
        fail(f"A-O file does not exist: {args.ao_file}")
    if not args.edits_file.exists():
        fail(f"Edits file does not exist: {args.edits_file}")

    print(f"A-O file:    {args.ao_file}")
    print(f"Edits file:  {args.edits_file}")
    print(f"A-O sheet:   {args.ao_sheet!r}")
    print(f"Edits sheet: {args.edits_sheet!r}")
    print(f"Dry run:     {args.dry_run}")
    print()

    edits_df = read_edits(args.edits_file, args.edits_sheet)
    print(f"Loaded {len(edits_df)} edit row(s) from {args.edits_file.name}")

    if not args.dry_run and not args.no_backup:
        bak = make_backup(args.ao_file)
        print(f"Backup:      {bak.name}")

    print()
    print("Opening A-O workbook (this preserves formatting)...")
    wb = load_workbook(args.ao_file)
    if args.ao_sheet not in wb.sheetnames:
        fail(f"Sheet {args.ao_sheet!r} not found in A-O file. "
             f"Available: {wb.sheetnames}")
    ws = wb[args.ao_sheet]

    header_row = find_header_row(ws)
    hmap = header_map(ws, header_row)
    print(f"Header row in A-O = {header_row}")
    year_cols_present = sorted([k for k in hmap if isinstance(k, int)])
    print(f"Year columns present in A-O: {year_cols_present[0]}..{year_cols_present[-1]} "
          f"({len(year_cols_present)} years)")
    print()

    print("Diff (cells that will change):")
    rows_changed, cells_changed, warnings = apply_edits(
        ws, hmap, header_row, edits_df, dry_run=args.dry_run
    )

    print()
    print(f"Summary: {rows_changed} row(s) changed, {cells_changed} cell(s) changed.")

    if warnings:
        print()
        print("Warnings:")
        for w in warnings:
            print(f"  • {w}")

    if args.dry_run:
        print()
        print("Dry run — no file written.")
        return 0

    if cells_changed == 0:
        print()
        print("No changes to write. A-O file untouched.")
        return 0

    print()
    print(f"Saving {args.ao_file}...")
    save_ao_safely(wb, args.ao_file)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
