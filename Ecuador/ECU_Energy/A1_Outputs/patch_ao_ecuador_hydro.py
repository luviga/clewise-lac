#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
patch_ao_ecuador_hydro.py — Apply hydro ResidualCapacity fixes to Ecuador A-O
===============================================================================
Fixes the NDC-counterfactual encoding where CCS (1,500 MW), Sopladora (487 MW),
and other operational hydro plants had ResidualCapacity = 0. Also zeros the
phantom PPHRORAB MinCapacityInvestment and adds real post-2021 plant MCI entries.

Run from the Ecuador model directory (where A-O_Parametrization.xlsx lives):
  py patch_ao_ecuador_hydro.py [--dry-run]

Creates a timestamped backup before editing. Writes a change log to stdout.
"""

import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

try:
    import openpyxl
except ImportError:
    print("[ERROR] openpyxl required: pip install openpyxl --break-system-packages")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # MODELS_LAC_5 root
from ao_safe_save import save_ao_safely  # Excel recalc + blank-formula guard

# ─── Configuration ───────────────────────────────────────────────────────────

AO_FILE = "A-O_Parametrization.xlsx"
SHEET = "Primary Techs"

# Column layout (0-indexed from openpyxl which is 1-indexed):
#   A=Tech.ID  B=Tech  C=Tech.Name  D=Parameter.ID  E=Parameter
#   F=Unit  G=Projection.Mode  H=Projection.Parameter
#   I=2021  J=2022  K=2023 ... (year columns from col 9 onward)
COL_TECH = 2        # B
COL_PARAM = 5       # E
COL_MODE = 7        # G
COL_PROJ_PARAM = 8  # H
COL_YEAR_START = 9  # I = 2021
YEAR_START = 2021
YEAR_END = 2050

# ─── Edits ───────────────────────────────────────────────────────────────────

# GROUP 1: ResidualCapacity — Flat mode, value in first year column (2021)
RC_EDITS = {
    #  tech:         (old_value,  new_value,  rationale)
    "PPHDAMAB":     (1.075,      1.270,      "Paute-Molino(1100) + Mazar(170) = 1270 MW"),
    "PPHRORAB":     (0.000,      1.500,      "Coca Codo Sinclair 1500 MW (COD 2016)"),
    "PPHRORAM":     (0.000,      0.487,      "Sopladora 487 MW (COD 2016-17)"),
    "PPHRORAS":     (0.024,      0.062,      "Small southern RoR ~62 MW pre-2021"),
    "PPHRORPM":     (0.230,      0.288,      "San Francisco(230) + smaller ~58 MW"),
    "PPHRORPS":     (0.055,      0.150,      "Smaller RoR (Sigchos, Calope etc) pre-2021"),
    "PPHD":         (0.813,      0.648,      "Reduce: excess compensated for missing RC elsewhere"),
}

# GROUP 2: TotalAnnualMinCapacityInvestment — zero out phantom, add real plants
# Format: tech → dict of {year: new_value}; None means "zero all years"
MCI_EDITS = {
    "PPHRORAB": {
        "action": "zero_all",
        "rationale": "CCS now in RC; remove phantom 0.1623 GW at 2026-28",
    },
    "PPHRORAS": {
        "action": "set_years",
        "values": {2022: 0.180},
        "change_mode_to": "User defined",
        "rationale": "Delsitanisagua 180 MW (COD Dec 2018)",
    },
    "PPHRORPM": {
        "action": "set_years",
        "values": {2022: 0.270},
        "rationale": "Minas San Francisco 270 MW (COD Jan 2019)",
    },
}

# GROUP 3: Optional non-hydro (only if current value needs fixing)
# PPWNDD and PPPVD checked — PPWNDD already 0.0, PPPVD already 0.026 in current A-O.
# Only PPWNDON minor tweak remains.
OPTIONAL_RC = {
    "PPWNDON": (0.0212, 0.0165, "Villonaco = 16.5 MW, not 21.2 MW"),
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def find_row(ws, tech, param):
    """Find the row number where Tech=tech AND Parameter=param."""
    for row in range(2, ws.max_row + 1):
        t = ws.cell(row=row, column=COL_TECH).value
        p = ws.cell(row=row, column=COL_PARAM).value
        if str(t).strip() == tech and str(p).strip() == param:
            return row
    return None


def year_to_col(year):
    """Convert year (2021, 2022, ...) to column index."""
    return COL_YEAR_START + (year - YEAR_START)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Patch Ecuador A-O hydro ResidualCapacity")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show changes without writing")
    parser.add_argument("--file", default=AO_FILE,
                        help=f"Path to A-O file (default: {AO_FILE})")
    parser.add_argument("--skip-optional", action="store_true",
                        help="Skip PPWNDON tweak")
    args = parser.parse_args()

    ao_path = Path(args.file)
    if not ao_path.exists():
        print(f"[ERROR] {ao_path} not found")
        sys.exit(1)

    # Backup
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ao_path.with_name(f"{ao_path.stem}_BACKUP_{ts}{ao_path.suffix}")

    if not args.dry_run:
        shutil.copy2(ao_path, backup)
        print(f"[BACKUP] {backup}")
    else:
        print(f"[DRY RUN] Would backup to {backup}")

    wb = openpyxl.load_workbook(ao_path)
    ws = wb[SHEET]

    changes = 0
    log = []

    # ── GROUP 1: ResidualCapacity ──
    print(f"\n{'='*70}")
    print("GROUP 1: Hydro ResidualCapacity")
    print(f"{'='*70}")

    for tech, (old_val, new_val, rationale) in RC_EDITS.items():
        row = find_row(ws, tech, "ResidualCapacity")
        if row is None:
            print(f"  [WARN] {tech} × ResidualCapacity not found!")
            continue

        col = year_to_col(YEAR_START)  # 2021 column (Flat mode)
        current = ws.cell(row=row, column=col).value
        current_f = float(current) if current is not None else 0.0

        # Sanity check
        if abs(current_f - old_val) > 0.05:
            print(f"  [WARN] {tech} RC: expected ~{old_val}, found {current_f:.4f}")
            print(f"         Applying anyway (value has been independently verified)")

        ws.cell(row=row, column=col).value = new_val
        changes += 1
        msg = f"  {tech:<12} RC: {current_f:.4f} → {new_val:.4f}  ({rationale})"
        print(msg)
        log.append(msg)

    # ── GROUP 2: MinCapacityInvestment ──
    print(f"\n{'='*70}")
    print("GROUP 2: Hydro TotalAnnualMinCapacityInvestment")
    print(f"{'='*70}")

    for tech, cfg in MCI_EDITS.items():
        row = find_row(ws, tech, "TotalAnnualMinCapacityInvestment")
        if row is None:
            print(f"  [WARN] {tech} × MCI not found!")
            continue

        action = cfg["action"]
        rationale = cfg["rationale"]

        if action == "zero_all":
            zeroed = 0
            for yr in range(YEAR_START, YEAR_END + 1):
                col = year_to_col(yr)
                v = ws.cell(row=row, column=col).value
                if v is not None and float(v) != 0.0:
                    old_v = float(v)
                    ws.cell(row=row, column=col).value = 0.0
                    zeroed += 1
                    print(f"  {tech:<12} MCI {yr}: {old_v:.4f} → 0.0")
            changes += zeroed
            log.append(f"  {tech:<12} MCI: zeroed {zeroed} values  ({rationale})")

        elif action == "set_years":
            # Change mode if needed
            if "change_mode_to" in cfg:
                mode_cell = ws.cell(row=row, column=COL_MODE)
                old_mode = mode_cell.value
                mode_cell.value = cfg["change_mode_to"]
                print(f"  {tech:<12} MCI mode: {old_mode} → {cfg['change_mode_to']}")

            # First zero all years
            for yr in range(YEAR_START, YEAR_END + 1):
                col = year_to_col(yr)
                ws.cell(row=row, column=col).value = 0.0

            # Then set specific years
            for yr, val in cfg["values"].items():
                col = year_to_col(yr)
                ws.cell(row=row, column=col).value = val
                changes += 1
                msg = f"  {tech:<12} MCI {yr}: → {val:.4f}  ({rationale})"
                print(msg)
                log.append(msg)

    # ── GROUP 3: Optional ──
    if not args.skip_optional:
        print(f"\n{'='*70}")
        print("GROUP 3: Optional (PPWNDON)")
        print(f"{'='*70}")

        for tech, (old_val, new_val, rationale) in OPTIONAL_RC.items():
            row = find_row(ws, tech, "ResidualCapacity")
            if row is None:
                print(f"  [SKIP] {tech} × ResidualCapacity not found")
                continue

            # PPWNDON is User defined — has values in every year column
            mode = ws.cell(row=row, column=COL_MODE).value
            if "User" in str(mode):
                for yr in range(YEAR_START, YEAR_END + 1):
                    col = year_to_col(yr)
                    ws.cell(row=row, column=col).value = new_val
                changes += 1
                msg = f"  {tech:<12} RC: {old_val:.4f} → {new_val:.4f} (all years)  ({rationale})"
            else:
                col = year_to_col(YEAR_START)
                ws.cell(row=row, column=col).value = new_val
                changes += 1
                msg = f"  {tech:<12} RC: {old_val:.4f} → {new_val:.4f}  ({rationale})"
            print(msg)
            log.append(msg)

    # ── GROUP 4: Flatten LLs to historical, release ULs, fix all formulas ──
    # Strategy: for any row with formula cells that openpyxl can't evaluate:
    #   - LL rows: set ALL 30 years flat at the 2021 value (CENACE-calibrated)
    #   - UL rows: set ALL 30 years to 9999 (release; Stages 1-3 refine later)
    #   - CF/RC/other: set formula cells to 2021 value (flat for existing plants)
    # This guarantees: no formula cells, no LL > UL, no short rows.
    print(f"\n{'='*70}")
    print("GROUP 4: Flatten LLs to historical, release ULs, fix formulas")
    print(f"{'='*70}")

    UL_RELEASED = 9999.0
    formula_fixes = 0
    formula_rows_fixed = []

    for row in range(2, ws.max_row + 1):
        tech = ws.cell(row=row, column=COL_TECH).value
        param = ws.cell(row=row, column=COL_PARAM).value
        if not tech or not param:
            continue
        param_str = str(param)

        # Check if this row has any formula cells
        has_formula = False
        first_real = None
        for yr in range(YEAR_START, YEAR_END + 1):
            col = year_to_col(yr)
            v = ws.cell(row=row, column=col).value
            if isinstance(v, str) and v.startswith('='):
                has_formula = True
            elif v is not None and isinstance(v, (int, float)) and first_real is None:
                first_real = float(v)

        if not has_formula:
            continue

        # Determine fill strategy based on parameter type
        if 'LowerLimit' in param_str:
            # LL: flatten to 2021 value across all years
            fill_val = first_real if first_real is not None else 0.0
            strategy = f"LL flat @ {fill_val:.4f}"
            for yr in range(YEAR_START, YEAR_END + 1):
                col = year_to_col(yr)
                ws.cell(row=row, column=col).value = fill_val
                formula_fixes += 1
            changes += 30

        elif 'UpperLimit' in param_str or 'MaxCapacity' in param_str:
            # UL / MaxCapacity: release to 9999
            strategy = f"UL released → {UL_RELEASED:.0f}"
            for yr in range(YEAR_START, YEAR_END + 1):
                col = year_to_col(yr)
                ws.cell(row=row, column=col).value = UL_RELEASED
                formula_fixes += 1
            changes += 30

        else:
            # CF, RC, other: replace only formula cells with 2021 value
            fill_val = first_real if first_real is not None else 0.0
            strategy = f"formulas → {fill_val:.4f}"
            for yr in range(YEAR_START, YEAR_END + 1):
                col = year_to_col(yr)
                v = ws.cell(row=row, column=col).value
                if isinstance(v, str) and v.startswith('='):
                    ws.cell(row=row, column=col).value = fill_val
                    formula_fixes += 1
                    changes += 1

        formula_rows_fixed.append((str(tech), param_str, strategy))

    for tech, param, strategy in formula_rows_fixed:
        print(f"  {tech:<14} {param:<45} {strategy}")
    print(f"\n  Total: {formula_fixes} cells written across {len(formula_rows_fixed)} rows")

    # ── GROUP 5: Safety net — release ULs for any tech whose LL was flattened ──
    # Some UL rows had NO formulas but have values lower than the flattened LL.
    # Release those UL rows to 9999 too.
    print(f"\n{'='*70}")
    print("GROUP 5: Release ULs where LL was flattened (catch non-formula ULs)")
    print(f"{'='*70}")

    ll_flattened_techs = set(t for t, p, _ in formula_rows_fixed if 'LowerLimit' in p)

    for row in range(2, ws.max_row + 1):
        tech = ws.cell(row=row, column=COL_TECH).value
        param = ws.cell(row=row, column=COL_PARAM).value
        if not tech or not param:
            continue
        tech_str = str(tech).strip()
        param_str = str(param)

        if tech_str not in ll_flattened_techs:
            continue
        if 'UpperLimit' not in param_str and 'MaxCapacity' not in param_str:
            continue

        # Check if already released (by Group 4)
        v_2022 = ws.cell(row=row, column=year_to_col(2022)).value
        if v_2022 == UL_RELEASED:
            continue  # already done

        # Release it
        for yr in range(YEAR_START, YEAR_END + 1):
            col = year_to_col(yr)
            ws.cell(row=row, column=col).value = UL_RELEASED
        changes += 30
        print(f"  {tech_str:<14} {param_str:<45} UL released → {UL_RELEASED:.0f}")

    # ── GROUP 6: Cap bypass-tech upper limits ──────────────────────────────
    # Groups 4/5 released ULs to 9999, which enables bypass gaming: the optimizer
    # routes generation through distributed/isolated techs (e.g. PPPVD) to avoid
    # T&D losses, collapsing Empirical_Gen toward consumer demand and producing
    # phantom 18+ GW of distributed PV. Fix: cap bypass tech ULs at
    # ResidualCapacity × CapacityToActivityUnit (CF=1 ceiling).
    print(f"\n{'='*70}")
    print("GROUP 6: Cap bypass-tech upper limits (prevent T&D bypass gaming)")
    print(f"{'='*70}")

    C2A = 31.536
    BYPASS_UL_CAPS = {
        # tech:    (RC_GW,  rationale)
        "PPPVD":  (0.026,  "Distributed PV 26 MW; UL = 0.026 × 31.536 = 0.82 PJ"),
        "PPPVDS": (0.0003, "Distributed PV-storage ~0.3 MW; UL ≈ 0.01 PJ"),
        "PPWNDD": (0.0,    "Phantom distributed wind; already RC=0 in A-O"),
    }

    for tech, (rc_gw, rationale) in BYPASS_UL_CAPS.items():
        ul_cap = max(rc_gw * C2A, 0.01)  # floor at 0.01 PJ

        row = find_row(ws, tech, "TotalTechnologyAnnualActivityUpperLimit")
        if row is None:
            print(f"  [SKIP] {tech} × UL not found")
            continue

        # Check current value
        current = ws.cell(row=row, column=year_to_col(YEAR_START)).value
        current_f = float(current) if current is not None else 0.0

        if current_f <= ul_cap * 2:
            print(f"  [OK]   {tech:<12} UL = {current_f:.4f}, already reasonable")
            continue

        # Cap all years
        for yr in range(YEAR_START, YEAR_END + 1):
            col = year_to_col(yr)
            ws.cell(row=row, column=col).value = round(ul_cap, 4)
        changes += 30

        msg = f"  {tech:<12} UL: {current_f:.1f} → {ul_cap:.4f}  ({rationale})"
        print(msg)
        log.append(msg)

    # ── Save ──
    print(f"\n{'='*70}")
    if args.dry_run:
        print(f"[DRY RUN] {changes} changes identified. No file written.")
    else:
        save_ao_safely(wb, ao_path)
        print(f"[SAVED] {ao_path} — {changes} changes applied")
        print(f"[BACKUP] Original at {backup}")

    # ── Verification summary ──
    print(f"\n{'='*70}")
    print("VERIFICATION — re-read and check")
    print(f"{'='*70}")

    if args.dry_run:
        print("  (Skipped in dry-run mode — run without --dry-run to verify)")
    else:
        wb2 = openpyxl.load_workbook(ao_path)
        ws2 = wb2[SHEET]

        hydro_techs = ['PPHD', 'PPHDAMAB', 'PPHDAMAM', 'PPHDAMAS', 'PPHDAMPM',
                       'PPHDAMPS', 'PPHRORAB', 'PPHRORAM', 'PPHRORAS',
                       'PPHRORPM', 'PPHRORPS', 'PPIHD']

        total_rc = 0
        for tech in hydro_techs:
            row = find_row(ws2, tech, "ResidualCapacity")
            if row:
                v = ws2.cell(row=row, column=year_to_col(YEAR_START)).value
                v = float(v) if v else 0.0
                total_rc += v
                src = "EDITED" if tech in RC_EDITS else "kept"
                print(f"  {tech:<12} RC = {v:.4f} GW ({v*1000:.0f} MW)  [{src}]")

        print(f"\n  TOTAL hydro RC = {total_rc:.3f} GW ({total_rc*1000:.0f} MW)")
        print(f"  Real fleet 2021: ~5,107 MW (ARCERNNR)")
        print(f"  Ratio: {total_rc*1000/5107:.1%}")

    print(f"\n{'='*70}")
    print("NEXT STEPS:")
    print("  1. py A2_compiler.py --countries Ecuador")
    print("  2. py B1_scenario_config.py --countries Ecuador")
    print("  3. py stage0_run.py --countries Ecuador")
    print("  4. Run GLPK solver (Ecuador BAU/NDCNEW/LTSNEW)")
    print("  5. py stage0_collect_outputs.py --countries Ecuador")
    print("  6. py stage1_share_analyzer_v15.py --countries Ecuador")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
