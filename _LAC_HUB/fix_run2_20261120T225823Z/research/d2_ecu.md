# d2_ecu: Ecuador power statistics 2018 to 2024 (ARCONEL, CENACE)

Retrieved 2026-11-20 (UTC). All values are as printed in the downloaded files (decimal comma converted to decimal point). Files are in `downloads/d2_ecu/`; hashes and URLs are in `research/d2_ecu_sources.csv`. Short names used below:

- E2018 ... E2025 = ARCONEL "Estadistica Anual y Multianual del Sector Electrico Ecuatoriano" of that year (`ARCONEL_Estadistica_<year>.pdf`; E2024 is the earlier download ECU-020, read in `LAC_sources_archive/cost_src_ecu_20261110T025435Z/ECX/ARCONEL_Estadistica_2024.pdf`).
- Page numbers are PDF pages. Printed page = PDF page for E2021 to E2025; printed = PDF minus 18 for E2019 and E2020; printed = PDF minus 14 for E2018 (from its index).
- C2021 ... C2025 = CENACE "Informe Anual" of that year (`CENACE_Informe_Anual_<year>_parteN.pdf`).
- Atlas2024 = `ARCONEL_Atlas_2024.pdf`.

"SNI" = national interconnected grid. "No Incorporado" = isolated systems (oil fields in the Amazon and Galapagos). "Autogeneradora" = self-generator (most are oil companies, E2024 p.44).

## (a) Plants that entered operation, 2018 to 2025

ARCONEL prints one table per year, "Centrales que entraron en operacion en el <year>" (company type, company, plant, type, system, nominal MW, effective MW), and a second table "Energia disponible de centrales incorporadas" with the start month. The tables do not print province, basin, dam or run-of-river, or fuel. CENACE prints dates of entry and of commercial operation for SNI plants. Province is added below only where the plant list of E2020 Annex A prints it.

