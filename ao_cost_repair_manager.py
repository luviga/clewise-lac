#! python
"""Plan, apply, verify, and restore AO energy cost repairs.

This tool is intentionally manifest-first:

- ``plan`` reads AO workbooks plus approved source workbooks and writes CSV
  manifests/review tables under ``_COST_REPAIR_OUTPUT``. It does not edit model
  workbooks.
- ``apply`` only edits cells listed in an approved manifest, creates backups,
  and writes an apply log.
- ``verify`` checks that workbook cells match either the planned new values or
  the original old values.
- ``restore`` copies workbook backups from an apply log back into place.

The first repair target is Ecuador, but the code is structured so the same
workflow can be extended to the other LAC energy AO workbooks.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

from openpyxl import Workbook, load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parent))  # MODELS_LAC_5 root
from ao_safe_save import save_ao_safely  # Excel recalc + blank-formula guard


COST_PARAMETERS = ("CapitalCost", "FixedCost", "VariableCost")
DEFAULT_OUTPUT_ROOT = Path("_COST_REPAIR_OUTPUT")
DEFAULT_FUEL_WORKBOOK = (
    Path.home() / "Downloads" / "LAC_Fuel_Price_Projections_2026_v2_audit.xlsx"
)
DEFAULT_FUEL_SCENARIO = "REF"
DEFAULT_COUNTRY = "Ecuador"

COUNTRY_MODELS: dict[str, dict[str, str]] = {
    "CostaRica": {
        "iso": "CRI",
        "model_label": r"CR_ENERGY\t1_confection",
        "ao_path": r"CostaRica\CR_ENERGY\t1_confection\A1_Outputs\A-O_Parametrization.xlsx",
    },
    "DominicanRepublic": {
        "iso": "DOM",
        "model_label": "RD_ENERGY",
        "ao_path": r"DominicanRepublic\RD_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
    },
    "Ecuador": {
        "iso": "ECU",
        "model_label": "ECU_Energy",
        "ao_path": r"Ecuador\ECU_Energy\A1_Outputs\A-O_Parametrization.xlsx",
    },
    "Guatemala": {
        "iso": "GTM",
        "model_label": "GUA_ENERGY",
        "ao_path": r"Guatemala\GUA_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
    },
    "Honduras": {
        "iso": "HND",
        "model_label": "HON_ENERGY",
        "ao_path": r"Honduras\HON_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
    },
    "Jamaica": {
        "iso": "JAM",
        "model_label": "JAM_ENERGY",
        "ao_path": r"Jamaica\JAM_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
    },
}

ECUADOR_LOCAL_SOURCE_PATHS = (
    r"Ecuador\ECU_Energy\A1_Outputs\A-O_Parametrization_PLANMICC.xlsx",
    r"Ecuador\ECU_Energy\A1_Outputs\reference_PLANMICC\A-O_Parametrization_ref_planmicc.xlsx",
    r"Ecuador\ECU_Energy\A1_Outputs\reference_edited\A-O_Parametrization_ref.xlsx",
)

MANIFEST_FIELDS = [
    "manifest_id",
    "approved",
    "decision",
    "country",
    "model_label",
    "ao_path",
    "sheet",
    "row_index",
    "tech",
    "tech_name",
    "parameter",
    "unit",
    "year",
    "old_value",
    "new_value",
    "source_kind",
    "source_path",
    "source_sheet",
    "source_row_index",
    "source_tech",
    "source_tech_name",
    "source_unit",
    "source_projection_mode",
    "fuel_code",
    "scenario",
    "score",
    "reason",
    "row_fingerprint",
    "projection_mode_old",
    "projection_mode_new",
    "unit_conversion",
    "generated_at",
]

MAPPING_FIELDS = [
    "country",
    "model_label",
    "target_sheet",
    "target_row_index",
    "target_tech",
    "target_tech_name",
    "target_parameter",
    "target_unit",
    "target_projection_mode",
    "target_issue",
    "source_kind",
    "source_path",
    "source_sheet",
    "source_row_index",
    "source_tech",
    "source_tech_name",
    "source_parameter",
    "source_unit",
    "source_projection_mode",
    "score",
    "decision",
    "reason",
    "name_similarity",
    "token_jaccard",
    "target_family",
    "source_family",
    "target_fuel_code",
    "source_fuel_code",
    "coverage_share",
    "hard_conflict",
]

NO_MATCH_FIELDS = [
    "country",
    "model_label",
    "ao_path",
    "sheet",
    "row_index",
    "tech",
    "tech_name",
    "parameter",
    "unit",
    "projection_mode",
    "issue",
    "suggested_next_source",
    "suggested_atb_family",
    "reason",
]

SUMMARY_FIELDS = [
    "country",
    "model_label",
    "ao_path",
    "source_kind",
    "decision",
    "rows",
    "cells",
]

APPLY_LOG_FIELDS = [
    "apply_id",
    "timestamp",
    "manifest_path",
    "country",
    "ao_path",
    "backup_path",
    "dry_run",
    "approved_cells_seen",
    "cells_changed",
    "projection_modes_changed",
]


@dataclass(frozen=True)
class RowStats:
    cells: int
    numeric: int
    blank: int
    non_numeric: int
    zeros: int
    ones: int
    unique_numeric: int
    first_numeric: float | None

    @property
    def one_share(self) -> float:
        return self.ones / self.numeric if self.numeric else 0.0

    @property
    def zero_share(self) -> float:
        return self.zeros / self.numeric if self.numeric else 0.0

    @property
    def blank_share(self) -> float:
        return self.blank / self.cells if self.cells else 0.0


@dataclass(frozen=True)
class AoCostRow:
    country: str
    model_label: str
    workbook_path: Path
    source_label: str
    source_kind: str
    sheet: str
    row_index: int
    tech: str
    tech_name: str
    parameter: str
    unit: str
    projection_mode: str
    year_values: dict[int, Any]
    header_years: tuple[int, ...]

    @property
    def row_fingerprint(self) -> str:
        text = "|".join(
            [
                self.country,
                self.model_label,
                str(self.workbook_path),
                self.sheet,
                str(self.row_index),
                self.tech,
                self.tech_name,
                self.parameter,
            ]
        )
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class MatchScore:
    score: float
    decision: str
    reason: str
    name_similarity: float
    token_jaccard: float
    target_family: str
    source_family: str
    target_fuel_code: str
    source_fuel_code: str
    coverage_share: float
    hard_conflict: str


@dataclass
class PlanResult:
    output_dir: Path
    manifest_rows: list[dict[str, Any]] = field(default_factory=list)
    mapping_rows: list[dict[str, Any]] = field(default_factory=list)
    no_match_rows: list[dict[str, Any]] = field(default_factory=list)
    summary_rows: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_text(value: Any) -> str:
    text = clean(value).lower()
    text = (
        text.replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
        .replace("ó", "o")
        .replace("í", "i")
        .replace("é", "e")
        .replace("á", "a")
        .replace("ú", "u")
    )
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def token_set(value: Any) -> set[str]:
    stop = {
        "primary",
        "secondary",
        "transformation",
        "import",
        "distribution",
        "demand",
        "for",
        "the",
        "and",
        "of",
        "power",
        "plant",
        "technology",
    }
    return {tok for tok in normalize_text(value).split() if tok and tok not in stop}


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)
    text = clean(value)
    if not text or text.upper() in {"NA", "N/A", "NAN", "NULL", "NONE"}:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def same_number(left: Any, right: Any, tolerance: float = 1e-8) -> bool:
    lf = parse_float(left)
    rf = parse_float(right)
    if lf is None or rf is None:
        return clean(left) == clean(right)
    return abs(lf - rf) <= tolerance


def format_number(value: Any) -> str:
    number = parse_float(value)
    if number is None:
        return clean(value)
    if abs(number) < 1e-12:
        number = 0.0
    text = f"{number:.10f}".rstrip("0").rstrip(".")
    return text or "0"


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def rel_or_abs(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def normalize_header(value: Any) -> str:
    return clean(value).lower().replace("_", ".")


def find_header_row(ws: Any) -> int | None:
    max_col = min(ws.max_column or 1, 300)
    for row_index in range(1, min(ws.max_row or 1, 8) + 1):
        values = [
            ws.cell(row=row_index, column=col).value for col in range(1, max_col + 1)
        ]
        normalized = {normalize_header(v) for v in values if v is not None}
        if "tech" in normalized and "parameter" in normalized:
            return row_index
    return None


def build_header_map(ws: Any, header_row: int) -> dict[str | int, int]:
    max_col = min(ws.max_column or 1, 300)
    headers: dict[str | int, int] = {}
    for col in range(1, max_col + 1):
        value = ws.cell(row=header_row, column=col).value
        if value is None:
            continue
        if isinstance(value, int):
            headers[value] = col
            continue
        text = clean(value)
        if re.fullmatch(r"\d{4}", text):
            headers[int(text)] = col
        else:
            headers[text] = col
    return headers


def header_lookup(headers: dict[str | int, int], name: str) -> int | None:
    wanted = normalize_header(name)
    for key, col in headers.items():
        if isinstance(key, str) and normalize_header(key) == wanted:
            return col
    return None


def read_ao_cost_rows(
    path: Path,
    country: str,
    model_label: str,
    source_label: str,
    source_kind: str,
) -> list[AoCostRow]:
    rows: list[AoCostRow] = []
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        for ws in wb.worksheets:
            header_row = find_header_row(ws)
            if header_row is None:
                continue
            headers = build_header_map(ws, header_row)
            tech_col = header_lookup(headers, "Tech")
            name_col = header_lookup(headers, "Tech.Name")
            param_col = header_lookup(headers, "Parameter")
            unit_col = header_lookup(headers, "Unit")
            mode_col = header_lookup(headers, "Projection.Mode")
            if tech_col is None or param_col is None:
                continue
            years = tuple(sorted(k for k in headers if isinstance(k, int)))
            if not years:
                continue
            max_col = max(
                [tech_col, param_col]
                + ([name_col] if name_col else [])
                + ([unit_col] if unit_col else [])
                + ([mode_col] if mode_col else [])
                + [headers[y] for y in years]
            )
            for row_index, values in enumerate(
                ws.iter_rows(
                    min_row=header_row + 1,
                    max_row=ws.max_row,
                    max_col=max_col,
                    values_only=True,
                ),
                start=header_row + 1,
            ):
                tech = clean(values[tech_col - 1] if len(values) >= tech_col else "")
                parameter = clean(
                    values[param_col - 1] if len(values) >= param_col else ""
                )
                if not tech or parameter not in COST_PARAMETERS:
                    continue
                tech_name = clean(
                    values[name_col - 1]
                    if name_col is not None and len(values) >= name_col
                    else ""
                )
                unit = clean(
                    values[unit_col - 1]
                    if unit_col is not None and len(values) >= unit_col
                    else ""
                )
                projection_mode = clean(
                    values[mode_col - 1]
                    if mode_col is not None and len(values) >= mode_col
                    else ""
                )
                year_values = {
                    year: values[headers[year] - 1]
                    if len(values) >= headers[year]
                    else None
                    for year in years
                }
                rows.append(
                    AoCostRow(
                        country=country,
                        model_label=model_label,
                        workbook_path=path,
                        source_label=source_label,
                        source_kind=source_kind,
                        sheet=ws.title,
                        row_index=row_index,
                        tech=tech,
                        tech_name=tech_name,
                        parameter=parameter,
                        unit=unit,
                        projection_mode=projection_mode,
                        year_values=year_values,
                        header_years=years,
                    )
                )
    finally:
        wb.close()
    return rows


def row_stats(row: AoCostRow) -> RowStats:
    numeric_values: list[float] = []
    blank = 0
    non_numeric = 0
    zeros = 0
    ones = 0
    for value in row.year_values.values():
        text = clean(value)
        number = parse_float(value)
        if number is None:
            if not text:
                blank += 1
            else:
                non_numeric += 1
            continue
        numeric_values.append(number)
        if abs(number) < 1e-12:
            zeros += 1
        if abs(number - 1.0) < 1e-12:
            ones += 1
    unique_numeric = len({round(v, 10) for v in numeric_values})
    first_numeric = numeric_values[0] if numeric_values else None
    return RowStats(
        cells=len(row.year_values),
        numeric=len(numeric_values),
        blank=blank,
        non_numeric=non_numeric,
        zeros=zeros,
        ones=ones,
        unique_numeric=unique_numeric,
        first_numeric=first_numeric,
    )


def target_issue(row: AoCostRow) -> str:
    stats = row_stats(row)
    if stats.numeric == 0:
        return "missing_all_years"
    if stats.one_share >= 0.5:
        return "mostly_one_placeholder"
    if row.parameter == "VariableCost" and stats.zero_share >= 0.9:
        return "mostly_zero_variable_cost"
    if stats.non_numeric:
        return "contains_non_numeric_values"
    if stats.numeric <= 1 and stats.blank_share >= 0.8:
        return "single_year_only"
    return ""


def is_suspicious_target(row: AoCostRow) -> bool:
    return bool(target_issue(row))


def source_issue(row: AoCostRow) -> str:
    stats = row_stats(row)
    if stats.numeric == 0:
        return "source_missing_all_years"
    if stats.one_share >= 0.8:
        return "source_mostly_one_placeholder"
    if stats.zero_share >= 0.95:
        return "source_mostly_zero"
    if stats.non_numeric:
        return "source_contains_non_numeric_values"
    return ""


def usable_source(row: AoCostRow) -> bool:
    issue = source_issue(row)
    if issue in {
        "source_missing_all_years",
        "source_mostly_one_placeholder",
        "source_contains_non_numeric_values",
    }:
        return False
    if issue == "source_mostly_zero" and row.parameter in {"CapitalCost", "FixedCost"}:
        return False
    return True


FAMILY_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("solar", ("solar", "photovoltaic", "pv", "spv", "pvd")),
    ("wind", ("wind", "wnd", "eolic")),
    ("hydro", ("hydro", "hydroelectric", "hydraul")),
    ("geothermal", ("geo", "geothermal")),
    ("biomass", ("biomass", "bim", "bms", "bagasse")),
    ("biogas", ("biogas", "bgs")),
    ("charcoal", ("charcoal", "cha")),
    ("coal", ("coal", "coa")),
    ("coke", ("coke", "cok")),
    ("diesel", ("diesel", "dsl")),
    ("gasoline", ("gasoline", "gsl", "gasolina")),
    ("fuel_oil", ("fuel oil", "foi", "hfo")),
    ("lpg", ("lpg", "glp")),
    ("natural_gas", ("natural gas", "natural_gas", "ngs", "lng", "methane")),
    ("kerosene", ("kerosene", "kerosen", "ker", "kjf")),
    ("jet", ("jet", "jta", "avtur")),
    ("crude", ("crude", "cru")),
    ("electricity", ("electricity", "electric", "ele")),
    ("hydrogen", ("hydrogen", "hyd")),
    ("transmission", ("transmission", "trans", "trn")),
    ("distribution", ("distribution", "distr", "dist", "dtr")),
    ("battery", ("battery", "storage", "batt")),
    ("nuclear", ("nuclear", "uranium", "ura")),
)


def detect_family(row_or_text: AoCostRow | str) -> str:
    if isinstance(row_or_text, AoCostRow):
        haystack = normalize_text(f"{row_or_text.tech} {row_or_text.tech_name}")
    else:
        haystack = normalize_text(row_or_text)
    for family, patterns in FAMILY_PATTERNS:
        for pattern in patterns:
            if normalize_text(pattern) in haystack:
                return family
    return ""


def detect_fuel_code(row_or_text: AoCostRow | str) -> str:
    if isinstance(row_or_text, AoCostRow):
        tech_code = clean(row_or_text.tech).upper()
        text = f"{row_or_text.tech} {row_or_text.tech_name}"
    else:
        tech_code = clean(row_or_text).split(" ", 1)[0].upper()
        text = row_or_text
    normalized_tokens = token_set(text)
    code_tokens = {
        token
        for token in re.split(r"[^A-Z0-9]+", tech_code.replace("_", " "))
        if token
    }

    def code_has(marker: str) -> bool:
        marker = marker.upper()
        return marker in code_tokens or tech_code.endswith(marker)

    if code_has("NGS") or code_has("LNG") or {"natural", "gas"} <= normalized_tokens:
        return "NGS"
    if code_has("LPG") or code_has("GLP") or "lpg" in normalized_tokens:
        return "LPG"
    if code_has("DSL") or "diesel" in normalized_tokens:
        return "DSL"
    if code_has("GSL") or "gasoline" in normalized_tokens or "gasolina" in normalized_tokens:
        return "GSL"
    if code_has("FOI") or code_has("HFO") or {"fuel", "oil"} <= normalized_tokens:
        return "HFO"
    if code_has("KER") or code_has("KRS") or code_has("KJF") or "kerosene" in normalized_tokens or "kerosen" in normalized_tokens:
        return "KRS"
    if code_has("JET") or code_has("JTA") or "jet" in normalized_tokens:
        return "JTA"
    if code_has("COA") or "coal" in normalized_tokens:
        return "COA"
    if code_has("CRU") or "crude" in normalized_tokens:
        return "CRD"
    return ""


def is_fuel_cost_target(row: AoCostRow) -> bool:
    if row.parameter != "VariableCost":
        return False
    if not detect_fuel_code(row):
        return False
    text = normalize_text(f"{row.tech} {row.tech_name} {row.sheet}")
    fuel_context = (
        "import" in text
        or "distribution" in text
        or "distributed" in text
        or "dist " in f"{text} "
        or row.tech.upper().startswith(("DIST_", "IMP", "T4"))
    )
    return fuel_context


def unit_compatible(target_unit: str, source_unit: str) -> tuple[bool, str]:
    target = normalize_text(target_unit)
    source = normalize_text(source_unit)
    if not target or not source:
        return True, "unit_unknown"
    if target == source:
        return True, "unit_exact"
    money_tokens = ("us", "usd", "mus", "m")
    if "pj" in target and "pj" in source and any(tok in target for tok in money_tokens):
        if any(tok in source for tok in money_tokens):
            return True, "unit_energy_cost_compatible"
    if "gwh" in target and "gwh" in source:
        return True, "unit_gwh_compatible"
    if "gvkm" in target and "gvkm" in source:
        return True, "unit_transport_activity_compatible"
    return False, "unit_incompatible"


def name_metrics(target: AoCostRow, source: AoCostRow) -> tuple[float, float]:
    target_name = normalize_text(target.tech_name)
    source_name = normalize_text(source.tech_name)
    if not target_name or not source_name:
        return 0.0, 0.0
    similarity = SequenceMatcher(None, target_name, source_name).ratio()
    target_tokens = token_set(target.tech_name)
    source_tokens = token_set(source.tech_name)
    if not target_tokens or not source_tokens:
        jaccard = 0.0
    else:
        jaccard = len(target_tokens & source_tokens) / len(target_tokens | source_tokens)
    return similarity, jaccard


def expanded_source_values(
    source: AoCostRow, target_years: Iterable[int]
) -> tuple[dict[int, float], float, str]:
    target_year_list = list(target_years)
    numeric_by_year = {
        year: parse_float(value)
        for year, value in source.year_values.items()
        if parse_float(value) is not None
    }
    if not numeric_by_year:
        return {}, 0.0, "no_numeric_source_values"

    mode = normalize_text(source.projection_mode)
    first_year = min(numeric_by_year)
    last_year = max(numeric_by_year)
    first_value = numeric_by_year[first_year]
    last_value = numeric_by_year[last_year]
    expanded: dict[int, float] = {}
    notes: list[str] = []
    for year in target_year_list:
        if year in numeric_by_year:
            expanded[year] = numeric_by_year[year]  # type: ignore[assignment]
        elif mode == "flat" and first_value is not None:
            expanded[year] = first_value
            notes.append("flat_projection_expanded")
        elif year > last_year and last_value is not None:
            expanded[year] = last_value
            notes.append("held_last_source_year_flat")
        elif year < first_year and first_value is not None:
            expanded[year] = first_value
            notes.append("held_first_source_year_flat")
    coverage = len(expanded) / len(target_year_list) if target_year_list else 0.0
    return expanded, coverage, ";".join(sorted(set(notes))) or "direct_year_copy"


def score_local_match(target: AoCostRow, source: AoCostRow) -> MatchScore:
    if target.parameter != source.parameter:
        return MatchScore(
            score=-999,
            decision="NO_SAFE_MATCH",
            reason="parameter_mismatch",
            name_similarity=0.0,
            token_jaccard=0.0,
            target_family="",
            source_family="",
            target_fuel_code="",
            source_fuel_code="",
            coverage_share=0.0,
            hard_conflict="parameter_mismatch",
        )
    name_similarity, token_jaccard = name_metrics(target, source)
    target_family = detect_family(target)
    source_family = detect_family(source)
    target_fuel = detect_fuel_code(target)
    source_fuel = detect_fuel_code(source)
    unit_ok, unit_reason = unit_compatible(target.unit, source.unit)
    _, coverage, coverage_note = expanded_source_values(source, target.header_years)
    score = 0.0
    reasons: list[str] = []
    hard_conflict = ""

    if target.tech == source.tech:
        score += 25
        reasons.append("same_tech_id")

    if normalize_text(target.tech_name) and normalize_text(target.tech_name) == normalize_text(
        source.tech_name
    ):
        score += 45
        reasons.append("same_normalized_name")
    else:
        score += max(name_similarity, token_jaccard) * 35
        if name_similarity >= 0.7:
            reasons.append("strong_name_similarity")
        if token_jaccard >= 0.5:
            reasons.append("strong_token_overlap")

    if target_family and source_family:
        if target_family == source_family:
            score += 20
            reasons.append(f"same_family:{target_family}")
        else:
            score -= 20
            hard_conflict = f"family_conflict:{target_family}!={source_family}"
    if target_fuel and source_fuel:
        if target_fuel == source_fuel:
            score += 20
            reasons.append(f"same_fuel:{target_fuel}")
        else:
            score -= 40
            hard_conflict = f"fuel_conflict:{target_fuel}!={source_fuel}"

    if target.sheet == source.sheet:
        score += 12
        reasons.append("same_sheet")
    elif sheet_family(target.sheet) == sheet_family(source.sheet):
        score += 6
        reasons.append("compatible_sheet_family")

    if unit_ok:
        score += 12
        reasons.append(unit_reason)
    else:
        score -= 30
        hard_conflict = "unit_incompatible"

    if usable_source(source):
        score += 8
        reasons.append("source_values_not_placeholder")
    else:
        score -= 50
        hard_conflict = source_issue(source)

    score += min(coverage, 1.0) * 10
    if coverage >= 0.95:
        reasons.append("full_year_coverage")
    elif coverage >= 0.5:
        reasons.append("partial_year_coverage")
    else:
        hard_conflict = "low_year_coverage"

    if target.tech == source.tech and name_similarity < 0.3 and target.tech_name and source.tech_name:
        score -= 40
        hard_conflict = "same_tech_id_but_name_conflict"

    if hard_conflict:
        decision = "NO_SAFE_MATCH" if score < 95 else "REVIEW_REQUIRED"
    elif score >= 95:
        decision = "AUTO_HIGH_CONFIDENCE"
    elif score >= 70:
        decision = "REVIEW_REQUIRED"
    else:
        decision = "NO_SAFE_MATCH"

    return MatchScore(
        score=round(score, 3),
        decision=decision,
        reason=" | ".join(reasons + ([coverage_note] if coverage_note else [])),
        name_similarity=round(name_similarity, 3),
        token_jaccard=round(token_jaccard, 3),
        target_family=target_family,
        source_family=source_family,
        target_fuel_code=target_fuel,
        source_fuel_code=source_fuel,
        coverage_share=round(coverage, 3),
        hard_conflict=hard_conflict,
    )


def sheet_family(sheet: str) -> str:
    text = normalize_text(sheet)
    if "primary" in text:
        return "primary"
    if "secondary" in text:
        return "secondary"
    if "vehicle" in text:
        return "vehicle"
    if "transport fuel" in text:
        return "transport_fuel_distribution"
    if "demand" in text:
        return "demand"
    if "other" in text:
        return "other"
    return text


def fuel_unit_conversion(raw_usd_per_pj: float, target_unit: str) -> tuple[float, str]:
    unit = normalize_text(target_unit)
    if not unit:
        return raw_usd_per_pj / 1_000_000, "usd_per_pj_to_musd_per_pj_default"
    if "pj" in unit and ("mus" in unit or "m us" in unit or unit.startswith("m ")):
        return raw_usd_per_pj / 1_000_000, "usd_per_pj_to_musd_per_pj"
    if "pj" in unit and ("usd" in unit or "us" in unit):
        return raw_usd_per_pj, "usd_per_pj_no_scale"
    return raw_usd_per_pj / 1_000_000, "usd_per_pj_to_musd_per_pj_default"


def read_fuel_series(
    workbook_path: Path, iso: str, fuel_code: str, scenario: str
) -> tuple[dict[int, float], dict[str, Any]]:
    if not workbook_path.exists():
        return {}, {"error": f"fuel_workbook_missing:{workbook_path}"}
    wb = load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        if "OSeMOSYS_VarCost" not in wb.sheetnames:
            return {}, {"error": "sheet_missing:OSeMOSYS_VarCost"}
        ws = wb["OSeMOSYS_VarCost"]
        header_row = None
        headers: dict[str | int, int] = {}
        for row_index in range(1, min(ws.max_row, 12) + 1):
            values = [
                ws.cell(row=row_index, column=col).value
                for col in range(1, min(ws.max_column, 80) + 1)
            ]
            normalized = {clean(v) for v in values}
            if {"ISO", "Fuel Code", "Scenario"}.issubset(normalized):
                header_row = row_index
                for col, value in enumerate(values, start=1):
                    text = clean(value)
                    if not text:
                        continue
                    if re.fullmatch(r"\d{4}", text):
                        headers[int(text)] = col
                    else:
                        headers[text] = col
                break
        if header_row is None:
            return {}, {"error": "fuel_header_not_found"}
        iso_col = headers.get("ISO")
        code_col = headers.get("Fuel Code")
        scen_col = headers.get("Scenario")
        if not isinstance(iso_col, int) or not isinstance(code_col, int) or not isinstance(scen_col, int):
            return {}, {"error": "fuel_required_columns_missing"}
        year_cols = {k: v for k, v in headers.items() if isinstance(k, int)}
        for row_index in range(header_row + 1, ws.max_row + 1):
            row_iso = clean(ws.cell(row=row_index, column=iso_col).value).upper()
            row_code = clean(ws.cell(row=row_index, column=code_col).value).upper()
            row_scen = clean(ws.cell(row=row_index, column=scen_col).value).upper()
            if row_iso == iso.upper() and row_code == fuel_code.upper() and row_scen == scenario.upper():
                values = {
                    year: parse_float(ws.cell(row=row_index, column=col).value)
                    for year, col in year_cols.items()
                }
                series = {year: value for year, value in values.items() if value is not None}
                meta = {
                    "source_sheet": "OSeMOSYS_VarCost",
                    "source_row_index": row_index,
                    "fuel_code": fuel_code.upper(),
                    "scenario": scenario.upper(),
                }
                return series, meta
        if fuel_code == "COA":
            return read_fuel_series(workbook_path, "WORLD", "COA", scenario)
        if fuel_code == "CRD":
            return read_fuel_series(workbook_path, "WORLD", "CRD", scenario)
        return {}, {"error": f"fuel_series_not_found:{iso}:{fuel_code}:{scenario}"}
    finally:
        wb.close()


def expand_fuel_series(series: dict[int, float], target_years: Iterable[int]) -> tuple[dict[int, float], str]:
    if not series:
        return {}, "fuel_series_empty"
    years = sorted(series)
    first_year = years[0]
    last_year = years[-1]
    expanded: dict[int, float] = {}
    notes: list[str] = []
    for year in target_years:
        if year in series:
            expanded[year] = series[year]
        elif year > last_year:
            expanded[year] = series[last_year]
            notes.append("held_ending_fuel_year_flat")
        elif year < first_year:
            expanded[year] = series[first_year]
            notes.append("held_starting_fuel_year_flat")
    return expanded, ";".join(sorted(set(notes))) or "direct_fuel_year_copy"


def make_manifest_rows(
    *,
    target: AoCostRow,
    new_values: dict[int, float],
    source_kind: str,
    source_path: Path | str,
    source_sheet: str,
    source_row_index: int | str,
    source_tech: str,
    source_tech_name: str,
    source_unit: str,
    source_projection_mode: str,
    fuel_code: str,
    scenario: str,
    score: float,
    decision: str,
    reason: str,
    unit_conversion: str,
    generated_at: str,
    approved: str | None = None,
) -> list[dict[str, Any]]:
    if approved is None:
        approved = "YES" if decision == "AUTO_HIGH_CONFIDENCE" else "NO"
    rows: list[dict[str, Any]] = []
    new_mode = "User defined"
    for year in sorted(target.header_years):
        if year not in new_values:
            continue
        new_value = new_values[year]
        old_value = target.year_values.get(year)
        if same_number(old_value, new_value):
            continue
        manifest_key = "|".join(
            [
                target.country,
                str(target.workbook_path),
                target.sheet,
                str(target.row_index),
                target.tech,
                target.parameter,
                str(year),
                source_kind,
            ]
        )
        manifest_id = hashlib.sha256(manifest_key.encode("utf-8")).hexdigest()[:16]
        rows.append(
            {
                "manifest_id": manifest_id,
                "approved": approved,
                "decision": decision,
                "country": target.country,
                "model_label": target.model_label,
                "ao_path": str(target.workbook_path),
                "sheet": target.sheet,
                "row_index": target.row_index,
                "tech": target.tech,
                "tech_name": target.tech_name,
                "parameter": target.parameter,
                "unit": target.unit,
                "year": year,
                "old_value": format_number(old_value),
                "new_value": format_number(new_value),
                "source_kind": source_kind,
                "source_path": str(source_path),
                "source_sheet": source_sheet,
                "source_row_index": source_row_index,
                "source_tech": source_tech,
                "source_tech_name": source_tech_name,
                "source_unit": source_unit,
                "source_projection_mode": source_projection_mode,
                "fuel_code": fuel_code,
                "scenario": scenario,
                "score": format_number(score),
                "reason": reason,
                "row_fingerprint": target.row_fingerprint,
                "projection_mode_old": target.projection_mode,
                "projection_mode_new": new_mode,
                "unit_conversion": unit_conversion,
                "generated_at": generated_at,
            }
        )
    return rows


def mapping_row(target: AoCostRow, source: AoCostRow, score: MatchScore, issue: str) -> dict[str, Any]:
    return {
        "country": target.country,
        "model_label": target.model_label,
        "target_sheet": target.sheet,
        "target_row_index": target.row_index,
        "target_tech": target.tech,
        "target_tech_name": target.tech_name,
        "target_parameter": target.parameter,
        "target_unit": target.unit,
        "target_projection_mode": target.projection_mode,
        "target_issue": issue,
        "source_kind": source.source_kind,
        "source_path": str(source.workbook_path),
        "source_sheet": source.sheet,
        "source_row_index": source.row_index,
        "source_tech": source.tech,
        "source_tech_name": source.tech_name,
        "source_parameter": source.parameter,
        "source_unit": source.unit,
        "source_projection_mode": source.projection_mode,
        "score": format_number(score.score),
        "decision": score.decision,
        "reason": score.reason,
        "name_similarity": format_number(score.name_similarity),
        "token_jaccard": format_number(score.token_jaccard),
        "target_family": score.target_family,
        "source_family": score.source_family,
        "target_fuel_code": score.target_fuel_code,
        "source_fuel_code": score.source_fuel_code,
        "coverage_share": format_number(score.coverage_share),
        "hard_conflict": score.hard_conflict,
    }


def no_match_row(
    target: AoCostRow,
    issue: str,
    suggested_next_source: str,
    reason: str,
) -> dict[str, Any]:
    family = detect_family(target)
    atb_family = family if is_atb_eligible(target) else ""
    return {
        "country": target.country,
        "model_label": target.model_label,
        "ao_path": str(target.workbook_path),
        "sheet": target.sheet,
        "row_index": target.row_index,
        "tech": target.tech,
        "tech_name": target.tech_name,
        "parameter": target.parameter,
        "unit": target.unit,
        "projection_mode": target.projection_mode,
        "issue": issue,
        "suggested_next_source": suggested_next_source,
        "suggested_atb_family": atb_family,
        "reason": reason,
    }


def is_atb_eligible(row: AoCostRow) -> bool:
    if row.parameter not in {"CapitalCost", "FixedCost"}:
        return False
    return detect_family(row) in {
        "solar",
        "wind",
        "hydro",
        "geothermal",
        "biomass",
        "biogas",
        "coal",
        "natural_gas",
        "battery",
        "nuclear",
    }


def select_countries(country_arg: str) -> list[str]:
    if country_arg.lower() == "all":
        return list(COUNTRY_MODELS)
    requested = [part.strip() for part in country_arg.split(",") if part.strip()]
    unknown = [country for country in requested if country not in COUNTRY_MODELS]
    if unknown:
        raise SystemExit(f"Unknown country: {', '.join(unknown)}")
    return requested


def local_sources_for_country(root: Path, country: str) -> list[Path]:
    if country != "Ecuador":
        return []
    return [root / rel_path for rel_path in ECUADOR_LOCAL_SOURCE_PATHS if (root / rel_path).exists()]


def load_source_rows(root: Path, country: str) -> list[AoCostRow]:
    rows: list[AoCostRow] = []
    model = COUNTRY_MODELS[country]
    for source_path in local_sources_for_country(root, country):
        label = rel_or_abs(root, source_path)
        rows.extend(
            read_ao_cost_rows(
                source_path,
                country=country,
                model_label=model["model_label"],
                source_label=label,
                source_kind="ecuador_local_reference",
            )
        )
    return rows


def plan_country(
    *,
    root: Path,
    output_dir: Path,
    country: str,
    fuel_workbook: Path,
    fuel_scenario: str,
    include_review_manifest: bool,
    replace_existing_fuel_costs: bool,
    top_candidates: int,
    generated_at: str,
) -> PlanResult:
    result = PlanResult(output_dir=output_dir)
    model = COUNTRY_MODELS[country]
    ao_path = root / model["ao_path"]
    if not ao_path.exists():
        result.warnings.append(f"AO workbook missing for {country}: {ao_path}")
        return result
    target_rows = read_ao_cost_rows(
        ao_path,
        country=country,
        model_label=model["model_label"],
        source_label="active_ao",
        source_kind="target",
    )
    source_rows = load_source_rows(root, country)
    source_by_param: dict[str, list[AoCostRow]] = defaultdict(list)
    for source_row in source_rows:
        source_by_param[source_row.parameter].append(source_row)

    fuel_cache: dict[tuple[str, str, str], tuple[dict[int, float], dict[str, Any]]] = {}
    counters: Counter[tuple[str, str]] = Counter()

    for target in target_rows:
        issue = target_issue(target)
        suspicious = bool(issue)
        if not suspicious and not (replace_existing_fuel_costs and is_fuel_cost_target(target)):
            continue

        used_auto_source = False
        if is_fuel_cost_target(target):
            fuel_code = detect_fuel_code(target)
            cache_key = (model["iso"], fuel_code, fuel_scenario.upper())
            if cache_key not in fuel_cache:
                fuel_cache[cache_key] = read_fuel_series(
                    fuel_workbook, model["iso"], fuel_code, fuel_scenario
                )
            raw_series, meta = fuel_cache[cache_key]
            if raw_series:
                expanded_raw, fuel_note = expand_fuel_series(raw_series, target.header_years)
                converted: dict[int, float] = {}
                conversion_notes: list[str] = []
                for year, raw_value in expanded_raw.items():
                    value, conversion_note = fuel_unit_conversion(raw_value, target.unit)
                    converted[year] = value
                    conversion_notes.append(conversion_note)
                decision = (
                    "AUTO_HIGH_CONFIDENCE"
                    if suspicious or replace_existing_fuel_costs
                    else "REVIEW_REQUIRED"
                )
                rows = make_manifest_rows(
                    target=target,
                    new_values=converted,
                    source_kind="fuel_workbook",
                    source_path=fuel_workbook,
                    source_sheet=clean(meta.get("source_sheet")),
                    source_row_index=meta.get("source_row_index", ""),
                    source_tech="",
                    source_tech_name=f"Fuel code {fuel_code}",
                    source_unit="USD/PJ",
                    source_projection_mode="REF trajectory",
                    fuel_code=fuel_code,
                    scenario=fuel_scenario.upper(),
                    score=100,
                    decision=decision,
                    reason=f"authoritative_fuel_variable_cost | {issue or 'replace_existing_fuel_cost'} | {fuel_note}",
                    unit_conversion=";".join(sorted(set(conversion_notes))),
                    generated_at=generated_at,
                )
                result.manifest_rows.extend(rows)
                counters[("fuel_workbook", decision)] += len(rows)
                used_auto_source = bool(rows and decision == "AUTO_HIGH_CONFIDENCE")
            else:
                result.no_match_rows.append(
                    no_match_row(
                        target,
                        issue or "fuel_cost_target",
                        "fuel_workbook",
                        clean(meta.get("error", "fuel_series_missing")),
                    )
                )

        # Fuel workbook has priority for import/distribution VariableCost. Still
        # record local mappings for review, but avoid creating competing auto
        # manifest rows for the same target.
        candidate_scores: list[tuple[MatchScore, AoCostRow]] = []
        for source in source_by_param.get(target.parameter, []):
            score = score_local_match(target, source)
            if score.decision != "NO_SAFE_MATCH" or score.score > 45:
                candidate_scores.append((score, source))
        candidate_scores.sort(key=lambda item: item[0].score, reverse=True)
        for score, source in candidate_scores[:top_candidates]:
            result.mapping_rows.append(mapping_row(target, source, score, issue))

        if used_auto_source:
            continue

        best_auto: tuple[MatchScore, AoCostRow] | None = None
        best_review: tuple[MatchScore, AoCostRow] | None = None
        for score, source in candidate_scores:
            if score.decision == "AUTO_HIGH_CONFIDENCE":
                best_auto = (score, source)
                break
            if score.decision == "REVIEW_REQUIRED" and best_review is None:
                best_review = (score, source)

        chosen = best_auto or (best_review if include_review_manifest else None)
        if chosen is not None:
            score, source = chosen
            expanded, coverage, coverage_note = expanded_source_values(source, target.header_years)
            if expanded and coverage >= 0.5:
                rows = make_manifest_rows(
                    target=target,
                    new_values=expanded,
                    source_kind=source.source_kind,
                    source_path=source.workbook_path,
                    source_sheet=source.sheet,
                    source_row_index=source.row_index,
                    source_tech=source.tech,
                    source_tech_name=source.tech_name,
                    source_unit=source.unit,
                    source_projection_mode=source.projection_mode,
                    fuel_code=detect_fuel_code(source),
                    scenario="",
                    score=score.score,
                    decision=score.decision,
                    reason=f"{score.reason} | {coverage_note}",
                    unit_conversion="source_ao_units_copied",
                    generated_at=generated_at,
                )
                result.manifest_rows.extend(rows)
                counters[(source.source_kind, score.decision)] += len(rows)
                continue

        if suspicious:
            if is_atb_eligible(target):
                next_source = "ATB"
                reason = "no_auto_ecuador_local_match; atb_eligible_generation_or_storage_cost"
            elif target.parameter in {"CapitalCost", "FixedCost"}:
                next_source = "manual_review"
                reason = "no_auto_ecuador_local_match; not_atb_scope"
            else:
                next_source = "manual_review"
                reason = "no_auto_ecuador_local_or_fuel_match"
            result.no_match_rows.append(no_match_row(target, issue, next_source, reason))

    for (source_kind, decision), cells in sorted(counters.items()):
        row_keys = {
            (
                row["country"],
                row["ao_path"],
                row["sheet"],
                row["row_index"],
                row["tech"],
                row["parameter"],
                row["source_kind"],
                row["decision"],
            )
            for row in result.manifest_rows
            if row["country"] == country
            and row["source_kind"] == source_kind
            and row["decision"] == decision
        }
        result.summary_rows.append(
            {
                "country": country,
                "model_label": model["model_label"],
                "ao_path": str(ao_path),
                "source_kind": source_kind,
                "decision": decision,
                "rows": len(row_keys),
                "cells": cells,
            }
        )
    return result


def command_plan(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    output_dir = (
        args.output_dir
        if args.output_dir is not None
        else root / DEFAULT_OUTPUT_ROOT / f"ao_cost_repair_{now_stamp()}"
    )
    output_dir = output_dir.resolve()
    ensure_output_dir(output_dir)
    generated_at = now_stamp()

    combined = PlanResult(output_dir=output_dir)
    for country in select_countries(args.country):
        result = plan_country(
            root=root,
            output_dir=output_dir,
            country=country,
            fuel_workbook=args.fuel_workbook.resolve(),
            fuel_scenario=args.fuel_scenario,
            include_review_manifest=args.include_review_manifest,
            replace_existing_fuel_costs=args.replace_existing_fuel_costs,
            top_candidates=args.top_candidates,
            generated_at=generated_at,
        )
        combined.manifest_rows.extend(result.manifest_rows)
        combined.mapping_rows.extend(result.mapping_rows)
        combined.no_match_rows.extend(result.no_match_rows)
        combined.summary_rows.extend(result.summary_rows)
        combined.warnings.extend(result.warnings)

    write_csv(output_dir / "manifest.csv", combined.manifest_rows, MANIFEST_FIELDS)
    write_csv(output_dir / "mapping_candidates.csv", combined.mapping_rows, MAPPING_FIELDS)
    write_csv(output_dir / "no_safe_match.csv", combined.no_match_rows, NO_MATCH_FIELDS)
    write_csv(output_dir / "summary.csv", combined.summary_rows, SUMMARY_FIELDS)
    config = {
        "generated_at": generated_at,
        "root": str(root),
        "country": args.country,
        "fuel_workbook": str(args.fuel_workbook.resolve()),
        "fuel_scenario": args.fuel_scenario,
        "include_review_manifest": args.include_review_manifest,
        "replace_existing_fuel_costs": args.replace_existing_fuel_costs,
        "top_candidates": args.top_candidates,
        "warnings": combined.warnings,
    }
    (output_dir / "run_config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )
    print(f"Plan output: {output_dir}")
    print(f"Manifest cells: {len(combined.manifest_rows)}")
    print(f"Mapping candidates: {len(combined.mapping_rows)}")
    print(f"No-safe-match rows: {len(combined.no_match_rows)}")
    if combined.warnings:
        print("Warnings:")
        for warning in combined.warnings:
            print(f"  - {warning}")
    return 0


def workbook_header_maps(path: Path) -> dict[str, dict[str | int, int]]:
    wb = load_workbook(path, read_only=True, data_only=False)
    maps: dict[str, dict[str | int, int]] = {}
    try:
        for ws in wb.worksheets:
            header_row = find_header_row(ws)
            if header_row is not None:
                headers = build_header_map(ws, header_row)
                headers["__header_row__"] = header_row
                maps[ws.title] = headers
    finally:
        wb.close()
    return maps


def make_backup(ao_path: Path, backup_dir: Path, country: str) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    safe_country = re.sub(r"[^A-Za-z0-9._-]+", "_", country)
    backup = backup_dir / f"{safe_country}__{ao_path.stem}.bak_{now_stamp()}{ao_path.suffix}"
    shutil.copy2(ao_path, backup)
    return backup


def approved_manifest_rows(rows: list[dict[str, str]], include_review: bool) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        approved = clean(row.get("approved")).upper() in {"YES", "Y", "TRUE", "1"}
        if approved:
            out.append(row)
            continue
        if include_review and clean(row.get("decision")) == "REVIEW_REQUIRED":
            out.append(row)
    return out


def group_manifest_by_workbook(rows: list[dict[str, str]], root: Path) -> dict[Path, list[dict[str, str]]]:
    grouped: dict[Path, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        path = Path(clean(row["ao_path"]))
        if not path.is_absolute():
            path = root / path
        grouped[path].append(row)
    return grouped


def apply_rows_to_workbook(
    *,
    ao_path: Path,
    rows: list[dict[str, str]],
    dry_run: bool,
    ignore_old_value_mismatch: bool,
) -> tuple[int, int]:
    wb = load_workbook(ao_path, data_only=False)
    cells_changed = 0
    modes_changed = 0
    mode_rows_changed: set[tuple[str, int]] = set()
    try:
        sheet_maps: dict[str, dict[str | int, int]] = {}
        for ws in wb.worksheets:
            header_row = find_header_row(ws)
            if header_row is not None:
                headers = build_header_map(ws, header_row)
                headers["__header_row__"] = header_row
                sheet_maps[ws.title] = headers

        for row in rows:
            sheet = clean(row["sheet"])
            year = int(clean(row["year"]))
            row_index = int(clean(row["row_index"]))
            if sheet not in wb.sheetnames:
                raise RuntimeError(f"Sheet missing in {ao_path}: {sheet}")
            ws = wb[sheet]
            headers = sheet_maps.get(sheet)
            if headers is None:
                raise RuntimeError(f"Header missing in {ao_path}:{sheet}")
            tech_col = header_lookup(headers, "Tech")
            param_col = header_lookup(headers, "Parameter")
            if tech_col is None or param_col is None:
                raise RuntimeError(f"Tech/Parameter columns missing in {ao_path}:{sheet}")
            if clean(ws.cell(row=row_index, column=tech_col).value) != clean(row["tech"]):
                raise RuntimeError(f"Tech fingerprint mismatch at {ao_path}:{sheet}:{row_index}")
            if clean(ws.cell(row=row_index, column=param_col).value) != clean(row["parameter"]):
                raise RuntimeError(f"Parameter fingerprint mismatch at {ao_path}:{sheet}:{row_index}")
            year_col = headers.get(year)
            if not isinstance(year_col, int):
                raise RuntimeError(f"Year {year} missing in {ao_path}:{sheet}")
            current = ws.cell(row=row_index, column=year_col).value
            if not ignore_old_value_mismatch and not same_number(current, row["old_value"]):
                raise RuntimeError(
                    f"Old value mismatch at {ao_path}:{sheet}:{row_index}:{year}; "
                    f"workbook={current!r}, manifest={row['old_value']!r}"
                )
            new_value = parse_float(row["new_value"])
            if new_value is None:
                raise RuntimeError(f"Manifest new_value is not numeric: {row}")
            if not same_number(current, new_value):
                cells_changed += 1
                if not dry_run:
                    ws.cell(row=row_index, column=year_col).value = new_value
            mode_col = header_lookup(headers, "Projection.Mode")
            new_mode = clean(row.get("projection_mode_new"))
            if mode_col is not None and new_mode:
                current_mode = clean(ws.cell(row=row_index, column=mode_col).value)
                if current_mode != new_mode and (sheet, row_index) not in mode_rows_changed:
                    modes_changed += 1
                    mode_rows_changed.add((sheet, row_index))
                    if not dry_run:
                        ws.cell(row=row_index, column=mode_col).value = new_mode
        if not dry_run and (cells_changed or modes_changed):
            save_ao_safely(wb, ao_path)
    finally:
        wb.close()
    return cells_changed, modes_changed


def command_apply(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    manifest_path = args.manifest.resolve()
    rows = approved_manifest_rows(read_csv(manifest_path), include_review=args.include_review)
    grouped = group_manifest_by_workbook(rows, root)
    apply_id = f"apply_{now_stamp()}"
    log_rows: list[dict[str, Any]] = []
    output_dir = args.output_dir.resolve() if args.output_dir else manifest_path.parent
    backup_dir = output_dir / "backups" / apply_id

    if not args.dry_run and not args.apply:
        raise SystemExit("Refusing to edit workbooks without --apply. Use --dry-run for preview.")

    total_cells = 0
    total_modes = 0
    for ao_path, workbook_rows in grouped.items():
        if not ao_path.exists():
            raise SystemExit(f"AO workbook missing: {ao_path}")
        country = clean(workbook_rows[0].get("country"))
        backup_path = ""
        if not args.dry_run:
            backup_path = str(make_backup(ao_path, backup_dir, country))
        cells, modes = apply_rows_to_workbook(
            ao_path=ao_path,
            rows=workbook_rows,
            dry_run=args.dry_run,
            ignore_old_value_mismatch=args.ignore_old_value_mismatch,
        )
        total_cells += cells
        total_modes += modes
        log_rows.append(
            {
                "apply_id": apply_id,
                "timestamp": now_stamp(),
                "manifest_path": str(manifest_path),
                "country": country,
                "ao_path": str(ao_path),
                "backup_path": backup_path,
                "dry_run": "YES" if args.dry_run else "NO",
                "approved_cells_seen": len(workbook_rows),
                "cells_changed": cells,
                "projection_modes_changed": modes,
            }
        )

    log_path = output_dir / f"{apply_id}_apply_log.csv"
    write_csv(log_path, log_rows, APPLY_LOG_FIELDS)
    print(f"Apply log: {log_path}")
    print(f"Approved manifest cells seen: {len(rows)}")
    print(f"Cells that would change: {total_cells}" if args.dry_run else f"Cells changed: {total_cells}")
    print(
        f"Projection modes that would change: {total_modes}"
        if args.dry_run
        else f"Projection modes changed: {total_modes}"
    )
    if args.dry_run:
        print("Dry run only. No AO workbooks were edited.")
    return 0


def verify_manifest_rows(
    *,
    root: Path,
    rows: list[dict[str, str]],
    expect: str,
    include_review: bool,
) -> tuple[int, list[str]]:
    selected = approved_manifest_rows(rows, include_review=include_review)
    grouped = group_manifest_by_workbook(selected, root)
    errors: list[str] = []
    checked = 0
    for ao_path, workbook_rows in grouped.items():
        wb = load_workbook(ao_path, read_only=True, data_only=True)
        try:
            sheet_maps: dict[str, dict[str | int, int]] = {}
            for ws in wb.worksheets:
                header_row = find_header_row(ws)
                if header_row is not None:
                    headers = build_header_map(ws, header_row)
                    headers["__header_row__"] = header_row
                    sheet_maps[ws.title] = headers
            for row in workbook_rows:
                sheet = clean(row["sheet"])
                row_index = int(clean(row["row_index"]))
                year = int(clean(row["year"]))
                ws = wb[sheet]
                headers = sheet_maps[sheet]
                col = headers.get(year)
                if not isinstance(col, int):
                    errors.append(f"Missing year {year}: {ao_path}:{sheet}")
                    continue
                expected_value = row["new_value"] if expect == "applied" else row["old_value"]
                actual = ws.cell(row=row_index, column=col).value
                checked += 1
                if not same_number(actual, expected_value):
                    errors.append(
                        f"Mismatch {ao_path}:{sheet}:{row_index}:{year}; "
                        f"actual={actual!r}, expected={expected_value!r}"
                    )
        finally:
            wb.close()
    return checked, errors


def command_verify(args: argparse.Namespace) -> int:
    rows = read_csv(args.manifest.resolve())
    checked, errors = verify_manifest_rows(
        root=args.root.resolve(),
        rows=rows,
        expect=args.expect,
        include_review=args.include_review,
    )
    print(f"Checked cells: {checked}")
    if errors:
        print(f"Verification failed: {len(errors)} mismatch(es)")
        for error in errors[:30]:
            print(f"  - {error}")
        if len(errors) > 30:
            print(f"  ... {len(errors) - 30} more")
        return 1
    print(f"Verification passed for expected state: {args.expect}")
    return 0


def command_restore(args: argparse.Namespace) -> int:
    log_rows = read_csv(args.apply_log.resolve())
    if not args.apply:
        print("Restore preview:")
        for row in log_rows:
            print(f"  {row['backup_path']} -> {row['ao_path']}")
        print("No files restored. Re-run with --apply to restore backups.")
        return 0
    restored = 0
    for row in log_rows:
        backup_path = Path(row["backup_path"])
        ao_path = Path(row["ao_path"])
        if not backup_path.exists():
            raise SystemExit(f"Backup missing: {backup_path}")
        shutil.copy2(backup_path, ao_path)
        restored += 1
    print(f"Restored workbook(s): {restored}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan/apply/verify reversible AO energy cost repairs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="MODELS_LAC_4 root directory",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="Create dry-run manifests and review tables")
    plan.add_argument("--country", default=DEFAULT_COUNTRY, help="Country name, comma list, or all")
    plan.add_argument("--fuel-workbook", type=Path, default=DEFAULT_FUEL_WORKBOOK)
    plan.add_argument("--fuel-scenario", default=DEFAULT_FUEL_SCENARIO)
    plan.add_argument("--output-dir", type=Path, default=None)
    plan.add_argument("--top-candidates", type=int, default=5)
    plan.add_argument(
        "--include-review-manifest",
        action="store_true",
        help="Also put REVIEW_REQUIRED local matches in manifest with approved=NO",
    )
    plan.add_argument(
        "--replace-existing-fuel-costs",
        action="store_true",
        help="Plan fuel-workbook VariableCost replacements even when values do not look suspicious",
    )
    plan.set_defaults(func=command_plan)

    apply_cmd = subparsers.add_parser("apply", help="Apply approved manifest rows")
    apply_cmd.add_argument("--manifest", type=Path, required=True)
    apply_cmd.add_argument("--output-dir", type=Path, default=None)
    apply_cmd.add_argument("--dry-run", action="store_true", help="Validate and preview only")
    apply_cmd.add_argument("--apply", action="store_true", help="Actually edit AO workbooks")
    apply_cmd.add_argument("--include-review", action="store_true")
    apply_cmd.add_argument("--ignore-old-value-mismatch", action="store_true")
    apply_cmd.set_defaults(func=command_apply)

    verify = subparsers.add_parser("verify", help="Verify workbook cells against manifest")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--expect", choices=("applied", "original"), default="applied")
    verify.add_argument("--include-review", action="store_true")
    verify.set_defaults(func=command_verify)

    restore = subparsers.add_parser("restore", help="Restore AO backups from an apply log")
    restore.add_argument("--apply-log", type=Path, required=True)
    restore.add_argument("--apply", action="store_true", help="Actually copy backups over AO files")
    restore.set_defaults(func=command_restore)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
