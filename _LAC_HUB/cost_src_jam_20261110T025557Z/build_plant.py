"""Step 5: plant costs (rules P1 to P3). Writes plant_costs.csv and plant_sources.csv.

Each technology and parameter gets one decision (documented in SPEC below), then a value for every model year 2021 to 2055.
Matching test: within 2 percent after the stated conversion. ATB years are aligned with model years (model 2021 uses ATB 2022,
years after 2050 use 2050). Values stay in the currency year of their source (no deflation), except where the match itself
is in 2021 USD (ATB deflated with CPI-U 2021/2022), which is stated in the derivation.
"""
import csv, json
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
YEARS = list(range(2021, 2056))
cur = pd.read_csv(HERE / "cost_rows_current.csv")
atb = pd.read_csv(HERE / "atb2024_series.csv")
fc = pd.read_csv(HERE / "fuel_constants.csv").set_index("name")
CPI21, CPI22 = float(fc.loc["CPIU_2021", "value"]), None
bls = json.load(open(HERE / "downloads" / "bls_cpiu_v1_post_2016_2025.json"))["Results"]["series"][0]["data"]
v22 = [float(x["value"]) for x in bls if x["year"] == "2022" and x["period"] not in ("M13",) and x["value"] != "-"]
CPI22 = round(sum(v22) / len(v22), 3)
DEF = CPI21 / CPI22  # 2022 USD to 2021 USD

def effective(tech, param):
    r = cur[(cur.Tech == tech) & (cur.Parameter == param)].iloc[0]
    out = {}
    for y in YEARS:
        v = r[str(y)]
        if r["Projection.Mode"] == "Flat":
            v = r["2021"]
        out[y] = None if pd.isna(v) else float(v)
    return out, r["Projection.Mode"]

def atb_series(tech, detail, metric, conv=1.0):
    d = atb[(atb.technology == tech) & (atb.techdetail == detail) & (atb.core_metric_parameter == metric)].set_index("year").value
    return {y: float(d[min(max(y, 2022), 2050)]) * conv for y in YEARS}

S_ATB = "PSJ-006"; S_IRP = "PSJ-004"; S_IRENA22 = "PSJ-001"; S_IRENA25 = "PSJ-002"; S_OUR = "PSJ-005"
ATBLOC = "ATBe.csv v4.0.0, scenario Moderate, core_metric_case Market, crpyears 30"
GJ_PER_MWH = 3.6

BAT_SENT_PV = ("ASSUMPTION: distributed solar PV with battery storage costs the distributed PV plant plus one kW of battery per kW of PV, "
               "with the battery at 816 USD/kW capital and 50 USD/kW-yr fixed O&M in 2018 USD (2018 Jamaica Integrated Resource Plan) declining after 2022 "
               "in line with the NREL ATB 2024 utility-scale 4-hour battery (Moderate), for all years. Reason: no published cost exists for the combined "
               "system in Jamaica, and the plant is the sum of its two parts. Check: the 2021 gap between the two model plants (824 USD/kW) is within "
               "1 percent of the IRP battery cost. Range: 0.5 to 2 kW of battery per kW of PV moves 2024 capital by minus 380 to plus 750 USD/kW.")
BAT_SENT_WIND = BAT_SENT_PV.replace("distributed solar PV with battery storage costs the distributed PV plant plus one kW of battery per kW of PV",
                                    "onshore wind with battery storage costs the onshore wind plant plus one kW of battery per kW of wind").replace(
    "Check: the 2021 gap between the two model plants (824 USD/kW) is within 1 percent of the IRP battery cost. Range: 0.5 to 2 kW of battery per kW of PV moves 2024 capital by minus 380 to plus 750 USD/kW.",
    "Check: the same rule reproduces the PV with battery plant within 1 percent in 2021. Range: 0.5 to 2 kW of battery per kW of wind moves 2024 capital by minus 380 to plus 750 USD/kW; variable O&M is that of the wind plant (2.5 USD/MWh, IRP).")

