# REPORT LAC_COST_REGIONAL 20261111T050439Z

Regional plant cost values for the plant rows that rest only on international sources.

## Run

- Pull request: not yet opened (recorded in a second commit)
- Branch: `job/cost-regional`
- `origin/main` hash at branch time: `9dcafbf15f2c6ba5b306efa383fc33ef333baa22` (all seven job folders of the preamble table present)
- Commit hash: the commit that adds this folder (recorded in a second commit)
- Job folder: `_LAC_HUB/cost_regional_20261111T050439Z/`

## Scope (Step 1)

The scope rule selects 2,217 rows, 68 country, technology and parameter groups and 40 country and technology pairs, equal to the expected 2,217, 68 and 40. Rows by country: CostaRica 360, DominicanRepublic 528, Ecuador 180, Guatemala 528, Honduras 132, Jamaica 489 (all equal to the brief).

## Outcome

- Groups with an accepted value: 28 of 68 (N 6, R1 3, R2 19); international kept: 40.
- `regional_proposals.csv`: 880 rows (one per year column of each accepted group), values in real 2024 USD and model units.
- Accepted groups by country: CostaRica 9, Ecuador 6, Guatemala 10, Honduras 2, Jamaica 1; Dominican Republic 0.

## Documents opened, by tier and region

| Source | Document | Region | Tier | Values in `regional_values.csv` | Used in proposals |
|---|---|---|---|---|---|
| REG-001 | Renewable Power Generation Costs in 2022 (International Renewable Energy Agency (IRENA), 2023-08) | LAC | R1 | 5 | no |
| REG-002 | Renewable Power Generation Costs in 2024 (International Renewable Energy Agency (IRENA), 2025-07) | LAC | R1 | 14 | yes |
| REG-003 | Renewable Power Generation Costs in 2025 (International Renewable Energy Agency (IRENA), 2026-07-02) | LAC | R1 | 11 | yes |
| REG-004 | Renewable Energy Roadmap for Central America: Towards a Regional Energy Transition (International Renewable Energy Agency (IRENA), 2022-03) | Central America | R1 | 24 | no |
| REG-005 | Plan de Expansion de la Generacion Electrica 2024-2040 (Instituto Costarricense de Electricidad (ICE), 2025-09) | Central America | N (Costa Rica); R2 (Guatemala, Honduras) | 129 | yes |
| REG-006 | Plan Indicativo de Expansion de la Generacion 2026-2035, Informe (Operador del Sistema (ODS) / Centro Nacional de Despacho, Honduras, 2026-09) | Central America | R2 | 114 | yes |
| REG-007 | Plan de Expansion Indicativo del Sistema de Generacion 2026-2050 (Ministerio de Energia y Minas (MEM), Guatemala, 2026-01) | Central America | R2 | 32 | no |
| REG-008 | Plan de Expansion Indicativo del Sistema de Generacion 2024-2054 (Ministerio de Energia y Minas (MEM), Guatemala; hosted by CNEE, 2024-01) | Central America | N (Guatemala); R2 | 0 | no |
| REG-009 | Plan de Expansion del Sistema Interconectado Nacional 2025-2039, Tomo II Plan Indicativo de Generacion (Empresa de Transmision Electrica S.A. (ETESA), Panama; hosted by ASEP, 2025-07) | Central America | R2 | 426 | no |
| REG-010 | Plan Indicativo de la Expansion de la Generacion Electrica de El Salvador 2020-2030 (Consejo Nacional de Energia / DGEHM, El Salvador, 2020-11) | Central America | R2 | 24 | no |
| REG-011 | Plan de Desarrollo del Sector Electrico (PLADESE) 2025-2039, Diario Oficial de la Federacion (Secretaria de Energia (SENER), Mexico, 2025-10-14) | Central America | R2 | 20 | no |
| REG-012 | Evolucion futura de costos de las energias renovables y almacenamiento en America Latina (Nota tecnica IDB-TN-1831) (Banco Interamericano de Desarrollo (BID), 2019-12) | LAC | R1 | 0 | no |
| REG-013 | Plan Indicativo de Expansion de la Generacion 2025-2039, version final (Unidad de Planeacion Minero Energetica (UPME), Colombia, 2026-07) | Andean | R2 | 0 | no |
| REG-014 | Catalogo Tecnologico Colombiano: Tecnologias de generacion y almacenamiento de energia, primera edicion (Ministerio de Minas y Energia (MME) and UPME, Colombia, with the Danish Energy Agency, 2025-03) | Andean | R2 | 282 | yes |
| REG-015 | 2018 Jamaica Integrated Resource Plan (Ministry of Science, Energy and Technology (MSET), Jamaica, 2020-02-21) | Caribbean | R2 | 25 | no |
| REG-016 | Plan Energetico Nacional 2022-2036 (Comision Nacional de Energia (CNE), Republica Dominicana, 2022-08) | Caribbean | R2 | 27 | no |
| REG-017 | Integrated Resource and Resiliency Plan for Barbados, Activity B: Draft Report (Government of Barbados (Mott MacDonald for the IDB), 2021-06-22) | Caribbean | R2 | 8 | no |
| REG-018 | Sustainable Energy Technology Considerations and Regional Outlook (Caribbean Centre for Renewable Energy and Energy Efficiency (CCREEE), 2022-03) | Caribbean | R1 | 8 | no |
| REG-019 | Puerto Rico Integrated Resource Plan 2018-2019, Draft for Review (Exhibit 1.0) (Puerto Rico Electric Power Authority (PREPA), prepared by Siemens PTI, 2019-02) | Caribbean | R2 | 40 | no |
| REG-020 | Plan Indicativo de Expansion de la Generacion 2026-2035, Anexos (Operador del Sistema (ODS) / Centro Nacional de Despacho, Honduras, 2026-09) | Central America | R2 | 0 | no |
| REG-021 | 2022 Jamaica Integrated Resource Plan (IRP-2) (Government of Jamaica, Generation Procurement Entity, 2024-11) | Caribbean | R2 | 0 | no |

