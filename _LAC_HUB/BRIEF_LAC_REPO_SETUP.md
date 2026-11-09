# BRIEF LAC_REPO_SETUP: pre-publish scan and first push of MODELS_LAC_5 to the public repository luviga/clewise-lac

Working copy: `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5` (Git Bash `/c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5`). It is not a git repository today.

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, record it, finish every step you still can, and write the three output files anyway.

## 1. Goal

Turn MODELS_LAC_5 into a git repository in place and publish it as the public GitHub repository `luviga/clewise-lac`, so the hub can clone it and check values, and every later job becomes a pull request against this baseline. Luis decided on 9 November 2026: public, permanent, on his personal account, named `clewise-lac`; he confirmed that he and his co-authors are comfortable with the model folder being public. Because a public push cannot be undone, a scan runs first and the push happens only if the scan's hard gates pass.

## 2. The standard

Do not change, move, rename or delete any existing file in MODELS_LAC_5. The only new files you create inside it are `.git/`, `.gitignore`, `.gitattributes` and your job folder `_LAC_HUB/repo_setup_<stamp>/`. Run no pipeline step, no A1, A2, B1, stage or solver script, and no writer script.

Scope is frozen. Do only what section 5 lists. Anything new you find goes to GAPS under "Known-limitation candidates", with where it is and one sentence on what it is. Do not fix it.

## 3. Facts already known

- The working copy was about 2.5 GB at the 8 November scan. Solver output `.txt` files can exceed 750 MB each.
- GitHub rejects any file over 100 MB and warns above 50 MB.
- LAC_SAFE_SAVE_FIX (stamp 20261109T053358Z) reported these SHA-256 values for the six energy A-O workbooks after its run. The job folder `_LAC_HUB/safe_save_fix_20261109T053358Z/` holds the record.
  - `Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`: `592ceda73c6df758684a8a2fea20ac152db70f44ce6a4d65888274bfada16695`
  - `Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx`: `f1fb407a78848aaf7a9cffd6d771f2f3b507f0bc105366195e89089f03f6ff68`
  - `CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Parametrization.xlsx`: `522d438ea7c27d4ceb3614267adff0503d059ecfe1a22d5d926bf7432dc9c8b7`
  - `DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`: `f396abf1b587d337040735f945d0b7b2c7b4a47bf2c11e121753d8b5b7e4af7c`
  - `Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`: `e2f9aad05f2b96c35392fb523e9bf056a9c71e067e564951b7770ac2e661e7f1`
  - `Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`: `d20f4aa8d4c55aa384a8bd0f7a6c93fd5e635427eba8e9e705651b8638b40458`
- No repository named `clewise-lac` is public on `github.com/luviga` as of 9 November. A private one may exist; check in Step 6.

## 4. Setup

