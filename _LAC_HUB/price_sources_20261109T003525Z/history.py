"""Step 2: annual averages 2018-2025 of each benchmark, converted to USD/GJ.
Reads only files in downloads/. Writes history_usd_per_gj.csv, conversion_factors.csv, monthly_benchmarks.csv.
Run: py -I history.py <output_folder>
"""
import sys, os
import pandas as pd

OUT = sys.argv[1]
DL = os.path.join(OUT, "downloads")
MMBTU_PER_GJ = 1 / 1.055056  # 1 MMBtu = 1.055056 GJ

URL_EIA_SPOT = "https://www.eia.gov/dnav/pet/xls/PET_PRI_SPT_S1_M.xls"
URL_EIA_REFOTH_AVG = "https://www.eia.gov/dnav/pet/xls/PET_PRI_REFOTH_A_EPPV_PWG_DPGAL_M.xls"
URL_EIA_REFOTH_RES = "https://www.eia.gov/dnav/pet/xls/PET_PRI_REFOTH_A_EPPR_PWG_DPGAL_M.xls"
URL_EIA_HH = "https://www.eia.gov/dnav/ng/xls/NG_PRI_FUT_S1_M.xls"
URL_EIA_LNGX = "https://www.eia.gov/dnav/ng/xls/NG_MOVE_EXPC_S1_M.xls"
URL_WB = "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"
URL_EPM = "https://www.eia.gov/electricity/monthly/xls/table_4_01continued.xlsx"
URL_EPM_COAL = "https://www.eia.gov/electricity/monthly/xls/table_4_01.xlsx"
URL_IPCC = "https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_1_Ch1_Introduction.pdf"
URL_UNSD = "https://unstats.un.org/unsd/energystats/pubs/yearbook/2023/09ii.pdf"

# Conversion factors: US gallons per metric ton (UNSD 2023 Yearbook Table II) and NCV TJ/Gg = GJ/t (IPCC 2006 V2 Ch1 Table 1.2)
CF = {
 # key: (gal_per_t, unsd_row, ncv, ipcc_row)
 "GSL": (357, "Motor gasoline", 44.3, "Motor Gasoline"),
 "DSL": (304, "Gas oil/diesel oil", 43.0, "Gas/Diesel Oil"),
 "JET": (326, "Kerosene-type jet fuel", 44.1, "Jet Kerosene"),
 "KER": (326, "Other kerosene", 43.8, "Other Kerosene"),
 "LPG": (489, "Liquefied petroleum gases (LPG)", 47.3, "Liquefied Petroleum Gases"),
 "FOI": (278, "Fuel oil", 40.4, "Residual Fuel Oil"),
 "AVG": (362, "Aviation gasoline", 44.3, "Aviation Gasoline"),
}
BBL_PER_T_CRUDE, NCV_CRUDE = 7.32, 42.3
GJ_PER_T_COAL_6000NAR = 6000 * 4.1868 / 1000  # 6000 kcal/kg NAR; 1 kcal = 4.1868 kJ

def eia_sheet(path, sheet, key):
    d = pd.read_excel(path, sheet_name=sheet, header=None)
    col = [c for c in range(d.shape[1]) if d.iloc[1, c] == key][0]
    s = pd.Series(pd.to_numeric(d.iloc[3:, col], errors="coerce").values,
                  index=pd.to_datetime(d.iloc[3:, 0])).dropna()
    s.index = s.index.to_period("M")
    return s

def wb(col_name):
    d = pd.read_excel(os.path.join(DL, "CMO-Historical-Data-Monthly.xlsx"), "Monthly Prices", header=None)
    col = [c for c in range(d.shape[1]) if str(d.iloc[4, c]).strip() == col_name][0]
    rows = d.iloc[6:, [0, col]].dropna(subset=[0])
    rows = rows[rows[0].astype(str).str.match(r"^\d{4}M\d{2}$")]
    s = pd.Series(pd.to_numeric(rows[col], errors="coerce").values,
                  index=pd.PeriodIndex([f"{x[:4]}-{x[5:]}" for x in rows[0]], freq="M")).dropna()
    return s

