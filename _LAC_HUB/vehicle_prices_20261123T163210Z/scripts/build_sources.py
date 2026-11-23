"""Write <CC>/sources_<CC>.csv with the columns of the cost-sources files plus source_type.

Each country file lists the sources its proposal rows cite, the sources named in their
derivations (CPI, exchange rates, ATB, HS nomenclature) and the country's own downloads that were
searched but give no unit counts.

    python -I scripts/build_sources.py
"""
import csv
import os

JOB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CCS = ["CR", "DR", "GUA", "HON", "JAM"]
RET = "2026-11-23"
CT = ("https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode={rc}&period=<year>&partnerCode=0"
      "&flowCode=M&cmdCode=<the HS 6-digit codes of vehicle_class_map.csv>&includeDesc=true")
RC = {"CR": 188, "DR": 214, "GUA": 320, "HON": 340, "JAM": 388}
NAME = {"CR": "Costa Rica", "DR": "Dominican Republic", "GUA": "Guatemala", "HON": "Honduras", "JAM": "Jamaica"}

COLS = ["id", "url", "title", "publisher", "date", "retrieval_date", "downloaded_file", "page_or_table",
        "notes", "source_type"]

COMMON = [
    ["GEN-001", "https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2005&endyear=2014&annualaverage=true "
     "(and startyear=2015&endyear=2024, startyear=2016&endyear=2025)",
     "Consumer Price Index for All Urban Consumers (CPI-U), All items in U.S. city average, series CUUR0000SA0, annual averages",
     "U.S. Bureau of Labor Statistics", "data as published to 2026-11", "2026-11-22",
     "downloads/GEN/bls_CUUR0000SA0_2005_2014_annualaverage.json; downloads/GEN/bls_CUUR0000SA0_2015_2024_annualaverage.json; "
     "downloads/GEN/bls_CUUR0000SA0_2016_2025_annualaverage.json",
     "JSON Results.series[0].data, period M13", "Factor to 2024 US$ = CPI(2024) / CPI(year): 2019 1.226992, 2020 1.212039, "
     "2021 1.157652, 2022 1.071873, 2023 1.029494.", "price_index"],
    ["WDI-001", "https://api.worldbank.org/v2/en/indicator/PA.NUS.FCRF?downloadformat=csv",
     "World Development Indicators: Official exchange rate (LCU per US$, period average), PA.NUS.FCRF",
     "World Bank", "last updated 2026-11-11", RET, "downloads/wdi/WDI_PA.NUS.FCRF_csv.zip",
     "API_PA.NUS.FCRF_DS2_en_csv_v2_73080.csv, rows CRI, DOM, GTM, HND, JAM, columns 2019 to 2023",
     "Used only for values published in local currency; every statistic used so far is published in US$.",
     "exchange_rate"],
    ["GEN-101", "https://oedi-data-lake.s3.amazonaws.com/ATB/transportation/csv/2022/vehicles/vehicles.csv",
     "2022 Annual Technology Baseline (ATB) Cost and Performance Data for Transportation Technologies: vehicles.csv",
     "National Renewable Energy Laboratory (NREL)", "2022", "2026-11-22",
     "downloads/GEN/NREL_ATB_2022_transportation_vehicles.csv", "scenario Mid; column vehicle_cost(2020$)",
     "Price path after the base year (year multipliers and Costa Rica year ratios) and the powertrain ratio for "
     "classes with no statistic in any country. Not a base price.", "technology_cost_projection"],
    ["HS-001", "https://www.wcoomd.org/-/media/wco/public/global/pdf/topics/nomenclature/instruments-and-tools/hs-nomenclature-2017/2017/1787_2017e.pdf?la=en",
     "Harmonized System Nomenclature 2017 edition, Chapter 87", "World Customs Organization", "2017", RET,
     "downloads/hs/WCO_HS2017_ch87_1787_2017e.pdf", "headings 87.02, 87.03, 87.04, 87.11",
     "Tariff lines of vehicle_class_map.csv.", "nomenclature"],
    ["HS-002", "https://www.wcoomd.org/-/media/wco/public/global/pdf/topics/nomenclature/instruments-and-tools/hs-nomenclature-2022/2022/1787_2022e.pdf?la=en",
     "Harmonized System Nomenclature 2022 edition, Chapter 87", "World Customs Organization", "2022", RET,
     "downloads/hs/WCO_HS2022_ch87_1787_2022e.pdf", "headings 87.02, 87.03, 87.04 (new lines 8704.41 to 8704.60), 87.11",
     "Tariff lines of vehicle_class_map.csv.", "nomenclature"],
]


