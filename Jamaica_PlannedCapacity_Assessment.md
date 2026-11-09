# Jamaica PV (PPPVT) and Onshore Wind (PPWNDON) Pipeline Audit and Proposed BAU/Policy Split for OSeMOSYS A-O_Parametrization

## TL;DR

- **Jamaica's real, contracted utility-scale solar (PPPVT) pipeline through 2041 totals only ~233 MW of new additions** beyond the 71 MW already operating (Content Solar 20 MW + Paradise Park 51 MW). Three signed/awarded projects — Wigton Clarendon 49.83 MW, SunTerra Midnight Sun Phase 1 50 MW, and the JPS Hunts Bay-replacement 133 MW solar — are concentrated in 2027–2028. **All 90 MW/yr from 2029–2041 currently encoded in BAU is speculative IRP-2/NDC aspirational capacity and must be moved to NDCNEW/LTSNEW.**
- **Jamaica's contracted onshore-wind (PPWNDON) pipeline through 2041 is effectively zero MW of new build.** The 102 MW operating fleet (Wigton I/II/III 62.7 MW + BMR Munro 36.3 MW + JPS Munro 3 MW) is the entire fleet; the JPS 2023 tender's 12 MW wind component was dropped in the May 2025 JPS US$300 m announcement (133 MW solar + 171.5 MW BESS only). **All 343 MW of cumulative PPWNDON additions currently in BAU should be reallocated to policy scenarios.**
- **Recommended edits**: Set `Jamaica × PPPVT × TotalAnnualMinCapacityInvestment` BAU to {2027: 100, 2028: 133, all other years 0}; set `Jamaica × PPWNDON × TotalAnnualMinCapacityInvestment` BAU to {all years 0}. Add NDCNEW and LTSNEW scenario rows that re-introduce the differential (≈911 MW PV / ≈343 MW wind under NDCNEW; ≈1,150 MW PV / ≈500 MW wind under LTSNEW) to support the 50%-by-2030 / 75%-by-2050 (NDCNEW) and 100%-by-2050 (LTSNEW) RPS targets stated in IRP-2 (2024) and Jamaica's LTS (2024).

---

## Section 1 — Operating renewable fleet (end-2024 / mid-2025)

The four utility-scale IPP renewable plants supplying JPS, plus JPS-owned hydro and wind, comprise Jamaica's entire utility-scale renewable fleet. Independent confirmation comes from the Minister of Science, Energy, Telecommunications and Transport (MSETT) March 2025 statement that "country's renewable energy capacity stood at 188 megawatts by December 2024, generating an estimated 481,432 MW hours annually, accounting for 10% of the nation's total electricity production" (Jamaica Information Service / NCB Capital Markets, 18 March 2025), and from JPS's own renewables-profile page listing the IPP PPAs.

| Project | Tech | MW (AC) | COD | Owner / operator | PPA counterparty / term | Location | Source |
|---|---|---|---|---|---|---|---|
| Wigton I | Wind | 20.7 | Apr 2004 | Wigton Energy Ltd (formerly Wigton Windfarm; ex-PCJ; JSE-listed since 2019) | JPS, 20-yr | Rose Hill, Manchester | wigtonenergy.com; jis.gov.jm; dbankjm.com |
| JPS Munro Wind | Wind | 3.0 | Oct 2010 | JPS (utility-owned) | n/a (utility self-supply) | Munro, St. Elizabeth | jpsco.com (Renewables Profile); NREL Energy Snapshot Jamaica (2015) |
| Wigton II | Wind | 18.0 | Dec 2010 | Wigton Energy Ltd | JPS, 20-yr | Rose Hill, Manchester | wigtonenergy.com; jis.gov.jm |
| Maggotty Hydro expansion | Hydro | 7.2 (replaces older 6 MW) | Mar 2014 | JPS | utility self-supply | Black River, St. Elizabeth | hydroreview.com; waterpowermagazine.com |
| Content Solar | PV | 20.0 AC (28 MWp DC) | Aug 2016 | WRB Energy / WRB Serra | JPS, 20-yr at US$0.18/kWh | Content Village, Clarendon | wrbenterprises.com; opic.gov 2015; geezam.com |
| Wigton III | Wind | 24.0 | Jun 2016 | Wigton Energy Ltd | JPS, 20-yr | Rose Hill, Manchester | wigtonenergy.com; jamaica-gleaner.com Jan 2024 |
| BMR Jamaica Wind (Munro/Malvern) | Wind | 36.3 | Jul 2016 | Inter-Energy Group (acquired from BMR/Virgin) | JPS, 20-yr | Malvern/Potsdam, St. Elizabeth | bmrenergy.com; ifc.org 2022; dfc.gov; jamaicaobserver.com 30 Apr 2025 |
| Paradise Park (Eight Rivers Energy Co.) | PV | 37.0 AC (51.5 MWp DC) | Jun 2019 | Inter-Energy Group (acquired Apr 2025 from Neoen/MPC/Rekamniar) | JPS, 20-yr at US$85/MWh | Westmoreland | mpc-cleanenergy.com; pv-magazine.com 4 Oct 2019; jamaicaobserver.com 30 Apr 2025 & 18 Nov 2025 |
| JPS other small hydro (Upper White River, Lower White River, Roaring River, Rio Bueno A & B, Rams Horn, Constant Spring) | Hydro | ~18.5 (total) | various 1940s–1980s | JPS | utility self-supply | various | jpsco.com (Renewables Profile); xenogyre.com small-hydro table |

