"""Step 4: fuel price series for the Jamaica supply rows (rules F1 to F6).

Reads the LAC_LOCAL_PRICES tables (read-only) and the benchmark files saved in downloads/,
writes fuel_prices.csv, price_points_2024.csv and fuel_constants.csv (merged into constants.csv later).
All prices in USD/GJ, net calorific basis, real 2024 USD.
"""
import csv, json, re
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
DL = HERE / "downloads"
LP = Path(__file__).resolve().parent.parent / "local_prices_20261109T085226Z"
YEARS = list(range(2021, 2056))
consts = []  # name, value, unit, source_id, page_or_table, derivation


def const(name, value, unit, sid, loc, der=""):
    consts.append([name, value, unit, sid, loc, der])
    return value


# ---------------- constants reused from LAC_LOCAL_PRICES ----------------
lpc = pd.read_csv(LP / "constants.csv").set_index("name")
def lp_const(name):
    r = lpc.loc[name]
    return const(name, float(r.value), r.unit, r.source_id, r.page_or_table, r.derivation if isinstance(r.derivation, str) else "")

GJ_PER_MMBTU = lp_const("GJ_PER_MMBTU")
NET_PER_GROSS = lp_const("UN_NGS_NET_PER_GROSS")
lp_const("MMBTU_PER_MCF_EIA")
BBL_PER_T_CRU = lp_const("UN_BBL_PER_T_CRU")
NCV_CRU = lp_const("IPCC_NCV_CRU")
L_PER_GAL = lp_const("L_PER_USGAL")
GAL = {k: lp_const(f"UN_GAL_PER_T_{k}") for k in ["GSL", "DSL", "KER", "JET", "FOI", "LPG"]}
NCV = {k: lp_const(f"IPCC_NCV_{k}") for k in ["GSL", "DSL", "KER", "JET", "FOI", "LPG", "COK"]}
FX2024 = lp_const("JAM_FX_2024")
GJ_PER_BBL_CRU = const("GJ_PER_BBL_CRU", round(NCV_CRU / BBL_PER_T_CRU, 6), "GJ per barrel of crude oil (net)",
                       "GEN-002;GEN-001", "IPCC Table 1.2; UNSD Table II", "IPCC_NCV_CRU 42.3 GJ/t / UN_BBL_PER_T_CRU 7.32 bbl/t")
KCAL_KJ = const("KJ_PER_KCAL_IT", 4.1868, "kJ per kilocalorie (International Table)", "GEN-003", "Appendix B.8, page 47 (calorie IT)", "1 cal_IT = 4.1868 J")
GJ_PER_T_COAL6000 = const("GJ_PER_T_COAL_6000NAR", round(6000 * KCAL_KJ / 1000, 4), "GJ per tonne at 6,000 kcal/kg net as received",
                          "CSJ-005;GEN-003", "Pink Sheet Description row 6; NIST SP811", "6000 kcal/kg x 4.1868 kJ/kcal / 1000")

# ---------------- CPI-U (BLS CUUR0000SA0) ----------------
bls = json.load(open(DL / "bls_cpiu_v1_post_2016_2025.json"))["Results"]["series"][0]["data"]
cpi_m = {}
for x in bls:
    if x["period"].startswith("M") and x["period"] != "M13" and x["value"] != "-":
        cpi_m.setdefault(int(x["year"]), []).append(float(x["value"]))
CPI = {}
for y in range(2018, 2026):
    v = cpi_m[y]
    CPI[y] = round(sum(v) / len(v), 3)
    const(f"CPIU_{y}", CPI[y], "index 1982-84=100, annual average", "CSJ-006",
          "series CUUR0000SA0, months M01 to M12" + (" (M10 not published)" if len(v) < 12 else ""),
          f"mean of {len(v)} monthly values")
def real(v, y):
    return v * CPI[2024] / CPI[y]

# ---------------- benchmarks (nominal) ----------------
def eia_annual(fname):
    d = pd.read_excel(DL / fname, sheet_name="Data 1", skiprows=2)
    return {int(str(t)[:4]): float(v) for t, v in zip(d.iloc[:, 0], d.iloc[:, 1]) if pd.notna(v)}
