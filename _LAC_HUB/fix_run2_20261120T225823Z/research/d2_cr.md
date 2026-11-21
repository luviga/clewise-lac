# d2_cr: Costa Rica capacity, commissioning and generation 2020-2024; Guatemala natural gas

All files are under `downloads/d2_cr/` or `downloads/d2_gua/` of this job unless noted; URLs and SHA-256 are in `research/d2_cr_sources.csv`. The 63 files of the stopped attempt were reused; URLs of the CENCE reports, the ARESEP JSON and the AMM GM/INFEST files were confirmed today by downloading them again to a temp folder and comparing SHA-256 (all identical). No new file was added to the topic folder.

Abbreviations: CENCE20 = `CENCE_Boletin_Anual_2020.pdf`; CENCE21..CENCE25 = `CENCE_Informe_Anual_2021.pdf` .. `_2025.pdf`; PEG = ICE Plan de Expansion de la Generacion 2024-2040 (earlier job id R1F-09, `../fix_run_20261111T200825Z/downloads/r1/CR_ICE_PEG_2024-2040.pdf`). In the CENCE reports the PDF page equals the printed page.

## (a) Installed capacity on the national system (SEN), plate kW as printed, end of year

Source: table "Capacidad Instalada en placa" CENCE20 p.27 (2020), CENCE21 p.29, CENCE22 p.29, CENCE23 p.27, CENCE24 p.25; the "Resumen" block (kW by source) and the plant rows. Diesel/bunker split by plant from PEG Tabla 10.1 p.132 column "Tipo de combustible" (Moin 2 and Moin 3: Diesel; Guapiles, Orotina, Garabito: Bunker).

| Source (Resumen) | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| Hidroelectrico | 2 331 292 | 2 330 889 | 2 330 553 | 2 371 920 | 2 352 970 |
| Termoelectrico | 474 112 | 425 962 | 380 962 | 380 962 | 520 962 |
| Geotermico | 261 860 | 258 840 | 262 660 | 262 660 | 262 660 |
| Bagazo | 71 000 | 71 000 | 71 000 | 71 000 | 71 000 |
| Eolico | 393 515 | 390 215 | 390 215 | 407 615 | 402 335 |
| Solar | 5 400 | 5 400 | 5 400 | 5 400 | 15 487 |
| Total | 3 537 178 | 3 482 305 | 3 440 789 | 3 499 556 | 3 625 414 |

Thermal by plant (plate kW, ICE TERMICO rows): Moin Gas 156 450 (4 units, 2020), 108 300 (3 units, 2021-2024); Moin Gas C.N.F.L. 90 000 (2020-2021), 45 000 (2022-2024); Guapiles 14 267; Orotina 10 686; Garabito 202 708 (11 units, footnote: plan with 10 units) all years; PTA Moin 105 000 (3 units) and PTA Garabito 35 000 (1 unit) in 2024 only (CENCE24 p.25; Subtotal Termico 520 962 = 380 962 + 140 000).
- Diesel (Moin Gas + Moin CNFL + PTA): 246 450 (2020), 198 300 (2021), 153 300 (2022), 153 300 (2023), 293 300 (2024, of which 140 000 rented PTA). PTA fuel: see (b).
- Bunker (Guapiles + Orotina + Garabito): 227 661 every year 2020-2024.
- Bagasse: El Viejo 32 500 + Taboga 38 500 = 71 000 plate (contract 37 800) every year. No other biomass rows; "Biogas" row is empty.
- Solar: Miravalles 1 000 + Juanilama 4 400 (2020-2023); 2024 adds P.S. Huacas 5 100 and P.S. Valle Escondido 4 987.
- Hydro reservoir vs run-of-river: CENCE does not split. PEG Tabla 10.1 (p.131, effective MW at Dec 2023, total hydro 2 335.0) with the reservoir list in PEG p.230 note 2 ("plantas con embalse": Angostura, Arenal-Dengo, Cachi, Cariblanco, Garita, Rio Macho, General, Penas Blancas, Pirris, Reventazon, Ventanas Garita, Sandillal, Toro I, Toro II, Brasil, Balsa Inferior, Cote, Pocosol-Agua Zarcas, Los Negros II, Chucas). Sum of those plants in Tabla 10.1 = 180+166+174+159+82+40.4+140+39+36.2+140+292+100+31+25.4+66+24+37.5+7+26+15+28+50 = 1 858.5 MW reservoir; run-of-river = 2 335.0 - 1 858.5 = 476.5 MW (Dec 2023, effective). Reservoir plants did not change 2020-2024 (the ICE plant list is identical in all five tables; La Joya and General only moved from BOT to ICE in 2023), so all hydro changes below are run-of-river.
- PEG Tabla 10.1 effective MW at Dec 2023 (p.131-132), for comparison with residuals: geothermal 222.5, wind 392.8, solar 5.4, thermal 353.1 (Moin 2 65.3 + Moin 3 70.0 diesel = 135.3; Guapiles 13.6 + Orotina 9.5 + Garabito 194.7 bunker = 217.8), biomass 38.0. Note (7): "Considera el retiro de 65 MW desde octubre 2022".

