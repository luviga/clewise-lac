# Feasibility protocol: input gates before any solve

Decided on 24 November 2026: input defects are found by checks, before any solve. The check suite `gates/` reads
the GMPL data files the solver reads (with the defaults they declare) and reports, by model, scenario, parameter,
technology, fuel, emission, year and time slice, every place where the limits cannot hold together or the
technology chain is broken. Every later job changes inputs until the suite passes, and the full chain is solved
once at the end.

## The three points

| Point | When | What is read | Command |
|---|---|---|---|
| `b1` | after the A2 compile and the B1 runners of every model | `Executables/<scenario>_0/<scenario>_0.txt` of every scenario each model's `B1_Scenario_Config.xlsx` lists; the parsed values are also compared with `B1_Output_Params/<scenario>` | `py -I gates --point b1` |
| `final` | after `scenario_rules.py`, `stage3_apply.py` and the emission cap of `stage3_emission_cap.py` | `Executables/<scenario>_FINAL_0/<scenario>_FINAL_0.txt` of the six energy models | `py -I gates --point final` |
| `results` | after results extraction of a solved run | `results_summary.csv` of the latest merged job (or `--results-file`) | `py -I gates --point results` |

Options: `--models`, `--scenarios`, `--out <folder>` (where `gate_results.csv`, `gate_summary.csv` and
`provenance.csv` go), `--data-dir <copy of the model folders>`, `--jobs <n>`. The suite exits with 1 when any FAIL is
found. Isolated mode leaves the working folder off the import path, so the package is run as a folder
(`py -I gates ...`) from the repository root; `py -m gates ...` works as well.

Translation itself is checked by the compile: the `glpsol` wrapper of the job scripts in check mode runs
`glpsol --check -m <model> -d <data>` (translation and generation, no solve) on every data file; a translation
error is check `T0`.

## Two classes

- **FAIL**: the data provably cannot be solved. A FAIL check uses only bounds the model's own constraints imply
  (listed per check in `config/gates/checks.csv`), and a violation counts only when it exceeds the solver's
  feasibility tolerance (`solver_abs_tol` in `config/gates/thresholds.csv`). A FAIL is never a false alarm.
  Rows of layer R are FAILs of the standard: the data breaks a rule in force even where the solver would accept it.
- **WARN**: suspicious and worth a look (a dead end, a free unlimited source, a one-year jump, an untraced value,
  a violation inside the solver's tolerance).

Technologies with several modes are read conservatively: a requirement takes the smallest ratio over every mode of
the mode set (0 when a mode has none), an availability the largest.

## What each check proves

Layer S (structure and connectivity), layer B (pairs of limits), layer P (limits pushed along the chain), layer R
(the standard) and layer X (results). One line per check, with the constraints it rests on, is in
`config/gates/checks.csv`; tolerances and thresholds are in `config/gates/thresholds.csv`, one sentence per row.

- S0 the data file is the compiled tables; S1 every demanded fuel is reachable from a source; S2 every input fuel
  has a producer; S3 dead-end fuels; S4 a forced technology whose input chain cannot run; S5 duplicate keys and
  unknown elements; S6 operational life, capacity-to-activity unit, factor ranges and split sums; S7 every listed
  scenario has its compiled folder and data file.
- B1 to B4 minimum against maximum (capacity, investment, activity, model period); B5 residual capacity against
  maximum capacity; B6 residual plus committed builds against maximum capacity; B7 minimum capacity against what
  residual capacity and the maximum investments can reach; B8 activity lower limit against what the reachable
  capacity allows (`CAa4`, `CAb1`).
- P1 least requirement of a fuel against the most its producers can supply, per year and per time slice, after
  tightening both ways along the chain; P2 least emissions against `AnnualEmissionLimit`; P3 the renewable target
  (`RE4`); P4 the reserve margin (`RM3`).
- R1 registered values reached the compiled files; R2 no emission penalty; R3 rule outputs in [0, 1]; R4 history
  identical across scenarios; R5 every BAU to policy difference registered; R6 published targets only as minimums;
  R7 provenance of every limit value (`provenance.csv`); R8 free unlimited sources.
- X1 one-year jumps; X2 loaded targets met; X3 solved history identical across scenarios.

## How to read a FAIL and fix it

1. Read the row of `gate_results.csv`: check, model, scenario, point, parameter, technology or fuel or emission,
   year, the two values compared and the message.
2. Find the input that writes the value: `provenance.csv` names the register row, the workbook location, the A2
   compiled table or the stage rule. A value marked UNTRACED has no origin yet.
3. Fix the data at its origin (a workbook cell, a register row, a rule's table), never the model file. Model files
   hold structure only; no `OSeMOSYS_Model.txt` changes to make data feasible.
4. Recompile and run the suite again at the same point; a fix is done when the row is gone and no new FAIL appears.
5. Every fix that changes a value goes through a register with its source, as the standard requires.

## When a solve still fails with every check passing

The checks use only bounds the constraints imply, so some infeasibilities are visible only to a solve: limits that
interact across several technologies at once (several fossil classes that can each take the whole demand while
their sum cannot stay under an emission cap), limits that link years (model period limits against investment
paths and operational lives), and storage that shifts supply between time slices. Then:

1. Bisect by released blocks with `bisect_blocks.py` (LAC_ALIGN job scripts): start from a feasible data file of
   the same model, copy the parameter blocks that differ from the infeasible file half at a time, and find the
   smallest set of blocks that makes it infeasible.
2. Write down the interaction those blocks hold, add the check that would have caught it to `gates/` with a row in
   `config/gates/checks.csv` and a flagged and a passing case in `test_gates.py`, and run the suite again.

## Traceability before a final run

Every limit value that differs from its default needs an origin. `R7` lists values with none as UNTRACED (a WARN
today). UNTRACED values are traced before a final run; once the fix jobs have traced everything, R7 becomes a FAIL.

## Tests

`py -I test_gates.py` builds, for every check, a tiny synthetic data file with one case that must be flagged and
one that must pass, and runs in a few seconds without the models.
