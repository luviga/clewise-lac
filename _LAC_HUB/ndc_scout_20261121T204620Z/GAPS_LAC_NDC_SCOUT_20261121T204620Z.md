# GAPS LAC_NDC_SCOUT 20261121T204620Z

Part 1 holds the hub's judgement calls, blocks, known-limitation candidates and incidents. Part 2 reproduces the notes of the six country tasks (`parts/notes_<code>.md`), which hold the per-country judgement calls, documents not fetched, ambiguous targets, known-limitation candidates, items left unchecked and incidents.

## Part 1. Hub

### Judgement calls

- **C1 done once by the hub for all six countries.** The brief gives each background task steps A to C. The hub ran C1 itself with one script (`scripts/c1_model_levers.py`) so that the six `model_levers_<code>.csv` files use the same rules. The country tasks did A, B and C2 and read C1.
- **Country tasks also drafted D1 and D2.** The brief puts step D after the pairs. The country tasks had the context to write `changes_since_paper_<code>.md` and draft proposal rows (`parts/proposals_<code>.csv`); the hub checked them and merged the rows into `proposed_scenario_changes.csv` unchanged, apart from the Ecuador correction below.
- **Pairs run strictly.** Pair 2 started only after both pair 1 countries had finished, and pair 3 after both pair 2 countries, even though one slot was free earlier. At most two background tasks ran at any time.
- **File names use country codes** (CR, DR, ECU, GUA, HON, JAM) for every file the brief names with `<country>`.
- **Page convention.** `page` is the physical PDF page, 1-based (`p.N`); the printed page and table name go in `table_or_figure`.
- **C1 tolerances and coverage.** A compiled-input row counts as different when the absolute difference is above 0.00005 and the relative difference above 0.01 percent in any year from 2025. Parameters without a year (for example OperationalLife) are compared as one value. Values are given for 2025, 2030, 2035, 2040 and 2050 (the brief asks for 2030, 2035 and 2050; 2025 and 2040 were added because the solved part needs them).
- **C1 renewable plant types:** hydro, solar PV, wind, geothermal, biomass and biogas, by name pattern; the list per country is in the `note` of the renewable share row. Costa Rica PWRSUG (sugarcane) is counted as non-renewable because its name does not match; see the Costa Rica notes.
- **C1 final energy per fuel** is the solved production of E4 and E5 fuels grouped by the fuel code at the end of the fuel name, leaving out vehicle-group outputs (E5TR...). It includes exports where a model treats them as E5EXP demand.
- **C1 electric share of transport groups.** Vehicle-based models: output of the ...ELE technologies over the output of the group fuel (E5TR...). Fuel-based models (Ecuador, Jamaica): electricity over all energy delivered to E5TRO* (and E5ALLTRN* in Ecuador).
- **Emission comparisons use one label.** The brief forbids summing labels. Where an energy-wide label exists, `CO2e_sources` (fuel combustion counted at the DIST_* technologies) is used; it leaves out fugitive and process emissions and does not carry the known unintended EmissionActivityRatio differences of power plants. Costa Rica has no such label, so its energy emission target is `not compared` and the three labels are listed in the note. Units of emission labels are assumed Mt CO2e from the size of the emission factors; the stage 3 workbook does not state them.
- **Ecuador correction by the hub.** The Ecuador task built the energy total as CO2e_DE + CO2e_FUG + CO2e_REF + CO2_PP. The hub replaced it in ECU-T001, T002, T003, T020 and T021 with `CO2e_sources` (`scripts/hub_fix_ecu_emissions.py`), and edited the two matching lines of `changes_since_paper_ECU.md` and proposal row 15. Ratios changed from 1.34, 0.62, 0.59, 1.28 and 1.72 to 1.82, 0.85, 0.54, 0.84 and 1.22; all five keep the status "same direction, different size".
- **Status by the 10 percent rule even for floors.** Guatemala (75 against at least 80 percent renewable in 2035), Honduras (64.8 against at least 70 percent in 2030) and Costa Rica (0.900 against 0.95) are labelled `matches` by the rule; their notes say the model is below a stated minimum.
- **Fleet shares against output shares.** Documents set shares of vehicle fleets; the model quantity is the electric share of transport group output. The tasks compared them directly as a proxy and said so in each row.
- **LTSNEW proposals to 2035 follow the NDC**, per Luis's decision of 21 November 2026 that LTS equals NDC through 2035 (brief section 3). Where an LTS states a different value before 2035, the proposal note names both.
- **Headline fields of `cross_country_summary.csv`** were written by the hub from the `published_<code>.md` files (`parts/headlines.csv`). The Costa Rica LTS date (12 December 2019) and the Jamaica LTS submission date (29 August 2025) come from the brief's leads; the portal could not be read to confirm them.
- **Hub edits to country files for the commit rules:** one literal em dash in `scripts/CR/check_files.py` replaced by `chr(0x2014)`; carriage returns removed from `scripts/DR/config_rows.txt` (a text dump of workbook cells).
- **Value check tool widened.** `scripts/hub_check_values.py` first tried up to 4 decimals; widened to 7 after GUA-T047 (0.12933) showed as non-numeric. Reruns of all countries gave the counts in the report.

### Documents not fetched (see `sources_pending.csv`)

Twelve rows: CR ICE generation expansion plan 2022-2040 and the Spanish INDC original; DR LT-LEDS and Plan Energetico Nacional 2025-2038; ECU PNMUS and ENEM; GUA ENDBE portal copy; HON ENDRCH, ENME and the NDC 3.0 technical annex; JAM LTS portal copy and BTR1/NID (not published).

### Blocks

