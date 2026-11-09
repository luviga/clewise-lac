# Jamaica (JAM) notes, job LAC_LOCAL_PRICES 20261109T085226Z

## Summary

Closed with local or customs evidence (2024):

- Natural gas (DIST_NGS): OUR now gives all 12 months of 2024. The plant gate price of gas to JPS averages 13.54 USD/MMBtu (12.833 USD/GJ, basis not stated, kept as gross). IPP gas plants paid less in June and July: SJPC and NFE 94 MW 8.66, Hill Run 10.48 USD/MMBtu. Comtrade LNG import CIF is 668.31 USD/t (13.923 USD/GJ net). MSET reports gas imports of 57.34 USD per BOE but publishes no BOE factor.
- Fuel oil (DIST_FOI): HFO to JPS averages 12.97 USD/MMBtu over 12 months (12.293 USD/GJ), also published as 81.87 USD/bbl. The IPP plants average 13.478 USD/MMBtu for June and July. MSET gives the 2024 Bunker C import value of the alumina companies: 80.95 USD/bbl (13.262 USD/GJ net).
- Diesel (DIST_DSL): ADO to JPS averages 27.088 USD/MMBtu over 12 months, including SCT. Taking out the SCT rate OUR states gives 21.047 USD/MMBtu (19.948 USD/GJ). The Petrojam refinery billing prices published by MSET are ADO 171.05 and ULSD 178.28 J$/L, and they include SCT. The Comtrade HS 271019 value mixes products.
- Gasoline (DIST_GSL): Comtrade HS 271012 import CIF is 759.29 USD/t (17.140 USD/GJ). Billing prices are E10-87 168.73 and E10-90 176.49 J$/L, both including SCT.
- LPG (DIST_LPG): Comtrade propane plus butane CIF is 426.59 USD/t (9.019 USD/GJ). No published margin was found.
- Coal (DIST_COA): Comtrade HS 2701 import CIF is 148.28 USD/t (5.747 USD/GJ), but the weight is estimated. The USA mirror record gives 80.00 USD/t FOB.
- Petroleum coke (DIST_COK): Comtrade HS 2713 import CIF is 100.32 USD/t (3.087 USD/GJ). MSET reports the cement company's petcoke imports at 23.72 USD/bbl, with no conversion to tonnes or energy.

Still open:

- Kerosene (DIST_KER) and jet (DIST_JET) are ASSUMPTION candidates at 18.0 USD/GJ, range 16.3 to 19.9.
- No pre-tax final consumer price was derived for any liquid fuel. The 2024 SCT schedule (specific plus ad valorem) and the Petrojam ex-refinery prices could not be retrieved.
- The LPG margin and all retail margins remain open.
- The calorific basis is not stated by the national balance, and the OLADE methodology returned HTTP 403.

Exchange rate: JAM_FX_2024 is 157.22 JMD/USD, the Bank of Jamaica annual weighted average selling rate, re-downloaded this session. This confirms the earlier value.

## Judgement calls and reasons

1. Generator prices use the OUR Annual Report 2024-2025 (Tables 24 and 25), not the June and July investigation. The annual report is the only 12-month OUR series. Its PDF is image only, so the values were read from page images at 3x render. The HFO and NG monthly means reproduce the published annual means (12.974 against 12.97, and 13.541 against 13.54), which checks the transcription.
2. 2024 ADO to JPS: Table 24 gives 25.85 USD/MMBtu and 158 USD/bbl. That equals the December monthly value, and the implied heat content is inconsistent with earlier years (6.11 against 5.82 MMBtu/bbl). The 12-month mean of Table 25 (27.088) is used instead. The history file keeps the value as published.
3. June 2024 NG to JPS is 12.80 in the annual report and 13.28 in the investigation report. The annual report value is kept so that the series stays consistent.
4. The ex-SCT diesel row subtracts only the specific SCT rate OUR states (37.4845 J$/L; 4.5611 in July). OUR says JPS paid this rate in 2024. The WTO TPR says diesel for public electricity is exempt by end use, and that the petroleum SCT also has an ad valorem part. Both sides are recorded. The heat content used (5.8147 MMBtu/bbl) is implied by OUR's own 2023 pair of values.
5. Refinery billing prices are recorded with price point `wholesale import parity` because no other listed point fits. Their tax treatment says they include SCT, and their notes say NOT pre-tax. Ex-refinery (pre-tax) prices appear only up to 2021, and they are in the history file.
6. Newspaper reports of the weekly Petrojam prices (Jamaica Observer, Our Today) were not used. They are secondary reports of a blocked primary source, and they also include taxes.
7. Kerosene and jet are not split out of HS 271019. Bunker C and lubricants share the code, so its unit value is a lower bound only. That bound is used in the ASSUMPTION check.
8. Coal: the weight in Jamaica's Comtrade record is a Comtrade estimate (20,806 t), and it is close to MSET's 2024 coal consumption (19 kt). The USA mirror weight is 37,884 t. Both rows are kept. The factor is IPCC other bituminous; the subbituminous alternative is in the notes.
9. Per-MMBtu gas prices are kept on their published (taken as gross) basis, as the coordinator directed. The Comtrade LNG value per tonne is converted with the IPCC net factor, and its gross equivalent is in the derivation.
10. Comtrade petcoke history keeps only years with fuel-grade volumes (2020, 2022 to 2025). Earlier years hold less than 1 kt of high-value coke.

