# GAPS LAC_REPO_SETUP 20261109T065948Z

## Judgement calls

1. **Oversized file excluded by path, not by folder.** The only file over 50 MB is `models_energy_RE_generation_costs_update/HON_ENERGY/Executables/NDCcond_0/NDCcond_0_output.txt` (212,339,781 bytes). Its folder also holds the scenario input `NDCcond_0.txt`, so at Step 2 the narrowest pattern was the file path. The later `Executables/` rule (call 3) covers it too; the path line stays as a record of the size rule.
2. **"2 GB" read as 2,000,000,000 bytes.** The first dry run totalled 2,457,423,765 bytes (2.29 GiB), over the limit under either reading. I used the stricter decimal limit so the gate holds whichever reading is meant. The final total is 1,994,869,006 bytes.
3. **One `Executables/` pattern instead of a folder-by-folder list.** Reaching 2,000,000,000 bytes meant dropping 457.4 MB, and all tracked `Executables` content together was 462.6 MB. Taking folders largest first would have excluded all but the few smallest. A single pattern is simpler and matches the brief's description of these folders as regenerated output: B1 writes the scenario `.txt` and `_Input.csv` into them, the solver writes `_output.txt` and `_Output.csv`, and the B2 results creators write `local_dataset_creator_0.py` and the dataset CSVs. The 30 folders now excluded, with the total working-copy size of each:

   | Folder | MB | Files |
   |---|---|---|
   | `models_energy_RE_generation_costs_update/HON_ENERGY/Executables/` | 241.6 | 18 |
   | `DominicanRepublic/RD_AFOLU/Executables/` | 58.6 | 18 |
   | `models_energy_RE_generation_costs_update/ECU_Energy/Executables/` | 37.5 | 23 |
   | `models_energy_RE_generation_costs_update/RD_ENERGY/Executables/` | 34.7 | 24 |
   | `Ecuador/ECU_USCUSS/Executables/` | 30.9 | 15 |
   | `Ecuador/ECU_Energy/Executables/` | 29.6 | 28 |
   | `models_energy_RE_generation_costs_update/CR_ENERGY/t1_confection/Executables/` | 26.2 | 17 |
   | `CostaRica/CR_AFOLU/t1_confection/Executables/` | 25.9 | 15 |
   | `Honduras/HON_AFOLU/HON_AFOLU/Executables/` | 24.4 | 13 |
   | `Ecuador/ECU_AGR/Executables/` | 21.0 | 18 |
   | `Guatemala/GUA_WASTE/Executables/` | 15.8 | 15 |
   | `models_energy_RE_generation_costs_update/JAM_ENERGY/Executables/` | 15.7 | 14 |
   | `models_energy_RE_generation_costs_update/GUA_ENERGY/Executables/` | 15.3 | 18 |
   | `CostaRica/CR_WASTE/Executables/` | 13.0 | 15 |
   | `Jamaica/JAM_TRANSPORT/Executables/` | 11.5 | 12 |
   | `Jamaica/JAM_AFOLU/Executables/` | 10.3 | 12 |
   | `Honduras/HON_WASTE/Executables/` | 9.7 | 12 |
   | `CostaRica/CR_IPPU/Executables/` | 9.0 | 15 |
   | `DominicanRepublic/RD_ENERGY/Executables/` | 7.7 | 19 |
   | `Guatemala/GUA_IPPU/Executables/` | 4.6 | 15 |
   | `Ecuador/ECU_WASTE/Executables/` | 3.9 | 12 |
   | `DominicanRepublic/RD_WASTE/Executables/` | 3.8 | 12 |
   | `Honduras/HON_IPPU/Executables/` | 3.4 | 12 |
   | `Honduras/HON_ENERGY/Executables/` | 3.3 | 10 |
   | `Ecuador/ECU_IPPU/Executables/` | 3.2 | 12 |
   | `CostaRica/CR_ENERGY/t1_confection/Executables/` | 3.2 | 10 |
   | `DominicanRepublic/RD_IPPU/Executables/` | 3.1 | 12 |
   | `Jamaica/JAM_WASTE/Executables/` | 2.8 | 9 |
   | `Jamaica/JAM_ENERGY/Executables/` | 2.7 | 10 |
   | `Guatemala/GUA_ENERGY/Executables/` | 2.3 | 10 |

   The pattern also stops any future `Executables` folder from being tracked, which fits the plan of reviewing changes as pull requests against inputs, not run output.
