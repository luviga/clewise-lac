# Phase C step C2: `if` branches that test an older scenario name, for scenarios never run; removed with their body.
BLOCKS = [
    ("CostaRica/CR_ENERGY/t1_confection/B1_Base_Scenarios_Adj_Parallel_CostaRica.py", "if LT.scenario('older_ndc_conditional') == scenario_list[s]:"),
    ("CostaRica/CR_ENERGY/t1_confection/B1_Base_Scenarios_Adj_Parallel_CostaRica.py", "scenario_list[ s ] == params[LT.scenario('older_ndp')]:"),
    ("DominicanRepublic/RD_ENERGY/B1_Base_Scenarios_Adj_Parallel_DominicanRepublic.py", "if scenario_list[s] == LT.scenario('older_ndc_conditional'):"),
    ("Guatemala/GUA_ENERGY/B1_Base_Scenarios_Adj_Parallel_Guatemala.py", "if scenario_list[s] == LT.scenario('older_ndp'):"),
    ("Guatemala/GUA_ENERGY/B1_Base_Scenarios_Adj_Parallel_Guatemala.py", "and scenario_list[ s ] == LT.scenario('older_ndp'):"),
]
