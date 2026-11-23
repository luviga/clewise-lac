"""Write sources_ECU.csv, search_log_ECU.csv and manual_downloads_ECU.csv."""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CC_DIR = os.path.dirname(HERE)
D = "2026-11-22"

sources = [
    ["ECU-001", "https://rimisp.org/wp-content/files_mf/1373468576DocEcuador9julio.pdf",
     "Consultoria sobre productividad del sector agropecuario ecuatoriano con enfasis en banano, cacao, arroz y maiz duro (Castillo Velez, M. J.)",
     "Rimisp, Centro Latinoamericano para el Desarrollo Rural (project Conocimiento y Cambio en Pobreza Rural y Desarrollo, FIDA and IDRC)",
     "2013", D, "downloads/ECU/Rimisp_DocEcuador_productividad.pdf",
     "Tabla 3.5 Analisis Costo de Factores Domesticos basado en 1 hectarea de produccion de arroz, MAGAP column, PDF p. 30 (printed p. 27)",
     "MAGAP budget for technified rice, 2012 costs (source note under the table): non-tradables 961.01 US$ (labour 377.50, water 40.00, land 210.00, capital 56.01, machinery non-tradable 277.50), tradables 560.29 US$ (agrochemicals 315.29, seed 60.00, machinery tradable 185.00), yield 75 sacks of 205 lb per ha."],
    ["ECU-002", "https://polodelconocimiento.com/ojs/index.php/es/article/view/5170/html",
     "Analisis de la cadena agroalimentaria del maiz en Ecuador (Ibarra Velasquez, Ramirez Flores, Molina Villamar, Zuniga Moreno), Polo del Conocimiento 8(1), pp. 1862-1873",
     "Polo del Conocimiento (journal)", "2023-01", D, "downloads/ECU/PoloConocimiento_5170_cadena_maiz_Ecuador.html",
     "Abstract and section Costos de produccion de maiz duro amarillo, Figura 3 (source: MAG, balance oferta demanda de maiz amarillo duro, ciclo noviembre 2021 a marzo 2022)",
     "MAG cost of hard yellow maize, summer 2022: variable cost 1,458.06 US$, fixed cost 304.02 US$, total 1,762.08 US$ per ha, 127 quintals per ha (wet and dirty), 13.91 US$ per quintal."],
    ["ECU-003", "https://rimisp.org/wp-content/files_mf/1437665697GanaderiaCarne_DocResultados_Final_editado.pdf",
     "Analisis de la Productividad y Competitividad de la Ganaderia de Carne en el Litoral Ecuatoriano (Castillo, M. J.), Serie Documentos de Trabajo N 144",
     "Rimisp, Centro Latinoamericano para el Desarrollo Rural", "2015-02", D, "downloads/ECU/Rimisp_GanaderiaCarne_DocResultados.pdf",
     "Tabla 23 Costos promedio por tipo de actividad and Tabla 24 Costos promedio por tipo de recurso, PDF p. 48 (printed p. 45 to 46)",
     "Focal groups of beef cattle producers in Balzar, Chone and Vinces, 2014: cost per head 159.4, 157.4, 285.5 US$; per ha 143.5, 159.4, 555.0 US$; 0.97, 1.05 and 2.03 head per ha. Land rent and herd value excluded."],
    ["ECU-004", "https://sipa.agricultura.gob.ec/boletines/situacionales/2023/boletin_situacional_palmito_2023.pdf",
     "Boletin situacional: palmito 2023",
     "Ministerio de Agricultura y Ganaderia (MAG), Coordinacion General de Informacion Nacional Agropecuaria, SIPA",
     "2023 (bulletin year)", D, "downloads/ECU/boletin_situacional_palmito_2023.pdf",
     "Precios de palmito a nivel de productor (USD/kilogramo, MAG CGINA 2023, chart labels 0.28 to 0.35, 0.33 in late 2023); Principales provincias productoras table and Rendimiento chart (national 5.57 t per ha 2023, INEC ESPAC)",
     "National weighted producer price of palm hearts about 0.33 US$ per kg in 2023; yield 6.68, 6.81, 6.55, 6.06, 5.57 t per ha for 2019 to 2023."],
]
with open(os.path.join(CC_DIR, "sources_ECU.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["id", "url", "title", "publisher", "date", "retrieval_date", "downloaded_file", "page_or_table", "notes"])
    w.writerows(sources)

log = [
    ["model structure", "ECU_AGR compiled BAU parameters and BAU results (read-only)", "B1_Output_Params/BAU OutputActivityRatio, InputActivityRatio, SpecifiedAnnualDemand; ECUOutput.csv", D,
     "Crops and livestock use land (E2_CRO, E2_PAS) at ratio 1: activity in Mha. Crop outputs in Mt (yields 0.17 to 77.7 t per ha); livestock outputs in million head (cattle 1.638 head per ha; sheep, goats, pigs, poultry 0.0107). Imports output E3_* at ratio 1: Mt for crops, million head for animals. In BAU 2021 the import techs supply the whole herd demand of poultry, pigs, sheep, goats, camelids, horses, mules and dairy cattle."],
    ["AG_* cost budgets", "MAG SIPA cost-of-production page", "https://sipa.agricultura.gob.ec/index.php/costos-de-produccion", D, "404 Categoria no encontrada. No cost section on the SIPA menu (home page and estadisticas economicas list prices, credit, trade; no cost files)."],
    ["AG_* cost budgets", "MAG SIPA crop situation bulletins 2021 to 2024 (arroz, maiz duro, cafe, cana de azucar, palmito, frejol, papa, soya)", "https://sipa.agricultura.gob.ec/boletines/situacionales/<year>/boletin_situacional_<crop>_<year>.pdf", D,
     "28 bulletins downloaded and searched for costo: no cost-of-production tables. The palmito 2023 bulletin gives producer price and yield (ECU-004, used for AG_PAL); the others were deleted."],
    ["AG_ARR, AG_MAI cost budgets", "Web search: MAG costos de produccion arroz maiz por hectarea", "sipa.agricultura.gob.ec costos de produccion arroz maiz por hectarea MAG Ecuador", D, "Leads: Rimisp productivity consultancy (2013) with a MAGAP rice budget; university theses (not used, case studies)."],
    ["AG_MAI cost budget", "Web search: MAG precio minimo de sustentacion costo de produccion", "MAG Ecuador costo de produccion por hectarea arroz maiz duro precio minimo de sustentacion acuerdo ministerial", D, "Found Polo del Conocimiento article quoting the MAG 2022 hard-maize budget (ECU-002). Press items (El Universo, Primicias) give 2,092 to 2,400 US$ per ha for 2025 (not used, press)."],
    ["AG_ARR cost budget", "Rimisp consultancy PDF", "https://rimisp.org/wp-content/files_mf/1373468576DocEcuador9julio.pdf", D, "Downloaded (ECU-001). Tabla 3.5 MAGAP rice budget used; Tabla 6.6 maize focal groups (Ventanas 1,598, Pajan 1,303 US$ per ha, 2013) kept as comparison only."],
    ["AG_MAI cost budget", "Polo del Conocimiento article 5170", "https://polodelconocimiento.com/ojs/index.php/es/article/view/5170/html", D, "Downloaded HTML full text (ECU-002); values confirmed in abstract and section text."],
    ["AG_ARR cost budget", "Web search: rice cost variable and fixed", "costo de produccion arroz por hectarea Ecuador MAG costo variable costo fijo 2022", D, "Only theses and Panama or Colombia budgets; no MAG document. Not used."],
    ["AG_TUB cost budget", "Web search: potato cost per ha", "costos de produccion papa por hectarea Ecuador Chimborazo dolares estudio", D, "Dialnet 9417977 download returned nothing (empty file); Tungurahua study (2,328 to 2,704 US$ per ha) only in a search snippet, not downloaded. Not used."],
    ["GA_BOV, GA_BOVLEC cost", "Web search: cattle cost per ha or head", "costo de produccion ganaderia bovina Ecuador por hectarea o por cabeza dolares leche carne", D, "Rimisp beef working paper 144 downloaded (ECU-003). Dairy cost studies are case studies per litre; not used."],
    ["AG_COF capital cost", "Web search: coffee establishment cost", "Ecuador cafe costo de establecimiento y mantenimiento por hectarea dolares MAG reactivacion cafetalera", D, "No Ecuadorian cost per ha; Costa Rica MAG model only. Not used."],
    ["AG_SUG cost", "Web search: sugarcane cost per ha", "Ecuador cana de azucar costo de produccion por hectarea dolares ingenio estudio", D, "No national cost budget; cane price 35.05 US$ per t (press). Not used."],
    ["AG_PAL cost", "Web search: palm heart cost per ha", "palmito Ecuador costo de produccion por hectarea dolares establecimiento mantenimiento", D, "University feasibility studies only (about 3,080 US$ per ha investment for a 40 ha project). Used as range for the capital assumption only."],
    ["BLEND_NO_DCOLL", "Web search: Ecuador municipal waste collection cost per t", "Ecuador costo recoleccion residuos solidos dolares por tonelada municipio estudio", D, "DATEH 2026 article on GAD spending efficiency (INEC data) downloaded: cost per t only in box plots, no number; deleted. INEC GAD waste statistics not opened. GEN CEPAL value used."],
    ["IMP* VariableCost", "GEN FAOSTAT trade unit values", "GEN/faostat_trade_unit_values.csv (GEN-201)", D, "Used for IMPARR, IMPCOF, IMPMAI, IMPLEG, IMPCER, IMPTUB, IMPFRT, IMPVEG, IMPPAL, IMPBOV, IMPPOR, IMPAVE, IMPCAB and (as sugar) IMPSUG. No imports of live sheep, goats, mules or camelids; soya bean imports tiny (seed)."],
]
with open(os.path.join(CC_DIR, "search_log_ECU.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["row", "lead", "url_or_query", "date", "result"])
    w.writerows(log)

with open(os.path.join(CC_DIR, "manual_downloads_ECU.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["url", "title", "what_it_would_source", "proposal_rows_waiting"])
print("meta written")
