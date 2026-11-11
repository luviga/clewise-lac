"""Phase C1 and C2: build write_set.csv, currency_conversion.csv, unplaced.csv and
one manifest per country for ao_cost_repair_manager.py (LAC_OVERNIGHT_COST_RUN).

Order (brief section 6, C1): ALL and STEPS rows of proposals_all.csv, overridden
by regional_proposals.csv, then D2, D3, D4, D6. Rows whose change_class is
"keep" are written only if a rule changes them. D5 and D10 cells are skipped.
Each cell is then located in the A-O workbook by sheet, Tech, Parameter and
year column (C2), and D8 sets projection_mode_new.
"""
from __future__ import annotations

import csv
import glob
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import openpyxl
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, r"C:\clw_overnight")
from currency_d3 import CPI, classify  # noqa: E402
from ao_cost_repair_manager import MANIFEST_FIELDS  # noqa: E402

ROOT = Path(r"C:\clw_overnight")
HUB = ROOT / "_LAC_HUB"
JOB = HUB / "cost_write_run_20261111T071733Z"
STAMP = "20261111T071733Z"

MODEL = {
    "CostaRica": "CostaRica/CR_ENERGY/t1_confection",
    "DominicanRepublic": "DominicanRepublic/RD_ENERGY",
    "Ecuador": "Ecuador/ECU_Energy",
    "Guatemala": "Guatemala/GUA_ENERGY",
    "Honduras": "Honduras/HON_ENERGY",
    "Jamaica": "Jamaica/JAM_ENERGY",
}
JOBKEY = {"CostaRica": "cr", "DominicanRepublic": "dr", "Ecuador": "ecu", "Guatemala": "gua", "Honduras": "hon",
          "Jamaica": "jam"}
CPI_SOURCE = {"CostaRica": "CRC-001", "DominicanRepublic": "CSD-001", "Ecuador": "BEN-004", "Guatemala": "FUE-001",
              "Honduras": "CSH-005", "Jamaica": "CSJ-006"}
SHEETS = ["Primary Techs", "Secondary Techs"]
TOL = 1e-12


def f(x):
    try:
        v = float(x)
        return None if math.isnan(v) else v
    except (TypeError, ValueError):
        return None


def load_constants():
    """CPI-U annual averages and WEO 2025 coal series from the country jobs' constants.csv."""
    cpi, coal = {}, {}
    for c, k in JOBKEY.items():
        fn = glob.glob(str(HUB / f"cost_src_{k}_*" / "constants.csv"))[0]
        df = pd.read_csv(fn, dtype=str, keep_default_na=False)
        name_col = df.columns[0]
        for _, r in df.iterrows():
            n, v = r[name_col], f(r["value"])
            if v is None:
                continue
            for pre in ("US_CPIU_", "CPIU_", "CPI_U_"):
                if n.startswith(pre) and n[len(pre):].isdigit():
                    cpi.setdefault(int(n[len(pre):]), set()).add(v)
            nl = n.upper()
            if nl.startswith("WEO2025_COAL_EU_") or nl.startswith("WEO2025_STEAM_COAL_JAPAN_"):
                coal[(c, nl)] = v
    cpi = {y: vs.pop() if len(vs) == 1 else None for y, vs in cpi.items()}
    return cpi, coal


def lin(points: dict, y: int) -> float:
    ys = sorted(points)
    if y <= ys[0]:
        return points[ys[0]]
    if y >= ys[-1]:
        return points[ys[-1]]
    for a, b in zip(ys, ys[1:]):
        if a <= y <= b:
            return points[a] + (points[b] - points[a]) * (y - a) / (b - a)
    raise ValueError(y)


