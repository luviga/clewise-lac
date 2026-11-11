"""Build sources.csv (all sources cited by this job) and constants.csv (fuel and plant constants)."""
import csv, re
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
LP = Path(__file__).resolve().parent.parent / "local_prices_20261109T085226Z"
COLS = ["id", "url", "title", "publisher", "date", "retrieval_date", "downloaded_file", "page_or_table", "notes"]

new = [
    dict(id="CSJ-001", url="https://www.eia.gov/dnav/pet/hist_xls/RBRTEa.xls", title="Europe Brent Spot Price FOB, annual (RBRTE)",
         publisher="U.S. Energy Information Administration", date="data to 2025", retrieval_date="2026-11-10", downloaded_file="RBRTEa.xls",
         page_or_table="sheet Data 1, rows dated 2018-06-30 to 2025-06-30", notes="Observed oil benchmark B(y) for oil products and crude"),
    dict(id="CSJ-002", url="https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDa.xls", title="Henry Hub Natural Gas Spot Price, annual (RNGWHHD)",
         publisher="U.S. Energy Information Administration", date="data to 2025", retrieval_date="2026-11-10", downloaded_file="RNGWHHDa.xls",
         page_or_table="sheet Data 1, rows dated 2018-06-30 to 2025-06-30", notes="Observed gas benchmark for US-sourced LNG; USD/MMBtu gross"),
    dict(id="CSJ-003", url="https://www.eia.gov/dnav/ng/xls/NG_MOVE_EXPC_S1_A.xls", title="U.S. Natural Gas Exports and Re-Exports by Country, annual (LNG by vessel to Jamaica: volume and price)",
         publisher="U.S. Energy Information Administration", date="data to 2025", retrieval_date="2026-11-10", downloaded_file="NG_MOVE_EXPC_S1_A.xls",
         page_or_table="sheets Data 1 and Data 2, columns Liquefied U.S. Natural Gas Exports by Vessel to Jamaica, rows 2018 to 2025",
         notes="Confirms US-sourced LNG cargoes to Jamaica each year 2018 to 2025 (2024: 13,201 MMcf at 5.55 USD/Mcf FOB)"),
    dict(id="CSJ-004", url="https://www.eia.gov/dnav/pet/xls/PET_PRI_SPT_S1_A.xls", title="Spot Prices for Crude Oil and Petroleum Products, annual",
         publisher="U.S. Energy Information Administration", date="data to 2025", retrieval_date="2026-11-10", downloaded_file="PET_PRI_SPT_S1_A.xls",
         page_or_table="sheet Data 6 (U.S. Gulf Coast Kerosene-Type Jet Fuel Spot Price FOB), row 2024; sheet Data 5 (USGC ULSD), row 2024",
         notes="Check value for the kerosene and jet ASSUMPTION"),
    dict(id="CSJ-005", url="https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Annual.xlsx",
         title="World Bank Commodity Price Data (The Pink Sheet), annual prices", publisher="World Bank", date="updated 2026-09-02",
         retrieval_date="2026-11-10", downloaded_file="CMO-Historical-Data-Annual.xlsx",
         page_or_table="sheet Annual Prices (Nominal), column G Coal South African, rows 2018 to 2025 (sheet rows 67 to 74); sheet Description row 6",
         notes="Observed coal benchmark: fob Richards Bay NAR 6000 kcal/kg"),
    dict(id="CSJ-006", url="https://api.bls.gov/publicAPI/v1/timeseries/data/ (POST {\"seriesid\":[\"CUUR0000SA0\"],\"startyear\":\"2016\",\"endyear\":\"2025\"})",
         title="Consumer Price Index for All Urban Consumers (CPI-U), all items, U.S. city average, not seasonally adjusted (CUUR0000SA0)",
         publisher="U.S. Bureau of Labor Statistics", date="data to 2025", retrieval_date="2026-11-10", downloaded_file="bls_cpiu_v1_post_2016_2025.json",
         page_or_table="series CUUR0000SA0, monthly values M01 to M12 for 2018 to 2025 (October 2025 not published)", notes="Deflator to real 2024 USD (rule F1)"),
    dict(id="CSJ-007", url="https://www.iea.org/reports/world-energy-outlook-2025", title="World Energy Outlook 2025",
         publisher="International Energy Agency (CC BY 4.0)", date="2025-11", retrieval_date="2026-11-10", downloaded_file="WorldEnergyOutlook2025.pdf",
         page_or_table="Table 2.3 Wholesale fossil fuel prices by scenario, page 109 (USD MER 2024; 2024, 2035, 2050; CPS, STEPS, NZE)",
         notes="Projection series. Written before the 2026 Middle East energy crisis."),
    dict(id="CSJ-008", url="https://www.petrojam.com/price/?wpv_view_count=1537-TCPID11733&wpcf_price_date=&wpv_paged=4",
         title="Petrojam Archives: Prices, petroleum product prices (weekly listing, pages 4 to 9 hold 2024; same URL with wpv_paged=1 to 10)",
         publisher="Petrojam Limited", date="weekly, 2023 to 2026", retrieval_date="2026-11-10",
         downloaded_file="petrojam/petrojam_price_p004.html; petrojam/petrojam_price_p005.html; petrojam/petrojam_price_p006.html; petrojam/petrojam_price_p007.html; petrojam/petrojam_price_p008.html; petrojam/petrojam_price_p009.html",
         page_or_table="table PETROLEUM PRODUCT PRICES, columns Gasolene 87 to ULSD, weeks dated 2024-01-04 to 2024-12-26",
         notes="J$ per litre; 2024 means equal MSET refinery billing prices, which include SCT"),
]

def main(plant_sources=None):
    used = set()
    for f in ["proposals.csv", "price_points_2024.csv", "fuel_constants.csv", "plant_costs.csv"]:
        p = HERE / f
        if not p.exists():
            continue
        d = pd.read_csv(p, keep_default_na=False)
        col = "source_ids" if "source_ids" in d.columns else "source_id"
        for v in d[col]:
            for s in re.split(r"[;,]\s*", str(v)):
                if s.strip():
                    used.add(s.strip())
    lps = pd.read_csv(LP / "sources.csv", keep_default_na=False)
    rows = []
    for r in lps.itertuples():
        if r.id in used:
            rows.append(dict(id=r.id, url=r.url, title=r.title, publisher=r.publisher, date=r.date, retrieval_date=r.retrieval_date,
                             downloaded_file=r.downloaded_file, page_or_table=r.page_or_table,
                             notes=f"reused from LAC_LOCAL_PRICES; file copied into downloads/. {r.rows_and_constants_supported}"))
    rows += [n for n in new if n["id"] in used]
    if plant_sources is not None and plant_sources.exists():
        ps = pd.read_csv(plant_sources, keep_default_na=False)
        rows += [dict(r._asdict()) for r in ps.itertuples(index=False) if r.id in used]
    missing = sorted(used - {r["id"] for r in rows})
    with open(HERE / "sources.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    print(len(rows), "sources written; ids cited but not defined:", missing)

if __name__ == "__main__":
    main(HERE / "plant_sources.csv")
