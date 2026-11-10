"""Step 5: plant costs for the Honduras plants in scope (rules P1 to P3). Writes plant_costs.csv.

Current values: BAU compiled CSVs (effective yearly values of the A-O rows).
Cited edition: ODS/CND Plan Indicativo de Expansion de la Generacion 2024-2033, Tabla 7 (2023 USD) and
Anexos Tablas B-2 and B-3 (yearly paths of the PV-plus-battery and wind-plus-battery rows).
Newer edition: ODS/CND PIEG 2026-2035, Tabla 19 (2024 USD); for wind, PV and hybrids the yearly path is the
NREL ATB 2024 Moderate index from 2024, as the ODS states in Anexos A.2.
Replacements: IRENA Renewable Power Generation Costs in 2022 (bioenergy), NREL ATB 2024 where IRENA, IEA WEO 2023
and the ODS plans give no value.
Units: CapitalCost USD/kW (MUSD/GW); FixedCost USD/kW-yr; VariableCost USD/GJ (MUSD/PJ) = USD/MWh / 3.6.
"""
import csv
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
BAU = HERE.parents[1] / "Honduras" / "HON_ENERGY" / "A2_Output_Params" / "BAU"
YEARS = list(range(2018, 2051))
MWH = 3.6  # GJ per MWh

cur = {}
for p in ["CapitalCost", "FixedCost", "VariableCost"]:
    d = pd.read_csv(BAU / f"{p}.csv")
    for r in d.itertuples():
        cur[(r.TECHNOLOGY, p, int(r.YEAR))] = float(r.Value)

atb = pd.read_csv(HERE / "atb2024_series.csv")
def atb_series(tech, detail, param):
    d = atb[(atb.technology == tech) & (atb.techdetail == detail) & (atb.core_metric_parameter == param)]
    return {int(y): float(v) for y, v in zip(d.year, d.value)}
def atb_at(s, y):
    return s[min(max(y, min(s)), max(s))]
IDX = {
    "PVB": ("Utility-Scale PV-Plus-Battery", "Class1"),
    "WIND": ("LandbasedWind", "Class4"),
    "UPV": ("UtilityPV", "Class1"),
}
def idx(key, param, y):
    s = atb_series(*IDX[key], param)
    return atb_at(s, y) / s[2024]

# ---- cited edition: ODS PIEG 2024-2033 (HON-018 Tabla 7, PDF p.42; CSH-010 Anexos Tablas B-2 p.18 and B-3 p.19) ----
B2_CAP = {2023: 1254.72, 2024: 1139.23, 2025: 1061.07, 2026: 1009.66, 2027: 970.86, 2028: 937.18, 2029: 911.54, 2030: 892.37, 2031: 876.24,
          2032: 861.52, 2033: 847.17, 2034: 832.55, 2035: 818.15, 2036: 809.59, 2037: 801.27, 2038: 793.16, 2039: 784.88, 2040: 777.10,
          2041: 769.21, 2042: 760.78}
B2_FOM = {2023: 25.36, 2024: 25.27, 2025: 25.19, 2026: 25.11, 2027: 25.03, 2028: 24.95, 2029: 24.88, 2030: 24.80, 2031: 24.73, 2032: 24.66,
          2033: 24.58, 2034: 24.52, 2035: 24.45, 2036: 24.38, 2037: 24.31, 2038: 24.25, 2039: 24.19, 2040: 24.12, 2041: 24.06, 2042: 24.00}
B3_CAP = {2023: 1716.52, 2024: 1597.70, 2025: 1528.71, 2026: 1494.58, 2027: 1477.70, 2028: 1465.84, 2029: 1454.16, 2030: 1441.99, 2031: 1429.09,
          2032: 1417.76, 2033: 1407.20, 2034: 1395.73, 2035: 1383.85, 2036: 1374.28, 2037: 1365.15, 2038: 1356.37, 2039: 1347.17, 2040: 1338.98,
          2041: 1330.49, 2042: 1320.81}