def main():
    cpi, coal = load_constants()
    for y, v in CPI.items():
        assert cpi.get(y) == v, (y, cpi.get(y), v)

    P = pd.read_csv(HUB / "cost_review_20261111T015203Z" / "proposals_all.csv", dtype=str, keep_default_na=False)
    R = pd.read_csv(HUB / "cost_regional_20261111T050439Z" / "regional_proposals.csv", dtype=str,
                    keep_default_na=False)
    fuel_groups = set(P[P.fuel_scenario.isin(["STEPS", "CPS", "NZE"])]
                      .groupby(["country", "Tech", "Parameter"]).size().index)
    src_text = {}
    for c, k in JOBKEY.items():
        fn = glob.glob(str(HUB / f"cost_src_{k}_*" / "sources.csv"))[0]
        s = pd.read_csv(fn, dtype=str, keep_default_na=False)
        for _, row in s.iterrows():
            src_text[(c, row.iloc[0])] = " | ".join(str(v) for v in row.values)

    base = P[P.fuel_scenario.isin(["ALL", "STEPS"])].copy()
    rows = {}
    for _, x in base.iterrows():
        k = (x.country, x.sheet, x.Tech, x.Parameter, int(x.year))
        assert k not in rows, ("duplicate proposal cell", k)
        rows[k] = dict(country=x.country, sheet=x.sheet, tech_id=x["Tech.ID"], tech=x.Tech, parameter=x.Parameter,
                       year=int(x.year), fuel_scenario=x.fuel_scenario, change_class=x.change_class,
                       basis_class=x.basis_class, proposed=f(x.proposed_value), value=f(x.proposed_value),
                       source_ids=x.source_ids, derivation=x.derivation, assumption=x.assumption_sentence,
                       unit=x.unit, rules=[f"proposals_all {x.fuel_scenario} ({x.change_class})"],
                       origin="proposals_all", currency_note="")
    # regional override
    reg_groups = set()
    n_reg = 0
    for _, x in R.iterrows():
        k = (x.country, x.sheet, x.Tech, x.Parameter, int(x.year))
        reg_groups.add((x.country, x.Tech, x.Parameter))
        r = rows.get(k)
        if r is None:
            r = dict(country=x.country, sheet=x.sheet, tech_id=x["Tech.ID"], tech=x.Tech, parameter=x.Parameter,
                     year=int(x.year), fuel_scenario="ALL", basis_class=x.basis_class, unit=x.unit, rules=[],
                     currency_note="")
            rows[k] = r
        r.update(change_class=x.change_class, proposed=f(x.proposed_value), value=f(x.proposed_value),
                 source_ids=x.source_ids, derivation=x.derivation, assumption=x.assumption_sentence,
                 origin="regional")
        r["rules"] = [f"regional_proposals {x.tier} ({x.change_class})"]
        n_reg += 1

    # D2: Costa Rica PWRHYDDAM CapitalCost
    plants = [(5986.0, 623.0), (6317.0, 162.0), (5910.0, 209.0)]
    r_2023 = sum(c * w for c, w in plants) / sum(w for _, w in plants)
    r_2024 = r_2023 * cpi[2024] / cpi[2023]
    d2_factor = r_2024 / 5100.0
    d2_rows = [r for k, r in rows.items() if k[0] == "CostaRica" and k[2] == "PWRHYDDAM" and k[3] == "CapitalCost"]
    assert len(d2_rows) == 30 and all(r["origin"] == "regional" for r in d2_rows)
    r24 = [r for r in d2_rows if r["year"] == 2024][0]
    assert abs(r24["value"] - 5100.0) < 1e-9, r24["value"]
    for r in d2_rows:
        r["value"] = r["value"] * d2_factor
        r["origin"] = "D2"
        r["source_ids"] = "REG-005;CRC-001"
        r["rules"].append(f"D2 x {r_2024:.6f}/5100 (ICE PEG 2024-2040 Tabla 10.9 capacity-weighted mean "
                          f"{r_2023:.6f} USD/kW Dec-2023 USD x CPI-U 2024/2023)")
        r["change_class"] = "D2"

    # D3: currency of non-fuel groups not from regional or D2
    overrides = {
        ("Guatemala", "PPHDAM", "FixedCost"): (None, "left: value 50 USD/kW-yr is from PEIG 2026-2050 Tabla 6 "
                                                    "(NAT-001, currency year not stated); IRENA 2022 (INT-001) is "
                                                    "only a range check"),
        ("Jamaica", "PPPVDS", "CapitalCost"): (None, "left: mixed currency years (PPPVD part 2022 USD, battery "
                                                     "part 2018 IRP USD)"),
        ("Jamaica", "PPPVDS", "FixedCost"): (None, "left: mixed currency years (PPPVD part 2022 USD, battery "
                                                   "part 2018 IRP USD)"),
        ("Jamaica", "PPWNDONS", "CapitalCost"): (None, "left: mixed currency years (PPWNDON part regional 2024 "
                                                       "USD, battery part 2018 IRP USD)"),
        ("Jamaica", "PPWNDONS", "FixedCost"): (None, "left: mixed currency years (PPWNDON part 2018 USD, "
                                                     "battery part 2018 IRP USD scaled by ATB)"),
    }
    d3_rows = []
    group_info = defaultdict(list)
    for k, r in rows.items():
        g = (r["country"], r["tech"], r["parameter"])
        if g in fuel_groups or r["origin"] in ("regional", "D2"):
            continue
        sources = {i: src_text.get((r["country"], i), "") for i in r["source_ids"].split(";") if i}
        y, how, ev = classify(r["derivation"], sources, r["country"], r["year"], r["tech"], r["value"],
                              r["change_class"])
        if g in overrides:
            y, ev = overrides[g]
            how = "override"
        if g[0] == "Jamaica" and g[1] in ("PPBGS", "PPBIM") and g[2] == "VariableCost":
            if r["change_class"] == "upgrade":
                y, how, ev = 2025, "stated", "IRENA RPGC in 2025 (PSJ-002, values in 2025 USD)"
            else:
                y, how, ev = 2022, "source", "IRENA RPGC in 2022 (PSJ-001, values in 2022 USD)"
        r["_d3_year"], r["_d3_how"], r["_d3_ev"] = y, how, ev
        d3_rows.append(r)
    # second pass for inherited rows (PPPVD may come after PPPVDS in dict order)
    for r in d3_rows:
        g = (r["country"], r["tech"], r["parameter"])
        if g in (("Guatemala", "PPPVDS", "CapitalCost"), ("Guatemala", "PPPVDS", "FixedCost")):
            parent = rows[(r["country"], r["sheet"], "PPPVD", r["parameter"], r["year"])]
            r["_d3_year"], r["_d3_how"] = parent["_d3_year"], "inherited"
            r["_d3_ev"] = f"PPPVD {r['parameter']} {r['year']} row ({parent['_d3_how']}: {parent['_d3_ev'][:60]}), " \
                          f"times a unitless ATB ratio"
    for r in d3_rows:
        y, how = r["_d3_year"], r["_d3_how"]
        g = (r["country"], r["tech"], r["parameter"])
        if r["value"] is None:
            r["_d3_status"] = "no value"
        elif how == "zero":
            r["_d3_status"] = "left: zero"
        elif y is None:
            r["_d3_status"] = "left: " + (r["_d3_ev"] if how == "override" else how)
        elif y == 2024:
            r["_d3_status"] = "left: 2024"
        elif y > 2024:
            r["_d3_status"] = f"left: {y} USD stated, after 2024 (D3 covers years before 2024)"
        elif y not in cpi or cpi[y] is None:
            r["_d3_status"] = f"left: {y} USD stated, no CPI-U {y} in any constants.csv"
        else:
            fac = cpi[2024] / cpi[y]
            r["value"] = r["value"] * fac
            r["_d3_status"] = f"converted from {y} USD x {fac:.6f}"
            r["rules"].append(f"D3 x CPI-U 2024/{y} = {cpi[2024]}/{cpi[y]} = {fac:.6f}")
            if CPI_SOURCE[r["country"]] not in r["source_ids"].split(";"):
                r["source_ids"] = r["source_ids"] + ";" + CPI_SOURCE[r["country"]]
            r["_d3_changed"] = True
        group_info[g].append(r)

    # D4: Dominican Republic EXTT_CRU and PRO_COA VariableCost = DIST_CRU and DIST_COA path
    # (filled after the workbook is read, since keep cells keep their workbook value)

    # D6: Ecuador coal (DIST_COA STEPS projected years): EU series in place of the Japan series
    eu = {2024: coal[("CostaRica", "WEO2025_COAL_EU_STEPS_2024")], 2035: coal[("CostaRica", "WEO2025_COAL_EU_STEPS_2035")],
          2050: coal[("CostaRica", "WEO2025_COAL_EU_STEPS_2050")]}
    jp = {2024: coal[("Ecuador", "WEO2025_STEAM_COAL_JAPAN_HIST_2024")],
          2035: coal[("Ecuador", "WEO2025_STEAM_COAL_JAPAN_STEPS_2035")],
          2050: coal[("Ecuador", "WEO2025_STEAM_COAL_JAPAN_STEPS_2050")]}
    d6_count = 0
    for k, r in rows.items():
        if k[0] == "Ecuador" and k[2] == "DIST_COA" and k[3] == "VariableCost" and r["fuel_scenario"] == "STEPS" \
                and r["basis_class"] == "projected" and r["year"] > 2024:
            fac = (lin(eu, r["year"]) / eu[2024]) / (lin(jp, r["year"]) / jp[2024])
            r["value"] = r["value"] * fac
            r["rules"].append(f"D6 x [EU(y)/EU(2024)]/[JP(y)/JP(2024)] = {fac:.6f} (WEO 2025 Table 2.3 STEPS, "
                              f"linear between 2024, 2035, 2050)")
            r["source_ids"] = r["source_ids"] + ";CRC-005"
            r["_d6_changed"] = True
            d6_count += 1

    # ---- C2: locate cells in the workbooks
    write, unplaced, skipped = [], [], Counter()
    wb_cache = {}
    for c in MODEL:
        path = ROOT / MODEL[c] / "A1_Outputs" / "A-O_Parametrization.xlsx"
        wbf = openpyxl.load_workbook(path, data_only=False)
        wbv = openpyxl.load_workbook(path, data_only=True)
        info = {}
        for sh in SHEETS:
            ws, wv = wbf[sh], wbv[sh]
            hdr = {ws.cell(1, j).value: j for j in range(1, ws.max_column + 1)}
            years = {}
            for name, j in hdr.items():
                if isinstance(name, int):
                    years[name] = j
                elif isinstance(name, str) and name.strip().isdigit() and len(name.strip()) == 4:
                    years[int(name.strip())] = j
            idx = defaultdict(list)
            for i in range(2, ws.max_row + 1):
                t, p = ws.cell(i, hdr["Tech"]).value, ws.cell(i, hdr["Parameter"]).value
                if t is None or p is None:
                    continue
                idx[(str(t).strip(), str(p).strip())].append(i)
            info[sh] = dict(ws=ws, wv=wv, hdr=hdr, years=years, idx=idx)
        wb_cache[c] = (path, info)

    def locate(r):
        path, info = wb_cache[r["country"]]
        sh = info.get(r["sheet"])
        if sh is None:
            return None, "sheet not in workbook"
        cand = sh["idx"].get((r["tech"], r["parameter"]), [])
        if not cand:
            return None, "no row with this Tech and Parameter in the sheet"
        if len(cand) > 1:
            cand2 = [i for i in cand if str(sh["ws"].cell(i, sh["hdr"]["Tech.ID"]).value).strip() == str(r["tech_id"]).strip()]
            if len(cand2) != 1:
                return None, f"{len(cand)} rows with this Tech and Parameter"
            cand = cand2
        col = sh["years"].get(r["year"])
        if col is None:
            return None, f"year column {r['year']} not in the sheet"
        return (cand[0], col, sh), ""

    # D4 needs DIST paths after writes
    def final_value(c, sheet, tech, param, year):
        r = rows.get((c, sheet, tech, param, year))
        loc, why = locate(dict(country=c, sheet=sheet, tech=tech, parameter=param, year=year, tech_id=""))
        if loc is None:
            return None, why
        i, col, sh = loc
        cur = sh["wv"].cell(i, col).value
        if r is not None and r["value"] is not None and not (r["change_class"] == "keep" and not r.get("_d3_changed")
                                                             and not r.get("_d6_changed")):
            return r["value"], "written"
        return f(cur), "workbook"

    d4 = []
    for src_t, dst_t in (("DIST_CRU", "EXTT_CRU"), ("DIST_COA", "PRO_COA")):
        c = "DominicanRepublic"
        path, info = wb_cache[c]
        dst_sheet = None
        for sh in SHEETS:
            if info[sh]["idx"].get((dst_t, "VariableCost")):
                dst_sheet = sh
        src_sheet = next(sh for sh in SHEETS if info[sh]["idx"].get((src_t, "VariableCost")))
        tech_id = info[dst_sheet]["ws"].cell(info[dst_sheet]["idx"][(dst_t, "VariableCost")][0],
                                             info[dst_sheet]["hdr"]["Tech.ID"]).value
        for y in sorted(info[dst_sheet]["years"]):
            v, how = final_value(c, src_sheet, src_t, "VariableCost", y)
            srow = rows.get((c, src_sheet, src_t, "VariableCost", y))
            k = (c, dst_sheet, dst_t, "VariableCost", y)
            assert k not in rows
            rows[k] = dict(country=c, sheet=dst_sheet, tech_id=str(tech_id), tech=dst_t, parameter="VariableCost",
                           year=y, fuel_scenario="STEPS" if (srow and srow["fuel_scenario"] == "STEPS") else "ALL",
                           change_class="D4", basis_class="D4", proposed=None, value=v,
                           source_ids=(srow["source_ids"] if srow else ""), derivation=f"D4: {src_t} VariableCost {y} "
                           f"({how}) = {v}", assumption="", unit="MUSD/PJ (USD/GJ)", origin="D4",
                           rules=[f"D4 = {src_t} VariableCost {y} ({how})"], currency_note="")
            d4.append(rows[k])

    # build the write list
    skipped_keep = {}
    for k, r in sorted(rows.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2], kv[0][3], kv[0][4])):
        c = r["country"]
        if c == "Ecuador" and r["tech"] in ("PPGEO", "PPPVDS"):
            skipped["D5 Ecuador PPGEO/PPPVDS"] += 1
            continue
        if c == "Honduras" and r["tech"] == "IMP_ELE" and r["year"] >= 2025:
            skipped["D10 Honduras IMP_ELE 2025+"] += 1
            continue
        if r["value"] is None:
            skipped["no proposed value (cell stays as is)"] += 1
            continue
        if r["change_class"] == "keep" and not r.get("_d3_changed") and not r.get("_d6_changed"):
            skipped["keep, unchanged by D3/D6"] += 1
            skipped_keep[k] = r
            continue
        loc, why = locate(r)
        if loc is None:
            unplaced.append(dict(country=c, sheet=r["sheet"], tech=r["tech"], parameter=r["parameter"],
                                 year=r["year"], value=r["value"], rule=" | ".join(r["rules"]), reason=why))
            continue
        i, col, sh = loc
        raw = sh["ws"].cell(i, col).value
        cached = sh["wv"].cell(i, col).value
        mode = sh["ws"].cell(i, sh["hdr"]["Projection.Mode"]).value
        main_rule = r["origin"]
        if r.get("_d3_changed"):
            main_rule += "+D3"
        if r.get("_d6_changed"):
            main_rule += "+D6"
        write.append(dict(country=c, sheet=r["sheet"], tech_id=r["tech_id"], tech=r["tech"],
                          tech_name=sh["ws"].cell(i, sh["hdr"]["Tech.Name"]).value,
                          parameter=r["parameter"], unit=sh["ws"].cell(i, sh["hdr"]["Unit"]).value,
                          year=r["year"], row_index=i, column=openpyxl.utils.get_column_letter(col),
                          current_value=cached, current_raw=raw,
                          current_is_formula=isinstance(raw, str) and raw.startswith("="),
                          value_to_write=r["value"], proposed_value=r["proposed"], rule=main_rule,
                          rule_detail=" | ".join(r["rules"]), change_class=r["change_class"],
                          fuel_scenario=r["fuel_scenario"], source_ids=r["source_ids"],
                          projection_mode_current=mode, assumption=r.get("assumption", ""),
                          derivation=r.get("derivation", "")))

    # D8 per workbook row
    by_row = defaultdict(list)
    for w in write:
        by_row[(w["country"], w["sheet"], w["row_index"])].append(w)
    d8 = {}
    fills = []

    def _norm(v):
        if v is None:
            return None
        try:
            v = float(v)
        except (TypeError, ValueError):
            return str(v)
        return round(v, 9) if v == v else None

    for key, ws_ in by_row.items():
        mode = (ws_[0]["projection_mode_current"] or "").strip()
        vals = [w["value_to_write"] for w in ws_]
        # D8 reads "written values" as the row as it stands after the write: written cells plus the
        # cells left as they are (A2's Flat mode copies the first year column to every year)
        c0, sheet0, ri = key
        sh0 = wb_cache[c0][1][sheet0]
        written_by_year = {w["year"]: w["value_to_write"] for w in ws_}
        row_after = [written_by_year.get(y, sh0["wv"].cell(ri, col).value) for y, col in sorted(sh0["years"].items())]
        varies = len({_norm(v) for v in row_after}) > 1
        for w in ws_:
            w["row_after_varies"] = varies
        nonzero = any(abs(v) > 0 for v in vals)
        new = ""
        why = ""
        if ws_[0]["tech"] in ("EXTT_CRU", "PRO_COA") and ws_[0]["country"] == "DominicanRepublic":
            if mode != "User defined":
                new, why = "User defined", "D4"
        if not new and varies and mode != "User defined":
            new, why = "User defined", "D8 values vary by year"
        if not new and mode in ("Zero", "EMPTY") and nonzero:
            new, why = "User defined", f"D8 {mode} row receives a non-zero value"
        d8[key] = (new, why)
        for w in ws_:
            w["projection_mode_new"] = new
            w["projection_mode_reason"] = why
        # D8 fill: a row switched to User defined must keep a value in every year column, or A2
        # compiles the empty years as missing; an empty unwritten cell gets its keep proposal value
        # (which equals what the old mode produced), so those years compile as before
        if new:
            w0 = ws_[0]
            for y, col in sorted(sh0["years"].items()):
                if y in written_by_year or sh0["wv"].cell(ri, col).value is not None:
                    continue
                kr = skipped_keep.get((c0, sheet0, w0["tech"], w0["parameter"], y))
                if kr is None:
                    unplaced.append(dict(country=c0, sheet=sheet0, tech=w0["tech"], parameter=w0["parameter"],
                                         year=y, value="", rule="D8 fill",
                                         reason="row switched to User defined has an empty year cell with no "
                                                "keep proposal; left empty"))
                    continue
                fill = dict(w0)
                fill.update(year=y, column=openpyxl.utils.get_column_letter(col), current_value=None,
                            current_raw=None, current_is_formula=False, value_to_write=kr["value"],
                            proposed_value=kr["proposed"], rule="proposals_all keep+D8 fill",
                            rule_detail=f"proposals_all {kr['fuel_scenario']} (keep) | D8 fill: empty cell of a row "
                                        f"switched to User defined; keep value equals what {mode} produced",
                            change_class="keep", fuel_scenario=kr["fuel_scenario"], source_ids=kr["source_ids"],
                            projection_mode_new=new, projection_mode_reason=why, assumption=kr.get("assumption", ""),
                            derivation=kr.get("derivation", ""))
                fills.append(fill)
                skipped["keep, unchanged by D3/D6"] -= 1

    write.extend(fills)
    write.sort(key=lambda w: (w["country"], w["sheet"], w["row_index"], w["year"]))
    print("D8 fill cells:", len(fills))
    gen = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # outputs
    wfields = ["country", "sheet", "tech_id", "tech", "tech_name", "parameter", "unit", "year", "row_index", "column",
               "current_value", "current_raw", "current_is_formula", "value_to_write", "proposed_value", "rule",
               "rule_detail", "change_class", "fuel_scenario", "source_ids", "projection_mode_current",
               "projection_mode_new", "projection_mode_reason"]
    with open(JOB / "write_set.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=wfields, extrasaction="ignore", lineterminator="\n")
        wr.writeheader()
        for w in write:
            o = dict(w)
            o["value_to_write"] = repr(float(w["value_to_write"]))
            wr.writerow(o)
    with open(JOB / "unplaced.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=["country", "sheet", "tech", "parameter", "year", "value", "rule", "reason"],
                            lineterminator="\n")
        wr.writeheader()
        for u in unplaced:
            wr.writerow(u)
    # manifests
    for c in MODEL:
        rows_c = [w for w in write if w["country"] == c]
        with open(JOB / f"manifest_{c}.csv", "w", newline="", encoding="utf-8") as fh:
            wr = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
            wr.writeheader()
            for n, w in enumerate(rows_c, 1):
                raw = w["current_raw"]
                wr.writerow(dict(
                    manifest_id=f"{c}-{n:05d}", approved="YES", decision="APPLY", country=c, model_label=MODEL[c],
                    ao_path=f"{MODEL[c]}/A1_Outputs/A-O_Parametrization.xlsx", sheet=w["sheet"],
                    row_index=w["row_index"], tech=w["tech"], tech_name=w["tech_name"] or "",
                    parameter=w["parameter"], unit=w["unit"] or "", year=w["year"],
                    old_value="" if raw is None else (raw if isinstance(raw, str) else repr(raw)),
                    new_value=repr(float(w["value_to_write"])), source_kind="LAC_OVERNIGHT_COST_RUN write_set",
                    source_path=f"_LAC_HUB/cost_write_run_{STAMP}/write_set.csv", source_sheet="",
                    source_row_index="", source_tech="", source_tech_name="", source_unit="",
                    source_projection_mode="", fuel_code="", scenario=w["fuel_scenario"], score="",
                    reason=w["rule_detail"][:500], row_fingerprint=f"{w['tech']}|{w['parameter']}",
                    projection_mode_old=w["projection_mode_current"] or "",
                    projection_mode_new=w["projection_mode_new"], unit_conversion="", generated_at=gen))
    # currency_conversion.csv: one line per non-fuel group
    cc = []
    for g, rs in sorted(group_info.items()):
        stat = Counter(r["_d3_status"] for r in rs)
        conv = sorted({r["_d3_status"] for r in rs if r["_d3_status"].startswith("converted")})
        years_stated = sorted({str(r["_d3_year"]) for r in rs if r["_d3_year"]})
        where = "; ".join(sorted({f"{r['_d3_how']}: {str(r['_d3_ev'])[:120]}" for r in rs
                                  if r["_d3_how"] not in ("zero",) and r["value"] is not None}))[:600]
        fac = "; ".join(f"{s.split(' x ')[1]} ({sum(1 for r in rs if r['_d3_status'] == s)} years)" for s in conv)
        left = "; ".join(f"{s} ({n} years)" for s, n in stat.items() if not s.startswith("converted"))
        cc.append(dict(country=g[0], tech=g[1], parameter=g[2], stated_year=",".join(years_stated),
                       where_stated=where, factor=fac, left=left,
                       keep_rows=sum(1 for r in rs if r["change_class"] == "keep")))
    for g in sorted(reg_groups):
        cc.append(dict(country=g[0], tech=g[1], parameter=g[2], stated_year="2024",
                       where_stated="regional_proposals.csv (values in real 2024 USD)" +
                       ("; D2 ICE PEG 2024-2040 Dec-2023 USD x CPI-U 2024/2023" if g == ("CostaRica", "PWRHYDDAM", "CapitalCost") else ""),
                       factor="", left="left: from regional_proposals.csv or D2 (not a D3 group)", keep_rows=""))
    with open(JOB / "currency_conversion.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=["country", "tech", "parameter", "stated_year", "where_stated", "factor",
                                            "left", "keep_rows"], lineterminator="\n")
        wr.writeheader()
        for x in cc:
            wr.writerow(x)

    # counts
    cnt = Counter((w["country"], w["rule"]) for w in write)
    print("regional cells applied:", n_reg, "D2 factor", d2_factor, "R2024", r_2024, "R2023", r_2023)
    print("D6 rows:", d6_count, "D4 rows:", len(d4))
    print("write rows:", len(write), "unplaced:", len(unplaced), "skipped:", dict(skipped))
    for (c, rule), n in sorted(cnt.items()):
        print(f"  {c:18s} {rule:28s} {n}")
    print("formula cells overwritten:", sum(1 for w in write if w["current_is_formula"]))
    print("rows switched to User defined:", Counter(v[1] for v in d8.values() if v[0]))
    with open(JOB / "write_set_counts.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh, lineterminator="\n")
        wr.writerow(["country", "rule", "cells_in_write_set", "cells_changing"])
        for (c, rule), n in sorted(cnt.items()):
            ch = sum(1 for w in write if w["country"] == c and w["rule"] == rule and not (
                w["current_value"] is not None and isinstance(w["current_value"], (int, float))
                and abs(float(w["current_value"]) - w["value_to_write"]) <= 1e-9 * max(1, abs(w["value_to_write"]))
                and not w["current_is_formula"]))
            wr.writerow([c, rule, n, ch])
        for s, n in skipped.items():
            wr.writerow(["(all)", f"skipped: {s}", n, 0])


if __name__ == "__main__":
    main()
