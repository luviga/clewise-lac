# Shared vehicle cost package (GEN-101 to GEN-104)

All rows are in `gen_vehicle_factors.csv`. Use national data first; use these rows only where the country has none.

## Which item for which row

| Item | Source | Use for |
| --- | --- | --- |
| `price_trajectory` | GEN-101, NREL ATB 2022 Transportation, scenario Mid | Multiplier cells of "User defined trajectory relative to BY" rows: take the ratio for the year. Ratios are relative to the powertrain's own 2024 price, so they apply when the base-year cell holds a 2024 price; state this in the derivation. |
| `reference_price` | GEN-101 (United States prices, 2020 USD, converted to 2024 USD) and GEN-104 (Dominican Republic plan, EV prices and one conventional car price) | Fallback price per vehicle. Compare in `value_2024usd`. US prices exclude Central American and Caribbean import duties and taxes. |
| `maintenance_cost` | GEN-102, ATB levelized maintenance and repair cost | FixedCost rows: use the `M US$ per Gvkm` row (2024 USD in `value_2024usd`). |
| `operational_life` | GEN-103 (15 years light duty and minibus), GEN-104 (10 years, whole fleet) | OperationalLife rows. |
| `annual_km` | GEN-104 (Dominican Republic: 7,500 cars and jeeps, 44,000 buses, 9,000 freight, 10,500 motorcycles) and GEN-103 (US light duty 19,108 km; Class 4 35,942 km) | Distance checks only (fallback). |

Class mapping (ATB class in brackets): car AUT, SED and taxi TAX (Compact), SUV (Small SUV), light freight YLF, FRELIG (Pickup), minibus MBS, MIC (Class 4 StepVan), heavy freight YTK, FREHEA (Class 8), public and tourism buses BPU, BUS, BTUR, BPR (Class 8 as a heavy-duty proxy, trajectory only; ATB has no bus, so there is no ATB bus reference price).

Powertrains: DSL diesel, GSL gasoline, NGS CNG, ELE BEV (BEV300 for light duty), HYD fuel cell, HG power-split hybrid, PHG PHEV50, HD diesel parallel hybrid and PHD diesel series PHEV (heavy duty). Proxies, stated in each row's derivation: LPG and Flex_Fuel take the gasoline vehicle (light duty) or diesel (heavy duty); light-duty HD and PHD take the gasoline hybrid and PHEV; heavy-duty GSL and NGS take diesel.

## Caveats

- ATB publishes 2020 (light duty) or 2021 (heavy duty), then every 5 years to 2050. The package interpolates linearly to every year from 2024 to 2050; no hold-flat is needed.
- Combustion-vehicle ratios stay close to 1 (car diesel 0.990 in 2030); BEV ratios fall (car 0.853 in 2030, 0.666 in 2050; heavy duty 0.799 and 0.595).
- No motorcycle trajectory or maintenance value exists in the family. Motorcycle rows need national data or an ASSUMPTION.
- The ATB Class 6 and Class 8 life is 5 years for the first owner only, so it is not used as a lifetime. Bus life (FTA, 12 years) is listed as manual.
- Maintenance is levelized over the vehicle life with discounting, US conditions.

## Origin of 11,525 (TRAUTDSL) and 10,504.4963 (TRAUTGSL)

Not confirmed in any external document. What was checked:
- The national electric mobility plan of the Dominican Republic (GEN-104) is the source of several sibling values in the Dominican Republic and Honduras models: electric car 30,000 US$, electric bus 360,000 (TRBTURELE), electric cargo vehicle 120,000 (TRYTKELE), electric motorcycle 3,000 (TRMOTELE), and the 7,500 km per year for cars. The electric-car multiplier of 0.6667 in 2030 brings 30,000 to 20,000, the plan's average new conventional vehicle price (USD 20,001, page 72). The plan does not contain 11,525 or 10,504.
- World Bank, Dominican Republic CCDR Annex 4 (Transport Deep Dive): no vehicle prices.
- Godinez-Zamora et al. (2020), Energy Strategy Reviews (the paper the Read the Docs pages cite): no vehicle price table. The DOI printed on the Read the Docs pages (10.1016/j.esr.2020.100545) is not the paper's DOI (10.1016/j.esr.2020.100573).
- The Costa Rica model documentation (lead only) states that vehicle capital costs came from the Costa Rica Ministry of Finance (Hacienda) vehicle value database. Its diesel and gasoline light-duty capital costs have a ratio of 1.099, close to 11,525 / 10,504.4963 = 1.097, which suggests the same lineage. The Hacienda database version behind the number was not identified, so country agents should treat 11,525 and 10,504.4963 as unsourced and use national data, GEN-104 or GEN-101.
- Jamaica's lead (IDB 2022, Strategic Framework for Electric Mobility) has no public PDF.