Documents opened by region: Central America 9, Caribbean 6, LAC 4, Andean 2 (21 documents). By tier: N 1 (ICE PEG 2024-2040, national for Costa Rica; MEM Guatemala PEG 2024-2054 would be N for Guatemala but prints no cost table); R1 6 (IRENA RPGC 2022, 2024 and 2025, IRENA Central America roadmap, IDB TN-1831, CCREEE); R2 14 (neighbour plans and the Colombian catalogue). CPI-U files of three country jobs (CRC-001, FUE-001, CSH-005) were copied for the currency conversion.

Leads: 28 rows in `leads.csv`; 46 entries in `search_log.csv`; 5 manual downloads. Extra documents beyond the lead list: Central America 2 of 10 (ICE PEG 2024-2040, MEM Guatemala PEG 2024-2054), Andean 1 of 10 (Ecuador PME chapter, did not open), Caribbean 1 of 10 (CNE Dominican Republic study, not found).

## The 68 groups

2024 values in model units (CapitalCost USD/kW, FixedCost USD/kW-year, VariableCost USD/GJ; Ecuador STOELE per PJ/yr of capacity). International values keep the currency year of their country job; regional values are real 2024 USD.

| Country | Technology | Parameter | Outcome | Source | 2024 international | 2024 regional | Change % |
|---|---|---|---|---|---|---|---|
| CostaRica | PP_SPV_DG | CapitalCost | international kept | | 2,600.5800 | | |
| CostaRica | PP_SPV_DG | FixedCost | international kept | | 29.5300 | | |
| CostaRica | PWRBMS | CapitalCost | N | ICE PEG 2024-2040 | 3,024.6120 | 1,801.6152 | -40.43 |
| CostaRica | PWRBMS | VariableCost | international kept | | 1.0366 | | |
| CostaRica | PWRDSL | VariableCost | R2 | ODS Honduras PIEG 2026-2035 | 1.3056 | 1.3889 | 6.38 |
| CostaRica | PWRFOI | VariableCost | R2 | ODS Honduras PIEG 2026-2035 | 1.3056 | 1.9444 | 48.93 |
| CostaRica | PWRGEO | FixedCost | N | ICE PEG 2024-2040 | 116.6183 | 164.7191 | 41.25 |
| CostaRica | PWRHYDDAM | CapitalCost | R2 | ODS Honduras PIEG 2026-2035 | 8,079.1443 | 5,100.0000 | -36.87 |
| CostaRica | PWRSPVDTR | CapitalCost | N | ICE PEG 2024-2040 | 1,282.8012 | 1,132.4438 | -11.72 |
| CostaRica | PWRSPVTRN | FixedCost | N | ICE PEG 2024-2040 | 19.3120 | 17.5014 | -9.38 |
| CostaRica | PWRWNONS | CapitalCost | N | ICE PEG 2024-2040 | 1,966.6509 | 1,956.0393 | -0.54 |
| CostaRica | PWRWNONS | FixedCost | N | ICE PEG 2024-2040 | 41.9826 | 51.4747 | 22.61 |
| DominicanRepublic | PPBGS | CapitalCost | international kept | | 2,162.0000 | | |
| DominicanRepublic | PPBGS | FixedCost | international kept | | 163.6660 | | |
| DominicanRepublic | PPBGS | VariableCost | international kept | | 1.3889 | | |
| DominicanRepublic | PPBIM | CapitalCost | international kept | | 2,162.0000 | | |
| DominicanRepublic | PPDHYD | CapitalCost | international kept | | 2,881.0000 | | |
| DominicanRepublic | PPDHYD | FixedCost | international kept | | 72.0250 | | |
| DominicanRepublic | PPHDAM | CapitalCost | international kept | | 3,241.3364 | | |
| DominicanRepublic | PPHDAM | FixedCost | international kept | | 92.0000 | | |
| DominicanRepublic | PPPVD | CapitalCost | international kept | | 1,789.6163 | | |
| DominicanRepublic | PPPVD | FixedCost | international kept | | 18.0000 | | |
| DominicanRepublic | PPPVT | CapitalCost | international kept | | 916.5241 | | |
| DominicanRepublic | PPPVT | FixedCost | international kept | | 21.6089 | | |
| DominicanRepublic | PPPVTHYD | CapitalCost | international kept | | 916.5241 | | |
| DominicanRepublic | PPPVTHYD | FixedCost | international kept | | 21.6089 | | |
| DominicanRepublic | PPWNDON | CapitalCost | international kept | | 1,281.8838 | | |
| DominicanRepublic | PPWNDON | FixedCost | international kept | | 31.6482 | | |
| Ecuador | PPPVD | CapitalCost | R2 | Colombian Technology Catalogue 2025 | 1,855.4872 | 1,180.0000 | -36.40 |
| Ecuador | PPPVD | FixedCost | R2 | Colombian Technology Catalogue 2025 | 19.7117 | 15.0000 | -23.90 |
| Ecuador | PPWNDD | CapitalCost | R2 | Colombian Technology Catalogue 2025 | 3,676.4387 | 3,400.0000 | -7.52 |
| Ecuador | PPWNDD | FixedCost | R2 | Colombian Technology Catalogue 2025 | 41.7387 | 68.5000 | 64.12 |
| Ecuador | STOELE | CapitalCost | R2 | Colombian Technology Catalogue 2025 | 60.1562 | 59.9315 | -0.37 |
| Ecuador | STOELE | FixedCost | R2 | Colombian Technology Catalogue 2025 | 1.5040 | 0.4756 | -68.37 |
| Guatemala | PPBIM | VariableCost | international kept | | 1.1111 | | |
| Guatemala | PPCOA | CapitalCost | international kept | | 2,100.0000 | | |
| Guatemala | PPFOI | FixedCost | R2 | ODS Honduras PIEG 2026-2035 | 35.1600 | 14.0000 | -60.18 |
| Guatemala | PPFOI | VariableCost | R2 | ODS Honduras PIEG 2026-2035 | 1.5806 | 1.9444 | 23.02 |
| Guatemala | PPGEO | CapitalCost | R2 | ODS Honduras PIEG 2026-2035 | 4,015.0000 | 6,179.2400 | 53.90 |
| Guatemala | PPHROR | CapitalCost | R2 | ODS Honduras PIEG 2026-2035 | 3,444.0000 | 3,786.5000 | 9.94 |
| Guatemala | PPNGS | CapitalCost | R2 | ODS Honduras PIEG 2026-2035 | 1,000.0000 | 1,437.5900 | 43.76 |
| Guatemala | PPPVD | CapitalCost | international kept | | 1,794.7388 | | |
| Guatemala | PPPVD | FixedCost | international kept | | 18.3870 | | |
| Guatemala | PPPVDS | CapitalCost | international kept | | 2,841.5304 | | |
| Guatemala | PPPVDS | FixedCost | international kept | | 52.3029 | | |
| Guatemala | PPPVT | CapitalCost | R1 | IRENA RPGC 2025 | 1,375.0000 | 1,077.0597 | -21.67 |
| Guatemala | PPPVT2 | CapitalCost | R1 | IRENA RPGC 2025 | 1,551.2727 | 1,077.0597 | -30.57 |
| Guatemala | PPPVT2 | FixedCost | R2 | ODS Honduras PIEG 2026-2035 | 21.6089 | 21.2500 | -1.66 |
| Guatemala | PPPVTS | CapitalCost | R2 | ODS Honduras PIEG 2026-2035 | 2,456.0613 | 1,434.7200 | -41.58 |
| Guatemala | PPPVTS | FixedCost | R2 | ODS Honduras PIEG 2026-2035 | 61.4677 | 40.3100 | -34.42 |
| Honduras | PPBIM | CapitalCost | R2 | ICE PEG 2024-2040 | 2,012.8163 | 1,801.6152 | -10.49 |
| Honduras | PPBIM | FixedCost | R2 | ICE PEG 2024-2040 | 163.6660 | 38.0913 | -76.73 |
| Honduras | PPBIM | VariableCost | international kept | | 1.3889 | | |
| Honduras | PPPVD | FixedCost | international kept | | 29.5317 | | |
| Jamaica | PPBGS | CapitalCost | international kept | | 2,015.8424 | | |
| Jamaica | PPBGS | FixedCost | international kept | | 163.6660 | | |
| Jamaica | PPBGS | VariableCost | international kept | | 1.1111 | | |
| Jamaica | PPBIM | CapitalCost | international kept | | 2,015.8424 | | |
| Jamaica | PPBIM | FixedCost | international kept | | 163.6660 | | |
| Jamaica | PPBIM | VariableCost | international kept | | 1.1111 | | |
| Jamaica | PPGEO | CapitalCost | international kept | | 6,471.5934 | | |
| Jamaica | PPGEO | FixedCost | international kept | | 128.7264 | | |
| Jamaica | PPHDAM | CapitalCost | international kept | | 3,007.7097 | | |
| Jamaica | PPHDAM | FixedCost | international kept | | 85.0000 | | |
| Jamaica | PPHROR | CapitalCost | international kept | | 7,436.0822 | | |
| Jamaica | PPPVD | CapitalCost | international kept | | 2,600.5763 | | |
| Jamaica | PPPVD | FixedCost | international kept | | 29.1128 | | |
| Jamaica | PPWNDON | CapitalCost | R1 | IRENA RPGC 2024 | 1,772.5899 | 2,108.0000 | 18.92 |

