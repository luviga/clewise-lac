"""Step 3.3 and 3.4: fuel_coverage.csv (country x fuel x scenario x year range, plus what the A-O
fuel supply rows need) and fuel_sources.csv (source class per anchor, with value counts).

Classes:
  R        external, retrievable from the reference given (a dated document whose description states the value)
  NR       external, not retrievable from the reference given (a landing page that changes, or the value is an
           estimate or derivation that the cited source does not state)
  INTERNAL internal file, sheet, chat or note
  NONE     no source and no ASSUMPTION label
Classification is made by reading the workbook's own descriptions only; no web page was opened.
Usage: py -I build_coverage_sources.py <output folder>
"""
import importlib.util
import os
import sys

import pandas as pd

ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
OUT = sys.argv[1]
WB = os.path.join(ROOT, "LAC_Fuel_Price_Projections_2026_v2_audit.xlsx")

# Load the tool's own mapping functions (module definitions only; main() is not called).
spec = importlib.util.spec_from_file_location("tool", os.path.join(ROOT, "ao_cost_repair_manager.py"))
tool = importlib.util.module_from_spec(spec)
sys.modules["tool"] = tool
spec.loader.exec_module(tool)

v = pd.read_excel(WB, sheet_name="OSeMOSYS_VarCost", header=3)
YEARS = [str(y) for y in range(2018, 2051)]
v["xl_row"] = v.index + 5


def yr(r):
    ys = [int(y) for y in YEARS if isinstance(r[y], (int, float)) and not pd.isna(r[y])]
    return (f"{min(ys)}-{max(ys)}", len(ys)) if ys else ("", 0)


ISO = {"CostaRica": "CRI", "DominicanRepublic": "DOM", "Ecuador": "ECU",
       "Guatemala": "GTM", "Honduras": "HND", "Jamaica": "JAM"}
ao = pd.read_csv(os.path.join(OUT, "ao_varcost_rows.csv"))
fs = ao[ao.tech.str.upper().str.startswith(("DIST_", "IMP"))].copy()
fs["tech_name"] = fs["tech_name"].fillna("")


def code_of(r):
    row = tool.AoCostRow(r.country, "", "", "", "", r.sheet, 0, r.tech, r.tech_name,
                         "VariableCost", "", "", {}, ())
    return tool.detect_fuel_code(row)


def targeted(r):
    row = tool.AoCostRow(r.country, "", "", "", "", r.sheet, 0, r.tech, r.tech_name,
                         "VariableCost", "", "", {}, ())
    return "YES" if tool.is_fuel_cost_target(row) else "NO"


fs["tool_fuel_code"] = fs.apply(code_of, axis=1)
fs["tool_targets_row"] = fs.apply(targeted, axis=1)
fs[["country", "sheet", "row", "tech", "tech_name", "tool_fuel_code", "tool_targets_row"]].to_csv(
    os.path.join(OUT, "ao_fuel_supply_mapping.csv"), index=False)

rows = []
codes = sorted(set(v["Fuel Code"].dropna()))
for country, iso in list(ISO.items()) + [("WORLD", "WORLD")]:
    need = fs[fs.country == country] if country != "WORLD" else fs[fs.tool_fuel_code.isin(["COA", "CRD"])]
    for code in codes + ["(no code)"]:
        rec = {"country": country, "iso": iso, "fuel_code": code}
        sub = v[(v.ISO == iso) & (v["Fuel Code"] == code)]
        for scen in ("REF", "HIGH", "LOW"):
            s = sub[sub.Scenario == scen]
            rec[f"{scen}_years"], rec[f"{scen}_n_values"] = yr(s.iloc[0]) if len(s) else ("", 0)
            rec[f"{scen}_xl_row"] = int(s.xl_row.iloc[0]) if len(s) else ""
        n = need[need.tool_fuel_code == ("" if code == "(no code)" else code)]
        rec["ao_fuel_supply_rows_needing_it"] = " ".join(
            (f"{cc}:" if country == "WORLD" else "") + t for cc, t in zip(n.country, n.tech))
        if code == "(no code)":
            if not len(n):
                continue
            rec["status"] = "A-O rows the tool cannot map to any workbook fuel (left unpriced)"
        elif len(n) and len(sub):
            rec["status"] = "needed and covered"
        elif len(n) and code in ("COA", "CRD"):
            rec["status"] = "needed; covered only by the WORLD benchmark (tool fallback, ao_cost_repair_manager.py:953-956)"
        elif len(n):
            rec["status"] = "NEEDED BUT MISSING in workbook"
        elif len(sub):
            rec["status"] = "in workbook, not used by any A-O fuel supply row"
        else:
            continue
        rows.append(rec)
