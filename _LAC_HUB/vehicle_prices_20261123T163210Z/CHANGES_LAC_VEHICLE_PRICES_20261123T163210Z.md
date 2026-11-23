# CHANGES LAC_VEHICLE_PRICES 20261123T163210Z

Pre-tax vehicle prices from government import statistics, as proposals for the 2,892 vehicle CapitalCost cells of CR_ENERGY, RD_ENERGY, GUA_ENERGY, HON_ENERGY and JAM_TRANSPORT. Read-only for the models: every file is in `_LAC_HUB/vehicle_prices_20261123T163210Z/`. The downloaded files sit in the job's `downloads/` folder, which is not tracked.

## Job folder

- `scope_cells.csv`: the 2,892 cells in scope (CapitalCost rows of the ENERGY and TRANSPORT models in the cost-sources proposal files), with their current values, units, projection modes, cell locators and the later-year price path of those proposals.
- `vehicle_class_map.csv`: one row per model and technology (176), with vehicle class, powertrain, the HS 2017 and HS 2022 six-digit lines that hold it, the truck weight band and one sentence on why. Lines follow the WCO nomenclature (HS-001, HS-002).
- `national_type_map.csv`: which Dominican customs vehicle types (cars, jeepetas, buses) price which model classes and powertrains.
- `parameters.csv`: every constant of the formulas (minimum of 10 units per line-year, years 2019 to 2023, price year 2024, CPI series, exchange-rate indicator, the 25 percent confirmation band, the factor 1000 of the compiled unit, the rejected Comtrade quantities), each with a source id or an ASSUMPTION sentence.
- `manual_downloads.csv`: six files or data requests that no route could reach by script (Guatemala SAT twice, Dominican ONE, Costa Rica Hacienda, Honduras customs, Jamaica STATIN), with the URL, the clicks, the file name, the folder and the rows that wait on each.
- `gates_result.md`: results of the eight gates.
- `PROGRESS.md`: step log of the job.

## Per country (`CR`, `DR`, `GUA`, `HON`, `JAM`)

- `search_log_<CC>.csv`: every attempt on routes 1 to 3 (URL, date, HTTP status, result), including the 25 UN Comtrade requests.
- `unit_values_<CC>.csv`: per tariff line (or customs vehicle type) and year, the customs value as published, currency, exchange rate, CPI factor, value in 2024 US$, units, unit value, and whether and why the line-year enters the average.
- `class_prices_<CC>.csv`: per technology, the base price in 2024 US$ per vehicle and how it was formed (own lines, own customs counts by vehicle type, the same lines in the other four countries, or the diesel vehicle of the class times the ATB powertrain ratio).
- `proposals_<CC>.csv`: one row per cell, with the columns of the cost-sources proposal files plus `unit_introduced_proposed`. The base-year cells hold the new prices or ratios; the later-year multipliers are those of the cost-sources proposals, unchanged; Costa Rica cells are prices per vehicle in every year.
- `sources_<CC>.csv`: the sources the rows cite or name in their derivations, with a `source_type` column.

## Scripts (`scripts/`)

- `make_scope.py`, `make_class_map.py`: write `scope_cells.csv` and `vehicle_class_map.csv`.
- `download_comtrade.py`: UN Comtrade annual imports with each country as reporter, partner World, one request per year, logged.
- `national_parsers.py`: readers for the Dominican customs vehicle bulletins and for tables saved by hand under `downloads/manual/<CC>/`.
- `build_prices.py`: unit values and class prices; reads only `downloads/`, `parameters.csv` and the two maps.
- `build_proposals.py`, `build_sources.py`: proposal and source files.
- `gates.py`: the eight gates.
