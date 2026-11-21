# REPORT LAC_NDC_SCOUT 20261121T204620Z

Published NDC and LTS documents of Costa Rica, the Dominican Republic, Ecuador, Guatemala, Honduras and Jamaica, read against the model scenarios BAU, NDCNEW and LTSNEW at `481a7c0`. Read-only for the models: no workbook, CSV, compiled file, script or stage output was changed. Branch `job/ndc-scout` from `origin/main` at `29dc938`.

## 1. Failed, blocked or pending items

1. **Solved results do not follow the compiled inputs (all six countries in some scenario).** Stage 3 replaces the plant activity limits from 2025 with controller values, so solved generation breaks the compiled `B1_Output_Params` limits. Hub-confirmed examples:

   | Country | Scenario, year, plant | Compiled limit (PJ) | Solved (PJ) |
   |---|---|---|---|
   | Costa Rica | LTSNEW 2035, PWRDSL | lower 2.1871 | 0.2247 |
   | Costa Rica | LTSNEW 2035, PWRFOI | lower 4.4409 | 0.4561 |
   | Guatemala | NDCNEW 2030, PPCOA | lower 12.5965, upper 13.8562 | 17.2176 |
   | Jamaica | NDCNEW 2030, PPFOI | upper 0 | 3.4535 |

   The Ecuador and Honduras tasks report the same pattern (Ecuador NDCNEW 2035 floors 255.7 PJ against 153.3 PJ solved; Honduras 306 technology-years outside the compiled limits, none outside the Stage 2 controller). The solved renewable share therefore comes from the Stage 1 and Stage 2 control curves (`stage1_share_analyzer_v16.py` lines 97 to 110, `stage2_apply_v2.py` lines 61 to 75, as traced by the country tasks), not from `B1_Scenario_Config.xlsx`. A proposal that changes only a B1 row will not move the solved result. In Costa Rica NDCNEW and BAU follow the compiled limits; only LTSNEW does not.
2. **UNFCCC long-term strategies portal not read.** Scripted fetches got a bot-check page. In the browser pane it showed a CAPTCHA, which the hub did not attempt. An archive.org copy was refused by the session permission system. A web search found no LTS submission by the Dominican Republic or Ecuador (leads only). The LTS status of each country therefore rests on the documents themselves and on Climate Policy Radar listings.
3. **Sources pending (12 rows in `sources_pending.csv`):**
   - Costa Rica: ICE generation expansion plan 2022-2040, which NDC 3.0 cites for its 95 percent renewable target; UNFCCC Spanish original of the 2015 INDC.
   - Dominican Republic: the LT-LEDS that NDC 3.0 names (no copy found); the Plan Energetico Nacional 2025-2038.
   - Ecuador: urban mobility policy (PNMUS) and electromobility strategy (ENEM).
   - Guatemala: the ENDBE as filed on the UNFCCC portal (the FAOLEX copy is used).
   - Honduras: the ENDRCH long-term strategy (in preparation, not published), the electric mobility strategy (ENME) and the NDC 3.0 technical annex.
   - Jamaica: the UNFCCC copy of the LTS (the Climate Policy Radar copy is used); no BTR1 or NID is published.
4. **Ecuador long-term plan not read in full.** The PLANMICC 2024-2070 (ECU-03) was read in full for p.90 to p.147 (scenarios and targets); its other chapters were searched by keyword only.
5. **Hub correction.** The Ecuador task had compared emission targets with a sum of four emission labels. The hub recomputed those five alignment rows from the single label `CO2e_sources` (`scripts/hub_fix_ecu_emissions.py`) and edited the matching text.

## 2. Countries

Model values below are NDCNEW unless stated. "Renewable share" is the solved share of generation; renewable plant types are hydro, solar PV, wind, geothermal, biomass and biogas (listed per country in `model_levers_<code>.csv`).

### Costa Rica (CR)

- **Published:** NDC 3.0 for 2025 to 2035 (CR-01), submitted 14 November 2025. Long-term strategy: National Decarbonization Plan 2018-2050 (CR-02 English, CR-03 Spanish), net zero by 2050 (CR-02 p.12). BTR1 (CR-06, 2024, no projections) and the 1990-2021 NID (CR-07). New since 1 January 2025: NDC 3.0 only.
- **Headline targets:** net emissions at most 11,380 Gg CO2e in 2030 and a 2025-2035 budget of 132,700 Gg CO2e, economy-wide, mostly conditional (CR-01); 95 percent renewable generation from 2027 (CR-01 p.46); electric shares in 2035 of 20 percent of light vehicles, 10 percent of public transport, 5 percent of heavy freight and 15 percent of light freight (CR-01).
- **Five largest disagreements** (`changes_since_paper_CR.md`):
  1. Heavy freight: 0.300 of output electric in 2035 against 5 percent of the fleet (ratio 6.0); light freight 0.300 against 15 percent (2.0).
  2. Buses: 0.100 electric in 2030 against 3.5 percent (2.86); 0.299 in 2035 against 10 percent (3.0).
  3. Public passenger demand grows 1.35 and 2.98 percent by 2030 and 2035 against the NDC's +10 and +20 percent on 2025 (0.135 and 0.149).
  4. Black carbon: the NDC cuts 20 percent against 2021 by 2030; model transport black carbon rises 2.2 percent (opposite direction).
  5. Fossil generation: 10.0 percent of 2035 generation against at most 5 percent (renewable 0.900 against 0.95).
