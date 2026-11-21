# d7b_trans_om: annual fixed O&M of transmission as a share of capital cost

Retrieved 2026-11-20 (UTC). All files are in `downloads/d7b_trans_om/` unless a path of the earlier job is given. SHA-256 of every file is in `research/d7b_trans_om_sources.csv`.

## Short answer

- Level 1 does print a share. The ETED expansion plan 2021-2035 prints 0.5 percent of the total investment cost as the O&M of a new transmission project. This is the same number the Dominican model uses, so the model value has a Dominican source (an ETED planning assumption, "elaboracion propia", not a regulatory value).
- The Dominican regulation (Ley 125-01 and its Reglamento, Art. 357 to 360) prints no percentage. The SIE toll resolution SIE-121-2019-PJ prints amounts, not a share; the amounts give 0.83 percent of VNR for "Intervenciones O&M" and 2.84 percent of VNR for all exploitation costs (computed here).
- Regional and international documents print higher shares: 1.5 to 3.4 percent per year. Median of the seven external values 2.72 percent; with the ETED value, median of eight 2.575 percent, range 0.5 to 3.37 percent.

## Table of shares found

| Level | Document | Publisher | Year | Share (percent per year) as printed | Asset scope | Locator |
|---|---|---|---|---|---|---|
| 1 | Plan de Expansion de la Transmision 2021-2035 | ETED | 2020 (footers 2023) | "OYM NUEVO PROYECTO TRANSMISION 0.5 %"; footnote 35: "O.5% del costo total de inversion del proyecto en cuestion." Also "ESCALAMIENTO OYM NUEVO PROYECTO TRANSMISION 0.1 %" | "Nuevo proyecto transmision" in the economic and financial evaluation of the plan (the text below the table applies it to the proposed SVC); O&M only | `..\fix_run_20261111T200825Z\downloads\r1\DR_ETED_Plan_Expansion_Actualizado_2021-2035.pdf`, PDF p.306 = printed p.306, Tabla 102 "Supuestos en evaluacion economica-financiera", source line "Elaboracion propia del Dpto. de Analisis y Planificacion del STN [ETED]" |
| 1 | Resolucion SIE-121-2019-PJ (modifies SIE-073-2018-PJ, toll 2017-2020) | SIE | 2019-12-18 | No share printed. Printed amounts: VNR total US$ 842,678,957; "Costos de Explotacion": "Estructura" US$ 16,885,902 and "Intervenciones O&M" US$ 7,012,369 per year. Computed: 0.83 percent (O&M interventions) and 2.84 percent (all exploitation costs) of VNR | Whole ETED system (substations, lines, non-electrical assets), base December 2016 | `DR_SIE-121-2019-PJ_Modif_Peaje_Transmision_2017-2020.pdf`, PDF p.28 = "Pagina 28 de 42" (scanned; table read as image); Articulo 1 on PDF p.38 adopts the total of this table |
| 1 | Reglamento de la Ley General de Electricidad 125-01 | Dominican Government (hosted by MEM) | 2002 | No share printed | n.a. | `DR_Reglamento_Ley_125-01_MEM.pdf`, PDF p.98, Art. 357 to 360 |
| 1 | Plan Energetico Nacional 2022-2036 | CNE | 2022 | No share printed | n.a. | `..\fix_run_20261111T200825Z\downloads\r4\PEN2022-2037.pdf`, section a.3.vi, printed p.145 |
| 2 | Reglamento del Mercado Electrico Regional (RMER), version 1 January 2019 | CRIE (hosted by EOR) | 2019 | "Hasta tanto la CRIE defina los costos eficientes de administracion, operacion y mantenimiento como un porcentaje del costo estandar de cada instalacion [...] se utilizara el 3%." | Each regional transmission installation; administration, operation and maintenance (AOM) over standard cost | `EOR_RMER_010119.pdf`, PDF p.430 = printed p.421, transitory 2.1.1; rule in Libro III 9.2.3 b), PDF p.255 = printed p.246 |
| 2 | Resolucion CRIE-60-2015 (authorised income 2016 of EPR) | CRIE | 2015-12-18 | "el AOM debe ser el 2,72% del costo estandar"; "el 2,72% de un costo estandar de USD 396,040,009" | SIEPAC line of EPR; AOM over standard cost | `CRIE-60-2015_con_fe_de_erratas.pdf`, PDF p.6 and p.4. Same share in the CRIE audit of EPR 2014, `CRIE_Informe_Auditoria_Administracion_Recursos_EPR.pdf`, PDF p.43 (US$ 9,653,927 = 2.72% of US$ 396,040,000) |
| 2 | IMP de ETESA 2017-2021, Metodologia de Calculo | ASEP Panama | 2018 | "OMT%M (2.43%), AMDT%M (0.93 %) para un total de AOYM/VNR (3.36 %)". Comparators (O&M over VNR): Transelec 2013 1.83%, ISA 2014 2.58%, REP 2014 2.35% | Whole transmission company (ETESA); O&M and administration separately, over VNR | `PA_ASEP_metodologia_IMP_trans_2017-2021.pdf`, PDF p.6 = printed p.6, Cuadro 2 |
| 2 | IMP de ETESA julio 2025 a junio 2029, Metodologia de Calculo | ASEP Panama | 2025 | "Indicador ETESA": ADMT%M*(ADM/VNR) 0.82%, OMT%M*(OyM/VNR) 1.75%, AOYM/VNR 2.57%. Comparators (O&M over VNR): Transelec 2021-2023 1.17%, REP 2021-2023 2.15%, CEMIG-GT 2017 1.53% | Whole transmission company (ETESA); over VNR | `PA_ASEP_metodologia_IMP_trans_2025-2029.pdf`, PDF p.7 = "Pagina 7 de 100", Cuadros 1 and 2 |
| 2 | Reglamento de la Ley General de Electricidad, Guatemala (AG 256-97, reformed by AG 68-2007) | CNEE Guatemala (Wayback copy) | 1997, 2007 | Art. 55: "Los costos anuales de operacion, mantenimiento y administracion, que seran como maximo el 3% del costo total de la inversion mencionada en el parrafo anterior." | Transmission installations of an economically adapted system (maximum toll); O&M plus administration | `GT_Reglamento_LGE_CNEE_wayback.pdf`, PDF p.18 = printed p.35 (article starts on printed p.34); text layer is garbled, read as image |
| 3 | Resolucion OSINERGMIN 080-2021-OS/CD | OSINERGMIN Peru (El Peruano) | 2021-04-29 | "% respecto de Costo de Inversion": 138 kV and above: Costa 3,23%, Sierra 3,37%, Selva 3,47%; above 30 kV and below 138 kV: Costa 2,73%, Sierra 3,49%, Selva 3,53% (1 to 30 kV feeder bays: 4,41%, 4,82%, 4,64%) | Transmission installations by voltage and region, May 2021 to April 2027; standard annual O&M cost | `PE_ElPeruano_1947918-1.html`, Articulo 1 |
| 3 | ETRI 2014, Energy Technology Reference Indicator projections 2010-2050 | European Commission JRC | 2014 | Table 39: "FOM % CAPEX ref. 1.5" for 2013 to 2050 (and "VOM % CAPEX ref. 2") | Overhead transmission lines (500 MVA) | `JRC_ETRI_2014_JRC92496.pdf`, PDF p.64 = printed p.64 |
| 3 | National Transmission Planning Study, Chapter 2 | U.S. DOE with NREL and PNNL | 2024-10 | "Annual transmission fixed O&M costs are assumed to be 1.5% of the upfront capital costs per year" (cites the JRC report above) | All transmission in the ReEDS capacity expansion model | `DOE_NTP_Study_Chapter2.pdf`, PDF p.87 = printed p.69; also PDF p.50 = printed p.32 |

