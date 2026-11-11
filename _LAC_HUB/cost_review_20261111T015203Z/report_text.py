"""Hand-written text of the review pack (answers, judgement calls), used by step8_report.py."""

PR_BLOCK = """- Branch: `job/cost-review`, from `2ddd560`, in a fresh clone at `C:\\clw_cost_review`.
- Pull request: #8, a draft titled "LAC_COST_REVIEW_PACK: checked review pack for the six country cost jobs". #8 was the next free number in luviga/clewise-lac when this report was written (the latest was #7). If GitHub assigned another number, the pull request page is the record.
- Commit: the single commit on `job/cost-review` with the message above. A file cannot carry the hash of the commit that contains it, so the hash is on the pull request page (Commits tab) and in `git log -1 job/cost-review`.
- The six branches were fetched at the heads the brief lists, with no difference: jam `789b36a` (PR 2), hon `79a3665` (PR 3), ecu `ddd8d31` (PR 4), dr `a0c2845` (PR 5), gua `0703ae2` (PR 6), cr `7e8dd76` (PR 7). All six pull requests were open drafts when fetched."""

TABLE_NOTES = """Notes to the table:
- Gates are this job's reruns (section 5, step 2 of the brief), not the jobs' own results. Full counts are in `gates.csv`.
- Value checks are explained in section 2 of GAPS. "Found" means the number as published before conversion was found in the row's downloaded source files. "Not found" means the files were searchable and the number did not appear. "Not run" means there was nothing to search: the proposed value is 0, 1 or empty and the derivation states no other number. No check ended "not run" because its files could not be read. Each row of `value_checks.csv` gives the number searched, the file and the location.
- Flag severity: high is a value outside a physical screen, or an unexplained 0 or 1 on an in-scope row. Medium is a change above 25 percent from a real current value, or a step above 20 percent at the join. Low is a change from a placeholder, or a 0 that a source or brief rule states. All flags are in `review_flags.csv`."""

RECOMPUTE_NOTE = """The automatic recompute evaluates each "a x b / c = d" chain written in a derivation once words, units, year labels and descriptive brackets are removed. It left {n} expressions above 0.5 percent. Each was recomputed by hand from the numbers the derivation states, and {m} of {n} match: the parser had read a percent sign, an edition year or a label as an operand (column `hand_review` of `derivation_recompute.csv`). No derivation was found wrong by more than 0.5 percent. Separately, every projected fuel series (row and scenario) was checked against rule F4: projected value / WEO 2025 value for the year is constant, with the WEO series linear between 2024, 2035 and 2050. All 165 series checked follow their WEO path within 0.5 percent. Six Ecuador series were not tested: `DIST_NGS`, held flat by its brief, and `DIST_OPE`, an ASSUMPTION copy of the fuel oil series, which is tested as `DIST_FOI`."""

