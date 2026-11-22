# REPORT: LAC_NDC_VERIFY 20261121T233937Z

Branch `job/ndc-verify`, started from `origin/main` at `a76ad81`. Model state read from `/c/clw_scout_model` at `481a7c0` (unchanged). Nothing in a model was changed; this job proposes and lists.

## 1. Failed, blocked or pending

- **UNFCCC NDC registry and long-term strategies portal: blocked.** Three addresses gave an Incapsula bot check to curl and an Imperva CAPTCHA in the browser; not passed. Versions were confirmed from title pages and UNFCCC file folders (`document_status.csv`). No table mixes versions: Honduras rows use NDC 3.0 (HON-01) only; the second update (HON-02) gives no NDC row.
- **Documents still pending (6 of 12):** Dominican Republic LT-LEDS (draft awaiting launch) and PEN 2025-2038; Ecuador ENEM; Honduras ENDRCH (not published) and NDC 3.0 technical annex; Jamaica BTR1 and NID. Fetched: ICE PEG 2022-2040 (CR-22), Costa Rica INDC Spanish (CR-21), PNMUS (ECU-21), ENDBE UNFCCC file (GUA-21), ENME (HON-21); the Jamaica LTS UNFCCC file is byte-identical to JAM-02.
- **12 conflicts held back** (section 3) and **5 rows with no number or no stated year** held back (`scenario_values_held_back.csv`).
- **165 values with two checks**, most for want of a second place (section 2).
- **Unconfirmed lead:** the UNFCCC case study naming CLG, UWI and CIRED for Jamaica's long-term strategy gave a bot check; not confirmed.
- **Values found in step D not yet given three checks**, among them the ICE PEG 2022-2040 that Costa Rica's NDC 3.0 relies on; they are not in `scenario_values.csv`.
- **Background tasks:** three ran at once for some minutes (the brief allows two) when a foreground search was moved to the background by the harness while both blind readers ran (GAPS, incidents).
- **Pull request number:** added in a second, report-only commit (a force push to amend is not used).

## 2. Values by check status

733 values checked: 556 at 3 of 3, 165 at 2 of 3, 12 conflicts. Check 2 agreed with check 1 on 698 values at the first comparison; the hub read 32 pages a third time (`parts/third_reading.csv`).

| Country | Values | 3 of 3 | 2 of 3 | conflict |
|---|---|---|---|---|
| Costa Rica | 102 | 74 | 28 | 0 |
| Dominican Republic | 66 | 35 | 28 | 3 |
| Ecuador | 114 | 85 | 29 | 0 |
| Guatemala | 126 | 82 | 42 | 2 |
| Honduras | 192 | 171 | 20 | 1 |
| Jamaica | 133 | 109 | 18 | 6 |
| All | 733 | 556 | 165 | 12 |

Missing check among the 2 of 3 rows:

| Country | missing check 2 | missing check 3 |
|---|---|---|
| Costa Rica | 0 | 28 |
| Dominican Republic | 10 | 18 |
| Ecuador | 0 | 29 |
| Guatemala | 0 | 42 |
| Honduras | 1 | 19 |
| Jamaica | 1 | 17 |

## 3. Every conflict with its three readings

