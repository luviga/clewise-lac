"""Step 4 documentation: --skip-orphan-cap leaves every command of PIPELINE_WORKFLOW.md and HANDOFF_STAGE4.md, and the
text that described the Guatemala exception says that Guatemala follows the common rule. Run after step3_apply.py
(scenario names already NDC and LTS). Result tables of earlier runs are left as they were written.
Usage: python step4_docs.py   (text matches the step 4.5 outcome: one controller row for Guatemala NDC and LTS)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from edits import edit  # noqa: E402

CMD_OLD = 'py stage3_apply.py --root . --clean --uncap-pp-maxcap --skip-orphan-cap Guatemala'
CMD_NEW = 'py stage3_apply.py --root . --clean --uncap-pp-maxcap'
COMMON = ('Stage 3 applies one rule to all six countries (orphan plants capped at 0 from 2025, zero-lower plants '
          'given upper 0); the Guatemala exception (`--skip-orphan-cap`) was removed in LAC_CLEANUP (November 2026). '
          'One part of it stays as a table row until Luis decides: `orphan_cap_exempt_scenarios` in '
          '`config/scenarios/rules/stage_controller.csv` leaves the orphan plants of Guatemala NDC and LTS uncapped, '
          'because these two scenarios have no feasible solution with the orphan cap and it is the only limit group '
          'that binds.')

edit('PIPELINE_WORKFLOW.md', [
    (CMD_OLD, CMD_NEW, 2),
    ('This is handled in Stage 3 via `--skip-orphan-cap Guatemala`.', COMMON, 1),
    (' zero-lower techs get upper=0 (except Guatemala: upper=99999 via `--skip-orphan-cap`)', ' zero-lower techs get upper=0', 1),
    ('lower=0, upper=0 from 2025+. Skipped for Guatemala.', 'lower=0, upper=0 from 2025+, in every country except the scenarios listed under `orphan_cap_exempt_scenarios` (Guatemala NDC and LTS).', 1),
    ("| `--skip-orphan-cap Guatemala` | Guatemala: orphans left uncapped, zero-lower techs get 99999 | Guatemala NDC/LTS have inflated Stage 0 denominators (orphan overproduction); tight capping causes infeasibility |\n", '', 1),
    ('### Guatemala exception — root cause\n', '### Guatemala exception: what remains and its history\n\n' + COMMON + ' The history of the exception follows.\n', 1),
    ('| Guatemala | PPPVT2 (1) | **SKIPPED** — left free to produce |', '| Guatemala | PPPVT2 (1) | Capped to 0 in BAU; left uncapped in NDC and LTS (`orphan_cap_exempt_scenarios`) |', 1),
    ('| Guatemala | `GUA_ENERGY` | GUA | skip-orphan-cap required |', '| Guatemala | `GUA_ENERGY` | GUA | |', 1),
])
edit('HANDOFF_STAGE4.md', [
    (CMD_OLD, CMD_NEW, 2),
    ('| Zero-lower tech upper | 0 (except Guatemala: 99999) |', '| Zero-lower tech upper | 0 (all six countries) |', 1),
    ('| Guatemala exception | `--skip-orphan-cap Guatemala` |', '| Guatemala exception | removed in LAC_CLEANUP (November 2026) except the orphan cap of NDC and LTS (`orphan_cap_exempt_scenarios`); the reason it had: |', 1),
    ('| Guatemala | `--skip-orphan-cap` | Inflated Stage 0 denominators; PPPVT2 orphan left free; share validation ~1pp looser |',
     '| Guatemala | `orphan_cap_exempt_scenarios` (NDC, LTS) | Orphan PPPVT2 left uncapped in NDC and LTS only; otherwise the common rule |', 1),
    ('Guatemala:         PPPVT2 (SKIPPED)', 'Guatemala:         PPPVT2 (capped to 0 in BAU; uncapped in NDC and LTS)', 1),
    ('Current workaround (`--skip-orphan-cap`) is acceptable but leaves Guatemala shares ~1pp looser.',
     'The workaround (`--skip-orphan-cap`) was removed in LAC_CLEANUP; only the orphan cap of Guatemala NDC and LTS stays open, as a controller row.', 1),
])
