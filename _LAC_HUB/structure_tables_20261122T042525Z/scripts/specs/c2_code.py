# Phase C step C2 (retire): A2 outputs under older scenario names are no longer written; where an older output
# fed the scenarios in use (Dominican Republic NDCcond, Guatemala and Honduras NDP, Jamaica LTS label), the
# compiler writes the same data straight into the folders of the scenarios in use (the label inside the files is
# unchanged until C3). B1 references to older names that only matter for scenarios never run are re-pointed to the
# scenario in use (same result for the three scenarios run). Applied with --target work.
CRA = "CostaRica/CR_ENERGY/t1_confection/A2_Compiler_CostaRica.py"
DRA = "DominicanRepublic/RD_ENERGY/A2_Compiler_DominicanRepublic.py"
ECA = "Ecuador/ECU_Energy/A2_Compiler_Ecuador.py"
GUA = "Guatemala/GUA_ENERGY/A2_Compiler_Guatemala.py"
HOA = "Honduras/HON_ENERGY/A2_Compiler_Honduras.py"
JAA = "Jamaica/JAM_ENERGY/A2_Compiler_Jamaica.py"
CRB = "CostaRica/CR_ENERGY/t1_confection/B1_Base_Scenarios_Adj_Parallel_CostaRica.py"
DRB = "DominicanRepublic/RD_ENERGY/B1_Base_Scenarios_Adj_Parallel_DominicanRepublic.py"
GUB = "Guatemala/GUA_ENERGY/B1_Base_Scenarios_Adj_Parallel_Guatemala.py"
HOB = "Honduras/HON_ENERGY/B1_Base_Scenarios_Adj_Parallel_Honduras.py"
JAB = "Jamaica/JAM_ENERGY/B1_Base_Scenarios_Adj_Parallel_Jamaica.py"
CRY = "CostaRica/CR_ENERGY/t1_confection/MOMF_T1_A.yaml"
POLICY = """    for scen in LT.scenarios('policy'):  # the scenarios in use that this output feeds
        df_to_print.to_csv( './A2_Output_Params/' + scen + '/' + list_dicts[d] + '.csv', index=False, header=True)"""
EDITS = [
    (CRA, """list_dicts = list( overall_param_df_dict_ndp.keys() )
for other_scen in other_setup_params[ 'Other_Scenarios' ]:
    for d in range( len( list_dicts ) ):
        df_to_print = overall_param_df_dict_ndp[ list_dicts[d] ]
        df_to_print = df_to_print.replace( { 'Scenario':{ other_setup_params[ 'Main_Scenario' ]:other_scen } } )
        df_to_print.to_csv( params['A2_output'] + other_scen + '/' + list_dicts[d] + '.csv', index=False, header=True)
""", """# The outputs under older scenario names (NDCincond, NDCcond) are retired: no scenario in use read them.
"""),
    (CRY, "  Other_Scenarios: ['NDCincond','NDCcond'],", "  Other_Scenarios: [],"),
    (CRY, "A2_output_NDP: './A2_Output_Params/NDCincond/'\n", ""),
    (ECA, """list_dicts = list( overall_param_df_dict_ndp.keys() )
for d in range( len( list_dicts ) ):
    df_to_print = overall_param_df_dict_ndp[ list_dicts[d] ]
    df_to_print = df_to_print.replace( { 'Scenario':{ other_setup_params[ 'Main_Scenario' ]:other_setup_params[ 'Other_Scenarios' ] } } )
    os.makedirs('./A2_Output_Params/' + other_setup_params['Other_Scenarios'], exist_ok=True)
    df_to_print.to_csv( './A2_Output_Params/'+other_setup_params[ 'Other_Scenarios' ]+'/' + list_dicts[d] + '.csv', index=False, header=True)
""", """# The output under the older scenario name NDCINC is retired: no scenario in use read it.
"""),
    (ECA, "LTS_STR = LT.scenario('older_ndc_incremental')\n", ""),
    (DRA, """    df_to_print.to_csv( './A2_Output_Params/' + LT.scenario('older_ndc_unconditional') + '/' + list_dicts[d] + '.csv', index=False, header=True)
    df_to_print = df_to_print.replace( { 'Scenario':{LT.scenario('older_ndc_unconditional'):LT.scenario('older_ndc_conditional')} } )
    df_to_print.to_csv( './A2_Output_Params/' + LT.scenario('older_ndc_conditional') + '/' + list_dicts[d] + '.csv', index=False, header=True)""",
     """    df_to_print = df_to_print.replace( { 'Scenario':{LT.scenario('older_ndc_unconditional'):LT.scenario('older_ndc_conditional')} } )
""" + POLICY),
    (GUA, "    df_to_print.to_csv( './A2_Output_Params/' + LT.scenario('older_ndp') + '/' + list_dicts[d] + '.csv', index=False, header=True)",
     POLICY),
    (HOA, """    df_to_print.to_csv( './A2_Output_Params/' + LT.scenario('older_ndp') + '/' + list_dicts[d] + '.csv', index=False, header=True)
    df_to_print = df_to_print.replace( { 'Scenario':{LT.scenario('older_ndp'):LT.scenario('older_ndp_ambitious')} } )
    df_to_print.to_csv( './A2_Output_Params/' + LT.scenario('older_ndp_ambitious') + '/' + list_dicts[d] + '.csv', index=False, header=True)
    df_to_print = df_to_print.replace( { 'Scenario':{LT.scenario('older_ndp_ambitious'):LT.scenario('older_ndc_unconditional')} } )
    df_to_print.to_csv( './A2_Output_Params/' + LT.scenario('older_ndc_unconditional') + '/' + list_dicts[d] + '.csv', index=False, header=True)
    df_to_print = df_to_print.replace( { 'Scenario':{LT.scenario('older_ndc_unconditional'):LT.scenario('older_ndc_conditional')} } )
    df_to_print.to_csv( './A2_Output_Params/' + LT.scenario('older_ndc_conditional') + '/' + list_dicts[d] + '.csv', index=False, header=True)""",
     POLICY),
    (JAA, "    df_to_print.to_csv( './A2_Output_Params/'+LTS_STR+'/' + list_dicts[d] + '.csv', index=False, header=True)", POLICY),
    (JAA, "LTS_STR = LT.scenario('lts')\n", ""),
    # ---------------------------------------------------------------- B1 re-points (branches only for scenarios never run)
    (DRB, "and LT.scenario('older_lts') in scenario_list[ s ]:", "and LT.scenario('lts') in scenario_list[ s ]:"),
    (DRB, "Blend_Shares[ LT.scenario('older_lts') ]", "Blend_Shares[ LT.scenario('lts') ]"),
    (GUB, "Blend_Shares[ LT.scenario('older_ndp') ]", "Blend_Shares[ LT.scenario('ndc') ]"),
    (HOB, "Blend_Shares[ LT.scenario('older_ndp') ]", "Blend_Shares[ LT.scenario('ndc') ]"),
    (HOB, "if scenario_list[s] not in  [LT.scenario('base'),LT.scenario('older_ndc_unconditional'),LT.scenario('older_ndc_conditional')]:",
     "if scenario_list[s] not in  [LT.scenario('base')]:"),
    (JAB, "LTS_STR = LT.scenario('older_lts')", "LTS_STR = LT.scenario('lts')"),
    (CRB, "Blend_Shares[ params[LT.scenario('older_ndp')] ]", "Blend_Shares[ LT.scenario('ndc') ]"),
]