| Value | Check 1 (scout) | Check 2 (blind) | Third reading (hub) | What the document supports |
|---|---|---|---|---|
| DR-T025 | 22,925.66 t CO2 eq per year, 2030, DR-01 p.155 | 31 km, 2026-2030 (corridor length of the same measure) | 22,925.66 on p.155 | check 1; no second place, so 1 of 3 |
| DR-T026 | 111,642 t CO2, 2035, p.156 | 10.5 km (monorail length) | 111,642 on p.156 | check 1; 1 of 3 |
| DR-T027 | 11,343 t CO2 eq, 2030, p.157 | 4,500 passengers per hour (cable car) | 11,343 on p.157 | check 1; 1 of 3 |
| GUA-T077 | 100,000 stoves, 2032, GUA-07 p.79 | 100,000 stoves, 2027 | 100,000, no year printed | neither year: a long-term goal of the 2013-2027 policy |
| GUA-P049 | 125 Mt CO2e, 2050, GUA-04 p.58 | 125 Mt CO2e, 2050 | not needed | the document contradicts itself: 125 against a 203 Mt BAU is 38 percent, not the 22 percent of the label |
| HON-T083 | 14,819.2 t CO2 eq, 2030, HON-05 p.552 | 2.5 percent, 2030 (same row) | 14,819.2 on p.552 | check 1; 1 of 3 |
| JAM-T058 | 8 percent, 2050, JAM-02 p.55 and p.54 | 8 percent, 2050 | not needed | the document contradicts itself: Table 1 (p.15) says 11 percent |
| JAM-T059 | 11 percent, 2050, JAM-02 p.15 | 11 percent, 2050 | not needed | the document contradicts itself: Table 4 (p.55) and text say 8 percent |
| JAM-T075 | 200 buses, 2026, JAM-02 p.57 | 200 EV buses, 2023 | 200, no year printed (over the next three years) | neither year |
| JAM-T121 | 171.5 MW, 2027, JAM-07 p.15, p.62, p.66 | 131.5 MW, 2027 (and 40 MW) | 131.5 MW turbines and 40 MW diesel, printed apart | check 2: 171.5 is a sum the plan never prints |
| JAM-T122 | 249.9 MW, 2033, JAM-07 p.20, p.15 | 65.5 MW, 2033 | 65.5 MW in 2033 (p.15); 249.9 is a scenario total of JPS retirements (p.20) | check 2 |
| JAM-P028 | 2.34 Mt CO2e, 2020, JAM-02 p.58 | 0.79 Mt CO2e, 2050 (same sentence) | 2.34 for 2020 on p.58 | check 1; 1 of 3 |

## 4. Headline values, document against model

Standard units; model values from the solved results at 481a7c0. `different quantity` and `not compared` rows carry no model value (reasons in `model_comparison.csv`). Fleet, blend, loss and measure-level rows are left out here; all rows are in `parts/headlines.md` and `model_comparison.csv`.

### Costa Rica

| Scen. | Value id | What | Year | Document (standard) | Model NDCNEW 2030 / 2035 / 2050 | Model LTSNEW 2035 / 2050 | Same kind |
|---|---|---|---|---|---|---|---|
| NDC | CR-T001 | net GHG emissions in 2030 | 2030 | 11380.0 kt CO2 eq (conditional) | -  | - | different quantity |
| NDC | CR-T003 | reduction of CO2e emissions in 2030 against scenario without | 2030 | 0.53 fraction (conditional) | -  | - | different quantity |
| NDC | CR-T004 | reduction of CO2e emissions in 2030 against scenario without | 2030 | 0.23 fraction (unconditional) | -  | - | different quantity |
| NDC | CR-T005 | net GHG emissions 2030 against 2015 | 2030 | 0.15 fraction (conditional) | -  | - | different quantity |
| NDC | CR-T006 | net GHG emissions in 2050 | 2050 | 0.0 kt CO2 eq (not stated) | -  | - | not compared |
| NDC | CR-T032 | renewable share of generation | 2027 | 0.95 fraction (conditional) | 0.8967 / 0.9 / 0.9 fraction | 0.99 / 0.99 | yes |
| NDC | CR-T033 | renewable share of generation | 2035 | 0.95 fraction (conditional) | 0.8967 / 0.9 / 0.9 fraction | 0.99 / 0.99 | yes |
| LTS | CR-T076 | net GHG emissions in 2050 | 2050 | 0.0 kt CO2 eq (not stated) | -  | - | not compared |
| LTS | CR-T077 | energy sector emissions 2050 | 2050 | 2640.0 kt CO2 eq (not stated) | -  | - | not compared |
| LTS | CR-T090 | renewable share of generation | 2030 | 1.0 fraction (not stated) | 0.8967 / 0.9 / 0.9 fraction | 0.99 / 0.99 | yes |

### Dominican Republic

