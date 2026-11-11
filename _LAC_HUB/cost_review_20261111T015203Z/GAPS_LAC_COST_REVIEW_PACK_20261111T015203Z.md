# GAPS LAC_COST_REVIEW_PACK 20261111T015203Z

## 1. Checks not run, and why

- Ecuador: 108 value checks not run. no number to search: the derivation states none and the proposed value is 0, 1 or empty (108).
- Ecuador: 30 value checks not found (files searchable, number absent). Likely cause read from the derivation: value converted from the published one (currency year, units); the published input is in the note (21); year value interpolated or held between published years, not printed (9). Each is listed in `value_checks.csv` with its derivation, the other inputs and whether they were found.
- Costa Rica: 9 value checks not run. no number to search: the derivation states none and the proposed value is 0, 1 or empty (9).
- Costa Rica: 0 value checks not found (files searchable, number absent). Likely cause read from the derivation: not classified. Each is listed in `value_checks.csv` with its derivation, the other inputs and whether they were found.
- Jamaica: 6 value checks not run. no number to search: the derivation states none and the proposed value is 0, 1 or empty (6).
- Jamaica: 5 value checks not found (files searchable, number absent). Likely cause read from the derivation: value converted from the published one (currency year, units); the published input is in the note (5). Each is listed in `value_checks.csv` with its derivation, the other inputs and whether they were found.
- Dominican Republic: 6 value checks not run. no number to search: the derivation states none and the proposed value is 0, 1 or empty (6).
- Dominican Republic: 78 value checks not found (files searchable, number absent). Likely cause read from the derivation: value is a sum of two published values (plant plus battery, or similar), not printed (78). Each is listed in `value_checks.csv` with its derivation, the other inputs and whether they were found.
- Guatemala: 4 value checks not run. no number to search: the derivation states none and the proposed value is 0, 1 or empty (4).
- Guatemala: 37 value checks not found (files searchable, number absent). Likely cause read from the derivation: year value built from a published anchor by an index or ratio path (ATB, IRENA decline, scaling), not printed (29); value is a mean of several published files (weekly, monthly or per-file prices), not printed in any one file (3); value converted from the published one (currency year, units); the published input is in the note (3); not classified: the hub should open the file and locator (1); year value interpolated or held between published years, not printed (1). Each is listed in `value_checks.csv` with its derivation, the other inputs and whether they were found.
- Honduras: 1 value checks not run. no number to search: the derivation states none and the proposed value is 0, 1 or empty (1).
- Honduras: 7 value checks not found (files searchable, number absent). Likely cause read from the derivation: not classified: the hub should open the file and locator (4); value converted from the published one (currency year, units); the published input is in the note (3). Each is listed in `value_checks.csv` with its derivation, the other inputs and whether they were found.
- Derivations with no arithmetic chain the parser could read (text-only derivations, or chains broken by words) were not recomputed. Counts of distinct derivations against expressions recomputed are in REPORT section 2.
- No model was run. Whether Costa Rica's `IMPELE` or the Dominican Republic's `EXTT_CRU` and `PRO_COA` are used in a least-cost solution was judged from their limits and costs only.
- Images and scanned pages in the downloads (PNG captures of Petrojam, MSET and other pages) were not searched. Every value check had at least one searchable text file among its sources, so none ended `not run` for that reason; a number printed only in an image would show as `no`.
- The decisions list was checked against its source text only for the items named in GAPS section 2, item 12.

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
- **Push and pull request.** See REPORT section 1.