| Year | Plant (owner) | Type, system | Nominal / effective MW | Start month (ARCONEL) | CENACE date and MW | Source |
|---|---|---|---|---|---|---|
| 2018 | Minas San Francisco (CELEC-Enerjubones) | Hydro, SNI; Azuay in E2020 Annex A.1 | 270.00 / 270.00 | nov-18 | | E2018 Tabla 1 p.21; Tabla 40 p.47 |
| 2018 | Delsitanisagua (CELEC-Gensur) | Hydro, SNI; Zamora Chinchipe | 180.00 / 180.00 | dic-18 | | same |
| 2018 | Pusuno (ElitEnergy) | Hydro, SNI; Napo | 38.25 / 38.25 | dic-18 | | same |
| 2018 | Ipnegal (IPNEGAL) | Hydro, SNI; Pichincha | 10.44 / 10.36 | ene-18 | | same |
| 2018 | Hidronormandia (self-generator) | Hydro, SNI; Morona Santiago | 49.58 / 49.58 | ago-18 | | same |
| 2018 | Sacha Norte 2, Sacha Sur GAS Wakesha, Cuyabeno E, Tambococha A (Petroamazonas), Estacion Mira (Orion) | Thermal, No Incorporado, self-generation | 15.33/11.49; 4.20/3.60; 3.65/2.74; 2.13/1.84; 0.18/0.17 | abr-18, dic-18, n/p, n/p, ago-18 | | same |
| 2018 | Isabela Solar (E.E. Galapagos); Panel Fotovoltaico (E.E. Ambato) | PV, No Incorporado as printed | 0.95/0.95; 0.20/0.20 | jul-18; ene-18 | | same |
| 2019 | CAMPO ITT (CELEC-Termopichincha) | Thermal (MCI, Orellana in Annex A.1), No Incorporado | 34.00 / 30.00 | ene-19 | | E2019 Tabla 1 p.26; Tabla 40 p.60 |
| 2019 | Rio Verde Chico (Hidrosierra) | Hydro, SNI; Tungurahua | 10.00 / 10.20 | abr-19 | | same |
| 2019 | Aurora (Andes Petro); Tambococha D, Tiputini Gas (Petroamazonas); MDC-LOC40 (Sipec) | Thermal, No Incorporado, self-generation | 2.43/1.95; 1.07/0.92; 5.25/4.75; 1.29/0.95 | ene-19; oct-19; ene-19; oct-19 | | same |
| 2020 | San Jose de Minas | Hydro, SNI; Pichincha | 6.75 / 5.95 | Jun-20 | | E2020 Tabla 37 p.66; Tabla 70 p.88 |
| 2020 | El Laurel (Cbsenergy) | Hydro, SNI; Carchi | 1.00 / 1.00 | Nov-20 | | same |
| 2020 | Hormiguero E (Andes Petro) | Thermal, No Incorporado | 0.75 / 0.50 | Feb-20 | | same |
| 2021 | Chalpi (EPMAPS) | Hydro, SNI | 8.10 / 8.10 | abr-21 | "C. H. Chalpi Grande" 7.76 MW, 12 Apr 2021 | E2021 Tabla 27 p.54; Tabla 60 p.75; C2021 parte2 p.2 (printed 98) Tabla 3.1 |
| 2021 | Cuyabeno Crudo Diesel CELEC (Petroecuador) | Thermal, No Incorporado, self-generation | 25.60 / 20.74 | n/p | | E2021 Tabla 27 p.54 |
| 2021 | Shushufindi - CG - Gas (CELEC EP) (Petroecuador) | Thermal, No Incorporado, self-generation | 22.80 / 15.00 | ago-21 | | E2021 p.54, p.75 |
| 2021 | Vindobona; Biogas Pichacay U2 (CENACE only) | Hydro; biogas; SNI | | | 4.85 MW, 9 Feb 2021; 0.847 MW, 1 Oct 2021 | C2021 parte2 p.2 Tabla 3.1 |
| 2022 | Huascachaca (Elecaustro) | Wind, SNI | 32.00 / 28.57 | dic-22 | Grupo A 18 MW 2 Dec 2022; Grupo B 18 MW 24 Dec 2022 | E2022 Tabla 27 p.45; Tabla 60 p.64; C2022 parte1 p.111 Tabla 3.1 |
| 2022 | Sarapullo (CELEC-Hidrotoapi) | Hydro, SNI | 48.45 / 48.45 | feb-22 | 49 MW, 07 Jul 2022 | same |
| 2022 | Central Hidroelectrica Sabanilla (Fideicomiso Titularizacion PHS) | Hydro, SNI | 36.00 / 30.60 | oct-22 | 30 MW, 1 Dec 2022 | same |
| 2022 | PBHI-Inchi CPF (Sipec) | Thermal, No Incorporado | 4.649 / 3.9 | feb-22 | | E2022 p.45, p.64 |
| 2022 | San Cristobal Solar (E.E. Galapagos) | PV, No Incorporado | 1.00 / 1.00 | ene-22 | | same |
| 2023 | Huascachaca (Elecaustro) | Wind, SNI | 49.98 / 49.98 | mar-23 | 50 MW, commercial operation 31 Mar 2023 | E2023 Tabla 27 p.44; Tabla 60 p.63; C2023 parte2 p.1 (printed 104) Tabla 3.1 |
| 2023 | Sarapullo (CELEC-Hidrotoapi) | Hydro, SNI | 48.45 / 48.45 | mar-23 | 49 MW, commercial operation 01 Mar 2023 | same |
| 2023 | Ulba (Hidroulba) | Hydro, SNI | 1.00 / 1.00 | abr-23 | 1 MW, 06 Apr 2023 | same |
| 2023 | Tarapoa 2 (Andes Petro); MDC-LOC16, MDC-LOC60 (Sipec) | Thermal, No Incorporado | 3.65/2.4; 0.9/0.65; 1.8/1.3 | feb-23; abr-23; oct-23 | | E2023 p.44, p.63 |
| 2023 | Agroazucar (CENACE only) | Biomass, SNI | | | 29.8 MW, commercial operation 01 Sep 2023 | C2023 parte2 p.1. ARCONEL already counted Ecudos A-G 29.80 MW in 2020 (Annex A.1), so no new MW in ARCONEL |
| 2024 | Huayquichuma (Sipenergy S.A., self-generator) | Hydro, SNI | 6.50 / 6.50 | ene-24 | 6.5 MW, 31 Jan 2024 | E2024 Tabla 27 p.44; Tabla 60 p.64; C2024 parte3 p.9 (printed 130) Tabla 3.2 |
| 2024 | Abanico, capacity increase (Hidroabanico, self-generator) | Hydro, SNI; Morona Santiago | 15.38 / 15.26 | may-24 | units 6 and 7, 15.46 MW, 28 May 2024 | same |
| 2024 | Ecudos A-G / La Troncal, capacity increase (Agroazucar) | Biomass, SNI | 14.00 / 13.70 | may-24 | turbogenerator 5, 14 MW, 31 May 2024 | same |
| 2024 | Mira (Hidromira) | Hydro, SNI | 0.99 / 1.03 | abr-24 | | E2024 p.44, p.64 |
| 2024 | Karpowership (CELEC-Electroguayas) | Thermal, SNI | 105.30 / 100.00 | sep-24 | floating plant Karpowership Emre Bey KPS 27, 100 MW, 16 Sep 2024; "Termoelectrico HFO, Arrendamiento", 19-sep-24 | E2024 p.44, p.64; C2024 parte3 p.9 Tabla 3.2 and p.3 (printed 124) Tabla 3.1 |
| 2024 | Alluriquin (CELEC-Hidrotoapi) | Hydro, SNI | 204.00 / 204.00 | dic-24 | unit 3, 68 MW, 21 Dec 2024, experimental | same |
| 2024 | MDC-LOC03, MDC-LOC70, PBHI-InchiE, PBH-PAR11 (Sipec) | Thermal, No Incorporado | 1.20/1.10; 2.24/2.00; 2.49/2.00; 1.70/1.50 | feb-24; feb-24; jul-24; feb-24 | | E2024 p.44, p.64 |
| 2024 | San Bartolo U1 capacity increase; Biogas Gasgreen (CENACE only) | Hydro; biogas | | | 1.07 MW, 13 Dec 2024; 2.84 MW, 21 Dec 2024; both experimental | C2024 parte3 p.9 |
| 2025 | Alluriquin (CELEC-Hidrotoapi) | Hydro, SNI | 204.00 / 195.12 | | U1 22-ene-25, U2 24-ene-25, U3 25-ene-25, 68 MW each | E2025 Tabla 17 p.32; C2025 parte2 p.2 Tabla 3.1 and p.6 (printed 120) Tabla 3.2 |
| 2025 | Mini Central Toachi (CELEC-Hidrotoapi) | Hydro, SNI | 1.40 / 1.40 | | 1.4 MW, 13 May 2025 | same |
| 2025 | Murat Bey (Esclusas I), Erin Sultan (Esclusas II), Murat Bey (Esclusas III) (Elecaustro) | Thermal, SNI | 100/100; 100/100; 95/95 | | Karpowership Murat Bey KPS 67 100 MW 03 Feb 2025 (first contract), Erin Sultan 100 MW 06 May 2025, Murat Bey 95 MW 10 Oct 2025 (second contract); "Termoelectrico HFO, Arrendamiento" | same |
| 2025 | El Descanso (Emergente); GASVESUBIO (Elecaustro) | Thermal, SNI | 20.00/20.00; 13.67/13.50 | | Descanso II 18 MW diesel, leased, 13 Sep 2025; Vesubio 13.5 MW natural gas, leased, 26 Aug 2025 | same |
| 2025 | MDC-LOC80 (Sipec); Hidrosanbartolo increase | Thermal No Incorporado; hydro SNI | 2.40/2.00; 1.07/1.08 | | San Bartolo unit 2, 17.73 MW, 23 May 2025 (CENACE) | same |

