"""Step 3: list current cost rows of the Ecuador A-O workbook and recheck the brief's section 5 values.

Usage: py -I step3_cost_rows.py <repo_root> <job_folder>
Reads only; writes cost_rows_current.csv and step3_check.txt in the job folder.
"""
import sys, os
import pandas as pd
import openpyxl

repo, job = sys.argv[1], sys.argv[2]
E = os.path.join(repo, 'Ecuador', 'ECU_Energy')
AO = os.path.join(E, 'A1_Outputs', 'A-O_Parametrization.xlsx')
BAU = os.path.join(E, 'A2_Output_Params', 'BAU')

PLANTS = ['PPBGS', 'PPBIM', 'PPCRU', 'PPDDSL', 'PPDFOI', 'PPDSL', 'PPFOI', 'PPHD', 'PPHDAMAB', 'PPHDAMAM',
          'PPHDAMAS', 'PPHDAMPM', 'PPHDAMPS', 'PPHRORAB', 'PPHRORAM', 'PPHRORAS', 'PPHRORPM', 'PPHRORPS',
          'PPIBIM', 'PPIHD', 'PPILPG', 'PPNGS', 'PPPVD', 'PPPVT', 'PPPVTS', 'PPRDSL', 'PPRNGS', 'PPWNDD', 'PPWNDON']
SUPPLY = ['DIST_COA', 'DIST_COK', 'DIST_CRU', 'DIST_DSL', 'DIST_FOI', 'DIST_GSL', 'DIST_JET', 'DIST_KER',
          'DIST_LPG', 'DIST_NGS', 'DIST_OPE', 'EXTT_CRU', 'EXTT_NGS']
IMPORT = ['IMPELE']
NOTED_OTHER = ['ADD_GRE', 'DIST_BGS', 'DIST_BIM', 'DIST_CHA', 'DIST_FIR', 'DIST_OID', 'DIST_RDF', 'ELE_DIST',
               'ELE_TRANS', 'HYD_DIST', 'HYD_G_PROD', 'PROCRU', 'PRONGS', 'STOELE',
               'REF_DSL', 'REF_FOI', 'REF_GSL', 'REF_JET', 'REF_LPG', 'REF_OPE']


def scope(t):
    if t in PLANTS:
        return 'plant in scope'
    if t in SUPPLY:
        return 'supply row'
    if t in IMPORT:
        return 'electricity import'
    if t in NOTED_OTHER:
        return 'other (country notes: proposal)'
    return 'other'


wb = openpyxl.load_workbook(AO, data_only=True, read_only=True)
out = []
for sheet in ['Primary Techs', 'Secondary Techs']:
    rows = list(wb[sheet].iter_rows(values_only=True))
    hdr = list(rows[0])
    years = [h for h in hdr if isinstance(h, int)]
    for r in rows[1:]:
        d = dict(zip(hdr, r))
        if d.get('Parameter') in ('CapitalCost', 'FixedCost', 'VariableCost'):
            rec = {'sheet': sheet, 'Tech.ID': d['Tech.ID'], 'Tech': d['Tech'], 'Tech.Name': d['Tech.Name'],
                   'Parameter': d['Parameter'], 'Unit': d['Unit'], 'Projection.Mode': d['Projection.Mode'],
                   'Projection.Parameter': d['Projection.Parameter']}
            for y in years:
                rec[str(y)] = d[y]
            rec['scope'] = scope(d['Tech'])
            out.append(rec)
df = pd.DataFrame(out)
df.to_csv(os.path.join(job, 'cost_rows_current.csv'), index=False)

# Recheck section 5 from the BAU compiled CSVs
def load(p):
    x = pd.read_csv(os.path.join(BAU, p + '.csv'))
    return x[['TECHNOLOGY', 'YEAR', 'Value']]

cc, fc, vc, rc = load('CapitalCost'), load('FixedCost'), load('VariableCost'), load('ResidualCapacity')
mx, mi = load('TotalAnnualMaxCapacity'), load('TotalAnnualMaxCapacityInvestment')
lines = []
v24 = lambda x, t: x[(x.TECHNOLOGY == t) & (x.YEAR == 2024)].Value
for t in PLANTS:
    r = v24(rc, t); r = float(r.iloc[0]) if len(r) else 0.0
    m = mx[(mx.TECHNOLOGY == t) & (mx.YEAR >= 2025)].merge(
        rc[rc.TECHNOLOGY == t], on=['TECHNOLOGY', 'YEAR'], how='left', suffixes=('', '_rc')).fillna({'Value_rc': 0})
    room = (len(m) == 0) or bool((m.Value > m.Value_rc + 1e-9).any())
    inv = mi[mi.TECHNOLOGY == t]
    inv_ok = len(inv) == 0 or bool((inv.Value != 0).any())
    vals = [v24(x, t) for x in (cc, fc, vc)]
    vals = [float(v.iloc[0]) if len(v) else None for v in vals]
    lines.append(f'{t},{r},{"yes" if room and inv_ok else "no"},{vals[0]},{vals[1]},{vals[2]}')
for t in SUPPLY + IMPORT:
    v = v24(vc, t)
    lines.append(f'{t},VariableCost2024,{float(v.iloc[0]) if len(v) else None}')
with open(os.path.join(job, 'downloads', '_extract', 'step3_check.txt'), 'w') as f:
    f.write('tech,residual2024,can_build_more,CapitalCost2024,FixedCost2024,VariableCost2024\n' + '\n'.join(lines) + '\n')
# placeholder counts
pl = [t for t in PLANTS]
print('rows', len(df), df.scope.value_counts().to_dict())
print('\n'.join(lines))