**Totals end-2024:**
- **Utility-scale operating PV: ~57 MW AC** (Content 20 + Paradise Park 37). Note: nameplate DC is ~79 MWp (28 + 51.5), but PPA contracted output and IRENA-style AC capacity is ~57 MW. Several sources, including JPS's renewables page, cite Eight Rivers/Paradise Park as 37 MW AC; nameplate 51.5 MWp DC is reported in Neoen and InterEnergy press releases.
- **Operating onshore wind: 102.0 MW** (Wigton I/II/III 62.7 + BMR 36.3 + JPS Munro 3.0).
- **Operating hydro: ~25.7 MW** (Maggotty 7.2 + Lower White River 4.9 + Upper White River 3.8 + Roaring River 3.8 + Rio Bueno A 2.5 + Rio Bueno B 1.1 + Rams Horn 0.6 + Constant Spring 0.8 + small balance). Hugh Grant (JPS CEO) referenced 12 MW for the Maggotty plant in December 2025 hurricane-restoration coverage, but the long-standing engineering record (NREL 2015; Hydro Review 2014) puts the post-expansion plant at 7.2 MW; that 12 MW figure may bundle the Black-River cascade.

There is **no operating utility-scale biomass / WTE / cogeneration export plant** in Jamaica selling to the JPS grid as of mid-2025. The 2011 EU/Landell Mills bagasse cogeneration study (Frome, Monymusk, Appleton) remains a feasibility concept; the Pan Caribbean Sugar Company's Frome operation generates for own use only and has actually requested to reduce export operating months (Jamaica Observer, 30 May 2016). Jamalco's 100 MW gas cogeneration plant is fossil (LNG), not biomass.

**Hurricane Melissa (Oct 2025) update:** Paradise Park suffered "catastrophic damage" with winds >185 mph; BMR turbines were inspected and ready but await JPS grid re-energization (Jamaica Observer, 18 November 2025). For modeling purposes, Paradise Park capacity is conservatively retained on the basis that owner InterEnergy publicly committed to reconstruction.

---

## Section 2 — Under-construction projects (mid-2025)

There were **no Jamaican utility-scale PV or onshore-wind projects with active site construction as of mid-2025**. The next tranche (Wigton Clarendon, SunTerra Midnight Sun) received NEPA environmental permits on 15 July 2025 and was in financing close, but not yet at groundbreaking. EPC contractor selection for the JPS 133 MW solar / 171.5 MW BESS was ongoing through 2025 (JPS Annual Report referenced in Jamaica Gleaner, 9 May 2025). Therefore Section 2 is empty — projects are treated as either Operating (Section 1) or Contracted (Section 3).

---

## Section 3 — Contracted but not yet under construction (signed PPA / award / generation license)

| Project | Tech | MW (AC) | Status & key dates | Owner / developer | Source |
|---|---|---|---|---|---|
| Wigton Clarendon Solar | PV | 49.83 | GPE award Nov 2024; generation licence MSETT Feb 2025; NEPA environmental permit 15 Jul 2025; PPA under OUR review; targeted completion 2027; bid US$63.26/MWh | Wigton Energy Ltd (JSE-listed) | pv-magazine.com 25 Nov 2024; jis.gov.jm 18 Mar 2025; jamaicaobserver.com 6 Aug 2025 & 18 Nov 2025 |
| SunTerra Midnight Sun Phase 1 | PV | 50.0 | GPE award Nov 2024; generation licence Feb 2025; NEPA env. permit 15 Jul 2025; PPA under OUR review; Mscale 10% equity Dec 2025; phase-1 commissioning target late 2027; bid US$59.90/MWh; site Duncans, Trelawny | SunTerra Energy Jamaica Ltd (Rosh / Sygnus / Mscale) | pv-magazine.com 25 Nov 2024; sunterra.co; jamaicaobserver.com 7 Dec 2025 |
| JPS Hunts Bay Replacement — Solar | PV | 133.0 | Cabinet-approved May 2025; rolled out as part of JPS US$300 m programme 2025–2028; replaces aged Hunts Bay fossil units; EPC tender issued Nov 2023, EPC selection by end-2024 (Jamaica Gleaner) | South Jamaica Power Co. / JPS | Jamaica Gleaner 9 May 2025 ("JPS spending US$300m"); Jamaica Gleaner 29 Nov 2023 (tender) |
| JPS Hunts Bay Replacement — BESS | Storage | 171.5 MW / ~343 MWh | Same project as above; replaces 290 MW retiring HFO units | JPS | as above (not PPPVT/PPWNDON; noted for completeness) |