pd.DataFrame(rows).to_csv(os.path.join(OUT, "fuel_coverage.csv"), index=False)

# ---------------- sources ----------------
CA = {  # Anchors_Countries row -> (iso, code, source_id, class, reason)
    5: ("HND", "GSL", "S013", "NR", "derived from the super price with an assumed HNL 2.10/L spread; S013 gives super only"),
    6: ("HND", "GSP", "S013", "NR", "GlobalPetrolPrices country page shows the current price; the 20 Apr 2026 value is not fixed at that URL"),
    7: ("HND", "DSL", "S014", "NR", "April estimate (+22% on a March quote); value not stated by any source"),
    8: ("HND", "LPG", "S013", "NR", "estimate from regional refinery economics; S013 is a gasoline page"),
    9: ("HND", "KRS", "S013", "NR", "estimate from a diesel-kerosene spread"),
    10: ("HND", "JTA", "S013", "NR", "estimate from a jet netback"),
    11: ("HND", "HFO", "S013", "NR", "estimate from Brent minus an assumed HFO discount"),
    12: ("CRI", "GSL", "S016", "R", "Tico Times article dated 1 May 2026 states CRC 748/L"),
    13: ("CRI", "GSP", "S016", "R", "Tico Times article dated 1 May 2026 states CRC 733/L"),
    14: ("CRI", "DSL", "S015/S016", "NR", "midpoint of a range built from two sources; CRC 626/L is stated by neither"),
    15: ("CRI", "LPG", "S016", "NR", "estimate from a cylinder price and an assumed density; not in the S016 description"),
    16: ("CRI", "KRS", "S015", "NR", "estimate: diesel minus CRC 100/L"),
    17: ("CRI", "JTA", "S015", "NR", "estimate: about 10% below retail diesel"),
    18: ("CRI", "HFO", "S015", "NR", "estimate from an international HFO netback"),
    19: ("JAM", "GSL", "S017", "R", "Petrojam dated price page states JMD 190.13/L"),
    20: ("JAM", "GSP", "S017", "R", "Petrojam dated price page states JMD 197.58/L"),
    21: ("JAM", "DSL", "S017", "R", "Petrojam dated price page states JMD 197.75/L"),
    22: ("JAM", "LPG", "S017", "NR", "anchor 0.59 USD/L does not equal the published propane JMD 82.28/L / 157 = 0.52; weighting not shown"),
    23: ("JAM", "KRS", "S017", "R", "Petrojam dated price page states JMD 182.40/L"),
    24: ("JAM", "JTA", "S017", "NR", "'JMD ~141/L est'; an estimate"),
    25: ("JAM", "HFO", "S017", "R", "Petrojam dated price page states JMD 137.01/L"),
    26: ("DOM", "GSL", "S019", "R", "MICM dated resolution article states RD$301.50/gal"),
    27: ("DOM", "GSP", "S019", "R", "MICM dated resolution article states RD$323.10/gal"),
    28: ("DOM", "DSL", "S019", "R", "MICM dated resolution article states RD$253.80/gal"),
    29: ("DOM", "LPG", "S019", "R", "MICM dated resolution article states RD$137.20/gal"),
    30: ("DOM", "KRS", "S020", "R", "Diario Libre dated article states RD$364.00/gal"),
    31: ("DOM", "JTA", "S020", "R", "Diario Libre dated article states RD$321.86/gal"),
    32: ("DOM", "HFO", "S020", "R", "Diario Libre dated article states Fuel Oil #6 RD$198.42/gal"),
    33: ("ECU", "GSL", "S022", "R", "Primicias dated article states USD 3.024/gal"),
    34: ("ECU", "GSP", "S022", "R", "Primicias dated article states USD 4.57/gal"),
    35: ("ECU", "DSL", "S022", "R", "Primicias dated article states USD 2.962/gal"),
    36: ("ECU", "LPG", "S023", "NR", "cylinder-based estimate; the S023 description covers the diesel-2 subsidy, not LPG"),
    37: ("ECU", "KRS", "S022", "NR", "estimate: 'similar to Extra gasoline'"),
    38: ("ECU", "JTA", "S022", "NR", "estimate: about 3-4% over diesel"),
    39: ("ECU", "HFO", "S023", "NR", "value is an implied diesel-2 power-generation parity labelled as fuel oil; derivation not shown"),
    40: ("GTM", "GSL", "S024", "NR", "MEM weekly price landing page; the 5-11 May 2026 week is not fixed at that URL"),
    41: ("GTM", "GSP", "S024", "NR", "MEM weekly price landing page; week not fixed at that URL"),
    42: ("GTM", "DSL", "S024", "NR", "MEM weekly price landing page; week not fixed at that URL"),
    43: ("GTM", "LPG", "S024", "NR", "estimate from regional cylinder pricing"),
    44: ("GTM", "KRS", "S024", "NR", "estimate from a diesel-kerosene spread"),
    45: ("GTM", "JTA", "S024", "NR", "bulk airport price, estimated"),
    46: ("GTM", "HFO", "S024", "NR", "Brent-discounted estimate"),
    50: ("DOM", "NGS", "S019", "NR", "published RD$43.97/m3 replaced by an unsourced 'typical industrial price' of 12.20 USD/MMBtu"),
    51: ("JAM", "NGS", "S017", "NR", "estimate HH + freight + margin; S017 (Petrojam) has no LNG price"),
}

