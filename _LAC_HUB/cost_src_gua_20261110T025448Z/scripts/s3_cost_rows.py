"""Step 3: list current cost rows of the Guatemala A-O workbook (cached values) and
recompute the brief's section 5 values from the BAU compiled CSVs."""
import sys, os
import openpyxl, pandas as pd

ROOT = sys.argv[1]  # clone root
JOB = sys.argv[2]   # job folder
WB = os.path.join(ROOT, 'Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx')
BAU = os.path.join(ROOT, 'Guatemala/GUA_ENERGY/A2_Output_Params/BAU')

PLANTS = ['PPBGS', 'PPBIM', 'PPCOA', 'PPDSL', 'PPFOI', 'PPGEO', 'PPHDAM', 'PPHROR', 'PPNGS',
          'PPPVD', 'PPPVDS', 'PPPVT', 'PPPVT2', 'PPPVTS', 'PPWNDON']
SUPPLY = ['DIST_COA', 'DIST_COK', 'DIST_DSL', 'DIST_FOI', 'DIST_GSL', 'DIST_KER', 'DIST_LPG',
          'DIST_NGS', 'EXTT_CRU']
IMPORT = ['IMP_ELE']

wb = openpyxl.load_workbook(WB, data_only=True, read_only=True)
out = []
for s in ['Primary Techs', 'Secondary Techs']:
    rows = list(wb[s].iter_rows(values_only=True))
    hdr = rows[0]
    years = [h for h in hdr if isinstance(h, int)]
    for r in rows[1:]:
        d = dict(zip(hdr, r))
        if d.get('Parameter') not in ('CapitalCost', 'FixedCost', 'VariableCost'):
            continue
        t = d['Tech']
        scope = ('plant in scope' if t in PLANTS else 'supply row' if t in SUPPLY
                 else 'electricity import' if t in IMPORT else 'other')
        rec = {'sheet': s, 'Tech.ID': d['Tech.ID'], 'Tech': t, 'Tech.Name': d['Tech.Name'],
               'Parameter': d['Parameter'], 'Unit': d['Unit'],
               'Projection.Mode': d['Projection.Mode'], 'Projection.Parameter': d['Projection.Parameter']}
        for y in years:
            rec[str(y)] = d[y]
        rec['scope'] = scope
        out.append(rec)
df = pd.DataFrame(out)
df.to_csv(os.path.join(JOB, 'cost_rows_current.csv'), index=False)
print('cost rows', len(df)); print(df.scope.value_counts().to_string())

# recompute section 5 values from BAU CSVs (2024)
def bau(name):
    x = pd.read_csv(os.path.join(BAU, name + '.csv'))
    return x
res = []
for p in ['CapitalCost', 'FixedCost', 'VariableCost']:
    x = bau(p)
    cols = x.columns.tolist()
    tcol = [c for c in cols if c.upper() in ('TECHNOLOGY', 'T', 'TECH')][0]
    ycol = [c for c in cols if c.upper() in ('YEAR', 'Y')][0]
    vcol = 'VALUE' if 'VALUE' in cols else cols[-1]
    sub = x[(x[ycol] == 2024) & (x[tcol].isin(PLANTS + SUPPLY + IMPORT))]
    for _, r in sub.iterrows():
        res.append({'tech': r[tcol], 'param': p, 'mode': r.get('MODE_OF_OPERATION', ''), 'value_2024': r[vcol]})
rc = pd.DataFrame(res)
for p in ['ResidualCapacity']:
    x = bau(p); tcol = [c for c in x.columns if c.upper() in ('TECHNOLOGY',)][0]
    sub = x[(x['YEAR'] == 2024) & (x[tcol].isin(PLANTS))]
    for _, r in sub.iterrows():
        rc = pd.concat([rc, pd.DataFrame([{'tech': r[tcol], 'param': p, 'mode': '', 'value_2024': r['Value']}])])
rc.to_csv(os.path.join(JOB, 'scripts', 's3_bau_2024_check.csv'), index=False)
print(rc.pivot_table(index='tech', columns='param', values='value_2024', aggfunc='first').to_string())
