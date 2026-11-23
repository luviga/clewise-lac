# Phase C step C3: the stage tests read their scenario names from the catalogue (applied with --target work).
T1 = "stage1_test_v16.py"
T2 = "stage2_test_v2.py"
T3 = "stage3_test.py"
NDC = 'LT.scenario("ndc")'
LTS = 'LT.scenario("lts")'
BASE = 'LT.scenario("base")'
EDITS = [
    (T1, "import pandas as pd\n", "import pandas as pd\n\nimport lac_tables as LT  # scenario names from config/scenarios/scenario_catalogue.csv\n"),
    (T1, 'EXPECTED_SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]', "EXPECTED_SCENARIOS = LT.scenarios()"),
    (T1, '("NDCNEW", ', "(" + NDC + ", ", -1),
    (T1, '("LTSNEW", ', "(" + LTS + ", ", -1),
    (T1, '(shares["Scenario"] == "BAU")', '(shares["Scenario"] == ' + BASE + ')', -1),
    (T1, 'for sc in ["NDCNEW", "LTSNEW"]:', 'for sc in LT.scenarios("policy"):', -1),
    (T2, "import openpyxl\n", "import openpyxl\n\nimport lac_tables as LT  # scenario names from config/scenarios/scenario_catalogue.csv\n"),
    (T2, '("NDCNEW", 2035, 0.70, "NDCNEW 75% target @2035 (5pp margin)")', '(' + NDC + ', 2035, 0.70, f"{' + NDC + '} 75% target @2035 (5pp margin)")'),
    (T2, '("NDCNEW", 2050, 0.70, "NDCNEW 75% target @2050 (5pp margin)")', '(' + NDC + ', 2050, 0.70, f"{' + NDC + '} 75% target @2050 (5pp margin)")'),
    (T2, '("LTSNEW", 2035, 0.70, "LTSNEW 75% target @2035 (5pp margin)")', '(' + LTS + ', 2035, 0.70, f"{' + LTS + '} 75% target @2035 (5pp margin)")'),
    (T2, '("LTSNEW", 2050, 0.94, "LTSNEW 99% target @2050 (5pp margin)")', '(' + LTS + ', 2050, 0.94, f"{' + LTS + '} 99% target @2050 (5pp margin)")'),
    (T2, '("NDCNEW", 2035, 0.85, "CR NDCNEW 90% @2035 (5pp)")', '(' + NDC + ', 2035, 0.85, f"CR {' + NDC + '} 90% @2035 (5pp)")'),
    (T2, '("NDCNEW", 2050, 0.85, "CR NDCNEW 90% @2050 (5pp)")', '(' + NDC + ', 2050, 0.85, f"CR {' + NDC + '} 90% @2050 (5pp)")'),
    (T2, '("LTSNEW", 2035, 0.94, "CR LTSNEW 99% @2035 (5pp)")', '(' + LTS + ', 2035, 0.94, f"CR {' + LTS + '} 99% @2035 (5pp)")'),
    (T2, '("LTSNEW", 2050, 0.94, "CR LTSNEW 99% @2050 (5pp)")', '(' + LTS + ', 2050, 0.94, f"CR {' + LTS + '} 99% @2050 (5pp)")'),
    (T2, '("NDCNEW", 2035, 0.75, "ECU NDCNEW 80% @2035 (5pp)")', '(' + NDC + ', 2035, 0.75, f"ECU {' + NDC + '} 80% @2035 (5pp)")'),
    (T2, '("NDCNEW", 2050, 0.75, "ECU NDCNEW 80% @2050 (5pp)")', '(' + NDC + ', 2050, 0.75, f"ECU {' + NDC + '} 80% @2050 (5pp)")'),
    (T2, '("LTSNEW", 2035, 0.75, "ECU LTSNEW 80% @2035 (5pp)")', '(' + LTS + ', 2035, 0.75, f"ECU {' + LTS + '} 80% @2035 (5pp)")'),
    (T2, '("LTSNEW", 2050, 0.94, "ECU LTSNEW 99% @2050 (5pp)")', '(' + LTS + ', 2050, 0.94, f"ECU {' + LTS + '} 99% @2050 (5pp)")'),
    (T2, 'ss == "BAU"', 'ss == ' + BASE, -1),
    (T2, '(c, "BAU", t)', '(c, ' + BASE + ', t)', -1),
    (T2, 'k[1] == "BAU"', 'k[1] == ' + BASE, -1),
    (T2, 'for sc in ["BAU", "NDCNEW", "LTSNEW"]:', 'for sc in LT.scenarios():', -1),
    (T2, 'bau_vals = csv_vals["BAU"]', 'bau_vals = csv_vals[' + BASE + ']', -1),
    (T2, 'for sc in ["NDCNEW", "LTSNEW"]:', 'for sc in LT.scenarios("policy"):', -1),
    (T3, "import pandas as pd\n", "import pandas as pd\n\nimport lac_tables as LT  # scenario names from config/scenarios/scenario_catalogue.csv\n"),
    (T3, 'SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]', "SCENARIOS = LT.scenarios()"),
]