## Level 1 detail (Dominican Republic)

1. ETED plan, Tabla 102 (PDF p.306). The row is "OYM NUEVO PROYECTO TRANSMISION" with superscript 35, value 0.5, unit column "%". Footnote 35 on the same page: "O.5% del costo total de inversion del proyecto en cuestion." (printed with a capital letter O instead of zero). The words "por ano" are not printed on this row; the annual meaning follows from the next row, an escalation of the O&M of 0.1 %, and from the 30 year cash flow of the table. The table is a set of assumptions made by ETED for its own project evaluation, not a regulated value.
2. Law and regulation. Ley 125-01 Art. 85 and 87 (quoted in the ETED plan, printed p.31-32) and the Reglamento Art. 359 (PDF p.98): "Las instalaciones del Sistema de Transmision, sus valores nuevos de reemplazo, la anualidad de la inversion y los costos de operacion y mantenimiento de cada una de las instalaciones existentes y aquellas por construir dentro de periodos de cuatro (4) anos, seran definidos mediante resolucion de la SIE." Art. 360 fixes a 30 year life for the annuity. No percentage of the VNR is stated anywhere in Art. 357 to 369; all "por ciento" strings of the Reglamento were searched.
3. SIE-121-2019-PJ, table "Recalculo del Peaje de Transmision" (Pagina 28 de 42), columns VNR, Anualidad (VAT), Incidencia:
   - Electricos SSEE: VNR US$ 265,456,301; annuity 25,884,385; 24.0%
   - Electricos Lineas: VNR US$ 535,566,998; annuity 52,222,616; 48.7%
   - No Electricos: VNR US$ 41,655,658; annuity 5,472,547; 5.1%
   - Costos de Explotacion, Estructura: 16,885,902; 15.7%
   - Costos de Explotacion, Intervenciones O&M: 7,012,369; 6.5%
   - TOTAL: VNR US$ 842,678,957; 107,477,819 US$/Ano; 8,956,485 US$/Mes
   The "Incidencia" column is the share of the annual toll, not of the VNR. Computed shares of VNR (not printed): 7,012,369 / 842,678,957 = 0.832 percent; (16,885,902 + 7,012,369) / 842,678,957 = 2.836 percent. Over the electrical VNR only (801,023,299): 0.875 and 2.983 percent. Articulo 1 of the resolution sets the base toll at 107,477,819.00 US$/ano (December 2016 values), the total of this table. The study behind it is the "Calculo del Valor Agregado de Transmision" by the consultant SIGLA; the study itself was not found.
