#! python
"""Create read-only Ecuador non-energy AO cost repair plans.

This tool is intentionally scoped and conservative:

- It only inspects Ecuador non-energy models: ECU_IPPU, ECU_WASTE, ECU_AGR,
  and ECU_USCUSS.
- It only has a ``plan`` command. There is no workbook-editing apply path yet.
- ``plan`` reads live AO workbooks plus local Ecuador/PLANMICC/reference
  workbooks and writes review artifacts. Use ``--no-write`` for a pure
  read-only smoke check that creates no files.
- Safe automatic proposals require exact technology id, same normalized name,
  same AO sheet, compatible units, full year coverage, and non-placeholder
  source values.

The structure mirrors ``ao_cost_repair_manager.py`` without reusing its
country-energy assumptions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

from openpyxl import load_workbook

from ao_cost_repair_manager import (
    COST_PARAMETERS,
    AoCostRow,
    clean,
    expanded_source_values,
    format_number,
    normalize_text,
    parse_float,
    read_ao_cost_rows,
    row_stats,
    same_number,
)


COUNTRY = "Ecuador"
DEFAULT_OUTPUT_ROOT = Path("_COST_REPAIR_OUTPUT")
DEFAULT_OUTPUT_PREFIX = "ecuador_non_energy_cost_plan"


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
    "score",
    "reason",
    "row_fingerprint",
    "projection_mode_old",
    "projection_mode_new",
    "unit_match",
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
    "target_values_summary",
    "source_kind",
    "source_path",
    "source_priority",
    "source_auto_allowed",
    "source_sheet",
    "source_row_index",
    "source_tech",
    "source_tech_name",
    "source_parameter",
    "source_unit",
    "source_projection_mode",
    "source_issue",
    "source_values_summary",
    "score",
    "decision",
    "reason",
    "unit_match",
    "name_similarity",
    "token_jaccard",
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
    "target_values_summary",
    "candidate_count",
    "suggested_next_source",
    "reason",
]

SUMMARY_FIELDS = [
    "country",
    "model_label",
    "parameter",
    "classification",
    "target_rows",
    "suspicious_target_rows",
    "source_rows",
    "auto_target_rows",
    "review_target_rows",
    "no_safe_match_rows",
    "manifest_cells",
    "approved_manifest_cells",
    "review_manifest_cells",
]


@dataclass(frozen=True)
class SourceSpec:
    rel_path: str
    source_kind: str
    priority: int
    allow_auto: bool = True
    reader: str = "ao"


@dataclass(frozen=True)
class ModelSpec:
    model_label: str
    live_rel_path: str
    sources: tuple[SourceSpec, ...]


@dataclass(frozen=True)
class SourceCandidate:
    row: AoCostRow
    rel_path: str
    source_kind: str
    priority: int
    allow_auto: bool


@dataclass(frozen=True)
class CandidateScore:
    score: float
    decision: str
    reason: str
    unit_match: str
    name_similarity: float
    token_jaccard: float
    coverage_share: float
    hard_conflict: str


@dataclass
class PlanResult:
    output_dir: Path | None
    manifest_rows: list[dict[str, Any]] = field(default_factory=list)
    mapping_rows: list[dict[str, Any]] = field(default_factory=list)
    no_match_rows: list[dict[str, Any]] = field(default_factory=list)
    summary_rows: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


MODEL_SPECS: dict[str, ModelSpec] = {
    "ECU_IPPU": ModelSpec(
        model_label="ECU_IPPU",
        live_rel_path=r"Ecuador\ECU_IPPU\A1_Outputs\A-O_Parametrization.xlsx",
        sources=(
            SourceSpec(
                r"Ecuador\ECU_IPPU\A1_Outputs\reference_edited\A-O_Parametrization_ref.xlsx",
                "ecuador_non_energy_ao_reference",
                10,
            ),
            SourceSpec(
                r"Ecuador\ECU_IPPU\A1_Outputs\A-O_Parametrization_PLANMICC_Procesos_Industriales.xlsx",
                "planmicc_ao_reference",
                20,
            ),
            SourceSpec(
                r"Ecuador\ECU_IPPU\A1_Outputs\A-O_Parametrization_COMPLETED.xlsx",
                "completed_ao_snapshot",
                50,
                allow_auto=False,
            ),
            SourceSpec(
                r"Ecuador\ECU_IPPU\A1_Outputs\A-O_Parametrization_Natural_COMPLETED.xlsx",
                "completed_ao_snapshot",
                60,
                allow_auto=False,
            ),
            SourceSpec(
                r"Ecuador\ECU_IPPU\A1_Outputs\Completos\A-O_Parametrization.xlsx",
                "completed_ao_snapshot",
                70,
                allow_auto=False,
            ),
        ),
    ),
    "ECU_WASTE": ModelSpec(
        model_label="ECU_WASTE",
        live_rel_path=r"Ecuador\ECU_WASTE\A1_Outputs\A-O_Parametrization.xlsx",
        sources=(
            SourceSpec(
                r"Ecuador\ECU_WASTE\A1_Outputs\A-O_Parametrization_REF.xlsx",
                "ecuador_non_energy_ao_reference",
                10,
            ),
            SourceSpec(
                r"Ecuador\ECU_WASTE\A1_Outputs\A-O_Parametrization_PLANMICC_Waste.xlsx",
                "planmicc_ao_reference",
                20,
            ),
            SourceSpec(
                r"Ecuador\ECU_WASTE\A1_Outputs\A-O_Parametrization_COMPLETED.xlsx",
                "completed_ao_snapshot",
                50,
                allow_auto=False,
            ),
            SourceSpec(
                r"Ecuador\ECU_WASTE\A1_Outputs\A-O_Parametrization_Natural_COMPLETED.xlsx",
                "completed_ao_snapshot",
                60,
                allow_auto=False,
            ),
        ),
    ),
    "ECU_AGR": ModelSpec(
        model_label="ECU_AGR",
        live_rel_path=r"Ecuador\ECU_AGR\A1_Outputs\A-O_Parametrization.xlsx",
        sources=(
            SourceSpec(
                r"Ecuador\ECU_AGR\A1_Outputs\reference_works\A-O_Parametrization_REF.xlsx",
                "ecuador_non_energy_ao_reference",
                10,
                allow_auto=False,
            ),
            SourceSpec(
                r"Ecuador\ECU_AGR\A1_Outputs\reference_works\ModeloSuelo_BAU.xlsx",
                "external_osemosys_reference",
                25,
                allow_auto=False,
                reader="osemosys",
            ),
            SourceSpec(
                r"Ecuador\ECU_AGR\A1_Outputs\reference_freeze\A-O_Parametrization.xlsx",
                "reference_freeze_snapshot",
                50,
                allow_auto=False,
            ),
        ),
    ),
    "ECU_USCUSS": ModelSpec(
        model_label="ECU_USCUSS",
        live_rel_path=r"Ecuador\ECU_USCUSS\A1_Outputs\A-O_Parametrization.xlsx",
        sources=(
            SourceSpec(
                r"Ecuador\ECU_USCUSS\A1_Outputs\reference_works\A-O_Parametrization_REF.xlsx",
                "ecuador_non_energy_ao_reference",
                10,
            ),
            SourceSpec(
                r"Ecuador\ECU_USCUSS\A1_Outputs\reference_works\ModeloSuelo_BAU.xlsx",
                "external_osemosys_reference",
                25,
                allow_auto=False,
                reader="osemosys",
            ),
            SourceSpec(
                r"Ecuador\ECU_USCUSS\A1_Outputs\reference_freeze\A-O_Parametrization.xlsx",
                "reference_freeze_snapshot",
                50,
                allow_auto=False,
            ),
        ),
    ),
}


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def rel_or_abs(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def value_signature(row: AoCostRow) -> str:
    values: list[float] = []
    for value in row.year_values.values():
        number = parse_float(value)
        if number is not None:
            values.append(number)
    if not values:
        return "no_numeric"
    unique = sorted({round(value, 10) for value in values})
    if len(unique) <= 6:
        return ";".join(format_number(value) for value in unique)
    return f"{format_number(unique[0])}..{format_number(unique[-1])} ({len(unique)} unique)"


def cost_row_issue(row: AoCostRow, *, source: bool) -> str:
    stats = row_stats(row)
    if stats.numeric == 0:
        return "missing_all_years" if not source else "source_missing_all_years"
    if stats.one_share >= 0.5:
        return "mostly_one_placeholder" if not source else "source_mostly_one_placeholder"
    if row.parameter in {"CapitalCost", "FixedCost"} and stats.zero_share >= 0.95:
        return "mostly_zero_placeholder" if not source else "source_mostly_zero_placeholder"
    if row.parameter == "VariableCost" and stats.zero_share >= 0.95:
        return "mostly_zero_variable_cost" if not source else "source_zero_variable_cost"
    if stats.non_numeric:
        return "contains_non_numeric_values" if not source else "source_contains_non_numeric_values"
    if not source and stats.numeric <= 1 and stats.blank_share >= 0.8:
        return "single_year_only"
    return ""


def is_suspicious_target(row: AoCostRow) -> bool:
    return bool(cost_row_issue(row, source=False))


def source_is_usable_for_review(row: AoCostRow) -> bool:
    issue = cost_row_issue(row, source=True)
    if issue in {
        "source_missing_all_years",
        "source_mostly_one_placeholder",
        "source_mostly_zero_placeholder",
        "source_contains_non_numeric_values",
    }:
        return False
    return True


def source_is_safe_value(row: AoCostRow) -> bool:
    return cost_row_issue(row, source=True) == ""


def canonical_unit(unit: str) -> str:
    tokens = normalize_text(unit).split()
    normalized: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        next_token = tokens[index + 1] if index + 1 < len(tokens) else ""
        if token == "m" and next_token in {"us", "usd"}:
            normalized.append("musd")
            index += 2
            continue
        if token in {"mus", "musd"}:
            normalized.append("musd")
        elif token in {"us", "usd"}:
            normalized.append("usd")
        else:
            normalized.append(token)
        index += 1
    return "".join(normalized)


def unit_denominator(canonical: str) -> str:
    for denominator in ("mha", "pj", "gwh", "gvkm", "mt", "ton", "kg"):
        if canonical.endswith(denominator) or denominator in canonical:
            return denominator
    return ""


def unit_match(target_unit: str, source_unit: str) -> str:
    target = canonical_unit(target_unit)
    source = canonical_unit(source_unit)
    if not target or not source:
        return "unit_unknown"
    if target == source:
        return "unit_exact"
    target_denom = unit_denominator(target)
    source_denom = unit_denominator(source)
    if "musd" in target and "musd" in source and target_denom and target_denom == source_denom:
        return "unit_money_denominator_compatible"
    if "usd" in target and "usd" in source and target_denom and target_denom == source_denom:
        return "unit_money_denominator_compatible"
    return "unit_incompatible"


def unit_allows_auto(match: str) -> bool:
    return match in {"unit_exact", "unit_money_denominator_compatible"}


def token_set(value: Any) -> set[str]:
    stop = {
        "primary",
        "secondary",
        "demand",
        "tech",
        "technology",
        "for",
        "the",
        "and",
        "of",
        "import",
    }
    return {part for part in normalize_text(value).split() if part and part not in stop}


def name_metrics(target: AoCostRow, source: AoCostRow) -> tuple[float, float]:
    target_name = normalize_text(target.tech_name)
    source_name = normalize_text(source.tech_name)
    if not target_name or not source_name:
        similarity = 0.0
    else:
        similarity = SequenceMatcher(None, target_name, source_name).ratio()
    target_tokens = token_set(target.tech_name)
    source_tokens = token_set(source.tech_name)
    if not target_tokens or not source_tokens:
        jaccard = 0.0
    else:
        jaccard = len(target_tokens & source_tokens) / len(target_tokens | source_tokens)
    return round(similarity, 3), round(jaccard, 3)


def normalized_name_equal(target: AoCostRow, source: AoCostRow) -> bool:
    target_name = normalize_text(target.tech_name)
    source_name = normalize_text(source.tech_name)
    return bool(target_name and source_name and target_name == source_name)


def read_osemosys_cost_rows(
    path: Path,
    *,
    model_label: str,
    source_label: str,
    source_kind: str,
) -> list[AoCostRow]:
    rows: list[AoCostRow] = []
    if not path.exists():
        return rows
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        for parameter in COST_PARAMETERS:
            if parameter not in wb.sheetnames:
                continue
            ws = wb[parameter]
            header_row = None
            headers: dict[str | int, int] = {}
            for row_index in range(1, min(ws.max_row or 1, 12) + 1):
                values = [
                    ws.cell(row=row_index, column=col).value
                    for col in range(1, min(ws.max_column or 1, 160) + 1)
                ]
                normalized = {clean(value).upper() for value in values if value is not None}
                if "PARAMETER" in normalized and "TECHNOLOGY" in normalized:
                    header_row = row_index
                    for col, value in enumerate(values, start=1):
                        text = clean(value)
                        if not text:
                            continue
                        if isinstance(value, int) or re.fullmatch(r"\d{4}", text):
                            headers[int(text)] = col
                        else:
                            headers[text.upper()] = col
                    break
            if header_row is None:
                continue
            param_col = headers.get("PARAMETER")
            tech_col = headers.get("TECHNOLOGY")
            if not isinstance(param_col, int) or not isinstance(tech_col, int):
                continue
            years = tuple(sorted(year for year in headers if isinstance(year, int)))
            if not years:
                continue
            max_col = max([param_col, tech_col] + [headers[year] for year in years])
            for row_index, values in enumerate(
                ws.iter_rows(
                    min_row=header_row + 1,
                    max_row=ws.max_row,
                    max_col=max_col,
                    values_only=True,
                ),
                start=header_row + 1,
            ):
                row_parameter = clean(values[param_col - 1] if len(values) >= param_col else "")
                tech = clean(values[tech_col - 1] if len(values) >= tech_col else "")
                if row_parameter != parameter or not tech:
                    continue
                year_values = {
                    year: values[headers[year] - 1] if len(values) >= headers[year] else None
                    for year in years
                }
                rows.append(
                    AoCostRow(
                        country=COUNTRY,
                        model_label=model_label,
                        workbook_path=path,
                        source_label=source_label,
                        source_kind=source_kind,
                        sheet=ws.title,
                        row_index=row_index,
                        tech=tech,
                        tech_name=tech,
                        parameter=parameter,
                        unit="",
                        projection_mode="OSeMOSYS parameter sheet",
                        year_values=year_values,
                        header_years=years,
                    )
                )
    finally:
        wb.close()
    return rows


def load_source_candidates(root: Path, spec: ModelSpec) -> tuple[list[SourceCandidate], list[str]]:
    candidates: list[SourceCandidate] = []
    warnings: list[str] = []
    for source_spec in spec.sources:
        path = root / source_spec.rel_path
        if not path.exists():
            warnings.append(f"source_missing:{source_spec.rel_path}")
            continue
        source_label = rel_or_abs(root, path)
        try:
            if source_spec.reader == "ao":
                rows = read_ao_cost_rows(
                    path,
                    country=COUNTRY,
                    model_label=spec.model_label,
                    source_label=source_label,
                    source_kind=source_spec.source_kind,
                )
            elif source_spec.reader == "osemosys":
                rows = read_osemosys_cost_rows(
                    path,
                    model_label=spec.model_label,
                    source_label=source_label,
                    source_kind=source_spec.source_kind,
                )
            else:
                warnings.append(f"unknown_reader:{source_spec.reader}:{source_spec.rel_path}")
                continue
        except Exception as exc:  # noqa: BLE001 - keep planning robust across messy workbooks.
            warnings.append(f"source_read_failed:{source_spec.rel_path}:{exc}")
            continue
        for row in rows:
            candidates.append(
                SourceCandidate(
                    row=row,
                    rel_path=source_label,
                    source_kind=source_spec.source_kind,
                    priority=source_spec.priority,
                    allow_auto=source_spec.allow_auto,
                )
            )
    return candidates, warnings


def score_candidate(target: AoCostRow, candidate: SourceCandidate) -> CandidateScore:
    source = candidate.row
    if target.parameter != source.parameter:
        return CandidateScore(
            score=-999.0,
            decision="NO_SAFE_MATCH",
            reason="parameter_mismatch",
            unit_match="",
            name_similarity=0.0,
            token_jaccard=0.0,
            coverage_share=0.0,
            hard_conflict="parameter_mismatch",
        )

    score = 0.0
    reasons: list[str] = []
    hard_conflict = ""
    exact_tech = clean(target.tech).upper() == clean(source.tech).upper()
    same_name = normalized_name_equal(target, source)
    name_similarity, token_jaccard = name_metrics(target, source)
    unit = unit_match(target.unit, source.unit)
    _expanded, coverage, coverage_note = expanded_source_values(source, target.header_years)
    source_issue = cost_row_issue(source, source=True)

    if exact_tech:
        score += 55
        reasons.append("same_tech_id")
    else:
        score += max(name_similarity, token_jaccard) * 35
        if name_similarity >= 0.75:
            reasons.append("strong_name_similarity")
        if token_jaccard >= 0.5:
            reasons.append("strong_token_overlap")

    if same_name:
        score += 35
        reasons.append("same_normalized_name")

    if target.sheet == source.sheet:
        score += 12
        reasons.append("same_sheet")
    elif normalize_text(target.sheet) == normalize_text(source.sheet):
        score += 8
        reasons.append("same_normalized_sheet")

    if unit_allows_auto(unit):
        score += 20
        reasons.append(unit)
    elif unit == "unit_unknown":
        score += 2
        reasons.append(unit)
    else:
        score -= 35
        reasons.append(unit)
        hard_conflict = "unit_incompatible"

    if source_is_safe_value(source):
        score += 18
        reasons.append("source_values_not_placeholder")
    elif source_issue == "source_zero_variable_cost":
        reasons.append("source_zero_variable_cost_review")
    else:
        score -= 80
        reasons.append(source_issue)
        hard_conflict = source_issue

    score += min(coverage, 1.0) * 12
    if coverage >= 0.95:
        reasons.append("full_year_coverage")
    elif coverage >= 0.5:
        reasons.append("partial_year_coverage")
    else:
        hard_conflict = hard_conflict or "low_year_coverage"

    if not candidate.allow_auto:
        reasons.append("source_review_only")

    auto_ready = (
        candidate.allow_auto
        and exact_tech
        and same_name
        and target.sheet == source.sheet
        and unit_allows_auto(unit)
        and source_is_safe_value(source)
        and coverage >= 0.95
    )
    review_ready = (
        source_is_usable_for_review(source)
        and coverage >= 0.5
        and (exact_tech or score >= 70)
    )

    if auto_ready:
        decision = "AUTO_HIGH_CONFIDENCE"
        hard_conflict = ""
    elif review_ready:
        decision = "REVIEW_REQUIRED"
    else:
        decision = "NO_SAFE_MATCH"

    if hard_conflict and decision == "AUTO_HIGH_CONFIDENCE":
        decision = "REVIEW_REQUIRED"

    if coverage_note:
        reasons.append(coverage_note)

    return CandidateScore(
        score=round(score, 3),
        decision=decision,
        reason=" | ".join(reason for reason in reasons if reason),
        unit_match=unit,
        name_similarity=name_similarity,
        token_jaccard=token_jaccard,
        coverage_share=round(coverage, 3),
        hard_conflict=hard_conflict,
    )


def mapping_row(target: AoCostRow, candidate: SourceCandidate, score: CandidateScore) -> dict[str, Any]:
    source = candidate.row
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
        "target_issue": cost_row_issue(target, source=False),
        "target_values_summary": value_signature(target),
        "source_kind": candidate.source_kind,
        "source_path": str(source.workbook_path),
        "source_priority": candidate.priority,
        "source_auto_allowed": "YES" if candidate.allow_auto else "NO",
        "source_sheet": source.sheet,
        "source_row_index": source.row_index,
        "source_tech": source.tech,
        "source_tech_name": source.tech_name,
        "source_parameter": source.parameter,
        "source_unit": source.unit,
        "source_projection_mode": source.projection_mode,
        "source_issue": cost_row_issue(source, source=True) or "ok",
        "source_values_summary": value_signature(source),
        "score": format_number(score.score),
        "decision": score.decision,
        "reason": score.reason,
        "unit_match": score.unit_match,
        "name_similarity": format_number(score.name_similarity),
        "token_jaccard": format_number(score.token_jaccard),
        "coverage_share": format_number(score.coverage_share),
        "hard_conflict": score.hard_conflict,
    }


def no_match_row(
    target: AoCostRow,
    *,
    candidate_count: int,
    suggested_next_source: str,
    reason: str,
) -> dict[str, Any]:
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
        "issue": cost_row_issue(target, source=False),
        "target_values_summary": value_signature(target),
        "candidate_count": candidate_count,
        "suggested_next_source": suggested_next_source,
        "reason": reason,
    }


def make_manifest_rows(
    *,
    target: AoCostRow,
    candidate: SourceCandidate,
    score: CandidateScore,
    generated_at: str,
    include_review: bool,
) -> list[dict[str, Any]]:
    if score.decision == "REVIEW_REQUIRED" and not include_review:
        return []
    source = candidate.row
    new_values, _coverage, coverage_note = expanded_source_values(source, target.header_years)
    if not new_values:
        return []
    approved = "YES" if score.decision == "AUTO_HIGH_CONFIDENCE" else "NO"
    rows: list[dict[str, Any]] = []
    for year in sorted(target.header_years):
        if year not in new_values:
            continue
        old_value = target.year_values.get(year)
        new_value = new_values[year]
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
                str(source.workbook_path),
                str(source.row_index),
            ]
        )
        rows.append(
            {
                "manifest_id": hashlib.sha256(manifest_key.encode("utf-8")).hexdigest()[:16],
                "approved": approved,
                "decision": score.decision,
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
                "source_kind": candidate.source_kind,
                "source_path": str(source.workbook_path),
                "source_sheet": source.sheet,
                "source_row_index": source.row_index,
                "source_tech": source.tech,
                "source_tech_name": source.tech_name,
                "source_unit": source.unit,
                "source_projection_mode": source.projection_mode,
                "score": format_number(score.score),
                "reason": " | ".join(part for part in [score.reason, coverage_note] if part),
                "row_fingerprint": target.row_fingerprint,
                "projection_mode_old": target.projection_mode,
                "projection_mode_new": "User defined",
                "unit_match": score.unit_match,
                "generated_at": generated_at,
            }
        )
    return rows


def select_models(model_arg: str) -> list[str]:
    if model_arg.lower() == "all":
        return list(MODEL_SPECS)
    requested = [part.strip() for part in model_arg.split(",") if part.strip()]
    unknown = [model for model in requested if model not in MODEL_SPECS]
    if unknown:
        raise SystemExit(f"Unknown model(s): {', '.join(unknown)}")
    return requested


def suggested_source_for(model: str, parameter: str) -> str:
    if model == "ECU_IPPU" and parameter == "CapitalCost":
        return "review B1_Output_Params scenario CSVs and PLANMICC IPPU logic"
    if model == "ECU_WASTE" and parameter == "FixedCost":
        return "manual source investigation; fixed-cost CSVs are empty in local outputs"
    if model in {"ECU_AGR", "ECU_USCUSS"}:
        return "review ModeloSuelo/Plantilla source mapping before any copy"
    return "manual_review"


def classification_from_counts(auto_rows: int, review_rows: int, no_match_rows: int) -> str:
    if auto_rows and not review_rows and not no_match_rows:
        return "safe automatic copy"
    if auto_rows:
        return "safe automatic copy partial"
    if review_rows:
        return "likely copy but needs review"
    if no_match_rows:
        return "no source found"
    return "not comparable"


def plan_model(
    *,
    root: Path,
    model: str,
    output_dir: Path | None,
    top_candidates: int,
    include_review_manifest: bool,
    generated_at: str,
) -> PlanResult:
    spec = MODEL_SPECS[model]
    result = PlanResult(output_dir=output_dir)
    live_path = root / spec.live_rel_path
    if not live_path.exists():
        result.warnings.append(f"live_workbook_missing:{spec.live_rel_path}")
        return result

    target_rows = read_ao_cost_rows(
        live_path,
        country=COUNTRY,
        model_label=spec.model_label,
        source_label="active_ao",
        source_kind="target",
    )
    source_candidates, warnings = load_source_candidates(root, spec)
    result.warnings.extend(warnings)

    sources_by_parameter: dict[str, list[SourceCandidate]] = defaultdict(list)
    sources_by_parameter_tech: dict[tuple[str, str], list[SourceCandidate]] = defaultdict(list)
    for candidate in source_candidates:
        sources_by_parameter[candidate.row.parameter].append(candidate)
        sources_by_parameter_tech[
            (candidate.row.parameter, clean(candidate.row.tech).upper())
        ].append(candidate)

    target_rows_by_parameter: dict[str, list[AoCostRow]] = defaultdict(list)
    for target in target_rows:
        target_rows_by_parameter[target.parameter].append(target)

    decision_by_parameter: dict[str, Counter[str]] = defaultdict(Counter)
    manifest_cells_by_parameter: dict[str, Counter[str]] = defaultdict(Counter)
    source_rows_by_parameter = Counter(candidate.row.parameter for candidate in source_candidates)

    for parameter in COST_PARAMETERS:
        for target in target_rows_by_parameter.get(parameter, []):
            if not is_suspicious_target(target):
                continue
            scored: list[tuple[CandidateScore, SourceCandidate]] = []
            exact_candidates = sources_by_parameter_tech.get(
                (parameter, clean(target.tech).upper()), []
            )
            if any(source_is_usable_for_review(candidate.row) for candidate in exact_candidates):
                candidate_pool = exact_candidates
            else:
                candidate_pool = exact_candidates + [
                    candidate
                    for candidate in sources_by_parameter.get(parameter, [])
                    if candidate.source_kind == "external_osemosys_reference"
                ]
            for candidate in candidate_pool:
                score = score_candidate(target, candidate)
                if score.score > -900:
                    scored.append((score, candidate))
            scored.sort(
                key=lambda item: (
                    item[0].decision == "AUTO_HIGH_CONFIDENCE",
                    item[0].decision == "REVIEW_REQUIRED",
                    item[0].score,
                    -item[1].priority,
                ),
                reverse=True,
            )
            for score, candidate in scored[:top_candidates]:
                result.mapping_rows.append(mapping_row(target, candidate, score))

            chosen: tuple[CandidateScore, SourceCandidate] | None = None
            for score, candidate in scored:
                if score.decision == "AUTO_HIGH_CONFIDENCE":
                    chosen = (score, candidate)
                    break
            if chosen is None:
                for score, candidate in scored:
                    if score.decision == "REVIEW_REQUIRED":
                        chosen = (score, candidate)
                        break

            if chosen is None:
                decision_by_parameter[parameter]["NO_SAFE_MATCH"] += 1
                result.no_match_rows.append(
                    no_match_row(
                        target,
                        candidate_count=len(scored),
                        suggested_next_source=suggested_source_for(model, parameter),
                        reason="no_auto_or_review_candidate_found",
                    )
                )
                continue

            score, candidate = chosen
            decision_by_parameter[parameter][score.decision] += 1
            manifest_rows = make_manifest_rows(
                target=target,
                candidate=candidate,
                score=score,
                generated_at=generated_at,
                include_review=include_review_manifest,
            )
            result.manifest_rows.extend(manifest_rows)
            if score.decision == "AUTO_HIGH_CONFIDENCE":
                manifest_cells_by_parameter[parameter]["approved"] += len(manifest_rows)
            elif score.decision == "REVIEW_REQUIRED":
                manifest_cells_by_parameter[parameter]["review"] += len(manifest_rows)

            if score.decision == "REVIEW_REQUIRED":
                result.no_match_rows.append(
                    no_match_row(
                        target,
                        candidate_count=len(scored),
                        suggested_next_source="review mapping_candidates.csv",
                        reason="best_candidate_requires_review",
                    )
                )

    for parameter in COST_PARAMETERS:
        targets = target_rows_by_parameter.get(parameter, [])
        suspicious = [target for target in targets if is_suspicious_target(target)]
        counters = decision_by_parameter[parameter]
        auto_rows = counters["AUTO_HIGH_CONFIDENCE"]
        review_rows = counters["REVIEW_REQUIRED"]
        no_match_rows = counters["NO_SAFE_MATCH"]
        approved_cells = manifest_cells_by_parameter[parameter]["approved"]
        review_cells = manifest_cells_by_parameter[parameter]["review"]
        result.summary_rows.append(
            {
                "country": COUNTRY,
                "model_label": spec.model_label,
                "parameter": parameter,
                "classification": classification_from_counts(auto_rows, review_rows, no_match_rows),
                "target_rows": len(targets),
                "suspicious_target_rows": len(suspicious),
                "source_rows": source_rows_by_parameter[parameter],
                "auto_target_rows": auto_rows,
                "review_target_rows": review_rows,
                "no_safe_match_rows": no_match_rows,
                "manifest_cells": approved_cells + review_cells,
                "approved_manifest_cells": approved_cells,
                "review_manifest_cells": review_cells,
            }
        )

    return result


def combine_results(output_dir: Path | None, results: Iterable[PlanResult]) -> PlanResult:
    combined = PlanResult(output_dir=output_dir)
    for result in results:
        combined.manifest_rows.extend(result.manifest_rows)
        combined.mapping_rows.extend(result.mapping_rows)
        combined.no_match_rows.extend(result.no_match_rows)
        combined.summary_rows.extend(result.summary_rows)
        combined.warnings.extend(result.warnings)
    return combined


def write_plan_outputs(
    *,
    root: Path,
    output_dir: Path,
    result: PlanResult,
    args: argparse.Namespace,
    generated_at: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    write_csv(output_dir / "manifest.csv", result.manifest_rows, MANIFEST_FIELDS)
    write_csv(output_dir / "mapping_candidates.csv", result.mapping_rows, MAPPING_FIELDS)
    write_csv(output_dir / "no_safe_match.csv", result.no_match_rows, NO_MATCH_FIELDS)
    write_csv(output_dir / "summary.csv", result.summary_rows, SUMMARY_FIELDS)
    run_config = {
        "generated_at": generated_at,
        "root": str(root),
        "country": COUNTRY,
        "models": select_models(args.model),
        "top_candidates": args.top_candidates,
        "include_review_manifest": args.include_review_manifest,
        "read_only": True,
        "apply_available": False,
        "source_scoping": "Ecuador non-energy local PLANMICC/reference artifacts only",
        "rules": {
            "auto": [
                "exact technology id",
                "same normalized technology name",
                "same AO sheet",
                "compatible non-unknown unit",
                "non-placeholder source values",
                "full target-year coverage",
                "source allow_auto is true",
            ],
            "review": [
                "exact or strong local candidate but unit/source quality needs human review",
                "external OSeMOSYS parameter-sheet sources are never auto-approved",
                "zero-only VariableCost sources are review-only",
            ],
        },
        "warnings": result.warnings,
    }
    (output_dir / "run_config.json").write_text(
        json.dumps(run_config, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )


def print_summary(result: PlanResult) -> None:
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  {warning}")
    print("Summary:")
    for row in result.summary_rows:
        print(
            "  {model} {param}: {classification}; "
            "suspicious={suspicious}, auto={auto}, review={review}, no_match={no_match}, "
            "manifest_cells={cells}".format(
                model=row["model_label"],
                param=row["parameter"],
                classification=row["classification"],
                suspicious=row["suspicious_target_rows"],
                auto=row["auto_target_rows"],
                review=row["review_target_rows"],
                no_match=row["no_safe_match_rows"],
                cells=row["manifest_cells"],
            )
        )


def command_plan(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    generated_at = now_stamp()
    output_dir = None
    if not args.no_write:
        output_dir = (
            args.output_dir
            if args.output_dir is not None
            else DEFAULT_OUTPUT_ROOT / f"{DEFAULT_OUTPUT_PREFIX}_{generated_at}"
        )
        output_dir = output_dir.resolve()

    results = [
        plan_model(
            root=root,
            model=model,
            output_dir=output_dir,
            top_candidates=args.top_candidates,
            include_review_manifest=args.include_review_manifest,
            generated_at=generated_at,
        )
        for model in select_models(args.model)
    ]
    combined = combine_results(output_dir, results)
    if args.no_write:
        print_summary(combined)
        print("No files written (--no-write).")
        return 0

    assert output_dir is not None
    write_plan_outputs(
        root=root,
        output_dir=output_dir,
        result=combined,
        args=args,
        generated_at=generated_at,
    )
    print_summary(combined)
    print(f"Wrote dry-run plan artifacts to: {output_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only Ecuador non-energy AO cost repair planner"
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository/workspace root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser(
        "plan",
        help="Create dry-run manifests and review tables; no workbook edits are possible",
    )
    plan.add_argument(
        "--model",
        default="all",
        help="Model label, comma list, or all. Valid: ECU_IPPU, ECU_WASTE, ECU_AGR, ECU_USCUSS",
    )
    plan.add_argument("--output-dir", type=Path, default=None)
    plan.add_argument("--top-candidates", type=int, default=5)
    plan.add_argument(
        "--include-review-manifest",
        action="store_true",
        help="Also put REVIEW_REQUIRED candidates in manifest.csv with approved=NO",
    )
    plan.add_argument(
        "--no-write",
        action="store_true",
        help="Read and score workbooks but do not create output files",
    )
    plan.set_defaults(func=command_plan)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
