# d12_lives: operational life of 36 Ecuador technologies

Retrieved and read 2026-11-20 (UTC). File paths are relative to the job folder `C:\clw_fix\_LAC_HUB\fix_run2_20261120T225823Z\` unless they start with `../` (earlier job folder) or `archive` (`C:\Users\luisfernando\Desktop\OSeMOSYS\LAC_sources_archive\`). Hashes and URLs are in `research/d12_lives_sources.csv`.

## Tech names checked

All 36 names exist in `C:\clw_base_4ba69d6\Ecuador\ECU_Energy\A1_Outputs\A-O_Parametrization.xlsx`, column Tech.Name:
Secondary Techs: ELE_TRANS "Secondary - Power Transmission", ELE_DIST "Secondary - Power Distribution", HYD_G_PROD "Secondary - Green Hydrogen Production", STOELE "Secondary - Storage", PPBIM "Biomass/Residue", PPBGS "Biogas", PPDSL "Diesel", PPFOI "Fuel Oil", PPNGS "Natural Gas", PPCRU "Power Plant Crude", PPRNGS "Isolated Power Plant Refinery Natural Gas", PPRDSL "Isolated Power Plant Refinery Diesel", PPDFOI "Distributed Power Plant Fuel Oil", PPDDSL "Distributed Power Plant Diesel", PPILPG "Isolated Power Plant LPG", PPIBIM "Isolated Power Plant Biomass/Residue".
Primary Techs: PRONGS "Production - Natural_Gas", PPGEO "Geothermal", PPHDAMAB/PPHRORAB "Amazon Big (+ 450 MW)", PPHDAMAM/PPHRORAM "Amazon Medium (< 450 MW)", PPHDAMPM/PPHRORPM "Pacific Medium (< 450 MW)", PPHDAMAS/PPHDAMPS/PPHRORAS/PPHRORPS "Small (<50 MW)", PPHD "Hidroeléctrica distribuida", PPIHD "Isolated Hidroeléctrica", PPWNDON "Wind", PPWNDD "Distributed Wind", PPPVT "Transmission Solar", PPPVTS "Transmission Solar with battery storage", PPPVD "Distributed Solar", PPPVDS "Distributed Solar with battery storage".

## Selection rule used

1. Where an Ecuador document states a life for a whole plant type, that value is used: wind and PV in ARCONEL-004/24 Tabla 2 legend; the reference internal-combustion-engine (MCI) plant in the ARCERNNR 2021 cost-of-service report.
2. Otherwise the regulated useful life of ARCONEL-004/24 Anexo 1 (Tabla 2 generation, Tabla 3 transmission and distribution) for the asset group that defines the plant: civil works ("Infraestructura Civil-Obras Hidráulicas") for hydro, "Equipos e Instalaciones Electromecánicas" for steam and gas-turbine plants, lines and networks for T&D. Plant types are by conversion technology, so a biomass steam plant takes "Térmica de Vapor".
3. Classes not covered by level 1 go to the kit (level 2), then PLANMICC (level 3), then NREL ATB 2024 / IRENA (level 4).
4. ARCONEL evaluation periods (ARCONEL-005/25 Tabla 4, ARCONEL-006/24 Tabla 4) are not used as lives: ARCONEL-006/24 PDF p.56 says they "no consideran plazo de concesión ni tampoco vida útil del proyecto". They are listed for context.

## Key source wording (as printed)

- S1 ARCONEL-004/24 Codificada, `downloads/d12_lives/ARCONEL_Regulacion-Nro.-ARCONEL-00424-CODIFICADA.pdf`, PDF p.40 (printed "Página 40 de 42"), "ANEXO 1. Vidas útiles de activos en servicio empresas públicas y mixtas". Tabla 2 (años de vida útil), columns 1 Hidráulica > 50MW, 2 Hidráulica 5 - 50MW, 3 Hidráulica 0,5 - 5MW, 4 Hidráulica 0 - 0.5MW, 5 Térmica de Vapor, 6 Térmica MCI < 514rpm, 7 Térmica MCI 514 - 900 rpm, 8 Térmica MCI > 900rpm, 9 Térmica Gas Industrial, 10 Térmica Gas Tipo Jet, 11 "Eólica (25 años)", 12 "Fotovoltaica (25 años)".
  - Infraestructura Civil-Obras Hidráulicas: 50 40 33 20 (cols 1 to 4).
  - Equipos e Instalaciones Electromecánicas: 35 33 30 20 30 15 14 6 20 6 (cols 1 to 10).
  - Edificios y Estructuras: 50 40 33 20 40 30 25 12 20 12.
  - Tabla 3 (VIDA ÚTIL (años)): Líneas de Transmisión 45; Subestaciones de Transmisión 30; Líneas de Subtransmisión 45; Subestaciones de Subtransmisión 30; Alimentadores Primarios 35; Transformadores de Distribución 30; Redes Secundarias 35; Acometidas y Medidores 20.
  - Body, section 10.3 (same PDF): depreciation "con base en las vidas útiles del Anexo 1"; private companies follow their Título Habilitante.
- S2 ARCERNNR cost-of-service update 2021 (Informe INF.DRETSE.2021.035), `downloads/d12_lives/ARCERNNR_costo_servicio_2021_esmap.pdf`, PDF p.18, Cuadro Nro. 1 "Tipo de Tecnología : Motor de combustión interna - MCI": "Vida Útil (n) (Años) 25"; "Vida Útil (n) (Meses) 300"; CUI 1.254 USD/kW-instalado. Regulación ARCERNNR 001/23 (`downloads/d12_lives/ARCONEL_Regulacion-001-23-Fe-Erratas.pdf`, PDF p.59, Anexo D) defines it: "Vida útil: Es el tiempo estimado en el que la central tipo cumple correctamente con la función para la cual se ha construido."
- S3 CELEC EP financial statements 2020, `downloads/d12_lives/CELEC_EEFF_2020_esmap.pdf`, PDF p.30 to 31 (printed Página 29 and 30 de 86), "Vida útil (en años)": Obras Hidráulicas Construcciones Civiles 70; líneas de transmisión hasta 230 KV 45, hasta 500 KV 50; redes de media tensión hasta 34,5 KV 40; redes de baja tensión 40; transformadores de distribución (postes) 40; Turbo generadores hidráulicos > 50 MW 35, 5 - 50 MW 33, 0 - 5 MW 30; Turbo generadores a vapor 30; a gas 25; Motogeneradores 25; Aerogeneradores 25; Transformadores de potencia 40; Transformadores de distribución (unidades de transformación) 25.
- S4 ARCONEL-005/25, `downloads/d12_lives/ARCONEL_2.2.-Regulacion-Nro.-005-25-ERNC.pdf`, PDF p.21 Tabla 4 Plazos Preferentes (años): Solar Fotovoltaica 25, Eólica 25, Hidroeléctrica 30, Biomasa 20, Geotérmica 25, Biogás 20 ("corresponde al tiempo de evaluación del proyecto"); same values PDF p.39 "6. PERIODO DE EVALUACIÓN". Artículo 20 (PDF p.19): "El recambio del Sistema de Almacenamiento está considerado en el costo de inversión de la CGRNC". No battery life is printed.
- S5 ARCONEL-006/24, `downloads/d12_lives/ARCONEL_Regulacion-ARCONEL-006-24-1-3.pdf`, PDF p.56 Tabla 4: same six evaluation periods; distributed generation is "Potencia Nominal igual o mayor a cien (100) kW y de hasta diez (10) MW" (scope, literal a).
- S6 Ley de Hidrocarburos Art. 23, `downloads/d12_lives/Ley_Hidrocarburos_primicias.pdf`, PDF p.15 to 16: "El período de explotación de estos contratos [gas natural] podrá durar hasta veinte y cinco (25) años, prorrogables"; crude oil "hasta veinte (20) años".
- S7 PME 2023-2032, `downloads/d12_lives/PME_completo_MAE.pdf`, PDF p.203: power transformer "diseñado para lograr una vida útil de 20-35 años y una vida mínima de 25 años". No life by technology in PME 2018-2027 cap. 4 and Anexos, PME adjustment 2026 (Acuerdo and Anexos A, B, C) or the hydrogen roadmap 2023 (full text searched).

## Table 1: proposed operational life by tech

| Tech | Class | Life (yr) | Level | Source file and locator | Wording or cell as printed |
|---|---|---|---|---|---|
| ELE_TRANS | Transmission grid | 45 | 1 | S1 PDF p.40 Tabla 3 | "Líneas de Transmisión 45" (Subestaciones de Transmisión 30) |
| ELE_DIST | Distribution grid | 35 | 1 | S1 PDF p.40 Tabla 3 | "Alimentadores Primarios 35", "Redes Secundarias 35" (Transformadores de Distribución 30, Acometidas y Medidores 20) |
| HYD_G_PROD | Electrolysis | 30 | 3 | PLANMICC OperationalLife.csv #L152 (HYDPROELEGRI) and #L151; workbook Fixed Horizon Parameters row 303 | Value 30.0; workbook column Note "No information" |
| STOELE | Battery storage | 15 | 4 | ATB2024_definitions.html, table Technical Lifetimes | "Utility-scale battery storage* 15" |
| PRONGS | Gas production | 25 | 1 (proxy) | S6 Art. 23, PDF p.16 | "podrá durar hasta veinte y cinco (25) años" (contract exploitation period, not an asset life) |
| PPBGS | Biogas engine | 25 | 1 | S2 PDF p.18 Cuadro 1 | "Motor de combustión interna - MCI ... Vida Útil (n) (Años) 25" |
| PPBIM | Biomass steam | 30 | 1 | S1 PDF p.40 Tabla 2 col 5 | Térmica de Vapor, Equipos e Instalaciones Electromecánicas 30 |
| PPIBIM | Biomass steam (isolated) | 30 | 1 | as PPBIM | as PPBIM |
| PPCRU | Oil engine (crude) | 25 | 1 | S2 PDF p.18 Cuadro 1 | "Vida Útil (n) (Años) 25" |
| PPDSL | Oil engine (diesel) | 25 | 1 | S2 | as above |
| PPRDSL | Oil engine (diesel, refinery isolated) | 25 | 1 | S2 | as above |
| PPDDSL | Oil engine (diesel, distributed) | 25 | 1 | S2 | as above |
| PPFOI | Oil engine (fuel oil) | 25 | 1 | S2 | as above |
| PPDFOI | Oil engine (fuel oil, distributed) | 25 | 1 | S2 | as above |
| PPILPG | LPG engine (isolated) | 25 | 1 | S2 | as above |
| PPNGS | Gas turbine | 20 | 1 | S1 PDF p.40 Tabla 2 col 9 | Térmica Gas Industrial, Equipos e Instalaciones Electromecánicas 20 |
| PPRNGS | Gas turbine (refinery isolated) | 20 | 1 | as PPNGS | as PPNGS |
| PPGEO | Geothermal | 20 | 2 | ../fix_run_20261111T200825Z/downloads/ccg/Ecuador_Base_SAND.xlsm, Parameters!J31144 (PWRGEO); DiB Table 10 PDF p.16 | 20 |
| PPHDAMAB | Hydro >50 MW | 50 | 1 | S1 PDF p.40 Tabla 2 col 1 | Infraestructura Civil-Obras Hidráulicas 50 (electromechanical 35) |
| PPHDAMAM | Hydro >50 MW | 50 | 1 | as above | as above |
| PPHDAMPM | Hydro >50 MW | 50 | 1 | as above | as above |
| PPHRORAB | Hydro >50 MW | 50 | 1 | as above | as above |
| PPHRORAM | Hydro >50 MW | 50 | 1 | as above | as above |
| PPHRORPM | Hydro >50 MW | 50 | 1 | as above | as above |
| PPHDAMAS | Hydro 5 to 50 MW | 40 | 1 | S1 PDF p.40 Tabla 2 col 2 | Infraestructura Civil-Obras Hidráulicas 40 (electromechanical 33) |
| PPHDAMPS | Hydro 5 to 50 MW | 40 | 1 | as above | as above |
| PPHRORAS | Hydro 5 to 50 MW | 40 | 1 | as above | as above |
| PPHRORPS | Hydro 5 to 50 MW | 40 | 1 | as above | as above |
| PPHD | Hydro 0.5 to 5 MW (distributed) | 33 | 1 | S1 PDF p.40 Tabla 2 col 3 | Infraestructura Civil-Obras Hidráulicas 33 (electromechanical 30) |
| PPIHD | Hydro 0.5 to 5 MW (isolated) | 33 | 1 | as PPHD | as PPHD |
| PPWNDON | Wind | 25 | 1 | S1 PDF p.40 Tabla 2 legend | "Eólica (25 años)" |
| PPWNDD | Wind (distributed) | 25 | 1 | as above | as above |
| PPPVT | Solar PV | 25 | 1 | S1 PDF p.40 Tabla 2 legend | "Fotovoltaica (25 años)" |
| PPPVTS | Solar PV with battery | 25 | 1 | as above; battery replacement inside capital cost per S4 Art. 20 | as above |
| PPPVD | Solar PV (distributed) | 25 | 1 | as above | as above |
| PPPVDS | Solar PV with battery (distributed) | 25 | 1 | as above | as above |

Assumptions to check: "Medium (< 450 MW)" hydro is taken as 50 to 450 MW because "Small" is "<50 MW". Small hydro (<50 MW) could include units under 5 MW (column 3 gives 33). PPHD is placed in column 3 because distributed generation in S5 is 100 kW to 10 MW; PPIHD size is not stated in the workbook (column 4, 0 to 0.5 MW, would give 20). Engine-based classes assume the oil, LPG and biogas plants are internal-combustion engines; the PLANMICC tech names confirm ICE for biogas (PP_BGSICE), diesel, fuel oil and crude (PP_DSLICE, PP_FOIICE, PPICRUPETICE) but PLANMICC also has diesel gas turbines (21 yr) and fuel-oil steam (15 yr). If PPNGS or PPRNGS are engines, S2 gives 25.

## Lower-level values for context, and disagreements

| Class | Level 1 other values | Kit (level 2) | PLANMICC (level 3) | ATB 2024 / IRENA (level 4) |
|---|---|---|---|---|
| Transmission | Subestaciones 30 (S1); CELEC lines 45 (230 kV), 50 (500 kV), power transformers 40 (S3); PME transformers 20-35 (S7) | 60 | 60 (#L108) | none |
| Distribution | CELEC MV and LV networks 40, distribution transformers 25 and 40 (S3) | 60 | 60 (#L109) | IRS class 49.14 T&D 30 (cross-check only) |
| Electrolysis | roadmap: none | none | 30, "No information" | IRENA 2020 PDF p.43: alkaline "proven lifetimes of over 30 years"; stack 60 (alkaline) and 50-80 (PEM) thousand hours (PDF p.12 Table ES1) |
| Storage | none (S4 Art. 20 only) | none (PV+2h storage 30 is a hybrid) | none | ATB 15 |
| Gas production | crude oil exploitation 20 (S6) | MINNGS 1 | PRONGS 1 (#L162) | IRS class 13.2: 14 |
| Biogas | evaluation 20 (S4, S5); ARCONEL MCI electromechanical 15/14/6 (S1) | none | 20 (#L123) | none |
| Biomass | evaluation 20 (S4, S5); CELEC steam turbo generators 30 (S3) | 25 | 20 (#L126) | IRENA 20; ATB biopower 45 |
| Oil and LPG engines | S1 MCI electromechanical 15 (<514 rpm), 14 (514-900), 6 (>900 rpm); CELEC Motogeneradores 25 (S3) | LFO plant 25; 1 kW generator 20 | ICE 15, diesel GT 21, crude 40 | none |
| Natural gas | S1 gas jet 6; CELEC turbo generadores a gas 25 | CCGT 30, SCGT 30 | 30 (#L132, #L144-146) | ATB natural gas 30 |
| Geothermal | evaluation 25 (S4, S5) | 20 | 30 (#L194) | ATB 30; IRENA 25 |
| Hydro | electromechanical 35/33/30; CELEC civil works 70, turbo generators 35/33/30; evaluation 30 | 60 (>100, 10-100, <10 MW); off-grid 40 | 75 (#L171-174, #L182-193) | ATB 100; IRENA 2022 economic 30; IRENA 2025 "30 to 80 years" |
| Wind | CELEC Aerogeneradores 25; evaluation 25 | onshore 30 | 20 (#L176, #L168) | ATB 30; IRENA 25 |
| Solar PV | evaluation 25 | utility 25; PV+storage 30; distributed with storage 24 | 25 (#L180, #L181) | ATB 30; IRENA 25 |

Disagreements worth a decision:
- Hydro civil works: ARCONEL-004/24 says 50 (>50 MW); CELEC EP's own accounts say 70; kit 60; PLANMICC 75; ATB 100. Using the electromechanical life instead would give 35/33/30.
- Engines: ARCONEL-004/24 depreciation lives 15/14/6 by speed against 25 for the reference MCI plant (S2) and CELEC Motogeneradores 25.
- Gas turbines: ARCONEL-004/24 20 (industrial) and 6 (jet) against CELEC 25 and kit, PLANMICC, ATB 30.
- Geothermal: kit 20 is the lowest value; national evaluation period 25, PLANMICC and ATB 30.
- T&D: national 45 / 35 against kit and PLANMICC 60.
- PRONGS: kit and PLANMICC carry 1 year, which is not a life; 25 is a contract term proxy; the IRS tax class life is 14.

## Table 2: CCG starter kit lives for these classes

Kit file: `../fix_run_20261111T200825Z/downloads/ccg/Ecuador_Base_SAND.xlsm` (earlier job CCG-002, Zenodo record 5498094), sheet Parameters, parameter OperationalLife, value in column J, tech code in column C; names from sheet SETS. Data article Table 10 (archive `cost_src_ecu_20261110T025435Z/CCG/Allington2022_DiB_108021_PMC8943422.pdf`, PDF p.16) prints the same values for the kit power plants; it has no T&D, off-grid hydro or hybrid rows.

| Tech | Kit tech (name) | Cell | Kit value | DiB Table 10 | Proposed | Equal |
|---|---|---|---|---|---|---|
| ELE_TRANS | PWRTRN (Electricity Transmission) | J31162 | 60 | not printed | 45 | no |
| ELE_DIST | PWRDIST (Electricity Distribution) | J31163 | 60 | not printed | 35 | no |
| HYD_G_PROD | none | | | | 30 | no kit value |
| STOELE | none | | | | 15 | no kit value |
| PRONGS | MINNGS (Natural Gas Extraction) | J31134 | 1 | not printed | 25 | no |
| PPBGS | none (nearest PWRBIO001 Biomass Power Plant) | J31141 | 25 | 25 | 25 | yes vs nearest |
| PPBIM | PWRBIO001 (Biomass Power Plant) | J31141 | 25 | 25 | 30 | no |
| PPIBIM | PWRBIO001 | J31141 | 25 | 25 | 30 | no |
| PPCRU | PWROHC001 (Light Fuel Oil Power Plant) | J31145 | 25 | 25 | 25 | yes |
| PPDSL | PWROHC001 | J31145 | 25 | 25 | 25 | yes |
| PPRDSL | PWROHC001 | J31145 | 25 | 25 | 25 | yes |
| PPDDSL | PWROHC003 (Light Fuel Oil Standalone Generator (1kW)) | J31164 | 20 | 20 | 25 | no |
| PPFOI | PWROHC001 | J31145 | 25 | 25 | 25 | yes |
| PPDFOI | PWROHC001 | J31145 | 25 | 25 | 25 | yes |
| PPILPG | PWROHC001 | J31145 | 25 | 25 | 25 | yes |
| PPNGS | PWRNGS001 (CCGT) / PWRNGS002 (SCGT) | J31147 / J31148 | 30 / 30 | 30 / 30 | 20 | no |
| PPRNGS | PWRNGS002 (SCGT) | J31148 | 30 | 30 | 20 | no |
| PPGEO | PWRGEO (Geothermal Power Plant) | J31144 | 20 | 20 | 20 | yes |
| PPHDAMAB, PPHRORAB | PWRHYD001 (Large Hydropower Plant (Dam) (>100MW)) | J31152 | 60 | 60 | 50 | no |
| PPHDAMAM, PPHDAMPM, PPHRORAM, PPHRORPM | PWRHYD001 / PWRHYD002 (Medium 10-100MW) | J31152 / J31153 | 60 | 60 | 50 | no |
| PPHDAMAS, PPHDAMPS, PPHRORAS, PPHRORPS | PWRHYD002 / PWRHYD003 (Small <10MW) | J31153 / J31154 | 60 | 60 | 40 | no |
| PPHD | PWRHYD003 | J31154 | 60 | 60 | 33 | no |
| PPIHD | PWRHYD004 (Off-grid Hydropower) | J31166 | 40 | not printed | 33 | no |
| PPWNDON | PWRWND001 (Onshore Wind) | J31155 | 30 | 30 | 25 | no |
| PPWNDD | PWRWND001 | J31155 | 30 | 30 | 25 | no |
| PPPVT | PWRSOL001 (Solar PV (Utility)) | J31149 | 25 | 25 | 25 | yes |
| PPPVTS | PWRSOL001S (Utility-scale PV with 2 hour storage) | J31158 | 30 | not printed | 25 | no |
| PPPVD | PWRSOL001 (no distributed PV without storage in kit) | J31149 | 25 | 25 | 25 | yes |
| PPPVDS | PWRSOL002 (Solar PV (Distributed with Storage)) | J31165 | 24 | 24 | 25 | no |

Deviations from the kit (24 techs): ELE_TRANS, ELE_DIST, PRONGS, PPBIM, PPIBIM, PPDDSL, PPNGS, PPRNGS, the 10 dam and run-of-river hydro techs, PPHD, PPIHD, PPWNDON, PPWNDD, PPPVTS, PPPVDS. No kit value: HYD_G_PROD, STOELE. Equal to the kit (10): PPBGS (nearest kit tech), PPCRU, PPDSL, PPRDSL, PPFOI, PPDFOI, PPILPG, PPGEO, PPPVT, PPPVD.

## Not found

- No Ecuador document (PME 2018-2027 chapter 4 and annexes, PME 2023-2032, PME 2026 adjustment, hydrogen roadmap 2023, ARCONEL regulations in the folder) states a life for electrolysers, stand-alone batteries, geothermal plants or gas production assets.
- The kit has no biogas, electrolyser or stand-alone storage technology; MINNGS carries 1.
- PLANMICC has no storage, LPG or distributed-hydro technology.

## Unreachable

- `https://rise.esmap.org/data/files/library/ecuador/Renewable%20Energy/Ecuador_Update%20to%20the%20Report%20on%20Cost%20of%20Public%20Electricity%20Services%202021.pdf` (S2): the file was saved in `downloads/d12_lives/` by the earlier, stopped attempt. Re-fetching on 2026-11-20 with Git Bash curl and with curl.exe (both `-L -A "Mozilla/5.0"`) returned a 6 012-byte HTML "Just a moment..." bot-check page, so the hash of the saved copy could not be compared with the live file. The saved PDF's own title, report number INF.DRETSE.2021.035 and dates match the ESMAP listing title "Ecuador Update to the Report on Cost of Public Electricity Services 2021". A Wayback Machine attempt was not run (blocked in this session).