## Values that could not be sourced externally

- 2024 ex-refinery (pre-tax) prices for every product (Petrojam, HTTP 403).
- 2024 SCT rates for gasoline, kerosene, LPG and jet, and the ad valorem part for all products.
- Importer, terminal, wholesale and retail margins for every product, including LPG.
- Kerosene and jet fuel 2024 prices of any kind.
- Freight and insurance components for any fuel.
- Net or gross basis of the OUR per-MMBtu prices (not stated). The HFO pair 81.87 USD/bbl and 12.97 USD/MMBtu implies 6.31 MMBtu/bbl, and 2019 to 2023 imply 6.286, which points to a gross basis.
- Energy content of MSET barrels for petcoke and of MSET BOE for natural gas.

## Differences above 10 percent from adders_2024.csv

- NGS: 12.833 against 9.847 (+30%). The earlier value averaged June and July across JPS and the IPP plants, including SJPC at 8.59. The new value is the 12-month price to JPS. The IPP rows (8.21 and 9.93 USD/GJ) are recorded separately.
- GSL: Comtrade CIF 17.140 against the earlier pre-tax 21.636 (-21%). The new value is an import cost without margins. The billing price (32.74, including SCT) is not comparable.
- DSL: the ex-SCT delivered value of 19.948 matches the earlier 19.925. The SCT-inclusive OUR price (25.675, +29%) differs because of tax.
- LPG: the CIF of 9.019 matches the earlier 9.037. Against the earlier pre-tax 10.393 it is -13%, because no margin is published.
- KER: 18.0 against 20.844 (-14%). JET: 18.0 against 22.092 (-19%). The ASSUMPTION value sits inside the range set by Jamaican data, not on a USGC benchmark plus margins from other countries.
- COA: 5.747 against 5.211 (+10.3%). The earlier value was a benchmark plus an assumed adder.
- COK: 3.087 against 3.606 (-14%). The earlier value was a US delivered proxy plus an adder.

## Known-limitation candidates

- EXTT_CRU (crude to the Petrojam refinery) has no coverage row. MSET Table 1 gives 2024 crude imports of 6,320,587 bbl at US$511,576,014 (80.94 USD/bbl), and Comtrade 2709 gives 586.37 USD/t.
- DIST_OPE also outputs E1COK to industry, and it would carry the same petcoke price question.
- The 2025 Comtrade LNG record gives 1,378.6 USD/t, with half the usual weight, which looks like a reporting error (history file).
- Comtrade classifies Jamaica's 2022 to 2025 petcoke imports as calcined (271312), but at fuel-grade unit values.
- OUR prices are for JPS plants. IPP plants have different contract prices (gas 8.6 to 10.5, HFO 11.5 to 15.9 USD/MMBtu in June and July), and the model's single power plant per fuel cannot show this.

## Left unchecked

- The Petrojam weekly price workbook for 2019 (MSET, `Petrojam-weekly-prices-2019.xlsx`) was downloaded but not parsed. It is history only.
- The PIOJ Economic and Social Survey 2024 energy chapter was not found online.
- Tax Administration Jamaica pages for SCT rates were not visited directly; only web searches were run.
- US Census 10-digit exports to Jamaica, which would split jet, kerosene and diesel from the US side, were not queried.

## Incidents

- The Comtrade preview returned HTTP 429 (rate limit) once. It was retried after 3 seconds, as the response instructs. A monthly query returned HTTP 400 (only one period allowed per preview query).
- Petrojam (HTTP 403), JPS (Incapsula challenge) and OLADE library (HTTP 403) refused automated requests. Each was tried once and is on the manual list. The MSET media API returned 401, and pcj.com does not resolve.