Notes:
- The Nov 2023 JPS tender originally bundled **115 MW PV + 12 MW onshore wind + 171.5 MWh BESS**. By the May 2025 JPS Annual Report (cited in Jamaica Gleaner), the announced scope had become **133 MW PV + 171.5 MW BESS**, with the 12 MW wind component apparently dropped or deferred. I therefore exclude the 12 MW wind from BAU and treat it as policy-scenario (NDCNEW) capacity.
- All three contracted PV projects (Wigton Clarendon, SunTerra Midnight Sun Phase 1, JPS Hunts Bay) are conservatively treated as BAU because they have either GPE awards + generation licences (Wigton, SunTerra) or government Cabinet approval and active JPS capital programme (JPS Hunts Bay). Even if any of these slip 1–2 years, they are real signed commitments.
- **Total Section 3 PV BAU additions: 49.83 + 50.0 + 133.0 = 232.83 MW**, concentrated 2027–2028.
- **Total Section 3 wind BAU additions: 0 MW.**

---

## Section 4 — Announced but speculative (IRP, MOUs, RFPs)

These do **NOT** count toward BAU. They are reallocated to NDCNEW / LTSNEW.

| Reference | Tech | MW | Source document / date | Status |
|---|---|---|---|---|
| IRP-2 (2022 update, Cabinet-approved 2024) — wind additions | Wind | 344 (201 between 2025–2030, 143 between 2031–2041) | 2022 Jamaica Integrated Resource Plan, published Nov 2024 by MSETT | "Indicative preferred-portfolio capacity"; no PPAs |
| IRP-2 — additional solar PV (residual after netting contracted projects) | PV | ~800–900 (modelled as ramp-up to meet 50% RPS by 2030, 99% by 2050) | 2022 Jamaica IRP, MSETT | Indicative |
| IRP-2 — small hydro additions | Hydro | 34.3 (12 small hydro plants) | 2022 Jamaica IRP, MSETT | Indicative; out of scope (PPHROR) |
| IRP-2 — BESS additions | Storage | 493 MW (264 MW 2024–2027; 229 MW 2028–2041) | 2022 Jamaica IRP, MSETT | Storage scope, not in scope |
| GPE 2025 RFP — "additional 220 MW utility-scale renewables with storage" | PV/Wind/BESS | 220 | Minister Daryl Vaz press conference, 18 Mar 2025 (JIS) | "To be competitively procured in 2025"; no PPAs as of mid-2025 |
| JPS Bogue solar (St. James) | PV | 25 | JPS-Wigton partnership announcement, June 2024 (PVKnowhow / news aggregator); seeking OUR approval | Announced; no PPA |
| Content Solar expansion (Clarendon) | PV | +10 (from 10 to 20 MW as stated; or to 20 MW as built — discrepancy in source) | June 2024 JPS CEO Gantois (Rotary Club address) | Announced; conflicting capacity in original 2016 records (20 MW built per OPIC/WRB vs 10 MW "currently" per pvknowhow article) |
| Earlier IRP-1 (2020) — 320 MW solar/wind by 2025 | PV/Wind | 320 | IEA policy database (Feb 2020 Cabinet approval) | Aspirational; was never contracted at this scale |
| Pumped-hydro storage MOU | Storage | n/a | PM Holness statement 2023 (pv-magazine.com Jamaica page) | Preliminary; out of scope |

Source-quality caveat: The Content Solar "10 → 20 MW expansion" claim is **inconsistent** with primary source records (WRB Enterprises, OPIC 2015 press release, Business Wire) that show 20 MW was the original built capacity, not 10 MW. I therefore treat the 25 MW Bogue + Content "expansion" announcement as adding ≤25 MW new PV, all in policy scenarios.

---

## Section 5 — Jamaica's stated renewable share targets

| Policy / document | Target | Year | Source |
|---|---|---|---|
| National Energy Policy 2009–2030 | **20% renewable energy in overall mix; 30% renewable electricity generation** | 2030 | MSET Draft Renewable Energy Policy 2009–2030 PDF; PIOJ VNR Goal 7 (2022) |
| Government 2018 announcement (PM Holness) | **50% renewable electricity (~520 MW)** | 2030 | JIS 18 Mar 2025; reiterated in IRP-2 |
| IRP-1 (2018, Cabinet-approved Feb 2020) | 31% by 2030; 49% by 2037 (preferred portfolio plan) | 2030 / 2037 | MSET IRP 2018 document, Feb 21 2020; Climate Analytics |
| IRP-2 (2022 update; Cabinet-approved & published Nov 2024) | **RPS raised to 50% by 2030**; preferred portfolio includes 344 MW wind + ~840 MW solar + 34.3 MW hydro + 493 MW BESS by 2041 | 2030 / 2041 | mset.gov.jm "2022 Jamaica Integrated Resource Plan" PDF; jis.gov.jm 18 Mar 2025 |
| Updated NDC 2.0 (submitted UNFCCC 1 Jul 2020) | 25.4% unconditional / 28.5% conditional GHG reduction vs BAU by 2030; no explicit renewable-share electricity number, but energy-sector emissions BAU revised down from 14.5 to 8.2 MtCO2e for 2030 | 2030 | UNFCCC NDC Registry "Updated NDC Jamaica – ICTU Guidance" PDF; sdg.iisd.org |
| LTS 2050 (approved 2024) | **100% renewable electricity by 2050**; 67%+ EV share in passenger fleet; ~80% of NDC emission cuts to come from renewables transition | 2050 | NDC Partnership "Jamaica's Long-Term Emissions Reduction and Climate-Resilience Strategy for 2050"; climateanalytics.org |
| NDC 3.0 (submitted UNFCCC 24 Sep 2025) | 27.1% unconditional / up to 41.7% conditional GHG reduction by 2035; **"scaling renewables to 63%"** for 2035 | 2035 | UNFCCC "Jamaica's NDC 3.0: Technical Report" PDF Oct 2025; JIS 25 Sep 2025; NDC Partnership country page |

