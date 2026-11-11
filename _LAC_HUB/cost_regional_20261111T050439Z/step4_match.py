"""Step 4: choose, for each of the 68 groups, the best regional value under the brief's tiers and
acceptance rules, or record why none is accepted. Writes scope.csv, match_log.csv and
scratch/accepted.json (input of step 5)."""
import json, sys
import pandas as pd
sys.path.insert(0, ".")
from step1_scope import select

RV = pd.read_csv("regional_values.csv")
TECHNAME = {  # Tech.Name from each country's A-O workbook (Primary or Secondary Techs sheet)
    ("CostaRica", "PP_SPV_DG"): "Primary - Transformation - Solar distributed", ("CostaRica", "PWRBMS"): "Power Plant Biomass - Steam Trubine",
    ("CostaRica", "PWRDSL"): "Power Plant Diesel", ("CostaRica", "PWRFOI"): "Power Plant Fuel_Oil", ("CostaRica", "PWRGEO"): "Primary - Transformation - Geothermal",
    ("CostaRica", "PWRHYDDAM"): "Primary - Transformation - Hydroelectric Dam", ("CostaRica", "PWRSPVDTR"): "Primary - Transformation - Photovoltaic in Distribution",
    ("CostaRica", "PWRSPVTRN"): "Primary - Transformation - Photovoltaic in Transmision", ("CostaRica", "PWRWNONS"): "Primary - Transformation - On shore Wind",
    ("DominicanRepublic", "PPBGS"): "Power Plant - Biogas", ("DominicanRepublic", "PPBIM"): "Power Plant - Biomass",
    ("DominicanRepublic", "PPDHYD"): "Power Plant - Selfproducer Power Plant Hydro", ("DominicanRepublic", "PPHDAM"): "Power Plant - Hydro Dam",
    ("DominicanRepublic", "PPPVD"): "Power Plant - Distributed Solar", ("DominicanRepublic", "PPPVT"): "Power Plant - Transmission Solar",
    ("DominicanRepublic", "PPPVTHYD"): "Power Plant - Transmission Solar", ("DominicanRepublic", "PPWNDON"): "Power Plant - Wind",
    ("Ecuador", "PPPVD"): "Primary - Transformation - Distributed Solar", ("Ecuador", "PPWNDD"): "Primary - Transformation - Distributed Wind",
    ("Ecuador", "STOELE"): "Secondary - Storage",
    ("Guatemala", "PPBIM"): "Primary - Transformation - Biomass", ("Guatemala", "PPCOA"): "Primary - Transformation - Coal",
    ("Guatemala", "PPFOI"): "Primary - Transformation - Fuel Oil", ("Guatemala", "PPGEO"): "Primary - Transformation - Geothermal",
    ("Guatemala", "PPHROR"): "Primary - Transformation - Hydro ROR", ("Guatemala", "PPNGS"): "Primary - Transformation - Natural Gas",
    ("Guatemala", "PPPVD"): "Primary - Transformation - Distributed Solar", ("Guatemala", "PPPVDS"): "Primary - Transformation - Distributed Solar with battery storage",
    ("Guatemala", "PPPVT"): "Primary - Transformation - Transmission Solar", ("Guatemala", "PPPVT2"): "Primary - Transformation - Transmission Solar",
    ("Guatemala", "PPPVTS"): "Primary - Transformation - Transmission Solar with battery storage",
    ("Honduras", "PPBIM"): "Primary - Transformation - Biomass", ("Honduras", "PPPVD"): "Primary - Transformation - Distributed Solar",
    ("Jamaica", "PPBGS"): "Primary - Transformation - Biogas", ("Jamaica", "PPBIM"): "Primary - Transformation - Biomass",
    ("Jamaica", "PPGEO"): "Primary - Transformation - Geothermal", ("Jamaica", "PPHDAM"): "Primary - Transformation - Hydro Dam",
    ("Jamaica", "PPHROR"): "Primary - Transformation - Hydro ROR", ("Jamaica", "PPPVD"): "Primary - Transformation - Distributed Solar",
    ("Jamaica", "PPWNDON"): "Primary - Transformation - Wind",
}
CONFIG = {
    "PP_SPV_DG": "distributed (rooftop) PV, no storage", "PWRBMS": "biomass steam turbine", "PWRDSL": "diesel engine plant", "PWRFOI": "fuel oil engine plant",
    "PWRGEO": "geothermal", "PWRHYDDAM": "hydro, dam (reservoir)", "PWRSPVDTR": "utility-scale ground PV connected at distribution level, no storage",
    "PWRSPVTRN": "utility-scale PV, transmission, no storage", "PWRWNONS": "onshore wind, utility-scale, no storage",
}
CONFIG_C = {
    ("DominicanRepublic", "PPBGS"): "biogas plant", ("DominicanRepublic", "PPBIM"): "biomass plant", ("DominicanRepublic", "PPDHYD"): "hydro, self-producer, type not stated",
    ("DominicanRepublic", "PPHDAM"): "hydro, dam", ("DominicanRepublic", "PPPVD"): "distributed PV, no storage",
    ("DominicanRepublic", "PPPVT"): "utility-scale PV; current path adds a 4-hour battery cost from 2025",
    ("DominicanRepublic", "PPPVTHYD"): "utility-scale PV; current path adds a 4-hour battery cost from 2025",
    ("DominicanRepublic", "PPWNDON"): "onshore wind; current path adds a 4-hour battery cost from 2025",
    ("Ecuador", "PPPVD"): "distributed PV (commercial/industrial rooftop class in the current source), no storage",
    ("Ecuador", "PPWNDD"): "distributed wind (small turbines)", ("Ecuador", "STOELE"): "utility-scale lithium-ion battery, 4 hours",
    ("Guatemala", "PPBIM"): "biomass plant", ("Guatemala", "PPCOA"): "coal steam plant", ("Guatemala", "PPFOI"): "fuel oil engine plant",
    ("Guatemala", "PPGEO"): "geothermal", ("Guatemala", "PPHROR"): "hydro, run-of-river (small class in the current source)",
    ("Guatemala", "PPNGS"): "natural gas combined cycle", ("Guatemala", "PPPVD"): "distributed PV, no storage", ("Guatemala", "PPPVDS"): "distributed PV with battery storage",
    ("Guatemala", "PPPVT"): "utility-scale PV, no storage", ("Guatemala", "PPPVT2"): "utility-scale PV, no storage", ("Guatemala", "PPPVTS"): "utility-scale PV with battery storage",
    ("Honduras", "PPBIM"): "biomass plant (sugar mill cogeneration)", ("Honduras", "PPPVD"): "distributed PV, no storage",
    ("Jamaica", "PPBGS"): "biogas plant", ("Jamaica", "PPBIM"): "biomass plant", ("Jamaica", "PPGEO"): "geothermal", ("Jamaica", "PPHDAM"): "hydro, dam",
    ("Jamaica", "PPHROR"): "hydro, run-of-river", ("Jamaica", "PPPVD"): "distributed PV, no storage", ("Jamaica", "PPWNDON"): "onshore wind, utility-scale, no storage",
}

