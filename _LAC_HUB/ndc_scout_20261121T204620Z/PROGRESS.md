# PROGRESS LAC_NDC_SCOUT 20261121T204620Z

- Start (UTC): 2026-11-21 20:46:20. Branch `job/ndc-scout` from `origin/main` at `29dc938`. Model worktree `/c/clw_scout_model` at `481a7c0` (checked).
- Setup: venv `/c/clw_scout_venv` (python.org 3.12.0; pypdf, pdfplumber, pandas 3.1.1, openpyxl). Job folder, `.gitignore` (`downloads/`), brief copied.
- C1 (all six countries): `scripts/c1_model_levers.py` written and run; `model_levers_<code>.csv` for CR, DR, ECU, GUA, HON, JAM. Solved renewable shares recomputed and equal to the brief's figures (ECU NDCNEW 2035 0.805).
- Conventions for country tasks: `country_task_conventions.md`.
- Pair 1 (CR, DR): started.
- DR task finished: 6 sources, 2 pending, 66 targets, 41 projection rows, 41 alignment rows, 16 proposal rows, spot check 10 of 10. Hub check (`scripts/hub_check_values.py`): 104 of 107 values found on the cited page text; the other 3 checked by hand (two carbon neutrality aspirations with value 0, one non-numeric clinker framework), all confirmed. Hub recomputed the DR emissions and capacity model values of alignment rows DR-T001, DR-T003, DR-T009, DR-T013 from `model_levers_DR.csv`: equal.
- CR task finished: 8 sources, 2 pending, 98 targets, 36 projection rows, 64 alignment rows, 35 proposal rows (20 A, 8 B, 7 documents silent), spot check 10 of 10. Hub check: 132 of 134 values found on the cited page text; the other 2 (carbon neutrality 2050, value 0) checked by hand on CR-01 p.143 and CR-02 p.12: confirmed. Hub confirmed the CR finding that LTSNEW solved fossil generation is below the LTSNEW input lower limits (PWRDSL 2035: input floor 2.1871 PJ, solved 0.2247 PJ; PWRFOI 2035: 4.4409 PJ, solved 0.4561 PJ); NDCNEW and BAU are consistent. Known-limitation candidate.
- Pair 1 committed and pushed. Pair 2 (ECU, GUA) started.