SPEC = {}
def spec(tech, param, **k):
    SPEC[(tech, param)] = k

# utility PV
spec("PPPVT", "CapitalCost", mode="indexed", V=1350.0, ref=2022, S=atb_series("UtilityPV", "Class1", "OCC"),
     sids=f"{S_IRP};{S_ATB}", der="2018 IRP Appendix C (PDF p.182) solar candidates 1350 USD/kW (2018 USD, matches model 2021 exactly) x ATB 2024 UtilityPV Class1 OCC index (year y / 2022)",
     level_note="matched: IRP 1350 equals the model 2021 value and is within 0.1 percent of 2024 (1348.6)")
spec("PPPVT", "FixedCost", mode="keep_flat", V=2.60 * 12, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) solar fixed O&M 2.60 USD/kW-month x 12 = 31.2 USD/kW-yr (2018 USD); constant in all years (the IRP gives one value)")
spec("PPPVT", "VariableCost", mode="flat_replace", V=0.0, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) solar variable O&M 0 USD/MWh")
# distributed PV
spec("PPPVD", "CapitalCost", mode="series", S=atb_series("ResPV", "Class1", "CAPEX"), sids=S_ATB, basis_level="replace",
     der=f"NREL ATB 2024 ResPV Class1 CAPEX (2022 USD), {ATBLOC}; IRENA 2022, IEA WEO 2023 and the 2018 IRP publish no distributed PV cost")
spec("PPPVD", "FixedCost", mode="series", S=atb_series("ResPV", "Class1", "Fixed O&M"), sids=S_ATB, basis_level="matched",
     der=f"NREL ATB 2024 ResPV Class1 Fixed O&M (2022 USD), {ATBLOC}; 2024 value 29.5 is within 1.4 percent of the model 29.1")
spec("PPPVD", "VariableCost", mode="flat_replace", V=0.0, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) solar variable O&M 0 USD/MWh")
# wind
spec("PPWNDON", "CapitalCost", mode="series", S=atb_series("LandbasedWind", "Class9", "CAPEX"), sids=S_ATB, basis_level="matched",
     extra={2021: (1870.0, S_IRP, "2018 IRP Appendix C (PDF p.182) wind 1870 USD/kW (2018 USD)")},
     der=f"NREL ATB 2024 LandbasedWind Class9 CAPEX (2022 USD), {ATBLOC}; 2024 value 1764.4 is within 0.5 percent of the model 1772.6")
spec("PPWNDON", "FixedCost", mode="keep_flat", V=3.00 * 12, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) wind fixed O&M 3.00 USD/kW-month x 12 = 36 USD/kW-yr (2018 USD); constant in all years")
spec("PPWNDON", "VariableCost", mode="keep_flat", V=2.5 / GJ_PER_MWH, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) wind variable O&M 2.5 USD/MWh / 3.6 = 0.6944 USD/GJ (2018 USD); constant")
# hydro
spec("PPHDAM", "CapitalCost", mode="series", S=atb_series("Hydropower", "NPD1", "CAPEX", DEF), sids=f"{S_ATB};CSJ-006", basis_level="matched",
     der=f"NREL ATB 2024 Hydropower NPD1 CAPEX (2022 USD) x CPIU_2021/CPIU_2022 {DEF:.5f} (2021 USD), {ATBLOC}")
spec("PPHDAM", "FixedCost", mode="series", S=atb_series("Hydropower", "NPD1", "Fixed O&M", DEF), sids=f"{S_ATB};CSJ-006", basis_level="matched",
     der=f"NREL ATB 2024 Hydropower NPD1 Fixed O&M (2022 USD) x CPIU_2021/CPIU_2022 {DEF:.5f} (2021 USD), {ATBLOC}")
spec("PPHROR", "CapitalCost", mode="series", S=atb_series("Hydropower", "NSD3", "OCC"), sids=S_ATB, basis_level="matched",
     der=f"NREL ATB 2024 Hydropower NSD3 (new stream-reach) OCC 7376 USD/kW (2022 USD), constant, {ATBLOC}")