def vid(sid, page, tech_sub, comp, vyear):
    m = RV[(RV.source_id == sid) & (RV.pdf_page == page) & (RV.cost_component == comp) & (RV.value_year.astype(str) == str(vyear))
           & RV.technology_as_printed.str.contains(tech_sub, regex=False)]
    assert len(m) >= 1, (sid, page, tech_sub, comp, vyear)
    return m.iloc[0]["value_id"]

# Common refusal reasons
NO_CY = "currency year not stated"
REF = {
    "DG_PV_CA": ("no regional value met section 2: ICE PEG 2024-2040 (N), IRENA RPGC 2022/2024/2025 (R1) and HON PIEG 2026-2035 (R2) print no distributed or rooftop PV cost; "
                 "IRENA Central America roadmap Table 16 distributed PV (1,400 USD/kW in 2018) has no currency year; GUA PEIG 2026-2050, Mexico PLADESE and El Salvador have no currency year"),
    "DG_PV_CAR": ("no regional value met section 2: IRENA tables print utility PV only; CCREEE 2022 gives residential and commercial ranges (658-4,236 and 651-2,974 USD/kW) without a currency year; "
                  "Jamaica IRP 2018, PREPA IRP 2019 and Barbados IRRP have no distributed PV cost"),
    "BIO_VOM_CA": ("no regional biomass variable O&M: ICE PEG 2024-2040 and HON PIEG 2026-2035 print none for biomass; GUA PEIG 2026-2050 cogeneration (10 USD/MWh) has no currency year; "
                   "IRENA gives global values only"),
    "BIO_CAR": ("no Caribbean or LAC biomass or biogas value met section 2: Jamaica IRP 2018 biomass rows carry no cost; Barbados IRRP (woody biomass, landfill gas) has no price base; "
                "DR PEN 2022-2036 has municipal waste only and no currency year; CCREEE and PREPA IRP 2019 have none; IRENA bioenergy costs are global"),
    "DR_STORAGE": ("configuration mismatch: the current Dominican Republic path adds a 4-hour battery cost from 2025, and no regional source prints a matching PV- or wind-plus-battery cost "
                   "with a stated currency year (Jamaica IRP and PREPA price plain plants; DR PEN tracker-plus-storage has no currency year)"),
    "HYDRO_NOCFG": ("no regional value with a matching hydro configuration: IRENA large and small hydropower classes state size, not dam or run-of-river; Jamaica IRP 2018 has run-of-river "
                    "fixed O&M only; DR PEN 100 MW reservoir project has no currency year"),
    "GEO_CAR": ("no Caribbean geothermal cost: Jamaica's neighbours (Caribbean states) publish none in the documents opened; IRENA geothermal costs are global; "
                "Central American sources are not neighbours of Jamaica under the brief"),
}