- **Proposed changes:** 20 class A, 8 class B, 0 class C, 7 levers where the documents are silent.

### Dominican Republic (DR)

- **Published:** NDC 3.0 RD-2025 (DR-01), uploaded to the UNFCCC in June 2026. No long-term strategy submitted; NDC 3.0 names an LT-LEDS without a copy; the national plan cited is the National Development Strategy 2030 (DR-06, Law 1-12, 2012). BTR1 with the fourth national communication (DR-04, 30 December 2025) and the 1998-2022 NID (DR-05). New since 1 January 2025: DR-01, DR-04, DR-05.
- **Headline targets:** 28 percent below BAU in 2030 (14,732.1 kt CO2eq; 8.5 points unconditional, 19.5 conditional) and 32 percent in 2035 (18,349.32 kt CO2eq) (DR-01 p.14, p.62); 1,429 MW of new gas combined cycle (DR-01 p.148) and 1,529 MW of new solar, wind and hydro by 2030 (DR-01 p.149); a small modular reactor of up to 300 MW by 2035 (DR-01 p.151).
- **Five largest disagreements:**
  1. New gas combined cycle: 1,429 MW in the NDC; 0 MW buildable in NDCNEW (`B1_Scenario_Config.xlsx`, Electrical, row 128, PPCCTNGSDSL maximum capacity 0).
  2. New renewable capacity 2025 to 2030: model 4,437 MW against 1,529 MW (2.90).
  3. Energy emission cut (label `CO2e_sources`): 49.9 percent in 2035 against the 32 percent economy-wide target (1.56); 22.7 percent in 2030 against 28 percent (0.81).
  4. Renewable share 2030: 42.1 percent against the 30 percent ministry target reported in BTR1 (DR-04 p.174, ratio 1.40); the model holds 75 percent from 2035, a level no document states.
  5. No model counterpart for the small modular reactor, two monorails and a cable car.
- **Proposed changes:** 5 class A, 3 class B, 1 class C, 7 documents silent.

### Ecuador (ECU)

- **Published:** Second NDC 2026-2035 (ECU-01, February 2025). No LTS submitted; the NDC calls the PLANMICC 2024-2070 (ECU-03, August 2024) its long-term strategy. BTR1 with the fifth national communication (ECU-04, December 2024) and the NID 2022 (ECU-05). Sector plans: Plan Maestro de Electricidad 2023-2032 (ECU-07), national efficiency plan (ECU-08), green hydrogen roadmap (ECU-09). New since 1 January 2025: the second NDC only.
- **Headline targets:** 7 percent below the trend scenario in 2035 (about 8,800 kt CO2eq) unconditional, plus 8 percent with support (ECU-01 p.55, p.56); PLANMICC 2035 hydro about 64 percent and non-conventional renewables about 24 percent of generation, 54 and 35 percent in 2050 (ECU-03 p.104); energy-sector emissions 39,200 Gg in 2035 and 35,800 Gg in 2050 (ECU-03 p.102).
- **Five largest disagreements:**
  1. Hydro: 4,034 MW added 2023 to 2032 in the power plan (ECU-07 p.159) against 144 MW added 2025 to 2035 in the model (0.036).
  2. Solar and wind 2050: about 3,800 MW in the PLANMICC against 21,104 MW in LTSNEW (5.55).
  3. Road transport energy 2035: PLANMICC saves 2.8 percent against trend; NDCNEW cuts 29.0 percent (10.3).
  4. End-use electrification: PLANMICC about 66 percent (residential) and 64 percent (industry) electric by 2050; the model keeps BAU shares of 38.3 and 44.6 percent.
  5. Energy emission levels (label `CO2e_sources`, which leaves out fugitive and refinery emissions): 32,765 kt in 2035 against 39,200 Gg (0.84); NDCNEW rises to 43,664 kt in 2050 against 35,800 Gg (1.22).
- **Proposed changes:** 7 class A, 5 class B, 2 class C, 2 documents silent.

### Guatemala (GUA)