B3_FOM = {2023: 36.37, 2024: 36.27, 2025: 36.18, 2026: 36.10, 2027: 36.01, 2028: 35.92, 2029: 35.84, 2030: 35.76, 2031: 35.68, 2032: 35.60,
          2033: 35.52, 2034: 35.44, 2035: 35.37, 2036: 35.29, 2037: 35.22, 2038: 35.15, 2039: 35.08, 2040: 35.01, 2041: 34.94, 2042: 34.88}
def path(tbl, y):
    return tbl[min(max(y, 2023), 2042)]

T7 = "HON-018"; T7LOC = "Tabla 7 (PDF page 42, printed 42 of 104), row"
OLD = {  # (tech, param): (function of year, source ids, locator/derivation text)
    ("PPBIM", "CapitalCost"): None, ("PPBIM", "FixedCost"): None, ("PPBIM", "VariableCost"): None,
    ("PPCOK", "CapitalCost"): (lambda y: 4769.52, T7, f"{T7LOC} Carbon 30 MW: 4,769.52 USD/kW (2023 USD)"),
    ("PPCOK", "FixedCost"): (lambda y: 45.68, T7, f"{T7LOC} Carbon 30 MW: 45.68 USD/kW-yr"),
    ("PPCOK", "VariableCost"): (lambda y: 5.06 / MWH, T7, f"{T7LOC} Carbon 30 MW: 5.06 USD/MWh / 3.6 = 1.4056 USD/GJ"),
    ("PPFOI", "CapitalCost"): (lambda y: 984.08, T7, f"{T7LOC} Motor bunker 100 MW: 984.08 USD/kW (2023 USD)"),
    ("PPFOI", "FixedCost"): (lambda y: 39.57, T7, f"{T7LOC} Motor bunker 100 MW: 39.57 USD/kW-yr"),
    ("PPFOI", "VariableCost"): (lambda y: 6.40 / MWH, T7, f"{T7LOC} Motor bunker 100 MW: 6.40 USD/MWh / 3.6 = 1.7778 USD/GJ"),
    ("PPGEO", "CapitalCost"): (lambda y: 5900.0, T7, f"{T7LOC} Geotermica 20 MW: 5,900.00 USD/kW (2023 USD)"),
    ("PPGEO", "FixedCost"): (lambda y: 153.98, T7, f"{T7LOC} Geotermica 20 MW: 153.98 USD/kW-yr"),
    ("PPGEO", "VariableCost"): (lambda y: 1.31 / MWH, T7, f"{T7LOC} Geotermica 20 MW: 1.31 USD/MWh / 3.6 = 0.3639 USD/GJ"),
    ("PPGTDSL", "CapitalCost"): (lambda y: 1204.83, T7, f"{T7LOC} CCGN 250 MW: 1,204.83 USD/kW (2023 USD); the number is the combined cycle row"),
    ("PPGTDSL", "FixedCost"): (lambda y: 13.73, T7, f"{T7LOC} CCGN 250 MW: 13.73 USD/kW-yr; the number is the combined cycle row"),
    ("PPGTDSL", "VariableCost"): (lambda y: 2.10 / MWH, T7, f"{T7LOC} CCGN 250 MW: 2.10 USD/MWh / 3.6 = 0.5833 USD/GJ; the number is the combined cycle row"),
    ("PPGTGLP", "CapitalCost"): (lambda y: 1204.83, T7, f"{T7LOC} CCGN 250 MW: 1,204.83 USD/kW (2023 USD); the number is the combined cycle row (LPG 30 MW row: 1,024.63)"),
    ("PPGTGLP", "FixedCost"): (lambda y: 18.35, T7, f"{T7LOC} LPG 30 MW: 18.35 USD/kW-yr"),
    ("PPGTGLP", "VariableCost"): (lambda y: 5.29 / MWH, T7, f"{T7LOC} LPG 30 MW: 5.29 USD/MWh / 3.6 = 1.4694 USD/GJ"),
    ("PPHDAM", "CapitalCost"): (lambda y: 3576.0, T7, f"{T7LOC} Hidroelectrica de embalse >100 MW: 3,576.00 USD/kW (2023 USD)"),
    ("PPHDAM", "FixedCost"): (lambda y: 47.06, T7, f"{T7LOC} Hidroelectrica de embalse >100 MW: 47.06 USD/kW-yr"),
    ("PPHROR", "CapitalCost"): (lambda y: 2000.0, T7, f"{T7LOC} Hidroelectrica de pasada 4-10 MW: 2,000.00 USD/kW (2023 USD)"),
    ("PPHROR", "FixedCost"): (lambda y: 47.06, T7, f"{T7LOC} Hidroelectrica de pasada 4-10 MW: 47.06 USD/kW-yr"),
    ("PPICEDSL", "CapitalCost"): (lambda y: 966.72, T7, f"{T7LOC} Motor diesel 80 MW: 966.72 USD/kW (2023 USD)"),
    ("PPICEDSL", "FixedCost"): (lambda y: 39.57, T7, f"{T7LOC} Motor diesel 80 MW: 39.57 USD/kW-yr"),
    ("PPICEDSL", "VariableCost"): (lambda y: 6.40 / MWH, T7, f"{T7LOC} Motor diesel 80 MW: 6.40 USD/MWh / 3.6 = 1.7778 USD/GJ"),
    ("PPPVD", "CapitalCost"): (lambda y: 871.80, T7, f"{T7LOC} Solar FV 20-50 MW: 871.80 USD/kW (2023 USD); utility-scale row; model holds it flat (Flat mode)"),
    ("PPPVD", "FixedCost"): None,
    ("PPPVD", "VariableCost"): (lambda y: 0.0, T7, f"{T7LOC} Solar FV: 0.00 USD/MWh"),
    ("PPPVT", "CapitalCost"): (lambda y: path(B2_CAP, y), T7 + ";CSH-010", "Tabla 7 row Solar FV + Bateria 50 MW: 1,254.72 USD/kW (2023 USD); path: Anexos Tabla B-2 (PDF page 18), column Central 50 MW, 2023 to 2042, held at the 2023 value before and at the 2042 value after"),
    ("PPPVT", "FixedCost"): (lambda y: path(B2_FOM, y), T7 + ";CSH-010", "Tabla 7 row Solar FV + Bateria 50 MW: 25.36 USD/kW-yr; path: Anexos Tabla B-2, column Central 50 MW (the model applies it one year later; within 2 percent)"),
    ("PPPVT", "VariableCost"): (lambda y: 0.0, T7, f"{T7LOC} Solar FV + Bateria: 0.00 USD/MWh"),
    ("PPWNDON", "CapitalCost"): (lambda y: path(B3_CAP, y), T7 + ";CSH-010", "Tabla 7 row Eolica + Bateria 20 to 120 MW: 1,716.52 USD/kW (2023 USD); path: Anexos Tabla B-3 (PDF page 19), 2023 to 2042, held at the 2023 value before and at the 2042 value after"),
    ("PPWNDON", "FixedCost"): (lambda y: path(B3_FOM, y), T7 + ";CSH-010", "Tabla 7 row Eolica + Bateria: 36.37 USD/kW-yr; path: Anexos Tabla B-3"),
    ("PPWNDON", "VariableCost"): (lambda y: 0.0, T7, f"{T7LOC} Eolica + Bateria: 0.00 USD/MWh"),
}
T19 = "HON-016"; T19LOC = "PIEG 2026-2035 Tabla 19 (PDF page 46, 2024 USD), row"
NEW = {
    ("PPCOK", "CapitalCost"): None, ("PPCOK", "FixedCost"): None, ("PPCOK", "VariableCost"): None,
    ("PPFOI", "CapitalCost"): (lambda y: 1269.20, T19, f"{T19LOC} Motor de combustion interna a gas natural/bunker/diesel 100 MW: 1,269.20 USD/kW"),
    ("PPFOI", "FixedCost"): (lambda y: 14.00, T19, f"{T19LOC} same row: 14.00 USD/kW-yr"),
    ("PPFOI", "VariableCost"): (lambda y: 7.0 / MWH, T19, f"{T19LOC} same row: 7 USD/MWh for bunker / 3.6 = 1.9444 USD/GJ"),
    ("PPICEDSL", "CapitalCost"): (lambda y: 1269.20, T19, f"{T19LOC} Motor de combustion interna a gas natural/bunker/diesel 100 MW (nearest to the 80 MW diesel row of the cited edition): 1,269.20 USD/kW"),
    ("PPICEDSL", "FixedCost"): (lambda y: 14.00, T19, f"{T19LOC} same row: 14.00 USD/kW-yr"),
    ("PPICEDSL", "VariableCost"): (lambda y: 5.0 / MWH, T19, f"{T19LOC} same row: 5 USD/MWh for diesel / 3.6 = 1.3889 USD/GJ"),
    ("PPGEO", "CapitalCost"): (lambda y: 6179.24, T19, f"{T19LOC} Geotermica 20 MW: 6,179.24 USD/kW"),
    ("PPGEO", "FixedCost"): (lambda y: 160.66, T19, f"{T19LOC} Geotermica 20 MW: 160.66 USD/kW-yr"),
    ("PPGEO", "VariableCost"): (lambda y: 1.50 / MWH, T19, f"{T19LOC} Geotermica 20 MW: 1.50 USD/MWh / 3.6 = 0.4167 USD/GJ"),
    ("PPGTDSL", "CapitalCost"): (lambda y: 1437.59, T19, f"{T19LOC} Turbina de gas en ciclo combinado a gas natural 250 MW (newer edition of the cited CCGN row): 1,437.59 USD/kW"),
    ("PPGTDSL", "FixedCost"): (lambda y: 16.00, T19, f"{T19LOC} same row: 16.00 USD/kW-yr"),
    ("PPGTDSL", "VariableCost"): (lambda y: 3.5 / MWH, T19, f"{T19LOC} same row: 3.5 USD/MWh / 3.6 = 0.9722 USD/GJ"),
    ("PPGTGLP", "CapitalCost"): (lambda y: 1437.59, T19, f"{T19LOC} Turbina de gas en ciclo combinado a gas natural 250 MW (newer edition of the cited CCGN row): 1,437.59 USD/kW"),
    ("PPGTGLP", "FixedCost"): (lambda y: 20.00, T19, f"{T19LOC} Turbina de gas en ciclo abierto a gas natural/diesel/LPG 30 MW (newer edition of the cited LPG row): 20.00 USD/kW-yr"),
    ("PPGTGLP", "VariableCost"): (lambda y: 6.0 / MWH, T19, f"{T19LOC} same row: 6.00 USD/MWh / 3.6 = 1.6667 USD/GJ"),
    ("PPHDAM", "CapitalCost"): (lambda y: 5100.0, T19, f"{T19LOC} Hidroelectrica de embalse >100 MW: 5,100.00 USD/kW"),
    ("PPHDAM", "FixedCost"): (lambda y: 37.93, T19, f"{T19LOC} Hidroelectrica de embalse >100 MW: 37.93 USD/kW-yr"),
    ("PPHROR", "CapitalCost"): (lambda y: 3786.50, T19, f"{T19LOC} Hidroelectrica de pasada <10 MW: 3,786.50 USD/kW"),
    ("PPHROR", "FixedCost"): (lambda y: 40.00, T19, f"{T19LOC} Hidroelectrica de pasada <10 MW: 40.00 USD/kW-yr"),
    ("PPPVD", "CapitalCost"): (lambda y: 1138.48 * idx("UPV", "OCC", y), T19 + ";HON-017;CSH-013",
                               f"{T19LOC} Solar fotovoltaica 50 MW: 1,138.48 USD/kW in 2024, times the NREL ATB 2024 UtilityPV Class1 Moderate OCC index (year / 2024), as the ODS Anexos A.2.2 states; years before 2024 not used"),
    ("PPPVT", "CapitalCost"): (lambda y: 1434.72 * idx("PVB", "OCC", y), T19 + ";HON-017;CSH-013",
                               f"{T19LOC} Central hibrida Solar fotovoltaica con bateria (30%) 50 MW (newer edition of the cited Solar FV + Bateria 50 MW row): 1,434.72 USD/kW in 2024, times the NREL ATB 2024 Utility-Scale PV-Plus-Battery Class1 Moderate OCC index (year / 2024), as the ODS Anexos A.2 states"),
    ("PPPVT", "FixedCost"): (lambda y: 40.31 * idx("PVB", "Fixed O&M", y), T19 + ";HON-017;CSH-013",
                             f"{T19LOC} same row: 40.31 USD/kW-yr in 2024, times the ATB 2024 PV-Plus-Battery Class1 Moderate Fixed O&M index (year / 2024)"),
    ("PPWNDON", "CapitalCost"): (lambda y: 1868.76 * idx("WIND", "OCC", y), T19 + ";HON-017;CSH-013",
                                 f"{T19LOC} Central hibrida Eolica con bateria (10%) 50 MW (newer edition of the cited Eolica + Bateria row): 1,868.76 USD/kW in 2024, times the NREL ATB 2024 LandbasedWind Class4 Moderate OCC index (year / 2024), as the ODS Anexos A.2.1 states"),
    ("PPWNDON", "FixedCost"): (lambda y: 41.14 * idx("WIND", "Fixed O&M", y), T19 + ";HON-017;CSH-013",
                               f"{T19LOC} same row: 41.14 USD/kW-yr in 2024, times the ATB 2024 LandbasedWind Class4 Moderate Fixed O&M index (year / 2024)"),
}
# rows whose current value is 0 or empty and match both editions at 0
ZERO_KEEP = {("PPPVD", "VariableCost"), ("PPPVT", "VariableCost"), ("PPWNDON", "VariableCost")}
ZERO_FILL = {("PPHDAM", "VariableCost"): "PIEG 2026-2035 Tabla 19 (PDF page 46), row Hidroelectrica de embalse: 0.00 USD/MWh (the 2024-2033 edition, Tabla 7, gave 1.57 USD/MWh)",
             ("PPHROR", "VariableCost"): "PIEG 2026-2035 Tabla 19 (PDF page 46), row Hidroelectrica de pasada: 0.00 USD/MWh (the 2024-2033 edition, Tabla 7, gave 1.57 USD/MWh)"}

