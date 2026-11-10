"""Step 4: fuel supply price series for the Dominican Republic (rules F1 to F6).

Outputs (job folder): fuel_prices.csv, price_points_2024.csv, constants_fuel.csv (merged later
into constants.csv). Inputs: LAC_LOCAL_PRICES outputs (read-only, in the clone) and the benchmark
files downloaded into downloads/bench, downloads/weo and downloads/gas.
"""
import os, sys, json, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import *

YEARS = list(range(2018, 2051))
BENCH = os.path.join(DL, "bench")

# ---------- constants (value, unit, source id, locator, derivation) ----------
CONST = []
def const(name, value, unit, sid, loc, deriv=""):
    CONST.append(dict(name=name, value=value, unit=unit, source_id=sid, page_or_table=loc, derivation=deriv))
    return value

# CPI-U annual averages (BLS CUUR0000SA0)
bls = json.load(open(os.path.join(BENCH, "bls_CUUR0000SA0_get.json"), encoding="utf-8"))
CPI = {}
for x in bls["Results"]["series"][0]["data"]:
    if x["period"] == "M13":
        y = int(x["year"])
        if 2018 <= y <= 2025:
            CPI[y] = const(f"CPIU_{y}", float(x["value"]), "index 1982-84=100, annual average", "CSD-001",
                           f"series CUUR0000SA0, year {y}, period M13 (Annual)")
def real(v, y):
    return v * CPI[2024] / CPI[y]

# Brent and Henry Hub annual (EIA)
def eia_annual(fname):
    d = pd.read_excel(os.path.join(BENCH, fname), sheet_name="Data 1", header=None, skiprows=3)
    return {pd.Timestamp(r[0]).year: float(r[1]) for r in d.itertuples(index=False) if pd.notna(r[1])}
brent = eia_annual("RBRTEa.xls"); hh = eia_annual("RNGWHHDa.xls")
for y in range(2018, 2026):
    const(f"BRENT_{y}", brent[y], "USD/bbl nominal, annual average", "CSD-002", f"sheet Data 1, row {y} (RBRTE annual)")
    const(f"HENRYHUB_{y}", hh[y], "USD/MMBtu nominal (gross), annual average", "CSD-003", f"sheet Data 1, row {y} (RNGWHHD annual)")
# World Bank Pink Sheet annual, Coal South African
pk = pd.read_excel(os.path.join(BENCH, "CMO-Historical-Data-Annual.xlsx"), sheet_name="Annual Prices (Nominal)", header=None)
assert str(pk.iloc[6, 6]).strip() == "Coal, South African", pk.iloc[6, 6]
coal = {}
for i in range(len(pk)):
    try: y = int(str(pk.iloc[i, 0]).strip())
    except ValueError: continue
    if 2018 <= y <= 2025:
        coal[y] = const(f"COAL_SA_{y}", float(pk.iloc[i, 6]), "USD/t nominal, fob Richards Bay NAR 6000 kcal/kg", "CSD-004",
                        f"sheet Annual Prices (Nominal), column G (Coal, South African), row {i+1} ({y})")

GJ_PER_MMBTU = const("GJ_PER_MMBTU", 1.055056, "GJ per MMBtu", "GEN-003", "Appendix B.8, page 45")
NETGROSS = const("UN_NGS_NET_PER_GROSS", 0.9, "net to gross calorific value ratio, natural gas", "GEN-006", "page xxv")
MMBTU_MCF = const("MMBTU_PER_MCF_EIA", 1.037, "MMBtu per thousand cubic feet (gross)", "GEN-005", "answer text")
NCV_CRU = const("IPCC_NCV_CRU", 42.3, "GJ per t (net)", "GEN-002", "Table 1.2, page 1.18")
BBL_T = const("UN_BBL_PER_T_CRU", 7.32, "barrels per tonne", "GEN-001", "Table II, page xxvii")
KCAL = const("KCAL_TO_KJ", 4.1868, "kJ per kcal", "GEN-003", "Appendix B.8, page 46")
NCV_NGS = const("IPCC_NCV_NGS", 48.0, "GJ per t (net)", "GEN-002", "Table 1.2, page 1.18")
GJ_PER_BBL = NCV_CRU / BBL_T
COAL_GJ_T = 6000 * KCAL / 1000
const("GJ_PER_BBL_CRU", round(GJ_PER_BBL, 6), "GJ per barrel (net)", "GEN-002;GEN-001", "derived",
      "42.3 GJ/t (IPCC_NCV_CRU) / 7.32 bbl/t (UN_BBL_PER_T_CRU)")
