# Costa Rica: what a deeper study would still need

**Where the evidence stands.** The NDC in force is NDC 3.0 (CR-01, November 2025); the long-term strategy is the National Decarbonization Plan 2018-2050 (CR-02, CR-03). Of 102 values checked, 74 reached 3 of 3 and 28 reached 2 of 3, all for want of a second place; there are no conflicts. The power target is 95 percent renewable national generation from 2027, held to 2035, conditional on finance (contribution EN-10, CR-01 p.46); the model has 0.897 in NDCNEW 2030 and 0.900 in 2035, and 0.937 and 0.990 in LTSNEW. The ICE generation plan the NDC relies on (CR-22, PEG 2022-2040) was fetched in this job: its Tabla 15.4 (p.202) gives 17 GWh of fuel oil out of 13,814 GWh in 2030. NDC 3.0 says it was built on the CLEW-CR-3.0 model (p.34, p.147) and the CLG repository `ndc_cr` holds models with scenarios BAU, NDCcond and NDCincond, so the NDC and the CLG model are not independent.

**What is missing.**
1. A three-check reading of the PEG 2022-2040 values (CR-22 was found in step D and is not yet in `verification_CR.csv`), so that the plan the NDC cites can give NDC rows.
2. The CLEW-CR-3.0 scenario outputs behind NDC 3.0 (DCC publication, or the CLG repository with the government's agreement), to compare NDCcond and NDCincond with NDCNEW year by year.
3. A model energy emissions total: the Costa Rica model has three CO2e labels (power, transport, demand) and no single energy label, so the 2.64 Mt energy target of the 1.5 C scenario in 2050 (CR-T077) cannot be compared without summing labels.
4. Vehicle stock and distance data: 14 of the NDC rows are fleet shares (public transport, buses, private, light and heavy freight), which the model's output shares cannot be compared with.
5. A fix of the gasoline blend in the model: `BLEND_GSL` takes 1.0 of pure gasoline and 1.0 of ethanol per unit of blend, so the E10 and E15 targets (CR-T020, CR-T021) have no model counterpart.
6. The distributed generation targets (250 and 300 MW, CR-T042, CR-T043): the model has no distributed solar capacity in any scenario.
7. The RAND and IDB cost-benefit result database (CR-23) for yearly sector paths of the NDP, not only the 2050 points.