BRENT = eia_annual("RBRTEa.xls")
HH = eia_annual("RNGWHHDa.xls")
cmo = pd.read_excel(DL / "CMO-Historical-Data-Annual.xlsx", sheet_name="Annual Prices (Nominal)", header=None)
SACOAL = {int(cmo.iloc[i, 0]): float(cmo.iloc[i, 6]) for i in range(len(cmo)) if str(cmo.iloc[i, 0]).isdigit() and 2015 < int(cmo.iloc[i, 0]) < 2026}
for y in range(2018, 2026):
    const(f"BRENT_{y}", BRENT[y], "USD/bbl nominal, annual average", "CSJ-001", f"sheet Data 1, row dated {y}-06-30", "")
    const(f"HENRYHUB_{y}", HH[y], "USD/MMBtu nominal (gross), annual average", "CSJ-002", f"sheet Data 1, row dated {y}-06-30", "")
    const(f"COAL_SAFRICA_{y}", SACOAL[y], "USD/t nominal, fob Richards Bay NAR 6000 kcal/kg", "CSJ-005",
          f"sheet Annual Prices (Nominal), column G (Coal, South African), row {y}", "")
# benchmark in USD/GJ net, nominal
BENCH = {
    "Brent": ({y: BRENT[y] / GJ_PER_BBL_CRU for y in BRENT}, "EIA Europe Brent spot FOB (RBRTE), annual average, / GJ_PER_BBL_CRU"),
    "HenryHub": ({y: HH[y] / GJ_PER_MMBTU / NET_PER_GROSS for y in HH}, "EIA Henry Hub spot (RNGWHHD), annual average, / GJ_PER_MMBTU / UN_NGS_NET_PER_GROSS"),
    "CoalSA": ({y: SACOAL[y] / GJ_PER_T_COAL6000 for y in SACOAL}, "World Bank Pink Sheet Coal South African (fob Richards Bay NAR 6000), / GJ_PER_T_COAL_6000NAR"),
}
BENCH_SRC = {"Brent": "CSJ-001;GEN-001;GEN-002", "HenryHub": "CSJ-002;GEN-003;GEN-006;GEN-008;GEN-005", "CoalSA": "CSJ-005;GEN-003"}

# ---------------- WEO 2025 Table 2.3 ----------------
WEO_RAW = {  # series: {scenario: {year: value}}, USD (MER, 2024)
    "WEO crude oil": {"CPS": {2024: 79, 2035: 89, 2050: 106}, "STEPS": {2024: 79, 2035: 80, 2050: 76}, "NZE": {2024: 79, 2035: 33, 2050: 25}},
    "WEO natural gas United States": {"CPS": {2024: 2.2, 2035: 4.5, 2050: 5.0}, "STEPS": {2024: 2.2, 2035: 3.9, 2050: 4.6}, "NZE": {2024: 2.2, 2035: 2.1, 2050: 2.2}},
    "WEO steam coal European Union": {"CPS": {2024: 112, 2035: 92, 2050: 82}, "STEPS": {2024: 112, 2035: 78, 2050: 66}, "NZE": {2024: 112, 2035: 47, 2050: 39}},
}
WEO_UNIT = {"WEO crude oil": "USD/barrel", "WEO natural gas United States": "USD/MBtu (gross)", "WEO steam coal European Union": "USD/tonne (6000 kcal/kg)"}
for s, d in WEO_RAW.items():
    for sc, yv in d.items():
        for y, v in yv.items():
            if y == 2024 and sc != "STEPS":
                continue
            const(f"{s.replace(' ', '_').upper()}_{sc if y != 2024 else 'ALL'}_{y}", v, WEO_UNIT[s] + ", real 2024 USD (MER)", "CSJ-007",
                  "Table 2.3 Wholesale fossil fuel prices by scenario, page 109", "")
