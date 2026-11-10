# BRIEF LAC_COST_SRC_ECU: sourced cost proposals for the Ecuador energy model

Repository: https://github.com/luviga/clewise-lac, `main` at `2ddd560`. No pull request is open at the time of writing. Five sibling jobs (one per other country) may run at the same time on their own clones and folders; they never touch this job's folder.
Main copy on this machine: `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5` (Git Bash `/c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5`). Claude Code opens there and this brief sits in its `_LAC_HUB/` folder.

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, record it, finish every step you still can, and write the three output files anyway. Never mark a pull request ready and never merge. This job changes no model file. It builds sourced proposals that a later job, LAC_COST_WRITE, writes into the workbooks.

## 1. Goal

Make every cost the Ecuador energy model uses legitimate for a least-cost model: each value externally sourced, downloaded and readable, or labelled ASSUMPTION. Output one file, `proposals.csv`, that says for every cost cell of the model's power plants, fuel supply rows and electricity imports what the value is today, what it should be, and why, plus the paper trail that tells Luis where the CLEWISE papers state these costs.

Luis's decisions, all closed:

- 8 November 2026: fuel prices are pre-tax import parity tracking the market, real 2024 USD. Model unit MUSD/PJ, equal to USD/GJ.
- 9 November 2026: each country's own published prices from LAC_LOCAL_PRICES; market over administrative prices; projections from the IEA World Energy Outlook, normalized; a multi-year average ratio to the benchmark as the anchor; gas published per MMBtu treated as gross and divided by 0.9; Ecuador fuel oil at export value and Ecuador gas at its domestic price.
- 10 November 2026: the latest WEO available now, WEO 2025, is used (WEO 2026 is not out).
- 10 November 2026: one price per fuel supply row, the pre-tax price at import or wholesale level. Generator-delivered and final-consumer prices are recorded beside it and not applied.
- 10 November 2026, plant costs: Costa Rica, Dominican Republic, Guatemala, Honduras and Jamaica keep their current capital, fixed and variable costs, and each value gets a refined source. Ecuador takes the CCG Ecuador starter kit, compared value by value with PLANMICC. Guatemala's plant variable cost unit slip is fixed. Minor upgrades are welcome: where the same publisher has a newer edition of a cited table, propose the newer value beside the old one.
- 10 November 2026: one job per country (this one), then one LAC_COST_WRITE job for all six.

## 2. The standard

Cite only external, retrievable sources: a URL, DOI, or public repository permalink with commit hash. Open every source you cite in this session, confirm the value, unit, year basis and scope are there, and save a copy of the file in this job's `downloads/` folder before you record the value. Each source record carries the exact URL that returns the file (the full query URL for an API), the page, table or sheet and cell range, the retrieval date, and the downloaded file name. Never cite internal files: workbooks, sheets, cells, markdown notes, handovers, CSVs we built, local paths, the CLEWISE paper drafts, or earlier job outputs. Those are leads only. The one exception is reuse of a source already recorded by LAC_LOCAL_PRICES: you may reuse its source id and downloaded file (copy the file into this job's `downloads/`), since that job opened and saved it.

An ASSUMPTION sentence follows Luis's rule: it states the value with its unit and coverage, a plain reason a stranger can follow with every constant stated, a check against a public document wherever one exists (cited in the source column), and a range when the value matters. It never mentions our process, jobs, files, history, rulings, or what could not be found; those go in GAPS and the search log. An ASSUMPTION is allowed only after the leads for that row are tried and logged in `search_log.csv`.

A value read from a document and converted (units, currency year, averaging, summing) is a derivation: write the formula with every constant and the source id of each constant.

Scope is frozen. Do only what section 6 lists. Anything else you find goes to GAPS under "Known-limitation candidates", with where it is and one sentence on what it is. Do not fix it.

Commits and the pull request carry no Co-Authored-By line and no "Generated with" line. A gate checks `git log`.

## 3. Rules to apply

### Fuel supply rows

