"""Tables the suite reads. No value of the system lives in the code: models, scenarios, tolerances, file names and
the history cut-off come from config/gates/*.csv, the model's own configuration or the pipeline's tables."""
from __future__ import annotations

import csv
import re
from pathlib import Path


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def thresholds(root: Path) -> dict:
    out = {}
    for r in read_csv(root / "config" / "gates" / "thresholds.csv"):
        v = r["value"]
        try:
            out[r["key"]] = float(v)
        except ValueError:
            out[r["key"]] = v
    return out


def models(root: Path):
    return read_csv(root / "config" / "gates" / "models.csv")


def checks(root: Path):
    return read_csv(root / "config" / "gates" / "checks.csv")


def controller(root: Path, key: str):
    """A value of config/scenarios/rules/stage_controller.csv (stage 'all' or any stage), as the pipeline reads it."""
    for r in read_csv(root / "config" / "scenarios" / "rules" / "stage_controller.csv"):
        if r.get("name") == key:
            return r["value"]
    raise KeyError(key)


def catalogue(root: Path):
    return read_csv(root / "config" / "scenarios" / "scenario_catalogue.csv")


def final_folder(root: Path):
    """{scenario: Stage 3 folder name} from the scenario catalogue."""
    return {r["scenario"]: r["stage3_folder"] for r in catalogue(root) if r.get("stage3_folder")}


def _stamp(p: Path):
    m = re.search(r"(\d{8}T\d{6}Z)", p.parent.name)
    return m.group(1) if m else ""


def job_files(root: Path, name: str, exclude=None):
    """Every _LAC_HUB/<job>/<name>, oldest job first (by the stamp in the folder name)."""
    files = [p for p in (root / "_LAC_HUB").glob(f"*/{name}") if exclude is None or exclude not in str(p)]
    return sorted(files, key=_stamp)


def latest_job_file(root: Path, name: str, exclude=None):
    f = job_files(root, name, exclude)
    return f[-1] if f else None
