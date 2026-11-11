"""Build sources.csv (new CSD records plus reused LAC_LOCAL_PRICES records) and constants.csv."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import *

R = RETRIEVED
NEW = [
    dict(id="CSD-001", url="https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2016&endyear=2025&annualaverage=true",
         title="CPI for All Urban Consumers (CPI-U), all items, U.S. city average, not seasonally adjusted, series CUUR0000SA0", publisher="U.S. Bureau of Labor Statistics",
         date="series to 2025", downloaded_file="bench/bls_CUUR0000SA0_get.json", page_or_table="JSON Results.series[0].data, period M13 (Annual), years 2018 to 2025"),
    dict(id="CSD-002", url="https://www.eia.gov/dnav/pet/hist_xls/RBRTEa.xls", title="Europe Brent Spot Price FOB, annual (RBRTE)",
         publisher="U.S. Energy Information Administration", date="series to 2025", downloaded_file="bench/RBRTEa.xls", page_or_table="sheet Data 1, rows 2018 to 2025"),
    dict(id="CSD-003", url="https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDa.xls", title="Henry Hub Natural Gas Spot Price, annual (RNGWHHD)",
         publisher="U.S. Energy Information Administration", date="series to 2025", downloaded_file="bench/RNGWHHDa.xls", page_or_table="sheet Data 1, rows 2018 to 2025"),
    dict(id="CSD-004", url="https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Annual.xlsx",
         title="World Bank Commodity Price Data (The Pink Sheet), annual prices", publisher="World Bank", date="updated 2026-09-02",
         downloaded_file="bench/CMO-Historical-Data-Annual.xlsx", page_or_table="sheet Annual Prices (Nominal), column G Coal, South African (USD/mt), rows 2018 to 2025; sheet Description row 6 (fob Richards Bay NAR 6000 kcal/kg)"),
    dict(id="CSD-005", url="https://www.iea.org/reports/world-energy-outlook-2025", title="World Energy Outlook 2025 (CC BY 4.0)", publisher="International Energy Agency",
         date="2025-11", downloaded_file="weo/WorldEnergyOutlook2025.pdf", page_or_table="Table 2.3 Wholesale fossil fuel prices by scenario, page 109; Table B.4b, page 455"),
    dict(id="CSD-006", url="https://totalenergies.com/newsroom/liquefied-natural-gas-totalenergies-will-supply-400000-tons-lng-year-15-years/?lang=eng",
         title="Liquefied Natural Gas: TotalEnergies will supply 400,000 tons of LNG per year for 15 years in the Dominican Republic", publisher="TotalEnergies",
         date="2025-04-15", downloaded_file="gas/te_press.html", page_or_table="press release text: heads of agreement with ENADOM (AES Dominicana and Energas), start mid-2027, price indexed to Henry Hub"),
    dict(id="CSD-007", url="https://www.eia.gov/dnav/ng/xls/NG_MOVE_EXPC_S1_A.xls", title="U.S. Natural Gas Exports and Re-Exports by Country, annual",
         publisher="U.S. Energy Information Administration", date="series to 2025", downloaded_file="gas/NG_MOVE_EXPC_S1_A.xls",
         page_or_table="sheet Data 1, column NGM_EPG0_EVE_NUS-NDR_MMCF (exports to the Dominican Republic, MMcf), 2024 = 90,594; sheet Data 2 column NGM_EPG0_EVE_NUS-NDR_DMCF (price USD/Mcf)"),
    dict(id="CSD-008", url="https://cne.gob.do/wp-admin/admin-ajax.php?action=outofthebox-download&OutoftheBoxpath=%2Fpen2022-2037.pdf&lastpath=%2F&account_id=dbid:AAAGpYR0ODh0f0jJZRlCsjhWYMYovXEms_Q&listtoken=255346f20b4341ea85f9ebf4917022f4&dl=1",
         title="Plan Energetico Nacional 2022-2036 (file PEN2022-2037.pdf), listed at https://cne.gob.do/documentos/tecnicos/pen/", publisher="Comision Nacional de Energia (Republica Dominicana)",
         date="2022", downloaded_file="pen/PEN2022-2037.pdf", page_or_table="Tabla 220 page 345, Tabla 223 page 347, Tabla 229 page 350 (Supuestos proyecto generico)"),
    dict(id="CSD-009", url="https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2023/Aug/IRENA_Renewable_power_generation_costs_in_2022.pdf",
         title="Renewable Power Generation Costs in 2022", publisher="International Renewable Energy Agency", date="2023-08",
         downloaded_file="irena/IRENA_Renewable_power_generation_costs_in_2022.pdf", page_or_table="Table H.1 page 15; hydropower O&M page 162; bioenergy O&M page 183"),
    dict(id="CSD-010", url="https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2025/Jul/IRENA_TEC_RPGC_in_2024_2025.pdf",
         title="Renewable Power Generation Costs in 2024", publisher="International Renewable Energy Agency", date="2025-07",
         downloaded_file="irena/IRENA_TEC_RPGC_in_2024_2025.pdf", page_or_table="Table S1 page 15 (2024 USD/kW)"),
    dict(id="CSD-011", url="https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2023/ATBe.parquet", title="Annual Technology Baseline 2023, electricity (ATBe)",
         publisher="National Renewable Energy Laboratory", date="2023 (file dated 2024-01-26)", downloaded_file="atb/ATBe_2023.parquet",
         page_or_table="rows filtered by technology, techdetail, core_metric_parameter, scenario Moderate (or as stated), core_metric_case Market, crpyears 20"),
    dict(id="CSD-012", url="https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2024/v3.0.0/ATBe.parquet", title="Annual Technology Baseline 2024 v3.0.0, electricity (ATBe)",
         publisher="National Renewable Energy Laboratory", date="2024", downloaded_file="atb/ATBe_2024_v3.0.0.parquet",
         page_or_table="rows filtered by technology, techdetail, core_metric_parameter, scenario Moderate, core_metric_case Market, crpyears 20"),
    dict(id="CSD-013", url="https://iea.blob.core.windows.net/assets/86ede39e-4436-42d7-ba2a-edf61467e070/WorldEnergyOutlook2023.pdf", title="World Energy Outlook 2023 (CC BY 4.0)",
         publisher="International Energy Agency", date="2023-10", downloaded_file="weo/WorldEnergyOutlook2023.pdf", page_or_table="Table B.4a Technology costs in selected regions in the Stated Policies Scenario, page 301"),
]
for n in NEW: n["retrieval_date"] = R; n["origin"] = "downloaded by this job"

def ids_in(series):
    s = set()
    for v in series.dropna().astype(str):
        for t in re.split(r"[;,\s]+", v):
            if re.match(r"^(DR|GEN|CSD)-\d{3}$", t): s.add(t)
    return s
used = set()
for f, col in [("proposals.csv", "source_ids"), ("fuel_prices.csv", "source_ids"), ("price_points_2024.csv", "source_ids"), ("plant_costs.csv", "source_ids")]:
    used |= ids_in(pd.read_csv(os.path.join(JOB, f))[col])
cf = pd.read_csv(os.path.join(JOB, "constants_fuel.csv")); used |= ids_in(cf.source_id)
used |= {"CSD-013"}
lp = pd.read_csv(os.path.join(LP, "sources.csv"))
reused = lp[lp.id.isin(used)].copy()
def remap(f):
    parts = [p.strip() for p in str(f).split(";") if p.strip()]
    return "; ".join("lp/" + p for p in parts)
reused["downloaded_file"] = reused.downloaded_file.map(remap)
reused["origin"] = "reused from LAC_LOCAL_PRICES (file copied into downloads/lp)"
src = pd.concat([pd.DataFrame(NEW), reused], ignore_index=True)
src = src[["id", "url", "title", "publisher", "date", "retrieval_date", "downloaded_file", "page_or_table", "origin"]]
missing = sorted(used - set(src.id))
src.to_csv(os.path.join(JOB, "sources.csv"), index=False)
print("sources", len(src), "new", len(NEW), "reused", len(reused), "missing ids", missing)

# constants.csv: fuel constants plus plant conversion constants
extra = pd.DataFrame([
    dict(name="GJ_PER_MWH", value=3.6, unit="GJ per MWh", source_id="GEN-003", page_or_table="Appendix B.8 (1 kWh = 3.6 MJ)", derivation=""),
    dict(name="PEN_T220_VOM", value=2.55, unit="USD/MWh", source_id="CSD-008", page_or_table="Tabla 220, page 345", derivation=""),
    dict(name="PEN_T223_VOM", value=4.50, unit="USD/MWh", source_id="CSD-008", page_or_table="Tabla 223, page 347", derivation=""),
    dict(name="PEN_T229_VOM", value=5.69, unit="USD/MWh", source_id="CSD-008", page_or_table="Tabla 229, page 350", derivation=""),
    dict(name="IRENA22_BIO_FOM_SHARE_RANGE", value="0.02 to 0.06", unit="share of total installed cost per year", source_id="CSD-009", page_or_table="page 183", derivation=""),
    dict(name="IRENA22_HYD_OM_SHARE_IEA", value=0.025, unit="share of investment per year", source_id="CSD-009", page_or_table="page 162", derivation="IEA average quoted by IRENA"),
    dict(name="US_LNG_EXPORTS_TO_DR_2024", value=90594, unit="MMcf", source_id="CSD-007", page_or_table="sheet Data 1, 2024", derivation=""),
    dict(name="DR_LNG_IMPORTS_2024_T", value=1842142.29, unit="t", source_id="DR-003", page_or_table="cmdCode 271111, netWgt", derivation="1842142290 kg / 1000"),
    dict(name="DR_LNG_IMPORTS_2024_MMCF_GROSS", value=round(1842142.29 * 48.0 / 0.9 / 1.055056 / 1.037 / 1000, 1), unit="MMcf (gross)", source_id="DR-003;GEN-002;GEN-006;GEN-003;GEN-005",
         page_or_table="derived", derivation="1,842,142.29 t x 48.0 GJ/t net / 0.9 / 1.055056 GJ/MMBtu / 1.037 MMBtu/Mcf / 1000"),
])
C = pd.concat([cf, extra], ignore_index=True)
C.to_csv(os.path.join(JOB, "constants.csv"), index=False)
print("constants", len(C)); print(extra[["name", "value"]].tail(1).to_string())
