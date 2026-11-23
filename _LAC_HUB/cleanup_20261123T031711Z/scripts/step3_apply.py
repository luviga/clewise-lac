"""Step 3 code fixes (values unchanged) and the step 1 test-setup fix, applied to the working tree.

  F5  the region code of rows the B1 transport rewrite appends comes from the country's own code
      (config/preparation/Config_country_codes.yaml); appended_region_code leaves the execution YAML
  F6  stage3_results.py checks each country against its own renewable target rows (Stage 1 and 2 lookup)
  F7  stage0_run.py visits the bypass plants in sorted order
  docs NDCNEW and LTSNEW replaced by NDC and LTS in PIPELINE_WORKFLOW.md and HANDOFF_STAGE4.md
  step 1  work/step1_tests.patch (test setup of the two safe-save unit tests)
Line endings of each file are kept. Each replacement must match the expected number of times.
Usage: python step3_apply.py
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import machine as M  # noqa: E402

ROOT = M.ROOT


from edits import edit  # noqa: E402


# F5
REG_OLD = "_TB1['appended_region_code']"
REG_NEW = "LT.country_value(_TC, 'code')"
edit('CostaRica/CR_ENERGY/t1_confection/B1_Base_Scenarios_Adj_Parallel_CostaRica.py', [(REG_OLD, REG_NEW, 1)])
edit('DominicanRepublic/RD_ENERGY/B1_Base_Scenarios_Adj_Parallel_DominicanRepublic.py', [(REG_OLD, REG_NEW, 2)])
edit('Guatemala/GUA_ENERGY/B1_Base_Scenarios_Adj_Parallel_Guatemala.py', [(REG_OLD, REG_NEW, 5)])
edit('config/execution/Config_MOMF_T1_AB.yaml', [
    ("    appended_region_code: RD              # region code appended to rows the transport rewrite adds\n", "", 1),
    ("    appended_region_code: RD\n", "", 1),
    ("    appended_region_code: GUA\n", "", 1),
])

# F6
edit('stage3_results.py', [
    ("""            # Policy targets: {scenario: {year: target_share}}
            # (inputs/scenarios/scenario_values.csv, lever renewable_share, general rows)
            RE_TARGETS = LT.scenario_values("renewable_share")
""", """            # Policy targets: {scenario: {year: target_share}} of each country, with the lookup of Stages 1
            # and 2: the country's own rows where it has them, else the general rows
            # (inputs/scenarios/scenario_values.csv, lever renewable_share)
            RE_TARGETS_GENERAL = LT.scenario_values("renewable_share")
            RE_TARGETS_COUNTRY = LT.scenario_value_overrides("renewable_share")
""", 1),
    ("""            for country in countries:
                for scen, year_targets in RE_TARGETS.items():
                    for year, target in year_targets.items():
""", """            for country in countries:
                for scen in RE_TARGETS_GENERAL:
                    year_targets = RE_TARGETS_COUNTRY.get(country, {}).get(scen, RE_TARGETS_GENERAL[scen])
                    for year, target in year_targets.items():
""", 1),
])

# F7
edit('stage0_run.py', [
    ("                for tech in BYPASS_TECHS:\n", "                for tech in sorted(BYPASS_TECHS):\n", 2),
])

# docs
for rel, n_ndc, n_lts in (('PIPELINE_WORKFLOW.md', None, None), ('HANDOFF_STAGE4.md', None, None)):
    p = ROOT / rel
    s = p.read_bytes().decode('utf-8')
    a, b = s.count('NDCNEW'), s.count('LTSNEW')
    p.write_bytes(s.replace('NDCNEW', 'NDC').replace('LTSNEW', 'LTS').encode('utf-8'))
    print('edited', rel, 'NDCNEW', a, 'LTSNEW', b)

# step 1 test setup
r = subprocess.run(['git', 'apply', str(M.JOB / 'work' / 'step1_tests.patch')], cwd=ROOT, capture_output=True, text=True)
print('step1 patch', r.returncode, r.stderr.strip())