| Scen. | Value id | What | Year | Document (standard) | Model NDCNEW 2030 / 2035 / 2050 | Model LTSNEW 2035 / 2050 | Same kind |
|---|---|---|---|---|---|---|---|
| NDC | DR-T002 | emission reduction against BAU | 2030 | 14732.1 kt CO2 eq (mixed) | -  | - | different quantity |
| NDC | DR-T004 | emission reduction against BAU | 2035 | 18349.32 kt CO2 eq (not stated) | -  | - | different quantity |
| NDC | DR-T011 | new natural gas combined cycle capacity | 2030 | 1429.0 MW (not stated) | 1371.1 / 1371.1 / 1281.6 MW | 1372.8 / 1617.4 | partly |
| NDC | DR-T013 | new renewable capacity | 2030 | 1529.0 MW (not stated) | 6519.9 / 14055.0 / 23852.5 MW | 14610.8 / 35434.9 | partly |
| NDC | DR-T014 | new solar PV capacity | 2030 | 1267.15 MW (not stated) | 4111.2 / 9420.8 / 16325.1 MW | 9811.9 / 24486.2 | partly |
| NDC | DR-T015 | new wind capacity | 2030 | 250.0 MW (not stated) | 1723.1 / 3948.5 / 6842.3 MW | 4112.4 / 10262.8 | partly |
| NDC | DR-T016 | new hydro capacity | 2030 | 12.0 MW (not stated) | 641.9 / 641.9 / 641.8 MW | 642.6 / 642.6 | partly |
| NDC | DR-T020 | nuclear capacity | 2035 | 300.0 MW (not stated) | -  | - | different quantity |

### Ecuador

| Scen. | Value id | What | Year | Document (standard) | Model NDCNEW 2030 / 2035 / 2050 | Model LTSNEW 2035 / 2050 | Same kind |
|---|---|---|---|---|---|---|---|
| NDC | ECU-T002 | emission reduction against BAU | 2035 | 8800.0 kt CO2 eq (unconditional) | -  | - | different quantity |
| NDC | ECU-T004 | emission reduction against BAU (additional) | 2035 | 10600.0 kt CO2 eq (conditional) | -  | - | different quantity |
| LTS | ECU-T017 | percent reduction against BAU | 2070 | 0.7 fraction (not stated) | -  | - | different quantity |
| LTS | ECU-T019 | net emissions | 2070 | 36400.0 kt CO2 eq (not stated) | -  | - | different quantity |
| LTS | ECU-T020 | sector emissions | 2035 | 39200.0 kt CO2 eq (not stated) | 31204.4 / 32764.8 / 43664.0 kt CO2 eq | 32706.6 / 30409.1 | partly |
| LTS | ECU-T021 | sector emissions | 2050 | 35800.0 kt CO2 eq (not stated) | 31204.4 / 32764.8 / 43664.0 kt CO2 eq | 32706.6 / 30409.1 | partly |
| LTS | ECU-T022 | sector emissions | 2070 | 33900.0 kt CO2 eq (not stated) | 31204.4 / 32764.8 / 43664.0 kt CO2 eq | 32706.6 / 30409.1 | partly |
| LTS | ECU-T026 | Hydro share of SNI generation, phase I | 2035 | 0.64 fraction (not stated) | 0.6755 / 0.6084 / 0.4715 fraction | 0.6075 / 0.4578 | yes |
| LTS | ECU-T027 | installed capacity | 2035 | 10000.0 MW (not stated) | 6341.1 / 6341.1 / 6428.2 MW | 6354.1 / 6441.2 | partly |
| LTS | ECU-T028 | Non-conventional renewable share of SNI generation, phase II | 2050 | 0.35 fraction (not stated) | 0.1054 / 0.1964 / 0.3424 fraction | 0.1974 / 0.5325 | yes |
| LTS | ECU-T029 | installed capacity | 2050 | 3800.0 MW (not stated) | 8911.7 / 12049.2 / 19728.6 MW | 12099.9 / 27972.9 | partly |
| LTS | ECU-T030 | Hydro share of SNI generation, phase II | 2050 | 0.54 fraction (not stated) | 0.6755 / 0.6084 / 0.4715 fraction | 0.6075 / 0.4578 | yes |
| LTS | ECU-T031 | Non-conventional renewable share of SNI generation, phase II | 2070 | 0.37 fraction (not stated) | 0.1054 / 0.1964 / 0.3424 fraction | 0.1974 / 0.5325 | yes |
| NDC | ECU-T069 | new capacity | 2032 | 4034.0 MW (not stated) | 6341.1 / 6341.1 / 6428.2 MW | 6354.1 / 6441.2 | partly |
| NDC | ECU-T070 | new capacity | 2032 | 1683.0 MW (not stated) | 6341.1 / 6341.1 / 6428.2 MW | 6354.1 / 6441.2 | partly |
| NDC | ECU-T071 | new capacity | 2032 | 587.0 MW (not stated) | -  | - | different quantity |

### Guatemala