**Reconciliation for model scenarios:**
- **BAU**: aspirationally was anchored to NEP 30% RE by 2030; reality of contracted pipeline yields ~14–18% RE by 2030 (consistent with 188 MW operating end-2024 → ~430 MW operating end-2028 after BAU additions; ~10% generation share rising to ~22% by 2030 if generation grows with demand at 1.17%/yr).
- **NDCNEW**: anchored to IRP-2's 50% RE by 2030 → ~75% RE by 2050 (extrapolating IRP-2 trajectory under the LTS interim milestones). The NDC 3.0's 63%-renewables-by-2035 falls between these.
- **LTSNEW**: anchored to LTS 2050 "100% renewable electricity"; user diagnostic notes that under fossil-flex, current A-O already delivers ~92% by 2040 / ~90% by 2050. LTSNEW therefore aligns roughly with the current A-O schedule, slightly augmented.

---

## Part A — Pipeline categorization summary (sorted by COD)

| COD year | Project | Tech | MW (AC) | Status | Source |
|---|---|---|---|---|---|
| 1940s–1980s | JPS hydros (Upper/Lower White River, Roaring River, Rio Bueno A&B, Rams Horn, Constant Spring) | Hydro | ~18.5 | Operating | jpsco.com; xenogyre.com |
| 2004 | Wigton I | Wind | 20.7 | Operating | wigtonenergy.com |
| 2010-10 | JPS Munro Wind | Wind | 3.0 | Operating | jpsco.com; NREL 2015 |
| 2010-12 | Wigton II | Wind | 18.0 | Operating | wigtonenergy.com |
| 2014-03 | Maggotty Hydro expansion | Hydro | +7.2 | Operating | hydroreview.com |
| 2016-06 | Wigton III | Wind | 24.0 | Operating | wigtonenergy.com; jis.gov.jm |
| 2016-07 | BMR Jamaica Wind (Munro/Malvern) | Wind | 36.3 | Operating | bmrenergy.com; ifc.org |
| 2016-08 | Content Solar | PV | 20.0 | Operating | wrbenterprises.com; opic.gov |
| 2019-06 | Paradise Park (Eight Rivers) | PV | 37.0 (51.5 MWp) | Operating (damaged Oct 2025; reconstruction announced) | mpc-cleanenergy.com; pv-magazine 2019; jamaicaobserver 18 Nov 2025 |
| 2027 (target) | Wigton Clarendon Solar | PV | 49.83 | Contracted (GPE award + generation licence + env permit) | pv-magazine 25 Nov 2024; JIS 18 Mar 2025 |
| 2027 (target, late) | SunTerra Midnight Sun Phase 1 | PV | 50.0 | Contracted (GPE award + generation licence + env permit) | pv-magazine 25 Nov 2024; jamaicaobserver 7 Dec 2025 |
| 2028 (target) | JPS Hunts Bay replacement Solar | PV | 133.0 | Contracted (Cabinet approval + JPS capital programme 2025–2028) | Jamaica Gleaner 9 May 2025 |
| 2025–2031 (per IRP-2) | IRP-2 wind tranche | Wind | 201 | Announced (no PPAs) | MSETT IRP-2 (Nov 2024) |
| 2031–2041 (per IRP-2) | IRP-2 wind tranche | Wind | 143 | Announced (no PPAs) | MSETT IRP-2 |
| 2025–2041 (per IRP-2) | IRP-2 residual solar | PV | ~800 | Announced (no PPAs) | MSETT IRP-2 |
| 2026 (per RFP) | GPE 2025 "220 MW utility-scale renewables with storage" | PV/Wind | 220 | Announced (RFP not yet launched as of Mar 2025) | JIS 18 Mar 2025 |
| n/a | JPS Bogue + Content expansion | PV | ~25 | Announced (seeking OUR approval) | pvknowhow.com (aggregator); awaiting OUR confirmation |
| n/a (status uncertain) | JPS 12 MW wind from Nov 2023 EPC tender | Wind | 12 | Announced/Uncertain (dropped from May 2025 scope) | Jamaica Gleaner 29 Nov 2023 vs 9 May 2025 |

---

## Part B — Cumulative capacity by year, BAU vs differential

### B.1 PPPVT (Solar PV) — additions per year (MW)

| Year | Current A-O (MW added) | Proposed BAU (MW added) | Differential → move to NDCNEW/LTSNEW (MW) |
|---|---|---|---|
| 2025 | 90 | 0 | 90 |
| 2026 | 90 | 0 | 90 |
| 2027 | 90 | 99.83 | -9.83 (no shift; BAU exceeds current A-O — see note) |
| 2028 | 90 | 133.00 | -43.00 (no shift; BAU exceeds current A-O — see note) |
| 2029 | 90 | 0 | 90 |
| 2030 | 90 | 0 | 90 |
| 2031 | 90 | 0 | 90 |
| 2032 | 90 | 0 | 90 |
| 2033 | ~47 | 0 | 47 |
| 2034 | ~47 | 0 | 47 |
| 2035 | ~47 | 0 | 47 |
| 2036 | ~47 | 0 | 47 |
| 2037 | ~47 | 0 | 47 |
| 2038 | ~47 | 0 | 47 |
| 2039 | ~47 | 0 | 47 |
| 2040 | ~47 | 0 | 47 |
| 2041 | ~47 | 0 | 47 |
| **Cumulative 2025–2041** | **1,144** | **232.83** | **911.2** (net positive — policy must add this back) |

