# BRIEF LAC_LOCAL_PRICES: per-country published fuel prices for the six LAC energy models

Repository: https://github.com/luviga/clewise-lac, `main` at `c5ca4ee`. No open pull requests.
Main copy on this machine: `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5` (Git Bash `/c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5`). Claude Code opens there and this brief sits in its `_LAC_HUB/` folder.

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, record it, finish every step you still can, and write the three output files anyway. Never mark a pull request ready and never merge. This job changes no model file and builds no final price series. It finds, downloads and records local published prices.

## 1. Goal

Luis decided on 8 November 2026 that fuel supply costs in the six energy models are pre-tax import parity in real 2024 USD: an international benchmark plus freight, insurance and margins to each country. The international part is done (EIA spot series and AEO2025, World Bank Pink Sheet, all downloaded). The local part is open: of the 55 country and fuel rows in `_LAC_HUB/price_sources_20261109T003525Z/adders_2024.csv`, 33 rest on a value taken from other countries, an assumed margin, or an ASSUMPTION candidate.

Luis's directions of 9 November 2026 set this job:

1. Every value gets a published source for that country. Local publishers first: regulators, ministries, system operators, central banks, customs and statistics offices, state oil companies, utilities' public filings. Regional or international sources come second, and a value taken from another country is never used for a row.
2. Fuel oil: each country's own published fuel oil import or delivered cost. One regional proxy ratio is not enough.
3. Margin scope: record the importer or terminal margin, the wholesale margin, inland freight and the retail margin, each as its own component, wherever a published source gives it. Where none is retrievable, leave that component empty and record why in the search log.
4. Coal and petroleum coke: each country's published delivered or import cost.
5. No ASSUMPTION as a substitute for searching. An ASSUMPTION candidate is allowed for a row only after every lead for that row in section 5 has been tried and logged. Where a source exists but does not open for you, put it on the manual download list (URL, what it should hold, which rows it closes, why it is needed, how it failed) so Luis can fetch it by hand.

Spend the tokens this takes. Coverage matters more than speed.

## 2. The standard

Cite only external, retrievable sources: a URL, DOI or public repository permalink with commit hash. Open every source you cite in this session, confirm the value, unit, period and tax treatment are there, and save a copy of the file in the job's `downloads/` folder before you record the value. Never cite internal files (workbooks, sheets, cells, markdown, handovers, CSVs we built, local paths). Files in this repository, including the earlier price-sources outputs and the fuel workbook `LAC_Fuel_Price_Projections_2026_v2_audit.xlsx`, are leads only.

An ASSUMPTION candidate sentence states the value with its unit and coverage, a plain reason, a check against a public document where one exists, and a range. It never mentions our process, our files, or what could not be found; that goes in GAPS and the search log.

A value read from a document is a derivation when you convert units, average months or sum rows. Write each derivation with every constant and the source of each constant.

Scope is frozen. Do only what section 5 lists. Anything else you find goes to GAPS under "Known-limitation candidates", with where it is and one sentence on what it is.

## 3. Facts already checked by values (hub, at `c5ca4ee`)

- Model price unit: MUSD/PJ, equal to USD/GJ (price-sources REPORT, Step 5, confirmed against the A-O 2025 values).
- The 33 open rows, by `adders_2024.csv` method:
  - ASSUMPTION candidate (14): coal `COA` and petroleum coke `COK` in all six countries; crude `CRU` in the Dominican Republic and Ecuador.
  - Built from other countries' data (7): Jamaica diesel, gasoline, kerosene and jet; Ecuador fuel oil and kerosene; Guatemala kerosene.
  - Built from published rates (4): natural gas in Costa Rica, Guatemala, Honduras and Ecuador (Henry Hub plus 4.26 US LNG export spread plus 1.42 small-scale shipping and regasification, 5.68 USD/GJ).
  - Observed import cost with an assumed margin (8): Honduras diesel, gasoline, kerosene; Ecuador diesel, gasoline, jet, LPG; Jamaica LPG (customs CIF).
- Partly covered observed rows to extend to a full year: Jamaica fuel oil and natural gas (OUR plant prices, June and July 2024 only); Guatemala liquids (31 of 52 weekly structures); Honduras weekly bulletins (January to July 2024 only).
- Rows where Luis has an open question and this job must record both sides:
  - Dominican Republic gasoline and LPG: the 2024 MICM import parity was administrative under a retail price freeze (gasoline adder 3.64, LPG 8.66 USD/GJ). Find a market-tracking 2024 import cost as well (for example the Platts quotes in the Ministry of Energy and Mines bulletins, customs unit values, or Comtrade).
  - Ecuador fuel oil: Ecuador exported fuel oil in 2024 (EP Petroecuador export FOB 61.68 USD/bbl, 10.11 USD/GJ) and imported none. Record the published export value and any published import or delivered-to-generator value.