4. **Dry run excludes the job folder.** `git add --dry-run -A` would list this job folder, which commit 2 must leave out. I ran it with the pathspec `:(exclude)_LAC_HUB/repo_setup_20261109T065948Z` so the count compares like with like against `git ls-files` after commit 2.
5. **Global git identity used as is.** Global `user.name` is `luviga` and `user.email` is `luis.fdo.victor.g@gmail.com`, so the brief's fallback (`luviga@users.noreply.github.com`) did not apply. That address will be public in the commit metadata once pushed, and GitHub may refuse the push (GH007) if Luis's email privacy setting blocks it. Commits can still be rewritten before the first push if a no-reply address is wanted.
6. **Case-insensitive `bnamericas` pattern.** Written as `*[bB][nN][aA][mM][eE][rR][iI][cC][aA][sS]*` so it works even if `core.ignorecase` is turned off later. It matched nothing today.
7. **What counted as a text file for the secret scan.** Every file of 50 MB or less that has no NUL byte in its first 8 KB and does not have a known binary extension (`.xlsx`, `.xls`, `.pdf`, `.zip`, `.pickle`, `.pyc`, `.twbx`, `.twbr`, `.msg`, `.pptx`, `.docx`, images). 9,119 files scanned, 1,557 skipped.
8. **Assignment rule written broadly.** The rule caught any `name = value` or `name: value` where the name contains `api_key`, `apikey`, `token`, `secret` or `password`, including unquoted code expressions, then each hit was reviewed. This casts a wider net than "non-empty literal" and produced more false positives, all resolved below.
9. **Strong vs weak literal hits.** For each literal (`sk-ant-`, `ghp_`, and so on) the scanner also checked for a key-shaped value (for example `AKIA` plus 16 upper-case letters or digits, `ghp_` plus 30 or more characters). There were no key-shaped matches; every literal hit was a weak substring hit, reviewed below.
10. **Commit 3 author and push.** Step 8 says push the reports if Step 6 pushed. It did not, so commit 3 is local only.

### Email-file history rewrite (Luis's follow-up instruction, before any push)

11. **Plumbing rebuild instead of `filter-branch`.** `git filter-repo` is not installed. `git filter-branch` refuses to run with an unstaged `.gitignore` edit, and at the end it checks out the rewritten tree, which would have deleted the `.msg` from disk. `rewrite_history.sh` rebuilds each commit in a temporary index (`read-tree`, `rm --cached`, `update-index`, `write-tree`, `commit-tree`), copies author, committer, dates and message from the old commit, then moves `main` with `update-ref` and refreshes only the real index (`read-tree HEAD`, no `-u`). The working tree is never written.
12. **New `.gitignore` written into every commit, including commit 1.** Commit 1 is the "ignore and attribute rules" commit, so the email patterns belong there. Adding them in a fourth commit would have left earlier commits with a `.gitignore` that does not match what they track. All three commits now carry the same `.gitignore` blob as the file on disk.
13. **Case-insensitive removal.** The removal pathspecs used `:(icase)`, so `.MSG` or `.Eml` variants would also go. Only one file matched. The `.gitignore` patterns are lower case; `core.ignorecase=true` (the Windows default set at `git init`) makes them match any case.
14. **Old objects purged, not just unreferenced.** `git reflog expire --expire=now --all` and `git gc --prune=now` ran after the rewrite and again after amending commit 3. The `.msg` blob and the old commits are no longer in `.git/`, so a later accidental `git push --mirror` or a copy of `.git/` cannot carry them.
15. **Commit 3 amended instead of adding a fourth commit.** The report updates and the rewrite script and log were folded into the reports commit, so its REPORT does not point at commit hashes that no longer exist. Its final hash is not written in REPORT, because a commit cannot contain its own hash; `git log -1` shows it.
16. **Temporary safety copy.** Before the rewrite I copied the `.msg` to the session scratchpad outside MODELS_LAC_5 as insurance. Once the on-disk file was confirmed byte-identical after the rewrite, I deleted that copy.
17. **Earlier listings left as they were.** `tracked_dry_run.txt`, `ls_files.txt`, `excluded_files.csv`, `check_ignore.txt`, `exclusion_by_pattern.csv` and `content_scan.csv` describe the state before the email rewrite and were not regenerated. `ls_files_baseline_after_rewrite.txt` and `excluded_files_after_rewrite.csv` give the current baseline (9,670 tracked, 1,008 excluded). These earlier files still mention the `.msg` path name as text; they do not contain the message.

### Third-party document rewrite (Luis's second follow-up instruction, before any push)

