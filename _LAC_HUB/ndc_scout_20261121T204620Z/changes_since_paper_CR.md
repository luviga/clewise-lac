# Costa Rica: changes since the paper design (draft D1)

## NDC: target year and type against the model design

The model design runs NDC measures to 2035 and holds them after that. NDC 3.0 (CR-01, submitted November 2025) matches that horizon: its contributions have milestones in 2027, 2030 and 2035.

The headline target is two absolute net limits on the whole economy (CR-01 p.33, p.138):

- at most 11380 Gg CO2e in 2030;
- at most 132700 Gg CO2e summed over 2025-2035.

The NDC says the 2030 cap is about 53 percent below a no-measures scenario, and that the unconditional actions alone give about 23 percent (p.34). It also prints its own trajectories (p.32, read as image), so the cap is in practice conditional:

| Scenario | 2030 | 2035 |
|---|---|---|
| No NDC | | 18946 Gg |
| Unconditional only | | 13877.7 Gg |
| Full portfolio | 11308.1 Gg | 10034 Gg |

The models hold no emission cap of any kind. The cap covers all sectors including land use, while CR_ENERGY covers energy only. The sector folders CR_AFOLU, CR_IPPU and CR_WASTE hold only BAU, DCC, NDCcond and NDCincond scenarios, with no NDCNEW or LTSNEW. The model therefore expresses the NDC only through energy and transport levers.

## LTS: existence and headline goal

The long-term strategy is the National Decarbonization Plan 2018-2050 (CR-02), dated 12 December 2019 on the UNFCCC portal. Its goal is net-zero emissions by 2050. Its 1.5 C pathway in Table 4 (p.34) puts 2050 emissions at:

| Sector | 2050 (Mt CO2e) |
|---|---|
| Energy | 2.64 |
| IPPU | 0.39 |
| Agriculture | 1.64 |
| Waste | 0.83 |
| Forest | -5.50 |

No newer long-term strategy has been published. The Plan is older than NDC 3.0, so the two disagree in places:

- **Renewable generation:** the LTS says 100 percent by 2030 (p.52); NDC 3.0 says 95 percent held to 2035 (p.46).
- **Light vehicles electric in 2035:** the LTS says 30 percent (p.46); NDC 3.0 says 20 percent (p.40).
- **Public transport zero-emission in 2035:** the LTS says 30 percent (p.41); NDC 3.0 says 10 percent (p.39).

The model's NDCNEW 2035 transport values follow the LTS numbers, not NDC 3.0.

## Five largest disagreements (from alignment_CR.csv)

1. **Heavy freight electrification, 2035.** NDCNEW has 0.300 of heavy freight output electric. NDC 3.0 states 5 percent of the heavy freight fleet (ratio 6.0). Light freight is 0.300 against 15 percent (ratio 2.0). Both NDC targets are conditional.
2. **Zero-emission public transport.** For buses in NDCNEW:

   | Year | NDCNEW (bus output electric) | NDC 3.0 | Ratio |
   |---|---|---|---|
   | 2030 | 0.100 | 3.5 percent of the bus fleet | 2.86 |
   | 2035 | 0.299 | 10 percent of the public transport fleet | 3.0 |

   The 2035 model value matches the LTS 30 percent.
3. **Bus passenger demand.** The NDC asks for +10 percent in 2030 and +20 percent in 2035 against 2025 (unconditional). NDCNEW public passenger demand grows only 1.35 and 2.98 percent (ratios 0.135 and 0.149); BAU grows 1.28 and 2.57 percent.
4. **Black carbon, opposite direction.** The NDC cuts black carbon from public transport, freight and industry by 20 percent against 2021 by 2030. In NDCNEW, transport black carbon (BC_TRN) rises 2.2 percent from 2021 to 2030 and end-use black carbon (BC_DE) rises 32 percent.
5. **Fossil generation.** NDCNEW keeps the BAU fossil floors (PWRDSL 2.18 PJ, PWRFOI 4.42 PJ in 2035), so 10.0 percent of 2035 generation is fossil. NDC 3.0 allows at most 5 percent (95 percent renewable from 2027) and thermal at the minimum operable. The renewable share itself (0.900 against 0.95) is within the 10 percent band. Model generation is 99.98 percent renewable in 2021 (BTR1 reports the same for 2021) but drops to 0.894 from 2025 in every scenario.

Also absent from the model: distributed renewable self-generation of 250 MW (2030) and 300 MW (2035), the E10 and E15 ethanol blends, natural gas for 10 percent of freight vehicles, and biomethane and sustainable aviation fuel.

Proposed changes are in parts/proposals_CR.csv: 20 class A, 8 class B, 0 class C, and 7 levers where the documents are silent.