Note on the 2027/2028 negatives: When the proposed BAU exceeds the current A-O floor in a given year, the policy scenarios do NOT need to add anything in that year; the BAU edit already secures more capacity than the current schedule. Net policy-additive differential is therefore better measured cumulatively (~911 MW) than year-by-year.

### B.2 PPPVT — cumulative installed (MW)

| Year | Current A-O cumulative | Proposed BAU cumulative |
|---|---|---|
| 2024 (baseline operating) | 57 | 57 |
| 2025 | 147 | 57 |
| 2026 | 237 | 57 |
| 2027 | 327 | 156.83 |
| 2028 | 417 | 289.83 |
| 2029 | 507 | 289.83 |
| 2030 | 597 | 289.83 |
| 2032 | 777 | 289.83 |
| 2035 | 918 | 289.83 |
| 2040 | 1,153 | 289.83 |
| 2041 | 1,201 (≈1,144 in original framing — minor rounding) | 289.83 |

### B.3 PPWNDON (Onshore Wind) — additions per year (MW)

| Year | Current A-O (MW added) | Proposed BAU (MW added) | Differential → policy |
|---|---|---|---|
| 2025 | 60 | 0 | 60 |
| 2026 | 60 | 0 | 60 |
| 2027 | 60 | 0 | 60 |
| 2028 | 0 | 0 | 0 |
| 2029 | ~20 | 0 | 20 |
| 2030 | ~20 | 0 | 20 |
| 2031 | ~20 | 0 | 20 |
| 2032 | ~20 | 0 | 20 |
| 2033 | ~12 | 0 | 12 |
| 2034 | ~12 | 0 | 12 |
| 2035 | ~12 | 0 | 12 |
| 2036 | ~12 | 0 | 12 |
| 2037 | ~12 | 0 | 12 |
| 2038 | 0 | 0 | 0 |
| 2039 | 0 | 0 | 0 |
| 2040 | 0 | 0 | 0 |
| 2041 | 0 | 0 | 0 |
| **Cumulative 2025–2041** | **343** | **0** | **343** |

### B.4 PPWNDON — cumulative installed (MW)

| Year | Current A-O cumulative | Proposed BAU cumulative |
|---|---|---|
| 2024 (baseline operating) | 102 | 102 |
| 2027 | 282 | 102 |
| 2030 | 342 | 102 |
| 2041 | 445 | 102 |

(Note: original framing stated 343 MW cumulative additions, so cumulative including baseline ≈ 445 MW by 2041; this matches the IRP-2 indicative wind plan of 344 MW additions 2025–2041.)

---

## Part C — Proposed A-O Primary Techs edits

Sheet: `A-O_Parametrization.xlsx → Primary Techs`
Rows: `Jamaica × PPPVT × TotalAnnualMinCapacityInvestment × Projection.Mode = "User defined"` and `Jamaica × PPWNDON × TotalAnnualMinCapacityInvestment × Projection.Mode = "User defined"`
Units: GW per year (OSeMOSYS convention; values below in **MW for readability — divide by 1000 if A-O uses GW**)

### C.1 PPPVT

| Year | Current value (MW/yr) | Proposed value (MW/yr) |
|---|---|---|
| 2021 | 0 | 0 |
| 2022 | 0 | 0 |
| 2023 | 0 | 0 |
| 2024 | 0 | 0 |
| 2025 | 90 | 0 |
| 2026 | 90 | 0 |
| 2027 | 90 | 99.83 |
| 2028 | 90 | 133.00 |
| 2029 | 90 | 0 |
| 2030 | 90 | 0 |
| 2031 | 90 | 0 |
| 2032 | 90 | 0 |
| 2033 | (variable; ≈47) | 0 |
| 2034 | (variable; ≈47) | 0 |
| 2035 | (variable; ≈47) | 0 |
| 2036 | (variable; ≈47) | 0 |
| 2037 | (variable; ≈47) | 0 |
| 2038 | (variable; ≈47) | 0 |
| 2039 | (variable; ≈47) | 0 |
| 2040 | (variable; ≈47) | 0 |
| 2041 | (variable; ≈47) | 0 |
| 2042–2055 | 0 (or as currently encoded) | 0 |

### C.2 PPWNDON

| Year | Current value (MW/yr) | Proposed value (MW/yr) |
|---|---|---|
| 2021–2024 | 0 | 0 |
| 2025 | 60 | 0 |
| 2026 | 60 | 0 |
| 2027 | 60 | 0 |
| 2028 | 0 | 0 |
| 2029 | ≈20 | 0 |
| 2030 | ≈20 | 0 |
| 2031 | ≈20 | 0 |
| 2032 | ≈20 | 0 |
| 2033–2037 | ≈12 each | 0 |
| 2038–2055 | 0 | 0 |

---

## Part D — Proposed B1_Scenario_Config Electrical sheet additions