def comtrade(cc):
    return [f"COMTRADE-{cc}", CT.format(rc=RC[cc]),
            f"UN Comtrade, annual imports of {NAME[cc]} by HS 6-digit line, reporter {NAME[cc]}, partner World, 2019 to 2023",
            f"United Nations Statistics Division, data as reported by {NAME[cc]}", "2019-2023", RET,
            "; ".join(f"downloads/comtrade/comtrade_{cc}_imports_{y}.json" for y in range(2019, 2024)),
            "fields cmdCode, period, cifvalue (or primaryValue), qty with qtyUnitCode 5 (number of items), isQtyEstimated",
            {"JAM": "Quantities reported by Jamaica for 2019 to 2021; 2022 and 2023 quantities are UN estimates and are not used.",
             "DR": "Quantities reported, but they are not vehicle counts (they add up to about 2 percent of the vehicles counted by DGA); not used.",
             }.get(cc, "Quantities are UN estimates from weight, not counts reported by the country; not used."),
            "trade_statistics_reported_by_country"]


NATIONAL = {
    "DR": [
        ["DR-DGA-2020", "https://www.aduanas.gob.do/media/d1gin11o/vehiculos-diciembre-2020.pdf",
         "Vehiculos, enero a diciembre 2020 vs 2019 (Boletines de Vehiculos)", "Direccion General de Aduanas (DGA), Republica Dominicana",
         "2021-01", RET, "downloads/DR/DGA_boletin_vehiculos_2020-12.pdf",
         "p. 1, tables Importaciones de vehiculos por tipo de vehiculo: cantidad de vehiculos; valor FOB en millones de US$",
         "Units and FOB by vehicle type, 2019 and 2020; new and used together; preliminary data.", "customs"],
        ["DR-DGA-2024", "https://www.aduanas.gob.do/media/yrepbn0i/informe-mensual-de-veh%C3%ADculos-diciembre-2024.pdf",
         "Informe mensual de importacion de vehiculos, enero a diciembre 2024", "Direccion General de Aduanas (DGA), Republica Dominicana",
         "2025-01", RET, "downloads/DR/DGA_informe_vehiculos_2024-12.pdf",
         "p. 3, tables Importacion de vehiculos segun tipo: cantidades en unidades; valor FOB en US$ millones",
         "Units and FOB by vehicle type, 2023 and 2024 (2024 is outside the averaging years); headings 8702 to 8705, despacho a consumo.",
         "customs"],
        ["DR-DGA-FOB", "https://www.aduanas.gob.do/media/rn0hkgzn/imports_tabla_dinamica_19.xlsx (and vuhjlaje/..._20, 523l4d0y/..._21, cl4ihwdt/..._22, ihlclzfp/..._23)",
         "Imports Tabla Dinamica 2019 to 2023", "Direccion General de Aduanas (DGA), Republica Dominicana", "2019-2023", RET,
         "downloads/DR/DGA_imports_tabla_dinamica_2019.xlsx; downloads/DR/DGA_imports_tabla_dinamica_2020.xlsx; downloads/DR/DGA_imports_tabla_dinamica_2021.xlsx; downloads/DR/DGA_imports_tabla_dinamica_2022.xlsx; downloads/DR/DGA_imports_tabla_dinamica_2023.xlsx",
         "sheet Data Tabla Dinamica, columns Codigo Arancelario, Valor FOB US$",
         "FOB by 8-digit line, no quantity column; searched, not used.", "customs"],
        ["DR-DGA-ARANCEL", "https://www.aduanas.gob.do/consultas/arancel-de-aduanas-7ma-enmienda-2022/",
         "Arancel de Aduanas de la Republica Dominicana, 7ma enmienda 2022", "Direccion General de Aduanas (DGA)", "2022", RET,
         "downloads/DR/DGA_arancel_de_aduanas_2022_7ma_enmienda.pdf", "PDF pages 557 to 566",
         "National lines at 8 digits; no new and used split.", "nomenclature"],
    ],
    "GUA": [
        ["GUA-BANGUAT-KF103", "https://banguat.gob.gt/sites/default/files/banguat/estaeco/ceie/hist/pdfs/<year>/CG/KF-103_<year>.xlsx",
         "Importaciones realizadas por partida, Comercio General, 2019 to 2023 (valor en US dolares y volumen en kilos)",
         "Banco de Guatemala (classification of SAT)", "2019-2023", RET,
         "; ".join(f"downloads/GUA/GUA_Banguat_KF103_imports_by_inciso_CG_{y}.xlsx" for y in range(2019, 2024)),
         "annual total columns Valor and Volumen by 10-digit SAC line", "CIF in US$ and weight in kg, no unit counts; searched, not used.",
         "customs"],
        ["GUA-BANGUAT-SAC", "https://banguat.gob.gt/sites/default/files/banguat/estaeco/ceie/SAC_ENMIENDA_7.xlsx",
         "SAC VII Enmienda, enero 2022", "Banco de Guatemala", "2022", RET,
         "downloads/GUA/GUA_Banguat_SAC_Enmienda7_tariff_nomenclature.xlsx", "sheet SAC VII ENMIENDA VERS 1",
         "National tariff lines; no new and used split.", "nomenclature"],
    ],
    "CR": [
        ["CR-PROCOMER-ODATA", "https://datos.vuce.cr/OpenData/EstadisticasOData.svc/od_import?$filter=startswith(partida,'8703') eq true and id_tiempo ge 253 and id_tiempo le 312 (and 8702, 8704, 8711)",
         "Datos abiertos de comercio exterior, od_import", "PROCOMER / VUCE, Costa Rica", "2019-2023 (preliminary)", RET,
         "downloads/CR/CR_PROCOMER_odata_imports_8702_8703_8704_8711_2019_2023.xlsx", "sheet by_line_year_regime",
         "CIF in US$ and weight in kg by 12-digit inciso, no unit counts; searched, not used.", "customs"],
        ["CR-TICA-ARANCEL", "https://ticaconsultas.hacienda.go.cr/Tica/hdbaranc.aspx",
         "TICA Consulta de Aranceles, headings 8702 to 8711", "Ministerio de Hacienda, Direccion General de Aduanas", "2019-2026", RET,
         "downloads/CR/CR_TICA_arancel_8702_8703_8704_8711.csv", "query results collected page by page in a browser",
         "12-digit lines with the new and used split by model age.", "nomenclature"],
    ],
    "JAM": [
        ["JAM-JCA-TARIFF", "https://jca.gov.jm/wp-content/uploads/2026/11/INTEGRATED-TARIFF-BASED-ON-HS-2022-October-30-2026.pdf",
         "Integrated Tariff based on HS 2022, October 30, 2026", "Jamaica Customs Agency", "2026-10-30", RET,
         "downloads/JAM/JCA_integrated_tariff_HS2022_2026-10-30.pdf", "pp. 316 to 350",
         "10-digit lines; statistical units kg and u.", "nomenclature"],
        ["JAM-JCA-MVLIST", "https://jca.gov.jm/wp-content/uploads/2020/07/MVIMPORTSwtihHS-CodesforINDIVIDUALandDEALERS.pdf",
         "Revised tariff (HS codes) classification for individuals / dealers", "Jamaica Customs Agency", "2020-07", RET,
         "downloads/JAM/JCA_MV_imports_HS_codes_list_individuals_dealers_2020.pdf", "pp. 1 to 9",
         "10-digit lines of the HS 2017 period.", "nomenclature"],
    ],
    "HON": [],
}


