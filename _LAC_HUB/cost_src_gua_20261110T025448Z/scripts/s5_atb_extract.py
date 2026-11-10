"""Step 5 helper: extract the NREL ATB Moderate, Market-case CAPEX, Fixed O&M and Variable O&M
paths used for the Guatemala plant rows from the saved ATB 2021, 2023 and 2024 ATBe.csv files.
Output: work/atb_paths.csv (edition, technology, techdetail, parameter, year, value, units, dollar_year, csv_row)."""
import os, sys
import pandas as pd

J = sys.argv[1]
D = os.path.join(J, 'downloads', 'intl')
FILES = {2024: 'NREL_ATB2024_v4_ATBe.csv', 2023: 'NREL_ATB2023_ATBe.csv', 2021: 'NREL_ATB2021_ATBe.csv'}
WANT = {  # technology: techdetail (default class)
    'UtilityPV': ['Class5', 'Class1'], 'CommPV': ['Class5', 'Class1'], 'ResPV': ['Class5', 'Class1'],
    'Utility-Scale PV-Plus-Battery': ['Class5', 'Class1'], 'LandbasedWind': ['Class4'], 'Geothermal': ['HydroFlash', 'Hydro / Flash'],
    'Hydropower': ['NPD1', 'NSD1'], 'Biopower': ['Dedicated'], 'NaturalGas_FE': ['F-Frame CC', 'CCAvgCF', 'F-Frame CT', 'CTAvgCF'],
    'NaturalGas': ['F-Frame CC', 'CCAvgCF', 'F-Frame CT', 'CTAvgCF'], 'Coal_FE': ['newAvgCF', 'New'], 'Coal': ['newAvgCF'],
    'Commercial Battery Storage': ['4Hr Battery Storage', '4Hr'], 'Residential Battery Storage': ['5kW 12.5kWh', '5kW12.5kWh'],
}
PARAMS = ['CAPEX', 'Fixed O&M', 'Variable O&M']
out = []
for ed, f in FILES.items():
    x = pd.read_csv(os.path.join(D, f), low_memory=False)
    x = x[(x.scenario == 'Moderate') & (x.core_metric_case == 'Market') & (x.core_metric_parameter.isin(PARAMS))]
    if 'tax_credit_case' in x.columns:
        x = x[x.tax_credit_case.isin(['ITC', 'PTC', 'None', 'No Tax Credit'] if False else x.tax_credit_case.unique())]
    x = x[x.technology.isin(WANT.keys())]
    for _, r in x.iterrows():
        if str(r.techdetail) not in WANT[r.technology]:
            continue
        out.append({'edition': f'ATB {ed}', 'technology': r.technology, 'techdetail': r.techdetail,
                    'tax_credit_case': r.get('tax_credit_case', ''), 'parameter': r.core_metric_parameter,
                    'year': int(r.core_metric_variable), 'value': float(r.value), 'units': r.units, 'csv_row_index': r.iloc[0]})
o = pd.DataFrame(out).drop_duplicates(subset=['edition', 'technology', 'techdetail', 'parameter', 'year', 'value'])
o.to_csv(os.path.join(J, 'work', 'atb_paths.csv'), index=False)
print(o.groupby(['edition', 'technology', 'techdetail', 'parameter']).agg(n=('value', 'size'), y0=('year', 'min'), y1=('year', 'max'),
      v2024=('value', lambda s: None)).to_string())