Printed yearly totals of the ARCONEL tables (nominal / effective MW): 2018 574.91 / 569.17; 2019 54.04 / 48.77; 2020 8.50 / 7.45; 2021 56.50 / 43.84; 2022 122.10 / 112.52; 2023 105.78 / 103.78; 2024 353.80 / 347.09; 2025 537.54 / 528.10.

Notes printed with the tables:
- E2022 p.45: Huascachaca, Sarapullo and San Cristobal Solar generated energy but had not entered commercial operation at 31 December 2022; Huascachaca ran 8 turbines of 3.57 MW effective each, final effective power 49.98 MW. E2023 p.44 lists Huascachaca and Sarapullo again with the note that in 2022 they generated "en la modalidad de operacion experimental". So the two plants appear in two yearly tables; count them once.
- E2024 p.44 Nota 1: Alluriquin started experimental operation in December 2024 and was not declared in commercial operation at the end of 2024. Nota 2: the Abanico and Ecudos A-G values are capacity increases.
- C2024 parte3 p.3 Tabla 3.1 "Ingreso de generacion para afrontar el estiaje" (total 589.2 MW): Quevedo reposicion 54.4 MW HFO, own, 19-sep-2024 and 21-oct-2024; Santa Elena reposicion 28 MW HFO, own, 27-jul-24; Emre Bey barge 100 MW HFO, leased, 19-sep-24; Alluriquin U1 to U3 68 MW each, January 2025; Murat Bey barge (Elecaustro) 100 MW, 3-feb-25; Alluriquin mini central 1 MW, 13-feb-25; Esclusas Elecaustro (Sultan) 100 MW, 3-mar-25. The two "reposicion" items are restored capacity of existing plants and are not in the ARCONEL table of new plants.
- C2025 parte2 p.6 Tabla 3.2 prints the commercial operation date of "Alluriquin U1, U2 y U3, 204 MW" as "31 MAYO 2024". This conflicts with the unit dates of January 2025 on p.2 and with E2024 Nota 1; it is probably a misprint for 2025. Not resolved.

