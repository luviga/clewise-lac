# Dominican Republic (DR): local fuel prices 2024, notes

Job LAC_LOCAL_PRICES 20261109T085226Z, country sub-task DR. All values are in `prices_DR.csv` (26 rows), `history_DR.csv` (27 rows), `constants_DR.csv` (3 rows), `sources_DR.csv` (152 documents), `search_log_DR.csv` (174 rows; every DR lead is logged for COA, COK, CRU, NGS and FOI, the rows that carried ASSUMPTION candidates or open questions), `manual_DR.csv` (12 items) and `calorific_DR.csv` (1 row). Weekly working values are in `dr_weekly_ppi_2024.csv` and `dr_weekly_ngs_ppi_2024.csv`.

## Summary

Closed with a published local or customs value (no ASSUMPTION candidate is left for DR):

| Row | Price point | USD/GJ | Evidence class | Source |
|---|---|---|---|---|
| COA DIST_COA | import CIF | 3.9747 | international customs (Comtrade) | DR imports HS 270112, 102.55 USD/t |
| COA DIST_COA | generator delivered | 3.8164 | local regulator or operator | OC-SENI Memoria 2024, Figura 45, 5,865.17 DOP/t (digitised chart) |
| COK DIST_COK | import CIF | 2.6222 | international customs (Comtrade) | DR imports HS 271311, 85.22 USD/t |
| CRU DIST_CRU | import CIF | 15.2993 | international customs (Comtrade) | DR imports HS 2709, 647.16 USD/t |
| NGS DIST_NGS | wholesale import parity | 8.6663 | local regulator or operator | MICM weekly PPI, mean 9.1435 USD/MMBTU (50 weeks) |
| NGS DIST_NGS | generator delivered | 8.1776 | local regulator or operator | OC-SENI Memoria 2024, Figura 46, 513.93 DOP/MMBTU (digitised chart) |
| NGS DIST_NGS | final consumer pre-tax | 17.1610 | local regulator or operator | MICM, vehicle gas station price less ad valorem and GAL |
| NGS DIST_NGS | import CIF | 8.9358 (net) | international customs (Comtrade) | DR imports HS 271111, 428.92 USD/t |
| FOI DIST_FOI | generator delivered | 13.9293 | local regulator or operator | MICM Fuel Oil EGP-C, PPI 113.55 + 1.35 + 5.68 DOP/gal |
| FOI DIST_FOI | wholesale import parity | 13.3521 | local regulator or operator | MICM Fuel Oil No. 6 PPI 115.58 DOP/gal |
| FOI DIST_FOI | final consumer pre-tax | 14.1861 | local regulator or operator | MICM Fuel Oil No. 6 PPI + 1.54 + 5.68 |
| FOI DIST_FOI (FO 1%S grade) | generator delivered / import parity | 15.5268 / 14.9497 | local regulator or operator | MICM FO6 1%S rows |
| DSL DIST_DSL | generator delivered | 19.2036 | local regulator or operator | MICM Gasoil Regular EGP-C, PPI 150.88 + 5.24 + 5.68 |
| DSL DIST_DSL | wholesale import parity | 17.9075 | local regulator or operator | MICM EGP-C PPI 150.88 DOP/gal |
| DSL DIST_DSL | final consumer pre-tax | 20.7229 | local regulator or operator | MICM public Gasoil Regular (frozen retail price) |
| GSL DIST_GSL | wholesale import parity (administrative) | 19.4897 | local regulator or operator | MICM Gasolina Regular PPI 144.06 DOP/gal |
| GSL DIST_GSL | final consumer pre-tax | 25.6821 | local regulator or operator | PPI + distributor, retailer and transport margins |
| GSL DIST_GSL | import CIF (market-tracking) | 19.6137 | built from published components | US export FOB to DR 98.02 USD/bbl x DR CIF/FOB ratio 1.0429 |
| LPG DIST_LPG | wholesale import parity (administrative) | 15.2531 | local regulator or operator | MICM GLP PPI 85.24 DOP/gal |
| LPG DIST_LPG | final consumer pre-tax | 21.1431 | local regulator or operator | PPI + margins |
| LPG DIST_LPG | import CIF (market-tracking) | 11.0415 | international customs (Comtrade) | DR imports HS 271112 + 271113, 522.26 USD/t |
| KER DIST_KER | import parity / final pre-tax | 19.8890 / 23.6113 | local regulator or operator | MICM Kerosene |
| JET DIST_KER | import parity / final pre-tax | 20.0147 / 22.6469 | local regulator or operator | MICM Avtur |

