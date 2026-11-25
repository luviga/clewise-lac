"""Documentation of the rules of this job in PIPELINE_WORKFLOW.md and HANDOFF_STAGE4.md (run once)."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402

EXEMPT = ('One part of it stays as a table row until Luis decides: `orphan_cap_exempt_scenarios` in '
          '`config/scenarios/rules/stage_controller.csv` leaves the orphan plants of Guatemala NDC and LTS uncapped, '
          'because these two scenarios have no feasible solution with the orphan cap and it is the only limit group '
          'that binds.')
NOW = ('The row `orphan_cap_exempt_scenarios` was removed in LAC_ALIGN (November 2026): every power plant without a '
       'controller row is capped at 0 from 2025 in every country and scenario.')
p = M.ROOT / 'PIPELINE_WORKFLOW.md'
s = p.read_text(encoding='utf-8')
reps = [
    (EXEMPT, NOW),
    ('- Country overrides: CR NDC 90%/LTS 99%, Ecuador NDC 80%/LTS 80→99%',
     '- Targets: published values only (`inputs/scenarios/scenario_values.csv`): renewable shares as published, '
     'and published new capacity turned into a share by the capacity rule of `renewable_targets.py` '
     '(capacity x anchor-year capacity factor x 31.536, added to the anchor-year renewable generation, over the '
     'Stage 0 generation of the target year). The last target is held after its year; a country and scenario '
     'without a target takes the BAU shares. Stage 1 writes the built targets to '
     '`_STAGE1_OUTPUT/RENEWABLE_TARGETS.csv`, which Stage 2, the Stage 3 results and the tests read.'),
    ('in every country except the scenarios listed under `orphan_cap_exempt_scenarios` (Guatemala NDC and LTS).',
     'in every country and scenario.'),
    ('| Guatemala | PPPVT2 (1) | Capped to 0 in BAU; left uncapped in NDC and LTS (`orphan_cap_exempt_scenarios`) |',
     '| Guatemala | PPPVT2 (1) | Capped to 0 in every scenario |'),
    ('py stage3_apply.py --root . --clean --uncap-pp-maxcap\npy stage3_test.py --root .\nstage3_run_all.bat\npy stage3_results.py --root .',
     'py stage3_apply.py --root . --clean --uncap-pp-maxcap\npy stage3_test.py --root .\nstage3_run_all.bat\n'
     'py stage3_emission_cap.py --root .\npy stage3_results.py --root .'),
]
for a, b in reps:
    assert a in s, a[:60]
    s = s.replace(a, b)
add = """
---

## Rules added by LAC_ALIGN (November 2026)

- **Scenario rules step** (`py scenario_rules.py --root .`, after the B1 runs and before Stage 0): every
  `Executables/{scenario}_0/{scenario}_0.txt` gets the hydrogen rule (technologies of group `hydrogen` in
  `config/scenarios/technology_types.csv` at activity upper limit 0, no lower limit) and the history rule (every
  value of a policy scenario up to `history_end_year` equals the BAU value). Log: `_STAGE0_OUTPUT/SCENARIO_RULES_LOG.csv`.
- **Stage 2 overflow**: frozen output (hydro, bagasse, geothermal and other locked renewables) and committed builds
  are kept; when they and the fossil path overflow the total, the non-committed fossil part gives way. Stage 2
  writes the sheets FROZEN (frozen plants and the override row behind each value) and FLOOR_LOWER (PJ kept as a
  lower limit when share pins are released).
- **Energy emission cap** (`py stage3_emission_cap.py --root .`, after `stage3_run_all.bat`): for a scenario with
  an `energy_emission_reduction_vs_bau` row in `inputs/scenarios/scenario_values.csv`, the yearly limits from
  `cap_start_year` to `cap_target_year` run on a straight line from the solved NDC energy emissions of
  `cap_from_year` to the solved BAU emissions of `cap_target_year` times (1 - r), on the labels of group
  `energy_cap` of `config/scenarios/emission_labels.csv`; the scenario is solved again. Stage 3 apply has
  released its power plant share pins from `cap_start_year` (upper limits open, lower limits = FLOOR_LOWER).
"""
s = s.rstrip('\n') + '\n' + add
p.write_text(s, encoding='utf-8', newline='\n') if False else open(p, 'w', encoding='utf-8', newline='\n').write(s)
h = M.ROOT / 'HANDOFF_STAGE4.md'
t = h.read_text(encoding='utf-8')
t = t.replace("| Guatemala exception | removed in LAC_CLEANUP (November 2026) except the orphan cap of NDC and LTS (`orphan_cap_exempt_scenarios`); the reason it had: |",
              "| Guatemala exception | removed in LAC_CLEANUP (November 2026); its last part (`orphan_cap_exempt_scenarios`) removed in LAC_ALIGN (November 2026); the reason it had: |")
t = t.replace("| Guatemala | `orphan_cap_exempt_scenarios` (NDC, LTS) | Orphan PPPVT2 left uncapped in NDC and LTS only; otherwise the common rule |",
              "| Guatemala | none (LAC_ALIGN) | Orphan PPPVT2 capped at 0 in every scenario, as in every country |")
open(h, 'w', encoding='utf-8', newline='\n').write(t)
print('ok')