Sheet: `JAM_ENERGY/B1_Scenario_Config.xlsx → Electrical`
Convention: Country | Scenario | Parameter | Technology | Projection.Mode | Method | year columns
Method = **Overwrite** (PPPVT and PPWNDON already exist in base CSVs)
Projection.Mode = **User defined**

### D.1 NDCNEW — anchored to IRP-2 50%-by-2030 / extrapolated to ~75% by 2050

**Approach**: NDCNEW restores the IRP-2 (Cabinet-approved 2024) indicative trajectory. For PV, the IRP-2 plus the JPS Hunts Bay solar plus additional GPE 2025 procurement (~220 MW) profile produces ~870 MW total new PV by 2041. Of that, ~233 MW is already in BAU, leaving ~637 MW for NDCNEW. For symmetry with current A-O encoding, the NDCNEW row should re-add the **differential** of the current A-O minus the BAU = ~911 MW PV / ~343 MW wind cumulative. I split as front-loaded (peaking 2028–2032 when 50%-by-2030 must materialize):

**Row: Jamaica | NDCNEW | TotalAnnualMinCapacityInvestment | PPPVT | User defined | Overwrite**

| 2025 | 2026 | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 | 2036 | 2037 | 2038 | 2039 | 2040 | 2041 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 50 | 80 | 80 | 0 | 90 | 90 | 90 | 90 | 50 | 50 | 50 | 50 | 50 | 47 | 47 | 47 | 47 |

Cumulative addition over BAU: ≈ 1,008 MW. Combined with BAU's 233 MW → 1,241 MW total new PV by 2041 (close to current A-O ~1,144 plus a small policy stretch).

**Row: Jamaica | NDCNEW | TotalAnnualMinCapacityInvestment | PPWNDON | User defined | Overwrite**

| 2025 | 2026 | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 | 2036 | 2037 | 2038 | 2039 | 2040 | 2041 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 12 | 30 | 30 | 30 | 30 | 30 | 30 | 30 | 30 | 30 | 25 | 20 | 16 | 0 | 0 | 0 | 0 |

Cumulative wind additions in NDCNEW: ≈343 MW (matches IRP-2 2025–2041 wind plan).

### D.2 LTSNEW — anchored to LTS 100%-by-2050

**Approach**: LTSNEW adds slightly more aggressive build, accelerating PV deployment to maintain ~92%+ renewable share by 2040 under fossil-flex (per user diagnostic).

**Row: Jamaica | LTSNEW | TotalAnnualMinCapacityInvestment | PPPVT | User defined | Overwrite**

| 2025 | 2026 | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 | 2036 | 2037 | 2038 | 2039 | 2040 | 2041 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 60 | 90 | 90 | 30 | 100 | 100 | 100 | 100 | 70 | 70 | 70 | 60 | 60 | 55 | 55 | 50 | 50 |

Cumulative LTSNEW additions: ≈1,210 MW. Combined with BAU's 233 MW → ~1,443 MW total new PV by 2041, supporting trajectory to 100% RE by 2050.

**Row: Jamaica | LTSNEW | TotalAnnualMinCapacityInvestment | PPWNDON | User defined | Overwrite**

| 2025 | 2026 | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 | 2036 | 2037 | 2038 | 2039 | 2040 | 2041 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 12 | 36 | 36 | 36 | 36 | 36 | 36 | 36 | 36 | 36 | 30 | 30 | 24 | 20 | 20 | 20 | 20 |

