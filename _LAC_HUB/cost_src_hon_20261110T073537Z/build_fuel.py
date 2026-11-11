"""Step 4: fuel price series for the Honduras supply rows (rules F1 to F6).

Reads the LAC_LOCAL_PRICES tables (read-only) and the benchmark files saved in downloads/,
writes fuel_prices.csv, price_points_2024.csv, fuel_summary.csv and fuel_constants.csv (merged into constants.csv later).
All prices in USD/GJ, net calorific basis, real 2024 USD.
"""
import csv, json, re
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
DL = HERE / "downloads"
LP = HERE.parent / "local_prices_20261109T085226Z"
YEARS = list(range(2018, 2051))
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
KCAL_KJ = lp_const("KCAL_TO_KJ")
GJ_PER_BBL_CRU = const("GJ_PER_BBL_CRU", round(NCV_CRU / BBL_PER_T_CRU, 6), "GJ per barrel of crude oil (net)",
                       "GEN-002;GEN-001", "IPCC 2006 V2 Ch1 Table 1.2; UNSD Yearbook Table II", "IPCC_NCV_CRU 42.3 GJ/t / UN_BBL_PER_T_CRU 7.32 bbl/t")
GJ_PER_T_COAL6000 = const("GJ_PER_T_COAL_6000NAR", round(6000 * KCAL_KJ / 1000, 4), "GJ per tonne at 6,000 kcal/kg net as received",
                          "CSH-004;GEN-003", "Pink Sheet sheet Description (Coal, South African: NAR 6000 kcal/kg); NIST SP811", "6000 kcal/kg x 4.1868 kJ/kcal / 1000")

# ---------------- CPI-U (BLS CUUR0000SA0) ----------------
bls = json.load(open(DL / "bls_cpiu_v1_2016_2025.json"))["Results"]["series"][0]["data"]
cpi_m = {}
for x in bls:
    if x["period"].startswith("M") and x["period"] != "M13" and x["value"] != "-":
        cpi_m.setdefault(int(x["year"]), []).append(float(x["value"]))
