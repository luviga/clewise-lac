# CHANGES LAC_REPO_SETUP 20261109T065948Z

No existing file in MODELS_LAC_5 was changed, moved, renamed or deleted (`files_compare.csv`: 0 changed, 0 removed; the `.msg` file and the eight third-party documents kept their SHA-256 through both history rewrites). Nothing was pushed.

## `.git/` (new, root)
Created by `git init -b main`. Holds the local history on branch `main`. There is no remote: creating `luviga/clewise-lac` was refused in this session, see REPORT. History was rewritten twice on Luis's instruction, first to drop email files and then to drop eight third-party documents; old objects were pruned each time.

## `.gitignore` (new, root)
Excludes the one file over 50 MB, every `Executables/` folder (regenerated run output, removed to keep the total under 2 GB), downloaded and licensed documents under `_LAC_HUB/`, eight third-party documents by exact path (two PDFs, six `RSS_*.pptx`), email files (`*.msg`, `*.eml`, `*.pst`, `*.ost`), and backups, caches and archives. 1,016 files and 1,007.3 MB are excluded; no `.xlsx`, `.csv` or `.txt` file is excluded by extension.

## `.gitattributes` (new, root)
The single line `* -text`, so git stores every file byte for byte with no line-ending conversion (the `.bat` files keep CRLF, `stage0_run_all.sh` keeps LF).

## Commit `8002fc262f82fbe4baaed34a3b60816daacf9a61` `repo: ignore and attribute rules`
Adds `.gitignore` (including the email patterns and the eight document paths) and `.gitattributes` only. Replaces `5d70056`, then `c77a90d`.

## Commit `6479441e44cbc36b0e5dae9c5c5c915db25a8776` `baseline: MODELS_LAC_5 after LAC_SAFE_SAVE_FIX 20261109T053358Z`
Adds 9,660 files (9,662 tracked in total, 1,988,473,662 bytes): every non-ignored file except this job folder. Includes the six energy A-O workbooks, whose hashes match the LAC_SAFE_SAVE_FIX record. Replaces `3fcf246` (which held the Outlook `.msg` and the eight documents), then `a27e8e7` (which still held the eight documents).

## Commit `hub: LAC_REPO_SETUP 20261109T065948Z reports`
Adds this job folder: the three output files, the inventories, the scan tables, the two history-rewrite scripts and logs, and the scripts that made them. Local only; hash from `git log -1`.
