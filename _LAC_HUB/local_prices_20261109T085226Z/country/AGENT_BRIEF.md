# Country sub-task brief, job LAC_LOCAL_PRICES 20261109T085226Z

You are one of six country sub-tasks. You work alone to the end and never ask anyone anything. Coverage matters more than speed: try every lead listed for your country, and add others you find. Plan on several hours of work if needed.

Read these first (all inside the job folder `_LAC_HUB/local_prices_20261109T085226Z/` of the job clone):

- `BRIEF_LAC_LOCAL_PRICES.md`: the job brief. Sections 1, 2, 3 and 5 (Step 2) apply to you.
- `STEER_1.md`: additions to the brief that override it (constants, retrievability).
- `coverage_before.csv`: the 55 country and fuel rows and their current status. Your open rows are those whose `status_before` starts with `open`, plus the `notes_before` items for your country (partial coverage, open questions).
- `consumers.csv`: which model technologies each supply row feeds (power, demand, refinery, export).

Leads only, never cite: the earlier job's outputs in `_LAC_HUB/price_sources_20261109T003525Z/` of the job clone (REPORT, GAPS, `adders_2024.csv`, `adders_working.txt`, `sources.csv`) and its downloads in the same folder of the main copy MODELS_LAC_5, under `downloads/<CC>/` (read only; the path was given to the sub-tasks in full during the run). If you rely on a document the earlier job used, fetch it again from its original URL in this session and save that fresh copy. If the original URL no longer returns it, you may not cite it: log it and put it on your manual list.

## Where you write

Only these two folders (create them). Nothing anywhere else on the machine, including temp folders and scratchpads.