spec("PPHROR", "FixedCost", mode="keep_flat", V=10.0 * 12, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) run-of-river hydro fixed O&M 10.00 USD/kW-month x 12 = 120 USD/kW-yr (2018 USD); constant")
spec("PPHROR", "VariableCost", mode="flat_replace", V=0.0, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) run-of-river hydro variable O&M 0.0 USD/MWh")
# geothermal
spec("PPGEO", "CapitalCost", mode="series", S=atb_series("Geothermal", "HydroFlash", "CAPEX", DEF), sids=f"{S_ATB};CSJ-006", basis_level="matched",
     der=f"NREL ATB 2024 Geothermal HydroFlash CAPEX (2022 USD) x CPIU_2021/CPIU_2022 {DEF:.5f} (2021 USD), {ATBLOC}; 2022 value 6679 is within 1.1 percent of the model 2021 value")
FOMGEO = atb_series("Geothermal", "HydroFlash", "Fixed O&M")
spec("PPGEO", "FixedCost", mode="upgrade", S={y: 128.0 * FOMGEO[y] / FOMGEO[2025] for y in YEARS}, sids=f"{S_IRENA22};{S_IRENA25};{S_ATB}",
     der="IRENA Renewable Power Generation Costs in 2022 p.173: geothermal O&M 115 USD/kW-yr (2022 USD), within 1.2 percent of the model 113.62 (old value); newer edition IRENA Renewable Power Generation Costs in 2025 p.123: 128 USD/kW-yr (2025 USD), applied in 2025 and moved by the NREL ATB 2024 HydroFlash Fixed O&M index (year y / 2025)")
# bioenergy (biomass and biogas share the model's values)
CAPB = atb_series("Biopower", "Dedicated", "CAPEX")
for t in ("PPBIM", "PPBGS"):
    spec(t, "CapitalCost", mode="series", S={y: 2162.0 * CAPB[y] / CAPB[2022] for y in YEARS}, sids=f"{S_IRENA22};{S_ATB}", basis_level="replace",
         der="IRENA Renewable Power Generation Costs in 2022 p.15 Table H.1: bioenergy global weighted-average total installed cost 2162 USD/kW in 2022 (2022 USD) x NREL ATB 2024 Biopower Dedicated CAPEX index (year y / 2022); newer edition (IRENA 2025 p.14) gives 3320 (2024) and 3606 (2025) in 2025 USD")
    spec(t, "FixedCost", mode="series", S=atb_series("Biopower", "Dedicated", "Fixed O&M"), sids=S_ATB, basis_level="replace",
         der=f"NREL ATB 2024 Biopower Dedicated Fixed O&M 163.7 USD/kW-yr (2022 USD), {ATBLOC}; IRENA 2022 p.183 gives only a share (2 to 6 percent of capital cost a year); the 2018 IRP biomass rows are blank")
    spec(t, "VariableCost", mode="upgrade", S={y: 0.004 * 1000 / GJ_PER_MWH for y in YEARS}, sids=f"{S_IRENA22};{S_IRENA25}",
         der="IRENA Renewable Power Generation Costs in 2022 p.183: bioenergy variable O&M 0.005 USD/kWh = 1.389 USD/GJ, within 0.8 percent of the model 1.4 (old value); newer edition IRENA 2025 p.133: about 0.004 USD/kWh = 4.0 USD/MWh / 3.6 = 1.111 USD/GJ; constant")
# natural gas combined cycle
spec("PPNGS", "CapitalCost", mode="keep_flat", V=1317.0, sids=S_OUR,
     der="OUR Generation Expansion Plan 2010, WASP DYNPRO summary of capital costs (PDF p.147, printed p.129): combined cycle 1317 USD/kW incl. IDC (January 2010 prices), within 1.3 percent of the model 1300; constant")