CROSS_TEXT = """Findings:
- **WEO 2025.** The table is Table 2.3 "Wholesale fossil fuel prices by scenario", page 109, in USD (MER, 2024), with years 2024, 2035 and 2050. The briefs called it Table 2.32. I read the page from the PDF in this job, and the WEO 2025 PDF is byte-identical in all six jobs' downloads. Every value each country recorded equals the published one: crude oil in 6 of 6 countries, US gas and EU steam coal in 5 of 6, Japan steam coal in 1.
- **One series disagrees.** Ecuador uses WEO steam coal Japan (151, 100 and 84 for 2024 and STEPS 2035 and 2050) with the World Bank Australian (Newcastle) coal price as observed benchmark. The other five use European Union coal with South African (Richards Bay). Ecuador's GAPS item 4 explains why: 95 percent of its 2024 anthracite came from Peru, on the Pacific. With no coal history, r is the 2024 ratio, so the choice sets only the path: STEPS 2050 is 56 percent of 2024 under Japan and 59 percent under the EU series.
- **US CPI-U (BLS CUUR0000SA0, annual average).** Identical in all six for 2018 to 2025 (2024: 313.689). Costa Rica and Guatemala also hold 2017 (245.12).
- **Benchmarks, 2024 annual averages.** All identical where used:
  - Brent 80.52 USD/bbl in 6 of 6;
  - Henry Hub 2.19 USD/MMBtu in 5 of 6 (Ecuador prices gas without a benchmark);
  - South African coal 105.8 USD/t in 5 of 6;
  - Australian coal 136.1 USD/t (Ecuador only).
  The whole 2018 to 2025 series of each agree too.
- **Units of r differ.** Ecuador and Guatemala state r against Brent in USD/bbl (for example Guatemala diesel r 0.2589 per USD/bbl). Costa Rica, the Dominican Republic, Honduras and Jamaica state it against Brent in USD/GJ (13.934 USD/GJ in 2024). For gas, Guatemala's r is per USD/MMBtu and Costa Rica's per USD/GJ net. Since r and the benchmark are always used together, the values are the same; only the stated r differs. LAC_COST_WRITE must not compare r across countries without converting.
- **Conversion constants are identical where shared:** GJ per MMBtu 1.055056, net/gross 0.9, MMBtu per Mcf 1.037, 7.32 bbl/t and 42.3 GJ/t for crude, 25.1208 GJ/t for 6,000 kcal/kg coal, 32.5 GJ/t for coke, 40.4 GJ/t and 278 gal/t for fuel oil.
- **Gas conversion.** Ecuador, Costa Rica, Guatemala and Honduras divide a gross 2024 value by 0.9 exactly once: the proposed value over the gross value is 1.1111. Each carries the brief's F5 sentence word for word on every gas VariableCost row. Jamaica and the Dominican Republic choose Comtrade LNG import CIF per tonne divided by the IPCC net calorific value (48.0 GJ/t), which is already net, so rule F5 needs no division and none was made. Both still attach the F5 sentence ("converted to the models' net basis by dividing by 0.9") to rows whose value was not divided: 105 rows in Jamaica and 81 projected rows in the Dominican Republic, whose observed rows carry no sentence. The values are consistent with F5; the sentence on those rows is not.
- **Exchange rates.** Each country converts its own currency, so no two countries share a currency source and the comparison does not apply. The rates are:
  - Costa Rica 515.1098 CRC/USD (World Bank WDI);
  - Dominican Republic 59.5665 DOP/USD (BCRD selling rate);
  - Guatemala 7.75960 GTQ/USD (Banguat);
  - Honduras 24.7950 HNL/USD (BCH buying rate);
  - Jamaica 157.22 JMD/USD (BOJ selling rate);
  - Ecuador uses the US dollar.
  Honduras is the only country on a buying rate."""