Plants named in the task:
- Sarapullo: 48.45 MW (ARCONEL), 49 MW (CENACE); experimental from 2022 (feb-22 ARCONEL, 07 Jul 2022 CENACE); commercial operation 01 Mar 2023.
- Alluriquin: 204 MW; experimental December 2024; units in January 2025; counted by ARCONEL in end-2024 capacity (hydro 5,419.17 MW includes it).
- Minas San Francisco 270 MW and Delsitanisagua 180 MW: 2018 (nov-18, dic-18).
- Minas de Huascachaca (wind): 32.00 MW nominal at end 2022, 49.98 MW in 2023; commercial operation 31 Mar 2023.
- Villonaco 2 and 3: not in operation. Atlas2024 p.21: "se han planificado expansiones como los proyectos Villonaco II y III, que anadiran 110 MW". National wind stays at 71.13 MW in 2023 and 2024 and 71.15 MW in 2025.
- El Aromo (PV): not in operation. Atlas2024 p.21: "capacidad planificada de 200 MW". National PV in plants is 29.13 MW in 2024 and 2025.
- Machala Gas / Termogas Machala: no new unit printed in any yearly table 2018 to 2025. E2020 Annex A.1 (p.212): Termogas Machala I 138.56 / 130.60 MW and II 136.80 / 119.00 MW (Turbogas, El Oro). E2024 Tabla 36 (p.50) still shows El Oro non-renewable 2 plants, 275.36 MW nominal (= 138.56 + 136.80).
- Emergency thermal 2023: none printed (E2023 Tabla 27 has no SNI thermal plant). 2024: Karpowership only (105.30 / 100.00 MW), plus the two restored plants above. Rented engines and further barges appear in 2025.

## (b) Installed capacity at year end, MW

National, nominal (N) and effective (E), each year from that year's own edition:

| Year | Hydro N / E | Wind N / E | PV N / E | Biomass N / E | Biogas N / E | Thermal MCI N / E | Turbogas N / E | Turbovapor N / E | Total N / E | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | 5,066.40 / 5,036.43 | 21.15 / 21.15 | 27.63 / 26.74 | 144.30 / 136.40 | 7.26 / 6.50 | 2,011.44 / 1,613.60 | 921.85 / 775.55 | 461.87 / 431.74 | 8,661.90 / 8,048.11 | E2018 Tabla 80 (1/3) p.108 |
| 2019 | 5,076.40 / 5,046.63 | 21.15 / 21.15 | 27.63 / 26.74 | 144.30 / 136.40 | 7.26 / 6.50 | 2,024.80 / 1,628.34 | 921.85 / 775.55 | 461.63 / 431.50 | 8,685.01 / 8,072.81 | E2019 Tabla 80 (1/3) p.128 |
| 2020 | 5,098.75 / 5,064.16 | 21.15 / 21.15 | 27.63 / 26.74 | 144.30 / 136.40 | 7.26 / 6.50 | 2,029.74 / 1,633.25 | 921.85 / 775.55 | 461.63 / 431.50 | 8,712.29 / 8,095.25 | E2020 Tabla 4 (1/3) p.28 |
| 2021 | 5,106.85 / 5,072.26 | 21.15 / 21.15 | 27.65 / 26.76 | 144.30 / 136.40 | 8.32 / 7.20 | 2,020.67 / 1,614.85 | 943.85 / 790.55 | 461.63 / 431.50 | 8,734.41 / 8,100.68 | E2021 Tabla 4 (1/3) p.27 |
| 2022 | 5,191.30 / 5,151.31 | 53.15 / 49.72 | 28.65 / 27.76 | 144.30 / 136.40 | 8.32 / 7.20 | 2,033.18 / 1,625.11 | 943.85 / 790.55 | 461.63 / 431.50 | 8,864.37 / 8,219.55 | E2022 Tabla 4 (1/3) p.21 |
| 2023 | 5,192.30 / 5,152.31 | 71.13 / 71.13 | 29.06 / 28.17 | 144.30 / 136.40 | 8.32 / 7.20 | 2,048.00 / 1,636.39 | 944.85 / 791.35 | 461.63 / 431.50 | 8,899.58 / 8,254.45 | E2023 Tabla 4 (1/3) p.20 |
| 2024 | 5,419.17 / 5,371.24 | 71.13 / 71.13 | 29.13 / 28.24 | 155.30 / 147.70 | 11.12 / 9.97 | 2,163.60 / 1,745.07 | 943.85 / 790.55 | 461.63 / 431.50 | 9,254.92 / 8,595.40 | E2024 Tabla 30 p.46 |
| 2025 | 5,388.85 / 5,387.42 | 71.15 / 71.13 | 29.13 / 28.24 | 156.05 / 148.50 | 11.12 / 9.97 | 2,377.09 / 1,980.08 | 955.31 / 808.05 | 460.13 / 446.00 | 9,448.83 / 8,879.39 | E2025 Tabla 20 p.33 |