- `...\local_prices_20261109T085226Z\downloads\<CC>\` for every downloaded file (PDF, XLS, HTML, JSON, PNG renders) and any scratch output. Not committed.
- `...\local_prices_20261109T085226Z\country\<CC>\` for your CSVs, your notes file and your `.py` scripts. Committed. Only `.csv`, `.md`, `.py`, `.txt` here.

`<CC>` is your code: CR, DR, ECU, GUA, HON, JAM. Never run git. Never edit any other file. Run Python as `py -I script.py args` with scripts saved in `country\<CC>\`, and pass paths as arguments. pandas, openpyxl, xlrd, pdfplumber, pypdf (pdfplumber can render a page to PNG through pypdfium2) and `pdftotext` are installed; install nothing. You can view a PNG or an image-only PDF page with your Read tool and transcribe numbers from it; record that the value was read from an image.

Download with `curl -L -sS -o <file> -w "%{http_code}" "<url>"` and check the file type afterwards. Do not try to get around a site that blocks automated access (no user-agent spoofing, no CAPTCHA solving, no proxies or cache mirrors used to defeat a block): log the status and put the page on the manual list. Use your web search and fetch tools to find documents. A search-results page is never a citation; the citation is the URL that returns the file itself (for a query or API, the full query URL).

## What to produce, in `country\<CC>\`

All CSVs UTF-8, comma separated, with exactly these headers. No em dashes anywhere. No machine paths in any field (file names are relative to `downloads\`, for example `CR/aresep_re0040.pdf`).

1. `prices_<CC>.csv`, 2024 values, one row per fuel and price point:
   `country,fuel,model_code,price_point,year,fob,freight,insurance,port,importer_terminal_margin,wholesale_margin,inland_freight,retail_margin,price_as_published,currency,unit,period,months_covered,tax_treatment,calorific_basis,exchange_rate,exchange_rate_constant,conversion_constants,value_usd_per_gj,evidence_class,source_id,page_or_table,downloaded_file,derivation,notes`
   - `fuel`: COA, COK, NGS, FOI, DSL, GSL, LPG, KER, JET, CRU, AVG. `model_code`: the supply row from `coverage_before.csv`.
   - `price_point`: one of `generator delivered`, `wholesale import parity`, `final consumer pre-tax`, `import CIF`, `export FOB`. Record each point that is published, separately.
   - Component columns: the published value in the published currency and unit (same unit as `price_as_published`); leave empty when not published and say why in the search log.
   - `tax_treatment`: as stated by the source (for example `pre-tax`, `includes VAT`, `excludes excise and VAT`).
   - `calorific_basis`: `net`, `gross` or `not stated`, as the source states it; the basis of the factor you used to convert goes in `derivation`.
   - `exchange_rate_constant`, `conversion_constants`: names from your `constants_<CC>.csv` or the shared constant names below, separated by `;`.
   - `evidence_class`: one of `local regulator or operator`, `local customs or statistics`, `international customs (Comtrade)`, `built from published components` (each component cited in `derivation` with its source id), `ASSUMPTION candidate` (sentence in `notes`, following brief section 2; allowed only after every lead for that fuel is in your search log).
   - `source_id`: an id in your `sources_<CC>.csv` (several separated by `;` when built).
   - `derivation`: every arithmetic step with every constant named, for example `331.11 CRC/L / 518.23 CRC/USD (CR_FX_2024) x 3.785411784 L/USgal (L_PER_USGAL) / 0.1414 GJ/USgal ...`. Months averaged: list them.
2. `history_<CC>.csv`: same header, years 2018 to 2025 nominal, only where one publisher gives a consistent annual series (do this after every 2024 row is done).
3. `sources_<CC>.csv`: `id,url,title,publisher,date,retrieval_date,downloaded_file,page_or_table,rows_and_constants_supported`. Ids `<CC>-001`, `<CC>-002`, ... One row per document. `url` must be the http(s) URL that returns the file. `retrieval_date` 2026-11-09 (or the actual date). Only documents you opened in this session and saved in `downloads\<CC>\`.
4. `constants_<CC>.csv`: `name,value,unit,source_id,page_or_table,derivation`. Every exchange rate and any country-specific factor (density, calorific value from a local publisher, unit factor) your prices pass through. Name them `<CC>_...`, for example `CR_FX_2024`. Exchange rates: download the publisher's file (daily or annual) for 2024 (and each history year you use); where you compute a mean from daily rates keep the daily file and the script, and write the mean in `derivation`. Earlier-job values to re-confirm: CRC 518.23 (BCCR daily reference rates, mean of selling rate), DOP 59.5665 (BCRD annual average), GTQ 7.7596 (Banguat reference rate mean), JMD 157.22 (Bank of Jamaica annual average). Honduras: use the BCH reference rate if any value is published in lempiras. Ecuador uses USD.
5. `search_log_<CC>.csv`: `country,fuel,lead_id,lead,url_or_query,date,result,detail`. One row per attempt per fuel (an attempt covering several fuels gets one row per fuel). `result` is one of `value found`, `no value`, `blocked HTTP <code>`, `timeout`, `paywalled`, `image only`, `login required`, `not found`. `lead_id` must use the ids below exactly; extra leads you find get `other_<short name>`.
6. `manual_<CC>.csv`: `url,title,publisher,should_hold,rows_it_closes,why_needed,how_failed,save_as,weight_rank`. `weight_rank` per brief Step 2 order: 1 coal and petcoke to power, 2 coal and petcoke to industry, 3 natural gas to power, 4 fuel oil, 5 diesel, 6 gasoline, LPG, kerosene, jet, crude, avgas. `save_as` is a file name for `downloads\manual\`.
7. `calorific_<CC>.csv`: `country,balance,publisher,url,net_or_gross,factor_NGS,factor_COA,factor_COK,factor_FOI,factor_units,page_or_table,source_id`. The national energy balance for your country (and OLADE SIELAC as second source if the national one does not state it): whether it uses net or gross calorific values, and its published conversion factors for natural gas, coal, petroleum coke and fuel oil, with units. Download the balance or its methodology note.
8. `notes_<CC>.md`: plain English, no em dashes. Sections: Summary (what was closed, what is still open); Judgement calls and reasons; Values that could not be sourced externally; Differences above 10 percent from the earlier job's values in `adders_2024.csv` (`observed_import_cost_usd_per_gj` or `pre_tax_price_2024_usd_per_gj`) and likely cause; Known-limitation candidates (where, one sentence each); Left unchecked; Incidents.

## Shared constants (do not source these yourself; the main session sources them)

Use these names in `conversion_constants`: `L_PER_USGAL` (3.785411784), `USGAL_PER_BBL` (42), `GJ_PER_MMBTU` (1.055056), `KCAL_TO_KJ` (4.1868), `UN_GAL_PER_T_<fuel>` (UN Energy Statistics Yearbook gallons per tonne: GSL 357, DSL 304, JET 326, KER 326, FOI 278, LPG 489, AVG 362), `UN_BBL_PER_T_CRU` (7.32), `IPCC_NCV_<fuel>` (IPCC 2006 Vol. 2 Table 1.2 net calorific values, GJ/t: GSL 44.3, DSL 43.0, JET 44.1, KER 43.8, FOI 40.4, LPG 47.3, AVG 44.3, CRU 42.3, COK 32.5, COA_OTHER_BITUMINOUS 25.8, NGS 48.0), `MMBTU_PER_MCF_EIA` (1.037). If you need another general factor, add it to your `constants_<CC>.csv` with a downloaded source. Where a source publishes its own calorific value or density for the fuel, prefer that and record it as a `<CC>_` constant.

## Rules that matter most

- Local publishers first; regional or international second (Comtrade is evidence class `international customs (Comtrade)`). Never a value from another country.
- Open every source you cite in this session, confirm value, unit, period and tax treatment, save the file, then record.
- For each row: 2024 first. Each published component separately. Generator-delivered price and pre-tax final consumer price both, where published.
- Comtrade: the public preview API works without a key, for example `https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=<M49>&period=2024&partnerCode=0&flowCode=M&cmdCode=2701,2713,2709,2710,2711` (M49: Costa Rica 188, Dominican Republic 214, Ecuador 218, Guatemala 320, Honduras 340, Jamaica 388). Save the JSON response and cite the full query URL. Use `cifvalue` and `netWgt` (kg); record `qtyUnitAbbr` and `isQtyEstimated`/`isNetWgtEstimated` flags. For petroleum products use 6-digit codes too (271012 light oils, 271019 medium and heavy oils incl. diesel and fuel oil, 271111 LNG, 271112-271119 LPG, 271121 natural gas gaseous), and note when a 6-digit code mixes products.
- A page that refuses automated access or is image only and cannot be read: put it on the manual list and keep going.
- When everything for your country is done, reply with a short summary (under 300 words): rows closed by evidence class, rows still open, manual list length, anything the main session must know. Do not paste your CSVs into the reply.

## Lead ids

All countries: `customs_national` (national customs or central bank import statistics by HS 2701, 2713, 2709, 2710, 2711 with CIF value and quantity, 2024), `comtrade` (UN Comtrade, same HS codes), `energy_balance` (national energy balance and methodology notes).

- CR: `aresep_recope` (ARESEP fuel price resolutions, RECOPE price structures), `procomer_bccr_hacienda` (PROCOMER, BCCR or Ministerio de Hacienda customs data, coal and petroleum coke for cement), `ice_aresep_generation` (ICE or ARESEP generation cost filings, diesel and bunker at thermal plants), `minae_balance` (MINAE/SEPSE energy balance).
- DR: `mem_bulletins` (Ministerio de Energia y Minas monthly fuel and coal bulletins), `ocseni` (OC-SENI declared variable costs and fuel prices of generators), `sie_cne_micm` (Superintendencia de Electricidad, CNE, MICM weekly price notices and open data), `dga_one_refidomsa` (DGA customs, ONE trade statistics, REFIDOMSA).
- ECU: `petroecuador` (EP Petroecuador statistical reports), `arcernnr` (ARCERNNR resolutions on terminal prices and commercialisation margins), `mem_cenace` (Ministerio de Energia y Minas, CENACE reports with thermal plant fuel prices or variable costs), `bce_senae` (Banco Central del Ecuador trade and oil statistics, SENAE customs).
- GUA: `mem_gua` (MEM weekly price structures, statistics, import statistics incl. coal and petcoke), `amm` (AMM declared variable costs and fuel prices; downloadable files), `cnee_peg` (CNEE tariff studies, PEG tender documents for natural gas), `banguat` (Banguat trade statistics).
- HON: `sen_weekly` (Secretaria de Energia weekly price bulletins and import parity structure, all of 2024), `sen_annual` (SEN annual hydrocarbon report), `cree` (CREE resolutions on generator fuel prices), `enee_ods_cnd` (ENEE, ODS, CND plant variable cost reports), `gaceta_lng` (Gaceta oficial, LNG supply documents for planned gas plants), `bch` (BCH trade statistics).
- JAM: `petrojam` (Petrojam weekly ex-refinery prices and annual reports), `our_jps` (OUR monthly fuel and IPP charge determinations, JPS fuel cost reports), `mset_pcj` (Ministry of Science, Energy, Telecommunications and Transport price notices; PCJ), `statin_boj` (STATIN trade statistics, Bank of Jamaica, coal and petroleum coke imports), `gazette` (Jamaica Gazette, margins).
