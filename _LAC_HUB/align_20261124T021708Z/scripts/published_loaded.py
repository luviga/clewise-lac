"""Step 2.9 gate: published_values_loaded.csv lists every row of the verified published-value table (and the
held-back conflicts) with the model input it went to and the value written, or the reason it is not loaded."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv

V = M.ROOT / '_LAC_HUB' / 'ndc_verify_20261121T233937Z'
loaded = {}
for r in csv.DictReader(open(M.ROOT / 'inputs' / 'scenarios' / 'scenario_values.csv', encoding='utf-8')):
    for vid in r['value_id'].split('|'):
        if vid:
            loaded.setdefault(vid, []).append(
                (f"inputs/scenarios/scenario_values.csv {r['country']} {r['scenario']} {r['lever']} {r['lever_kind']} {r['year']}",
                 r['value'], r['unit']))
for r in csv.DictReader(open(M.JOB / 'work' / 'transport_targets.csv', encoding='utf-8')):
    if r['result'] == 'loaded':
        loaded.setdefault(r['value_id'], []).append(
            (f"{r['model']}/B1_Scenario_Config.xlsx Tech_Adoption {r['scenario']} {r['technology']} {r['column']}",
             r['value'], 'share of the class output'))
REASON = {
    'CR-T024': 'not representable: the model has no biomethane vehicle technology',
    'CR-T025': 'not representable as one share: natural gas runs only in heavy freight in the model, the target covers light and heavy freight',
    'CR-T020': 'not representable: BLEND_GSL takes 1.0 gasoline and 1.0 ethanol per unit, so no blend share can be set',
    'CR-T021': 'not representable: BLEND_GSL takes 1.0 gasoline and 1.0 ethanol per unit, so no blend share can be set',
    'CR-T087': 'not representable: BLEND_GSL takes 1.0 gasoline and 1.0 ethanol per unit, so no blend share can be set',
    'CR-T042': 'not represented: the model has no distributed renewable capacity of this kind (Known-limitation candidate)',
    'CR-T043': 'not represented: the model has no distributed renewable capacity of this kind (Known-limitation candidate)',
    'CR-T044': 'not represented: the model has no storage technology (Known-limitation candidate)',
    'CR-T088': 'not loaded: an LTS value before 2035, where the NDC (which states no LPG share) rules',
    'DR-T011': 'not loaded: new gas capacity does not enter the renewable share rule; committed builds come from the model data',
    'ECU-T027': 'not loaded: a long-term plan value for 2035, where the NDC plan values (ECU-T069, ECU-T070, 2032) rule',
    'ECU-T029': 'not loaded: the 2050 share of the same document (ECU-T028, ECU-T030) is loaded for that year',
    'ECU-T040': 'not loaded: a mode share of public transport (passenger-km), not a fleet technology share; the Ecuador policy scenarios have no adoption rows',
    'ECU-T041': 'not loaded: the Ecuador policy scenarios have no transport adoption rows in the model inputs (Known-limitation candidate)',
    'ECU-T042': 'not loaded: the Ecuador policy scenarios have no transport adoption rows in the model inputs (Known-limitation candidate)',
    'ECU-T043': 'not loaded: a 2070 value, after the model horizon',
    'GUA-T009': 'not loaded: the share target of the same year (GUA-T008) rules',
    'GUA-T016': 'not loaded: a count of added vehicles; the model holds no vehicle count of the class for 2035 (Known-limitation candidate)',
    'GUA-T017': 'not loaded: a count of added vehicles; the model holds no vehicle count of the class for 2035 (Known-limitation candidate)',
    'GUA-T021': 'not loaded: a share of one bus system (Transmetro) whose fleet the model does not separate',
    'GUA-T022': 'not loaded: a count of routes',
    'GUA-T060': 'not loaded: a long-term document value before 2035, where the NDC rules',
    'HON-T089': 'not loaded: the NDC value of the same year (HON-T018, 0.70) wins',
    'HON-T090': 'not loaded: the NDC value of the same year (HON-T019, 0.70) wins',
    'HON-T091': 'not loaded: the NDC share of the same year (HON-T019) rules',
    'HON-T092': 'not loaded: thermal capacity does not enter the renewable share rule',
    'HON-T093': 'not represented: storage (Known-limitation candidate)',
    'HON-T095': 'not loaded: thermal capacity does not enter the renewable share rule',
    'HON-T096': 'not loaded: thermal capacity does not enter the renewable share rule',
    'JAM-T047': 'not loaded: a long-term document value before 2035, where the NDC rules',
    'JAM-T048': 'not loaded: a long-term document value before 2035, where the NDC rules (same value as JAM-T028)',
    'JAM-T049': 'not loaded: a long-term document value before 2035, where the NDC rules',
    'JAM-T062': 'not loaded: the long-term document states the share of the same years (JAM-T050 to T052)',
    'JAM-T115': 'not loaded: the NDC value of the same year (JAM-T028) is loaded',
    'JAM-T116': 'not loaded: the NDC value of the same year (JAM-T029) is loaded',
    'JAM-T120': 'not represented: battery storage (Known-limitation candidate)',
    'JAM-T127': 'not loaded: a share of electricity demand, not a fleet share',
    'JAM-T064': 'not loaded: an LTS value before 2035, where the NDC rules; the JAM_TRANSPORT adoption rows of the LTS scenario are unchanged',
    'JAM-T065': 'not loaded: an LTS value before 2035, where the NDC rules; the JAM_TRANSPORT adoption rows of the LTS scenario are unchanged',
    'JAM-T066': 'not loaded: an LTS value before 2035, where the NDC rules; the JAM_TRANSPORT adoption rows of the LTS scenario are unchanged',
    'JAM-T067': 'not loaded: an LTS value before 2035, where the NDC rules; the JAM_TRANSPORT adoption rows of the LTS scenario are unchanged',
    'JAM-T069': 'not loaded: a count of electric buses; the JAM_TRANSPORT model holds no bus count for 2040 (Known-limitation candidate)',
    'JAM-T070': 'present in the JAM_TRANSPORT LTS adoption rows (0.67 in 2050) before this job; unchanged',
    'JAM-T068': 'not loaded: a fuel efficiency change, not a fleet share',
    'JAM-T074': 'not loaded: a share of alternative fuels across modes, not representable as one fleet share',
}
out = []
for fn, tag in [('scenario_values.csv', ''), ('scenario_values_held_back.csv', 'conflict')]:
    for r in csv.DictReader(open(V / fn, encoding='utf-8')):
        vid = r['value_id']
        if vid in loaded:
            for inp, val, unit in loaded[vid]:
                out.append([vid, r['country'], r['scenario'], r['year'], r.get('value_standard', ''), r.get('unit_standard', ''),
                            r.get('check_status', ''), 'loaded', inp, val, unit, ''])
            continue
        mq = (r.get('model_quantity') or 'none')
        if tag:
            why = 'not loaded: conflict between readings (held back)'
        elif vid in REASON:
            why = REASON[vid]
        elif mq.startswith('emissions') or mq.startswith('reduction against'):
            why = 'not imposed: an emission level, reported against the model after the solve (emission_targets_check.csv)'
        elif mq == 'none':
            why = 'not a model quantity of the energy models (economy-wide, another sector, or a qualitative or count measure)'
        elif mq.startswith('none readable'):
            why = 'not representable: ' + mq
        else:
            why = 'not loaded: a value of a document that does not rule for that year, or not needed by the rules of step 2'
        out.append([vid, r['country'], r['scenario'], r['year'], r.get('value_standard', ''), r.get('unit_standard', ''),
                    r.get('check_status', ''), 'not loaded', '', '', '', why])
with open(M.JOB / 'published_values_loaded.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['value_id', 'country', 'scenario', 'year', 'value_standard', 'unit_standard', 'check_status', 'result',
                'model_input', 'value_written', 'unit_written', 'reason'])
    w.writerows(out)
from collections import Counter  # noqa: E402
print(Counter(r[7] for r in out), len({r[0] for r in out if r[7] == 'loaded'}), 'value ids loaded')