spec("PPNGS", "FixedCost", mode="flat_replace", V=1.2 * 12, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) NGCC fixed O&M 1.2 USD/kW-month x 12 = 14.4 USD/kW-yr (2018 USD); constant")
spec("PPNGS", "VariableCost", mode="flat_replace", V=2.6 / GJ_PER_MWH, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) NGCC variable O&M 2.6 USD/MWh / 3.6 = 0.7222 USD/GJ (2018 USD); constant")
# diesel (ADO-fired combustion turbine) and HFO medium-speed diesel
spec("PPDSL", "CapitalCost", mode="flat_replace", V=800.0, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) combustion turbine (natural gas or ADO) 800 USD/kW incl. IDC (2018 USD); constant")
spec("PPDSL", "FixedCost", mode="flat_replace", V=1.0 * 12, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) combustion turbine fixed O&M 1.0 USD/kW-month x 12 = 12 USD/kW-yr (2018 USD); constant")
spec("PPDSL", "VariableCost", mode="flat_replace", V=1.0 / GJ_PER_MWH, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) combustion turbine variable O&M 1.0 USD/MWh / 3.6 = 0.2778 USD/GJ (2018 USD); constant")
spec("PPFOI", "CapitalCost", mode="flat_replace", V=1400.0, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) medium speed diesel (HFO) 1400 USD/kW incl. IDC (2018 USD); constant")
spec("PPFOI", "FixedCost", mode="unit_fix", V=3.0 * 12, sids=S_IRP,
     der="2018 IRP Appendix C (PDF p.182) medium speed diesel (HFO) fixed O&M 3.0 USD/kW-month; the model value 2.99 matches it as a monthly figure (0.3 percent); x 12 = 36 USD/kW-yr (2018 USD); constant")
spec("PPFOI", "VariableCost", mode="flat_replace", V=6.5 / GJ_PER_MWH, sids=S_IRP, der="2018 IRP Appendix C (PDF p.182) medium speed diesel (HFO) variable O&M 6.5 USD/MWh / 3.6 = 1.8056 USD/GJ (2018 USD); constant")

def within(a, b, tol=0.02):
    return a is not None and b is not None and (abs(a - b) <= tol * abs(b) if b != 0 else abs(a) < 1e-9)

rows = []
def add(t, p, y, cv, pv, cls, basis, sids, der, sent=""):
    rows.append(dict(technology=t, parameter=p, year=y, current_value="" if cv is None else round(cv, 6), proposed_value=round(pv, 4),
                     change_class=cls, basis_class=basis, source_ids=sids, derivation=der, assumption_sentence=sent))

PROPOSED = {}
for (t, p), s in SPEC.items():
    eff, mode = effective(t, p)
    out = {}
    for y in YEARS:
        cv = eff[y]
        m = s["mode"]
        if m == "keep_flat":
            pv = s["V"]
            if within(cv, pv):
                add(t, p, y, cv, cv, "keep", "matched", s["sids"], s["der"] + f"; model value {cv:g} kept (within 2 percent)"); out[y] = cv; continue
            add(t, p, y, cv, pv, "replace", "replace", s["sids"], s["der"]); out[y] = pv; continue
        if m in ("flat_replace", "unit_fix"):
            pv = s["V"]
            cls = "unit_fix" if m == "unit_fix" else ("fill_empty" if cv is None else ("keep" if within(cv, pv, 0.0005) else "replace"))
            add(t, p, y, cv, pv, cls, "matched" if m == "unit_fix" else ("matched" if cls == "keep" else "replace"), s["sids"], s["der"]); out[y] = pv; continue
        if m == "indexed":
            pv = s["V"] * s["S"][y] / s["S"][s["ref"]]
            der = s["der"] + f": {s['V']:g} x {s['S'][y]:.1f} / {s['S'][s['ref']]:.1f}"
            if within(cv, pv):
                add(t, p, y, cv, cv, "keep", "matched", s["sids"], der + f"; model value kept (within 2 percent of {pv:.1f})"); out[y] = cv
            else:
                add(t, p, y, cv, pv, "replace", "replace", s["sids"], der + f" ({s['level_note']}; path replaced in this year)"); out[y] = pv
            continue
        if m in ("series", "upgrade"):
            pv = s["S"][y]
            ex = s.get("extra", {}).get(y)
            if m == "upgrade":
                add(t, p, y, cv, pv, "upgrade", "matched, newer edition", s["sids"], s["der"] + f"; year {y}: {pv:.4f}"); out[y] = pv; continue
            if within(cv, pv):
                add(t, p, y, cv, cv, "keep", "matched", s["sids"], s["der"] + f"; year {y} source value {pv:.2f}, model value kept (within 2 percent)"); out[y] = cv
            elif ex and within(cv, ex[0]):
                add(t, p, y, cv, cv, "keep", "matched", ex[1], ex[2] + f"; model value {cv:g} kept (within 2 percent)"); out[y] = cv
            else:
                add(t, p, y, cv, pv, "replace", "replace", s["sids"], s["der"] + f"; year {y} source value {pv:.2f}"); out[y] = pv
            continue
    PROPOSED[(t, p)] = out

