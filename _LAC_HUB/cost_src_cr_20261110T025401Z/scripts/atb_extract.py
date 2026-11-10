"""Extract the NREL ATB 2024 rows used for Costa Rica plant paths (Market case, Moderate scenario) into scripts/atb_extract.csv."""
import sys, os, pandas as pd
JOB = sys.argv[1]
f = os.path.join(JOB, 'downloads', 'plants', 'NREL_ATB2024_v4.0.0_ATBe.csv')
keep = {('UtilityPV', 'Class5'), ('CommPV', 'Class5'), ('ResPV', 'Class5'), ('LandbasedWind', 'Class4'), ('Hydropower', 'NPD1'),
        ('Hydropower', 'NSD2'), ('Hydropower', 'NSD3'), ('Geothermal', 'HydroFlash'), ('Geothermal', 'HydroBinary'), ('Biopower', 'Dedicated')}
out = []
for ch in pd.read_csv(f, chunksize=500000, low_memory=False):
    m = ch[(ch.core_metric_case == 'Market') & (ch.scenario == 'Moderate') & ch.core_metric_parameter.isin(['CAPEX', 'OCC', 'Fixed O&M', 'Variable O&M'])]
    m = m[[ (t, d) in keep for t, d in zip(m.technology, m.techdetail)]]
    out.append(m)
d = pd.concat(out)
d = d.drop_duplicates(subset=['technology', 'techdetail', 'core_metric_parameter', 'core_metric_variable'])
d[['technology', 'techdetail', 'core_metric_parameter', 'units', 'core_metric_variable', 'value']].to_csv(os.path.join(JOB, 'scripts', 'atb_extract.csv'), index=False)
p = d.pivot_table(index=['technology', 'techdetail', 'core_metric_parameter'], columns='core_metric_variable', values='value')
print(p[[2022, 2024, 2030, 2035, 2040, 2050]].round(2).to_string())
print(d.columns.tolist())
