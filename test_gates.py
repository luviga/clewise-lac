"""Tests for the check suite gates/ (LAC_INPUT_GATES). Each check gets a tiny synthetic data file in a temporary
folder with one case that must be flagged and one that must pass. No model of the repository is read.

Run:  py -I test_gates.py      or      py -m pytest test_gates.py
"""

from __future__ import annotations

import copy
import csv
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from gates import gmpl  # noqa: E402
from gates import run as RUN  # noqa: E402
from gates.findings import FIELDS  # noqa: E402
from gates.layers import layer_b, layer_p, layer_s  # noqa: E402
from gates.results import layer_x  # noqa: E402
from gates.standard import (bau_differences, history_identity, layer_r_scenario, published_as_maximum,  # noqa: E402
                            provenance, renewable_rule_outputs, value_register_check)
from gates.view import View  # noqa: E402

# Parameter declarations of the OSeMOSYS model files (structure only).
MODEL = """
set EMISSION; set FUEL; set MODE_OF_OPERATION; set REGION; set STORAGE; set TECHNOLOGY; set TIMESLICE; set YEAR;
param AccumulatedAnnualDemand{r in REGION, f in FUEL, y in YEAR};
param AnnualEmissionLimit{r in REGION, e in EMISSION, y in YEAR};
param AnnualExogenousEmission{r in REGION, e in EMISSION, y in YEAR};
param AvailabilityFactor{r in REGION, t in TECHNOLOGY, y in YEAR};
param CapacityFactor{r in REGION, t in TECHNOLOGY, l in TIMESLICE, y in YEAR};
param CapacityToActivityUnit{r in REGION, t in TECHNOLOGY};
param CapitalCost{r in REGION, t in TECHNOLOGY, y in YEAR};
param EmissionActivityRatio{r in REGION, t in TECHNOLOGY, e in EMISSION, m in MODE_OF_OPERATION, y in YEAR};
param EmissionsPenalty{r in REGION, e in EMISSION, y in YEAR};
param InputActivityRatio{r in REGION, t in TECHNOLOGY, f in FUEL, m in MODE_OF_OPERATION, y in YEAR};
param OperationalLife{r in REGION, t in TECHNOLOGY};
param OutputActivityRatio{r in REGION, t in TECHNOLOGY, f in FUEL, m in MODE_OF_OPERATION, y in YEAR};
param REMinProductionTarget{r in REGION, y in YEAR};
param RETagFuel{r in REGION, f in FUEL, y in YEAR};
param RETagTechnology{r in REGION, t in TECHNOLOGY, y in YEAR};
param ReserveMargin{r in REGION, y in YEAR};
param ReserveMarginTagFuel{r in REGION, f in FUEL, y in YEAR};
param ReserveMarginTagTechnology{r in REGION, t in TECHNOLOGY, y in YEAR};
param ResidualCapacity{r in REGION, t in TECHNOLOGY, y in YEAR};
param SpecifiedAnnualDemand{r in REGION, f in FUEL, y in YEAR};
param SpecifiedDemandProfile{r in REGION, f in FUEL, l in TIMESLICE, y in YEAR};
param TechnologyFromStorage{r in REGION, t in TECHNOLOGY, s in STORAGE, m in MODE_OF_OPERATION};
param TechnologyToStorage{r in REGION, t in TECHNOLOGY, s in STORAGE, m in MODE_OF_OPERATION};
param TotalAnnualMaxCapacity{r in REGION, t in TECHNOLOGY, y in YEAR};
param TotalAnnualMaxCapacityInvestment{r in REGION, t in TECHNOLOGY, y in YEAR};
param TotalAnnualMinCapacity{r in REGION, t in TECHNOLOGY, y in YEAR};
param TotalAnnualMinCapacityInvestment{r in REGION, t in TECHNOLOGY, y in YEAR};
param TotalTechnologyAnnualActivityLowerLimit{r in REGION, t in TECHNOLOGY, y in YEAR};
param TotalTechnologyAnnualActivityUpperLimit{r in REGION, t in TECHNOLOGY, y in YEAR};
param TotalTechnologyModelPeriodActivityLowerLimit{r in REGION, t in TECHNOLOGY};
param TotalTechnologyModelPeriodActivityUpperLimit{r in REGION, t in TECHNOLOGY};
param VariableCost{r in REGION, t in TECHNOLOGY, m in MODE_OF_OPERATION, y in YEAR};
param YearSplit{l in TIMESLICE, y in YEAR};
"""