CPI = {}
for y in range(2018, 2026):
    v = cpi_m[y]
    CPI[y] = round(sum(v) / len(v), 3)
    const(f"CPIU_{y}", CPI[y], "index 1982-84=100, annual average", "CSH-005",
          "series CUUR0000SA0, monthly values M01 to M12" + (f" ({12 - len(v)} month not published)" if len(v) < 12 else ""),
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
hdr = [str(x) for x in cmo.iloc[4].tolist()] + [str(x) for x in cmo.iloc[5].tolist()]
assert "South African" in str(cmo.iloc[4, 6]) or "South African" in str(cmo.iloc[5, 6]) or any("South African" in str(cmo.iloc[i, 6]) for i in range(8)), "column G is not Coal, South African"
SACOAL = {int(cmo.iloc[i, 0]): float(cmo.iloc[i, 6]) for i in range(len(cmo)) if str(cmo.iloc[i, 0]).isdigit() and 2015 < int(cmo.iloc[i, 0]) < 2026}
SAROW = {int(cmo.iloc[i, 0]): i + 1 for i in range(len(cmo)) if str(cmo.iloc[i, 0]).isdigit()}
for y in range(2018, 2026):
    const(f"BRENT_{y}", BRENT[y], "USD/bbl nominal, annual average", "CSH-001", f"sheet Data 1, row dated {y}-06-30", "")
    const(f"HENRYHUB_{y}", HH[y], "USD/MMBtu nominal (gross), annual average", "CSH-002", f"sheet Data 1, row dated {y}-06-30", "")
    const(f"COAL_SAFRICA_{y}", SACOAL[y], "USD/t nominal, fob Richards Bay NAR 6000 kcal/kg", "CSH-004",
          f"sheet Annual Prices (Nominal), column G (Coal, South African), row {y} (sheet row {SAROW[y]})", "")
BENCH = {
    "Brent": ({y: BRENT[y] / GJ_PER_BBL_CRU for y in BRENT}, "EIA Europe Brent spot FOB (RBRTE), annual average, / GJ_PER_BBL_CRU"),
    "HenryHub": ({y: HH[y] / GJ_PER_MMBTU / NET_PER_GROSS for y in HH}, "EIA Henry Hub spot (RNGWHHD), annual average, / GJ_PER_MMBTU / UN_NGS_NET_PER_GROSS"),
    "CoalSA": ({y: SACOAL[y] / GJ_PER_T_COAL6000 for y in SACOAL}, "World Bank Pink Sheet Coal South African (fob Richards Bay NAR 6000), / GJ_PER_T_COAL_6000NAR"),
}
BENCH_SRC = {"Brent": "CSH-001;GEN-001;GEN-002", "HenryHub": "CSH-002;GEN-003;GEN-006;GEN-008;GEN-005", "CoalSA": "CSH-004;GEN-003;CSH-007;HON-016"}

# ---------------- WEO 2025 Table 2.3 (PDF page 109) ----------------
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
            const(f"{s.replace(' ', '_').upper()}_{sc if y != 2024 else 'ALL'}_{y}", v, WEO_UNIT[s] + ", real 2024 USD (MER)", "CSH-006",
                  "Table 2.3 Wholesale fossil fuel prices by scenario, PDF page 109", "")
def weo(series, sc, y):
    pts = sorted(WEO_RAW[series][sc].items())
    if y >= pts[-1][0]:
        return pts[-1][1]
    for (y0, v0), (y1, v1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return v0 + (v1 - v0) * (y - y0) / (y1 - y0)
    return pts[0][1]

# ---------------- local observations (LAC_LOCAL_PRICES) ----------------
lp24 = pd.read_csv(LP / "local_prices_2024.csv"); lp24 = lp24[lp24.country == "Honduras"]
lph = pd.read_csv(LP / "local_history.csv"); lph = lph[lph.country == "Honduras"]

def hist(fuel, point):
    d = lph[(lph.fuel == fuel) & (lph.price_point == point)]
    out = {}
    for r in d.itertuples():
        if pd.notna(r.value_usd_per_gj):
            extra = r.conversion_constants_source_ids if isinstance(r.conversion_constants_source_ids, str) else ""
            sid = ";".join(dict.fromkeys(re.findall(r"[A-Z]{2,4}-\d{3}", r.source_id + ";" + extra)))
            der = r.derivation if isinstance(r.derivation, str) else ""
            out[int(r.year)] = (float(r.value_usd_per_gj), sid, f"{r.page_or_table}: {der}")
    return out

def lp_row(fuel, point, sid=None):
    d = lp24[(lp24.fuel == fuel) & (lp24.price_point == point)]
    if sid:
        d = d[d.source_id == sid]
    assert len(d) == 1, (fuel, point, len(d))
    return d.iloc[0]

# chosen point by rule F2, with the import CIF used for case 2 of rule F4 (BCH, HON-002, the source of the history)
ROWS = {
    "DIST_COA": dict(fuel="COA", point="import CIF", chosen=lp_row("COA", "import CIF"), cif=None, bench="CoalSA", weo="WEO steam coal European Union"),
    "DIST_COK": dict(fuel="COK", point="import CIF", chosen=lp_row("COK", "import CIF"), cif=None, bench="CoalSA", weo="WEO steam coal European Union"),
    "DIST_DSL": dict(fuel="DSL", point="wholesale import parity (pre-tax)", chosen=lp_row("DSL", "wholesale import parity"), cif=lp_row("DSL", "import CIF", "HON-002"), bench="Brent", weo="WEO crude oil"),
    "DIST_FOI": dict(fuel="FOI", point="import CIF", chosen=lp_row("FOI", "import CIF", "HON-002"), cif=None, bench="Brent", weo="WEO crude oil"),
    "DIST_GSL": dict(fuel="GSL", point="wholesale import parity (pre-tax)", chosen=lp_row("GSL", "wholesale import parity"), cif=lp_row("GSL", "import CIF", "HON-002"), bench="Brent", weo="WEO crude oil"),
    "DIST_KER": dict(fuel="KER", point="wholesale import parity (pre-tax)", chosen=lp_row("KER", "wholesale import parity"), cif=lp_row("KER", "import CIF", "HON-002"), bench="Brent", weo="WEO crude oil"),
    "DIST_LPG": dict(fuel="LPG", point="wholesale import parity (pre-tax)", chosen=lp_row("LPG", "wholesale import parity"), cif=lp_row("LPG", "import CIF", "HON-002"), bench="Brent", weo="WEO crude oil"),
    "DIST_NGS": dict(fuel="NGS", point="generator delivered (ODS LNG chain, Henry Hub indexed)", chosen=lp_row("NGS", "generator delivered"), cif=None, bench="HenryHub", weo="WEO natural gas United States"),
}
GAS_SENTENCE = ("ASSUMPTION: natural gas prices published per MMBtu are on a gross calorific basis and are converted to the models' net basis by dividing by 0.9 "
                "(net = 0.9 x gross for natural gas, UN Statistics Division), for all six countries and all years. Reason: natural gas in the Americas, Henry Hub included, "
                "is priced on a gross basis, and the energy balances behind the models follow the UN recommendation to use net values (IRES, UN 2018). "
                "Check: EIA reports US natural gas at 1,037 Btu per cubic foot, a gross value. Range: a source already on a net basis would be overstated by about 11 percent.")
GAS_SIDS = "GEN-008;GEN-006;GEN-005"

out = []; summ = []
for row, R in ROWS.items():
    c = R["chosen"]
    v24 = float(c.value_usd_per_gj); der24 = c.derivation
    cc = c.conversion_constants_source_ids if isinstance(c.conversion_constants_source_ids, str) else ""
    sid24 = ";".join(dict.fromkeys(re.findall(r"[A-Z]{2,4}-\d{3}", c.source_id + ";" + cc)))
    if row == "DIST_NGS":
        v24 = v24 / NET_PER_GROSS
        sid24 = sid24 + ";" + GAS_SIDS
        der24 = f"{der24}; gross {float(c.value_usd_per_gj):.4f} USD/GJ / UN_NGS_NET_PER_GROSS 0.9 = {v24:.4f} USD/GJ net"
    bvals, bder = BENCH[R["bench"]]
    breal = {y: real(v, y) for y, v in bvals.items() if y in CPI}
    B24 = breal[2024]
    # history of the chosen point
    hchosen = {} if R["cif"] is not None or row == "DIST_NGS" else hist(R["fuel"], "import CIF")
    obs = {y: (real(v, y), sid, loc, v) for y, (v, sid, loc) in hchosen.items() if y in CPI and y != 2024}
    obs[2024] = (v24, sid24, f"{c.page_or_table}", v24)
    if hchosen:
        ys = sorted(set(hchosen) & set(CPI))
        rr = [(obs[y][0]) / breal[y] for y in ys]
        r = sum(rr) / len(rr)
        r_case = f"case 1: history of the chosen point in {', '.join(map(str, ys))}; mean of yearly ratios to the benchmark ({', '.join(f'{x:.3f}' for x in rr)})"
        r_sids = ";".join(dict.fromkeys(";".join(obs[y][1] for y in ys).split(";")))
    elif R["cif"] is not None:
        hc = hist(R["fuel"], "import CIF")
        ys = sorted(set(hc) & set(CPI))
        rr = [real(hc[y][0], y) / breal[y] for y in ys]
        r_cif = sum(rr) / len(rr)
        cif24 = float(R["cif"].value_usd_per_gj)
        k = v24 / cif24
        r = r_cif * k
        r_case = (f"case 2: no history for the chosen point; r = mean ratio of import CIF (BCH) to the benchmark in {', '.join(map(str, ys))} "
                  f"({', '.join(f'{x:.3f}' for x in rr)}; mean {r_cif:.4f}) x 2024 ratio of the chosen point to import CIF ({v24:.3f} / {cif24:.3f} = {k:.4f})")
        r_sids = ";".join(dict.fromkeys((";".join(hc[y][1] for y in ys) + ";" + sid24).split(";")))
    else:
        r = v24 / B24
        r_case = f"case 3: no history for the chosen point or for import CIF; r is the 2024 ratio alone ({v24:.4f} / {B24:.4f})"
        r_sids = sid24
    has25 = 2025 in obs
    last_obs = 2025 if has25 else 2024
    for sc in ["STEPS", "CPS", "NZE"]:
        for y in YEARS:
            if y in obs and y <= 2025:
                v, case = obs[y][0], "observed"
                if y == 2024:
                    sid, der = obs[y][1], f"2024 chosen point ({obs[y][2]}): {der24}"
                else:
                    sid = obs[y][1] + ";CSH-005"
                    der = f"{obs[y][3]:.4f} USD/GJ nominal {y} ({obs[y][2]}) x CPIU_2024 {CPI[2024]} / CPIU_{y} {CPI[y]}"
            elif y < 2024 or (y == 2025 and has25):
                v, case = r * breal[y], "history from ratio"
                sid = r_sids + ";" + BENCH_SRC[R["bench"]] + ";CSH-005"
                der = f"r {r:.4f} x benchmark {y} in real 2024 USD {breal[y]:.4f} USD/GJ ({bder}; x CPIU_2024 / CPIU_{y})"
            else:
                w = weo(R["weo"], sc, y); w0 = weo(R["weo"], sc, 2024)
                v, case = r * B24 * w / w0, "projected"
                sid = r_sids + ";" + BENCH_SRC[R["bench"]] + ";CSH-006;CSH-005"
                der = (f"r {r:.4f} x B(2024) {B24:.4f} USD/GJ x {R['weo']} {sc} {w:.3f} / {w0:.3f} "
                       f"(Table 2.3, linear between 2024, 2035 and 2050)")
            if row == "DIST_NGS" and GAS_SIDS not in sid:
                sid = sid + ";" + GAS_SIDS
            sid = ";".join(dict.fromkeys(s for s in sid.split(";") if s))
            out.append(dict(row=row, fuel=R["fuel"], year=y, scenario=sc, value_usd_per_gj=round(v, 4), case=case,
                            chosen_point=R["point"], r=round(r, 4), r_case=r_case, benchmark=R["bench"], weo_series=R["weo"],
                            source_ids=sid, derivation=der))
    vals = {(o["scenario"], o["year"]): o["value_usd_per_gj"] for o in out if o["row"] == row}
    fp = last_obs + 1
    step = vals[("STEPS", fp)] / vals[("STEPS", last_obs)] - 1
    summ.append(dict(row=row, chosen_point=R["point"], v2024=round(vals[("STEPS", 2024)], 3), r=round(r, 4), r_case=r_case,
                     steps2030=round(vals[("STEPS", 2030)], 3), steps2050=round(vals[("STEPS", 2050)], 3), cps2050=round(vals[("CPS", 2050)], 3),
                     nze2050=round(vals[("NZE", 2050)], 3), join=f"{last_obs} to {fp}", step_pct=round(100 * step, 1),
                     observed_years=";".join(str(y) for y in sorted(obs))))
    R["v24net"] = v24

with open(HERE / "fuel_prices.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

# ---------------- price points 2024 (rule F2) ----------------
pp = []
for row, R in ROWS.items():
    for r in lp24[lp24.fuel == R["fuel"]].itertuples():
        chosen = r.Index == R["chosen"].name
        val = float(r.value_usd_per_gj)
        der = r.derivation
        if row == "DIST_NGS":
            val = val / NET_PER_GROSS
            der = f"{der}; / UN_NGS_NET_PER_GROSS 0.9 (net basis)"
        pp.append(dict(row=row, fuel=R["fuel"], price_point=r.price_point, chosen="yes" if chosen else "no", value_usd_per_gj=round(val, 3),
                       diff_pct_vs_chosen=round(100 * (val / R["v24net"] - 1), 1), tax_treatment=r.tax_treatment,
                       months_covered=r.months_covered, source_ids=r.source_id, page_or_table=r.page_or_table, derivation=der))
with open(HERE / "price_points_2024.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(pp[0].keys())); w.writeheader(); w.writerows(pp)

with open(HERE / "fuel_constants.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["name", "value", "unit", "source_id", "page_or_table", "derivation"]); w.writerows(consts)
pd.DataFrame(summ).to_csv(HERE / "fuel_summary.csv", index=False)
print(pd.DataFrame(summ).drop(columns=["r_case"]).to_string())
for s in summ:
    print(s["row"], s["r_case"])
print({y: CPI[y] for y in CPI})
(HERE / "fuel_assumptions.txt").write_text(json.dumps({"GAS": GAS_SENTENCE}, indent=1), encoding="utf-8")