- **Published:** NDC 3.0 (GUA-01, UNFCCC folder 2026-11). Long-term strategy: ENDBE (GUA-04, 2018). BTR1 with the NID (GUA-05, March 2025) and the 1990-2018 inventory report (GUA-06). Sector plan: Plan Nacional de Energia 2017-2032 (GUA-07). New since 1 January 2025: GUA-01 and GUA-05.
- **Headline targets:** net emissions 23.7 percent below BAU in 2035 (57,763.7 kt against 75,738.0 kt; GUA-01 p.28, p.131), 88.4 percent of it from forests; at least 80 percent renewable generation in 2035 (GUA-01 p.40); at least 1,000 MW of new renewables; E10 from 2026; 10,000 more electric and 20,000 more hybrid vehicles than in 2025.
- **Five largest disagreements:**
  1. Electric vehicles: 10,000 more (at most 0.27 percent of the fleet) against 20 percent of road output electric in 2035 (73).
  2. Energy cut 2035: 1,184.9 kt in the NDC against 8,479 kt in NDCNEW; cumulative 2026 to 2035 7,211.6 against 40,632 kt (5.6).
  3. Renewable share 2035: 75 percent against a floor of at least 80 percent (0.94, inside the 10 percent band but below a stated minimum).
  4. New renewable capacity 2025 to 2035: 4,104 MW against at least 1,000 MW.
  5. No model counterpart for the Aerometro cable car or household electricity access; hybrids stay at BAU.
- **Proposed changes:** 6 class A, 2 class B, 2 class C, 6 documents silent.

### Honduras (HON)