YEARS = ["2023", "2024", "2025"]
DEFAULTS = {"TotalAnnualMaxCapacity": 99999, "TotalAnnualMaxCapacityInvestment": 99999,
            "TotalTechnologyAnnualActivityUpperLimit": 99999, "TotalTechnologyModelPeriodActivityUpperLimit": 99999,
            "AnnualEmissionLimit": 99999, "CapacityFactor": 1, "AvailabilityFactor": 1, "OperationalLife": 1,
            "CapacityToActivityUnit": 1}

# A tiny system: SRC (no input) gives F1, CONV turns F1 into DEM, DEM has a demand of 10 a year in two slices.
BASE = {
    "sets": {"REGION": ["R"], "YEAR": YEARS, "TECHNOLOGY": ["SRC", "CONV"], "FUEL": ["F1", "DEM"],
             "EMISSION": ["CO2"], "MODE_OF_OPERATION": ["1"], "TIMESLICE": ["S1", "S2"], "STORAGE": []},
    "params": {
        "OperationalLife": {("R", "SRC"): 10, ("R", "CONV"): 10},
        "CapacityToActivityUnit": {("R", "SRC"): 1, ("R", "CONV"): 1},
        "YearSplit": {(l, y): 0.5 for l in ("S1", "S2") for y in YEARS},
        "SpecifiedAnnualDemand": {("R", "DEM", y): 10 for y in YEARS},
        "SpecifiedDemandProfile": {("R", "DEM", l, y): 0.5 for l in ("S1", "S2") for y in YEARS},
        "OutputActivityRatio": {**{("R", "SRC", "F1", "1", y): 1 for y in YEARS},
                                **{("R", "CONV", "DEM", "1", y): 1 for y in YEARS}},
        "InputActivityRatio": {("R", "CONV", "F1", "1", y): 1 for y in YEARS},
        "EmissionActivityRatio": {("R", "SRC", "CO2", "1", y): 0.1 for y in YEARS},
        "CapitalCost": {("R", t, y): 1 for t in ("SRC", "CONV") for y in YEARS},
    },
}

THR = None


def thresholds():
    global THR
    if THR is None:
        from gates import config as C
        THR = C.thresholds(HERE)
    return THR


def write_data(path: Path, spec, model: Path | None = None):
    out = []
    for name, members in spec["sets"].items():
        out.append(f"set {name} := {' '.join(members)} ;")
    dims = gmpl.model_dims(str(model or path.parent / "OSeMOSYS_Model.txt"))
    for name in dims:
        vals = spec["params"].get(name, {})
        d = DEFAULTS.get(name, 0)
        out.append(f"param {name} default {d} :=")
        for k, v in vals.items():
            out.append(" ".join(k) + f" {v}")
        out.append(";")
    out.append("end;")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def view_of(tmp: Path, spec, name="BAU_0.txt"):
    (tmp / "OSeMOSYS_Model.txt").write_text(MODEL, encoding="utf-8")
    f = tmp / name
    write_data(f, spec)
    d = gmpl.read_data(str(f), gmpl.model_dims(str(tmp / "OSeMOSYS_Model.txt")))
    return View(d, "R", thresholds())


def ctx(**kw):
    c = dict(model="TEST", scenario="BAU", point="b1", thr=thresholds(), root=HERE, base="BAU")
    c.update(kw)
    return c