spot = os.path.join(DL, "PET_PRI_SPT_S1_M.xls")
series = {}
series["CRU_Brent"] = (eia_sheet(spot, "Data 1", "RBRTE"), "USD/bbl", "EIA Europe Brent Spot Price FOB (RBRTE)", URL_EIA_SPOT)
series["GSL_USGC"] = (eia_sheet(spot, "Data 2", "EER_EPMRU_PF4_RGC_DPG"), "USD/gal", "EIA U.S. Gulf Coast Conventional Gasoline Regular Spot Price FOB", URL_EIA_SPOT)
series["DSL_USGC"] = (eia_sheet(spot, "Data 5", "EER_EPD2DXL0_PF4_RGC_DPG"), "USD/gal", "EIA U.S. Gulf Coast Ultra-Low Sulfur No 2 Diesel Spot Price", URL_EIA_SPOT)
series["JET_USGC"] = (eia_sheet(spot, "Data 6", "EER_EPJK_PF4_RGC_DPG"), "USD/gal", "EIA U.S. Gulf Coast Kerosene-Type Jet Fuel Spot Price FOB", URL_EIA_SPOT)
series["LPG_MB"] = (eia_sheet(spot, "Data 7", "EER_EPLLPA_PF4_Y44MB_DPG"), "USD/gal", "EIA Mont Belvieu, TX Propane Spot Price FOB", URL_EIA_SPOT)
series["AVG_US_resale"] = (eia_sheet(os.path.join(DL, "PET_PRI_REFOTH_A_EPPV_PWG_DPGAL_M.xls"), "Data 1", "EMA_EPPV_PWG_R30_DPG"), "USD/gal", "EIA Gulf Coast (PADD 3) Aviation Gasoline Wholesale/Resale Price by Refiners (ends 2022-03)", URL_EIA_REFOTH_AVG)
series["FOI_US_resale"] = (eia_sheet(os.path.join(DL, "PET_PRI_REFOTH_A_EPPR_PWG_DPGAL_M.xls"), "Data 1", "EMA_EPPR_PWG_NUS_DPG"), "USD/gal", "EIA U.S. Residual Fuel Oil Wholesale/Resale Price by Refiners (ends 2022-03)", URL_EIA_REFOTH_RES)
series["NGS_HH"] = (eia_sheet(os.path.join(DL, "eia_ng", "NG_PRI_FUT_S1_M.xls"), "Data 1", "RNGWHHD"), "USD/MMBtu", "EIA Henry Hub Natural Gas Spot Price (RNGWHHD)", URL_EIA_HH)
lngx = os.path.join(DL, "eia_ng", "NG_MOVE_EXPC_S1_M.xls")
series["LNG_FOB_US_all"] = (eia_sheet(lngx, "Data 2", "N9133US3"), "USD/Mcf", "EIA Price of Liquefied U.S. Natural Gas Exports (N9133US3)", URL_EIA_LNGX)
series["LNG_FOB_US_to_DR"] = (eia_sheet(lngx, "Data 2", "NGM_EPG0_EVE_NUS-NDR_DMCF"), "USD/Mcf", "EIA Price of Liquefied U.S. Natural Gas Exports by Vessel to Dominican Republic", URL_EIA_LNGX)
series["LNG_FOB_US_to_JAM"] = (eia_sheet(lngx, "Data 2", "NGM_EPG0_EVE_NUS-NJM_DMCF"), "USD/Mcf", "EIA Price of Liquefied U.S. Natural Gas Exports by Vessel to Jamaica", URL_EIA_LNGX)
series["LNG_FOB_US_to_HON"] = (eia_sheet(lngx, "Data 2", "NGM_EPG0_EVE_NUS-NHO_DMCF"), "USD/Mcf", "EIA Price of U.S. Liquefied Natural Gas Exports by Vessel to Honduras", URL_EIA_LNGX)
series["LNG_FOB_US_to_PAN"] = (eia_sheet(lngx, "Data 2", "NGM_EPG0_EVE_NUS-NPM_DMCF"), "USD/Mcf", "EIA Price of Liquefied U.S. Natural Gas Exports to Panama", URL_EIA_LNGX)
series["NGS_HH_WB"] = (wb("Natural gas, US"), "USD/MMBtu", "World Bank Pink Sheet Natural gas, US (Henry Hub)", URL_WB)
series["LNG_Japan_WB"] = (wb("Liquefied natural gas, Japan"), "USD/MMBtu", "World Bank Pink Sheet Liquefied natural gas, Japan (cif import price)", URL_WB)
series["CRU_Brent_WB"] = (wb("Crude oil, Brent"), "USD/bbl", "World Bank Pink Sheet Crude oil, Brent", URL_WB)
series["COA_SAfrica_WB"] = (wb("Coal, South African **"), "USD/t", "World Bank Pink Sheet Coal, South African (fob Richards Bay, NAR 6000 kcal/kg)", URL_WB)
series["COA_Australia_WB"] = (wb("Coal, Australian"), "USD/t", "World Bank Pink Sheet Coal, Australian (fob Newcastle, 6000 kcal/kg)", URL_WB)

