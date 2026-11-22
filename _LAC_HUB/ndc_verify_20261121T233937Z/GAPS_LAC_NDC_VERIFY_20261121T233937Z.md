# GAPS: LAC_NDC_VERIFY 20261121T233937Z

## 1. Judgement calls and reasons

1. **Which targets rows to verify (step A).** Every targets row cited by a class A or B proposal (same source, a shared page), plus every numeric row whose indicator, description or unit matches keyword rules for emissions, renewable share or generation, capacity, vehicles, blends, losses and efficiency (`scripts/a2_values_to_verify.py`). Measure-level emission reductions are included, because a sector target in these NDCs is often the sum of measures and splitting them by hand would be a judgement per row. Rows from superseded NDCs, BTRs and sector plans are included as the brief lists kinds, not documents. 111 targets rows were left out (forest, agriculture, waste, HFC and count indicators; list in `parts/values_not_selected.csv`).
2. **Which projection rows.** The BAU and mitigation series of the NDC in force and of the long-term strategy or named plan; inventory, historic and common-start rows were left out.
3. **Blind items.** Target rows sharing source, pages and description (with numbers, years and units masked) became one blind item, and the reader reported every year; projection series became one item per scenario and sector. The Dominican Republic BAU table by gas lost the gas in this grouping (hub error), so ten values got a blind reading of the total instead; their third reading by the hub and the repeat of the same table on p.195 carry them to 2 of 3.
4. **Status rule (step B).** Check 1 counts unless the hub's third reading overturns it; check 2 counts when the blind value matches for the same year; check 3 counts for an identity among printed numbers, or the same figure on another page or document in a line that also holds the year or a keyword of the value's kind. Pages in the scout's page list other than the first count as second places when the figure is printed there. The hub's third reading decides what the document supports but is not counted as a fourth check. One check out of three, or a document that supports neither reading, gives `conflict`.
5. **Verbal targets.** Net zero, carbon neutrality, phase out 100 percent, all stoves, halved and no new fossil plant are words the scout encoded as numbers (0, 0 MW, 100 percent, 50 percent). Where the blind reader found the same statement and year, check 2 counts (`parts/third_reading.csv`, 11 rows). Their check 3 counts when the statement is on a second page.
6. **Document self-contradictions.** Values whose document gives two figures for the same quantity and year, or a figure its own label contradicts, are conflicts whatever their counts (`parts/self_conflicts.csv`: JAM-T058, JAM-T059, GUA-P049).
7. **Plans the NDC cites.** NDC rows come from the NDC in force plus the plans it names in its text: the PIEG 2026-2035 (HON-01 p.26), the IRP-2 (JAM-01 p.5) and the Plan Maestro de Electricidad (ECU-01 p.14, p.102). The PLANEE (ECU-08) is not named in the text of ECU-01 that was searched, though the scout had recorded p.67, so its values are not NDC rows. The Guatemala Plan Nacional de Energia (GUA-07) is not named by GUA-01 either.
8. **Plans named by the NDC as long-term plans.** END 2030 (DR-06, named in DR-01 p.9 and p.26) and the PLANMICC (ECU-03, named in ECU-01 p.10 and p.33). Honduras names neither a submitted strategy nor another plan with values: one row says `no published long-term value`.
9. **BAU projections are not written to `scenario_values.csv`.** The table has NDC and LTS rows only; BAU series stay in the verification files as reference values.
10. **Model quantity rules (step C).** Shares of generation are recomputed under each country's definition (`model_comparison.csv`, note column). Capacity targets are matched to plant types by the indicator first, then the description; added or retired capacity is marked `partly` because the model gives installed capacity. Emissions are compared only for energy sector totals, with the label `CO2e_sources`; economy-wide, non-energy, measure-level and subsector values are `different quantity`. Fleet shares are `different quantity` (the model has output shares). The model's emission label unit is read as Mt CO2 eq from its emission factors; the GWP set of the model factors is not stated in the model files.
11. **Model generation for Jamaica is read as net generation** (the model has no plant own use), so the net-generation targets are marked `yes (model generation read as net generation)`.
12. **Ecuador renewable split** is computed over all plant types, not the SNI only; the PLANMICC table does not define its denominator further.
13. **Classes of sources.** The 46 scout documents are `official`. HON-01 credits Climate Lead Group-Libelula with its drafting (p.4), GUA-01 credits CLG for technical support (p.5) and ECU-01 names OSeMOSYS (p.66), but these are government submissions and stay `official`. The research tasks classed every document with CLG authors as `lead` (16 documents), including the IDB monograph 1138 (DR-23), the DDP 2025 chapters (CR-24, DR-25, GUA-22), the RDM guide (GUA-23) and an AFD interview with a CLG modeller (ECU-25). CR-23 (RAND for the IDB) is `external`: three authors later wrote CLG documents but the report credits the University of Costa Rica.
14. **Second places found by text search** were not each opened by the hub; the rule requires the year or a keyword in the same line. Weak matches (number only) do not count.
15. **Conditionality** is taken from the scout's targets rows. Nine rows say `mixed` (a single value that combines conditional and unconditional contributions, for example Jamaica's 8.5 points unconditional and 19.5 points conditional); they are kept as `mixed` rather than forced into one of the three words, and no split was computed.
16. **Text extraction.** Pages were cached with `pdftotext -layout`; pypdf was used for GUA-02 (no text from pdftotext) and GUA-04 (page split did not match the page count). The first pypdf pass was stopped as too slow.