D = {}
def acc(c, t, p, tier, sid, picks, reason, path, extra=None):
    D[(c, t, p)] = dict(outcome=tier, tier=tier, source_id=sid, picks=picks, reason=reason, path=path, extra=extra or {})
def keep(c, t, p, reason):
    D[(c, t, p)] = dict(outcome="international kept", tier="", source_id="", picks=[], reason=reason, path="", extra={})

# ---------------- Costa Rica ----------------
keep("CostaRica", "PP_SPV_DG", "CapitalCost", REF["DG_PV_CA"])
keep("CostaRica", "PP_SPV_DG", "FixedCost", REF["DG_PV_CA"])
acc("CostaRica", "PWRBMS", "CapitalCost", "N", "REG-005", [vid("REG-005", 153, "Biomasa Genericos", "capital", "candidate (Dec-2023 prices)")],
    "ICE PEG 2024-2040 Tabla 10.9 Biomasa Genericos overnight cost (sugarcane biomass, steam cycle) matches a biomass steam turbine; national source not used by the Costa Rica job", "single")
keep("CostaRica", "PWRBMS", "VariableCost", REF["BIO_VOM_CA"])
acc("CostaRica", "PWRDSL", "VariableCost", "R2", "REG-006", [vid("REG-006", 46, "gas natural/bunker/diesel, 50 MW (gas natural/diesel)", "variable_om", "2024 reference")],
    "no N or R1 engine variable O&M; HON PIEG 2026-2035 Tabla 19 internal combustion engine on gas/bunker/diesel prints 5 USD/MWh for diesel (2024 USD), same for all sizes", "single")
