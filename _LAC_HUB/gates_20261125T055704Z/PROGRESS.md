# PROGRESS of LAC_INPUT_GATES (stamp 20261125T055704Z)

Clone of the repository, branch `job/gates` from `origin/main`. Start check: tree of `origin/main` equals the tree
the brief names.

| Step | State | Note |
|---|---|---|
| Setup | done | job folder, brief, scripts and machine.json copied (machine.json excluded from git) |
| 0 Tests | done | test_ao_safe_save.py and test_ao_cost_repair_manager.py pass with TMP set to the temporary folder |
| 1.1 Model table | done | config/gates/models.csv, 24 rows, four model file versions as the brief states |
| 1.2 Check-mode wrapper | done | scripts/glpsol_wrap.py with GLPSOL_CHECK=1; writes a stub output so runners that loop on the solution file stop |
| 2.1 Compile | done | 24 models, 80 data files written and translated, no T0 |
| 2.2 Tracked changes | done | side files restored by the drivers; nothing outside A2/B1_Output_Params changed except the two compiler fixes |
| 2.3 Stage 3 build | done | scripts/stage3_build.py: scenario_rules.py, stage3_apply.py, tracked caps, 18 FINAL files translated |
| 3 Stale | done | RD_AFOLU and ECU_USCUSS compilers fixed and recompiled; 80 stale files kept, 37 row-order files restored; stale_compiled.csv |
| 4 Suite | done | gates/ package, config/gates/{models,checks,thresholds}.csv |
| 5 Tests | done | test_gates.py, 33 tests pass in about 2 s |
| 6 Replay | done | 11 defects put back, all flagged; Honduras control case not flagged; replay_check.csv |
| 7 Run on main | done | scripts/run_main.py: gate_results.csv, gate_summary.csv, provenance.csv, run_times.json |
| 8 Protocol | done | FEASIBILITY_PROTOCOL.md and three lines in PIPELINE_WORKFLOW.md |
| 9 Gates | done | see REPORT section 11 |
| 10 Pull request | see REPORT | three commits, draft pull request, temporary folder deleted |