# storage-paired plants: ASSUMPTION
BCAP = atb_series("Utility-Scale Battery Storage", "4Hr Battery Storage", "CAPEX")
BFOM = atb_series("Utility-Scale Battery Storage", "4Hr Battery Storage", "Fixed O&M")
for t, base, sent in (("PPPVDS", "PPPVD", BAT_SENT_PV), ("PPWNDONS", "PPWNDON", BAT_SENT_WIND)):
    for p, B, V in (("CapitalCost", BCAP, 816.0), ("FixedCost", BFOM, 50.0)):
        eff, _ = effective(t, p)
        basev = PROPOSED.get((base, p))
        if basev is None:  # wind fixed is keep_flat
            basev = PROPOSED[(base, p)]
        for y in YEARS:
            bat = V * B[y] / B[2022]
            pv = basev[y] + bat
            der = f"{base} proposed {basev[y]:.2f} + battery {V:g} x ATB 4Hr battery {('CAPEX' if p == 'CapitalCost' else 'Fixed O&M')} {B[y]:.1f} / {B[2022]:.1f} = {bat:.2f} (IRP BESS PDF p.107)"
            cv = eff[y]
            cls = "keep" if within(cv, pv, 0.0005) else ("fill_empty" if cv is None else "replace")
            add(t, p, y, cv, pv, cls, "ASSUMPTION", f"{S_IRP};{S_ATB};" + ("PSJ-006" if True else ""), der, sent)
eff, _ = effective("PPWNDONS", "VariableCost")
for y in YEARS:
    add("PPWNDONS", "VariableCost", y, eff[y], 2.5 / GJ_PER_MWH, "fill_empty" if eff[y] is None else "replace", "ASSUMPTION", S_IRP,
        "2018 IRP Appendix C (PDF p.182) wind variable O&M 2.5 USD/MWh / 3.6 = 0.6944 USD/GJ, as for PPWNDON", BAT_SENT_WIND)
eff, _ = effective("PPPVDS", "VariableCost")
for y in YEARS:
    add("PPPVDS", "VariableCost", y, eff[y], 0.0, "fill_empty" if eff[y] is None else "replace", "ASSUMPTION", S_IRP,
        "2018 IRP Appendix C (PDF p.182) solar variable O&M 0 USD/MWh, as for PPPVD", BAT_SENT_PV)