The multi-year tables E2024 Tabla 28 and 29 (p.45) and E2025 Tabla 18 and 19 (p.33) repeat the same values for hydro, wind, biomass, PV, biogas and total thermal (no revision of earlier years). Thermal is split by engine type only (MCI = internal combustion engines, Turbogas, Turbovapor). Capacity by fuel is not printed in any edition.

SNI and non-incorporated, 2015 to 2024 series (E2024 Figura 33 p.43 and Figura 34 p.44, values read from the figure labels):

| Year | SNI nominal | SNI effective | No Incorporado nominal | No Incorporado effective |
|---|---|---|---|---|
| 2018 | 7,355.52 | 7,052.32 | 1,306.38 | 995.79 |
| 2019 | 7,317.92 | 7,022.02 | 1,367.10 | 1,050.79 |
| 2020 | 7,340.26 | 7,039.55 | 1,372.04 | 1,055.70 |
| 2021 | 7,357.84 | 7,048.35 | 1,376.57 | 1,052.32 |
| 2022 | 7,472.69 | 7,154.57 | 1,391.68 | 1,064.98 |
| 2023 | 7,491.67 | 7,176.98 | 1,407.91 | 1,077.46 |
| 2024 | 7,838.25 | 7,509.12 | 1,416.67 | 1,086.28 |

Check: 2018 7,355.52 + 1,306.38 = 8,661.90. In 2024 the non-incorporated 1,416.67 MW nominal is 1,380.71 continental plus 35.96 Galapagos (E2024 Figura 35 p.44).

SNI nominal by technology, 2024 (E2024 Tabla 4 (1/3) p.21): hydro 5,415.97; wind 66.48; PV 24.46; biomass 155.30; biogas 11.12; MCI 899.13; Turbogas 819.80; Turbovapor 446.00; total 7,838.25. So non-incorporated MCI = 2,163.60 - 899.13 = 1,264.47 MW nominal. 2025 (E2025 Tabla 4 p.19): SNI total 8,029.75; MCI 1,110.29 of 2,377.09.

By company type, 2024 (E2024 Tabla 33 p.47): generators 7,001.26 / 6,753.67; self-generators 1,800.56 / 1,460.70 (hydro 262.77, MCI 1,242.81, Turbogas 124.05, Turbovapor 15.63, biomass 155.30 nominal); distributors 453.10 / 381.03.

By province, 2024: E2024 Tabla 36 p.50 to 51 (for example Orellana 91 plants 759.37 MW and Sucumbios 69 thermal plants 548.25 MW non-renewable; Santo Domingo de los Tsachilas 1 renewable plant 204.00 MW, which can only be Alluriquin).

### Hydro plant list and size classes

The only plant-by-plant capacity table found is E2020 Annex A.1, A.2, A.3 "Potencia nominal y efectiva ... por tipo de central" (PDF p.211 to 220, printed 193 to 202), at end 2020. Editions 2021 to 2025 do not print it. The extracted list of the 74 hydro plants (company, plant, province, nominal, effective) is saved as `downloads/d2_ecu/ARCONEL_Estadistica_2020_AnexoA_hydro_list.txt` (full extraction of the annex in `..._AnexoA_tables_extract.txt`). Sum of the list: 5,098.74 MW nominal (printed annex totals 4,715.70 + 240.89 + 142.16 = 5,098.75, equal to the 2020 hydro total).