18. **Exact paths, not extension patterns.** As instructed, `.gitignore` lists the eight files by exact path, each anchored with a leading `/`. No `*.pdf` or `*.pptx` rule was added outside `_LAC_HUB/`, so a new PDF or deck elsewhere would still be tracked if added later. The path with spaces, a full stop and a comma (`Anexo 4. Monitoreo de emisiones, RC y productividad-1.pdf`) needs no escaping in `.gitignore`; `git check-ignore -v` confirmed each path matches its own line.
19. **Same method as the email rewrite.** `rewrite_history_docs.sh` repeats the temporary-index rebuild with `:(literal)` pathspecs, so the eight paths match only themselves and not as globs. It writes the new `.gitignore` into all three commits, keeps author, committer, dates and messages, and never touches the working tree. The reflog was expired and objects pruned after the rewrite and again after amending commit 3.
20. **No safety copies this time.** The method had already been shown to leave the working tree alone, so I did not copy the eight files elsewhere first. Their SHA-256 values were checked against `files_before.csv` after the rewrite: all equal.
21. **Listings regenerated only for the current baseline.** `ls_files_baseline_after_docs_rewrite.txt` and `excluded_files_after_docs_rewrite.csv` give the current state (9,662 tracked, 1,016 excluded). The email-rewrite listings and the original scan files were left as historical records; they mention the eight paths as text only.

## Content-scan hits marked "not a secret"

All 176 hits are in `content_scan.csv` with path, line, masked text and reason. Grouped:

| Hits | Where | Matched | Reason |
|---|---|---|---|
| 7 | `_LAC_HUB/BRIEF_LAC_REPO_SETUP.md` line 55 | `sk-ant-`, `ghp_`, `gho_`, `github_pat_`, `AKIA`, `xox`, `-----BEGIN` | The brief's own list of search patterns, in prose. Tracked. |
| 31 | `_LAC_HUB/price_sources_20261109T003525Z/downloads/**/*.html` | `xox` | The letters `xox` inside long base64 values (page integrity or state hashes) in downloaded web pages. Files excluded by `/_LAC_HUB/**/downloads/`. |
| 44 | same downloads folder (Jamaica news pages) | `apiKey = AIza...`, `lsvr_pressville_google_api_key = AIza...` | Third-party public browser keys for Google Maps that the news site embeds in every page. Not a credential of this project. Files excluded. |
| 6 | same downloads folder | `eael_resetpassword_nonce`, `eael_lostpassword_nonce` | WordPress form nonces in downloaded pages. Files excluded. |
| 45 | same downloads folder | `onToken = tok...` | A JavaScript callback assignment, not a literal value. Files excluded. |
| 43 | `ao_cost_repair_manager.py`, `ecuador_non_energy_cost_repair_manager.py`, `stage1_share_analyzer_v16.py`, `stage1_test_v16.py`, `stage2_apply_v2.py`, `stage2_test_v2.py`, and the backup `ao_cost_repair_manager.py.pre_20261109T053358Z` | `token_jaccard`, `target_tokens`, `HYDRO_TOKENS = ["HY...`, and similar | Text-tokenizing variables (word tokens used to match technology names) assigned from code or word lists. The backup copy is excluded by `backups/`; the rest are tracked. |

Unresolved: 0.

## Known-limitation candidates

- **No licence file.** The repository has no `LICENSE`, so once public it is "all rights reserved" by default until Luis adds one.
- **Personal paths.** 82 text files contain the user profile path (`C:\Users\luisfernando` or `/c/Users/luisfernando`), 37,354 occurrences in all; 71 of those files are tracked. None were edited. The ten with the most hits (full list in `personal_paths.csv`):

  | File | Hits |
  |---|---|
  | `_COST_REPAIR_OUTPUT/ao_cost_repair_20260511_205736/manifest.csv` | 15,900 |
  | `_COST_REPAIR_OUTPUT/ao_cost_repair_20260511_210318/manifest.csv` | 6,360 |
  | `_LAC_HUB/fuel_check_20261108T223320Z/plan_Ecuador/manifest.csv` | 6,360 |
  | `_COST_REPAIR_OUTPUT/ao_cost_repair_20260511_210318/mapping_candidates.csv` | 1,503 |
  | `_COST_REPAIR_OUTPUT/ao_cost_repair_20260511_205736/mapping_candidates.csv` | 1,497 |
  | `_LAC_HUB/fuel_check_20261108T223320Z/plan_Ecuador/mapping_candidates.csv` | 1,435 |
  | `_LAC_HUB/fuel_check_20261108T223320Z/plan_Jamaica/manifest.csv` | 630 |
  | `_LAC_HUB/fuel_check_20261108T223320Z/plan_DominicanRepublic/manifest.csv` | 528 |
  | `_LAC_HUB/fuel_check_20261108T223320Z/plan_Jamaica/no_safe_match.csv` | 437 |
  | `_LAC_HUB/fuel_check_20261108T223320Z/plan_Guatemala/manifest.csv` | 396 |