# replacements (no source gives the current number)
bio_occ = atb_series("Biopower", "Dedicated", "OCC")
bio_fom = atb_series("Biopower", "Dedicated", "Fixed O&M")
res_fom = atb_series("ResPV", "Class1", "Fixed O&M")
REPL = {
    ("PPBIM", "CapitalCost"): (lambda y: 2162.0 * atb_at(bio_occ, y) / bio_occ[2022], "CSH-011;CSH-013",
                               "IRENA 2022 Table H.1 (page 15): bioenergy global weighted average total installed cost 2,162 USD/kW in 2022 (2022 USD), times the NREL ATB 2024 Biopower Dedicated Moderate OCC index (year / 2022); years before 2022 held at 2,162"),
    ("PPBIM", "FixedCost"): (lambda y: atb_at(bio_fom, y), "CSH-013;CSH-011",
                             "NREL ATB 2024 Biopower Dedicated Moderate Fixed O&M 163.67 USD/kW-yr (2022 USD), constant; IRENA 2022 (page 183) gives fixed O&M only as 2 to 6 percent of installed cost per year, IEA WEO 2023 Annex B and both ODS plans have no bioenergy row"),
    ("PPBIM", "VariableCost"): (lambda y: 0.005 * 1000 / MWH, "CSH-011",
                                "IRENA 2022 page 183: bioenergy variable O&M average 0.005 USD/kWh = 5 USD/MWh / 3.6 = 1.3889 USD/GJ"),
    ("PPPVD", "FixedCost"): (lambda y: atb_at(res_fom, y), "CSH-013",
                             "NREL ATB 2024 ResPV Class1 Moderate Fixed O&M (2022 USD), yearly 2022 to 2050, years before 2022 held at the 2022 value; IRENA 2022 and 2025, IEA WEO 2023 Annex B and both ODS plans give no distributed PV O&M"),
}
CLASS_LEVEL = {}  # (tech, param) -> P2 class on the level