- Which technologies each supply row feeds, from `A2_Output_Params/BAU/InputActivityRatio.csv` and `OutputActivityRatio.csv` in each energy folder. One supply row serves power plants and final demand at one price wherever both exist:

| Country | Power plants fed | Final demand fed |
|---|---|---|
| Costa Rica | `IMPPURDSL` (PWRDSL), `IMPFOI` (PWRFOI) | every fuel; coal and petroleum coke feed industry only; `IMPNGS` feeds only `NGS_DTR` |
| Dominican Rep. | diesel 5, fuel oil 5, natural gas 5, coal 1, gasoline 1, LPG 1 | every fuel; crude feeds the refinery (`REF_*`) |
| Ecuador | diesel 3, fuel oil 2, natural gas 2 | every fuel; crude feeds `PROCRU` and exports; coal and petroleum coke industry only |
| Guatemala | coal, diesel, fuel oil, natural gas (1 each) | coal and natural gas feed power only; petroleum coke feeds industry and cement |
| Honduras | coal, petroleum coke, diesel 2, fuel oil, LPG, natural gas | coal and natural gas feed power only |
| Jamaica | diesel, fuel oil, natural gas (1 each) | every fuel; coal and petroleum coke feed industry only (cement, bauxite, sugar, other) |

  So for each fuel the job records two price points where published: delivered to power generators, and pre-tax to final consumers. The build job decides how to use them.
- Exchange rates already sourced for 2024: CRC 518.23 (BCCR daily reference rates, mean), DOP 59.5665 (BCRD annual average), GTQ 7.7596 (Banguat reference rates, mean), JMD 157.22 (Bank of Jamaica annual average). Reuse them with their sources; add other years only if you collect history.
- Conversion factors already sourced (price-sources REPORT, Step 1): UN Energy Statistics Yearbook 2023 Table II gallons per tonne; IPCC 2006 Vol. 2 Table 1.2 net calorific values; 1.055056 GJ/MMBtu. Reuse them with those citations.
- Downloads from the earlier job are on this machine only, at `MODELS_LAC_5/_LAC_HUB/price_sources_20261109T003525Z/downloads/`. Read them as leads; copy any file you rely on into this job's `downloads/` folder and cite its original URL.

## 4. Setup

- Environment: Windows, Git Bash, the `py` launcher. Run your scripts with `py -I`. pandas and openpyxl are installed. If you need a PDF text reader and none is installed, you may run `py -m pip install --user pdfplumber pypdf`; record it in CHANGES. Install nothing else. Use your web search and web fetch tools. You may run one sub-task per country in parallel.
- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Use it in the output folder name and the three output file names.
- New clone from the local main copy, then point it at GitHub:

```bash
git clone /c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5 /c/clw_local_prices
cd /c/clw_local_prices
git remote set-url origin https://github.com/luviga/clewise-lac.git
git fetch origin
git checkout -b job/local-prices c5ca4ee
```

  If `c5ca4ee` is missing from the local clone, clone from GitHub instead (about 2 GB) and branch from the same commit.
