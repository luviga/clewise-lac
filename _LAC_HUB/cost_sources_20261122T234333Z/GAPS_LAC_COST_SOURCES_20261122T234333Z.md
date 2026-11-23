# GAPS LAC_COST_SOURCES 20261122T234333Z

## Judgement calls

1. Free producer. A producer is not free when its 2030 activity lower and upper limits are equal, when its 2030 TotalAnnualMaxCapacity is zero, or when its 2030 activity upper limit is zero (an activity cap at zero has the same effect as a capacity cap at zero). Every other producer is free, including those whose capacity cap equals their activity lower limit; those are flagged in `choice_sets.csv` (`free_but_capacity_equals_activity_lower_limit`) and stay free, because the brief's rule names only equal activity limits and a zero capacity cap.
2. Inactive. A technology is `inactive` when it has no output in any year and no positive activity lower limit, when it is capped at zero in every year it has an output, or when it is not in the compiled BAU model at all. A technology with no output fuel but a positive activity lower limit is `total_only`.
3. Vehicle scope. Section 5 lists "the vehicles" before "the sector-model rows of class choice". Phase 2 sources every Vehicle Techs row with a non-zero cost of a technology that produces a 2030 fuel with two or more producers, whatever its BAU class, because the BAU caps electric and hybrid vehicles at zero or at their own lower limit and the optimised scenarios compare exactly these vehicles. Vehicle rows of class `total_only` or `inactive` sourced this way keep their class in `cost_inventory.csv`.
4. Energy copies in sector models. RD_AFOLU and HON_AFOLU hold full copies of their country's energy model (plants, fuel supply, vehicles). Their rows of class `choice` whose technology also exists in the energy model are tagged `energy_copy` and are not sourced: plants and fuel supply were sourced in November, and vehicles are sourced once, in the energy model.
5. Energy models' EmissionsPenalty (RD_ENERGY and HON_ENERGY `Health`, GUA_ENERGY `Accidents`, `Congestion`, `Health`) are listed in `penalty.csv` but are outside scope (the energy models contribute only vehicles to this job).
6. Fixed Horizon source text. The brief names JAM_TRANSPORT and HON_AFOLU as the only sheets with a source column; GUA_ENERGY and HON_ENERGY also have one. All four are read into `fixed_horizon_sources.csv`.
7. GUA_AFOLU. Its live input is `2_Model/<scenario>/ModeloSuelo_<scenario>.xlsx`, which `1_csv_generation.py` turns into `1_Parameters/<scenario>/*.csv`. As the brief says, the CSV files and the structure workbook were read; the structure workbook holds sets and parameter lists, not values.
8. Vehicle chain check uses the distance series the compiler saved (`A-O_Fleet_Groups_Distance.pickle`); its first value equals `Ref.km.BY` of the group in every model.

## Known-limitation candidates

- Guatemala `GUA_ENERGY`, Vehicle Techs, `TRAUTHG` and `TRAUTPHG`: "Relative to TRAUTELE" while `TRAUTELE` is itself "Relative to TRAUTDSL"; the compiler multiplies by the raw ratio, so both compile to 1.33 US$ per vehicle (0.0694 M US$ per Gvkm).
- Costa Rica `CR_ENERGY`, Vehicle Techs: CapitalCost rows labelled "US$ / vehicle" hold values that behave like M US$ per Gvkm (cell x distance / 1000 gives a plausible price), so the compiler divides by distance twice and compiled capital costs are 12 to 59 times too low.
- Costa Rica `CR_ENERGY`, Vehicle Techs: hybrid taxi CapitalCost cells repeat the previous year by formula from 2023; rail cells divide a constant by 0.7315286784, a factor with no stated meaning.
- Costa Rica `CR_AFOLU` Secondary Techs: rice, other vegetables and other grains share one CapitalCost of 3,507.5; the unit columns of CR_AFOLU and CR_WASTE are empty.
- Dominican Republic `RD_ENERGY` (and its RD_AFOLU copy), Vehicle Techs: `TRYLFNGS` is "Relative to TRYLFDSL" but its cell holds a price (17,466.62), so it compiles to 33,898,064 M US$ per Gvkm in 2030.
- Dominican Republic `RD_ENERGY`, Vehicle Techs: `TRBPUELE` FixedCost falls from 53.6 to 0.96 M US$ per Gvkm by 2050.
- Dominican Republic `RD_AFOLU`: wastewater rows carry the unit "No se si aplica" or none; `GA_*` rows carry "MUSD/Mton converted to MUSD/MHa" with no conversion factor; `AG_SGC` CapitalCost 0.3735 is a token value; `IMPSGC` is priced as sugar, not cane.
- Dominican Republic `RD_ENERGY` (and its copy in RD_AFOLU), Fixed Horizon Parameters: OperationalLife 1 year for `TRAUT*`, `TRMOT*`, `TRTAX*`; Costa Rica `CR_ENERGY`: OperationalLife 1 year for `TRNMIC*`.
- `A2_Extra_Inputs/A-Xtra_Battery_Replacement.xlsx` in every vehicle model: read by the compiler and never used; its technology codes do not match most model codes.
- JAM_TRANSPORT aviation and maritime groups and Costa Rica rail carry a distance of 1 km per vehicle; their capital cost rows are zero today.
- HON_WASTE `B1_Scenario_Config.xlsx` waste externalities: about 1000 times smaller than in the other waste models and with the opposite sign for `FERT_ORG` and `RM`.
- Land co-benefit penalties have sign +1000 in HON_AFOLU and -1000 in RD_AFOLU and JAM_AFOLU.
- GUA_AFOLU and ECU_USCUSS: no output fuel has two producers, so the brief's choice rule finds no choice; land technologies compete through activity limits and penalties (GUA_AFOLU incomes) instead, which the rule does not see.
- RD_AFOLU and HON_AFOLU hold full copies of their energy model, with costs that can diverge from the energy model over time.
- Guatemala `GUA_ENERGY`, Vehicle Techs: `TRMOTELE` price (1,814.88) is below the gasoline motorcycle (2,820.16); heavy-freight `Ref.km.BY` equals the bus distance (50,400) with no source.

## Costs left for Luis (rows of class total_only, by model)

Non-zero `total_only` rows (see `cost_inventory.csv`, column `class`): CR_ENERGY 2, CR_AFOLU 26, CR_WASTE 20, RD_AFOLU 99, RD_WASTE 6, ECU_AGR 121, ECU_USCUSS 544, ECU_IPPU 2, ECU_WASTE 17, GUA_ENERGY 5, GUA_AFOLU 37, GUA_WASTE 10, HON_ENERGY 1, HON_AFOLU 53, HON_IPPU 2, HON_WASTE 10, JAM_AFOLU 12, JAM_TRANSPORT 6, JAM_WASTE 11. Non-zero `inactive` rows are listed there too.

## Left unchecked

(Added during Phase 2 and 3.)

## Incidents

(None so far.)
