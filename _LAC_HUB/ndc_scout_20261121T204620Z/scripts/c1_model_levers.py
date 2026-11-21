"""Step C1 of LAC_NDC_SCOUT: model levers and solved quantities, read-only at 481a7c0.

Usage: python -I c1_model_levers.py <model_root> <job_folder>
Writes model_levers_<country>.csv into the job folder.
Part "input_difference": every compiled-input row (parameter, key) whose value differs
between BAU and NDCNEW or LTSNEW in any year from 2025 (abs tol 0.00005 and rel tol 0.01 percent).
Part "solved": solved quantities per scenario from _STAGE3_RESULTS/stage3_results.xlsx.
"""
import os
import re
import sys
import glob
import pandas as pd

MODEL = sys.argv[1]
JOB = sys.argv[2]
YEARS = [2025, 2030, 2035, 2040, 2050]
SCEN = ["BAU", "NDCNEW", "LTSNEW"]
ABS_TOL = 0.00005
REL_TOL = 0.0001  # 0.01 percent

COUNTRIES = {
    "CostaRica": ("CR", "CostaRica/CR_ENERGY/t1_confection"),
    "DominicanRepublic": ("DR", "DominicanRepublic/RD_ENERGY"),
    "Ecuador": ("ECU", "Ecuador/ECU_Energy"),
    "Guatemala": ("GUA", "Guatemala/GUA_ENERGY"),
    "Honduras": ("HON", "Honduras/HON_ENERGY"),
    "Jamaica": ("JAM", "Jamaica/JAM_ENERGY"),
}

KNOWN_EAR = {
    "DominicanRepublic": {"PPCOA", "PPCCTNGS", "PPCCTNGSDSL", "PPICEGASFOI", "PPICEFOI", "PPCCTDSL"},
    "Ecuador": {"PPNGS", "PPRNGS", "PPDSL", "PPRDSL", "PPCRU", "PPFOI"},
    "Honduras": {"PPICEDSL", "PPGTDSL", "PPCOK", "PPGTGLP", "PPBIM", "PPFOI"},
}

KEYCOLS = ["PARAMETER", "REGION", "TECHNOLOGY", "FUEL", "EMISSION", "MODE_OF_OPERATION",
           "TIMESLICE", "SEASON", "DAYTYPE", "DAILYTIMEBRACKET", "STORAGE"]

RE_TOKENS = ["HYD", "HD", "HDAM", "HROR", "PV", "WND", "GEO", "BIM", "BMS", "BGS", "DBIM", "DBGS"]


def is_plant(t):
    return bool(re.match(r"^(PP|PWR)", str(t)))


def is_renewable(t):
    """Plant types counted as renewable: hydro, solar PV, wind, geothermal, biomass, biogas."""
    s = re.sub(r"^(PP|PWR)", "", str(t))
    return bool(re.search(r"(HYD|^HD|^IHD|HDAM|HROR|HRO|PV|WND|WN|GEO|BIM|BMS|BGS)", s))


def is_transport(t):
    t = str(t)
    return bool(re.match(r"^(TR|Techs_|T4)", t))


def group_of(param, tech, fuel, emission):
    tech = str(tech) if pd.notna(tech) else ""
    fuel = str(fuel) if pd.notna(fuel) else ""
    if param in ("SpecifiedAnnualDemand", "SpecifiedDemandProfile", "AccumulatedAnnualDemand"):
        return "demand per fuel"
    if param == "EmissionActivityRatio":
        return "fuel emission factors"
    if tech.upper().startswith("IMP") or tech in ("IMP_ELE", "IMPELE"):
        return "imports"
    if re.match(r"^ELE_(DIST|TRANS|TRANS2|DTR|TRN)$", tech) and param in ("InputActivityRatio", "OutputActivityRatio"):
        return "grid losses"
    if is_plant(tech) and param.startswith(("TotalTechnologyAnnualActivity", "TotalAnnualMax", "TotalAnnualMin",
                                             "TotalTechnologyModelPeriod", "ResidualCapacity")):
        return "plant limits"
    if is_transport(tech) and param.startswith(("TotalTechnologyAnnualActivity", "TotalAnnualMax", "TotalAnnualMin",
                                                 "TotalTechnologyModelPeriod")):
        return "transport limits"
    return "other"


def known_unintended(country, param, tech):
    tech = str(tech)
    if country == "Guatemala" and tech == "IMP_ELE" and param == "TotalTechnologyAnnualActivityLowerLimit":
        return "known unintended difference (Guatemala IMP_ELE lower limit)"
    if country == "Honduras" and tech == "IMP_ELE" and param == "TotalTechnologyAnnualActivityUpperLimit":
        return "known unintended difference (Honduras IMP_ELE upper limit)"
    if param == "EmissionActivityRatio" and tech in KNOWN_EAR.get(country, set()):
        return "known unintended difference (EmissionActivityRatio of plant from 2025)"
    return ""


