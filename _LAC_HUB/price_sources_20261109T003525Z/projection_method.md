# Projection method for benchmark prices, 2026 to 2050 (Jamaica to 2055)

All values below trace to `history_usd_per_gj.csv`, `history_ratios.csv`, `projections.csv` and `projections_usd_per_gj.csv` in this folder.

## Driver source

- Publisher: U.S. Energy Information Administration (EIA).
- Edition: Annual Energy Outlook 2025 (AEO2025), released 15 April 2025.
- Cases: Reference (`ref2025`) for REF, High Oil Price (`highprice`) for HIGH, Low Oil Price (`lowprice`) for LOW.
- Tables:
  - Table 12, Brent spot, rows `PPP000:ba_WorldOilPrice` (2024 USD/bbl) and `PPP000:nom_WorldOilPric` (nominal USD/bbl).
  - Table 13, Henry Hub spot, rows `NGS000:ia_HenryHub` (2024 USD/MMBtu) and `NGS000:nom_HenryHub` (nominal).
  - Table 15, US coal exports, free alongside ship at the US port of exit, rows `CSD000:ja_Exports` (2024 USD/short ton) and `CSD000:nom_Exports` (nominal).
- Years: 2024 to 2050.
- Basis: AEO publishes both real (2024 dollars) and nominal series. The real 2024-dollar series is the one proposed, because the models' other costs are in constant dollars; Luis decides.
- AEO2026 (released 8 April 2026) is newer but has no High or Low Oil Price case. Its side cases are oil and gas supply, macroeconomic growth, zero-carbon technology cost, electricity and transportation. AEO2025 is the latest edition with all three oil price cases.

Driver values in 2024 USD per GJ (Brent: 7.32 bbl/t over 42.3 GJ/t; Henry Hub: gross basis, 1.055056 GJ/MMBtu):

| Year | Brent REF | Brent HIGH | Brent LOW | Henry Hub REF | HH HIGH | HH LOW |
|---|---|---|---|---|---|---|
| 2026 | 14.09 | 21.44 | 6.67 | 2.59 | 2.53 | 2.81 |
| 2030 | 13.81 | 21.50 | 7.15 | 2.92 | 2.69 | 3.52 |
| 2040 | 14.65 | 25.08 | 7.77 | 4.05 | 4.41 | 4.68 |
| 2050 | 15.83 | 27.19 | 8.32 | 4.55 | 5.14 | 4.29 |

In AEO2025 the oil price cases move Brent by about +72% (HIGH) and -47% (LOW) in 2050 against REF. Henry Hub and US coal export prices move little and not always in the same direction, because the cases are built on world oil supply and demand assumptions. So HIGH and LOW are mainly oil-price shocks, which fits the paper's question.

Short-term alternative: the World Bank Commodity Markets Outlook, October 2026, forecasts nominal Brent at 91 (2026), 79 (2027) and 70 (2028) USD/bbl, Henry Hub at 3.5, 3.7 and 3.9 USD/MMBtu, and Australian coal at 135, 130 and 125 USD/t (`projections.csv`, case `WB_baseline`). It has a single case only.

## Rules by fuel

The ratio method takes the mean of the annual product-to-driver ratio, in USD/GJ, over the history years shown. Ratios are kept constant over the projection. The adder from Step 4 is added on top and kept the same in all three cases.

| Fuel | Benchmark | Driver | Rule | Ratio (period) | Spread of the annual ratio (std) |
|---|---|---|---|---|---|
| Crude oil | Brent | Brent | equal to driver | 1.000 | 0 |
| Gasoline | USGC conventional regular | Brent | Brent x ratio | 1.310 (2018-2025) | 0.068 |
| Diesel | USGC ULSD | Brent | Brent x ratio | 1.249 (2018-2025) | 0.099 |
| Jet fuel | USGC jet | Brent | Brent x ratio | 1.260 (2018-2025) | 0.113 |
| Kerosene | USGC jet (proxy) | Brent | Brent x jet ratio x 44.1/43.8 (same USD/gal price on the kerosene NCV) | 1.269 (2018-2025) | 0.113 |
| LPG | Mont Belvieu propane | Brent | Brent x ratio | 0.648 (2018-2025) | 0.123 |
| Fuel oil | Brent x 0.814 (proxy) | Brent | Brent x ratio | 0.814 (ARESEP 2024 FOB bunker over 2024 Brent; one year) | n/a (one year); EIA resale alternative 0.946 (2018-2021), std 0.103 |
| Aviation gasoline | PADD 3 avgas resale (proxy) | USGC gasoline | gasoline x ratio | 1.579 (2018-2021, full years only; series ends March 2022) | 0.222 |
| Natural gas (LNG) | Henry Hub | Henry Hub | HH plus the Step 4 LNG adder (liquefaction spread plus shipping plus regasification) | n/a | n/a |
| Coal | World Bank South African | AEO US coal export FAS price | 2024 benchmark x (AEO coal export price in year / AEO 2024 value), same case | index | n/a |
| Petroleum coke | EIA US delivered petcoke (proxy) | coal benchmark | coal x ratio | 0.638 (2018-2025) | 0.106 |

Notes on the rules:

- Product ratios move with the period chosen. Over 2021-2025 instead of 2018-2025: gasoline 1.354, diesel 1.291, jet 1.299, LPG 0.656 (`history_ratios.csv`). The 2018-2025 mean is proposed because it covers a full cycle (pre-2020, the 2020 low, the 2022 spike).
- LNG: a ratio to Henry Hub is not proposed. The FOB-to-HH ratio for US cargoes to the Dominican Republic ranged from 1.35 to 4.12 in 2018-2025, because the liquefaction charge is largely fixed per MMBtu. A fixed adder in USD/GJ follows the contract structure better.
- Coal: AEO is the only retrievable source found with three cases to 2050 for coal. It describes US exports, not Colombian or South African coal. The real index barely moves (2024 = 166.7, 2050 REF = 165.6 2024 USD/short ton), so REF coal is close to flat in real terms.
- Bridging: the history runs to 2025 (12 months observed). AEO2025 values start in 2026. 2025 observed Brent averaged 69.1 USD/bbl while AEO2025 REF had 72.1 for 2025. From January to October 2026 observed Brent averaged 96.3 USD/bbl (`monthly_benchmarks.csv`), above AEO REF 2026 (81.45 in 2024 dollars) and close to the HIGH case. How to treat 2026 is a decision for Luis (see REPORT).
- Jamaica 2051 to 2055: AEO stops in 2050. The rule that changes least is to hold 2050 real values flat to 2055.