STEP6 = {
    "cr": """1. **Electricity import technology.** Yes. The Costa Rica A-O at `2ddd560` has `IMPELE` ("Import/Distribution - Electricity", Primary Techs, Tech.ID 9, the same Tech.ID as `PROINDWAS`).
   - In the BAU CSVs it outputs `E1_ELE` (OutputActivityRatio 1.0, 30 years) and has a TotalTechnologyAnnualActivityUpperLimit of 2.245 PJ (2021), 2.3889 (2022), 2.8261 (2023), 3.8463 (2024) and 2.8266 from 2025 to 2050 ("User defined" in the A-O).
   - It has no row in ResidualCapacity, TotalAnnualMaxCapacity, TotalAnnualMaxCapacityInvestment, TotalTechnologyAnnualActivityLowerLimit, CapitalCost, FixedCost or VariableCost. Those rows exist in the A-O with mode EMPTY.
   - So the model can use it: capacity can be built without limit at no cost, and activity is capped only by the upper limit. Whether a run actually uses it was not checked: no model was run.
   - The brief's statement "There is no electricity import technology" was wrong.
2. **Commit `7e8dd76` "price electricity imports (IMPELE)".**
   - It changed 18 files in the job folder (163 lines added, 41 removed).
   - It added 30 `IMPELE` VariableCost rows to `proposals.csv`. All carry 57.2387 USD/GJ (206.06 USD/MWh): 2024 is `observed`, the other 29 years `ASSUMPTION`, held flat. The current value is empty.
   - The derivation is 74,953,098.26 USD / 363,748.07 MWh, the total ICE paid for regional market imports in 2024 (ICE DOCSE Informe Anual 2024, page 17). That total includes the CMORC transmission charge of 20,629,009.48 USD; without it the price is 149.35 USD/MWh.
   - It also added rows to `constants.csv` (5), `sources.csv` (1) and `search_log.csv` (6), and rewrote the REPORT, GAPS and CHANGES sections.
   - Costa Rica GAPS item 20 says this was done "on Luis's instruction of 10 November 2026", against the brief's "skip Step 6". This job cannot confirm that instruction; it is listed under decisions.
3. **Coal and petroleum coke (`structure_proposals.csv`, 5 rows).**
   - The one proposed change is `A-O_Demand.xlsx` sheet Demand_Projection, row 25 (`E5INDCOA`, Demand Industrial Coal), cell M25 (2021): 0.675 to 0.00667 PJ. SpecifiedAnnualDemand would follow on regeneration.
   - No change to `E5INDCOK` (4.091 PJ in 2021, 3.713 in 2022) or to the coal and coke fuel links.
   - Moving the 0.675 PJ to petroleum coke is recorded as an alternative, not recommended: it would put 2021 coke at 4.766 PJ, 18 percent above customs.
   - At `2ddd560` the model has `E5INDCOA` 0.675 PJ in 2021 only, then 0.00667 (2022), 0.0076 (2024) and 0.0109 (2050). The brief's "0.675 PJ a year" applies to 2021 alone.
   - The balance page it cites, MINAE Balance Energetico Nacional 2022, PDF page 40, Tabla 3, reads in this job: "Carbon Mineral ... 0.26 [kt] 6.67 [TJ]; Coque de Petroleo ... 138.6 [kt] 3 713.16 [TJ]".
   - PDF page 36 reads "En el periodo del 2022 se importaron 138 602 toneladas de coque de petroleo, en comparacion con el periodo del 2021 que se importaron 124 327 toneladas".
   - So 2022 industry coal is 6.67 TJ, and 2022 coke equals the model's 3.713 PJ. The 0.675 PJ in 2021 is not supported by the balance, and coke is already counted. The job's reading holds against the pages.""",
    "ecu": """1. **Rows that were 1.** `cost_rows_current.csv` has 167 cells equal to 1 (one per row: the Flat value in 2021). 161 rows have a proposal, and none is still 1. Six rows have no proposal: `PPGEO` and `PPPVDS` CapitalCost, FixedCost and VariableCost. Both technologies are outside the brief's section 5 plant list; the job lists them as a known-limitation candidate (its GAPS section 5). So the answer is "every row in scope, yes; two out-of-list technologies, no".
2. **CCG against PLANMICC.** `plant_costs.csv` flags 1,769 cells over 25 percent, 61 technology-parameter pairs. The pairs, with 2024 proposed against PLANMICC:
   - hydro capital: `PPHDAMAB` 3,562 vs 1,572 (+127 percent), `PPHRORAB` 3,500 vs 1,318 (+170), `PPHRORAM` and `PPHRORPM` 3,562 vs 2,741 (+30), `PPHD` and `PPIHD` 4,241 vs 3,081 (+38);
   - hydro fixed costs: +38 to +155 percent on all ten hydro rows plus `PPHD` and `PPIHD`. CCG fixed costs include variable O&M;
   - thermal: `PPFOI` and `PPDFOI` capital 1,454 vs 1,070 (+36); `PPNGS` and `PPRNGS` capital 707 vs 1,000 (-29) and fixed 12.1 vs 21.1 (-43); `PPCRU` fixed 18.2 vs 44.3 (-59); `PPBGS`, `PPBIM` and `PPIBIM` fixed 15.8 vs 90 to 95 (-83);
   - PV and wind: `PPPVT` capital 1,485 vs 963 (+54) and fixed 19.3 vs 13.6 (+42); `PPPVD` capital 1,855 vs 963 (+93); `PPWNDON` fixed 57.2 vs 34.3 (+67);
   - plant VariableCost 0 against PLANMICC 0.56 to 18.9 (-100 percent): 20 pairs, all hydro and thermal plants mapped to CCG;
   - refineries: `REF_DSL`, `REF_GSL`, `REF_JET` and `REF_LPG` 0.87 vs 3.25 to 14.5; `REF_FOI` 0.87 vs 0.69 (+27);
   - supply and imports: `DIST_BIM` 6.79 vs 2.23, `DIST_FIR` 6.79 vs 0.66, `IMPELE` 73.19 vs 11.83.
   The full list with codes is in `country_points.txt`.
3. **CCG plants have VariableCost 0.** 27 plants take CapitalCost or FixedCost from the CCG kit (CCG-002). All 810 of their VariableCost cells are 0, and none differs.""",
    "jam": """1. **Petrojam prices are tax-inclusive, so not used as pre-tax.** The job parsed the 10 saved Petrojam pages (52 weeks of 2024, no gap). The 2024 weekly means equal MSET's refinery billing prices. The evidence, re-read in this job:
   - MSET Jamaica Energy Statistics 2025 (JAM-015), page 8, Table 4 "Refinery Billing Price", 2024 row: E10-90 176.49, E10-87 168.73, A.D.O 171.05, ULSD 178.28 J$/L, "Source: Petrojam Limited". The same row is in the 2024 edition (JAM-016), page 8.
   - The job's weekly means are 168.738, 176.494, 171.059 and 178.284 (its GAPS item 1).
   - The MSET note in PETROLEUM-PRICES-2018.pdf (JAM-022 of LAC_LOCAL_PRICES, in the job's downloads) reads: "(3) Ex-refinery Price = US Gulf Reference Price + freight + insurance +premium factor+ other charges and fees (4) Billing price = ex-refinery price + taxes (SCT) and fees".
   So the Petrojam prices include the Special Consumption Tax, and the job used none of them as the pre-tax point. They sit in `price_points_2024.csv` as `wholesale import parity, chosen = no` (diesel 29.116 and 30.347, gasoline 32.739 and 34.244 USD/GJ). Diesel and gasoline fall back to import CIF, and kerosene and jet stay ASSUMPTION at 18.0 USD/GJ. The brief's premise ("use their 2024 mean ... where it is pre-tax") is answered: they are not pre-tax.
2. **Current values from the A-O.** `cost_rows_current.csv` against the A-O at `2ddd560` read with cached values: 192 rows and 6,720 cells compared, 0 differ, and no row is missing on either side. The values were read from the A-O, not from Jamaica's A2 or B1 CSVs.""",
    "dr": """1. **`DIST_GSL` and `DIST_LPG` use the market values with the MICM parity beside them.** Yes, in `price_points_2024.csv`:
   - `DIST_GSL`: chosen import CIF 19.6137 USD/GJ (LAC_LOCAL_PRICES row 67). The MICM wholesale import parity 19.4897 (-0.63 percent, row 50) and the final consumer pre-tax 25.6821 (+30.9 percent) sit beside it.
   - `DIST_LPG`: chosen import CIF 11.0415 USD/GJ (Comtrade, row 66). The MICM wholesale import parity 15.2531 (+38.1 percent, row 52) and the final consumer pre-tax 21.1431 (+91.5 percent) sit beside it.
   - In `proposals.csv`, 2024 is 19.6137 and 11.0415 in STEPS, CPS and NZE, basis `observed`. These match the brief's 19.614 and 11.042, with MICM 19.490 and 15.253.
2. **Rows left unpriced (from the BAU at `2ddd560`).**
   - `EXTT_NGS` and `IMP_ELE` have an activity upper limit of 0, so they cannot run.
   - `EXTT_CRU` (upper limit 43.1971 PJ a year) and `PRO_COA` (3.1492 PJ) can run at VariableCost 0. The job proposes nothing for them and records them as known-limitation candidates, as the brief allows.
   - The Dominican Republic produces no crude or coal, so a least-cost run can draw up to 43.2 PJ of free domestic crude and 3.1 PJ of free coal. This is listed as a decision.""",
    "gua": """1. **The unit evidence behind the plant VariableCost correction.**
   - The A-O at `2ddd560` labels the plant VariableCost rows "M US$ / GWh" (read in this job: `PPBGS` 0.005, `PPCOA` 0.0064, `PPFOI` 0.00569 in 2018). The fuel rows say "M US$ / PJ".
   - Guatemala's REPORT states: "The workbook's plant VariableCost unit label is "M US$ / GWh"." It also states: "Data in Brief Table 57 prints "M USD/GWh"."
   - It continues: "Every source behind these values gives variable O&M in USD/MWh: PEG 2020-2050 biogas 5 and coal 6; EIA 2020 engines 5.69; IRENA bioenergy 0.005 USD/kWh. So the model values are USD/kWh."
   - The `unit_fix` rows (66 cells, `PPBGS` and `PPFOI`) carry these derivations:
     - `PPFOI`: "current 0.00569 is USD/kWh; EIA 2020 cost study Table 2 p.28, Case 4 Internal Combustion Engines, variable O&M 5.69 USD/MWh (2019 USD); 5.69 / 3.6 = 1.580556 USD/GJ";
     - `PPBGS`: "current 0.005 is USD/kWh (MUSD/GWh, the unit label of the cell); PEG 2020-2050 Tabla 4/5 (PDF pp.41-42), row biogas 5 USD/MWh ... 5 / 3.6 = 1.388889 USD/GJ".
   - The other plants (`PPCOA`, `PPDSL`, `PPNGS`, `PPBIM`) get a sourced value in USD/MWh / 3.6 as `replace`. After the x277.78 conversion they differ from the current values by -6, -17, +10 and -59 percent.
   - The source numbers were searched in the downloads ({gua_unit_check}).
   - 1 M US$ / GWh = 1 USD/kWh = 277.78 USD/GJ, so a cell labelled M US$ / GWh read as M US$ / PJ is 277.78 times too small. The evidence supports the slip.""",
    "hon": """1. **`IMP_ELE` years with 99999.** In the A-O at `2ddd560` (and in `cost_rows_current.csv`), `IMP_ELE` VariableCost and FixedCost ("User defined") are 500 in 2018, 559.8 in 2024, and 99999 in every year from 2025 to 2050 (26 years). The brief said "from 2030"; it is from 2025. CapitalCost is mode Zero.
   - `proposals.csv` has no `IMP_ELE` row in any year from 2025 to 2050, so the 99999 years are absent and stay as they are.
   - It has 14 `IMP_ELE` rows, all 2018 to 2024:
     - VariableCost 31.8216 USD/GJ for 2018 to 2021 (ASSUMPTION) and for 2024 (observed), 34.2098 for 2022 and 37.266 for 2023 (observed, from CREE MER purchase totals);
     - FixedCost 0 for 2018 to 2024 (`replace`), as the brief asked when both parameters carry the price.
   - Gate 6 note: the Honduras ASSUMPTION sentence on the 2018 to 2021 rows contains "the earlier years", a literal hit on the word "earlier". It refers to calendar years, not to the job's process."""
}

