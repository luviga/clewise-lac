# Honduras: what changed since the paper design (draft)

Model state 481a7c0, read-only. Model numbers come from `model_levers_HON.csv` and the Stage 3 results; document numbers come from `targets_HON.csv`. Source ids refer to `parts/sources_HON.csv`.

## NDC target year and type against the model design

- **Current documents.** NDC 3.0 (HON-01) runs from 2021 to 2035 and sets a single-year, economy-wide target for 2035. Net emissions, LULUCF included, are to be 12,847.2 Gg CO2e below BAU, 19.6 percent, with 8,564.8 Gg (17 percent) in 2030 (p.22, p.23). The whole target is conditional on climate finance. Agriculture provides more of the cut (6,801.5 Gg in 2035) than energy (3,778.6 Gg) (p.25).
- **Model design.** NDCNEW carries measures to 2035 and then holds them, which matches the NDC horizon. It does not follow the NDC 3.0 measures: it is larger in electric vehicles, smaller in renewables in 2030, and has no hybrids.
- **Emissions.** On the energy-wide label `CO2e_sources`, NDCNEW is 7.6 percent below the model BAU in 2030 and 17.4 percent in 2035. In absolute terms that is 964 and 2,482 kt.
- **BAU.** The NDC energy BAU is a declining linear projection: 9,161 Gg in 2030 and 8,963 Gg in 2035 (p.24). The model BAU is 12,722 and 14,251 kt, ratios 1.39 and 1.59. The 2021 NDC energy BAU (12,142 kt in 2030, HON-03 p.33) was close to the model BAU (ratio 1.05).

## Long-term strategy

None is submitted. NDC 3.0 calls the LTS (ENDRCH) a strategy in consolidation that was used only as guidance (HON-01 p.14, p.15); no document is published. LTSNEW's 99 percent renewable share and 90 percent electric road transport in 2050, and its 60 percent cut against the model BAU, have no document behind them.

## Five largest disagreements (from `alignment_HON.csv`)

1. **Size of the energy cut.** NDC 3.0 assigns energy 2,519.1 Gg in 2030 and 3,778.6 Gg in 2035. NDCNEW delivers 964 kt (ratio 0.38) and 2,482 kt (ratio 0.66), and LTSNEW 2,935 kt in 2035. Against its own BAU the NDC energy cut is 27.5 percent in 2030; the model cut is 7.6 percent.
2. **Power sector path.** The PIEG 2026-2035 (HON-08) cuts power CO2 by 49 percent from 2025 to 2030 and reaches a 76 percent renewable share. NDCNEW power CO2 rises 3.0 percent over the same years (opposite direction), and its renewable share is 64.8 percent in 2030. That is below the NDC 3.0 floor of 70 percent (ratio 0.93, inside the 10 percent band). The solved share comes from the Stage 1 default curve (`stage1_share_analyzer_v16.py` lines 97 to 99, no Honduras override), not from `B1_Scenario_Config.xlsx`.
3. **Hybrids.** NDC 3.0 wants 20 percent of light vehicles to be gasoline hybrids and 15 percent of freight vehicles diesel hybrids by 2035 (p.27). NDCNEW has no hybrid cars, against 1.0 percent in BAU. The cars are capped at 2 percent and have no floor (Tech_Adoption row 154). Light-freight hybrids equal BAU at 3.3 percent and heavy-truck hybrids are 0.
4. **Electric vehicles.** NDC 3.0 asks for 3 percent of the fleet by 2030 and 7.5 percent by 2035. NDCNEW makes 10 and 20 percent of the output of every road group electric (ratios 3.3 and 2.7), and LTSNEW makes it 30 percent in 2035.
5. **Biofuels.** NDC 3.0 asks for 5 percent of transport final energy by 2030. The model blends 5 percent ethanol into gasoline only, which is about 2.3 percent of transport energy (ratio 0.46). The biodiesel list in the B1 script is empty (line 3714).

Other points:
- **Gas.** The PIEG adds a 250 MW gas combined cycle in 2029. NDCNEW builds gas capacity only from 2033 (263 MW in 2035), and no scenario ever runs it.
- **Matching values.** The 1,343 MW of fossil retirements in the PIEG match the model (about 1,238 MW). The model also meets the 2035 renewable floor (75 percent against 70) and the PIEG demand projection (ratios 1.04 and 1.06).
- **Solved results and compiled inputs.** The solved plant generation follows the Stage 2 controller exactly, not the compiled limits in `B1_Output_Params`: 306 NDCNEW technology-years lie outside them. For example, NDCNEW fuel oil in 2030 is solved at 16.40 PJ, against a compiled value of 11.53 PJ.
- **LPG exports.** The policy scenarios carry higher LPG export demand than BAU, which `CO2e_sources` counts. See `parts/notes_HON.md`.

Proposals (`parts/proposals_HON.csv`): 8 of class A, 1 of class B and 2 of class C, plus 5 levers where the documents are silent.
