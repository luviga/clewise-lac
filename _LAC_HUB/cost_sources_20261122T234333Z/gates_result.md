# Gate results

## Gate 0. Coverage

Cells 8983, proposal rows 8983, duplicates 0, cells without a proposal 0, proposals without a cell 0, current values differing from the cell list 0.

## Gate 1. Read-only

`git diff --name-only b51f24b HEAD`: 101 files, 0 outside the job folder. `git status --porcelain` lines outside the job folder: 0.

## Gate 2. Current values

100 of 100 random proposal rows (seed 20261122) match the workbook or compiled file at b51f24b.

## Gate 3. Sources

Non-assumption rows whose source ids are missing from the sources files: 0 ([]). Sources whose downloaded file is missing: 0 ([]).

Value checks (10 per country, seed 20261122, one per distinct source value): 10 of 60 found by text search in the downloaded file; the rest are listed in `gate3_value_checks.csv` for a reading check.

## Gate 4. No internal citation

Hits: 0.

## Gate 5. Currency

Converted rows 6018; rows with a missing year or factor, or a factor that differs from `cpi_u.csv` (GEN-001): 0.

## Gate 6. Commit hygiene

Co-Authored-By or Generated-with lines in the branch log: 0. `git diff --check b51f24b HEAD` lines: 0. Output files with an em dash: 0 [].

## Result

All gates pass.