acc("CostaRica", "PWRFOI", "VariableCost", "R2", "REG-006", [vid("REG-006", 46, "gas natural/bunker/diesel, 50 MW (bunker)", "variable_om", "2024 reference")],
    "no N or R1 engine variable O&M; HON PIEG 2026-2035 Tabla 19 internal combustion engine prints 7 USD/MWh for bunker (2024 USD), same for all sizes", "single")
acc("CostaRica", "PWRGEO", "FixedCost", "N", "REG-005", [vid("REG-005", 151, "Geotermico Genericos", "fixed_om", "candidate (Dec-2023 prices)")],
    "ICE PEG 2024-2040 Tabla 10.8 Geotermico Genericos fixed O&M 160 USD/kW-year (Dec-2023 USD)", "single")
acc("CostaRica", "PWRHYDDAM", "CapitalCost", "R2", "REG-006", [vid("REG-006", 46, "Hidroelectrica de embalse, <100 MW", "capital", "2024 reference")],
    "N refused: ICE PEG 2024-2040 generic hydro has 0 useful volume (run-of-river) and its reservoir projects (Diquis, RG-430) are single projects, not a class value; "
    "R1 refused: IRENA hydropower classes state size, not dam or run-of-river; R2 HON PIEG 2026-2035 Hidroelectrica de embalse 5,100 USD/kW (2024 USD), same for both sizes", "single")
acc("CostaRica", "PWRSPVDTR", "CapitalCost", "N", "REG-005", [vid("REG-005", 153, "Solar Genericos (10 MW)", "capital", "candidate (Dec-2023 prices)")],
    "ICE PEG 2024-2040 Tabla 10.9 Solar Genericos (10 MW, fixed) overnight 1,100 USD/kW (Dec-2023 USD); the Costa Rica job already treated this row as utility-scale ground PV", "single")
acc("CostaRica", "PWRSPVTRN", "FixedCost", "N", "REG-005", [vid("REG-005", 151, "Solar Genericos (10 MW)", "fixed_om", "candidate (Dec-2023 prices)")],
    "ICE PEG 2024-2040 Tabla 10.8 Solar Genericos fixed O&M 17 USD/kW-year (Dec-2023 USD)", "single")
acc("CostaRica", "PWRWNONS", "CapitalCost", "N", "REG-005", [vid("REG-005", 153, "Eolico Genericos", "capital", "candidate (Dec-2023 prices)")],
    "ICE PEG 2024-2040 Tabla 10.9 Eolico Genericos overnight 1,900 USD/kW (Dec-2023 USD); N ranks above the IRENA Central America and Caribbean table", "single")
acc("CostaRica", "PWRWNONS", "FixedCost", "N", "REG-005", [vid("REG-005", 151, "Eolico Genericos", "fixed_om", "candidate (Dec-2023 prices)")],
    "ICE PEG 2024-2040 Tabla 10.8 Eolico Genericos fixed O&M 50 USD/kW-year (Dec-2023 USD)", "single")

# ---------------- Dominican Republic ----------------
for p in ("CapitalCost", "FixedCost", "VariableCost"):
    keep("DominicanRepublic", "PPBGS", p, REF["BIO_CAR"])
keep("DominicanRepublic", "PPBIM", "CapitalCost", REF["BIO_CAR"])
for p in ("CapitalCost", "FixedCost"):
    keep("DominicanRepublic", "PPDHYD", p, "the model row does not state a hydro type (self-producer hydro), so no dam or run-of-river value can be matched; " + REF["HYDRO_NOCFG"])
    keep("DominicanRepublic", "PPHDAM", p, REF["HYDRO_NOCFG"])
    keep("DominicanRepublic", "PPPVD", p, REF["DG_PV_CAR"])
    for t in ("PPPVT", "PPPVTHYD", "PPWNDON"):
        keep("DominicanRepublic", t, p, REF["DR_STORAGE"])

