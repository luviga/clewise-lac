"""Step 7: coal versus petroleum coke check for Costa Rica; writes structure_proposals.csv."""
import csv, os, sys
JOB = sys.argv[1]
COK_NCV = 32.5          # IPCC_NCV_COK, GEN-002
BAL_COK_GJ_PER_T = 3713.16 / 138.6   # balance 2022 Tabla 3: 3,713.16 TJ over 138.6 kt
cok2021_ipcc = 124327.9 * COK_NCV / 1e6
cok2021_bal = 124327.9 * BAL_COK_GJ_PER_T / 1e6
rows = [
    dict(status='proposed', file='CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Demand.xlsx', sheet='Demand_Projection',
         row_identifiers='row 25, Demand/Share=Demand, Fuel/Tech=E5INDCOA, Name=Demand Industrial Coal', column='2021 (cell M25)',
         current_value=0.675, proposed_value=0.00667,
         reason=('Industry coal in 2021 has no support: customs record 2.5 t of anthracite and no other coal in 2021 (PROCOMER HS 2701, CR-017; '
                 'UN Comtrade 2,472 kg), and the 2022 balance gives industry coal of 0.26 kt, 6.67 TJ. The model already uses 0.00667 PJ from 2022 on. '
                 'The 0.675 PJ is not petroleum coke recorded as coal: 2021 petroleum coke imports of 124,327.9 t (CR-016; balance p.36 states 124,327 t) '
                 'give %.3f PJ at the IPCC 32.5 GJ/t (GEN-002), within 1.2 percent of the model 2021 E5INDCOK of 4.091 PJ, so petroleum coke is already counted. '
                 'Least change: hold 2021 industry coal at the 2022 balance value.') % cok2021_ipcc,
         balance_page='Balance Energetico Nacional 2022, PDF p.40 Tabla 3 (Carbon Mineral 0.26 kt, 6.67 TJ; Coque de Petroleo 138.6 kt, 3,713.16 TJ); PDF p.36 (2021 petroleum coke imports 124,327 t)',
         source_ids='CRC-006;CR-016;CR-017;CR-018;GEN-002'),
    dict(status='follows from regeneration (no direct edit)', file='CostaRica/CR_ENERGY/t1_confection/A2_Output_Params/{BAU,NDCNEW,LTSNEW}/SpecifiedAnnualDemand.csv and B1_Output_Params copies',
         row_identifiers='TECHNOLOGY blank, FUEL=E5INDCOA, YEAR=2021', column='Value', current_value=0.675, proposed_value=0.00667,
         reason='Compiled from A-O_Demand.xlsx Demand_Projection by the A2 compiler; changes when the workbook cell changes.',
         balance_page='as above', source_ids='CRC-006'),
    dict(status='no change', file='CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Demand.xlsx', sheet='Demand_Projection',
         row_identifiers='row 21, Fuel/Tech=E5INDCOK, Name=Demand Industrial Petroleum Coke', column='2021 to 2050',
         current_value='4.091 (2021), 3.713 (2022)', proposed_value='unchanged',
         reason=('2022 value equals the balance 3,713.16 TJ. 2021 value 4.091 PJ is within 1.2 percent of customs petroleum coke 124,327.9 t x 32.5 GJ/t = %.3f PJ '
                 '(with the balance implied %.2f GJ/t it would be %.3f PJ; see GAPS).') % (cok2021_ipcc, BAL_COK_GJ_PER_T, cok2021_bal),
         balance_page='PDF p.40 Tabla 3; PDF p.36', source_ids='CRC-006;CR-016;CR-018;GEN-002'),
    dict(status='no change', file='CostaRica/CR_ENERGY/t1_confection/A2_Output_Params/BAU/InputActivityRatio.csv and OutputActivityRatio.csv',
         row_identifiers='T5COAIND (E0_COA to E5INDCOA), T5COKIND (E1_COK to E5INDCOK), IMPCOA (E0_COA), IMPCOK (E1_COK)', column='Value',
         current_value=1.0, proposed_value='unchanged', reason='The fuel links are already separate for coal and petroleum coke; only the 2021 coal quantity is wrong.',
         balance_page='PDF p.26 (solid fuels imported by final consumers for industry, not used for power)', source_ids='CRC-006'),
    dict(status='alternative, not recommended', file='CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Demand.xlsx', sheet='Demand_Projection',
         row_identifiers='rows 25 (E5INDCOA) and 21 (E5INDCOK)', column='2021 (cells M25 and M21)', current_value='0.675 and 4.091', proposed_value='0 and 4.766',
         reason=('Moving the 0.675 PJ into petroleum coke would put 2021 petroleum coke at 4.766 PJ, 18 percent above the %.3f PJ that 2021 customs imports give at the IPCC factor.') % cok2021_ipcc,
         balance_page='PDF p.36; PDF p.40', source_ids='CRC-006;CR-016;GEN-002'),
]
cols = ['status', 'file', 'sheet', 'row_identifiers', 'column', 'current_value', 'proposed_value', 'reason', 'balance_page', 'source_ids']
with open(os.path.join(JOB, 'structure_proposals.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, '') for k in cols})
print('cok2021 ipcc %.3f bal %.3f (%.2f GJ/t)' % (cok2021_ipcc, cok2021_bal, BAL_COK_GJ_PER_T))