Size classes at end 2020, nominal MW (my sums of the annex rows):
- Above 450 MW: 3 plants, 3,062.00 (Coca Codo Sinclair 1,500.00 Napo; Molino 1,075.00 Azuay; Sopladora 487.00 Azuay).
- 50 to 450 MW: 9 plants, 1,423.66 (Minas San Francisco 270.00 Azuay; San Francisco 230.00 Tungurahua; Marcel Laniado 213.00 Guayas; Delsitanisagua 180.00 Zamora Chinchipe; Mazar 170.00 Azuay; Agoyan 160.00 Tungurahua; Pucara 73.00 Tungurahua; Due 64.30 Sucumbios; Manduriacu 63.36 Imbabura).
- Under 50 MW: 62 plants, 613.08. By province group: Amazon provinces 8 plants 197.91 (Hidrosanbartolo 49.98, Hidronormandia 49.58, Abanico 38.45, Pusuno 38.25, Victoria 10.32, Papallacta 6.63, Carlos Mora 2.40, Loreto 2.30); coast provinces 2 plants 57.57 (Baba 42.20, Sibimbe 15.37); Sierra provinces 52 plants 357.60.

Additions 2021 to 2024, nominal MW (yearly tables in section a): Chalpi 8.10 (2021); Sarapullo 48.45 and Sabanilla 36.00 (2022); Ulba 1.00 (2023); Huayquichuma 6.50, Abanico +15.38, Mira 0.99, Alluriquin 204.00 (2024). Sum 320.42; 5,098.75 + 320.42 = 5,419.17, equal to the printed 2024 hydro total. So over 2021 to 2024 the documents show: one medium plant (Alluriquin 204.00, 50 to 450 MW) and 116.42 MW of plants under 50 MW (Abanico with its increase becomes 53.83 MW). No plant above 450 MW.

Slope (Amazon or Pacific): the statistics do not print it per plant. What is printed: E2020 Tabla 21 p.49 puts Coca Codo Sinclair, Amaluza, Minas San Francisco, Delsitanisagua, Mazar, Agoyan and Pisayambo under "Cuenca Hidrografica Oriental" and Daule Peripa under "Occidental". Atlas2024 p.28 says the largest plants are on the eastern slope and "en la vertiente del pacifico se ubican las centrales Minas San Francisco, Manduriacu y Marcel Laniado de Wind" (the two documents disagree on Minas San Francisco). Province is printed for the 2020 list only; the province groups above are my grouping by province (Napo, Sucumbios, Orellana, Pastaza, Morona Santiago, Zamora Chinchipe = Amazon), not a printed basin. Province of Chalpi, Sarapullo, Sabanilla, Ulba, Huayquichuma and Mira is not printed in the files read. Dam or run-of-river is not printed.

## (c) Generation, GWh

Gross generation, national (SNI plus non-incorporated), each year from that year's own edition:

| Year | Hydro | Wind | PV | Biomass | Biogas | MCI | Turbogas | Turbovapor | Total gross | Imports | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | 20,678.00 | 80.26 | 38.08 | 382.44 | 45.52 | 4,942.06 | 1,339.29 | 1,737.93 | 29,243.59 | 106.08 | E2018 Tabla 80 (2/3) p.109 |
| 2019 | 24,640.57 | 85.53 | 37.62 | 413.56 | 41.16 | 4,618.39 | 1,185.73 | 1,261.39 | 32,283.96 | 5.83 | E2019 Tabla 80 (2/3) p.129 |
| 2020 | 24,333.26 | 77.10 | 37.76 | 426.59 | 43.99 | 4,422.11 | 981.75 | 925.43 | 31,248.00 | 250.79 | E2020 Tabla 4 (1/3) p.28 |
| 2021 | 25,574.61 | 62.01 | 36.87 | 372.80 | 42.13 | 4,335.56 | 911.82 | 871.07 | 32,206.88 | 363.80 | E2021 Tabla 4 (1/3) p.27 |
| 2022 | 24,635.16 | 60.60 | 38.50 | 348.08 | 41.59 | 5,366.38 | 1,021.54 | 1,496.46 | 33,008.30 | 465.83 | E2022 Tabla 4 (1/3) p.21 |
| 2023 | 25,348.71 | 208.58 | 40.57 | 318.02 | 38.33 | 6,301.47 | 1,533.74 | 1,572.60 | 35,362.03 | 1,320.94 | E2023 Tabla 4 (1/3) p.20 |
| 2024 | 22,614.43 | 223.54 | 38.77 | 460.91 | 36.11 | 7,156.96 | 1,724.26 | 2,115.35 | 34,370.33 | 1,269.56 | E2024 Tabla 4 (1/3) p.21; Tabla 53 p.58 |
| 2025 | 28,128.72 | 188.31 | 37.06 | 370.72 | 42.94 | 6,398.31 | 1,296.81 | 1,749.44 | 38,212.31 | 624.35 | E2025 Tabla 4 (1/3) p.19; Tabla 35 p.40 |