rows = []
PLANTS = ["PPBIM", "PPCOK", "PPFOI", "PPGEO", "PPGTDSL", "PPGTGLP", "PPHDAM", "PPHROR", "PPICEDSL", "PPPVD", "PPPVT", "PPWNDON"]
for t in PLANTS:
    for p in ["CapitalCost", "FixedCost", "VariableCost"]:
        k = (t, p)
        for y in YEARS:
            c = cur.get((t, p, y))
            rec = dict(technology=t, parameter=p, year=y, current_value="" if c is None else round(c, 6))
            if k in REPL:
                f, sid, der = REPL[k]
                v = f(y)
                rec.update(proposed_value=round(v, 4), p2_class="replace", change_class="replace" if c is not None else "fill_empty",
                           basis_class="replace", source_ids=sid, derivation=der)
            elif k in ZERO_KEEP:
                rec.update(proposed_value=0.0, p2_class="matched", change_class="keep", basis_class="matched", source_ids="HON-018;HON-016",
                           derivation=OLD[k][2] + "; PIEG 2026-2035 Tabla 19 (PDF page 46) also gives 0.00 USD/MWh")
            elif k in ZERO_FILL:
                rec.update(proposed_value=0.0, p2_class="matched", change_class="fill_empty" if c is None else "keep", basis_class="matched",
                           source_ids="HON-016;HON-018", derivation=ZERO_FILL[k])
            else:
                fo, sido, dero = OLD[k]
                ov = fo(y)
                matched = c is not None and abs(c / ov - 1) <= 0.02 if ov else (c == 0)
                if not matched:
                    raise SystemExit(f"not matched: {k} {y} current {c} source {ov}")
                newk = NEW.get(k)
                if newk is None or y <= 2023:
                    rec.update(proposed_value=round(c, 6), p2_class="matched", change_class="keep", basis_class="matched", source_ids=sido,
                               derivation=dero + (f" (year {y}: {ov:.4f})" if "path" in dero else ""))
                else:
                    fn, sidn, dern = newk
                    v = fn(y)
                    rec.update(proposed_value=round(v, 4), p2_class="matched, newer edition", change_class="upgrade",
                               basis_class="matched, newer edition", source_ids=sido + ";" + sidn,
                               derivation=f"current value matches the cited edition ({dero}); newer edition: {dern}")
            rec["assumption_sentence"] = ""
            rows.append(rec)

with open(HERE / "plant_costs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
d = pd.DataFrame(rows)
s = d[d.year.isin([2024, 2030, 2050])].pivot_table(index=["technology", "parameter"], columns="year", values="proposed_value", aggfunc="first")
c = d[d.year.isin([2024])].set_index(["technology", "parameter"])[["current_value", "p2_class"]]
print(s.join(c).to_string())
print(d.change_class.value_counts().to_dict())