# monthly file
mon = pd.DataFrame({k: v[0] for k, v in series.items()})
mon = mon[(mon.index >= pd.Period("2017-01", "M"))]
mon.index = mon.index.astype(str)
mon.to_csv(os.path.join(OUT, "monthly_benchmarks.csv"), index_label="month")

# conversion to USD/GJ
def to_gj(key, unit):
    if unit == "USD/gal":
        fuel = key.split("_")[0]
        g, _, n, _ = CF[fuel]
        return g / n, f"x {g} gal/t (UNSD 2023 Table II, {CF[fuel][1]}) / {n} GJ/t (IPCC 2006 Table 1.2, {CF[fuel][3]})"
    if unit == "USD/bbl":
        return BBL_PER_T_CRUDE / NCV_CRUDE, f"x {BBL_PER_T_CRUDE} bbl/t (UNSD 2023 Table II, Conventional crude oil) / {NCV_CRUDE} GJ/t (IPCC 2006 Table 1.2, Crude Oil)"
    if unit == "USD/MMBtu":
        return MMBTU_PER_GJ, "/ 1.055056 GJ per MMBtu (gross calorific basis as published)"
    if unit == "USD/Mcf":
        return MMBTU_PER_GJ / 1.037, "/ 1.037 MMBtu per Mcf (EIA FAQ id=45, 2025 average heat content 1,037 Btu/cf) / 1.055056 GJ per MMBtu (gross basis)"
    if unit == "USD/t":
        return 1 / GJ_PER_T_COAL_6000NAR, f"/ {GJ_PER_T_COAL_6000NAR:.3f} GJ/t (6000 kcal/kg NAR x 4.1868 kJ/kcal)"
    raise ValueError(unit)

rows = []
for key, (s, unit, name, url) in series.items():
    f, how = to_gj(key, unit)
    for y in range(2018, 2026):
        sy = s[(s.index.year == y)]
        if len(sy) == 0:
            continue
        avg = sy.mean()
        rows.append(dict(benchmark=key, series=name, year=y, months=len(sy), value_published=round(avg, 4),
                         unit_published=unit, factor_to_usd_per_gj=round(f, 5), usd_per_gj=round(avg * f, 3),
                         conversion=how, source_url=url,
                         note=("" if len(sy) == 12 else f"average of {len(sy)} months")))
# petroleum coke and US delivered coal (annual, from EIA EPM table 4.1)
for key, fn, col_cost, name, url in [
    ("COK_US_power", "table_4_01continued.xlsx", 3, "EIA Electric Power Monthly Table 4.1 (continued): average cost of petroleum coke delivered for electricity generation, all sectors", URL_EPM),
    ("COA_US_power", "table_4_01.xlsx", 3, "EIA Electric Power Monthly Table 4.1: average cost of coal delivered for electricity generation, all sectors", URL_EPM_COAL)]:
    d = pd.read_excel(os.path.join(DL, "eia_epm", fn), header=None)
    seen = set()
    for i in range(len(d)):
        y = str(d.iloc[i, 0]).strip()
        if y.isdigit() and 2018 <= int(y) <= 2025 and y not in seen:
            seen.add(y)
            v = float(d.iloc[i, col_cost])
            rows.append(dict(benchmark=key, series=name, year=int(y), months=12, value_published=v,
                             unit_published="USD/MMBtu", factor_to_usd_per_gj=round(MMBTU_PER_GJ, 5),
                             usd_per_gj=round(v * MMBTU_PER_GJ, 3),
                             conversion="/ 1.055056 GJ per MMBtu (EIA heat content basis, gross)", source_url=url, note="annual total row"))
h = pd.DataFrame(rows)