Exchange rate DR_FX_2024 = 59.5665 DOP/USD, BCRD 2024 annual average of the daily reference selling rate (re-downloaded, sheet PromAnual; buying rate 59.2507).

MICM weekly series: 52 weeks (6 Jan to 28 Dec 2024) for the unfrozen rows (EGP-C gasoil, avtur, fuel oil rows) and 51 weeks for the frozen rows (gasolines, public gasoil, kerosene, LPG; the week of 14 to 20 Dec has no resolution). Sources by week: 28 digital avisos (typed values, all sums checked), 23 scanned resolutions read from rendered page images (`dr_resolution_image_reads.csv`), and for unfrozen rows a derivation from the MICM quarterly price history checked against the OCR text of each resolution.

Open question, both sides in numbers (USD/GJ):

- Gasoline. MICM administrative PPI 19.49 (144.06 DOP/gal; retail price frozen at 272.50). Market-tracking import CIF 19.61 (US-reported exports to DR, 98.02 USD/bbl FOB, 18.81 USD/GJ, times the DR CIF/FOB ratio for HS 271012). On the annual mean the two sides differ by less than 1 percent, although the MICM weekly PPI hardly moved while the market moved.
- LPG. MICM administrative PPI 15.25 (85.24 DOP/gal, 1.431 USD/gal; 14.80 with the UN 489 gal/t factor). Market-tracking import CIF 11.04 (Comtrade DR, propane and butane, 522.26 USD/t; propane alone 1.007 USD/gal CIF from the reported litres). The MICM parity is about 38 percent above the customs import cost. The PPI is a residual of the frozen official price: on 25 May 2024 margins rose by 3.50 DOP/gal and PPI plus ad valorem fell by exactly 3.50.

Still open for DR: no row is open. Petroleum coke has only the Comtrade value (no local publisher found). Coal and natural gas generator-delivered values come from charts, not tables (manual list item 1 and 2 would replace them with tabulated values).

## Judgement calls and reasons

