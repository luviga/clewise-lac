"""Step C: units.csv, share_definitions.csv and model_comparison.csv.

Model quantities come from the solved results C:/clw_scout_model/_STAGE3_RESULTS/stage3_results.xlsx
(cached by this script in the scratchpad as pickles): generation and capacity by plant type,
emissions by label, electric share of transport groups. Renewable shares are recomputed under each
country's own definition (RENEW_DEF below, from the documents' pages).
"""
import os
import re
import sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, CODES, COUNTRY, read_csv, write_csv

S3 = "C:/clw_scout_model/_STAGE3_RESULTS/stage3_results.xlsx"
CACHE = sys.argv[1] if len(sys.argv) > 1 else JOB + "/parts"
MODEL_COUNTRY = {"CR": "CostaRica", "DR": "DominicanRepublic", "ECU": "Ecuador", "GUA": "Guatemala", "HON": "Honduras", "JAM": "Jamaica"}
YEARS = [2030, 2035, 2050]
SCEN = ["NDCNEW", "LTSNEW"]


def load(sheet):
    p = os.path.join(CACHE, f"s3_{sheet}.pkl")
    if os.path.exists(p):
        return pd.read_pickle(p)
    d = pd.read_excel(S3, sheet_name=sheet)
    d.to_pickle(p)
    return d


prod = load("ProductionByTechnologyAnnual")
cap = load("TotalCapacityAnnual")
emis = load("AnnualEmissions")

