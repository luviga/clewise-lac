# Dominican Republic: what changed since the paper design (draft)

Model state 481a7c0, read-only. Model numbers come from `model_levers_DR.csv` and document numbers from `targets_DR.csv`. Source ids refer to `parts/sources_DR.csv`.

## NDC target year and type against the model design

- **Current documents.** NDC 3.0 (DR-01) sets a two-step, economy-wide target against a projected baseline (BAU, base year 2022): minus 28 percent in 2030 and minus 32 percent in 2035 (p.14, p.62). The implementation period is 2026 to 2035, and the NDC is to be updated in 2030 (p.133 to p.134). Gases are CO2, CH4, N2O and HFC. Only the 2030 step has a conditional split, of 8.5 points unconditional and 19.5 conditional.
- **Model design.** NDCNEW carries measures to 2035 and then holds them. This fits the NDC's 2035 horizon. The NDC's quantified energy measures, however, mostly end in 2030: new gas and renewable capacity by 2030, and distribution losses by 2029. Only the reactor and the Santo Domingo monorail have 2035 dates.
- **Target type.** The NDC target is relative to BAU and economy-wide. The model has no emission limits; its scenarios are built from generation shares, transport shares and demand. On the energy-wide label `CO2e_sources`, NDCNEW is 22.7 percent below the model BAU in 2030 and 49.9 percent below it in 2035. The energy part of the NDC 3.0 portfolio (7,477.22 kt in 2030) matches the model's 2030 energy reduction of 7,755 kt (ratio 1.04).
- **BAU check.** The BTR1 projects energy emissions without measures at 38,200 kt CO2eq in 2035 (DR-04 p.173). The model BAU `CO2e_sources` is 38,916 kt in 2035, a ratio of 1.02.

## Long-term strategy

There is no long-term strategy on the UNFCCC portal. NDC 3.0 names a low-emission long-term strategy, but no document has been found. The only long-term goal in the documents is carbon neutrality by 2050, stated as an aspiration in NDC 2020 (DR-02 p.26) and as a long-term objective in BTR1 (DR-04 p.111). The National Development Strategy 2030 (DR-06) is the national long-term plan the NDC cites; it targets 2.8 t CO2 per capita by 2030. LTSNEW (99 percent renewable generation and 90 percent electric road transport in 2050) is therefore supported in direction only. In 2050 its energy emissions are 6,893 kt, not zero.

## Five largest disagreements (from `alignment_DR.csv`)

1. **New gas combined cycle capacity.** The NDC adds 1,429 MW by 2030 (DR-01 p.148). The model adds 0 MW of new gas in NDCNEW (PPCCTNGSDSL capacity 0) and 17 MW in LTSNEW. Status: in documents, not in the model.
2. **New renewable capacity 2025 to 2030.** The NDC adds 1,529 MW: 1,267 MW solar including 170 MW of storage, 250 MW wind and 12 MW hydro (p.149). The model adds 4,437 MW (ratio 2.90), and wind alone grows by 1,306 MW against 250 MW (ratio 5.2). The NDC figures are measures, not caps. Status: same direction, different size.
3. **2035 emission cut.** The NDC target is minus 32 percent economy-wide. The model cuts energy emissions by 49.9 percent in NDCNEW and 51.6 percent in LTSNEW (ratio 1.56 and 1.61). For 2030 the model is below the target: 22.7 percent against 28 percent (ratio 0.81).
4. **Renewable share of generation in 2030.** The Ministry of Energy and Mines target, as reported in the BTR1, is 30 percent (DR-04 p.174). The model has 42.1 percent (ratio 1.40), rising to 75 percent from 2035, a level no document states.
5. **Measures with no model counterpart.** A small modular reactor of up to 300 MW by 2035 (p.151), two monorails (111,642 t CO2eq per year, p.156) and a cable car (11,343 t per year, p.157). The model has no nuclear plant type, and its mode-shift levers for rail and cable car are 0.

Other points:
- Distribution losses match: the NDC saves 1,005,400 MWh per year against about 1,045,000 MWh in the model in 2030 (ratio 1.04).
- The NDC 3.0 states no electric vehicle target. The model's electric shares (10 percent in 2030, then 30 or 90 percent) rest only on the superseded NDC 2020 vehicle counts.

Proposals (`parts/proposals_DR.csv`): 5 of class A, 3 of class B and 1 of class C, plus 7 levers where the documents are silent.
