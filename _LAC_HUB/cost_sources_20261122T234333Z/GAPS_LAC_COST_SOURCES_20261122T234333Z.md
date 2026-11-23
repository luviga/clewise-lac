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
9. Shared method. To keep the six countries consistent, every country uses one family for vehicle price trajectories and maintenance (NREL ATB 2022, scenario Mid), and where no national vehicle price exists, the Dominican national electric mobility plan anchors buses and heavy trucks with ATB Class 8 powertrain ratios; national data is used first wherever it was found (Costa Rica bus prices, Jamaica bus contract and car prices, Dominican plan prices).
10. Current model values carry no currency year and are compared with sourced real 2024 USD values as they are.
11. Values averaged over several years (FAOSTAT 2019 to 2023) carry the year range as `source_currency_year` and one CPI factor per year in `cpi_factor`; gate 5 checks each factor against `cpi_u.csv`.
12. Source values that are interpolated or computed from a downloaded file (ATB prices between published years, price ratios, multi-budget means) were confirmed in gate 3 by recomputing them from the file (`scripts/p3_gate3_derived.py`); values printed in a PDF table were confirmed by reading (listed in that script).
13. The research agents could not write their country report text to the job folder (the harness refuses report files from them); each returned the text, and it is merged into the REPORT sections 2.1 to 2.6 with light edits.
14. The self-check scripts in the country folders contain the search patterns for machine paths (for example `/c/clw`); they are patterns, not paths, and stay as written.
15. Rows labelled ASSUMPTION keep the current value where no source contradicts it and give a range; some ASSUMPTIONs (Ecuador, crop and livestock rows) use FAOSTAT value of production per ha as a stand-in for total cost and cite it in the derivation.

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
- Honduras `HON_AFOLU`: `AG_CAF` VariableCost (4,318.8) equals FAOSTAT producer price times yield, a gross output value rather than a cost; `AG_MAI` VariableCost (1,782.8 US$ per ha) is above the FAOSTAT gross output value (about 997); `AG_FRI` and `IMPFRI` VariableCost hold the same number (725.9) in different units; import technology names are wrong (`IMPFRI`, `IMPCAF`, `IMPMEL`, `IMPLEG` named "Import Sugarcane", `IMPRIC` and `IMPMAI` named "Import Banana").
- Honduras `HON_ENERGY`: `Techs_Buses_Tur` distance equals the car distance (7,500 km); freight FixedCost (464.79 and 236.83 M US$ per Gvkm) is 2.5 to 4 times the ATB maintenance value.
- Jamaica `JAM_WASTE`: `AERO_PTAR` and `SEPT_SYST` VariableCost carry the unit label "No se si aplica".
- Jamaica `JAM_TRANSPORT`: `TRAUTHG` ratio 1.02 to `TRAUTELE` compiles to 57,135 US$ against 43,532 sourced (the ratio stays within 25 percent, so confirmed).
- Jamaica `JAM_AFOLU`: `AG_CER` and `AG_COF` fixed plus variable cost total only 14 and 23 US$ per ha; crop costs are 12 to 106 times below the Ministry's 2022 operating costs with no common factor.
- UN Comtrade: Jamaica's 2021 motorcycle imports (HS 871120) show an implausible unit value of 447 US$ CIF; Guatemala and Honduras do not report vehicle imports to Comtrade, so their unit counts are partner estimates.
- Ecuador `ECU_AGR`: every cost cell in scope holds the placeholder 1; livestock `GA_OVE`, `GA_CBR`, `GA_POR`, `GA_AVE` (and `GA_PAT`, `GA_PAV`, `GA_PON`) carry an OutputActivityRatio of 0.0107 head per ha, so these herds can only be met by imports; the 2021 activity lower limits of the import technologies equal the export demands (`IMPCER` 1.4903, `IMPPAL` 0.0479, `IMPCOF` 0.0091, `IMPSUG` 0.0391, `IMPMAI` 0.0568); pasture `LU_PAS` and `GA_PAT` use 59.5 Mha in 2021 (57.1 by `GA_PAT`), more than Ecuador's land area of about 25.6 Mha; the import cost unit "MUS$ / Mha" does not match the activity (Mt or million head).

## Costs left for Luis (rows of class total_only, by model)

Non-zero `total_only` rows (see `cost_inventory.csv`, column `class`): CR_ENERGY 2, CR_AFOLU 26, CR_WASTE 20, RD_AFOLU 99, RD_WASTE 6, ECU_AGR 121, ECU_USCUSS 544, ECU_IPPU 2, ECU_WASTE 17, GUA_ENERGY 5, GUA_AFOLU 37, GUA_WASTE 10, HON_ENERGY 1, HON_AFOLU 53, HON_IPPU 2, HON_WASTE 10, JAM_AFOLU 12, JAM_TRANSPORT 6, JAM_WASTE 11. Non-zero `inactive` rows are listed there too.

## Left unchecked

- Vehicle prices from national tax or customs valuation tables in Costa Rica, Guatemala and Honduras (online queries or bot checks; listed as manual). Light-duty prices there come from ATB United States prices.
- Distances per vehicle other than buses and minibuses in Costa Rica (ASSUMPTIONs at current values), heavy-freight distance in Guatemala and Jamaica (ASSUMPTIONs).
- Jamaica: Jamaica Customs Agency, STATIN, Island Traffic Authority and Coffee Industry Regulation Division were not searched within the time.
- Ecuador: no national crop budget could be downloaded for coffee, sugarcane, soy, pulses, other cereals, tubers, fruit, vegetables or dairy.
- The origin of `TRAUTDSL` 11,525 and `TRAUTGSL` 10,504.4963 (REPORT 1.5).
- The waste externality penalties and the IDB waste cost studies (manual).
- Energy-copy rows in RD_AFOLU and HON_AFOLU (not sourced by design) and every `total_only` and `inactive` row.

## Incidents

- No restart. The job ran once from setup to the pull request.
- Bot checks and blocks: IDB publications (scripts and browser), UNEP wedocs, Guatemala SAT (Cloudflare), Dominican ONE (Cloudflare 403), Honduras strategy draft (403), Jamaica Ministry of Agriculture alternate host (503; the main host worked), Costa Rica Hacienda (query only). UN Comtrade rate-limited some requests (HTTP 429); those files are in downloads and are not cited.
- Git Bash curl crashed on some Dominican government sites; Windows curl worked.
- The first inventory flagged 1,233 rows as holding formulas because it read the `Tech.ID` column; the flag was restricted to value cells and Phase 1 was rerun (only `has_formula` changed).
