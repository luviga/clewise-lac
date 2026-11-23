# Vehicle cost chain: from US$ per vehicle to M US$ per Gvkm

Models: Costa Rica (`CostaRica/CR_ENERGY/t1_confection`, compiler `A2_Compiler_CostaRica.py`), Dominican Republic (`DominicanRepublic/RD_ENERGY`, `A2_Compiler_DominicanRepublic.py`), Guatemala (`Guatemala/GUA_ENERGY`, `A2_Compiler_Guatemala.py`), Honduras (`Honduras/HON_ENERGY`, `A2_Compiler_Honduras.py`) and Jamaica transport (`Jamaica/JAM_TRANSPORT`, `A2_Compiler.py`). The five compilers hold the same vehicle block (Costa Rica reads the same strings from `MOMF_T1_A.yaml`). The A1 scripts (`A1_Model_Structure*.py`) only build the workbook layout; no vehicle cost is computed there.

## 1. What the compiler does

The A2 compiler reads the `Vehicle Techs` sheet of `A1_Outputs/A-O_Parametrization.xlsx` row by row. For a cost row (CapitalCost or FixedCost) it first builds a yearly series in the unit the row was entered in, then converts it.

Step 1, yearly series in the entered unit (`Unit.Introduced`), with `BY` the first year column of the sheet (2018; 2021 in JAM_TRANSPORT):

