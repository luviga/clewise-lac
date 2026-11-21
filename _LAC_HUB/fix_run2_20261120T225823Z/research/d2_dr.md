# d2_dr: Dominican Republic commissionings 2021-2024, net metering, self-producers

Retrieved 2026-11-21 (UTC). All paths are relative to the job folder unless marked ARCHIVE (`C:\Users\luisfernando\Desktop\OSeMOSYS\LAC_sources_archive\`) or PREVJOB (`C:\clw_fix\_LAC_HUB\fix_run_20261111T200825Z\`). SHA-256 values are in `research/d2_dr_sources.csv`. "p." is the PDF page; the printed page follows in brackets where it differs.

Short names used below:
- OC21: OC-SENI Memoria 2021, `downloads/d2_dr/mem2021/OC Memoria 2021.VF 2022.03.31.pdf` (from `memoria_anual_oc_2021.zip`)
- OC22: OC-SENI Memoria 2022, `downloads/d2_dr/mem2022/Memoria Anual OC 2022/OC Memoria 2022 WEB.pdf`
- OC23: OC-SENI Memoria 2023, `downloads/d2_dr/mem2023/OC Memoria 2023 WEB.pdf`
- OC24: OC-SENI Memoria 2024, ARCHIVE `cost_src_dr_20261110T025405Z/lp/DR/ocseni/memoria2024/Memoria Anual 2024.pdf` (from `memoria_anual_oc_2024.zip`, OC entry 200289, 11,496,253 bytes, same size as listed on the OC page)
- OC20: OC-SENI Memoria 2020, `downloads/d2_dr/mem2020/OC Memoria 2020 web.VF 26.03.2021.pdf`
- CNE21 to CNE25: CNE Memoria Institucional 2021 to 2025, `downloads/d2_dr/cne_memoria_institucional_20XX.pdf`
- PEN: CNE Plan Energetico Nacional 2022-2036, PREVJOB `downloads/r4/PEN2022-2037.pdf` (earlier job id CSD-008)
- IRENA25: IRENA Renewable Energy Statistics 2025, `downloads/d2_dr/irena/IRENA_DAT_RE_Statistics_2025.pdf`
- OC memoria download URL pattern: `https://www.oc.do/DesktopModules/Bring2mind/DMX/API/Entries/Download?EntryId=<id>&PortalId=0` (ids from `downloads/map_dr/oc_memoria_anual.html`; checked 2026-11-21 for EntryId 176192: HTTP 206, application/zip, starts with "PK")
- UN: UNSD Energy Statistics Database pages (UNdata, last update 2025/12/15), `downloads/d2_dr/un/*.html`

## (a) SENI commissionings 2021-2024 and installed capacity

### Plants that entered the SENI (gross MW as printed in Tabla 2 of each memoria)

| Year | Plant (agent) | MW | Technology / fuel as printed | Date as printed | Locator |
|---|---|---|---|---|---|
| 2021 | Parque Fotovoltaico Bayahonda (Parque Eolico Beata) | 50.00 | Solar / SOL | entrada comercial 10 jul 2021 | OC21 p.31 [29] text and Tabla 2 |
| 2021 | Girasol (EGE-Haina) | 100.00 | Solar / SOL | 04 dic 2021 | OC21 p.31 |
| 2021 | Estrella del Mar 3 (Seaboard) | 150.00 | Ciclo Combinado / GAS | "en proceso de codigo de conexion" but counted in Tabla 2 | OC21 p.31 |
| 2022 | Parque Solar El Soco (Koror Business) | 50.00 | Solar | 01 oct 2022 | OC22 p.37 |
| 2022 | Planta Santanasol (AES Andres) | 50.00 | Solar | 29 oct 2022 | OC22 p.37 |
| 2022 | Parque Eolico Los Guzmancito II (Poseidon) | 46.80 | Eolica / VIENTO | "en proceso de codigo de conexion"; counted in Tabla 2 2022 | OC22 p.37 |
| 2023 | SIBA (SIBA Energy Corporation) | 191.48 | Turbinas a Gas / GAS NATURAL | 02 sep 2023 | OC23 p.37-38 [36] |
| 2023 | Parque Solar Esperanza (EGE-Haina) | 76.00 | Solar | 04 nov 2023 | OC23 p.37-38 |
| 2023 | Cumayasa 1 and 2 (EFD Ecoener) | 50.00 + 30.00 | Solar | 09 dic 2023 | OC23 p.38 |
| 2023 | Calabaza (Enren) | 50.60 | Solar | "en proceso de entrada comercial"; in Tabla 2 2023 | OC23 p.38 |
| 2023 | Matrisol | 46.00 | Solar | same as above | OC23 p.38 |
| 2023 | Los Negros (Phinie & Co.) | 17.00 | Solar | same as above | OC23 p.38 |
| 2023 | Powership Azua KPS 26 + KPS 60 (Karpowership) | 108.78 + 79.88 = 188.66 | Motor combustion interna / FUEL OIL # 6 | entrada comercial 20 ene 2024; already in Tabla 2 2023 | OC23 p.37-38 |
| 2024 | Pimentel 4 (LAESA) | 36.26 | FUEL OIL #6 (ICE) | 23 may 2024 | OC24 p.38 [37] text, p.41 Tabla 2 |
| 2024 | Maranatha Fase 1 | 10.00 | Solar | 21 jun 2024 | OC24 p.38, p.41 |
| 2024 | Sajoma (EGE-Haina) | 68.40 | Solar | 24 ago 2024 | OC24 p.38-39 |
| 2024 | La Victoria (Desarrollos Fotovoltaicos DSS) | 50.00 | Solar | 26 nov 2024 | OC24 p.38 |
| 2024 | Mirasol (AES Dominicana Renewable Energy) | 100.00 | Solar | 14 dic 2024 | OC24 p.38 |
| 2024 | Monte Plata Solar repowering | 30 to 60 (+30) | Solar | ago 2024 | OC24 p.38, p.40 |
| 2024 | Matafongo wind repowering | 34 to 49.6 (+15.6) | Eolica | ago 2024 | OC24 p.38, p.40 |

OC24 synthesis (text near line 450 of the extraction, PDF p.8): "ingresaron ... un total de 310.26 MW: 258.4 MW solar, 15.6 MW eolico y 36.26 MW termico".

Removals and derates printed: San Felipe 180 MW not counted from 2021 (dismantled, OC21 p.31); CEPP 76.86 MW left commercial operation (OC22 p.37); Sultana del Este 68 to 51 MW, oct 2023, and San Pedro Vapor 33 MW out, oct 2023 (OC23 p.37). OC21 also states that from 2021 solar plants are reported at inverter net capacity, which lowered the solar total.

Totals added 2021-2024 (sum of the rows above): utility PV 150 + 100 + 269.6 + 258.4 = 778.0 MW; wind 46.8 (2022) + 15.6 (2024) = 62.4 MW; fuel-oil ICE 188.66 (Karpowership, in 2023 table, commercial 2024) + 36.26 (2024) = 224.92 MW; gas turbine 191.48 MW (2023); combined cycle 150 MW (2021, Estrella del Mar 3); hydro 0; coal 0. No dual-fuel ICE unit, no self-producer plant and no hydro plant entered the SENI in 2021-2024.

### Installed capacity by technology, SENI, MW (OC24 p.127 [126], Tabla 36 "Evolucion de la capacidad instalada bruta del SENI por tecnologia 2012-2024 [MW]")

| Technology (as printed) | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| Ciclo Combinado | 1163.25 | 1163.25 | 1128.25 | 1128.25 | 1128.50 | 1128.50 |
| Eolica | 370.25 | 370.25 | 370.25 | 417.05 | 417.05 | 432.65 |
| Hidroelectrica | 623.28 | 623.28 | 623.28 | 623.28 | 623.28 | 623.28 |
| Motor combustion interna | 1285.92 | 1286.28 | 1286.28 | 1209.42 | 1380.74 | 1416.96 |
| Solar | 155.48 | 155.48 | 305.48 | 405.48 | 675.08 | 933.48 |
| Turbina a Gas | 134.00 | 134.00 | 134.00 | 134.00 | 325.48 | 325.48 |
| Turbina a Vapor | 1156.87 | 1156.87 | 1156.87 | 1156.87 | 1125.00 | 1125.00 |
| Total | 4889.05 | 4889.41 | 5004.41 | 5074.35 | 5675.12 | 5985.34 |

Notes: Turbina a Vapor in 2024 = CTPC Punta Catalina 782 + EGE-Itabo 260 + EGE-Haina 53 (all coal) + San Pedro Bio-Energy 30 (biomass), rows on the same page; coal = 1095.00 MW (OC23 Tabla 4, extraction line 1641, "1,095.00"). Hydro 623.28 MW is flat from 2019 to 2024; the last hydro addition was +7.56 MW in 2019 (615.72 in 2018 to 623.28 in 2019, same table). End-2020 as first published: 4,921.39 MW with solar 187.46 MW (OC20 p.26 [24] and p.28, before the inverter-net restatement); the 2024 memoria restates 2020 as 4889.41 MW with solar 155.48 MW. OC21 text prints the 2021 total as 5,004.10 and OC22 text prints 5,075.38 for 2022, while Tabla 36 prints 5004.41 and 5074.35.

Comparison with the model builds 2021-2024 (5 percent or 2 MW rule):
- PPPVT 488 MW vs sourced utility PV 778.0 MW: no match (no single year or subset matches 488 either: 2021-2022 = 250, 2023-2024 = 528).
- PPWNDON 47 MW vs Los Guzmancito II 46.80 MW (2022): match within 2 MW. Adding the Matafongo repowering (+15.6, 2024) gives 62.4 MW, which does not match.
- PPHDAM 7.6 MW vs no SENI hydro addition 2021-2024; the +7.56 MW addition is dated 2019. Cause to fix: timing (residual capacity should include it from 2019).
- PPICEFOI 80 / 67 / 75 MW vs fuel-oil ICE additions 224.92 MW (Karpowership 188.66 + Pimentel 4 36.26) with retirements CEPP -76.86 (2022) and Sultana del Este -17.4 (2023); net ICE change 2020-2024 = 1416.96 - 1286.28 = +130.68 MW. None matches.
- PPICEGASFOI 9.6 MW: no dual-fuel ICE commissioning found in 2021-2024.
- PPANGS, PPAFOI, PPDGSL, PPDHYD, PPDBGS (self-producers): no OC source applies; see (c).
- Gas: SIBA 191.48 MW gas turbine (2023) and Estrella del Mar 3 150 MW combined cycle (2021) are sourced additions with no model build listed in the task.

## (b) Distributed PV under net metering (Programa de Medicion Neta, PMN)

Best series: CNE24 p.30 [26], table "Periodo / Acumulativos / Por periodo", cumulative "MW" (as printed, no "p"):

| End of year | Users (cumulative) | MW (cumulative) | MW added in year |
|---|---|---|---|
| 2019 | 4927 | 131.17 | 38.15 |
| 2020 | 6746 | 177.06 | 45.89 |
| 2021 | 9120 | 219.70 | 42.64 |
| 2022 | 11577 | 285.88 | 66.18 |
| 2023 | 14974 | 346.98 | 61.10 |
| 2024 | 18034 | 424.32 | 138.44 |

Added 2021-2024 = 424.32 - 177.06 = 247.26 MW. Model PPPVD build 143 MW: no match.

Point values printed in other memorias (different cut-off dates, kW or kWp as printed):
- CNE21 p.6: 8,300 users, "200,363.51 kW instalados" (2021, no month given).
- CNE22 p.9 and p.28: 10,987 users, "272,499.42 kW" (to Oct/Nov 2022); about 422.28 GWh/yr "actualizado hasta octubre del 2022".
- CNE23 p.9 and p.14: 14,181 users, "338,794.44kW" (to Aug 2023); energy about 2 percent of system demand.
- CNE24 p.9 and p.29: 18,332 users, "433,167.40 kWp" (to Sep/Oct 2024; table by distributor "octubre 2024").
- CNE25 p.9, p.27 and p.29: 21,561 users, "495,000 kWp" (to Oct 2025); distributor table total 513,587.40 kWp (22,052 clients); about 383.61 GWh.
The memoria point values are higher than the CNE24 year-end series for the same years (for example 272.5 MW in Oct 2022 against 285.88 at end 2022 is consistent, but 200.36 in 2021 is below 219.70); the series in CNE24 is the only year-end series found.

CNE open-data workbooks `downloads/d2_dr/cne_pmn_2012_2024.xlsx` and `cne_pmn_2012_2025.xlsx` (sheet "Programa Medicion Neta", column B "Potencia Instalada (kW)") are not usable after 2019-10: rows 2019-11 and 2019-12 repeat the 2014-11/12 values (B85 12150.04, B86 12313.42), 2020 repeats 2017 (B98 58250), 2021 and 2022 repeat 2018 (B110 and B122 94520), 2023 repeats 2017 (B134 58250), 2024 rows (A135:C146) hold the 2019 values as text, 2025 repeats 2017. The last credible value is 2019-10, B84 = 120,808.58 kW. Values from 2016-06 to 2018 are fractional, apparently interpolated.

## (c) Self-producers (autoproductores) outside the SENI

### Capacity

- PEN p.211 [printed 211], Tabla 70 "Capacidad instalada autoproductores 2018" (source printed: SIEN 2020), MW: Residencial urbano 162.57; Residencial rural 9.00; Restaurantes 79.57; Hoteles 161.35; Industrias 546.59; Falconbridge 0.00; Refidomsa 4.30; PVDC (Barrick, Quisqueya I) 225.30; Autoproductores (solar outside PMN) 9.90; Medicion Neta 93.00; Micro hidroelectricas 1.53; Biodigestores 1.97; Total 1295.09. No split by fuel for the thermal groups. PEN p.208: isolated systems (CEPM, CEB, etc.) thermal capacity 353.16 MW.
- IRENA25 (MW, flags as printed: o official, e estimate):
  - Off-grid hydropower, p.99: 2018 1.528; 2019 1.665o; 2020 1.685o; 2021 1.685e; 2022 1.860e; 2023 1.860; 2024 1.860e.
  - Biogas, p.89: 2 MW each year 2015-2021; 4 MW 2022, 2023, 2024.
  - Other solid biofuels, p.83: 31 MW each year 2017-2024.
  - Bagasse, p.81: 18 (2015-2016), 48 (2017-2024). The 48 includes San Pedro Bio-Energy 30 MW on the SENI (OC24 Tabla 36, from 2017), so non-SENI bagasse is 48 - 30 = 18 MW (inference).
  - Other off-grid renewable energy, p.102: 51.050 (2017-2021), 53.390 (2022-2024), which equals 18 bagasse + 31 other solid + 2 (later 4) biogas within rounding.
- UN (thousand kW): self-producer hydro, `un/undata_EC_13322_DR.html`: 2 (2018), 1 (2013-2017); no value after 2018. Self-producer combustible fuels, `un/undata_EC_13342_DR.html`: 1,189 (2018), 1,255 (2019), 740 (2020, flagged estimate), 705 (2021, 2022, 2023, estimate). Self-producer solar, `un/undata_EC_13362_DR.html`: 116 (2018-2020), 85 (2021), 120 (2022), 220 (2023). No per-fuel capacity (diesel, fuel oil, gas, gasoline, LPG) was found in any source.

### Generation

- UN, "Kilowatt-hours, million": Hydro autoproducer (`un/undata_EL_016HY_DR.html`) 7 (2018), 9 (2019, 2020, 2021, 2022), 10 (2023). Total autoproducer (`undata_EL_SP_DR.html`) 2,011 (2018), 2,973 (2019), 1,852 (2020), 2,398 (2021), 2,585 (2022), 1,967 (2023). From combustible fuels (`undata_EL_016C_DR.html`) 1,856 / 2,808 / 1,658 / 2,122 / 2,092 / 1,173 for 2018-2023. Solar autoproducer (`undata_EL_016S_DR.html`) 148 / 156 / 185 / 267 / 484 / 785.
- UN fuel inputs to autoproducer electricity plants (no per-fuel output is published): biogas 157 TJ (2016-2020), 160 TJ (2021-2023), all flagged estimate (`undata_BI_08812_DR.html`); vegetal waste 151 TJ (2018), 150 TJ (2019-2023) (`undata_VW_08812_DR.html`); bagasse 121 / 151 / 123 / 155 / 118 / 124 thousand t (2018-2023, `undata_BS_08812_DR.html`); fuel oil 193 / 448 / 212 / 218 / 218 / 213 thousand t (`undata_RF_08812_DR.html`); natural gas 628 / 657 / 519 / 603 / 771 TJ (2019-2023, `undata_NG_08812_DR.html`); motor gasoline 14 / 14 / 5 / 14 / 14 / 14 thousand t (2018-2023, `undata_MO_08812_DR.html`). No autoproducer series for LPG; gas oil/diesel query returned no records.
- IRENA25 production, GWh (years 2015-2023): biogas p.91: 14, 16, 16, 16, 14, 14, 14, 22, 30; other solid biofuels p.85: 122 in each of the 7 printed years (2017-2023); bagasse p.82: 96e, 96e, 234e, 323e, 328e, 287e, 320e, 304o, 322 (includes the SENI plant). No off-grid hydro generation table in IRENA25.
- SENI bagasse and biomass generation for comparison: `downloads/map_dr/CNE_DataCNE_GeneracionFuenteSENI.xlsx`, sheet Hoja1, row 13 "Bagazo" and row 14 "Biomasa" (unit not printed, magnitudes are GWh; note B22: "no incluye los Sistemas Aislados, ni la autoproduccion"): 2023 Z13 178.43 and Z14 30.22; 2024 AA13 159.66 and AA14 56.35.
- No 2024 self-producer generation found (UN ends 2023, IRENA25 production ends 2023).
- Download URL of the DataCNE file (checked 2026-11-21): `https://datacne.gob.do/api/dropbox/pdf-proxy?path=/generaci%C3%B3n%20y%20consumo%20por%20central/generaci%C3%B3n%20por%20fuente/generacionfuenteseni.xlsx` (plain GET, the endpoint the DataCNE repository page at https://datacne.gob.do/repositorio-estadistico uses for previews). A second route, `POST https://datacne.gob.do/api/dropbox/preview` with body `{"path":"/generación y consumo por central/generación por fuente/generacionfuenteseni.xlsx"}`, returns a temporary dl.dropboxusercontent.com link (expires after a few hours; Dropbox metadata: server_modified 2026-06-30T19:41:07Z, 26,029 bytes). Both downloads with curl.exe gave SHA-256 763877bf8864114a400b2b2736da88d4f4bd1237cbd3cf8c5494aa02a0a71dc4, identical to the saved `downloads/map_dr/CNE_DataCNE_GeneracionFuenteSENI.xlsx`.

### Capacity factors (generation GWh / (MW x 8.76))

| Tech | Year | Capacity (source) | Generation (source) | CF |
|---|---|---|---|---|
| Self-producer hydro | 2018 | 1.528 MW (IRENA25 p.99) | 7 GWh (UN 016HY) | 7 / (1.528 x 8.76) = 0.52 |
| Self-producer hydro | 2018 | 1.53 MW (PEN Tabla 70) | 7 GWh (UN) | 0.52 |
| Self-producer hydro | 2020 | 1.685 MW (IRENA25) | 9 GWh (UN) | 9 / 14.76 = 0.61 |
| Self-producer hydro | 2023 | 1.860 MW (IRENA25) | 10 GWh (UN) | 10 / 16.29 = 0.61 |
| Model PPDHYD | | 1.75 MW residual | 64.7 GWh (0.2328 PJ) | 64.7 / 15.33 = 4.22 |
| Biogas | 2019 | 2 MW (IRENA25 p.89) | 14 GWh (IRENA25 p.91) | 14 / 17.52 = 0.80 |
| Biogas | 2022 | 4 MW | 22 GWh | 22 / 35.04 = 0.63 |
| Biogas | 2023 | 4 MW | 30 GWh | 30 / 35.04 = 0.86 |
| Model PPDBGS | | 2.4 MW residual | 15.7 GWh (0.0565 PJ) | 15.7 / 21.02 = 0.75 |
| Other solid biofuels (non-SENI) | 2017-2023 | 31 MW (IRENA25 p.83) | 122 GWh (IRENA25 p.85) | 122 / 271.6 = 0.45 |
| Model PPDBIO (biomass) | | 9.6 MW residual | 0.21 to 0.26 PJ = 58.3 to 72.2 GWh | 0.69 to 0.86 |

IRENA rounds biogas capacity to whole MW, so the biogas CF range is wide. Conclusion for the model: the published self-producer hydro generation is 9 to 10 GWh a year (2019-2023) on 1.7 to 1.9 MW, so the PPDHYD activity limit of 64.7 GWh is about 6.5 times the published value (64.7 / 10). Biogas (about 2 to 4 MW, 14 to 30 GWh) is consistent with the model's 2.4 MW and 15.7 GWh. For biomass the published non-SENI capacity (31 MW other solid plus about 18 MW bagasse) is far above the model's 9.6 MW; the 0.21 to 0.26 PJ limit is below the 122 GWh (0.44 PJ) printed for other solid biofuels.

## What could not be found

- Per-fuel capacity and generation of fossil self-producers (diesel, fuel oil, gas, gasoline, LPG) for 2018-2024: only the 2018 PEN split by user type and the UN aggregate (combustible-fuel capacity, generation, fuel inputs). The CNE SIEN (sien.cne.gob.do) balance matrix would hold the autoproducer row by fuel but did not render (see Unreachable).
- The annex of autoproductores of the Balance Energetico Nacional: no published PDF or workbook was found for 2018-2024.
- Self-producer data for 2024 (UN and IRENA production end in 2023).

## Unreachable

- `https://sien.cne.gob.do/WebForms/Reportes/ReporteBalanceEnergetico.aspx?or=600&ss=2&v=1` (SIEN balance matrix, DevExpress page): opened in a browser, stayed on "Espere por favor" for more than 15 s, nothing to download; `ReporteInstalaciones.aspx?tp=1&oc=169,380&or=731&ss=2&v=1` same result. `ReporteBalanceCentros.aspx?oc=47` loads but only gives SENI monthly totals (1662.63 GWh, Dec 2022), `oc=33` refinery and `oc=75` charcoal. Also tried: `downloads/map_dr/sien_balance_form.html` (form only, no data), web searches for a published autoproducer annex (none found).
- `https://data.un.org/Handlers/DownloadHandler.ashx?DataFilter=crID:214&DataMartId=EDATA&Format=csv`: returned an HTML page, not a zip; used the per-series `Data.aspx?d=EDATA&f=cmID:..;trID:..;crID:214` pages instead (saved in `downloads/d2_dr/un/`).
- `https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2025/Jul/IRENA_DAT_Renewable_Energy_Statistics_2025.pdf`: HTTP 403; the file name `IRENA_DAT_RE_Statistics_2025.pdf` at the same path worked.
- OC-SENI Memoria 2024 was not re-downloaded; the archive copy (OC entry 200289, same byte size as the OC listing) was used.