def weo(series, sc, y):
    pts = sorted(WEO_RAW[series][sc].items())
    if y >= pts[-1][0]:
        return pts[-1][1]
    for (y0, v0), (y1, v1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return v0 + (v1 - v0) * (y - y0) / (y1 - y0)
    return pts[0][1]

# ---------------- local observations ----------------
lp24 = pd.read_csv(LP / "local_prices_2024.csv"); lp24 = lp24[lp24.country == "Jamaica"]
lph = pd.read_csv(LP / "local_history.csv"); lph = lph[lph.country == "Jamaica"]

def hist(fuel, point, flt=None):
    d = lph[(lph.fuel == fuel) & (lph.price_point == point)]
    if flt is not None:
        d = d[flt(d)]
    out = {}
    for r in d.itertuples():
        if pd.notna(r.value_usd_per_gj):
            extra = r.conversion_constants_source_ids if isinstance(r.conversion_constants_source_ids, str) else ""
            sid = ";".join(dict.fromkeys(re.findall(r"[A-Z]{2,4}-\d{3}", r.source_id + ";" + extra)))
            der = r.derivation if isinstance(r.derivation, str) else ""
            out[int(r.year)] = (float(r.value_usd_per_gj), sid, f"{r.page_or_table}: {der}")
    return out

# crude: MSET Table 1 refinery crude imports (value US$ / volume bbl)
CRU_MSET = {2018: (516496439, 7452579, "JAM-018"), 2019: (617574942, 9568843, "JAM-018"), 2020: (380099717, 7977310, "JAM-018"),
            2021: (580889967, 8186366, "JAM-015"), 2022: (728222217, 7118678, "JAM-015"), 2023: (486447045, 5741996, "JAM-015"),
            2024: (511576014, 6320587, "JAM-015"), 2025: (488283538, 6815231, "JAM-015")}
cru_obs = {}
for y, (val, bbl, sid) in CRU_MSET.items():
    usd_bbl = val / bbl
    cru_obs[y] = (usd_bbl / GJ_PER_BBL_CRU, sid, f"Table 1 Total Petroleum Imports, Refinery, Crude, {y}" + (" (2025p)" if y == 2025 else ""))
    const(f"JAM_CRUDE_IMPORT_{y}", round(usd_bbl, 3), "USD/bbl nominal", sid,
          f"Table 1 Total Petroleum Imports, Refinery, Crude, {y}{' preliminary' if y == 2025 else ''} (page 2)", f"{val} USD / {bbl} bbl")

ROWS = {
    # row: fuel, chosen point label, 2024 value (nominal USD/GJ), 2024 source ids, history dict, benchmark, weo series, notes
    "DIST_COA": dict(fuel="COA", point="import CIF", hist={k: v for k, v in hist("COA", "import CIF").items() if k != 2025}, bench="CoalSA", weo="WEO steam coal European Union"),
    "DIST_COK": dict(fuel="COK", point="import CIF", hist=hist("COK", "import CIF"), bench="CoalSA", weo="WEO steam coal European Union"),
    "DIST_FOI": dict(fuel="FOI", point="import CIF", hist=hist("FOI", "import CIF"), bench="Brent", weo="WEO crude oil"),
    "DIST_GSL": dict(fuel="GSL", point="import CIF", hist=hist("GSL", "import CIF"), bench="Brent", weo="WEO crude oil"),
    "DIST_LPG": dict(fuel="LPG", point="import CIF", hist=hist("LPG", "import CIF"), bench="Brent", weo="WEO crude oil"),
    "DIST_NGS": dict(fuel="NGS", point="import CIF", hist={k: v for k, v in hist("NGS", "import CIF").items() if k != 2025}, bench="HenryHub", weo="WEO natural gas United States"),
    "DIST_DSL": dict(fuel="DSL", point="generator delivered (excluding SCT)", hist={}, bench="Brent", weo="WEO crude oil"),
    "DIST_KER": dict(fuel="KER", point="wholesale import parity (pre-tax)", hist=hist("KER", "wholesale import parity"), bench="Brent", weo="WEO crude oil"),
    "DIST_JET": dict(fuel="JET", point="wholesale import parity (pre-tax)", hist={}, bench="Brent", weo="WEO crude oil"),
    "EXTT_CRU": dict(fuel="CRU", point="import CIF (MSET import value)", hist=cru_obs, bench="Brent", weo="WEO crude oil"),
}
ROWS["DIST_OPE"] = dict(fuel="COK", point="import CIF (petroleum coke, same commodity E1COK as DIST_COK)", hist=ROWS["DIST_COK"]["hist"], bench="CoalSA", weo="WEO steam coal European Union")
# 2024 chosen values
def lp_row(fuel, point, sid_contains=None, unit=None):
    d = lp24[(lp24.fuel == fuel) & (lp24.price_point == point)]
    if sid_contains: d = d[d.source_id.str.contains(sid_contains, regex=False)]
    if unit: d = d[d.unit == unit]
    assert len(d) == 1, (fuel, point, len(d))
    return d.iloc[0]
c24 = {
    "DIST_COA": lp_row("COA", "import CIF", "JAM-002"),
    "DIST_COK": lp_row("COK", "import CIF", "JAM-002"),
    "DIST_FOI": lp_row("FOI", "import CIF", "JAM-015"),
    "DIST_GSL": lp_row("GSL", "import CIF", "JAM-003"),
    "DIST_LPG": lp_row("LPG", "import CIF", "JAM-003"),
    "DIST_NGS": lp_row("NGS", "import CIF", "JAM-003"),
    "DIST_DSL": lp24[(lp24.fuel == "DSL") & (lp24.price_point == "generator delivered") & (lp24.tax_treatment.str.startswith("excludes SCT"))].iloc[0],
    "DIST_KER": lp_row("KER", "wholesale import parity"),
    "DIST_JET": lp_row("JET", "wholesale import parity"),
}
c24["DIST_OPE"] = c24["DIST_COK"]
for k, r in c24.items():
    ROWS[k]["v24"] = float(r.value_usd_per_gj); ROWS[k]["sid24"] = r.source_id; ROWS[k]["loc24"] = r.page_or_table; ROWS[k]["der24"] = r.derivation
ROWS["EXTT_CRU"].update(v24=cru_obs[2024][0], sid24="JAM-015;GEN-001;GEN-002", loc24=cru_obs[2024][2],
                        der24=f"511576014 USD / 6320587 bbl = 80.938 USD/bbl; / GJ_PER_BBL_CRU {GJ_PER_BBL_CRU} = {cru_obs[2024][0]:.3f} USD/GJ")
# make sure the 2024 chosen value is in the history set (it is for import CIF rows)
for k, R in ROWS.items():
    if 2024 not in R["hist"] and k != "DIST_KER":
        pass

ASSUME_KERJET = {
    "DIST_KER": ("ASSUMPTION: the 2024 pre-tax wholesale price of kerosene in Jamaica is 18.0 USD/GJ (net calorific basis, real 2024 USD, annual average). "
                 "Reason: Jamaica prices kerosene at import parity with US Gulf Coast middle distillates, so its pre-tax wholesale price sits between the Gulf Coast cargo price and the pre-tax price of diesel delivered to the power utility. "
                 "Check: the 2024 US Gulf Coast kerosene-type jet fuel spot price averaged 2.338 USD/gal (EIA), which is 17.3 USD/GJ with 326 gal/t (UNSD) and 44.1 GJ/t (IPCC), before freight to Kingston; diesel delivered to the utility net of consumption tax was 19.9 USD/GJ (OUR). "
                 "Range: 17.3 to 19.9 USD/GJ; the 2018 to 2019 Petrojam pre-tax ex-refinery kerosene price ran 25 to 28 percent above the Gulf Coast jet price, which would give about 21.8 USD/GJ."),
}
ASSUME_KERJET["DIST_JET"] = ASSUME_KERJET["DIST_KER"].replace("kerosene in Jamaica", "jet fuel in Jamaica").replace("Jamaica prices kerosene", "Jamaica prices jet fuel").replace(
    "the 2018 to 2019 Petrojam pre-tax ex-refinery kerosene price ran 25 to 28 percent above the Gulf Coast jet price, which would give about 21.8 USD/GJ.",
    "the 2018 to 2019 Petrojam pre-tax ex-refinery kerosene price, the same distillation cut, ran 25 to 28 percent above the Gulf Coast jet price, which would give about 21.8 USD/GJ.")
GAS_SENTENCE = ("ASSUMPTION: natural gas prices published per MMBtu are on a gross calorific basis and are converted to the models' net basis by dividing by 0.9 "
                "(net = 0.9 x gross for natural gas, UN Statistics Division), for all six countries and all years. Reason: natural gas in the Americas, Henry Hub included, "
                "is priced on a gross basis, and the energy balances behind the models follow the UN recommendation to use net values (IRES, UN 2018). "
                "Check: EIA reports US natural gas at 1,037 Btu per cubic foot, a gross value. Range: a source already on a net basis would be overstated by about 11 percent.")

out = []; summary = []
for row, R in ROWS.items():
    bvals, bder = BENCH[R["bench"]]
    breal = {y: real(v, y) for y, v in bvals.items() if y in CPI}
    # observed local (real 2024): history, plus the chosen 2024 value
    obs = {y: (real(v, y), sid, loc) for y, (v, sid, loc) in R["hist"].items() if y in CPI}
    if row in ("DIST_DSL", "DIST_KER", "DIST_JET"):
        obs_2024 = (R["v24"], R["sid24"], R["loc24"])
    else:
        obs_2024 = obs.get(2024, (R["v24"], R["sid24"], R["loc24"]))
    # r
    if row == "DIST_KER":
        ys = sorted(y for y in obs if y != 2024)
        rr = [obs[y][0] / breal[y] for y in ys]; r = sum(rr) / len(rr)
        r_case = f"history of the chosen point (pre-tax ex-refinery kerosene) in {', '.join(map(str, ys))}; mean of ratios {', '.join(f'{x:.3f}' for x in rr)}"
    elif obs and row not in ("DIST_DSL", "DIST_JET"):
        ys = sorted(obs)
        rr = [obs[y][0] / breal[y] for y in ys]; r = sum(rr) / len(rr)
        r_case = f"history of the chosen point in {', '.join(map(str, ys))}; mean of ratios {', '.join(f'{x:.3f}' for x in rr)}"
    else:
        r = obs_2024[0] / breal[2024]
        r_case = "no history for the chosen point or for import CIF; r is the 2024 ratio alone"
    R["r"] = r; R["r_case"] = r_case
    used_y = [y for y in obs if (row != "DIST_KER" or y != 2024)] if (obs and row not in ("DIST_DSL", "DIST_JET")) else []
    r_sids = ";".join(dict.fromkeys(";".join([obs[y][1] for y in sorted(used_y)] + ([] if used_y else [obs_2024[1]])).split(";")))
    B24 = breal[2024]
    has25 = 2025 in obs
    last_obs = 2025 if has25 else 2024
    for sc in ["STEPS", "CPS", "NZE"]:
        for y in YEARS:
            if y == 2024:
                v, case, sid, der = obs_2024[0], "observed", obs_2024[1], f"2024 chosen point: {R['der24'] if isinstance(R['der24'], str) else ''}"
            elif y < 2024 or (y == 2025 and has25):
                if y in obs:
                    v, case, sid = obs[y][0], "observed", obs[y][1]
                    der = f"{R['hist'][y][0]:.4f} USD/GJ nominal {y} ({obs[y][2]}) x CPIU_2024 {CPI[2024]} / CPIU_{y} {CPI[y]}"
                else:
                    v, case, sid = r * breal[y], "history from ratio", r_sids + ";" + BENCH_SRC[R["bench"]] + ";CSJ-006"
                    der = f"r {r:.4f} x benchmark {y} real 2024 {breal[y]:.4f} USD/GJ ({bder}; x CPIU_2024/CPIU_{y})"
            else:
                w = weo(R["weo"], sc, y); w0 = weo(R["weo"], sc, 2024)
                v, case, sid = r * B24 * w / w0, "projected", r_sids + ";" + BENCH_SRC[R["bench"]] + ";CSJ-007;CSJ-006"
                der = f"r {r:.4f} x B(2024) {B24:.4f} USD/GJ x {R['weo']} {sc} {w:.3f} / {w0:.3f} (Table 2.3, linear between 2024, 2035, 2050, flat after 2050)"
            src = sid if case != "projected" else sid
            if case == "observed" and y != 2024 and row != "EXTT_CRU":
                src = sid + ";CSJ-006"
            if case == "observed" and y == 2024:
                src = sid
            if row == "EXTT_CRU" and case == "observed":
                src = sid + ";GEN-001;GEN-002" + (";CSJ-006" if y != 2024 else "")
            out.append(dict(row=row, fuel=R["fuel"], year=y, scenario=sc, value_usd_per_gj=round(v, 4), case=case,
                            chosen_point=R["point"], r=round(r, 4), r_case=r_case, benchmark=R["bench"], weo_series=R["weo"],
                            source_ids=src, derivation=der))
    # step at join
    vals = {(o["scenario"], o["year"]): o["value_usd_per_gj"] for o in out if o["row"] == row}
    first_proj = last_obs + 1
    step = vals[("STEPS", first_proj)] / vals[("STEPS", last_obs)] - 1
    R["step"] = (last_obs, first_proj, step)
    R["vals"] = vals

with open(HERE / "fuel_prices.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

# ---------------- price points 2024 ----------------
pp = []
def add_pp(row, fuel, point, value, tax, sid, loc, der, chosen):
    pp.append(dict(row=row, fuel=fuel, price_point=point, value_usd_per_gj=None if value is None else round(value, 3), tax_treatment=tax,
                   source_ids=sid, page_or_table=loc, derivation=der, chosen="yes" if chosen else "no"))
for row, R in ROWS.items():
    if row == "EXTT_CRU":
        continue
    for r in lp24[lp24.fuel == R["fuel"]].itertuples():
        chosen = (row in c24 and r.Index == c24[row].name)
        add_pp(row, R["fuel"], r.price_point, r.value_usd_per_gj if pd.notna(r.value_usd_per_gj) else None, r.tax_treatment, r.source_id, r.page_or_table,
               r.derivation, chosen)
# crude points
add_pp("EXTT_CRU", "CRU", "import CIF (MSET import value)", cru_obs[2024][0], "import value, before taxes; equals the Comtrade CIF value", "JAM-015;GEN-001;GEN-002",
       cru_obs[2024][2], ROWS["EXTT_CRU"]["der24"], True)
add_pp("EXTT_CRU", "CRU", "import CIF (Comtrade)", 511577973.37 / 872448.72013 / NCV_CRU, "customs value CIF, before duties and taxes", "JAM-002;GEN-002",
       "cmdCode 2709, flow M, partner World", f"511577973.37 USD / 872448720.13 kg = {511577973.37/872448.72013:.2f} USD/t; / IPCC_NCV_CRU 42.3 GJ/t", False)
# Petrojam weekly 2024 means (tax-inclusive billing prices)
pj = pd.read_csv(HERE / "petrojam_weekly.csv", parse_dates=["date"])
pj24 = pj[pj.date.dt.year == 2024]
PJMAP = {"Gasolene 87": ("DIST_GSL", "GSL"), "Gasolene 90": ("DIST_GSL", "GSL"), "Auto Diesel": ("DIST_DSL", "DSL"), "ULSD": ("DIST_DSL", "DSL"),
         "Kerosene": ("DIST_KER", "KER"), "Propane": ("DIST_LPG", "LPG"), "Butane": ("DIST_LPG", "LPG"), "HFO": ("DIST_FOI", "FOI")}
for col, (row, fuel) in PJMAP.items():
    m = pj24[col].mean(); n = pj24[col].count()
    usd_gj = m / FX2024 * L_PER_GAL * GAL[fuel] / NCV[fuel]
    add_pp(row, fuel, f"refinery billing price (Petrojam weekly {col})", usd_gj,
           "includes Special Consumption Tax and fees: the 2024 means equal the MSET refinery billing prices (Table 4), which MSET defines as including SCT",
           "CSJ-008;JAM-001;GEN-004;GEN-001;GEN-002", f"weekly listing pages 4 to 9, column {col}, {n} weeks of 2024",
           f"mean {m:.3f} J$/L / JAM_FX_2024 {FX2024} x L_PER_USGAL {L_PER_GAL} x UN_GAL_PER_T_{fuel} {GAL[fuel]} / IPCC_NCV_{fuel} {NCV[fuel]}", False)
    if row == "DIST_KER":
        add_pp("DIST_JET", "JET", f"refinery billing price (Petrojam weekly {col}; same cut as jet)", usd_gj, pp[-1]["tax_treatment"], pp[-1]["source_ids"],
               pp[-1]["page_or_table"], pp[-1]["derivation"], False)
for p in pp:
    ch = next((q for q in pp if q["row"] == p["row"] and q["chosen"] == "yes"), None)
    p["diff_pct_vs_chosen"] = "" if (ch is None or p["value_usd_per_gj"] is None) else round(100 * (p["value_usd_per_gj"] / ch["value_usd_per_gj"] - 1), 1)
with open(HERE / "price_points_2024.csv", "w", newline="", encoding="utf-8") as f:
    cols = ["row", "fuel", "price_point", "chosen", "value_usd_per_gj", "diff_pct_vs_chosen", "tax_treatment", "source_ids", "page_or_table", "derivation"]
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows([{c: p[c] for c in cols} for p in pp])

with open(HERE / "fuel_constants.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["name", "value", "unit", "source_id", "page_or_table", "derivation"]); w.writerows(consts)

summ = []
for row, R in ROWS.items():
    v = R["vals"]; lo, fp, st = R["step"]
    summ.append(dict(row=row, chosen_point=R["point"], v2024=round(v[("STEPS", 2024)], 3), r=round(R["r"], 4), r_case=R["r_case"],
                     steps2030=round(v[("STEPS", 2030)], 3), steps2050=round(v[("STEPS", 2050)], 3), cps2050=round(v[("CPS", 2050)], 3),
                     nze2050=round(v[("NZE", 2050)], 3), join=f"{lo} to {fp}", step_pct=round(100 * st, 1)))
pd.DataFrame(summ).to_csv(HERE / "fuel_summary.csv", index=False)
print(pd.DataFrame(summ).drop(columns=["r_case"]).to_string())
json.dump({"ASSUME_KERJET": ASSUME_KERJET, "GAS": GAS_SENTENCE}, open(HERE / "fuel_assumptions.txt", "w", encoding="utf-8"), indent=1)