VOM0 = {
    "PPHDAM": ("ASSUMPTION: the variable O&M cost of dam hydro in Jamaica is 0 USD/GJ in all years, all non-fuel O&M being carried by the fixed cost (85 USD/kW-yr in 2021 USD). "
               "Reason: published cost sets for hydropower give O&M only as an annual fixed cost per kW. Check: NREL ATB 2024 publishes fixed O&M and no variable O&M for hydropower, "
               "and the 2018 Jamaica IRP gives 0 USD/MWh variable O&M for run-of-river hydro. Range: 0 to 1 USD/MWh (0 to 0.28 USD/GJ).", "PSJ-006;PSJ-004"),
    "PPGEO": ("ASSUMPTION: the variable O&M cost of geothermal power in Jamaica is 0 USD/GJ in all years, all non-fuel O&M being carried by the fixed cost. "
              "Reason: published cost sets for geothermal give O&M only as an annual fixed cost per kW. Check: NREL ATB 2024 publishes fixed O&M and no variable O&M for geothermal, "
              "and IRENA (2022, p.173) states geothermal O&M as 115 USD/kW-yr. Range: 0 to 1 USD/MWh (0 to 0.28 USD/GJ).", "PSJ-006;PSJ-001"),
}
for t, (sent, sids) in VOM0.items():
    eff, _ = effective(t, "VariableCost")
    for y in YEARS:
        add(t, "VariableCost", y, eff[y], 0.0, "fill_empty" if eff[y] is None else "replace", "ASSUMPTION", sids,
            "zero variable O&M: all non-fuel O&M in the fixed cost (see sentence)", sent)

cols = ["technology", "parameter", "year", "current_value", "proposed_value", "change_class", "basis_class", "source_ids", "derivation", "assumption_sentence"]
with open(HERE / "plant_costs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

# plant sources (from the two plant source registers, re-keyed)
A = pd.read_csv(HERE / "downloads" / "plant" / "sources_irena_iea.csv", keep_default_na=False).set_index("source_key")
B2 = pd.read_csv(HERE / "downloads" / "plant2" / "sources_atb_jam.csv", keep_default_na=False).set_index("source_key")
def srow(sid, reg, key, folder, page, title=None):
    r = reg.loc[key]
    return dict(id=sid, url=r.url, title=title or r.title, publisher=r.publisher, date=r.edition, retrieval_date=r.retrieval_date,
                downloaded_file=f"{folder}/{r.downloaded_file}", page_or_table=page, notes=r.notes[:300])
ps = [
    srow("PSJ-001", A, "IRENA2022", "plant", "p.15 Table H.1 (bioenergy 2162 USD/kW, 2022); p.173 (geothermal O&M 115 USD/kW-yr); p.183 (bioenergy variable O&M 0.005 USD/kWh; fixed O&M 2 to 6 percent)"),
    srow("PSJ-002", A, "IRENA2025", "plant", "p.123 (geothermal O&M 128 USD/kW-yr); p.133 section 8.5 (bioenergy variable O&M about 0.004 USD/kWh); p.14 Figure S1 (bioenergy 3320 in 2024, 3606 in 2025)"),
    srow("PSJ-004", B2, "JAM_IRP2018", "plant2", "Appendix C, PDF p.182 (candidate cost table: wind, solar, run-of-river hydro, combustion turbine, NGCC, medium speed diesel); PDF p.107 (BESS 816 USD/kW, 50 USD/kW-yr, 2018 USD)"),
    srow("PSJ-005", B2, "OUR_GEP2010", "plant2", "PDF p.147 (printed p.129), WASP DYNPRO summary of capital costs: combined cycle 1317 USD/kW"),
    srow("PSJ-006", B2, "NREL_ATB2024", "plant2", "ATBe.csv v4.0.0 rows: scenario Moderate, core_metric_case Market, crpyears 30; technologies UtilityPV Class1, ResPV Class1, LandbasedWind Class9, Hydropower NPD1 and NSD3, Geothermal HydroFlash, Biopower Dedicated, Utility-Scale Battery Storage 4Hr; parameters CAPEX, OCC, Fixed O&M; years 2022 to 2050 (extract in atb2024_series.csv)"),
]
with open(HERE / "plant_sources.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "url", "title", "publisher", "date", "retrieval_date", "downloaded_file", "page_or_table", "notes"]); w.writeheader(); w.writerows(ps)

P = pd.DataFrame(rows)
s = P[P.year.isin([2021, 2024, 2030, 2050])].pivot_table(index=["technology", "parameter"], columns="year", values=["current_value", "proposed_value"], aggfunc="first")
print(s.to_string())
print(P.groupby(["change_class"]).size()); print(P.groupby("basis_class").size())