| Scen. | Value id | What | Year | Document (standard) | Model NDCNEW 2030 / 2035 / 2050 | Model LTSNEW 2035 / 2050 | Same kind |
|---|---|---|---|---|---|---|---|
| NDC | GUA-T001 | percent reduction against BAU | 2035 | 0.237 fraction (not stated) | -  | - | different quantity |
| NDC | GUA-T002 | net emissions | 2035 | 57763.7 kt CO2 eq (not stated) | -  | - | different quantity |
| NDC | GUA-T003 | emission reduction against BAU | 2035 | 17974.3 kt CO2 eq (not stated) | -  | - | different quantity |
| NDC | GUA-T005 | emission reduction against BAU | 2035 | 1184.9 kt CO2 eq (not stated) | 4275.9 / 8479.3 / 14582.8 kt CO2 eq | 8492.4 / 43055.3 | partly |
| NDC | GUA-T006 | sector emissions | 2035 | 27320.2 kt CO2 eq (not stated) | 30504.1 / 34617.8 / 60021.0 kt CO2 eq | 34604.7 / 31548.5 | partly |
| NDC | GUA-T008 | renewable share of generation | 2035 | 0.8 fraction (not stated) | 0.6576 / 0.75 / 0.7501 fraction | 0.75 / 0.99 | yes |
| NDC | GUA-T009 | new renewable capacity | 2035 | 1000.0 MW (not stated) | 4354.1 / 6818.8 / 11364.4 MW | 7955.3 / 23977.6 | partly |
| NDC | GUA-T010 | emission reduction against BAU | 2035 | 696.7 kt CO2 eq (not stated) | -  | - | different quantity |
| LTS | GUA-T056 | percent reduction against BAU | 2050 | 0.59 fraction (not stated) | -  | - | different quantity |
| LTS | GUA-T057 | percent reduction against BAU | 2030 | 0.44 fraction (not stated) | -  | - | different quantity |
| LTS | GUA-T060 | renewable share of generation | 2032 | 0.64 fraction (not stated) | 0.6576 / 0.75 / 0.7501 fraction | 0.75 / 0.99 | yes |

### Honduras

| Scen. | Value id | What | Year | Document (standard) | Model NDCNEW 2030 / 2035 / 2050 | Model LTSNEW 2035 / 2050 | Same kind |
|---|---|---|---|---|---|---|---|
| NDC | HON-T001 | emission reduction against BAU | 2035 | 12847.2 kt CO2 eq (conditional) | -  | - | different quantity |
| NDC | HON-T003 | emission reduction against BAU | 2030 | 8564.8 kt CO2 eq (conditional) | -  | - | different quantity |
| NDC | HON-T004 | percent reduction against BAU | 2030 | 0.17 fraction (conditional) | -  | - | different quantity |
| NDC | HON-T005 | net emissions | 2030 | 41816.4 kt CO2 eq (conditional) | -  | - | different quantity |
| NDC | HON-T006 | net emissions | 2035 | 52769.0 kt CO2 eq (conditional) | -  | - | different quantity |
| NDC | HON-T007 | emission reduction against BAU | 2035 | 7268.0 kt CO2 eq (conditional) | -  | - | different quantity |
| NDC | HON-T008 | emission reduction against BAU | 2030 | 2519.1 kt CO2 eq (conditional) | 964.2 / 2481.5 / 2134.3 kt CO2 eq | 2935.4 / 11544.8 | partly |
| NDC | HON-T009 | emission reduction against BAU | 2035 | 3778.6 kt CO2 eq (conditional) | 964.2 / 2481.5 / 2134.3 kt CO2 eq | 2935.4 / 11544.8 | partly |
| NDC | HON-T018 | renewable share of generation | 2030 | 0.7 fraction (conditional) | 0.6477 / 0.75 / 0.75 fraction | 0.75 / 0.99 | yes |
| NDC | HON-T019 | renewable share of generation | 2035 | 0.7 fraction (conditional) | 0.6477 / 0.75 / 0.75 fraction | 0.75 / 0.99 | yes |
| NDC | HON-T089 | renewable share of generation | 2030 | 0.76 fraction (not stated) | 0.6477 / 0.75 / 0.75 fraction | 0.75 / 0.99 | yes |
| NDC | HON-T090 | renewable share of generation | 2035 | 0.71 fraction (not stated) | 0.6477 / 0.75 / 0.75 fraction | 0.75 / 0.99 | yes |
| NDC | HON-T091 | new renewable capacity | 2035 | 1796.24 MW (not stated) | 3656.6 / 5465.9 / 9294.8 MW | 5793.0 / 15117.6 | partly |
| NDC | HON-T092 | new thermal capacity | 2035 | 1285.0 MW (not stated) | 0.0 / 262.8 / 1302.0 MW | 354.7 / 2255.2 | partly |
| NDC | HON-T094 | retired capacity | 2035 | 1342.62 MW (not stated) | -  | - | different quantity |
| NDC | HON-T095 | new capacity | 2029 | 250.0 MW (not stated) | 0.0 / 262.8 / 1302.0 MW | 354.7 / 2255.2 | partly |
| NDC | HON-T096 | new capacity | 2029 | 105.0 MW (not stated) | 0.0 / 0.0 / 0.0 MW | 0.0 / 0.0 | partly |

