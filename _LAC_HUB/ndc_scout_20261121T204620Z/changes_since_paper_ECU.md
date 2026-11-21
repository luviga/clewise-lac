# Ecuador: what changed since the paper design (draft)

Model state 481a7c0, read-only. Model numbers come from `model_levers_ECU.csv` and `alignment_ECU.csv`; document numbers come from `targets_ECU.csv`. Source ids refer to `parts/sources_ECU.csv`.

## NDC target year and type against the model design

- **Current documents.** The second NDC (ECU-01, February 2025) has a single-year, economy-wide target for 2035. The reduction is 7 percent below the trend scenario (base year 2010), about 8,800 kt CO2eq, unconditional, with 8 percent more (about 10,600 kt) if support comes (p.55, p.56). The implementation period is 2026 to 2035. The NDC has no sector numbers; its energy content is three lines of action (renewables, efficiency, sustainable mobility, p.57).
- **Model design.** NDCNEW carries measures to 2035 and then holds them, which fits the NDC horizon. NDCNEW cuts energy combustion emissions (label CO2e_sources) by 12.7 percent against the model BAU in 2035: above the 7 percent unconditional target (ratio 1.82), below 15 percent with the conditional part (ratio 0.85). The model has no emission limits and covers energy and transport only. The hub uses the single label CO2e_sources (fuel combustion counted at the DIST_* technologies); it leaves out fugitive and refinery process emissions, and it does not carry the known unintended EmissionActivityRatio differences of the power plants.
- **Solved results and inputs disagree.** The solved results follow the stage-3 control shares (renewable share 0.800 in NDCNEW 2035, 0.990 in LTSNEW 2050). They do not follow the compiled activity limits in `B1_Output_Params`. Those floors add up to 255.7 PJ in NDCNEW 2035, against 153.3 PJ of solved generation; most plant types are solved at 40 to 70 percent of their floor. Several solved values also exceed their compiled upper limits (details in `parts/notes_ECU.md`).

## Long-term strategy

No long-term strategy is on the UNFCCC portal. The national long-term plan is the PLANMICC 2024-2070 (ECU-03), which the NDC calls its long-term strategy. Its CC 2070 scenario cuts emissions by about 70 percent against the trend in 2070 and by about 50 percent against 2018 (p.96). It has no net-zero year. For electricity it keeps a share of thermal generation: hydro about 64 percent plus non-conventional renewables about 24 percent in 2035, and 54 plus 35 percent in 2050 (p.104). LTSNEW reaches 99 percent renewable in 2050 and nearly phases out thermal plants.

## Five largest disagreements (from `alignment_ECU.csv`)

1. **Hydro expansion.** The Plan Maestro de Electricidad adds 4,034 MW of hydro from 2023 to 2032 (ECU-07 p.159), and the PLANMICC has about 10,000 MW of hydro in 2035 (ECU-03 p.104). The model adds 144 MW of hydro from 2025 to 2035 and has 6,341 MW in 2035 (ratios 0.036 and 0.63). Status: same direction, different size.
2. **Solar and wind in 2050.** The PLANMICC has about 3,800 MW of non-conventional renewables and a 35 percent share in 2050 (p.104). LTSNEW has 21,104 MW of solar and wind (ratio 5.55) and a 53.3 percent share (ratio 1.52), with 1 percent non-renewable generation against the thermal share the plan keeps.
3. **Road transport energy.** The PLANMICC saves 2.8 percent of transport energy against the trend in 2035 (p.106). NDCNEW cuts road transport energy by 29.0 percent against the model BAU in 2035 (ratio 10.3), mainly gasoline (151.2 to 102.5 PJ).
4. **Energy-sector emission levels.** The PLANMICC energy phase targets are 39,200 Gg CO2eq in 2035 and 35,800 Gg in 2050 (p.102). The model combustion label CO2e_sources has 32,765 kt in NDCNEW 2035 (ratio 0.84), 43,664 kt in NDCNEW 2050 (1.22) and 30,409 kt in LTSNEW 2050 (0.85); it leaves out fugitive and refinery process emissions, which the plan's energy sector includes. NDCNEW rises again after 2035 because its measures are held, while the plan keeps cutting.
5. **Electrification and efficiency of end uses.** The PLANMICC raises the electricity share to about 66 percent in residential use and 64 percent in industry by 2050 (p.105). In the model these shares stay at 38.3 and 44.6 percent, equal to BAU, because the policy scenarios scale each fuel down and do not switch fuels. Non-transport efficiency is 5.0 percent against the 8.4 percent target for 2035 (ratio 0.60).

Other points:
- Matches: the hydro share of generation in 2035 (60.8 percent against 64 percent, ratio 0.95).
- In documents, not in the model: vehicle targets (hybrids, electric light freight, public transport passenger-km, ECU-03 p.106, p.107), ethanol blending (ECU-08 p.65), distribution losses of 8.3 percent by 2035 (ECU-08 p.67; model 12.2 percent, constant) and green hydrogen (ECU-09 p.6).

Proposals (`parts/proposals_ECU.csv`): 7 of class A, 5 of class B and 2 of class C, plus 2 levers where the documents are silent.