## Flags (Step 6)

17 of 28 accepted groups carry a flag; no accepted value is outside the screens (CapitalCost 300 to 8,000 USD/kW, FixedCost 0 to 200 USD/kW-year, VariableCost up to 8.33 USD/GJ). Flags do not block a proposal.

- CostaRica PWRBMS CapitalCost: 2024 change above 25 percent; change above 25 percent in 30 of 30 years (max 40.4).
- CostaRica PWRFOI VariableCost: 2024 change above 25 percent; change above 25 percent in 30 of 30 years (max 48.9).
- CostaRica PWRGEO FixedCost: 2024 change above 25 percent; change above 25 percent in 30 of 30 years (max 41.2).
- CostaRica PWRHYDDAM CapitalCost: 2024 change above 25 percent; change above 25 percent in 30 of 30 years (max 36.9).
- Ecuador PPPVD CapitalCost: 2024 change above 25 percent; change above 25 percent in 30 of 30 years (max 47.5).
- Ecuador PPWNDD CapitalCost: change above 25 percent in 21 of 30 years (max 78.5).
- Ecuador PPWNDD FixedCost: 2024 change above 25 percent; change above 25 percent in 30 of 30 years (max 64.1).
- Ecuador STOELE FixedCost: 2024 change above 25 percent; change above 25 percent in 30 of 30 years (max 68.9).
- Guatemala PPFOI FixedCost: 2024 change above 25 percent; change above 25 percent in 33 of 33 years (max 60.2).
- Guatemala PPGEO CapitalCost: 2024 change above 25 percent; change above 25 percent in 33 of 33 years (max 53.9).
- Guatemala PPNGS CapitalCost: 2024 change above 25 percent; change above 25 percent in 33 of 33 years (max 43.8).
- Guatemala PPPVT CapitalCost: change above 25 percent in 29 of 33 years (max 52.5).
- Guatemala PPPVT2 CapitalCost: 2024 change above 25 percent; change above 25 percent in 30 of 33 years (max 52.4).
- Guatemala PPPVTS CapitalCost: 2024 change above 25 percent; change above 25 percent in 33 of 33 years (max 41.6).
- Guatemala PPPVTS FixedCost: 2024 change above 25 percent; change above 25 percent in 33 of 33 years (max 34.4).
- Honduras PPBIM FixedCost: 2024 change above 25 percent; change above 25 percent in 33 of 33 years (max 76.7).
- Jamaica PPWNDON CapitalCost: change above 25 percent in 1 of 34 years (max 31.5).

## Gates (Step 7)

| Gate | Result | Counts |
|---|---|---|
| 1 Read-only | pass | 186 files hashed before and after (6 A-O workbooks and 180 BAU A2_Output_Params CSVs in the main copy), 0 changed |
| 2 Changed files | pass | 29 files changed against origin/main, all in the job folder, all .md, .csv or .py; 0 under downloads/ or scratch/ |
| 3 Sources | pass | 8 source ids in proposals, all in `sources.csv` (24 sources); every source has an http(s) URL, a locator, a retrieval date and a file in `downloads/`; no local path or internal file named |
| 4 Values as printed | pass | 43 of 43 accepted printed values found in the file text at the recorded page (`value_checks.csv`) |
| 5 Coverage | pass | 28 accepted groups, 880 rows, no year missing or duplicated |
| 6 Commit messages | not run | runs on the commit itself; result recorded in the second commit |
| 7 Dashes and whitespace | pass | no em dash in the 29 tracked files; git diff --check clean (0 lines) |
