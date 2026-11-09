# CHANGES LAC_LOCAL_PRICES 20261109T085226Z

Job LAC_LOCAL_PRICES: per-country published fuel prices for the six LAC energy models (Costa Rica, Dominican Republic, Ecuador, Guatemala, Honduras, Jamaica), 2024 first, history 2018 to 2025 where one publisher gives a consistent series. Run from a new clone on branch `job/local-prices` from `c5ca4ee`. All files are in `_LAC_HUB/local_prices_20261109T085226Z/`.

## Result in one paragraph

Of the 55 country and fuel supply rows, the 33 open rows were searched country by country. 29 now rest on a source published for that country (local regulator or operator, local customs or statistics, UN Comtrade, or built from published local components); 4 remain ASSUMPTION candidates (natural gas in Costa Rica and Guatemala, which imported none in 2024; kerosene and jet in Jamaica). Coal and petroleum coke, all ASSUMPTION candidates before, now have a 2024 import cost in all six countries. `local_prices_2024.csv` has 176 price points, `local_history.csv` 330, `sources.csv` 352 downloaded sources, `constants.csv` 90 constants, `search_log.csv` 1,070 attempts, `manual_downloads.csv` 43 entries. Gates 1 to 7 pass (see REPORT).

## No model file changed

The SHA-256 of the six energy A-O workbooks and the six BAU `InputActivityRatio.csv` and `OutputActivityRatio.csv` files are identical before and after (`baseline_before.csv`, `baseline_after.csv`, 18 of 18). The commit adds files under `_LAC_HUB/local_prices_20261109T085226Z/` only.

## Packages

None installed. pandas, openpyxl, xlrd, pdfplumber, pypdf, PyMuPDF (installed on this machine since July 2026) and `pdftotext` were already present.

## Files created (tracked)

Job folder:

- `BRIEF_LAC_LOCAL_PRICES.md`: the job brief, copied verbatim.
- `STEER_1.md`: the hub's steer message received during the run, copied verbatim.
- `REPORT_LAC_LOCAL_PRICES_20261109T085226Z.md`, `GAPS_LAC_LOCAL_PRICES_20261109T085226Z.md`, `CHANGES_LAC_LOCAL_PRICES_20261109T085226Z.md`: the three outputs.
- `baseline_before.csv`, `baseline_after.csv`: SHA-256 of the 18 model files before and after.
- `consumers.csv`: supply row to consumer technology table recomputed from the BAU ratio files.
- `coverage_before.csv`: the 55 rows of the earlier `adders_2024.csv` with status, partial-coverage notes and open questions.
- `coverage_after.csv`: the 55 rows with old and new evidence class and values from both jobs side by side, by price point.
- `local_prices_2024.csv`: every 2024 price point found (176 rows), with components, units, tax treatment, calorific basis, exchange rate and constants with their source ids, derivation and evidence class.
- `local_history.csv`: 2018 to 2025 nominal series from single publishers (330 rows).
- `sources.csv`: 352 sources (id, URL, title, publisher, date, retrieval date, downloaded file, page or table, rows and constants supported).
- `constants.csv`: 90 constants (name, value, unit, source id, page or table, derivation), including the five exchange rates.
- `calorific_basis.csv`: 9 sourced rows on the calorific basis and factors of the national balances; `calorific_not_retrieved.csv`: 2 rows (Costa Rica) with no retrievable source.
- `search_log.csv`: 1,070 attempts (country, fuel, lead id, URL or query, date, result).
- `manual_downloads.csv`: 43 documents for Luis to fetch by hand, sorted by weight.
- `spot_checks.csv`: 9 values re-read from the downloaded documents in the main session.
- `downloads_inventory.csv`: every file under `downloads/` with its source ids and origin URL, or why it is not cited.
- `gate_check_sourcing.txt`: output of the gate 4 and gate 5 check; `scan_gate7.txt`: output of the em dash and machine path scan; `assemble_output.txt`: log of the assembly script.

`scripts/` (main session):

- `baseline.py`: SHA-256 of the 18 model files.
- `consumers.py`: builds `consumers.csv` from the BAU ratio files.
- `coverage_before.py`: builds `coverage_before.csv` from the earlier `adders_2024.csv`.
- `find_balance.py` and its output `find_balance_hits.txt`: scan of tracked energy-model files for energy balance names (leads for Step 3).
- `render_page.py`: renders one PDF page to PNG (used to read IPCC Table 1.2).
- `assemble.py`: merges the per-country files into the job outputs and builds `coverage_after.csv`.
- `check_sourcing.py`: gate 4 (STEER_1 version plus file existence) and gate 5.
- `scan_text.py`: gate 7 scan for em dashes and machine paths.
- `inventory.py`: builds `downloads_inventory.csv`.
- `normalize_eol.py`: converts Windows line endings to LF and strips trailing spaces in the job's tracked text files (content otherwise unchanged), so that `git diff --check` passes; also makes `baseline.py` and `consumers.py` write LF.

`country/` (one folder per sub-task; every CSV follows the headers in `country/AGENT_BRIEF.md`):