# ---------------- Ecuador (R2 Colombia) ----------------
acc("Ecuador", "PPPVD", "CapitalCost", "R2", "REG-014",
    [vid("REG-014", 64, "escala industrial", "capital", y) for y in (2024, 2030, 2050)],
    "no N or R1 distributed PV value; Colombian Technology Catalogue (MME/UPME 2025) industrial rooftop PV (100 kW, grid-connected), specific investment per MWe (AC), 2024 USD; "
    "the industrial class matches the commercial PV class of the current source", "multi", {"rows": "AC"})
acc("Ecuador", "PPPVD", "FixedCost", "R2", "REG-014",
    [vid("REG-014", 64, "escala industrial", "fixed_om", y) for y in (2024, 2030, 2050)],
    "Colombian Technology Catalogue industrial rooftop PV fixed O&M per MWe (AC), 2024 USD", "multi")
acc("Ecuador", "PPWNDD", "CapitalCost", "R2", "REG-014",
    [vid("REG-014", 92, "Peque", "capital", y) for y in (2024, 2030, 2050)],
    "Colombian Technology Catalogue small onshore wind turbines (<1 MW) specific investment, 2024 USD; distributed wind class", "multi")
acc("Ecuador", "PPWNDD", "FixedCost", "R2", "REG-014",
    [vid("REG-014", 92, "Peque", "fixed_om", y) for y in (2024, 2030, 2050)],
    "Colombian Technology Catalogue small onshore wind turbines fixed O&M, 2024 USD", "multi")
acc("Ecuador", "STOELE", "CapitalCost", "R2", "REG-014",
    [vid("REG-014", 316, "Gran escala", "capital", y) for y in (2024, 2030, 2050)],
    "Colombian Technology Catalogue grid-scale lithium-ion battery, 4 hours, total investment per MW, 2024 USD; matches the 4-hour utility battery of the current source", "multi", {"per_pj": True})
acc("Ecuador", "STOELE", "FixedCost", "R2", "REG-014",
    [vid("REG-014", 315, "Gran escala", "fixed_om", y) for y in (2024, 2030, 2050)],
    "Colombian Technology Catalogue grid-scale lithium-ion battery fixed O&M per MWe, 2024 USD", "multi", {"per_pj": True})

# ---------------- Guatemala ----------------
keep("Guatemala", "PPBIM", "VariableCost", REF["BIO_VOM_CA"])
keep("Guatemala", "PPCOA", "CapitalCost", "no regional coal value met section 2: HON PIEG 2026-2035 and ICE PEG 2024-2040 have no coal; DR PEN steam turbine and Mexico PLADESE carboelectrica have no currency year")
acc("Guatemala", "PPFOI", "FixedCost", "R2", "REG-006", [vid("REG-006", 46, "gas natural/bunker/diesel, 50 MW", "fixed_om", "2024 reference")],
    "no N or R1 engine value; HON PIEG 2026-2035 Tabla 19 internal combustion engine gas/bunker/diesel fixed O&M 14.00 USD/kW-year (2024 USD), same for all sizes; "
    "most recent R2 (ICE PEG 2024-2040 medium-speed bunker engine 40 USD/kW-year is older)", "single")
acc("Guatemala", "PPFOI", "VariableCost", "R2", "REG-006", [vid("REG-006", 46, "gas natural/bunker/diesel, 50 MW (bunker)", "variable_om", "2024 reference")],
    "HON PIEG 2026-2035 Tabla 19 engine variable O&M 7 USD/MWh on bunker (2024 USD)", "single")
acc("Guatemala", "PPGEO", "CapitalCost", "R2", "REG-006", [vid("REG-006", 46, "Geotermica, 20 MW", "capital", "2024 reference")],
    "no N or R1 geothermal value; HON PIEG 2026-2035 Tabla 19 geothermal 6,179.24 USD/kW (2024 USD) is the most recent R2 (ICE PEG 2024-2040 generic 6,645 overnight, Dec-2023 USD, is older)", "single")
