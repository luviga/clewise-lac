# PROGRESS LAC_VEHICLE_PRICES

Stamp: 20261123T163210Z. Branch: job/vehicle-prices. Pull request #16 not merged at start: its files are read from origin/job/cost-sources into a temporary folder.

| Step | Status | Notes |
| --- | --- | --- |
| Setup | done | clone, venv, job folder |
| 1 Vehicle classes and tariff lines | done | vehicle_class_map.csv, 176 rows; scope_cells.csv, 2,892 cells |
| 2 Import statistics | done | Comtrade 25 files; national routes searched (search logs); units only for JAM (Comtrade 2019-2021) and DR (DGA bulletins by vehicle type) |
| 3 Unit values | done | scripts/build_prices.py, national_parsers.py; unit_values and class_prices per country |
| 4 Proposals | next | |
| 5 Gates | | |
| 6 Pull request | | |