- `AGENT_BRIEF.md`: the written brief given to the six country sub-tasks (two machine paths replaced by folder descriptions after the run).
- `GEN/`: `sources_GEN.csv`, `constants_GEN.csv`, `search_log_GEN.csv`, `manual_GEN.csv`: shared constants (NIST, UN Energy Statistics Yearbook 2023, IPCC 2006, EIA, UN IRES) sourced by the main session.
- Each of `CR/`, `DR/`, `ECU/`, `GUA/`, `HON/`, `JAM/` holds `prices_<CC>.csv`, `history_<CC>.csv`, `sources_<CC>.csv`, `constants_<CC>.csv`, `search_log_<CC>.csv`, `manual_<CC>.csv`, `calorific_<CC>.csv` and `notes_<CC>.md`, plus:
  - CR: `build_cr.py` (builds the CSVs), `check_cr.py` (sourcing check), `extract_text.py` (PDF text by page), `make_meta_cr.py` (sources, log, manual and calorific files), `parse_aresep_cr.py` (parses the ARESEP monthly resolutions), `vuce_imports.py` (summarises PROCOMER open-data imports).
  - DR: `dr_build_outputs.py` (builds the CSVs), `dr_check_image_reads.py` (arithmetic check of values read from images), `dr_check_sources.py` (sourcing check), `dr_digitise_oc_chart.py` and `dr_digitise_oc_outline.py` (digitise OC-SENI Memoria charts), `dr_dump_words.py` (PDF word inspection), `dr_merge_weekly.py` (merges image reads into the weekly series), `dr_parse_avisos.py` (parses MICM weekly notices), `dr_render_page.py` (renders PDF pages), `dr_weekly_liquids.py` (weekly liquid fuel parity series), `dr_write_logs.py` (log, manual and calorific files); data files `dr_resolution_image_reads.csv`, `dr_weekly_ppi_2024.csv`, `dr_weekly_ngs_ppi_2024.csv`.
  - ECU: `bce_annual.py` (BCE annual oil sector values), `build_history_ECU.py`, `build_prices_ECU.py`, `build_search_log_ECU.py` (build the CSVs), `dispatch_2024.py` (dispatch unit values to the electric sector without VAT), `parse_estructuras.py` (parses EP Petroecuador price structures), `pdf_find.py`, `pdf_page_text.py`, `pdf_render.py` (PDF helpers), `structures_2024.py` (day-weighted 2024 terminal prices without VAT).
  - GUA: `gua_aggregate.py` (averages weekly structures), `gua_banguat_trade.py` (Banguat tariff lines), `gua_build.py` (builds the CSVs), `gua_estructuras.py` (parses MEM weekly structures), `gua_fx.py` (mean of Banguat daily rates), `gua_logs.py` (log and manual files), `gua_mem_imports.py` (MEM import workbooks).
  - HON: `build_hon.py` (builds the CSVs), `fx_bch.py` (BCH daily rate means), `parse_cchac.py`, `parse_cchac_glp.py`, `summarise_cchac.py` (CCHAC weekly bulletins), `parse_sen_monthly.py` (SEN monthly reports).
  - JAM: `build_jam.py` (builds the CSVs), `check_jam.py` (checks), `comtrade_summary.py` (Comtrade unit values), `contact_sheet.py` and `render_pages.py` (page images of image-only PDFs), `logs_jam.py` (log and manual files).

## Files downloaded (local only, not committed)

827 files, 589 MB, under `downloads/` (`GEN/`, `CR/`, `DR/`, `ECU/`, `GUA/`, `HON/`, `JAM/`). `downloads_inventory.csv` gives each file with its origin URL where it is a cited source (360 files cited by the 352 sources), or marks it as a probe, rendered page image, parsed output, scratch file, duplicate or superseded file. Main-session downloads (`downloads/GEN/`):

- `UNSD_EnergyYearbook2023_TableII.pdf`: https://unstats.un.org/unsd/energystats/pubs/yearbook/2023/09ii.pdf
- `UNSD_EnergyYearbook2023_TableI.pdf`: https://unstats.un.org/unsd/energystats/pubs/yearbook/2023/08i.pdf
- `UNSD_EnergyYearbook2023_units.pdf`: https://unstats.un.org/unsd/energystats/pubs/yearbook/2023/07umc.pdf
- `IPCC2006_V2_Ch1.pdf`: https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_1_Ch1_Introduction.pdf
- `NIST_SP811_2008.pdf`: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication811e2008.pdf
- `NIST_HB44_2024.pdf`: https://nvlpubs.nist.gov/nistpubs/hb/2024/NIST.HB.44-2024.pdf
- `eia_faq_45.html`: https://www.eia.gov/tools/faqs/faq.php?id=45&t=8
- `UN_IRES_2018.pdf`: https://unstats.un.org/unsd/energystats/methodology/documents/IRES-web.pdf

Deleted during the run: two empty EIA MER Table A4 exports (no data), an IEA 404 page, OLADE 403 pages, a scratch PNG of IPCC Table 1.2, and the sub-tasks' files listed in GAPS, section 8. A stray empty `/tmp/x` created in the main session was deleted.