- **UNFCCC long-term strategies portal** (https://unfccc.int/process/the-paris-agreement/long-term-strategies). (1) Scripted fetches by the country tasks: bot-check page. (2) Hub, browser pane: CAPTCHA page (Imperva), not attempted. (3) Hub, archive.org copy: refused by the session permission system, not retried. (4) Web search: no LTS submission found for the Dominican Republic or Ecuador; a 2025 DDP Initiative report describes the Dominican Republic LT-LEDS as awaiting official launch (lead only, not a source).
- **Dominican Republic National Energy Plan:** behind a script-driven file browser; one scripted listing request to the CNE site was refused by the session permission system and not retried (DR notes).

### Known-limitation candidates (hub-confirmed)

1. **Solved results do not follow compiled plant limits.**
   - Where: `_STAGE3_RESULTS/stage3_results.xlsx` against `<model>/B1_Output_Params/<scenario>/TotalTechnologyAnnualActivity{Lower,Upper}Limit.csv` at `481a7c0`.
   - Values: CR LTSNEW 2035 PWRDSL lower 2.1871 PJ, solved 0.2247; PWRFOI lower 4.4409, solved 0.4561 (B1_Scenario_Config.xlsx Electrical row 57 holds the same 2.18708). GUA NDCNEW 2030 PPCOA lower 12.5965 and upper 13.8562, solved 17.2176. JAM PPFOI upper 0 from 2027 in all scenarios, solved 3.4535 in NDCNEW 2030. ECU and HON as reported by their tasks.
   - What it is: Stage 3 replaces plant limits from 2025 with controller values (Stage 1 and Stage 2 share curves), so the compiled inputs are not what was solved; in Costa Rica this holds for LTSNEW only.
2. **Unlisted BAU against policy differences** found in C1 and by the tasks, not in the brief's known list:
   - Ecuador PROCRU EmissionActivityRatio (CO2_REF 0.0038 BAU against 0.0043 policy; CO2e_REF 0.0036 against 0.0039) from 2025 (`model_levers_ECU.csv` rows 8 and 9).
   - Honduras LPG export demand E5EXPLPG: BAU 11.4114 PJ in 2035, NDCNEW 21.4808 PJ (2035) and 39.2474 PJ (2050), from a BAU-only override row (B1_Scenario_Config.xlsx, Efficiency row 92).
   - Jamaica road emission factors T5DSLTRO and T5GSLTRO (label CO2e_DETRN): BAU improves them, the policy scenarios reset them from 2025 (SmartGrid rows 11 to 18).
   - Guatemala and Honduras gasoline emission factors (DIST_GSL on CO2e_sources, T4GSL_* on CO2 and CO2e) differ from 2025 or 2026; read by the tasks as the ethanol blend.
3. **Honduras PPNGS:** capacity 0.262759 GW (2035) and 1.30199 GW (2050) in NDCNEW with no generation rows in any scenario.
4. **Costa Rica fossil floors from 2023 in all scenarios** pull the renewable share from 0.9998 (2021) to 0.894 (2025 on) (Costa Rica notes, item 1).

### Left unchecked by the hub

- Proposal rows: the hub checked the cited workbook rows for a sample (CR Electrical rows 48, 49, 57; DR Electrical row 128), not every row.
- Alignment model values: the hub recomputed a sample per country, not every row.
- Sector models (AFOLU, IPPU, waste): no values read; targets of these sectors are `not compared` or name the folder.

### Incidents

- The hub used one shell heredoc (to patch `scripts/c1_model_levers.py`), against the brief's rule. The patch was small (year handling); the script was rerun and its output checked. All later scripts were written with the file tool.
- The brief's lead record for Honduras NDC 3.0 (`..._21f1`) holds the April 2025 second update; the Costa Rica lead record on climate-laws.org returned HTTP 404 (Climate Policy Radar worked).
- The Costa Rica task wrote three temporary files to /tmp and deleted them; it also invoked one empty heredoc that wrote nothing (Costa Rica notes).

## Part 2. Country task notes

### Notes for GAPS: Costa Rica (CR)

#### Judgement calls and reasons

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

#### Documents not fetched

- ICE Generation Expansion Plan 2022-2040. It is cited by NDC 3.0 (p.36, p.46). Three searches found no file (see parts/sources_pending_CR.csv).
- The archived ICE PEG 2020-2035 mirror (LAC_sources_archive, cost_src_cr_20261110T025401Z/plants; original URL in the cost_src_cr register, CRC-012: vvalner.com SGCR006-536.pdf) is an older edition and is not the one cited. It was not reused.
- The 2024-2040 edition reported in the press was not searched (scope).
- The other sector plans named in NDC 3.0's bibliography were not fetched. The Plan Nacional de Transporte Electrico 2018-2030 appears in the bibliography but is not cited for a quantified target in the contribution text.

#### Ambiguous targets and how they were read

- **CR-T058 (FOLU-1, CR-01 p.68 and p.69).** The text gives a forest-sector minimum net emission "below 76000 GgCO2e" (2027) and "76938 Gg CO2e" (2035). That is about six times national gross emissions, so it is likely a unit or sign error. Recorded as printed and not compared.
- **CR-T019 (EN-4).** "Light transport fleet" was read as cars and SUVs; whether motorcycles are included is not stated. The motorcycle EV share proposal is "documents silent".
- **CR-T098 (BTR1 p.90).** BTR1 attributes "at least 25 percent of the total fleet electric by 2035" to the Decarbonization Plan, but the Plan says 30 percent of light vehicles (CR-02 p.46). Recorded as printed and not compared.
- **Budget period.** CR-01 p.147 mentions an "emission budget 2021-2030" while the headline (p.33, p.138) is 2025-2035. The headline was used.
- **LTS freight goal.** CR-02 p.50 gives "20 percent reduction compared to 2018" for 2026 and 2030 only as an example ("for example"). It was not entered as a target; the 2050 vision value (p.49) was.
- **INDC target trajectory.** CR-08 p.3 Image 1 is footnoted as a linear extrapolation, not a modelled projection. It was entered in projections with that note.

#### Known-limitation candidates

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

#### Left unchecked

- NDC 3.0 adaptation chapter (pp.87 to 129): scanned by keyword for energy, transport, MW, GWh and fuel terms, not read line by line. Only hydro-related adaptation goals turned up, with no mitigation quantity.
- LTS (CR-02) sections 6 and 7 (pp.71 to 92) and the annex action plan (pp.93 to 113): scanned for numbers. The quantified items found repeat the axis goals, or are study results such as the PIMUS estimates on p.79, which are not targets.
- BTR1: the inventory chapter totals and the NDC 2020 tracking chapter (pp.75 to 135) were read for targets; the adaptation, finance and gender chapters were not read. A text search found no emission projections in BTR1 (only a gender-annex heading "Proyecciones" on p.380). Whether BTR1 formally uses a flexibility for projections was not checked.
- NID (CR-07): only the summary was read (2021 totals on p.29). It has no targets or projections.
- CR-03 (Spanish LTS): registered and cached, not compared value by value with CR-02.
- Blend_Shares_0.pickle and the sector folders' scenario values: not opened.
- The CR stage 3 renewable shares for 2024 and 2027 come from scripts/CR/query_stage3_b.py. They are not in model_levers_CR, so the hub may re-run that script.

#### Incidents

- The climate-laws.org record URL in the brief returned HTTP 404. The Climate Policy Radar app page for the same record worked and gave the CDN link.
- UNFCCC document pages (unfccc.int/documents/204474 and /645177) returned empty bot pages to WebFetch. Direct file URLs under unfccc.int/sites/default/files downloaded normally.
- One empty shell heredoc was invoked by mistake while listing alignment rows. It ran an interactive Python with no input, wrote no file and changed nothing.
- Three temporary files (the CDN copy of NDC 3.0 used for the SHA-256 comparison, and two HTML pages) were written to /tmp, outside the job folder. They were deleted before finishing.
- Text caching of the image-heavy PDFs (LTS, BTR1) with pdfplumber took about 40 minutes.

### Notes for GAPS: Dominican Republic (DR)

#### Judgement calls and reasons

- **Long-term strategy.** None was found on the UNFCCC portal. The portal returned an empty page to WebFetch and a bot-check page to curl, and Climate Policy Radar lists no long-term strategy for the country. NDC 3.0 names a low-emission long-term strategy (DR-01 p.120) with no date or link. I recorded it in `sources_pending_DR.csv` as not found and treated it as not submitted. As the "national long-term plan the newest NDC cites", I registered the National Development Strategy 2030 (Law 1-12, DR-06; cited by DR-01 p.14, p.30, p.128), kind `LTS-national-not-submitted`. Its horizon is 2030, not 2050. I chose it because it is the only cited long-term national plan that exists as a document. The 2050 carbon neutrality aspiration is taken from DR-02 p.26 and DR-04 p.111.
- **END 2030 copy.** The Ministry of Finance URL returned a Cloudflare challenge, so I used the ESMAP RISE library copy of the Ministry of Economy edition (DR-06, 94 pages).
- **Sector plans.**
  - The National Energy Plan 2025-2038 is cited for BAU demand and planning assumptions (DR-01 p.36, p.129), not for a stated target. It could not be fetched: the CNE page is a script-driven Dropbox browser, and a scripted listing request was refused by the session permission system and not retried. It is listed as pending.
  - The Organismo Coordinador long-term operation programme is cited only as the data source of the PAM 1 and PAM 2 capacity figures (DR-01 p.148, p.149, "enero 2025-diciembre 2029, publicado en diciembre 2024"). The OC file list from the earlier job has no edition with that span; the nearest are "ENE 2025_DIC 2028" (January 2025) and "ENE 2026_DIC 2030". Since it is a data source and not a plan that sets a target, I did not download it.
  - The transport plans named in the ICTU list (DR-01 p.129: SIT plan 2025, PMUS Gran Santo Domingo) are not tied to a quantified target in the NDC text and were not fetched.
- **Reused files.**
  - DR-04 (BTR1/NC4) is the earlier download `DR_BTR1_CN4_2025.pdf`. Its SHA-256 equals the Climate Policy Radar copy fetched today, whose source URL is the UNFCCC file also cited in DR-01 p.21. The earlier register had no URL for this file.
  - DR-05 (NID) is the earlier download, with the same SHA-256 and URL as register row FR2-D3-DRNID.
- **First NDC.** The archived registry entry is the English unofficial translation of the August 2015 INDC (DR-03, 4 pages). The Spanish original (https://unfccc.int/sites/default/files/NDC/2022-06/INDC-RD%20Agosto%202015%20%28espa%C3%B1ol%29.pdf, from a search result) was not fetched. The translation was enough for its single target.
- **Dates.** DR-01 is titled 2025 but carries the UNFCCC upload date of June 2026 (Climate Policy Radar record 9 June 2026; file folder 2026-06). DR-02 has the Climate Policy Radar date of 29 December 2020; the BTR1 (p.111) says 28 December 2020.
- **Alignment choices.**
  - Emission targets are compared through the energy-wide label `CO2e_sources`. That label is fuel combustion counted at the DIST_* technologies, assumed to be in Mt CO2e (emission factor about 0.074 per PJ of diesel). It is used as a percent change against the model's own BAU, because the model holds no IPPU, AFOLU or waste emissions and its BAU is not the NDC BAU. This label is not affected by the known unintended EmissionActivityRatio differences, which sit on PP technologies and the CO2e_PP label.
  - The capacity targets have base year 2024. The levers file starts in 2025, so the model increase is measured from 2025 to 2030.
  - Distribution loss savings in the model are computed as ELE delivered times (BAU InputActivityRatio minus scenario InputActivityRatio) of ELE_DIST in 2030. This assumes all delivered electricity passes ELE_DIST.
  - The NDC 2020 vehicle-count options (DR-T054, DR-T058) are `not compared`: the levers file holds output shares, not fleets. The taxi share (15 percent of the fleet) is compared with the taxi group's electric share of output.
  - Superseded NDC 2020 capacity options (DR-T046 to DR-T052) are listed in targets but not aligned.
- **Proposals.** NDC 3.0 items are proposed for NDCNEW only. LTSNEW is mentioned in notes, because the hub has decided that LTS equals NDC through 2035 and a later job writes that. The 30 percent renewable share (2030) and the 1,529 MW of new renewable capacity are floors that the model already exceeds; they are proposed as class A, and the hub decides whether NDCNEW should sit on the stated values. No proposals are written for the IPPU, AFOLU and waste sector models; those targets are listed in alignment with their folder.

#### Ambiguous targets and how I read them

- **PAM 2 (DR-01 p.149).** The objective line says +109 percent of renewable capacity and the description says +109.5 percent of 2024 installed renewable capacity; 1,529 MWn is used.
- **LULUCF total (DR-01 p.42).** Table 5 prints the total as "2,010,000" in a kt column, while the PAM rows and the infographic (p.57) give 2,010. I read it as 2,010 kt.
- **2035 split.** The 8.5/19.5 conditional split is printed for 2030 only. The 2035 target (32 percent) is marked "not stated".
- **HFC.** NDC 3.0 aims to cut HFC imports by 5 percent against BAU in 2030 (DR-01 p.162 to p.163), while the BTR1 cites a 35 percent HFC cut by 2030 (DR-04 p.179) with no base. Both are kept.
- **Private cars (DR-02 p.160).** "Up to 240,000" cars is printed next to phases of 100,000 and 120,000 (sum 220,000); 240,000 is kept.
- **Fuel oil to gas conversion (DR-02 p.140).** 951 MWp in the table, 911 MWp summed in the description, and 800 MW in the BTR1 progress table (DR-04 p.154). 951 is kept.
- **Reforestation rate.** 15,000 ha per year (DR-04 p.181, p.164) has no target year printed next to it. The NDC 2020 horizon of 2030 is assumed.
- **Enabling frameworks.** 25 enabling frameworks (DR-01 p.122) has no year; it is read as the end of the NDC period, 2035.
- **NDC 3.0 baseline tables.** In Table 4 (DR-01 p.32 and p.195), CH4 and N2O are in kt of gas and HFC is already in kt CO2eq, even though a GWP of 1950 is printed. The totals only add up that way. Annex 4 Table No.2 (p.191) gives N2O in 2035 as 10.97, while Tables 3 and 4 give 19.83. The projections file uses Table 4.
- **BTR1 Table 3.14 (p.189).** The 2035 total is 57,291.91 kt CO2eq against 57,292.65 in DR-01.
- **Agriculture projection (DR-04 p.182).** The 5,800 kt CO2eq is given without an explicit year; it is read as 2035 because the next sentence (p.183) totals the sector at 2035.

#### Known-limitation candidates

- **New natural gas.** `B1_Scenario_Config.xlsx` sheet Electrical, row 128 (NDCNEW, TotalAnnualMaxCapacity PPCCTNGSDSL) is 0 in every year, and row 127 (PPCCTNGS) is flat at 1.36162 GW before the 1.05 multiplier. NDCNEW therefore cannot build any of the 1,429 MW of new gas combined cycle that the NDC lists for 2030, while BAU adds 153 MW of PPCCTNGS by 2030.
- **Rail and cable car.** `B1_Scenario_Config.xlsx` sheet Mode_Shift, rows 13, 14, 17 and 18 (Techs_Telef, Techs_Trains, both policy scenarios) are 0, and TRANRAILINF capacity is 0. Measures named in both NDCs (monorail, cable car, metro) have no effect in the model.
- **Distribution losses.** The ELE_DIST InputActivityRatio in NDCNEW and LTSNEW falls to 1.0826 in 2030 and then rises again to 1.1005 by 2050 (`model_levers_DR.csv` row 8). Losses grow back after 2030 in the policy scenarios.
- **Battery storage.** It is part of the NDC solar measure (170 MW, DR-01 p.149), but there is no storage technology among the listed levers.

#### Left unchecked

- The IPPU, AFOLU and waste sector models were not read for values. Only technology names were read, to name the folder.
- The adaptation annex (DR-01 Annex 2, physical p.184) is one image page of a 67-page annex that is not included in this PDF.
- The BTR1 was not read in full: chapters 1 and 2 (circumstances, inventory) and chapter 4 onward (adaptation, support) were skimmed through searches. I read the NDC tracking, policies and projections sections (printed p.87 to p.191).
- The NID was searched for projections and mitigation tables; none were found.
- The model's 2024 capacities were not read; 2025 is used as the base for capacity increases.

#### C1 file (`model_levers_DR.csv`)

- No error found in the rows used. Rows whose printed 2030, 2035 and 2050 values are equal across scenarios (for example TRBPUDSL TotalAnnualMaxCapacity 9999) differ only in 2025, as their `first_diff_year_from_2025` and `n_diff_years` columns show.

#### Incidents

- One scripted request to the CNE website's file-browser endpoint was refused by the session permission system. It was not retried, and the document is in the pending list.
- The DDP 2025 report URL (a search lead) returned a "page not found" HTML page, which was deleted. The first attempt at the END 2030 download returned a Cloudflare page, which was also deleted.
- In spot-check preparation, a self-check found that the DR-T009 value (7,477.22) is printed on p.41 and in the p.45 image, not on p.40. The page reference was corrected before round 1.

### Notes for GAPS: Ecuador (ECU)

#### Judgement calls and reasons

- **Long-term strategy.** The UNFCCC long-term strategies portal could not be read by script. WebFetch returned an empty page, and curl returned a 957-byte bot-check page. The Climate Policy Radar geography page lists no long-term strategy for Ecuador. The second NDC calls the PLANMICC 2024-2070 its long-term strategy (ECU-01 p.10, p.33, p.44, p.113). I registered the PLANMICC (ECU-03) as `LTS-national-not-submitted` and read its chapter 6 (scenarios, targets, indicators; physical p.90 to p.147) in full.
- **Current NDC.** ECU-01 was downloaded directly from the UNFCCC file address (February 2025 folder); the NDC registry page itself was not read. The first NDC (ECU-02) was also downloaded from UNFCCC. Both files start with `%PDF`.
- **Conditional target.** ECU-01 p.55 and p.56 say "8% adicional" (about 10,600 kt). The executive summary (p.10) says the conditional target could reach 8 percent. I read it as 8 percent on top of the 7 percent, 15 percent in total, which matches 10,600 kt being additional (8,800 kt is 7 percent). In alignment, 15 percent is used for the conditional comparison.
- **Sector plans (at most five).** Five plans are cited for quantified energy or transport targets. The NDC names the Plan Maestro de Electricidad 2023-2032 and the PLANEE 2016-2035 as sources of the energy target (ECU-01 p.67). The PLANMICC names the PLANEE, the urban mobility policy (PNMUS) and the electromobility strategy as the basis of its energy and transport hypotheses (ECU-03 p.101, Tabla 14), and the green hydrogen roadmap for hydrogen in transport (p.100). PME, PLANEE and the hydrogen roadmap are registered (ECU-07 to ECU-09). PNMUS and the electromobility strategy failed after three attempts each and are in `parts/sources_pending_ECU.csv`. The 2026 PME adjustment (Acuerdo MAE-MAE-2026-0066-AM and annexes) is cited by neither the NDC nor the PLANMICC and would be a sixth plan, so it was not registered. Its copy was removed from `downloads/ECU/`.
- **Reused files.** ECU-05 (NID) is the earlier download with the same SHA-256 and URL as register row FR2-D3-ECUNID. ECU-07 (PME 2023-2032) and ECU-09 (hydrogen roadmap) are earlier downloads; their SHA-256 values equal the rows of `C:\clw_fix\_LAC_HUB\fix_run2_20261120T225823Z\research\d12_lives_sources.csv`, which also gives their URLs (they are not in that job's `sources.csv`). ECU-06 (CN4/BUR2) is the earlier download `ECU_CN4_BUR2_2022.pdf`; its UNFCCC address comes from a search result, and byte identity with that address was not checked.
- **ECU-06 scope.** The CN4/BUR2 is superseded by the BTR1 (ECU-04). Its first NDC chapter (physical p.623 to p.624) repeats the first NDC scenarios that ECU-04 reprints in updated form. It was searched, not read, and no rows come from it.
- **Energy emissions in the model.** Energy-sector total = CO2e_DE + CO2e_FUG + CO2e_REF + CO2_PP, in Mt CO2e (diesel road factor 0.0741 per PJ in `EmissionActivityRatio.csv`). I used CO2_PP instead of CO2e_PP because CO2e_PP carries the known unintended EmissionActivityRatio differences, while CO2_PP is equal across scenarios. CO2e_sources was not used: it counts fuels at the DIST_* technologies and overlaps the other labels. Its BAU value even falls from 2025 to 2030 (33.45 to 32.56).
- **Renewable categories.** For the PLANMICC non-conventional renewable (ERNC) share I counted solar PV, wind, biogas and biomass plant types (p.108 says the indicator also covers biomass). Hydro counts PPHD, PPHDAM*, PPHROR* and PPIHD. The model has no separate SNI; all generation is used.
- **Comparison years.** The PME expansion runs 2023 to 2032. The model increase is taken from 2025 to 2035, the nearest printed years in the levers file.
- **Electricity share of final energy (ECU-T024).** The delivered-fuel rows of the levers file include fuel to power plants and exports. The model value (ELE over all deliveries except CRU and OPE) is indicative only.
- **Proposals.** PLANMICC phase I values are proposed for NDCNEW, because the NDC builds its target on the PLANMICC model and states no sector numbers. The hub decides whether NDCNEW should follow them. LTSNEW follows the hub decision that LTS equals NDC through 2035.

#### Ambiguous targets and how I read them

- **ERNC phase I (ECU-03 p.104, Tabla 15).** The table prints "about 24 percent (about 240 MW)" for 2035, against "about 35 percent (about 3,800 MW)" in 2050 and "about 37 percent (about 8,400 MW)" in 2070. 240 MW cannot give 24 percent of generation, so the MW figure looks like a typing error (perhaps 2,400 MW). The percentage is kept as the target; the 240 MW is only mentioned in the note. The 3,800 MW of 2050 also looks low for a 35 percent share at solar and wind capacity factors.
- **Energy sector efficiency (ECU-03 p.104).** "Save about 8.4 percent, about 6,500 kBEP of national energy consumption" against the trend; footnote 22 says transport is excluded. I compared it with all non-road-transport demand rows of the model.
- **PLANMICC Figure 16 (p.97, read as image).** Its waste labels (2,667; 2,643; 3,255; 4,120 Gg) differ from Figura 36 (2,541; 2,347; 2,785; 3,650 Gg). Both are in `projections_ECU.csv` with a note. The energy labels of Figure 16 add up to Figure 17 (for example 20,245 + 19,039 = 39,284, against 39,200).
- **First NDC conditional target.** The first NDC gives 20.9 percent (ECU-02 p.22); the BTR1 says it was adjusted to 13.5 percent in the implementation plan (ECU-04 p.215). Both are kept.
- **BTR1 projections** use AR2 GWP and IPCC 1996 guidelines (ECU-04 p.231); the second NDC uses AR5 (ECU-01 p.60). They are not comparable with each other or with the 2022 inventory.
- **Quito Metro and Cuenca tram (ECU-02 p.18).** Recorded as 22 km of metro; the 12 km tram is in the note (no sum).

#### Solved results against compiled inputs (asked by the hub)

The solved results at 481a7c0 are not consistent with the compiled policy inputs in `Ecuador/ECU_Energy/B1_Output_Params`.
- **Floors far above solved generation.** NDCNEW `TotalTechnologyAnnualActivityLowerLimit` rows add up to 231.5 PJ in 2030 and 255.7 PJ in 2035, against 138.1 and 153.3 PJ of solved total generation. Per plant type the solved/floor ratio is 0.40 to 0.70 for most types. Examples for NDCNEW 2035: PPFOI floor 22.854 against solved 9.181 PJ; PPHDAMAB 26.947 against 17.800; PPHRORAB 40.140 against 24.709; PPWNDON 53.524 against 12.292; PPRDSL 18.305 against 7.348. LTSNEW 2050 floors add up to 354.7 PJ against 203.7 PJ solved (PPWNDON 182.072 against 50.832).
- **Solved values above compiled caps.** NDCNEW 2030: PPHRORAS solved 6.378 PJ against an upper limit of 2.685; PPHRORPM 11.578 against 9.504; PPRNGS 4.254 against 2.529. NDCNEW 2035: PPPVD 8.676 against 5.785.
- **Shares.** The compiled NDCNEW floors imply a renewable share of 0.750 in 2035, while the solved share is 0.805. `ShareValidation` control shares (0.800 in NDCNEW 2035, 0.990 in LTSNEW 2050) match the solver.
- **Reading.** The solved results seem to come from the stage-3 target shares, not from the activity limits now in `B1_Output_Params`. The floors look scaled by about 1.67. BAU is consistent: its floors (112 PJ) are below solved generation (155 PJ in 2035).
- **Same pattern as Costa Rica.** The hub should check how stage 3 builds and applies these limits before the solved values are used.
- **Tables affected.** All model values in `alignment_ECU.csv` are solved values.

#### Known-limitation candidates

- **Refinery emission factor.** `model_levers_ECU.csv` rows 8 and 9: the PROCRU EmissionActivityRatio is 0.0038 (CO2_REF) and 0.0036 (CO2e_REF) in BAU, against 0.0043 and 0.0039 in NDCNEW and LTSNEW from 2025. This difference is not in the brief's list of known unintended differences. It raises policy-scenario refinery emissions (CO2e_REF in 2035: 1.344 Mt in NDCNEW, 1.245 in BAU) and makes NDCNEW energy emissions in 2025 slightly higher than BAU (44,648 against 44,565 kt).
- **Distribution losses.** The ELE_DIST InputActivityRatio is 1.1393 (12.2 percent losses) and ELE_TRANS is 1.0398, in every scenario. No grid-loss lever exists in `B1_Scenario_Config.xlsx` (SmartGrid and Electrical sheets).
- **No fuel switching in end uses.** Efficiency sheet rows 8 to 33 (LTSNEW) and 63 to 88 (NDCNEW) scale each fuel; the residential electricity share stays at 38.3 percent and the industrial one at 44.6 percent in 2050 in every scenario.
- **Hydro capacity.** Hydro capacity grows only from 6.18 to 6.34 GW between 2025 and 2035 in every scenario, although the PME adds 4,034 MW of hydro by 2032. TotalAnnualMaxCapacity of hydro types is 99 GW (not binding) in the policy scenarios.
- **Geothermal.** PPGEO TotalAnnualMaxCapacity is 0 in BAU and 99 GW in NDCNEW and LTSNEW (Electrical rows 89 and 155), but no geothermal generation is solved.
- **Hydrogen.** E5INDHYD demand is 0 in every scenario (Efficiency rows 21 and 76), although HYD_G_PROD exists.
- **C1 renewable list.** The renewable list in `model_levers_ECU.csv` does not count PPIBIM or PPGEO. Neither has solved generation, so the shares are not affected.

#### Left unchecked

- **Sector models.** The sector models (ECU_AGR, ECU_USCUSS, ECU_IPPU, ECU_WASTE) were not read for values; only technology names were read to name the folder.
- **NDC2 (ECU-01).** Read page by page from the text cache. The adaptation, loss and damage and finance chapters (p.72 to p.118) were read for mitigation numbers only.
- **PLANMICC (ECU-03).**
  - Chapter 6 (p.90 to p.147) was read in full; Tabla 15 (p.104 to p.107) and Figures 16 and 23 were also read as page images.
  - Chapters 1 to 5 and 7 to 8 (diagnosis, process, vision, action plan, finance, gender, MRV) were searched by keyword, and only the pages with hits were read. This deviates from "read in full", for time.
- **BTR1 (ECU-04, 1,119 pages).** Only the NDC tracking and projections part was read (physical p.145 to p.148 contents, p.208 to p.238). The inventory, adaptation and support chapters were not read.
- **NID (ECU-05).** Searched for projections and targets; none found.
- **Sector plans.** PME (ECU-07): only the expansion summary table (p.159) and keyword searches. PLANEE (ECU-08): target tables and summary pages (p.20, p.65, p.67). Hydrogen roadmap (ECU-09): summary page p.6 and keyword searches.
- **NDC2 Figure 6 (p.57).** It plots the trend, unconditional and conditional series without printing values, so no series was copied.

#### Incidents

- The UNFCCC long-term strategies portal returned an empty page to WebFetch and a bot-check page to curl.
- The 2026 PME adjustment annexes were copied and cached as ECU-08 by mistake before the selection of sector plans. The copy and its cache were deleted, and ECU-08 was rebuilt for the PLANEE.
- pypdf printed fontTools warnings during the spot check; the extraction still worked.
- The self-check of values against the cited page text found two rows not matching. One value was a sum of two printed lengths (34 km), now replaced by the printed 22 km. The other was a decimal form (12,307.30), now written with both decimals. After the fixes, all 197 numeric values were found on their pages.

#### Hub corrections (LAC_NDC_SCOUT hub)

- The emission comparisons ECU-T001, ECU-T002, ECU-T003, ECU-T020 and ECU-T021 in `alignment_ECU.csv`, the matching lines of `changes_since_paper_ECU.md` and proposal row 15 were recomputed by the hub from the single label CO2e_sources (`scripts/hub_fix_ecu_emissions.py`), because the brief forbids summing emission labels. The four-label build described above was dropped.

### Notes for GAPS: Guatemala (GUA)

#### Judgement calls and reasons

- **Long-term strategy.** The ENDBE (GUA-04) is registered with kind `LTS`. The BTR1 calls it the country's long-term mitigation strategy (GUA-05 p.260, Tabla 4.6), and the brief's lead says it is on the UNFCCC portal. I could not open the portal to confirm the listing or its date. WebFetch returned an empty page, curl returned an Incapsula bot-check page, and three guessed UNFCCC file names returned 404. The copy used is the FAOLEX file linked from the UNEP LEAP record, whose date of text is 2018. Whether it is byte-identical to the portal file is unknown (`parts/sources_pending_GUA.csv`).
- **Newest NID.** The BTR1 (GUA-05) contains the National Inventory Document (1990 to 2022) as its Section I, so no separate 2024 or 2025 NID was sought. GUA-06 is the older inventory report (1990 to 2018, version 2 of 14 August 2023). It is listed for completeness; no value is cited from it.
- **First NDC.** GUA-03 is the INDC dated 29 September 2015, which the BTR1 counts as the first NDC from 2017 (GUA-05 p.251).
- **NDC 2021 copy.** The UNFCCC NDC folder also holds `Contribucion Nacionalmente Determinada Guatemala.pdf`. Its server sends exactly 62,914,560 bytes with no end-of-file marker, and the first pages show it is the same 2021 update. I deleted it and used the complete 230 MB file from the 2022-06 folder (GUA-02, 94 pages).
- **Sector plans.** Only the Plan Nacional de Energia 2017-2032 (GUA-07) was fetched. The LTS cites it for a quantified energy target (64 percent renewable in 2032, GUA-04 p.24), and the BTR1 lists it (p.264).
  - Not fetched because no quantified energy or transport target is cited from them: the Politica Energetica 2013-2027 and the Politica Nacional de Eficiencia Energetica 2023-2050 (named in GUA-01 p.39, p.41, p.45); the Politica Energetica 2019-2050 and the Plan de Expansion Indicativo del Sistema de Generacion 2020-2050 (BTR1 Tablas 4.13 and 4.16); and the electric mobility law (Decreto 40-2022).
  - NDC 3.0 does not cite a source for its 1,000 MW and 80 percent figures. The documents behind them, MARN 2026a and 2026b and the measure sheets, are "available at MARN" (GUA-01 p.134) and not published.
- **Scope of targets.** Mitigation targets and joint mitigation and adaptation targets are listed. Adaptation-only targets in NDC 3.0 are not listed: health, water, irrigation, coast and reef, roads, information systems. Superseded NDC 2021 and INDC targets are listed and marked superseded.
- **Emission label.** Emission targets are compared through `CO2e_sources`, the DIST_* fuel distribution technologies. I assume Mt CO2e, because the emission factors are 0.0743 per PJ for diesel and 0.0632 per PJ for gasoline. `CO2e` overlaps it: plants, T4 transport and T5 demand techs, about 1 point higher. `Accidents`, `Congestion` and `Health` are not greenhouse gases. No labels were summed.
- **Status rule.** Status is judged on NDCNEW for NDC and sector-plan targets and on LTSNEW for LTS targets; the other ratio is given. The 80 percent renewable floor for 2035 is `matches` by the 10 percent rule (75 against 80, ratio 0.94), but the model is below a stated minimum. The hub may prefer `same direction, different size`.
- **Vehicle targets.** The documents count vehicles; the model holds output shares. For GUA-T016 and GUA-T017 I derived an upper-bound fleet share from the January 2024 fleet of 5.3 million (GUA-01 p.45) and the September 2025 baselines (p.107). The model value is the electric share of car output and the hybrid share of car output respectively.
- **Capacity base year.** The annex gives base year 2025 for the 1,000 MW target, so the model increase is measured from 2025 to 2035.
- **Firewood.** The model value for GUA-T078 is the cut in residential firewood demand. The plan's 2030 figure is derived from Tablas 10 and 11 (GUA-07 p.79, p.80).
- **ENDBE energy and transport.** For GUA-T059, the energy (374 Mt) and transport (80 Mt) cumulative reductions were summed to 454 Mt to match the model's energy-system label. Industry (103 Mt) mixes process and energy emissions and was left out.
- **Proposals.** NDC 3.0 items are proposed for NDCNEW; LTSNEW follows the hub decision that LTS equals NDC through 2035. For the renewable share, the lever that the solver actually sees is the Stage 1 target curve and the Stage 2 controller, not `B1_Scenario_Config.xlsx` (see below). No proposals are written for the AFOLU, IPPU and waste models.

#### Ambiguous targets and how I read them

- **Conditionality of the 23.7 percent target.** The NDC says it will be met with national resources, complemented in forests by results-based payments and cooperation (p.28), and with "national and international resources" (p.132). It never labels the target conditional or unconditional. Recorded as `not stated`.
- **NDC 2021 clean generation.** Cuadro 3 (p.72) says 80 percent of generation from clean energy by 2030. p.77 says renewables are 80 percent of the "energy matrix". ENE-1 counts natural gas as clean (p.71). Read as a generation share that may include gas.
- **NDC 2021 ethanol.** No year is printed for the 10 percent blend (p.77); I read it as 2030. The BTR1 roadmap expected 15 percent by 2030 (p.254); NDC 3.0 keeps E10.
- **Plan Nacional de Energia.** The renewable mix is said to save 10.82 Mt in 2032 (p.70). Yet the whole plan cuts energy emissions from 16.82 to 11.91 Mt, only 4.91 Mt (p.92). Both are listed. The 2016 renewable share is 58 percent in GUA-07 (Grafica 22, p.68) and 54 percent in GUA-04 (p.24).
- **ENDBE stoves.** "100,00 hogares" on p.26 is read as a misprint, either 10,000 or 100,000. The value recorded is the 11 Mt CO2e reduction in 2050.
- **ENDBE p.30 and p.17.** These pages carry text in a broken font. p.30 was read as an image for the options list; the 80 Mt figure is also in the text layer.
- **PRE 10.5 Mt (GUA-05 p.254).** No period is printed. The target year is set to 2025 as the likely end of the ERPA period; this is uncertain.
- **UTC-2 value 0.12933 (GUA-T047).** It has five decimals, so the hub value check, which tries at most four, will report `no_value`. It is printed on GUA-02 p.71. GUA-T012 (five indicators) is printed as the word "cinco", and GUA-T011 has no number.

#### Solved results against compiled inputs (requested check)

- **Against the compiled limits.** The solved plant generation (`stage3_results.xlsx`, TotalTechnologyAnnualActivity) does not respect the compiled activity limits in `GUA_ENERGY/B1_Output_Params` in any scenario. Checked 2025 to 2050 with a tolerance of 0.5 percent: 790 technology-years are outside the compiled range. Examples in PJ:
  - NDCNEW 2030: PPCOA solved 17.218, compiled lower 12.597 and upper 13.856. PPNGS 5.830 against 4.115 to 4.526. PPPVT 6.446 against a lower limit of 13.133. PPWNDON 4.668 against a lower limit of 7.173. PPHDAM 21.317 against an upper limit of 19.867.
  - NDCNEW 2035: PPNGS 4.725 against a lower limit of 7.363. PPCOA 18.224 against an upper limit of 17.330.
  - LTSNEW 2035: PPCOA 21.579 against an upper limit of 19.937. PPPVT 18.104 against a lower limit of 23.414.
  - LTSNEW 2050: PPWNDON 119.254 against an upper limit of 81.858.
  - BAU 2030: PPPVT and PPWNDON solved 0 against lower limits of 3.636 and 1.888.
- **Against the Stage 2 controller.** The solved results match `_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx` (sheet CURRENT_LOWER, Guatemala) exactly: 0 technology-years below the controller lower limit or above lower times 1.05. The reason is that Stage 3 replaces the plant lower and upper limits from 2025 with controller values (`PIPELINE_WORKFLOW.md`, Stage 3). Two consequences follow:
  - The compiled NDCNEW limits imply a 75 percent renewable share already in 2030 (share of lower limits 0.7500), while the solved 2030 share is 0.658.
  - The renewable share lever for the solved runs is `stage1_share_analyzer_v16.py` lines 97 to 110, where Guatemala has no override.
- **For the hub.** Any change written only to `B1_Scenario_Config.xlsx` for plant activity will not reach the solved results unless Stages 0 to 3 are re-run. Unlike Costa Rica, the solved fossil generation here is not below the controller floors.
- **Transport.** Transport limits are not patched by Stage 3, and the solved electric shares match the compiled limits. For example, cars in NDCNEW 2035 are 0.2002 solved against 0.1998 compiled.

#### Known-limitation candidates

- **Model BAU energy emissions are high against the documents.** `CO2e_sources` in BAU is 25.90 Mt in 2025 and 43.10 Mt in 2035 (`model_levers_GUA.csv` line 186). The 2022 energy inventory is 21.32 Mt (GUA-05 p.274), and the NDC 3.0 energy BAU for 2035 is 28.51 Mt (GUA-01 p.29). Model BAU coal generation alone is 22.3 PJ in 2035, at an emission factor of 0.369 per PJ.
- **Policy emissions exceed BAU in 2025.** `CO2e_sources` is 26.78 in NDCNEW and LTSNEW against 25.90 in BAU. The cause is the IMP_ELE lower limit of 0 in the policy scenarios (known unintended difference), which pushes domestic generation up.
- **Fuel oil capacity in LTSNEW 2050.** PPFOI installed capacity is 4.269 GW with 0.335 PJ of generation (line 154), against 0.85 GW in 2040. This looks like a reserve-margin artefact of Stage 3, which tags firm generators.
- **Hybrids.** LTSNEW caps hybrid cars at an activity of about 0.22 (lines 130, 131) against 5.03 in BAU in 2050 (line 88). The LTS scenario has fewer hybrids than BAU.
- **Cable car.** E6AERO demand and T5ELEAERO costs exist only for the NDP scenario (`B1_Scenario_Config.xlsx` sheet Efficiency row 13, SmartGrid rows 4 and 5). NDCNEW and LTSNEW cannot represent the Aerometro.
- **E10 timing.** The blend starts at 5 percent in 2025 in the policy scenarios (B1 script line 3617), one year before the NDC date and before the BTR1's reported start of January 2026.

#### C1 file (`model_levers_GUA.csv`)

- No error found in the rows used. One caution: the `input_difference` rows for plant limits (TotalTechnologyAnnualActivityLower and UpperLimit, PP techs) do not drive the solved results from 2025; the Stage 2 controller does (see above). The `solved` rows are correct against `stage3_results.xlsx`: I recomputed the renewable shares for 2030 and 2035 and the emissions for 2030, 2035 and 2050.

#### Left unchecked

- The AFOLU, IPPU and waste sector models were not read for values. Only their technology names were read, to name the folder.
- BTR1 Section I (inventory chapters) was searched, not read page by page; it holds no projections. BTR1 Section II (NDC tracking, policies) was read in full. GUA-06 was searched for projections; none were found.
- NDC 3.0 was read in full. The annex matrices for the adaptation-only sectors (p.110 to p.130) were skimmed for numbers only.
- ENDBE figures and MAC curves (p.25, p.31, p.36, p.42, p.47, p.51, p.54) were not read as images. The option names in the annex (p.61 to p.66) were checked as images on p.61 only; they carry names, not numbers.
- Plan Nacional de Energia: chapters 8.1 to 8.3 were read; the context chapters (p.1 to p.59) were not.

#### Incidents

- First attempt at the alternative NDC 2021 URL: truncated file (no end-of-file marker), deleted.
- OLADE copy of the ENDBE: HTTP 404 HTML page, not kept.
- UNFCCC LTS portal and an unfccc.int documents page: bot-check or empty page.
- Climate Policy Radar API search: HTTP 404 JSON.
- No request was refused by the session permission system.
- Helper outputs of the solved-versus-input checks were written to the session scratchpad, not to the job folder. Scripts: `scripts/GUA/check_solved_vs_inputs.py` and `scripts/GUA/controller_check.py`.

### Notes for GAPS: Honduras (HON)

#### Judgement calls and reasons

- **Which document is NDC 3.0.** The brief's lead record (`climate-laws.org/document/honduras-nationally-determined-contribution-ndc3-0_21f1`) returned HTTP 404 to WebFetch and curl. Its Climate Policy Radar twin holds the April 2025 second update (HON-02) and a one-page scanned cover letter, which was not kept. The NDC 3.0 itself is the UNFCCC file of January 2026 (HON-01), which is byte-identical to the Climate Policy Radar record `..._bd82`.
- **Long-term strategy.** None is submitted, and none is published. NDC 3.0 says the LTS (ENDRCH) is being consolidated and was consulted only as guidance (HON-01 p.14, p.15). The BTR1 describes the 2024 update work, which used OSeMOSYS for energy, transport and LULUCF, but prints no figures (HON-05 p.563 to p.565). No `LTS-national-not-submitted` source was registered, because the newest NDC cites no published national long-term plan. The CLG endrch-hon site was not used. The pending row records the searches.
- **Older energy plans.** The BTR1 also names the Prospectiva Energetica 2017-2038 (more than 80 percent renewable by 2038) and the Hoja de Ruta 2050 (HON-05 p.524). Neither the newest NDC nor an LTS cites them for a number, so they were not fetched. The Prospectiva figure is listed from the BTR1 (HON-T073).
- **Sector plans.** Only the PIEG 2026-2035 (HON-08) was fetched; NDC 3.0 names it for the 70 percent target (p.26). NDC 3.0 was written when only the September 2025 draft existed. I used the final version approved on 16 September 2026 (document control, HON-08 p.2), which is the current plan. The draft was not compared. The ENME (electric mobility) could not be fetched (pending).
- **Earlier downloads.** The BTR1, NIR 2024 and BUR2 were downloaded again from the UNFCCC addresses on 2026-11-21. All three are byte-identical to the copies in `C:\clw_fix\...\d3_ef`, so their URLs are now proven. The BTR1 URL is the one NDC 3.0 cites (p.69). The draft PIEG 2024-2033 and the approved annex copy named in the leads were not used, because NDC 3.0 cites the 2026-2035 plan.
- **NDC 2021 file.** Every copy (UNFCCC, Climate Policy Radar, FAOLEX) is exactly 31,457,280 bytes, with the same SHA-256 and no `%%EOF` marker. All 68 pages open and the text extracts through p.66; p.67 and p.68 are the back matter. It was used as is.
- **NDC 3.0 arithmetic.** The sector percentages on p.25 are shares of the national net BAU, not of each sector's BAU: 2,519.1 / 50,381.3 = 5.0 percent. The text says the sector values are 'during the implementation period 2021-2030', but they add up to the single-year national target, so they are read as the reduction in the target year. The cumulative reading is given in the alignment note.
- **Emission label.** Every emission comparison uses `CO2e_sources` alone. It is the energy-wide total, since every fossil fuel passes through a DIST_* technology, and is assumed to be in Mt CO2e (diesel 0.0743, LPG 0.0632 per PJ). The other labels cover parts of the same fuel: CO2e and CO2 for T4 transport, CO2e_DE for T5 final use, CO2e_PP for plants. They are never added, and Health is not a greenhouse gas. `CO2e_sources` does not carry firewood CH4 and N2O, which the inventory's energy sector does, and it does count LPG exports (see below).
- **Power-sector comparisons with the PIEG** use CO2_PP over the scenario's own 2025 to 2030 and 2035 path, because the PIEG measures against 2025. Plant emission factors change between BAU and the policy scenarios from 2025 (a known unintended difference), but they are constant within each scenario after 2025.
- **Unlisted emission factor differences.** These are DIST_GSL (0.069543 to 0.0661) and T4GSL_* (CO2 0.0693 to 0.0658) from 2026. They come from the ethanol blend in `B1_Base_Scenarios_Adj_Parallel_Honduras.py` lines 3712 to 3769: 0 in 2025, 4.99 percent in 2030 and 5 percent in 2035, in every scenario except BAU, NDCincond and NDCcond. The biodiesel list `Diesel_Techs` is empty (line 3714), so diesel factors do not change. This lever carries NDC 3.0's 5 percent biofuel target only in part (HON-T024).
- **Vehicle targets.** The documents count vehicles; the model holds output shares by group. Fleet shares were compared directly with output shares, and the note says so.
- **Firewood.** 2012 lies before the model start. The model cut is measured from 2018, and the per-household target was compared with total residential demand.
- **Status rule.** Status is judged on NDCNEW for NDC and plan targets, and the LTSNEW ratio is given too. HON-T018 (70 percent in 2030) is `matches` by the 10 percent rule (ratio 0.93), but the model sits below a stated floor. HON-T094 (retirements) compares a derived gross figure.
- **Proposals.** NDC 3.0 items are proposed for NDCNEW. LTSNEW follows the hub decision that LTS equals NDC through 2035. The PIEG gas item is proposed as class A but marked as an indicative sector plan.

#### Ambiguous targets and how I read them

- **Three national totals in NDC 3.0.** The 2035 reduction is 12,847.2 Gg on p.23. On p.22 a '19.6 percent cumulative 2021-2035' is said to equal 8,564.8 Gg, which is the 2030 value. On p.25 a 'national mitigation target' of 7,268 Gg is printed for 2021-2035. I read 12,847.2 Gg and 19.6 percent as the 2035 single-year target (12,847.2 / 65,616.6 = 19.58 percent). The 7,268 is listed but not compared.
- **17 or 16 percent.** NDC 3.0 says it keeps the second update's '17 percent'. The second update states 16 percent plus 1 percent for LULUCF (HON-02 p.3). Both are listed.
- **Sector split in the second update.** p.3 gives energy 9, agriculture 5, IPPU 1 and waste 1 percent; Cuadro 3 on p.11 swaps agriculture and IPPU. The 2021 update (HON-03 p.30) agrees with p.3.
- **IPPU, waste and LULUCF in 2035.** The 2035 column on p.25 says 'respecto al BAU en 2030' for these three; I read it as 2035.
- **Electrification base year.** The +3 and +5 point targets give no base. 2022 is assumed, the base of the intensity target in the same paragraph.
- **Electricity intensity.** '3.4 kWh/USD' and '4 kWh/USD' are recorded as printed. As intensity reductions they look too large, so the unit or scale may be wrong. Not compared.
- **BTR1 HCFC.** The text says 15 percent of baseline by 2030 (p.525), while Table 3-6 lists an import maximum of 2.5 percent in 2030 (p.552). Both are listed.
- **Removals in the BAU table.** In projections, LULUCF removals printed in parentheses are given as positive magnitudes with the unit 'Gg CO2e (removal)'.
- **Word values.** HON-T075 (total HCFC elimination by 2040) has value 0 for a word, so the hub value check will report it not found. HON-T030 (urban mobility plans) has no number.

#### Solved results against compiled inputs (requested check)

- **Against the compiled limits.** Solved plant generation (`stage3_results.xlsx`, TotalTechnologyAnnualActivity) does not follow the compiled activity limits in `HON_ENERGY/B1_Output_Params`. Checked 2025 to 2050 with a tolerance of 0.5 percent: 169 BAU, 306 NDCNEW and 281 LTSNEW technology-years are outside the compiled range. Examples in PJ:
  - NDCNEW 2030: PPFOI 16.395 solved against a compiled value of 11.531 (lower equals upper); PPCOK 2.984 against 2.061; PPPVT 10.056 against 14.669; PPWNDON 7.218 against 9.421; PPHDAM 7.818 against 6.682.
  - NDCNEW 2035: PPPVT 17.814 against 18.698; PPWNDON 12.787 against 12.010.
  - NDCNEW 2050: PPWNDON 24.572 against 20.229.
  - LTSNEW 2050: PPPVT 59.198 against 54.694.
  - BAU 2030: PPHDAM 7.818 against a lower limit of 9.086; PPPVT 6.998 against an upper limit of 4.859.
- **Against the Stage 2 controller.** The solved results match `_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx` (CURRENT_LOWER, Honduras) exactly: no technology-year is below the controller lower limit or above lower times 1.05. Stage 3 replaces the plant limits from 2025 (`PIPELINE_WORKFLOW.md`, Stage 3). Two consequences follow:
  - The compiled NDCNEW lower limits imply a 75 percent renewable share in 2030, while the controller and solved share is 64.8 percent.
  - The renewable share lever for the solved runs is `stage1_share_analyzer_v16.py` lines 97 to 110, where Honduras has no override. Changes written only to `B1_Scenario_Config.xlsx` Electrical rows 82 to 101 and 162 to 181 will not reach the solved results unless Stages 0 to 3 are re-run.
- **IMP_ELE.** The known unintended difference (BAU 99,999, policy 0) has no effect on the solved results: imports are 0 in every scenario, BAU included.
- **Transport.** Transport limits are not patched by Stage 3. The solved electric shares match the compiled limits; for example, NDCNEW cars in 2035 are solved at 0.1998 against a compiled limit of 0.6175 over 3.0904.

#### Known-limitation candidates

- **LPG export demand differs between BAU and the policy scenarios.** This is not on the brief's list. E5EXPLPG is held at 11.41 PJ from 2025 in BAU, through `B1_Scenario_Config.xlsx` sheet Efficiency row 92, a BAU-only override mislabelled 'Demand Commecial Electricity'. NDCNEW and LTSNEW have no such row and grow to 14.37, 17.57, 21.48 and 39.25 PJ in 2025, 2030, 2035 and 2050 (`model_levers_HON.csv` line 31).
  - DIST_LPG carries the `CO2e_sources` factor 0.063155, so the policy scenarios gain about 0.19 Mt in 2025, 0.39 in 2030, 0.64 in 2035 and 1.76 in 2050.
  - This is why NDCNEW `CO2e_sources` in 2025 (11.188) exceeds BAU (11.062), and why `CO2e_DE` is higher in the policy scenarios than in BAU in every year.
- **Gas plants built but never run.** PPNGS capacity reaches 0.74 GW in BAU, 1.30 GW in NDCNEW and 2.26 GW in LTSNEW by 2050 (line 186), with zero generation in every year. The controller lower limit for PPNGS is 0, so Stage 3 sets its activity upper limit to 0, while the 1.15 reserve margin still builds it as firm capacity.
- **Policy has fewer hybrid cars than BAU.** BAU forces TRAUTHG through a lower limit (1.0 percent of car output in 2035, line 111). NDCNEW and LTSNEW only cap it at 2 percent (Tech_Adoption rows 154 and 184), so the solver builds none.
- **Electrification identical in BAU and policy.** The policy demand cuts are a uniform percentage across fuels, so the electric share of residential, commercial and industrial demand is the same in all three scenarios (24.7 percent in 2022, 30.9 in 2030, 31.8 in 2035).
- **Model BAU energy emissions against the documents.** `CO2e_sources` BAU is 9.76 Mt in 2022, against an inventory energy sector of 10.88 Mt (HON-01 p.11), which includes firewood CH4 and N2O. It is 12.72 and 14.25 Mt in 2030 and 2035, against an NDC 3.0 energy BAU of 9.16 and 8.96 Mt, which comes from a linear projection that declines.
- **Fuel oil in NDCNEW after 2035.** PPFOI generation rises again from 13.93 PJ in 2035 to 22.24 PJ in 2050, with 0.88 GW installed (lines 164, 179). The 75 percent renewable share is held flat, so fossil output grows with demand.
- **Battery storage.** The PIEG plans 215 MW of stand-alone batteries and 685 MW of batteries in hybrid solar and wind plants (Tabla 43, HON-08 p.82). No storage technology has capacity in the Honduras results.

#### C1 file (`model_levers_HON.csv`)

- No error found in the rows used. I recomputed from `stage3_results.xlsx` the renewable shares of 2030 and 2035, the `CO2e_sources`, `CO2e_PP` and `CO2_PP` values of 2025, 2030, 2035 and 2050, and the installed capacity; all equal the file.
- Two cautions:
  - As for Guatemala, the `input_difference` plant limit rows do not drive the solved results from 2025.
  - The electricity import row (line 208) is empty because imports are zero.

#### Left unchecked

- **NDC 3.0** was read in full, every page through the text cache. The pages with little text (p.1, 9, 19, 33, 45, 51, 59, 64, 71, 72) are photographs or section covers. p.66 is the diagram of the monitoring system (caption in the text layer), not viewed as an image. p.25, p.26 and p.68 were also read as images: p.68 is the cover of the ICTU appendix, and no appendix content follows.
- **Second update** (20 pages) and **INDC** (8 pages) were read in full. **NDC 2021 update:** the mitigation chapters (p.9 to p.47) were read in full; adaptation, finance and MRV (p.48 to p.66) were not.
- **BTR1:** chapter 3 (mitigation and NDC tracking, p.494 to p.579) was read in full. The inventory chapters were not read beyond the values that NDC 3.0 quotes from them. Chapters 4 to 6 were not read.
- **BUR2:** the mitigation chapter (p.72 to p.94) was read; p.90 to p.93 (REDD+, carbon markets) were skimmed for numbers. The NIR 2024 (HON-06) was searched for projections and none were found; no value is cited from it.
- **PIEG:** the executive summary, chapter 4.1, the emission factors, the demand projection, chapter 6.3.5 (the selected scenario), 6.3.7 to 6.5 and the conclusions were read. The other scenarios and the cost chapters were not.
- The AFOLU, IPPU and waste models were not read for values; only their technology names were read, to name the folder.

#### Incidents

- The lead record `..._21f1` returned 404 on climate-laws.org.
- The UNFCCC long-term strategies portal returned an Incapsula page to curl and an empty page to WebFetch.
- The IAIP transparency portal returned HTTP 403.
- The Article 6 initial report (www4.unfccc.int Submissions Staging, cited by HON-01 p.22) returned an HTML application page, not a PDF. It was not kept; it is not a required kind.
- One empty shell heredoc was run by mistake while checking the table writer. It did nothing and wrote no file. All scripts were written with the file tool.
- No request was refused by the session permission system.
- Helper outputs of the self-checks went to the session scratchpad, not to the job folder. Scripts: `scripts/HON/model_numbers.py`, `check_solved_vs_inputs.py`, `self_check_HON.py`, `config_index.py`.
- The self-check uses the hub rules: 250 of 252 values were found on the cited page. Not found: HON-T075, whose value 0 stands for a word. No value: HON-T030.

### Notes for GAPS: Jamaica (JAM)

#### Judgement calls and reasons

- **LTS copy and date.** JAM-02 is the Climate Policy Radar copy. Its cover says November 2023, its PDF was created on 18 August 2025 and last modified on 27 August 2025, and NDC 3.0 says the strategy was approved in 2024 (JAM-01 p.3, p.22). The UNFCCC record (documents/649405, submission 29 August 2025 per the brief) returned a 212-byte Incapsula page to curl and an empty page to WebFetch. Whether the copy is byte-identical to the UNFCCC file is unknown (`parts/sources_pending_JAM.csv`). The PDF dates make it very likely to be the submitted version.
- **NDC 3.0 file.** The UNFCCC file `2025-09/Jamaica ICTU Final Report Sep19.pdf` and the Climate Policy Radar NDC 3.0 file are byte-identical (same SHA-256); the UNFCCC address is registered as the URL. The same holds for the 2020 update (UNFCCC NDC/2022-06 file and the Climate Policy Radar copy).
- **No BTR1 found.** Three search routes, the UNFCCC listing (bot-check) and four guessed UNFCCC file names (HTTP 404) gave nothing. NDC 3.0 (September 2025) says the BTR will be prepared (p.18). The TNC (JAM-06, 2018) and BUR1 (JAM-05, inventory 2006-2012) are registered as the newest inventory documents. BUR1 has no date on its cover; it is registered as 2016 from a web-search lead (UNFCCC submission 18 November 2016), which no opened document confirms. The BUR1 and TNC inventory totals for 2006-2012 disagree (BUR1 Table ES1 CO2 2012 14,296 Gg, JAM-05 p.3; TNC Table 2 CO2 2012 7,387 Gg, JAM-06 p.11). No value from either inventory is used in the comparison.
- **Sector plans.** Only IRP-2 (JAM-07) qualifies under the brief: NDC 3.0 lists it as a data source (p.5) and its 63.4 percent for 2035 equals the NDC figure. IRP-1 (JAM-08, superseded) was reused from `LAC_sources_archive` (same SHA-256) because NDC 2.0 cites it and it records the earlier 30 percent target; a fresh download of IRP-2 from gpe.gov.jm had the same SHA-256 as the archive copy. Not fetched, because the LTS and NDC take no number from them: National Energy Policy 2009-2030 (its targets are quoted in JAM-08 p.16 and JAM-04 p.2), Electric Vehicle Policy 2023 (JAM-02 p.150), Strategic Framework for Electric Mobility 2022 (JAM-02 p.57), National Biofuels Policy 2010-2030 (JAM-02 p.93), Energy-from-Waste Policy (p.88). No IRP newer than IRP-2 was found in one search (the archive search log of 10 November 2026 found none either).
- **Scope of targets.** Mitigation and mixed targets are listed, including mangrove and seagrass items that NDC 3.0 says were not evaluated quantitatively. Adaptation-only items of the LTS (tourism, health costs, coastal works) are not listed. LTS figures that are scenario results (98 percent power cut, 60 percent industry cut, transport 0.79 Mt) are listed with a note.
- **Emission label.** Emission targets are compared through `CO2e_sources`, the DIST_* fuel distribution technologies (diesel 0.0742758 per PJ, so Mt CO2e). `CO2e_PP` (plants), `CO2e_DE` (end-use demand techs) and `CO2e_DETRN` (road, maritime, jet) are subsets of it, computed with technology-level factors; `CO2e_CEM` (clinker), `CO2e_LIME`, `CO2e_HFC` and `CO2e_LUBRI` are non-energy. No labels were summed. NDC targets that cover energy plus cement are compared on the energy label only, and rows that need both labels are `not compared`.
- **Base year.** The model starts in 2021. 2021 stands in for 2020 in the LTS comparisons (JAM-T045, JAM-T063); targets against 2012 are `not compared`.
- **Status rule.** NDC and sector-plan targets are judged on NDCNEW, LTS targets on LTSNEW; the other ratio is given. Floors met within 10 percent (90 percent renewable in 2040, ratio 0.92) are `matches` by the 10 percent rule although the model is below a stated minimum.
- **Transport units.** The LTS gives fleet shares; the JAM_TRANSPORT Tech_Adoption rows give shares of group activity, which feed the energy model only as E5TRO fuel demand. The model value in the transport rows is the transport-model input share; the energy-model electric share of road energy is in the note.
- **Losses.** The model puts all losses in distribution (ELE_DIST input 1.27, ELE_TRANS 1.0); 1 - 1/1.27 = 21.26 percent is compared with losses as a share of generation. The LTS 2030 milestone (21 percent) matches only by coincidence, so that row is `matches` while the NDC rows are `in documents, not in the model` because no scenario changes the factor.
- **Proposals.** NDC 3.0 items are proposed for NDCNEW; LTS milestones for LTSNEW, with a note where a pre-2035 LTS value conflicts with the hub decision that LTS equals NDC through 2035. For the renewable share the lever that the solver sees is the Stage 1 and Stage 2 curve, not `B1_Scenario_Config.xlsx`. No proposals for AFOLU and waste.

#### Ambiguous targets and how I read them

- **LTS 73 percent and 7.25 Mt (JAM-02 p.13).** The parenthesis follows "2020 levels", so 7.25 MtCO2e is read as the 2020 level. The LTS also gives 10.15 Mt for 2019 (p.33), from another source (ClimateWatch), so the two are not on the same basis.
- **LTS 2050 losses.** Table 1 (p.15) says 11 percent, Table 4 and the text (p.54, p.55) say 8 percent. Both rows are listed; the 8 percent row is compared.
- **LTS fuel efficiency year.** Table 1 and the text (p.14, p.61) give 2030; Table 6 (p.62) lists it under 2025. Read as 2030.
- **LTS transport goals attributed to the NDC.** The LTS says the updated NDC set 35 percent urban public transport, 15 percent fuel efficiency and 20 percent alternative fuels by 2030 (p.61), and that forestry targets come from the NDC (p.80). The 2020 NDC (JAM-03) contains none of these numbers. They are listed as LTS targets.
- **LTS fossil phase-out against renewable milestones.** 100 percent fossil phase-out in 2040 conflicts with 90 percent renewable in 2040 in the same tables (p.15, p.55).
- **LTS afforestation.** Table 13 gives 150 ha per year; the text gives 100 ha per year (p.80, p.81).
- **Forest cover baseline.** NDC 3.0 uses 47.9 percent (p.16); the LTS says 30 percent citing Vision 2030 (p.75); the TNC says 40 percent (p.9).
- **IRP-2 internal inconsistencies.** 2035 renewable share 63.4 percent in Tables 11-6 and 11-13 (p.67, p.77) but 56.3 percent in Table 11-7 (p.68); 2030 power emissions 1.29 Mt (p.15, p.62) or 1.26 Mt (p.90); the 65.5 MW IPP retirement in 2033 (p.15) or 2032 (p.62). Table 11-6 shows HFO at 0.0 percent in every year including 2022, which conflicts with Table 11-7 (12.9 percent in 2022); not used.
- **NDC 3.0 renewable and loss targets: conditionality.** They are listed under the Global Stocktake response, and the next sentence says enhanced ambition is contingent on international support (p.14). Recorded as `not stated`.
- **NDC 3.0 target years read from durations.** Three million trees in five years (read as 2030); non-revenue water over 11 years (read as 2036); 200 electric buses in three years from 2023 (read as 2026).
- **Values the hub check will not find as digits.** JAM-T037 (printed "three million"), JAM-T060 and JAM-T061 (value 0 from "phase out 100%"), JAM-T046 (net zero, value 0). JAM-T002 is found by pypdf but not in the pdfplumber cache, because the two-column table interleaves the text.

#### Solved results against compiled inputs (requested check)

- **Against the compiled limits.** Solved plant generation (`stage3_results.xlsx`, TotalTechnologyAnnualActivity) breaks the compiled `B1_Output_Params` activity limits in every scenario, 2025 to 2050, 0.5 percent tolerance: BAU 106 technology-years below the lower and 29 above the upper limit, NDCNEW 82 and 52, LTSNEW 86 and 56 (`scripts/JAM/model_numbers.py`). Examples in PJ:
  - Fuel oil: compiled upper limit 0 from 2027 in all scenarios (model_levers lines 57 and 70); solved PPFOI 4.73 (BAU 2030), 3.45 (NDCNEW 2030), 1.56 (NDCNEW 2035), 1.66 (LTSNEW 2035).
  - NDCNEW 2030: PPPVT solved 3.61 against a compiled lower limit of 8.02; PPWNDON 2.11 against 4.32; PPHDAM 0.40 against an upper limit of 0.24.
  - BAU 2030: PPPVT 1.07 against a lower limit of 5.30; PPWNDON 0.28 against 2.85.
  - LTSNEW 2050: PPPVT 23.54 against an upper limit of 22.29; PPWNDON 7.88 against a lower limit of 10.33.
- **Implied shares.** The compiled lower limits imply a renewable share of 75 percent already in 2030 in NDCNEW and LTSNEW and 52.9 percent in BAU (66.0 in 2035, 78.1 in 2050). The solved shares are 39.1 percent (policy) and 13.9 percent (BAU) in 2030. The compiled BAU therefore carries a far greener power plan than the solved BAU.
- **Against the Stage 2 controller.** Solved values stay within the controller lower limit and lower times 1.05 (`_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx` sheet CURRENT_LOWER, rows 281 to 304) in every technology-year of all three scenarios. Stage 3 replaces the plant limits from 2025 with controller values (`PIPELINE_WORKFLOW.md`, Stage 3).
- **What does reach the solver from B1.** TotalAnnualMinCapacityInvestment (Electrical rows 86 to 89) is not patched by Stage 3. Solved solar capacity in 2030 equals 57 + 99.83 + 133 + 90 + 90 = 469.8 MW and wind 102 + 3 x 60 + 21 = 303 MW. Demand per fuel, the road emission factors and transport demand also reach the solver unchanged.
- **For the hub.** A renewable share change written only to `B1_Scenario_Config.xlsx` will not reach the solved results unless Stages 0 to 3 are re-run. The renewable share lever is `stage2_apply_v2.py` lines 61 to 75 (and `stage1_share_analyzer_v16.py` lines 97 to 110).

#### Model lever not on the brief's known list: road emission factors (T5DSLTRO, T5GSLTRO on CO2e_DETRN)

- **What it is.** `B1_Scenario_Config.xlsx` sheet SmartGrid rows 11 to 18 apply an `Exact_Multiplier` to the EmissionActivityRatio of the road diesel and gasoline demand technologies. The multipliers are the inverse of fuel-efficiency factors in rows 22 (label LTS: 1.15 in 2030, 1.40 in 2050) and 23 (BAU: 1.05 in 2030, 1.30 in 2050). BAU (rows 13 and 14) therefore lowers the factor by 4.8 percent in 2030 and 23 percent in 2050. NDCNEW and LTSNEW (rows 15 to 18) use 1 from 2025, so the factors return to 0.0743 (diesel) and 0.0695 (gasoline). It is a vehicle fuel-efficiency proxy. It is not biofuel blending: the blend block of the B1 script (lines 3702 to 3770) has empty technology lists and is inactive for Jamaica.
- **Effect.** The inactive LTS rows match the LTS targets exactly (15 percent by 2030, 40 percent by 2050), so the policy scenarios appear to have lost the efficiency gain that BAU keeps. `CO2e_DETRN` in 2025 is 2.636 Mt in both policy scenarios against 2.581 in BAU. The lever changes only this label: fuel demand and `CO2e_sources` (computed at DIST_DSL and DIST_GSL with fixed factors) are unchanged. In 2025 `CO2e_sources` is 5.470 in all three scenarios.
- **`model_levers_JAM.csv`.** Lines 2 and 3 are correct but unlabelled. They are better read as a likely unintended inversion than as a policy measure.

#### Known-limitation candidates

- **Policy road emission factors above BAU** (SmartGrid rows 15 to 18; model_levers lines 2 and 3): see above. BAU 2050 diesel factor 0.0571 against 0.0743 in NDCNEW and LTSNEW.
- **Road diesel above BAU in NDCNEW** (model_levers line 35; Efficiency row 240): 17.61 PJ against 13.91 in 2040 and 22.83 against 17.87 in 2050, while gasoline falls to 17.57 against 37.42. The diesel and gasoline paths come from the transport model and may reflect a fleet-split error.
- **Grid losses fixed at 21.3 percent in all scenarios** (InputActivityRatio ELE_DIST 1.27); the only loss lever is on the inactive LTS label (SmartGrid row 2).
- **Fuel oil in compiled inputs against the controller.** The compiled inputs phase out PPFOI from 2027 in all scenarios; the controller keeps it (BAU 4.73 PJ in 2030). The B1 workbook and the solved runs describe different power systems.
- **Diesel capacity in LTSNEW 2050.** PPDSL capacity 413 MW (77 MW in 2040, 181 MW in 2045) with 0.007 PJ of generation; likely a reserve-margin artefact of Stage 3, which tags firm generators.
- **Biomass plant.** PPBIM has 5 MW capacity and compiled lower limits (0.15 PJ in BAU) but solved generation 0 in all scenarios; the Stage 3 controller gives it 0.
- **Cement process emissions** (`CO2e_CEM`) identical in all scenarios; no clinker substitution technology.
- **History cells.** The brief's six known history lower-limit cells to 2024 per policy scenario are PPDSL 2022 (BAU 0.5754, policy 0.5645), PPDSL 2024 (0.0348, 0.0342) and PPHDAM 2021 to 2024 (0.4979, 0.4884). Policy scenarios also carry 28 zero-valued lower-limit rows to 2024 for techs absent from BAU (PPBGS, PPGEO, PPPVD, PPPVDS, PPPVTS, PPWNDOFF, PPWNDONS), with no value difference.
- **Storage** (STOELE) is the same in all scenarios: 102.5 MW in 2030 against 264 MW in IRP-2.

#### C1 file (`model_levers_JAM.csv`)

- No error found in the rows used. Recomputed from `stage3_results.xlsx`: renewable share 2030 and 2035, capacity of PPPVT, PPWNDON, PPFOI, and emissions `CO2e_sources`, `CO2e_PP`, `CO2e_DETRN`, `CO2e_CEM` for 2025 to 2050 agree.
- Two cautions. The plant-limit rows (lines 39 to 77) do not drive the solved results from 2025; the controller does. The renewable plant list in line 88 (PPBIM PPHDAM PPHROR PPPVT PPWNDON) is right for the solved results, since the other renewable PP techs are capped at 0 by Stage 3.

#### Left unchecked

- LTS read page by page via the text cache (194 pages). Figures with data only in graphics were not read as images: Figure 1 (p.33), Figures 2, 4, 6, 7, 9 (p.50, p.52, p.58, p.71, p.77), Figure 5 (p.53), Figure 10 (p.84). p.14 and p.172 were viewed as images (Table 1 check; p.172 is a photo).
- NDC 3.0 (23 pages), NDC 2020 (12 pages) and INDC (9 pages) read in full.
- IRP-2: executive summary, chapters 4, 5, 9, 11 (p.61 to p.77) and 13 read; transmission chapters (p.79 to p.88) and cost tables skipped. IRP-1: only the target pages p.16 and p.143.
- TNC: summary (p.7 to p.13) and mitigation chapter pages p.327 to p.329, p.345 to p.347, p.354 to p.356, p.364 to p.365. BUR1: executive summary and mitigation tables (p.2 to p.6, p.105 to p.110). Neither was read in full.
- The JAM_AFOLU and JAM_WASTE models were not read for values; only technology names, to name the folder. JAM_TRANSPORT was read only for the Tech_Adoption and Mode_Shift rows of `B1_Scenario_Config.xlsx`; its compiled outputs exist only for BAU and LTS.

#### Incidents

- UNFCCC record pages (documents/649405, first-biennial-transparency-reports) returned bot-check or empty pages. UNFCCC resource files (BUR1, TNC, NDC files) downloaded normally with curl.
- A search lead `resource/Fourth National GHG Inventory rev Aug42020.pdf` turned out to be Belize's inventory; deleted. The `www4.unfccc.int` TNC address returned an HTML page; deleted.
- No request was refused by the session permission system.
- Helper outputs of the model checks were written to the session scratchpad, not to the job folder. Scripts: `scripts/JAM/model_numbers.py`, `config_dump.py`, `config_rows.py`, `self_check_JAM.py`, `spot_check_JAM.py`, `render_pages.py`, `text_cache.py`, and the four `write_*_JAM.py` writers.

