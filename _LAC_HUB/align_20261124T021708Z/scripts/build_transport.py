"""Register rows of step 2.5: published fleet shares written to the transport adoption rows (B1_Scenario_Config.xlsx
sheet Tech_Adoption) of the NDC and LTS scenarios. ASSUMPTION of the step: within one vehicle class, electric and
other vehicles run the same distance, so a fleet share equals the share of that class's output. A share stated for
a group of classes (private, light, public, freight) is written to every class of the group (same share in each
class, so the distance-weighted share of the group equals it). The last stated value is held. LTS equals NDC
through 2035; after 2035 a long-term document value applies where one is stated. Writes work/register_transport.csv
and work/transport_targets.csv (value_id, model input, value written)."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv

import openpyxl

FIELDS = ['model', 'file', 'sheet', 'tech', 'parameter', 'year', 'before', 'after', 'unit', 'source_id', 'page',
          'derivation', 'assumption_sentence', 'range_low', 'range_high']
ASSUM = ('ASSUMPTION: within one vehicle class, electric (or hybrid) and other vehicles run the same distance a year, '
         'so the published fleet share equals the share of the class output (passenger-km or tonne-km); a share stated '
         'for a group of classes is the same in every class of the group.')
# (model, scenario, tech, column, value, value_ids, source, page)
CR = 'CostaRica/CR_ENERGY/t1_confection'
HN = 'Honduras/HON_ENERGY'
T = []
for sc in ['NDC', 'LTS']:
    # Costa Rica: columns y_ini, v_2030, v_2035, v_2050
    T += [(CR, sc, 'TRNBUSELE', 'v_2030', 0.035, 'CR-T012', 'CR-01', 'p.39'),
          (CR, sc, 'TRNBUSELE', 'v_2035', 0.10, 'CR-T015', 'CR-01', 'p.39'),
          (CR, sc, 'TRNBUSELE', 'v_2050', 0.10, 'CR-T015', 'CR-01', 'p.39'),
          (CR, sc, 'TRNMICELE', 'v_2035', 0.10, 'CR-T015', 'CR-01', 'p.39'),
          (CR, sc, 'TRNMICELE', 'v_2050', 0.10, 'CR-T015', 'CR-01', 'p.39'),
          (CR, sc, 'TRNPASRAIELE', 'v_2030', 0.5, 'CR-T013', 'CR-01', 'p.39'),
          (CR, sc, 'TRNPASRAIELE', 'v_2035', 0.5, 'CR-T013', 'CR-01', 'p.39'),
          (CR, sc, 'TRNPASRAIELE', 'v_2050', 0.5 if sc == 'NDC' else 1.0, 'CR-T013' if sc == 'NDC' else 'CR-T084',
           'CR-01' if sc == 'NDC' else 'CR-02', 'p.39' if sc == 'NDC' else 'p.41'),
          (CR, sc, 'TRNPASRAIELE', 'Restriction_Type', 'Min/Max', 'CR-T013', 'CR-01', 'p.39'),
          (CR, sc, 'TRNFREHEAELE', 'v_2035', 0.05, 'CR-T027', 'CR-01', 'p.42'),
          (CR, sc, 'TRNFREHEAELE', 'v_2050', 0.05, 'CR-T027', 'CR-01', 'p.42'),
          (CR, sc, 'TRNFRELIGELE', 'v_2035', 0.15, 'CR-T028', 'CR-01', 'p.42'),
          (CR, sc, 'TRNFRELIGELE', 'v_2050', 0.15, 'CR-T028', 'CR-01', 'p.42')]
    for t in ['TRNSEDELE', 'TRNSUVELE', 'TRNMOTELE']:
        T += [(CR, sc, t, 'v_2030', 0.10, 'CR-T016', 'CR-01', 'p.40'),
              (CR, sc, t, 'v_2035', 0.20, 'CR-T019', 'CR-01', 'p.40'),
              (CR, sc, t, 'v_2050', 0.20 if sc == 'NDC' else 0.30, 'CR-T019' if sc == 'NDC' else 'CR-T085',
               'CR-01' if sc == 'NDC' else 'CR-02', 'p.40' if sc == 'NDC' else 'p.46')]
    T += [(CR, sc, 'TRNTAXELE', 'v_2030', 'interp', 'CR-T019', 'CR-01', 'p.40'),
          (CR, sc, 'TRNTAXELE', 'v_2035', 0.20, 'CR-T019', 'CR-01', 'p.40'),
          (CR, sc, 'TRNTAXELE', 'v_2050', 0.20 if sc == 'NDC' else 0.30, 'CR-T019' if sc == 'NDC' else 'CR-T085',
           'CR-01' if sc == 'NDC' else 'CR-02', 'p.40' if sc == 'NDC' else 'p.46')]
    # Honduras: columns y_ini, v_2030, v_2040, v_2050 (no 2035 column: the 2035 value is written in 2040 and held)
    for t in ['TRAUTELE', 'TRTAXELE', 'TRMOTELE', 'TRSUVELE', 'TRBPUELE', 'TRBTURELE', 'TRMBSELE', 'TRYTKELE', 'TRYLFELE']:
        T += [(HN, sc, t, 'v_2030', 0.03, 'HON-T026', 'HON-01', 'p.27'),
              (HN, sc, t, 'v_2040', 0.075, 'HON-T027', 'HON-01', 'p.27'),
              (HN, sc, t, 'v_2050', 0.075, 'HON-T027', 'HON-01', 'p.27')]
    T += [(HN, sc, 'TRAUTHG', 'v_2040', 0.20, 'HON-T028', 'HON-01', 'p.27'),
          (HN, sc, 'TRAUTHG', 'v_2050', 0.20, 'HON-T028', 'HON-01', 'p.27'),
          (HN, sc, 'TRAUTHG', 'Restriction_Type', 'Min/Max', 'HON-T028', 'HON-01', 'p.27')]
    for t in ['TRYTKHD', 'TRYLFHD']:
        T += [(HN, sc, t, 'v_2040', 0.15, 'HON-T029', 'HON-01', 'p.27'),
              (HN, sc, t, 'v_2050', 0.15, 'HON-T029', 'HON-01', 'p.27'),
              (HN, sc, t, 'Restriction_Type', 'Min/Max', 'HON-T029', 'HON-01', 'p.27')]
cur = {}
for model in {t[0] for t in T}:
    wb = openpyxl.load_workbook(M.ROOT / model / 'B1_Scenario_Config.xlsx', read_only=True)
    data = list(wb['Tech_Adoption'].iter_rows(values_only=True))
    hdr = [str(h) for h in data[0]]
    for r in data[1:]:
        cur[(model, r[0], r[4])] = dict(zip(hdr, r))
rows, loaded = [], []
for model, sc, tech, col, val, vid, src, page in T:
    c = cur.get((model, sc, tech))
    if c is None:
        loaded.append([vid, model, sc, tech, col, val, 'not loaded: no adoption row of the technology'])
        continue
    loaded.append([vid, model, sc, tech, col, val, 'loaded'])
    if str(c[col]) == str(val):
        continue
    rows.append(dict(model=model, file='B1_Scenario_Config.xlsx', sheet='Tech_Adoption', tech=f'{sc}|{tech}', parameter='',
                     year=col, before=c[col], after=val, unit='share of the class output', source_id=src, page=page,
                     derivation=f'{vid}: published fleet share written as the class output share' +
                                (' (2035 value written in the 2040 column and held; the 2035 share interpolates)' if col == 'v_2040' else ''),
                     assumption_sentence=ASSUM, range_low='', range_high=''))
with open(M.JOB / 'work' / 'register_transport.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
with open(M.JOB / 'work' / 'transport_targets.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['value_id', 'model', 'scenario', 'technology', 'column', 'value', 'result'])
    w.writerows(loaded)
print(len(rows), 'cells;', sum(1 for l in loaded if l[-1] != 'loaded'), 'not loaded')
