"""Step 5 and 6: plant CapitalCost, FixedCost and VariableCost for the Dominican Republic (rules P1 to P3).

For every plant in scope, parameter and year column (2018-2050) the effective current value (BAU compiled
CSV; the workbook cell where it is filled) is compared with candidate source values in P1 order. A cell is
`matched` when a candidate is within 2 percent; `matched, newer edition` when it matches the cited edition and
the newer edition of the same table differs; otherwise `replace` (or `fill_placeholder` for zero placeholders)
with the proposal rule stated per technology. Output: plant_costs.csv, plant_summary.csv.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import *

YEARS = list(range(2018, 2051))
TOL = 0.02
ATB_DL = os.path.join(DL, "atb")

# ---------- current values ----------
cur_rows = pd.read_csv(os.path.join(JOB, "cost_rows_current.csv"))
bau = {p: pd.read_csv(os.path.join(BAU, p + ".csv")) for p in COST_PARAMS}
def effective(tech, par, y):
    d = bau[par]; s = d[(d.TECHNOLOGY == tech) & (d.YEAR == y)].Value
    return float(s.iloc[0]) if len(s) else 0.0
def cell(tech, par, y):
    r = cur_rows[(cur_rows.Tech == tech) & (cur_rows.Parameter == par)]
    if not len(r): return None, None, None
    v = r[str(y)].iloc[0]
    return (None if pd.isna(v) else float(v)), r["sheet"].iloc[0], r["Projection.Mode"].iloc[0]

# ---------- ATB series ----------
def atb_loader(fname):
    d = pd.read_parquet(os.path.join(ATB_DL, fname))
    return d[(d.core_metric_case == "Market") & (d.scenario == "Moderate") & (d.crpyears.astype(str) == "20")]
A23, A24 = atb_loader("ATBe_2023.parquet"), atb_loader("ATBe_2024_v3.0.0.parquet")
def atb(d, tech, td, par):
    s = d[(d.technology == tech) & (d.techdetail == td) & (d.core_metric_parameter == par)]
    s = s.groupby("core_metric_variable").value.first()
    s.index = s.index.astype(int)
    first = s.index.min()
    return {y: float(s[y]) if y in s.index else (float(s[first]) if y < first else float(s[s.index.max()])) for y in YEARS}, int(first)
def flat(v): return {y: v for y in YEARS}
def at(v, y0): return {y0: v}

SID = {"PEN": "CSD-008", "IRENA22": "CSD-009", "IRENA24": "CSD-010", "ATB23": "CSD-011", "ATB24": "CSD-012", "WEO25": "CSD-005"}
LOC = {
    "PEN220": "PEN 2022-2037, Tabla 220 Supuestos proyecto generico Ciclo combinado gas natural, page 345",
    "PEN223": "PEN 2022-2037, Tabla 223 Supuestos proyecto generico Turbina de vapor (carbon USC), page 347",
    "PEN229": "PEN 2022-2037, Tabla 229 Supuestos proyecto generico Motores combustion interna, page 350",
    "IRENA22_H1": "IRENA Renewable Power Generation Costs in 2022, Table H.1, page 15 (2022 USD/kW, 2022 column)",
    "IRENA24_S1": "IRENA Renewable Power Generation Costs in 2024, Table S1, page 15 (2024 USD/kW, 2024 column)",
    "IRENA22_HYD_OM": "IRENA Renewable Power Generation Costs in 2022, chapter 6 Hydropower, Operation and maintenance costs, page 162",
    "IRENA22_BIO_OM": "IRENA Renewable Power Generation Costs in 2022, chapter 8 Bioenergy, Operation and maintenance costs, page 183",
}
def atb_loc(ed, tech, td, par):
    return f"NREL ATB {ed} electricity data (ATBe.parquet), technology {tech}, techdetail {td}, {par}, scenario Moderate, case Market, crpyears 20"

# ---------- candidate and proposal definitions ----------
# candidate: (label, sid, locator, series, newer) where newer = (label, sid, locator, series) or None
def C(label, sid, loc, series, newer=None): return dict(label=label, sid=sid, loc=loc, series=series, newer=newer)

pen = {
    "220_cap": 1084.0, "220_fc": 14100 / 1000, "220_vc": 2.55 / 3.6,
    "223_cap": 3676.0, "223_fc": 40580 / 1000, "223_vc": 4.50 / 3.6,
    "229_cap": 1100.0, "229_fc": 35160 / 1000, "229_vc": 5.69 / 3.6,
}
PEN_DER = {
    "220_cap": "Costo Desarrollo 1084 USD/kW = 1084 MUSD/GW", "220_fc": "Costo Fijo O&M 14,100 USD/MW-yr / 1000 = 14.1 USD/kW-yr",
    "220_vc": "Costo Variable O&M 2.55 USD/MWh / 3.6 GJ per MWh = 0.708333 USD/GJ",
    "223_cap": "Costo Desarrollo 3,676 USD/kW", "223_fc": "Costo Fijo O&M 40,580 USD/MW-yr / 1000 = 40.58 USD/kW-yr",
    "223_vc": "Costo Variable O&M 4.50 USD/MWh / 3.6 = 1.25 USD/GJ",
    "229_cap": "Costo Desarrollo 1,100 USD/kW", "229_fc": "Costo Fijo O&M 35,160 USD/MW-yr / 1000 = 35.16 USD/kW-yr",
    "229_vc": "Costo Variable O&M 5.69 USD/MWh / 3.6 = 1.580556 USD/GJ",
}
def penC(k):
    t = k.split("_")[0]
    return C(f"PEN Tabla {t}", SID["PEN"], LOC["PEN" + t] + "; " + PEN_DER[k], flat(pen[k]))

ngcc24, ng0 = atb(A24, "NaturalGas_FE", "NG 2-on-1 Combined Cycle (F-Frame)", "CAPEX")
upv24, _ = atb(A24, "UtilityPV", "Class1", "CAPEX"); upv24f, _ = atb(A24, "UtilityPV", "Class1", "Fixed O&M")
lbw24, _ = atb(A24, "LandbasedWind", "Class1", "CAPEX"); lbw24f, _ = atb(A24, "LandbasedWind", "Class1", "Fixed O&M")
bat24, _ = atb(A24, "Utility-Scale Battery Storage", "4Hr Battery Storage", "CAPEX")
bat24f, _ = atb(A24, "Utility-Scale Battery Storage", "4Hr Battery Storage", "Fixed O&M")
bat23occ, _ = atb(A23, "Utility-Scale Battery Storage", "4Hr Battery Storage", "OCC")
bat23f, _ = atb(A23, "Utility-Scale Battery Storage", "4Hr Battery Storage", "Fixed O&M")
npd23, _ = atb(A23, "Hydropower", "NPD1", "CAPEX"); npd24, _ = atb(A24, "Hydropower", "NPD1", "CAPEX")
npd23f, _ = atb(A23, "Hydropower", "NPD1", "Fixed O&M"); npd24f, _ = atb(A24, "Hydropower", "NPD1", "Fixed O&M")
cpv23, _ = atb(A23, "CommPV", "Class1", "CAPEX"); cpv24, _ = atb(A24, "CommPV", "Class1", "CAPEX")
cpv23f, _ = atb(A23, "CommPV", "Class1", "Fixed O&M"); cpv24f, _ = atb(A24, "CommPV", "Class1", "Fixed O&M")

IRENA22 = {"pv": 876.0, "wind": 1274.0, "hydro": 2881.0, "bio": 2162.0}
IRENA24 = {"pv": 691.0, "wind": 1041.0, "hydro": 2267.0, "bio": 3242.0}

def path_scale(level, ref, base_year):
    return {y: (level if y <= base_year else level * ref[y] / ref[base_year]) for y in YEARS}

TECH_ROWS = {}
THERMAL_220 = ["PPADSL", "PPAFOI", "PPANGS", "PPDBGS", "PPDBIM", "PPDDSL", "PPDFOI", "PPDGLP", "PPDGSL", "PPDNGS", "PPCCTNGS", "PPICEGASFOI"]
cap_220_prop = path_scale(1084.0, ngcc24, 2022)
for t in THERMAL_220:
    TECH_ROWS[t] = {
        "CapitalCost": dict(cands=[penC("220_cap")], prop=cap_220_prop, prop_sid=f"{SID['PEN']};{SID['ATB24']}",
            prop_der="1084 USD/kW (PEN Tabla 220, page 345) for 2018-2022; from 2023: 1084 x ATB 2024 NG 2-on-1 Combined Cycle (F-Frame) CAPEX(y) / CAPEX(2022), Moderate, Market, crpyears 20"),
        "FixedCost": dict(cands=[penC("220_fc")], prop=flat(pen["220_fc"]), prop_sid=SID["PEN"], prop_der=PEN_DER["220_fc"] + " (PEN Tabla 220, page 345), held flat"),
        "VariableCost": dict(cands=[penC("220_vc"), penC("229_vc")], prop=flat(pen["220_vc"]), prop_sid=SID["PEN"], prop_der=PEN_DER["220_vc"] + " (PEN Tabla 220, page 345), held flat"),
    }
TECH_ROWS["PPCCTDSL"] = {
    "CapitalCost": dict(cands=[penC("229_cap"), penC("220_cap")], prop=flat(1100.0), prop_sid=SID["PEN"], prop_der=PEN_DER["229_cap"]),
    "FixedCost": dict(cands=[penC("229_fc"), penC("220_fc")], prop=flat(pen["229_fc"]), prop_sid=SID["PEN"], prop_der=PEN_DER["229_fc"]),
    "VariableCost": dict(cands=[penC("220_vc"), penC("229_vc")], prop=flat(pen["220_vc"]), prop_sid=SID["PEN"],
        prop_der=PEN_DER["220_vc"] + " (PEN Tabla 220, the national plan's combined cycle, which can run on liquid fuel), held flat"),
}
TECH_ROWS["PPICEFOI"] = {
    "CapitalCost": dict(cands=[penC("229_cap")], prop=flat(1100.0), prop_sid=SID["PEN"], prop_der=PEN_DER["229_cap"]),
    "FixedCost": dict(cands=[penC("229_fc")], prop=flat(pen["229_fc"]), prop_sid=SID["PEN"], prop_der=PEN_DER["229_fc"]),
    "VariableCost": dict(cands=[penC("229_vc")], prop=flat(pen["229_vc"]), prop_sid=SID["PEN"], prop_der=PEN_DER["229_vc"] + " (PEN Tabla 229, page 350), held flat"),
}
TECH_ROWS["PPCOA"] = {
    "CapitalCost": dict(cands=[penC("223_cap")], prop=flat(3676.0), prop_sid=SID["PEN"], prop_der=PEN_DER["223_cap"]),
    "FixedCost": dict(cands=[penC("223_fc")], prop=flat(pen["223_fc"]), prop_sid=SID["PEN"], prop_der=PEN_DER["223_fc"] + " (PEN Tabla 223, page 347), held flat"),
    "VariableCost": dict(cands=[penC("223_vc")], prop=flat(pen["223_vc"]), prop_sid=SID["PEN"], prop_der=PEN_DER["223_vc"] + " (PEN Tabla 223, page 347), held flat"),
}
ZERO_VOM_DER = "the source publishes no variable O&M for this technology (all O&M is in Fixed O&M), so non-fuel variable O&M is 0"
def zeroC(label, sid, loc): return C(label, sid, loc + "; " + ZERO_VOM_DER, flat(0.0))
TECH_ROWS["PPHDAM"] = {
    "CapitalCost": dict(cands=[C("ATB 2023 Hydropower NPD1", SID["ATB23"], atb_loc(2023, "Hydropower", "NPD1", "CAPEX") + "; values before 2021 held at 2021", npd23,
                                 newer=("ATB 2024 Hydropower NPD1", SID["ATB24"], atb_loc(2024, "Hydropower", "NPD1", "CAPEX") + "; values before 2022 held at 2022", npd24))],
                        prop=npd24, prop_sid=SID["ATB24"], prop_der=atb_loc(2024, "Hydropower", "NPD1", "CAPEX")),
    "FixedCost": dict(cands=[C("ATB 2023 Hydropower NPD1", SID["ATB23"], atb_loc(2023, "Hydropower", "NPD1", "Fixed O&M"), npd23f,
                               newer=("ATB 2024 Hydropower NPD1", SID["ATB24"], atb_loc(2024, "Hydropower", "NPD1", "Fixed O&M"), npd24f))],
                      prop=npd24f, prop_sid=SID["ATB24"], prop_der=atb_loc(2024, "Hydropower", "NPD1", "Fixed O&M")),
    "VariableCost": dict(cands=[zeroC("ATB 2023 Hydropower", SID["ATB23"], atb_loc(2023, "Hydropower", "NPD1", "parameter list"))], prop=flat(0.0), prop_sid=SID["ATB23"], prop_der=ZERO_VOM_DER),
}
TECH_ROWS["PPPVD"] = {
    "CapitalCost": dict(cands=[C("ATB 2023 CommPV Class1", SID["ATB23"], atb_loc(2023, "CommPV", "Class1", "CAPEX") + "; values before 2021 held at 2021", cpv23,
                                 newer=("ATB 2024 CommPV Class1", SID["ATB24"], atb_loc(2024, "CommPV", "Class1", "CAPEX") + "; values before 2022 held at 2022", cpv24))],
                        prop=cpv24, prop_sid=SID["ATB24"], prop_der=atb_loc(2024, "CommPV", "Class1", "CAPEX")),
    "FixedCost": dict(cands=[C("ATB 2023 CommPV Class1", SID["ATB23"], atb_loc(2023, "CommPV", "Class1", "Fixed O&M"), cpv23f,
                               newer=("ATB 2024 CommPV Class1", SID["ATB24"], atb_loc(2024, "CommPV", "Class1", "Fixed O&M"), cpv24f))],
                      prop=cpv24f, prop_sid=SID["ATB24"], prop_der=atb_loc(2024, "CommPV", "Class1", "Fixed O&M") + " (ATB 2023 path where the current flat value does not match it)"),
    "VariableCost": dict(cands=[zeroC("ATB 2023 CommPV", SID["ATB23"], atb_loc(2023, "CommPV", "Class1", "parameter list"))], prop=flat(0.0), prop_sid=SID["ATB23"], prop_der=ZERO_VOM_DER),
}
hyd_fc = IRENA22["hydro"] * 0.025
TECH_ROWS["PPDHYD"] = {
    "CapitalCost": dict(cands=[C("IRENA 2022 hydropower", SID["IRENA22"], LOC["IRENA22_H1"], at(IRENA22["hydro"], 2022))],
                        prop=flat(IRENA22["hydro"]), prop_sid=SID["IRENA22"],
                        prop_der="IRENA 2022 global weighted average total installed cost of hydropower 2,881 USD/kW (2022 USD), held flat; newer edition (IRENA 2024): 2,267 USD/kW (2024 USD)"),
    "FixedCost": dict(cands=[], prop=flat(hyd_fc), prop_sid=SID["IRENA22"],
                      prop_der="2,881 USD/kW (IRENA 2022 Table H.1) x 2.5 percent per year (IEA average O&M share quoted in IRENA 2022, page 162; 2.2 to 3 percent for smaller projects) = 72.025 USD/kW-yr"),
    "VariableCost": dict(cands=[C("IRENA 2022 hydropower O&M", SID["IRENA22"], LOC["IRENA22_HYD_OM"] + "; O&M is quoted as an annual share of investment, so variable O&M is 0", flat(0.0))], prop=flat(0.0), prop_sid=SID["IRENA22"], prop_der="O&M is quoted only as an annual share of investment (fixed), variable O&M 0"),
}
def pvwind(kind, lvl22, a24, a24f, irena_lbl, atb_tech):
    cap = {y: (lvl22 if y <= 2022 else lvl22 * a24[y] / a24[2022]) + (bat24[y] if y >= 2025 else 0.0) for y in YEARS}
    fc = {y: a24f[y] + (bat24f[y] if y >= 2025 else 0.0) for y in YEARS}
    return {
        "CapitalCost": dict(cands=[C(irena_lbl, SID["IRENA22"], LOC["IRENA22_H1"], at(lvl22, 2022))], prop=cap, prop_sid=f"{SID['IRENA22']};{SID['ATB24']}",
            prop_der=(f"{lvl22:.0f} USD/kW (IRENA 2022 Table H.1, 2022 global weighted average, {kind}) for 2018-2022; from 2023: {lvl22:.0f} x ATB 2024 {atb_tech} Class1 CAPEX(y)/CAPEX(2022) "
                      "(Moderate, Market, crpyears 20); from 2025 plus the ATB 2024 Utility-Scale Battery Storage 4Hr CAPEX(y) (Moderate, Market, crpyears 20), keeping the storage adder that the current row applies from 2025")),
        "FixedCost": dict(cands=[], prop=fc, prop_sid=SID["ATB24"],
            prop_der=f"ATB 2024 {atb_tech} Class1 Fixed O&M(y); from 2025 plus ATB 2024 Utility-Scale Battery Storage 4Hr Fixed O&M(y) (Moderate, Market, crpyears 20)"),
        "VariableCost": dict(cands=[zeroC(f"ATB 2024 {atb_tech}", SID["ATB24"], atb_loc(2024, atb_tech, "Class1", "parameter list"))], prop=flat(0.0), prop_sid=SID["ATB24"], prop_der=ZERO_VOM_DER),
    }
TECH_ROWS["PPPVT"] = pvwind("solar PV", IRENA22["pv"], upv24, upv24f, "IRENA 2022 solar PV", "UtilityPV")
TECH_ROWS["PPPVTHYD"] = pvwind("solar PV", IRENA22["pv"], upv24, upv24f, "IRENA 2022 solar PV", "UtilityPV")
TECH_ROWS["PPWNDON"] = pvwind("onshore wind", IRENA22["wind"], lbw24, lbw24f, "IRENA 2022 onshore wind", "LandbasedWind")
bio24f, _ = atb(A24, "Biopower", "Dedicated", "Fixed O&M")
BIO_FC_DER = ("ATB 2024 Biopower Dedicated Fixed O&M 163.666 USD/kW-yr (Moderate, Market, crpyears 20), the first source in P1 order that "
              "publishes a value (IRENA 2022, page 183, gives only a range of 2 to 6 percent of total installed cost per year, 43.24 to 129.72 USD/kW-yr at 2,162 USD/kW)")
BGS_FC_SENT = ("ASSUMPTION: fixed O&M of biogas and biomass power plants in the Dominican Republic is 86.48 USD/kW-yr for all years "
               "(4 percent per year of a total installed cost of 2,162 USD/kW). Reason: IRENA reports fixed O&M of bioenergy power plants "
               "between 2 and 6 percent of total installed costs per year, and 4 percent is the midpoint. Check: IRENA Renewable Power "
               "Generation Costs in 2022, page 183. Range: 43.24 to 129.72 USD/kW-yr.")
TECH_ROWS["PPBIM"] = {
    "CapitalCost": dict(cands=[C("IRENA 2022 bioenergy", SID["IRENA22"], LOC["IRENA22_H1"], at(IRENA22["bio"], 2022))],
                        prop=flat(IRENA22["bio"]), prop_sid=SID["IRENA22"],
                        prop_der="IRENA 2022 global weighted average total installed cost of bioenergy 2,162 USD/kW (2022 USD), held flat; newer edition (IRENA 2024): 3,242 USD/kW"),
    "FixedCost": dict(cands=[penC("229_fc")], prop=bio24f, prop_sid=SID["ATB24"], prop_der=BIO_FC_DER),
    "VariableCost": dict(cands=[penC("229_vc")], prop=flat(5.0 / 3.6), prop_sid=SID["IRENA22"], prop_der="IRENA 2022 bioenergy average variable O&M USD 0.005/kWh = 5 USD/MWh / 3.6 = 1.388889 USD/GJ (page 183)"),
}
TECH_ROWS["PPBGS"] = {
    "CapitalCost": dict(cands=[C("IRENA 2022 bioenergy", SID["IRENA22"], LOC["IRENA22_H1"], at(IRENA22["bio"], 2022))], prop=flat(IRENA22["bio"]), prop_sid=SID["IRENA22"],
                        prop_der="IRENA 2022 global weighted average total installed cost of bioenergy (solid biomass, biogas and landfill gas) 2,162 USD/kW (2022 USD), held flat; newer edition (IRENA 2024): 3,242 USD/kW"),
    "FixedCost": dict(cands=[], prop=bio24f, prop_sid=SID["ATB24"], prop_der=BIO_FC_DER),
    "VariableCost": dict(cands=[], prop=flat(5.0 / 3.6), prop_sid=SID["IRENA22"], prop_der="IRENA 2022 bioenergy average variable O&M USD 0.005/kWh = 5 USD/MWh / 3.6 = 1.388889 USD/GJ (page 183)"),
}
assert sorted(TECH_ROWS) == sorted(PLANTS), set(PLANTS) ^ set(TECH_ROWS)

UNIT = {"CapitalCost": "MUSD/GW (USD/kW)", "FixedCost": "MUSD/GW per year (USD/kW-yr)", "VariableCost": "MUSD/PJ (USD/GJ)"}
def close(a, b):
    if b == 0: return abs(a) < 1e-9
    return abs(a - b) <= TOL * abs(b)

rows = []
for tech in PLANTS:
    for par in COST_PARAMS:
        spec = TECH_ROWS[tech][par]
        for y in YEARS:
            curv = effective(tech, par, y); cv, sheet, mode = cell(tech, par, y)
            klass = None; prop = None; sid = ""; der = ""; old = ""
            for c in spec["cands"]:
                sv = c["series"].get(y)
                if sv is not None and close(curv, sv):
                    if c.get("newer") and not close(c["newer"][3][y], sv):  # same-year newer edition
                        nl, nsid, nloc, nser = c["newer"]
                        klass, prop = "matched, newer edition", nser[y]
                        sid = f"{c['sid']};{nsid}"; der = f"matched {c['label']} {sv:.4f} ({c['loc']}); newer edition {nl} {nser[y]:.4f} ({nloc})"
                        old = f"{sv:.4f}"
                    else:
                        klass, prop = "matched", curv
                        sid = c["sid"]; der = f"{c['label']} gives {sv:.4f} ({c['loc']}); current {curv:.4f} within 2 percent"
                    break
            if klass is None:
                prop = spec["prop"][y]; sid = spec["prop_sid"]; der = spec["prop_der"]
                klass = "replace"
            change = ("keep" if klass == "matched" else "upgrade" if klass == "matched, newer edition"
                      else ("fill_placeholder" if (curv == 0 and prop != 0) else "replace"))
            if klass == "replace" and close(prop, curv): change = "keep"
            asent = spec.get("assumption", "") if klass == "replace" else ""
            basis = "ASSUMPTION" if asent else klass
            rows.append(dict(technology=tech, parameter=par, year=y, sheet=sheet, projection_mode=mode,
                             workbook_cell=("" if cv is None else round(cv, 6)), current_value=round(curv, 6),
                             proposed_value=round(prop, 6), unit=UNIT[par], p2_class=basis, change_class=change,
                             change_pct=(round((prop / curv - 1) * 100, 2) if curv else ""),
                             cited_edition_value=old, source_ids=sid, derivation=der, assumption_sentence=asent))
PC = pd.DataFrame(rows)
PC.to_csv(os.path.join(JOB, "plant_costs.csv"), index=False)

# Step 6: electricity import IMP_ELE has activity upper limit 0 in every year: no proposal (recorded in REPORT).
summ = []
for (t, p), g in PC.groupby(["technology", "parameter"], sort=False):
    g = g.set_index("year")
    summ.append(dict(technology=t, parameter=p, cur_2024=g.current_value[2024], prop_2024=g.proposed_value[2024],
                     class_2024=g.p2_class[2024], classes=";".join(sorted(g.p2_class.unique())),
                     cur_2030=g.current_value[2030], prop_2030=g.proposed_value[2030], cur_2050=g.current_value[2050],
                     prop_2050=g.proposed_value[2050], source_2024=g.source_ids[2024]))
S = pd.DataFrame(summ); S.to_csv(os.path.join(JOB, "plant_summary.csv"), index=False)
pd.set_option("display.width", 250)
print(S.drop(columns=["source_2024"]).to_string())
print(PC.p2_class.value_counts().to_dict(), PC.change_class.value_counts().to_dict())
