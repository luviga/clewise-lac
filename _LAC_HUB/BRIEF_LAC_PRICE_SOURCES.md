# BRIEF LAC_PRICE_SOURCES: source plan for import-parity fuel prices in six countries

Working copy: `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5` (Git Bash: `/c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5`). Claude Code opens here.
Hub folder: `MODELS_LAC_5/_LAC_HUB/`. This brief lives there.

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, record it, finish every step you still can, and write the three output files anyway. This job changes no model file and builds no final price series; it finds and tests the sources for one.

## 1. Goal

Luis decided on 8 November 2026 that fuel supply costs in the six country energy models (Costa Rica, Dominican Republic, Ecuador, Guatemala, Honduras, Jamaica) are pre-tax import parity:

**price(country, fuel, year) = international benchmark(fuel, year) + freight and insurance to the country + terminal and wholesale margin**, all before taxes, in USD per GJ (equal to the models' MUSD/PJ), nominal or real as decided in REPORT.

The models need these for 2018 to 2050 (Jamaica to 2055) in three price cases, REF, HIGH and LOW, where HIGH and LOW move the benchmarks and keep the adders. The paper using these models compares the cost of fossil import dependence across the six countries under oil price shocks, so the six must share one benchmark set.

Find, open and record the external sources for every piece, test the adder for 2024 in each country where an observed import parity price is published, and say what remains an ASSUMPTION. Deliver a source plan Luis can approve.

## 2. The standard

Cite only external, retrievable sources: a URL, DOI or public repository permalink with commit hash. Open every source you cite in this session and confirm the value, unit and year are there. Never cite internal files (workbooks, sheets, cells, markdown, handovers, CSVs we built, local paths); the existing fuel workbook in MODELS_LAC_5 may be used as a lead only. If no external source exists, the value becomes an ASSUMPTION candidate: write the sentence as a statement about the value with its unit and coverage, a plain reason, a check against a public document where one exists, and a range. Never write "not found", "no public source" or our process in an ASSUMPTION sentence; list what you could not source in GAPS instead. Paywalled sources (Argus, Platts, S&P) are not retrievable; name them in GAPS if they are the only origin.

Scope is frozen. Do only what section 5 lists. Anything else goes to GAPS under "Known-limitation candidates".

## 3. What the models need and what is already known

Fuel supply rows to price (VariableCost), by country (from job LAC_FUEL_CHECK, `_LAC_HUB/fuel_check_20261108T223320Z/`, `ao_fuel_supply_mapping.csv` and `gap_rows.csv`):

| Fuel | Code in the models |
|---|---|
| Gasoline | `DIST_GSL`; Costa Rica `IMPPURGSL` |
| Diesel | `DIST_DSL`; Costa Rica `IMPPURDSL` |
| LPG | `DIST_LPG`; Costa Rica `IMPLPG` |
| Kerosene | `DIST_KER`; Costa Rica `IMPKJF` (kerosene and jet together) |
| Jet fuel | `DIST_JET` (Ecuador, Jamaica) |
| Fuel oil | `DIST_FOI`; Costa Rica `IMPFOI` |
| Natural gas (as LNG) | `DIST_NGS` (Dominican Republic, Ecuador, Guatemala, Honduras, Jamaica); Costa Rica `IMPNGS` |
| Coal | `DIST_COA`; Costa Rica `IMPCOA` |
| Petroleum coke | `DIST_COK`; Costa Rica `IMPCOK` |
| Crude oil | `DIST_CRU` (Dominican Republic, Ecuador) |
| Aviation gasoline | Costa Rica `IMPAVG` |

Out of scope: electricity imports, biomass, firewood, biogas, charcoal, uranium, flex fuel, refinery rows, domestic extraction (`EXTT_*`).

Leads to check, not facts:

- US Gulf Coast spot prices for gasoline, ultra-low sulfur diesel, jet fuel and Mont Belvieu propane are published by the US EIA (spot prices series). The Caribbean and Central America import most refined products from the US Gulf Coast.
- The World Bank Commodity Price Data (Pink Sheet) publishes monthly and annual Brent, Henry Hub, Japan LNG and Colombian, Australian and South African coal prices, and its Commodity Markets Outlook gives short-term projections.
- The EIA Annual Energy Outlook publishes Brent and Henry Hub to 2050 in Reference, High Oil Price and Low Oil Price cases, a natural source for REF, HIGH and LOW. The IEA World Energy Outlook 2025 gives scenario prices but parts may be paywalled.
- Several regulators publish import parity prices or price structures that separate the import cost from taxes: Guatemala's Ministerio de Energía y Minas, Honduras's Secretaría de Energía, the Dominican Republic's Ministerio de Industria, Comercio y Mipymes (weekly fuel prices with import parity), Costa Rica's ARESEP (RECOPE price structure), Jamaica's Petrojam (ex-refinery prices). Ecuador sets domestic prices by decree; check for a published import cost.
- LNG to the Dominican Republic and Jamaica comes mainly from the US; a landed LNG price is commonly built as Henry Hub times a factor plus liquefaction, shipping and regasification, each with published estimates.
- Energy contents and densities: IPCC 2006 Guidelines Vol. 2 Table 1.2 gives net calorific values per mass; densities need their own source (for example EIA or IEA conversion tables).

## 4. Setup

- Environment: Windows, Git Bash and the `py` launcher. Run your own scripts with `py -I`. pandas and openpyxl are installed. Install nothing. Use your web search and web fetch tools for sources.
- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Create `_LAC_HUB/price_sources_<stamp>/` and put every file you write there, including helper scripts and downloaded public data files (CSV or XLSX from the source sites).
- Write only inside `_LAC_HUB/price_sources_<stamp>/`.
- Read-only: every other file in MODELS_LAC_5. Do not open anything under `C:\Users\luisfernando\Dropbox\`.
- Another read-only job on A-O formula cells may run at the same time in its own folder; ignore it.
- Expected run time: 1.5 to 3 hours.

## 5. Work

### Step 1. Benchmarks

For each fuel in the table in section 3, choose the international benchmark that best matches where these countries buy it. Give the series name, publisher, URL, unit, frequency and first and last observation. Download the public data file where one exists. Prefer one publisher for all oil products so the six countries share a base. For fuel oil, petroleum coke and aviation gasoline, where a free benchmark may not exist, give the best retrievable proxy and how it relates to a benchmark that is published (for example a ratio to Brent or to coal, with its source).

Save `benchmarks.csv` (fuel, series, publisher, URL, unit, frequency, coverage, retrieval date, notes).

### Step 2. History, 2018 to 2025

For each benchmark, compute annual averages for 2018 to 2025 from the downloaded data, convert to USD/GJ, and show the conversion factors with their sources. Save `history_usd_per_gj.csv`, with the source of every value. If 2025 is incomplete, say how many months the average covers.

### Step 3. Projections, REF, HIGH and LOW, to 2050

Find retrievable projections for each benchmark or its driver (Brent, Henry Hub, coal) in three cases. Prefer one publisher that offers all three cases to 2050. Report the publisher, edition, table, cases, years, unit and whether the values are real or nominal (and the base year). Explain how each refined product would follow its driver (for example a product to Brent ratio from the history in Step 2, with the period used). Save `projections.csv` with the driver values as published, and `projection_method.md` with the rule for each fuel.

### Step 4. Freight, insurance and margins

For each country and fuel, find the adder that takes the benchmark to a pre-tax import price:

1. Where a regulator publishes an import parity price or a price structure with the import cost separated from taxes, collect 2024 values (monthly or a published annual figure), convert to USD/GJ, and compute the observed adder as that price minus the 2024 benchmark average. Give the source, the exact table or page, the currency and exchange rate (with its source), and the result.
2. Where no such price is published, find published freight rates or margins for the route (for example product tanker rates from the US Gulf Coast to the Caribbean, LNG shipping costs, coal freight) and build the adder from them, with sources.
3. Where neither exists, write an ASSUMPTION candidate sentence with a range, following section 2.

Save `adders_2024.csv` (country, fuel, method, observed or built adder in USD/GJ, components, sources) and show the full working for each country's diesel and fuel oil in REPORT.

### Step 5. Sanity check against the models

Read, without changing anything, the current diesel and fuel oil supply VariableCost values for 2025 in each country's `A1_Outputs/A-O_Parametrization.xlsx` (energy folders: Costa Rica `CR_ENERGY/t1_confection`, Dominican Republic `RD_ENERGY`, Ecuador `ECU_Energy`, Guatemala `GUA_ENERGY`, Honduras `HON_ENERGY`, Jamaica `JAM_ENERGY`, each under its country folder). Compare them with benchmark 2024 plus the Step 4 adder. Report the ratio. Ecuador holds placeholders of 1; say so and skip it.

### Step 6. Gates

1. Read-only gate: SHA-256 of the six main A-O workbooks and of `LAC_Fuel_Price_Projections_2026_v2_audit.xlsx` before Step 1 and after Step 5 (`baseline_before.csv`, `baseline_after.csv`) must match. Any difference is a failure: report it at the top of REPORT.
2. Nothing written outside `_LAC_HUB/price_sources_<stamp>/`.
3. Every source in the output files was opened in this session; `sources.csv` lists each with URL, title, publisher, date and retrieval date.
4. Every number in REPORT traces to a CSV or downloaded file in the output folder.

## 6. Outputs

All in `_LAC_HUB/price_sources_<stamp>/`, plain English, no em dashes.

`REPORT_LAC_PRICE_SOURCES_<stamp>.md`: start with the gate results. Then a short answer: the benchmark set you propose; the projection source and cases; for each country and fuel whether the adder is observed, built from published rates, or an ASSUMPTION candidate (as a table); what cannot be sourced; and the decisions Luis must take before a build job. Then sections for Steps 1 to 5.

`GAPS_LAC_PRICE_SOURCES_<stamp>.md`: every judgement call and its reason; sources you could not open or that are paywalled; values without a retrievable source; "Known-limitation candidates"; anything left unchecked.

`CHANGES_LAC_PRICE_SOURCES_<stamp>.md`: every file you created or downloaded, with its purpose or origin URL in one line. Confirm that no model file changed.

Supporting files: `baseline_before.csv`, `baseline_after.csv`, `sources.csv`, `benchmarks.csv`, `history_usd_per_gj.csv`, `projections.csv`, `projection_method.md`, `adders_2024.csv`, downloaded public data files, and your helper scripts.
