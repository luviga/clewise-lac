"""Write sources.csv (every source id cited in proposals.csv, price_points_2024.csv, fuel_constants.csv and plant_costs.csv)
and constants.csv (fuel constants, WEO 2025 values, CPI-U, plant unit constants)."""
import csv, re
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
LP = HERE.parent / "local_prices_20261109T085226Z"
COLS = ["id", "url", "title", "publisher", "date", "retrieval_date", "downloaded_file", "page_or_table", "notes"]
R = "2026-11-10"
CREE = "https://www.cree.gob.hn/wp-content/uploads/2019/02/"
TAB = "Tabla 'Costos reales de generacion' (Tabla 2 in 2022 and 2023 reports, Tabla 3 later), rows MER under Contratos and Oportunidad"
new = [
    dict(id="CSH-001", url="https://www.eia.gov/dnav/pet/hist_xls/RBRTEa.xls", title="Europe Brent Spot Price FOB, annual (RBRTE)", publisher="U.S. Energy Information Administration",
         date="data to 2025", downloaded_file="RBRTEa.xls", page_or_table="sheet Data 1, rows dated 2018-06-30 to 2025-06-30", notes="Observed oil benchmark for oil products"),
    dict(id="CSH-002", url="https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDa.xls", title="Henry Hub Natural Gas Spot Price, annual (RNGWHHD)", publisher="U.S. Energy Information Administration",
         date="data to 2025", downloaded_file="RNGWHHDa.xls", page_or_table="sheet Data 1, rows dated 2018-06-30 to 2025-06-30", notes="Observed gas benchmark; USD/MMBtu gross"),
    dict(id="CSH-004", url="https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Annual.xlsx",
         title="World Bank Commodity Price Data (The Pink Sheet), annual prices", publisher="World Bank", date="updated September 2026", downloaded_file="CMO-Historical-Data-Annual.xlsx",
         page_or_table="sheet Annual Prices (Nominal), column G Coal, South African, rows 2018 to 2025; sheet Description (fob Richards Bay, NAR 6000 kcal/kg)",
         notes="Observed coal benchmark (Atlantic); the monthly file was also opened and has no Colombian coal series"),
    dict(id="CSH-005", url="https://api.bls.gov/publicAPI/v1/timeseries/data/ (POST {\"seriesid\":[\"CUUR0000SA0\"],\"startyear\":\"2016\",\"endyear\":\"2025\"})",
         title="Consumer Price Index for All Urban Consumers (CPI-U), all items, U.S. city average, not seasonally adjusted (CUUR0000SA0)", publisher="U.S. Bureau of Labor Statistics",
         date="data to 2025", downloaded_file="bls_cpiu_v1_2016_2025.json", page_or_table="series CUUR0000SA0, monthly values M01 to M12 for 2018 to 2025 (October 2025 not published)",
         notes="Deflator to real 2024 USD (rule F1)"),
    dict(id="CSH-006", url="https://www.iea.org/reports/world-energy-outlook-2025", title="World Energy Outlook 2025", publisher="International Energy Agency (CC BY 4.0)",
         date="2025-11", downloaded_file="WorldEnergyOutlook2025.pdf",
         page_or_table="Table 2.3 Wholesale fossil fuel prices by scenario, PDF page 109 (USD MER 2024; 2024, 2035, 2050; CPS, STEPS, NZE); Annex B Tables B.4a and B.4b checked for plant costs",
         notes="Projection series. Written before the 2026 Middle East energy crisis."),
    dict(id="CSH-007", url="https://comtradeapi.un.org/public/v1/preview/C/A/HS?period=2024&partnerCode=340&flowCode=X&cmdCode=270112,271311",
         title="UN Comtrade public preview API: exports to Honduras 2024 reported by partner countries (mirror), HS 270112 and 271311", publisher="UN Comtrade (reported by exporting countries)",
         date="2024 data", downloaded_file="HON_extra/comtrade_mirror_exports_to_HON_2024_coal_coke.json",
         page_or_table="records reporterCode 170 (Colombia) cmdCode 270112: fobvalue 2733526, netWgt 27500000 kg; reporterCode 842 (USA) cmdCode 270112 and 271311",
         notes="Confirms the Colombian origin of Honduras coal (benchmark and WEO series choice)"),
    dict(id="CSH-010", url="https://cnd.enee.hn/wp-content/uploads/2024/07/G02-Anexos-PIEG-2024-2033-Aprobado.pdf",
         title="Anexos del Plan Indicativo de Expansion de la Generacion 2024-2033 (aprobado)", publisher="Operador del Sistema (ODS) / Centro Nacional de Despacho (CND), Honduras",
         date="2024-07", downloaded_file="plant/G02-Anexos-PIEG-2024-2033-Aprobado.pdf",
         page_or_table="Anexo B: Tabla B-1 (PDF page 16), Tabla B-2 (PDF page 18, columns Central 50 MW), Tabla B-3 (PDF page 19); 2023 to 2042",
         notes="Yearly capital and fixed O&M paths of the PV-plus-battery and wind-plus-battery candidates"),
    dict(id="CSH-011", url="https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2023/Aug/IRENA_Renewable_power_generation_costs_in_2022.pdf",
         title="Renewable Power Generation Costs in 2022", publisher="International Renewable Energy Agency (IRENA)", date="2023-08 (values in 2022 USD)",
         downloaded_file="plant/IRENA_Renewable_power_generation_costs_in_2022.pdf",
         page_or_table="Table H.1 page 15 (bioenergy 2,162 USD/kW, 2022); page 177 (same value in text); page 183 (bioenergy variable O&M 0.005 USD/kWh; fixed O&M 2 to 6 percent of installed cost)",
         notes="Edition cited by the CLEWISE Data in Brief [13]"),
    dict(id="CSH-012", url="https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2026/Jul/IRENA_TEC_RPGC_in_2025_2026.pdf",
         title="Renewable Power Generation Costs in 2025", publisher="International Renewable Energy Agency (IRENA)", date="2026-07 (values in 2025 USD)",
         downloaded_file="plant/IRENA_TEC_RPGC_in_2025_2026.pdf", page_or_table="Figure S1 page 14 (bioenergy 3,606 USD/kW, 2025); bioenergy chapter, variable O&M 0.004 USD/kWh",
         notes="Newest IRENA edition; checked as a lead, recorded in GAPS"),
    dict(id="CSH-013", url="https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/csv/2024/v4.0.0/ATBe.csv",
         title="Annual Technology Baseline 2024, Electricity, summary CSV (ATBe.csv)", publisher="National Renewable Energy Laboratory (NREL) via Open Energy Data Initiative",
         date="ATB 2024 v4.0.0 (values in 2022 USD)", downloaded_file="plant/ATBe_2024_v4.0.0.csv",
         page_or_table="rows scenario Moderate, core_metric_case Market, crpyears 30; UtilityPV Class1, ResPV Class1, LandbasedWind Class4, Utility-Scale PV-Plus-Battery Class1, Biopower Dedicated; parameters OCC and Fixed O&M; years 2022 to 2050",
         notes="ODS PIEG 2026-2035 Anexos A.2 projects wind, PV and hybrid costs with the ATB 2024 Moderate rates"),
    dict(id="CSH-014", url="https://www.iea.org/files/86ede39e-4436-42d7-ba2a-edf61467e070/WorldEnergyOutlook2023.pdf", title="World Energy Outlook 2023",
         publisher="International Energy Agency", date="2023-10 (values in 2022 USD)", downloaded_file="plant/WorldEnergyOutlook2023.pdf",
         page_or_table="Annex B Table B.4a (PDF page 301) and Table B.5 (PDF page 305)", notes="Edition cited by the CLEWISE Data in Brief [14]; checked as a lead"),
    dict(id="CSH-020", url=CREE + "Informe-de-Ajuste-Tarifario-Abr-Jun-2022.pdf", title="Informe de Ajuste Tarifario Abril-Junio 2022", publisher="Comision Reguladora de Energia Electrica (CREE), Honduras",
         date="2022", downloaded_file="imp/cree_Informe-de-Ajuste-Tarifario-Abr-Jun-2022.pdf", page_or_table=TAB + ", December 2021 to February 2022, pages 10 to 11", notes="MER import cost and energy"),
    dict(id="CSH-021", url=CREE + "Informe-de-Ajuste-Tarifario-Jul-Sep-2022.pdf", title="Informe de Ajuste Tarifario Julio-Septiembre 2022", publisher="Comision Reguladora de Energia Electrica (CREE), Honduras",
         date="2022", downloaded_file="imp/cree_Informe-de-Ajuste-Tarifario-Jul-Sep-2022.pdf", page_or_table=TAB + ", March to May 2022, pages 10 to 11", notes="MER import cost and energy"),
    dict(id="CSH-022", url=CREE + "Informe-de-Ajuste-Tarifario-Oct-Dic-2022-.pdf", title="Informe de Ajuste Tarifario Octubre-Diciembre 2022", publisher="Comision Reguladora de Energia Electrica (CREE), Honduras",
         date="2022", downloaded_file="imp/cree_Informe-de-Ajuste-Tarifario-Oct-Dic-2022-.pdf", page_or_table=TAB + ", June to August 2022, pages 9 to 11", notes="MER import cost and energy"),
    dict(id="CSH-023", url=CREE + "Informe-de-1er-Ajuste-Tarifario-2023_CREE_F.pdf", title="Informe de Ajuste Tarifario Primer Trimestre 2023", publisher="Comision Reguladora de Energia Electrica (CREE), Honduras",
         date="2022-12", downloaded_file="imp/cree_Informe-de-1er-Ajuste-Tarifario-2023_CREE_F.pdf", page_or_table=TAB + ", September to November 2022, pages 10 to 11", notes="MER import cost and energy"),
    dict(id="CSH-024", url=CREE + "Informe-de-2do-Ajuste-Tarifario-2023.pdf", title="Informe de Ajuste Tarifario Segundo Trimestre 2023", publisher="Comision Reguladora de Energia Electrica (CREE), Honduras",
         date="2023-03", downloaded_file="imp/cree_Informe-de-2do-Ajuste-Tarifario-2023.pdf", page_or_table=TAB + ", December 2022 to February 2023, pages 11 to 12", notes="MER import cost and energy"),
    dict(id="CSH-025", url=CREE + "Informe-de-3er-Ajuste-Tarifario-2023-Final.pdf", title="Informe de Ajuste Tarifario Tercer Trimestre 2023", publisher="Comision Reguladora de Energia Electrica (CREE), Honduras",
         date="2023", downloaded_file="imp/cree_Informe-de-3er-Ajuste-Tarifario-2023-Final.pdf", page_or_table=TAB + ", March to May 2023, pages 11 to 12", notes="MER import cost and energy"),
    dict(id="CSH-026", url=CREE + "Informe-de-4to-Ajuste-Tarifario-2023-Final.pdf", title="Informe de Ajuste Tarifario Cuarto Trimestre 2023", publisher="Comision Reguladora de Energia Electrica (CREE), Honduras",
         date="2023", downloaded_file="imp/cree_Informe-de-4to-Ajuste-Tarifario-2023-Final.pdf", page_or_table=TAB + ", June to August 2023, pages 11 to 12", notes="MER import cost and energy"),
    dict(id="CSH-027", url="https://crie.org.gt/wp-content/uploads/2025/04/Informe-Estadistico-Anual-2024.pdf", title="Informe Estadistico Anual 2024, Mercado Electrico Regional",
         publisher="Comision Regional de Interconexion Electrica (CRIE)", date="2025-04", downloaded_file="imp/crie_Informe-Estadistico-Anual-2024.pdf",
         page_or_table="Tabla 6 page 17 (MER withdrawals by country 2018 to 2024; Honduras 158.80 GWh in 2024); Figura 20 page 33 (nodal prices)", notes="Volume check of the CREE import data"),
]
for n in new:
    n["retrieval_date"] = R