def found(rows, check, cls=None):
    return [r for r in rows if r["check"] == check and (cls is None or r["class"] == cls)]


def spec_with(**changes):
    s = copy.deepcopy(BASE)
    for name, vals in changes.items():
        if name == "sets":
            s["sets"].update(vals)
        else:
            s["params"].setdefault(name, {}).update(vals)
    return s


def run_layers(spec, *layers):
    with tempfile.TemporaryDirectory() as tmp:
        v = view_of(Path(tmp), spec)
        rows = []
        for layer in layers:
            rows += list(layer(v, ctx()))
        return rows


def flagged_and_pass(check, bad, good, layer, cls="FAIL"):
    rb = run_layers(bad, layer)
    rg = run_layers(good, layer)
    assert found(rb, check, cls), (check, "not flagged", rb)
    assert not found(rg, check), (check, "flagged on the passing case", found(rg, check))


# ------------------------------------------------------------------------------------------------ parser
def test_parser_table_and_slice_forms():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "OSeMOSYS_Model.txt").write_text(MODEL, encoding="utf-8")
        (t / "d.txt").write_text(
            "set REGION := R ;\nset YEAR := 2023 2024 ;\nset TECHNOLOGY := A B ;\nset FUEL := F ;\n"
            "set MODE_OF_OPERATION := 1 ;\nset TIMESLICE := S ;\n"
            "param CapacityToActivityUnit default 1 :\nA B :=\nR 31.5 2\n;\n"
            "param OutputActivityRatio default 0 :=\n[R,A,F,*,*]:\n2023 2024 :=\n1 0.5 0.7\n;\n"
            "param ResidualCapacity default 0 :=\nR A 2023 3\n;\nend;\n", encoding="utf-8")
        d = gmpl.read_data(str(t / "d.txt"), gmpl.model_dims(str(t / "OSeMOSYS_Model.txt")))
        assert d.params["CapacityToActivityUnit"].values[("R", "A")] == 31.5
        assert d.params["OutputActivityRatio"].values[("R", "A", "F", "1", "2024")] == 0.7
        assert d.params["ResidualCapacity"].get(("R", "B", "2024")) == 0