1. Diesel to generators and diesel import parity use the MICM Gasoil Regular EGP-C row, as in the earlier job. Its PPI follows the market (133.00 to 176.83 DOP/gal), while the public gasoil PPI is administrative under the price freeze. The public gasoil row is kept as the final consumer pre-tax point and flagged.
2. Generator delivered = PPI + distributor margin + transport commission (EGP-C rows). The EGP-T rows differ only by excluding the 5.68 transport commission. The tables add Ley 112-00 and the 16 percent ad valorem tax to these rows; whether generators are exempt was not checked, and the values here are pre-tax.
3. Weekly means are simple means over the weeks starting 6 Jan to 28 Dec 2024 (the last week runs to 3 Jan 2025), not day-weighted. The 30 Dec 2023 week was left out because its resolution is a 2023 document.
4. For weeks without a digital aviso, the unfrozen PPIs were derived as (price paid by public in the MICM quarterly xlsx minus Ley 112-00, distributor, retailer and transport) / (1 + ad valorem rate). The derivation reproduces the aviso PPI to 0.01 in every aviso week except 20 to 26 Jan 2024 (the xlsx repeats the previous week; the aviso value is used) and 3 to 9 Aug (0.02 rounding). A derived value is accepted when the same figure appears in the OCR text of that week's resolution or in my reading of the page image; one week per product (14 to 20 Dec, no resolution) rests on the xlsx alone.
5. Frozen rows (gasolines, public gasoil, kerosene, LPG) in scanned weeks use values read from the page images. An automatic OCR pattern match was rejected because it produced false matches in 4 weeks. Two of my own image readings were corrected after the arithmetic check against the printed ad valorem and official price (noted in `dr_resolution_image_reads.csv`).
6. Public margins for gasolines, public gasoil and LPG changed from the week of 25 May 2024 (gasoline 15.09/22.57 to 16.59/25.07; gasoil 12.78/19.25 to 14.28/21.75; LPG 10.21/14.90 to 11.71/16.90); the margin means follow that date.
7. LPG from MICM is converted with MICM's own published gallons per tonne (DR_LPG_GAL_PER_T_MICM 504.1454, mean of 28 weekly factors) rather than the UN 489, following the brief's preference for source-published factors. The UN-based figure is given in the notes of that row.
8. Natural gas MICM PPI is the USD/MMBTU figure in Parrafo I of each resolution (mean 9.1435). It is fixed in pesos (592.25 DOP/MMBTU to 14 Jun, 504.97 from 15 Jun), so it is administrative too. One OCR value (10.1761) was read as 10.176 because 592.25 / 58.20 = 10.176. The earlier job used the importer price to the wholesaler (716.72 DOP/MMBTU), which includes the 16 percent ad valorem, GAL, SICOEX and MDGNV; this job records the pre-tax PPI.
9. Natural gas per-MMBTU values are kept on their published basis (not stated, gross by convention) and not converted. The Comtrade LNG value is per tonne and converted with IPCC NCV, so it is on a net basis.
10. Coal and natural gas generator-delivered values were digitised from the vector charts of the OC-SENI Memoria 2024 (Figures 45 and 46: average costs declared by the generating agents). Each series is one polyline with one vertex per month; the y axis was fitted to all tick labels (residual 0.03 pt). The month alignment was checked against the x-axis year labels (coal: 282 points, Jul 2001 to Dec 2024; gas: 262 points, Mar 2003 to Dec 2024). The coal figure title says RD$/LB but the axis says RD$/TM; per tonne is the only reading that fits the level.
11. Fuel oil from the same OC chart (Figure 44) was not recorded: the series are drawn as filled outlines and the month alignment is uncertain. The rough 2024 level (about 115 DOP/gal for No. 6) is close to the MICM EGP-C delivered value (120.58 DOP/gal pre-tax).
12. Gasoline market-tracking cost: the DR Comtrade record for HS 271012 has a value but no quantity, so the unit value comes from the US-reported exports to DR in barrels (altQtyUnitCode 19). US petroleum weights in Comtrade are volume-based (about 1 kg per litre) and were not used. DR freight and insurance enter through the DR CIF/FOB ratio for the same code (1.0429).
13. Crude: the DR-reported CIF per tonne is used for USD/GJ. The per-barrel figure depends on density: 88.41 USD/bbl at UN 7.32 bbl/t, 84.71 at the 7.64 bbl/t implied by the DR 2025 record. US-reported exports of crude to DR were 75.75 USD/bbl FOB for 8.99 million barrels, which does not reconcile with the DR CIF value (802 million USD); the cause was not found.
14. History (`history_DR.csv`) uses only DR-reported Comtrade unit values 2018 to 2025, the one consistent annual series found. 2018 and 2020 have no CIF value, 2021 coal and crude have no weight, and several weights are flagged as estimated by UN Comtrade (2019, 2022 and 2023 coal; 2022 petroleum coke; 2023 crude). The 2023 coal value (7.15 USD/GJ) looks high relative to its neighbours and has an estimated weight. MICM weekly series were not extended to 2018 to 2025 because the PPI is only in weekly resolutions.

## Values that could not be sourced externally

