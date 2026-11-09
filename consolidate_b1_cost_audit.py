#!/usr/bin/env python3
"""Consolidate B1 configs, technology names, and BAU cost anomalies.

Default scope is the live ENERGY models under each country folder. The script
also gathers all live B1_Scenario_Config*.xlsx workbooks into the output folder
so they can be reviewed side by side.

It only writes inside a fresh timestamped folder under --output-root.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

try:
    from openpyxl import load_workbook
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "Missing dependency: openpyxl. Run with the Python that has openpyxl "
        "installed, for example: py -3 consolidate_b1_cost_audit.py"
    ) from exc


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
}
TECH_HEADER_KEYS = ("tech", "technology")
NAME_HEADER_KEYS = ("tech.name", "technology.name", "name", "description")


@dataclass(frozen=True)
class ConfigFile:
    country: str
    path: Path
    model_root: Path
    model_label: str
    matches_sector: bool


@dataclass
class ValueStats:
    rows: int = 0
    blank_or_null: int = 0
    non_numeric: int = 0
    numeric: int = 0
    zeros: int = 0
    ones: int = 0
    values: Counter[str] = field(default_factory=Counter)
    years: set[str] = field(default_factory=set)
    fuels: set[str] = field(default_factory=set)
    modes: set[str] = field(default_factory=set)
    files: set[str] = field(default_factory=set)

    def add_row(self, row: dict[str, str], file_name: str) -> None:
        self.rows += 1
        self.files.add(file_name)

        year = clean_text(row.get("YEAR"))
        if year:
            self.years.add(year)

        fuel = clean_text(row.get("FUEL"))
        if fuel:
            self.fuels.add(fuel)

        mode = clean_text(row.get("MODE_OF_OPERATION"))
        if mode:
            self.modes.add(mode)

        raw_value = clean_text(row.get("Value"))
        parsed = parse_decimal(raw_value)
        if parsed is None:
            if is_blank_or_null(raw_value):
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


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def is_blank_or_null(value: str) -> bool:
    return value == "" or value.upper() in {"NULL", "NA", "N/A", "NAN", "NONE"}


def parse_decimal(value: str) -> Decimal | None:
    if is_blank_or_null(value):
        return None
    try:
        return Decimal(value.replace(",", ""))
    except InvalidOperation:
        return None


def format_decimal(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(int(value))
    out = format(value.normalize(), "f")
    return out.rstrip("0").rstrip(".") if "." in out else out


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
    return (
        text.replace("\\", "__")
        .replace("/", "__")
        .replace(":", "")
        .replace(" ", "_")
    )


def is_live_path(root: Path, path: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    return not any(part in SKIP_ROOT_DIRS for part in parts)


def iter_country_dirs(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.iterdir()
        if p.is_dir() and not p.name.startswith("_") and p.name not in SKIP_ROOT_DIRS
    )


def sector_matches(path: Path, root: Path, sector: str) -> bool:
    if sector.lower() == "all":
        return True
    sector_lower = sector.lower()
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    return any(sector_lower in part.lower() for part in parts)


def find_configs(root: Path, sector: str) -> list[ConfigFile]:
    configs: list[ConfigFile] = []
    for country_dir in iter_country_dirs(root):
        for path in sorted(country_dir.rglob("B1_Scenario_Config*.xlsx")):
            if path.name.startswith("~$"):
                continue
            if not is_live_path(root, path):
                continue
            model_root = path.parent
            configs.append(
                ConfigFile(
                    country=country_dir.name,
                    path=path,
                    model_root=model_root,
                    model_label=rel(country_dir, model_root),
                    matches_sector=sector_matches(model_root, country_dir, sector),
                )
            )
    return configs


def unique_model_roots(configs: Iterable[ConfigFile]) -> list[ConfigFile]:
    selected: dict[Path, ConfigFile] = {}
    for config in configs:
        if not config.matches_sector:
            continue
        current = selected.get(config.model_root)
        if current is None:
            selected[config.model_root] = config
        elif config.path.name == "B1_Scenario_Config.xlsx":
            selected[config.model_root] = config
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
        for row in rows:
            writer.writerow(row)


def copy_configs(root: Path, out_dir: Path, configs: list[ConfigFile]) -> list[dict[str, Any]]:
    copied_root = out_dir / "B1_Scenario_Config_collected"
    copied_root.mkdir(parents=True, exist_ok=False)
    index_rows: list[dict[str, Any]] = []

    for config in configs:
        country_dir = copied_root / config.country
        country_dir.mkdir(parents=True, exist_ok=True)
        dest_name = f"{safe_slug(config.model_label)}__{config.path.name}"
        dest = country_dir / dest_name
        if dest.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {dest}")
        shutil.copy2(config.path, dest)
        index_rows.append(
            {
                "country": config.country,
                "model_label": config.model_label,
                "source_relpath": rel(root, config.path),
                "copied_relpath": rel(root, dest),
                "size_bytes": config.path.stat().st_size,
                "matches_requested_sector": "YES" if config.matches_sector else "NO",
            }
        )
    return index_rows


def normalize_header(value: Any) -> str:
    return clean_text(value).lower().replace("_", ".")


def header_map(headers: Iterable[Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for idx, value in enumerate(headers):
        key = normalize_header(value)
        if key and key not in out:
            out[key] = idx
    return out


def first_existing(mapping: dict[str, int], keys: Iterable[str]) -> int | None:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def cell(row: tuple[Any, ...], idx: int | None) -> str:
    if idx is None or idx >= len(row):
        return ""
    return clean_text(row[idx])


def direct_a1_workbooks(a1_outputs: Path | None) -> list[Path]:
    if a1_outputs is None or not a1_outputs.is_dir():
        return []
    return sorted(
        p
        for p in a1_outputs.glob("*.xlsx")
        if not p.name.startswith("~$")
        and p.name.startswith(("A-O_Parametrization", "A-O_AR_Model_Base_Year", "A-O_Demand", "A-O_Fleet"))
    )


def extract_technology_sources(
    root: Path,
    model_configs: list[ConfigFile],
) -> tuple[list[dict[str, Any]], dict[tuple[str, str, str], dict[str, str]]]:
    source_rows: list[dict[str, Any]] = []
    aggregate: dict[tuple[str, str, str], dict[str, set[str]]] = defaultdict(
        lambda: {
            "tech_names": set(),
            "fuels": set(),
            "parameters": set(),
            "units": set(),
            "source_workbooks": set(),
            "source_sheets": set(),
        }
    )

    for config in model_configs:
        a1_outputs = find_a1_outputs_path(config.model_root)
        for workbook_path in direct_a1_workbooks(a1_outputs):
            try:
                workbook = load_workbook(workbook_path, read_only=True, data_only=True)
            except Exception as exc:
                source_rows.append(
                    {
                        "country": config.country,
                        "model_label": config.model_label,
                        "source_workbook": rel(root, workbook_path),
                        "sheet": "",
                        "tech": "",
                        "tech_name": "",
                        "fuel": "",
                        "parameter": "",
                        "unit": "",
                        "source_row": "",
                        "note": f"ERROR: {exc}",
                    }
                )
                continue

            try:
                for sheet in workbook.worksheets:
                    rows = sheet.iter_rows(values_only=True)
                    try:
                        headers = next(rows)
                    except StopIteration:
                        continue
                    mapping = header_map(headers)
                    tech_idx = first_existing(mapping, TECH_HEADER_KEYS)
                    if tech_idx is None:
                        continue
                    name_idx = first_existing(mapping, NAME_HEADER_KEYS)
                    fuel_idx = first_existing(mapping, ("fuel",))
                    parameter_idx = first_existing(mapping, ("parameter",))
                    unit_idx = first_existing(mapping, ("unit", "unit.introduced"))

                    for row_number, row in enumerate(rows, start=2):
                        tech = cell(row, tech_idx)
                        if not tech:
                            continue
                        tech_name = cell(row, name_idx)
                        fuel = cell(row, fuel_idx)
                        parameter = cell(row, parameter_idx)
                        unit = cell(row, unit_idx)
                        key = (config.country, config.model_label, tech)
                        if tech_name:
                            aggregate[key]["tech_names"].add(tech_name)
                        if fuel:
                            aggregate[key]["fuels"].add(fuel)
                        if parameter:
                            aggregate[key]["parameters"].add(parameter)
                        if unit:
                            aggregate[key]["units"].add(unit)
                        aggregate[key]["source_workbooks"].add(rel(root, workbook_path))
                        aggregate[key]["source_sheets"].add(sheet.title)

                        source_rows.append(
                            {
                                "country": config.country,
                                "model_label": config.model_label,
                                "source_workbook": rel(root, workbook_path),
                                "sheet": sheet.title,
                                "tech": tech,
                                "tech_name": tech_name,
                                "fuel": fuel,
                                "parameter": parameter,
                                "unit": unit,
                                "source_row": row_number,
                                "note": "",
                            }
                        )
            finally:
                workbook.close()

    lookup: dict[tuple[str, str, str], dict[str, str]] = {}
    for key, data in aggregate.items():
        lookup[key] = {
            "tech_name_candidates": " | ".join(sorted(data["tech_names"])),
            "fuel_candidates": " | ".join(sorted(data["fuels"])),
            "parameter_candidates": " | ".join(sorted(data["parameters"])),
            "unit_candidates": " | ".join(sorted(data["units"])),
            "source_workbooks": " | ".join(sorted(data["source_workbooks"])),
            "source_sheets": " | ".join(sorted(data["source_sheets"])),
        }
    return source_rows, lookup


def summarize_stats(
    stats: ValueStats,
    dominant_threshold: float,
    placeholder_threshold: float,
) -> dict[str, Any]:
    top_value = ""
    top_count = 0
    if stats.values:
        top_value, top_count = stats.values.most_common(1)[0]
    unique_values = len(stats.values)
    top_share = top_count / stats.numeric if stats.numeric else 0.0
    zero_share = stats.zeros / stats.numeric if stats.numeric else 0.0
    one_share = stats.ones / stats.numeric if stats.numeric else 0.0

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
        only_value = next(iter(stats.values))
        if only_value not in {"0", "1"}:
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


def read_costs(
    root: Path,
    model_configs: list[ConfigFile],
    tech_lookup: dict[tuple[str, str, str], dict[str, str]],
    dominant_threshold: float,
    placeholder_threshold: float,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    stats_by_key: dict[tuple[str, str, str, str], ValueStats] = defaultdict(ValueStats)
    inventory_rows: list[dict[str, Any]] = []

    for config in model_configs:
        bau_path = find_bau_path(config.model_root)
        a1_outputs = find_a1_outputs_path(config.model_root)
        inventory = {
            "country": config.country,
            "model_label": config.model_label,
            "model_root": rel(root, config.model_root),
            "primary_config": rel(root, config.path),
            "a1_outputs": rel(root, a1_outputs),
            "bau_path": rel(root, bau_path),
        }
        for file_name in COST_FILES:
            inventory[file_name] = "YES" if bau_path and (bau_path / file_name).is_file() else "NO"
        inventory_rows.append(inventory)

        if bau_path is None:
            continue

        for file_name in COST_FILES:
            cost_path = bau_path / file_name
            parameter = file_name.replace(".csv", "")
            if not cost_path.is_file():
                continue
            with cost_path.open("r", newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    tech = clean_text(
                        row.get("TECHNOLOGY")
                        or row.get("Technology")
                        or row.get("tech")
                        or row.get("TECH")
                    )
                    if not tech:
                        tech = "(missing technology)"
                    key = (config.country, config.model_label, tech, parameter)
                    stats_by_key[key].add_row(row, file_name)

    parameter_rows: list[dict[str, Any]] = []
    value_distribution_rows: list[dict[str, Any]] = []
    tech_keys: set[tuple[str, str, str]] = set()

    for (country, model_label, tech, parameter), stats in sorted(stats_by_key.items()):
        tech_keys.add((country, model_label, tech))
        lookup = tech_lookup.get((country, model_label, tech), {})
        summary = summarize_stats(stats, dominant_threshold, placeholder_threshold)
        row = {
            "country": country,
            "model_label": model_label,
            "technology": tech,
            "parameter": parameter,
            **lookup,
            **summary,
        }
        parameter_rows.append(row)

        for value, count in stats.values.most_common():
            value_distribution_rows.append(
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

    for country, model_label, tech in sorted(tech_keys):
        lookup = tech_lookup.get((country, model_label, tech), {})
        matrix: dict[str, Any] = {
            "country": country,
            "model_label": model_label,
            "technology": tech,
            **lookup,
        }
        missing_parameters: list[str] = []
        all_flags: list[str] = []

        for parameter in COST_PARAMETERS:
            stats = stats_by_key.get((country, model_label, tech, parameter))
            prefix = parameter.replace("Cost", "").lower()
            if stats is None:
                missing_parameters.append(parameter)
                matrix[f"{prefix}_exists"] = "NO"
                for suffix in (
                    "rows",
                    "zero_share",
                    "one_share",
                    "unique_values",
                    "dominant_value",
                    "dominant_share",
                    "flags",
                ):
                    matrix[f"{prefix}_{suffix}"] = ""
                continue

            summary = summarize_stats(stats, dominant_threshold, placeholder_threshold)
            matrix[f"{prefix}_exists"] = "YES"
            matrix[f"{prefix}_rows"] = summary["rows"]
            matrix[f"{prefix}_zero_share"] = summary["zero_share"]
            matrix[f"{prefix}_one_share"] = summary["one_share"]
            matrix[f"{prefix}_unique_values"] = summary["unique_values"]
            matrix[f"{prefix}_dominant_value"] = summary["dominant_value"]
            matrix[f"{prefix}_dominant_share"] = summary["dominant_share"]
            matrix[f"{prefix}_flags"] = summary["flags"]
            if summary["flags"]:
                all_flags.extend(f"{parameter}:{flag}" for flag in summary["flags"].split(" | "))

        if missing_parameters:
            all_flags.append("MISSING_COST_PARAMETERS:" + ",".join(missing_parameters))
        matrix["review_flags"] = " | ".join(all_flags)
        matrix_rows.append(matrix)
        if all_flags:
            anomaly_rows.append(matrix)

    return inventory_rows, parameter_rows, matrix_rows, value_distribution_rows, anomaly_rows


def write_readme(
    out_dir: Path,
    sector: str,
    copied_count: int,
    model_count: int,
    anomaly_count: int,
) -> None:
    readme = out_dir / "README.txt"
    if readme.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {readme}")
    readme.write_text(
        "\n".join(
            [
                "B1 cost consolidation audit",
                "",
                f"Requested sector analyzed for costs: {sector}",
                f"B1 config workbooks copied: {copied_count}",
                f"Sector model roots analyzed: {model_count}",
                f"Technology rows with review flags: {anomaly_count}",
                "",
                "Files:",
                "- B1_Scenario_Config_collected/: copied live config workbooks, grouped by country.",
                "- configs_index.csv: source and copied path for each gathered config workbook.",
                "- model_inventory.csv: model roots, A1 output paths, BAU paths, and cost file presence.",
                "- technology_dictionary.csv: unique technology IDs and names inferred from A1_Outputs.",
                "- technology_dictionary_sources.csv: detailed source rows behind the dictionary.",
                "- energy_cost_parameter_summary.csv: one row per technology and cost parameter.",
                "- energy_cost_technology_matrix.csv: one row per technology with capital/fixed/variable summaries.",
                "- energy_cost_anomalies.csv: filtered matrix rows with any review flag.",
                "- energy_cost_value_distribution.csv: exact numeric value counts by technology and parameter.",
                "",
                "Review flags are intentionally conservative. A repeated or zero value can be valid,",
                "but these rows are the places worth checking before changing model inputs.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def make_output_dir(root: Path, output_root_name: str, sector: str) -> Path:
    output_root = root / output_root_name
    output_root.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = output_root / f"{sector.lower()}_b1_cost_audit_{timestamp}"
    if out_dir.exists():
        raise FileExistsError(f"Refusing to reuse output folder: {out_dir}")
    out_dir.mkdir()
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gather B1 scenario configs and summarize BAU cost anomalies."
    )
    parser.add_argument("--root", default=".", help="Repository/model root folder.")
    parser.add_argument(
        "--sector",
        default="energy",
        help="Sector name to analyze for costs. Use 'all' for every live B1 config model root.",
    )
    parser.add_argument(
        "--output-root",
        default="_COST_AUDIT_OUTPUT",
        help="Folder where a fresh timestamped output folder will be created.",
    )
    parser.add_argument(
        "--dominant-threshold",
        type=float,
        default=0.90,
        help="Share at or above which a repeated value is flagged as dominant.",
    )
    parser.add_argument(
        "--placeholder-threshold",
        type=float,
        default=0.50,
        help="Share at or above which Value=1 is flagged as placeholder-like.",
    )
    parser.add_argument(
        "--sector-configs-only",
        action="store_true",
        help="Only copy B1 configs that match --sector. Default copies all live configs.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"Root folder does not exist: {root}")

    configs = find_configs(root, args.sector)
    model_configs = unique_model_roots(configs)
    configs_to_copy = [c for c in configs if c.matches_sector] if args.sector_configs_only else configs

    out_dir = make_output_dir(root, args.output_root, args.sector)
    config_index_rows = copy_configs(root, out_dir, configs_to_copy)
    tech_source_rows, tech_lookup = extract_technology_sources(root, model_configs)

    dictionary_rows = []
    for (country, model_label, tech), data in sorted(tech_lookup.items()):
        dictionary_rows.append(
            {
                "country": country,
                "model_label": model_label,
                "technology": tech,
                **data,
            }
        )

    (
        inventory_rows,
        parameter_rows,
        matrix_rows,
        value_distribution_rows,
        anomaly_rows,
    ) = read_costs(
        root,
        model_configs,
        tech_lookup,
        args.dominant_threshold,
        args.placeholder_threshold,
    )

    write_csv(
        out_dir / "configs_index.csv",
        config_index_rows,
        [
            "country",
            "model_label",
            "source_relpath",
            "copied_relpath",
            "size_bytes",
            "matches_requested_sector",
        ],
    )
    write_csv(
        out_dir / "model_inventory.csv",
        inventory_rows,
        [
            "country",
            "model_label",
            "model_root",
            "primary_config",
            "a1_outputs",
            "bau_path",
            *COST_FILES,
        ],
    )
    write_csv(
        out_dir / "technology_dictionary.csv",
        dictionary_rows,
        [
            "country",
            "model_label",
            "technology",
            "tech_name_candidates",
            "fuel_candidates",
            "parameter_candidates",
            "unit_candidates",
            "source_workbooks",
            "source_sheets",
        ],
    )
    write_csv(
        out_dir / "technology_dictionary_sources.csv",
        tech_source_rows,
        [
            "country",
            "model_label",
            "source_workbook",
            "sheet",
            "tech",
            "tech_name",
            "fuel",
            "parameter",
            "unit",
            "source_row",
            "note",
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
            "tech_name_candidates",
            "fuel_candidates",
            "parameter_candidates",
            "unit_candidates",
            "source_workbooks",
            "source_sheets",
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
        out_dir / "energy_cost_technology_matrix.csv",
        matrix_rows,
        [
            "country",
            "model_label",
            "technology",
            "tech_name_candidates",
            "fuel_candidates",
            "parameter_candidates",
            "unit_candidates",
            "source_workbooks",
            "source_sheets",
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
        ],
    )
    write_csv(
        out_dir / "energy_cost_anomalies.csv",
        anomaly_rows,
        [
            "country",
            "model_label",
            "technology",
            "tech_name_candidates",
            "fuel_candidates",
            "parameter_candidates",
            "unit_candidates",
            "source_workbooks",
            "source_sheets",
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
        ],
    )
    write_csv(
        out_dir / "energy_cost_value_distribution.csv",
        value_distribution_rows,
        [
            "country",
            "model_label",
            "technology",
            "parameter",
            "value",
            "count",
            "share_of_numeric_values",
        ],
    )
    write_readme(out_dir, args.sector, len(config_index_rows), len(model_configs), len(anomaly_rows))

    print(f"Output folder: {out_dir}")
    print(f"B1 config workbooks copied: {len(config_index_rows)}")
    print(f"Sector model roots analyzed: {len(model_configs)}")
    print(f"Technology dictionary rows: {len(dictionary_rows)}")
    print(f"Cost technology rows: {len(matrix_rows)}")
    print(f"Rows with review flags: {len(anomaly_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
