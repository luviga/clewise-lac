"""Step 5.1 and 5.3: one decision per candidate from the search (work/step5_search.csv), written to deletions.csv.

A candidate is deleted only when no pipeline script or table names it (first pass) and no other kept script or
configuration of its energy folder or of the root reads it (second pass). Hits that do not name the candidate are
listed with the reason they are set aside: a comment, a name of another folder's file (the root table names the
Ecuador runner; root tools name sector-model folders), a generic name list of the repository-cleanup tools.
Usage: python step5_decide.py
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import machine as M  # noqa: E402

# candidates with hits: decision and reason (judged from the hit lines in step5_search.csv)
JUDGED = {
    'CostaRica/CR_ENERGY/t1_confection/Blend_Shares_0.pickle':
        ('delete', 'named only as the output path of the Costa Rica B1 runner, written inside if Use_Blend_Shares_B1 (false '
                   'in MOMF_B1_exp_manager.yaml); no script loads it (F8)'),
    'Honduras/HON_ENERGY/B1_Base_Scenarios_Adj_Parallel.py':
        ('delete', 'the root table names B1_Base_Scenarios_Adj_Parallel.py as the Ecuador runner (another folder); the '
                   'cleanup tool clean_repo_identify.py lists the name as a pattern, it does not read the file'),
    'Jamaica/JAM_ENERGY/B1_Base_Scenarios_Adj_Parallel.py':
        ('delete', 'as for the Honduras copy: the hits name the Ecuador runner or a cleanup-tool pattern'),
    'Guatemala/GUA_ENERGY/B1_Base_Scenarios_Adj_Parallel.py':
        ('delete', 'hits: the Ecuador runner in the root table, a commented path in the Guatemala runner, a cleanup-tool pattern'),
    'Guatemala/GUA_ENERGY/B1_Base_Scenarios_Adj_Parallel2.py':
        ('delete', 'hits on the stem only: a comment, the Ecuador runner in the root table, a comment of the execution YAML'),
    'Guatemala/GUA_ENERGY/Modify_m1.py':
        ('delete', 'named only in a commented-out line of the Guatemala runner'),
    'Guatemala/GUA_ENERGY/B1_Base_Scenarios.py':
        ('keep', 'the live Guatemala B1 runner names it (os.path.abspath("B1_Base_Scenarios.py") to find its folder)'),
    'CostaRica/CR_ENERGY/t1_confection/A2_Extra_Inputs/A-Xtra_Scenarios.xlsx':
        ('keep', 'read by the Costa Rica A2 compiler through MOMF_T1_A.yaml (Xtra_Scen)'),
    'Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization_COMPLETED.xlsx': ('keep', 'written by the Guatemala A2 compiler'),
    'Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization_Natural_COMPLETED.xlsx': ('keep', 'written by the Guatemala A2 compiler'),
    'Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx':
        ('keep', 'read by the Honduras A2 compiler (the A-O workbook of the model) and written by its A1 script'),
    'Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization_COMPLETED.xlsx': ('keep', 'written by the Honduras A2 compiler'),
    'Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization_Natural_COMPLETED.xlsx': ('keep', 'written by the Honduras A2 compiler'),
    # second-pass hits
    'Jamaica/JAM_ENERGY/A2_Compiler.py': ('delete', 'only a pattern of the cleanup tool clean_repo_identify.py'),
    'Ecuador/ECU_Energy/A2_Compiler.py': ('delete', 'only a pattern of the cleanup tool clean_repo_identify.py'),
    'DominicanRepublic/RD_ENERGY/A2_Compiler.py': ('delete', 'only a pattern of the cleanup tool clean_repo_identify.py'),
    'Honduras/HON_ENERGY/A2_Compiler.py': ('delete', 'only a pattern of the cleanup tool clean_repo_identify.py'),
    'Jamaica/JAM_ENERGY/JAM_AO_BAU_edits.xlsx': ('keep', 'read by Jamaica apply_ao_edits.py (a kept tool)'),
    'CostaRica/CR_ENERGY/config_plots/test_inputs.py': ('keep', 'named by MOMF_B1_exp_manager.yaml (test_path), the configuration the Costa Rica B1 runner loads'),
    'DominicanRepublic/RD_ENERGY/B1_Base_Scenarios_Adj_Parallel_ADJ_TESTEOS.py':
        ('keep', 'named in the keep list of clean_repo_apply.py and clean_repo_identify.py ("DR\'s production runner")'),
    'CostaRica/CR_ENERGY/config_plots/plots_config.yaml': ('keep', 'read by CostaRica config_plots/plot_csvs.py (a kept tool)'),
    'Honduras/HON_ENERGY/plots_config.yaml': ('keep', 'read by Honduras plot_csvs.py (a kept tool)'),
    'Jamaica/JAM_ENERGY/plots_config.yaml': ('keep', 'read by Jamaica plot_csvs.py (a kept tool)'),
    'CostaRica/CR_ENERGY/t1_confection/MOMF_T1_B1.yaml': ('delete', 'named only in a comment of change_default_vals_params.py'),
    'Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization_PLANMICC.xlsx': ('keep', 'in the source list of ao_cost_repair_manager.py'),
    'Ecuador/ECU_Energy/A1_Outputs/reference_PLANMICC/': ('keep', 'a file in it is in the source list of ao_cost_repair_manager.py'),
    'Ecuador/ECU_Energy/A1_Outputs/reference_edited/': ('keep', 'a file in it is in the source list of ao_cost_repair_manager.py'),
    'DominicanRepublic/RD_ENERGY/A1_Outputs/reference_works/':
        ('delete', 'the hits name reference_works folders of the Ecuador sector models (ecuador_non_energy_cost_repair_manager.py), not this folder'),
    'Guatemala/GUA_ENERGY/A2_Compiler.py': ('keep', 'run by Guatemala Nuevo_A2_Compiler_mac2025.py (a kept wrapper)'),
    'Guatemala/GUA_ENERGY/B1_Energy_Base_Scenarios_Adj_Parallel_mac_DR.py': ('keep', 'run by Guatemala Modelo_nuevoDR_2024.py (a kept wrapper)'),
}

rows = []
with open(M.JOB / 'work' / 'step5_search.csv', encoding='utf-8', newline='') as fh:
    for r in csv.DictReader(fh):
        p, h, o = r['path'], int(r['hits']), int(r['other_hits'])
        if p in JUDGED:
            dec, why = JUDGED[p]
        elif h == 0 and o == 0:
            dec, why = 'delete', 'no hit'
        else:
            raise SystemExit(f'unjudged hits for {p}')
        res = f'pipeline scripts and tables: {r["search_result"]}; other scripts: {r["other_result"]}'
        rows.append(dict(path=p, files=r['files'], bytes=r['bytes'], why_dead=r['why'], search_result=res[:1500],
                         decision=dec, decision_reason=why))
with open(M.JOB / 'deletions.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
d = [r for r in rows if r['decision'] == 'delete']
print(f'candidates {len(rows)}; delete {len(d)} ({sum(int(r["files"]) for r in d)} files, {sum(int(r["bytes"]) for r in d) / 1e6:.1f} MB); keep {len(rows) - len(d)}')