## 2. Documents not fetched

- UNFCCC NDC registry and long-term strategies portal: Incapsula bot check to curl on three addresses (`unfccc.int/NDCREG`, the registry page, `unfccc.int/ndc-3.0`) and an Imperva CAPTCHA in the browser pane, not passed. Document versions were confirmed from title pages and UNFCCC file folders instead (`document_status.csv`).
- Still pending after step D1 (`sources_pending.csv`): the Dominican Republic LT-LEDS (a draft awaiting launch, DR-25 p.2) and the PEN 2025-2038 (final publication stage, DR-26); the Ecuador ENEM; the Honduras ENDRCH (not published) and the NDC 3.0 technical annex; the Jamaica BTR1 and NID.
- Fetched in D1: ICE PEG 2022-2040 (CR-22), the Costa Rica INDC Spanish original (CR-21), the PNMUS (ECU-21), the ENDBE UNFCCC file (GUA-21, a 2021 reprint with the same figures as GUA-04, not byte-identical), the ENME (HON-21). The Jamaica LTS UNFCCC file is byte-identical to JAM-02 and was not registered again.
- Supporting analyses not obtained: Guatemala MARN 2026a and 2026b, the MEM PEG 2024-2054 (Cloudflare check) and the Deloitte and Enel roadmap (bot check); the Jamaica Vivid Economics and World Bank 2021 LTS reports, RMI 2021, the MEGJC NDC implementation plan (expired certificate, not bypassed); the Honduras SEN LEAP study and an ES&T paper behind a paywall; the Ecuador CCDR background note 4; the UNFCCC case study on Jamaica's LTS (bot check), so the CLG, UWI and CIRED claim is unconfirmed.

## 3. Values with only two checks

165 values are at 2 of 3 (`verification_<code>.csv`, `status_note`). Missing check 3 (no second place): CR 28, DR 18, ECU 29, GUA 42, HON 19, JAM 17. Missing check 2: DR 10 (the BAU-by-gas hub error), HON 1, JAM 1. 108 of the 442 value rows of `scenario_values.csv` have status `2 of 3`; 334 have `3 of 3`.

## 4. Shares that are not the same kind as the model's

- Every fleet share (Costa Rica 14 NDC and LTS rows, Honduras electric and hybrid shares, Jamaica private and public fleet shares, Ecuador freight and passenger shares, Guatemala Transmetro, Dominican Republic taxis): stock shares against the model's output shares. Needed: vehicle stock by technology and distance per vehicle.
- Blend shares: volume shares; the Costa Rica model's `BLEND_GSL` gives no readable share (see 5), and the other models have no ethanol fuel.
- Electricity share of final use (Honduras +3 and +5 points), renewable share of primary energy (Jamaica 20 percent), EV share of electricity demand (Jamaica 3 percent): no model quantity computed.
- Ecuador SNI shares against the model's all-plant shares (denominator not defined in the PLANMICC).
- Guatemala NDC 2.0 "clean" share (GUA-T042, superseded NDC) against the model's renewable share: `partly`.
- T&D losses: `not computed` (solved results report outputs only).

