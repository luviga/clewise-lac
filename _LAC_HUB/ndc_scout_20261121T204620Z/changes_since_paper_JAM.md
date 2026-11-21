# Jamaica: what changed since the paper design (draft)

Model state 481a7c0, read-only. Model numbers come from `model_levers_JAM.csv` and the Stage 3 results; document numbers come from `targets_JAM.csv`. Source ids refer to `parts/sources_JAM.csv`.

## NDC target year and type against the model design

- **Current documents.** NDC 3.0 (JAM-01, September 2025) has single-year targets for 2030 and 2035 against a 2012 base year, with BAU equivalents. Unconditionally, energy and cement emissions fall 16.3 percent below 2012 in 2030 and 16.9 percent in 2035 (19.55 and 25.9 percent below BAU). The energy sector alone is to emit 5.8 Mt in 2030 and 5.7 Mt in 2035 (p.21). Forestry is reported both inside and outside the headline.
- **Model design.** NDCNEW carries measures to 2035 and then holds them, which fits the NDC horizon. The paper's stylised NDCNEW sets a 75 percent renewable share in 2035. Its road electrification and demand cuts have no counterpart in NDC 3.0, which quantifies only renewable share, losses and cement.
- **Emissions.** On the energy-wide label `CO2e_sources`, NDCNEW emits 5.11 Mt in 2030 and 4.19 Mt in 2035, below the NDC energy levels (ratios 0.88 and 0.73). Against the model BAU the cut is 14.2 percent in 2030 and 33.1 percent in 2035; the NDC figures are 19.55 and 25.9 percent, but they include cement.

## Long-term strategy

The LT-LEDS (JAM-02) sets economy-wide emissions 73 percent below 2020 by 2050 and indicative net zero by 2060 (p.13). Its milestone tables cover electricity, transport, buildings, industry, forestry and agriculture for 2025 to 2050 (p.14, p.15). LTSNEW reaches 99 percent renewable generation in 2050 and cuts energy emissions 59 percent from 2021 to 2050. The power and transport labels fall 97.5 and 67 percent, close to the strategy's sector figures of 98 and 66 percent (p.51, p.58).

## Five largest disagreements (from `alignment_JAM.csv`)

1. **Renewable share path.** NDC 3.0 and IRP-2 set 50 percent in 2030 and 63 percent in 2035 (JAM-01 p.14, JAM-07 p.77). The model reaches 39.1 percent in 2030 and 75.0 percent in 2035 in both policy scenarios: 11 points short in 2030, 12 points over in 2035. The solved path comes from the Stage 2 controller curve (`stage2_apply_v2.py` lines 61 to 75), which interpolates from 2026 to 75 percent in 2035; `B1_Scenario_Config.xlsx` does not reach it.
2. **Grid losses.** The NDC cuts losses to 17.7 percent (2030) and 16.45 percent (2035) of generation; the LTS goes to 8 percent by 2050. The model holds distribution losses at 21.3 percent (ELE_DIST input 1.27) in every scenario and year, with no lever active.
3. **Road fuel efficiency.** The LTS improves fleet efficiency 15 percent by 2030 and cuts truck fuel 40 percent by 2050 (p.14, p.15). NDCNEW and LTSNEW reset the road emission factors to their raw values from 2025 (SmartGrid rows 15 to 18), while BAU improves them by 4.8 percent in 2030 and 23 percent in 2050. The policy scenarios are less efficient than BAU, and the road emission label `CO2e_DETRN` is higher in the policy scenarios than in BAU in 2025.
4. **Heavy fuel oil and fossil phase-out.** The LTS phases out HFO capacity by 2035 and fossil generation by 2040. LTSNEW keeps 162 MW of fuel oil plant and 1.66 PJ of its generation in 2035, and 17 percent fossil generation in 2040. The compiled B1 inputs already set fuel oil to 0 from 2027 in all scenarios. Stage 3 replaces them with controller values that keep 3.45 PJ in 2030, so solved and compiled inputs disagree.
5. **Buildings and cement.** The LTS cuts LPG use to 10 percent of 2020 by 2050 and replaces wood, kerosene and charcoal stoves by 2035. In LTSNEW, LPG in 2050 is 121 percent of 2021 and the traditional fuels fall only 5 percent below BAU in 2035. The NDC cement measures (40 kt in 2035) and the LTS clinker ratios (70 percent by 2030) have no counterpart: cement process emissions are the same in all scenarios.

Other points:
- **Capacity matches IRP-2 well.** The NDCNEW and LTSNEW investment floors (Electrical rows 86 to 89) carry the IRP-2 build: wind 303 MW in 2030 against 300 MW, hydro +34 MW, storage 540 MW by 2040 against 493 MW. Solar is 470 MW in 2030 against 597 MW.
- **Transport electrification.** The LTS sets 12 percent of private and 16 percent of public vehicles electric in 2030 and 67 percent of the passenger fleet in 2050. The transport model gives each group 10 percent of activity in 2030 and 90 percent in 2050 (LTSNEW); NDC 3.0 states no figure.
- **Solved results and compiled inputs.** Solved plant generation breaks the compiled B1 limits in 134 to 142 technology-years per scenario (2025 to 2050, 0.5 percent tolerance). It stays inside the Stage 2 controller band in every technology-year. Compiled NDCNEW lower limits imply 75 percent renewable already in 2030, against a solved 39 percent. See `parts/notes_JAM.md`.

Proposals (`parts/proposals_JAM.csv`): 14 of class A, 3 of class B and 1 of class C, plus 5 levers where the documents are silent.