- Environment: Git Bash, the Python Luis uses (`py`), and `gh` if installed. Run your own Python scripts with `py -I -B`.
- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`, and use it in the job folder name and the three output file names.
- Job folder: `_LAC_HUB/repo_setup_<stamp>/` inside MODELS_LAC_5. Put every script, list and log there.
- Write only: the job folder, `.git/`, `.gitignore`, `.gitattributes` at the MODELS_LAC_5 root.
- Never open or write: anything under `C:\Users\luisfernando\Dropbox\` (opening the online-only archive triggers downloads), `C:\Users\luisfernando\Desktop\OSeMOSYS\` outside MODELS_LAC_5, and `C:\Users\luisfernando\OneDrive - Climate Lead Group\`.

## 5. Work

### Step 1. Baseline

1. Write `files_before.csv`: every file under MODELS_LAC_5 (path relative to the root, size in bytes, SHA-256, mtime), excluding your job folder.
2. Check the six A-O hashes against section 3. Record each as MATCH or DIFFERENT in REPORT. If any is DIFFERENT, do not push (Step 6 stops at the local commit); finish the other steps.
3. List any existing `.git` folder or `.gitmodules` file anywhere under the root. If one exists, exclude that folder in `.gitignore` and record it.

### Step 2. Size scan

1. Write `size_scan.csv`: every file over 10 MB with path and size, largest first, plus a total per top-level folder and per extension.
2. Rule: no tracked file may exceed 50 MB. Every file over 50 MB goes into `.gitignore` by its narrowest pattern (a folder pattern if all files in that folder are regenerated outputs, else the file path).

### Step 3. Content scan

Write `content_scan.csv` with one row per hit: path, line (if text), rule, matched text with any secret value masked to its first 4 characters.

1. Secrets (hard gate): search every text file under 50 MB for `sk-ant-`, `ghp_`, `gho_`, `github_pat_`, `AKIA`, `xox`, `-----BEGIN`, and assignments of a non-empty literal to a name containing `api_key`, `apikey`, `token`, `secret` or `password` (any case). Also list any file named `.env`, `*.pem`, `*.key`, `credentials*`, `secrets*`. A hit that is clearly not a secret (an empty string, a variable read from the environment, a word in prose) is recorded as "not a secret" with the reason.
2. Licensed or third-party documents (exclude): any file or folder whose name contains `bnamericas` (any case); every `.pdf`, `.htm`, `.html`, `.docx`, `.doc`, `.pptx` file under `_LAC_HUB/` (downloaded sources and paper drafts); any folder named `sources`, `downloads` or `downloaded` under `_LAC_HUB/`. These go into `.gitignore`. Keep the `.md`, `.csv`, `.json`, `.py`, `.log` and `.txt` files of `_LAC_HUB/` tracked, so briefs, REPORT, GAPS, CHANGES and their tables are public.
3. Backups and caches (exclude): `__pycache__/`, `*.pyc`, `*.pre_*`, every folder named `backups` or `backup`, `~$*` (Excel lock files), `*.tmp`, `Thumbs.db`, `desktop.ini`, `*.zip`, `*.7z`.
4. Personal paths (report only): count text files containing `C:\Users\luisfernando` or `/c/Users/luisfernando`. Record the count and the ten files with most hits in GAPS as a known-limitation candidate. Do not edit them.

### Step 4. Ignore and attribute files

1. Write `.gitignore` with the patterns from Steps 1 to 3, grouped under short comments (size, licensed documents, backups and caches). Do not ignore `.xlsx`, `.csv` or `.txt` files by extension; only by size or by the named folders.
2. Write `.gitattributes` with the single line `* -text`, so git stores every file byte for byte and no line ending is converted (the `.bat` files need CRLF, `stage0_run_all.sh` needs LF).
3. After `git init` (Step 5), run `git add --dry-run -A` and write `tracked_dry_run.txt`. Check: no listed file over 50 MB; total of listed files under 2 GB. If the total is 2 GB or more, add the largest regenerated output folders (solver outputs, `Executables` outputs, `B1_Output_Params` archives) to `.gitignore` until it is under 2 GB, and record each one in GAPS.

### Step 5. Local repository and first commit

1. `git init -b main` at the MODELS_LAC_5 root.
2. Git identity: use the global `user.name` and `user.email` if set. If not, set them for this repository only to `luviga` and `luviga@users.noreply.github.com`, and record it.
3. Commit 1: `.gitignore` and `.gitattributes`, message `repo: ignore and attribute rules`.
4. Commit 2: everything else that is not ignored, except your job folder, message `baseline: MODELS_LAC_5 after LAC_SAFE_SAVE_FIX 20261109T053358Z`.
5. Gate: `git status --short` is empty apart from your job folder; `git ls-files` count equals the dry-run count.

### Step 6. Publish (only if the hard gates pass)

Hard gates, all required before any push:
- zero unresolved secret hits from Step 3.1;
- the six A-O hashes MATCH (Step 1.2);
- no tracked file over 50 MB and total under 2 GB (Step 4.3).

If any fails, do not push. Record which gate failed and stop this step.

If all pass:
1. Run `gh auth status`. If `gh` is installed and logged in as `luviga`:
   - `gh repo view luviga/clewise-lac`. If it exists and has any commit, do not push; record it. If it exists and is empty, add it as `origin`. If it does not exist, run `gh repo create luviga/clewise-lac --public --description "CLEWISE: six national OSeMOSYS models for Latin America and the Caribbean (MODELS_LAC)"` and add it as `origin`.
   - `git push -u origin main`. A push of 1 to 2 GB can take 30 minutes or more; let it finish.
2. If `gh` is missing or not logged in, try `git push -u https://github.com/luviga/clewise-lac.git main` once (this works only if the empty repository already exists and git has stored credentials). If that fails, do not retry; write in REPORT the exact manual steps for Luis: create the empty public repository `clewise-lac` on github.com with no README, licence or .gitignore, then run the Git Bash block (cd to the root, `git remote add origin https://github.com/luviga/clewise-lac.git`, `git push -u origin main`).

### Step 7. Gates after the push

1. Working copy unchanged: write `files_after.csv` the same way as Step 1 and compare with `files_before.csv`. Expected: zero differences. The only new paths are `.git/`, `.gitignore`, `.gitattributes` and your job folder.
2. If the push succeeded: clone `https://github.com/luviga/clewise-lac.git` into `C:\clw_verify_<stamp>` with `--depth 1`, compute SHA-256 of every file in the clone, and compare with the same paths in `files_before.csv`. Expected: every tracked file equal, count equal to `git ls-files`. Then delete `C:\clw_verify_<stamp>`.
3. Record the pushed commit hashes.

### Step 8. Outputs commit

Write the three output files (section 6) into the job folder, commit the job folder with message `hub: LAC_REPO_SETUP <stamp> reports`, and push it if Step 6 pushed. Check with `git status --short` that the tree is clean.

## 6. Outputs

All three in `_LAC_HUB/repo_setup_<stamp>/`, plain English, no em dashes.

`REPORT_LAC_REPO_SETUP_<stamp>.md`: the repository URL and visibility; pushed or not, and why; commit hashes; tracked file count and total size; the six A-O hash checks; every hard gate with its result and counts; the after-push gates; what `.gitignore` excludes, as a short table of pattern, reason and number of files and MB excluded; if not pushed, the manual steps for Luis.

`GAPS_LAC_REPO_SETUP_<stamp>.md`: every judgement call and its reason; every content-scan hit marked "not a secret" with its reason; "Known-limitation candidates" (including the personal-path count, and that the repository has no licence file, which means all rights reserved until Luis adds one); anything left unchecked; incidents.

`CHANGES_LAC_REPO_SETUP_<stamp>.md`: the new files (`.gitignore`, `.gitattributes`, `.git/`) and the two commits, two or three lines each.
