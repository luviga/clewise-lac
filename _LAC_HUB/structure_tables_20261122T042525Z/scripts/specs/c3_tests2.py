# Phase C step C3: scenario lists of stage2_test_v2.py left by c3_tests.py, read from the catalogue.
T2 = "stage2_test_v2.py"
EDITS = [
    (T2, 'for sc in ["BAU", "NDCNEW", "LTSNEW"]]', 'for sc in LT.scenarios()]'),
    (T2, 'for s in ["BAU", "NDCNEW", "LTSNEW"]}', 'for s in LT.scenarios()}'),
    (T2, 'for s in ["BAU", "NDCNEW", "LTSNEW"]]', 'for s in LT.scenarios()]'),
    (T2, """f"{c} {y}: BAU={vals.get('BAU','?'):.1f} NDC={vals.get('NDCNEW','?'):.1f} \"""",
     """f"{c} {y}: BAU={vals.get(LT.scenario('base'),'?'):.1f} NDC={vals.get(LT.scenario('ndc'),'?'):.1f} \""""),
    (T2, """f"LTS={vals.get('LTSNEW','?'):.1f} (spread={spread:.1f} PJ)")""",
     """f"LTS={vals.get(LT.scenario('lts'),'?'):.1f} (spread={spread:.1f} PJ)")"""),
]