const("GJ_PER_T_COAL_6000", round(COAL_GJ_T, 6), "GJ per t (net as received)", "GEN-003", "derived",
      "6000 kcal/kg x 4.1868 kJ/kcal (KCAL_TO_KJ) / 1000")

# WEO 2025 Table 2.3, page 109, USD (MER, 2024)
WEO_LOC = "Table 2.3 Wholesale fossil fuel prices by scenario, page 109, USD (MER, 2024)"
WEO_RAW = {
    "crude": {"unit": "USD/barrel", 2024: 79, "CPS": (89, 106), "STEPS": (80, 76), "NZE": (33, 25)},
    "gas_us": {"unit": "USD/MBtu (gross)", 2024: 2.2, "CPS": (4.5, 5.0), "STEPS": (3.9, 4.6), "NZE": (2.1, 2.2)},
    "coal_eu": {"unit": "USD/tonne (6000 kcal/kg)", 2024: 112, "CPS": (92, 82), "STEPS": (78, 66), "NZE": (47, 39)},
}
WEO_NAME = {"crude": "IEA crude oil", "gas_us": "Natural gas, United States", "coal_eu": "Steam coal, European Union"}
for k, d in WEO_RAW.items():
    const(f"WEO2025_{k}_2024", d[2024], d["unit"] + ", real 2024", "CSD-005", WEO_LOC + f", row {WEO_NAME[k]}, column 2024")
    for s in ("CPS", "STEPS", "NZE"):
        for yy, v in zip((2035, 2050), d[s]):
            const(f"WEO2025_{k}_{s}_{yy}", v, d["unit"] + ", real 2024", "CSD-005", WEO_LOC + f", row {WEO_NAME[k]}, column {s} {yy}")
def weo(k, s, y):
    d = WEO_RAW[k]; a, b = d["STEPS" if s == "STEPS" else s]
    if y <= 2024: return d[2024]
    if y <= 2035: return d[2024] + (a - d[2024]) * (y - 2024) / 11
    if y <= 2050: return a + (b - a) * (y - 2035) / 15
    return b

# Benchmarks in USD/GJ net, real 2024
def bench_val(kind, y):
    if kind == "brent": return real(brent[y] / GJ_PER_BBL, y)
    if kind == "hh": return real(hh[y] / GJ_PER_MMBTU / NETGROSS, y)
    if kind == "coal": return real(coal[y] / COAL_GJ_T, y)
BENCH_SID = {"brent": "CSD-002;GEN-002;GEN-001", "hh": "CSD-003;GEN-003;GEN-006;GEN-008;GEN-005;CSD-006;CSD-007", "coal": "CSD-004;GEN-003;DR-006"}
BENCH_TXT = {"brent": "EIA Brent spot RBRTE annual, USD/bbl / 5.778689 GJ/bbl",
             "hh": "EIA Henry Hub RNGWHHD annual, USD/MMBtu gross / 1.055056 / 0.9 (net)",
             "coal": "World Bank Pink Sheet Coal South African fob Richards Bay NAR 6000 kcal/kg, USD/t / 25.1208 GJ/t"}

# ---------- local prices ----------
lp = pd.read_csv(os.path.join(LP, "local_prices_2024.csv")); lp["row"] = lp.index + 2
lh = pd.read_csv(os.path.join(LP, "local_history.csv"))
lp_dr = lp[lp.country == "DominicanRepublic"]; lh_dr = lh[lh.country == "DominicanRepublic"]

GAS_SENT = ("ASSUMPTION: natural gas prices published per MMBtu are on a gross calorific basis and are converted to the "
            "models' net basis by dividing by 0.9 (net = 0.9 x gross for natural gas, UN Statistics Division), for all six "
            "countries and all years. Reason: natural gas in the Americas, Henry Hub included, is priced on a gross basis, and "
            "the energy balances behind the models follow the UN recommendation to use net values (IRES, UN 2018). Check: EIA "
            "reports US natural gas at 1,037 Btu per cubic foot, a gross value. Range: a source already on a net basis would be "
            "overstated by about 11 percent.")
GAS_SIDS = "GEN-008;GEN-006;GEN-005"

