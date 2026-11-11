# CHANGES LAC_COST_REVIEW_PACK 20261111T015203Z

All files are new, in `_LAC_HUB/cost_review_20261111T015203Z/` on branch `job/cost-review` (from `2ddd560`). Nothing else in the repository was added, changed or removed.

- `BRIEF_LAC_COST_REVIEW_PACK.md`: copy of this job's brief.
- `CHANGES_LAC_COST_REVIEW_PACK_20261111T015203Z.md`: this list.
- `GAPS_LAC_COST_REVIEW_PACK_20261111T015203Z.md`: checks not run, judgement calls, known-limitation candidates, incidents.
- `REPORT_LAC_COST_REVIEW_PACK_20261111T015203Z.md`: the report the hub reads first.
- `assumptions_all.csv`: Step 7: every ASSUMPTION row with its sentence, plus non-ASSUMPTION rows carrying a sentence (marked).
- `common.py`: shared paths and loaders (read-only on everything outside this folder).
- `country_points.txt`: Step 6: raw evidence printed by step6_country_points.py.
- `cross_country.csv`: Step 4: WEO, CPI, benchmarks, conversion constants, gas conversion, exchange rates.
- `decisions_raised.csv`: Step 7: judgement calls, questions, choices and ASSUMPTIONs from the six GAPS and REPORT files.
- `derivation_recompute.csv`: Step 3: derivation expressions above 0.5 percent before hand review, with the hand review.
- `derivation_recompute_summary.csv`: Step 3: counts of derivations and projection series recomputed.
- `gates.csv`: Step 2: gates 1 to 8 per country, with counts and notes.
- `inventory.csv`: Step 1: per branch head, commits, job folder, section 4 files present.
- `paper_trace_all.csv`: Step 7: the six paper_trace.csv stacked, de-duplicated, sorted.
- `proposals_all.csv`: Step 7: the six proposals.csv stacked (17,921 rows).
- `report_text.py`: hand-written text of REPORT and GAPS.
- `review_flags.csv`: Step 5: every value outside the screens, with current value and sources.
- `step1_2_inventory_gates.py`: Step 1 inventory and Step 2 gates 1 to 8.
- `step3_values.py`: Step 3 value checks against the downloaded sources.
- `step3b_recompute.py`: Step 3 derivation recompute (arithmetic chains and the WEO projection path).
- `step3c_review_recompute.py`: Step 3 hand review of the recompute differences.
- `step3d_classify.py`: Step 3 likely cause of each value not found, read from its derivation.
- `step4_cross_country.py`: Step 4 shared inputs across the six.
- `step5_range_screen.py`: Step 5 range screen.
- `step6_country_points.py`: Step 6 evidence for the country points.
- `step7_merge.py`: Step 7 merged files.
- `step8_report.py`: writes REPORT, GAPS and CHANGES.
- `summary_all.csv`: Step 7: the six proposals_summary.csv stacked.
- `textindex.py`: text extraction of downloaded files (PDF, XLSX, XLS, HTML, DOCX, JSON, CSV, parquet) and number search.
- `value_checks.csv`: Step 3: each value searched in its downloaded sources.

Not tracked: `scratch/` (branch extracts, the six A-O copies, cached text of the downloaded files); it is left out of the commit.

Confirmation:
- No model file was changed: the clone `C:\clw_cost_review` differs from `2ddd560` only by this job folder (`git status` before the commit listed nothing else).
- No branch of the six was changed: nothing was pushed to `job/cost-src-*`. The six pull requests were not marked ready or merged.
- No file in the six job folders or in `C:\clw_cost_<cc>` was edited: they were read through `git show`, `git archive` into `scratch/`, and read-only file opens of the local `downloads/`.
- `C:\clw_local_prices` and OneDrive were read only (one PDF page of the MINAE balance; OneDrive not opened). Nothing under Dropbox was opened.