# ---------------- units ----------------
SI = "SI prefixes (BIPM SI Brochure, 9th edition)"
UNITS = [
    # unit as printed, standard unit, factor, source or note
    ("Gg CO2e", "kt CO2 eq", 1, "1 Gg = 1 kt (" + SI + ")"),
    ("Gg CO2eq", "kt CO2 eq", 1, "1 Gg = 1 kt (" + SI + ")"),
    ("Gg CO2-eq", "kt CO2 eq", 1, "1 Gg = 1 kt (" + SI + ")"),
    ("Gg CO2e (removal)", "kt CO2 eq", 1, "1 Gg = 1 kt; removals keep their sign as printed"),
    ("Gg CO2e per year", "kt CO2 eq per year", 1, "1 Gg = 1 kt (" + SI + ")"),
    ("kt CO2eq", "kt CO2 eq", 1, "same unit"),
    ("kt CO2 eq", "kt CO2 eq", 1, "same unit"),
    ("kt CO2", "kt CO2 eq", 1, "CO2 has GWP 1 in every IPCC set"),
    ("ktCO2", "kt CO2 eq", 1, "CO2 has GWP 1 in every IPCC set"),
    ("ktCO2e per year", "kt CO2 eq per year", 1, "same unit"),
    ("kt CO2e per year (upper bound)", "kt CO2 eq per year", 1, "same unit"),
    ("Mt CO2e", "kt CO2 eq", 1000, "1 Mt = 1000 kt (" + SI + ")"),
    ("MtCO2e", "kt CO2 eq", 1000, "1 Mt = 1000 kt (" + SI + ")"),
    ("Mt CO2eq", "kt CO2 eq", 1000, "1 Mt = 1000 kt (" + SI + ")"),
    ("MtCO2", "kt CO2 eq", 1000, "1 Mt = 1000 kt; CO2 has GWP 1"),
    ("MtCO2 per year", "kt CO2 eq per year", 1000, "1 Mt = 1000 kt; CO2 has GWP 1"),
    ("t CO2eq", "kt CO2 eq", 0.001, "1 t = 0.001 kt (" + SI + ")"),
    ("t CO2e", "kt CO2 eq", 0.001, "1 t = 0.001 kt (" + SI + ")"),
    ("t CO2eq per year", "kt CO2 eq per year", 0.001, "1 t = 0.001 kt (" + SI + ")"),
    ("t CO2e per year", "kt CO2 eq per year", 0.001, "1 t = 0.001 kt (" + SI + ")"),
    ("t CO2 per year", "kt CO2 eq per year", 0.001, "1 t = 0.001 kt; CO2 has GWP 1"),
    ("t CO2 per capita", "t CO2 per capita", 1, "kept: per-capita indicator, no standard stock unit"),
    ("kt CH4", "kt CH4", 1, "kept in mass of gas; converting needs the GWP the document prints in the same table, not done"),
    ("kt N2O", "kt N2O", 1, "kept in mass of gas; converting needs the GWP the document prints in the same table, not done"),
    ("percent", "fraction", 0.01, "percent / 100"),
    ("%", "fraction", 0.01, "percent / 100"),
    ("percent of fleet", "fraction", 0.01, "percent / 100; denominator in share_definitions.csv"),
    ("percent of generation", "fraction", 0.01, "percent / 100"),
    ("percent of net generation", "fraction", 0.01, "percent / 100"),
    ("percent reduction", "fraction", 0.01, "percent / 100"),
    ("percent increase", "fraction", 0.01, "percent / 100"),
    ("percent ethanol by volume", "fraction", 0.01, "percent / 100; volume basis"),
    ("percent by volume", "fraction", 0.01, "percent / 100; volume basis"),
    ("percent (range 5 to 10)", "fraction", 0.01, "percent / 100"),
    ("percent of boilers", "fraction", 0.01, "percent / 100"),
    ("percent of herd", "fraction", 0.01, "percent / 100"),
    ("percent of land", "fraction", 0.01, "percent / 100"),
    ("percent of households", "fraction", 0.01, "percent / 100"),
    ("percent of units", "fraction", 0.01, "percent / 100"),
    ("percent of buildings", "fraction", 0.01, "percent / 100"),
    ("percent of 2020 level", "fraction", 0.01, "percent / 100"),
    ("percentage points", "fraction (points)", 0.01, "percentage points / 100"),
    ("MW", "MW", 1, "same unit"),
    ("MW (nominal)", "MW", 1, "same unit"),
    ("MWp", "MW", 1, "peak (DC) capacity as printed; an AC rating would need the inverter ratio, not converted"),
    ("GW", "MW", 1000, "1 GW = 1000 MW (" + SI + ")"),
    ("GWh", "PJ", 0.0036, "1 GWh = 3.6 TJ = 0.0036 PJ (" + SI + ")"),
    ("GWh per year", "PJ per year", 0.0036, "1 GWh = 0.0036 PJ (" + SI + ")"),
    ("MWh per year", "PJ per year", 3.6e-6, "1 MWh = 3.6 GJ (" + SI + ")"),
    ("Mbep", "PJ", 6.118, "1 barrel of oil equivalent = 6.118 GJ (US EIA, Units and calculators: 5.8 million Btu x 1.055 GJ per million Btu)"),
    ("million BOE per year", "PJ per year", 6.118, "1 barrel of oil equivalent = 6.118 GJ (US EIA)"),
    ("barrels of oil equivalent", "PJ", 6.118e-6, "1 barrel of oil equivalent = 6.118 GJ (US EIA)"),
    ("MJ/USD", "MJ per USD", 1, "kept: intensity in USD of the year the document states"),
    ("kWh/USD", "MJ per USD", 3.6, "1 kWh = 3.6 MJ (" + SI + ")"),
    ("km", "km", 1, "same unit"),
    ("km (of 66.6 km route)", "km", 1, "same unit"),
    ("ha", "ha", 1, "same unit"),
    ("ha per year", "ha per year", 1, "same unit"),
    ("t", "t", 1, "same unit"),
    ("t per year", "t per year", 1, "same unit"),
    ("Mt", "t", 1e6, "1 Mt = 1,000,000 t (" + SI + ")"),
    ("million t of solid waste", "t", 1e6, "1 million t = 1,000,000 t"),
    ("litres per year", "litres per year", 1, "same unit"),
    ("year", "year", 1, "calendar year"),
]
COUNTS = ["vehicles", "stoves", "stations", "buses", "passengers per day", "businesses", "indicators", "households",
          "lines", "routes", "projects", "farms", "installations", "EV buses", "efficient wood stoves"]