- No published FOB, freight, insurance or terminal split of the MICM import parity; all component columns except the margins are empty for MICM rows.
- No published calorific value or density from a Dominican source for coal, petroleum coke, fuel oil, diesel or gasoline; IPCC NCV and UN gallons per tonne (shared constants) are used.
- No net or gross statement in the national balance page; only the natural gas factor (0.83 toe per thousand Nm3) is published there.
- Petroleum coke delivered to cement plants: no local price found.
- Plant-level generator fuel prices in a table: not retrievable (OC weekly programmes, manual list).

## Differences above 10 percent from the earlier job (`adders_2024.csv`)

| Row | Earlier (USD/GJ) | This job (USD/GJ) | Change | Likely cause |
|---|---|---|---|---|
| NGS observed import cost | 11.404 | 8.666 (PPI); 8.178 (generator delivered); 8.936 net (Comtrade CIF) | -24% | earlier value was the importer selling price including ad valorem 16%, GAL, SICOEX and MDGNV |
| COA pre-tax (ASSUMPTION) | 5.211 | 3.975 (CIF); 3.816 (generator delivered) | -24% | earlier value was a World Bank South African benchmark plus an assumed adder |
| COK pre-tax (ASSUMPTION) | 3.606 | 2.622 (CIF) | -27% | earlier value was the EIA US delivered petcoke proxy plus an assumed adder |
| GSL pre-tax | 21.66 | 25.682 (final consumer pre-tax) | +19% | earlier pre-tax included only the distributor margin; this row adds retailer margin and transport commission |
| LPG pre-tax | 16.719 | 21.143 (final consumer pre-tax) | +26% | same margin scope difference; also the MICM gal/t factor |
| KER pre-tax | 21.109 | 23.611 (final consumer pre-tax) | +12% | same margin scope difference |
| LPG observed import cost | 14.783 | 11.042 (Comtrade CIF) | -25% | different price point: customs import cost versus administrative MICM parity |

Import parity values for DSL, GSL, LPG (MICM), KER, JET and FOI are within 4 percent of the earlier values; crude is +7 percent (15.30 against 14.285).

## Known-limitation candidates

- MICM gasoline, public gasoil, kerosene and LPG parities in 2024 are residuals of frozen retail prices, not market values (MICM resolutions 2024).
- MICM natural gas PPI is fixed in pesos and changes only twice a year (MICM natural gas resolutions 2024).
- OC-SENI coal and gas generator costs are read from charts, with an unreconciled unit label in the coal figure (OC-SENI Memoria Anual 2024, Figures 45 and 46).
- DR Comtrade 2024 has no quantity for HS 271012 and 271019 (UN Comtrade, reporter 214).
- Crude import value reported by DR does not reconcile with US-reported exports to DR (UN Comtrade 2709, reporters 214 and 842).
- The 2024 BCRD balance-of-payments coal import value (260.3 million USD) is 13 percent below the Comtrade CIF value (298.0 million USD) (BCRD Informe de la Economia Dominicana 2024, Anexo 6).

## Left unchecked

- Whether generators pay Ley 112-00 and the ad valorem tax on EGP-C fuel (tax exemption regime).
- The Decree 625-11 formula for the LPG parity and the PPI marker for liquids (not stated in the MICM documents opened).
- Monthly MEM bulletins for Jan, Mar, May to Aug and Oct 2024 were listed but not opened, since they hold the same Platts references as the annual bulletin.
- MICM 2023 resolution for the week 30 Dec 2023 to 5 Jan 2024.
- Earlier-year MICM weekly series (history) and OC-SENI fuel oil chart values.

## Incidents

- The coordinator changed the download rule during the run (no user-agent spoofing). No request in this sub-task used a spoofed user agent; every 403 was logged and listed in `manual_DR.csv`.
- The MICM open-data workbook 2010-2025 again returned HTTP 403; a 2010-2026 file linked from datos.gob.do opened but holds retail prices only.
- One heredoc failed in the shell; the script was written with the file tool instead. A text replacement in `dr_build_outputs.py` did not apply on the first try and was redone.
- Downloads include placeholder pages saved by failed probes (HTTP 403/404 html); they are not cited.