COUNTRY_FLAGS = {
    "cr": "Also for the hub: `PWRHYDDAM` CapitalCost 8,079.14 USD/kW (2022 to 2050) is above the 8,000 screen. It is a `keep` matched to NREL ATB 2024 Hydropower NSD2 (new stream-reach) CAPEX 8,140.07 USD/kW, within 0.8 percent. The value is sourced, but a new stream-reach plant may not represent Costa Rica's hydro dams.",
    "dr": "Also for the hub: `EXTT_CRU` and `PRO_COA` keep VariableCost 0 while they can run (see the answers above).",
    "gua": "Value checks of the 2024 fuel points: three are not found. None of the three is a single published number:\n- `DIST_LPG`, 57.3774 GTQ per cylinder, is the mean of the 35 MEM price structures;\n- `DIST_NGS`, 7.763 USD/GJ gross, is the ASSUMPTION value built from Henry Hub plus adders;\n- `EXTT_CRU`, 389.85 USD/t, is value over weight from Banguat KG-103.\nTheir inputs are listed in `value_checks.csv`.",
}

DECISIONS_INTRO = """`decisions_raised.csv` holds {n} items taken from the six GAPS and REPORT files ({k}). Below, every item except incidents, grouped by topic, each with its country, file and section, and the rows it touches. Items marked "choice for Luis or hub" or "open question" are the ones the jobs explicitly left to a decision."""