for c in COUNTS:
    UNITS.append((c, "count", 1, "count of items as printed"))
MODEL_UNITS = [
    ("PJ (model activity)", "PJ", 1, "model activity unit of the six energy models"),
    ("GW (model capacity)", "MW", 1000, "1 GW = 1000 MW (" + SI + ")"),
    ("fraction (model share)", "fraction", 1, "same unit"),
    ("model unit of emission label", "kt CO2 eq", 1000, "read as Mt CO2 eq: model emission factors are in Mt per PJ of fuel (for example 0.0568 to 0.0632 for gasoline in Guatemala, model_levers_GUA.csv); the GWP set of the model factors is not stated in the model files"),
]
UMAP = {u: (s, f, src) for u, s, f, src in UNITS}

# ---------------- renewable definitions ----------------
RENEW = r"(BMS|BIM|BGS|DBIM|DBGS|SUG|GEO|HYD|HD|HROR|ROR|SPV|PV|WND|WN)"
RENEW_DEF = {
    "CR": ("national electricity generation; renewable = hydro, geothermal, wind, solar, biomass including bagasse (PWRSUG counted renewable); imports excluded",
           "CR-01 p.46 (Generacion electrica nacional renovable, contribution EN-10, conditional)"),
    "DR": ("renewable = hydro, wind, solar, biomass, biogas (Law 57-07 list not re-read in this job); imports excluded",
           "DR-02 p.101 and DR-04 p.174 (targets of 25 and 30 percent of generation); NDC 3.0 states capacity targets, not a share"),
    "ECU": ("two shares of SNI generation: non-conventional renewables (ERNC: solar, wind, biomass, biogas) and hydro, each over total generation",
            "ECU-03 p.104 (LA1: ERNC share and hydro share of SNI generation)"),
    "GUA": ("renewable = bioenergy, geothermal, hydro, wind, solar PV and other renewables; denominator electricity generated",
            "GUA-01 p.41 (list of sources) and p.102 (indicator: percent of electricity generated from renewable sources)"),
    "HON": ("renewable sources in the generation mix; the NDC prints no list; hydro, geothermal, wind, solar, biomass used",
            "HON-01 p.26"),
    "JAM": ("renewable share of net generation; the model has no plant own use, so model generation is read as net",
            "JAM-01 p.14 (share of net generation); JAM-02 p.55 (electricity from renewable sources)"),
}


def plants(code):
    p = prod[(prod.Country == MODEL_COUNTRY[code]) & prod.Technology.str.match(r"^(PWR|PP)") & prod.Fuel.str.contains("ELE")]
    return p


def is_renew(t):
    t2 = re.sub(r"^(PWR|PP)", "", t)
    if re.search(r"(DSL|FOI|NGS|COA|COK|CRU|GLP|GSL|LPG)", t2):
        return False
    return bool(re.match(RENEW, t2) or re.search(r"(HYD|SPV|PV|WN|GEO|BIM|BMS|SUG|BGS|HD|HROR)", t2))


def ernc(t):
    t2 = re.sub(r"^(PWR|PP)", "", t)
    return bool(re.search(r"(SPV|PV|WN|BIM|BMS|BGS|SUG)", t2)) and not re.search(r"HD|HYD|ROR", t2)


def hydro(t):
    return bool(re.search(r"(HYD|HD|HROR)", re.sub(r"^(PWR|PP)", "", t)))


def share(code, scen, year, which="renew"):
    p = plants(code)
    q = p[(p.Scenario == scen) & (p.Year == year)]
    tot = q.Value.sum()
    if tot == 0:
        return None
    f = {"renew": is_renew, "ernc": ernc, "hydro": hydro}[which]
    return round(q[q.Technology.map(f)].Value.sum() / tot, 4)


def capacity(code, scen, year, pattern, plants_only=True):
    c = cap[(cap.Country == MODEL_COUNTRY[code]) & (cap.Scenario == scen) & (cap.Year == year)]
    if plants_only:
        c = c[c.Technology.str.match(r"^(PWR|PP)")]
    c = c[c.Technology.map(pattern)]
    return round(c.Value.sum() * 1000, 1)