INT = {}


def put(series, year, ref, high, low, sid, reason):
    INT[(series, year)] = ({"REF": ref, "HIGH": high, "LOW": low}, sid, reason)


for y in range(2018, 2024):
    put("Brent", y, "R", "R", "R", "S029", "Energy Institute Statistical Review annual average (historical series)")
put("Brent", 2024, "NR", "NR", "NR", "S006", "EIA STEO landing page shows the latest edition, not April 2026")
put("Brent", 2025, "R", "R", "R", "S008", "World Bank press release dated 28 Apr 2026")
put("Brent", 2026, "NR", "R", "NONE", "S006/S008",
    "REF from the EIA STEO landing page; HIGH from the WB release; LOW = 96 chosen as 'transition year', not labelled ASSUMPTION")
put("Brent", 2027, "NR", "NONE", "NR", "S006", "REF/LOW from the EIA STEO landing page; HIGH = 100 'slow recovery' has no source")
put("Brent", 2030, "NONE", "NONE", "NONE", "S002/S003", "author's transition values; no source states them; not labelled ASSUMPTION")
put("Brent", 2035, "R", "R", "R", "S002/S003/S005", "IEA WEO 2025 STEPS/CPS/NZE values per the IISD table")
for y in (2040, 2045):
    put("Brent", y, "NR", "NR", "NR", "S002/S003", "described as 'path'/'interpolation'; values not stated by the source")
put("Brent", 2050, "R", "R", "R", "S002/S003/S005", "IEA WEO 2025 values per the IISD table")
for y in range(2018, 2024):
    put("HH", y, "NR", "NR", "NR", "S011", "the S011 article covers 2024-2025; earlier years are not in its description")
for y in (2024, 2025):
    put("HH", y, "R", "R", "R", "S011", "EIA Today in Energy article states the 2024 and 2025 averages")
put("HH", 2026, "NONE", "NONE", "NONE", "S012", "EIA value 3.50 adjusted by +1.00 (REF) and other amounts (HIGH/LOW) without a source")
put("HH", 2027, "R", "NONE", "NONE", "S012", "REF 4.60 stated by S012; HIGH/LOW deviations unsourced")
for y in (2030, 2035, 2040, 2045, 2050):
    put("HH", y, "NR", "NR", "NR", "S002/S003/S004", "IEA text is qualitative for Henry Hub; values not stated")
for y in (2024, 2025, 2026):
    put("Coal", y, "NR", "NR", "NR", "S008", "WB press release description gives Brent only; coal values not in it")
for y in (2030, 2035, 2040, 2045, 2050):
    put("Coal", y, "NR", "NR", "NR", "S002/S003", "'IEA paths'; values not stated")

RANK = {"NONE": 0, "INTERNAL": 1, "NR": 2, "R": 3}


def weak(*cs):
    return min(cs, key=lambda c: RANK[c])


def path_class(series, year, scen):
    if (series, year) in INT:
        return INT[(series, year)][0][scen]
    ys = sorted(y for (s, y) in INT if s == series)
    lo = max(y for y in ys if y < year)
    hi = min(y for y in ys if y > year)  # linear interpolation between the two bracketing anchors
    return weak(INT[(series, lo)][0][scen], INT[(series, hi)][0][scen])


PARAM = {"alpha": "NR", "fuel_factor": "NR", "energy_content": "R", "ng_formula": "NONE"}

srows = []
for r, (iso, code, sid, cl, why) in CA.items():
    srows.append({"item": f"Anchors_Countries!D{r}", "iso": iso, "fuel_code": code,
                  "source_id": sid, "class": cl, "reason": why})