SNI only, gross (same tables): 2018 hydro 20,661.59, wind 73.70, PV 34.77, biomass 382.44, biogas 45.52, MCI 1,447.85, Turbogas 1,021.53, Turbovapor 1,708.52, total 25,375.92. 2019: 24,619.13; 79.98; 33.13; 413.56; 41.16; 854.22; 888.65; 1,234.30; total 28,164.14. 2020: 24,312.85; 71.64; 33.82; 426.59; 43.99; 783.10; 708.16; 920.37; total 27,300.52. 2021: hydro 25,555.53; wind 60.06; PV 33.44; biomass 372.80; biogas 42.13; MCI 671.95; Turbogas 594.53; Turbovapor 843.06; total 28,173.50. 2022: 24,624.39; 57.89; 33.28; 348.08; 41.59; 1,557.76; 703.56; 1,496.45; total 28,863.00. 2023: 25,338.84; 205.99; 34.83; 318.02; 38.33; 2,470.00; 1,246.10; 1,556.48; total 31,208.59. 2024: 22,607.19; 221.80; 33.21; 460.91; 36.11; 3,259.99; 1,385.77; 2,107.74; total 30,112.72. 2025: 28,124.02; 185.82; 31.65; 370.72; 42.94; 2,528.09; 932.12; 1,749.44; total 33,964.78.

Revised totals: the multi-year table (E2024 Tabla 51 p.57, same in E2025 Tabla 33 p.39 and in `ARCONEL_Balance_multianual_2015_2024.xlsx` row 3) gives gross generation 2018 29,244.63; 2019 32,270.89; 2020 31,252.27; 2021 32,218.33; 2022 33,012.80; 2023 35,362.03; 2024 34,370.33; 2025 38,212.31. So 2018 to 2022 were revised slightly after the yearly editions; the split by technology is printed only in the yearly editions. The same table gives energy delivered to public service (2024: 27,997.81) and energy not delivered to public service, which is mostly oil-company self-generation (2018 4,906.68; 2021 5,727.72; 2024 5,940.32).

Generation by fuel is not printed. The editions print fuel consumption for power generation instead, for example E2024 Tabla 59 p.64 for 2024: fuel oil 290.27 million gal, diesel 247.28 million gal, natural gas 16.27 "kpc x 10^6", residuo 16.73 million gal, crude 141.88 million gal, LPG 3.64 million gal, bagasse 1,640.65 thousand t, biogas 21,529,716.52 m3; total 3,024,063.90 TEP. By system in 2024 (E2024 Tabla 52 p.58): non-incorporated self-generator thermal 4,151.32 GWh, non-incorporated generator thermal 91.74 GWh, SNI generator thermal 6,104.62 GWh.

Energy of plants in their entry year (E2024 Tabla 60 p.64): Karpowership 249.72 GWh (sep to dec 2024), Alluriquin 18.21, Huayquichuma 32.13, Abanico increase 61.15. E2023 Tabla 60 p.63: Sarapullo 164.51, Huascachaca 131.79, Ulba 6.08. E2022 Tabla 60 p.64: Sarapullo 42.46, Sabanilla 16.17, Huascachaca 4.45.

## (d) Distributed generation for self-supply (SGDA)

E2024 Tabla 108 p.108 "Cantidad y potencia nominal total de SGDAS instalados a nivel nacional, periodo 2019-2024" and E2025 Tabla 79 p.68 (same series plus 2025). Cumulative number and nominal MW:

| Year | Number | Nominal MW |
|---|---|---|
| 2019 | 2 | 0.06 |
| 2020 | 28 | 2.35 |
| 2021 | 120 | 5.90 |
| 2022 | 360 | 20.22 |
| 2023 | 869 | 38.38 |
| 2024 | 1,247 | 54.78 |
| 2025 | 2,359 | 113.26 |