# ------------------------------------------------------------------------------------------------ layer S
def test_S0_b1_consistency():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        v = view_of(t, BASE)
        folder = t / "M" / "B1_Output_Params" / "BAU"
        folder.mkdir(parents=True)

        def table(value):
            with open(folder / "ResidualCapacity.csv", "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["PARAMETER", "Scenario", "REGION", "TECHNOLOGY", "YEAR", "Value"])
                w.writerow(["ResidualCapacity", "BAU", "R", "SRC", "2023", value])
        table(5)
        m = {"path": "M"}
        bad = list(RUN.b1_consistency(m, "BAU", v.d, ctx(), t, thresholds()))
        table(0)
        good = list(RUN.b1_consistency(m, "BAU", v.d, ctx(), t, thresholds()))
        assert found(bad, "S0", "FAIL") and not found(good, "S0")


def test_S1_demand_not_reachable():
    bad = spec_with(OutputActivityRatio={("R", "SRC", "F1", "1", y): 0 for y in YEARS})
    flagged_and_pass("S1", bad, BASE, layer_s)


def test_S2_input_without_producer():
    bad = spec_with(OutputActivityRatio={("R", "SRC", "F1", "1", y): 0 for y in YEARS},
                    TotalTechnologyAnnualActivityLowerLimit={("R", "CONV", "2024"): 1})
    flagged_and_pass("S2", bad, BASE, layer_s)


def test_S3_dead_end_fuel():
    bad = spec_with(sets={"FUEL": ["F1", "DEM", "WASTE"]},
                    OutputActivityRatio={("R", "SRC", "WASTE", "1", y): 0.2 for y in YEARS})
    flagged_and_pass("S3", bad, BASE, layer_s, cls="WARN")


def test_S4_forced_with_dead_chain():
    bad = spec_with(TotalAnnualMaxCapacity={("R", "SRC", y): 0 for y in YEARS},
                    TotalTechnologyAnnualActivityLowerLimit={("R", "CONV", "2024"): 1})
    good = spec_with(TotalTechnologyAnnualActivityLowerLimit={("R", "CONV", "2024"): 1})
    flagged_and_pass("S4", bad, good, layer_s)


def test_S5_duplicate_key():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        v = view_of(t, BASE)
        text = (t / "BAU_0.txt").read_text().replace("R SRC 2023 1\n", "R SRC 2023 1\nR SRC 2023 2\n", 1)
        (t / "bad.txt").write_text(text)
        d = gmpl.read_data(str(t / "bad.txt"), v.d.dims)
        bad = list(layer_s(View(d, "R", thresholds()), ctx()))
        good = list(layer_s(v, ctx()))
        assert found(bad, "S5", "FAIL") and not found(good, "S5")


def test_S6_capacity_factor_range():
    bad = spec_with(CapacityFactor={("R", "SRC", "S1", "2024"): 1.3})
    flagged_and_pass("S6", bad, BASE, layer_s)


def test_S7_missing_scenario_file():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        for rel in ("config/gates/thresholds.csv", "config/scenarios/scenario_catalogue.csv",
                    "config/scenarios/rules/stage_controller.csv", "config/scenarios/technology_types.csv"):
            (t / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(HERE / rel, t / rel)
        md = t / "M"
        (md / "Executables" / "BAU_0").mkdir(parents=True)
        (md / "B1_Output_Params" / "BAU").mkdir(parents=True)
        (md / "OSeMOSYS_Model.txt").write_text(MODEL, encoding="utf-8")
        write_data(md / "Executables" / "BAU_0" / "BAU_0.txt", BASE, md / "OSeMOSYS_Model.txt")
        m = {"model": "M", "path": "M", "kind": "sector", "a2_compiler": "a2.py", "b1_runner": "b1.py",
             "scenarios": "BAU|NDC", "base_scenario": "BAU", "stage3": "no"}
        rows, _, _ = RUN.check_model((m, "b1", [], t, t, t))
        assert [r for r in found(rows, "S7", "FAIL") if r["scenario"] == "NDC"]
        assert not [r for r in found(rows, "S7") if r["scenario"] == "BAU"]


# ------------------------------------------------------------------------------------------------ layer B
def test_B1_min_above_max_capacity():
    bad = spec_with(TotalAnnualMinCapacity={("R", "SRC", "2024"): 50}, TotalAnnualMaxCapacity={("R", "SRC", "2024"): 40})
    good = spec_with(TotalAnnualMinCapacity={("R", "SRC", "2024"): 30}, TotalAnnualMaxCapacity={("R", "SRC", "2024"): 40})
    flagged_and_pass("B1", bad, good, layer_b)


def test_B2_min_above_max_investment():
    bad = spec_with(TotalAnnualMinCapacityInvestment={("R", "SRC", "2024"): 5},
                    TotalAnnualMaxCapacityInvestment={("R", "SRC", "2024"): 4})
    good = spec_with(TotalAnnualMinCapacityInvestment={("R", "SRC", "2024"): 3},
                     TotalAnnualMaxCapacityInvestment={("R", "SRC", "2024"): 4})
    flagged_and_pass("B2", bad, good, layer_b)


def test_B3_lower_above_upper_activity():
    bad = spec_with(TotalTechnologyAnnualActivityLowerLimit={("R", "SRC", "2024"): 5},
                    TotalTechnologyAnnualActivityUpperLimit={("R", "SRC", "2024"): 4})
    good = spec_with(TotalTechnologyAnnualActivityLowerLimit={("R", "SRC", "2024"): 3},
                     TotalTechnologyAnnualActivityUpperLimit={("R", "SRC", "2024"): 4})
    flagged_and_pass("B3", bad, good, layer_b)


def test_B4_model_period_limits():
    bad = spec_with(TotalTechnologyAnnualActivityLowerLimit={("R", "SRC", y): 5 for y in YEARS},
                    TotalTechnologyModelPeriodActivityUpperLimit={("R", "SRC"): 12})
    good = spec_with(TotalTechnologyAnnualActivityLowerLimit={("R", "SRC", y): 5 for y in YEARS},
                     TotalTechnologyModelPeriodActivityUpperLimit={("R", "SRC"): 15})
    flagged_and_pass("B4", bad, good, layer_b)


def test_B5_residual_above_max():
    bad = spec_with(ResidualCapacity={("R", "SRC", "2024"): 2}, TotalAnnualMaxCapacity={("R", "SRC", "2024"): 1.5})
    good = spec_with(ResidualCapacity={("R", "SRC", "2024"): 1}, TotalAnnualMaxCapacity={("R", "SRC", "2024"): 1.5})
    flagged_and_pass("B5", bad, good, layer_b)


def test_B6_residual_plus_committed_above_max():
    bad = spec_with(ResidualCapacity={("R", "SRC", "2024"): 1.0},
                    TotalAnnualMinCapacityInvestment={("R", "SRC", "2023"): 0.5},
                    TotalAnnualMaxCapacity={("R", "SRC", "2024"): 1.4999})
    good = spec_with(ResidualCapacity={("R", "SRC", "2024"): 1.0},
                     TotalAnnualMinCapacityInvestment={("R", "SRC", "2023"): 0.5},
                     TotalAnnualMaxCapacity={("R", "SRC", "2024"): 1.5})
    flagged_and_pass("B6", bad, good, layer_b)


def test_B7_min_capacity_unreachable():
    inv = {("R", "SRC", y): 0.1 for y in YEARS}
    bad = spec_with(TotalAnnualMinCapacity={("R", "SRC", "2024"): 1}, TotalAnnualMaxCapacityInvestment=inv)
    good = spec_with(TotalAnnualMinCapacity={("R", "SRC", "2024"): 0.15}, TotalAnnualMaxCapacityInvestment=inv)
    flagged_and_pass("B7", bad, good, layer_b)


def test_B8_lower_limit_above_capacity_allows():
    cap = {("R", "SRC", y): 2 for y in YEARS}
    bad = spec_with(TotalAnnualMaxCapacity=cap, TotalTechnologyAnnualActivityLowerLimit={("R", "SRC", "2024"): 2.5})
    good = spec_with(TotalAnnualMaxCapacity=cap, TotalTechnologyAnnualActivityLowerLimit={("R", "SRC", "2024"): 1.5})
    flagged_and_pass("B8", bad, good, layer_b)


# ------------------------------------------------------------------------------------------------ layer P
def test_P1_fuel_short_in_year_and_slice():
    bad = spec_with(TotalTechnologyAnnualActivityUpperLimit={("R", "SRC", "2024"): 8})
    good = spec_with(TotalTechnologyAnnualActivityUpperLimit={("R", "SRC", "2024"): 12})
    flagged_and_pass("P1", bad, good, layer_p)
    # time slice: capacity 21 a year covers 10 a year but not a profile of 0.9 in one slice of half the year
    slc = spec_with(TotalAnnualMaxCapacity={("R", "CONV", "2024"): 12},
                    SpecifiedDemandProfile={("R", "DEM", "S1", "2024"): 0.9, ("R", "DEM", "S2", "2024"): 0.1})
    rows = run_layers(slc, layer_p)
    assert [r for r in found(rows, "P1", "FAIL") if r["timeslice"] == "S1"], rows


def test_P2_emission_limit_unreachable():
    bad = spec_with(AnnualEmissionLimit={("R", "CO2", "2024"): 0.5})
    good = spec_with(AnnualEmissionLimit={("R", "CO2", "2024"): 1.5})
    flagged_and_pass("P2", bad, good, layer_p)
    # two levels: emissions sit on the fuel supply, a ceiling on the clean vehicle forces the fossil path
    two = {"sets": {"TECHNOLOGY": ["GSUP", "ESUP", "CARG", "CARE"], "FUEL": ["GSL", "ELE", "DEM"]}}

    def two_level(ceiling):
        s = copy.deepcopy(BASE)
        s["sets"].update(two["sets"])
        p = s["params"]
        p["OperationalLife"] = {("R", t): 10 for t in two["sets"]["TECHNOLOGY"]}
        p["CapacityToActivityUnit"] = {("R", t): 1 for t in two["sets"]["TECHNOLOGY"]}
        p["OutputActivityRatio"] = {k: 1 for y in YEARS for k in (("R", "GSUP", "GSL", "1", y), ("R", "ESUP", "ELE", "1", y),
                                                                     ("R", "CARG", "DEM", "1", y), ("R", "CARE", "DEM", "1", y))}
        p["InputActivityRatio"] = {k: 1 for y in YEARS for k in (("R", "CARG", "GSL", "1", y), ("R", "CARE", "ELE", "1", y))}
        p["EmissionActivityRatio"] = {("R", "GSUP", "CO2", "1", y): 1 for y in YEARS}
        p["CapitalCost"] = {}
        p["TotalTechnologyAnnualActivityUpperLimit"] = {("R", "CARE", "2024"): ceiling}
        p["AnnualEmissionLimit"] = {("R", "CO2", "2024"): 5}
        return s
    flagged_and_pass("P2", two_level(4), two_level(6), layer_p)


def test_P3_renewable_target_unreachable():
    tags = {"RETagFuel": {("R", "DEM", "2024"): 1}, "RETagTechnology": {("R", "CONV", "2024"): 1},
            "REMinProductionTarget": {("R", "2024"): 0.9}}
    bad = spec_with(**tags, TotalTechnologyAnnualActivityUpperLimit={("R", "CONV", "2024"): 10})
    bad["params"]["SpecifiedAnnualDemand"][("R", "DEM", "2024")] = 10
    bad["sets"]["TECHNOLOGY"] = ["SRC", "CONV", "ALT"]
    bad["params"]["OutputActivityRatio"].update({("R", "ALT", "DEM", "1", y): 1 for y in YEARS})
    bad["params"]["TotalTechnologyAnnualActivityUpperLimit"][("R", "CONV", "2024")] = 5
    good = spec_with(**tags)
    flagged_and_pass("P3", bad, good, layer_p)


def test_P4_reserve_margin_uncovered():
    tags = {"ReserveMargin": {("R", "2024"): 1.2}, "ReserveMarginTagFuel": {("R", "DEM", "2024"): 1},
            "ReserveMarginTagTechnology": {("R", "CONV", "2024"): 1}}
    bad = spec_with(**tags, TotalAnnualMaxCapacity={("R", "CONV", "2024"): 11})
    good = spec_with(**tags, TotalAnnualMaxCapacity={("R", "CONV", "2024"): 13})
    flagged_and_pass("P4", bad, good, layer_p)


# ------------------------------------------------------------------------------------------------ layer R
def two_scenarios(tmp: Path, policy_changes, base_changes=None):
    vb = view_of(tmp, spec_with(**(base_changes or {})), "BAU_0.txt")
    vp = view_of(tmp, spec_with(**{**(base_changes or {}), **policy_changes}), "NDC_0.txt")
    return {"BAU": vb, "NDC": vp}


def test_R1_register_value_stale():
    reg = [{"model": "M", "parameter": "CapitalCost", "tech": "SRC", "year": "2024", "before": "1", "after": "2",
            "unit": "", "_where": "job/value_register.csv line 2"}]
    with tempfile.TemporaryDirectory() as tmp:
        vs = two_scenarios(Path(tmp), {})
        bad = list(value_register_check({"path": "M"}, vs, ctx(), reg, {}))
        reg[0]["before"], reg[0]["after"] = "3", "1"
        good = list(value_register_check({"path": "M"}, vs, ctx(), reg, {}))
    assert found(bad, "R1", "FAIL") and not found(good, "R1")


def test_R2_emission_penalty():
    bad = spec_with(EmissionsPenalty={("R", "CO2", "2024"): 10})
    flagged_and_pass("R2", bad, BASE, layer_r_scenario)


def test_R3_rule_outputs_in_range():
    bad = spec_with(REMinProductionTarget={("R", "2024"): 1.35})
    good = spec_with(REMinProductionTarget={("R", "2024"): 0.95})
    flagged_and_pass("R3", bad, good, layer_r_scenario)
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "_STAGE1_OUTPUT").mkdir()
        (t / "_STAGE1_OUTPUT" / "RENEWABLE_TARGETS.csv").write_text(
            "country,scenario,year,value,basis,value_ids,derivation\nX,NDC,2030,1.35,capacity rule,,test\n"
            "X,NDC,2035,0.9,capacity rule,,test\n")
        rows = list(renewable_rule_outputs(t, ctx(point="final")))
    assert len(found(rows, "R3", "FAIL")) == 1


def test_R4_history_identical():
    with tempfile.TemporaryDirectory() as tmp:
        bad = list(history_identity({}, two_scenarios(Path(tmp), {"CapitalCost": {("R", "SRC", "2023"): 5}}),
                                    ctx(), stage3_model=False))
        good = list(history_identity({}, two_scenarios(Path(tmp), {"CapitalCost": {("R", "SRC", "2025"): 5}}),
                                     ctx(), stage3_model=False))
    assert found(bad, "R4", "FAIL") and not found(good, "R4")


def test_R5_difference_registered():
    with tempfile.TemporaryDirectory() as tmp:
        vs = two_scenarios(Path(tmp), {"CapitalCost": {("R", "SRC", "2025"): 5}})
        bad = list(bau_differences("M", vs, ctx(), {}))
        good = list(bau_differences("M", vs, ctx(), {("M", "CapitalCost", "NDC", "SRC", "", ""): [(2025, 2025)]}))
    assert found(bad, "R5", "FAIL") and not found(good, "R5")


def test_R6_published_target_as_maximum():
    import pandas as pd
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "config" / "gates").mkdir(parents=True)
        shutil.copy(HERE / "config" / "gates" / "thresholds.csv", t / "config" / "gates" / "thresholds.csv")
        job = t / "_LAC_HUB" / "job_20260101T000000Z"
        job.mkdir(parents=True)
        (job / "published_values_loaded.csv").write_text(
            "value_id,country,scenario,year,value_standard,unit_standard,check_status,result,model_input,value_written,"
            "unit_written,reason\nX-T1,X,NDC,2030,0.1,fraction,3 of 3,loaded,M/B1_Scenario_Config.xlsx Tech_Adoption NDC SRC v_2030,"
            "0.1,share,\n")
        (t / "M").mkdir()
        vs = two_scenarios(t, {})
        res = {}
        for rt in ("Min/Max", "Min"):
            pd.DataFrame({"Scenario": ["NDC"], "Tech_Set": ["SRC"], "v_2030": [0.1], "Restriction_Type": [rt]}).to_excel(
                t / "M" / "B1_Scenario_Config.xlsx", sheet_name="Tech_Adoption", index=False)
            res[rt] = list(published_as_maximum({"path": "M"}, vs, ctx(root=t), t))
    assert found(res["Min/Max"], "R6", "FAIL") and not found(res["Min"], "R6")


