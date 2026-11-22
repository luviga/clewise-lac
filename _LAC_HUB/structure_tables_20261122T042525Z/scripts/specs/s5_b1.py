# Phase B edits of the six B1 runners (after the rounding line rule). Count -1: every code line.
CR = "CostaRica/CR_ENERGY/t1_confection/B1_Base_Scenarios_Adj_Parallel_CostaRica.py"
DR = "DominicanRepublic/RD_ENERGY/B1_Base_Scenarios_Adj_Parallel_DominicanRepublic.py"
EC = "Ecuador/ECU_Energy/B1_Base_Scenarios_Adj_Parallel.py"
GU = "Guatemala/GUA_ENERGY/B1_Base_Scenarios_Adj_Parallel_Guatemala.py"
HO = "Honduras/HON_ENERGY/B1_Base_Scenarios_Adj_Parallel_Honduras.py"
JA = "Jamaica/JAM_ENERGY/B1_Base_Scenarios_Adj_Parallel_Jamaica.py"
ALL = [CR, DR, EC, GU, HO, JA]
N5 = [DR, EC, GU, HO, JA]
SEC = [CR, DR, GU, HO]


def V(k):
    return "_TB1['%s']" % k


S_BASE = "LT.scenario('base')"
EDITS = [
    # ---------------------------------------------------------------- whole blocks first
    (DR, """IGNORE_TECHS = ['TRANRAILFREINF',  'TRANOMOTWalk', 'TRANOMOTBike',
                'TRXTRAIELE', 'TRXTRAIFREELE', 'TRANRAILINF', 'TRANPUB',
                'TRANRAILCAR', 'LATR', 'PROD_CLK_TRAD', 'NO_CONTR_OD',
                'AG_TRVEG']""", "IGNORE_TECHS = LT.techs('transport_cap_ignore', _TC)"),
    (GU, """        ignore_techs = ['TRANRAILFREINF',  'TRANOMOTWalk', 'TRANOMOTBike',
                         'TRXTRAIELE','TRXTRAIFREELE', 'TRANRAILINF', 'TRANPUB', 'TRANRAILCAR']""",
     "        ignore_techs = LT.techs('transport_cap_ignore', _TC)"),
    (HO, """        ignore_techs = ['TRANRAILFREINF',  'TRANOMOTWalk', 'TRANOMOTBike',
                        'TRXTRAIELE', 'TRXTRAIFREELE', 'TRANRAILINF', 'TRANPUB', 'TRANRAILCAR']""",
     "        ignore_techs = LT.techs('transport_cap_ignore', _TC)"),
    (DR, "externality_list = ['Accidents', 'Health', 'Congestion', 'RM', 'FERT_ORG', 'salud_residuos', 'contam_agua', 'turismo_residuos','turismo_residuos', 'CONHAB', 'CONTUR', 'CONVAR', 'CONHICK', 'RESHID', 'DAPANI']",
     "externality_list = LT.emissions('externality', _TC)"),
    ([EC, HO, JA], "this_combination[2] in ['Accidents', 'Health', 'Congestion', 'CONVAR', 'CONHICK', 'REHAB']",
     "this_combination[2] in LT.emissions('externality', _TC)", 0),
    (GU, "this_combination[2] in ['Accidents', 'Health', 'Congestion']", "this_combination[2] in LT.emissions('externality', _TC)", 0),
    (DR, """                                this_set_complement_vals_rel_100 = {
                                    'Techs_He_Freight':100}""",
     "                                this_set_complement_vals_rel_100 = LT.tech_map('freight_rail_complement_share', _TC)"),
    (DR, """                                this_set_complement_vals_rel_100 = {
                                    'Techs_Auto': 15.5,
                                    'Techs_Buses_Micro': 5,
                                    'Techs_Buses_Pub': 0,
                                    'Techs_Buses_Tur': 0,
                                    'Techs_Motos': 70.7,
                                    'Techs_SUV': 8.5,
                                    'Techs_Taxi': 0.3,
                                    }""",
     "                                this_set_complement_vals_rel_100 = LT.tech_map('bus_efficiency_complement_share', _TC)"),
    (GU, """            Gasoline_Techs = [
                'T4GSL_LIG',
                'T4GSL_PRI',
                'DIST_GSL' ]
            #
            Gasoline_Techs_Emissions = {
                'T4GSL_LIG':[ 'CO2e' ],
                'T4GSL_PRI':[ 'CO2e' ],
                'DIST_GSL':['CO2e_sources'] }""", """            Gasoline_Techs = LT.techs('gasoline_blend', _TC)
            #
            Gasoline_Techs_Emissions = LT.emission_map('gasoline_blend', _TC)"""),
    (HO, """            Gasoline_Techs = [
                'T4GSL_LIG',
                'T4GSL_PRI',
                'T4GSL_PUB',
                'T4GSL_TUR',
                'DIST_GSL' ]
            #
            Gasoline_Techs_Emissions = {
                'T4GSL_LIG':[ 'CO2e',  'CO2', 'CH4', 'N2O'],
                'T4GSL_PRI':[ 'CO2e',  'CO2', 'CH4', 'N2O'],
                'T4GSL_PUB':[ 'CO2e',  'CO2', 'CH4', 'N2O'],
                'T4GSL_TUR':[ 'CO2e',  'CO2', 'CH4', 'N2O'],
                'DIST_GSL':['CO2e_sources'] }""", """            Gasoline_Techs = LT.techs('gasoline_blend', _TC)
            #
            Gasoline_Techs_Emissions = LT.emission_map('gasoline_blend', _TC)"""),
    # ---------------------------------------------------------------- module constants
    (DR, "REGION_STR = 'RD'", "REGION_STR = LT.country_value(_TC, 'code')"),
    (EC, "REGION_STR = 'ECU'", "REGION_STR = LT.country_value(_TC, 'code')"),
    (HO, "REGION_STR = 'HON'", "REGION_STR = LT.country_value(_TC, 'code')"),
    (JA, "REGION_STR = 'JAM'", "REGION_STR = LT.country_value(_TC, 'code')"),
    (EC, "LTS_STR = 'LTSNEW'", "LTS_STR = LT.scenario('lts')"),
    (JA, "LTS_STR = 'LTS'", "LTS_STR = LT.scenario('older_lts')"),
    (DR, "BAU_STR = 'BAU'", "BAU_STR = " + S_BASE),
    (DR, "BY_INT = 2018", "BY_INT = " + V('first_year')),
    (DR, "START_VAR_YR_INT = 2024", "START_VAR_YR_INT = " + V('variation_start_year')),
    (DR, "DISC_YR = 2024", "DISC_YR = " + V('discount_year')),
    ([EC, HO, JA], "DISC_YR = 2025", "DISC_YR = " + V('discount_year')),
    ([DR, EC, JA], "DISC_RATE = 0.0504", "DISC_RATE = " + V('discount_rate')),
    (HO, "DISC_RATE = 0.08", "DISC_RATE = " + V('discount_rate')),
    (DR, "EY_INT = 2050", "EY_INT = " + V('last_year')),
    (EC, "INI_YR = 2021", "INI_YR = " + V('first_year')),
    (EC, "END_YR = 2050", "END_YR = " + V('last_year')),
    (EC, "INFLEX_YEAR = 2025", "INFLEX_YEAR = " + V('inflexion_year')),
    (GU, "output_csv_r = 0.10*100", "output_csv_r = " + V('output_discount_rate') + "*100"),
    (GU, "output_csv_year = 2025", "output_csv_year = " + V('discount_year')),
    # ---------------------------------------------------------------- scenario names
    (CR, "params['BAU']", "params[" + S_BASE + "]", -1),
    (CR, "params['NDP']", "params[LT.scenario('older_ndp')]", -1),
    (CR, "Reference_driven_distance['BAU']", "Reference_driven_distance[" + S_BASE + "]", -1),
    (CR, "Reference_occupancy_rate['BAU']", "Reference_occupancy_rate[" + S_BASE + "]", -1),
    (ALL, "'Relative reduction to BAU - distance'", "'Relative reduction to ' + " + S_BASE + " + ' - distance'", -1),
    (ALL, "'Relative increase to BAU - occupancy rate'", "'Relative increase to ' + " + S_BASE + " + ' - occupancy rate'", -1),
    (CR, "if 'NDCcond' == scenario_list[s]:", "if LT.scenario('older_ndc_conditional') == scenario_list[s]:", -1),
    (DR, "if scenario_list[s] == 'NDCcond':", "if scenario_list[s] == LT.scenario('older_ndc_conditional'):", -1),
    (DR, "and 'LTS' in scenario_list[ s ]:", "and LT.scenario('older_lts') in scenario_list[ s ]:", -1),
    (DR, "Blend_Shares[ 'LTS' ]", "Blend_Shares[ LT.scenario('older_lts') ]", -1),
    ([GU, HO], "Blend_Shares[ 'NDP' ]", "Blend_Shares[ LT.scenario('older_ndp') ]", -1),
    (GU, "scenario_list[ s ] == 'NDP'", "scenario_list[ s ] == LT.scenario('older_ndp')", -1),
    (GU, "scenario_list[s] == 'NDP'", "scenario_list[s] == LT.scenario('older_ndp')", -1),
    (GU, "stable_scenarios['NDP']", "stable_scenarios[LT.scenario('older_ndp')]", -1),
    (HO, "if scenario_list[s] not in  ['BAU','NDCincond','NDCcond']:",
     "if scenario_list[s] not in  [" + S_BASE + ",LT.scenario('older_ndc_unconditional'),LT.scenario('older_ndc_conditional')]:", -1),
    (N5, "'BAU'", S_BASE, -1),
    (EC, '"BAU"', S_BASE, -1),
    # ---------------------------------------------------------------- technology, fuel and emission names
    (CR, 'if this_set == "TRNPASRAI":', "if this_set == LT.tech('rail_passenger_tech', _TC):", -1),
    (CR, "str( 'TRNMIC' )", "str( LT.tech('microbus_tech', _TC) )", -1),
    ([CR, DR, EC, HO, JA], "'IMP' not in e", "LT.tech('import_token') not in e", -1),
    ([CR, DR], "if 'ELE' in this_set:", "if LT.tech('electric_set_token') in this_set:", -1),
    (HO, "if this_set=='TRAUTHG':", "if this_set==LT.tech('security_special_tech', _TC):", -1),
    ([EC, HO, JA], "'CO2' in i]", "LT.emission('co2_token') in i]", -1),
    (N5, "'Techs_Trains_Freight'", "LT.tech('rail_freight_set')", -1),
    (N5, "'Techs_Trains'", "LT.tech('rail_passenger_set')", -1),
    ([DR, GU, HO], "'Techs_He_Freight'", "LT.tech('heavy_freight_set')", -1),
    (DR, "'Techs_Telef'", "LT.tech('cable_car_set')", -1),
    (DR, "'Techs_Bus_Efi'", "LT.tech('efficient_bus_set')", -1),
    (DR, "'Techs_Buses_Pub'", "LT.tech('public_bus_set')", -1),
    (DR, "'Techs_Buses_Micro'", "LT.tech('minibus_set')", -1),
    (DR, "'Techs_Buses_Tur'", "LT.tech('tourism_bus_set')", -1),
    (DR, "'Techs_Auto'", "LT.tech('car_set')", -1),
    (DR, "'Techs_Motos'", "LT.tech('motorcycle_set')", -1),
    (DR, "'Techs_SUV'", "LT.tech('suv_set')", -1),
    (DR, "'Techs_Taxi'", "LT.tech('taxi_set')", -1),
    ([DR, EC, GU, HO, JA], "'E6TDPASPRI'", "LT.fuel('passenger_private_demand')", -1),
    ([DR, EC, GU, HO, JA], "'E6TDPASPUB'", "LT.fuel('passenger_public_demand')", -1),
    ([DR, EC, GU, HO, JA], "'E6TDFREHEA'", "LT.fuel('freight_heavy_demand')", -1),
    ([DR, EC, GU, HO, JA], "'E6TDFRELIG'", "LT.fuel('freight_light_demand')", -1),
    ([DR, EC, GU, HO, JA], "'E6TRNOMOT'", "LT.fuel('nonmotorised_demand')", -1),
    (DR, "'E6TDPASTUR'", "LT.fuel('passenger_tourism_demand')", -1),
    ([CR, DR], ".append('RD')", ".append(" + V('appended_region_code') + ")", -1),
    (GU, ".append( 'GUA' )", ".append( " + V('appended_region_code') + " )", -1),
    # ---------------------------------------------------------------- numbers
    (SEC, "security_multiplier_factor = 1.01", "security_multiplier_factor = " + V('upper_security_factor'), -1),
    (SEC, "security_multiplier_factor = 0.999", "security_multiplier_factor = " + V('lower_security_factor'), -1),
    (SEC, "security_multiplier_factor = 1.001", "security_multiplier_factor = " + V('upper_security_factor_fine'), -1),
    (HO, "security_multiplier_factor = 1.005", "security_multiplier_factor = " + V('upper_security_factor_special'), -1),
    (SEC, "value_list = [1.01*group_value_list", "value_list = [" + V('upper_security_factor') + "*group_value_list", -1),
    (SEC, "value_list = [0.999*group_value_list", "value_list = [" + V('lower_security_factor') + "*group_value_list", -1),
    (ALL, "[ 1.01*float(value_list[j])", "[ " + V('upper_security_factor') + "*float(value_list[j])", -1),
    (SEC, "if 999 in known_values:", "if " + V('unknown_value_marker') + " in known_values:", -1),
    (SEC, "if x != float( 999 ) ]", "if x != float( " + V('unknown_value_marker') + " ) ]", -1),
    (N5, ".append( 9999 )", ".append( " + V('max_capacity_open') + " )", -1),
    (ALL, "this_year_index-3]", "this_year_index-" + V('driven_distance_lag_years') + "]", -1),
    ([DR, GU, HO, JA], "time_range_vector.index(2050)", "time_range_vector.index(" + V('last_year') + ")", -1),
    ([DR, GU, HO, JA], "time_range_vector.index(2019)", "time_range_vector.index(" + V('driven_distance_reference_year') + ")", -1),
    ([GU, HO, JA], "time_range_vector.index(2024)", "time_range_vector.index(" + V('history_end_year') + ")", -1),
    ([GU, HO, JA], "int(this_year) >= 2024", "int(this_year) >= " + V('history_end_year'), -1),
    ([GU, HO, JA], "int(this_year) > 2018+", "int(this_year) > " + V('first_year') + "+", -1),
    ([GU, HO, JA], "int(this_year) - subtract_index_accum_old <= 2024", "int(this_year) - subtract_index_accum_old <= " + V('history_end_year'), -1),
    ([GU, HO, JA], "int(this_year) - subtract_index_accum_old > 2024", "int(this_year) - subtract_index_accum_old > " + V('history_end_year'), -1),
    ([GU, HO, JA], "range( 2018 , 2050+1 )", "range( " + V('first_year') + " , " + V('last_year') + "+1 )", -1),
    ([GU, HO, JA], "all_years.index( 2024 )", "all_years.index( " + V('history_end_year') + " )", -1),
    ([GU, HO], "(M-2050)", "(M-" + V('last_year') + ")", -1),
    ([GU, HO], "Initial_Year_of_Uncertainty+1,2050+1 )", "Initial_Year_of_Uncertainty+1," + V('last_year') + "+1 )", -1),
    ([GU, HO], "range(2018, int(y_ini)+1)", "range(" + V('first_year') + ", int(y_ini)+1)", -1),
    (CR, "time_range_vector[y] == 2032", "time_range_vector[y] == " + V('milestone_years') + "[0]", -1),
    (CR, "time_range_vector[y] == 2033", "time_range_vector[y] == " + V('milestone_years') + "[1]", -1),
    (CR, "time_range_vector[y] == 2034", "time_range_vector[y] == " + V('milestone_years') + "[2]", -1),
    ([DR, GU, HO], "time_range_vector[y] == 2030", "time_range_vector[y] == " + V('milestone_years') + "[0]", -1),
    ([DR, GU, HO], "time_range_vector[y] == 2040", "time_range_vector[y] == " + V('milestone_years') + "[1]", -1),
    ([DR, GU, HO], "time_range_vector[y] == 2050", "time_range_vector[y] == " + V('milestone_years') + "[2]", -1),
    ([DR, GU, HO], "known_years_ini + [2030, 2040, 2050 ]", "known_years_ini + " + V('milestone_years'), -1),
    (DR, "for year in range(2018, 2035+1):", "for year in range(" + V('first_year') + ", " + V('modeshift_exact_last_year') + "+1):", -1),
    (DR, "if time_range_vector[y] <= 2035:", "if time_range_vector[y] <= " + V('modeshift_exact_last_year') + ":", -1),
    (DR, "(1/1.006)", "(1/" + V('private_demand_divisor') + ")", -1),
    # ---------------------------------------------------------------- blend points
    ([EC, JA], "start_blend_point = [2026, 1]", "start_blend_point = " + V('biodiesel_blend_start'), -1),
    ([EC, JA], "final_blend_point = [2030, 5]", "final_blend_point = " + V('biodiesel_blend_final'), -1),
    ([EC, JA], "start_blend_point = [2024, 9.98]", "start_blend_point = " + V('ethanol_blend_start'), -1),
    ([EC, JA], "mid_blend_point = [2025, 9.99]", "mid_blend_point = " + V('ethanol_blend_mid'), -1),
    ([EC, JA], "final_blend_point = [2026, 10]", "final_blend_point = " + V('ethanol_blend_final'), -1),
    (GU, "start_blend_point = [2026, 0]", "start_blend_point = " + V('biodiesel_blend_start'), -1),
    (GU, "final_blend_point = [2030, 0]", "final_blend_point = " + V('biodiesel_blend_final'), -1),
    (GU, "start_blend_point = [2024, 0]", "start_blend_point = " + V('ethanol_blend_start'), -1),
    (GU, "mid_blend_point = [2025, 5]", "mid_blend_point = " + V('ethanol_blend_mid'), -1),
    (GU, "final_blend_point = [2026, 10]", "final_blend_point = " + V('ethanol_blend_final'), -1),
    (HO, """start_blend_point = [2025, 0]
                    final_blend_point = [2030, 5]""",
     "start_blend_point = " + V('biodiesel_blend_start') + """
                    final_blend_point = """ + V('biodiesel_blend_final')),
    (HO, """start_blend_point = [2025, 0]
                    mid_blend_point = [2030, 4.99]
                    final_blend_point = [2035, 5.00]""",
     "start_blend_point = " + V('ethanol_blend_start') + """
                    mid_blend_point = """ + V('ethanol_blend_mid') + """
                    final_blend_point = """ + V('ethanol_blend_final')),
]
