"""Step 3: list current cost rows of the CR A-O workbook and recompute the brief's section 5 table."""
import pandas as pd, sys, os
ROOT = sys.argv[1]; JOB = sys.argv[2]
B = os.path.join(ROOT, 'CostaRica/CR_ENERGY/t1_confection')
WB = os.path.join(B, 'A1_Outputs/A-O_Parametrization.xlsx')
PLANTS = ['PP_SPV_DG','PWRBMS','PWRDSL','PWRFOI','PWRGEO','PWRHYDDAM','PWRHYDROR','PWRSPVDTR','PWRSPVTRN','PWRWNONS']
SUPPLY = ['IMPAVG','IMPCOA','IMPCOK','IMPFOI','IMPKJF','IMPLPG','IMPNGS','IMPPURDSL','IMPPURGSL']
IMPORT = ['IMPELE']
rows = []
for s in ['Primary Techs', 'Secondary Techs']:
    d = pd.read_excel(WB, s)
    years = [c for c in d.columns if isinstance(c, int)]
    c = d[d['Parameter'].isin(['CapitalCost', 'FixedCost', 'VariableCost'])].copy()
    c.insert(0, 'sheet', s)
    def scope(t):
        if t in PLANTS: return 'plant in scope'
        if t in SUPPLY: return 'supply row'
        if t in IMPORT: return 'electricity import'
        return 'other'
    c['scope'] = c['Tech'].map(scope)
    rows.append(c[['sheet','Tech.ID','Tech','Tech.Name','Parameter','Unit','Projection.Mode','Projection.Parameter','scope'] + years])
out = pd.concat(rows)
out.to_csv(os.path.join(JOB, 'cost_rows_current.csv'), index=False)
print('cost rows', len(out), out['scope'].value_counts().to_dict())
# Recompute section 5 from BAU csvs
P = os.path.join(B, 'A2_Output_Params/BAU')
def load(n):
    d = pd.read_csv(os.path.join(P, n + '.csv'))
    return d.pivot_table(index='TECHNOLOGY', columns='YEAR', values='Value', aggfunc='first')
cc, fc, vc, rc = load('CapitalCost'), load('FixedCost'), load('VariableCost'), load('ResidualCapacity')
mx, mi = load('TotalAnnualMaxCapacity'), load('TotalAnnualMaxCapacityInvestment')
def g(t, df, y=2024):
    try: return df.loc[t, y]
    except KeyError: return float('nan')
res = []
for t in PLANTS + SUPPLY:
    yrs = [y for y in range(2025, 2051)]
    room = any((g(t, mx, y) if not pd.isna(g(t, mx, y)) else 1e9) > (0 if pd.isna(g(t, rc, y)) else g(t, rc, y)) + 1e-9 for y in yrs)
    inv0 = t in mi.index and all(g(t, mi, y) == 0 for y in yrs if not pd.isna(g(t, mi, y))) and mi.loc[t].notna().any()
    res.append(dict(tech=t, residual_2024=g(t, rc), can_build_more='yes' if room and not inv0 else 'no',
                    CapitalCost_2024=g(t, cc), FixedCost_2024=g(t, fc), VariableCost_2024=g(t, vc)))
r = pd.DataFrame(res)
r.to_csv(os.path.join(JOB, 'scripts', 'section5_recomputed.txt'), index=False)
print(r.to_string())
