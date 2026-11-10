# REPORT LAC_COST_SRC_CR 20261110T025401Z

Costa Rica energy model: sourced cost proposals for power plants and fuel supply rows. No model file changed.

- Pull request: luviga/clewise-lac#7 (draft), https://github.com/luviga/clewise-lac/pull/7
- Branch: `job/cost-src-cr`, from `2ddd560`
- Commit: ca0c5eb "LAC_COST_SRC_CR: sourced cost proposals for Costa Rica" on top of 2ddd560, followed by one report-only commit "LAC_COST_SRC_CR: report pull request number" (see GAPS, incidents)

## Gates

- Gate 1 read-only: PASS. 6 files hashed, 6 equal
- Gate 2 diff scope: PASS. 38 files changed, 0 outside the job folder []
- Gate 3 tracked types: PASS. 38 tracked files; 0 with other extensions; 0 under downloads/
- Gate 4 sourcing: PASS. 1560 proposal rows not ASSUMPTION, 0 with a missing source id; 40 sources, 0 with problems []
- Gate 5 ASSUMPTION rows: PASS. 150 ASSUMPTION rows for ['IMPNGS', 'PWRDSL', 'PWRFOI']; without leads []; sentence problems []
- Gate 6 coverage: PASS. 10 plants x 3 parameters x 30 years and 9 supply rows x 3 scenarios x 30 years checked; gaps []
- Gate 7 hygiene: PASS. em dash files []; machine paths []; git diff --check output 0 chars; trailer lines False

Counts: `proposals.csv` has 1710 rows:
- 810 fuel rows: 9 supply rows x 3 scenarios x 30 years;
- 900 plant rows: 10 plants x 3 parameters x 30 years.

By change class: replace 1020, keep 450, fill_empty 210, upgrade 30.

By basis class: projected 600, replace 420, matched 390, ASSUMPTION 150, history from ratio 72, observed 48, matched, newer edition 30.

## Fuel supply rows

Values in USD/GJ (= MUSD/PJ), net calorific basis, real 2024 USD. r cases:
- A: the chosen point has history;
- B: wholesale import parity, with r from the import CIF history times the 2024 ratio to CIF;
- C: no history, so the 2024 ratio alone.

The step at the join is STEPS 2026 minus 2025 (2025 = history from the observed 2025 benchmark).

| Row | Chosen point | 2024 value | Current 2024 | r (case) | STEPS 2030 | STEPS 2050 | CPS 2050 | NZE 2050 | Step at join 2025 to 2026 |
|---|---|---|---|---|---|---|---|---|---|
| IMPAVG | wholesale import parity | 43.102 | 34.703 | 3.0772 (B) | 43.174 | 41.250 | 57.533 | 13.569 | +7.103 (+19.8%) |
| IMPCOA | import CIF | 21.080 | 4.739 | 8.9288 (A) | 31.378 | 22.160 | 27.532 | 13.095 | +5.666 (+19.0%) |
| IMPCOK | import CIF | 3.128 | empty | 0.2806 (A) | 3.937 | 3.762 | 5.246 | 1.237 | +1.064 (+37.3%) |
| IMPFOI | wholesale import parity | 15.458 | 9.681 | 1.0757 (B) | 15.092 | 14.419 | 20.111 | 4.743 | +2.483 (+19.8%) |
| IMPKJF | wholesale import parity | 22.690 | 21.959 | 1.7477 (B) | 24.520 | 23.427 | 32.675 | 7.706 | +4.034 (+19.8%) |
| IMPLPG | wholesale import parity | 13.694 | 8.805 | 0.9899 (B) | 13.888 | 13.269 | 18.507 | 4.365 | +2.285 (+19.8%) |
| IMPNGS | import CIF | 8.626 | empty | 3.7399 (C) | 12.261 | 18.035 | 19.604 | 8.626 | -3.671 (-27.2%) |
| IMPPURDSL | wholesale import parity | 19.966 | 12.615 | 1.5286 (B) | 21.446 | 20.490 | 28.578 | 6.740 | +3.528 (+19.8%) |
| IMPPURGSL | wholesale import parity | 20.266 | 13.933 | 1.5056 (B) | 21.124 | 20.182 | 28.149 | 6.639 | +3.475 (+19.8%) |

Benchmarks:
- Oil products and petroleum coke: EIA Brent (RBRTE) with the WEO 2025 IEA crude oil price.
- `IMPNGS`: Henry Hub with the WEO United States gas price.
- `IMPCOA`: World Bank South African coal with the WEO European Union steam coal price.

WEO 2025 fuel price table: Table 2.3, PDF page 109, USD (MER, 2024).

## Power plants (2024)

CapitalCost in USD/kW, FixedCost in USD/kW-yr, VariableCost in USD/GJ. These are 2024 column values, on the workbook basis of 2022 USD.