acc("Guatemala", "PPHROR", "CapitalCost", "R2", "REG-006", [vid("REG-006", 46, "Hidroelectrica de pasada, <10 MW", "capital", "2024 reference")],
    "R1 refused (IRENA small hydropower is a size class, not run-of-river, and the 2018-2024 Central America value is n.a.); HON PIEG 2026-2035 Tabla 19 run-of-river <10 MW "
    "3,786.50 USD/kW (2024 USD); the small size row matches the small hydro class of the current source", "single")
acc("Guatemala", "PPNGS", "CapitalCost", "R2", "REG-006", [vid("REG-006", 46, "Turbina de gas en ciclo combinado a gas natural, 250 MW", "capital", "2024 reference")],
    "HON PIEG 2026-2035 Tabla 19 gas turbine combined cycle 1,437.59 USD/kW (2024 USD); the current source is a combined cycle cost; most recent R2", "single")
for p in ("CapitalCost", "FixedCost"):
    keep("Guatemala", "PPPVD", p, REF["DG_PV_CA"])
    keep("Guatemala", "PPPVDS", p, "no regional distributed PV-plus-battery value; " + REF["DG_PV_CA"])
for t in ("PPPVT", "PPPVT2"):
    acc("Guatemala", t, "CapitalCost", "R1", "REG-003",
        [vid("REG-003", 62, "Utility-scale solar PV", "capital", 2015) if False else
         RV[(RV.source_id == "REG-003") & (RV.pdf_page == 62) & (RV.geography == "Central America and the Caribbean") & (RV.value_year.astype(str) == y)].iloc[0]["value_id"]
         for y in ("2015", "2025")],
        "IRENA RPGC 2025 Table 3.1 utility-scale PV weighted average total installed cost, Central America and the Caribbean, 2015 and 2025 (2025 USD); "
        "R1 ranks above the HON PIEG utility PV value (R2); most recent IRENA edition", "multi")
acc("Guatemala", "PPPVT2", "FixedCost", "R2", "REG-006", [vid("REG-006", 46, "Solar fotovoltaica, 50 MW", "fixed_om", "2024 reference")],
    "no N or R1 utility PV fixed O&M for the region (IRENA O&M tables group countries by OECD status); HON PIEG 2026-2035 Tabla 19 solar PV fixed O&M 21.25 USD/kW-year (2024 USD), same for all sizes", "single")
acc("Guatemala", "PPPVTS", "CapitalCost", "R2", "REG-006", [vid("REG-006", 46, "Solar fotovoltaica con bateria (30%), 50 MW", "capital", "2024 reference")],
    "HON PIEG 2026-2035 Tabla 19 hybrid solar PV with battery (battery 30 percent of PV power) 1,434.72 USD/kW (2024 USD); size row rule: middle printed size (lower middle of 20/50/100/150 MW)", "single")
acc("Guatemala", "PPPVTS", "FixedCost", "R2", "REG-006", [vid("REG-006", 46, "Solar fotovoltaica con bateria (30%), 50 MW", "fixed_om", "2024 reference")],
    "HON PIEG 2026-2035 Tabla 19 hybrid solar PV with battery (30 percent) fixed O&M 40.31 USD/kW-year (2024 USD), same for all sizes", "single")

# ---------------- Honduras ----------------
acc("Honduras", "PPBIM", "CapitalCost", "R2", "REG-005", [vid("REG-005", 153, "Biomasa Genericos", "capital", "candidate (Dec-2023 prices)")],
    "no N or R1 biomass value; ICE PEG 2024-2040 (Costa Rica, SICA neighbour) Biomasa Genericos overnight 1,750 USD/kW (Dec-2023 USD), sugarcane biomass; GUA PEIG cogeneration has no currency year", "single")