4. PEN 2022-2036 only describes the toll and prints toll income against ETED expenses (Tabla 49); no share.

## Median and range

One value per independent determination, percent of capital cost (investment, VNR or standard cost) per year:

- 0.5 (ETED plan, O&M only)
- 1.5 (JRC ETRI 2014, FOM of overhead lines; the DOE study repeats this value and is not counted again)
- 1.75 (Panama 2025-2029, O&M only)
- 2.43 (Panama 2017-2021, O&M only)
- 2.72 (CRIE, SIEPAC line, AOM; the audit repeats it and is not counted again)
- 3 (RMER default, AOM)
- 3 (Guatemala Art. 55, maximum, O&M and administration)
- 3.37 (Peru, 138 kV and above, Sierra; this is also the middle of the three regional values 3.23, 3.37, 3.47)

All eight: median (2.43 + 2.72) / 2 = 2.575 percent; range 0.5 to 3.37 percent.
Seven external values (without the Dominican one): median 2.72 percent; range 1.5 to 3.37 percent.

By scope:
- O&M without administration (0.5, 1.5, 1.75, 2.43): median 1.625 percent; range 0.5 to 2.43.
- O&M with administration (Panama 2.57 and 3.36, CRIE 2.72, RMER 3, Guatemala 3): median 3 percent; range 2.57 to 3.36. The Peruvian resolution does not say whether administration is inside its percentages.
- Company ratios printed by ASEP (O&M over VNR): Transelec 1.17 and 1.83, CEMIG-GT 1.53, REP 2.15 and 2.35, ISA 2.58.
- Dominican toll, computed from SIE-121-2019-PJ: 0.83 (O&M interventions) and 2.84 (all exploitation costs) percent of VNR.