- `Flat`: every year takes the BY cell.
- `User defined`: every year takes its own cell.
- `User defined trajectory relative to BY`, unit `US$ / vehicle`: BY keeps its cell; every later year is BY cell times that year's cell, so the year cells are multipliers on the BY price (for example Honduras `TRAUTELE`: 23,065.81 US$ in 2018, multiplier 0.6667 in 2030, 0.6345 in 2050).
- `Relative to <REF>` with `Flat`: every year is the BY cell of `<REF>` times the BY cell of the row (the row holds a ratio to the reference vehicle's base-year price).
- `Relative to <REF>` with `User defined trajectory relative to BY`: BY is the BY cell of `<REF>` times the BY cell of the row; every later year is that product times the year's cell (multiplier).

The reference value is always the raw BY cell of `<REF>`. If `<REF>` is itself a "Relative to" row, its raw cell is a ratio, not a price, and the chain breaks. This happens in Guatemala: `TRAUTHG` and `TRAUTPHG` are "Relative to TRAUTELE", and `TRAUTELE` is "Relative to TRAUTDSL", so both compile from 1.0 x 1.3333 = 1.33 US$ per vehicle to 0.0694 M US$ per Gvkm in 2030 (a near-zero capital cost).

Step 2, conversion. When `Unit` contains "Gvkm" and `Unit.Introduced` contains "vehicle" or "Relative", each year is converted as

`CapitalCost[y] (M US$ per Gvkm) = 1000 x price[y] (US$ per vehicle) / km[y] (km per vehicle per year)`

(US$ per vehicle divided by km per vehicle-year gives US$ per km of annual capacity; times 1e9 km per Gvkm and divided by 1e6 US$ per M US$ gives the factor 1000). Capacity rows entered in "Vehicles" are converted the other way (vehicles x km / 1e9 = Gvkm). FixedCost rows are entered directly in M US$ per Gvkm and are not converted; one Costa Rica row (`TRNPASRAIELE`, rail) is entered in M US$ per GPkm and is not converted either.

## 2. Distance per vehicle

`km[y]` comes from the vehicle's group (`A1_Outputs/A-O_Fleet_Groups.pickle`, for example `Techs_Auto` holds `TRAUTDSL`, `TRAUTGSL`, `TRAUTELE`, `TRAUTHG`). The base-year distance is the group's `Ref.km.BY` cell in `A1_Outputs/A-O_Demand.xlsx`. Each later year multiplies the previous one by (1 + change / 100), with the change taken from `A2_Extra_Inputs/A-Xtra_Projections.xlsx`, column `Variation_km_Passenger` (or `Variation_km_Freight` for groups with "Freight" in the name). In Honduras and the Dominican Republic the change is -25 percent in 2020 and +15.47 percent in 2021 and zero otherwise, so the distance returns to its base value (7,500 km for automobiles; 7,500.006 after rounding). In Costa Rica, Guatemala and JAM_TRANSPORT the distance is constant. Some groups carry a placeholder distance of 1 km (Costa Rica rail, JAM_TRANSPORT aviation and maritime), and their capital cost rows are zero today; a price per vehicle entered there would compile to 1000 times its value in M US$ per Gvkm. The series the compiler used is saved in `A1_Outputs/A-O_Fleet_Groups_Distance.pickle`; the check below uses that file. Every vehicle in a group shares one distance, so the distance does not change the ranking of vehicles inside a group, but it scales the capital cost of the whole group against the fuel costs, and it scales the electric vehicles' capital cost against their lower fuel cost.

## 3. Battery replacement

Every compiler opens `A2_Extra_Inputs/A-Xtra_Battery_Replacement.xlsx` into a table and never uses it again; no B1 script reads it. It enters no cost. Its technology codes also do not match most model codes (for example `TRBUSELE` and `TRMBUSELE` against the model's `TRBPUELE` and `TRMBSELE`). The rows are listed in `vehicle_chain_inputs.csv` with `used_by_compiler = no`.

## 4. OperationalLife

OperationalLife comes from the `Fixed Horizon Parameters` sheet. It sets how the capital cost is spread over years in the solver. Several values are one year: Dominican Republic automobiles, motorcycles and taxis (`TRAUT*`, `TRMOT*`, `TRTAX*`), and Costa Rica minibuses (`TRNMIC*`). A one-year life makes the full vehicle price fall in the year of purchase, with a new purchase every year. Where the sheet has a "Source / Assumption" column (Guatemala, Honduras, JAM_TRANSPORT), every vehicle OperationalLife row says "Provisional"; Costa Rica and the Dominican Republic have no source column.

## 5. Check: recompute against the compiled BAU CapitalCost

All CapitalCost rows were recomputed from the A-O inputs and the saved distance series for 2024, 2030 and 2050 (`vehicle_chain_check.csv`). Every row with a compiled value matches to four decimals: Costa Rica 41 of 41, Dominican Republic 41 of 41, Guatemala 39 of 39, Honduras 30 of 30, JAM_TRANSPORT 35 of 35, in each of the three years. Costa Rica (5) and the Dominican Republic (3) have rows with a zero price and no compiled value.

Three vehicles per model, 2030:

| Model | Tech | Unit.Introduced | Projection | US$ per vehicle | km per vehicle-year | Recomputed M US$ per Gvkm | Compiled BAU |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CR_ENERGY | TRNSEDGSL | US$ / vehicle | User defined | 710.69 | 12,095 | 58.7591 | 58.7591 |
| CR_ENERGY | TRNSEDELE | US$ / vehicle | User defined | 1,130.21 | 12,095 | 93.4443 | 93.4443 |
| CR_ENERGY | TRNBUSDSL | US$ / vehicle | User defined | 1,627.42 | 58,999 | 27.5838 | 27.5838 |
| RD_ENERGY | TRAUTDSL | US$ / vehicle | Flat | 11,525.00 | 7,500.006 | 1536.6654 | 1536.6654 |
| RD_ENERGY | TRAUTLPG | Relative to TRAUTDSL | Flat | 16,135.00 | 7,500.006 | 2151.3316 | 2151.3316 |
| RD_ENERGY | TRAUTELE | US$ / vehicle | trajectory relative to BY | 20,000.05 | 7,500.006 | 2666.6709 | 2666.6709 |
| GUA_ENERGY | TRAUTDSL | US$ / vehicle | Flat | 16,597.12 | 19,220 | 863.5338 | 863.5338 |
| GUA_ENERGY | TRAUTLPG | Relative to TRAUTDSL | Flat | 23,235.97 | 19,220 | 1208.9473 | 1208.9473 |
| GUA_ENERGY | TRAUTHG | Relative to TRAUTELE | trajectory relative to BY | 1.33 | 19,220 | 0.0694 | 0.0694 |
| HON_ENERGY | TRAUTDSL | US$ / vehicle | Flat | 11,525.00 | 7,500.006 | 1536.6654 | 1536.6654 |
| HON_ENERGY | TRAUTELE | US$ / vehicle | trajectory relative to BY | 15,377.24 | 7,500.006 | 2050.2975 | 2050.2975 |
| HON_ENERGY | TRAUTHG | Relative to TRAUTELE | trajectory relative to BY | 15,358.97 | 7,500.006 | 2047.8610 | 2047.8610 |
| JAM_TRANSPORT | TRAUTDSL | US$ / vehicle | Flat | 11,525.00 | 12,000 | 960.4167 | 960.4167 |
| JAM_TRANSPORT | TRAUTELE | US$ / vehicle | trajectory relative to BY | 16,705.24 | 12,000 | 1392.1034 | 1392.1034 |
| JAM_TRANSPORT | TRAUTHG | Relative to TRAUTELE | trajectory relative to BY | 16,685.39 | 12,000 | 1390.4490 | 1390.4490 |

## 6. Costa Rica unit

Costa Rica's rows are labelled "US$ / vehicle" and compile through the same formula, but the entered values are far below a vehicle price: a diesel bus at 1,627 and a gasoline sedan at 711 "US$ per vehicle" in 2030. Multiplied by the group distance and divided by 1000 they give plausible prices (diesel bus 96,016 US$, gasoline sedan 8,596), so the cells most likely already hold M US$ per Gvkm and the compiler divides them by the distance a second time; compiled capital costs are then 12 to 59 times too low. The cells are plain numbers except the hybrid taxi rows (from 2023 each cell repeats the previous year by formula) and the rail rows (a constant divided by 0.7315286784). Proposals for Costa Rica give prices per vehicle in the labelled convention, and the unit is reported as a decision (section "Costa Rica" of the REPORT).

## 7. Inputs a vehicle choice depends on

`vehicle_chain_inputs.csv` lists, per model and vehicle, the base-year distance and its 2030 and 2050 values, the OperationalLife (with any source text), and every battery replacement row. Phase 2 sources the distance per vehicle and the OperationalLife; the battery rows are listed because they enter no cost.