def label(code, scen, year, lab):
    e = emis[(emis.Country == MODEL_COUNTRY[code]) & (emis.Scenario == scen) & (emis.Year == year) & (emis.Emission == lab)]
    return round(e.Value.sum() * 1000, 1) if len(e) else None


def tech_pattern(desc):
    d = desc.lower()
    if "storage" in d or "almacenamiento" in d or "batter" in d:
        return lambda t: "STO" in t or "BAT" in t, "storage technologies"
    if "distribut" in d or "self-generation" in d or "autoprod" in d:
        return lambda t: bool(re.search(r"(PVD|SPVD|DBIM|DBGS|DHYD)", t)), "distributed renewable plant types"
    if re.search(r"solar|photovolt|\bpv\b", d):
        return lambda t: bool(re.search(r"(SPV|PV)", t)), "solar PV plant types"
    if "wind" in d or "eolic" in d:
        return lambda t: bool(re.search(r"(WND|WN)", t)), "wind plant types"
    if "hydro" in d or "hidro" in d:
        return hydro, "hydro plant types"
    if "geotherm" in d:
        return lambda t: "GEO" in t, "geothermal plant types"
    if "biomass" in d or "bagasse" in d or "biogas" in d:
        return lambda t: bool(re.search(r"(BIM|BMS|BGS|SUG)", t)), "biomass and biogas plant types"
    if "natural gas" in d or " gas " in d or "lng" in d:
        return lambda t: "NGS" in t, "natural gas plant types"
    if "coal" in d or "carbon" in d:
        return lambda t: "COA" in t, "coal plant types"
    if re.search(r"diesel|hfo|fuel oil|bunker|ipp|combustion turbine|jps", d):
        return lambda t: bool(re.search(r"(DSL|FOI)", t)), "diesel and fuel oil plant types"
    if "renewab" in d or "renovab" in d or "clean" in d:
        return is_renew, "renewable plant types"
    return None, ""


def classify(v):
    t = (v["indicator"] + " | " + v["description"]).lower()
    u = v["check1_unit"].lower()
    sec = v.get("sector", "").lower()
    if re.search(r"t&d|grid loss|transmission|distribution loss|system losses|losses as share|electricity loss|p.rdidas", t):
        return "losses"
    if re.search(r"renewable share|clean share|share of generation|renewable portfolio|share of electricity|renewable share of", t) \
            and not re.search(r"fleet|final|primary|demand|consumption|energy mix", t):
        return "share of generation"
    if re.search(r"\bmw\b|\bgw\b|\bmwp\b|\bmw \(", u):
        return "capacity"
    if re.search(r"co2|ch4|n2o", u) or "emission" in t:
        return "emissions"
    if re.search(r"fleet|vehic|bus|taxi|train|railway|rail|freight|passenger", t):
        return "vehicles"
    if re.search(r"ethanol|blend|biofuel|biodiesel|saf|e10|e15", t):
        return "blend"
    if re.search(r"efficien|saving|saved|intensity", t):
        return "efficiency"
    return "other"