F1. Units and currency year. Every price in USD/GJ on a net calorific basis, real 2024 USD. Convert nominal values of other years with the US CPI-U annual average (BLS series CUUR0000SA0, all items, US city average): download it, record it in `constants.csv`, cite it.

F2. One price per supply row: the pre-tax price at import or wholesale level, taken from `local_prices_2024.csv` of LAC_LOCAL_PRICES in this order: `wholesale import parity` that is pre-tax; then `import CIF`; then `export FOB` where the country exports the fuel and imports none; then, only where none of these is published, the closest pre-tax point, with the reason in the row. Where an administrative and a market value both exist, use the market one. Write every other published 2024 point for the row (`generator delivered`, `final consumer pre-tax`, others) into `price_points_2024.csv` beside the chosen one, with the difference in percent. Section 5 lists the row-by-row starting point.

F3. History years. For each model year up to 2025 that has an observed value for the chosen point in `local_history.csv` (or in a source you add), use it, deflated to 2024 USD. For a history year without an observed value, use the anchor ratio of F4 times the benchmark's observed value for that year.

F4. Projection. For each row, compute the ratio of the chosen local price to its benchmark for every year in `local_history.csv` (both real 2024 USD) and average it over all available years (r). If the chosen point has no history but `import CIF` has, compute r on the import CIF history and multiply it by the 2024 ratio of the chosen point to import CIF. If there is no history at all, r is the 2024 ratio alone. Record which case applies. Then, for every projected year y and fuel scenario s:

    P(y, s) = r x B(2024) x WEO_s(y) / WEO_s(2024)

  where B(2024) is the benchmark's observed 2024 annual average and WEO_s is the matching IEA WEO 2025 price series for scenario s, linearly interpolated between the years WEO publishes and held flat after its last year. Benchmarks and WEO series: oil products and crude use EIA Brent spot (RBRTE, annual average) and the WEO crude oil price; natural gas uses EIA Henry Hub (RNGWHHD) and the WEO United States natural gas price where the country's LNG is US-sourced or Henry Hub-indexed, confirmed from a published contract, regulator or company document that you cite (otherwise choose the WEO gas series that matches the published supply origin, and say why); coal uses the WEO steam coal series that matches the origin or index of the country's published coal import price (for example coal FOB Puerto Bolivar, Colombia), and the matching observed benchmark for r. Scenarios: Stated Policies (STEPS) is the central case the base model uses; Current Policies (CPS) is high; Net Zero Emissions by 2050 (NZE) is low. Projected years start in 2026, or in 2025 where no observed 2025 value exists. Report the step at the join between the last observed year and the first projected year for every row; do not smooth it.

F5. Natural gas published per MMBtu is on a gross basis; divide by 0.9 to reach the net basis. Use this ASSUMPTION sentence for every gas price: "ASSUMPTION: natural gas prices published per MMBtu are on a gross calorific basis and are converted to the models' net basis by dividing by 0.9 (net = 0.9 x gross for natural gas, UN Statistics Division), for all six countries and all years. Reason: natural gas in the Americas, Henry Hub included, is priced on a gross basis, and the energy balances behind the models follow the UN recommendation to use net values (IRES, UN 2018). Check: EIA reports US natural gas at 1,037 Btu per cubic foot, a gross value. Range: a source already on a net basis would be overstated by about 11 percent." Cite IRES (GEN-008), `UN_NGS_NET_PER_GROSS` (GEN-006) and `MMBTU_PER_MCF_EIA` (GEN-005) from LAC_LOCAL_PRICES. Gas priced per tonne of LNG with an IPCC net factor is already net.