E2023 Tabla 109 p.109 gives the same in kW: 62.24; 2,352.61; 5,900.31; 20,217.67; 38,379.51 (2019 to 2023). Increase from end 2020 to end 2024 = 54.78 - 2.35 = 52.43 MW. The E2024 text (p.108) says the systems were installed under Regulations ARCONEL-003/18 and later ones; the text calls the unit "MVA" while the table header says MW. By distributor for 2024 and 2025: E2024 Tabla 109 p.108, E2025 Tabla 80 p.68. These systems are not part of the 29.13 MW of PV in plants in section b. Emergency generator sets qualified (GEE), 2024: 336 units, 404.56 MW (E2024 Tabla 110 p.109); they are not counted in installed capacity either.

## What the documents show against the model builds of 2021 to 2024

(Values as printed; sums are mine.)
- Hydro, all sizes: +320.42 MW nominal over 2021 to 2024 (5,098.75 to 5,419.17), of which Alluriquin 204.00 and Sarapullo 48.45 (Toachi Pilaton), Sabanilla 36.00, Abanico +15.38, Chalpi 8.10, Huayquichuma 6.50, Ulba 1.00, Mira 0.99.
- Wind: +49.98 MW (21.15 to 71.13), Huascachaca only.
- PV in plants: +1.50 MW (27.63 to 29.13). SGDA: +52.43 MW (2.35 to 54.78).
- Biomass +11.00 MW (144.30 to 155.30); biogas +3.86 MW (7.26 to 11.12).
- Thermal MCI: +133.86 MW nominal (2,029.74 to 2,163.60). Listed new MCI or thermal plants 2021 to 2024: Karpowership 105.30 (SNI, HFO per CENACE) and non-incorporated oil-field plants 25.60 + 22.80 + 4.649 + 3.65 + 0.9 + 1.8 + 1.20 + 2.24 + 2.49 + 1.70 = 67.03 MW (the type MCI or turbine is not printed for these; Shushufindi is named "Gas").
- Turbogas: 921.85 (2020) to 943.85 (2021 to 2022), 944.85 (2023), 943.85 (2024). Turbovapor unchanged at 461.63.

## Not found

- Province, basin and dam or run-of-river for plants added after 2020. Tried: yearly tables and province tables of E2021 to E2025, Atlas2024 text, CENACE reports (plant names only).
- Capacity and generation by fuel. Only engine type (MCI, Turbogas, Turbovapor) and fuel consumption are printed.
- A per-plant capacity list after 2020.
- CELEC EP documents: none downloaded. The CELEC site pages `informacion-tecnica/generacion/` returned only the menu (content loads by script), `rendicion-de-cuentas/` and `rendicion-de-cuentas-2024/` returned 404, and one web search did not find the CELEC accountability report.
- CENACE Informe Anual 2018 to 2020 and Atlas of other years: not downloaded (time). CENACE "Informe Operativo Anual 2023" was downloaded but not used.
- Statistical annexes in xlsx: ARCONEL publishes only `Balance-multianual-2015-2024.xlsx` (saved) and the monthly `BNEE_agosto_2026.xls` (saved, one sheet, not used for values). No xlsx annex of the yearly statistics is linked on the publications page.

## Unreachable

- `https://www.controlelectrico.gob.ec` and `https://controlelectrico.gob.ec`: curl error 6, could not resolve host. The Wayback Machine (`https://web.archive.org/web/2026/https://www.controlelectrico.gob.ec/`) redirects to a capture of `https://arconel.gob.ec/`, which works and was used.
- `https://www.controlrecursosyenergia.gob.ec/`: curl TLS certificate error.
- `https://anda.inec.gob.ec/anda/index.php/catalog/ARCERNNR` and `.../catalog`: HTTP 403 with Git Bash curl (plain and browser user agent) and with `curl.exe`. Wayback capture of 2025-02-10 opens but shows the general INEC catalogue list (censuses), no ARCERNNR entries on the page. Not needed, the regulator site has every edition.
- `https://www.cenace.gob.ec/informe-anual-2024/`: 404. The files are linked from `https://www.cenace.gob.ec/biblioteca/` (used).
- CENACE download ids 3414 (Informe Anual 2021, full) and 3826 (2022, full) return an HTML page with a flip-book (`online.fliphtml5.com`), not a PDF. Used the part files instead (ids 3412, 3413, 3827).
- `https://www.celec.gob.ec/rendicion-de-cuentas/` and `/rendicion-de-cuentas-2024/`: 404.
