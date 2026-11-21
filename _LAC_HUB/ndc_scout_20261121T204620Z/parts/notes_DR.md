# Notes for GAPS: Dominican Republic (DR)

## Judgement calls and reasons

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

## Ambiguous targets and how I read them

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

## Known-limitation candidates

- **New natural gas.** `B1_Scenario_Config.xlsx` sheet Electrical, row 128 (NDCNEW, TotalAnnualMaxCapacity PPCCTNGSDSL) is 0 in every year, and row 127 (PPCCTNGS) is flat at 1.36162 GW before the 1.05 multiplier. NDCNEW therefore cannot build any of the 1,429 MW of new gas combined cycle that the NDC lists for 2030, while BAU adds 153 MW of PPCCTNGS by 2030.
- **Rail and cable car.** `B1_Scenario_Config.xlsx` sheet Mode_Shift, rows 13, 14, 17 and 18 (Techs_Telef, Techs_Trains, both policy scenarios) are 0, and TRANRAILINF capacity is 0. Measures named in both NDCs (monorail, cable car, metro) have no effect in the model.
- **Distribution losses.** The ELE_DIST InputActivityRatio in NDCNEW and LTSNEW falls to 1.0826 in 2030 and then rises again to 1.1005 by 2050 (`model_levers_DR.csv` row 8). Losses grow back after 2030 in the policy scenarios.
- **Battery storage.** It is part of the NDC solar measure (170 MW, DR-01 p.149), but there is no storage technology among the listed levers.

## Left unchecked

- The IPPU, AFOLU and waste sector models were not read for values. Only technology names were read, to name the folder.
- The adaptation annex (DR-01 Annex 2, physical p.184) is one image page of a 67-page annex that is not included in this PDF.
- The BTR1 was not read in full: chapters 1 and 2 (circumstances, inventory) and chapter 4 onward (adaptation, support) were skimmed through searches. I read the NDC tracking, policies and projections sections (printed p.87 to p.191).
- The NID was searched for projections and mitigation tables; none were found.
- The model's 2024 capacities were not read; 2025 is used as the base for capacity increases.

## C1 file (`model_levers_DR.csv`)

- No error found in the rows used. Rows whose printed 2030, 2035 and 2050 values are equal across scenarios (for example TRBPUDSL TotalAnnualMaxCapacity 9999) differ only in 2025, as their `first_diff_year_from_2025` and `n_diff_years` columns show.

## Incidents

- One scripted request to the CNE website's file-browser endpoint was refused by the session permission system. It was not retried, and the document is in the pending list.
- The DDP 2025 report URL (a search lead) returned a "page not found" HTML page, which was deleted. The first attempt at the END 2030 download returned a Cloudflare page, which was also deleted.
- In spot-check preparation, a self-check found that the DR-T009 value (7,477.22) is printed on p.41 and in the p.45 image, not on p.40. The page reference was corrected before round 1.
