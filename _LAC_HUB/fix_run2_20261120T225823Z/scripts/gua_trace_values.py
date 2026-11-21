"""D8 trace values (read-only): Guatemala hydro at each pipeline step, from the tracked stage outputs at the base commit.
Run from the clone root: py -I scripts/gua_trace_values.py"""
import openpyxl, pandas as pd
YRS = [2023, 2024, 2025, 2026, 2027, 2030, 2040, 2050]
def ctrl(path, sheet):
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)[sheet]
    rows = list(ws.iter_rows(values_only=True)); h = [str(x) for x in rows[0]]
    d = pd.DataFrame(rows[1:], columns=h)
    d = d[(d.Country == 'Guatemala') & (d.Sub_Group.astype(str).str.upper().str.startswith('HYDRO'))]
    return d
for stage, path in [('Stage 1', '_STAGE1_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx'), ('Stage 2', '_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx')]:
    for sh in ['CURRENT_SHARES', 'CURRENT_LOWER']:
        d = ctrl(path, sh)
        print(f'## {stage} {sh}')
        for _, r in d.iterrows():
            print(r.Scenario, r.Tech, [round(float(r[str(y)]), 4) for y in YRS])
        tot = d.groupby('Scenario')[[str(y) for y in YRS]].apply(lambda g: g.astype(float).sum())
        print('sum by scenario'); print(tot.round(4).to_string())
den = pd.read_excel('_STAGE0_OUTPUT/STAGE0_DENOMINATORS.xlsx', sheet_name='ALL')
den = den[den.Country == 'Guatemala'].pivot_table(index='Year', columns='Scenario', values='Empirical_Gen_PJ')
print('## Stage 0 denominators (PJ)'); print(den.loc[YRS].round(3).to_string())
x = pd.read_excel('_STAGE3_RESULTS/stage3_results.xlsx', sheet_name='TotalTechnologyAnnualActivity')
x = x[(x.Country == 'Guatemala') & x.Technology.isin(['PPHDAM', 'PPHROR']) & x.Year.isin(YRS)]
print('## Stage 3 hydro activity (PJ)'); print(x.pivot_table(index=['Technology', 'Year'], columns='Scenario', values='Value').round(4).to_string())
for sc in ['BAU', 'NDCNEW', 'LTSNEW']:
    m = pd.read_csv(f'Guatemala/GUA_ENERGY/B1_Output_Params/{sc}/TotalAnnualMinCapacityInvestment.csv')
    m = m[m.TECHNOLOGY.isin(['PPHDAM', 'PPHROR']) & (m.Value > 0)]
    print('## B1 MinCapInvest', sc, m[['TECHNOLOGY', 'YEAR', 'Value']].values.tolist())