## 5. Known-limitation candidates

- `CostaRica/CR_ENERGY/t1_confection/B1_Output_Params/NDCNEW/InputActivityRatio.csv`, `BLEND_GSL`: input ratio 1.0 for `E1_PURGSL` and 1.0 for `E1_ETA` per unit of `E1_GSL` in 2030 and 2035; output ratio 1.0. A blend that takes two units of input per unit of output does not conserve energy; solved 2030 NDCNEW: `PROETA` 40.93 PJ of ethanol for 40.93 PJ of blend.
- Costa Rica model: no distributed solar capacity in any scenario (`TotalCapacityAnnual`, 0 MW) against NDC 3.0 targets of 250 and 300 MW (CR-T042, CR-T043); no storage technology (0 MW) against 15 MW (CR-T044).
- Costa Rica model: no single energy CO2e label (`CO2e_PWR`, `CO2e_TRN`, `CO2e_DE` only), so energy emission targets cannot be compared without summing labels.
- Ecuador renewable shares in the model reach 0.990 in LTSNEW 2050 while the PLANMICC phase II gives non-conventional 35 percent and hydro 54 percent (89 percent together) in 2050 (ECU-03 p.104).
- Guatemala NDC 3.0 target of 80 percent renewable generation in 2035 (GUA-01 p.40, p.102) against the controller value 0.75 for NDCNEW 2035 (`stage1_share_analyzer_v16.py` lines 97 to 110, `stage2_apply_v2.py` lines 61 to 75).
- Jamaica NDC 3.0 50 percent renewables of net generation in 2030 (JAM-01 p.14) against the model's 0.391 in NDCNEW 2030; the controller target applies from 2035.
- Dominican Republic model solar PV capacity 9,421 MW in NDCNEW 2035 and 16,325 MW in 2050 against an NDC 3.0 measure of 1,267.15 MW of new solar parks to 2030 (DR-T014).
- Honduras model natural gas capacity 0 MW in NDCNEW 2030 against 250 MW in 2029 in the PIEG (HON-T095); coal 0 MW against 105 MW in 2029 (HON-T096).
- Script constant scan: `stage3_apply.py` line 731 logs a message containing an en or em dash; quoted repository text in `script_constants.csv` had the dash replaced by a hyphen so that the job files carry none.
- `models_energy_RE_generation_costs_update/` holds 2,934 of the 11,170 rows of `script_constants.csv`; it duplicates the energy models and is not used by Stage 0 to 3.

## 6. What was left unchecked

- Second places found by text search were accepted by rule without opening each page.
- The 174 values whose check 3 is an identity (CR 0, DR 5, ECU 22, GUA 15, HON 132, JAM 0) rely on the identity search over the checked values; the identities were not reread on the page.
- The analyses values were checked against the page text (hub script) and five by the hub on the rendered page or saved HTML (`parts/analyses_hub_confirmed.csv`); they were not given three checks, and no analysis value enters `scenario_values.csv`.
- The values of documents found in step D (for example the ICE PEG 2022-2040, which NDC 3.0 relies on, and the ENME) were not added to `values_to_verify.csv`; a later job could give them three checks.
- `script_constants.csv`: the classification of each number (what it controls, target table) is automatic from its context in the code; rows were spot-checked in `stage1_share_analyzer_v16.py`, not read one by one. YAML configuration files were not scanned (they are already external to code). Whether the 30 copies of `OSeMOSYS_Model.txt` are identical was not checked.
- The `Default` count in `scenario_names.csv` includes generic uses of the word.
- No model was run.

## 7. Incidents

- The first full-text extraction with pypdf was stopped after about 35 minutes (12 of 46 documents) and redone with pdftotext in three minutes.
- The first second-place search scanned every page line by line for every value and was stopped after 10 minutes; it was rewritten with a number index (7 seconds).
- One empty shell heredoc was run by mistake (it wrote nothing); the brief forbids heredocs and none was used to write a file.
- The blind file for the Dominican Republic dropped the gas from the BAU-by-gas series (see 1.3).
- The brief allows at most two background tasks. The text extraction ran beside the first blind reader and was stopped before the second started. The first second-place search was started in the foreground while both blind readers ran; at its 10-minute limit the harness moved it to the background, so three background tasks ran at once for some minutes until it was stopped. The two research tasks ran alone later.