- **`Ecuador/ECU_AGR/Modelamiento sector agricultura - 20241115.msg`** (resolved): an Outlook email message (3.1 MB) holding 11 distinct email addresses from `ambiente.gob.ec`, `fao.org`, `clg-cr.com` and Outlook routing domains. On Luis's instruction it was removed from every commit and is now ignored; it stays on disk. See "History rewrite" in REPORT and calls 11 to 17 above.
- **Third-party documents outside `_LAC_HUB/`** (resolved): `Ecuador/ECU_AGR/Anexo 4. Monitoreo de emisiones, RC y productividad-1.pdf`, `Guatemala/GUA_AFOLU/RES.pdf`, and three `RSS_*.pptx` decks in `Jamaica/JAM_ENERGY/` plus their copies in `models_energy_RE_generation_costs_update/JAM_ENERGY/`. They were first tracked because the brief's document rule covers `_LAC_HUB/` only, and their licence status is unknown. On Luis's instruction all eight were removed from every commit and are now ignored by exact path; they stay on disk. See calls 18 to 21 and "History rewrite (third-party documents)" in REPORT.
- **`Honduras/HON_AFOLU/HON_AFOLU/Executables/NDP_0/checking.xlsx`**: the only file in any `Executables` folder that does not look generated (a hand-named workbook). It is now excluded by `Executables/`, so it is not in the repository.
- **Duplicate dated outputs.** `DominicanRepublic/RD_AFOLU/` tracks 24 `RDOutput*.csv` and `RDInput*.csv` files at its top level, most of them dated copies (271.5 MB together, the largest 17.5 MB), and the three `Guatemala/GUA_AFOLU/2_Model/*/data_land_output.txt` files are identical in size (32.7 MB each). This is the bulk of what keeps the repository near 2 GB.
- **`models_energy_RE_generation_costs_update/`** (949 MB in the working copy, the largest top-level folder) looks like a parallel copy of the six energy models. It is tracked except for its `Executables` folders.
- **Root `__pycache__/`** (4 files) predates this job; it is ignored, not deleted.

## Left unchecked

- Binary files were not scanned for secrets or personal paths: 1,178 tracked binary files (1,009 `.xlsx`, 136 `.pickle`, 21 `.twbx`, 6 `.pptx`, 3 `.twbr`, 2 `.pdf`, 1 `.msg`). A secret typed into a workbook cell would not have been found.
- Step 7.2 (fresh clone and hash comparison) did not run, because nothing was pushed.
- Byte-for-byte equality of the stored blobs with the working files was not checked separately before the push. It relies on `* -text`, and Step 7.2 would confirm it.
- Whether a private repository named `clewise-lac` exists under another owner or name was not checked; `gh repo view luviga/clewise-lac` reported none under `luviga`.
- The `bnamericas` rule matched nothing. Licensed material under other names was not searched for.

## Incidents

- **Publish refused.** `gh repo create luviga/clewise-lac --public ...` was refused by the Claude Code permission layer ("Create Public Surface") before it ran. No remote was added and no push attempted. The brief's `git push` fallback applies when `gh` is missing or logged out, which was not the case, and it would have failed against a repository that does not exist, so it was not tried.
- **CRLF in one intermediate list.** The first run of `git check-ignore --stdin` read a path list written by Python with Windows line endings, so four paths failed to match and sizes came out as zero. Rerun with LF output. All 1,007 excluded paths are now attributed.
- **Raw scan file deleted.** `content_scan_raw.csv` (created by this job) held unmasked context around the weak `xox` hits. After writing the masked and classified `content_scan.csv`, I deleted the raw file so it would not be committed.
- `git add -A` for commit 2 took about 3 minutes; no errors or warnings.
- **History rewritten after the first report.** On Luis's instruction, all three local commits were rebuilt without email files (old to new: `5d70056` to `c77a90d`, `3fcf246` to `a27e8e7`, `fb5620d` to `fc8be6a`, then commit 3 amended again with these notes). The old hashes are gone. Nothing had been pushed, so no remote copy holds them.
- **History rewritten a second time.** On Luis's second instruction, all three commits were rebuilt again without the eight third-party documents (`c77a90d` to `8002fc2`, `a27e8e7` to `6479441`, `5fd7f5b` to `a56b44c`, then commit 3 amended with these notes). The old hashes and the eight document blobs were pruned. Still nothing pushed.
