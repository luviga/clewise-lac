# Notes for GAPS: Costa Rica (CR)

## Judgement calls and reasons

- **Which scenario sets the status.** Each alignment row gets one status. It is judged on NDCNEW for NDC and BTR targets and on LTSNEW for LTS targets. Both model values and both ratios are always given.
- **Headline target read as conditional.** CR-01 p.32 and p.34 say the unconditional actions alone give about 23 percent and do not reach the 11380 Gg cap. Only the full conditional plus unconditional portfolio does.
- **Fleet shares against output shares.** Document targets are shares of the vehicle fleet. The model quantity is the electric share of each transport group's output (activity), from model_levers_CR "electric share of transport group". The two are compared directly, which is a proxy.
- **Bus passenger demand.** Compared with the public passenger demand DEMTRNPASPUB as a change against 2025. That demand also covers microbus, taxi and rail.
- **Passenger train.** The NDC 3.0 statement "52 km electric, 14.6 km diesel" was turned into a route-length share of 0.78 (derived, not printed). This was compared with the electric share of rail output.
- **New-building savings.** The 260 and 655 GWh per year were compared with the cut in commercial plus residential electricity demand against BAU (1 PJ = 277.78 GWh). The document does not name the energy carrier.
- **Industrial boilers.** The share of boilers converted from bunker was compared with the percent cut of industrial fuel oil demand against BAU. This is a proxy.
- **Cement kiln fuel substitution.** Status is "same direction, different size" with no ratio. Converting tonnes to PJ needs a heating value the document does not give.
- **Black carbon.** The 20 percent cut against 2021 was turned into a model-unit target using the model's own 2021 value. BC_TRN covers all transport (the targets cover public transport and freight). BC_DE was read as all end-use demand, wider than industry.
- **LTS energy target "not compared".** The 1.5 C energy value of 2.64 Mt CO2e in 2050 is an energy target. The model has no single energy total and the hub rule forbids summing labels, so the three LTSNEW labels are listed in the note instead.
- **Units of LTS Table 4.** Read as Mt CO2e from the Figure 8 axis on the same page (CR-02 p.34) and the text on p.19. The table prints no unit; p.34 text once writes "Gg", which is inconsistent.
- **NDC 3.0 Figure 4 (p.32).** Read as an image. The years of the labelled points (2024, 2025, 2030, 2035) were read from their x positions.
- **Derived non-renewable share row.** Added to show that 0.900 renewable "matches" 0.95 within 10 percent while the fossil share is double the ceiling.
- **Dates in sources_CR.csv.**
  - CR-01 (2025-11-14) and CR-04 (2020-12-29) come from the Climate Policy Radar record metadata, fetched with curl. CR-01 itself is dated October 2025.
  - The LTS UNFCCC portal date of 12 December 2019 comes from the brief's lead and search results. The portal pages returned an empty or bot page, so sources_CR.csv holds "2019" only.
  - BTR1's submission date (31 December 2024 per a UNDP page in search results) was not confirmed, so sources_CR.csv holds "2024".
- **NDC 3.0 file.** The CDN copy (cdn.climatepolicyradar.org) has the same SHA-256 as the UNFCCC file (57606c72...). The UNFCCC URL is recorded.
- **First NDC.** The UNFCCC Spanish original of the INDC returned a bot-check page. The English text was taken from a third-party copy on v-20.org (CR-08), and is kept because it is the only fetchable full text.
- **Proposals for LTSNEW to 2035.** They follow NDC 3.0, per the hub decision that LTS equals NDC through 2035. Where the 2019 LTS states a different value, both values are named in the note:
  - light vehicles 30 percent;
  - public transport 30 percent;
  - 100 percent renewable by 2030;
  - 20 percent freight LPG by 2030.
- **Ethanol blend proposal class B.** The blend structure exists (BLEND_GSL with E1_ETA), but no scenario-specific blend lever appears in B1_Scenario_Config.xlsx. Blend_Shares_0.pickle was not opened.
- **Distributed PV proposal class A.** PWRSPVDTR and PP_SPV_DG exist in the compiled inputs. The hub should confirm they are the same plant.

## Documents not fetched

- ICE Generation Expansion Plan 2022-2040. It is cited by NDC 3.0 (p.36, p.46). Three searches found no file (see parts/sources_pending_CR.csv).
- The archived ICE PEG 2020-2035 mirror (LAC_sources_archive, cost_src_cr_20261110T025401Z/plants; original URL in the cost_src_cr register, CRC-012: vvalner.com SGCR006-536.pdf) is an older edition and is not the one cited. It was not reused.
- The 2024-2040 edition reported in the press was not searched (scope).
- The other sector plans named in NDC 3.0's bibliography were not fetched. The Plan Nacional de Transporte Electrico 2018-2030 appears in the bibliography but is not cited for a quantified target in the contribution text.

## Ambiguous targets and how they were read

- **CR-T058 (FOLU-1, CR-01 p.68 and p.69).** The text gives a forest-sector minimum net emission "below 76000 GgCO2e" (2027) and "76938 Gg CO2e" (2035). That is about six times national gross emissions, so it is likely a unit or sign error. Recorded as printed and not compared.
- **CR-T019 (EN-4).** "Light transport fleet" was read as cars and SUVs; whether motorcycles are included is not stated. The motorcycle EV share proposal is "documents silent".
- **CR-T098 (BTR1 p.90).** BTR1 attributes "at least 25 percent of the total fleet electric by 2035" to the Decarbonization Plan, but the Plan says 30 percent of light vehicles (CR-02 p.46). Recorded as printed and not compared.
- **Budget period.** CR-01 p.147 mentions an "emission budget 2021-2030" while the headline (p.33, p.138) is 2025-2035. The headline was used.
- **LTS freight goal.** CR-02 p.50 gives "20 percent reduction compared to 2018" for 2026 and 2030 only as an example ("for example"). It was not entered as a target; the 2050 vision value (p.49) was.
- **INDC target trajectory.** CR-08 p.3 Image 1 is footnoted as a linear extrapolation, not a modelled projection. It was entered in projections with that note.