- **Published:** NDC 3.0 (HON-01, submitted 21 January 2026); second NDC update (HON-02, April 2025; the brief's lead record `..._21f1` is this document, not NDC 3.0). No long-term strategy submitted or published (ENDRCH in preparation, HON-01 p.14, p.15). BTR1 (HON-05, December 2024), NIR 2024 (HON-06), BUR2 (HON-07), and the approved PIEG 2026-2035 (HON-08, September 2026).
- **Headline targets:** 12,847.2 Gg CO2e below a BAU of 65,616.6 Gg in 2035 (19.6 percent) and 8,564.8 Gg below BAU in 2030, all conditional (HON-01 p.23, p.25); 70 percent renewable generation by 2030, held to 2035; electric fleet 3 percent by 2030 and 7.5 percent by 2035; hybrids 20 percent of light and 15 percent of freight vehicles by 2035; 5 percent biofuels in transport by 2030 (HON-01 p.26, p.27).
- **Five largest disagreements:**
  1. Energy cut: 964 kt (2030) and 2,482 kt (2035) against 2,519.1 and 3,778.6 Gg (0.38 and 0.66).
  2. Power sector: the PIEG cuts power CO2 by 49 percent from 2025 to 2030; NDCNEW power CO2 rises 3.0 percent (opposite direction); renewable share 64.8 percent in 2030 against the 70 percent floor.
  3. Hybrids: none in NDCNEW cars against 20 percent of light vehicles.
  4. Electric vehicles: 10 and 20 percent of road output in 2030 and 2035 against 3 and 7.5 percent of the fleet (3.3 and 2.7).
  5. Biofuels: about 2.3 percent of transport energy (ethanol in gasoline only) against 5 percent (0.46).
- **Proposed changes:** 8 class A, 1 class B, 2 class C, 5 documents silent.

### Jamaica (JAM)

- **Published:** NDC 3.0 (JAM-01, September 2025). Long-term strategy: 2050 Long-term Emission Reduction and Climate Resilient Strategy (JAM-02, cover November 2023; UNFCCC submission 29 August 2025 per the brief's lead). No BTR1 or NID published; newest inventory documents are the 2018 Third National Communication (JAM-06) and BUR1 (JAM-05). Sector plan: IRP-2 (JAM-07, August 2023).
- **Headline targets:** energy and cement emissions 16.3 percent below 2012 in 2030 and 16.9 percent in 2035 unconditional, 19.6 and 28.3 percent conditional (JAM-01 p.2, p.4, p.5); renewable share of net generation 50 percent in 2030 and 63 percent in 2035; system losses 17.7 and 16.45 percent (JAM-01 p.14); LTS 73 percent below 2020 by 2050, indicative net zero by 2060 (JAM-02 p.13), HFO phase-out by 2035 and fossil generation phase-out by 2040.
- **Five largest disagreements:**
  1. Renewable share: 39.1 percent in 2030 against 50 percent, 75.0 percent in 2035 against 63 percent.
  2. Grid losses: fixed at 21.3 percent in every scenario against 17.7 and 16.45 percent.
  3. Road fuel efficiency: the policy scenarios reset road emission factors to raw values from 2025, while BAU improves them 4.8 percent by 2030 and 23 percent by 2050 (`B1_Scenario_Config.xlsx`, SmartGrid rows 15 to 18); the LTS asks for 15 percent by 2030.
  4. HFO and fossil phase-out: LTSNEW keeps 162 MW of fuel oil plant and 1.66 PJ of its generation in 2035, and 17 percent fossil generation in 2040.
  5. Buildings and cement: LPG in 2050 is 121 percent of 2021 against 10 percent of 2020 in the LTS; no cement measure in the model.
- **Proposed changes:** 14 class A, 3 class B, 1 class C, 5 documents silent.

## 3. Cross-country table

Full table: `cross_country_summary.csv`. Alignment status counts:

| Country | Current NDC | LTS | Matches | Same direction, different size | Opposite | In documents, not in model | In model, not in documents | Not compared | A | B | C | Silent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CR | NDC 3.0, Nov 2025, 2030 cap and 2025-2035 budget | Decarbonization Plan 2019, net zero 2050 | 10 | 17 | 2 | 14 | 6 | 15 | 20 | 8 | 0 | 7 |
| DR | NDC 3.0, 2026, minus 28 and 32 percent against BAU (2030, 2035) | none submitted | 2 | 13 | 0 | 6 | 5 | 15 | 5 | 3 | 1 | 7 |
| ECU | Second NDC, Feb 2025, minus 7 percent against trend 2035 | none submitted (PLANMICC 2024-2070) | 1 | 15 | 1 | 8 | 4 | 12 | 7 | 5 | 2 | 2 |
| GUA | NDC 3.0, 2026, minus 23.7 percent against BAU 2035 | ENDBE 2018, no binding target | 5 | 15 | 0 | 2 | 4 | 9 | 6 | 2 | 2 | 6 |
| HON | NDC 3.0, Jan 2026, minus 19.6 percent against BAU 2035 | none published | 8 | 26 | 2 | 3 | 5 | 49 | 8 | 1 | 2 | 5 |
| JAM | NDC 3.0, Sep 2025, minus 16.3 and 16.9 percent against 2012 | LTS 2023/2025, minus 73 percent by 2050 | 13 | 27 | 3 | 12 | 4 | 19 | 14 | 3 | 1 | 5 |
| Total | | | 39 | 113 | 8 | 45 | 28 | 119 | 60 | 22 | 8 | 32 |

Every NDC now in force has target years of 2030 and/or 2035, which fits the model design (NDC measures to 2035, then held). Costa Rica and Jamaica have long-term strategies with 2050 goals; the Dominican Republic, Ecuador and Honduras have none submitted, and Guatemala's (2018) sets no binding target.

## 4. Counts

- Sources: 46 (`sources.csv`), each downloaded and opened, with SHA-256; 12 pending rows.
- Targets: 549 (CR 98, DR 66, ECU 76, GUA 79, HON 101, JAM 129). Projection rows: 505 (CR 36, DR 41, ECU 129, GUA 70, HON 151, JAM 78).
- Alignment rows: 352. Proposed changes: 122 rows (60 A, 22 B, 8 C, 32 documents silent).
- Hub value check (`scripts/hub_check_values.py`, `parts/hub_value_check_<code>.csv`): every target and projection value was searched on the cited PDF page. 1,031 of 1,054 rows were found automatically. The other 23 (non-numeric rows, numbers printed in words, zero values for phase-out or neutrality targets, one number with a broken space) were opened by the hub and confirmed. Hub recomputed selected model values of the alignment files from `model_levers_<code>.csv` (DR emissions and capacity, CR and GUA and JAM plant limits against solved values): equal.

## 5. Gates

| Gate | Result | Detail |
|---|---|---|
| E1 `git diff --name-only origin/main` lists only job folder files | pass | 0 files outside `_LAC_HUB/ndc_scout_20261121T204620Z/` |
| E2 every row of targets_, projections_, alignment_ has a known source id and a page or table | pass | 1,406 rows, 0 failing (`parts/gate_results.csv`) |
| E3 every source file exists with matching SHA-256 | pass | 46 of 46 |
| E4 spot check ends ten of ten for every country | pass | round 1, 10 of 10 in all six countries (`spot_checks.csv`) |
| E5 `git -C /c/clw_scout_model status --short` empty | pass | empty; worktree at `481a7c0` |

## 6. Pull request and commits

- Start: `origin/main` at `29dc938`. Model state read at `481a7c0`.
- Work-in-progress commits: `4e8b521` (setup, C1), `d72ed60` (pair 1), `2f6095a` (pair 2), `405d3aa` (pair 3, merged step D tables).
- Final commit and pull request number: see the last section, added after the pull request was opened.