DECISIONS_SYNTHESIS = """Points that cut across countries, for the hub to settle first (this job's synthesis, from the items below and the checks above):
1. **Keep or replace plant costs.** Luis's 10 November decision keeps current plant costs with refined sources. Rule P2 also defines `replace` where no source gives the number. The five countries under that decision applied P2 as written and kept the current value in each `replace` row. Guatemala, Honduras and Jamaica say so explicitly. Rows with basis `replace` among plant, import and other technology rows (`fuel_scenario = ALL`): Costa Rica 420 of 930, Dominican Republic 1,323 of 2,277, Guatemala 504 of 1,518, Honduras 139 of 1,202, Jamaica 635 of 1,365. LAC_COST_WRITE can write only `keep` and `upgrade`, or all classes. One choice is needed for all five countries; Ecuador is separate, with its CCG rule.
2. **Costa Rica `IMPELE`.** Priced after the first push against the brief's "skip Step 6", citing an instruction from Luis. Accept or drop the 30 rows.
3. **Free supply that can run.** Dominican Republic `EXTT_CRU` (43.2 PJ a year) and `PRO_COA` (3.1 PJ) at VariableCost 0. The Ecuador extraction rows are priced at CCG levels above the export value (`EXTT_CRU` 13.94 against `DIST_CRU` 11.86 USD/GJ).
4. **Gas sentence on undivided LNG rows** (Jamaica, Dominican Republic). Wording only: drop the F5 sentence from rows priced per tonne, or keep it as the shared gas sentence.
5. **Projection mode.** Plant and fuel rows in Flat or "Percent growth of incomplete years" mode need a year-by-year mode to take the proposals. Every country raised this; LAC_COST_WRITE has to do it for all six.
6. **Steps at the join above 20 percent** (section 4 of each country). They are reported, not smoothed, as the briefs require. The largest: Jamaica coal -40 percent and LNG -28 percent (STEPS 2024 to 2025), Costa Rica coke +37 percent, Dominican Republic coke +35 percent and LNG -30 percent."""