Reading: 0.5 percent is the lowest published value found and comes from ETED itself. Every regulator value outside the Dominican Republic is three to six times higher, and the Dominican toll itself pays ETED exploitation costs equal to 2.84 percent of VNR.

## Not found

- An SIE resolution or study that states the O&M of ETED as a percentage of the VNR. The SIE resolutions SIE-080-2017, SIE-177-2018, SIE-122-2019 and SIE-082-2020 named in the PEN, the SIGLA study (2018), the Estudios Energeticos Consultores study for 2021-2024 and the 2025-2028 update were searched for by title and number (four web searches) and not found as files. The resolution list of sie.gob.do is a script-driven table that curl cannot read.
- IEA ETSAP brief E12 (2014) and the ACER unit investment cost reports of 2023 and 2026 were downloaded and searched: none prints an O&M share of transmission capital cost.
- Colombia (CREG 011 of 2009, AOM percentage per company) and Chile (COMA) were not pursued for lack of time; the search results show the CREG percentages are set per company in separate resolutions.

## Unreachable

- `https://sie.gob.do/la-superintendencia-de-electricidad-realiza-audiencia-publica-para-conocer-propuesta-de-calculo-del-valor-agregado-de-transmision/`: WebFetch HTTP 403; curl with a browser user agent returned the page, which has no document links. `https://sie.gob.do/audiencia-publica/` and `https://sie.gob.do/sobre-nosotros/marco-legal/resoluciones-sie/` load but list no files without scripts. A query of the site search interface was blocked by the session permission system.
- `https://www.cnee.gob.gt/...` (RLGE.pdf, Reglamento de la LGE.pdf, CNEE-150-2022.pdf, CRIE-34-2024.pdf, CRIE-24-2024.pdf): the site returns an HTML page "Sitio en mantenimiento" (34,057 bytes) with Git Bash curl and with curl.exe. Solved for the Reglamento with the Wayback Machine copy; the CRIE resolutions were taken from crie.org.gt instead.
- `https://mem.gob.gt/wp-content/uploads/2025/04/1.3.2-Reglamento-de-la-Ley-General-de-Electricidad-Ac.-Gub.-256-97.pdf`: Cloudflare block page.
- `https://rise.esmap.org/data/files/library/nicaragua/Energy%20Efficiency/Nicaragua_Regulation%20of%20the%20Regional%20Market.pdf` (RMER copy): HTML page of 5,924 bytes. Solved with the EOR copy.
- `https://faolex.fao.org/docs/pdf/gua60660.pdf`: downloads, but it is the Law (Decreto 93-96), not the Reglamento; deleted.
- `https://core.ac.uk/download/38629009.pdf` (JRC ETRI copy): Cloudflare challenge. `https://publications.jrc.ec.europa.eu/repository/bitstream/JRC92496/ldna26950enn.pdf` gave "Request Rejected" with a short user agent and worked with a full browser user agent.
- `https://iea-etsap.org/E-TechDS/PDF/E12_el-t&d_KV_Apr2014_GSOK.pdf` (also with www and with %26): returns the site home page (70,560 bytes). Solved with the Wayback Machine copy.
- NREL ReEDS documentation: `https://www.osti.gov/servlets/purl/3013259` curl error 56; `https://www.nrel.gov/docs/fy22osti/78224.pdf` and `https://docs.nrel.gov/...` could not resolve host; `https://docs.nlr.gov/...` and `https://www.nlr.gov/...` returned a 235 byte HTML page. The DOE National Transmission Planning Study (which uses ReEDS) was used instead.
- `https://sie.gob.do/wp-content/uploads/2025/08/SIE-097-2025-REG.pdf` and `.../2025/12/SIE-155-2025-REG.pdf` were downloaded as candidates for the 2025-2028 toll regulation; they are the national electrical code and a distribution design standard, so they were deleted.