def read_param(folder, scen, fname):
    f = os.path.join(folder, scen, fname)
    if not os.path.exists(f):
        return None
    d = pd.read_csv(f, dtype=str, keep_default_na=False)
    if d.empty:
        return d
    d["Value"] = pd.to_numeric(d["Value"], errors="coerce")
    d["YEAR"] = pd.to_numeric(d["YEAR"], errors="coerce").fillna(9999)  # 9999 = parameter without a year
    return d


def differs(a, b):
    if pd.isna(a) and pd.isna(b):
        return False
    if pd.isna(a) or pd.isna(b):
        return True
    diff = abs(a - b)
    return diff > ABS_TOL and diff > REL_TOL * max(abs(a), abs(b))


def input_differences(country, folder):
    rows = []
    files = sorted(set(os.path.basename(p) for s in SCEN for p in glob.glob(os.path.join(folder, s, "*.csv"))))
    for fname in files:
        frames = {s: read_param(folder, s, fname) for s in SCEN}
        cols = None
        for s in SCEN:
            if frames[s] is not None and not frames[s].empty:
                cols = [c for c in KEYCOLS if c in frames[s].columns]
                break
        if cols is None:
            continue
        piv = {}
        for s in SCEN:
            d = frames[s]
            if d is None or d.empty:
                piv[s] = pd.Series(dtype=float)
                continue
            piv[s] = d.groupby(cols + ["YEAR"])["Value"].sum()
        allidx = piv["BAU"].index.union(piv["NDCNEW"].index).union(piv["LTSNEW"].index)
        if len(allidx):
            allidx = pd.MultiIndex.from_tuples(list(allidx), names=cols + ["YEAR"])
        if len(allidx) == 0:
            continue
        table = pd.DataFrame({s: piv[s].reindex(allidx) for s in SCEN})
        table = table.reset_index()
        later = table[table["YEAR"] >= 2025]
        flag = later.apply(lambda r: differs(r["BAU"], r["NDCNEW"]) or differs(r["BAU"], r["LTSNEW"]), axis=1) if len(later) else pd.Series(dtype=bool)
        if flag.empty or not flag.any():
            continue
        keys_diff = later[flag][cols].drop_duplicates()
        for _, k in keys_diff.iterrows():
            sub = table
            for c in cols:
                sub = sub[sub[c] == k[c]]
            sub = sub.set_index("YEAR")
            sl = sub[sub.index >= 2025]
            dif_years = [int(y) for y, r in sl.iterrows() if differs(r["BAU"], r["NDCNEW"]) or differs(r["BAU"], r["LTSNEW"])]
            param = k["PARAMETER"]
            tech = k.get("TECHNOLOGY", "")
            rec = {
                "part": "input_difference",
                "group": group_of(param, tech, k.get("FUEL", ""), k.get("EMISSION", "")),
                "quantity": param,
                "technology": tech,
                "fuel": k.get("FUEL", ""),
                "emission": k.get("EMISSION", ""),
                "mode": k.get("MODE_OF_OPERATION", ""),
                "timeslice": k.get("TIMESLICE", ""),
                "unit": "model input unit",
                "first_diff_year_from_2025": min(dif_years) if dif_years else "",
                "last_diff_year": max(dif_years) if dif_years else "",
                "n_diff_years": len(dif_years),
            }
            for s in SCEN:
                for y in YEARS:
                    v = sub[s].get(y) if y in sub.index else None
                    rec[f"{s}_{y}"] = "" if v is None or pd.isna(v) else round(float(v), 6)
            rec["note"] = known_unintended(country, param, tech)
            rows.append(rec)
    return rows


def fuel_code(f):
    f = str(f)
    m = re.match(r"^E4(.+?)_(.+)$", f)
    if m:
        return m.group(1)
    codes = ["PURDSL", "PURGSL", "Flex_Fuel", "CEM_PROD", "LUBRI", "LIME", "R125", "R134A", "R143A", "R227EA", "R236FA",
             "R32", "ELE", "DSL", "GSL", "LPG", "FOI", "NGS", "COA", "COK", "BIM", "BMS", "FIR", "KER", "JET", "JTF",
             "AVG", "KJF", "HYD", "BGS", "CRU", "OPE", "OID", "OTP", "RDF", "IWA", "SUG", "CHA", "WAS", "PV", "HOU"]
    body = f[2:] if f.startswith("E5") else f
    for c in codes:
        if body.endswith(c):
            return c
    return body