FILE_DESC = {
    "BRIEF_LAC_COST_REVIEW_PACK.md": "copy of this job's brief.",
    "REPORT": "the report the hub reads first.",
    "GAPS": "checks not run, judgement calls, known-limitation candidates, incidents.",
    "CHANGES": "this list.",
    "common.py": "shared paths and loaders (read-only on everything outside this folder).",
    "textindex.py": "text extraction of downloaded files (PDF, XLSX, XLS, HTML, DOCX, JSON, CSV, parquet) and number search.",
    "step1_2_inventory_gates.py": "Step 1 inventory and Step 2 gates 1 to 8.",
    "step3_values.py": "Step 3 value checks against the downloaded sources.",
    "step3b_recompute.py": "Step 3 derivation recompute (arithmetic chains and the WEO projection path).",
    "step3c_review_recompute.py": "Step 3 hand review of the recompute differences.",
    "step3d_classify.py": "Step 3 likely cause of each value not found, read from its derivation.",
    "step4_cross_country.py": "Step 4 shared inputs across the six.",
    "step5_range_screen.py": "Step 5 range screen.",
    "step6_country_points.py": "Step 6 evidence for the country points.",
    "step7_merge.py": "Step 7 merged files.",
    "step8_report.py": "writes REPORT, GAPS and CHANGES.",
    "report_text.py": "hand-written text of REPORT and GAPS.",
    "inventory.csv": "Step 1: per branch head, commits, job folder, section 4 files present.",
    "gates.csv": "Step 2: gates 1 to 8 per country, with counts and notes.",
    "value_checks.csv": "Step 3: each value searched in its downloaded sources.",
    "derivation_recompute.csv": "Step 3: derivation expressions above 0.5 percent before hand review, with the hand review.",
    "derivation_recompute_summary.csv": "Step 3: counts of derivations and projection series recomputed.",
    "cross_country.csv": "Step 4: WEO, CPI, benchmarks, conversion constants, gas conversion, exchange rates.",
    "review_flags.csv": "Step 5: every value outside the screens, with current value and sources.",
    "country_points.txt": "Step 6: raw evidence printed by step6_country_points.py.",
    "proposals_all.csv": "Step 7: the six proposals.csv stacked (17,921 rows).",
    "summary_all.csv": "Step 7: the six proposals_summary.csv stacked.",
    "paper_trace_all.csv": "Step 7: the six paper_trace.csv stacked, de-duplicated, sorted.",
    "decisions_raised.csv": "Step 7: judgement calls, questions, choices and ASSUMPTIONs from the six GAPS and REPORT files.",
    "assumptions_all.csv": "Step 7: every ASSUMPTION row with its sentence, plus non-ASSUMPTION rows carrying a sentence (marked).",
}

CONFIRM = """Confirmation:
- No model file was changed: the clone `C:\\clw_cost_review` differs from `2ddd560` only by this job folder (`git status` before the commit listed nothing else).
- No branch of the six was changed: nothing was pushed to `job/cost-src-*`. The six pull requests were not marked ready or merged.
- No file in the six job folders or in `C:\\clw_cost_<cc>` was edited: they were read through `git show`, `git archive` into `scratch/`, and read-only file opens of the local `downloads/`.
- `C:\\clw_local_prices` and OneDrive were read only (one PDF page of the MINAE balance; OneDrive not opened). Nothing under Dropbox was opened."""

