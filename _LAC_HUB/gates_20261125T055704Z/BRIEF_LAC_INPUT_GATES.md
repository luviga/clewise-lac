# BRIEF LAC_INPUT_GATES: feasibility checks for every compiled model input, built, proven on known defects and run on main, with no solve

Repository: https://github.com/luviga/clewise-lac, `main` at `b3ec008` (#19 on #18). No open pull request.

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, record it, finish every step you still can, and write the three output files anyway. Never mark the pull request ready and never merge. This is a long run (estimate 6 to 10 hours); keep `PROGRESS.md` current after every step so a restart of this brief resumes from the last finished step.

## 1. Goal

Luis decided on 24 November 2026 that input defects are found by checks, before any solve. Until now each defect cost a full run: LAC_ALIGN made seven runs (align1 to align7) and five of them stopped on input defects that the data files already showed. This job builds a check suite that reads the exact data files the solver reads and reports, by model, scenario, parameter, technology, fuel and year, every place where the limits cannot hold together or the technology chain is broken. The suite is proven on the known defects, run once on main, and written up as a protocol. After this job, every later job (energy fixes, sector jobs, Stage 4 inputs, the OSTRAM layout) changes inputs until the suite passes, and the full chain is solved once at the end.

This job solves nothing. `glpsol --check` (translation of model and data, no solve) is allowed and used as a check. Model inputs (workbooks, `inputs/`, `config/scenarios/`, model files) do not change, with one exception in step 3: compiled files that no longer match their own workbooks are regenerated.

## 2. The standard

- The models run only on externally sourced values, values a rule computes every run from sourced inputs, and labelled ASSUMPTIONs. This job writes no model value.
- No value of the system lives in a script. The check suite holds rules only. Every tolerance, threshold, list of models, scenario name, emission label or year boundary it uses goes in a table under `config/gates/`, with one plain sentence per row saying what it is for. Code reads the model list, the scenario list of each model and the history cut-off year from those tables or from the model's own configuration, never from literals.
- Model files hold structure only. No `OSeMOSYS_Model.txt` (24 copies) changes in this job.
- Rules in force (Luis, 21 November): no input differs between BAU and a policy scenario unless it is a policy measure; history (years up to 2024) is identical in every scenario; published targets are held after their last stated year; LTS equals NDC through 2035.
- Writing: plain English, no em dashes, in every file you write. Commits and the pull request carry no "Co-Authored-By" line and no "Generated with Claude Code" line. Check `git log -1 --format=%B` after each commit and amend if such a line appears. REPORT, GAPS and CHANGES name pull requests by number and do not quote commit hashes.

Scope is frozen. Do only what section 5 lists. A defect the suite finds in a model input is reported, never fixed, except the stale compiled files of step 3. A new finding outside these steps goes to GAPS under "Known-limitation candidates".

## 3. Facts already checked by values (hub 18, at `b3ec008`)

- `main`'s tree is `966d7bd0880ce986166a2e62c272c982ca7e86af`, the reviewed tree of #19.
- There are 24 `OSeMOSYS_Model.txt` files in four content versions (CR_ENERGY, CR_AFOLU, HON_ENERGY, HON_AFOLU, JAM_TRANSPORT share one; the WASTE models of CR, DR, GUA, HON share one; GUA_ENERGY has its own; the other 11 share one). All four declare the same 94 constraints, the standard OSeMOSYS set with storage, reserve margin, renewable target and emission limits.
- Constraint semantics you must reproduce in the checks (read from the model files):
  - Energy balance per time slice and per year is an inequality: production is at least demand plus use (`EBa11_EnergyBalanceEachTS5`, `EBb4_EnergyBalanceEachYear4`). Oversupply is allowed; shortage is infeasible.
  - `CAa4_Constraint_Capacity`: rate of activity in each time slice is at most capacity times `CapacityFactor` times `CapacityToActivityUnit`. `CAb1_PlannedMaintenance`: yearly activity is at most capacity times the year-split-weighted capacity factor times `AvailabilityFactor` times `CapacityToActivityUnit`.
  - Capacity is residual capacity plus new capacity still within `OperationalLife` (`CAa1`, `CAa2`).
  - `TCC1` (max capacity), `NCC1` (max new capacity) and `AAC2` (activity upper limit) apply to every technology and year, so the default value declared in the data file matters. `TCC2`, `NCC2`, `AAC3`, `TAC2` and `TAC3` apply only where the value is above 0.
  - `E8_AnnualEmissionsLimit`: annual emissions plus exogenous emissions at most the limit. `RE4_EnergyConstraint`: `REMinProductionTarget` times production of tagged fuels at most production of tagged technologies.
