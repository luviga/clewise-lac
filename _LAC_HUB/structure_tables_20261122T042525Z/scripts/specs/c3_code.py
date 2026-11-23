# Phase C step C3 (rename): code edits after C2. The A2 outputs that feed the policy scenarios take the name of
# the folder they are written to (the label goes, the values stay); the older roles leave the code.
# Applied with --target work.
DRA = "DominicanRepublic/RD_ENERGY/A2_Compiler_DominicanRepublic.py"
GUA = "Guatemala/GUA_ENERGY/A2_Compiler_Guatemala.py"
HOA = "Honduras/HON_ENERGY/A2_Compiler_Honduras.py"
JAA = "Jamaica/JAM_ENERGY/A2_Compiler_Jamaica.py"
POLICY_OLD = """    for scen in LT.scenarios('policy'):  # the scenarios in use that this output feeds
        df_to_print.to_csv( './A2_Output_Params/' + scen + '/' + list_dicts[d] + '.csv', index=False, header=True)"""
POLICY_NEW = """    for scen in LT.scenarios('policy'):  # the scenarios in use that this output feeds, labelled with their name
        df_to_print.replace( { 'Scenario':{ other_setup_params[ 'Main_Scenario' ]:scen } } ).to_csv( './A2_Output_Params/' + scen + '/' + list_dicts[d] + '.csv', index=False, header=True)"""
EDITS = [
    (DRA, """    df_to_print = df_to_print.replace({ 'Scenario':{ other_setup_params[ 'Main_Scenario' ]:other_setup_params[ 'Other_Scenarios' ] } })
""", ""),
    (DRA, """    df_to_print = df_to_print.replace( { 'Scenario':{LT.scenario('older_ndc_unconditional'):LT.scenario('older_ndc_conditional')} } )
""", ""),
    ([GUA, HOA, JAA], """    df_to_print = df_to_print.replace( { 'Scenario':{ other_setup_params[ 'Main_Scenario' ]:other_setup_params[ 'Other_Scenarios' ] } } )
""", ""),
    ([DRA, GUA, HOA, JAA], POLICY_OLD, POLICY_NEW),
]
