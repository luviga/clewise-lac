"""Step 4 code changes: the Stage 2 cause of the Guatemala solar and wind holes, and one Stage 3 rule.

  stage2_apply_v2.py  when the frozen non-hydro renewables (biomass, biogas, geothermal) alone exceed the room
                      that fossil and hydro leave, they and the solar and wind plants are scaled together into
                      that room (the gap-fill of Stage 1), instead of scaling the frozen plants and setting solar
                      and wind to 0. Same change in the forward rebase (Phase 2) and in the policy enforcement
                      (Phase 5), which held the same branch.
  stage3_apply.py     --skip-orphan-cap removed: orphan plants capped at 0 from 2025 and zero-lower plants given
                      upper 0 in every country; a scenario listed under orphan_cap_exempt_scenarios in the controller
                      table keeps its orphan plants uncapped (step 4.5: Guatemala NDC and LTS, the one binding group).
  stage_controller.csv  the row orphan_cap_exempt_scenarios with its reason.
Line endings kept; each replacement must match the expected number of times.
Usage: python step4_apply.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import machine as M  # noqa: E402
from edits import edit  # noqa: E402

ROOT = M.ROOT

edit('stage2_apply_v2.py', [
    ("""            # If locked > nh_target, scale locked down
            if locked_sum > nh_target > 0:
                factor = nh_target / locked_sum
                for t in locked_techs:
                    s2_shares[(c, s, t)][y] *= factor
                for t in growth_techs:
                    s2_shares[(c, s, t)][y] = 0.0
""", """            # If locked > nh_target, the frozen plants and the solar and wind plants share the room left by
            # fossil and hydro in proportion to their rule and floor values (Stage 1 gap-fill), so solar and
            # wind keep their committed place instead of being set to 0
            if locked_sum > nh_target > 0:
                nh_sum = locked_sum + sum(s2_shares[(c, s, t)][y] for t in growth_techs)
                factor = nh_target / nh_sum
                for t in locked_techs + growth_techs:
                    s2_shares[(c, s, t)][y] *= factor
""", 1),
    ("""                # If locked > NH_target, scale locked down
                if locked_sum > NH_target > 0:
                    factor = NH_target / locked_sum
                    for t in locked_techs:
                        s2_shares[(c, s, t)][y] *= factor
                    for t in growth_techs:
                        s2_shares[(c, s, t)][y] = 0.0
""", """                # If locked > NH_target, the frozen plants and the solar and wind plants share the room left
                # by fossil and hydro in proportion to their values (as in the forward rebase above)
                if locked_sum > NH_target > 0:
                    nh_sum = locked_sum + sum(s2_shares[(c, s, t)][y] for t in growth_techs)
                    factor = NH_target / nh_sum
                    for t in locked_techs + growth_techs:
                        s2_shares[(c, s, t)][y] *= factor
""", 1),
])

FACTOR = ('LOWER_TO_UPPER_FACTOR = LT.controller("lower_to_upper_factor", "3")  # tight cap = lower * factor when '
          'controller says uncapped but lower > 0\n')
edit('stage3_apply.py', [
    ("""    parser.add_argument("--skip-orphan-cap", nargs="*", default=[],
                        help="Countries to skip orphan tech capping (e.g., Guatemala)")
""", "", 1),
    ("""            # Find orphan PP techs (in model but not in controller) — needed for Steps 3b and 4
            skip_orphans = country in args.skip_orphan_cap
            if skip_orphans:
                orphan_techs = []
                log.append(f"  Orphan capping SKIPPED for {country} (--skip-orphan-cap)")
            else:
""", """            # Find orphan PP techs (in model but not in controller) — needed for Steps 3b and 4.
            # Every country caps them at 0 from 2025, except a scenario that the controller table lists under
            # orphan_cap_exempt_scenarios for the country (config/scenarios/rules/stage_controller.csv, with its reason)
            if scenario in ORPHAN_CAP_EXEMPT.get(country, []):
                orphan_techs = []
                log.append(f"  Orphan capping not applied for {country} {scenario} (orphan_cap_exempt_scenarios)")
            else:
""", 1),
    ("""                # Zero lower → zero upper (prevent unconstrained techs from producing).
                # UNLESS skip_orphans is set (e.g., Guatemala) — then leave zero-lower uncapped.
                zero_lower_upper = 0.0 if not skip_orphans else LT.controller("uncapped_value", "3")
""", """                # Zero lower → zero upper (prevent unconstrained techs from producing), in every country.
                zero_lower_upper = 0.0
""", 1),
    (FACTOR, FACTOR +
     '# {country: [scenario, ...]} whose orphan plants are left uncapped (stage_controller.csv, orphan_cap_exempt_scenarios)\n'
     'ORPHAN_CAP_EXEMPT = {c: (v if isinstance(v, list) else [v])\n'
     '                     for c, v in LT.controller_by_country("orphan_cap_exempt_scenarios", "3").items()}\n', 1),
])

# step 4.5: the one limit group that binds in Guatemala NDC and LTS under the common rule (work/gua_relax.csv),
# held as a table row with its reason; a decision for Luis
ROW = '3,uncapped_value,all,99999.0,PJ or GW,stage3_apply.py,value written for a limit that Stage 3 leaves open\n'
edit('config/scenarios/rules/stage_controller.csv', [
    (ROW, ROW + '3,orphan_cap_exempt_scenarios,Guatemala,NDC|LTS,scenario names,stage3_apply.py,'
     'scenarios whose orphan plants (in the model and not in the controller) Stage 3 leaves uncapped: under the '
     'common rule these two scenarios have no feasible solution and relaxing one limit group at a time (LAC_CLEANUP '
     'November 2026) showed that only the orphan cap binds; kept until Luis decides\n', 1),
])
