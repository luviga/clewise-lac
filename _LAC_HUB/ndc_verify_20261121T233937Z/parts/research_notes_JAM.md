# Research notes, Jamaica (step D)

Accessed 2026-11-22. Eight new sources: one external report, one external web page, six CLG pages (lead). Analyses file: `analyses_JAM.csv`, 54 rows.

## The analyses

- **JAM-21, World Bank and Vivid Economics (June 2020), external.** Prepared for the Ministry of Economic Growth and Job Creation to inform the updated NDC. LEAP energy model plus a bespoke land use model (p.14). Scenarios: Baseline (commitments after 2005 left out, p.19), Unconditional NDC and Conditional NDC. It prints the 25.4 and 28.5 percent cuts below BAU in 2030 (p.8) that the updated NDC adopts (JAM-03 p.3, p.5, p.12); JAM-03 p.10 describes the same LEAP baseline. Annex 1 of the LTS (JAM-02 p.188 onward) presents the Vivid Economics modelling approach, and JAM-02 p.13 and p.24 say the LTS mitigation estimates rest on the Vivid Economics and World Bank long-term strategy recommendations (2021).
- **JAM-22, Climate Analytics project page, external.** Climate Analytics supported the Climate Change Division and the PIOJ in drafting the LTS (January to November 2023), funded by IKI and the 2050 Pathways Platform. It cites the World Bank and Vivid Economics result that emissions could grow 50 percent from 2020 to 2050 without action (the same figure is in JAM-02 p.23).
- **JAM-23 to JAM-28, jam-lts Read the Docs site, lead (CLG authorship).** The contributors page lists Luis Victor-Gallardo, Jairo Quiros-Tortos and four others; the GitHub source is `clg-admin/JAM-LTS`. It is a cost-benefit analysis of the LTS made after the strategy was written: OSeMOSYS sector models, Robust Decision Making over 100 futures, a GIZ tool for adaptation and the iSDG model for macroeconomics (JAM-23). Scenarios: Reference or BAU (the 2018 IRP for power; the IDB Strategy Framework for Electric Mobility for transport) and LTS. Results are marked preliminary: 15.3 billion USD of benefits by 2050 (JAM-24), 8.3 billion USD net benefit in transport (JAM-27), at least 0.4 billion USD in industry energy use and a 0.05 billion USD net cost for the clinker measure (JAM-28). The NDC 3.0 says the Cost Benefit Analysis and Investment Plan for the LTS were completed (JAM-01 p.22) and names no author. This fits the CLG work but does not prove it.

## What could not be obtained

- The UNFCCC case study page that the brief cites as naming CLG, the University of the West Indies and CIRED (https://unfccc.int/about-us/regional-collaboration-centres/rcc-events/building-a-long-term-vision-for-climate-resilience-in-jamaica): curl got an 851-byte Incapsula bot-check page, and WebFetch got an empty page. Neither was passed, so the claim is still unconfirmed. In the JAM-02 text that was searched, CLG and CIRED do not appear, and UWI appears only for M&E capacity (p.177) and references (p.186).
- The Vivid Economics and World Bank 2021 reports "Jamaica's long-term climate change strategy recommendations" and "Developing Jamaica's long-term strategy" (JAM-02 Box 1 p.24, references p.186). Searches found no public copy. They are the direct basis of the LTS numbers.
- RMI 2021, Costing and financing option analysis for the updated NDC (JAM-02 p.24): no copy found in one search.
- The MEGJC NDC Implementation Plan (August 2021, https://megjc.gov.jm/wp-content/uploads/2022/08/210824-Implementation-Plan-Report-Final-with-acknowledgment-added.pdf): Windows curl stopped because the site certificate has expired (SEC_E_CERT_EXPIRED). The check was not bypassed.
- The World Bank Sectoral Review (October 2019, the companion of JAM-21) was located (bitstream 648d436d-10b8-51d6-8514-e1f0c66c1973) but not registered. It is qualitative and was superseded by JAM-21.
- Jamaica BTR1 and NID: still pending (see `pending_D_JAM.csv`).

## Judgement calls

- JAM-21 Table 2 (p.23) is headed TWh, but its values (527 in 2018, 1,611 in 2030) can only be GWh. The rows keep the unit as printed, `TWh as printed`. They are not converted.
- JAM-21 prints the absolute 2030 cut as a range, 1.8 to 2.0 MtCO2e. The lower end is assigned to the unconditional scenario and the upper end to the conditional one. The 2 and 11 percent transport cuts and the 42 and 44 percent electricity cuts are split the same way, following the order of the sentence.
- The 2015 NDC figures that JAM-21 reports (BAU 14.5, NDC 13.4 and 13.0 MtCO2e in 2030, p.13) are labelled `Original NDC (2015)`. They sit on a different baseline from the study's own (8.2 MtCO2e in 2030, p.19).
- jam-lts pages carry no date and mark their results as preliminary. The JAM-28 industry results page says the clinker ratio reaches 70 percent by 2030, while the industry scenarios page of the same site says 70 percent by 2050. Both readings are noted. The scenarios page was not registered.
- The battery share of 22 percent (JAM-25) is given the year 2038 from the bullet above it.

## Scenarios against the models

The jam-lts LTS scenario is close in kind to LTSNEW: a fully renewable power system by 2050 (aligned with the 2018 IRP until 2038), 540 MW of batteries by 2038 and 67 percent electric private and public fleets in 2050. Its BAU follows the 2018 IRP (JAM-08), and the IRP 2022 update (JAM-07) is not used. JAM-21's Unconditional and Conditional NDC scenarios belong to the updated NDC of 2020 (JAM-03), not to NDC 3.0. The model's NDCNEW uses a 0.75 renewable share in 2035 and 2050 (hub 11). No analysis found prints a renewable share of generation for NDC 3.0.

## What a deeper study would need

The 2021 Vivid Economics and World Bank LTS recommendations with their LEAP scenario tables, because they are the numbers behind JAM-02. The jam-lts model outputs from `clg-admin/JAM-LTS` (SelectedResults-type CSV files), so that the preliminary benefit figures can be traced to years and discount rates. A copy of the UNFCCC case study taken by a person in a browser. Confirmation from the Climate Change Division of who did the LTS Cost Benefit Analysis named in JAM-01 p.22. The JPS or OUR generation data, to check the 2018 IRP renewable path that both BAU definitions take as given.