OVR = {  # locators for reused LAC_LOCAL_PRICES sources used here for other values
    "HON-016": "Tabla 19 page 46 (technology costs, 2024 USD); sections 4.3.2 to 4.3.12 pages 42 to 46; section 5.3.4 page 56 (coal: FOB Colombia); section 5.3.5 pages 56 to 57 (LNG chain referenced to Henry Hub)",
    "HON-017": "Anexos A.2 page 22 (cost projections with NREL ATB 2024 Moderate rates from 2024); Anexo D pages 40 to 41 (LNG chain)",
    "HON-018": "Tabla 7 (PDF page 42, printed 42 of 104), technology costs referenced to 2023; sections 4.6.1 to 4.6.11 pages 36 to 41",
    "HON-009": TAB + ", September to November 2023, pages 13 to 14",
    "HON-010": TAB + ", December 2023 to February 2024, pages 18 to 20",
    "HON-011": TAB + ", March to May 2024, pages 18 to 20",
    "HON-012": TAB + ", June to August 2024, pages 18 to 20",
    "HON-013": TAB + ", September to November 2024, pages 18 to 20",
    "HON-014": TAB + ", December 2024, pages 18 to 19",
}

def main():
    used = set()
    for f in ["proposals.csv", "price_points_2024.csv", "fuel_constants.csv", "plant_costs.csv"]:
        d = pd.read_csv(HERE / f, keep_default_na=False)
        col = "source_ids" if "source_ids" in d.columns else "source_id"
        for v in d[col]:
            used |= {s.strip() for s in re.split(r"[;,]\s*", str(v)) if s.strip()}
    used |= {"CSH-012", "CSH-014", "CSH-027"}  # opened and checked; cited in GAPS and the search log
    lps = pd.read_csv(LP / "sources.csv", keep_default_na=False)
    rows = []
    for r in lps.itertuples():
        if r.id in used:
            loc = OVR.get(r.id, r.page_or_table)
            if r.id in OVR:
                loc = f"{OVR[r.id]}; also (LAC_LOCAL_PRICES use) {r.page_or_table}"
            rows.append(dict(id=r.id, url=r.url, title=r.title, publisher=r.publisher, date=r.date, retrieval_date=r.retrieval_date,
                             downloaded_file=r.downloaded_file, page_or_table=loc,
                             notes=f"reused source id; file copied into downloads/. {r.rows_and_constants_supported}"))
    rows += [n for n in new if n["id"] in used]
    missing = sorted(used - {r["id"] for r in rows})
    with open(HERE / "sources.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    print(len(rows), "sources written; ids cited but not defined:", missing)
    # constants
    c = pd.read_csv(HERE / "fuel_constants.csv", keep_default_na=False)
    extra = pd.DataFrame([
        dict(name="GJ_PER_MWH", value=3.6, unit="GJ per MWh", source_id="GEN-003", page_or_table="NIST SP 811 Appendix B.8, PDF page 63 (kilowatt hour = 3.6 E+06 joule)", derivation="1 kWh = 3.6 MJ"),
    ])
    pd.concat([c, extra]).to_csv(HERE / "constants.csv", index=False)
    print(len(c) + len(extra), "constants")

if __name__ == "__main__":
    main()