Model residuals against these: PWRDSL 0.1533 = 153.3 MW plate 2022-2023 (end 2021 was 198.3, end 2020 246.45). PWRFOI 0.214 is near PEG effective bunker 217.8 (plate 227.661). PWRGEO 0.229 is near PEG effective 222.5 (plate 258.84-262.66). PWRWNONS 0.3761 is 4 percent below PEG effective 392.8 and below plate 390.2. PWRSPVTRN 0.0054 = 5.4 MW plate. PWRBMS 0.071 = 71.0 MW bagasse plate. PWRHYDROR: 476.5 MW effective (PEG split above). PWRSUG: bagasse is already in PWRBMS; no further sugar-cane capacity exists in any table.
BAU history caps are far above the sourced values: PWRGEO 455-516 vs 258.8-262.7 MW; PWRDSL 380.5 vs 198.3/153.3/153.3 and 511.9 vs 293.3 (2024); PWRFOI 391-577 vs 227.7; PWRSPVTRN 10.7 vs 5.4 (2021-2023) and 31.1 vs 15.5 (2024); PWRWNONS 748-806 vs 390-408.

## (b) Commissioning and retirements 2021-2024 (footnotes of the same tables)

- 2021 (CENCE21 p.29 notes 6-10): Tejona wind units out 1 Jan, 1 Feb and 1 Sep 2021 (16 500 -> 13 200 kW); Pailas II plate updated Jan 2021 (55 000 -> 51 980, a rating change); one Moin Gas unit out 15 Sep 2021 (156 450 -> 108 300); Rio Segundo II contract ended 30 May 2021 (1 074 kW); Platanar contract ended 7 Aug 2021 (15 840 kW). PEG p.20 (printed 3) speaks of "la capacidad termica retirada en el ano 2021".
- 2022 (CENCE22 p.29 notes 7-10): Santa Rufina out 7 May 2022 (336 kW); Pailas II updated 3 Jun 2022 to 55 800; Moin CNFL unit 10 out from Oct 2022 (90 000 -> 45 000). No addition.
- 2023 (CENCE23 p.27 notes 5-12): El Angel out 9 Jan 2023 (3 424); El Embalse and Tapezco contracts ended 31 Jan 2023; Platanar back in operation under Coopelesca 25 Jan 2023 (2 units, 15 840 kW); Don Pedro (14 000) and Volcan (17 000) back from 15 Apr 2023; La Joya and General passed from BOT to ICE (no capacity change); PE Tilaran commercial operation 25 Nov 2023 (55 units, 17 400 kW plate, 19 800 kW contract).
- 2024 (CENCE24 p.25 notes 13-18): Tejona 5 units removed Jan 2024 and 3 more 1 Mar 2024 (13 200 -> 7 920); PTA Moin block 1 on 2 Mar, block 3 on 3 Apr, block 2 on 15 Apr 2024 (105 000 kW); PTA Garabito block 3 on 22 Mar 2024 (35 000 kW); P.S. Huacas from 22 Mar 2024 (5 100 kW); Dona Julia contract ended 30 Jun 2024 (16 470); distributor capacities updated from 1 Aug 2024. Valle Escondido solar (4 987 kW) has no footnote; its generation column on CENCE24 p.20 is empty January-July and non-zero August-December 2024 (1 531.338 MWh). PEG Tabla 14.3 p.216 (printed 199): "Termico Alquiler" 140 MW available in 2024, 105 in 2025. CENCE25 p.31 note 14: PTA Moin block 1 (35 MW) left on 24 Jan 2025.
- PTA fuel: no CENCE or PEG page names the fuel of the rented blocks. ARESEP open data 2024 (`ARESEP_od_GeneracionFuentePlantaYCapacidadInstalada_2024.json`) has a second GARABITO record with energiaPunta+Valle+Noche = 6 525.924 MWh (March) and 20 624.585 MWh (April), comsumoDiesel 1 787 481 and 5 635 081.26 l and consumoBunAZ 0; CENCE24 p.20 gives PTA Garabito 6 527.982 (March) and 20 615.720 MWh (April). A second MOIN GAS III record gives 21 697.749 MWh in March (diesel 5 844 304 l, no bunker) against PTA Moin 21 654.548 MWh. I read this match as: both PTA blocks burnt diesel in 2024 (inference from matching monthly energy, not a printed statement). Garabito, Guapiles and Orotina records burn mainly "consumoBunAZ" (bunker); Moin records burn diesel.
- Geothermal: no plant commissioned 2020-2024 (plant list unchanged; only Pailas II rating updates). PEG p.22 (printed 5): "PG Borinquen 1 (55 MW), cuya entrada en operacion esta prevista para finales del ano 2029".