acc("Honduras", "PPBIM", "FixedCost", "R2", "REG-005", [vid("REG-005", 151, "Biomasa Genericos", "fixed_om", "candidate (Dec-2023 prices)")],
    "ICE PEG 2024-2040 Tabla 10.8 Biomasa Genericos fixed O&M 37 USD/kW-year (Dec-2023 USD)", "single")
keep("Honduras", "PPBIM", "VariableCost", REF["BIO_VOM_CA"])
keep("Honduras", "PPPVD", "FixedCost", REF["DG_PV_CA"])

# ---------------- Jamaica ----------------
for t in ("PPBGS", "PPBIM"):
    for p in ("CapitalCost", "FixedCost", "VariableCost"):
        keep("Jamaica", t, p, REF["BIO_CAR"])
for p in ("CapitalCost", "FixedCost"):
    keep("Jamaica", "PPGEO", p, REF["GEO_CAR"])
    keep("Jamaica", "PPHDAM", p, REF["HYDRO_NOCFG"])
    keep("Jamaica", "PPPVD", p, REF["DG_PV_CAR"])
keep("Jamaica", "PPHROR", "CapitalCost", "no run-of-river capital cost: Jamaica IRP 2018 leaves it to be supplied by PCJ, and no Caribbean neighbour or regional body prints one with a stated currency year; IRENA small hydro is a size class")
acc("Jamaica", "PPWNDON", "CapitalCost", "R1", "REG-002",
    [RV[(RV.source_id == "REG-002") & (RV.pdf_page == 71) & (RV.geography == "Central America and the Caribbean") & (RV.value_year.astype(str) == y)].iloc[0]["value_id"] for y in ("2012", "2024")],
    "IRENA RPGC 2024 Table 2.1 onshore wind weighted average total installed cost, Central America and the Caribbean, 2012 (regional data start, table note) and 2024 (2024 USD); "
    "the 2025 edition has no Central America and Caribbean row; CCREEE 2022 LAC 2,062 is older and has no stated currency year", "multi")

if __name__ == "__main__":
    d, s = select()
    s["year"] = s["year"].astype(int)
    scope, log = [], []
    for (c, t, p), g in s.groupby(["country", "Tech", "Parameter"]):
        r24 = g[g.year == 2024].iloc[0]
        dec = D[(c, t, p)]
        cfg = CONFIG.get(t) if c == "CostaRica" else CONFIG_C[(c, t)]
        scope.append({"country": c, "technology": t, "parameter": p, "tech_name": TECHNAME[(c, t)], "configuration": cfg,
                      "rows": len(g), "years": f"{g.year.min()}-{g.year.max()}", "proposed_2024": r24["proposed_value"], "unit": r24["unit"],
                      "source_ids_2024": r24["source_ids"], "outcome": dec["outcome"], "regional_source": dec["source_id"],
                      "regional_value_ids": ";".join(dec["picks"]), "reason": dec["reason"]})
        log.append({"country": c, "technology": t, "parameter": p, "decision": "accepted" if dec["picks"] else "refused",
                    "tier": dec["tier"], "source_id": dec["source_id"], "value_ids": ";".join(dec["picks"]), "path_rule": dec["path"],
                    "reason": dec["reason"]})
    assert len(scope) == 68 and len(D) == 68, (len(scope), len(D))
    sc = pd.DataFrame(scope)
    for col in sc.columns:
        if sc[col].dtype == object:
            sc[col] = sc[col].str.replace(chr(0x2014), "-").str.replace(chr(0x2013), "-")
    sc.to_csv("scope.csv", index=False, lineterminator="\n")
    pd.DataFrame(log).to_csv("match_log.csv", index=False, lineterminator="\n")
    json.dump({f"{k[0]}|{k[1]}|{k[2]}": v for k, v in D.items() if v["picks"]}, open("scratch/accepted.json", "w"), indent=1)
    print(sc.outcome.value_counts().to_dict())