def manual_source(cc):
    """Row for files saved by hand under downloads/manual/<CC>/ (see manual_downloads.csv)."""
    import glob
    files = sorted(glob.glob(os.path.join(JOB, "downloads", "manual", cc, "*")))
    rel = "; ".join(os.path.relpath(f, JOB).replace("\\", "/") for f in files)
    with open(os.path.join(JOB, "manual_downloads.csv"), newline="", encoding="utf-8") as f:
        m = [r for r in csv.DictReader(f) if r["country"] == cc]
    url = m[0]["url"] if m else ""
    return [f"{cc}-MANUAL", url, f"Import statistics of {NAME[cc]} by tariff line with units, saved by hand",
            "national customs or statistics office (see manual_downloads.csv)", "2019-2023", "", rel,
            "table with tariff code, units and value columns", "Read by national_parsers.manual_records.", "customs"]


def main():
    catalog = {r[0]: r for r in COMMON}
    for cc in CCS:
        catalog[f"COMTRADE-{cc}"] = comtrade(cc)
        catalog[f"{cc}-MANUAL"] = manual_source(cc)
        for r in NATIONAL[cc]:
            catalog[r[0]] = r
    for cc in CCS:
        cited = set()
        with open(os.path.join(JOB, cc, f"proposals_{cc}.csv"), newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["tech"] == "TRNPASRAIELE":
                    continue
                cited |= {s for s in r["source_ids"].split(";") if s}
        ids = sorted(cited) + [i for i in ["GEN-001", "WDI-001", "GEN-101", "HS-001", "HS-002", f"COMTRADE-{cc}"]
                               if i not in cited] + [r[0] for r in NATIONAL[cc] if r[0] not in cited]
        with open(os.path.join(JOB, cc, f"sources_{cc}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(COLS)
            for i in dict.fromkeys(ids):
                w.writerow(catalog[i])
        print(cc, len(dict.fromkeys(ids)), "sources; cited:", sorted(cited))


if __name__ == "__main__":
    main()
