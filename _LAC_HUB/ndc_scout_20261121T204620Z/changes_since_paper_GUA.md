# Guatemala: what changed since the paper design (draft)

Model state 481a7c0, read-only. Model numbers come from `model_levers_GUA.csv` and the Stage 3 results; document numbers come from `targets_GUA.csv`. Source ids refer to `parts/sources_GUA.csv`.

## NDC target year and type against the model design

- **Current documents.** NDC 3.0 (GUA-01) runs from 2026 to 2035 and has a single-year, economy-wide target. Net emissions in 2035 are to be 23.7 percent below BAU, or 57,763.7 kt against 75,738.0 kt CO2eq (p.28, p.131). It has no 2030 national target, only sector milestones. The target is net of LULUCF, and forests supply 88 percent of the cut.
- **Model design.** NDCNEW carries measures to 2035 and then holds them. That matches the NDC horizon. The paper's stylised NDCNEW (75 percent renewable, 10 to 30 percent electric road transport) does not follow the NDC 3.0 measures, which are smaller in transport and larger in the renewable share.
- **Emissions.** On the energy-wide label `CO2e_sources`, NDCNEW is 19.7 percent below the model BAU in 2035. In absolute terms that is 8,479 kt, against an NDC energy and transport reduction of 1,184.9 kt (ratio 7.2).
- **BAU.** The NDC energy BAU for 2035 is 28,505.1 kt (p.29). The model BAU is 43,097 kt, ratio 1.51.

## Long-term strategy

The ENDBE (GUA-04, 2018) is the long-term strategy; the BTR1 names it so (GUA-05 p.260). Its 43 options would cut projected emissions from 203 to 83 Mt CO2e in 2050, 59 percent below BAU, economy-wide and without a power or transport share (p.58). LTSNEW cuts energy emissions by 57.7 percent against the model BAU in 2050 (ratio 0.98), but only through a 99 percent renewable share and 90 percent electric road transport, which no document states. An ENDBE update and a PANCC to 2050 are in preparation and not yet published (GUA-01 p.22, p.78).

## Five largest disagreements (from `alignment_GUA.csv`)

1. **Electric vehicles.** NDC 3.0 adds 10,000 electric vehicles to 2035, on a 2025 base of 4,451 (p.47, p.107). Against a fleet of 5.3 million, that is at most 0.27 percent. NDCNEW makes 20 percent of the output of every road group electric in 2035 (ratio 73), and LTSNEW makes it 30 percent.
2. **Size of the energy cut.** The NDC energy and transport reduction is 1,184.9 kt in 2035, against 8,479 kt in NDCNEW. The cumulative figures for 2026 to 2035 are 7,211.6 kt against 40,632 kt (ratio 5.6).
3. **Renewable share.** NDC 3.0 sets at least 80 percent renewable generation in 2035 (p.40). The model holds 75 percent from 2035 (ratio 0.94, inside the 10 percent band but below a stated floor). The superseded 2030 targets of 80 percent (GUA-02, GUA-03) compare with 65.8 percent in 2030. The solved share comes from the Stage 1 target curve (`stage1_share_analyzer_v16.py` line 98), not from `B1_Scenario_Config.xlsx`.
4. **Renewable capacity.** The NDC sets at least 1,000 MW of new renewables between 2025 and 2035. NDCNEW adds 4,104 MW and LTSNEW 5,241 MW. The model BAU alone adds 1,514 MW.
5. **Measures with no model counterpart.** The model has no Aerometro cable car: E6AERO demand exists only for the old NDP scenario. Nor does it represent electricity access for 47,000 households. On hybrids, NDC 3.0 adds 20,000 vehicles; in NDCNEW hybrids stay at the BAU level, and LTSNEW cuts them to about 0.22 model units.

Other points:
- **E10 matches.** The model applies a 10 percent ethanol blend to the gasoline emission factors from 2026, at 5 percent in 2025 (B1 script lines 3616 to 3618).
- **Transmetro.** The NDC electrifies 25 percent of the Transmetro diesel fleet; the model electrifies 20 percent of all public buses in 2035.
- **Solved results and compiled inputs.** The solved plant generation does not match the compiled activity limits in `B1_Output_Params` in any scenario. It does match the Stage 2 controller exactly, because Stage 3 replaces the plant limits from 2025. For example, NDCNEW coal in 2030 is solved at 17.22 PJ, against a compiled range of 12.60 to 13.86 PJ. See `parts/notes_GUA.md`.

Proposals (`parts/proposals_GUA.csv`): 6 of class A, 2 of class B and 2 of class C, plus 6 levers where the documents are silent.