Check of the base-solve builds (rule: within 5 percent or 2 MW):

| Model build | Sourced event | Verdict |
|---|---|---|
| PWRDSL 104 MW 2022 | none; -45 MW Moin CNFL Oct 2022 | no match |
| PWRDSL 104 MW 2024 | PTA Moin 105 MW, 2 Mar-15 Apr 2024 | match (1 MW) |
| PWRFOI 76 MW 2024 | no bunker addition; PTA Garabito 35 MW burns diesel (ARESEP) | no match; at most 35 MW, as diesel |
| PWRGEO 63 / 31 / 31 MW | none; Borinquen 1 end 2029 | no match |
| PWRHYDROR 105 / 0 / 0 MW | re-entries 2023: 15.84 + 14 + 17 = 46.84 MW; net hydro end 2020 to end 2024 +21.678 MW | BAU no match |
| PWRSPVTRN 13 / 10 / 10 MW | Huacas 5.1 + Valle Escondido 4.987 = 10.087 MW (2024) | NDC/LTS match; BAU off by 2.9 MW |
| PWRSUG 0 / 1 241 / 1 792 MW | bagasse 71 MW constant, no addition | no match (NDC/LTS) |
| PWRWNONS 86 / 29 / 29 MW | PE Tilaran 17.4 MW plate (19.8 contract) 25 Nov 2023; Tejona -3.3 (2021), -5.28 (2024) | no match |

## (c) Generation by source 2021-2024 (MWh as printed, "Por Fuente" block, TOTAL column)

CENCE21 p.23, CENCE22 p.24, CENCE23 p.22, CENCE24 p.20.

| Source | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| Hidroelectrico | 9 285 714,150 | 9 448 708,650 | 8,327,023.480 | 8.412.329,098 |
| Termoelectrico | 2 859,657 | 92 115,313 | 608,066.716 | 1.331.030,468 |
| Geotermico | 1 601 729,159 | 1 618 690,966 | 1,479,251.635 | 1.498.096,484 |
| Bagazo | 67 313,763 | 55 514,517 | 55,178.289 | 59.906,097 |
| Eolico | 1 573 299,593 | 1 369 231,791 | 1,461,247.724 | 1.239.469,177 |
| Solar | 9 163,733 | 8 035,651 | 8,950.990 | 25.836,160 |

Thermal by plant (MWh, TOTAL of each plant column/row on the same pages; sums equal the Termoelectrico total):
- 2021: Moin Gas 589,179; Moin Gas CNFL 184,521; Guapiles 47,221; Orotina 83,012; Garabito 1 955,724. Diesel 773.700, bunker 2 085.957.
- 2022: Moin Gas 652,769; Moin CNFL 242,314; Guapiles 2 891,790; Orotina 2 516,406; Garabito 85 812,035. Diesel 895.083, bunker 91 220.231.
- 2023: Moin Gas 71,067.317; Moin CNFL 26,005.167; Guapiles 18,777.655; Orotina 17,184.264; Garabito 475,032.313. Diesel 97 072.484, bunker 510 994.232.
- 2024: Moin Gas 213.403,357; Moin CNFL 81.075,702; PTA Moin 147.031,037; PTA Garabito 52.560,939; Guapiles 15.953,315; Orotina 35.273,444; Garabito 785.732,674. Diesel incl. PTA 494 071.035, bunker 836 959.433.
- 2024 solar plants: Juanilama 7.494,629; Huacas 7.757,214; Valle Escondido 1.531,338 (CENCE24 p.20).
Implied bagasse capacity factor: 67 313.763 MWh / (71 MW x 8 760 h) = 10.8 percent (2021); it does not support any PWRSUG build.

