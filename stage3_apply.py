"""
Stage 3 Apply — Patch .txt data files with Stage 2 lower/upper limits.

For each (country, scenario):
  1. Copy  Executables/{scenario}_0/  →  Executables/{scenario}_FINAL_0/
  2. Rename internal .txt:  {scenario}_0.txt  →  {scenario}_FINAL_0.txt
  3. Patch TotalTechnologyAnnualActivityLowerLimit  (PP-prefix techs, years ≥ 2025)
  4. Patch TotalTechnologyAnnualActivityUpperLimit  (PP-prefix techs, years ≥ 2025)
  5. Insert ReserveMargin = 1.15 block  (if not already present)
  6. Never touch originals, non-PP techs, or years ≤ 2024.

Usage (Windows Anaconda cmd):
    py stage3_apply.py --root C:/path/to/MODELS_LAC_4
    py stage3_apply.py --root C:/path/to/MODELS_LAC_4 --dry-run
    py stage3_apply.py --root C:/path/to/MODELS_LAC_4 --countries CostaRica Jamaica
    py stage3_apply.py --root . --clean
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

import pandas as pd

# =====================================================================
# CONFIGURATION
# =====================================================================

SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]
PP_PREFIXES = ("PP", "PWR")
FIRST_PATCH_YEAR = 2025
RESERVE_MARGIN = 1.15
UPPER_UNCAPPED = 9999.0  # controller sentinel for "no cap"
LOWER_TO_UPPER_FACTOR = 1.05  # tight cap = lower * 1.05 when controller says uncapped but lower > 0

COUNTRY_CONFIG = {
    "CostaRica":         {"model_dir": "CR_ENERGY/t1_confection"},
    "DominicanRepublic": {"model_dir": "RD_ENERGY"},
    "Ecuador":           {"model_dir": "ECU_Energy"},
    "Guatemala":         {"model_dir": "GUA_ENERGY"},
    "Honduras":          {"model_dir": "HON_ENERGY"},
    "Jamaica":           {"model_dir": "JAM_ENERGY"},
}

CONTROLLER_LOWER_SHEET = "CURRENT_LOWER"
CONTROLLER_UPPER_SHEET = "CURRENT_UPPER"
CONTROLLER_TECHMAP_SHEET = "TECH_MAP"


def is_pp_tech(name):
    return str(name).strip().upper().startswith(PP_PREFIXES)


# Variable renewable tech identifiers — these do NOT provide firm reserve capacity
VARIABLE_RE_KEYS = ("SPV", "PVD", "PVT", "PVS", "WND", "WNO")


def is_variable_re(name):
    """Return True if tech is variable renewable (solar/wind) — no RM credit."""
    t = str(name).strip().upper()
    return any(k in t for k in VARIABLE_RE_KEYS)


# =====================================================================
# CONTROLLER LOADER
# =====================================================================

def load_controller(xlsx_path):
    """Return (lower_df, upper_df, fossil_techs_set)."""
    lower = pd.read_excel(xlsx_path, sheet_name=CONTROLLER_LOWER_SHEET)
    upper = pd.read_excel(xlsx_path, sheet_name=CONTROLLER_UPPER_SHEET)
    tech_map = pd.read_excel(xlsx_path, sheet_name=CONTROLLER_TECHMAP_SHEET)
    fossil_techs = set(tech_map[tech_map["Group"] == "FOSSIL"]["Tech"])
    return lower, upper, fossil_techs


def controller_slice(df, country, scenario):
    """Return dict  {tech: {year_int: value, ...}}  for a (country, scenario)."""
    sub = df[(df["Country"] == country) & (df["Scenario"] == scenario)]
    yr_cols = [c for c in sub.columns if isinstance(c, (int, float))]
    out = {}
    for _, row in sub.iterrows():
        tech = row["Tech"]
        out[tech] = {int(y): float(row[y]) for y in yr_cols}
    return out


# =====================================================================
# TXT PARSER / PATCHER
# =====================================================================

def parse_block_bounds(content, param_name):
    """Find start/end offsets of a `param ... ;` block. Returns (start, end) or None."""
    pat = rf"param\s+{re.escape(param_name)}\s+default\s+[\d.\-]+\s*:"
    m = re.search(pat, content)
    if not m:
        return None
    start = m.start()
    semi = content.find("\n;\n", start)
    if semi == -1:
        semi = content.find("\n;", start)
    if semi == -1:
        return None
    end = semi + 2  # include the ; and trailing newline
    return start, end


def parse_year_header(line):
    """Parse a line like '2021 2022 ... 2050 :=' → list of int years."""
    parts = line.replace(":=", "").strip().split()
    years = []
    for p in parts:
        try:
            y = int(p)
            if 2000 <= y <= 2100:
                years.append(y)
        except ValueError:
            continue
    return years


def parse_region_code(content):
    """Extract region code from 'set REGION := XX ;'."""
    m = re.search(r"set REGION\s*:=\s*(\S+)\s*;", content)
    return m.group(1) if m else None


def format_val(v):
    """Format a float for .txt output: 4 decimals, strip trailing zeros."""
    if v == int(v) and abs(v) < 1e12:
        return str(int(v))
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s


def patch_block(content, param_name, ctrl_dict, first_patch_year, log,
                default_val=0.0, uncap_sentinel=None,
                paired_lower=None, lower_to_upper_factor=None):
    """
    Patch a single param block in the .txt content.

    ctrl_dict: {tech: {year: value}} from controller.
    default_val: the 'default X' in the param declaration (0 for lower, 99999 for upper).
    uncap_sentinel: if set, controller values >= this are treated as "use default".
    paired_lower: when patching upper, pass the lower dict here. For techs/years where
                  controller upper >= uncap_sentinel but lower > 0, upper is computed
                  as lower * lower_to_upper_factor (tight cap). For zero lowers, leaves
                  uncapped.
    lower_to_upper_factor: multiplier for tight cap computation (e.g., 1.05).

    Returns new content string and number of values changed.
    """

    def effective_upper(tech, year, ctrl_v):
        """Compute the actual upper value to write, given pairing rule."""
        # If we're patching upper and controller says uncapped, check paired lower
        if paired_lower is not None and uncap_sentinel is not None and ctrl_v >= uncap_sentinel:
            lower_v = paired_lower.get(tech, {}).get(year, 0.0)
            if lower_v > 1e-10:
                return lower_v * lower_to_upper_factor, True  # tight cap
            return None, False  # leave uncapped (no row needed)
        if uncap_sentinel is not None and ctrl_v >= uncap_sentinel:
            return None, False
        return ctrl_v, True
    bounds = parse_block_bounds(content, param_name)
    if bounds is None:
        log.append(f"  [WARN] '{param_name}' block not found")
        return content, 0

    start, end = bounds
    block = content[start:end]
    lines = block.split("\n")

    new_lines = []
    year_header = None
    in_data = False
    changes = 0
    seen_techs = set()

    for line in lines:
        stripped = line.rstrip()
        bare = stripped.strip()

        # Year header line (contains := but not param declaration)
        if ":=" in bare and not bare.startswith("param"):
            years = parse_year_header(bare)
            if years and years[0] >= 2000:
                year_header = years
                in_data = True
            new_lines.append(stripped)
            continue

        # Region header [XX,*,*]:
        if bare.startswith("[") and bare.endswith(":"):
            in_data = False
            new_lines.append(stripped)
            continue

        # Semicolon terminator
        if bare == ";":
            # Before closing, add any controller techs not yet seen
            if year_header:
                for tech, yr_vals in sorted(ctrl_dict.items()):
                    if tech in seen_techs:
                        continue
                    if not is_pp_tech(tech):
                        continue
                    # Check if this tech has any non-default values in patch range
                    needs_row = False
                    for y in year_header:
                        if y >= first_patch_year and y in yr_vals:
                            ctrl_v = yr_vals[y]
                            if paired_lower is not None:
                                eff, has_cap = effective_upper(tech, y, ctrl_v)
                                if has_cap and abs(eff - default_val) > 1e-10:
                                    needs_row = True
                                    break
                            else:
                                if uncap_sentinel and ctrl_v >= uncap_sentinel:
                                    continue
                                if abs(ctrl_v - default_val) > 1e-10:
                                    needs_row = True
                                    break
                    if not needs_row:
                        continue
                    # Build new row: default_val for years < first_patch_year,
                    # effective values for years >= first_patch_year
                    vals = []
                    for y in year_header:
                        if y < first_patch_year:
                            vals.append(format_val(default_val))
                        elif y in yr_vals:
                            ctrl_v = yr_vals[y]
                            if paired_lower is not None:
                                eff, has_cap = effective_upper(tech, y, ctrl_v)
                                if has_cap:
                                    vals.append(format_val(eff))
                                    changes += 1
                                else:
                                    vals.append(format_val(default_val))
                            elif uncap_sentinel and ctrl_v >= uncap_sentinel:
                                vals.append(format_val(default_val))
                            else:
                                vals.append(format_val(ctrl_v))
                                changes += 1
                        else:
                            vals.append(format_val(default_val))
                    new_line = tech + " " + " ".join(vals) + " "
                    new_lines.append(new_line)
                    seen_techs.add(tech)
                    log.append(f"    + Added {tech} to {param_name}")
            new_lines.append(stripped)
            continue

        # Data row: TECHNAME val val val ...
        if in_data and year_header and bare and not bare.startswith(";"):
            parts = bare.split()
            if len(parts) >= 2:
                tech_name = parts[0]
                values = parts[1:]

                if is_pp_tech(tech_name) and tech_name in ctrl_dict and len(values) == len(year_header):
                    seen_techs.add(tech_name)
                    yr_vals = ctrl_dict[tech_name]
                    new_values = list(values)
                    for i, y in enumerate(year_header):
                        if y >= first_patch_year and y in yr_vals:
                            ctrl_v = yr_vals[y]
                            if paired_lower is not None:
                                eff, has_cap = effective_upper(tech_name, y, ctrl_v)
                                new_v = eff if has_cap else 99999.0
                            elif uncap_sentinel and ctrl_v >= uncap_sentinel:
                                new_v = 99999.0
                            else:
                                new_v = ctrl_v
                            try:
                                old_v = float(values[i])
                            except ValueError:
                                continue
                            if abs(new_v - old_v) > 1e-10:
                                new_values[i] = format_val(new_v)
                                changes += 1
                    new_line = tech_name + " " + " ".join(new_values) + " "
                    new_lines.append(new_line)
                    continue

        new_lines.append(stripped)

    new_block = "\n".join(new_lines)
    new_content = content[:start] + new_block + content[end:]
    return new_content, changes


def parse_output_activity_ratio(content):
    """
    Parse OutputActivityRatio block to find which technologies produce which fuels.
    Returns dict {tech: set(fuels)}.
    Format expected:  [REGION,TECH,FUEL,*,*]:
    """
    m = re.search(r"param\s+OutputActivityRatio\s+default\s+[\d.\-]+\s*:", content)
    if not m:
        return {}
    start = m.start()
    semi = content.find("\n;\n", start)
    if semi == -1:
        semi = content.find("\n;", start)
    if semi == -1:
        return {}
    block = content[start:semi]

    tech_fuel = {}
    for line in block.split("\n"):
        s = line.strip()
        bm = re.match(r"\[(\w+),(\w+),(\w+),\*,\*\]:", s)
        if bm:
            region, tech, fuel = bm.group(1), bm.group(2), bm.group(3)
            tech_fuel.setdefault(tech, set()).add(fuel)
    return tech_fuel


def find_generation_fuel_and_techs(content):
    """
    Identify the E1-level electricity fuel and the PP/PWR generators producing it.
    Returns (fuel_name, sorted_list_of_techs) or (None, []) if not found.
    """
    tech_fuel = parse_output_activity_ratio(content)
    # Find candidate E1 generation fuels: start with 'E1' and contain 'ELE'
    candidate_fuels = set()
    for fuels in tech_fuel.values():
        for f in fuels:
            up = f.upper()
            if up.startswith("E1") and "ELE" in up:
                candidate_fuels.add(f)
    if not candidate_fuels:
        return None, []
    # Pick the fuel with the most PP/PWR producers
    best_fuel, best_techs = None, []
    for f in candidate_fuels:
        techs = sorted(t for t, fs in tech_fuel.items()
                       if f in fs and is_pp_tech(t))
        if len(techs) > len(best_techs):
            best_fuel, best_techs = f, techs
    return best_fuel, best_techs


def populate_tag_block(content, param_name, region, years, tags_dict, log,
                       index_kind):
    """
    Populate an empty `param X default 0 := ;` block for a tag-style parameter.

    tags_dict: {entity_name: value}  -- entity is a fuel (for TagFuel) or tech (for TagTechnology).
    index_kind: "fuel" or "technology" -- only used for log messages.

    Block format produced:
        param X default 0 :=
        [REGION,*,*]:
        <year-headers> :=
        ENT1 v v v ...
        ENT2 v v v ...
        ;
    """
    if not tags_dict:
        log.append(f"  [WARN] No entries for {param_name} — left empty")
        return content

    yr_str = " ".join(str(y) for y in years)
    rows = []
    for ent, val in sorted(tags_dict.items()):
        val_str = " ".join(format_val(val) for _ in years)
        rows.append(f"{ent} {val_str} ")
    rows_str = "\n".join(rows)

    new_block = (
        f"param {param_name} default 0 :=\n"
        f"[{region},*,*]:\n"
        f"{yr_str} :=\n"
        f"{rows_str}\n"
        f";"
    )

    empty_pat = rf"param\s+{re.escape(param_name)}\s+default\s+[\d.\-]+\s*:=\s*[\r\n]+\s*;"
    m = re.search(empty_pat, content)
    if m:
        content = content[:m.start()] + new_block + content[m.end():]
        log.append(f"  Populated {param_name}: {len(tags_dict)} {index_kind}(s) tagged")
        return content

    pop_pat = rf"param\s+{re.escape(param_name)}\s+default\s+[\d.\-]+\s*:=\s*[\r\n]+\["
    if re.search(pop_pat, content):
        log.append(f"  {param_name} already populated — skipped")
        return content

    end_pos = content.rfind("end;")
    if end_pos == -1:
        content += "\n" + new_block + "\n\nend;\n"
    else:
        content = content[:end_pos] + new_block + "\n\n" + content[end_pos:]
    log.append(f"  Inserted {param_name}: {len(tags_dict)} {index_kind}(s) tagged")
    return content


def find_all_pp_techs_in_txt(content):
    """
    Find ALL PP/PWR-prefix tech names appearing in any param block of the .txt file.
    Scans LowerLimit, UpperLimit, ResidualCapacity, and OutputActivityRatio blocks.
    Returns a sorted list of unique tech names.
    """
    all_techs = set()
    for param in ["TotalTechnologyAnnualActivityLowerLimit",
                  "TotalTechnologyAnnualActivityUpperLimit",
                  "ResidualCapacity",
                  "TotalAnnualMaxCapacity",
                  "OutputActivityRatio"]:
        bounds = parse_block_bounds(content, param)
        if not bounds:
            continue
        start, end = bounds
        block = content[start:end]
        in_data = False
        for line in block.split("\n"):
            s = line.strip()
            if ":=" in s and not s.startswith("param"):
                in_data = True
                continue
            if s.startswith("["):
                # Check bracket headers for tech names: [REGION,TECH,...]
                parts = s.strip("[]():").split(",")
                if len(parts) >= 2 and is_pp_tech(parts[1].strip()):
                    all_techs.add(parts[1].strip())
                continue
            if in_data and s and not s.startswith(";"):
                parts = s.split()
                if parts and is_pp_tech(parts[0]):
                    all_techs.add(parts[0])
    return sorted(all_techs)


def insert_reserve_margin(content, years, region, reserve_margin, log):
    """Populate the ReserveMargin param block with data.

    The block usually already exists as an empty stub:
        param ReserveMargin default 0 :=
        ;
    We replace it with a populated version. If missing entirely, we insert
    before 'end;'.
    """
    yr_val_lines = "\n".join(f"{region} {y} {format_val(reserve_margin)}" for y in years)
    new_block = (
        f"param ReserveMargin default 0 :=\n"
        f"{yr_val_lines}\n"
        f";"
    )

    # Try to find and replace the existing empty block
    empty_pat = r"param\s+ReserveMargin\s+default\s+[\d.\-]+\s*:=\s*[\r\n]+\s*;"
    m = re.search(empty_pat, content)
    if m:
        content = content[:m.start()] + new_block + content[m.end():]
        log.append(f"  Populated ReserveMargin = {reserve_margin} (replaced empty block)")
        return content

    # Check if there's already a populated block
    pop_pat = r"param\s+ReserveMargin\s+default\s+[\d.\-]+\s*:=\s*[\r\n]+\["
    if re.search(pop_pat, content):
        log.append("  ReserveMargin already populated — skipped")
        return content

    # Not found at all — insert before end;
    end_pos = content.rfind("end;")
    if end_pos == -1:
        log.append("  [WARN] 'end;' not found — appending ReserveMargin at EOF")
        content += "\n" + new_block + "\n\nend;\n"
    else:
        content = content[:end_pos] + new_block + "\n\n" + content[end_pos:]
    log.append(f"  Inserted ReserveMargin = {reserve_margin}")
    return content


# =====================================================================
# MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description="Stage 3: Patch .txt files with Stage 2 values")
    parser.add_argument("--root", required=True, help="MODELS_LAC_4 root directory")
    parser.add_argument("--controller", default=None,
                        help="Path to controller xlsx (default: {root}/_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing")
    parser.add_argument("--countries", nargs="*", default=[], help="Subset of countries to process")
    parser.add_argument("--scenarios", nargs="*", default=SCENARIOS, help="Subset of scenarios")
    parser.add_argument("--no-reserve-margin", action="store_true", help="Skip ReserveMargin insertion")
    parser.add_argument("--no-upper-cap", action="store_true",
                        help="Skip UpperLimit patching (leave at default 99999)")
    parser.add_argument("--uncap-pp-maxcap", action="store_true",
                        help="Reset TotalAnnualMaxCapacity for PP techs to 99999")
    parser.add_argument("--reserve-margin", type=float, default=RESERVE_MARGIN)
    parser.add_argument("--skip-orphan-cap", nargs="*", default=[],
                        help="Countries to skip orphan tech capping (e.g., Guatemala)")
    parser.add_argument("--clean", action="store_true",
                        help="Remove all existing _FINAL_0 folders before running")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"ERROR: root dir not found: {root}")
        sys.exit(1)

    ctrl_path = Path(args.controller) if args.controller else root / "_STAGE2_OUTPUT" / "CONTROLLER_NEW_SCENARIOS.xlsx"
    if not ctrl_path.exists():
        print(f"ERROR: controller not found: {ctrl_path}")
        sys.exit(1)

    countries = args.countries if args.countries else list(COUNTRY_CONFIG.keys())
    scenarios = args.scenarios

    # Clean pass: remove all _FINAL_0 folders first
    if args.clean:
        removed = 0
        for country in countries:
            cfg = COUNTRY_CONFIG.get(country)
            if not cfg:
                continue
            exe_dir = root / country / cfg["model_dir"] / "Executables"
            if not exe_dir.exists():
                continue
            for scenario in scenarios:
                final_dir = exe_dir / f"{scenario}_FINAL_0"
                if final_dir.exists():
                    shutil.rmtree(final_dir)
                    removed += 1
        print(f"Cleaned {removed} existing _FINAL_0 folders")
        print()

    print(f"Stage 3 Apply")
    print(f"  Root:       {root}")
    print(f"  Controller: {ctrl_path}")
    print(f"  Dry-run:    {args.dry_run}")
    print()

    lower_df, upper_df, fossil_techs = load_controller(ctrl_path)

    summary = []

    for country in countries:
        cfg = COUNTRY_CONFIG.get(country)
        if cfg is None:
            print(f"[SKIP] Unknown country: {country}")
            continue

        for scenario in scenarios:
            log = []
            tag = f"{country}/{scenario}"
            log.append(f"--- {tag} ---")

            model_dir = root / country / cfg["model_dir"]
            src_dir = model_dir / "Executables" / f"{scenario}_0"
            dst_dir = model_dir / "Executables" / f"{scenario}_FINAL_0"

            if not src_dir.exists():
                log.append(f"  [SKIP] Source dir not found: {src_dir}")
                summary.append((tag, "SKIP", 0, 0, log))
                continue

            src_txt = src_dir / f"{scenario}_0.txt"
            if not src_txt.exists():
                log.append(f"  [SKIP] Source .txt not found: {src_txt}")
                summary.append((tag, "SKIP", 0, 0, log))
                continue

            # Step 1: Copy folder
            if dst_dir.exists():
                log.append(f"  [WARN] Destination exists, removing: {dst_dir}")
                if not args.dry_run:
                    shutil.rmtree(dst_dir)

            log.append(f"  Copy {src_dir.name}/ → {dst_dir.name}/")
            if not args.dry_run:
                shutil.copytree(src_dir, dst_dir)

            # Step 2: Rename internal .txt
            dst_txt_old = dst_dir / f"{scenario}_0.txt"
            dst_txt = dst_dir / f"{scenario}_FINAL_0.txt"
            log.append(f"  Rename {dst_txt_old.name} → {dst_txt.name}")
            if not args.dry_run:
                if dst_txt_old.exists():
                    dst_txt_old.rename(dst_txt)

            if args.dry_run:
                summary.append((tag, "DRY-RUN", 0, 0, log))
                continue

            # Read .txt content
            # Read .txt content (preserve line endings)
            with open(dst_txt, "r", encoding="utf-8", errors="replace", newline="") as f:
                content = f.read()
            # Detect line ending style, then normalize to \n for processing
            line_ending = "\r\n" if "\r\n" in content else "\n"
            content = content.replace("\r\n", "\n")

            # Parse region and years from the file
            region = parse_region_code(content)
            if not region:
                log.append("  [ERROR] Could not parse REGION from .txt")
                summary.append((tag, "ERROR", 0, 0, log))
                continue

            # Parse years from LowerLimit block header
            bounds = parse_block_bounds(content, "TotalTechnologyAnnualActivityLowerLimit")
            if bounds:
                block_snippet = content[bounds[0]:bounds[0]+500]
                for bline in block_snippet.split("\n"):
                    if ":=" in bline and not bline.strip().startswith("param"):
                        txt_years = parse_year_header(bline)
                        if txt_years:
                            break
                else:
                    txt_years = list(range(2021, 2051))
            else:
                txt_years = list(range(2021, 2051))

            log.append(f"  Region: {region}, Years: {txt_years[0]}–{txt_years[-1]}")

            # Get controller data for this (country, scenario)
            ctrl_lower = controller_slice(lower_df, country, scenario)
            ctrl_upper = controller_slice(upper_df, country, scenario)
            log.append(f"  Controller techs: {len(ctrl_lower)} lower, {len(ctrl_upper)} upper")

            # Step 3: Patch LowerLimit
            content, n_lower = patch_block(
                content, "TotalTechnologyAnnualActivityLowerLimit",
                ctrl_lower, FIRST_PATCH_YEAR, log,
                default_val=0.0, uncap_sentinel=None
            )
            log.append(f"  Patched LowerLimit: {n_lower} values changed")

            # Find orphan PP techs (in model but not in controller) — needed for Steps 3b and 4
            skip_orphans = country in args.skip_orphan_cap
            if skip_orphans:
                orphan_techs = []
                log.append(f"  Orphan capping SKIPPED for {country} (--skip-orphan-cap)")
            else:
                all_pp_in_txt = find_all_pp_techs_in_txt(content)
                ctrl_pp_techs = {t for t in ctrl_lower if is_pp_tech(t)}
                orphan_techs = [t for t in all_pp_in_txt if t not in ctrl_pp_techs]
                if orphan_techs:
                    log.append(f"  Found {len(orphan_techs)} orphan PP techs: {', '.join(orphan_techs)}")

            # Step 3b: Zero out orphan tech lower limits (in case originals had non-zero)
            if orphan_techs:
                orphan_lower = {t: {y: 0.0 for y in txt_years if y >= FIRST_PATCH_YEAR}
                                for t in orphan_techs}
                content, n_orphan_lower = patch_block(
                    content, "TotalTechnologyAnnualActivityLowerLimit",
                    orphan_lower, FIRST_PATCH_YEAR, log,
                    default_val=0.0, uncap_sentinel=None
                )
                if n_orphan_lower:
                    log.append(f"    Zeroed {n_orphan_lower} orphan lower limits")

            # Step 4: Patch UpperLimit
            if args.no_upper_cap:
                # Clear any pre-existing upper limits on PP techs so they don't
                # conflict with our new (potentially higher) lower limits.
                # Set all PP tech uppers to 99999 (uncapped).
                # BUT still zero out orphan techs.
                uncap_dict = {}
                for tech in ctrl_lower:
                    if is_pp_tech(tech):
                        uncap_dict[tech] = {y: 99999.0 for y in txt_years if y >= FIRST_PATCH_YEAR}
                for tech in orphan_techs:
                    uncap_dict[tech] = {y: 0.0 for y in txt_years if y >= FIRST_PATCH_YEAR}
                if orphan_techs:
                    log.append(f"    Capped {len(orphan_techs)} orphan PP techs to 0: {', '.join(sorted(orphan_techs))}")
                content, n_upper = patch_block(
                    content, "TotalTechnologyAnnualActivityUpperLimit",
                    uncap_dict, FIRST_PATCH_YEAR, log,
                    default_val=99999.0, uncap_sentinel=None
                )
                log.append(f"  UpperLimit: cleared {n_upper} PP tech caps to 99999 (--no-upper-cap)")
            else:
                # Always use lower × factor for upper limits (tight share control).
                # Zero lower → zero upper (prevent unconstrained techs from producing).
                # UNLESS skip_orphans is set (e.g., Guatemala) — then leave zero-lower uncapped.
                zero_lower_upper = 0.0 if not skip_orphans else 99999.0
                tight_upper = {}
                for tech, yr_vals in ctrl_lower.items():
                    if is_pp_tech(tech):
                        tight_upper[tech] = {
                            y: v * LOWER_TO_UPPER_FACTOR if v > 1e-10 else zero_lower_upper
                            for y, v in yr_vals.items()
                        }

                # Also cap orphan PP techs (in model but not in controller) at zero
                for tech in orphan_techs:
                    tight_upper[tech] = {y: 0.0 for y in txt_years if y >= FIRST_PATCH_YEAR}
                if orphan_techs:
                    log.append(f"    Capped {len(orphan_techs)} orphan PP techs to 0: {', '.join(sorted(orphan_techs))}")

                content, n_upper = patch_block(
                    content, "TotalTechnologyAnnualActivityUpperLimit",
                    tight_upper, FIRST_PATCH_YEAR, log,
                    default_val=99999.0, uncap_sentinel=None
                )
                log.append(f"  Patched UpperLimit: {n_upper} values changed (always lower x {LOWER_TO_UPPER_FACTOR})")

            # Step 4b: Uncap TotalAnnualMaxCapacity for PP techs
            if args.uncap_pp_maxcap:
                uncap_maxcap = {}
                for tech in ctrl_lower:
                    if is_pp_tech(tech):
                        uncap_maxcap[tech] = {y: 99999.0 for y in txt_years if y >= FIRST_PATCH_YEAR}
                content, n_maxcap = patch_block(
                    content, "TotalAnnualMaxCapacity",
                    uncap_maxcap, FIRST_PATCH_YEAR, log,
                    default_val=99999.0, uncap_sentinel=None
                )
                log.append(f"  MaxCapacity: cleared {n_maxcap} PP tech caps to 99999 (--uncap-pp-maxcap)")

            # Step 5: ReserveMargin + tags
            if not args.no_reserve_margin:
                # ReserveMargin scalar (flat across years)
                content = insert_reserve_margin(
                    content, txt_years, region, args.reserve_margin, log
                )

                # Identify generation fuel and PP/PWR generators producing it
                gen_fuel, gen_techs = find_generation_fuel_and_techs(content)
                if gen_fuel is None:
                    log.append("  [WARN] Could not identify generation fuel — RM tags left empty")
                else:
                    log.append(f"  Generation fuel: {gen_fuel}; {len(gen_techs)} generators")

                    # ReserveMarginTagFuel: tag the generation fuel with 1
                    content = populate_tag_block(
                        content, "ReserveMarginTagFuel", region, txt_years,
                        {gen_fuel: 1}, log, "fuel"
                    )

                    # ReserveMarginTagTechnology: tag all firm generators with 1
                    # Only solar/wind (variable RE) excluded — hydro, geo, biomass, fossil all firm
                    firm_generators = [t for t in gen_techs if not is_variable_re(t)]
                    variable_generators = [t for t in gen_techs if is_variable_re(t)]
                    log.append(f"  RM tagging: {len(firm_generators)} firm, {len(variable_generators)} variable (excluded: {', '.join(variable_generators) if variable_generators else 'none'})")
                    content = populate_tag_block(
                        content, "ReserveMarginTagTechnology", region, txt_years,
                        {t: 1 for t in firm_generators}, log, "technology"
                    )

            # Write patched .txt
            # Write patched .txt (restore original line endings)
            if line_ending == "\r\n":
                content = content.replace("\n", "\r\n")
            with open(dst_txt, "w", encoding="utf-8", newline="") as f:
                f.write(content)
            log.append(f"  Written: {dst_txt}")

            summary.append((tag, "OK", n_lower, n_upper, log))

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for tag, status, nl, nu, log in summary:
        for line in log:
            print(line)
        print()

    print("-" * 60)
    print(f"{'Tag':<35} {'Status':<10} {'Lower':<10} {'Upper':<10}")
    print("-" * 60)
    for tag, status, nl, nu, _ in summary:
        print(f"{tag:<35} {status:<10} {nl:<10} {nu:<10}")

    ok_count = sum(1 for _, s, _, _, _ in summary if s == "OK")
    skip_count = sum(1 for _, s, _, _, _ in summary if s in ("SKIP", "DRY-RUN"))
    err_count = sum(1 for _, s, _, _, _ in summary if s == "ERROR")
    print(f"\nTotal: {ok_count} OK, {skip_count} skipped, {err_count} errors")


if __name__ == "__main__":
    main()