| Technology | CapitalCost current to proposed | FixedCost current to proposed | VariableCost current to proposed | P2 class (Cap / Fix / Var) | Main source |
|---|---|---|---|---|---|
| PP_SPV_DG | 2392.10 to 2600.58 | 20.00 to 29.53 | empty to empty | replace / replace / matched | NREL ATB 2024 ResPV |
| PWRBMS | 2157.02 to 3024.61 | 47.52 to 42.35 | empty to 1.0366 | matched, newer edition / replace / replace | IRENA RPGC 2022 and 2024; ICE PEG 2020-2035 |
| PWRDSL | 1488.67 to 1488.67 | 54.97 to 24.04 | 1.3056 to 1.3056 | matched / replace / ASSUMPTION | ICE PEG 2020-2035 (MMV engines) |
| PWRFOI | 4650.33 to 1488.13 | 16.30 to 24.04 | 1.3056 to 1.3056 | replace / replace / ASSUMPTION | ICE PEG 2020-2035 (MMV engines) |
| PWRGEO | 6348.29 to 6348.29 | 128.49 to 116.62 | empty to empty | matched / replace / matched | ICE PEG 2020-2035; IRENA RPGC 2024 |
| PWRHYDDAM | 8079.14 to 8079.14 | 31.86 to 36.63 | empty to empty | matched / replace / matched | NREL ATB 2024 NSD2; ICE PEG 2020-2035 |
| PWRHYDROR | 4588.50 to 4588.50 | 43.20 to 54.95 | empty to empty | matched / replace / matched | ICE PEG 2020-2035 |
| PWRSPVDTR | 1134.28 to 1282.80 | 20.00 to 20.00 | empty to empty | replace / matched / matched | IRENA RPGC 2024; ICE PEG 2020-2035 |
| PWRSPVTRN | 1315.03 to 1315.03 | 14.24 to 19.31 | empty to empty | matched / replace / matched | ICE PEG 2020-2035; IRENA RPGC 2024 |
| PWRWNONS | 1900.66 to 1966.65 | 59.00 to 41.98 | empty to empty | replace / replace / matched | IRENA RPGC 2024 |

How the workbook builds its plant cost paths: the 2021 value x 1.0800 (CPI-U 2022/2021) x the NREL ATB 2024 shape (y) / (2022), an exact match for `PWRGEO`, `PWRWNONS`, `PWRSPVTRN`, `PWRBMS`, `PWRHYDROR` and `PWRDSL`. Only the 2021 levels needed separate sources. `PWRFOI` CapitalCost 4,650.33 USD/kW has no source; the ICE medium-speed engine overnight cost is 1,300 USD/kW (Dec-2019 USD), 1,488 USD/kW in 2022 USD.

## Electricity imports

Step 6 was skipped as the brief instructs. The brief says Costa Rica has no electricity import technology, but the BAU data has one:
- `IMPELE` (output `E1_ELE`) has a TotalTechnologyAnnualActivityUpperLimit of 2.245 PJ in 2021, 3.846 PJ in 2024 and 2.827 PJ a year from 2025 to 2050.
- It has no lower limit and no CapitalCost, FixedCost or VariableCost.
- In a least-cost run, imports up to that limit are therefore free.
- Under rule E1 it should be priced at the 2024 regional market (MER) price. It is listed under Known-limitation candidates in GAPS for Luis to decide; no proposal rows were written for it.

## Country task: coal or petroleum coke

- The MINAE Balance Energetico Nacional 2022 (Tabla 3, PDF p.40) gives industry coal of 0.26 kt, 6.67 TJ, and petroleum coke of 138.6 kt, 3,713.16 TJ.
- The model already uses these values: `E5INDCOA` is 0.00667 PJ and `E5INDCOK` is 3.713 PJ in 2022, and coal stays near 0.008 to 0.011 PJ after 2022.
- The 0.675 PJ of industry coal appears only in 2021 (`A-O_Demand.xlsx`, `Demand_Projection`, cell M25).
- Customs show 2.5 t of anthracite in 2021 and 124,327.9 t of petroleum coke. At the IPCC 32.5 GJ/t, the coke is 4.041 PJ, within 1.2 percent of the model 2021 coke of 4.091 PJ.
- So the 0.675 PJ is not coke recorded as coal: coke is already counted.
- `structure_proposals.csv` proposes the least change, setting 2021 `E5INDCOA` to 0.00667 PJ, and records the literal move to coke as a non-recommended alternative.
- The 2021 balance could not be opened (Cloudflare check).

## ASSUMPTION rows

150 rows: IMPNGS VariableCost 90; PWRDSL VariableCost 30; PWRFOI VariableCost 30.
- `IMPNGS`: Costa Rica imports no natural gas. The 2024 delivered small-scale LNG cost of 7.763 USD/GJ gross is the ASSUMPTION, together with the F5 gross-to-net sentence.
- Engines: non-fuel variable O&M is unchanged at 4.70 USD/MWh, checked against EIA AEO2023 (6.40 USD/MWh).

## Paper trail

- CLEWISE_DataInBrief.docx: 30 statements.
- CLEWISE_JCLP_draft_v2.docx: 5 statements.
- CLEWISE_MethodsX_v02.docx: 2 statements.
- Data_v2.xlsx: 1 statements.
- Suplementary.xlsx: 1 statements.

What changes:
- Data in Brief Table 49 (and `Suplementary.xlsx` `Costos_CR`) prints 2021 values. Its fuel rows need the 2024 pre-tax import or wholesale prices, and its plant rows need the 2024 values with currency year and source.
- Data in Brief section 4.8 needs the editions and tables per technology and the fuel price method (pre-tax import parity, real 2024 USD, WEO 2025 scaling with CPS and NZE as high and low cases).
- MethodsX needs one sentence on the fuel price method.
- The JCLP draft cost indicators (Delta CAPEX, Delta OPEX, accumulated investment) and `Data_v2.xlsx` `5.CR_Costos` need a rerun after the proposals are written.
