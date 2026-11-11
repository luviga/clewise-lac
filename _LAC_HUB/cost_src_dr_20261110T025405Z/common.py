"""Shared constants for the LAC_COST_SRC_DR job (paths are read-only inputs)."""
import os
JOB = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(JOB))  # repository root of the clone
RD = os.path.join(ROOT, "DominicanRepublic", "RD_ENERGY")
WB = os.path.join(RD, "A1_Outputs", "A-O_Parametrization.xlsx")
BAU = os.path.join(RD, "A2_Output_Params", "BAU")
LP = os.path.join(ROOT, "_LAC_HUB", "local_prices_20261109T085226Z")
DL = os.path.join(JOB, "downloads")
STAMP = "20261110T025405Z"
RETRIEVED = "2026-11-10"
PLANTS = ["PPADSL","PPAFOI","PPANGS","PPBGS","PPBIM","PPCCTDSL","PPCCTNGS","PPCOA",
          "PPDBGS","PPDBIM","PPDDSL","PPDFOI","PPDGLP","PPDGSL","PPDHYD","PPDNGS",
          "PPHDAM","PPICEFOI","PPICEGASFOI","PPPVD","PPPVT","PPPVTHYD","PPWNDON"]
SUPPLY = ["DIST_COA","DIST_COK","DIST_CRU","DIST_DSL","DIST_FOI","DIST_GSL","DIST_KER",
          "DIST_LPG","DIST_NGS","EXTT_CRU","EXTT_NGS","PRO_COA"]
IMPORT = ["IMP_ELE"]
COST_PARAMS = ["CapitalCost","FixedCost","VariableCost"]
def scope_of(tech):
    if tech in PLANTS: return "plant in scope"
    if tech in SUPPLY: return "supply row"
    if tech in IMPORT: return "electricity import"
    return "other"