### Jamaica

| Scen. | Value id | What | Year | Document (standard) | Model NDCNEW 2030 / 2035 / 2050 | Model LTSNEW 2035 / 2050 | Same kind |
|---|---|---|---|---|---|---|---|
| NDC | JAM-T002 | percent reduction against BAU | 2030 | 0.1955 fraction (unconditional) | -  | - | different quantity |
| NDC | JAM-T004 | percent reduction against BAU | 2035 | 0.259 fraction (unconditional) | -  | - | different quantity |
| NDC | JAM-T017 | emission level | 2030 | 5800.0 kt CO2 eq (unconditional) | 5107.8 / 4188.2 / 5309.7 kt CO2 eq | 3941.7 / 1964.4 | partly |
| NDC | JAM-T018 | emission level | 2035 | 5700.0 kt CO2 eq (unconditional) | 5107.8 / 4188.2 / 5309.7 kt CO2 eq | 3941.7 / 1964.4 | partly |
| NDC | JAM-T019 | emission level | 2030 | 5500.0 kt CO2 eq (conditional) | 5107.8 / 4188.2 / 5309.7 kt CO2 eq | 3941.7 / 1964.4 | partly |
| NDC | JAM-T020 | emission level | 2035 | 4900.0 kt CO2 eq (conditional) | 5107.8 / 4188.2 / 5309.7 kt CO2 eq | 3941.7 / 1964.4 | partly |
| NDC | JAM-T021 | emission level | 2030 | 6200.0 kt CO2 eq (unconditional) | -  | - | different quantity |
| NDC | JAM-T022 | emission level | 2035 | 6100.0 kt CO2 eq (unconditional) | -  | - | different quantity |
| NDC | JAM-T023 | emission level | 2030 | 5900.0 kt CO2 eq (conditional) | -  | - | different quantity |
| NDC | JAM-T024 | emission level | 2035 | 5300.0 kt CO2 eq (conditional) | -  | - | different quantity |
| NDC | JAM-T025 | emission level (net) | 2030 | 4200.0 kt CO2 eq (unconditional) | -  | - | different quantity |
| NDC | JAM-T026 | emission level (net) | 2035 | 4000.0 kt CO2 eq (unconditional) | -  | - | different quantity |
| NDC | JAM-T027 | emission level (net) | 2035 | 3300.0 kt CO2 eq (conditional) | -  | - | different quantity |
| NDC | JAM-T028 | renewable share of generation | 2030 | 0.5 fraction (not stated) | 0.3911 / 0.7503 / 0.7501 fraction | 0.7503 / 0.99 | yes (model generation read as net generation) |
| NDC | JAM-T029 | renewable share of generation | 2035 | 0.63 fraction (not stated) | 0.3911 / 0.7503 / 0.7501 fraction | 0.7503 / 0.99 | yes (model generation read as net generation) |
| LTS | JAM-T046 | net emissions | 2060 | 0.0 kt CO2 eq (not stated) | -  | - | not compared |
| LTS | JAM-T047 | renewable share of generation | 2025 | 0.27 fraction (not stated) | 0.3911 / 0.7503 / 0.7501 fraction | 0.7503 / 0.99 | yes (model generation read as net generation) |
| LTS | JAM-T048 | renewable share of generation | 2030 | 0.5 fraction (not stated) | 0.3911 / 0.7503 / 0.7501 fraction | 0.7503 / 0.99 | yes (model generation read as net generation) |
| LTS | JAM-T049 | renewable share of generation | 2035 | 0.65 fraction (not stated) | 0.3911 / 0.7503 / 0.7501 fraction | 0.7503 / 0.99 | yes (model generation read as net generation) |
| LTS | JAM-T050 | renewable share of generation | 2040 | 0.9 fraction (not stated) | 0.3911 / 0.7503 / 0.7501 fraction | 0.7503 / 0.99 | yes (model generation read as net generation) |
| LTS | JAM-T051 | renewable share of generation | 2045 | 0.95 fraction (not stated) | 0.3911 / 0.7503 / 0.7501 fraction | 0.7503 / 0.99 | yes (model generation read as net generation) |
| LTS | JAM-T052 | renewable share of generation | 2050 | 1.0 fraction (not stated) | 0.3911 / 0.7503 / 0.7501 fraction | 0.7503 / 0.99 | yes (model generation read as net generation) |
| LTS | JAM-T060 | HFO capacity remaining | 2035 | 0.0 MW (not stated) | -  | - | not compared |
| LTS | JAM-T062 | new intermittent renewable capacity | 2050 | 2000.0 MW (not stated) | 842.0 / 1430.0 / 1903.8 MW | 1527.8 / 3348.5 | partly |
| NDC | JAM-T115 | renewable share of generation | 2030 | 0.5 fraction (not stated) | 0.3911 / 0.7503 / 0.7501 fraction | 0.7503 / 0.99 | yes (model generation read as net generation) |
| NDC | JAM-T116 | renewable share of generation | 2035 | 0.634 fraction (not stated) | 0.3911 / 0.7503 / 0.7501 fraction | 0.7503 / 0.99 | yes (model generation read as net generation) |
| NDC | JAM-T117 | new wind capacity | 2041 | 344.0 MW (not stated) | 303.0 / 379.6 / 459.4 MW | 406.9 / 821.8 | partly |
| NDC | JAM-T118 | new solar PV capacity | 2041 | 1143.0 MW (not stated) | 469.8 / 978.1 / 1372.0 MW | 1048.5 / 2454.3 | partly |
| NDC | JAM-T119 | new hydro capacity | 2033 | 34.3 MW (not stated) | 64.2 / 67.4 / 67.4 MW | 67.4 / 67.4 | partly |
| NDC | JAM-T123 | new fossil capacity | 2041 | 0.0 MW (not stated) | -  | - | not compared |
| NDC | JAM-T124 | electricity sector emissions | 2030 | 1290.0 kt CO2 eq (not stated) | -  | - | different quantity |