# proxy benchmarks (fuel oil, aviation gasoline), defined as ratios to published benchmarks
cr = pd.read_csv(os.path.join(DL, "CR", "CR_regulator_2024.csv"))
cr["date_or_period"] = cr["date_or_period"].astype(str)
fob = cr[(cr.fuel.str.contains("Bunker")) & (cr.component == "fob_reference") & (cr.unit == "USD/bbl") & cr.date_or_period.str.match(r"^2024-\d\d$")]
FOB_FOI_2024 = fob.value.mean() * 6.62 / 40.4   # USD/bbl x 6.62 bbl/t (UNSD, fuel oil) / 40.4 GJ/t (IPCC)
br24 = h[(h.benchmark == "CRU_Brent") & (h.year == 2024)].usd_per_gj.iloc[0]
R_FOI = round(FOB_FOI_2024 / br24, 3)
g = h[h.benchmark == "AVG_US_resale"].set_index("year").usd_per_gj / h[h.benchmark == "GSL_USGC"].set_index("year").usd_per_gj
R_AVG = round(g.loc[2018:2021].mean(), 3)
extra = []
for y in range(2018, 2026):
    b = h[(h.benchmark == "CRU_Brent") & (h.year == y)].usd_per_gj.iloc[0]
    gs = h[(h.benchmark == "GSL_USGC") & (h.year == y)].usd_per_gj.iloc[0]
    extra.append(dict(benchmark="FOI_proxy", series=f"PROXY fuel oil = EIA Brent x {R_FOI} (ratio of ARESEP 2024 'Precio FOB estimado' bunker, {len(fob)} months mean {fob.value.mean():.2f} USD/bbl, to 2024 Brent, USD/GJ basis)",
                      year=y, months=12, value_published=None, unit_published="USD/GJ", factor_to_usd_per_gj=1, usd_per_gj=round(b * R_FOI, 3),
                      conversion="ratio applied to CRU_Brent USD/GJ", source_url="https://www.eia.gov/dnav/pet/xls/PET_PRI_SPT_S1_M.xls; ARESEP resolutions RE-0002 to RE-0083-IE-2024 (see sources.csv)", note="proxy"))
    extra.append(dict(benchmark="AVG_proxy", series=f"PROXY aviation gasoline = EIA USGC gasoline x {R_AVG} (EIA PADD 3 avgas resale / USGC gasoline, USD/GJ, 2018-2021 mean)",
                      year=y, months=12, value_published=None, unit_published="USD/GJ", factor_to_usd_per_gj=1, usd_per_gj=round(gs * R_AVG, 3),
                      conversion="ratio applied to GSL_USGC USD/GJ", source_url=URL_EIA_REFOTH_AVG + "; " + URL_EIA_SPOT, note="proxy"))
h = pd.concat([h, pd.DataFrame(extra)], ignore_index=True)
print("R_FOI", R_FOI, "FOB_FOI_2024", round(FOB_FOI_2024, 3), "R_AVG", R_AVG)
h.to_csv(os.path.join(OUT, "history_usd_per_gj.csv"), index=False)

# ratios used by projection rules (USD/GJ basis)
pv = h.pivot(index="year", columns="benchmark", values="usd_per_gj")
rat = pd.DataFrame({
    "GSL_to_Brent": pv["GSL_USGC"] / pv["CRU_Brent"],
    "DSL_to_Brent": pv["DSL_USGC"] / pv["CRU_Brent"],
    "JET_to_Brent": pv["JET_USGC"] / pv["CRU_Brent"],
    "LPG_to_Brent": pv["LPG_MB"] / pv["CRU_Brent"],
    "FOI_US_resale_to_Brent": pv["FOI_US_resale"] / pv["CRU_Brent"],
    "AVG_PADD3_to_GSL_USGC": pv["AVG_US_resale"] / pv["GSL_USGC"],
    "COK_US_to_COA_SAfrica": pv["COK_US_power"] / pv["COA_SAfrica_WB"],
    "COA_SAfrica_to_Brent": pv["COA_SAfrica_WB"] / pv["CRU_Brent"],
    "LNG_FOB_DR_minus_HH_usd_per_gj": pv["LNG_FOB_US_to_DR"] - pv["NGS_HH"],
    "LNG_FOB_DR_to_HH": pv["LNG_FOB_US_to_DR"] / pv["NGS_HH"],
    "LNG_FOB_JAM_to_HH": pv["LNG_FOB_US_to_JAM"] / pv["NGS_HH"],
}).round(3)
rat.to_csv(os.path.join(OUT, "history_ratios.csv"))
print(pv.round(2).to_string())
print(rat.to_string())
