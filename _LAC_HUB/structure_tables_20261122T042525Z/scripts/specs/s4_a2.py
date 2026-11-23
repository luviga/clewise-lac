# Phase B edits of the A2 compilers that the line rules did not cover.
CR = "CostaRica/CR_ENERGY/t1_confection/A2_Compiler_CostaRica.py"
DR = "DominicanRepublic/RD_ENERGY/A2_Compiler_DominicanRepublic.py"
EC = "Ecuador/ECU_Energy/A2_Compiler_Ecuador.py"
GU = "Guatemala/GUA_ENERGY/A2_Compiler_Guatemala.py"
HO = "Honduras/HON_ENERGY/A2_Compiler_Honduras.py"
JA = "Jamaica/JAM_ENERGY/A2_Compiler_Jamaica.py"
D = "_TA2['rounding_digits']"
OUT = "'./A2_Output_Params/' + LT.scenario('%s') + '/'"
EDITS = [
    ([CR, EC, GU, HO, JA], "round( this_df_select_by_fi[ inp ], 4 ) #", "round( this_df_select_by_fi[ inp ], " + D + " ) #"),
    (DR, "round(this_df_select_by_fi[ inp ], 4) #", "round(this_df_select_by_fi[ inp ], " + D + ") #"),
    (DR, "df_to_print.to_csv('./A2_Output_Params/BAU/' + list_dicts[d]", "df_to_print.to_csv(" + OUT % 'base' + " + list_dicts[d]"),
    ([EC, GU, HO, JA], "df_to_print.to_csv( './A2_Output_Params/BAU/' + list_dicts[d]", "df_to_print.to_csv( " + OUT % 'base' + " + list_dicts[d]"),
    (EC, "os.makedirs('./A2_Output_Params/BAU/', exist_ok=True)", "os.makedirs(" + OUT % 'base' + ", exist_ok=True)"),
    ([DR, HO], "df_to_print.to_csv( './A2_Output_Params/NDCincond/' + list_dicts[d]", "df_to_print.to_csv( " + OUT % 'older_ndc_unconditional' + " + list_dicts[d]"),
    ([DR, HO], "df_to_print.to_csv( './A2_Output_Params/NDCcond/' + list_dicts[d]", "df_to_print.to_csv( " + OUT % 'older_ndc_conditional' + " + list_dicts[d]"),
    ([DR, HO], """df_to_print = df_to_print.replace( { 'Scenario':{"NDCincond":"NDCcond"} } )""",
     """df_to_print = df_to_print.replace( { 'Scenario':{LT.scenario('older_ndc_unconditional'):LT.scenario('older_ndc_conditional')} } )"""),
    ([GU, HO], "df_to_print.to_csv( './A2_Output_Params/NDP/' + list_dicts[d]", "df_to_print.to_csv( " + OUT % 'older_ndp' + " + list_dicts[d]"),
    (HO, """df_to_print = df_to_print.replace( { 'Scenario':{"NDP":"NDPAMB"} } )""",
     """df_to_print = df_to_print.replace( { 'Scenario':{LT.scenario('older_ndp'):LT.scenario('older_ndp_ambitious')} } )"""),
    (HO, "df_to_print.to_csv( './A2_Output_Params/NDPAMB/' + list_dicts[d]", "df_to_print.to_csv( " + OUT % 'older_ndp_ambitious' + " + list_dicts[d]"),
    (HO, """df_to_print = df_to_print.replace( { 'Scenario':{"NDPAMB":"NDCincond"} } )""",
     """df_to_print = df_to_print.replace( { 'Scenario':{LT.scenario('older_ndp_ambitious'):LT.scenario('older_ndc_unconditional')} } )"""),
    (EC, "LTS_STR = 'NDCINC'", "LTS_STR = LT.scenario('older_ndc_incremental')"),
    (JA, "LTS_STR = 'LTSNEW'", "LTS_STR = LT.scenario('lts')"),
]