## 5. Supporting analyses found and what they add

38 documents were added (`sources.csv`): 7 official, 15 external, 16 lead (CLG). 258 printed results are in `analyses_<code>.csv`, every one found on its cited page (253 by text search, 5 by the hub on the rendered page or saved HTML). The comparison with BAU, NDCNEW and LTSNEW is in `analyses_comparison.md`.

| Country | Analyses (class) | What they add |
|---|---|---|
| Costa Rica | ICE PEG 2022-2040 (official, cited by NDC 3.0); RAND and IDB cost-benefit of the NDP (external); Climate Action Tracker (external); DDP chapter and `ndc_cr` repository (lead) | The PEG gives yearly generation by source (fuel oil 17 GWh of 13,814 GWh in 2030) behind the 95 percent target; RAND gives the NDP against no decarbonization (net zero against 18.8 Mt in 2050, 41 billion USD net benefit). NDC 3.0 was built on CLEW-CR-3.0, which the CLG repository holds. |
| Dominican Republic | World Bank CCDR and power annex (external); CNE bulletin on the PEN (official); IDB monograph 1138, LTS-RD documentation, DDP chapter (lead) | An independent power model with NP, NDC2030 and NZP2050 (grid emissions 14.3, 8.7 and 0 Mt in 2050; 67 percent renewables in NZP2050). The long-term strategy is still a draft. |
| Ecuador | World Bank CCDR and IDB note 3000 (external, ELENA model); Climate Analytics 1.5 C page (external); PNMUS (official); AFD interview (lead) | The only model family independent of the PLANMICC's OSeMOSYS model; it counts large hydro as renewable and follows the first NDC. The PNMUS sets no number a model could take. |
| Guatemala | ENDBE UNFCCC file (official); IRENA Central America roadmap and IDB project page (external); DDP chapter, RDM guide, `GUA_LTS` repository (lead) | No Guatemala scenario results published. The NDC 3.0 credits the IDB, 2050 Pathways, UNDP and CLG; its BAU rests on two unpublished MARN reports. |
| Honduras | ENME and SEN Prospectiva (official); UNEP green economy study and World Bank CCDR (external); ENDRCH documentation (lead) | The Prospectiva compares four power and transport scenarios (CO2 19 to 56 percent below its reference in 2050); the ENME confirms 3 percent electric vehicles in 2030 but not the NDC's 7.5 percent for 2035. NDC 3.0 credits CLG-Libelula with its drafting. |
| Jamaica | World Bank and Vivid Economics 2020 (external); Climate Analytics project page (external); jam-lts documentation, six pages (lead) | The LEAP study behind the 2020 NDC update (25.4 and 28.5 percent below BAU in 2030). The LTS numbers rest on 2021 Vivid Economics reports that were not found. The jam-lts cost-benefit (preliminary) is CLG work. |