## Known-limitation candidates

1. **Fossil generation floors from 2023, all scenarios.**
   - Where: B1_Scenario_Config.xlsx, Electrical, BAU R5 (PWRFOI) and R7 (PWRDSL), described as "Stage 5 v7: BAU fossil=NDCNEW absolute". The same values are in the NDCNEW and LTSNEW rows.
   - Values: lower limits in PJ.

     | Plant | 2023 | 2024 | 2025 |
     |---|---|---|---|
     | PWRFOI | 1.845 | 3.2008 | 3.3692 |
     | PWRDSL | 0.3504 | 1.5763 | 1.6593 |

   - Effect: solved renewable share falls from 0.9998 (2021) to 0.902 (2024) and 0.894 (2025 onward). CO2e_PWR rises from 0.118 Mt (2021) to 2.84 Mt (2025). BTR1 reports 99.98 percent renewable in 2021 (CR-06 p.96).
   - What it is: this is what holds BAU and NDCNEW near 0.89 to 0.90; whether 2023 to 2024 thermal output reflects actual drought years was not checked.
2. **LTSNEW solved results do not agree with LTSNEW compiled inputs at 481a7c0.**
   - LTSNEW lower limits in 2035: PWRDSL 2.1871 PJ and PWRFOI 4.4409 PJ (model_levers_CR input_difference).
   - Solved LTSNEW generation in 2035: 0.2247 and 0.4561 PJ.
   - The 2030 and 2040 values disagree in the same way; NDCNEW agrees. The stage 3 results may predate the inputs; the hub should check this before using LTSNEW solved values.
3. **Passenger rail electric share collapses in 2050.**
   - Where: B1_Scenario_Config.xlsx, Tech_Adoption, R224 (NDCNEW) and R270 (LTSNEW), TRNPASRAIELE v_2050 = 0.
   - Effect: the solved electric share of passenger rail is 0.012 in 2050 in both scenarios, against 0.989 in 2030 to 2035. The NDCNEW measure is therefore not held after 2035.
4. **PWRSUG.**
   - TotalAnnualMaxCapacity is 0 in BAU and 99999 in the policy scenarios.
   - LTSNEW shows 0.440291 GW installed in 2050 with no generation.
   - C1 counts PWRSUG as non-renewable; if it is bagasse, it would be renewable.
5. **Sector models have no NDCNEW or LTSNEW scenario.** CostaRica/CR_AFOLU, CR_IPPU and CR_WASTE B1_Output_Params hold only BAU, DCC, NDCcond and NDCincond. The economy-wide NDC cap cannot be assessed against NDCNEW.
6. **Duplicate hydro rows.** Electrical has two PWRHYDROR lower-limit rows per scenario: R52 and R55 for NDCNEW, R61 and R64 for LTSNEW. Their 2021 to 2024 values differ slightly (20.742 against 20.3911 PJ in 2021).
7. **Energy labels against the inventory.**
   - Model 2021: CO2e_TRN 5.896, CO2e_PWR 0.118, CO2e_DE 1.646 Mt (labels; the hub rule forbids summing them).
   - Inventory 2021: energy sector 8075.2 Gg CO2e (CR-06 p.64).
   - Not compared here.

## Left unchecked

- NDC 3.0 adaptation chapter (pp.87 to 129): scanned by keyword for energy, transport, MW, GWh and fuel terms, not read line by line. Only hydro-related adaptation goals turned up, with no mitigation quantity.
- LTS (CR-02) sections 6 and 7 (pp.71 to 92) and the annex action plan (pp.93 to 113): scanned for numbers. The quantified items found repeat the axis goals, or are study results such as the PIMUS estimates on p.79, which are not targets.
- BTR1: the inventory chapter totals and the NDC 2020 tracking chapter (pp.75 to 135) were read for targets; the adaptation, finance and gender chapters were not read. A text search found no emission projections in BTR1 (only a gender-annex heading "Proyecciones" on p.380). Whether BTR1 formally uses a flexibility for projections was not checked.
- NID (CR-07): only the summary was read (2021 totals on p.29). It has no targets or projections.
- CR-03 (Spanish LTS): registered and cached, not compared value by value with CR-02.
- Blend_Shares_0.pickle and the sector folders' scenario values: not opened.
- The CR stage 3 renewable shares for 2024 and 2027 come from scripts/CR/query_stage3_b.py. They are not in model_levers_CR, so the hub may re-run that script.

## Incidents

- The climate-laws.org record URL in the brief returned HTTP 404. The Climate Policy Radar app page for the same record worked and gave the CDN link.
- UNFCCC document pages (unfccc.int/documents/204474 and /645177) returned empty bot pages to WebFetch. Direct file URLs under unfccc.int/sites/default/files downloaded normally.
- One empty shell heredoc was invoked by mistake while listing alignment rows. It ran an interactive Python with no input, wrote no file and changed nothing.
- Three temporary files (the CDN copy of NDC 3.0 used for the SHA-256 comparison, and two HTML pages) were written to /tmp, outside the job folder. They were deleted before finishing.
- Text caching of the image-heavy PDFs (LTS, BTR1) with pdfplumber took about 40 minutes.