# row config: chosen local_prices_2024 row, benchmark, WEO series, reason
CFG = {
    "DIST_COA": dict(fuel="COA", row=62, bench="coal", weo="coal_eu",
        why="import CIF is the first published pre-tax point under F2 (no wholesale import parity published for coal)"),
    "DIST_COK": dict(fuel="COK", row=63, bench="brent", weo="crude",
        why="import CIF is the only published point"),
    "DIST_CRU": dict(fuel="CRU", row=64, bench="brent", weo="crude",
        why="import CIF is the only published point"),
    "DIST_DSL": dict(fuel="DSL", row=43, bench="brent", weo="crude",
        why="MICM Gasoil Regular EGP-C import parity (PPI), pre-tax and market-tracking (weekly PPI follows the market)"),
    "DIST_FOI": dict(fuel="FOI", row=46, bench="brent", weo="crude",
        why="MICM Fuel Oil No. 6 import parity (PPI), pre-tax and market-tracking; the FO 1%S grade is recorded beside it"),
    "DIST_GSL": dict(fuel="GSL", row=67, bench="brent", weo="crude",
        why="market import cost (import CIF built from US-reported export FOB times the DR CIF/FOB ratio, HS 271012) chosen over the MICM administrative parity"),
    "DIST_KER": dict(fuel="KER", row=54, bench="brent", weo="crude",
        why="MICM kerosene import parity (PPI), pre-tax; no market import value for kerosene is published"),
    "DIST_LPG": dict(fuel="LPG", row=66, bench="brent", weo="crude",
        why="market import cost (DR customs CIF, HS 271112 plus 271113) chosen over the MICM administrative parity"),
    "DIST_NGS": dict(fuel="NGS", row=65, bench="hh", weo="gas_us",
        why="market import cost (DR customs CIF of LNG, HS 271111, already net) chosen over the MICM PPI, which is fixed in pesos (administrative)"),
}

fp_rows, pp_rows, summary = [], [], []
for tech, c in CFG.items():
    ch = lp_dr[lp_dr.row == c["row"]].iloc[0]
    assert ch.model_code == tech, (tech, ch.model_code)
    v24 = float(ch.value_usd_per_gj)
    conv = str(ch.conversion_constants_source_ids)
    conv_ids = sorted({t.strip() for part in conv.split(";") for t in part.split("=")[-1:] if t.strip() and t.strip() != "nan"})
    loc_sids = ";".join(dict.fromkeys(str(ch.source_id).split(";") + conv_ids + (["DR-001"] if str(ch.currency) == "DOP" else [])))
    # history of the chosen point
    hist = lh_dr[(lh_dr.model_code == tech) & (lh_dr.price_point == ch.price_point)]
    obs = {int(r.year): real(float(r.value_usd_per_gj), int(r.year)) for r in hist.itertuples()}
    obs_sid = {int(r.year): str(r.source_id) for r in hist.itertuples()}
    obs[2024] = v24; obs_sid[2024] = loc_sids
    r_sids = list(dict.fromkeys(x for y_ in sorted(obs_sid) for x in obs_sid[y_].split(";")))
    B = {y: bench_val(c["bench"], y) for y in range(2018, 2026)}
    ratios = {y: obs[y] / B[y] for y in sorted(obs)}
    if len(ratios) > 1:
        r = sum(ratios.values()) / len(ratios)
        case = f"multi-year average of chosen point over benchmark, years {','.join(str(y) for y in ratios)}"
    else:
        r = ratios[2024]; case = "2024 ratio alone (no history for the chosen point or for import CIF)"
    rtxt = "; ".join(f"{y}: {obs[y]:.4f}/{B[y]:.4f}={ratios[y]:.4f}" for y in ratios)
    weo_ids = "CSD-005"
    cpi_ids = "CSD-001"
    for s in ("STEPS", "CPS", "NZE"):
        for y in YEARS:
            if y in obs:
                val = obs[y]; kind = "observed"
                if y == 2024:
                    sid = loc_sids
                    der = f"{ch.derivation}" if str(ch.derivation) != "nan" else f"published {ch.price_as_published} {ch.unit}"
                    der = f"2024 {ch.price_point}: {v24:.4f} USD/GJ (LAC_LOCAL_PRICES row {c['row']}; nominal 2024 = real 2024)"
                else:
                    sid = ";".join(dict.fromkeys(obs_sid[y].split(";") + ["GEN-002", cpi_ids]))
                    nom = float(hist[hist.year == y].value_usd_per_gj.iloc[0])
                    der = f"{y} {ch.price_point} nominal {nom:.4f} USD/GJ x CPI-U 2024 {CPI[2024]} / CPI-U {y} {CPI[y]} = {val:.4f}"
            elif y <= 2025:
                val = r * B[y]; kind = "history from ratio"
                sid = ";".join(dict.fromkeys(r_sids + BENCH_SID[c["bench"]].split(";") + [cpi_ids]))
                der = f"r {r:.4f} x benchmark {y} {B[y]:.4f} USD/GJ real 2024 ({BENCH_TXT[c['bench']]}, deflated with CPI-U) = {val:.4f}"
            else:
                w0, wy = weo(c["weo"], s, 2024), weo(c["weo"], s, y)
                val = r * B[2024] * wy / w0; kind = "projected"
                sid = ";".join(dict.fromkeys(r_sids + BENCH_SID[c["bench"]].split(";") + [weo_ids, cpi_ids]))
                der = (f"r {r:.4f} x B(2024) {B[2024]:.4f} x WEO2025 {WEO_NAME[c['weo']]} {s} {y} {wy:.4f} / 2024 {w0:.4f} "
                       f"(linear between 2024, 2035 and 2050) = {val:.4f}")
            fp_rows.append(dict(row=tech, fuel=c["fuel"], year=y, scenario=s, value_usd_per_gj=round(val, 4), case=kind,
                                r=round(r, 6), r_case=case, r_detail=rtxt, chosen_point=ch.price_point,
                                benchmark=BENCH_TXT[c["bench"]], weo_series=f"WEO 2025 {WEO_NAME[c['weo']]} ({s})",
                                source_ids=sid, derivation=der,
                                assumption_sentence=GAS_SENT if (tech == "DIST_NGS" and kind != "observed") else ""))
    # price points beside the chosen one (all published 2024 points for the row)
    for p in lp_dr[(lp_dr.model_code == tech)].itertuples():
        pv = float(p.value_usd_per_gj)
        conv_p = sorted({t.strip() for part in str(p.conversion_constants_source_ids).split(";") for t in part.split("=")[-1:] if t.strip() and t.strip() != "nan"})
        sids_p = ";".join(dict.fromkeys(str(p.source_id).split(";") + conv_p + (["DR-001"] if str(p.currency) == "DOP" else [])))
        gross = "MMBTU" in str(p.unit).upper()
        pv_net = pv / NETGROSS if gross else pv
        pp_rows.append(dict(row=tech, fuel=p.fuel, price_point=p.price_point, chosen="yes" if p.row == c["row"] else "no",
                            value_usd_per_gj_published_basis=round(pv, 4),
                            value_usd_per_gj_net=round(pv_net, 4),
                            basis_note=("per MMBtu, gross by convention; net = value / 0.9 (UN_NGS_NET_PER_GROSS)" if gross else "net calorific basis"),
                            diff_vs_chosen_pct=round((pv_net / v24 - 1) * 100, 2),
                            evidence_class=p.evidence_class, tax_treatment=p.tax_treatment,
                            lac_local_prices_row=p.row, source_ids=sids_p,
                            assumption_sentence=GAS_SENT if gross else "",
                            note=("FO 1%S grade" if (tech == "DIST_FOI" and p.row in (48, 49)) else
                                  ("Fuel Oil No. 6" if tech == "DIST_FOI" else ""))))
    if tech == "DIST_KER":  # jet fuel points published under the same supply row
        pass
    v25 = [x for x in fp_rows if x["row"] == tech and x["year"] == 2025 and x["scenario"] == "STEPS"][0]["value_usd_per_gj"]
    summary.append(dict(row=tech, chosen=ch.price_point, v2024=v24, r=r, case=case, v2025=v25, bench2024=B[2024]))

