#!/usr/bin/env python3
"""Gather A2 structure lists and audit BAU cost values.

Default behavior:
- copy all live A2_Structure_Lists*.xlsx files into one timestamped folder,
  grouped by country;
- analyze ENERGY model BAU CapitalCost, FixedCost, and VariableCost CSV files;
- use A2 lists plus A1_Outputs workbooks to build technology/fuel dictionaries;
- flag zero, one, flat, and dominant repeated cost values.

The script only writes inside a fresh timestamped folder under --output-root.
It never edits model inputs.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

from openpyxl import load_workbook


COST_FILES = ("CapitalCost.csv", "FixedCost.csv", "VariableCost.csv")
COST_PARAMETERS = ("CapitalCost", "FixedCost", "VariableCost")
SKIP_ROOT_DIRS = {
    "_deprecate",
    "_deprecate_csv",
    "_old_scripts",
    "_STAGE1_OUTPUT",
    "_STAGE3_OUTPUT",
    "_STAGE4_OUTPUT",
    "_STAGE5_OUTPUT",
    "_COST_AUDIT_OUTPUT",
}
A1_NAME_WORKBOOK_PREFIXES = (
    "A-O_Parametrization",
    "A-O_AR_Model_Base_Year",
    "A-O_Demand",
    "A-O_Fleet",
)
NULLISH = {"", "NULL", "NA", "N/A", "NAN", "NONE"}


@dataclass(frozen=True)
class StructureFile:
    country: str
    path: Path
    model_root: Path
    model_label: str
    matches_sector: bool


@dataclass
class CostStats:
    rows: int = 0
    numeric: int = 0
    blank_or_null: int = 0
    non_numeric: int = 0
    zeros: int = 0
    ones: int = 0
    values: Counter[str] = field(default_factory=Counter)
    years: set[str] = field(default_factory=set)
    fuels: set[str] = field(default_factory=set)
    modes: set[str] = field(default_factory=set)

    def add(self, row: dict[str, str]) -> None:
        self.rows += 1

        year = clean(row.get("YEAR"))
        if year:
            self.years.add(year)
        fuel = clean(row.get("FUEL"))
        if fuel:
            self.fuels.add(fuel)
        mode = clean(row.get("MODE_OF_OPERATION"))
        if mode:
            self.modes.add(mode)

        parsed = parse_decimal(clean(row.get("Value")))
        if parsed is None:
            if clean(row.get("Value")).upper() in NULLISH:
                self.blank_or_null += 1
            else:
                self.non_numeric += 1
            return

        self.numeric += 1
        if parsed == 0:
            self.zeros += 1
        if parsed == 1:
            self.ones += 1
        self.values[format_decimal(parsed)] += 1


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_header(value: Any) -> str:
    return clean(value).lower().replace("_", ".")


def parse_decimal(value: str) -> Decimal | None:
    if value.upper() in NULLISH:
        return None
    try:
        return Decimal(value.replace(",", ""))
    except InvalidOperation:
        return None


def format_decimal(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(int(value))
    text = format(value.normalize(), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return ""
    return f"{100 * numerator / denominator:.1f}%"


def rel(root: Path, path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def safe_slug(text: str) -> str:
    out = []
    for char in text:
        if char.isalnum() or char in "._-":
            out.append(char)
        elif char in "\\/ ":
            out.append("__")
    return "".join(out).strip("_") or "model"


def is_live_path(root: Path, path: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    return not any(part in SKIP_ROOT_DIRS for part in parts)


def iter_country_dirs(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith("_") and path.name not in SKIP_ROOT_DIRS
    )


def sector_matches(path: Path, country_dir: Path, sector: str) -> bool:
    if sector.lower() == "all":
        return True
    sector_lower = sector.lower()
    try:
        parts = path.relative_to(country_dir).parts
    except ValueError:
        parts = path.parts
    return any(sector_lower in part.lower() for part in parts)


def find_structure_files(root: Path, sector: str) -> list[StructureFile]:
    files: list[StructureFile] = []
    for country_dir in iter_country_dirs(root):
        for path in sorted(country_dir.rglob("A2_Structure_Lists*.xlsx")):
            if path.name.startswith("~$") or not is_live_path(root, path):
                continue
            model_root = path.parent
            files.append(
                StructureFile(
                    country=country_dir.name,
                    path=path,
                    model_root=model_root,
                    model_label=rel(country_dir, model_root),
                    matches_sector=sector_matches(model_root, country_dir, sector),
                )
            )
    return files


def select_sector_models(files: Iterable[StructureFile]) -> list[StructureFile]:
    selected: dict[Path, StructureFile] = {}
    for item in files:
        if not item.matches_sector:
            continue
        current = selected.get(item.model_root)
        if current is None or item.path.name == "A2_Structure_Lists.xlsx":
            selected[item.model_root] = item
    return [selected[path] for path in sorted(selected)]


def find_bau_path(model_root: Path) -> Path | None:
    candidates = (
        model_root / "B1_Output_Params" / "BAU",
        model_root / "t1_confection" / "B1_Output_Params" / "BAU",
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def find_a1_outputs_path(model_root: Path) -> Path | None:
    candidates = (
        model_root / "A1_Outputs",
        model_root / "t1_confection" / "A1_Outputs",
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def copy_structure_files(root: Path, out_dir: Path, files: list[StructureFile]) -> list[dict[str, Any]]:
    copied_root = out_dir / "A2_Structure_Lists_collected"
    copied_root.mkdir(parents=True, exist_ok=False)
    rows: list[dict[str, Any]] = []
    for item in files:
        country_dir = copied_root / item.country
        country_dir.mkdir(parents=True, exist_ok=True)
        dest = country_dir / f"{safe_slug(item.model_label)}__{item.path.name}"
        if dest.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {dest}")
        shutil.copy2(item.path, dest)
        rows.append(
            {
                "country": item.country,
                "model_label": item.model_label,
                "source_relpath": rel(root, item.path),
                "copied_relpath": rel(root, dest),
                "size_bytes": item.path.stat().st_size,
                "matches_requested_sector": "YES" if item.matches_sector else "NO",
            }
        )
    return rows


def extract_a2_list_values(root: Path, files: list[StructureFile]) -> tuple[list[dict[str, Any]], set[tuple[str, str, str]], set[tuple[str, str, str]]]:
    rows: list[dict[str, Any]] = []
    sector_techs: set[tuple[str, str, str]] = set()
    sector_fuels: set[tuple[str, str, str]] = set()

    for item in files:
        try:
            workbook = load_workbook(item.path, read_only=True, data_only=True)
            try:
                for sheet in workbook.worksheets:
                    iterator = sheet.iter_rows(values_only=True)
                    headers = next(iterator, None)
                    if not headers:
                        continue
                    header_names = [clean(header) for header in headers]
                    seen_by_column: list[set[str]] = [set() for _ in header_names]
                    for row_number, values in enumerate(iterator, start=2):
                        for index, list_name in enumerate(header_names):
                            if not list_name or index >= len(values):
                                continue
                            value = clean(values[index])
                            if not value or value in seen_by_column[index]:
                                continue
                            seen_by_column[index].add(value)
                            rows.append(
                                {
                                    "country": item.country,
                                    "model_label": item.model_label,
                                    "source_workbook": rel(root, item.path),
                                    "sheet": sheet.title,
                                    "list_name": list_name,
                                    "value": value,
                                    "source_row": row_number,
                                    "matches_requested_sector": "YES" if item.matches_sector else "NO",
                                }
                            )
                            if item.matches_sector and list_name.lower() == "tech":
                                sector_techs.add((item.country, item.model_label, value))
                            if item.matches_sector and list_name.lower() == "fuel":
                                sector_fuels.add((item.country, item.model_label, value))
            finally:
                workbook.close()
        except Exception as exc:
            rows.append(
                {
                    "country": item.country,
                    "model_label": item.model_label,
                    "source_workbook": rel(root, item.path),
                    "sheet": "",
                    "list_name": "",
                    "value": "",
                    "source_row": "",
                    "matches_requested_sector": "YES" if item.matches_sector else "NO",
                    "note": f"ERROR: {exc}",
                }
            )

    return rows, sector_techs, sector_fuels


def direct_a1_workbooks(a1_outputs: Path | None) -> list[Path]:
    if a1_outputs is None or not a1_outputs.is_dir():
        return []
    return sorted(
        path
        for path in a1_outputs.glob("*.xlsx")
        if not path.name.startswith("~$") and path.name.startswith(A1_NAME_WORKBOOK_PREFIXES)
    )


def header_map(headers: Iterable[Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for index, header in enumerate(headers):
        key = normalize_header(header)
        if key and key not in out:
            out[key] = index
    return out


def cell(row: tuple[Any, ...], index: int | None) -> str:
    if index is None or index >= len(row):
        return ""
    return clean(row[index])


def add_id_source(
    rows: list[dict[str, Any]],
    aggregate: dict[tuple[str, str, str, str], dict[str, set[str]]],
    country: str,
    model_label: str,
    id_type: str,
    identifier: str,
    name: str,
    source_workbook: str,
    sheet: str,
    source_row: int,
) -> None:
    if not identifier or identifier.lower() == "none":
        return
    key = (country, model_label, id_type, identifier)
    if name:
        aggregate[key]["name_candidates"].add(name)
    aggregate[key]["source_workbooks"].add(source_workbook)
    aggregate[key]["source_sheets"].add(sheet)
    rows.append(
        {
            "country": country,
            "model_label": model_label,
            "id_type": id_type,
            "id": identifier,
            "name": name,
            "source_workbook": source_workbook,
            "sheet": sheet,
            "source_row": source_row,
        }
    )


def extract_a1_id_names(
    root: Path,
    model_files: list[StructureFile],
) -> tuple[list[dict[str, Any]], dict[tuple[str, str, str, str], dict[str, str]]]:
    source_rows: list[dict[str, Any]] = []
    aggregate: dict[tuple[str, str, str, str], dict[str, set[str]]] = defaultdict(
        lambda: {"name_candidates": set(), "source_workbooks": set(), "source_sheets": set()}
    )

    for item in model_files:
        for workbook_path in direct_a1_workbooks(find_a1_outputs_path(item.model_root)):
            source_relpath = rel(root, workbook_path)
            try:
                workbook = load_workbook(workbook_path, read_only=True, data_only=True)
                try:
                    for sheet in workbook.worksheets:
                        iterator = sheet.iter_rows(values_only=True)
                        headers = next(iterator, None)
                        if not headers:
                            continue
                        mapping = header_map(headers)
                        raw_headers = [clean(header) for header in headers]

                        tech_idx = mapping.get("tech")
                        tech_name_idx = mapping.get("tech.name")
                        fuel_tech_idx = mapping.get("fuel/tech")
                        generic_name_idx = mapping.get("name")

                        fuel_pairs: list[tuple[int, int | None]] = []
                        for idx, header in enumerate(raw_headers):
                            header_norm = normalize_header(header)
                            if not header_norm.startswith("fuel") or header_norm.endswith(".name"):
                                continue
                            name_idx = mapping.get(f"{header_norm}.name")
                            fuel_pairs.append((idx, name_idx))

                        for row_number, row in enumerate(iterator, start=2):
                            add_id_source(
                                source_rows,
                                aggregate,
                                item.country,
                                item.model_label,
                                "technology",
                                cell(row, tech_idx),
                                cell(row, tech_name_idx),
                                source_relpath,
                                sheet.title,
                                row_number,
                            )
                            add_id_source(
                                source_rows,
                                aggregate,
                                item.country,
                                item.model_label,
                                "fuel_or_tech",
                                cell(row, fuel_tech_idx),
                                cell(row, generic_name_idx),
                                source_relpath,
                                sheet.title,
                                row_number,
                            )
                            for fuel_idx, name_idx in fuel_pairs:
                                add_id_source(
                                    source_rows,
                                    aggregate,
                                    item.country,
                                    item.model_label,
                                    "fuel",
                                    cell(row, fuel_idx),
                                    cell(row, name_idx),
                                    source_relpath,
                                    sheet.title,
                                    row_number,
                                )
                finally:
                    workbook.close()
            except Exception as exc:
                source_rows.append(
                    {
                        "country": item.country,
                        "model_label": item.model_label,
                        "id_type": "",
                        "id": "",
                        "name": "",
                        "source_workbook": source_relpath,
                        "sheet": "",
                        "source_row": "",
                        "note": f"ERROR: {exc}",
                    }
                )

    lookup: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for key, values in aggregate.items():
        lookup[key] = {
            "name_candidates": " | ".join(sorted(values["name_candidates"])),
            "source_workbooks": " | ".join(sorted(values["source_workbooks"])),
            "source_sheets": " | ".join(sorted(values["source_sheets"])),
        }
    return source_rows, lookup


def summarize_stats(stats: CostStats, dominant_threshold: float, placeholder_threshold: float) -> dict[str, Any]:
    top_value = ""
    top_count = 0
    if stats.values:
        top_value, top_count = stats.values.most_common(1)[0]

    unique_values = len(stats.values)
    top_share = top_count / stats.numeric if stats.numeric else 0
    one_share = stats.ones / stats.numeric if stats.numeric else 0
    flags: list[str] = []

    if stats.blank_or_null:
        flags.append("HAS_BLANK_OR_NULL")
    if stats.non_numeric:
        flags.append("HAS_NON_NUMERIC")
    if stats.numeric == 0 and stats.rows:
        flags.append("NO_NUMERIC_VALUES")
    if stats.numeric and stats.zeros == stats.numeric:
        flags.append("ALL_ZERO")
    elif stats.zeros:
        flags.append("HAS_ZERO_VALUES")
    if stats.numeric and stats.ones == stats.numeric:
        flags.append("ALL_ONE")
    elif stats.ones and one_share >= placeholder_threshold:
        flags.append("MANY_ONE_VALUES")
    if stats.numeric > 1 and unique_values == 1:
        if top_value not in {"0", "1"}:
            flags.append("FLAT_REPEATED_NONZERO")
        else:
            flags.append("FLAT_REPEATED")
    elif stats.numeric >= 10 and top_share >= dominant_threshold:
        flags.append("DOMINANT_REPEATED_VALUE")
    if stats.numeric >= 10 and unique_values <= 2:
        flags.append("LOW_VARIETY")

    return {
        "rows": stats.rows,
        "numeric_values": stats.numeric,
        "blank_or_null": stats.blank_or_null,
        "non_numeric": stats.non_numeric,
        "zero_count": stats.zeros,
        "zero_share": pct(stats.zeros, stats.numeric),
        "one_count": stats.ones,
        "one_share": pct(stats.ones, stats.numeric),
        "unique_values": unique_values,
        "dominant_value": top_value,
        "dominant_count": top_count,
        "dominant_share": pct(top_count, stats.numeric),
        "year_min": min(stats.years) if stats.years else "",
        "year_max": max(stats.years) if stats.years else "",
        "year_count": len(stats.years),
        "fuel_values_in_cost_file": " | ".join(sorted(stats.fuels)),
        "mode_values": " | ".join(sorted(stats.modes)),
        "flags": " | ".join(flags),
    }


def cost_tech(row: dict[str, str]) -> str:
    for key in ("TECHNOLOGY", "Technology", "tech", "TECH"):
        value = clean(row.get(key))
        if value:
            return value
    return "(missing technology)"


def read_costs(
    root: Path,
    model_files: list[StructureFile],
    a2_techs: set[tuple[str, str, str]],
    a2_fuels: set[tuple[str, str, str]],
    id_lookup: dict[tuple[str, str, str, str], dict[str, str]],
    dominant_threshold: float,
    placeholder_threshold: float,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    stats_by_key: dict[tuple[str, str, str, str], CostStats] = defaultdict(CostStats)
    file_stats: dict[tuple[str, str, str], CostStats] = defaultdict(CostStats)
    inventory_rows: list[dict[str, Any]] = []

    for item in model_files:
        bau_path = find_bau_path(item.model_root)
        a1_path = find_a1_outputs_path(item.model_root)
        inventory = {
            "country": item.country,
            "model_label": item.model_label,
            "model_root": rel(root, item.model_root),
            "a2_structure_list": rel(root, item.path),
            "a1_outputs": rel(root, a1_path),
            "bau_path": rel(root, bau_path),
        }
        for file_name in COST_FILES:
            inventory[file_name] = "YES" if bau_path and (bau_path / file_name).is_file() else "NO"
        inventory_rows.append(inventory)

        if bau_path is None:
            continue

        for file_name in COST_FILES:
            cost_path = bau_path / file_name
            if not cost_path.is_file():
                continue
            parameter = file_name.replace(".csv", "")
            with cost_path.open("r", newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    tech = cost_tech(row)
                    stats_by_key[(item.country, item.model_label, tech, parameter)].add(row)
                    file_stats[(item.country, item.model_label, parameter)].add(row)

    parameter_rows: list[dict[str, Any]] = []
    distribution_rows: list[dict[str, Any]] = []
    technology_keys: set[tuple[str, str, str]] = set()

    for (country, model_label, tech, parameter), stats in sorted(stats_by_key.items()):
        technology_keys.add((country, model_label, tech))
        tech_lookup = id_lookup.get((country, model_label, "technology", tech), {})
        summary = summarize_stats(stats, dominant_threshold, placeholder_threshold)
        parameter_rows.append(
            {
                "country": country,
                "model_label": model_label,
                "technology": tech,
                "parameter": parameter,
                "in_a2_tech_list": "YES" if (country, model_label, tech) in a2_techs else "NO",
                "tech_name_candidates": tech_lookup.get("name_candidates", ""),
                "name_source_sheets": tech_lookup.get("source_sheets", ""),
                **summary,
            }
        )
        for value, count in stats.values.most_common():
            distribution_rows.append(
                {
                    "country": country,
                    "model_label": model_label,
                    "technology": tech,
                    "parameter": parameter,
                    "value": value,
                    "count": count,
                    "share_of_numeric_values": pct(count, stats.numeric),
                }
            )

    matrix_rows: list[dict[str, Any]] = []
    anomaly_rows: list[dict[str, Any]] = []
    high_priority_rows: list[dict[str, Any]] = []
    for country, model_label, tech in sorted(technology_keys):
        tech_lookup = id_lookup.get((country, model_label, "technology", tech), {})
        row: dict[str, Any] = {
            "country": country,
            "model_label": model_label,
            "technology": tech,
            "in_a2_tech_list": "YES" if (country, model_label, tech) in a2_techs else "NO",
            "tech_name_candidates": tech_lookup.get("name_candidates", ""),
            "name_source_sheets": tech_lookup.get("source_sheets", ""),
        }
        review_flags: list[str] = []
        for parameter in COST_PARAMETERS:
            stats = stats_by_key.get((country, model_label, tech, parameter))
            prefix = parameter.replace("Cost", "").lower()
            if stats is None:
                row[f"{prefix}_exists"] = "NO"
                for suffix in ("rows", "zero_share", "one_share", "unique_values", "dominant_value", "dominant_share", "flags"):
                    row[f"{prefix}_{suffix}"] = ""
                review_flags.append(f"{parameter}:MISSING")
                continue
            summary = summarize_stats(stats, dominant_threshold, placeholder_threshold)
            row[f"{prefix}_exists"] = "YES"
            row[f"{prefix}_rows"] = summary["rows"]
            row[f"{prefix}_zero_share"] = summary["zero_share"]
            row[f"{prefix}_one_share"] = summary["one_share"]
            row[f"{prefix}_unique_values"] = summary["unique_values"]
            row[f"{prefix}_dominant_value"] = summary["dominant_value"]
            row[f"{prefix}_dominant_share"] = summary["dominant_share"]
            row[f"{prefix}_flags"] = summary["flags"]
            if summary["flags"]:
                review_flags.extend(f"{parameter}:{flag}" for flag in summary["flags"].split(" | "))
        row["review_flags"] = " | ".join(review_flags)
        matrix_rows.append(row)
        if review_flags:
            anomaly_rows.append(row)
        if any(
            token in row["review_flags"]
            for token in (
                "HAS_ZERO_VALUES",
                "ALL_ZERO",
                "MANY_ONE_VALUES",
                "ALL_ONE",
                "MISSING",
                "HAS_BLANK_OR_NULL",
                "HAS_NON_NUMERIC",
                "NO_NUMERIC_VALUES",
            )
        ):
            high_priority_rows.append(row)

    file_summary_rows: list[dict[str, Any]] = []
    for (country, model_label, parameter), stats in sorted(file_stats.items()):
        file_summary_rows.append(
            {
                "country": country,
                "model_label": model_label,
                "parameter": parameter,
                **summarize_stats(stats, dominant_threshold, placeholder_threshold),
            }
        )

    fuel_dictionary_rows: list[dict[str, Any]] = []
    for country, model_label, fuel in sorted(a2_fuels):
        lookup = id_lookup.get((country, model_label, "fuel", fuel), {})
        fallback = id_lookup.get((country, model_label, "fuel_or_tech", fuel), {})
        fuel_dictionary_rows.append(
            {
                "country": country,
                "model_label": model_label,
                "fuel": fuel,
                "fuel_name_candidates": lookup.get("name_candidates") or fallback.get("name_candidates", ""),
                "name_source_sheets": lookup.get("source_sheets") or fallback.get("source_sheets", ""),
            }
        )

    return (
        inventory_rows,
        file_summary_rows,
        parameter_rows,
        matrix_rows,
        anomaly_rows,
        high_priority_rows,
        distribution_rows,
        fuel_dictionary_rows,
    )


def make_output_dir(root: Path, output_root_name: str, sector: str) -> Path:
    output_root = root / output_root_name
    output_root.mkdir(exist_ok=True)
    out_dir = output_root / f"a2_{sector.lower()}_cost_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if out_dir.exists():
        raise FileExistsError(f"Refusing to reuse output folder: {out_dir}")
    out_dir.mkdir()
    return out_dir


def write_readme(out_dir: Path, sector: str, copied: int, analyzed: int, anomalies: int) -> None:
    readme = out_dir / "README.txt"
    if readme.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {readme}")
    readme.write_text(
        "\n".join(
            [
                "A2 structure list and BAU cost audit",
                "",
                f"Cost sector analyzed: {sector}",
                f"A2 structure list workbooks copied: {copied}",
                f"Sector model roots analyzed: {analyzed}",
                f"Technology rows with review flags: {anomalies}",
                "",
                "Main files:",
                "- A2_Structure_Lists_collected/: copied A2 workbooks, grouped by country.",
                "- a2_structure_lists_index.csv: source and copied path for every gathered A2 workbook.",
                "- a2_structure_list_values.csv: long-form IDs from Year/Tech/Fuel/Emission/MOO/Region lists.",
                "- model_inventory.csv: sector model roots and BAU cost file presence.",
                "- id_dictionary.csv and id_name_sources.csv: names inferred from A1_Outputs.",
                "- fuel_dictionary.csv: A2 fuel IDs with inferred names where available.",
                "- country_cost_file_summary.csv: file-level cost value patterns.",
                "- energy_cost_parameter_summary.csv: one row per technology and cost parameter.",
                "- energy_cost_technology_matrix.csv: capital/fixed/variable side by side per technology.",
                "- energy_cost_anomalies.csv: technologies with any review flag, including flat/repeated values.",
                "- energy_cost_high_priority_anomalies.csv: zeros, ones, missing, blank/null, or nonnumeric values.",
                "- energy_cost_value_distribution.csv: exact value counts by technology and parameter.",
                "",
                "Flags are review prompts, not automatic errors. Zero, one, or flat values can be valid.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Gather A2 structure lists and audit BAU costs.")
    parser.add_argument("--root", default=".", help="Repository/model root.")
    parser.add_argument("--sector", default="energy", help="Sector to analyze for costs; use 'all' for all sectors.")
    parser.add_argument("--output-root", default="_COST_AUDIT_OUTPUT", help="Where timestamped outputs are written.")
    parser.add_argument("--sector-a2-only", action="store_true", help="Only copy A2 workbooks matching --sector.")
    parser.add_argument("--dominant-threshold", type=float, default=0.90, help="Dominant repeated-value flag threshold.")
    parser.add_argument("--placeholder-threshold", type=float, default=0.50, help="Value=1 placeholder-like threshold.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"Root folder does not exist: {root}")

    all_structure_files = find_structure_files(root, args.sector)
    sector_models = select_sector_models(all_structure_files)
    files_to_copy = [item for item in all_structure_files if item.matches_sector] if args.sector_a2_only else all_structure_files

    out_dir = make_output_dir(root, args.output_root, args.sector)
    index_rows = copy_structure_files(root, out_dir, files_to_copy)
    list_value_rows, a2_techs, a2_fuels = extract_a2_list_values(root, files_to_copy)
    id_source_rows, id_lookup = extract_a1_id_names(root, sector_models)

    id_dictionary_rows = []
    for (country, model_label, id_type, identifier), data in sorted(id_lookup.items()):
        id_dictionary_rows.append(
            {
                "country": country,
                "model_label": model_label,
                "id_type": id_type,
                "id": identifier,
                **data,
            }
        )

    (
        inventory_rows,
        file_summary_rows,
        parameter_rows,
        matrix_rows,
        anomaly_rows,
        high_priority_rows,
        distribution_rows,
        fuel_dictionary_rows,
    ) = read_costs(
        root,
        sector_models,
        a2_techs,
        a2_fuels,
        id_lookup,
        args.dominant_threshold,
        args.placeholder_threshold,
    )

    write_csv(
        out_dir / "a2_structure_lists_index.csv",
        index_rows,
        ["country", "model_label", "source_relpath", "copied_relpath", "size_bytes", "matches_requested_sector"],
    )
    write_csv(
        out_dir / "a2_structure_list_values.csv",
        list_value_rows,
        ["country", "model_label", "source_workbook", "sheet", "list_name", "value", "source_row", "matches_requested_sector"],
    )
    write_csv(
        out_dir / "model_inventory.csv",
        inventory_rows,
        ["country", "model_label", "model_root", "a2_structure_list", "a1_outputs", "bau_path", *COST_FILES],
    )
    write_csv(
        out_dir / "id_dictionary.csv",
        id_dictionary_rows,
        ["country", "model_label", "id_type", "id", "name_candidates", "source_workbooks", "source_sheets"],
    )
    write_csv(
        out_dir / "id_name_sources.csv",
        id_source_rows,
        ["country", "model_label", "id_type", "id", "name", "source_workbook", "sheet", "source_row"],
    )
    write_csv(
        out_dir / "fuel_dictionary.csv",
        fuel_dictionary_rows,
        ["country", "model_label", "fuel", "fuel_name_candidates", "name_source_sheets"],
    )
    write_csv(
        out_dir / "country_cost_file_summary.csv",
        file_summary_rows,
        [
            "country",
            "model_label",
            "parameter",
            "rows",
            "numeric_values",
            "blank_or_null",
            "non_numeric",
            "zero_count",
            "zero_share",
            "one_count",
            "one_share",
            "unique_values",
            "dominant_value",
            "dominant_count",
            "dominant_share",
            "year_min",
            "year_max",
            "year_count",
            "fuel_values_in_cost_file",
            "mode_values",
            "flags",
        ],
    )
    write_csv(
        out_dir / "energy_cost_parameter_summary.csv",
        parameter_rows,
        [
            "country",
            "model_label",
            "technology",
            "parameter",
            "in_a2_tech_list",
            "tech_name_candidates",
            "name_source_sheets",
            "rows",
            "numeric_values",
            "blank_or_null",
            "non_numeric",
            "zero_count",
            "zero_share",
            "one_count",
            "one_share",
            "unique_values",
            "dominant_value",
            "dominant_count",
            "dominant_share",
            "year_min",
            "year_max",
            "year_count",
            "fuel_values_in_cost_file",
            "mode_values",
            "flags",
        ],
    )
    matrix_fields = [
        "country",
        "model_label",
        "technology",
        "in_a2_tech_list",
        "tech_name_candidates",
        "name_source_sheets",
        "capital_exists",
        "capital_rows",
        "capital_zero_share",
        "capital_one_share",
        "capital_unique_values",
        "capital_dominant_value",
        "capital_dominant_share",
        "capital_flags",
        "fixed_exists",
        "fixed_rows",
        "fixed_zero_share",
        "fixed_one_share",
        "fixed_unique_values",
        "fixed_dominant_value",
        "fixed_dominant_share",
        "fixed_flags",
        "variable_exists",
        "variable_rows",
        "variable_zero_share",
        "variable_one_share",
        "variable_unique_values",
        "variable_dominant_value",
        "variable_dominant_share",
        "variable_flags",
        "review_flags",
    ]
    write_csv(out_dir / "energy_cost_technology_matrix.csv", matrix_rows, matrix_fields)
    write_csv(out_dir / "energy_cost_anomalies.csv", anomaly_rows, matrix_fields)
    write_csv(out_dir / "energy_cost_high_priority_anomalies.csv", high_priority_rows, matrix_fields)
    write_csv(
        out_dir / "energy_cost_value_distribution.csv",
        distribution_rows,
        ["country", "model_label", "technology", "parameter", "value", "count", "share_of_numeric_values"],
    )
    write_readme(out_dir, args.sector, len(index_rows), len(sector_models), len(anomaly_rows))

    print(f"Output folder: {out_dir}")
    print(f"A2 structure list workbooks copied: {len(index_rows)}")
    print(f"Sector model roots analyzed: {len(sector_models)}")
    print(f"A2 list values extracted: {len(list_value_rows)}")
    print(f"A1 ID/name dictionary rows: {len(id_dictionary_rows)}")
    print(f"Cost technology rows: {len(matrix_rows)}")
    print(f"Technology rows with review flags: {len(anomaly_rows)}")
    print(f"High-priority anomaly rows: {len(high_priority_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
