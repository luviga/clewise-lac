"""Model list for the LAC_COST_SOURCES job (live paths only)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(JOB))

def _m(cc, model, folder, kind, ao=True):
    d = {"cc": cc, "model": model, "folder": folder, "kind": kind}
    d["ao"] = folder + "/A1_Outputs/A-O_Parametrization.xlsx" if ao else None
    d["bau"] = folder + ("/B1_Output_Params/BAU" if ao else "/1_Parameters/BAU")
    return d

MODELS = [
    _m("CR", "CR_ENERGY", "CostaRica/CR_ENERGY/t1_confection", "energy"),
    _m("CR", "CR_AFOLU", "CostaRica/CR_AFOLU/t1_confection", "sector"),
    _m("CR", "CR_IPPU", "CostaRica/CR_IPPU", "sector"),
    _m("CR", "CR_WASTE", "CostaRica/CR_WASTE", "sector"),
    _m("DR", "RD_ENERGY", "DominicanRepublic/RD_ENERGY", "energy"),
    _m("DR", "RD_AFOLU", "DominicanRepublic/RD_AFOLU", "sector"),
    _m("DR", "RD_IPPU", "DominicanRepublic/RD_IPPU", "sector"),
    _m("DR", "RD_WASTE", "DominicanRepublic/RD_WASTE", "sector"),
    _m("ECU", "ECU_Energy", "Ecuador/ECU_Energy", "energy"),
    _m("ECU", "ECU_AGR", "Ecuador/ECU_AGR", "sector"),
    _m("ECU", "ECU_USCUSS", "Ecuador/ECU_USCUSS", "sector"),
    _m("ECU", "ECU_IPPU", "Ecuador/ECU_IPPU", "sector"),
    _m("ECU", "ECU_WASTE", "Ecuador/ECU_WASTE", "sector"),
    _m("GUA", "GUA_ENERGY", "Guatemala/GUA_ENERGY", "energy"),
    _m("GUA", "GUA_AFOLU", "Guatemala/GUA_AFOLU", "sector", ao=False),
    _m("GUA", "GUA_IPPU", "Guatemala/GUA_IPPU", "sector"),
    _m("GUA", "GUA_WASTE", "Guatemala/GUA_WASTE", "sector"),
    _m("HON", "HON_ENERGY", "Honduras/HON_ENERGY", "energy"),
    _m("HON", "HON_AFOLU", "Honduras/HON_AFOLU/HON_AFOLU", "sector"),
    _m("HON", "HON_IPPU", "Honduras/HON_IPPU", "sector"),
    _m("HON", "HON_WASTE", "Honduras/HON_WASTE", "sector"),
    _m("JAM", "JAM_ENERGY", "Jamaica/JAM_ENERGY", "energy"),
    _m("JAM", "JAM_AFOLU", "Jamaica/JAM_AFOLU", "sector"),
    _m("JAM", "JAM_TRANSPORT", "Jamaica/JAM_TRANSPORT", "sector"),
    _m("JAM", "JAM_WASTE", "Jamaica/JAM_WASTE", "sector"),
]