def test_R7_untraced_limit():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        for rel in ("config/scenarios/rules/stage_controller.csv", "config/scenarios/technology_types.csv"):
            (t / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(HERE / rel, t / rel)
        vs = {"BAU": view_of(t, spec_with(TotalAnnualMaxCapacity={("R", "SRC", "2024"): 7}))}
        m = {"model": "M", "path": "M", "a2_compiler": "a2.py", "b1_runner": "b1.py"}
        bad = list(provenance(m, vs, ctx(root=t), [], None, t))
        reg = [{"model": "M", "parameter": "TotalAnnualMaxCapacity", "tech": "SRC", "year": "2024", "after": "7",
                "_where": "job/value_register.csv line 2"}]
        good = list(provenance(m, vs, ctx(root=t), reg, None, t))
    assert found(bad, "R7", "WARN") and not found(good, "R7")


def test_R8_free_unlimited_source():
    bad = spec_with(CapitalCost={("R", "SRC", y): 0 for y in YEARS})
    flagged_and_pass("R8", bad, BASE, layer_r_scenario, cls="WARN")


# ------------------------------------------------------------------------------------------------ layer X
def results_case(tmp: Path, rows, values):
    (tmp / "config" / "scenarios" / "rules").mkdir(parents=True)
    shutil.copy(HERE / "config" / "scenarios" / "rules" / "stage_controller.csv",
                tmp / "config" / "scenarios" / "rules" / "stage_controller.csv")
    (tmp / "inputs" / "scenarios").mkdir(parents=True)
    (tmp / "inputs" / "scenarios" / "scenario_values.csv").write_text(
        "country,scenario,lever,lever_kind,year,value,unit,source_id,value_id,note\n" + values)
    f = tmp / "results_summary.csv"
    with open(f, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["country", "scenario", "year", "energy_emissions_kt", "gen_pj_solar", "newcap_gw_solar",
                    "renewable_share"])
        w.writerows(rows)
    return list(layer_x(tmp, f, ctx(point="results", root=tmp)))


def test_X1_jump():
    with tempfile.TemporaryDirectory() as tmp:
        bad = results_case(Path(tmp), [["X", "BAU", 2035, 100, 5, 0, 0.5], ["X", "BAU", 2036, 60, 5, 0, 0.5]], "")
    with tempfile.TemporaryDirectory() as tmp:
        good = results_case(Path(tmp), [["X", "BAU", 2035, 100, 5, 0, 0.5], ["X", "BAU", 2036, 95, 5, 0, 0.5]], "")
    assert found(bad, "X1", "WARN") and not found(good, "X1")


def test_X2_target_met():
    val = "X,NDC,renewable_share,share of generation,2030,0.9,fraction,S,X-T1,test\n"
    rows = [["X", "BAU", 2030, 100, 5, 0, 0.5], ["X", "NDC", 2030, 100, 5, 0, 0.8]]
    with tempfile.TemporaryDirectory() as tmp:
        bad = results_case(Path(tmp), rows, val)
    rows[1][6] = 0.9
    with tempfile.TemporaryDirectory() as tmp:
        good = results_case(Path(tmp), rows, val)
    assert found(bad, "X2", "FAIL") and not found(good, "X2")


def test_X3_history_results_identical():
    rows = [["X", "BAU", 2023, 100, 5, 0, 0.5], ["X", "NDC", 2023, 187, 5, 0, 0.5]]
    with tempfile.TemporaryDirectory() as tmp:
        bad = results_case(Path(tmp), rows, "")
    rows[1][3] = 100
    with tempfile.TemporaryDirectory() as tmp:
        good = results_case(Path(tmp), rows, "")
    assert found(bad, "X3", "WARN") and not found(good, "X3")


def test_result_fields():
    assert FIELDS[:2] == ["check", "class"]


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]

if __name__ == "__main__":
    failed = 0
    for t in TESTS:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as exc:  # report every test, then fail
            failed += 1
            print(f"FAIL {t.__name__}: {exc!r}"[:600])
    sys.exit(1 if failed else 0)