- Data files: the B1 runner of each model writes `Executables/<scenario>_0/<scenario>_0.txt` (GMPL data, with `default` values declared per parameter). Stage 0 copies them to `<scenario>_S0_0`; `stage3_apply.py` copies them to `Executables/<scenario>_FINAL_0/<scenario>_FINAL_0.txt` and patches them (lines 584 to 610 and 785 onward). `stage3_emission_cap.py` writes `AnnualEmissionLimit` into the capped scenario's FINAL data file from `_STAGE3_RESULTS/EMISSION_CAPS.csv` (tracked; for example Dominican LTS 2036 cap 35.297545 Mt CO2e, r 0.56, 2050 cap 23.496176). `Executables/` is gitignored.
- Run harness: LAC_ALIGN's scripts in `_LAC_HUB/align_20261124T021708Z/scripts/` (`b1_driver.py`, `full_run.py`, `glpsol_wrap.py`, `sector_run.py`, `sector_solve.py`, `stage_runner.py`, `machine.py`, `dat_compare.py`, `keyed_compare.py`). `b1_driver.py` puts a `glpsol` wrapper first on the path so every solver call goes through it. In align6, A2 and B1 of the six energy models with their `_0` solves took 1,902 s, Stage 0 1,856 s, Stage 3 1,849 s. `machine.json` (paths of the Anaconda Python and `glpsol.exe`) is at `C:\clw_machine\machine.json`.
- Defects present on main that the suite must find (checked in the tracked compiled files):
  - RD_AFOLU BAU compiled costs and penalties are stale: VariableCost of IMPRIC in 2030 is 1,445.56 in `B1_Output_Params/BAU` (the value before #19) and 743.63 in `NDCcond` (the value #19 wrote); IMPCARBOV 3,810.56 against 10,995.21. `A2_Output_Params/BAU` was not regenerated by #19 while the four policy folders were. BAU keeps 231 non-zero EmissionsPenalty values; LTS and LTSNZ keep 396 each.
  - ECU_USCUSS: `B1_Output_Params/NDC` and `NDCCON` keep 30 non-zero EmissionsPenalty values each; BAU and NDCINC have none. Every EmissionsPenalty in the 18 energy scenario folders is 0.
  - RD_AFOLU: residual capacity above maximum capacity for TRAUTELE (2018 to 2027) and TRMOTELE (2018 to 2025), from its own Tech_Adoption rows; its BAU, NDCcond and NDCincond solves are infeasible (#19 REPORT).
  - Honduras energy, `B1_Scenario_Config.xlsx` sheet `Tech_Adoption`: in NDC and LTS, all nine electric classes (TRAUTELE, TRTAXELE, TRMOTELE, TRSUVELE, TRBPUELE, TRBTURELE, TRMBSELE, TRYTKELE, TRYLFELE) carry 0.03 in 2030, 0.075 in 2040 and 0.075 in 2050 with `Restriction_Type` Min/Max, so the published 2035 share (HON-T027) acts as a ceiling to 2050.
  - Cost cells where BAU is 0 and a policy scenario has a value (same technology and year), unchanged by #19: CR_IPPU 198 per policy scenario, RD_IPPU 100, ECU_IPPU 150 and 175, GUA_IPPU 100, 52 and 100, HON_IPPU 185, HON_WASTE 50, ECU_WASTE 50, HON_AFOLU 30 and 30, RD_AFOLU 25 to 78.
- Results of #19 (tracked, `_LAC_HUB/align_20261124T021708Z/results_summary.csv`): LTS energy emissions fall in one year from 36,112 to 23,932 kt (Dominican, 2035 to 2036) and from 12,630 to 10,009 kt (Honduras). Solved history differs across scenarios although inputs are identical: Ecuador energy emissions up to 87 kt and renewable share up to 0.66 points in 2021 to 2024; Costa Rica 15 kt in 2023 and 2024.
- Defects LAC_ALIGN met and fixed on its branch, with before and after values in its job folder (`work/register_*_write_log.csv`, `work/register_distance_revert*.csv`, `work/register_policy_history_cr*.csv`, REPORT tables): Dominican PPICEFOI BAU TotalAnnualMaxCapacity 2023 and 2024 at 0.583419 and 0.472 GW against its history generation lower limit; Ecuador maximum capacity rows 0.1 MW below residual capacity plus committed builds; Ecuador NDC PPHDAMPS second maximum capacity row; four vehicle distances that rescaled transport demand and left Guatemala NDC and LTS infeasible; Costa Rica and Dominican policy plant limits below history capacity; JAM_TRANSPORT scenarios sharing one input folder after the rename; Honduras LTS infeasible at r 0.47 with the vehicle ceilings above; Ecuador capacity-based target computing a share of 1.35 before it was capped at 1.0. Forced hydrogen with no supply was the hub 15 case (Guatemala TRYTKHYD 0.0101, TRBPUHYD 0.0032, TRBPRHYD 0.0027 PJ in 2050 from 2040; PPPVT2's only output E7ELE feeds only HYD_G_PROD).

## 4. Setup

- Environment: the Anaconda Python the pipeline uses (read its path from `C:\clw_machine\machine.json`). Run your own scripts with `-I`. Excel must be closed before any compile that touches workbooks.
- New clone `C:\clw_gates` from GitHub: `git clone https://github.com/luviga/clewise-lac.git C:\clw_gates`, then branch `job/gates` from `origin/main`. Start check: `git rev-parse origin/main^{tree}` equals `966d7bd0880ce986166a2e62c272c982ca7e86af`. If it differs, record the new head in REPORT, read `git log b3ec008..origin/main`, and continue only if those commits touch nothing this brief edits.
- Temporary files in `C:\clw_gates_tmp`. Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Job folder: `C:\clw_gates\_LAC_HUB\gates_<stamp>\`. Copy this brief into it. Copy LAC_ALIGN's scripts into `gates_<stamp>\scripts\` and `C:\clw_machine\machine.json` beside them (add it to `.git/info/exclude`).
- Write only inside `C:\clw_gates` and `C:\clw_gates_tmp`.
- Read-only, never write: `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5` (except reading this brief), `C:\clw_machine`, `C:\clw_scout`, `C:\clw_scout_ostram`, `C:\clw_scout_venv`, `C:\clw_fix` if it exists, `C:\Users\luisfernando\Desktop\OSeMOSYS\LAC_sources_archive\`.
- At most three background tasks at a time.

## 5. Work

### Step 0. Tests
Run `test_ao_safe_save.py` and `test_ao_cost_repair_manager.py` once with the temporary folder set to `C:\clw_gates_tmp`. Both must pass.

### Step 1. Model table and a no-solve wrapper
1. Write `config/gates/models.csv`: one row per `OSeMOSYS_Model.txt` (24), with model path, kind (energy, transport, sector), the runner that compiles it, the scenario list as the model's own configuration defines it, and whether the pipeline's Stage 3 patches it. Discover rows from the tree; if a model folder without a model file holds compiled inputs (for example GUA_AFOLU), list it in GAPS.
2. Write a check mode for the `glpsol` wrapper: it runs `glpsol --check -m <model> -d <data>` (translation only, no solve), logs status, rows, columns and run time per data file to `check_log.jsonl`, and exits with glpsol's return code. A translation error is a check failure (`T0`).

### Step 2. Compile everything, no solve
1. Run every model's own A2 and B1 compile with the wrapper in check mode, so that every `Executables/<scenario>_0/<scenario>_0.txt` is written and translated and nothing is solved. If a runner stops after its solver call because no solution file exists, let it stop there; the data files are already written. Record per model and scenario: data file written, translation status, time.
2. After the compile, list every tracked file the compile changed. Workbooks, `SelectedResults.csv` files and anything outside `A2_Output_Params` and `B1_Output_Params` are restored with `git checkout --`; changes inside those two folders go to step 3.
3. Build the Stage 3 data files without solving: run `stage3_apply.py` on the compiled `_0` folders with the tracked Stage 2 controller (`_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx`), then write the tracked caps of `_STAGE3_RESULTS/EMISSION_CAPS.csv` into the capped FINAL data files by calling the pipeline's own writing function (import it; do not rewrite it). Translate every FINAL data file with the wrapper in check mode. If `stage3_apply.py` needs a Stage 0 output that only a solve produces, record which one, use the tracked copy under `_STAGE0_OUTPUT/` where one exists, and list the rest in GAPS.

### Step 3. Stale compiled files
1. Compare every regenerated `A2_Output_Params` and `B1_Output_Params` file with its tracked copy, keyed by all index columns. Each difference is either staleness (the tracked file no longer matches its own workbook) or compiler nondeterminism (row order, formatting, float noise below 1e-9).
2. Find why a compiled folder went stale (example: RD_AFOLU `A2_Output_Params/BAU`, ECU_USCUSS `B1_Output_Params/NDC` and `NDCCON`). If the cause is in compile code (a scenario the compiler skips, or a tracked copy read in place of a regenerated one), fix the code, recompile, and confirm the compiled files then match their workbooks.
3. Commit the regenerated compiled files whose differences are staleness, and nothing else. Record each in `stale_compiled.csv` (model, scenario, parameter, cells changed, example cell with before and after, the cause). Nondeterministic differences are not committed.

### Step 4. The check suite
Write it as a tracked package `gates/` at the repository root, run as `py -I -m gates --point <b1|final|results> [--models ...] [--scenarios ...]`. It parses the GMPL data files themselves (the solver's input, with declared defaults), and at the `b1` point confirms the parsed values equal `B1_Output_Params` for every parameter. Every check has an id, a class and a row in `config/gates/checks.csv` (id, layer, class, what it proves, the constraint names it relies on). Tolerances and thresholds sit in `config/gates/thresholds.csv`.

Two classes. FAIL means the data provably cannot be solved: the check uses only valid bounds (each bound it computes is one the solver's constraints imply), so a FAIL is never a false alarm. WARN means suspicious and worth a look (a dead end, a missing resource limit, a one-year jump). Multi-mode technologies are treated conservatively: for a requirement take the smallest ratio over modes, for an availability the largest, so the FAIL class stays sound.

Layer S, structure and connectivity (graph technology to fuel to technology from `InputActivityRatio` and `OutputActivityRatio`):
- `S1` every fuel with `SpecifiedAnnualDemand` or `AccumulatedAnnualDemand` above 0 is reachable from a technology with no input fuel (FAIL).
- `S2` every fuel a technology takes as input has at least one producer (FAIL when the consumer is forced by a lower limit or minimum capacity, WARN otherwise).
- `S3` a fuel produced but neither demanded, used, tagged for renewables nor tagged for reserve margin (WARN).
- `S4` a forced technology (activity lower limit, minimum capacity or minimum investment above 0) whose whole supply chain upstream has maximum activity 0 in that year (FAIL); the Guatemala hydrogen case is the example.
- `S5` duplicate keys in a parameter block, or a value for an element missing from its set (FAIL).
- `S6` every technology has `OperationalLife` and `CapacityToActivityUnit`; `CapacityFactor` and `AvailabilityFactor` in [0, 1]; `YearSplit` sums to 1 per year and `SpecifiedDemandProfile` to 1 per fuel and year within tolerance (FAIL).
- `S7` each scenario a runner lists has its own compiled folder and data file (FAIL; the JAM_TRANSPORT rename case).

Layer B, pairs of limits, per technology and year:
- `B1` minimum capacity at most maximum capacity; `B2` minimum investment at most maximum investment; `B3` activity lower limit at most activity upper limit; `B4` model period lower limit at most model period upper limit, and the sum of annual lower limits at most the model period upper limit (all FAIL).
- `B5` residual capacity at most maximum capacity (FAIL; the RD_AFOLU case).
- `B6` residual capacity plus minimum investments still within their operational life at most maximum capacity (FAIL; the Ecuador 0.1 MW case).
- `B7` minimum capacity at most residual capacity plus the maximum investments still within their life (FAIL).
- `B8` activity lower limit at most the largest activity capacity allows: maximum reachable capacity (the smaller of maximum capacity and residual plus reachable investments) times the year-split-weighted capacity factor times availability times `CapacityToActivityUnit` (FAIL; the Dominican PPICEFOI and the Costa Rica and Dominican policy-limit cases).

Layer P, limits pushed along the chain, per year and, for fuels with a demand profile, per time slice. For each technology compute the smallest and largest activity its own limits allow; for each fuel, the least it must supply (demand plus the users' least activity times their smallest input ratio) and the most it can get (producers' largest activity times their largest output ratio). Tighten in both directions until nothing changes: a producer's largest activity is limited by what its input fuels can deliver; when a fuel must be supplied and every producer but one is at its largest, the last producer's least activity rises to cover the rest.
- `P1` a fuel whose least requirement exceeds its most supply, in a year or a time slice (FAIL). Fuels with storage linked to them are checked per year only and get a WARN per time slice.
- `P2` an emission label with an `AnnualEmissionLimit`: the least emissions the tightened activities allow (least activity times the smallest positive emission ratio over modes, plus exogenous emissions) exceed the limit (FAIL; the Honduras LTS case at r 0.47).
- `P3` `REMinProductionTarget`: the largest tagged production cannot reach the target share of the least tagged-fuel production (FAIL).
- `P4` reserve margin: the largest capacity of tagged technologies cannot cover the margin on the least production rate of tagged fuels in some time slice (FAIL).

Layer R, the standard and nothing invisible:
- `R1` every value in the value registers of the merged job folders (`_LAC_HUB/*/value_register.csv` and the registers they point to) appears in the compiled file of every scenario that should carry it (FAIL; the stale RD_AFOLU and ECU_USCUSS cases).
- `R2` every EmissionsPenalty is 0, except models listed in `config/gates/thresholds.csv` with the reason (FAIL).
- `R3` every rule output read by the pipeline (Stage 1 targets in `_STAGE1_OUTPUT/RENEWABLE_TARGETS.csv`, shares in the controllers) lies in [0, 1] (FAIL; the Ecuador 1.35 case).
- `R4` inputs for years up to the history cut-off identical across a model's scenarios (FAIL).
- `R5` an input that differs between BAU and a policy scenario has a row in `scenario_difference_register.csv` of the latest merged job (FAIL); this covers the cost cells listed in section 3.
- `R6` a published target (a row of `inputs/scenarios/scenario_values.csv`, `published_values_loaded.csv` or a transport or power input mapped to a source id) is written only as a minimum; a maximum built from it is a FAIL (the Honduras vehicle case). Where the mapping from a target to the rows it creates cannot be traced, report it in GAPS.
- `R7` traceability: for every value of a limit parameter (maximum and minimum capacity, investment limits, activity limits, model period limits, `ResidualCapacity`, `AnnualEmissionLimit`, `REMinProductionTarget`) different from its default, name its origin: a workbook cell, a rule of the stage scripts with its rule name, or a register row. Write `provenance.csv`; values with no origin are listed as UNTRACED (WARN in this job; the class becomes FAIL once the fix jobs have traced everything).
- `R8` a technology with no input fuel and no limit on activity or capacity, and zero capital and variable cost (WARN; the Dominican biomass case).

Layer X, results, run at the `results` point on a solved run's extracted results (`results_summary.csv` format):
- `X1` year-to-year change above the thresholds of `thresholds.csv` in energy emissions, generation by technology or capacity (WARN; the 2036 drop).
- `X2` each loaded target met within tolerance (FAIL).
- `X3` results for history years identical across scenarios within tolerance (WARN; the Ecuador case).

The suite writes `gate_results.csv` (check id, class, model, scenario, point, parameter, technology, fuel, emission, year, time slice, the values compared, message) and `gate_summary.csv` (counts by check, class and model), and exits with a non-zero code when any FAIL is found. Target run time for the `b1` and `final` points over all models: under 15 minutes. Record the real time.

### Step 5. Tests for the suite
Write `test_gates.py` at the repository root (same style as the existing `test_*.py`). For every check, build a tiny synthetic data file in a temporary folder with one case that must be flagged and one that must pass. The whole file runs in under one minute without the models.

### Step 6. Replay of the known defects
On copies of the compiled data files in `C:\clw_gates_tmp`, put back each defect of section 3 that main no longer carries (use the before values of LAC_ALIGN's write logs), run the suite, and record in `replay_check.csv` (defect, model, scenario, how it was put back, expected check, flagged yes or no, the line of `gate_results.csv`). For Honduras, write the 2036 to 2050 cap at r 0.47 into the LTS FINAL data file (straight line from the solved NDC 2035 level to 0.53 times the solved BAU 2050 level, both from `results_summary.csv`) with the vehicle ceilings in place, and a second time with every published vehicle share as a minimum only. For the defects still on main (RD_AFOLU, ECU_USCUSS, the Honduras ceilings, the cost cells), the run of step 7 is the proof. For the results checks, run `--point results` on the tracked #19 results. A defect the suite does not flag is a finding: improve the check until it flags it, or, if no sound bound can show it, write in REPORT which interaction of limits only a solve can reveal.

### Step 7. Run on main
Run the suite at the `b1` and `final` points over every model and scenario of the compiled main (after the stale files of step 3 are regenerated), and at the `results` point on the #19 results. Report every FAIL and WARN in `gate_results.csv`, summarised in REPORT by check and model, with the first few lines of each kind. Fix nothing.

### Step 8. Protocol
Write `FEASIBILITY_PROTOCOL.md` at the repository root, in plain English: the three points where the suite runs (after compile, after Stage 3 apply and the cap, after results extraction); what each check proves and on which constraint it rests; how to read a FAIL and fix it in the data, never in the model; what to do when a solve still fails with every check passing (bisect by released blocks with `bisect_blocks.py`, then add the check that would have caught it); and that UNTRACED values are traced before a final run. Add three lines to `PIPELINE_WORKFLOW.md` naming the three points and the command.

### Step 9. Gates of this job
1. Tracked changes only in: `gates/`, `config/gates/`, `test_gates.py`, `FEASIBILITY_PROTOCOL.md`, `PIPELINE_WORKFLOW.md`, the stale compiled files of step 3 with any compile-code fix that step needed, and the job folder. Any other tracked change is restored.
2. `test_gates.py` passes, `test_ao_safe_save.py` and `test_ao_cost_repair_manager.py` pass, `git diff --check` is clean, and no em dash appears in any file you wrote.
3. Every data file of every model and scenario was translated by `glpsol --check`, at the `_0` and FINAL points.
4. No `OSeMOSYS_Model.txt`, workbook, `inputs/` or `config/scenarios/` file changed.

### Step 10. Pull request and clean-up
- Commit 1: `gates/`, `config/gates/`, `test_gates.py`. Commit 2: regenerated stale compiled files and any compile-code fix. Commit 3: `FEASIBILITY_PROTOCOL.md`, `PIPELINE_WORKFLOW.md` and the job folder.
- Push and open one draft pull request titled "LAC_INPUT_GATES: feasibility checks for every compiled input, proven on known defects, run on main", body taken from CHANGES.
- Delete `C:\clw_gates_tmp`. Leave `C:\clw_gates` in place for the merge.

## 6. Outputs

All three in `C:\clw_gates\_LAC_HUB\gates_<stamp>\`, plain English, no em dashes. Also in that folder: `check_log.jsonl`, `stale_compiled.csv`, `gate_results.csv`, `gate_summary.csv`, `provenance.csv`, `replay_check.csv`, `PROGRESS.md`.

`REPORT_LAC_INPUT_GATES_<stamp>.md`: pull request number; the check catalogue with one line per check; compile and translation results per model and scenario; the stale files found and their cause; the replay table (flagged or not, and why); the run on main summarised by check and model; the share of limit values traced; run times (compile, Stage 3 apply, each check point); which kinds of infeasibility only a solve can reveal.

`GAPS_LAC_INPUT_GATES_<stamp>.md`: every judgement call and its reason; "Known-limitation candidates"; anything left unchecked; incidents.

`CHANGES_LAC_INPUT_GATES_<stamp>.md`: file by file, what changed and why, in two or three lines each.

Tracked files follow the repository's writing rules: no machine paths, no figures from model results outside the job folder, no hash values.