def main():
    vals = {v["value_id"]: v for v in read_csv(os.path.join(JOB, "values_to_verify.csv"))}
    levers = {}
    for code in CODES:
        levers[code] = read_csv(os.path.join(os.path.dirname(JOB), "ndc_scout_20261121T204620Z", f"model_levers_{code}.csv"))
    # units.csv
    seen = {}
    for v in vals.values():
        seen[v["unit"]] = seen.get(v["unit"], 0) + 1
    for code in CODES:
        for r in read_csv(os.path.join(JOB, f"blind_answers_{code}.csv")):
            pass
    urows = []
    for u, s, f, src in UNITS:
        urows.append({"unit": u, "where": "documents", "times_in_values_to_verify": seen.get(u, 0), "standard_unit": s, "factor": f, "source_of_factor": src})
    for u, s, f, src in MODEL_UNITS:
        urows.append({"unit": u, "where": "models", "times_in_values_to_verify": 0, "standard_unit": s, "factor": f, "source_of_factor": src})
    missing = [u for u in seen if u and u not in UMAP]
    gwp = [("CR-01", "AR5", "p.136"), ("CR-02", "not stated", ""), ("DR-01", "AR6", "p.32 (GWP column 29.8 for CH4 and 273 for N2O) and p.142"),
           ("ECU-01", "AR5", "p.60"), ("ECU-03", "not stated", ""), ("GUA-01", "AR5", "p.133"), ("GUA-04", "not stated", ""),
           ("HON-01", "AR5", "p.23"), ("JAM-01", "AR6 (stated with the 2021 IPCC AR6 for accounting)", "p.17 to p.18"), ("JAM-02", "not stated", "")]
    for sid, g, pg in gwp:
        urows.append({"unit": f"kt CO2 eq in {sid}", "where": "documents (GWP set)", "times_in_values_to_verify": "", "standard_unit": "kt CO2 eq",
                      "factor": 1, "source_of_factor": f"GWP set {g}; {sid} {pg}. Values are never converted between GWP sets."})
    write_csv(os.path.join(JOB, "units.csv"), urows)
    print("units", len(urows), "missing", missing)

    # share definitions and model comparison
    srows, mrows = [], []
    for code in CODES:
        ver = read_csv(os.path.join(JOB, f"verification_{code}.csv"))
        for r in ver:
            v = vals[r["value_id"]]
            v = dict(v, check1_unit=v["unit"])
            kind = classify(v)
            u = v["unit"]
            std = UMAP.get(u, (u, 1, ""))
            try:
                sv = round(float(r["settled_value"]) * std[1], 6)
            except ValueError:
                sv = ""
            # share definitions
            if std[0].startswith("fraction"):
                t = (v["indicator"] + " | " + v["description"]).lower()
                num = den = ""
                if kind == "share of generation":
                    num = "electricity generated from sources the document calls renewable" if "clean" not in t else "electricity generated from clean sources"
                    den = "net electricity generation" if "net" in t else ("generation of the national interconnected system (SNI)" if code == "ECU" else "national electricity generation (gross or net not stated)")
                    if code == "ECU" and "hydro" in t:
                        num = "hydro generation"
                    elif code == "ECU" and ("non-conventional" in t or "ernc" in t):
                        num = "non-conventional renewable generation (ERNC: solar, wind and others)"
                elif "fleet" in t or "vehicles" in t or "units" in v["unit"]:
                    num = "vehicles of the stated technology"
                    m = re.search(r"(public transport fleet|bus fleet|private vehicle fleet|light transport fleet|light vehicle fleet|heavy freight fleet|light freight fleet|freight fleet|freight vehicles|vehicle fleet|passenger fleet|public fleet|private fleet|taxi fleet|railway units|light vehicles|gasoline vehicles)", t)
                    den = (m.group(1) if m else "vehicle fleet as described") + " (stock of vehicles)"
                elif "passenger-km" in t or "passenger transport" in t:
                    num, den = "passenger-km of the stated mode", "total passenger-km"
                elif "blend" in t or "ethanol" in t or "biofuel" in t or "saf" in t:
                    num = "ethanol, biodiesel or biofuel volume" if "volume" in v["unit"] or "ethanol" in t else "biofuel energy"
                    den = "gasoline blend volume" if "gasoline" in t or "ethanol" in t else ("final energy of transport" if "transport" in t else "fuel use as described")
                elif "loss" in t:
                    num, den = "transmission and distribution losses", "net generation" if "net" in v["unit"] or "generation" in t else "electricity supplied (as described)"
                elif "against bau" in t or "below bau" in t or "reduction" in t:
                    num, den = "reduction as described", "reference value named in the description (BAU, base year or baseline)"
                else:
                    num, den = "as described", "as described"
                srows.append({"value_id": r["value_id"], "country": code, "source_id": v["source_id"], "page": v["page"],
                              "indicator": v["indicator"], "value_printed": f"{v['value']} {v['unit']}", "year": v["year"],
                              "numerator": num, "denominator": den,
                              "renewable_definition": (RENEW_DEF[code][0] + " (source: " + RENEW_DEF[code][1] + ")") if kind == "share of generation" else "",
                              "conditionality": v["conditionality"], "status": r["status"]})
            # model quantity
            row = {"value_id": r["value_id"], "country": code, "status": r["status"], "kind": kind,
                   "document_value_standard": sv, "standard_unit": std[0], "year": v["year"], "model_quantity": "", "same_kind": "",
                   "model_unit": "", "data_needed_to_convert": "", "note": ""}
            for s in SCEN:
                for y in YEARS:
                    row[f"{s}_{y}"] = ""
            desc = v["description"]
            if r["status"] == "conflict" or r["verbal_target"] == "yes" and kind not in ("share of generation",):
                row["same_kind"] = "not compared"
                row["note"] = "conflict row (held back)" if r["status"] == "conflict" else "verbal target"
            elif kind == "share of generation":
                which = "renew"
                t = (v["indicator"] + " " + desc).lower()
                if code == "ECU" and ("hydro" in t):
                    which = "hydro"
                elif code == "ECU" and ("non-conventional" in t or "ernc" in t):
                    which = "ernc"
                for s in SCEN:
                    for y in YEARS:
                        row[f"{s}_{y}"] = share(code, s, y, which)
                row["model_quantity"] = {"renew": "renewable share of generation under the country definition", "hydro": "hydro share of generation", "ernc": "non-conventional renewable share of generation"}[which]
                row["model_unit"] = "fraction"
                row["same_kind"] = "yes" if code != "JAM" else "yes (model generation read as net generation)"
                row["note"] = RENEW_DEF[code][0]
                if "clean" in t:
                    row["same_kind"] = "partly: the document says clean, the model share counts renewables only"
            elif kind == "capacity":
                pat, pname = tech_pattern(v["indicator"])
                if pat is None:
                    pat, pname = tech_pattern(desc)
                if pat is None:
                    row["same_kind"] = "different quantity"
                    row["data_needed_to_convert"] = "the plant types the target covers"
                else:
                    for s in SCEN:
                        for y in YEARS:
                            row[f"{s}_{y}"] = capacity(code, s, y, pat, pname != "storage technologies")
                    row["model_quantity"] = f"installed capacity of {pname}"
                    row["model_unit"] = "MW"
                    b = capacity(code, "NDCNEW", 2022, pat, pname != "storage technologies")
                    t = (v["indicator"] + " " + desc).lower()
                    if re.search(r"new|additional|adicional|retire|retir|phase", t):
                        row["same_kind"] = "partly: the document states added or retired capacity, the model gives installed capacity in each year"
                        row["data_needed_to_convert"] = "the document's start year and starting capacity"
                    else:
                        row["same_kind"] = "yes"
                    row["note"] = f"model installed capacity of the same plant types in 2022: {b} MW"
            elif kind == "emissions":
                t = (v["indicator"] + " " + desc + " " + v.get("sector", "")).lower()
                sec = v.get("sector", "")
                energy = re.search(r"energ", sec.lower()) or re.search(r"energy sector|sector energ|energy and transport|energ[ií]a", t)
                lab = "CO2e_sources" if code != "CR" else None
                energy_total = sec.strip().lower() in ("energy", "energy (including transport)") and (
                    v["origin"].startswith("projections") or re.search(
                        r"energy sector|sector de energ|energy \(including transport\)|energy and transport measures|energy emissions|emissions of the energy|sector emissions|energy sector emissions", t))
                if energy and not energy_total and not re.search(r"economy-wide", sec.lower()):
                    row["same_kind"] = "different quantity"
                    row["data_needed_to_convert"] = "emissions of the technologies of this one measure or subsector (AnnualTechnologyEmission, one label); the comparison here is for energy sector totals only"
                elif not energy or re.search(r"economy-wide|national|net ghg|total", sec.lower() + " " + v["indicator"].lower()) and not re.search(r"energ", sec.lower()):
                    row["same_kind"] = "different quantity"
                    row["data_needed_to_convert"] = "results of the AFOLU, IPPU and waste models (and LULUCF) of the same scenario and GWP set; the energy model covers energy and transport only"
                elif lab is None:
                    row["same_kind"] = "not compared"
                    row["note"] = "Costa Rica model has no single energy CO2e label (CO2e_PWR, CO2e_TRN, CO2e_DE); labels are not summed"
                    row["data_needed_to_convert"] = "one energy CO2e label in the Costa Rica model"
                else:
                    pct = "percent" in v["unit"]
                    red = re.search(r"reduc|against bau|abat", t)
                    for s in SCEN:
                        for y in YEARS:
                            a, b = label(code, s, y, lab), label(code, "BAU", y, lab)
                            if a is None:
                                continue
                            if pct and red:
                                row[f"{s}_{y}"] = round(1 - a / b, 4) if b else None
                            elif red:
                                row[f"{s}_{y}"] = round(b - a, 1)
                            else:
                                row[f"{s}_{y}"] = a
                    row["model_quantity"] = ("reduction against the model BAU, " if red else "emissions, ") + f"label {lab}"
                    row["model_unit"] = "fraction" if pct and red else "kt CO2 eq"
                    row["same_kind"] = "partly: energy emissions of one model label; the model BAU is not the document BAU and the GWP set of the model factors is not stated"
            elif kind == "vehicles":
                row["same_kind"] = "different quantity"
                row["model_quantity"] = "electric share of transport group output (passenger-km or tonne-km), not a share of the vehicle stock"
                row["data_needed_to_convert"] = "vehicle stock by technology and distance driven per vehicle, by vehicle class, for the scenario"
                el = [x for x in levers[code] if x["quantity"] == "electric share of transport group"]
                row["note"] = "nearest model quantity, NDCNEW 2035: " + "; ".join(f"{x['technology']} {x['NDCNEW_2035']}" for x in el[:8])
            elif kind == "blend":
                t = desc.lower()
                if code == "CR" and re.search(r"ethanol|e10|e15|gasolin", t + " " + v["indicator"].lower()):
                    row["model_quantity"] = "none readable: BLEND_GSL takes 1.0 of E1_PURGSL and 1.0 of E1_ETA per unit of E1_GSL (B1_Output_Params NDCNEW InputActivityRatio, 2030 and 2035), so the solved flows give no blend share"
                    row["same_kind"] = "different quantity"
                    row["data_needed_to_convert"] = "blend input ratios that sum to one unit of blend (energy basis), then the lower heating values per litre of ethanol and gasoline to compare with a volume share"
                else:
                    row["same_kind"] = "different quantity"
                    row["data_needed_to_convert"] = "a biofuel or ethanol fuel and blending technology in the model, or the blend shares the model applies"
            elif kind == "losses":
                gl = [x for x in levers[code] if x.get("group") == "grid losses"]
                row["same_kind"] = "not computed"
                row["data_needed_to_convert"] = "flows of the ELE_TRANS and ELE_DIST technologies with their input-activity ratios (solved results report outputs only)"
                row["note"] = ("compiled grid-loss inputs that differ from BAU: " + "; ".join(f"{x['quantity']} {x['technology']} NDCNEW 2035 {x['NDCNEW_2035']}" for x in gl[:4])) if gl else "no grid-loss input differs between scenarios"
            else:
                row["same_kind"] = "different quantity"
                row["data_needed_to_convert"] = "no model quantity of this kind in the energy model"
            mrows.append(row)
    write_csv(os.path.join(JOB, "share_definitions.csv"), srows)
    write_csv(os.path.join(JOB, "model_comparison.csv"), mrows)
    import collections
    print("shares", len(srows), "comparison", len(mrows), collections.Counter(r["same_kind"].split(":")[0] for r in mrows))


if __name__ == "__main__":
    main()