GAPS = """# GAPS LAC_COST_REVIEW_PACK 20261111T015203Z

## 1. Checks not run, and why

{notrun}

## 2. Judgement calls

Method of each check:
1. **Gate 4.** It compares the SHA-256 of the git blobs at `2ddd560` and at each branch head. The hashes each job recorded in `baseline_before.csv` were also compared with the blob at `2ddd560`, and all match.
2. **Gate 5, internal files.** A source field naming a workbook (`.xlsx`, `.xlsm`) counts as internal unless the cited URL serves that same file. Five Ecuador sources pass this way: CCG-002 and CCG-007 (Zenodo files of the CCG kit), ECU-002 (BCE `SerieCifrasPetroleras.xlsx`), and PMC-008 and PMC-009 (PLANMICC files at a commit permalink). All are published external files.
3. **Gate 6, the word list.**
   - Words are matched as whole words, case-insensitive, with a plural "s" allowed.
   - "Henry Hub" is read as the benchmark's proper name, not the word "hub". It is part of the gas sentence every brief prescribes (rule F5), and a literal reading would fail all four countries that carry that sentence for the brief's own wording.
   - Honduras' "the earlier years" is kept as a literal fail, since the brief lists "earlier" without exception. It is reported as low severity, because it refers to calendar years.
4. **Gate 6, leads.** An ASSUMPTION technology counts as logged if its name appears in any field of a `search_log.csv` entry, or in a `DIST_*` group entry for supply rows. All ASSUMPTION technologies were found by name.
5. **Gate 7, coverage.**
   - Every plant in the brief's table needs CapitalCost, FixedCost and VariableCost in every year column of the A-O at `2ddd560`. Every supply row needs VariableCost in every year for STEPS, CPS and NZE.
   - The import technology is checked where the brief's Step 6 applied: Ecuador `IMPELE`, Guatemala `IMP_ELE`, Honduras `IMP_ELE`. For Honduras, only the years with a positive activity lower limit in the BAU (2018 to 2024) were required, as its brief says.
   - Dominican Republic `EXTT_CRU`, `EXTT_NGS` and `PRO_COA` are counted as absences the brief allows ("If they cannot run, leave them and record it; if they can, record it as a known-limitation candidate"). Two of them can run; see decisions.
6. **Gate 8.** It counts em dashes in every tracked file of each branch's job folder. None was found anywhere, so whether the brief copies count as output files does not matter.
7. **Value checks, the number searched.**
   - Fuel rows: `price_as_published` where the job recorded it (Ecuador, Guatemala). Otherwise the first input number of the price point derivation (Honduras, Jamaica). Otherwise the `price_as_published` of the matching LAC_LOCAL_PRICES row (Costa Rica, Dominican Republic, whose price points carry no derivation).
   - Plant rows: the first number in the derivation, once these are removed: identifiers (table, page, row, cell, class and case numbers), years, quantities with units such as MW or percent, the job's own current or model value quoted beside the source, and deflators and conversion factors from `constants.csv`.
   - If that number is not printed in the row's source files, the other input numbers of the derivation with three or more significant digits are tried in order. The first one found is reported as the number searched, and the note says the first number itself is not printed. This covers values the source prints as inputs (customs value and weight, or a 2020 USD value later converted).
   - Up to six other inputs are listed in the note, with whether each was found.
   - Where a derivation names its source but states no number (for example "NREL ATB 2024 ... Fixed O&M, scenario Moderate"), the proposed value itself is searched, as the published value.
   - Rows whose proposed value is 0, 1 or empty and whose derivation states no other number are `not run` ("no number to search"). These are mostly zero variable O&M and ASSUMPTION zeros; their sentences are in `assumptions_all.csv` and their sources were not checked here.
8. **Value checks, what counts as found.** A printed number in English or Spanish notation (thousands separators allowed) that rounds to the searched number at its stated precision. The location is the PDF page, the sheet and cell, or the line. Numbers of two significant digits or fewer are marked as possibly coincidental.
9. **Value checks, grouping.** Rows with identical technology, parameter, derivation, source ids and proposed value were checked once, with the year range in the `year` column. The plant check covers every `fuel_scenario = ALL` row not `keep`. The keep sample is `pandas.DataFrame.sample(n=20, random_state=20261110)` on each country's `keep` rows of `fuel_scenario = ALL`.
10. **Means over many files.** A value that is a mean of weekly or monthly files (for example the Dominican Republic MICM weekly tables, Guatemala's 35 price structures, the Ecuador terminal price lists) is not printed in any one file. Such checks come out "not found", and the note says the value is a mean.
11. **Range screen.**
    - "Plant" means the technologies in the brief's plant table.
    - The Brent screen uses Brent 2024 = 80.52 USD/bbl = 13.934 USD/GJ (7.32 bbl/t, 42.3 GJ/t) times the row's r. For Ecuador and Guatemala, whose r is per USD/bbl, it uses 80.52 times r.
    - Severity rules are in REPORT section 2.
    - A 0 is low severity when a cited source states 0 for that cost, when a brief rule prescribes it, or when an ASSUMPTION sentence sets it. It is medium when it is read from a source's 0.0001 placeholder (Ecuador `EXTT_CRU` and `EXTT_NGS` capital and fixed).
    - The step at the join is the change from the last `observed` year to the first `projected` year of the row and scenario.
12. **Decisions list.** The 348 items of `decisions_raised.csv` were extracted from the twelve GAPS and REPORT files by three helper agents working in parallel (two countries each). Each was given the same column rules. I read the Ecuador GAPS in full and checked the extracted items against it. I also checked every "choice for Luis or hub" and "open question" item of all six against the text it cites. The other items were not checked one by one against their files.
13. **Paper trace de-duplication.** Two records are one passage when document, first eight words and statement (normalised to letters and digits) are equal. 351 records became 332 passages, and 12 passages merged records of two or more countries. Passages the countries quote with different wording stay separate.
14. **`assumptions_all.csv`.** It holds the 2,147 ASSUMPTION rows and also the 504 non-ASSUMPTION rows that carry an ASSUMPTION sentence (gas F5 sentence on projected rows, history rows), marked in `row_kind`.

## 3. Known-limitation candidates

Outside the scope of this job; not acted on.
- **Briefs.** The six country briefs name the WEO table "Table 2.32"; it is Table 2.3, page 109.
- **Honduras brief.** It says `IMP_ELE` costs are 99999 "from 2030"; the A-O at `2ddd560` has 99999 from 2025.
- **Costa Rica brief.**
  - It says there is no electricity import technology; `IMPELE` exists with an activity upper limit and no cost.
  - It says `E5INDCOA` is 0.675 PJ "a year"; that is 2021 only.
  - `A-O_Parametrization.xlsx` Primary Techs: `IMPELE` and `PROINDWAS` share Tech.ID 9 (Costa Rica GAPS). LAC_COST_WRITE should match on Tech.
- **Dominican Republic BAU.** `EXTT_CRU` and `PRO_COA` can run with VariableCost 0, although the country produces no crude or coal.
- **Units of r.** The stated r is per USD/bbl in Ecuador and Guatemala and per USD/GJ elsewhere. Anything that compares r across countries needs a conversion.
- **Exchange rates.** Honduras converts at the BCH buying rate; the other countries use selling or period-average rates.
- **Costa Rica `PWRHYDDAM`.** It is matched to ATB NSD2 (new stream-reach) at 8,079 USD/kW, above the 8,000 screen. That ATB class may not represent dam hydro in Costa Rica.

## 4. Incidents

- **Value-check reruns.** Four more runs followed the first. They fixed, in turn:
  - the job's own current or model values being taken as the searched number;
  - published inputs not being tried;
  - a tokenizer bug that skipped every number right after a comma, which covers most CSV cells, so for example NREL ATB values were not found at first;
  - derivations that state no number.
  Only the last run's results are in `value_checks.csv`.
- **First value-check run.** It rescanned the full text of large files for every number: the Ecuador CCG workbook (80 MB of cell text) and the NREL ATB file (100 MB). It was stopped and the search rewritten as a one-pass numeric index per file. A second run evicted the indexes too early and was also stopped; the third run kept each country's indexes in memory.
- **Stopping the run.** A command to stop all Python processes was refused by the session's permission check. The run was then stopped by its own process ids only.
- **The `git archive` extract.** It of each branch into `scratch/` holds the whole `_LAC_HUB` folder of the branch, not only the job folder. It is read-only, not tracked, and not committed.
- **Push and pull request.** See REPORT section 1."""