for (s, y), (cls, sid, why) in sorted(INT.items()):
    for scen, cl in cls.items():
        srows.append({"item": f"Anchors_International {s} {y} {scen}", "iso": "WORLD",
                      "fuel_code": {"Brent": "CRD (and every country fuel via the Brent ratio)",
                                    "HH": "HH (feeds DOM/JAM NGS)", "Coal": "COA"}[s],
                      "source_id": sid, "class": cl, "reason": why})
srows += [
    {"item": "Anchors_Parameters!C6:C11 pass-through alpha (6 values)", "iso": "all", "fuel_code": "all",
     "source_id": "S034", "class": "NR",
     "reason": "S034 is described as 'Goldman Sachs / industry consensus' but its URL is a World Bank subsidy-reform page; no alpha values stated"},
    {"item": "Anchors_Parameters!C16:C22 fuel pass-through factors (7 values)", "iso": "all", "fuel_code": "all",
     "source_id": "S034", "class": "NR", "reason": "same as alpha"},
    {"item": "Anchors_Parameters!C27:C36 energy contents (10 values)", "iso": "all", "fuel_code": "all",
     "source_id": "S026", "class": "R",
     "reason": "IPCC 2006 Vol 2 gives calorific values per mass; the per-litre figures also rest on densities the workbook states without a source"},
    {"item": "Country_DOM / Country_JAM natural gas formula 0.4 + 0.6 x HH ratio", "iso": "DOM,JAM", "fuel_code": "NGS",
     "source_id": "", "class": "NONE", "reason": "coefficients 0.4 and 0.6 have no source and no ASSUMPTION label"},
    {"item": "Country_XXX floor MAX(..., 0.30 x anchor)", "iso": "all", "fuel_code": "all", "source_id": "",
     "class": "NONE", "reason": "method choice stated in README!B26; no ASSUMPTION label"},
    {"item": "Sources!A32 S028 World Bank pump prices 2018-2024", "iso": "all", "fuel_code": "all", "source_id": "S028",
     "class": "n/a",
     "reason": "listed for pre-2025 history but no cell outside Sources cites it; 2018-2025 country values are back-cast from the May 2026 anchor via the Brent ratio"},
]

anchor_by = {(iso, code): cl for (iso, code, sid, cl, why) in CA.values()}
vrows = []
for _, r in v.iterrows():
    for ys in YEARS:
        val = r[ys]
        if not isinstance(val, (int, float)) or pd.isna(val):
            continue
        y = int(ys)
        iso, code, scen = r.ISO, r["Fuel Code"], r.Scenario
        if iso == "WORLD":
            a = path_class("Brent" if code == "CRD" else "Coal", y, scen)
            chain = weak(a, PARAM["energy_content"])
        elif code == "NGS":
            a = anchor_by[(iso, code)]
            chain = weak(a, path_class("HH", y, scen), PARAM["ng_formula"], PARAM["energy_content"])
        else:
            a = anchor_by[(iso, code)]
            chain = weak(a, PARAM["alpha"], PARAM["fuel_factor"], path_class("Brent", y, scen), PARAM["energy_content"])
        vrows.append({"iso": iso, "fuel_code": code, "scenario": scen, "year": y,
                      "xl_cell": f"OSeMOSYS_VarCost!row{int(r.xl_row)}:{ys}",
                      "anchor_class": a, "chain_class": chain})
vv = pd.DataFrame(vrows)
vv.to_csv(os.path.join(OUT, "fuel_values_classified.csv"), index=False)

summary = []
for k, n in vv.groupby("anchor_class").size().items():
    summary.append({"item": "COUNT: OSeMOSYS_VarCost numeric values by class of their own anchor", "class": k,
                    "reason": f"{n} of {len(vv)}"})
for k, n in vv.groupby("chain_class").size().items():
    summary.append({"item": "COUNT: OSeMOSYS_VarCost numeric values by weakest link of the whole formula chain",
                    "class": k, "reason": f"{n} of {len(vv)}"})
for k, n in pd.Series([c[3] for c in CA.values()]).value_counts().items():
    summary.append({"item": "COUNT: Anchors_Countries anchors by class", "class": k, "reason": str(n)})
pd.concat([pd.DataFrame(srows), pd.DataFrame(summary)], ignore_index=True).to_csv(
    os.path.join(OUT, "fuel_sources.csv"), index=False)
print(pd.DataFrame(summary).to_string())
print(vv[vv.scenario == "REF"].groupby("anchor_class").size())