F6. WEO 2025 is in `C:\clw_local_prices\_LAC_HUB\local_prices_20261109T085226Z\downloads\manual\WorldEnergyOutlook2025.pdf` (origin https://www.iea.org/reports/world-energy-outlook-2025, IEA, CC BY 4.0). Read the fuel price table by scenario (Table 2.32 per Luis's note; confirm the table number, its units and its currency year, and record them). Copy the PDF into this job's `downloads/`. Caveat for the method notes: WEO 2025 was written before the 2026 Middle East energy crisis.

### Power plants and other technology costs

P1. For every technology in section 5's plant list and every one of CapitalCost, FixedCost and VariableCost, in every year column of the A-O workbook: record the current value and its projection mode, then find its source, in this order:
  1. what the CLEWISE MethodsX and Data in Brief say about that cost (Step 2 gives the locations), as leads to the documents they name;
  2. IRENA Renewable Power Generation Costs in 2022 (the edition the Data in Brief cites), and the newest IRENA edition as a minor upgrade;
  3. IEA World Energy Outlook 2023 power generation technology costs (the edition cited), and WEO 2025 if it publishes the same table;
  4. the country's national expansion plan or regulator cost study;
  5. NREL Annual Technology Baseline 2024, as the last external source.
  Plant VariableCost is non-fuel variable O&M: fuel reaches plants only through the supply rows.

P2. Classify each value: `matched` (a source gives the same number within 2 percent after a stated conversion); `matched, newer edition` (matched to the cited edition, and the newer edition differs: propose the newer value and keep the old one in the row); `replace` (no source gives this number; propose the value of the first source in P1 order that covers the technology, with the change in percent); `ASSUMPTION` (no source covers the technology after the leads are logged; propose a value with its ASSUMPTION sentence). Values that change over the years: source the path as well as the level (for example the IRENA or ATB decline), or state the rule that produced it.

P3. Scope order: plants with residual capacity first, then plants that can be built, as listed in section 5. The model's Stage 3 holds each plant's yearly generation between its lower limit and 1.05 times that limit from 2025, so plant costs change total cost and capacity built, not the generation mix. Spend the effort accordingly, and keep each source search short when the effect is small.

### Electricity imports

E1. Where the model has an electricity import technology with a positive activity limit, price it at the published 2024 price the country paid for imported electricity (regional market MER or EOR prices, bilateral contract prices, or the system operator's annual report), in USD/GJ (1 USD/MWh = 0.27778 USD/GJ), real 2024 USD, held flat after 2024 with an ASSUMPTION sentence unless a published projection exists.

## 4. The paper trail

The CLEWISE papers are in Luis's OneDrive, read-only: `C:\Users\luisfernando\OneDrive - Climate Lead Group\ODI - 2_Journals\2025_P19_CLEWs++`. Find these files by name anywhere below that folder: `CLEWISE_MethodsX_v02.docx`, `CLEWISE_DataInBrief.docx`, `CLEWISE_JCLP_draft_v2.docx`, `Suplementary.xlsx`, `Data_v2.xlsx`. Copy them to a scratch folder outside OneDrive (inside this job folder under `downloads/paper/`, which is not tracked) and read the copies. Never write, rename or move anything in OneDrive. If a file is online-only and does not open, record it and continue.

For Ecuador, the Data in Brief cost table is none (the draft has no Ecuador cost table).

## 5. Facts already checked by values (hub, at `2ddd560`)

Energy folder: `Ecuador/ECU_Energy`; workbook `A1_Outputs/A-O_Parametrization.xlsx` (sheets "Primary Techs" and "Secondary Techs" hold the plant and supply cost rows). Values below are 2024 values from the BAU compiled CSVs under `A2_Output_Params/BAU/`. CapitalCost is MUSD/GW = USD/kW; FixedCost MUSD/GW per year = USD/kW-yr; VariableCost MUSD/PJ = USD/GJ (times 3.6 gives USD/MWh). "Can build more" is yes when the BAU TotalAnnualMaxCapacity leaves room above residual capacity in some year from 2025 and TotalAnnualMaxCapacityInvestment is not zero in every year.

Power plants in scope (residual capacity above 0 in 2024, or can build more):

| Technology | Residual capacity 2024 (GW) | Can build more | CapitalCost (USD/kW) | FixedCost (USD/kW-yr) | VariableCost (USD/GJ) |
|---|---|---|---|---|---|
| `PPBGS` | 0.129 | yes | 1 | 1 | 1 |
| `PPBIM` | 0.087 | yes | 2 | 2 | 2 |
| `PPCRU` | 0.242 | yes | 1 | 1 | 1 |
| `PPDDSL` | 0.202 | yes | 1 | 1 | 1 |
| `PPDFOI` | 0.069 | yes | 1 | 1 | 1 |
| `PPDSL` | 0.433 | yes | 1 | 1 | 1 |
| `PPFOI` | 0.785 | yes | 1 | 1 | 1 |
| `PPHD` | 0.648 | yes | 1 | 1 | 1 |
| `PPHDAMAB` | 1.27 | yes | 5,000.0 | 1 | 1 |
| `PPHDAMAM` | 0.33 | yes | 3,500.0 | 1 | 1 |
| `PPHDAMAS` | 0.001 | yes | 5,000.0 | 1 | 1 |
| `PPHDAMPM` | 0.286 | yes | 3,500.0 | 1 | 1 |
| `PPHDAMPS` | 0.042 | yes | 5,000.0 | 1 | 1 |
| `PPHRORAB` | 1.5 | yes | 3,500.0 | 1 | 1 |
| `PPHRORAM` | 0.487 | yes | 5,000.0 | 1 | 1 |
| `PPHRORAS` | 0.062 | yes | 3,500.0 | 1 | 1 |
| `PPHRORPM` | 0.288 | yes | 5,000.0 | 1 | 1 |
| `PPHRORPS` | 0.15 | yes | 3,500.0 | 1 | 1 |
| `PPIBIM` | 0.212 | yes | 1 | 1 | 1 |
| `PPIHD` | 0.241 | yes | 1 | 1 | 1 |
| `PPILPG` | 0.076 | yes | 1 | 1 | 1 |
| `PPNGS` | 0.524 | yes | 1 | 1 | 1 |
| `PPPVD` | 0.026 | yes | 100.0 | 1 | 1 |
| `PPPVT` | 0 | yes | 800.0 | 1 | 1 |
| `PPPVTS` | 0 | yes | 1 | 1 | 1 |
| `PPRDSL` | 0.234 | yes | 1 | 1 | 1 |
| `PPRNGS` | 0.242 | yes | 1 | 1 | 1 |
| `PPWNDD` | 0 | yes | 1 | 1 | 1 |
| `PPWNDON` | 0.017 | yes | 1,300.0 | 1 | 1 |

Fuel supply rows (consumers from `consumers.csv` of LAC_LOCAL_PRICES: power plants, final demand, refinery, export):

| Supply row | Feeds | Current VariableCost 2024 (USD/GJ) | First published point in `local_prices_2024.csv` by the order of rule F2 | Value 2024 (USD/GJ) |
|---|---|---|---|---|
| `DIST_COA` | demand 1 | 1 | import CIF | 8.913 |
| `DIST_COK` | demand 1 | 1 | import CIF | 3.794 |
| `DIST_CRU` | refinery 1, export 1 | 1 | export FOB | 11.9 |
| `DIST_DSL` | demand 9, power 3, refinery 1 | 1 | wholesale import parity | 19.3 |
| `DIST_FOI` | demand 8, power 2, refinery 1 | 1 | export FOB | 10.1 |
| `DIST_GSL` | demand 10, refinery 1 | 1 | wholesale import parity | 20.7 |
| `DIST_JET` | demand 4, refinery 1 | 1 | wholesale import parity | 18.8 |
| `DIST_KER` | demand 1 | 1 | wholesale import parity | 18.3 |
| `DIST_LPG` | demand 8, refinery 1 | 1 | wholesale import parity | 16.3 |
| `DIST_NGS` | demand 4, power 2 | 1 | generator delivered | 2.881 |
| `DIST_OPE` | demand 3 | 1 | none | none |
| `EXTT_CRU` | refinery 1, export 1 | 1 | none | none |
| `EXTT_NGS` | refinery 1 | 1 | none | none |

Country notes:

- Ecuador's A-O year columns start in 2021. Plant cost rows are mode `Flat` with the value in the first year column.
- Placeholders, checked by values in the BAU compiled CSVs: FixedCost is 1 on 30 of 31 power plants; CapitalCost is 1 on 17 of 31 (every thermal plant, gas, geothermal, storage PV, distributed wind); VariableCost is 1 on every plant and every supply row. Real numbers exist only for hydro capital (3,500 or 5,000 USD/kW), utility PV 800, wind 1,300 and distributed PV 100. Non-plant rows at 1 for CapitalCost, FixedCost and VariableCost: `ADD_GRE`, `DIST_BGS`, `DIST_BIM`, `DIST_CHA`, `DIST_COA`, `DIST_COK`, `DIST_CRU`, `DIST_DSL`, `DIST_FIR`, `DIST_FOI`, `DIST_GSL`, `DIST_JET`, `DIST_KER`, `DIST_LPG`, `DIST_NGS`, `DIST_OID`, `DIST_OPE`, `DIST_RDF`, `ELE_DIST`, `ELE_TRANS`, `EXTT_CRU`, `EXTT_NGS`, `HYD_DIST`, `HYD_G_PROD`, `IMPELE`, `PROCRU`, `PRONGS`, `STOELE`; VariableCost also `REF_DSL`, `REF_FOI`, `REF_GSL`, `REF_JET`, `REF_LPG`, `REF_OPE`. Every one of these rows gets a proposal in this job.
- The Data in Brief has no Ecuador cost table. Read the MethodsX for anything it says about Ecuador costs.
- Luis's decision (10 November 2026): Ecuador's plant and other cost values come from the CCG Ecuador starter kit, and every value is compared with PLANMICC.
  - CCG Starter Data Kit: Ecuador, v1.0, 9 September 2021, Zenodo record https://zenodo.org/record/5498094 (open). Download every file of the record into `downloads/`. The kit's method is described in Allington et al. 2022, Data in Brief 42, 108021, https://doi.org/10.1016/j.dib.2022.108021 (CC BY 4.0): South America costs come from the SAMBA model base, in 2020 USD; its fixed costs include variable O&M; fossil plant costs are flat over time; renewable cost declines follow IRENA trends (its Table 13). Download the article PDF too.
  - PLANMICC Ecuador OSeMOSYS model: https://github.com/PLANMICC/OSeMOSYS_Ecuador, `main` at commit `7483e67a5a7a733b4a2697a950eda23a27929df7`. Cite files by permalink at that commit. Compiled BAU costs: `Energia/t1_confection_CON_TCE/A2_Output_Params/BAU/CapitalCost.csv`, `FixedCost.csv`, `VariableCost.csv`. Source workbook: `Energia/Data_inputs/Calibracion y BAU/Requerimiento_Datos_Energia_Costos_Ecuador_v6.xlsx`, sheet "Costos Sector Eléctrico (v2)", whose first column gives a source code per row and whose "Referencias Bibliográficas" block lists: 1 and 2 "Información Solicitada" (data supplied on request by the government), 3 IEA WEO 2022 Table B.4a, 4 the ELENA model, 5 a Galápagos energy scenarios study (Table 4.10), 6 a Brazil CSP paper (Table A5). Hub-checked 2024 values (USD/kW, USD/kW-yr): gas turbine `PP_NGSTGS` 1,000 and 21.1; diesel engine `PP_DSLICE` 1,200 and 20; fuel oil engine `PP_FOIICE` 1,070 and 20; fuel oil steam `PP_FOITST` 1,770 and 44.3; utility PV `PP_SPV_US` 963.3 and 13.6; wind `PP_WND_US` 1,552.8 and 34.3; large reservoir hydro 1,572.5 and 42; geothermal `PP_GEO` 5,000 and 102. The repository is large: clone it with `git clone --depth 1 --filter=blob:none --no-checkout` and fetch single files with `git show HEAD:<path>`, with a time limit on each command.
  - Rule for Ecuador proposals: the proposed value is the CCG value converted to real 2024 USD (US CPI, rule F1), mapped to our technology. Record the PLANMICC value and its source code beside it, and flag every pair that differs by more than 25 percent. Where CCG has no counterpart for a row, propose the PLANMICC value when its source code is 3, 4, 5 or 6 (published documents), citing the permalink and the document; for code 1 or 2 rows, cite the PLANMICC permalink as the published dataset and say in the row that the figure was supplied by the government to PLANMICC. Where neither has a counterpart, use rule P2.
  - Because CCG fixed costs include variable O&M, propose VariableCost 0 for plants taken from CCG and state it in the derivation; record PLANMICC's variable O&M beside it.
  - Map our hydro rows (`PPHDAMAB`, `PPHDAMAM`, `PPHDAMAS`, `PPHDAMPM`, `PPHDAMPS`, `PPHRORAB`, `PPHRORAM`, `PPHRORAS`, `PPHRORPM`, `PPHRORPS`: dam or run-of-river, Amazon or Pacific basin, big, medium or small) to CCG's large, medium and small hydro classes and to PLANMICC's basin and size rows; write the mapping in `mapping_ECU.csv`.
  - Import and distribution rows (`DIST_*`) carry the fuel price in VariableCost; propose CapitalCost and FixedCost 0 for them with an ASSUMPTION sentence. Transmission, distribution, refinery, gas processing and storage rows (`ELE_TRANS`, `ELE_DIST`, `PROCRU`, `PRONGS`, `REF_*`, `STOELE`) take CCG values where the kit has them (CCG Table 23 gives refinery costs) and PLANMICC values otherwise.
- Fuel decisions for Ecuador (decision 6): fuel oil `DIST_FOI` at export FOB (EP Petroecuador, 10.106 USD/GJ in 2024); crude at export FOB (11.864 USD/GJ in 2024); natural gas at the observed domestic price to generators (2.881 USD/GJ gross in 2024, 3.201 net under F5). Ecuador's terminal prices for diesel, gasoline, LPG, jet and kerosene are administered; under decision 2 use the market import unit values (`import CIF` rows of EP Petroecuador) for those rows and record the terminal prices beside them. Natural gas is an administered domestic price with no import benchmark: hold it flat in real terms from 2025 at the mean of its observed real values, with an ASSUMPTION sentence, in all three fuel scenarios.
- `EXTT_CRU` and `EXTT_NGS` are domestic extraction rows. Propose a sourced production cost where CCG or PLANMICC gives one; otherwise rule P2.
- `IMPELE` (electricity imports, Colombia and Peru): quantity fixed by activity limits (1.675 to 1.759 PJ a year in BAU), current price 1. Step 6 applies.
- `DIST_OPE` (other petroleum products) has no row in `local_prices_2024.csv`; price it from a published Ecuador source or rule P2.

Other facts:

- LAC_LOCAL_PRICES is merged on `main`: `_LAC_HUB/local_prices_20261109T085226Z/` holds `local_prices_2024.csv` (176 price points), `local_history.csv` (330 rows, 2018 to 2025, nominal), `sources.csv` (352 sources), `constants.csv` (90 constants), `calorific_basis.csv`, `consumers.csv`, and per-country notes in `country/<CC>/notes_<CC>.md`. Its downloaded files are only on this machine, in `C:\clw_local_prices\_LAC_HUB\local_prices_20261109T085226Z\downloads\`.
- Observed benchmark series (EIA Brent, Henry Hub, US Gulf Coast products) are listed with URLs in `_LAC_HUB/price_sources_20261109T003525Z/benchmarks.csv`; download the annual series you use again into this job's `downloads/`.
- The 2018 to 2025 history in `local_history.csv` is nominal and mostly `import CIF`.

## 6. Setup

- Environment: Windows, Git Bash, the `py` launcher. Run your scripts with `py -I`. pandas, openpyxl, pdfplumber, pypdf and PyMuPDF are installed. Install nothing else. Use your web search and web fetch tools. You may split the work into sub-tasks.
- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Use it in the job folder name and the three output file names.
- New clone from the local main copy, then point it at GitHub:

```bash
git clone /c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5 /c/clw_cost_ecu
cd /c/clw_cost_ecu
git remote set-url origin https://github.com/luviga/clewise-lac.git
git fetch origin
git checkout -b job/cost-src-ecu 2ddd560
```

  If `2ddd560` is missing from the local clone, clone from GitHub instead and branch from the same commit.
- Job folder: `C:\clw_cost_ecu\_LAC_HUB\cost_src_ecu_<stamp>\`, with `downloads\` inside it. `.gitignore` keeps `/_LAC_HUB/**/downloads/` and every PDF, HTML, DOCX and PPTX under `_LAC_HUB` out of commits.
- Write only inside the job folder. The pull request adds files there and nowhere else.
- Read-only: every other file in `C:\clw_cost_ecu`, the main copy `MODELS_LAC_5`, `C:\clw_local_prices` and every other `C:\clw_*` folder, and the OneDrive paper folder. Do not open anything under `C:\Users\luisfernando\Dropbox\`.
- Expected run time: 6 to 10 hours. Sleep must be off on the machine.

## 7. Work

### Step 1. Baseline

Record SHA-256 of `Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx` and of the BAU `CapitalCost.csv`, `FixedCost.csv`, `VariableCost.csv`, `InputActivityRatio.csv` and `OutputActivityRatio.csv` under `Ecuador/ECU_Energy/A2_Output_Params/BAU/` in the clone (`baseline_before.csv`).

### Step 2. Paper trail

Read the copies of the paper files (section 4). For every passage, table or cell that states a cost value, a cost source, a fuel price or a fuel price method relevant to Ecuador or to all countries, write a row in `paper_trace.csv`: document, section and heading, table or figure number, the first eight words of the paragraph (to find it), the statement or value as written, the model rows it concerns, and what it will need to say if this job's proposals are applied (one sentence). Do not edit the papers.

### Step 3. Current cost rows

Read the A-O workbook with cached values (pandas or openpyxl `data_only=True`). For every row of "Primary Techs" and "Secondary Techs" whose parameter is CapitalCost, FixedCost or VariableCost, write `cost_rows_current.csv`: sheet, Tech.ID, Tech, Tech.Name, Parameter, Unit, Projection.Mode, Projection.Parameter, every year column. Add a scope column: `plant in scope` (section 5 list), `supply row`, `electricity import`, or `other` (other rows are listed only, unless the country notes say otherwise). Confirm the section 5 values by recomputing them; record any difference in GAPS.

### Step 4. Fuel price series

For every supply row in section 5, apply F1 to F6. Outputs: `fuel_prices.csv` (row, fuel, year, scenario STEPS, CPS or NZE, value USD/GJ net real 2024, case: observed, history from ratio, or projected; r and how it was computed; benchmark; WEO series; source ids) and `price_points_2024.csv` (rule F2). Write the WEO values you used, with page and table, into `constants.csv`.

### Step 5. Plant and other technology costs

Apply P1 to P3 to every plant in section 5, and to the other rows the country notes name. Log every lead in `search_log.csv` (row, lead, URL or query, date, result). Output `plant_costs.csv`: technology, parameter, year, current value, proposed value, class (P2), source ids, derivation, ASSUMPTION sentence where used.

### Step 6. Electricity imports

Apply E1 where the country notes say so. Output the rows into `plant_costs.csv` with technology set to the import technology.

### Step 7. Country task

Do what the country notes in section 5 ask beyond Steps 4 to 6.

### Step 8. Proposals file

Write `proposals.csv`, the only file LAC_COST_WRITE reads. One row per cell to write: country, sheet, Tech.ID, Tech, Parameter, fuel_scenario (`ALL` for plant and import rows; `STEPS`, `CPS` or `NZE` for fuel rows), year, current_value, proposed_value, unit, change_class (`keep`, `upgrade`, `replace`, `fill_placeholder`, `unit_fix`, `fill_empty`), basis_class (`matched`, `matched, newer edition`, `replace`, `ASSUMPTION`, `observed`, `history from ratio`, `projected`), source_ids, derivation, assumption_sentence. Cover every year column of the workbook for each proposed row. A `keep` row repeats the current value with its new source. Also write `proposals_summary.csv`: one row per technology and parameter with the 2024, 2030 and 2050 current and proposed values and the change in percent. `structure_proposals.csv` (Costa Rica only, Step 7) is separate.

### Step 9. Gates

1. Read-only: recompute the Step 1 hashes (`baseline_after.csv`); they equal `baseline_before.csv`.
2. After the commit, `git diff --name-only 2ddd560 HEAD` lists only files inside `_LAC_HUB/cost_src_ecu_<stamp>/`.
3. Tracked files in the job folder are only `.md`, `.csv`, `.py` and `.txt`; `git ls-files` shows nothing under its `downloads/`.
4. Sourcing check, as a script with counts in REPORT: every `proposals.csv` row whose basis is not `ASSUMPTION` names source ids that exist in `sources.csv`; every source has an http(s) URL, a page or table locator, a retrieval date and a file present in `downloads/`; no source field holds a local path or an internal file.
5. Every ASSUMPTION row has its leads in `search_log.csv`, and its sentence passes the ASSUMPTION rule of section 2 (no words about jobs, files, searches or what was not found).
6. Coverage: every plant in section 5, every supply row in section 5 and, where Step 6 applies, the import technology have proposals for every year column and, for fuel rows, all three scenarios.
7. `git diff --check` passes; no output file contains an em dash or a machine path outside quoted URLs and the copied brief; `git log -3 --format=%B` contains no "Co-Authored-By" and no "Generated with".

### Step 10. Pull request

- Copy this brief into the job folder as `BRIEF_LAC_COST_SRC_ECU.md`.
- One commit with the job folder's tracked files, message "LAC_COST_SRC_ECU: sourced cost proposals for Ecuador", no trailer lines. Push `job/cost-src-ecu` and open one draft pull request with the same title, body taken from CHANGES, no trailer lines.
- If the push or the pull request fails, keep the local commit, record the exact error in REPORT, and finish the outputs.

## 8. Outputs

All three in `_LAC_HUB/cost_src_ecu_<stamp>/`, plain English, no em dashes.

`REPORT_LAC_COST_SRC_ECU_<stamp>.md`: pull request number, branch, commit hash; gate results with counts. Then a table of fuel supply rows: chosen point, 2024 value, current value, r and its case, STEPS 2030 and 2050, CPS and NZE 2050, step at the join. Then a table of plants: for 2024, current and proposed CapitalCost, FixedCost and VariableCost, the P2 class and source. Then electricity imports, the country task, and the count of ASSUMPTION rows with their technologies. Then the paper trail: how many statements in each document and what changes.

`GAPS_LAC_COST_SRC_ECU_<stamp>.md`: every judgement call and its reason; each ASSUMPTION row with the leads tried; proposed changes above 25 percent with their likely cause; sources blocked or paywalled; "Known-limitation candidates"; anything left unchecked; incidents.

`CHANGES_LAC_COST_SRC_ECU_<stamp>.md`: every file created or downloaded, with its purpose or origin URL in one line; confirmation that no model file changed.

Supporting files: `baseline_before.csv`, `baseline_after.csv`, `paper_trace.csv`, `cost_rows_current.csv`, `fuel_prices.csv`, `price_points_2024.csv`, `plant_costs.csv`, `proposals.csv`, `proposals_summary.csv`, `sources.csv`, `constants.csv`, `search_log.csv`, any mapping or structure file the country notes ask for, your helper scripts, and `downloads/` (local only).