FP = pd.DataFrame(fp_rows); FP.to_csv(os.path.join(JOB, "fuel_prices.csv"), index=False)
PP = pd.DataFrame(pp_rows); PP.to_csv(os.path.join(JOB, "price_points_2024.csv"), index=False)
pd.DataFrame(CONST).to_csv(os.path.join(JOB, "constants_fuel.csv"), index=False)

# summary for the report
cur = pd.read_csv(os.path.join(JOB, "cost_rows_current.csv"))
out = []
for s_ in summary:
    t = s_["row"]
    g = FP[FP.row == t].set_index(["scenario", "year"]).value_usd_per_gj
    vb = pd.read_csv(os.path.join(BAU, "VariableCost.csv"))
    cv = vb[(vb.TECHNOLOGY == t) & (vb.YEAR == 2024)].Value.iloc[0]
    p26 = g[("STEPS", 2026)]
    out.append(dict(row=t, chosen_point=s_["chosen"], value_2024=round(s_["v2024"], 4), current_2024=round(float(cv), 4),
                    r=round(s_["r"], 4), r_case=s_["case"], STEPS_2030=g[("STEPS", 2030)], STEPS_2050=g[("STEPS", 2050)],
                    CPS_2050=g[("CPS", 2050)], NZE_2050=g[("NZE", 2050)], value_2025=s_["v2025"], STEPS_2026=p26,
                    join_step_pct=round((p26 / s_["v2025"] - 1) * 100, 2)))
pd.DataFrame(out).to_csv(os.path.join(JOB, "fuel_summary.csv"), index=False)
print(pd.DataFrame(out).drop(columns=["r_case"]).to_string())
print("fuel_prices rows", len(FP), "price points", len(PP), "constants", len(CONST))