- Job folder: `C:\clw_local_prices\_LAC_HUB\local_prices_<stamp>\`, with `downloads\` inside it for every source file. `.gitignore` already keeps `/_LAC_HUB/**/downloads/` and every PDF, HTML, DOCX and PPTX under `_LAC_HUB` out of commits, so downloaded documents stay on this machine.
- Write only inside the job folder. The pull request adds files there and nowhere else.
- Read-only: every other file in `C:\clw_local_prices`, the main copy `MODELS_LAC_5` (including its `_LAC_HUB`), and every other `C:\clw_*` folder. Do not open anything under `C:\Users\luisfernando\Dropbox\`.
- Expected run time: 4 to 8 hours. Sleep must be off on the machine.

## 5. Work

### Step 1. Baseline and row list

1. Record SHA-256 of the six energy A-O workbooks and the six BAU `InputActivityRatio.csv` and `OutputActivityRatio.csv` files in the clone (`baseline_before.csv`). Energy folders: `CostaRica/CR_ENERGY/t1_confection`, `DominicanRepublic/RD_ENERGY`, `Ecuador/ECU_Energy`, `Guatemala/GUA_ENERGY`, `Honduras/HON_ENERGY`, `Jamaica/JAM_ENERGY`; workbook `A1_Outputs/A-O_Parametrization.xlsx`; ratios under `A2_Output_Params/BAU/`.
2. Recompute the supply-to-consumer table in section 3 from the BAU ratio files and save it as `consumers.csv` (country, supply row, fuel code out, consumer technology, consumer type power or demand or refinery or export). If it differs from section 3, record the difference in GAPS and use yours.
3. Write `coverage_before.csv`: the 55 rows of `adders_2024.csv` with their current method, plus the Jamaica, Guatemala and Honduras partial-coverage notes and the two open questions in section 3.

### Step 2. Search, country by country

For each country, work through every row in `coverage_before.csv` that is not fully observed locally, in this order of weight in the models:

1. Coal and petroleum coke where they feed power plants (Dominican Republic, Guatemala, Honduras), then where they feed industry and cement (all six).
2. Natural gas where it feeds power plants (Guatemala, Honduras, Ecuador; extend Jamaica to 12 months; confirm the Dominican Republic).
3. Fuel oil, all six, with the generator-delivered price first.
4. Diesel, then gasoline, LPG, kerosene, jet, crude, aviation gasoline.

For each row, collect 2024 first. Record each published component separately: import cost (FOB, freight, insurance, port), importer or terminal margin, wholesale margin, inland freight, retail margin, and the delivered price to generators where published. Record the price as published (currency, unit, period, tax treatment, calorific basis if stated) and the conversion to USD/GJ. After every 2024 row is done, and only where the same publisher gives a consistent annual series, also record 2018 to 2025 in nominal terms with the year.

Log every attempt in `search_log.csv` (country, fuel, lead, URL or query, date, result: value found, no value, blocked with HTTP status, paywalled, image only). An ASSUMPTION candidate is allowed for a row only when every lead below for that country and fuel appears in the log.

Leads by country. Try them all for the open rows; add others you find.

- All countries:
  - National customs or central bank import statistics by HS code (2701 coal, 2713 petroleum coke, 2709 crude, 2710 refined products, 2711 LPG and LNG), giving CIF value and quantity for 2024.
  - UN Comtrade (public preview API or website) for the same HS codes, as a second source or where national data do not open.
  - The national energy balance and its methodology notes (also the source for Step 3).
- Costa Rica: ARESEP fuel price resolutions and RECOPE price structures (already used for liquids); PROCOMER or BCCR import statistics and Ministerio de Hacienda customs data for coal and petroleum coke used by cement; ICE or ARESEP generation cost filings for diesel and bunker at thermal plants; MINAE energy balance.
- Dominican Republic:
  - Ministerio de Energía y Minas monthly fuel and coal bulletins (coal fob Puerto Bolívar and Platts quotes already seen; look for delivered coal, LNG and fuel oil).
  - OC-SENI declared variable costs and fuel prices of generators (Punta Catalina, Itabo, AES Andrés, others).
  - Superintendencia de Electricidad and CNE publications; MICM weekly price notices (gasoline and LPG market-tracking parity for the open question; the MICM open-data workbook 2010 to 2025 returned HTTP 403 last time).
  - DGA customs and ONE trade statistics; REFIDOMSA reports for crude imports.
- Ecuador:
  - EP Petroecuador statistical reports (import unit values already used; look for terminal and commercialisation margins, domestic natural gas and fuel oil values, crude export prices).
  - ARCERNNR resolutions on terminal prices and commercialisation margins.
  - Ministerio de Energía y Minas; CENACE annual and monthly reports with fuel prices or variable costs of thermal plants, including natural gas plants.
  - Banco Central del Ecuador trade and oil statistics; SENAE customs.
- Guatemala:
  - MEM weekly price structures and statistics (extend to 52 weeks; import statistics by fuel, including coal and petroleum coke).
  - AMM reports of declared variable costs and fuel prices of coal, bunker and diesel plants (`wl12.amm.org.gt` and `reportesbi.amm.org.gt` were dynamic last time; try their downloadable files).
  - CNEE tariff studies and any public document for the natural gas supply of planned plants (the PEG tender documents).
  - Banguat trade statistics.
- Honduras:
  - Secretaría de Energía weekly price bulletins and the import parity structure (all of 2024; bulletins 9, 14 and 22 were missing and 30 and 31 image-only).
  - Secretaría de Energía annual hydrocarbon report (CIF values already used; look for margins).
  - CREE resolutions on generator fuel prices (bunker already used; look for coal, petroleum coke and diesel).
  - ENEE and the system operator ODS or CND reports with plant variable costs (`appcnd.enee.hn:3200` refused connection; try other ENEE pages).
  - Gaceta oficial (`gaceta.iaip.gob.hn` did not respond) and any public LNG supply documents for planned gas plants.
  - BCH trade statistics.
- Jamaica:
  - Petrojam weekly ex-refinery prices and annual reports (`petrojam.com` returned HTTP 403 to automated tools; put the exact pages on the manual list).
  - OUR monthly fuel and IPP charge determinations and JPS fuel cost reports (extend HFO, natural gas and diesel to 12 months of 2024).
  - Ministry of Science, Energy, Telecommunications and Transport price notices; PCJ; STATIN trade statistics and Bank of Jamaica for coal and petroleum coke imports; the Jamaica Gazette for margins.

Where a page refuses automated access or is image-only and you cannot read it, add it to the manual list and keep going.

### Step 3. Calorific basis

Find which energy balance the six models' fuel quantities come from: search the clone's tracked scripts, READMEs and input workbooks for the names of balances (OLADE SIELAC, national energy balances) as leads, then open the external balance and its methodology. For each country, record whether the balance uses net or gross calorific values, and the published conversion factors for natural gas, coal, petroleum coke and fuel oil. Record the basis of every price you collect (Henry Hub and US LNG prices are gross; IPCC factors are net). Save `calorific_basis.csv` (country, balance, publisher, URL, net or gross, factor by fuel, page or table).

### Step 4. Assemble

1. `local_prices_2024.csv`: one row per country, fuel and price point (generator delivered, wholesale import parity, final consumer pre-tax). Columns: country, fuel, model code, price point, each component as published, currency, unit, period, months covered, tax treatment, calorific basis, exchange rate and its source, conversion constants and their sources, value in USD/GJ, evidence class, source id, page or table, downloaded file name. Evidence classes: `local regulator or operator`, `local customs or statistics`, `international customs (Comtrade)`, `built from published components` (each component cited), `ASSUMPTION candidate` (with its sentence).
2. `local_history.csv`: the same layout for 2018 to 2025, only where Step 2 found a consistent series.
3. `coverage_after.csv`: the 55 rows with their new evidence class, the old one, and the row's 2024 value from both jobs side by side.
4. `manual_downloads.csv`: URL, page title or document name, publisher, what it should hold, rows it closes, why it is needed, how it failed (HTTP status, timeout, image only, login), and a file name to save it under. Sort by weight as in Step 2. Luis will save these files in `C:\clw_local_prices\_LAC_HUB\local_prices_<stamp>\downloads\manual\` and a follow-up job will read them.
5. `sources.csv`: id, URL, title, publisher, date, retrieval date, downloaded file name, rows it supports.

### Step 5. Gates

1. Read-only: recompute the hashes of Step 1.1 (`baseline_after.csv`). They must equal `baseline_before.csv`.
2. After the commit, `git diff --name-only c5ca4ee HEAD` lists only files inside `_LAC_HUB/local_prices_<stamp>/`.
3. Tracked files in the job folder are only `.md`, `.csv`, `.py` and `.txt`; nothing under `downloads/` is tracked (`git ls-files _LAC_HUB/local_prices_<stamp>/downloads` prints nothing).
4. Every row of `local_prices_2024.csv` whose evidence class is not `ASSUMPTION candidate` names a source id in `sources.csv` and a file that exists in `downloads/`; write the check as a script and report its counts.
5. Every ASSUMPTION candidate row has, in `search_log.csv`, an entry for each lead of section 5 for its country and fuel; write the check as a script and report its counts.
6. Every number in REPORT traces to a CSV in the job folder.
7. `git diff --check` passes, and no output file contains an em dash or a machine path outside quoted URLs.

### Step 6. Pull request

- Copy this brief into the job folder as `BRIEF_LAC_LOCAL_PRICES.md`.
- One commit with the job folder's tracked files. Push `job/local-prices` and open one draft pull request titled "LAC_LOCAL_PRICES: per-country published fuel prices", body taken from CHANGES.
- If the push or the pull request fails (permissions, authentication), keep the local commit, record the exact error in REPORT, and finish the outputs.

## 6. Outputs

All three in `_LAC_HUB/local_prices_<stamp>/`, plain English, no em dashes.

`REPORT_LAC_LOCAL_PRICES_<stamp>.md`: start with the pull request number, branch, commit hash and the gate results with counts. Then a coverage table, country by fuel, before and after, by evidence class. Then, for each country, the 2024 values found for coal, petroleum coke, natural gas and fuel oil with full working, and the components found for the liquids. Then the two open questions with both sides in numbers (Dominican gasoline and LPG; Ecuador fuel oil import and export). Then the calorific basis by country. Then the length of the manual download list and the rows it would close.

`GAPS_LAC_LOCAL_PRICES_<stamp>.md`: every judgement call and its reason; every row left as an ASSUMPTION candidate with the leads tried; sources blocked or paywalled; differences from the earlier price-sources values above 10 percent and their likely cause; "Known-limitation candidates"; anything left unchecked; incidents.

`CHANGES_LAC_LOCAL_PRICES_<stamp>.md`: every file created or downloaded, with its purpose or origin URL in one line; any package installed; confirmation that no model file changed.

Supporting files: `baseline_before.csv`, `baseline_after.csv`, `consumers.csv`, `coverage_before.csv`, `coverage_after.csv`, `search_log.csv`, `calorific_basis.csv`, `local_prices_2024.csv`, `local_history.csv`, `manual_downloads.csv`, `sources.csv`, your helper scripts, and `downloads/` (local only).