Not found: plant-level split of distributor hydro into reservoir and run-of-river in CENCE (used PEG instead, one year only, effective MW). Distributed (net-metering) generation is outside these SEN tables; ARESEP dataset `EnergiaGeneradaRetiradaInyectadaTipoFuente` is in the folder but its capacity field has no stated unit and December 2023 is missing, so I did not use it.

## (d) Guatemala natural gas (AMM files in downloads/d2_gua)

- Plants: ACTUN CAN GAS GENERACION, 1 unit, plate 4.0 MW, effective 2.586 MW, "9 de agosto de 2020", Santa Elena/San Benito, Peten, combustible "Gas Natural" (`AMM_Capacidad_Instalada_2020.xls` sheet Hoja 1 row 146; group row 145 TURBINAS DE GAS NATURAL 2.8 plate / 2.586 effective; same plant 2.586 MW in 2021-2025 files, e.g. 2024 sheet Resumen row 130). OCULTUN, 12 units, 12.517 MW effective, "16 de junio de 2024", La Libertad, Peten, "Gas Natural", under MOTORES DE COMBUSTION INTERNA (2024 Resumen row 144; 12.921 MW in the 2025 file row 144). No gas plant in the 2018 and 2019 capacity files. AMM Informe Estadistico 2021 p.37: TURBINAS DE GAS NATURAL 2.59 MW effective.
- Natural gas generation (GWh, sheet Energia, column O TOTAL): 2018 none (no gas row); 2019 0.008078 (GM2019 row 180, July only); 2020 5.698151 (GM2020 row 183); 2021 13.897525 (GM2021 O179; INFEST 2021 p.9 "GAS NATURAL 13.90"); 2022 9.239463 (GM2022 O181); 2023 0 (GM2023 O184); 2024 74.297096 (GM2024 O214 = OCULTUN 70.540678 O191 + ACTUN CAN 3.756418 O193; Ocultun output starts February 2024).
- PPNGS 0.7 MW built in 2021: there was no gas commissioning in 2021. Actun Can (2.586 MW effective) operated from 9 Aug 2020; 2021 output 13.897525 GWh / 8 760 h = 1.59 MW average. The cause is a missing residual capacity of about 0.0026 GW from 2020 (plus 0.0125 GW Ocultun from mid-2024), not a new build.

## Unreachable

- AMM capacity workbooks (`AMM_Capacidad_Instalada_*.xls`): the stopped attempt did not record their URL. Tried: https://www.amm.org.gt/pdfs2/capacidad_instalada/Capacidad_Instalada_2024.xls (404), .../pdfs2/pub_capacidad_instalada/Capacidad_Instalada_2024.xls (404), .../pdfs2/capacidad_instalada/2024.xls (404), .../pdfs2/capacidad_instalada/CAPACIDAD_INSTALADA_2024.xls (404), .../pdfs2/pub_capacidad_instalada/2024.xls (404), Wayback https://web.archive.org/web/2026/https://www.amm.org.gt/pdfs2/capacidad_instalada/Capacidad_Instalada_2024.xls (404), AMM portal pages page_id 145, 155, 1995, 2617 (no file links, list is loaded by script), two web searches. The files are cited by SHA-256 only; Actun Can's 2.59 MW is confirmed in AMM INFEST 2021 p.37 (URL verified).
- CENCE Boletin 2018, 2019 and Informe 2017 URLs were not recovered (not needed for 2020-2024; not cited). The CENCE "anteriores" listing (https://apps.grupoice.com/CenceWeb/CenceDescargaArchivos.jsf?init=true&categoria=3&codigoTipoArchivo=3008&fecha_inic=ante) lists only 2021-2025.
- ARESEP search for the API name returned nothing; the endpoint was read from https://aresep.go.cr/datos-abiertos/generacion-fuente-planta-capacidad-instalada/ and the 2024 file was matched by SHA-256.