def solved(country, s3):
    rows = []

    def add(quantity, key, unit, values, note=""):
        rec = {"part": "solved", "group": "", "quantity": quantity, "technology": key, "fuel": "", "emission": "",
               "mode": "", "timeslice": "", "unit": unit, "first_diff_year_from_2025": "", "last_diff_year": "",
               "n_diff_years": ""}
        for s in SCEN:
            for y in YEARS:
                v = values.get((s, y))
                rec[f"{s}_{y}"] = "" if v is None or pd.isna(v) else round(float(v), 6)
        rec["note"] = note
        rows.append(rec)

    def series(df, mask, col="Value"):
        d = df[mask & df["Year"].isin(YEARS)]
        return d.groupby(["Scenario", "Year"])[col].sum().to_dict()

    p = s3["ProductionByTechnologyAnnual"]
    p = p[p["Country"] == country]
    pp = p[p["Technology"].map(is_plant) & p["Fuel"].astype(str).str.contains("ELE")]
    for t in sorted(pp["Technology"].unique()):
        add("generation by plant type", t, "PJ", series(pp, pp["Technology"] == t),
            "renewable" if is_renewable(t) else "non-renewable")
    tot = series(pp, pp["Technology"].notna())
    ren = series(pp, pp["Technology"].map(is_renewable))
    add("generation total (all PP/PWR)", "ALL", "PJ", tot)
    add("generation renewable", "RENEWABLE", "PJ", ren,
        "renewable = hydro, solar PV, wind, geothermal, biomass, biogas plant types")
    share = {k: (ren.get(k, 0.0) / v if v else None) for k, v in tot.items()}
    add("renewable share of generation", "RENEWABLE/ALL", "fraction", share,
        "renewable types: " + " ".join(sorted(t for t in pp["Technology"].unique() if is_renewable(t))))

    c = s3["TotalCapacityAnnual"]
    c = c[(c["Country"] == country) & c["Technology"].map(is_plant)]
    for t in sorted(c["Technology"].unique()):
        add("installed capacity by plant type", t, "GW", series(c, c["Technology"] == t),
            "renewable" if is_renewable(t) else "non-renewable")

    fin = p[p["Fuel"].astype(str).str.match(r"^(E4|E5)") & ~p["Fuel"].astype(str).str.match(r"^E5TR(N|A|B|M|S|T|Y|X)")]
    fin = fin[~fin["Technology"].astype(str).str.match(r"^(TR|Techs_)")]
    fin = fin.assign(code=fin["Fuel"].map(fuel_code))
    for code in sorted(fin["code"].unique()):
        add("final energy delivered per fuel", code, "PJ", series(fin, fin["code"] == code),
            "sum of production of E4 and E5 fuels (end-use delivery, incl. transport fuel delivery and exports where modelled as E5EXP)")

    tr = p[p["Technology"].astype(str).str.match(r"^(TR|TRN)") & p["Fuel"].astype(str).str.match(r"^E5TR")]
    for g in sorted(tr["Fuel"].unique()):
        sub = tr[tr["Fuel"] == g]
        tot_g = series(sub, sub["Technology"].notna())
        ele_g = series(sub, sub["Technology"].astype(str).str.endswith("ELE"))
        add("electric share of transport group", g, "fraction of group output",
            {k: (ele_g.get(k, 0.0) / v if v else None) for k, v in tot_g.items()},
            "electric techs: " + " ".join(sorted(t for t in sub["Technology"].unique() if str(t).endswith("ELE"))))
    fb = p[p["Fuel"].astype(str).str.match(r"^E5(TRO|ALLTRN)")]
    for prefix in ["E5TRO", "E5ALLTRN"]:
        sub = fb[fb["Fuel"].astype(str).str.startswith(prefix)]
        if sub.empty:
            continue
        tot_g = series(sub, sub["Fuel"].notna())
        ele_g = series(sub, sub["Fuel"].astype(str).str.endswith("ELE"))
        add("electric share of transport group (fuel-based)", prefix + "*", "fraction of energy delivered",
            {k: (ele_g.get(k, 0.0) / v if v else None) for k, v in tot_g.items()},
            "electricity share of final energy delivered to this transport fuel group")

    a = s3["TotalTechnologyAnnualActivity"]
    a = a[a["Country"] == country]
    for t in sorted(set(a["Technology"]) & {"IMP_ELE", "IMPELE"}):
        add("electricity imports", t, "PJ", series(a, a["Technology"] == t))
    for t in sorted(t for t in set(a["Technology"]) if re.match(r"^T5ELEEXP$", str(t))):
        add("electricity exports", t, "PJ", series(a, a["Technology"] == t))

    e = s3["AnnualEmissions"]
    e = e[e["Country"] == country]
    for lab in sorted(e["Emission"].unique()):
        add("emissions by label", lab, "model unit of label", series(e, e["Emission"] == lab),
            "never summed across labels")
    return rows


def main():
    s3 = pd.read_excel(os.path.join(MODEL, "_STAGE3_RESULTS", "stage3_results.xlsx"), sheet_name=None)
    for country, (code, rel) in COUNTRIES.items():
        folder = os.path.join(MODEL, rel, "B1_Output_Params")
        rows = input_differences(country, folder) + solved(country, s3)
        out = pd.DataFrame(rows)
        out.insert(0, "country", country)
        fn = os.path.join(JOB, f"model_levers_{code}.csv")
        out.to_csv(fn, index=False, lineterminator="\n")
        print(country, len(out), "rows;", out[out.part == "input_difference"].groupby("group").size().to_dict())


if __name__ == "__main__":
    main()