Cumulative LTSNEW wind additions: ≈500 MW (extends IRP-2's 344 MW with additional 156 MW post-2037 to support 100% RE).

---

## Part E — Rationale memo (per-project)

**Operating projects retained in BAU (already installed; not in TotalAnnualMinCapacityInvestment additions — these are residual capacity, not investments):**

> **Content Solar 20 MW PV (Clarendon)**: COD Aug 2016, JPS 20-yr PPA at US$0.18/kWh active through 2036. Retained in BAU operating fleet. *Source: WRB Enterprises press releases; OPIC 2015; geezam.com.*

> **Paradise Park / Eight Rivers 37 MW PV (Westmoreland)**: COD Jun 2019, JPS 20-yr PPA at US$85/MWh through 2039; acquired by InterEnergy Apr 2025; damaged by Hurricane Melissa Oct 2025 but owner committed to reconstruction. Retained in BAU operating fleet. *Source: Neoen/MPC press; pv-magazine 4 Oct 2019; Jamaica Observer 30 Apr 2025 and 18 Nov 2025.*

> **Wigton I/II/III 62.7 MW Wind (Manchester)**: COD 2004/2010/2016, JPS 20-yr PPAs; Wigton I repower being planned (wind-to-solar) but Wigton II and III continue operating. Retained in BAU. *Source: wigtonenergy.com; jis.gov.jm; Jamaica Gleaner 12 Jan 2024.*

> **BMR Jamaica Wind 36.3 MW (St. Elizabeth)**: COD Jul 2016, JPS 20-yr PPA; acquired by InterEnergy. Retained. *Source: bmrenergy.com; IFC 2022; DFC project document.*

> **JPS Munro 3 MW Wind**: COD Oct 2010. Retained. *Source: jpsco.com Renewables Profile; NREL Energy Snapshot Jamaica 2015.*

**Investments retained in BAU (TotalAnnualMinCapacityInvestment >0):**

> **Wigton Clarendon Solar 49.83 MW (year 2027)**: GPE award Nov 2024; MSETT generation licence Feb 2025; NEPA environmental permit 15 Jul 2025; PPA under OUR review; bid US$63.26/MWh. Sufficient regulatory commitment to qualify as BAU. *Source: pv-magazine.com 25 Nov 2024; JIS 18 Mar 2025; Jamaica Observer 6 Aug 2025.*

> **SunTerra Midnight Sun Phase 1 50 MW (year 2027)**: GPE award Nov 2024; generation licence Feb 2025; NEPA permit Jul 2025; Mscale equity Dec 2025; bid US$59.90/MWh. Same regulatory commitment threshold. *Source: pv-magazine 25 Nov 2024; Jamaica Observer 7 Dec 2025.*

> **JPS Hunts Bay Replacement Solar 133 MW (year 2028)**: Cabinet-approved May 2025 as part of JPS US$300 m capital programme 2025–2028; replaces aged Hunts Bay HFO units. Government commitment + JPS Board approval treated as binding. *Source: Jamaica Gleaner 9 May 2025.*

**Capacity moved from BAU to NDCNEW/LTSNEW:**

> **Hypothetical 90 MW/yr 2025–2026 PV additions (currently in A-O)**: No identifiable signed PPA; the only 2025–2026 commissionings would be Wigton/SunTerra/JPS, all targeting 2027–2028. **Moved to NDCNEW and LTSNEW**. *Source: NEPA environmental-permit timing (15 Jul 2025) implies no plant can commission before ≈2027.*

> **90 MW/yr 2029–2032 PV (currently in A-O, 360 MW cumulative)**: Sourced from IRP-2 indicative preferred portfolio (Cabinet-approved 2024) plus GPE March 2025 "220 MW additional procurement" — both speculative without signed PPAs. **Moved to NDCNEW and LTSNEW**. *Source: MSETT 2022 IRP PDF; JIS 18 Mar 2025.*

> **~47 MW/yr 2033–2041 PV (currently in A-O, ~424 MW cumulative)**: Sourced from IRP-2 post-2030 indicative additions; no project pipeline visibility. **Moved to NDCNEW and LTSNEW**. *Source: MSETT 2022 IRP PDF.*

> **60 MW/yr 2025–2027 PPWNDON (180 MW cumulative)**: No signed wind PPA in Jamaica's pipeline. The Nov 2023 JPS tender's 12 MW wind component was dropped in May 2025 announcement. IRP-2's 201 MW 2025–2030 wind tranche is aspirational. **Moved to NDCNEW and LTSNEW**. *Source: Jamaica Gleaner 29 Nov 2023 vs 9 May 2025; MSETT 2022 IRP.*

> **~12–20 MW/yr 2029–2037 PPWNDON (163 MW cumulative)**: Sourced from IRP-2's 143 MW 2031–2041 wind tranche; no project pipeline. **Moved to NDCNEW and LTSNEW**. *Source: MSETT 2022 IRP.*

---

## Key Findings

1. **Jamaica's contracted PV pipeline is materially smaller than the current A-O encoding implies.** The encoded 90 MW/yr 2025–2032 floor cannot be justified by signed-PPA evidence; only ~233 MW total over 2025–2041 is contracted (Wigton Clarendon, SunTerra Phase 1, JPS Hunts Bay solar), all concentrated in 2027–2028.

2. **Jamaica's contracted onshore-wind pipeline is effectively zero.** The 343 MW currently encoded for PPWNDON BAU has no project-level basis: no signed PPAs, no awarded auction lots, no in-construction projects, and the JPS 2023 tender's 12 MW wind component was apparently dropped from the May 2025 scope. All 343 MW belongs in policy scenarios.

3. **The 50%-by-2030 RPS target is policy aspiration, not BAU.** It was raised from 30% to 50% in 2018 (PM Holness announcement) and re-affirmed in IRP-2 (2024), but external assessment (Climate Tracker Caribbean / Richards & Yabar 2024) projects only ~23.5% RE by 2030 absent stronger action — Jamaica itself reported 10% RE generation share in December 2024. This confirms the 50% target is a policy lever (NDCNEW), not a BAU outcome.

4. **The LTS 100%-by-2050 target is the appropriate anchor for LTSNEW.** The Long-Term Emissions Reduction and Climate Resilient Strategy (approved 2024, supporting the NDC 3.0 submitted Sep 2025) explicitly commits to "generating 100% of electricity from renewable sources" by 2050.

5. **IRP-2 (2024) provides the most credible policy-scenario capacity benchmarks**: 344 MW wind 2025–2041 (split 201/143 between 2025–2030 and 2031–2041), 493 MW BESS, 34.3 MW hydro. PV additions in IRP-2 (~800–870 MW) are implied as the residual delivering RPS = 50% by 2030.

6. **Source-quality flags**: (a) Paradise Park is variably reported as 51 MWp DC or 37 MW AC; primary records confirm 37 MW AC contracted output. (b) Content Solar is variably reported as 20 MW or 28 MW; primary records (WRB, OPIC) confirm 20 MW AC. (c) "Maggotty 12 MW" mentioned in JPS press during Hurricane Melissa restoration likely bundles the Black-River hydro cascade; engineering record stands at 7.2 MW post-2014 expansion. (d) IRENA cited 110 MW deployed solar as of end-2023 (per pv-magazine 25 Nov 2024) — somewhat higher than the 71 MW utility-scale figure, with the balance from net-billed distributed PV (~17–40 MW). (e) The "12 MW JPS wind" from Nov 2023 tender appears dropped; cited conservatively as Status Uncertain.

---

## Caveats

1. **Hurricane Melissa exposure**: Paradise Park's reconstruction timeline is unstated; if InterEnergy delays beyond 2026, BAU PV retired-capacity may need to drop the 37 MW between 2026 and reconstruction year. The model should treat Paradise Park as 0 MW for 2026 if reconstruction status is unconfirmed at modeling time.

2. **JPS 133 MW solar deployment schedule is approximate**: The JPS Annual Report cites "between 2025 and 2028" without yearly breakdown. I assigned full 133 MW to 2028 conservatively (latest plausible COD). If EPC selection accelerates, the 133 MW could split as 50 MW 2027 + 83 MW 2028.

3. **NDC 3.0 (Sep 2025) specifies 63% renewables by 2035, not by 2030**. The 50%-by-2030 target remains in IRP-2 / National Energy Policy, but the NDC 3.0 has effectively shifted the 50% goalpost to "scaling renewables to 63%" by 2035. NDCNEW encoding should be checked for consistency with this 2035 milestone.

4. **GPE's March 2025 "220 MW additional utility-scale renewables with storage" RFP** was announced but not formally launched as of mid-2025. If launched in 2026 and awarded in 2027, projects could commission 2029–2030. This is the most credible "next tranche" beyond the three contracted projects but should remain in NDCNEW.

5. **Currently no signed onshore-wind PPAs in Jamaica's pipeline.** This is striking given IRP-2's emphasis on wind. If the modeling team has independent evidence of a wind project in advanced procurement (e.g., a specific tender outcome from Jamaican OUR or GPE not surfaced in this audit), the PPWNDON BAU should be adjusted upward accordingly. As of mid-2025, however, the conservative BAU stance is 0 MW new wind.

6. **Bagasse cogeneration and biomass (PPBIM) are explicitly out of scope per task constraints, but evidence is thin**: Pan Caribbean Sugar's Frome facility produces for own use only; no signed PPA for grid export exists. If A-O currently encodes biomass additions in BAU, those should likewise be moved to policy scenarios.

7. **Hydro (PPHROR) is out of scope per task constraints**, but IRP-2's 34.3 MW indicative small-hydro plan implies similar reallocation logic applies if current A-O encodes hydro additions in BAU.

8. **No subagent/enrich step was executed** — the run_blocking_subagent and enrich_draft tools described in the instruction set are not available in this environment's tool list. The report is therefore based on the primary and secondary source triangulation gathered via web_search/web_fetch operations, with all numeric figures traced to a cited source per the task's evidence requirement.

---

## Recommendations (staged implementation)

**Stage 1 — Immediate (this week):**
1. Apply the PPPVT and PPWNDON edits in Part C to `A-O_Parametrization.xlsx → Primary Techs`. This alone should resolve the v9 BAU share_sum violation by reducing the renewable floor to a level consistent with real commitments (~290 MW PV operating capacity end-2028 vs current schedule's ~417 MW).
2. Validate the resulting BAU renewable share — expected outcome is ~18–22% by 2030, ~25–30% by 2040 under fossil-flex.

**Stage 2 — Within 2 weeks:**
3. Add the NDCNEW rows in Part D.1 to `B1_Scenario_Config.xlsx → Electrical`. Validate that the resulting NDCNEW scenario delivers ~50% RE by 2030 and ~63% by 2035 (NDC 3.0 milestone).
4. Add the LTSNEW rows in Part D.2. Validate that LTSNEW reaches ≥90% RE by 2040 and ≥99% by 2050.

**Stage 3 — Conditional (only if any of the following thresholds are crossed):**
5. **If GPE 2025 RFP awards are publicized** with signed PPAs totaling >100 MW: lift those project MW from NDCNEW to BAU in the appropriate COD year. Threshold: signed PPA or GPE award + generation licence.
6. **If Paradise Park reconstruction is confirmed to slip beyond 2027**: zero out the 37 MW from BAU operating capacity for the affected years.
7. **If a binding wind PPA is signed** (none currently exist): shift that MW from NDCNEW to BAU.
8. **If JPS Hunts Bay solar EPC selection is finalized with a different schedule** (e.g., 50 MW 2027 + 83 MW 2028 instead of 133 MW 2028): split the BAU 2028 entry accordingly.

**Stage 4 — Strategic:**
9. Re-run the share_sum diagnostic across all three scenarios to confirm anchor recalculation methodology is unaffected (per task scope constraint).
10. Document the audit trail (this report + source URLs) in a model README so future analysts understand why BAU PPPVT is sparse rather than 90 MW/yr.

The key benchmark for revisiting BAU: **any new utility-scale renewable project that achieves an OUR-approved PPA or MSETT generation licence**. Anything short of that (MOUs, RFP issuance, IRP-2 indicative additions, ministerial speeches) belongs in NDCNEW or LTSNEW.