## 6. Values and names held in code

`script_constants.csv` lists 11,170 values and names written in code outside `_LAC_HUB/` (7,027 numbers, 1,282 scenario names, 660 country names and codes, 1,165 technology names and prefixes, 567 fuel names, 469 emission names). 1,977 of them sit in the 32 files that Stage 0 to 3 results depend on; 2,934 sit in the duplicate folder `models_energy_RE_generation_costs_update/`. `script_constants_accepted.csv` holds 52,301 constants of the mathematics or presentation with the reason. `scenario_names.csv` finds 12 scenario names; `structure_map.md` maps the layout against OSTRAM.

| File (Stage 0 to 3 depend on it) | Rows | of which numbers |
|---|---|---|
| Honduras/HON_ENERGY/B1_Base_Scenarios_Adj_Parallel_Honduras.py | 229 | 140 |
| DominicanRepublic/RD_ENERGY/B1_Base_Scenarios_Adj_Parallel_DominicanRepublic.py | 226 | 133 |
| Guatemala/GUA_ENERGY/B1_Base_Scenarios_Adj_Parallel_Guatemala.py | 211 | 139 |
| Jamaica/JAM_ENERGY/B1_Base_Scenarios_Adj_Parallel_Jamaica.py | 149 | 108 |
| Ecuador/ECU_Energy/B1_Base_Scenarios_Adj_Parallel.py | 140 | 93 |
| CostaRica/CR_ENERGY/t1_confection/B1_Base_Scenarios_Adj_Parallel_CostaRica.py | 116 | 53 |
| stage2_apply_v2.py | 115 | 75 |
| stage1_share_analyzer_v16.py | 105 | 58 |
| stage3_run_all.bat | 61 | 1 |
| stage0_run.py | 57 | 20 |
| stage3_results.py | 55 | 29 |
| stage3_apply.py | 50 | 30 |
| stage0_collect_outputs.py | 46 | 25 |
| A2 compilers (six files) | 196 | 173 |
| stage0_recommend_shares.py | 36 | 19 |
| stage0_capacity_check.py | 24 | 8 |
| OSeMOSYS_Model.txt (six energy copies) | 97 | 97 |
| stage2_post_clean.py, stage0_run_all.bat and .sh, stage0_clean.py, ao_safe_save.py | 64 | 20 |
| All 32 files | 1,977 | 1,221 |

The other 221 files hold 9,193 rows (sector models, plotting, tests, audits and the duplicate folder). The renewable targets typed twice (`stage1_share_analyzer_v16.py` lines 97 to 110, `stage2_apply_v2.py` lines 61 to 75) are rows of this list and are the proposed home of `scenario_values.csv`.

## 7. Gates

| Gate | Result |
|---|---|
| 1. `git diff --name-only origin/main` lists only files under the job folder | pass |
| 2. Every row of `verification_`, `analyses_` and `scenario_values.csv` has a source id in `sources.csv` and a page; no `scenario_values.csv` row cites a `lead` source | pass |
| 3. Every value of `values_to_verify.csv` has a verification row | pass (733 of 733) |
| 4. Every standard unit of `scenario_values.csv` is listed in `units.csv` | pass |
| 5. Every source file exists with a matching SHA-256 | pass (84 sources) |
| 6. `git -C /c/clw_scout_model status --short` is empty | pass |

## 8. Pull request and commits

Pull request: pending (filled in by the report-only commit).
